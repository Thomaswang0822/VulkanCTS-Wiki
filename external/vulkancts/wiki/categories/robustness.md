# Vulkan CTS Robustness Tests

The `robustness` category verifies Vulkan behavior around robust buffer, image, vertex-input, index-buffer, descriptor,
pipeline-robustness, and non-robust unexecuted out-of-bounds access scenarios. The category root is registered in the
standard Vulkan package and Vulkan SC package as `robustness`, then delegates most generation and verification logic to
implementation files under `modules/vulkan/robustness`.

## Registration Entry Point

The Vulkan package root attaches the category through `addRootChild("robustness", ..., robustness::createTests)` in
[vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1372-L1374); the Vulkan SC package does the same in
[vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1438-L1441). The category factory is
`robustness::createTests()`, which constructs the category group from the caller-provided name and registers direct child
groups in [vktRobustnessTests.cpp](../../modules/vulkan/robustness/vktRobustnessTests.cpp#L61-L99).

## Subgroup Structure

The root dispatcher registers the following direct children. Display names below are the verified registered group names
created by implementation files, not factory-symbol names.

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

Evidence for this structure:

- The dispatcher adds `buffer_access`, `vertex_access`, and `index_access` first, then searches for `buffer_access` and
  inserts `through_pointers` below it in
  [vktRobustnessTests.cpp](../../modules/vulkan/robustness/vktRobustnessTests.cpp#L65-L82).
- It adds `robustness2`, `image_robustness`, optional `pipeline_robustness`, `non_robust_buffer_access`, optional
  `pipeline_robustness_buffer_access`, optional `bind_index_buffer2`, optional `descriptor_heap_buffer_access`,
  `robustness1_vertex_access`, and `oob_access` in
  [vktRobustnessTests.cpp](../../modules/vulkan/robustness/vktRobustnessTests.cpp#L84-L97).
- The registered literal group names are verified in the implementation files: `buffer_access`,
  `pipeline_robustness_buffer_access`, and `descriptor_heap_buffer_access` in
  [vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2097-L2122);
  `through_pointers` in
  [vktRobustBufferAccessWithVariablePointersTests.cpp](../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1897-L1902);
  `vertex_access` in
  [vktRobustnessVertexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1290-L1296);
  `index_access` and `bind_index_buffer2` in
  [vktRobustnessIndexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1132-L1204);
  `robustness2`, `image_robustness`, and `pipeline_robustness` in
  [vktRobustnessExtsTests.cpp](../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4311-L4372);
  `non_robust_buffer_access` in
  [vktNonRobustBufferAccessTests.cpp](../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L57);
  `robustness1_vertex_access` in
  [vktRobustness1VertexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L943-L951);
  and `oob_access` in
  [vktRobustnessOOBAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L965-L1058).
- The default Vulkan mustpass list contains direct prefixes for these registered roots, for example `bind_index_buffer2`
  and `buffer_access` near the start of
  [robustness.txt](../../mustpass/main/vk-default/robustness.txt#L1-L42), `index_access`, `non_robust_buffer_access`, and
  `oob_access` in [robustness.txt](../../mustpass/main/vk-default/robustness.txt#L13746-L13874), and `vertex_access` in
  [robustness.txt](../../mustpass/main/vk-default/robustness.txt#L96874-L96963).

## File Inventory

| File | Role | Registered groups / purpose |
|------|------|-----------------------------|
| [vktRobustnessTests.cpp](../../modules/vulkan/robustness/vktRobustnessTests.cpp#L25-L99) | Root registration / dispatcher | Registers direct category children and inserts `through_pointers` under `buffer_access`. |
| [vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1930-L2122) | Implementation with local registration | Generates `buffer_access`, `pipeline_robustness_buffer_access`, and `descriptor_heap_buffer_access` matrices. |
| [vktRobustBufferAccessWithVariablePointersTests.cpp](../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1897-L2001) | Nested implementation with local registration | Generates `buffer_access.through_pointers` read/write cases using SPIR-V variable pointers. |
| [vktRobustnessVertexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1190-L1296) | Implementation with local registration | Generates `vertex_access` format groups and draw/draw-indexed vertex-input OOB cases. |
| [vktRobustnessIndexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1116-L1204) | Implementation with local registration | Generates `index_access` and non-VulkanSC `bind_index_buffer2`. |
| [vktRobustnessExtsTests.cpp](../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3840-L4372) | Implementation with local registration | Generates `robustness2`, `image_robustness`, and non-VulkanSC `pipeline_robustness`. |
| [vktNonRobustBufferAccessTests.cpp](../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L57) | Compact Amber registration | Registers `non_robust_buffer_access` Amber tests outside Vulkan SC builds. |
| [vktRobustness1VertexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L951) | Implementation with local registration | Generates four `robustness1_vertex_access` stride/layout leaves. |
| [vktRobustnessOOBAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L965-L1058) | Implementation with local registration | Generates `oob_access.robust_on` and `oob_access.robust_off` compute cases. |
| [vktRobustnessUtil.cpp](../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L53-L500) and [vktRobustnessUtil.hpp](../../modules/vulkan/robustness/vktRobustnessUtil.hpp#L41-L149) | Helper files | Shared robust-device creation, value predicates, deterministic buffer population, and compute/graphics environments; no direct registered group was observed. |
| Header files in [robustness/](../../modules/vulkan/robustness/) | Declarations | Public factory declarations and helper declarations corresponding to the implementation files. |

## Recurring Test Families and Themes

- **Buffer out-of-bounds access**: `buffer_access`, `pipeline_robustness_buffer_access`, and
  `descriptor_heap_buffer_access` share one generator for uniform/storage buffers, uniform/storage texel buffers,
  compute/graphics stages, regular descriptor range overrun, and `out_of_alloc` backing-allocation overrun
  ([vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1930-L2095)).
- **Variable-pointer storage-buffer robustness**: `buffer_access.through_pointers` builds SPIR-V assembly with
  `VariablePointersStorageBuffer` and `SPV_KHR_variable_pointers`, then exercises read/write paths through selected
  pointer values in compute and graphics stages
  ([vktRobustBufferAccessWithVariablePointersTests.cpp](../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L839-L1239)).
- **Vertex-input robustness**: `vertex_access` sweeps vertex formats through `draw` and `draw_indexed` leaves, while
  `robustness1_vertex_access` focuses on stride, padding, and binding-layout patterns for robustBufferAccess behavior
  ([vktRobustnessVertexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1190-L1287),
  [vktRobustness1VertexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L389)).
- **Index-buffer robustness**: `index_access` manipulates `firstIndex` and draw mode with robustness2 enabled, while
  `bind_index_buffer2` varies binding offset, binding size, out-of-range index values, and device-address command variants
  ([vktRobustnessIndexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1116-L1204)).
- **Extension robustness matrices**: `robustness2`, `image_robustness`, and `pipeline_robustness` generate descriptor,
  format, null-descriptor, shader-stage, image-view, and pipeline-construction matrices from shared arrays and loop nests
  ([vktRobustnessExtsTests.cpp](../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3840-L4291)).
- **Compute OOB resource access**: `oob_access` generates robust-on/off texel-buffer and storage-image compute cases,
  separating defined robust results from successful-execution-only non-robust image cases
  ([vktRobustnessOOBAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L965-L1058)).
- **Non-robust unexecuted branches**: `non_robust_buffer_access` registers Amber compute tests where out-of-bounds
  accesses remain in unexecuted branches and the executed branch output must match an expected buffer
  ([vktNonRobustBufferAccessTests.cpp](../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L57)).

## Recurring Parameter Dimensions

| Dimension | Observed examples | Evidence |
|-----------|-------------------|----------|
| Shader stage / execution path | `vertex`, `fragment`, `compute`; extension tests also include `rgen` outside Vulkan SC | Buffer-access stage array in [vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1906-L1943); extension stage cases in [vktRobustnessExtsTests.cpp](../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3912-L3923). |
| Resource or descriptor type | Uniform/storage buffers, uniform/storage texel buffers, storage images, sampled images, vertex attribute fetch, descriptor heap resources | Buffer shader/access construction in [vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L318-L574); extension descriptor arrays in [vktRobustnessExtsTests.cpp](../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3864-L3879). |
| Format width and numeric type | `r32_*`, `r64_*`, vector formats, packed `a2b10g10r10_unorm_pack32`, extension format groups such as `r32ui` and `rgba32f` | Vertex format array in [vktRobustnessVertexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1258-L1275); buffer format arrays in [vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1945-L1951); extension format cases in [vktRobustnessExtsTests.cpp](../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3850-L3862). |
| Access direction and operation type | OOB uniform reads, storage reads, storage writes; explicit `read`/`write` leaves; `draw`, `draw_indexed`, indirect-count, multi-draw variants | Buffer access operation subgroups in [vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2027-L2058); OOB read/write loops in [vktRobustnessOOBAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L990-L1051); index draw mode arrays in [vktRobustnessIndexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1118-L1123). |
| Robustness mode | `robust_on`/`robust_off`, robustBufferAccess, robustBufferAccess2, robustImageAccess, pipeline robustness | OOB robust branch generation in [vktRobustnessOOBAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L973-L1058); extension robust-feature selection in [vktRobustnessExtsTests.cpp](../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L519-L738). |
| OOB distance / range / size | 1/3/4/32 byte ranges, 1/3 texel ranges, `out_of_alloc`, variable-pointer `1B` through `32B`, image extents `16x16` through `128x128`, index binding offsets `0` and `100` | Buffer ranges in [vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1953-L1963); variable-pointer ranges in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1929-L1984); OOB image extents in [vktRobustnessOOBAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L1034-L1050); index offsets in [vktRobustnessIndexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1132-L1140). |
| Descriptor update mode and pipeline construction | `bind`, `push`, descriptor templates, null descriptors, monolithic and graphics-pipeline-library pipeline robustness | Extension generator arrays and loop nest in [vktRobustnessExtsTests.cpp](../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3940-L4291). |

## Recurring Support and Feature Gates

- **Build-profile gates**: `pipeline_robustness`, `pipeline_robustness_buffer_access`, `bind_index_buffer2`, and
  `descriptor_heap_buffer_access` are registered only outside Vulkan SC builds in
  [vktRobustnessTests.cpp](../../modules/vulkan/robustness/vktRobustnessTests.cpp#L86-L95). `non_robust_buffer_access` is
  registered as a group in all builds, but its Amber children are added only outside Vulkan SC in
  [vktNonRobustBufferAccessTests.cpp](../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L48-L55).
- **Robust-buffer feature setup**: several families create a dedicated device with `robustBufferAccess` enabled rather
  than relying on the default context device
  ([vktRobustnessUtil.cpp](../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L53-L92),
  [vktRobustness1VertexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L861-L884)).
- **Robustness2 and image robustness**: robustness2 cases require `VK_KHR_robustness2` or `VK_EXT_robustness2` feature
  support, and image robustness cases require `VK_EXT_image_robustness` / robust image access support in their respective
  checks
  ([vktRobustnessExtsTests.cpp](../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L519-L546),
  [vktRobustnessOOBAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L578-L586)).
- **Pipeline and descriptor-heap extensions**: pipeline-robustness buffer tests require `VK_EXT_pipeline_robustness`, and
  descriptor-heap buffer tests require `VK_EXT_descriptor_heap` plus buffer-device-address support
  ([vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L741-L768),
  [vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L843-L875)).
- **Shader/storage capabilities**: 64-bit formats and OOB R64 cases require `shaderInt64` and, where images/atomics are
  involved, int64 atomic/image features
  ([vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L308-L310),
  [vktRobustnessOOBAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L145-L160)).
  Graphics-stage storage writes require stage store features such as `vertexPipelineStoresAndAtomics` and
  `fragmentStoresAndAtomics`
  ([vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L311-L315)).
- **Feature-specific branches**: variable-pointer tests require `variablePointersStorageBuffer`
  ([vktRobustBufferAccessWithVariablePointersTests.cpp](../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L214-L224));
  indirect-count and multi-draw index tests require their draw extensions, and device-address variants require
  `VK_KHR_device_address_commands`
  ([vktRobustnessIndexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L499-L523)).

## Recurring Verification Methods

- **Memory-content verification after dispatch/draw**: buffer-access and variable-pointer tests initialize known input and
  output data, run compute or graphics work, invalidate output memory, and classify each slot as in-bounds,
  partially out-of-bounds, or out-of-bounds
  ([vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1591-L1851),
  [vktRobustBufferAccessWithVariablePointersTests.cpp](../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1589-L1848)).
- **Allowed robust OOB values**: verifiers generally accept deterministic in-bounds values, zero, unchanged destination
  bytes for writes, and specific helper-approved vector patterns where the implementation may legally return a value from
  the accessible backing range
  ([vktRobustnessUtil.cpp](../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L166-L243),
  [vktRobustnessBufferAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1727-L1807)).
- **Rendered-image verdicts**: vertex and index families render deterministic geometry and then compare selected pixels or
  the full image to expected colors
  ([vktRobustnessVertexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1005-L1179),
  [vktRobustness1VertexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L761-L779),
  [vktRobustnessIndexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L415-L461),
  [vktRobustnessIndexAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1080-L1113)).
- **Extension-matrix copy-back and comparisons**: robustness extension tests set up descriptors/images/buffers, execute
  the selected shader path, then copy results back and compare against expected robust values
  ([vktRobustnessExtsTests.cpp](../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2021-L3495)).
- **OOB resource-specific checks**: OOB texel-buffer `rba2` reads require zero and writes require unchanged backing data;
  robust image reads require zero and writes require unchanged image data, while non-robust storage-image cases pass after
  successful execution in the inspected branch
  ([vktRobustnessOOBAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L517-L540),
  [vktRobustnessOOBAccessTests.cpp](../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L926-L948)).
- **Amber equality checks**: non-robust unexecuted-branch cases use Amber `EXPECT ... EQ_BUFFER ...` after compute dispatch
  rather than local C++ comparison logic
  ([vktNonRobustBufferAccessTests.cpp](../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L49-L54)).

## Level-3 Documentation

| Level-3 page | Registered scope |
|--------------|------------------|
| [vktRobustnessTests](../testfiles/robustness/vktRobustnessTests.md) | Root dispatcher for `robustness`. |
| [vktRobustnessBufferAccessTests](../testfiles/robustness/vktRobustnessBufferAccessTests.md) | `buffer_access`, `pipeline_robustness_buffer_access`, `descriptor_heap_buffer_access`. |
| [vktRobustBufferAccessWithVariablePointersTests](../testfiles/robustness/vktRobustBufferAccessWithVariablePointersTests.md) | `buffer_access.through_pointers`. |
| [vktRobustnessVertexAccessTests](../testfiles/robustness/vktRobustnessVertexAccessTests.md) | `vertex_access`. |
| [vktRobustnessIndexAccessTests](../testfiles/robustness/vktRobustnessIndexAccessTests.md) | `index_access`, `bind_index_buffer2`. |
| [vktRobustnessExtsTests](../testfiles/robustness/vktRobustnessExtsTests.md) | `robustness2`, `image_robustness`, `pipeline_robustness`. |
| [vktNonRobustBufferAccessTests](../testfiles/robustness/vktNonRobustBufferAccessTests.md) | `non_robust_buffer_access`. |
| [vktRobustness1VertexAccessTests](../testfiles/robustness/vktRobustness1VertexAccessTests.md) | `robustness1_vertex_access`. |
| [vktRobustnessOOBAccessTests](../testfiles/robustness/vktRobustnessOOBAccessTests.md) | `oob_access`. |

## Scope and Uncertainty

- This Level-2 page was synthesized from the generated Level-3 pages and direct inspection of the robustness root,
  implementation files, shared helper files, package registration, and the default Vulkan mustpass list. It intentionally
  does not edit Level-3 pages or the wiki README.
- The subgroup tree uses verified registered names from implementation `TestCaseGroup` construction and mustpass evidence.
  It does not use factory-symbol names as display names.
- Vulkan SC statements are limited to visible `CTS_USES_VULKANSC` guards in inspected source. Vulkan SC mustpass files were
  not inspected for this page.
- The default mustpass file is large; line-linked examples are used as coverage evidence for registered prefixes and
  representative generated families, not as a complete enumeration of every leaf.
