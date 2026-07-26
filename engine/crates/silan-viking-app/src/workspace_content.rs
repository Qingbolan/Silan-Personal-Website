//! Source-backed workspace editing use cases.
//!
//! This is the application contract consumed by presentation adapters. It
//! deliberately exposes source identities and editable DTOs, never projection
//! rows or database schema details.

use crate::parser::{EntryValue, Parsed};
use crate::{ContentEditor, EditorError, TranslationLocator, Workspace};
use serde::{Deserialize, Serialize};
use silan_viking_base::HasMeta;
use silan_viking_content::{ContentKind, PartShape};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum WorkspaceContentError {
    #[error("workspace open failed: {0}")]
    Open(#[from] crate::workspace::OpenError),
    #[error("workspace scan failed: {0}")]
    Scan(#[from] crate::workspace::ScanError),
    #[error("content parse failed: {0}")]
    Parse(#[from] crate::parser::ParseError),
    #[error("content edit failed: {0}")]
    Edit(#[from] EditorError),
    #[error("editable document `{0}` was not found")]
    NotFound(String),
    #[error("invalid translation id `{0}`; expected `<part_id>:<language>`")]
    InvalidTranslationId(String),
    #[error("invalid content metadata: {0}")]
    InvalidMetadata(String),
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct EditableWorkspace {
    pub documents: Vec<EditableDocument>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct EditableDocument {
    pub id: String,
    pub item_id: String,
    pub content_type: String,
    pub slug: String,
    pub title: String,
    pub description: Option<String>,
    pub series_slug: Option<String>,
    pub episode_number: Option<i64>,
    pub status: String,
    pub visibility: String,
    pub updated_at: String,
    pub cover_uri: Option<String>,
    pub cover_source_type: Option<String>,
    pub cover_website_url: Option<String>,
    pub github_url: Option<String>,
    pub demo_url: Option<String>,
    pub article_attribution: Option<ArticleAttribution>,
    pub date: Option<String>,
    pub pinned: bool,
    pub parts: Vec<EditablePart>,
}

/// One external destination surfaced with a Blog as a compact attachment.
///
/// `kind` is a stable semantic key (`website`, `github`, `paper`, `doi`, …);
/// presentation adapters localize the visible kind label while `label`
/// preserves an optional author override.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct ArticleResource {
    pub kind: String,
    pub label: String,
    pub url: String,
}

/// Blog-level project identity and image attribution authored in frontmatter.
///
/// This data stays independent from the Markdown body so the desktop editor,
/// CLI watermark workflow, website resource strip, and SEO renderer consume
/// one source contract.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct ArticleAttribution {
    pub project_name: String,
    pub publication_venue: String,
    pub project_url: String,
    pub external_resources: Vec<ArticleResource>,
    pub image_author: String,
    pub image_site_url: String,
    pub image_watermark_mode: String,
    pub image_watermark_position: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct EditablePart {
    pub id: String,
    pub role: String,
    pub shape: String,
    pub canonical_language: String,
    pub translations: Vec<EditableTranslation>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct EditableTranslation {
    pub id: String,
    pub language: String,
    pub content: String,
    pub source_revision: SourceRevision,
    pub source_path: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct SourceRevision(pub String);

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct SaveTranslationInput {
    pub translation_id: String,
    pub content: String,
    pub expected_revision: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct SaveLifecycleInput {
    pub translation_id: String,
    pub status: String,
    pub visibility: String,
    pub pinned: Option<bool>,
    pub expected_revision: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct SaveMetadataInput {
    pub translation_id: String,
    pub title: String,
    pub description: Option<String>,
    pub cover_url: Option<String>,
    pub cover_source_type: Option<String>,
    pub cover_website_url: Option<String>,
    pub github_url: Option<String>,
    pub demo_url: Option<String>,
    pub article_attribution: Option<ArticleAttribution>,
    pub expected_revision: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct SaveProjectFeaturedInput {
    pub translation_id: String,
    pub is_featured: bool,
    pub expected_revision: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CreateTranslationInput {
    pub part_id: String,
    pub language: String,
    pub title: String,
    pub body: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct WorkspaceEntityCount {
    pub content_type: String,
    pub count: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct EditableSection {
    pub role: String,
    pub shape: String,
    pub canonical_language: String,
    pub entries: Vec<EditableEntry>,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct EditableEntry {
    pub id: String,
    pub sort_order: usize,
    pub shared: serde_json::Value,
    pub localized: serde_json::Value,
}

/// Source-backed application service. The projection database is accepted
/// only by mutation methods that must synchronize after an atomic source save.
pub struct WorkspaceContent {
    content_root: PathBuf,
    workspace: Workspace,
    editor: ContentEditor,
}

impl WorkspaceContent {
    pub fn open(content_root: impl AsRef<Path>) -> Result<Self, WorkspaceContentError> {
        let content_root = content_root.as_ref().to_path_buf();
        Ok(Self {
            workspace: Workspace::open(&content_root)?,
            editor: ContentEditor::open(&content_root)?,
            content_root,
        })
    }

    pub fn editable_workspace(&self) -> Result<EditableWorkspace, WorkspaceContentError> {
        Ok(EditableWorkspace {
            documents: self.editable_documents()?,
        })
    }

    pub fn editable_documents(&self) -> Result<Vec<EditableDocument>, WorkspaceContentError> {
        let scan = self.workspace.scan()?;
        let mut documents = Vec::with_capacity(scan.items().len());
        for item in scan.items() {
            let parsed = self.workspace.parsers().parser_for(item)?.parse(item)?;
            let canonical_language = item
                .parts()
                .first()
                .map(|part| part.canonical_lang().to_string())
                .unwrap_or_else(|| "en".to_owned());
            let title = parsed
                .langs()
                .iter()
                .find(|(language, _)| language.to_string() == canonical_language)
                .and_then(|(_, variant)| variant.text("title"))
                .or_else(|| {
                    parsed
                        .langs()
                        .values()
                        .find_map(|variant| variant.text("title"))
                })
                .unwrap_or_else(|| item.slug().as_str())
                .to_owned();
            let description = parsed
                .main()
                .text("excerpt")
                .or_else(|| parsed.main().text("abstract"))
                .or_else(|| parsed.main().text("description"))
                .or_else(|| {
                    parsed
                        .langs()
                        .iter()
                        .find(|(language, _)| language.to_string() == canonical_language)
                        .and_then(|(_, variant)| {
                            variant
                                .text("excerpt")
                                .or_else(|| variant.text("abstract"))
                                .or_else(|| variant.text("description"))
                        })
                })
                .map(str::to_owned);
            let series_slug = (item.kind() == ContentKind::Episode)
                .then(|| parsed.main().text("series").map(str::to_owned))
                .flatten();
            let parts = item
                .parts()
                .iter()
                .map(|part| {
                    let translations = part
                        .files()
                        .iter()
                        .map(|file| EditableTranslation {
                            id: translation_id(part.id().as_str(), &file.lang().to_string()),
                            language: file.lang().to_string(),
                            content: source_body(part.shape(), file.body()),
                            source_revision: SourceRevision(file.hash().to_string()),
                            source_path: source_path(
                                item.kind(),
                                series_slug.as_deref(),
                                item.slug().as_str(),
                                part.role().as_str(),
                                &file.lang().to_string(),
                                part.shape(),
                            ),
                        })
                        .collect();
                    EditablePart {
                        id: part.id().to_string(),
                        role: part.role().to_string(),
                        shape: part.shape().schema_name().to_owned(),
                        canonical_language: part.canonical_lang().to_string(),
                        translations,
                    }
                })
                .collect();
            documents.push(EditableDocument {
                id: item.id().to_string(),
                item_id: item.id().to_string(),
                content_type: item.kind().frontmatter_value().to_owned(),
                slug: item.slug().to_string(),
                title,
                description,
                series_slug,
                episode_number: parsed.main().int("episode_number"),
                status: parsed.main().text("status").unwrap_or("draft").to_owned(),
                visibility: parsed
                    .main()
                    .text("visibility")
                    .unwrap_or("private")
                    .to_owned(),
                updated_at: item.meta().updated_at().to_string(),
                cover_uri: parsed
                    .main()
                    .text("cover_url")
                    .or_else(|| parsed.main().text("cover_image"))
                    .or_else(|| parsed.main().text("featured_image_url"))
                    .or_else(|| parsed.main().text("thumbnail_url"))
                    .or_else(|| {
                        parsed
                            .langs()
                            .iter()
                            .find(|(language, _)| language.to_string() == canonical_language)
                            .and_then(|(_, variant)| variant.text("featured_image_url"))
                    })
                    .map(str::to_owned),
                cover_source_type: match item.kind() {
                    ContentKind::Project => Some(normalize_cover_source_type(
                        parsed.main().text("cover_source_type"),
                    )),
                    _ => None,
                },
                cover_website_url: match item.kind() {
                    ContentKind::Project => {
                        parsed.main().text("cover_website_url").map(str::to_owned)
                    }
                    _ => None,
                },
                github_url: match item.kind() {
                    ContentKind::Project => parsed.main().text("github_url").map(str::to_owned),
                    _ => None,
                },
                demo_url: match item.kind() {
                    ContentKind::Project => parsed.main().text("demo_url").map(str::to_owned),
                    _ => None,
                },
                article_attribution: (item.kind() == ContentKind::Blog)
                    .then(|| article_attribution(&parsed)),
                date: parsed
                    .main()
                    .text("date")
                    .or_else(|| parsed.main().text("published_at"))
                    .map(str::to_owned),
                pinned: parsed.main().bool("pinned").unwrap_or(false),
                parts,
            });
        }
        Ok(documents)
    }

    pub fn editable_document(
        &self,
        document_id: &str,
    ) -> Result<EditableDocument, WorkspaceContentError> {
        self.editable_documents()?
            .into_iter()
            .find(|document| document.id == document_id)
            .ok_or_else(|| WorkspaceContentError::NotFound(document_id.to_owned()))
    }

    pub fn translation(
        &self,
        id: &str,
    ) -> Result<(EditableDocument, EditablePart, EditableTranslation), WorkspaceContentError> {
        for document in self.editable_documents()? {
            for part in &document.parts {
                if let Some(translation) = part.translations.iter().find(|value| value.id == id) {
                    return Ok((document.clone(), part.clone(), translation.clone()));
                }
            }
        }
        Err(WorkspaceContentError::NotFound(id.to_owned()))
    }

    pub fn entity_counts(&self) -> Result<Vec<WorkspaceEntityCount>, WorkspaceContentError> {
        let mut counts = std::collections::BTreeMap::<String, usize>::new();
        for document in self.editable_documents()? {
            *counts.entry(document.content_type).or_default() += 1;
        }
        Ok(counts
            .into_iter()
            .map(|(content_type, count)| WorkspaceEntityCount {
                content_type,
                count,
            })
            .collect())
    }

    pub fn document_for_part(
        &self,
        part_id: &str,
    ) -> Result<(EditableDocument, EditablePart), WorkspaceContentError> {
        for document in self.editable_documents()? {
            if let Some(part) = document.parts.iter().find(|part| part.id == part_id) {
                return Ok((document.clone(), part.clone()));
            }
        }
        Err(WorkspaceContentError::NotFound(part_id.to_owned()))
    }

    pub fn editable_sections(
        &self,
        content_type: ContentKind,
        language: &str,
    ) -> Result<Vec<EditableSection>, WorkspaceContentError> {
        let scan = self.workspace.scan()?;
        let Some(item) = scan.items().iter().find(|item| item.kind() == content_type) else {
            return Ok(Vec::new());
        };
        let parsed = self.workspace.parsers().parser_for(item)?.parse(item)?;
        let requested = parsed
            .langs()
            .iter()
            .find(|(lang, _)| lang.to_string() == language)
            .map(|(_, variant)| variant)
            .or_else(|| parsed.langs().values().next());
        let Some(variant) = requested else {
            return Ok(Vec::new());
        };
        Ok(item
            .parts()
            .iter()
            .filter(|part| !part.shape().is_prose())
            .map(|part| EditableSection {
                role: part.role().to_string(),
                shape: part.shape().schema_name().to_owned(),
                canonical_language: part.canonical_lang().to_string(),
                entries: variant
                    .entries(part.role().as_str())
                    .iter()
                    .enumerate()
                    .map(|(index, entry)| EditableEntry {
                        id: entry.entry_id().to_owned(),
                        sort_order: index,
                        shared: entry_map_json(entry.shared()),
                        localized: entry_map_json(entry.localized()),
                    })
                    .collect(),
            })
            .collect())
    }

    pub fn save_translation(
        &self,
        input: &SaveTranslationInput,
        db_path: impl AsRef<Path>,
    ) -> Result<EditableDocument, WorkspaceContentError> {
        let (document, part, translation) = self.translation(&input.translation_id)?;
        if part.shape != PartShape::Prose.schema_name() {
            return Err(WorkspaceContentError::InvalidTranslationId(
                input.translation_id.clone(),
            ));
        }
        let locator = locator(&document, &part, &translation.language)?;
        self.editor.save_markdown_and_sync(
            &locator,
            &input.content,
            &input.expected_revision,
            db_path,
        )?;
        WorkspaceContent::open(&self.content_root)?.editable_document(&document.id)
    }

    pub fn create_translation(
        &self,
        input: &CreateTranslationInput,
        db_path: impl AsRef<Path>,
    ) -> Result<EditableDocument, WorkspaceContentError> {
        let (document, part) = self.document_for_part(&input.part_id)?;
        if part.shape != PartShape::Prose.schema_name() {
            return Err(WorkspaceContentError::InvalidTranslationId(format!(
                "{}:{}",
                input.part_id, input.language
            )));
        }
        if part
            .translations
            .iter()
            .any(|translation| translation.language == input.language)
        {
            return Err(WorkspaceContentError::InvalidTranslationId(format!(
                "{}:{} already exists",
                input.part_id, input.language
            )));
        }
        let locator = locator(&document, &part, &input.language)?;
        let source = markdown_source(&input.title, &input.body)?;
        self.editor
            .create_markdown_and_sync(&locator, &source, db_path)?;
        WorkspaceContent::open(&self.content_root)?.editable_document(&document.id)
    }

    pub fn save_lifecycle(
        &self,
        input: &SaveLifecycleInput,
        db_path: impl AsRef<Path>,
    ) -> Result<EditableDocument, WorkspaceContentError> {
        let (document, part, translation) = self.translation(&input.translation_id)?;
        let locator = locator(&document, &part, &translation.language)?;
        let pinned = input.pinned.map(|value| value.to_string());
        let mut fields = vec![
            ("status", input.status.as_str()),
            ("visibility", input.visibility.as_str()),
        ];
        if let Some(value) = pinned.as_deref() {
            fields.push(("pinned", value));
        }
        self.editor.save_frontmatter_fields_and_sync(
            &locator,
            &fields,
            &input.expected_revision,
            db_path,
        )?;
        WorkspaceContent::open(&self.content_root)?.editable_document(&document.id)
    }

    pub fn save_metadata(
        &self,
        input: &SaveMetadataInput,
        db_path: impl AsRef<Path>,
    ) -> Result<EditableDocument, WorkspaceContentError> {
        let (document, part, translation) = self.translation(&input.translation_id)?;
        let kind = ContentKind::from_frontmatter_value(&document.content_type)
            .map_err(|_| WorkspaceContentError::NotFound(document.id.clone()))?;
        let locator = locator(&document, &part, &translation.language)?;
        let mut fields = vec![yaml_text("title", input.title.trim())];
        if let Some(field) = summary_field_for(kind) {
            fields.push(yaml_text(
                field,
                input.description.as_deref().unwrap_or_default().trim(),
            ));
        }
        if let Some(field) = cover_field_for(kind) {
            fields.push(yaml_text(
                field,
                input.cover_url.as_deref().unwrap_or_default().trim(),
            ));
        }
        if kind == ContentKind::Project {
            fields.push(yaml_text(
                "cover_source_type",
                &normalize_cover_source_type(input.cover_source_type.as_deref()),
            ));
            fields.push(yaml_text(
                "cover_website_url",
                input
                    .cover_website_url
                    .as_deref()
                    .unwrap_or_default()
                    .trim(),
            ));
            fields.push(yaml_text(
                "github_url",
                input.github_url.as_deref().unwrap_or_default().trim(),
            ));
            fields.push(yaml_text(
                "demo_url",
                input.demo_url.as_deref().unwrap_or_default().trim(),
            ));
        }
        if kind == ContentKind::Blog {
            if let Some(attribution) = input.article_attribution.clone() {
                let attribution = normalize_article_attribution(attribution)?;
                fields.extend(article_attribution_yaml(&attribution));
            }
        }
        self.editor.save_frontmatter_values_and_sync(
            &locator,
            &fields,
            &input.expected_revision,
            db_path,
        )?;
        WorkspaceContent::open(&self.content_root)?.editable_document(&document.id)
    }

    /// Change whether a project is selected for the website home page.
    ///
    /// The authored frontmatter remains the source of truth; the projection
    /// is refreshed atomically after the source mutation.
    pub fn save_project_featured(
        &self,
        input: &SaveProjectFeaturedInput,
        db_path: impl AsRef<Path>,
    ) -> Result<EditableDocument, WorkspaceContentError> {
        let (document, part, translation) = self.translation(&input.translation_id)?;
        if document.content_type != ContentKind::Project.frontmatter_value() {
            return Err(WorkspaceContentError::InvalidTranslationId(
                input.translation_id.clone(),
            ));
        }
        let locator = locator(&document, &part, &translation.language)?;
        let value = input.is_featured.to_string();
        self.editor.save_frontmatter_fields_and_sync(
            &locator,
            &[("is_featured", value.as_str())],
            &input.expected_revision,
            db_path,
        )?;
        WorkspaceContent::open(&self.content_root)?.editable_document(&document.id)
    }

    pub fn content_root(&self) -> &Path {
        &self.content_root
    }

    pub fn editor(&self) -> &ContentEditor {
        &self.editor
    }
}

pub fn translation_id(part_id: &str, language: &str) -> String {
    format!("{part_id}:{language}")
}

fn source_body(shape: PartShape, raw: &str) -> String {
    if !shape.is_prose() {
        return raw.to_owned();
    }
    crate::parser::frontmatter::split(raw).body
}

fn source_path(
    kind: ContentKind,
    series_slug: Option<&str>,
    slug: &str,
    role: &str,
    language: &str,
    shape: PartShape,
) -> String {
    let mut path = PathBuf::from("resources").join(kind.dir_name());
    if let Some(series_slug) = series_slug {
        path.push(series_slug);
    }
    path.push(slug);
    path.join("parts")
        .join(role)
        .join(format!("{language}.{}", shape.file_extension()))
        .to_string_lossy()
        .replace('\\', "/")
}

fn locator(
    document: &EditableDocument,
    part: &EditablePart,
    language: &str,
) -> Result<TranslationLocator, WorkspaceContentError> {
    let kind = ContentKind::from_frontmatter_value(&document.content_type)
        .map_err(|_| WorkspaceContentError::NotFound(document.id.clone()))?;
    TranslationLocator::new(
        kind,
        document.slug.clone(),
        document.series_slug.clone(),
        part.role.clone(),
        language,
    )
    .map_err(WorkspaceContentError::Edit)
}

fn summary_field_for(kind: ContentKind) -> Option<&'static str> {
    match kind {
        ContentKind::Blog => Some("excerpt"),
        ContentKind::Idea => Some("abstract"),
        ContentKind::Project => Some("description"),
        _ => None,
    }
}

fn cover_field_for(kind: ContentKind) -> Option<&'static str> {
    match kind {
        ContentKind::Blog => Some("featured_image_url"),
        ContentKind::Project => Some("thumbnail_url"),
        _ => None,
    }
}

fn normalize_cover_source_type(value: Option<&str>) -> String {
    match value.map(str::trim) {
        Some("website") => "website".to_owned(),
        _ => "image".to_owned(),
    }
}

fn article_attribution(parsed: &Parsed) -> ArticleAttribution {
    let resources = parsed
        .main()
        .get("external_resources")
        .and_then(|value| value.as_records())
        .unwrap_or_default()
        .iter()
        .filter_map(|record| {
            let url = record_text(record, "url");
            (!url.is_empty()).then(|| ArticleResource {
                kind: record_text(record, "kind"),
                label: record_text(record, "label"),
                url,
            })
        })
        .collect();
    ArticleAttribution {
        project_name: parsed
            .main()
            .text("project_name")
            .unwrap_or_default()
            .to_owned(),
        publication_venue: parsed
            .main()
            .text("publication_venue")
            .unwrap_or_default()
            .to_owned(),
        project_url: parsed
            .main()
            .text("project_url")
            .unwrap_or_default()
            .to_owned(),
        external_resources: resources,
        image_author: parsed
            .main()
            .text("image_author")
            .unwrap_or_default()
            .to_owned(),
        image_site_url: parsed
            .main()
            .text("image_site_url")
            .unwrap_or_default()
            .to_owned(),
        image_watermark_mode: parsed
            .main()
            .text("image_watermark_mode")
            .unwrap_or("off")
            .to_owned(),
        image_watermark_position: parsed
            .main()
            .text("image_watermark_position")
            .unwrap_or("bottom-right")
            .to_owned(),
    }
}

fn record_text(record: &BTreeMap<String, String>, key: &str) -> String {
    record
        .get(key)
        .map(|value| value.trim().to_owned())
        .unwrap_or_default()
}

fn normalize_article_attribution(
    attribution: ArticleAttribution,
) -> Result<ArticleAttribution, WorkspaceContentError> {
    let mode = attribution.image_watermark_mode.trim();
    if !matches!(mode, "" | "off" | "metadata" | "visible" | "both") {
        return Err(WorkspaceContentError::InvalidMetadata(format!(
            "unsupported image watermark mode `{mode}`"
        )));
    }
    let position = attribution.image_watermark_position.trim();
    if !matches!(position, "" | "bottom-left" | "bottom-right") {
        return Err(WorkspaceContentError::InvalidMetadata(format!(
            "unsupported image watermark position `{position}`"
        )));
    }

    let mut resources = Vec::new();
    let mut seen_urls = std::collections::BTreeSet::new();
    for resource in attribution.external_resources {
        let url = normalize_external_url("external resource URL", &resource.url)?;
        if url.is_empty() || !seen_urls.insert(url.clone()) {
            continue;
        }
        let kind = normalize_resource_kind(&resource.kind);
        if kind.is_empty() {
            return Err(WorkspaceContentError::InvalidMetadata(
                "every external resource requires a kind".to_owned(),
            ));
        }
        resources.push(ArticleResource {
            kind,
            label: resource.label.trim().to_owned(),
            url,
        });
    }

    let image_author = attribution.image_author.trim().to_owned();
    let image_site_url = normalize_external_url("image site URL", &attribution.image_site_url)?;
    let resolved_mode = if mode.is_empty() { "off" } else { mode };
    if !matches!(resolved_mode, "off") && (image_author.is_empty() || image_site_url.is_empty()) {
        return Err(WorkspaceContentError::InvalidMetadata(
            "visible or metadata watermarks require both image_author and image_site_url"
                .to_owned(),
        ));
    }

    Ok(ArticleAttribution {
        project_name: attribution.project_name.trim().to_owned(),
        publication_venue: attribution.publication_venue.trim().to_owned(),
        project_url: normalize_external_url("project URL", &attribution.project_url)?,
        external_resources: resources,
        image_author,
        image_site_url,
        image_watermark_mode: resolved_mode.to_owned(),
        image_watermark_position: if position.is_empty() {
            "bottom-right".to_owned()
        } else {
            position.to_owned()
        },
    })
}

fn normalize_external_url(field: &str, value: &str) -> Result<String, WorkspaceContentError> {
    let value = value.trim();
    if value.is_empty() {
        return Ok(String::new());
    }
    let parsed = url::Url::parse(value).map_err(|error| {
        WorkspaceContentError::InvalidMetadata(format!("{field} `{value}` is invalid: {error}"))
    })?;
    if !matches!(parsed.scheme(), "http" | "https") {
        return Err(WorkspaceContentError::InvalidMetadata(format!(
            "{field} must use http or https"
        )));
    }
    Ok(parsed.to_string())
}

fn normalize_resource_kind(value: &str) -> String {
    let mut normalized = String::with_capacity(value.len());
    let mut separator = true;
    for ch in value.trim().chars() {
        if ch.is_ascii_alphanumeric() {
            normalized.push(ch.to_ascii_lowercase());
            separator = false;
        } else if !separator {
            normalized.push('-');
            separator = true;
        }
    }
    while normalized.ends_with('-') {
        normalized.pop();
    }
    normalized
}

fn yaml_text(key: &str, value: &str) -> (String, serde_yaml::Value) {
    (key.to_owned(), serde_yaml::Value::String(value.to_owned()))
}

fn article_attribution_yaml(attribution: &ArticleAttribution) -> Vec<(String, serde_yaml::Value)> {
    let resources = attribution
        .external_resources
        .iter()
        .map(|resource| {
            let mut record = serde_yaml::Mapping::new();
            for (key, value) in [
                ("kind", resource.kind.as_str()),
                ("label", resource.label.as_str()),
                ("url", resource.url.as_str()),
            ] {
                record.insert(
                    serde_yaml::Value::String(key.to_owned()),
                    serde_yaml::Value::String(value.to_owned()),
                );
            }
            serde_yaml::Value::Mapping(record)
        })
        .collect();
    vec![
        yaml_text("project_name", &attribution.project_name),
        yaml_text("publication_venue", &attribution.publication_venue),
        yaml_text("project_url", &attribution.project_url),
        (
            "external_resources".to_owned(),
            serde_yaml::Value::Sequence(resources),
        ),
        yaml_text("image_author", &attribution.image_author),
        yaml_text("image_site_url", &attribution.image_site_url),
        yaml_text("image_watermark_mode", &attribution.image_watermark_mode),
        yaml_text(
            "image_watermark_position",
            &attribution.image_watermark_position,
        ),
    ]
}

fn entry_map_json(fields: &BTreeMap<String, EntryValue>) -> serde_json::Value {
    serde_json::Value::Object(
        fields
            .iter()
            .map(|(name, value)| (name.clone(), entry_value_json(value)))
            .collect(),
    )
}

fn markdown_source(title: &str, body: &str) -> Result<String, WorkspaceContentError> {
    let title = title.trim();
    if title.is_empty() {
        return Err(WorkspaceContentError::InvalidTranslationId(
            "generated translation title is empty".to_owned(),
        ));
    }
    let body = body.trim();
    if body.is_empty() {
        return Err(WorkspaceContentError::InvalidTranslationId(
            "generated translation body is empty".to_owned(),
        ));
    }
    let mut frontmatter = serde_yaml::Mapping::new();
    frontmatter.insert(
        serde_yaml::Value::String("title".to_owned()),
        serde_yaml::Value::String(title.to_owned()),
    );
    let yaml =
        serde_yaml::to_string(&serde_yaml::Value::Mapping(frontmatter)).map_err(|error| {
            WorkspaceContentError::Edit(EditorError::Io {
                path: "generated translation".to_owned(),
                detail: format!("cannot serialize generated frontmatter: {error}"),
            })
        })?;
    Ok(format!("---\n{}\n---\n{}\n", yaml.trim_end(), body))
}

fn entry_value_json(value: &EntryValue) -> serde_json::Value {
    match value {
        EntryValue::Text(value) => serde_json::Value::String(value.clone()),
        EntryValue::Int(value) => serde_json::Value::from(*value),
        EntryValue::Float(value) => serde_json::Value::from(*value),
        EntryValue::Bool(value) => serde_json::Value::from(*value),
        EntryValue::List(values) => serde_json::Value::Array(
            values
                .iter()
                .cloned()
                .map(serde_json::Value::String)
                .collect(),
        ),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn repository_content() -> PathBuf {
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../content")
    }

    #[test]
    fn editable_workspace_uses_stable_source_identities() {
        let workspace = WorkspaceContent::open(repository_content()).expect("open content");
        let documents = workspace.editable_documents().expect("scan documents");
        assert!(!documents.is_empty());
        for document in documents {
            assert!(document.id.starts_with("i_"));
            for part in document.parts {
                assert!(part.id.starts_with("p_"));
                for translation in part.translations {
                    assert_eq!(
                        translation.id,
                        format!("{}:{}", part.id, translation.language)
                    );
                    assert!(!translation.source_path.contains("item_part"));
                }
            }
        }
    }

    #[test]
    fn episode_source_paths_include_the_series_container() {
        let workspace = WorkspaceContent::open(repository_content()).expect("open content");
        let episode = workspace
            .editable_documents()
            .expect("scan documents")
            .into_iter()
            .find(|document| document.content_type == "episode")
            .expect("episode fixture");
        let source = &episode.parts[0].translations[0].source_path;
        assert!(
            source.starts_with("resources/episode/using-silan-viking/"),
            "{source}"
        );
    }
}
