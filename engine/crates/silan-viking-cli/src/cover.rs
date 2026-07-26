//! CLI adapter for the source-backed cover workflow.

use crate::credentials;
use silan_viking_app::{
    CoverApplyState, CoverBrief, CoverGenerationInput, CoverTargetKind, CoverWorkspace,
    ImageOutputFormat, ImageQuality, ImageSize,
};
use std::path::Path;

pub fn find(content_root: &Path, args: &[&str]) -> Result<(), String> {
    let options = FindOptions::parse(args)?;
    let workspace = CoverWorkspace::open(content_root).map_err(|error| error.to_string())?;
    let targets = workspace
        .find_targets(&options.query, options.kind, Some(options.limit))
        .map_err(|error| error.to_string())?;
    if options.json {
        println!(
            "{}",
            serde_json::to_string_pretty(&targets).map_err(|error| error.to_string())?
        );
        return Ok(());
    }
    for target in targets {
        println!(
            "{}\t{}\t{}\t{}",
            target.kind.as_str(),
            target.uri,
            target.title,
            target.current_cover_uri.unwrap_or_else(|| "-".to_owned())
        );
    }
    Ok(())
}

pub fn generate(
    content_root: &Path,
    db_path: &Path,
    target_uri: &str,
    args: &[&str],
) -> Result<(), String> {
    let options = GenerateOptions::parse(args)?;
    let workspace = CoverWorkspace::open(content_root).map_err(|error| error.to_string())?;
    let target = workspace
        .target(target_uri)
        .map_err(|error| error.to_string())?;
    let mut brief = CoverBrief::from_target(&target);
    if let Some(value) = options.language {
        brief.set_language(target.kind, value);
    }
    if let Some(value) = options.headline {
        brief.headline = value;
    }
    if let Some(value) = options.audience {
        brief.audience = value;
    }
    if let Some(value) = options.value {
        brief.value = value;
    }
    if let Some(value) = options.visual_direction {
        brief.visual_direction = value;
    }
    let prompt = options
        .prompt_override
        .as_deref()
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .map(str::to_owned)
        .unwrap_or_else(|| brief.xhs_editorial_prompt(target.kind, options.size));

    if options.dry_run {
        if options.json {
            println!(
                "{}",
                serde_json::to_string_pretty(&serde_json::json!({
                    "target": target,
                    "asset_directory_uri": format!("{target_uri}/assets/"),
                    "apply": options.apply,
                    "size": options.size_value,
                    "quality": options.quality_value,
                    "output_format": options.output_format_value,
                    "prompt": prompt,
                }))
                .map_err(|error| error.to_string())?
            );
        } else {
            println!("target={target_uri}");
            println!("asset_directory_uri={target_uri}/assets/");
            println!("apply={}", options.apply);
            println!("prompt:\n{prompt}");
        }
        return Ok(());
    }

    let api_key = credentials::openai_api_key()?;
    let result = workspace
        .generate_cover(
            &api_key,
            &CoverGenerationInput {
                target_uri: target_uri.to_owned(),
                brief,
                prompt_override: Some(prompt),
                size: options.size,
                quality: options.quality,
                output_format: options.output_format,
                apply: options.apply,
            },
            db_path,
        )
        .map_err(|error| error.to_string())?;
    if options.json {
        println!(
            "{}",
            serde_json::to_string_pretty(&result).map_err(|error| error.to_string())?
        );
    } else {
        println!("target={}", result.target.uri);
        println!("asset={}", result.asset.uri);
        println!("path={}", result.asset.relative_path);
        println!(
            "state={}",
            match result.state {
                CoverApplyState::Candidate => "candidate",
                CoverApplyState::Applied => "applied",
            }
        );
    }
    Ok(())
}

struct FindOptions {
    query: String,
    kind: Option<CoverTargetKind>,
    limit: usize,
    json: bool,
}

