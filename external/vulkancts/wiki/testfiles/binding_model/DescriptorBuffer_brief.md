# Understanding Brief: `binding_model.descriptor_buffer`

## One-Sentence Test Purpose

This test checks whether an implementation can encode, place, bind, and access `VK_EXT_descriptor_buffer` descriptors across traditional and sparse buffer modes while preserving each scenario's descriptor, shader-stage, synchronization, robustness, and readback contract.

## Background Knowledge

### Descriptor bytes are located through several independent offsets

A descriptor buffer replaces an allocated descriptor set with application-managed bytes. The implementation reports the byte size of a set layout and the byte offset of each binding. `vkGetDescriptorEXT` supplies opaque bytes for ordinary descriptors, while inline uniform data is written directly. At shader access time, Vulkan locates an array element at:

```text
bufferAddress + setOffset + bindingOffset + arrayElement * descriptorSize
```

The buffer address comes from `vkCmdBindDescriptorBuffersEXT`; the set-to-buffer index and set offset come from `vkCmdSetDescriptorBufferOffsetsEXT`; and the binding offset comes from `vkGetDescriptorSetLayoutBindingOffsetEXT` ([Descriptor Buffers](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L12-L122)).

Why it matters here:

- The test varies the number of bound buffers, sets packed into each buffer, descriptor array lengths, and a deliberately shifted buffer address.
- A correct descriptor payload at the wrong layout, binding, set, or array offset still produces a shader-visible failure.

### Sparse creation does not make unbound descriptor bytes valid

Sparse binding separates buffer creation from memory binding. `sparseBinding` permits sparse buffer memory binding, while `sparseResidencyBuffer` permits partial residency ([sparse features](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L70-L130)). The descriptor-buffer specification still says that dynamically reading descriptor data from an unbound region of a sparse partially resident buffer produces invalid descriptor data and undefined behavior ([descriptor-buffer sparse rule](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L928-L939)).

Why it matters here:

