## Overview

The `robustness` test category collects tests that check how Vulkan handles out-of-range buffer, image, vertex-input, and index-buffer accesses, together with selected non-robust control-flow cases. The tests compare valid data and invalid-access results against the robustness contract selected by the case.

## Background Knowledge

- **Bounded resource access:** a descriptor or view exposes a usable range, which can be smaller than its backing allocation. Robustness tests distinguish an access beyond that visible range from an access beyond the allocation itself.
- **Robustness contracts:** Vulkan features such as `robustBufferAccess`, `robustBufferAccess2`, image robustness, and pipeline robustness constrain what an invalid access may return or modify. The permitted result is not always one fixed bit pattern.
- **Shader and host responsibilities:** shaders perform the access or capture a fetched value; the host then submits the work, copies or maps the result, and applies the case-specific predicate. Some families instead compare a rendered image or use Amber's buffer-equality command.
- **Indexed and vertex input addressing:** vertex and index buffers turn draw indices, binding offsets, strides, and input rates into memory addresses. Small changes in those parameters can move only one attribute or one primitive across a boundary.

## Category Structure

The root dispatcher attaches these direct children to `robustness`. `through_pointers` is inserted below `buffer_access`; the parenthesized entries are registered only outside Vulkan SC.

```text
robustness
├── buffer_access
│   └── through_pointers
├── vertex_access
├── index_access
├── robustness2
├── image_robustness
├── pipeline_robustness (non-VulkanSC only)
├── non_robust_buffer_access
├── pipeline_robustness_buffer_access (non-VulkanSC only)
├── bind_index_buffer2 (non-VulkanSC only)
├── descriptor_heap_buffer_access (non-VulkanSC only)
├── robustness1_vertex_access
└── oob_access
```

The dispatcher and its `through_pointers` insertion logic are defined in [vktRobustnessTests.cpp](../../modules/vulkan/robustness/vktRobustnessTests.cpp#L61-L99).

## How the Families Fit Together

The families share a boundary-testing goal but vary the resource address calculation and the observation point.

- **Buffer families** test uniform, storage, and texel-buffer operations, including descriptor-range and backing-allocation boundaries; the variable-pointer subgroup dereferences storage-buffer pointers produced by runtime-dependent SPIR-V `OpSelect` instructions.
- **Vertex and index families** test addresses produced by vertex-input and indexed-draw state, so their primary evidence is captured vertex data or a rendered image.
- **Extension and OOB families** select robustness features for buffers, images, pipelines, and resource-specific out-of-range accesses, including null descriptors and pipeline-library paths.
- **Non-robust buffer access** deliberately keeps invalid references in unexecuted Amber branches; it checks that valid executed branches remain unaffected rather than defining an executed OOB value.

Together these families cover both the access operation and the state that determines its usable range.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `buffer_access`, `pipeline_robustness_buffer_access`, `descriptor_heap_buffer_access` | [BufferAccess](../testfiles/robustness/BufferAccess.md) | Shared buffer/texel-buffer generator, feature modes, boundary variants, shader access forms, and host verification. |
| `buffer_access.through_pointers` | [VariablePointers](../testfiles/robustness/VariablePointers.md) | Direct SPIR-V variable-pointer loads and stores across descriptor and allocation boundaries. |
| `vertex_access` | [VertexAccess](../testfiles/robustness/VertexAccess.md) | Format, draw, and draw-indexed vertex-input fetch cases. |
| `index_access`, `bind_index_buffer2` | [IndexAccess](../testfiles/robustness/IndexAccess.md) | Robust indexed draws, sized index-buffer bindings, indirect modes, and device-address variants. |
| `robustness2`, `image_robustness`, `pipeline_robustness` | [Exts](../testfiles/robustness/Exts.md) | Extension feature matrices, descriptor/resource types, image views, pipeline robustness, and null descriptors. |
| `non_robust_buffer_access` | [NonRobustBufferAccess](../testfiles/robustness/NonRobustBufferAccess.md) | Amber programs whose invalid buffer references remain in unexecuted branches. |
| `robustness1_vertex_access` | [Robustness1VertexAccess](../testfiles/robustness/Robustness1VertexAccess.md) | Stride, padding, allocation, and binding-layout variants for robust vertex fetch. |
| `oob_access` | [OOBAccess](../testfiles/robustness/OOBAccess.md) | Robust-on/off texel-buffer and storage-image compute cases and their resource-specific verdicts. |

## Category Notes

The registration source contains additional helper and dispatcher code, but this rewrite keeps registration-only facts here rather than creating a separate implementation page for `vktRobustnessTests.cpp`. The eight Level-3 pages above cover the implementation-bearing families from the approved rewrite outline.
