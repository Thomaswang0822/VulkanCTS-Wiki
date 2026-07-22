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

Keep this heading in every Level-3 page. During initial Level-3 drafting, make this section self-contained: do not depend on a future Level-2 page or another Level-3 page for prerequisite concepts. A later category-level consolidation pass may move repeated shared concepts into the Level-2 page and compact the affected Level-3 bullets.

Use this section only for the minimum external concepts that the target reader must understand before the rest of this page makes sense. It supplies conceptual tools; it does not preview or summarize the test.

Choose the opening shape according to prerequisite ownership:

- If the page has only page-local prerequisites, begin directly with the local prerequisite bullets.
- If category-shared prerequisites were consolidated into the Level-2 page, begin with a standalone upward-link sentence that names the shared concept and links to the Level-2 `## Background Knowledge` section. Put any remaining page-local bullets after that sentence.
- Use a recommended sentence shape such as `For the shared <concept> model, see the [category-level Background Knowledge](...).`. The ownership and link are required; the exact English wording is not.
- If no prerequisites remain, use the canonical no-prerequisite sentence below instead of an upward link or bullets.

When bullets are present, use a brief unordered list. Each item should:

- define one prerequisite concept outside the target-reader baseline;
- be needed by a later behavior, shader, runtime, validation, pruning, or failure explanation;
- explain the minimum concept and, only when useful, briefly identify why later reasoning depends on it;
- remain understandable as a concept rather than becoming narration of the concrete CTS case.

A concise realistic example or analogy is allowed when it materially improves the reader's mental model. Make clear that it is
illustrative rather than the actual CTS setup. For example, explain BLAS/TLAS separation through multiple transformed instances of
one mesh in a larger scene when an abstract definition would not explain why the two levels exist.

A brief test-specific contrast is also allowed when ordinary use of a concept would otherwise create a wrong mental model. State
the ordinary use, flag the unconventional use in this test, and give only the interpretive consequence needed for later sections.
Stop before the detailed setup or mechanism. For example, a procedural-geometry page may note that AABBs normally enclose a custom
surface but this test also uses controlled non-enclosing proxies, so proxy location must not be read as the surface bounds.

Do not include concrete test setup, registered values, parameter matrices, execution steps, expected outputs, pass/fail rules,
correctness contracts, conclusions, or failure meaning. Those belong in the page body, `## Overview`, or `## Key Takeaways`.
Keep substantive overlap with those two sections minimal, and do not turn this section into a generic Vulkan tutorial.

During later category Background Knowledge consolidation, classify every existing Level-3 BGK item before editing it:

| Item type | Consolidation action |
|-----------|----------------------|
| Repeated category-shared prerequisite | Move the full explanation to Level-2; add the standalone upward-link sentence at the beginning of the affected Level-3 section. |
| Mixed shared concept plus page-local consequence | Move or remove the shared explanation, add the standalone upward-link sentence, and preserve the local prerequisite consequence as a bullet after it. |
| Definitely page-local prerequisite | Preserve the bullet title and wording unless a confirmed meaningful defect requires a minimal edit. |
| Concrete setup, parameters, execution, validation, expected result, or conclusion | Remove from BGK or relocate only if the correct later section does not already explain it. |
| Helpful illustrative example for a shared concept | Preserve once in Level-2 BGK when it materially improves the shared mental model. |

Do not leave the upward link embedded inside a prerequisite bullet after consolidation. Do not rewrite this section wholesale during consolidation.

If the target reader needs no additional prerequisite concepts, keep the heading and write exactly:

```text
No additional prerequisite concepts are needed for this page.
```

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
placeholder lines inside the fenced tree. Put deeper test case leaves and large generated ranges in `## Behavior Parameters`,
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

## Parameter Dimensions and Observed Values

This section comes before `## Behavior Parameters`. The order is: all parameter dimensions first (the full matrix inventory),
then the primary behavioral axis (the one dimension that most controls test behavior, explained in depth).

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

## Behavior Parameters

This section explains the registered parameter that most directly controls test behavior. Identify the primary behavioral axis —
the registered dimension whose values change *what is being tested*, not just configuration details — and explain each of its
values in a subsection.

The behavioral axis can be any registered dimension depending on the test family:

- the test case leaf, when leaves are the primary behavior choice (for example, `geometry.layered` where each leaf changes shader
  logic and validation);
- an intermediate node, when nodes below the test family are the primary behavior choice (for example, `memory_model.shared` where
  layout nodes like `scalar_types` or `nested_structs_arrays` are the behavior axis);