- `sparse_binding_buffer` and `sparse_residency_buffer` create descriptor buffers with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT` and bind memory with `vkQueueBindSparse`.
- The sparse-residency path adds allocation padding before binding the reported range. It does not use an unbound descriptor byte as an expected zero or other oracle.

### Descriptor data and referenced resource data have separate synchronization

A transfer that uploads encoded descriptor bytes must become visible to `VK_ACCESS_2_DESCRIPTOR_BUFFER_READ_BIT_EXT`. Resource data has its own transfer-to-shader dependency. Result writes then need shader-to-host or transfer-to-host visibility before the host reads them. Vulkan defines the descriptor-buffer access bit as descriptor-buffer read access in shader stages ([access flag](../../../../vulkan-docs/src/chapters/synchronization.adoc#L1277-L1281)); availability and visibility determine whether later accesses can read earlier writes ([memory dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#L110-L160)).

## One Concrete Example

The representative leaf is:

```text
dEQP-VK.binding_model.descriptor_buffer.traditional_buffer.single.compute_comp_storage_buffer
```

With the default `--deqp-base-seed=0`, registration hashes `single` and `compute_comp_storage_buffer`, producing the test value `0xaa2367fa`. The generated layout has set 0 binding 0 as a 4096-element storage buffer and binding 1 as a four-word result buffer. The compute shader checks indices `0`, `1365`, `2730`, and `4095`. Each expected value is `0xaa2367fa + index`. Every match increments `result.x`; a mismatch stores the packed set, binding, and element index. The shader writes all four result words through binding 1, and the host expects `result.x == 4`.

This example is small enough to expose the core contract: the host initializes resource values, obtains and places two storage-buffer descriptors at implementation-reported offsets, binds the descriptor buffer by address, dispatches one workgroup, and reads a diagnostic result.

## End-to-End Test Flow

```text
[host] choose residency mode, scenario family, queue, shader stage, descriptor type, layout counts, and optional command form
[host] derive deterministic binding layouts and generated GLSL from the case name and base seed
[host] reject unsupported extension, feature, queue, stage, descriptor-limit, sparse, robustness, ray-tracing, or format combinations
[host] create a custom device and the required ordinary and sparse queues
[host] create descriptor-set layouts with VK_DESCRIPTOR_SET_LAYOUT_CREATE_DESCRIPTOR_BUFFER_BIT_EXT
[host] query each layout size and binding offset, then pack aligned sets into descriptor buffers
[host] create traditional or sparse descriptor buffers; sparse modes submit vkQueueBindSparse and wait for its fence
[host] create and initialize referenced buffers, images, samplers, input attachments, inline data, or acceleration structures
[host] call vkGetDescriptorEXT for opaque descriptors, or write inline data directly, at set offset + binding offset + array stride
[host] create a descriptor-buffer pipeline and bind buffer addresses, set-to-buffer indices, and set offsets
[host] copy staged descriptor bytes when needed and make transfer writes visible to descriptor-buffer reads
[host] upload image data and make resource writes visible to the selected shader path
[device] execute one dispatch, ray trace, or full-screen draw; the selected stage reads each tested resource and records successes
[device] compute and ray-tracing paths write a result buffer; graphics paths pass uvec4 diagnostics to a fragment output image
[device] finish with shader-to-host or transfer-to-host barriers for the result data
[host] wait, invalidate the compute or ray-tracing result allocation, and read the result
[host] compare the success count with a host-computed expected count
[host] on mismatch, report the first failing set, binding, and array or buffer index; capture/replay cases run a second replay iteration
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `delayedInit()` turns each case's parameters into deterministic `SimpleBinding` entries. Single cases use one target binding plus helper resources. Matrix families shuffle descriptor types and choose array counts from one to three using the case hash.
- `glslDeclareBinding()` emits the GLSL declaration for sampler, image, texel-buffer, uniform-buffer, storage-buffer, input-attachment, inline-uniform, or acceleration-structure descriptors.
- `glslOutputVerification()` emits type-specific reads. Ordinary resources compare case-specific data; robustness cases expect zeros or zero texel-buffer size; capture/replay checks the replayed resource; YCbCr cases compare converted components with tolerance.
- Graphics pipelines pass a `uvec4` result through location 0 until the fragment shader writes one component per x coordinate. Compute and ray-tracing shaders write the same four fields to a storage buffer.
- Ray-tracing shader sources use explicit SPIR-V 1.4 build options. The representative compute source uses the CTS default SPIR-V 1.0 target.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Descriptor-set layouts | yes | through the pipeline layout | used to interpret descriptor bytes | no | Supply layout size, binding offsets, descriptor types, counts, and stage visibility. |
| Descriptor buffers | yes | yes, by device address and usage | read by shader descriptor fetch | no | Hold opaque descriptors or inline data at implementation-reported locations. |
| Sparse descriptor-buffer memory | yes | yes, through `vkQueueBindSparse` | read through the descriptor buffer | no | Exercises sparse buffer creation, queue selection, and memory binding without treating unbound descriptor bytes as valid. |
| Descriptor staging buffer | when direct host-visible device-local memory is unavailable | source of a transfer copy | read by transfer, not by shader | no | Tests device-side descriptor upload and the descriptor-buffer read barrier. |
| Referenced buffers and texel buffers | as required | through encoded descriptors | read by selected shader stage | result buffer only | Carry deterministic values and, for compute or ray tracing, the four-word diagnostic. |
| Images, views, and samplers | as required | through encoded descriptors | sampled, loaded, or used as input attachments | only the graphics result image | Exercise image layouts, sampler pairing, border color, YCbCr conversion, and descriptor encodings. |
| Acceleration structures and shader binding tables | for acceleration-structure or ray-tracing cases | yes | queried or traced | diagnostic result only | Extend descriptor access to ray-query and ray-tracing stages. |
| Graphics `R32_UINT` result image and host buffer | for graphics stages | image as color attachment, buffer as copy destination | fragment writes image; transfer copies it | yes | Stores success count and first-failure coordinates as four pixels. |

## What Is Checked

- Ordinary descriptor cases require every generated shader comparison to succeed. The host independently computes the expected comparison count from descriptor types and array sizes.
- A failed comparison leaves the counter short and stores the first failing packed set/binding identifier plus an array or buffer index. The `max` family also records the sampler binding used with the failed image.
- Robust buffer access expects zero for selected in-bounds and out-of-bounds reads. Null-descriptor cases expect zero data. Null texel-buffer size cases expect `textureSize()` or `imageSize()` to return zero.
- Capture/replay cases compare regenerated descriptor bytes with captured bytes and then rerun shader access with replay-created resources. Separate consistency leaves compare descriptor payload and resource usage data.
- YCbCr cases compare sampled components with a `0.005` tolerance. Other scalar checks are exact.
- The `basic.limits` leaves check reported `VkPhysicalDeviceDescriptorBufferPropertiesEXT` values against extension limits without running the generated resource shader path.

