# Understanding Brief: IndirectTest

## One-Sentence Test Purpose

This test checks that Vulkan sequential and indexed indirect draws fetch command and draw-count data from the correct buffer locations, after optional compute generation, and produce the expected image across ordinary, multi-draw, instanced, multiview, offset, and count-clamping cases.

## Background Knowledge

- `vkCmdDrawIndirect` and `vkCmdDrawIndexedIndirect` read draw parameters from `VkDrawIndirectCommand` and `VkDrawIndexedIndirectCommand` records rather than from the command call.
- A count-buffer command reads a `uint32_t` draw count and executes no more than `maxDrawCount` records; the extension entry points require `VK_KHR_draw_indirect_count`.
- A supplied indirect offset and stride are byte addressing parameters. The implementation must not treat the buffer start or tightly packed structure size as implicit values.
- A compute shader write must be made visible to a later indirect-command read. This test deliberately exercises that producer/consumer transition.
- The image comparison is an end-to-end oracle: a mismatch may involve command fetch, synchronization, vertex/index fetch, primitive assembly, rasterization, or readback.

## One Concrete Example

For `draw.renderpass.indirect_draw.indexed.indirect_draw_count.triangle_list_multi_draw`, the indexed case stores multiple `VkDrawIndexedIndirectCommand` records, uses the count-buffer command with a multi-draw count, and renders a triangle list. The source enables the multi-draw path through `MultiDrawScopedSetter`; support checking requires `multiDrawIndirect` and a sufficient `maxDrawIndirectCount`.

## End-to-End Test Flow

```text
[registration] choose sequential/indexed, producer, offsets, and mechanism group
[registration] choose triangle_list, triangle_strip, or triangle_list_multi_draw
[host] create padded indirect data and (for count cases) a padded count buffer
[optional device producer] NegateData.comp restores the command/count bytes
[barrier] make compute shader writes visible to indirect-command reads
[device] issue ordinary, count-buffer, parameter-count, instanced, or multiview draw
[host] read the color target and compare it with the expected reference image
```

The `indexed_draw_count_clamping` family instead initializes an intentionally oversized count (`kOOBDrawCount = 4096`) and verifies that only valid commands are executed.

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Role |
|---|---|
| `VertexFetch.vert` / `VertexFetch.frag` | Graphics shaders used by the indirect cases. |
| `NegateData.comp` | Optional compute producer that restores bitwise-negated indirect and count data. |
| Indirect buffer | Contains padded `VkDrawIndirectCommand` or `VkDrawIndexedIndirectCommand` records. |
| Count buffer | Contains the count value at a non-zero offset for count mechanisms. |
| Vertex and index buffers | Supply the geometry; indexed cases additionally apply bind/allocation offsets. |
| Color target | Receives the rendered result for image comparison. |

## What Is Checked

The test compares the rendered image against a reference generated from the expected command parameters. Ordinary and instanced paths use `tcu::fuzzyCompare` with threshold `0.05`; the clamping case has a reference that distinguishes the valid draws from accidental extra draws. The source checks command issue, resource setup, and synchronization rather than exposing an independent counter for every field.

## Behavior Parameter Identification

> **Behavior parameter:** indirect execution mechanism.
>
> **Candidate values:** `indirect_draw`, `indirect_draw_count`, `indirect_draw_param_count`, `indirect_draw_instanced`, `indirect_draw_multiview`, and the corresponding first-instance/count variants.

Cross-cutting dimensions are the exact registered draw-type suffixes (`sequential`, `indexed`, `_data_from_compute`, `_bind_offset_16`, `_alloc_offset_16`), topology leaves (`triangle_list`, `triangle_list_multi_draw`, `triangle_strip`), and instanced children (`first_instance`, `no_first_instance`).

## What Failure Means

| Failing behavior | Likely area to investigate |
|---|---|
| `indirect_draw` | Indirect record address, stride, field fetch, or ordinary primitive assembly. |
| `*_multi_draw` | `drawCount`, record stepping, `multiDrawIndirect`, or `maxDrawIndirectCount`. |
| `indirect_draw_count` | Count-buffer address/value, extension command, or maximum draw-count handling. |
| `indirect_draw_param_count` | Parameter-count mechanism and its count source. |
| `_data_from_compute` | Compute writes, compute-to-indirect synchronization, or visibility scope. |
| `_bind_offset_16` / `_alloc_offset_16` | Index-buffer binding offset, allocation offset, or address arithmetic. |
| `*_instanced.*` / `*_first_instance` | `instanceCount`, instance-rate fetch, or `firstInstance` feature behavior. |
| `indirect_draw_multiview` | Layer count, multiview feature, or per-view rendering. |
| `indexed_draw_count_clamping` | Bounds/clamping of count-buffer execution against valid indirect records. |

## Important Variations and Special Cases

- Count mechanisms require `VK_KHR_draw_indirect_count`; multi-draw requires core `multiDrawIndirect` and `maxDrawIndirectCount >= kDrawCount`.
- Dynamic rendering requires `VK_KHR_dynamic_rendering`, multiview requires `multiview`, and non-zero first-instance cases require `drawIndirectFirstInstance`.
- Vulkan SC excludes the non-SC dynamic/secondary registration branches under `CTS_USES_VULKANSC`. Do not infer dynamic-rendering coverage from `vksc-default/draw.txt`.
- Non-zero index bind/allocation offsets are generated only for indexed draw types. Compute variants restore both command and count data before the draw when applicable.
- The source uses exact identifiers such as `indexed_alloc_offset_16`, not a normalized spelling such as `indexed_allocation_offset`.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Group and suffix generation | [`vktDrawIndirectTest.cpp#L1871-L1924`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1871-L1924) | Defines the matrix and exact names. |
| Mechanism/leaf registration | [`vktDrawIndirectTest.cpp#L1925-L2049`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1925-L2049) | Defines ordinary, count, parameter-count, multiview, and topology leaves. |
| Instanced and first-instance groups | [`vktDrawIndirectTest.cpp#L2055-L2319`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L2055-L2319) | Defines nested exact identifiers. |
| Compute producer and barriers | [`vktDrawIndirectTest.cpp#L427-L500`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L427-L500) | Shows device generation and visibility barrier. |
| Count command issue | [`vktDrawIndirectTest.cpp#L590-L671`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L590-L671) | Shows ordinary versus count dispatch and offsets. |
| Support gates | [`vktDrawIndirectTest.cpp#L1835-L1867`](../../../modules/vulkan/draw/vktDrawIndirectTest.cpp#L1835-L1867) | Shows required functionality and features. |
| Mustpass evidence | [`vk-default/draw.txt`](../../../mustpass/main/vk-default/draw.txt), [`vksc-default/draw.txt`](../../../mustpass/main/vksc-default/draw.txt) | Confirms release registration identifiers and SC boundary. |
| Vulkan semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc) and [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc) | Defines indirect parameters, count execution, and synchronization. |

## Questions / Risk Points for User Audit

- A failing image does not uniquely identify whether stale compute data, wrong buffer offsets, malformed records, or rasterization caused the mismatch; correlate the exact registration suffix and mechanism with validation output.
- The mustpass files are evidence of listed release cases, not proof that every source-generated combination is present in every profile.
- Vulkan SC language gates intentionally limit the dispatcher matrix; preserve that distinction when comparing default and SC lists.

## Conversion Notes for Final Wiki Rewrite

Preserve `vktDrawIndirectTest.md` unchanged. This brief belongs to the new `IndirectTest.md` page and preserves the exact registration vocabulary, source links, spec chapters, mustpass evidence, language gates, and validator-auditable headings.
