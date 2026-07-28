# Understanding Brief: `binding_model.unused_invalid_descriptor`

## One-Sentence Test Purpose

This test checks whether a partially bound descriptor array can contain an undefined, access-incompatible, or copied undefined element when shader execution accesses only the two valid elements.

## Background Knowledge

### Static use and dynamic use are different tests

Vulkan defines static use on shader objects: an entry point statically uses an object when its call tree contains an instruction that uses the object's pointer, or when the entry point lists the variable in its interface. Dynamic descriptor use is narrower. A descriptor is dynamically used only when a shader invocation executes an instruction that performs a memory access through it.

Why it matters here:

- The generated shader statically uses the resource variable at set `0`, binding `1` and indexes its array through a push constant.
- The binding has three API-side elements, while the generated shader declares two elements and the host pushes `index = 0`. Shader invocations therefore access elements `0` and `1`, never element `2`.
- `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT` changes the population requirement for that binding from statically used descriptors to dynamically used descriptors. The two accessed elements must be populated and valid; element `2` need not be.
- The separate sampler at binding `2` is statically and dynamically used only by the `sampled_image` shader. Other resource variants still write that descriptor on the host, but their compiled shader does not use it.

The Vulkan definitions appear in [Static Use](../../../../vulkan-docs/src/chapters/shaders.adoc#shaders-staticuse), [`VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#VkDescriptorBindingFlagBits), and [descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptor-validity).

### Undefined, access-incompatible, and copied descriptors

These states are related but not interchangeable:

- A newly allocated descriptor is undefined until an update populates it. Destroying its underlying resource or view also makes the descriptor undefined.
- The `write.invalid` cases populate element `2` with live image objects that are incompatible with the generated shader if accessed. Sampled-image variants use a four-sample image with a non-multisampled `texture2D` declaration. The storage-image variant uses `VK_FORMAT_R32_UINT` with an `rgba32f` declaration and float image operations.
- Vulkan permits copying a descriptor that references a destroyed resource and permits copying an undefined descriptor. The destination descriptor becomes undefined. Copying the reference does not use the referenced resource.
- None of these allowances applies to elements `0` or `1`. The shader accesses both, so they must remain valid and produce the expected values.

See [descriptor initial state](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptor-set-initial-state), [descriptor copying](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-sets-updates), [texel input validation](../../../../vulkan-docs/src/chapters/textures.adoc#textures-input-validation), and the SPIR-V [sample-count rule](../../../../vulkan-docs/src/appendices/spirvenv.adoc#VUID-RuntimeSpirv-samples-08725).

## One Concrete Example

Consider `dEQP-VK.binding_model.unused_invalid_descriptor.write.invalid.sampled_image`.

- The descriptor set layout gives binding `1` three sampled-image descriptors and marks the binding partially bound.
- The shader declares `texture2D u_textures[2]`, reads `u_textures[ndx + 0]` and `u_textures[ndx + 1]`, and receives `ndx = 0` through a push constant.
- Elements `0` and `1` reference single-sample images cleared to `(0.5, 0.5, 0.5, 0.5)`.
- Element `2` references a four-sample image. That image would not match the shader's non-multisampled `texture2D` type if a shader invocation accessed it.
- Each invocation adds the two accessed values and writes `(1.0, 1.0, 1.0, 1.0)` to the result image. Element `2` contributes nothing because no invocation accesses it.

The example separates an access-incompatible descriptor from a dynamically accessed descriptor. Merely placing the former in a bound set does not make its image referenced during command execution when the partially bound rules determine that the descriptor is not dynamically used.

## End-to-End Test Flow

```text
[host] select write.unused, write.invalid, or copy and one registered resource type
[host] verify descriptor indexing, partially bound, and resource-array dynamic-indexing support
[host] generate one compute shader for the selected resource type
[host] create a 32 by 32 rgba32f result image and a host-visible readback buffer
[host] create and initialize the valid input resources to four components of 0.5
[host] create a three-element binding 1 with VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT
[host] populate or copy descriptors according to the selected behavior
[host] push index = 0, bind the compute pipeline and destination descriptor set, and dispatch 32 by 32 by 1
[device] each invocation reads binding 1 elements 0 and 1, adds them, and writes the result image
[host] copy the result image to the readback buffer and wait for completion
[host] compare every pixel exactly with (1.0, 1.0, 1.0, 1.0)
[host] repeat the flow for each compute-capable queue selected by MultiQueueRunnerTestInstance
```

The update step differs by behavior:

1. `write.unused` writes elements `0` and `1` and leaves element `2` undefined.
2. `write.invalid` also writes element `2`, but uses a live image that would be incompatible with the shader declaration if accessed.
3. `copy` writes all three source elements, destroys the resource behind source element `2`, copies bindings `0`, `1`, and `2` into a destination set, and executes with the destination. Destination element `2` is undefined after the copy; elements `0` and `1` remain valid.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`getResourceDeclaration()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L245-L293) emits one of five binding `1` forms: uniform-buffer block array, storage-buffer block array, `texture2D` array, `sampler2D` array, or `rgba32f image2D` array. Every shader-side array has two elements.
- [`getResourceAccess()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L295-L337) emits two accesses, indexed as `ndx + 0` and `ndx + 1`.
- Both [`UnusedInvalidDescriptorWriteTestCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L635-L655) and [`InvalidDescriptorCopyTestCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L982-L1002) build the same compute-shader shape. No explicit `ShaderBuildOptions` are supplied, so the CTS baseline target is SPIR-V 1.0.
- The shader has no explicit local-size declaration, so GLSL uses a local size of `1, 1, 1`. A `32, 32, 1` dispatch therefore produces one invocation per output pixel.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result image at set `0`, binding `0` | yes | yes | shader writes | copied to readback | Carries the per-pixel sum used for validation. |
| Binding `1` element `0` | yes | yes | shader reads | no | First valid input, initialized to `0.5` in every component. |
| Binding `1` element `1` | yes | yes | shader reads | no | Second valid input, initialized to `0.5` in every component. |
| Binding `1` element `2` | behavior-dependent | yes as undefined or access-incompatible state | no | no | Carries the state under test and must remain dynamically unaccessed. |
| Separate sampler at set `0`, binding `2` | yes | yes | sampled-image shader reads; other variants do not | no | Completes the separate sampled-image access. |
| Push constant `index` | yes | pipeline state | shader reads | no | The host sets it to zero, fixing actual accesses to elements `0` and `1`. |
| Host-visible readback buffer | yes | transfer destination | transfer writes | yes | Receives the result image for exact comparison. |

Buffer inputs contain one `vec4` and use host-visible memory. Image inputs are 32 by 32, are cleared to `0.5`, and transition to `VK_IMAGE_LAYOUT_GENERAL` before compute access. The result image uses `VK_FORMAT_R32G32B32A32_SFLOAT` and starts with a red clear value so missing shader writes do not resemble the expected white result.

## What Is Checked

- Each available compute-capable queue path produces a complete 32 by 32 result image.
- Every pixel must equal `(1.0, 1.0, 1.0, 1.0)` with a zero threshold in `tcu::floatThresholdCompare`.
- A matching image proves that the two valid elements were accessed and summed. It also proves that the element under test did not replace or corrupt those accesses.
- The host does not inspect element `2` directly. Its evidence is negative and behavioral: execution completes and the valid elements alone determine every output pixel.

## Behavior Parameter Identification

> **Behavior parameter:** descriptor state and update path (behavioral group)
>
> **Candidate values:** `write.unused`, `write.invalid`, `copy`

The resource type is a second dimension that changes declaration and access form. The three values above change the descriptor state being tolerated and therefore form the primary behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `write.unused` | Incorrect handling of an undefined, dynamically unaccessed array element in a partially bound descriptor binding. |
| `write.invalid` | Incorrect validation or execution treatment of a live but access-incompatible image descriptor that no invocation accesses. |
| `copy` | Incorrect copying or later consumption of a destination binding whose unaccessed element became undefined after its source resource was destroyed. |

A mismatch shared by all three values can instead come from their common dynamic indexing, descriptor selection, resource initialization, compute execution, transfer, or host comparison path.

## Important Variations and Special Cases

- `write.unused` and `copy` cover `uniform_buffer`, `storage_buffer`, `sampled_image`, `combined_image_sampler`, and `storage_image`.
- `write.invalid` covers only image descriptors because this implementation creates a controlled access incompatibility with image sample count or format. It does not register buffer variants.
- For sampled and combined image descriptors, the access-incompatible image uses `VK_SAMPLE_COUNT_4_BIT`; the ordinary inputs use `VK_SAMPLE_COUNT_1_BIT`. Four samples are used because Vulkan requires support for that count for the relevant distinction, avoiding an extra optional sample-count assumption.
- For storage images, the access-incompatible image view uses `VK_FORMAT_R32_UINT`, while the shader declares `rgba32f image2D` and performs a float `imageLoad`.
- All cases require `VK_EXT_descriptor_indexing` functionality, `descriptorBindingPartiallyBound`, and the dynamic-indexing feature for the selected resource class.
- The family is registered only outside `CTS_USES_VULKANSC`.
- Design pruning keeps the generated shader fixed at two actual inputs. There is no path that pushes a nonzero index or intentionally accesses element `2`, because that would violate the condition under which the undefined or access-incompatible descriptor is allowed.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Resource kinds and image incompatibilities | [`ResourceType`, `makeImageCI()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L57-L214) | Defines all five resource classes, four-sample image variants, and the `VK_FORMAT_R32_UINT` storage-image variant. |
| Generated declarations and accesses | [`getResourceDeclaration()`, `getResourceAccess()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L245-L337) | Shows the two-element shader arrays and the two indexed accesses. |
| Resource creation and initialization | [`Resource`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L339-L599) | Creates buffers, images, views, samplers, memory, and `0.5` input data. |
| Write shader and support gates | [`initPrograms()`, `commonCheckSupport()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L635-L699) | Generates the compute program and checks descriptor indexing features. |
| Write execution and validation | [`UnusedInvalidDescriptorWriteTestInstance::queuePass()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L701-L946) | Builds the partially bound set, writes the selected state, dispatches, copies back, and compares. |
| Copy construction | [`InvalidDescriptorCopyTestInstance::queuePass()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1014-L1279) | Destroys source element `2`, copies three elements, and executes with the destination set. |
| Registration | [`createUnusedInvalidDescriptorTests()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1283-L1354) | Defines `write.unused`, `write.invalid`, `copy`, and exact resource leaves. |
| Category registration boundary | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L71) | Registers the family only for Vulkan, not Vulkan SC. |
| Mustpass evidence | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L146935-L146947) | Lists all thirteen executable paths. |
| Queue iteration | [`MultiQueueRunnerTestInstance`](../../../modules/vulkan/vktTestCase.cpp#L1815-L1877) | Runs the case on the available compute-capable queue paths and aggregates failures. |
| Descriptor population and dynamic-use rules | [Descriptor Sets](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptor-set-initial-state) | Defines undefined descriptors and the effect of partially bound bindings. |
| Copying undefined descriptors | [Descriptor Set Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-sets-updates) | States that copying does not use the resource and that an undefined source makes the destination undefined. |
| Shader and image compatibility | [Texel Input Validation](../../../../vulkan-docs/src/chapters/textures.adoc#textures-input-validation) | Defines sample-count, sampled-type, and image-format compatibility when an image is accessed. |

## Questions / Risk Points for User Audit

All semantic risk points found during investigation are resolved:

- The primary axis uses three behavioral groups. The direct `write` child divides into `write.unused` and `write.invalid` because they create different descriptor states; `copy` supplies the third group.
- Element `2` is described as dynamically unaccessed. The page does not claim that a descriptor array variable containing runtime indexing is statically unused.
- `write.invalid` is described as access-incompatible rather than undefined. Its image and view remain live through execution.
- `copy` is described as a legal copy that propagates undefined state after destruction of the source resource, not as a forbidden copy operation.
- The pass result is limited to this generated workload and checked output. It does not support a blanket claim about a hardware or driver implementation.

## Conversion Notes for Final Wiki Rewrite

- Keep the static-use versus dynamic-use distinction compact in final Background Knowledge.
- Use `write.unused`, `write.invalid`, and `copy` as the Behavior Parameters subsections.
- Preserve one sampled-image walkthrough because it exposes dynamic indexing, the two accessible elements, the undeclared third API-side element, and the exact output signal. Summarize buffer, combined-image-sampler, storage-image, and copy differences in the variation table.
- Preserve the resource-state distinction in runtime prose: never written, written but access-incompatible, and copied undefined.
- Copy the `### Failure Cause Mapping` table above byte-for-byte into the final page.
- Keep source navigation in the appendix and retain the exact Vulkan spec links for descriptor validity, partially bound behavior, copying, and image compatibility.
