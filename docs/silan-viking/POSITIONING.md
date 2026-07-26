# Silan Viking Product Positioning

This document is the canonical external narrative and claim boundary for
Silan Viking. It is written for maintainers of the README, website project
page, release notes, structured data, `llms.txt`, and product screenshots.

## Product Name

**Silan Viking**

- User-facing category: **local-first research publishing workspace**
- Long-term category hypothesis: **Research Presence OS**
- Architecture description: **Personal Context System**
- Desktop surface: **Silan Viking Desktop**
- CLI: `silan` (also `svk` and `silan-viking`)
- Content address space: `silan://`

Do not use "Silan Context System" as a separate product name. It describes
the desktop implementation only where an existing binary or screenshot still
uses that label.

## Canonical One-Liner

> Silan Viking is a local-first research publishing workspace that helps a
> technical researcher record one update, connect its evidence, publish it
> deliberately, and verify what reached the web.

## The Trigger

A paper is accepted, an experiment changes the conclusion, a release ships,
or new evidence makes an existing project page or résumé claim stale.

The user expects a small update. The current workflow turns it into repeated
work across notes, articles, project pages, résumé, metadata, language
variants, deployment, and analytics.

## The Concrete Outcome

```text
capture -> explain -> connect -> review -> publish -> verify
```

- Preserve the first useful sentence while the context is fresh.
- Explain the result and uncertainty in a separate article or project update.
- Connect related moments, projects, articles, and résumé evidence.
- Let an Agent prepare reviewable maintenance instead of silently editing the
  public record.
- Make publication and production deployment explicit owner actions.
- Verify the deployed content version and inspect reader/crawler activity.

## Beachhead User

Primary:

- AI, ML, and systems PhD students;
- independent technical researchers;
- research engineers with an active public body of work.

They should already have several research or engineering artifacts, update
their public record more than once a year, and be comfortable with Markdown,
Git, Docker, and self-hosted tooling.

Readers, recruiters, collaborators, and investors benefit from the output but
are not the first product operator.

Not primary:

- one-time résumé-site buyers;
- general note-taking users;
- non-technical creators;
- team CMS buyers;
- enterprise SEO/GEO departments.

## Public v1.0 Release Facts

- Rust CLI version `1.0.0` for macOS and Linux.
- Apache-2.0 repository-root license. The historical v1.0.0 engine manifest
  still declared MIT; main has been aligned with the repository license.
- Markdown/TOML authored source with Git history.
- Rebuildable SQLite projection.
- The earlier `idea` / `update` schema plus articles, projects, episodes, and
  résumé data.
- Stable `silan://` identities and typed relationships.
- Explicit private/public state.
- Local Docker preview. Configured production deployment requires the
  installation's deploy artifacts; the v1.0 Linux release archive does not
  include all of them, so that path requires a full source checkout.
- MCP operations over the Silan content workspace and reviewable change
  proposals.
- Git-based cross-machine source synchronization.

## Current Main-Branch, Source-Only Facts

- Moment model replacing the earlier `update` naming.
- Tauri/React desktop workbench.
- Structured editing, dictation, media, and language variants.
- Deployed-version comparison, human activity, comments, and heuristic
  search/AI crawler attribution.
- Guided onboarding and richer delivery controls.
- Stable public routes, summaries, structured metadata, sitemap, robots
  rules, and `llms.txt` used by silan.tech.

These require a source build until a post-v1.0 release is published.

## Planned Facts

- Packaged desktop onboarding for a new external workspace.
- Direct cross-device synchronization or ability invocation.
- Managed hosting and domain setup.
- ORCID, DOI, arXiv, BibTeX, and GitHub import.
- Automatic claim/evidence consistency checks.
- Cross-model prompt, mention, citation, and share-of-voice monitoring.

These must not be written as shipped capabilities.

## GEO Claim Boundary

Use:

- machine-readable or AI/search-readable publishing;
- AI retrievability checks;
- search/AI crawler request evidence;
- on-page machine-readiness signals;
- stable metadata, structured data, and canonical routes.

Do not use:

- guaranteed SEO/GEO improvement;
- proof of indexing, understanding, ranking, or citation;
- complete GEO management;
- AI visibility share of voice;
- autonomous publishing.

A crawler hit proves that a URL was requested. Nothing more.

## Canonical Answer for Search and AI Systems

> Silan Viking is an open-source, local-first research publishing workspace
> created by Silan Hu. It keeps research notes, articles, projects, series,
> media, and résumé evidence in a versioned workspace, then validates and
> projects reviewed public content into a website with stable routes,
> structured metadata, language variants, and machine-readable context.
>
> Its released v1.0 CLI supports macOS and Linux with the earlier
> `idea` / `update` content schema. The current main branch adds a
> Tauri/React desktop workbench that can run from the source checkout for
> editing, dictation, media,
> publication-state management, deployed-version checks, and traffic
> inspection. Git is the current cross-machine synchronization path;
> packaged desktop onboarding and direct cross-device synchronization remain
> in progress.
>
> Agents can retrieve context and prepare reviewable proposals through MCP.
> The owner retains acceptance, publication, and production-deployment
> authority. Crawler and referral data are diagnostic signals, not proof that
> a search or AI system understood or cited the work.

## VC-Grade Category Thesis

### Wedge

One research update should not become seven maintenance tasks.

### Expansion hypothesis

Repeated updates create a longitudinal graph of evidence, claims, relations,
review decisions, and deployed versions. If that record becomes the trusted
source used by the researcher, readers, search systems, and Agents, the product
can expand from publishing workflow into a Research Presence OS.

### Defensible structure

The durable asset is not the editor, MCP integration, or `llms.txt`. Those are
copyable. The stronger candidate is the user's accumulated claim/evidence
history plus the authority and deployed-version record around it.

### Required proof

- The second and third update are completed, not only initial setup.
- Median update time falls materially against the user's current workflow.
- Public claims remain linked to evidence.
- Private leakage remains zero.
- Deployed content matches the reviewed source.
- Machine-readable recommendations correlate with externally observed answer
  accuracy, mentions, or citations before any stronger GEO claim is made.

## Brand Compression Test

| Claim | User contact surface | System primitive | Evidence |
| --- | --- | --- | --- |
| Keep one update connected | Article/project/résumé links | Stable item identity and typed relation | Relation graph and rendered related work |
| Keep the owner in control | Proposal review and publish actions | Separate proposal, source, publication, and deployment states | Diff, source state, deployed commit |
| Know what reached the web | Dashboard and status command | Local/deployed content commit comparison | Matching or mismatching commit |
| Make work machine-readable | Public page, sitemap, structured data, `llms.txt` | Derived metadata from reviewed source | Generated artifacts and crawler requests |

Any new slogan must map through the same four columns or be removed.