- a test family, when the page covers multiple families that each test a different property (for example, `memory_model` where
  `message_passing`, `write_after_read`, and `transitive` are the behavior axis);
- a behavioral group, when leaves cluster into groups with distinct mechanisms (for example, `geometry.basic` where leaves group
  into fixed-output, runtime-varying, and side-effect behaviors).

Rules:

- Use `### <parameter value name> — <very brief description>` subsections for each value of the primary behavioral axis.
- For families with multiple important behavioral axes, use multiple groups of subsections, each introduced by a short paragraph
  identifying the axis.
- For a test family with no meaningful behavioral axis (for example, a single fixed test case), state that briefly and do not create
  artificial subsections.
- Use a concept-first explanation for each subsection. A useful default shape is:
  - one sentence for the property being tested;
  - one sentence for the essential test mechanism;
  - one sentence for relation to other parameter values, special cases, or delegated pages when relevant.
- Keep source links as evidence, but do not let line references dominate the explanation.
- If the source file also performs registration, mention that responsibility briefly in `Overview` or `Registration Hierarchy`, but
  keep the page focused on implemented test behavior.
- Do not use `node` as an alias for the test category or the test family. Use `intermediate node`, `test case leaf`, or `test
  family` per the terminology policy when referring to hierarchy positions.

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
- In each walkthrough's `#### Structural Design`, avoid raw ASCII flowcharts or plain-text decision trees. Use Mermaid for flowchart-like or tree-like control flow, while still allowing tables, mappings, or other structured non-plain-text formats when they explain the shader better.
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
- final pass/fail condition.

Avoid repeating detailed shader analysis here. Focus on how shader-observed failures become CTS case results. Detailed failure analysis belongs in `## Failure Meaning`, not here.

## Failure Meaning

Explain what a failure of this test means. This section has two fixed subsections.

### Failure Cause Mapping

If an Understanding Brief exists for this page, copy its `### Failure Cause Mapping` table directly from the brief's
`## What Failure Means` section. Do not craft a new table from scratch when a brief is available.

If no brief exists, map each value of the primary behavioral axis (the axis identified in `## Behavior Parameters`) to the possible
failure cause(s) that value's failure would point to. Use a table:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `<value>` | <cause description> |

Rules:

- The left column uses the same parameter values documented in `## Behavior Parameters`.
- For families with multiple behavioral axes, use multiple small tables, one per axis.
- The right column names the cause concisely. Detailed explanation goes in `### Cause Analysis`.
- If all values share a common failure cause (for example, shared infrastructure), add a row or short paragraph after the table.
- For a test family with no behavioral axis (single fixed test case), replace the table with a short paragraph stating the cause
  directly.

### Cause Analysis

Explain each cause named in `### Failure Cause Mapping` in its own `#### <cause name>` subsection.

For each cause, address two questions using the bold lead-in pattern:

**Possible failure symptoms:** the observable failure symptom, derived from what the test actually checks (its validation
  logic, pass/fail condition, or expected output). This is always written because it is derivable from the test's own checking.

**Possible implementation causes:** the driver, hardware, compiler, or host-side behavior that would produce that
  symptom. Write this only when the cause can be grounded in Vulkan spec semantics, GPU architecture knowledge, or CTS source
  inspection. If no evidence-based cause can be found, state that source-level investigation is needed rather than inventing one.

Use the exact bold lead-in labels `**Possible failure symptoms:**` and `**Possible implementation causes:**` so
the pattern is consistent across all pages and easy to scan.

Rules:

- Derive each page's failure analysis case by case from what that specific test exercises. Do not apply preconceived assumptions
  about where bugs live (GPU hardware, driver, host); the failure mode depends on what the test checks.
- The depth of `### Cause Analysis` scales with the number of distinct mechanisms the test exercises. A single-mechanism test gets
  one short subsection; a multi-mechanism test gets more.
- Do not add subsections for causes that have no meaningful analysis. No padding.
- Do not repeat the full runtime execution or behavior parameters content here. Focus on what failure means.
- If a cause has sub-mechanisms that need separate analysis, use **bold lead-in paragraphs** within the `####` subsection instead of
  deeper headings. For example: `**Depth/stencil layered rendering.** <analysis>` as a paragraph inside `#### Attachment load and copyback failures`.

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
- Prefer conclusions about what the test proves and which design choices are central.
- Reference `## Failure Meaning` for failure analysis instead of duplicating it here.
- Do not repeat the full shader walkthrough, runtime section, or failure-meaning section.

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
