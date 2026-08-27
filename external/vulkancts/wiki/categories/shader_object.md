## Overview

The `shader_object` test category collects tests that check the API, lifecycle, execution, and performance behavior of `VK_EXT_shader_object`.

The category has ten direct test families. The registration-only dispatcher in `vktShaderObjectTests.cpp` is represented here rather than by a separate rewritten Level-3 page.

## Background Knowledge

- **Shader objects, pipelines, and dynamic state.** A `VkShaderEXT` object represents one programmable stage. Applications bind shader objects by stage instead of binding one `VkPipeline`, so they must provide through dynamic-state commands the graphics state that a pipeline would otherwise supply.
- **Per-stage binding, linked creation, and stage chains.** `vkCmdBindShadersEXT` replaces only the listed stage bindings. `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT` links shaders created together, while `VkShaderCreateInfoEXT::nextStage` declares legal following stages. These rules shape the creation, link, binding, and pipeline-interaction families.
- **Dynamic rendering.** Graphics shader objects execute inside dynamic rendering rather than through a render pass baked into a graphics pipeline. Attachment slots map fragment output locations to image views and may include null views or locations with no matching shader output.
- **Shader binaries.** `vkGetShaderBinaryDataEXT` returns an implementation-defined representation of a shader object. A compatible device can use those bytes with `vkCreateShadersEXT`, allowing the tests to check query behavior, recreation, compatibility failures, and creation cost.
- **Tessellation stages.** Tessellation uses a control shader, a fixed-function tessellator, and an evaluation shader. Their patch sizes and execution modes determine subdivision, primitive domain, spacing, orientation, and generated positions.

## Category Structure

```text
shader_object
├── api
├── create
├── link
├── tessellation
├── binary
├── pipeline_interaction
├── binding
├── performance
├── rendering
└── misc
```

[`createTests()`](../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) registers all ten test families directly. Each family maps to one rewritten Level-3 page.

## How the Families Fit Together

The families cover the shader-object lifecycle from capability discovery to execution and diagnostics:

- **API and object data:** `api` checks the required API surface, while `create` and `binary` cover creation, result handling, binary queries, and recreation.
- **Stage relationships:** `link`, `binding`, and `tessellation` check legal stage chains, linked creation, per-stage replacement or unbinding, and tessellation execution modes.
- **Execution state:** `pipeline_interaction`, `rendering`, and `misc` check switching between object types, dynamic-rendering attachment routing, dynamic state, interfaces, lifetime, and push constants.
- **Relative cost:** `performance` compares shader-object operations with pipeline, linked-shader, SPIR-V, binary, and host-copy reference paths.

Together, these families check that shader objects expose the required API, preserve their data and relationships, and execute with the state active at each draw or dispatch.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `api` | [ApiTests](../testfiles/shader_object/ApiTests.md) | Proc-address availability, extension revisions, dynamic-rendering support, and `shaderBinaryUUID`. |
| `create` | [CreateTests](../testfiles/shader_object/CreateTests.md) | Batch creation, binary round trips, required result codes, and output-handle rules. |
| `link` | [LinkTests](../testfiles/shader_object/LinkTests.md) | Linked and unlinked stage combinations, `nextStage`, creation order, and bind layouts. |
| `tessellation` | [TessellationTests](../testfiles/shader_object/TessellationTests.md) | Execution-mode placement, tessellation behavior, and temporary stage rebinding. |
| `binary` | [BinaryTests](../testfiles/shader_object/BinaryTests.md) | Binary query invariance, recreation, incompatible input, and device-feature variation. |
| `pipeline_interaction` | [PipelineInteractionTests](../testfiles/shader_object/PipelineInteractionTests.md) | Binding disturbance and switching between pipelines and shader objects. |
| `binding` | [BindingTests](../testfiles/shader_object/BindingTests.md) | Stage swaps, unbinding forms, feature-disabled stages, interleaving, and mesh paths. |
| `performance` | [PerformanceTests](../testfiles/shader_object/PerformanceTests.md) | Relative timing for draw, dispatch, binding, binary creation, and host-copy paths. |
| `rendering` | [RenderingTests](../testfiles/shader_object/RenderingTests.md) | Attachment counts, output holes, formats, binding time, depth, and output arrays. |
| `misc` | [MiscTests](../testfiles/shader_object/MiscTests.md) | Dynamic-state comparisons, stage interfaces, tessellation edge cases, lifetime, and push constants. |

## Category Notes

- The `performance` family is source-registered but excluded from the default mustpass selection by `dEQP-VK.shader_object.performance.*` in [excluded-tests.txt](../../mustpass/main/src/excluded-tests.txt#L8).
- `vktShaderObjectTests.cpp` only dispatches the ten direct families. Its registration facts are folded into this Level-2 page, so there is no rewritten dispatcher Level-3 page.
