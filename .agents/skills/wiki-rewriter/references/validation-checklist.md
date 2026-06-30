# Validation Checklist

Run this checklist before reporting a rewritten page as complete.

## Naming And Output

- [ ] Rewritten output is in a new file.
- [ ] Obsolete original page remains untouched.
- [ ] Level-2 filename keeps snake_case category style, such as `memory_model.md`.
- [ ] Level-3 filename is shortened CamelCase family/source suffix style, such as `MessagePassing.md`.
- [ ] Rewritten output page omits the top `#` title and starts at `## Overview`.

## Semantic Audit

- [ ] Core question or category purpose is clear.
- [ ] Test intent matches source behavior.
- [ ] Execution flow is understandable without source reading as the main path.
- [ ] Validation and pass/fail conditions are explicit.
- [ ] Failure meaning names plausible implementation bug classes.
- [ ] C++ details support understanding instead of dominating it.
- [ ] No speculative hardware, driver, or Vulkan implementation claims are presented as facts.

## Registration And Mustpass Audit

- [ ] Registered identifiers are exact.
- [ ] Hierarchy shape matches source/mustpass evidence.
- [ ] Implemented test families are not omitted.
- [ ] Delegated or registration-only areas are marked accurately.
- [ ] Pure registration-only source files are not turned into unnecessary Level-3 technical pages.
- [ ] Parameter values and test case names are exact.
- [ ] Registration validation script passes for the rewritten page or active category.

### Registration validation script

Use the existing wiki-analyzer validator from the repository root.

```bash
# Check one rewritten Level-3 wiki file.
python3 .agents/skills/wiki-analyzer/scripts/verify_registration_paths.py \
  --wiki-file external/vulkancts/wiki/testfiles/<category>/<rewritten_page>.md

# Check all extracted paths for a category.
python3 .agents/skills/wiki-analyzer/scripts/verify_registration_paths.py <category>

# Save category results for review when needed.
python3 .agents/skills/wiki-analyzer/scripts/verify_registration_paths.py <category> \
  > external/vulkancts/wiki/internal_doc/error_paths_<category>.txt 2>&1
```

Notes:

- Use single-file validation while rewriting one Level-3 page.
- Use category validation before considering a Level-2 + Level-3 category batch stable.
- The script reads the canonical `## Registration Hierarchy` tree in Level-3 pages.
- Trailing parenthesized notes on child lines are intended to be ignored by the parser.
- Special categories may dispatch to adapters under `registration_validators/`.

## Link Audit

- [ ] Wiki link validation script passes for the rewritten page or active category.
- [ ] Source-code line references use GitHub fragment syntax, such as `file.cpp#L82` or `file.cpp#L82-L95`.
- [ ] Colon-style source line references such as `file.cpp:82` are not present in wiki links.
- [ ] Relative links resolve from the owning markdown file's directory.
- [ ] Level-2 navigation links point to rewritten Level-3 pages when available.
- [ ] Links are attached to meaningful source functions, ranges, or purpose labels.
- [ ] Old source-inventory links were either used as evidence or deliberately omitted as irrelevant.

### Wiki link validation script

Use the existing wiki-analyzer validator from the repository root.

```bash
# Check one rewritten page.
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --files external/vulkancts/wiki/testfiles/<category>/<rewritten_page>.md \
  --repo-root . \
  --verbose

# Check one active category scope.
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --files external/vulkancts/wiki/categories/<category>.md external/vulkancts/wiki/testfiles/<category>/*.md \
  --repo-root . \
  --verbose

# Save category results for review when needed.
python3 .agents/skills/wiki-analyzer/scripts/validate_wiki_links.py \
  --wiki-dir external/vulkancts/wiki \
  --files external/vulkancts/wiki/categories/<category>.md external/vulkancts/wiki/testfiles/<category>/*.md \
  --repo-root . \
  --verbose \
  > external/vulkancts/wiki/internal_doc/error_urls_<category>.txt 2>&1
```

Notes:

- Prefer category-scoped validation during active rewrite work.
- Whole-wiki validation is mainly for global cleanup after category pages are expected to resolve cleanly.
- The validator ignores external URLs, URI schemes, and anchor-only links.
- `--auto-fix` only rewrites colon-style source references to `#L` form; it does not repair broken relative paths or wrong filenames.

## Shader And SPIR-V Audit

Use when the page includes shader analysis.

- [ ] `## Shader Analysis` exists.
- [ ] No walkthrough is created when shader code is irrelevant.
- [ ] Each walkthrough corresponds to an exact CTS case or parameter path.
- [ ] No more than three representative walkthroughs are used.
- [ ] `shader-analyzer` produced the walkthrough material.
- [ ] Reconstructed GLSL/HLSL preserves source-generated `//` comments and uses concise wiki-authored `///` comments.
- [ ] Important resource facts appear near shader declarations when concise.
- [ ] Every representative walkthrough ends with `#### SPIR-V`.
- [ ] `shader-disassembler` generated the SPIR-V subsection from reconstructed GLSL or HLSL.
- [ ] Target SPIR-V environment comes from CTS shader build options, not from guessed Vulkan runtime version.
- [ ] SPIR-V assembly is full, collapsed, fenced as `llvm`, and not hand-edited.

## Brief-to-Page Audit

Use when an Understanding Brief was created.

- [ ] Final page distills the brief rather than copying beginner scaffolding verbatim.
- [ ] Brief source mapping becomes a focused source appendix.
- [ ] Important concrete examples become formal walkthroughs, tables, or concise explanations.
- [ ] Risk points are resolved or reported.
