# Understanding Brief: <scope>

## One-Sentence Test Purpose

State the test's core purpose in one sentence.

Good shape:

```text
This test checks whether <implementation area> correctly handles <tested behavior> under <important condition>.
```

Rules:

- Avoid source-file inventory.
- Avoid generic Vulkan tutorial language.
- State what the test proves or tries to catch.

## Background Knowledge

Explain only the concepts needed to understand this test before the concrete example and flow.

Guidelines:

- Prefer one or two focused topics, not a general tutorial.
- Choose concepts that can later be reused in the final Level-3 page's `Background Knowledge` section.
- Explain the domain/scope of key terms, such as whether memory is per invocation, per workgroup, per queue, or device-wide.
- Explain important caveats early when they prevent wrong mental models.
- For shader-heavy tests, include the minimum shader execution model needed to understand the test.

Good shape:

```text
### <concept central to this test>

<short explanation>

Why it matters here:
- <point directly used by this test>
- <point directly used by this test>
```

## One Concrete Example

Start from a small concrete example before explaining generators, matrices, or abstractions.

Useful examples:

- a representative shader path;
- a small generated shader fragment;
- one resource layout;
- one synchronization sequence;
- one draw/dispatch case;
- one image/buffer/descriptor setup.

Rules:

- Prefer a simplified but faithful example.
- Clearly mark reconstructed or conceptual code.
- Keep exact technical terms, identifiers, and registered test names when relevant.
- Follow wiki hierarchy terminology: use `test category` for Level-2 components, `test family` for Level-3 components, `node` only
  for intermediate components below a test family, and `test case` or `test case leaf` for executable leaves. Do not use `node`
  as an alias for a test category or test family.

## End-to-End Test Flow

Explain the test in time order. Use `[host]` and `[device]` markers instead of separate fixed host-only and device-only sections.

Preferred shape:

```text
[host] choose or generate test parameters
[host] create/configure resources and descriptors
[host] generate or load shader/program artifacts
[host] submit draw/dispatch/copy work
[device] execute shader or fixed-function behavior
[device] write result data or observable output
[host] copy/read/inspect results
[host] decide pass/fail
```

Guidelines:

- Preserve temporal order when host and device work interleave.
- Include synchronization, barriers, queue submissions, copyback, or waits when they are conceptually important.
- For pages with multiple distinct flows, keep one `text` flow block but use numbered subflows, such as regular path versus
  special path, so readers can compare shared host setup and divergent device behavior.
- Avoid low-level boilerplate unless it changes the tested behavior.

## Generated Test Artifacts and Bound Resources

Explain the important artifacts produced, configured, loaded, or bound by the test before execution.

This section is not shader-only. It should cover both generated program artifacts and GPU-visible resources when they matter for
understanding the test.

### Generated or loaded program artifacts

Include items such as:

- inline GLSL shader source strings;
- generated SPIR-V assembly;
- generated HLSL text;
- Amber scripts;
- specialization constants;
- generated pipeline state;
- generated renderpass/framebuffer descriptions;
- randomized test case matrices;
- generated descriptor or resource layouts.

Explain what is generated, why it is generated, and which parts affect the tested behavior.

### Bound resources and memory objects

Include the memory/resource picture needed to understand the test, such as:

- uniform buffers / constant buffers;
- storage buffers / UAV-like resources;
- sampled images / SRV-like resources;
- storage images;
- textures and samplers;
- image views and buffer views;
- color, depth, stencil, or input attachments;
- descriptor sets and binding points;
- push constants;
- host-visible readback buffers;
- device-local target resources;
- external, protected, sparse, or aliased memory when relevant;
- image layouts, access masks, and memory barriers when they are central to the test.

For each important resource, answer:

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `<resource>` | yes/no | yes/no | yes/no | yes/no | <role in test> |

Rules:

- Do not list every helper object or boilerplate wrapper.
- Include resources whose omission would confuse the reader's mental model.
- Be explicit when something is **not** a real host-created/bound GPU resource, such as GLSL `shared` variables.

## What Is Checked

Explain the pass condition from the test's point of view.

Useful questions:

