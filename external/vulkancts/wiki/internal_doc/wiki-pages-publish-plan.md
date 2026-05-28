# Wiki Pages Publish Plan

## Background

All Vulkan CTS wiki pages were created locally under `external/vulkancts/wiki/` using the
[wiki-analyzer](../../../../.agents/skills/wiki-analyzer/SKILL.md) skill. The wiki content
is complete for all existing test categories. The next goal is to publish these local markdown
files as actual wiki pages on a remote Git hosting platform so they are browsable alongside
the repository.

### Repository Setup

The project has two remotes:

| Remote | Host | Purpose |
|--------|------|---------|
| GitHub (public fork) | `github.com` | Synchronizes upstream source changes from the official Khronos Group repo |
| GitLab (private internal) | `gitlab.com` | Hosts the wiki pages |

Wiki pages will be published to the **GitLab** remote only. No dual-compatible link scheme is
needed. The GitLab project URL used for source-code links is:

```text
https://sh-code.mthreads.com/haoxuan.wang/vulkan-cts-wiki
```

The GitLab source repository default branch has been changed from `main` to `vkcts-wiki`, which is
the primary wiki development branch. Published source-code links should use this branch by default so
readers see the latest wiki pages together with the latest codebase.

### Wiki Repo Clone Status

The GitLab wiki repository has been initialized through the Web UI with a `Home` page. It is cloned
at the workspace root as:

```text
vkcts-wiki-pages/
```

This directory is the local clone of the separate wiki repo (`REPO.wiki.git`) and is a publish target
only. It must not be treated as the canonical English wiki source.

The GitLab Wiki Web UI displays content from the wiki repo's `master` branch. The local wiki repo
clone is therefore kept on `master` and tracks `origin/master`. All publish-target changes should be
made on `master`.

### Current Wiki Structure

```text
external/vulkancts/wiki/
├── README.md                                   # Navigation entry point
├── Vulkan_CTS_Framework_and_Mechanism.md       # Framework overview
├── Objectives.md                               # Wiki objectives
├── categories/                                 # Level-2 category pages (53 files)
│   ├── api.md
│   ├── pipeline.md
│   └── ...
├── testfiles/                                  # Level-3 source-file pages (~300+ files)
│   ├── api/
│   ├── draw/
│   └── ...
└── internal_doc/                               # Process-internal docs (not for publishing)
    ├── merge_update_log.md
    └── wiki-pages-publish-plan.md              # This file
```

## Key Decisions

### Decision 1: Model A — Local Wiki is Canonical, Wiki Repo is a Publish Target

After evaluating two models, we chose **Model A**: the local `external/vulkancts/wiki/`
directory remains the single canonical source of wiki content, and the GitLab wiki repo
serves as a publish target only.

**Why not Model B (wiki repo as canonical, mounted as submodule)?**

Model B would require the wiki directory to be a git submodule pointing to the GitLab wiki
repo, with all source-code links written as absolute GitLab URLs from the start. This breaks
the evidence-based authoring workflow in several ways:

1. **Agent authoring loop breaks.** The `wiki-analyzer` skill assumes the agent can read
   source code at relative paths like `../../../modules/vulkan/...` and write wiki pages
   that link back with relative URLs. Absolute URLs would make local markdown preview
   non-functional for source-code links.

2. **Validation scripts break.** `validate_wiki_links.py` resolves relative URLs against
   the local filesystem. It would need significant rewrites to handle absolute GitLab URLs
   by mapping them back to local paths.

3. **Sync workflow becomes complex.** The `vkcts-wiki-sync` skill manages wiki updates as
   ordinary files in the main repo's branch lifecycle (integration branches, merge commits,
   etc.). A submodule adds two-git-history coordination at every step — committing inside
   the submodule, then updating the submodule pointer in the main repo.

4. **Submodule overhead is ongoing.** Every wiki edit requires a commit+push inside the
   submodule, then a separate commit+push to update the submodule pointer in the main repo.
   This is tedious and error-prone for a workflow where wiki edits are frequent and
   agent-driven.

**What Model A preserves:**

- All existing skills (`wiki-analyzer`, `vkcts-wiki-sync`) work unchanged.
- Relative URLs work in local markdown preview.
- Validation scripts work unchanged.
- The sync workflow (integration branches, merge commits) works as designed.
- The publish step is a clean, automatable pipeline.

### Decision 2: Bilingual Wiki — English Local, Mandarin Chinese on GitLab

