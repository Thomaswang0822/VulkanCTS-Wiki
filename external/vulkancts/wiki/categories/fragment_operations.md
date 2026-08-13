## Overview

The `fragment_operations` test category collects tests that check how fragment-stage execution interacts with scissor clipping, early fragment tests, occlusion queries, and transient attachments.

The category is registered by [`createTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L50-L53) and its dispatcher [`addFragmentOperationsTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L38-L46). Exact current behavior is explained in the Level-3 pages linked below.

## Background Knowledge

- **Per-fragment tests and sample coverage.** Scissor, depth, and stencil tests determine whether covered samples continue through the fragment pipeline. Occlusion queries count samples that survive these tests, while multisampling represents coverage with one bit per sample. This shared relationship is needed to understand the scissor, early-fragment, and occlusion-query families.
- **Viewport and scissor selection.** A fragment's `ViewportIndex` selects the matching viewport and scissor rectangle. The multi-viewport scissor family uses this parallel indexing to test several independent viewport-scissor pairs in one draw. See the [Vulkan scissor-test definition](../../../vulkan-docs/src/chapters/fragops.adoc#L426-L445).
- **Transient attachment lifetime.** A transient attachment can be used as a render-pass attachment and, when its usage and layout permit, read as an input attachment. Load and store operations define whether contents are cleared, retained, or made available across attachment uses. The transient-attachment family tests this lifetime boundary rather than treating transient memory as an ordinary host-visible image.

## Category Structure

```text
fragment_operations
├── scissor
├── early_fragment
├── occlusion_query
└── transient_attachment_bit
```

The `multi_viewport` test family is nested below `scissor` and has its own Level-3 page; it is not a fifth direct child of the test category.

## How the Families Fit Together

The four direct test families cover different ways that fragment-stage state and attachment behavior affect observable results:

- **Scissor** checks fixed-function sample clipping for points, lines, triangles, and multiple viewport-scissor pairs.
- **Early fragment** checks the relationship between depth/stencil timing, shader side effects, discard, sample masks, sample counts, and selected early-and-late or maintenance5 modes.
- **Occlusion query** checks whether query results reflect samples surviving the fragment tests, with separate conservative and precise result contracts.
- **Transient attachment** checks whether cleared color, depth, or stencil contents survive a store/load handoff and can be read through an input attachment under two memory-property modes.

Together, the families move from per-draw coverage decisions, through shader and sample-test ordering, to query observability and attachment lifetime.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `scissor.points`, `scissor.lines`, `scissor.triangles` | [Scissor.md](../testfiles/fragment_operations/Scissor.md) | Primitive-specific scissor coverage, generated geometry, reference-image construction, and comparison. |
| `scissor.multi_viewport` and `scissor_1` through `scissor_16` | [ScissorMultiViewport.md](../testfiles/fragment_operations/ScissorMultiViewport.md) | Per-viewport scissor selection driven by a geometry shader and the viewport-count sweep. |
| `early_fragment` direct cases | [EarlyFragment.md](../testfiles/fragment_operations/EarlyFragment.md) | Early depth/stencil behavior, discard, sample masks, sample-count variants, shader side effects, and feature gates. |
| `occlusion_query` conservative and precise cases | [OcclusionQuery.md](../testfiles/fragment_operations/OcclusionQuery.md) | Query-pool setup, modifier combinations, precision modes, and pass/fail result rules. |
| `transient_attachment_bit` color, depth, and stencil cases | [TransientAttachment.md](../testfiles/fragment_operations/TransientAttachment.md) | Render-pass store/load behavior, input-attachment reads, memory-property variants, and image comparison. |

## Category Notes

- The registered category name is `fragment_operations`, while the source directory is `fragment_ops/` and the default mustpass file is [`fragment-operations.txt`](../../mustpass/main/vk-default/fragment-operations.txt).
- [`vktFragmentOperationsTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L38-L46) is a registration-only dispatcher. Its category-level routing is folded into this page; it does not receive a separate Level-3 implementation page.