## Behavior Parameter Identification

> **Behavior parameter:** resource residency intermediate node and scenario family intermediate node
>
> **Candidate residency values:** `traditional_buffer`, `sparse_binding_buffer`, `sparse_residency_buffer`
>
> **Candidate scenario values:** `basic`, `single`, `multiple`, `max`, `embedded_imm_samplers`, `push_descriptor`, `push_template`, `robust`, `capture_replay`, `invalidation_rules`, `mutable_descriptor`, `ycbcr_sampler`

## What Failure Means

### Failure Cause Mapping

Resource-residency axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `traditional_buffer` | Traditional buffer memory binding, descriptor address/offset selection, descriptor encoding, resource access, synchronization, or readback failure. |
| `sparse_binding_buffer` | Sparse queue selection or binding failure, sparse descriptor-buffer address/range handling failure, or a shared descriptor encoding, resource access, synchronization, or readback failure. |
| `sparse_residency_buffer` | Sparse-residency feature or allocation-range handling failure, sparse descriptor-buffer address/range handling failure, or a shared descriptor encoding, resource access, synchronization, or readback failure. |

Scenario-family axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Descriptor-buffer property reporting outside the extension's required limits. |
| `single` | Type-specific descriptor encoding, layout offset, shader-stage access, resource initialization, or result transport failure. |
| `multiple` | Multi-buffer or multi-set packing, array stride, immutable-sampler layout, binding-index selection, or broad descriptor-type interaction failure. |
| `max` | Sampler/resource binding-limit handling or separate sampler and resource descriptor-buffer usage failure. |
| `embedded_imm_samplers` | Embedded immutable sampler layout or binding command failure, or incorrect pairing with sampled-image descriptors. |
| `push_descriptor` | Coexistence of descriptor-buffer sets and directly pushed descriptors, push-buffer handle, set selection, or maintenance6 command failure. |
| `push_template` | Descriptor update-template packing or push-template execution failure while descriptor-buffer sets remain bound. |
| `robust` | Robust descriptor size selection, out-of-bounds zeroing, null-descriptor encoding, or null texel-buffer size-query failure. |
| `capture_replay` | Opaque capture-data retrieval, replay object creation, byte-for-byte descriptor reproduction, custom-border-color interaction, or replayed resource access failure. |
| `invalidation_rules` | Incorrect invalidation or preservation when switching between legacy descriptor sets and descriptor-buffer bindings under pipeline-layout compatibility rules. |
| `mutable_descriptor` | Mutable descriptor layout support, maximum descriptor-size allocation, concrete-type encoding, or runtime access failure. |
| `ycbcr_sampler` | Multiplanar descriptor count/layout, combined-image-sampler array placement, YCbCr conversion, or sampled-value comparison failure. |

## Important Variations and Special Cases

