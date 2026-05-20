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

Tests descriptor heap limit reporting. Created in [`populateLimitsTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12698); adds a single `limits` function case. Evidence: [`vktBindingDescriptorHeapTests.cpp:12701`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12701).

### basic — Basic descriptor heap access

Tests basic descriptor heap binding and shader access across shader stages (fragment, compute, raygen) and descriptor types (sampler, sampled image, storage image, uniform/storage texel buffer, uniform/storage buffer, input attachment, acceleration structure). Created in [`populateBasicTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12706); iterates shader stages and descriptor types. Evidence: [`vktBindingDescriptorHeapTests.cpp:12709`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12709).

### invariance — Invariant descriptor access

Tests descriptor access invariance across descriptor types. Created in [`populateInvarianceTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12845); iterates descriptor types with `captureReplay = false`. Evidence: [`vktBindingDescriptorHeapTests.cpp:12863`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12863).

### capture_replay — Capture-replay descriptor access

Tests descriptor capture-replay behavior across descriptor types. Created in [`populateInvarianceTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12845); iterates descriptor types with `captureReplay = true`, including a `sampler_custom_border` variant. Evidence: [`vktBindingDescriptorHeapTests.cpp:12863`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12863).

### dynamic_indexing — Dynamic indexing of descriptor arrays

Tests dynamic (runtime) indexing into descriptor arrays. Created in [`populateDynamicIndexingTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12898). Evidence: [`vktBindingDescriptorHeapTests.cpp:12901`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12901).

### binding_mapping — Descriptor binding mapping sources

Tests descriptor binding mapping across multiple `VkDescriptorMappingSourceEXT` values (constant offset, push index, indirect index, resource heap data, push data/address, indirect address, shader record index/data/address, indirect index array) and descriptor types. Contains subgroups per mapping source. Created in [`populateBindingMappingTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13004). Evidence: [`vktBindingDescriptorHeapTests.cpp:13007`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13007).

### high_binding — High descriptor set and binding values

Tests descriptor heap access with high descriptor set indices and binding values. Created in [`populateHighBindingTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13231). Evidence: [`vktBindingDescriptorHeapTests.cpp:13234`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13234).

### combined_image_samplers — Combined image sampler descriptors

Tests combined image sampler descriptor access with embedded and non-embedded sampler modes, across mapping sources. Contains subgroups per mapping source and embedded/non-embedded mode. Created in [`populateCombinedImageSamplerTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13278). Evidence: [`vktBindingDescriptorHeapTests.cpp:13281`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13281).

### reserved_heap — Reserved heap operations

Tests reserved heap behavior with copy operations (buffer-to-image, copy image, image-to-buffer, clear color image, blit image) and heap binding combinations (resource, sampler, both). Created in [`populateReservedHeapTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13517). Evidence: [`vktBindingDescriptorHeapTests.cpp:13520`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13520).

### push_data — Push data descriptor access

Tests push data descriptor access across shader stages (fragment, compute, raygen). Created in [`populatePushDataTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13573). Evidence: [`vktBindingDescriptorHeapTests.cpp:13576`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13576).

### null_descriptor — Null descriptor access

Tests null descriptor behavior across shader stages and descriptor types. Created in [`populateNullDescriptorTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13638). Evidence: [`vktBindingDescriptorHeapTests.cpp:13641`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13641).

### ycbcr — YCbCr sampler conversion

Tests YCbCr sampler conversion with descriptor heaps. Created in [`populateYcbcrTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13753). Evidence: [`vktBindingDescriptorHeapTests.cpp:13756`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13756).

### different_mappings_per_shader — Different mappings per shader stage

Tests that different descriptor mappings can be used per shader stage. Created in [`populateDifferentMappingsPerShader`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13765). Evidence: [`vktBindingDescriptorHeapTests.cpp:13768`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13768).

### graphics_pipeline_library — Graphics pipeline library

Tests descriptor heap access with graphics pipeline library. Created in [`populateGraphicsPipelineLibraryTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13779). Evidence: [`vktBindingDescriptorHeapTests.cpp:13782`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13782).

### switch_heaps — Heap switching

Tests switching between descriptor heaps, with optional push descriptors and NV command buffer inheritance. Created in [`populateSwitchHeapsTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13805). Evidence: [`vktBindingDescriptorHeapTests.cpp:13807`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13807).

### concurrent_queues — Concurrent queue access

Tests descriptor heap access from concurrent queues across shader stages and descriptor types. Contains subgroups per shader stage. Created in [`populateConcurrentQueuesTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13833). Evidence: [`vktBindingDescriptorHeapTests.cpp:13836`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13836).

### concurrent_heap_set — Concurrent heap set access

Tests concurrent access to the same heap set from multiple queues. Created in [`populateConcurrentHeapSetTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13975). Evidence: [`vktBindingDescriptorHeapTests.cpp:13978`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13978).

### state_invalidation — State invalidation

Tests descriptor heap state invalidation behavior. Created in [`populateStateInvalidationTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13990). Evidence: [`vktBindingDescriptorHeapTests.cpp:13993`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L13993).

### write_after_record — Write after record

Tests writing to descriptor heaps after command buffer recording. Created in [`populateWriteAfterRecordTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14004). Evidence: [`vktBindingDescriptorHeapTests.cpp:14007`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14007).

### spirv — SPIR-V specific tests

