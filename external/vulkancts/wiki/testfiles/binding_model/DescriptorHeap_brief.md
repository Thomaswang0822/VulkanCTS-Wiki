# Understanding Brief: `binding_model.descriptor_heap`

## One-Sentence Test Purpose

This test checks whether `VK_EXT_descriptor_heap` can write, bind, map, and directly access sampler and resource descriptors while preserving representation, state lifetime, concurrency, shader-stage, and SPIR-V contracts across the extension's major usage modes.

## Background Knowledge

### A heap is bound address state, not a descriptor object

A descriptor heap is a device-address range recorded as command-buffer state. The sampler heap stores sampler descriptors. The resource heap stores image, buffer, texel-buffer, and acceleration-structure descriptors. The application asks the implementation to write opaque descriptor bytes to host memory, transfers or exposes those bytes through heap memory, and binds the heap range with `vkCmdBindSamplerHeapEXT` or `vkCmdBindResourceHeapEXT` ([descriptor-heap model](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L5-L32), [heap binding](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L733-L903)).

Why it matters here:

- Correct resource data is not enough. The descriptor bytes must be written to the address and stride selected by the shader mapping.
- Each heap includes an application range and may include an implementation-reserved range that the application must not access while bound.
- Binding heap state and recording legacy descriptor state invalidate one another ([state invalidation](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L675-L710)).

### Shader resources can reach heaps through two interfaces

A shader can use the `ResourceHeapEXT` and `SamplerHeapEXT` built-ins directly, or keep ordinary `DescriptorSet` and `Binding` decorations and receive a `VkDescriptorSetAndBindingMappingEXT` at pipeline or shader creation. Mapping sources derive a descriptor location from constants, push data, an address in push data, indirect memory, resource-heap data, or shader-record data ([shader bindings](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1113-L1200), [mapping-source selection](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1213-L1318)).

Why it matters here:

- The same GLSL declaration can resolve to different heap bytes in different stages or pipelines.
- `resourceMask` decides which SPIR-V resource declarations a mapping applies to.
- Array indexing and descriptor stride are separate parts of the final byte offset. Non-packed and unaligned cases are designed to expose implementations that silently substitute a preferred stride.

### Push data and descriptor memory have independent roles

`vkCmdPushDataEXT` supplies bytes through the existing SPIR-V `PushConstant` storage class. Those bytes may be shader data, an index, or a device address used by a mapping. Push data is heap-compatible replacement state for ordinary push constants, and recording either binding model invalidates the other ([push data](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L965-L1032)).

## One Concrete Example

The representative leaf `dEQP-VK.binding_model.descriptor_heap.write_after_record.write_after_record` creates a storage-texel-buffer descriptor mapping for set 0, binding 0. It records heap binding, a pushed random value, pipeline binding, and one dispatch before any descriptor bytes are written. After the command buffer is complete, the host calls `vkWriteResourceDescriptorsEXT` into the already referenced heap memory, submits, waits, and expects the shader to store the pushed value into the output buffer ([shader and mapping](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L3446-L3509), [record, late write, and check](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L3511-L3569)).

This case separates command recording from descriptor-memory population. A passing result shows that recording captured the heap address and mapping state, not stale descriptor contents.

## End-to-End Test Flow

```text
[host] choose a first-level behavior group, stage, descriptor type, mapping source, queue mode, and deterministic seed
[host] reject unsupported descriptor-heap, shader, queue, sparse/protected, ray-tracing, YCbCr, or pipeline feature combinations
[host] query descriptor sizes, alignments, heap limits, and implementation reservation sizes
[host] create descriptor-heap buffers and the images, buffers, samplers, acceleration structures, or output resources used by the case
[host] write opaque sampler/resource descriptors, direct heap data, push data, indirect indices, or shader-record data as required
[host] create a descriptor-heap pipeline or shader object with per-stage VkDescriptorSetAndBindingMappingEXT records when decorated bindings are used
[host] bind resource and sampler heap ranges, record push data and draw/dispatch/trace commands, and submit one or more queues
[device] resolve direct heap built-ins or apply the selected mapping formula to shader DescriptorSet and Binding resources
[device] read, sample, query, atomically update, or write the selected resources and emit an expected value, image, vector, or counter
[host] wait and make shader writes visible to the host or a copy operation
[host] compare exact descriptor bytes, scalar/vector values, pixels, query results, counters, or multisample values with the case oracle
```

