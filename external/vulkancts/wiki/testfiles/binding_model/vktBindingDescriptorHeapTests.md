# Descriptor Heap Tests

Covers `VK_EXT_descriptor_heap` behavior across limits, basic descriptor access, dynamic indexing, binding mappings, heap switching, queues, invalidation, graphics, SPIR-V, non-packed and unaligned mappings.

## Source

- [`vktBindingDescriptorHeapTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp)

## Registration Hierarchy

```text
binding_model.descriptor_heap
├── limit
├── basic
├── invariance
├── capture_replay
├── dynamic_indexing
├── binding_mapping
├── high_binding
├── combined_image_samplers
├── reserved_heap
├── push_data
├── null_descriptor
├── ycbcr
├── different_mappings_per_shader
├── graphics_pipeline_library
├── switch_heaps
├── concurrent_queues
├── concurrent_heap_set
├── state_invalidation
├── write_after_record
├── spirv
├── resource_masking
├── null_image_queries
├── graphics
├── graphics_and_compute
├── different_mappings_same_shader
├── non_uniform_mappings
├── msaa_image_read
├── resource_heap_access
├── sampler_heap_access
├── shader_object_invariance
├── push_data_access
├── non_uniform_access
├── special_heap
├── non_packed
├── unaligned
└── secondary
```

## Test Families

### limit — Descriptor heap limit queries

Tests descriptor heap limit reporting. Created in [`populateLimitsTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13331); adds a single `limits` function case. Evidence: [`vktBindingDescriptorHeapTests.cpp:13335`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13335).

### basic — Basic descriptor heap access

Tests basic descriptor heap binding and shader access across shader stages (fragment, compute, raygen) and descriptor types (sampler, sampled image, storage image, uniform/storage texel buffer, uniform/storage buffer, input attachment, acceleration structure). Created in [`populateBasicTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13339); iterates shader stages and descriptor types. Evidence: [`vktBindingDescriptorHeapTests.cpp:13345`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13345).

### invariance — Invariant descriptor access

Tests descriptor access invariance across descriptor types. Created in [`populateInvarianceTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13478); iterates descriptor types with `captureReplay = false`. Evidence: [`vktBindingDescriptorHeapTests.cpp:13494`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13494).

### capture_replay — Capture-replay descriptor access

Tests descriptor capture-replay behavior across descriptor types. Created in [`populateInvarianceTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13478); iterates descriptor types with `captureReplay = true`, including a `sampler_custom_border` variant. Evidence: [`vktBindingDescriptorHeapTests.cpp:13494`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13494).

### dynamic_indexing — Dynamic indexing of descriptor arrays

Tests dynamic (runtime) indexing into descriptor arrays. Created in [`populateDynamicIndexingTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13531). Evidence: [`vktBindingDescriptorHeapTests.cpp:13534`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13534).

### binding_mapping — Descriptor binding mapping sources

Tests descriptor binding mapping across multiple `VkDescriptorMappingSourceEXT` values (constant offset, push index, indirect index, resource heap data, push data/address, indirect address, shader record index/data/address, indirect index array) and descriptor types. Contains subgroups per mapping source. Created in [`populateBindingMappingTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13637). Evidence: [`vktBindingDescriptorHeapTests.cpp:13644`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13644).

### high_binding — High descriptor set and binding values

Tests descriptor heap access with high descriptor set indices and binding values. Created in [`populateHighBindingTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13864). Evidence: [`vktBindingDescriptorHeapTests.cpp:13867`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13867).

### combined_image_samplers — Combined image sampler descriptors

Tests combined image sampler descriptor access with embedded and non-embedded sampler modes, across mapping sources. Contains subgroups per mapping source and embedded/non-embedded mode. Created in [`populateCombinedImageSamplerTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13911). Evidence: [`vktBindingDescriptorHeapTests.cpp:13914`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13914).

### reserved_heap — Reserved heap operations

Tests reserved heap behavior with copy operations (buffer-to-image, copy image, image-to-buffer, clear color image, blit image) and heap binding combinations (resource, sampler, both). Created in [`populateReservedHeapTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14150). Evidence: [`vktBindingDescriptorHeapTests.cpp:14156`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14156).

