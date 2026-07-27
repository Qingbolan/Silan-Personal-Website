# VISION — Keep the Public Record Current

> A new research result should become an accurate public explanation before
> its context goes cold.

Silan Viking exists to shorten that update for the person who actually pays
the maintenance cost: an AI, ML, or systems researcher with a public body of
work to keep current. The current operator is comfortable with Markdown, Git,
Docker, and self-hosted tooling, but that is the current onboarding constraint.
The user need is broader: record one result, connect it to the right project
and résumé evidence, review every public claim, publish deliberately, deploy
explicitly, and verify what reached the web without rebuilding the website
workflow for every update.

This document describes the product direction and its non-negotiable
boundaries. The numbered documents under `docs/silan-viking/` describe the
implementation.

## 1. The Recurring Job

The product starts from one event:

- an experiment changes the conclusion;
- a paper is accepted;
- a benchmark, archive, or release provides stronger evidence;
- a project ships a meaningful milestone;
- a résumé claim becomes stale or gains proof.

The researcher does not want to rebuild a site or run a generic SEO program.
They want the current claim, evidence, uncertainty, and next step to be
findable by the people and machines that need an accurate explanation.

Today that update is fragmented across notes, an article draft, project page,
résumé, images, language variants, search metadata, deployment, and a fresh
Agent conversation. None of the steps is individually difficult. The setup
cost across all of them is enough to delay the public record, so the product
must reduce the repeated update roundtrip rather than optimize only the first
site setup.

## 2. The End State

Imagine a Friday afternoon after a useful result:

1. The researcher dictates the first accurate sentence while the evidence is
   still open.
2. The sentence becomes a dated moment with stable identity, not a disposable
   chat message.
3. A separate article explains what changed, what supports it, and what
   remains uncertain.
4. The article links to the project and the résumé evidence without forcing
   one paragraph to serve every reader.
5. An Agent can recover related records and prepare a maintenance proposal.
6. The researcher reviews the diff and decides what becomes public.
7. The system validates and deploys the reviewed state.
8. The researcher can see whether that content version reached the site and
   whether people or classified crawlers requested it.

The end state is not "a website that grows by itself" and not Generative
Engine Optimization (GEO) management as a dashboard label. It is a public
research record that is easier to keep honest than to neglect.

## 3. The Product Boundary

### Primary user

An AI, ML, or systems researcher, PhD student, or research engineer who:

- has several public research or engineering artifacts;
- updates work more than once a year;
- maintains a personal site, project pages, and résumé;
- can use Markdown, Git, Docker, and self-hosted infrastructure;
- cares whether search engines and answer engines can retrieve an accurate
  explanation.

### Public v1.0 release

- Rust CLI for macOS and Linux.
- Earlier `idea` / `update` content naming plus articles, projects, episodes,
  résumé, relations, proposals, indexing, site tooling, stats, and MCP.
- A clean workspace can create and validate a private article with ordinary
  files.

### Current main branch

- Versioned Markdown/TOML content source and rebuildable SQLite projection.
- Moments, articles, projects, episode series, media, and résumé data.
- Structured desktop editing, dictation, language variants, and publication
  state from a source checkout.
- Local preview and configured production deployment.
- Stable routes, metadata, sitemap, `llms.txt`, and structured data.
- Deployed-version checks, interaction data, and heuristic crawler
  attribution.
- MCP retrieval and reviewable change proposals.

The main-branch Moment/Desktop/onboarding capabilities are source-only until a
post-v1.0 release is published.

### Current limits

- Git is the practical cross-machine synchronization path.
- Packaged desktop onboarding is not yet the default installation experience.
- Search and AI signals measure machine reachability, not understanding,
  ranking, citation, or share of voice.
- `llms.txt`, structured data, and search/AI-readable text are discovery
  hygiene outputs. They are not a GEO dashboard or proof of answer-engine
  adoption.
- New workspaces need explicit hosting and deployment configuration.
- Agent proposals do not carry publication or production-deployment authority.

### Future directions

- Packaged desktop onboarding.
- Direct cross-device continuation without rebuilding context.
- ORCID, DOI, arXiv, BibTeX, and GitHub evidence import.
- Claim/evidence consistency checks across article, project, and résumé.
- External prompt, mention, citation, and answer-accuracy monitoring.

Future directions stay labeled as such until a user can complete them in a
clean workspace.

## 4. The Three Invariants

### 4.1 Authored truth remains inspectable

Markdown/TOML and media are the authored source. Databases, indexes, public
pages, and machine-readable files are derived and rebuildable.

**Failure prevented:** a public claim exists only in an opaque database or
interface and cannot be diffed, reviewed, or restored.

**Recovery:** rebuild derived state from the source commit.

### 4.2 Related records keep separate identities

A moment, article, project update, and résumé claim serve different readers.
They remain separate records connected by typed relationships.

**Failure prevented:** copy-pasted explanations drift while their provenance
disappears.

**Recovery:** follow stable identities and relations back to the evidence and
review the affected surfaces.

### 4.3 Authority is enforced by the workflow

An Agent may search, summarize, translate, and propose. Accepting source
changes, publishing content, and deploying production are distinct actions.

**Failure prevented:** a plausible draft silently becomes a public research
claim.

**Recovery:** reject or revert the proposal/source commit without changing the
deployed state.

## 5. What Makes the System Worth Building

The system is successful only if it improves a repeated user outcome:

- shorter time from fresh evidence to public explanation;
- fewer inconsistencies between article, project, résumé, and deployed page;
- visible evidence and uncertainty for public claims;
- zero private-content leaks;
- a clear next action when delivery or discovery fails;
- repeated use for the second and third update, not just the first site setup.

The initial benchmark is the **Research Update Roundtrip**:

```text
new evidence
  -> reviewed article/project/résumé changes
  -> machine-readable public output
  -> verified deployed version
```

Compare the time, inconsistency rate, evidence coverage, private leakage, and
deployment correctness against a manual Markdown/Git or CMS workflow.

## 6. Category Direction

The user-facing category is **local-first research publishing workspace**.
It names the job without asking a new user to understand the architecture.

The longer-term category hypothesis is **Research Presence OS**: a system of
record for a researcher's evidence, public claims, review history, and
deployed versions. `Personal Context System` remains the architectural
description for the linked source and Agent context underneath.

The larger category is not earned by adding features. It is earned if years
of update history create a trustworthy claim/evidence graph that is costly to
reconstruct elsewhere and useful to the researcher, readers, search systems,
and future Agents.

## 7. Decision Rule

Every product or architecture decision should answer:

> Does this make the next real research update easier to capture, explain,
> review, publish, and verify without weakening provenance or owner control?

If the answer is no, it is outside the current wedge even if the capability is
technically impressive.