Reserved-heap cases use a distinct multi-queue flow: setup work initializes resources, several queue submissions use timeline semaphores while heap reservations are live, and a final submission copies data for host comparison ([reserved-heap execution](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L6585-L7050)). Capture/replay cases also recreate resources and compare descriptor bytes before accepting replay ([invariance execution](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L6052-L6120)).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `DescriptorHeapTestCaseBasic::initQueuePrograms()` emits stage-specific GLSL declarations and type-specific reads or writes from each `ShaderBinding`. Pipeline creation attaches the selected descriptor mapping records ([program generation](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L3901-L4217)).
- The `spirv` group loads source-authored SPIR-V assembly for descriptor size, untyped pointer, heap built-in, function-call, variable-pointer, and image-atomic operations and assembles it for SPIR-V 1.6 ([SPIR-V programs](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L7408-L8083)).
- Dedicated paths generate YCbCr, graphics pipeline library/shader object, graphics-stage, combined graphics and compute, MSAA, direct heap, push-data, non-uniform, and secondary-command-buffer shaders.
- Deterministic seeds select heap indices, push offsets, indirect addresses, data values, and some binding numbers. This broadens address patterns without making results nondeterministic.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Resource descriptor heap | yes | yes, by device address | descriptors and direct data are read | normally no | Holds image, buffer, texel-buffer, and acceleration-structure descriptors plus its reserved range. |
| Sampler descriptor heap | when sampling uses heap samplers | yes, by device address | sampler descriptors are read | no | Separates sampler selection from resource selection and supports combined-image mappings. |
| Reserved heap range | allocated by host, owned by implementation while bound | part of heap binding | not application-accessible | no | Exercises reservation size, overlap, lifetime, and cross-command-buffer rules. |
| Referenced buffers and images | as required | through heap descriptors or mapped addresses | read, sampled, queried, atomically updated, or written | output resources only | Carry deterministic test values and observable results. |
| Push-data bytes | yes | command-buffer state | read as PushConstant data, indices, or addresses | no | Select heap entries and carry small shader-visible payloads. |
| Indirect-index/address storage and shader records | for selected mappings | by device address or SBT record | read during mapping resolution | no | Distinguish constant, push, indirect, and shader-record mapping formulas. |
| Output buffers/images and staging copies | yes | yes | shaders or transfers write | yes | Transport exact values, pixels, vectors, samples, and diagnostics to the host. |

## What Is Checked

- `limit` verifies required minima, maxima, alignment rules, and nonzero descriptor-heap properties ([limit check](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L801-L927)).
- `invariance` and `capture_replay` compare written descriptor bytes, check that writes stop at the reported descriptor size, and recreate capture/replay resources where required.
- The shared typed-access path computes expected results from initialized descriptors and checks every output entry. Mapping, indexing, stage, queue, null, special-heap, packed-stride, and unaligned variants reuse that value oracle.
- Specialized groups check YCbCr components with tolerance, graphics colors and vectors, graphics-plus-compute sentinel values, null image query sizes/levels, four MSAA samples, resource/sampler direct-access outputs, secondary command-buffer results, and shader-object binary equality.
- `spirv` compares operation-specific words, including descriptor sizes, `0xcafe` writes, atomic values, function-call results, and variable-pointer selections ([SPIR-V result oracle](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L8085-L8681)).

## Behavior Parameter Identification

> **Behavior parameter:** first-level behavior cluster
>
> **Candidate values:** `limits and representation`, `typed access and descriptor semantics`, `binding mappings and resource selection`, `heap state lifetime`, `reservation, concurrency, and memory modes`, `push data and mapped addresses`, `pipeline and stage integration`, `direct heap built-ins`, `irregular mapping layouts`, `SPIR-V operations`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `limits and representation` | Descriptor-heap property reporting, descriptor-size reporting, deterministic descriptor encoding, capture/replay reconstruction, or shader-object binary invariance failure. |
| `typed access and descriptor semantics` | Type-specific descriptor writing, heap placement, shader decoding, array indexing, null behavior, combined image sampler handling, or YCbCr conversion failure. |
| `binding mappings and resource selection` | Descriptor set and binding matching, mapping-source address calculation, per-stage mapping selection, or SPIR-V resource-mask classification failure. |
| `heap state lifetime` | Heap rebinding, legacy-state invalidation, secondary-command-buffer inheritance, or descriptor visibility after command recording failure. |
| `reservation, concurrency, and memory modes` | Reserved-range lifetime or isolation failure, cross-queue heap use failure, or sparse/protected descriptor-heap allocation and access failure. |
| `push data and mapped addresses` | `vkCmdPushDataEXT` range handling, PushConstant exposure, push-index/address mapping, or maximum push-data transfer failure. |
| `pipeline and stage integration` | Graphics-stage, compute-stage, graphics pipeline library, shader-object, or multisample image integration failure. |
| `direct heap built-ins` | `ResourceHeapEXT` or `SamplerHeapEXT` lowering, direct descriptor selection, or non-uniform direct heap access failure. |
| `irregular mapping layouts` | Non-uniform mapped-array selection, non-packed descriptor size/stride handling, or unaligned base/index arithmetic failure. |
| `SPIR-V operations` | `SPV_EXT_descriptor_heap`, untyped pointer, size, array-length, image atomic, function-call, variable-pointer, or 64-bit operation lowering failure. |

