## Test Intent

The extension tests ask whether valid accesses preserve their initialized values while out-of-bounds and null accesses return only values permitted by the active robustness contract. The same generator covers `robustness2`, `image_robustness`, and non-VulkanSC `pipeline_robustness`, so the important distinction is where the contract comes from and which resource classes it covers.

## Registration Scope

- `robustness.robustness2`: `bind`, non-VulkanSC `push`, `misc`, and non-VulkanSC `64b_indexing`.
- `robustness.image_robustness`: `bind` and non-VulkanSC `push`.
- Non-VulkanSC `robustness.pipeline_robustness`: nested `robustness2` and `image_robustness` families.
- The generator expands descriptor update mode, format, descriptor/resource type, access modifiers, image shape, shader stage, queue, and pipeline-construction variants.

Evidence: [root factories](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4311-L4372), [matrix generator](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3840-L4308), and [mustpass paths](../../../mustpass/main/vk-default/robustness.txt#L1866-L96873).

## Core Mechanism

1. Create a custom device that enables the requested robustness features.
2. Initialize buffers or images with deterministic reference data.
3. Generate a shader that performs both valid and deliberately invalid accesses.
4. Compare valid reads with the reference data and invalid reads with the selected robustness result set.
5. Encode success as `(1,0,0,1)` and failure as `(0,0,0,0)` in an 8-by-8 storage image.
6. Copy the result to host-visible memory and check every pixel.

The separate `misc.out_of_bounds_stride*` cases verify that a vertex attribute fully inside the buffer remains in bounds even when the complete stride chunk extends beyond the buffer.

## Behavior Parameter Identification

The primary behavioral axis is the robustness mode:

- `robustness2`: strict robust buffer/image and null-descriptor behavior enabled as device features; includes reduced `64b_indexing` storage-buffer coverage.
- `image_robustness`: image-only robustness with the extension's permitted zero-or-one alpha behavior.
- `pipeline_robustness`: robustness selected through `VkPipelineRobustnessCreateInfoEXT` for monolithic or graphics-pipeline-library construction.

`bind` versus `push`, formats, resource types, stages, and access modifiers are important coverage dimensions, but they change the route through the implementation rather than the core correctness contract.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `robustness2` | Incorrect robust buffer/image result, broken null-descriptor semantics, or corruption of an in-bounds access. |
| `image_robustness` | Image access returned a value outside the extension's permitted result set or changed valid texels. |
| `pipeline_robustness` | Pipeline robustness state was ignored, attached to the wrong pipeline component, or applied to the wrong resource category. |

## Case Selection and Pruning

- Requirement checks cover robustness features, push descriptors, ray tracing, scalar layout, shader stores/atomics, 64-bit indexing and formats, dynamic vertex stride, and requested queues.
- Pipeline-robustness and `64b_indexing` matrices use reduced format sets.
- Pipeline robustness further reduces descriptor types, samples, view types, lengths, null descriptors, and ray-generation combinations.
- `64b_indexing` keeps storage-buffer cases only.

These reductions preserve distinct behavior while preventing the cross-product from duplicating equivalent coverage.

## Evidence Pointers

| Topic | Link |
|-------|------|
| Feature/device setup | [vktRobustnessExtsTests.cpp lines 69–180](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L69-L180) |
| Support checks | [vktRobustnessExtsTests.cpp lines 519–738](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L519-L738) |
| Shader generation and comparisons | [vktRobustnessExtsTests.cpp lines 1070–1993](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1070-L1993) |
| Runtime and host validation | [vktRobustnessExtsTests.cpp lines 2021–3495](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2021-L3495) |
| Stride tests | [vktRobustnessExtsTests.cpp lines 3497–3820](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3497-L3820) |
| Registration and pruning | [vktRobustnessExtsTests.cpp lines 3840–4372](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3840-L4372) |
