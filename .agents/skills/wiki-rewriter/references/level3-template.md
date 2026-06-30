## Overview

Start with a single bold `Core question` line that states the main correctness question answered by the page. Keep it short,
reader-facing, and sharper than the full overview bullets.

Then use a high-information-density summary, usually an unordered list.

Condense only the helpful information from the old opening paragraph, `Overview`, and `Role of File` sections:

- what source file or generated test area this page covers;
- what test category, test family, intermediate node, or test cases it registers or implements;
- what the core test idea is;
- what information the reader should expect from the page.

Keep C++ details as support for understanding the test, not as source-structure inventory.

## Background Knowledge

Provide only the prerequisite concepts needed to understand this page.

Use an unordered list. Keep each item brief and page-specific.

Examples for `memory_model` / `message_passing`:

- release/acquire synchronization;
- availability and visibility;
- payload versus guard;
- synchronization scope, such as device, workgroup, and subgroup;
- why a race instance may be skipped when the guard is not observed.

Do not turn this section into a generic Vulkan tutorial.

## Registration Hierarchy

Show the smallest useful registered hierarchy that places this page's implemented test logic in context.

Choose the tree shape based on page scope:

- For a page covering multiple test families, start at the test category and show those test families.
- For a page covering one test family, start at `<test category>.<test family>` or show the category with only the relevant family
  expanded:
  - if the test family has intermediate nodes, show the relevant intermediate nodes;
  - if the test family has no intermediate nodes, show the direct path from the test family to the test case leaf or leaves.
- For hybrid registration + implementation files, include delegated test families in the tree and mark them with
  `(registration only)`.

Keep exact registered path names. Do not use `node` for the test category or the page-scope test family. Keep the hierarchy focused:
do not expand unrelated siblings or delegated test families beyond the `(registration only)` marker.

The parseable tree must expand exactly one level below its root. Do not include deeper descendants, `...`, or descriptive
placeholder lines inside the fenced tree. Put deeper test case leaves and large generated ranges in `## Intermediate Nodes`,
`## Parameter Dimensions and Observed Values`, or prose tables instead.

Examples:

Multiple test families implemented by one source file, with delegated registrations:

```text
memory_model
├── message_passing
├── write_after_read
├── transitive
├── padding (registration only)
└── shared (registration only)
```

One test family with intermediate nodes:

```text
memory_model.shared
├── scalar_types
├── vector_types
├── 16bit
└── 8bit
```

Single test case leaf with no intermediate nodes:

```text
memory_model.padding
└── test
```

## <Scope-Specific Structure Section>

Choose the heading based on the page scope. Keep this section even when the structure is trivial, so special cases are explicit.

Use one of these headings:

- `## Test Families` when the page covers multiple test families.
- `## Intermediate Nodes` when the page covers one test family, including when that test family has no intermediate nodes.

Rules:

- For multiple-test-family pages, keep one subsection for each implemented test family.
- For one-test-family pages with meaningful intermediate nodes, use `## Intermediate Nodes` and keep one subsection for each
  intermediate node that needs explanation.
- For one-test-family pages with no intermediate nodes, use `## Intermediate Nodes` but do not create fake subsections. Add a brief
  statement that the path goes directly from the test family to the test case leaf or leaves.
- Use `node` only for intermediate path components below the page's test family; do not use `node` as an alias for the test category
  or the Level-3 test family/page scope.
- If the source file also performs registration, mention that responsibility briefly in `Overview` or `Registration Hierarchy`, but
  keep the page focused on implemented test behavior.

### <test family or intermediate node name> — <very brief description>

Use a concept-first explanation for each subsection when subsections are needed. A useful default shape is:

- one sentence for the property being tested;
- one sentence for the essential test mechanism;
- one sentence for relation to other test families, intermediate nodes, special cases, or delegated pages when relevant.

Keep source links as evidence, but do not let line references dominate the explanation.

## Parameter Dimensions and Observed Values

Use this section when the page has a generated matrix, parameterized test families, or important observed values.

Keep the original values table, but add local meaning so the table is not only an inventory.

Preferred table shape:

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| <dimension> | `<value>`, `<value>` | <why this dimension matters for this page> | <source link> |

Guidelines:

- If a page has no meaningful parameter matrix, keep this section short or omit it.
- Explain what each dimension changes in the test design, shader behavior, resource layout, execution mode, or validation logic.
- Keep values and registered test names exact.