## Important Variations and Special Cases

- The default Vulkan mustpass contains 457 leaves under `binding_model.descriptor_heap`, covering 36 first-level registered groups ([mustpass range](../../../mustpass/main/vk-default/binding-model.txt#L10441-L10897)). `non_packed` contributes 120 leaves, but this brief treats it as one layout mechanism rather than listing every stride leaf.
- `basic`, `concurrent_queues`, `null_descriptor`, `push_data`, and graphics groups vary stage. Input attachments are fragment-only. Ray-generation and shader-record mappings require ray-tracing support.
- Descriptor types include sampler, sampled/storage image, uniform/storage texel buffer, uniform/storage buffer, input attachment, combined image sampler behavior, and acceleration structure where legal.
- `special_heap` has `sparse`, `protected`, and `sparse_and_protected` modes. These change heap memory setup, not the shader's expected payload.
- Reserved-range tests may pass early when all advertised reservation sizes are zero; the implementation then has no nonzero reservation behavior to exercise ([zero-reservation branch](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L6585-L6593)).
- `non_packed` queries or overrides larger byte strides across five index-producing mapping sources. `unaligned` disables scaled mapping strides for push, indirect, and shader-record index sources to ensure the byte formulas are honored exactly ([non-packed registration](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15091-L15259), [unaligned registration](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15261-L15413)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter and resource model | [`TestParams`, `ShaderBinding`, and stride helpers](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L61-L228) | Defines feature switches, mapping records, descriptor kinds, and aligned default strides. |
| Common support gates | [`DescriptorHeapTestCaseBase::checkSupport()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L500-L722) | Applies extension, feature, stage, sparse/protected, and indexing requirements. |
| Shared shader generator and execution | [`initQueuePrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L3901-L4217), [`DescriptorHeapTestInstanceBasic::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L4219-L4847) | Implements the broad typed descriptor and mapping path. |
| Capture/replay and descriptor invariance | [`DescriptorHeapTestInstanceInvariance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L6052-L6120) | Checks descriptor bytes, write bounds, and replay behavior. |
| State and concurrency paths | [heap switching through late descriptor writes](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L2127-L3570) | Covers switching, concurrent use, invalidation, and write-after-record. |
| SPIR-V operations and oracle | [SPIR-V builder and execution](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L7408-L8681) | Exercises extension instructions and operation-specific expected results. |
| Graphics and direct heap paths | [graphics through sampler heap access](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L9634-L11759) | Covers stage pipelines, MSAA, and direct resource/sampler heap access. |
| Registration | [`populateDescriptorHeapTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13331-L15461) | Defines all 36 first-level groups and generated dimensions. |
| Descriptor heap specification | [writing and binding heaps](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L28-L903), [shader mappings](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1113-L2150) | Defines the semantics used to interpret failures. |

## Questions / Risk Points for User Audit

- Is the distinction between direct heap built-ins and decorated-binding mappings clear?
- Do the ten behavior clusters retain every first-level group without becoming a leaf inventory?
- Is late descriptor writing correctly separated from command-buffer state recording?
- Are reserved ranges described as implementation-owned portions of an application-allocated heap range?
- Do the representative shader paths cover ordinary mapped access, push-data plus direct heap access, and non-uniform direct heap access without redundant walkthroughs?

## Conversion Notes for Final Wiki Rewrite

- Keep the one-level 36-child registration tree because it is the smallest parseable view that proves full first-level coverage.
- Carry the ten-cluster behavior axis into `## Behavior Parameters`; name all exact first-level groups inside those cluster subsections.
- Preserve three shader walkthroughs: `write_after_record.write_after_record`, `push_data_access.push_data_access`, and `non_uniform_access.storage_buffer`.
- Distill background material into the heap/state model, mapping interface, and push-data role. Move concrete setup to runtime sections.
- Copy `### Failure Cause Mapping` byte-for-byte into the final page and write fresh cause analysis.