The local wiki files are written in English and will remain in English as the canonical
source. The GitLab wiki pages will be written in **Mandarin Chinese**. This means each
published wiki page is a translated version of the corresponding local English page, with
source-code links converted to absolute GitLab URLs.

This decision strongly reinforces Model A: the local English wiki stays as the
evidence-based authoring source, and the GitLab Chinese wiki is a derived publish target.
Translation is a one-way transformation applied during the publish step, just like the
URL transformation. Keeping two language versions in the same repo would create
maintenance burden; keeping them in separate repos with a clear canonical/derived
relationship is cleaner.

### Decision 3: GitLab Wiki Pages are Generated Artifacts

GitLab wiki pages are generated publish artifacts, not an editing source. The wiki pages repo
will be write-protected to prevent direct edits from the GitLab Web UI or other ad-hoc paths.

Reader feedback should flow through issues:

1. A reader reports an error or improvement request as an issue.
2. The English local canonical wiki is updated first under `external/vulkancts/wiki/`.
3. Existing local validation and evidence review are run against the canonical source.
4. The corrected English wiki is translated and propagated to the Chinese GitLab wiki pages.

This intentionally removes routine reverse sync from the workflow. Reverse reconciliation is an
exception path only, for example if an administrator accidentally bypasses protection or an
emergency hotfix must be recovered. Normal maintenance never starts from the GitLab wiki pages.

### Decision 4: Source-Code Links Must Be Converted to Absolute URLs

The wiki files contain two categories of relative links:

| Link type | Example | Works in wiki repo? | Fix |
|-----------|---------|---------------------|-----|
| Wiki → source code | `../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L1` | **Not tested yet** — wiki repo has no source tree | Convert to absolute GitLab URLs |
| Wiki → mustpass/source-adjacent docs | `../mustpass/main/vk-default/renderpasses.txt` | **Not tested yet** — wiki repo has no mustpass/doc/source tree | Convert to absolute GitLab URLs if it points outside the wiki publish tree |
| Wiki → wiki (same dir) | `Vulkan_CTS_Framework_and_Mechanism.md` | **Works after dropping `.md`** | Publish target should be `Vulkan_CTS_Framework_and_Mechanism` |
| Wiki → wiki (cross-dir) | `categories/info.md` | **Works after dropping `.md`** | Publish target should be `categories/info` |

The source-code link transformation is mechanical and deterministic:

```text
Before (local relative):
../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L446-L1256

After (absolute GitLab URL):
https://sh-code.mthreads.com/haoxuan.wang/vulkan-cts-wiki/-/blob/vkcts-wiki/external/vulkancts/modules/vulkan/ubo/vktUniformBlockTests.cpp#L446-L1256
```

The URL builder must be configurable rather than hardcoding most repository details:

- `GITLAB_PROJECT_URL`: `https://sh-code.mthreads.com/haoxuan.wang/vulkan-cts-wiki`.
- `SOURCE_REF`: branch/tag/commit used in source-code URLs. Default decision: `vkcts-wiki` branch.
- `SOURCE_ROOT_PREFIX`: repository-relative prefix used when forming blob URLs.

The default branch-based `SOURCE_REF` is intentional: readers should see latest wiki pages plus
latest codebase. A commit SHA or tag can still be supported later if a frozen snapshot publish is
needed.

This transformation will be implemented as part of a future **wiki-publisher** skill. The link
transformation should be scriptable and repeatable for one markdown file, one category, or the full
publish set. It should not mutate the English canonical wiki; it operates on translated files in the
wiki repo publish target.

The script's core responsibility:

- Accept one or more `.md` file paths, a category name, or the wiki repo publish tree.
- Resolve relative links against the owning markdown file's directory.
- Identify repo-local links that point outside the wiki publish tree, including but not limited to
  `external/vulkancts/modules/`, `external/vulkancts/mustpass/`, `doc/`, and `framework/`.
- Rewrite those repo-local non-wiki links to absolute GitLab blob URLs using the configured base URL
  and `SOURCE_REF`.
- Preserve GitHub/GitLab-style line fragments such as `#L82` and `#L82-L95`.
- Convert inter-wiki markdown page links by removing the `.md` suffix from the link target, while
  preserving directory paths and heading fragments when present.
- Update translated files in the wiki repo publish tree in place, not in the canonical English wiki.

### Decision 5: Wiki Repo is Separate, Not a Submodule

Per GitHub and GitLab design, wiki pages live in a separate Git repository
(`REPO.wiki.git`). The wiki repo and the primary repo share no Git history. The only
connection is the platform-level link (the "Wiki" tab on the project page).

