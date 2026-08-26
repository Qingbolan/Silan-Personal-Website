# Silan Context System

![Silan Context System banner](../output/imagegen/silan-context-system-banner.png)

Standalone Tauri authoring application for the local `content/` workspace.
It is not part of the public React website and is not served by the Go
backend.

Silan Context System is the local desktop surface for managing personal
research, creator material, project history, and public publishing context.
It keeps authoring local: Markdown remains the source of truth, SQLite remains
a rebuildable read model, and the Rust engine owns validation, serialization,
and synchronization.

## Launch the compiled application

Install a release bundle once, then use the CLI from any configured project:

```bash
packaging/release/dev-install-local.sh --desktop-only --user-apps
silan desktop
```

The historical `destop` spelling remains an alias:

```bash
silan destop
```

Both commands refresh the local SQLite projection and launch the compiled
`Silan Context System.app`. The CLI injects the workspace paths and
`SILAN_VIKING_BIN` so desktop delivery actions call the same reviewed engine
binary that opened the app.

Workspace paths come from the nearest `silan-viking.toml`. In particular,
`[project].content_dir` may name a restored content repository such as
`silan.tech`; Desktop does not assume every device stores authored source in a
directory literally named `content`.

## Development session

The Tauri/Vite development server is explicit:

```bash
npm ci --prefix desktop
silan desktop dev
```

Do not run `npm run desktop` directly unless `SILAN_DESKTOP_CONTENT` and
`SILAN_DESKTOP_DB` are already set.

## Archived resources

Archiving keeps source files intact and removes the resource from active
shelves. The Settings → Archived resources view offers two explicit exits:
restore the resource privately, or permanently delete it after typing its
source coordinate (`slug`, or `series/slug` for an episode). Permanent deletion
is accepted only for archived resources with a current source revision and no
incoming content relations; the engine restores the source directory if the
SQLite projection cannot be rebuilt.

## OpenAI connection

Open the standalone **Settings** page from the gear button at the bottom of
the desktop sidebar. The AI connection section can verify and save a Platform
API key, test the stored credential, replace it, or remove it. The secret is
stored only in macOS Keychain; it is never written to the workspace, Tauri
state, logs, or frontend storage.

Translation uses the Responses API with strict structured output. The default
model is `gpt-5-nano` with minimal reasoning to keep routine translation costs
low; set `SILAN_OPENAI_TRANSLATION_MODEL` before launching the desktop process
only when the workspace needs an explicit model override.
Voice capture uses `gpt-4o-mini-transcribe`.

## macOS app bundle

The product name, window title, bundle name, executable name, and Dock name are
configured as **Silan Context System** in `src-tauri/tauri.conf.json`.

```bash
npm --prefix desktop run generate:icon
npm --prefix desktop run build:desktop -- --debug --bundles app --ci --no-sign
```

The debug app bundle is written to:

```text
desktop/src-tauri/target/debug/bundle/macos/Silan Context System.app
```

The app icon source is:

```text
desktop/src-tauri/icons/source/software-update-logo.png
```

`npm --prefix desktop run generate:icon` derives the Tauri icon set from that
source, including `icon.icns`, `icon.ico`, and `icon.png`.

## Data ownership

```text
content/**/*.md                 authoritative prose
        |
        | ContentEditor::save_markdown_and_sync
        v
Workspace::sync
        |
        v
_deploy/api/portfolio.db       local read store
        |- authored content tables (rebuildable projection)
        `- runtime tables (optional comments/interactions)
```

The Tauri adapter opens SQLite read-only. `ProjectionRepository` reads
rebuildable content metadata, while `RuntimeInsightsRepository` reads optional
traffic and comment tables. A newly synchronized database has no runtime
tables, which is represented as zero observations rather than a load error.

Editor bodies and revisions are always loaded from Markdown. Saving performs
an optimistic revision check, preserves YAML frontmatter, writes the source
atomically, and refreshes the projection. Saves are serialized inside the
engine. If projection fails, rollback occurs only while the just-written
source is still unchanged, so an external edit is never overwritten.

Structured Resume Parts remain TOML and are intentionally excluded from the
Markdown editor until a shape-specific structured editor exists.

## Development checks

```bash
npm --prefix desktop run build
cargo check --manifest-path desktop/src-tauri/Cargo.toml
cargo test --manifest-path desktop/src-tauri/Cargo.toml
cargo test --manifest-path engine/Cargo.toml -p silan-viking-app
```