### push_data — Push data descriptor access

Tests push data descriptor access across shader stages (fragment, compute, raygen). Created in [`populatePushDataTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14206). Evidence: [`vktBindingDescriptorHeapTests.cpp:14212`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14212).

### null_descriptor — Null descriptor access

Tests null descriptor behavior across shader stages and descriptor types. Created in [`populateNullDescriptorTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14271). Evidence: [`vktBindingDescriptorHeapTests.cpp:14277`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14277).

### ycbcr — YCbCr sampler conversion

Tests YCbCr sampler conversion with descriptor heaps. Created in [`populateYcbcrTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14386). Evidence: [`vktBindingDescriptorHeapTests.cpp:14391`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14391).

### different_mappings_per_shader — Different mappings per shader stage

Tests that different descriptor mappings can be used per shader stage. Created in [`populateDifferentMappingsPerShader`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14398). Evidence: [`vktBindingDescriptorHeapTests.cpp:14403`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14403).

### graphics_pipeline_library — Graphics pipeline library

Tests descriptor heap access with graphics pipeline library. Created in [`populateGraphicsPipelineLibraryTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14412). Evidence: [`vktBindingDescriptorHeapTests.cpp:14417`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14417).

### switch_heaps — Heap switching

Tests switching between descriptor heaps, with optional push descriptors and NV command buffer inheritance. Created in [`populateSwitchHeapsTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14437). Evidence: [`vktBindingDescriptorHeapTests.cpp:14442`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14442).

### concurrent_queues — Concurrent queue access

Tests descriptor heap access from concurrent queues across shader stages and descriptor types. Contains subgroups per shader stage. Created in [`populateConcurrentQueuesTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14466). Evidence: [`vktBindingDescriptorHeapTests.cpp:14470`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14470).

### concurrent_heap_set — Concurrent heap set access

Tests concurrent access to the same heap set from multiple queues. Created in [`populateConcurrentHeapSetTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14608). Evidence: [`vktBindingDescriptorHeapTests.cpp:14613`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14613).

### state_invalidation — State invalidation

Tests descriptor heap state invalidation behavior. Created in [`populateStateInvalidationTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14623). Evidence: [`vktBindingDescriptorHeapTests.cpp:14628`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14628).

### write_after_record — Write after record

Tests writing to descriptor heaps after command buffer recording. Created in [`populateWriteAfterRecordTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14637). Evidence: [`vktBindingDescriptorHeapTests.cpp:14642`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14642).

### spirv — SPIR-V specific tests

Tests SPIR-V specific descriptor heap behaviors including `SizeOf`, `UntypedStorageBuffer`, `UntypedArrayLength`, `SimpleStorageTexelBuffer`, `UntypedImageTexelPointer`, `SimpleSamplerHeap`, `FunctionCallBinding`, `StorageTexelBufferAtomic64`, `SimpleVariablePointers`, `ArrayVariablePointers`, and `AtomicImageWithinFunction`. Created in [`populateSpirvTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14650). Evidence: [`vktBindingDescriptorHeapTests.cpp:14655`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14655).

### resource_masking — Resource masking

Tests descriptor heap resource masking behavior. Created in [`populateResourceMaskingTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14687). Evidence: [`vktBindingDescriptorHeapTests.cpp:14692`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14692).

### null_image_queries — Null image queries

Tests query operations on null image descriptors. Created in [`populateNullImageQueriesTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14699). Evidence: [`vktBindingDescriptorHeapTests.cpp:14704`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14704).

### graphics — Graphics pipeline descriptor access

Tests descriptor heap access across graphics pipeline stages (vertex, fragment, tessellation, geometry) with primary and secondary command buffers. Current source also generates `_vectors` variants for the non-mesh graphics-stage combinations; these add descriptor-heap uniform-matrix and storage-vector descriptors and verify per-stage vector outputs ([`vktBindingDescriptorHeapTests.cpp:9410`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L9410), [`vktBindingDescriptorHeapTests.cpp:10050`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L10050)). Created in [`populateGraphicsTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14712), with vector variants registered at [`vktBindingDescriptorHeapTests.cpp:14725`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14725).

### graphics_and_compute — Combined graphics and compute access

Tests descriptor heap access from both graphics and compute pipelines simultaneously. Created in [`populateGraphicsAndComputeTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14797). Evidence: [`vktBindingDescriptorHeapTests.cpp:14801`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14801).