We will **not** add the wiki repo as a git submodule of the primary repo. The overhead
(submodule pointer updates, two-repo coordination) outweighs the benefit for our workflow.
Instead, the wiki repo is cloned to a separate location and used only during the publish
step.

### Decision 6: Translation Invariants

The Mandarin Chinese GitLab wiki is translated for readability, but translation must preserve
technical identifiers and machine-checkable structure. The exact glossary can evolve as problematic
translations are discovered, but the first version of the rules should preserve the following:

- Code blocks.
- Inline code spans.
- Markdown link targets, except when the link transformer changes them.
- Source filenames, paths, symbols, enum names, struct names, function names, test names, and
  registered path components.
- `#Lx` and `#Lx-Ly` line fragments.
- Parseable registration hierarchy trees, including registered child names and Unicode tree markers.
- GPU and Vulkan concepts/identifiers that readers commonly know by English names, such as `VS`,
  `Vertex Shader`, `device`, queue, pipeline, descriptor, render pass, shader, image, buffer, and
  similar domain terms.

The translation rules should remain adjustable. If generated Chinese wiki pages translate a term in
a way that is awkward or less familiar than the English term, that term should be added to the
publisher skill's protected glossary.

## Initial Setup Roadmap

The first setup phase is intentionally small and empirical. It should prove GitLab Wiki behavior
before building a full publisher for hundreds of pages.

1. **Translate the landing pages first.** Translate local `README.md` into Chinese and publish it as
   `vkcts-wiki-pages/home.md`. Also translate
   `external/vulkancts/wiki/Vulkan_CTS_Framework_and_Mechanism.md` into Chinese and publish it as
   `vkcts-wiki-pages/Vulkan_CTS_Framework_and_Mechanism.md`.

2. **Check relative inter-wiki links.** The `home.md` page links to
   `Vulkan_CTS_Framework_and_Mechanism.md`. This test showed that GitLab Wiki renders the target as a
   raw markdown page when the `.md` suffix is kept. The rendered wiki page link works when `.md` is
   removed, e.g. `Vulkan_CTS_Framework_and_Mechanism`.

3. **Build the future `wiki-publisher` skill with one category.** Use one representative category to
   define the translation, in-place wiki repo output, link transformation, GitLab absolute URL
   validation, protected glossary, and publish-artifact validation workflow.

4. **Refine the publisher with another category.** Use a second category to test whether the skill is
   general enough and to adjust translation invariants, link handling, validation scripts, and
   directory preservation rules.

5. **Batch publish after setup confidence.** After the two-page link check and two-category publisher
   refinement, batch publishing the remaining wiki pages should become repeatable.

## Publish Pipeline (High Level)

1. **Treat the English local wiki as read-only input.** The existing English wiki under
   `external/vulkancts/wiki/` is well-written and audited. The publisher must not edit it during
   publishing. Future factual fixes still happen there first through the normal `wiki-analyzer` /
   `vkcts-wiki-sync` workflow, but publishing itself only reads from it.

2. **Translate directly into the wiki repo publish tree.** For each category or file, the
   `wiki-publisher` skill reads the English source page, translates page content to Mandarin Chinese
   while applying translation invariants, and writes the translated page to the corresponding relative
   path under `vkcts-wiki-pages/`.

3. **Preserve filenames and directory layout.** Level-2 and Level-3 wiki filenames stay in English.
   Directory structure is preserved so markdown link handling remains predictable, for example
   `categories/api.md` and `testfiles/api/vktApiBufferTests.md` remain at those paths in the wiki
   repo.

4. **Do not adjust markdown links during translation.** The translation step should preserve link
   targets exactly, except for unavoidable escaping required by markdown syntax. Link conversion is a
   separate mechanical step.

5. **Run link transformation in the wiki repo.** A dedicated script updates markdown links in the
   translated wiki repo files in place:
   - Convert source-code and other repo-local non-wiki relative URLs to absolute GitLab blob URLs.
   - Convert inter-wiki markdown page links by dropping the `.md` suffix from link targets.
   - Preserve source line fragments such as `#L82` and `#L82-L95`.

