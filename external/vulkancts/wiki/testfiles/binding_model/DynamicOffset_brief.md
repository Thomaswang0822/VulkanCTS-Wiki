# Understanding Brief: `binding_model.dynamic_offset`

## One-Sentence Test Purpose

This test checks whether dynamic uniform and storage buffer offsets keep selecting the intended buffer ranges when shaders and descriptor state move between pipelines with different or shared layouts, optional extra descriptor sets, and push constants recorded at different times.

## Background Knowledge

### Dynamic buffer descriptors and offset ordering

A dynamic buffer descriptor has a base offset and range from its descriptor update. `vkCmdBindDescriptorSets` adds a dynamic offset when the set is bound. Vulkan consumes one offset for every dynamic descriptor in every bound set, ordered first by set number, then binding number, then array element ([dynamic offset order and effective address](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4627-L4643)).

Why it matters here:

- A layout binding can consume a dynamic offset even when the selected shader does not use that binding.
- The offset for a uniform buffer must satisfy `minUniformBufferOffsetAlignment`; the storage-buffer offset must satisfy `minStorageBufferOffsetAlignment` ([dynamic-offset valid usage](../../../../vulkan-docs/src/chapters/commonvalidity/bind_descriptor_sets_common.adoc#L14-L35)).

### Pipeline-layout compatibility and push constants

A pipeline layout combines an ordered sequence of descriptor-set layouts with push-constant ranges ([Pipeline Layouts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1168-L1179)). Two layouts are compatible for set N only when the set layouts through N are identically defined and the push-constant ranges are identical. Compatible bindings can remain valid across a pipeline change; incompatible bindings may be disturbed and must be rebound ([Pipeline Layout Compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2021-L2055)).

Push-constant values are command-buffer state. Binding an incompatible pipeline does not erase them, but a dispatch that reads them must use a pipeline layout compatible with the layout used for the update ([Push Constant Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L5156-L5208)).

Why it matters here:

- The generated cases either give both pipelines one layout or use a first layout without a push-constant range and a second layout with one.
- Some cases update 128 bytes of push constants before any descriptor or pipeline binding, while others update them near the dispatch that consumes them.

## One Concrete Example

Use this executable leaf as the representative:

```text
dEQP-VK.binding_model.dynamic_offset.two_pipelines_separate_offsets_pc_first_different_sets
```

The first pipeline uses descriptor set 0 with a dynamic uniform buffer at binding 0 and a dynamic storage buffer at binding 1. Its one-invocation `comp0` shader copies the second aligned input item, `(1, 2, 3, 4)`, to the second aligned output item.

The second pipeline has a different layout. Set 0 retains both dynamic bindings, even though `comp1` only declares its input binding. Set 1 adds a dynamic storage buffer at binding 0, and `comp1` writes there. The second bind therefore supplies three offsets in exact layout order:

| Offset position | Set and binding | Selected byte offset |
|-----------------|-----------------|----------------------|
| 0 | set 0, binding 0, dynamic uniform buffer | `2 * itemSizeUniform` |
| 1 | set 0, binding 1, dynamic storage buffer unused by `comp1` | `2 * itemSizeStorage` |
| 2 | set 1, binding 0, dynamic storage buffer written by `comp1` | `2 * itemSizeStorage` |

Before either descriptor bind, the host records eight `vec4` push-constant values. The first is `(100, 200, 300, 400)` and the remaining seven are zero. `comp1` sums all eight values and writes `(100, 200, 300, 400)` to the third aligned output item. The first pipeline's incompatible layout does not erase the push-constant state before the second dispatch.

## End-to-End Test Flow

```text
1. Amber shader-reuse paths
[host] load one fixed Amber script for the compute or graphics leaf
[host] let Amber compile the script's embedded GLSL and create two separately described pipelines
[host] bind dynamic buffers at offset 0 for pipeline0 and offset 256 for pipeline1
[device] reuse the same compute shader, or the same vertex and fragment shaders, with the two pipeline layouts
[device] write two storage-buffer regions or render two colored framebuffer quadrants
[host] let Amber compare the named buffer or framebuffer regions with the script's EXPECT commands

2. Generated two-pipeline paths
[host] choose four Boolean parameters, generate comp0 and comp1 GLSL, and compile both compute shaders
[host] create aligned three-item input and output buffers, descriptor-set layouts, one or two pipeline layouts, and one or two descriptor sets
[host] update push constants at command start when pcFirst is true
[host] bind descriptorSet0 with the first offset list, bind pipeline0, optionally update push constants, and dispatch once
[device] comp0 copies its dynamically selected input vec4 to its dynamically selected output region
[host] issue a shader-write barrier, then rebind descriptors when layout compatibility or a changed offset requires it
[host] bind pipeline1, update push constants here when required, and dispatch once
[device] comp1 sums the eight push-constant vec4 values and writes through its dynamically selected output descriptor
[host] issue a shader-write-to-host-read barrier, submit, wait, invalidate output memory, and compare every output float with the constructed expected buffer
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The two Amber leaves load fixed scripts from [`binding_model/dynamic_offset`](../../../data/vulkan/amber/binding_model/dynamic_offset/). Their embedded GLSL belongs to the scripts; `vktBindingDynamicOffsetTests.cpp` does not generate it.
- The generated `two_pipelines*` leaves specialize one C++ string template into `comp0` and `comp1`. `comp0` copies its input and declares the push-constant block only for `singleLayout`. `comp1` always declares the 8-element block, replaces the input value with `pc.color[0]`, adds elements 1 through 7, and selects its output set from `differentSets` ([`DynamicOffsetPCCase::initPrograms`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L91-L149)).
- Neither generated shader supplies explicit shader build options, so the CTS default GLSL build target uses baseline SPIR-V 1.0 ([default source collections](../../../modules/vulkan/vktTestPackage.cpp#L476-L483), [baseline version](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Amber `buf` or `framebuffer` | by Amber from the loaded script | yes | written or sampled and rendered | checked by Amber | Makes offset 0 and offset 256 produce distinct expected regions. |
| Generated input buffer | yes | as `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC` | read by compute shaders | no | Contains zero, `(1, 2, 3, 4)`, and `(5, 6, 7, 8)` at device-aligned strides. |
| Generated output buffer | yes | as `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC` | written by both dispatches | yes | Holds the observable result at the selected aligned regions, including zero padding. |
| `descriptorSet0` | yes | set 0 | supplies dynamic input and output bindings | no | Used by pipeline0 and retained or rebound for pipeline1. |
| `descriptorSet1` | only for `differentSets` | set 1 | supplies pipeline1 output binding 0 | no | Makes descriptor-set selection and three-entry dynamic-offset ordering observable. |
| Push constants | yes | through pipeline layout state | read by `comp1` | no | Carry eight `vec4` values totaling 128 bytes; only the first is nonzero. |

## What Is Checked

- The Amber compute script requires `(1, 2, 3, 4)` at byte offsets 0 and 256 in `buf` after the two pipelines run.
- The Amber graphics script requires a red top-left quadrant, a green bottom-right quadrant, and black in the other two quadrants. Offset 0 selects red and offset 256 selects green.
- Generated cases build an expected output buffer on the host. The first dispatch copies `(1, 2, 3, 4)` to the first storage offset. The second dispatch writes `(100, 200, 300, 400)` to either that same offset or the doubled offset. When both use the same output offset, the second value replaces the first in the expected result.
- The host compares every float in the full aligned output allocation, including regions expected to remain zero. A mismatch logs the float index, expected value, and actual value. The case passes only if all floats match.

## Behavior Parameter Identification

> **Behavior parameter:** execution-flow behavioral group (the two direct Amber leaves and the generated `two_pipelines*` leaf cluster)
>
> **Candidate values:** `shader_reuse_differing_layout_compute`, `shader_reuse_differing_layout_graphics`, `two_pipelines*`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shader_reuse_differing_layout_compute` | Compute-shader reuse across differing pipeline layouts, storage dynamic-offset selection, or Amber buffer validation failure. |
| `shader_reuse_differing_layout_graphics` | Graphics-shader reuse across differing pipeline layouts, uniform dynamic-offset selection, rendering, or framebuffer validation failure. |
| `two_pipelines*` | Pipeline-layout compatibility or rebinding failure, push-constant ordering or preservation failure, descriptor-set or dynamic-offset ordering failure, or generated output synchronization and readback failure. |

## Important Variations and Special Cases

- `separateOffsets=false` makes both dispatches target the second aligned output item, so the second dispatch overwrites the first result. `true` doubles every second-dispatch offset and preserves both results in separate items.
- `pcFirst=true` records `vkCmdPushConstants` before descriptor and pipeline binding. When false, a shared-layout case updates before the first dispatch; a two-layout case updates after pipeline1 is bound.
- `singleLayout=true` gives both pipelines `pipelineLayout1`, makes `comp0` declare the push-constant block, and can preserve the first descriptor binding across the pipeline switch. A changed offset still forces a descriptor rebind.
- `differentSets=true` puts `comp1` output at set 1, binding 0. The second descriptor bind includes sets 0 and 1 and supplies three dynamic offsets. This choice never combines with `singleLayout`.
- The registered family contains 14 executable leaves in the current `vk-default` mustpass file: 2 Amber leaves and 12 generated leaves ([mustpass entries](../../../mustpass/main/vk-default/binding-model.txt#L46169-L46182)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Amber compute script | [`shader_reuse_differing_layout_compute.amber`](../../../data/vulkan/amber/binding_model/dynamic_offset/shader_reuse_differing_layout_compute.amber) | Defines the fixed compute shader, two pipelines, offsets, and buffer expectations. |
| Amber graphics script | [`shader_reuse_differing_layout_graphics.amber`](../../../data/vulkan/amber/binding_model/dynamic_offset/shader_reuse_differing_layout_graphics.amber) | Defines the fixed graphics shaders, two pipelines, offsets, draw regions, and framebuffer expectations. |
| Generated shader source | [`DynamicOffsetPCCase::initPrograms`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L91-L149) | Specializes the exact `comp0` and `comp1` GLSL forms. |
| Resource and layout setup | [`DynamicOffsetPCInstance::iterate`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L160-L293) | Creates aligned buffers, set layouts, pipeline layouts, descriptors, and push-constant data. |
| Command ordering and checking | [command recording through comparison](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L294-L385) | Applies the parameter choices and validates the complete output buffer. |
| Registration and design pruning | [`populateDynamicOffsetTests`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L388-L418) | Registers the Amber leaves and 12 valid generated combinations. |
| Vulkan and Vulkan SC split | [`createBindingModelTests`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L41-L68) | Registers `dynamic_offset` only for Vulkan. |
| Mustpass coverage | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L46169-L46182) | Confirms all 14 executable paths. |
| Dynamic descriptor contract | [Dynamic Offsets](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4627-L4649) | Defines offset count, ordering, effective address, and layout compatibility at bind time. |
| Pipeline-layout contract | [Pipeline Layout Compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2021-L2055) | Defines when descriptor state survives a pipeline change. |
| Push-constant contract | [Push Constant Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L5156-L5208) | Defines update state and compatibility at dispatch time. |
| Compute pipeline model | [Compute Pipelines](../../../../vulkan-docs/src/chapters/pipelines.adoc#L808-L820) | Identifies the compute shader and pipeline layout as the two parts relevant to generated pipeline creation. |

## Questions / Risk Points for User Audit

- The behavioral axis groups the two exact Amber leaves separately from the generated `two_pipelines*` cluster because they have different setup and validation engines.
- The Amber scripts are loaded artifacts. Only `comp0` and `comp1` are generated by the C++ source.
- The representative generated leaf is present in mustpass and exercises `separateOffsets`, `pcFirst`, and `differentSets` together.
- Source, scripts, mustpass, and specification text resolve the layout, ordering, validation, and pruning questions. No unresolved risk point changes the final page.

## Conversion Notes for Final Wiki Rewrite

- Keep dynamic-offset ordering, pipeline-layout compatibility, and push-constant state as the prerequisites.
- Use `two_pipelines_separate_offsets_pc_first_different_sets` for one analyzer-produced generated-shader walkthrough with validated SPIR-V 1.0.
- Explain both loaded Amber flows outside that generated walkthrough and preserve the distinction between script GLSL and C++-generated GLSL.
- Carry the execution-flow behavioral group into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table unchanged.
- Keep the full 12-row generated matrix, then explain the four Boolean dimensions and the pruned `singleLayout && differentSets` combinations.