### different_mappings_same_shader — Different mappings within same shader

Tests that different descriptor mappings can coexist within the same shader. Created in [`populateDifferentMappingsSameShader`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14809). Evidence: [`vktBindingDescriptorHeapTests.cpp:14814`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14814).

### non_uniform_mappings — Non-uniform descriptor mappings

Tests non-uniform descriptor mapping access with runtime descriptor arrays. Created in [`populateNonUniformMappings`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14821). Evidence: [`vktBindingDescriptorHeapTests.cpp:14826`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14826).

### msaa_image_read — MSAA image read

Tests reading from MSAA images via descriptor heaps with sample-rate shading. Created in [`populateMSAAImageReadTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14833). Evidence: [`vktBindingDescriptorHeapTests.cpp:14838`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14838).

### resource_heap_access — Resource heap access

Tests resource heap access from graphics and compute queues. Created in [`populateResourceHeapAccessTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14847). Evidence: [`vktBindingDescriptorHeapTests.cpp:14852`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14852).

### sampler_heap_access — Sampler heap access

Tests sampler heap access from graphics and compute queues. Created in [`populateSamplerHeapAccessTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14864). Evidence: [`vktBindingDescriptorHeapTests.cpp:14869`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14869).

### shader_object_invariance — Shader object invariance

Tests descriptor heap invariance with `VK_EXT_shader_object`. Created in [`populateShaderObjectInvariance`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14898). Evidence: [`vktBindingDescriptorHeapTests.cpp:14903`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14903).

### push_data_access — Push data access

Tests push data access through descriptor heaps. Created in [`populatePushDataAccessTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14910). Evidence: [`vktBindingDescriptorHeapTests.cpp:14915`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14915).

### non_uniform_access — Non-uniform access

Tests non-uniform descriptor access across descriptor types (sampled image, storage image, uniform/storage texel buffer, uniform/storage buffer). Created in [`populateNonUniformAccessTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14922). Evidence: [`vktBindingDescriptorHeapTests.cpp:14924`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14924).

### special_heap — Special heap types

Tests descriptor heap access with special heap types (sparse, protected, sparse-and-protected) across descriptor types. Contains subgroups per special mode. Created in [`populateSpecialHeapTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14963). Evidence: [`vktBindingDescriptorHeapTests.cpp:14968`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14968).

### non_packed — Non-packed descriptor stride

Tests non-packed descriptor stride with override strides across mapping sources and descriptor types. Contains subgroups per mapping source. Created in [`populateNonPackedTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15091). Evidence: [`vktBindingDescriptorHeapTests.cpp:15123`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15123).

### unaligned — Unaligned descriptor mapping

Tests unaligned descriptor mapping with scaled strides across mapping sources and descriptor types. Contains subgroups per mapping source. Created in [`populateUnalignedTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15261). Evidence: [`vktBindingDescriptorHeapTests.cpp:15290`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15290).

### secondary — Descriptor heap inheritance in secondary command buffers

Tests that descriptor heap bindings inherited by a secondary command buffer can be used from both compute and graphics queues. The compute variant samples a descriptor-heap texture/sampler and writes a `vec4` result to a descriptor-heap storage buffer; the graphics variant samples through descriptor heaps in a secondary render-pass command buffer and verifies copied image pixels against the expected color. The cases are registered as `compute` and `graphics` in [`populateSecondaryCommandBufferTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14880) and added to the category in [`populateDescriptorHeapTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15454).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorHeapTests.cpp:15461`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15461) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorHeapTests.cpp:15420`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15420) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorHeapTests.cpp:509`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L509). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases bind resource and sampler heaps, execute shader pipelines, and compare results; support checks gate descriptor-heap and selected extension features. The secondary-command-buffer family additionally verifies inherited descriptor heaps by comparing either a compute-written `vec4` or graphics-rendered pixels to the expected sampled color ([`vktBindingDescriptorHeapTests.cpp:11992`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L11992), [`vktBindingDescriptorHeapTests.cpp:12171`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12171)).

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