- What value, image, buffer, counter, query result, or shader-observed condition is checked?
- Is the check done on the device, on the host, or both?
- Is there a tolerance, mask, expected layout, or expected ordering rule?
- Does the test check every generated case independently or aggregate results?

Prefer concise lists or tables.

## Behavior Parameter Identification

State the primary behavioral axis and its candidate values for user confirmation before writing the failure analysis below.

> **Behavior parameter:** `<axis name>` (for example: behavior leaf, intermediate node, test family, or behavioral group)
>
> **Candidate values:** `<value 1>`, `<value 2>`, ...

If the identification is wrong, the failure analysis below will need to be redone together. Keep this block brief and eye-catching.

## What Failure Means

### Failure Cause Mapping

Map each behavior parameter value to the possible failure cause(s) that value's failure would point to. Use the same table format
as the final Level-3 page's `### Failure Cause Mapping` so this table can be copied over directly.

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `<value>` | <cause description> |

Rules:

- The left column uses the same values listed in `## Behavior Parameter Identification` above.
- For families with multiple behavioral axes, use multiple small tables, one per axis.
- The right column names the cause concisely. Do not include detailed analysis here — the detailed `### Cause Analysis` is written
  during the final Level-3 rewrite, not in this brief.

## Important Variations and Special Cases

Use this flexible section for important page-specific behavior that does not fit cleanly elsewhere.

Examples:

- 8-bit / 16-bit variants;
- feature-gated subfamilies;
- special synchronization forms;
- special resource types;
- special shader stages;
- non-obvious pruning rules;
- unusual fallback paths;
- cases where the same mental model has one important exception.

Rules:

- Keep the section focused on variations that affect understanding.
- Do not duplicate full parameter tables from the final wiki page unless needed for learning.
- State whether the variation changes the core mental model or only extends it.

## Source Mapping

Map the understanding above back to source entry points.

Preferred table:

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| <topic> | <relative source link> | <role> |

Guidelines:

- Use source links as evidence, not as the main narrative.
- Prefer function/range labels over repeated filename-only entries.
- Include only links needed to audit the brief's claims.
- In addition to the source-mapping table, add inline source links for important back-ticked concepts when the concept is specific
  to the implementation and the link would make reading/navigation easier. Do not link every technical term; prioritize generated
  functions, shader variables, core pass/fail checks, non-obvious resource behavior, and special-case control flow.

## Questions / Risk Points for User Audit

End with concrete review questions for the user.

Examples:

- Is the core test purpose clear?
- Is the host/device timeline understandable?
- Are generated artifacts distinguished from real GPU resources?
- Are important buffers, images, descriptors, samplers, or attachments included?
- Is the shader or device-side behavior explained at the right depth?
- Are special variants explained only as much as needed?
- Is any analogy misleading?
- Which parts should become final wiki content, and which parts are only learning scaffolding?

## Conversion Notes for Final Wiki Rewrite

Briefly record how this Understanding Brief should influence the final Level-3 page.

Important rule:

- Do not copy the brief's beginner-friendly `Background Knowledge` section directly into the final wiki page. Distill it into
  the final Level-3 template style: a brief unordered list of page-specific prerequisites, similar to the
  `vktMemoryModelMessagePassing.md` pilot page.

Examples:

- Which concrete example should become the representative walkthrough?
- Which source details should move to the appendix?
- Which concepts belong in the final wiki's `Background Knowledge` list?
- Which brief-only explanations, analogies, or teaching scaffolding should be shortened or removed?
- Which flow or resource table should be preserved in a more formal style?
- The `### Failure Cause Mapping` table from `## What Failure Means` should be copied directly into the final page's
  `## Failure Meaning` → `### Failure Cause Mapping`. The `### Cause Analysis` subsection is written fresh during the final
  rewrite, not carried from the brief.
- After the brief is complete, assess whether built-in knowledge is sufficient to write grounded `### Cause Analysis` for every
  cause in the mapping. If any cause's implementation-level explanation cannot be grounded in Vulkan spec semantics, GPU
  architecture knowledge, or CTS source inspection, flag it here as a KB gap. A domain knowledge-base file should be created
  before the final rewrite begins. See `wiki-rewriter/SKILL.md` Step 4 for the KB gap assessment procedure.