6. **Validate the publish artifact in place.** The future `wiki-publisher` skill should own this
   validation, including scripts similar in spirit to the local `wiki-analyzer` validators. Validation
   should include:
   - GitLab absolute source URLs use the configured project URL and `SOURCE_REF`.
   - Source URL path prefixes resolve to expected repository paths.
   - Line fragments are preserved in GitLab-compatible form.
   - Inter-wiki links follow the GitLab Wiki-compatible format.
   - Protected terms, code spans, code blocks, filenames, directory paths, and registration hierarchy
     structures were not accidentally translated.

7. **Review, commit, and push to GitLab.** Publish changes from `vkcts-wiki-pages/` after reviewing
   the wiki repo diff and confirming Git safety checks.

8. **Handle reader feedback through issues.** Fixes start from the English local canonical wiki and
   are then republished. Direct GitLab Web UI edits are prevented by write protection and are not part
   of the normal workflow.

## Publish Scope

Publishable content should be controlled by an allowlist rather than copying the whole wiki tree.

Publish by default:

- `README.md` or its GitLab Wiki landing-page equivalent.
- `Objectives.md`.
- `Vulkan_CTS_Framework_and_Mechanism.md`.
- `categories/`.
- `testfiles/`.
- `images/`, if image assets are present and referenced by publishable pages.

Exclude by default:

- `internal_doc/`.
- Progress trackers.
- Validation logs such as `error_paths_*.txt` and `error_urls_*.txt`.
- Draft files and temporary files.
- Any generated temporary output from previous publish runs.

## GitLab Wiki Compatibility Checks

Before publishing the full wiki, run a small end-to-end dry run in the GitLab wiki repo. The dry run
should decide the following items empirically:

- `home.md` is the GitLab Wiki landing page file.
- Same-page Chinese heading links work in GitLab Wiki when written as Chinese heading anchors, e.g.
  `#类别命名说明`.
- Same-directory and cross-directory inter-wiki markdown links should drop the `.md` suffix in the
  publish target, e.g. `Vulkan_CTS_Framework_and_Mechanism` and `categories/info`.
- Source-code links, mustpass links, and source-adjacent documentation links have **not** been tested
  yet in GitLab Wiki and should still be handled by the future link transformation script.
- Nested pages under `categories/` and `testfiles/` still need to be validated at category scale.

The local canonical `README.md` should remain unchanged. The publisher should map local `README.md`
to `home.md` only in the wiki repo.

## Git Safety Policy

The publish workflow touches two repositories: the primary source repo and the GitLab wiki repo.
Git operations should stay conservative:

- Prefer read-only Git commands for inspection.
- Confirm the primary repo working tree before publishing so generated Chinese output is not
  accidentally committed to the source repo.
- Confirm the GitLab wiki repo working tree before copying staging output into it.
- Review the wiki repo diff before commit.
- Treat `git commit`, `git push`, branch switching, reset, clean, and other history-changing actions
  as explicit publish actions requiring user approval or manual execution.
- Keep `vkcts-wiki-pages/` as an ignored publish-target clone at the workspace root.
- Keep the wiki repo clone on `master` tracking `origin/master`, because GitLab Wiki Web UI displays
  the wiki repo's `master` content.

## Decided Deferred Items

- `internal_doc/` contents are **excluded** from publishing.
- GitLab wiki pages are generated artifacts protected against direct Web UI edits.
- Reader corrections flow through issues and then through the English canonical wiki.
- The GitLab project URL for source links is `https://sh-code.mthreads.com/haoxuan.wang/vulkan-cts-wiki`.
- Source-code links use the GitLab `vkcts-wiki` branch by default so readers see latest wiki pages
  and latest codebase together.
- The wiki repo is cloned at `vkcts-wiki-pages/` at the workspace root.
- The first wiki page was initialized as `Home` / `home.md`.
- GitLab Wiki Web UI displays wiki repo `master`; all wiki repo publish-target changes are made on
  `master` tracking `origin/master`.
- Inter-wiki markdown page links in the GitLab Wiki publish target should drop `.md` from link
  targets so they route to rendered wiki pages instead of raw markdown pages.
- Publish artifact validation and publish automation will be owned by a future `wiki-publisher`
  skill.

## Remaining Deferred Items

The following technical details will be decided during implementation:

- Final `wiki-publisher` skill design, including transformation scripts and validation scripts.
- Exact transformation and validation rules for source-code links, mustpass links, and source-adjacent
  documentation links.
- Initial protected glossary for GPU/Vulkan concepts and identifiers that should remain in English.
- Which category to use for building the initial `wiki-publisher` skill.
- Which second category to use for validating and refining the `wiki-publisher` skill.
- Integration of the publish step into the `vkcts-wiki-sync` workflow.
