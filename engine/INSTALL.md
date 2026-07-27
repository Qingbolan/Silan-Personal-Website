# Installing Silan CLI

`silan` is the primary command for the Silan Viking research publishing
workspace.
`svk` is its compact alias, while `silan-viking` remains available for
compatibility. All three names execute the same binary.
(Engine developers: use `engine/install-dev.sh` to build from a checkout.)

## One-line install

```sh
curl -fsSL https://raw.githubusercontent.com/Qingbolan/Silan-Context-System/main/engine/install.sh | sh
```

This:

1. detects your OS and CPU architecture (macOS and Linux, Intel and ARM);
2. downloads the matching prebuilt binary from the project's GitHub Releases;
3. installs `silan-viking` and creates the `silan` / `svk` aliases;
4. tells you the next command to run.

If no prebuilt binary exists for your platform (or no release is published
yet), the script **falls back to building from source** with `cargo` — that
path needs the Rust toolchain ([rustup.rs](https://rustup.rs)).

### Options

The installer reads two environment variables:

```sh
# install somewhere other than ~/.local/bin
curl -fsSL .../install.sh | SILAN_INSTALL_DIR="$HOME/bin" sh

# pin a specific release tag instead of the latest
curl -fsSL .../install.sh | SILAN_VERSION="v0.1.0" sh
```

### Put it on your PATH

If the installer says `~/.local/bin is not on your PATH`, add this to your
shell profile (`~/.zshrc` or `~/.bashrc`) and restart the shell:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

## From zero to validated content

The public `v1.0.0` release can initialize, validate, index, and publish
Markdown-backed content. It uses the earlier `idea` / `update` naming. The
current main branch has since moved `update` to `moment` and added source-only
desktop/onboarding work; those post-release commands require a source build
until a newer release is published.

```sh
mkdir my-site && cd my-site

silan init                   # scaffold the project — ends by printing
                             # the next steps for you

silan guide                  # "what do I do now?" — re-run this anytime

silan index sync             # build the derived database from content/

silan blog new first-result  # create one private article
silan content lint
silan index sync
```

`init` lays down `content/`, `silan-viking.toml`, and `SCHEMA.md`. The exact
seed types follow the installed release. `guide` reads the project state and
points at the next compatible command.

Add a private article with `silan blog new <slug>`, then re-run
`content lint` and `index sync`. `silan --help` is the authority for the
installed binary's complete command surface.

## Configure a DeepSeek API key

On macOS, let the CLI verify the key with DeepSeek's read-only model-list
endpoint and store it in the current user's Keychain:

```sh
silan credentials deepseek set
silan credentials deepseek status
silan credentials deepseek test
```

`rotate` is an alias for `set`, and `remove` deletes the Keychain entry.
For CI and non-macOS systems, provide `DEEPSEEK_API_KEY`; environment
configuration takes precedence over Keychain storage:

```sh
export DEEPSEEK_API_KEY="<your-api-key>"
silan credentials deepseek test
```

The CLI never writes API keys to `silan-viking.toml`, workspace files, command
arguments, or output.

To review reader-facing Blog prose or a complete episode series for unnatural
phrasing, logical gaps, concept misuse, and odd terminology:

```sh
# All Blog language variants
silan blog language-check --report artifacts/blog-language-audit.json

# Every series, including series metadata and all episode language variants
silan episode series language-check \
  --report artifacts/series-language-audit.json

# One Blog or one series
silan blog language-check <slug>
silan episode series language-check <series>

# Raise or lower the default high-precision confidence threshold (0.80)
silan blog language-check --min-confidence 0.90
```

The default model is `deepseek-v4-flash`. Override it with `--model` or
`SILAN_DEEPSEEK_LANGUAGE_AUDIT_MODEL`. The default minimum confidence is
`0.80`; use `--min-confidence 0` to retain every model candidate. These
commands send the selected authored source to DeepSeek for read-only analysis;
they never modify source files or apply suggestions automatically.

## Uninstalling

```sh
silan uninstall                  # remove the skill + derived files,
                                 # keep your content/
silan uninstall --purge          # also delete content/ and the config
```

`uninstall` prints exactly what it will delete and asks for confirmation
first. It does not delete the `silan-viking` binary itself — remove that by
hand (e.g. `rm ~/.local/bin/silan-viking`).
