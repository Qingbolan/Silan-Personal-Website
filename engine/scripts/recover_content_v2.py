#!/usr/bin/env python3
"""Recover a source content tree from a legacy v2 release projection.

Bundle v2 archived the complete public SQLite projection and media, but not
the authoring tree.  This migration reconstructs the projection-equivalent
source while preserving Item/Part/Entry identities and source timestamps.
New bundle versions carry ``source.tar`` and do not need this migration.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sqlite3
from collections.abc import Iterable, Mapping
from pathlib import Path
from urllib.parse import unquote


MEDIA_URL = re.compile(r"/api/v1/media\?f=([^&)\s]+)&v=[0-9a-f]+")
TYPE_LAYOUT = {
    "blog": ("blog_posts", "blog_post_translations", "blog_post_id"),
    "project": ("projects", "project_translations", "project_id"),
    "episode": ("episodes", "episode_translations", "episode_id"),
    "moment": ("moments", "moment_translations", "moment_id"),
}
TYPE_DIR = {
    "blog": "blog",
    "project": "projects",
    "episode": "episode",
    "moment": "moment",
}
TRANSLATABLE_FIELDS = {
    "blog": ("title", "excerpt", "featured_image_url"),
    "project": ("title", "description"),
    "episode": ("title",),
    "moment": ("title",),
}
MAIN_FIELDS = {
    "blog": (
        "slug",
        "content_type",
        "status",
        "visibility",
        "is_featured",
        "published_at",
        "category_id",
        "series_id",
        "series_order",
        "project_name",
        "publication_venue",
        "project_url",
        "external_resources",
    ),
    "project": (
        "slug",
        "status",
        "visibility",
        "project_type",
        "start_date",
        "end_date",
        "is_featured",
        "github_url",
        "demo_url",
        "documentation_url",
        "thumbnail_url",
        "cover_source_type",
        "cover_website_url",
    ),
    "episode": (
        "slug",
        "series_id",
        "episode_number",
        "status",
        "visibility",
        "published_at",
        "duration_minutes",
    ),
    "moment": (
        "slug",
        "moment_type",
        "status",
        "priority",
        "visibility",
        "date",
    ),
}
SOURCE_NAMES = {
    "category_id": "category",
    "series_id": "series",
}


class RecoveryError(RuntimeError):
    """The legacy release cannot be reconstructed safely."""


class ProjectionRecovery:
    """Projection-to-source migration for a durable bundle v2 release."""

    def __init__(self, database: Path, media: Path, schema: Path) -> None:
        self.database = database.resolve()
        self.media = media.resolve()
        self.schema = schema.resolve()
        self.connection = sqlite3.connect(f"file:{self.database}?mode=ro", uri=True)
        self.connection.row_factory = sqlite3.Row

    def recover(self, destination: Path) -> None:
        destination = destination.resolve()
        self._require_safe_destination(destination)
        destination.mkdir(parents=True)
        shutil.copy2(self.schema, destination / "SCHEMA.md")
        (destination / ".gitignore").write_text(".DS_Store\n.viking/\n", encoding="utf-8")
        private_namespace = destination / "agent"
        private_namespace.mkdir()
        (private_namespace / ".gitkeep").write_text("", encoding="utf-8")
        resources = destination / "resources"
        shutil.copytree(self.media, resources)
        self._recover_series(resources)
        for kind in TYPE_LAYOUT:
            self._recover_prose_type(resources, kind)
        self._recover_resume(resources)

    def _recover_series(self, resources: Path) -> None:
        rows = self.connection.execute(
            "SELECT id, slug, title, description, cover_url, status FROM episode_series ORDER BY slug"
        )
        for row in rows:
            series_dir = resources / "episode" / row["slug"]
            series_dir.mkdir(parents=True, exist_ok=True)
            values = {
                "title": row["title"],
                "slug": row["slug"],
                "description": self._source_reference(row["description"]),
                "cover_url": self._source_reference(row["cover_url"]),
                "status": row["status"],
            }
            self._write_toml_table(series_dir / "series.toml", values)

    def _recover_prose_type(self, resources: Path, kind: str) -> None:
        table, _, _ = TYPE_LAYOUT[kind]
        rows = self.connection.execute(f"SELECT * FROM {table} ORDER BY slug")
        for row in rows:
            item_dir = self._item_dir(resources, kind, row)
            item_dir.mkdir(parents=True, exist_ok=True)
            self._write_toml_table(item_dir / "item.toml", {"item_id": row["id"]})
            frontmatter_by_lang = self._frontmatter(kind, row)
            parts = self.connection.execute(
                "SELECT * FROM item_part WHERE entity_type = ? AND entity_id = ? ORDER BY sort_order",
                (kind, row["id"]),
            ).fetchall()
            for part_index, part in enumerate(parts):
                part_dir = item_dir / "parts" / part["role"]
                part_dir.mkdir(parents=True, exist_ok=True)
                self._write_toml_table(
                    part_dir / "meta.toml",
                    {
                        "part_id": part["part_id"],
                        "type": part["role"],
                        "shape": "prose",
                        "canonical_lang": part["canonical_lang"],
                    },
                )
                translations = self.connection.execute(
                    "SELECT language_code, body FROM item_part_translation "
                    "WHERE item_part_id = ? ORDER BY language_code",
                    (part["id"],),
                ).fetchall()
                for translation in translations:
                    language = translation["language_code"]
                    frontmatter = frontmatter_by_lang.get(language, {}) if part_index == 0 else {}
                    body = self._source_reference(translation["body"] or "")
                    self._write_markdown(part_dir / f"{language}.md", frontmatter, body)
            self._set_item_timestamp(item_dir, row["created_at"])

    def _item_dir(self, resources: Path, kind: str, row: sqlite3.Row) -> Path:
        if kind == "episode":
            series_slug = self.connection.execute(
                "SELECT slug FROM episode_series WHERE id = ?", (row["series_id"],)
            ).fetchone()
            if series_slug is None:
                raise RecoveryError(f"episode {row['slug']} references a missing series")
            return resources / "episode" / series_slug["slug"] / row["slug"]
        return resources / TYPE_DIR[kind] / row["slug"]

    def _frontmatter(self, kind: str, row: sqlite3.Row) -> dict[str, dict[str, object]]:
        _, translation_table, foreign_key = TYPE_LAYOUT[kind]
        translations = self.connection.execute(
            f"SELECT * FROM {translation_table} WHERE {foreign_key} = ? ORDER BY language_code",
            (row["id"],),
        ).fetchall()
        output: dict[str, dict[str, object]] = {}
        for translation in translations:
            language = translation["language_code"]
            localized = {
                field: self._source_reference(translation[field])
                for field in TRANSLATABLE_FIELDS[kind]
                if field in translation.keys() and translation[field] is not None
            }
            output[language] = localized
        canonical = output.setdefault("en", {})
        canonical["kind"] = kind
        for field in MAIN_FIELDS[kind]:
            if field not in row.keys() or row[field] is None:
                continue
            name = SOURCE_NAMES.get(field, field)
            value: object = row[field]
            if field == "external_resources":
                value = json.loads(value) if value else []
            if field in {"is_featured"}:
                value = bool(value)
            canonical[name] = self._source_reference(value)
        tags = [
            tag["slug"]
            for tag in self.connection.execute(
                "SELECT t.slug FROM content_tag ct JOIN tag t ON t.id = ct.tag_id "
                "WHERE ct.entity_type = ? AND ct.entity_id = ? ORDER BY ct.id",
                (kind, row["id"]),
            )
        ]
        if tags:
            canonical["tags"] = tags
        relations = []
        for relation in self.connection.execute(
            "SELECT to_type, to_id, relation_type FROM content_relation "
            "WHERE from_type = ? AND from_id = ? ORDER BY COALESCE(sort_order, 0), id",
            (kind, row["slug"]),
        ):
            target_dir = TYPE_DIR.get(relation["to_type"], relation["to_type"])
            relations.append(
                {
                    "type": relation["relation_type"],
                    "to": f"silan://resources/{target_dir}/{relation['to_id']}",
                }
            )
        if relations:
            canonical["relations"] = relations
        if kind == "project":
            detail = self.connection.execute(
                "SELECT license, version FROM project_details WHERE project_id = ?", (row["id"],)
            ).fetchone()
            if detail:
                for field in ("license", "version"):
                    if detail[field] is not None:
                        canonical[field] = detail[field]
        return output

    def _recover_resume(self, resources: Path) -> None:
        personal = self.connection.execute("SELECT * FROM personal_info LIMIT 1").fetchone()
        if personal is None:
            return
        item_dir = resources / "resume"
        item_dir.mkdir(parents=True, exist_ok=True)
        self._write_toml_table(item_dir / "item.toml", {"item_id": personal["id"]})
        parts = self.connection.execute(
            "SELECT * FROM item_part WHERE entity_type = 'resume' ORDER BY sort_order"
        ).fetchall()
        personal_translations = {
            row["language_code"]: row
            for row in self.connection.execute(
                "SELECT * FROM personal_info_translations WHERE personal_info_id = ? ORDER BY language_code",
                (personal["id"],),
            )
        }
        for part in parts:
            role = part["role"]
            shape = self._resume_shape(role)
            part_dir = item_dir / "parts" / role
            part_dir.mkdir(parents=True, exist_ok=True)
            self._write_toml_table(
                part_dir / "meta.toml",
                {
                    "part_id": part["part_id"],
                    "type": role,
                    "shape": shape,
                    "canonical_lang": part["canonical_lang"],
                },
            )
            if role == "summary":
                bodies = self.connection.execute(
                    "SELECT language_code, body FROM item_part_translation "
                    "WHERE item_part_id = ? ORDER BY language_code",
                    (part["id"],),
                )
                for body in bodies:
                    language = body["language_code"]
                    translation = personal_translations.get(language)
                    frontmatter: dict[str, object] = {}
                    if translation:
                        for field in ("full_name", "title", "current_status"):
                            if translation[field] is not None:
                                frontmatter[field] = translation[field]
                    if language == part["canonical_lang"]:
                        frontmatter["kind"] = "resume"
                        frontmatter["visibility"] = "public"
                        for field in ("email", "phone", "location", "website", "avatar_url"):
                            if personal[field] is not None:
                                frontmatter[field] = self._source_reference(personal[field])
                        links = [
                            {
                                key: link[key]
                                for key in ("platform", "url", "display_name")
                                if link[key] is not None
                            }
                            for link in self.connection.execute(
                                "SELECT * FROM social_links WHERE personal_info_id = ? ORDER BY sort_order",
                                (personal["id"],),
                            )
                        ]
                        if links:
                            frontmatter["social_links"] = links
                    self._write_markdown(
                        part_dir / f"{language}.md",
                        frontmatter,
                        self._source_reference(body["body"] or ""),
                    )
            elif role == "overview":
                # Legacy sources could carry an identity-only open Part.
                (part_dir / f"{part['canonical_lang']}.md").write_text("", encoding="utf-8")
            else:
                self._recover_resume_entries(part_dir, part["id"])

    def _recover_resume_entries(self, part_dir: Path, part_id: str) -> None:
        shared_entries = self.connection.execute(
            "SELECT entry_id, sort_order, shared_payload FROM part_entry "
            "WHERE item_part_id = ? ORDER BY sort_order",
            (part_id,),
        ).fetchall()
        languages = [
            row[0]
            for row in self.connection.execute(
                "SELECT DISTINCT pet.language_code FROM part_entry_translation pet "
                "JOIN part_entry pe ON pe.entry_id = pet.part_entry_id "
                "WHERE pe.item_part_id = ? ORDER BY pet.language_code",
                (part_id,),
            )
        ]
        for language in languages:
            entries = []
            for shared in shared_entries:
                localized = self.connection.execute(
                    "SELECT localized_payload FROM part_entry_translation "
                    "WHERE part_entry_id = ? AND language_code = ?",
                    (shared["entry_id"], language),
                ).fetchone()
                if localized is None:
                    continue
                values = {"entry_id": shared["entry_id"]}
                values.update(json.loads(shared["shared_payload"]))
                values.update(json.loads(localized["localized_payload"]))
                entries.append(self._source_reference(values))
            self._write_entry_list(part_dir / f"{language}.toml", entries)

    @staticmethod
    def _resume_shape(role: str) -> str:
        if role in {"summary", "overview"}:
            return "prose"
        if role == "skills":
            return "key_value_list"
        return "entry_list"

    @staticmethod
    def _write_markdown(path: Path, frontmatter: Mapping[str, object], body: str) -> None:
        if not frontmatter:
            path.write_text(body, encoding="utf-8")
            return
        lines = ["---"]
        lines.extend(ProjectionRecovery._yaml_lines(frontmatter))
        lines.extend(["---", body])
        path.write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _yaml_lines(values: Mapping[str, object], indent: int = 0) -> list[str]:
        lines = []
        prefix = " " * indent
        for key, value in values.items():
            if isinstance(value, list) and value and all(isinstance(entry, dict) for entry in value):
                lines.append(f"{prefix}{key}:")
                for entry in value:
                    lines.append(f"{prefix}  - {json.dumps(entry, ensure_ascii=False)}")
            else:
                lines.append(f"{prefix}{key}: {json.dumps(value, ensure_ascii=False)}")
        return lines

    @staticmethod
    def _write_toml_table(path: Path, values: Mapping[str, object]) -> None:
        lines = [f"{key} = {ProjectionRecovery._toml_value(value)}" for key, value in values.items() if value is not None]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def _write_entry_list(path: Path, entries: Iterable[Mapping[str, object]]) -> None:
        lines: list[str] = []
        for entry in entries:
            if lines:
                lines.append("")
            lines.append("[[entry]]")
            lines.extend(f"{key} = {ProjectionRecovery._toml_value(value)}" for key, value in entry.items())
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    @staticmethod
    def _toml_value(value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return repr(value)
        return json.dumps(value, ensure_ascii=False)

    @classmethod
    def _source_reference(cls, value: object) -> object:
        if isinstance(value, str):
            return MEDIA_URL.sub(
                lambda found: f"silan://resources/{unquote(found.group(1))}", value
            )
        if isinstance(value, list):
            return [cls._source_reference(entry) for entry in value]
        if isinstance(value, dict):
            return {key: cls._source_reference(entry) for key, entry in value.items()}
        return value

    @staticmethod
    def _set_item_timestamp(item_dir: Path, value: str | None) -> None:
        if not value:
            return
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        nanoseconds = int(parsed.timestamp() * 1_000_000_000)
        os.utime(item_dir, ns=(nanoseconds, nanoseconds))

    @staticmethod
    def _require_safe_destination(destination: Path) -> None:
        if destination.exists() and any(destination.iterdir()):
            raise RecoveryError(f"destination is not empty: {destination}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--media", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--to", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ProjectionRecovery(args.database, args.media, args.schema).recover(args.to)


if __name__ == "__main__":
    main()