Tests SPIR-V specific descriptor heap behaviors including `SizeOf`, `UntypedStorageBuffer`, `UntypedArrayLength`, `SimpleStorageTexelBuffer`, `UntypedImageTexelPointer`, `SimpleSamplerHeap`, `FunctionCallBinding`, `StorageTexelBufferAtomic64`, `SimpleVariablePointers`, `ArrayVariablePointers`, and `AtomicImageWithinFunction`. Created in [`populateSpirvTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14017). Evidence: [`vktBindingDescriptorHeapTests.cpp:14020`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14020).

### resource_masking — Resource masking

Tests descriptor heap resource masking behavior. Created in [`populateResourceMaskingTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14054). Evidence: [`vktBindingDescriptorHeapTests.cpp:14057`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14057).

### null_image_queries — Null image queries

Tests query operations on null image descriptors. Created in [`populateNullImageQueriesTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14066). Evidence: [`vktBindingDescriptorHeapTests.cpp:14069`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14069).

### graphics — Graphics pipeline descriptor access

Tests descriptor heap access across graphics pipeline stages (vertex, fragment, tessellation, geometry) with primary and secondary command buffers. Current source also generates `_vectors` variants for the non-mesh graphics-stage combinations; these add descriptor-heap uniform-matrix and storage-vector descriptors and verify per-stage vector outputs ([`vktBindingDescriptorHeapTests.cpp:9410`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L9410), [`vktBindingDescriptorHeapTests.cpp:10050`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L10050)). Created in [`populateGraphicsTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14712), with vector variants registered at [`vktBindingDescriptorHeapTests.cpp:14725`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14725).

### graphics_and_compute — Combined graphics and compute access

Tests descriptor heap access from both graphics and compute pipelines simultaneously. Created in [`populateGraphicsAndComputeTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14158). Evidence: [`vktBindingDescriptorHeapTests.cpp:14161`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14161).

### different_mappings_same_shader — Different mappings within same shader

Tests that different descriptor mappings can coexist within the same shader. Created in [`populateDifferentMappingsSameShader`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14170). Evidence: [`vktBindingDescriptorHeapTests.cpp:14173`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14173).

### non_uniform_mappings — Non-uniform descriptor mappings

Tests non-uniform descriptor mapping access with runtime descriptor arrays. Created in [`populateNonUniformMappings`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14182). Evidence: [`vktBindingDescriptorHeapTests.cpp:14185`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14185).

### msaa_image_read — MSAA image read

Tests reading from MSAA images via descriptor heaps with sample-rate shading. Created in [`populateMSAAImageReadTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14194). Evidence: [`vktBindingDescriptorHeapTests.cpp:14197`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14197).

### resource_heap_access — Resource heap access

Tests resource heap access from graphics and compute queues. Created in [`populateResourceHeapAccessTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14208). Evidence: [`vktBindingDescriptorHeapTests.cpp:14211`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14211).

### sampler_heap_access — Sampler heap access

Tests sampler heap access from graphics and compute queues. Created in [`populateSamplerHeapAccessTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14225). Evidence: [`vktBindingDescriptorHeapTests.cpp:14228`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14228).

### shader_object_invariance — Shader object invariance

Tests descriptor heap invariance with `VK_EXT_shader_object`. Created in [`populateShaderObjectInvariance`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14241). Evidence: [`vktBindingDescriptorHeapTests.cpp:14244`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14244).

### push_data_access — Push data access

Tests push data access through descriptor heaps. Created in [`populatePushDataAccessTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14253). Evidence: [`vktBindingDescriptorHeapTests.cpp:14256`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14256).

### non_uniform_access — Non-uniform access

Tests non-uniform descriptor access across descriptor types (sampled image, storage image, uniform/storage texel buffer, uniform/storage buffer). Created in [`populateNonUniformAccessTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14265). Evidence: [`vktBindingDescriptorHeapTests.cpp:14274`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14274).

### special_heap — Special heap types

Tests descriptor heap access with special heap types (sparse, protected, sparse-and-protected) across descriptor types. Contains subgroups per special mode. Created in [`populateSpecialHeapTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14306). Evidence: [`vktBindingDescriptorHeapTests.cpp:14309`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14309).

### non_packed — Non-packed descriptor stride

Tests non-packed descriptor stride with override strides across mapping sources and descriptor types. Contains subgroups per mapping source. Created in [`populateNonPackedTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14434). Evidence: [`vktBindingDescriptorHeapTests.cpp:14437`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14437).

### unaligned — Unaligned descriptor mapping

Tests unaligned descriptor mapping with scaled strides across mapping sources and descriptor types. Contains subgroups per mapping source. Created in [`populateUnalignedTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14604). Evidence: [`vktBindingDescriptorHeapTests.cpp:14607`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14607).

### secondary — Descriptor heap inheritance in secondary command buffers

Tests that descriptor heap bindings inherited by a secondary command buffer can be used from both compute and graphics queues. The compute variant samples a descriptor-heap texture/sampler and writes a `vec4` result to a descriptor-heap storage buffer; the graphics variant samples through descriptor heaps in a secondary render-pass command buffer and verifies copied image pixels against the expected color. The cases are registered as `compute` and `graphics` in [`populateSecondaryCommandBufferTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14880) and added to the category in [`populateDescriptorHeapTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L15454).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDescriptorHeapTests.cpp:14803`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L14803) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDescriptorHeapTests.cpp:12700`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12700) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingDescriptorHeapTests.cpp:508`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L508). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases bind resource and sampler heaps, execute shader pipelines, and compare results; support checks gate descriptor-heap and selected extension features. The secondary-command-buffer family additionally verifies inherited descriptor heaps by comparing either a compute-written `vec4` or graphics-rendered pixels to the expected sampled color ([`vktBindingDescriptorHeapTests.cpp:11992`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L11992), [`vktBindingDescriptorHeapTests.cpp:12171`](../../../modules/vulkan/binding_model/vktBindingDescriptorHeapTests.cpp#L12171)).

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
