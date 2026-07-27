# 18 · DeepSeek reader-review workflow

## Purpose

The reader-review workflow detects reader-facing prose and Markdown reading
structure problems from several reader angles. It checks whether expert,
technical, research, adjacent-technical, and ordinary readers can understand
the claim, feel enough pull to continue, know how to act on it, and trust the
expression. It is diagnostic: it never rewrites authored Markdown or accepts a
suggestion.

The same application workflow serves the CLI and Silan Viking Desktop.
Provider calls, target discovery, failure handling, and report construction do
not belong to either presentation adapter.

## Fixed workflow

Every review follows the same state progression:

```text
target selected
  -> saved-source guard
  -> typed source discovery
  -> sequential DeepSeek review
  -> response validation and confidence filtering
  -> source-line resolution
  -> complete | partial_failure | failed report
  -> owner review
```

The workflow supports three concrete targets:

| Target | Source set |
|---|---|
| Current language | One saved Blog or episode Markdown translation |
| Complete Blog | Every Markdown part and language belonging to one Blog slug |
| Complete series | `series.toml` plus every Markdown part and language in one episode series |

The default provider configuration is:

```text
provider        deepseek
model           deepseek-v4-flash
min-confidence  0.80
thinking        disabled
output          structured JSON
```

An individual provider failure is recorded against its source path. Remaining
documents continue, and the terminal report becomes `partial_failure` or
`failed` instead of silently discarding completed work.

## Desktop contract

The content editor's document column exposes:

- **Current language** — reviews the selected saved translation.
- **Complete article** — reviews all parts and languages of the open Blog.
- **Complete series** — reviews the series metadata and every episode source.

Unsaved target files disable the corresponding action. This guarantees that
the source displayed in the report is the source sent to DeepSeek. After a
review, the document column shows either a pass mark or its finding count.
Opening the report shows four iteration scores, exact quotes, source lines,
category, severity, explanation, suggested repair, model, and confidence
threshold.

DeepSeek credentials are configured under **Workspace settings → AI
connection**. Desktop and CLI use the same stable macOS Keychain service and
account, so a key configured through either surface is immediately available
to the other.

## Authority and privacy

- Authored source is sent to DeepSeek only after the owner invokes a review.
- Credentials stay in the environment or macOS Keychain.
- Reports are advisory and do not mutate content.
- Suggestions require owner review before any edit or publication action.