impl FindOptions {
    fn parse(args: &[&str]) -> Result<Self, String> {
        let mut query = Vec::new();
        let mut kind = None;
        let mut limit = 20usize;
        let mut json = false;
        let mut index = 0;
        while index < args.len() {
            match args[index] {
                "--type" => {
                    index += 1;
                    kind = Some(
                        CoverTargetKind::parse(
                            args.get(index)
                                .ok_or("cover find --type requires a value")?,
                        )
                        .map_err(|error| error.to_string())?,
                    );
                }
                value if value.starts_with("--type=") => {
                    kind = Some(
                        CoverTargetKind::parse(value.trim_start_matches("--type="))
                            .map_err(|error| error.to_string())?,
                    );
                }
                "--limit" => {
                    index += 1;
                    limit = parse_limit(
                        args.get(index)
                            .ok_or("cover find --limit requires a value")?,
                    )?;
                }
                value if value.starts_with("--limit=") => {
                    limit = parse_limit(value.trim_start_matches("--limit="))?;
                }
                "--json" => json = true,
                value if value.starts_with('-') => {
                    return Err(format!("unknown cover find flag `{value}`"));
                }
                value => query.push(value),
            }
            index += 1;
        }
        Ok(Self {
            query: query.join(" "),
            kind,
            limit,
            json,
        })
    }
}

struct GenerateOptions {
    language: Option<String>,
    headline: Option<String>,
    audience: Option<String>,
    value: Option<String>,
    visual_direction: Option<String>,
    prompt_override: Option<String>,
    size: ImageSize,
    size_value: String,
    quality: ImageQuality,
    quality_value: String,
    output_format: ImageOutputFormat,
    output_format_value: String,
    apply: bool,
    dry_run: bool,
    json: bool,
}

impl GenerateOptions {
    fn parse(args: &[&str]) -> Result<Self, String> {
        let mut options = Self {
            language: None,
            headline: None,
            audience: None,
            value: None,
            visual_direction: None,
            prompt_override: None,
            size: ImageSize::Landscape1536x1024,
            size_value: "1536x1024".to_owned(),
            quality: ImageQuality::Medium,
            quality_value: "medium".to_owned(),
            output_format: ImageOutputFormat::Png,
            output_format_value: "png".to_owned(),
            apply: true,
            dry_run: false,
            json: false,
        };
        let mut index = 0;
        while index < args.len() {
            let flag = args[index];
            match flag {
                "--language" => {
                    options.language = Some(next_value(args, &mut index, flag)?.to_owned())
                }
                "--headline" => {
                    options.headline = Some(next_value(args, &mut index, flag)?.to_owned())
                }
                "--audience" => {
                    options.audience = Some(next_value(args, &mut index, flag)?.to_owned())
                }
                "--value" => options.value = Some(next_value(args, &mut index, flag)?.to_owned()),
                "--visual" => {
                    options.visual_direction = Some(next_value(args, &mut index, flag)?.to_owned())
                }
                "--prompt" => {
                    options.prompt_override = Some(next_value(args, &mut index, flag)?.to_owned())
                }
                "--size" => {
                    let value = normalize_size(next_value(args, &mut index, flag)?)?;
                    options.size = ImageSize::parse(value).map_err(|error| error.to_string())?;
                    options.size_value = value.to_owned();
                }
                "--quality" => {
                    let value = next_value(args, &mut index, flag)?;
                    options.quality =
                        ImageQuality::parse(value).map_err(|error| error.to_string())?;
                    options.quality_value = value.to_owned();
                }
                "--format" => {
                    let value = next_value(args, &mut index, flag)?;
                    options.output_format =
                        ImageOutputFormat::parse(value).map_err(|error| error.to_string())?;
                    options.output_format_value = value.to_owned();
                }
                "--apply" => options.apply = true,
                "--no-apply" => options.apply = false,
                "--dry-run" => options.dry_run = true,
                "--json" => options.json = true,
                value => return Err(format!("unknown cover generate flag `{value}`")),
            }
            index += 1;
        }
        Ok(options)
    }
}

fn next_value<'a>(args: &'a [&str], index: &mut usize, flag: &str) -> Result<&'a str, String> {
    *index += 1;
    args.get(*index)
        .copied()
        .ok_or_else(|| format!("cover generate {flag} requires a value"))
}

fn parse_limit(value: &str) -> Result<usize, String> {
    let value = value
        .parse::<usize>()
        .map_err(|_| format!("invalid cover result limit `{value}`"))?;
    if (1..=100).contains(&value) {
        Ok(value)
    } else {
        Err("cover result limit must be between 1 and 100".to_owned())
    }
}

fn normalize_size(value: &str) -> Result<&str, String> {
    match value {
        "wide" | "landscape" | "1536x1024" => Ok("1536x1024"),
        "portrait" | "1024x1536" => Ok("1024x1536"),
        "square" | "1024x1024" => Ok("1024x1024"),
        other => Err(format!(
            "unsupported cover size `{other}`; expected wide, portrait, square, or an OpenAI pixel size"
        )),
    }
}