## Shader Analysis

Keep this heading in every Level-3 page. If the test has no shader or shader code is not part of the tested behavior, state that
briefly here and do not create any `### Representative Shader Walkthrough` subsection.

Representative shader walkthroughs are always produced through the [`shader-analyzer`](../../shader-analyzer/SKILL.md) skill. Do not draft walkthrough subsections directly from this template. Each walkthrough must end with the mandatory collapsed `#### SPIR-V` subsection generated by [`shader-disassembler`](../../shader-disassembler/SKILL.md).

Use at most 3 representative shader walkthroughs:

- Most pages should use 1 walkthrough.
- Add a 2nd or 3rd walkthrough only when it is significantly different from the first and also important to the test core.
- Ordinary differences should be covered by `Parameter Variation Summary`, not by separate walkthroughs.
- When using multiple walkthroughs, explain the reason and difference in the paragraph between `## Shader Analysis` and
  `### Representative Shader Walkthrough 1`.

Workflow:

- Select the exact representative CTS case or parameter path for each needed walkthrough.
- Invoke `shader-analyzer` in auto mode when the exact source file, builder function, target page, and insertion location are known.
- If the source file or builder function is not confirmed, use `shader-analyzer` manual mode and stop at its confirmation checkpoint.
- Insert or keep only the final `shader-analyzer` output here, including the generated `#### SPIR-V` subsection.
- This template intentionally omits walkthrough subsection details, which are kept in SKILL `shader-analyzer` instead of here.

## Runtime Execution and Result Checking

Explain the important **host-side** behavior that completes the picture after shader logic is understood.

Start with unordered lists. If a repeated structure becomes clear across pages, this section may later be split into subsections.

Useful content includes:

- resource setup and initialization;
- specialization constants or runtime dimensions;
- dispatch, draw, submit, or iteration counts;
- resource clearing or synchronization between runs;
- result copyback;
- host-side result scan;
- final pass/fail condition;
- what a recorded failure means for this specific test.

Avoid repeating detailed shader analysis here. Focus on how shader-observed failures become CTS case results.

## Case Pruning

Explain why some possible cases or parameter combinations are removed or skipped.

### Requirement-based pruning

Use this subsection for hardware, API, driver, feature, format, or stage requirements.

Examples:

- minimum Vulkan version;
- required device features;
- unsupported storage, atomic, stage, or scope combinations;
- device limits checked before execution.

This pruning means the case is not legal or not supported on the current implementation.

### Design-based pruning

Use this subsection for intentional exclusions from the generated matrix.

Examples:

- redundant combinations;
- combinations outside the intended test shape;
- combinations that are not meaningful for the tested property;
- fixed dimensions for a special test family.

This pruning is part of test design and may explain important intent.

## Key Takeaways

Summarize page-specific conclusions the reader should remember.

Rules:

- Keep takeaways specific to this file, test family, or intermediate node.
- Avoid generic statements that could be copied to many pages.
- Prefer conclusions about what the test proves, what failures mean, and which design choices are central.
- When possible, state what hardware-level, architecture-level, driver-level, or compiler/codegen mistakes this test can expose.
- Do not repeat the full shader walkthrough or runtime section.

Examples for `memory_model` / `message_passing`:

- Observing the guard is not required in every race instance; the key rule is that observing the guard implies the partner payload must be visible.
- A nonzero fail-buffer entry records a shader-detected ordering violation.
- `write_after_read` inverts the timing expectation: an early read must not observe a partner write that is only performed after synchronization.
- `transitive` focuses on chained availability/visibility, including who performs the visibility handoff.
- The test can expose missing release/acquire propagation, incorrect scope handling, guard visibility without payload visibility, or shader compiler lowering that weakens memory semantics.

## Source Reference Appendix

Combine the old `Source Code` and `Other Inspected Related Files` sections here.

This section is intentionally last. It is an appendix for readers who want source entry points after understanding the page.

Preferred table shape:

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| <function, range, or purpose label> | <source link> | <brief role> |

Guidelines:

- Prefer function names, range labels, or purpose labels over repeated filenames.
- Use filenames only when the file itself is the useful unit.
- Include source links that support the page's claims, not every inspected file.
- Keep delegated or related files only when they help readers follow the tested behavior or page boundary.