- The default mustpass contains 5,432 Vulkan leaves: 1,818 under `traditional_buffer` and 1,807 under each sparse mode. Vulkan SC has no `descriptor_buffer` leaves in its binding-model list.
- `invalidation_rules` and eight descriptor-data consistency leaves under `capture_replay` exist only in `traditional_buffer`. The other major scenario families repeat across all three residency modes.
- Shader stages include vertex, tessellation control, tessellation evaluation, geometry, fragment, compute, ray generation, any-hit, closest-hit, miss, intersection, and callable. A compute-only queue is used only with compute shaders; graphics queue cases cover the other stages and compute where registered.
- Input attachments are restricted to fragment cases. Long `multiple` cases run only in vertex, fragment, or compute. The largest `max` counts are pruned for ray-tracing stages.
- `commands_2` leaves use `VK_KHR_maintenance6` structure-based descriptor-buffer and push-descriptor commands. `compute_maintenance5` uses the flags2 pipeline path. `non_buffer_aligned` shifts the bound buffer address by `descriptorBufferOffsetAlignment` and compensates in each set offset.
- Optional acceleration-structure bindings in matrix cases become storage buffers when ray query is unavailable. Cases whose requested descriptor is an acceleration structure require ray query; ray-tracing stages require the acceleration-structure and ray-tracing-pipeline extensions.
- Descriptor capture/replay and invalidation have dedicated host-side behavior beyond the shared counter oracle. They must not be read as ordinary single-descriptor variants.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameters and residency enum | [`TestParams` and `ResourceResidency`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L187-L222) | Defines the three modes and all matrix controls. |
| Generated case names and expected data | [`getCaseNameUpdateHash()` and `getExpectedData()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L767-L860) | Connects exact registered suffixes to deterministic shader data. |
| GLSL declarations and checks | [`glslDeclareBinding()` through `glslOutputVerification()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L910-L1540) | Generates resource interfaces, comparisons, and diagnostic writes. |
| Binding-layout generation | [`DescriptorBufferTestCase::delayedInit()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L1568-L1887) | Expands each scenario into sets, bindings, arrays, and helper resources. |
| Program generation | [`DescriptorBufferTestCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L1889-L2349) | Builds graphics, compute, and ray-tracing programs. |
| Support gates | [`DescriptorBufferTestCase::checkSupport()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L2351-L2586) | Applies extension, feature, stage, sparse, and limit requirements. |
| Layout size and binding offsets | [`createDescriptorSetLayouts()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L3355-L3439) | Queries implementation-defined descriptor memory layout. |
| Traditional and sparse descriptor buffers | [`createDescriptorBuffers()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L3441-L3716) | Creates, allocates, sparsely binds, addresses, and stages descriptor storage. |
| Address and set-offset binding | [`bindDescriptorBuffers()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L3718-L3844) | Records embedded samplers, buffer addresses, binding indices, and set offsets. |
| Descriptor serialization | [`initializeBinding()` descriptor write path](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L4710-L4950) | Calls `vkGetDescriptorEXT` or writes inline data at the calculated location. |
| Runtime and oracle | [`DescriptorBufferTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L5208-L5995) | Uploads, synchronizes, executes, reads back, and reports failures. |
| Registration | [`populateDescriptorBufferTestGroup()` and factory](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7174-L7899) | Defines scenario families, pruning, and three residency intermediate nodes. |
| Mustpass evidence | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L4718-L10149) | Contains the 5,432 default Vulkan leaves. |
| Descriptor-buffer layout and binding spec | [Descriptor Buffers](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L4-L251), [Binding Descriptor Buffers](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L661-L940) | Defines descriptor bytes, addresses, set offsets, visibility, and sparse access limits. |
| Sparse memory spec | [Sparse Resource Features](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L70-L130), [`vkQueueBindSparse`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L1691-L1730) | Defines sparse feature tiers and queue submission. |
| Shader-resource interface | [`VkDescriptorSetLayoutBinding`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L469), [Pipeline Layouts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1169-L1182) | Connects binding numbers and stage flags to shader resources. |

## Questions / Risk Points for User Audit

- The three residency values are kept separate from the scenario-family values so sparse failures are not flattened into descriptor-type failures.
- The `basic`, capture/replay consistency, and invalidation leaves use specialized host checks. The final page must keep them separate from the shared generated-shader counter path.
- Sparse residency is described as a sparse-residency allocation and binding path, not as a test that expects valid reads from unbound descriptor bytes.
- One representative compute storage-buffer shader is sufficient to explain generated declarations, case-specific data, diagnostic fields, and host readback. Stage transport, ray tracing, robustness, and YCbCr differences belong in the variation summary rather than redundant full shaders.
- No semantic risk remains after checking implementation, registration, mustpass, and specification evidence.

## Conversion Notes for Final Wiki Rewrite

- Carry both behavior axes into `## Behavior Parameters` and copy both failure-mapping tables byte for byte.
- Distill descriptor-location, sparse validity, synchronization, and shader-interface prerequisites into short bullets.
- Keep the compute storage-buffer case as the only full walkthrough. Embed compiler-produced, validated SPIR-V 1.0.
- Put mustpass counts and registration-only differences in the parameter and pruning sections.
- Explain the common runtime in time order, then call out `basic`, capture/replay, invalidation, robustness, and YCbCr exceptions.
