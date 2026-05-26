# vktDescriptorSetsIndexingTests.cpp

## Overview

[`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4736-L4924) is the main implementation-heavy source for the `descriptor_indexing` category. It registers most category-root test cases directly in [`descriptorIndexingDescriptorSetsCreateTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4736-L4924), including descriptor-type matrices, minimum-`NonUniform` SPIR-V assembly cases, no-runtime-array cases, and the `non_uniform_atomics` function case.

The same registration function also calls [`createDescriptorIndexingMiscTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4923), so the parseable hierarchy below uses the category root `descriptor_indexing` and lists the direct children visible in the default mustpass file. This page focuses on the implementation in [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp); the misc cases are only noted as delegated registrations.

## Role

Implementation-heavy registration and execution file.

## Source Code

| Role | File |
|---|---|
| Main implementation and registration | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1) |
| Public declaration | [`vktDescriptorSetsIndexingTests.hpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.hpp#L1) |
| Shared descriptor-indexing helpers | [`vktDescriptorSetsIndexingTestsUtils.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTestsUtils.cpp#L71-L109) |
| Root dispatcher that delegates here | [`vktDescriptorIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L32-L37) |
| Delegated misc registration called here | [`vktDescriptorIndexingMiscTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L587-L612) |
| Mustpass cross-check | [`descriptor-indexing.txt`](../../../mustpass/main/vk-default/descriptor-indexing.txt#L1-L114) |

## Registration Hierarchy

This tree uses `descriptor_indexing` as the Level-3 root because the implementation function receives the already-created category group and calls `group->addChild(...)` for direct category-root test cases. It fully lists the observed direct children exactly one level below the category root; no nested subgroup is shown because the inspected main registration code does not create a `TestCaseGroup` under this root.

```text
descriptor_indexing
├── combined_image_sampler
├── combined_image_sampler_after_bind
├── combined_image_sampler_after_bind_in_loop
├── combined_image_sampler_after_bind_in_loop_lifetime
├── combined_image_sampler_after_bind_in_loop_with_lod
├── combined_image_sampler_after_bind_in_loop_with_lod_lifetime
├── combined_image_sampler_after_bind_lifetime
├── combined_image_sampler_after_bind_with_lod
├── combined_image_sampler_after_bind_with_lod_lifetime
├── combined_image_sampler_in_loop
├── combined_image_sampler_in_loop_lifetime
├── combined_image_sampler_in_loop_with_lod
├── combined_image_sampler_in_loop_with_lod_lifetime
├── combined_image_sampler_lifetime
├── combined_image_sampler_minNonUniform
├── combined_image_sampler_no_runtime_array
├── combined_image_sampler_with_lod
├── combined_image_sampler_with_lod_lifetime
├── combined_image_sampler_with_lod_minNonUniform
├── input_attachment
├── input_attachment_in_loop
├── input_attachment_in_loop_lifetime
├── input_attachment_lifetime
├── misc_common_nonuniform_index_arraysize_64_at_0
├── misc_common_nonuniform_index_arraysize_64_at_mid
├── misc_common_nonuniform_index_arraysize_8_at_0
├── misc_common_nonuniform_index_arraysize_8_at_mid
├── non_uniform_atomics
├── sampled_image
├── sampled_image_after_bind
├── sampled_image_after_bind_in_loop
├── sampled_image_after_bind_in_loop_lifetime
├── sampled_image_after_bind_in_loop_with_lod
├── sampled_image_after_bind_in_loop_with_lod_lifetime
├── sampled_image_after_bind_lifetime
├── sampled_image_after_bind_with_lod
├── sampled_image_after_bind_with_lod_lifetime
├── sampled_image_in_loop
├── sampled_image_in_loop_lifetime
├── sampled_image_in_loop_with_lod
├── sampled_image_in_loop_with_lod_lifetime
├── sampled_image_lifetime
├── sampled_image_with_lod
├── sampled_image_with_lod_lifetime
├── sampler
├── sampler_after_bind
├── sampler_after_bind_in_loop
├── sampler_after_bind_in_loop_lifetime
├── sampler_after_bind_in_loop_with_lod
├── sampler_after_bind_in_loop_with_lod_lifetime
├── sampler_after_bind_lifetime
├── sampler_after_bind_with_lod
├── sampler_after_bind_with_lod_lifetime
├── sampler_in_loop
├── sampler_in_loop_lifetime
├── sampler_in_loop_with_lod
├── sampler_in_loop_with_lod_lifetime
├── sampler_lifetime
├── sampler_with_lod
├── sampler_with_lod_lifetime
├── storage_buffer
├── storage_buffer_after_bind
├── storage_buffer_after_bind_in_loop
├── storage_buffer_after_bind_in_loop_lifetime
├── storage_buffer_after_bind_lifetime
├── storage_buffer_dynamic
├── storage_buffer_dynamic_in_loop
├── storage_buffer_dynamic_in_loop_lifetime
├── storage_buffer_dynamic_lifetime
├── storage_buffer_in_loop
├── storage_buffer_in_loop_lifetime
├── storage_buffer_lifetime
├── storage_buffer_minNonUniform
├── storage_buffer_no_runtime_array
├── storage_image
├── storage_image_after_bind
├── storage_image_after_bind_in_loop
├── storage_image_after_bind_in_loop_lifetime
├── storage_image_after_bind_lifetime
├── storage_image_in_loop
├── storage_image_in_loop_lifetime
├── storage_image_lifetime
├── storage_image_minNonUniform
├── storage_image_no_runtime_array
├── storage_texel_buffer
├── storage_texel_buffer_after_bind
├── storage_texel_buffer_after_bind_in_loop
├── storage_texel_buffer_after_bind_in_loop_lifetime
├── storage_texel_buffer_after_bind_lifetime
├── storage_texel_buffer_in_loop
├── storage_texel_buffer_in_loop_lifetime
├── storage_texel_buffer_lifetime
├── storage_texel_buffer_minNonUniform
├── storage_texel_buffer_no_runtime_array
├── uniform_buffer
├── uniform_buffer_dynamic
├── uniform_buffer_dynamic_in_loop
├── uniform_buffer_dynamic_in_loop_lifetime
├── uniform_buffer_dynamic_lifetime
├── uniform_buffer_in_loop
├── uniform_buffer_in_loop_lifetime
├── uniform_buffer_lifetime
├── uniform_buffer_minNonUniform
├── uniform_buffer_no_runtime_array
├── uniform_texel_buffer
├── uniform_texel_buffer_after_bind
├── uniform_texel_buffer_after_bind_in_loop
├── uniform_texel_buffer_after_bind_in_loop_lifetime
├── uniform_texel_buffer_after_bind_lifetime
├── uniform_texel_buffer_in_loop
├── uniform_texel_buffer_in_loop_lifetime
├── uniform_texel_buffer_lifetime
├── uniform_texel_buffer_minNonUniform
└── uniform_texel_buffer_no_runtime_array
```

## Test Families

### combined_image_sampler — Combined image sampler descriptor arrays

`combined_image_sampler` is one of the descriptor-type bases in the `casesAfterBindAndLoop` table and maps to `VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER`, graphics stages, mipmap-capable image access, and runtime arrays in the primary matrix ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4791)). The suffix loops combine it with `_after_bind`, `_in_loop`, `_with_lod`, and `_lifetime` when the guard helpers allow those suffixes ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831)). Its implementation creates one sampler plus per-descriptor images, writes only prime descriptor indices, and optionally uses the final mip level for `_with_lod` cases ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3928-L4018)).

### input_attachment — Input-attachment descriptor arrays

`input_attachment` comes from the same main table, but the suffix guards restrict it to the observed direct children without `_after_bind` or `_with_lod` variants ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831)). The implementation builds descriptor images, creates input-attachment references with intentionally unused attachment gaps before prime-indexed attachments, and constructs a render pass that exposes those inputs to the fragment stage ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3480-L3595)).

### misc_common_nonuniform_index_arraysize_64_at_0 — Delegated misc direct-root case

`misc_common_nonuniform_index_arraysize_64_at_0` and the three related `misc_common_nonuniform_index_arraysize_*` children are not implemented by the main descriptor-set classes in this file. They are appended by the delegated call to [`createDescriptorIndexingMiscTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4923), whose own registration function generates the four direct root names ([`vktDescriptorIndexingMiscTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L587-L612)).

### misc_common_nonuniform_index_arraysize_64_at_mid — Delegated misc direct-root case

This exact direct child is one of the four misc names appended through the delegated misc registration loop. Its implementation details are documented in the misc Level-3 page.

### misc_common_nonuniform_index_arraysize_8_at_0 — Delegated misc direct-root case

This exact direct child is one of the four misc names appended through the delegated misc registration loop. Its implementation details are documented in the misc Level-3 page.

### misc_common_nonuniform_index_arraysize_8_at_mid — Delegated misc direct-root case

This exact direct child is one of the four misc names appended through the delegated misc registration loop. Its implementation details are documented in the misc Level-3 page.

### non_uniform_atomics — Compute storage-buffer atomics

`non_uniform_atomics` is registered as a direct function case with explicit support, program, and run callbacks ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4920-L4921)). It uses two descriptor sets, each with 128 storage-buffer descriptors, dispatches 1024 compute invocations in 64-thread workgroups, and checks both the per-index output buffers and atomic counter buffers against CPU reference arrays ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4558-L4708)).

### sampled_image — Sampled-image descriptor arrays

`sampled_image` is a main-table descriptor base using `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE`, graphics stages, mipmap-capable image access, and an additional sampler descriptor ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4791)). The registered variants include update-after-bind, looped index computation, mipmap, and lifetime suffixes where allowed by the registration guards ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831)). Its instance updates a single sampler in the additional binding and then updates the image descriptor array through the common descriptor update path ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3761-L3811)).

### sampler — Sampler descriptor arrays

`sampler` is generated from the main table with an additional sampled-image descriptor, so the indexed descriptors are samplers while the image is provided separately ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4791)). Its suffix set mirrors the allowed `_after_bind`, `_in_loop`, `_with_lod`, and `_lifetime` combinations from the registration loops ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831)). The instance writes the shared image into `BINDING_Additional` and maintains a sampler array for the tested binding ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3612-L3655)).

### storage_buffer — Storage-buffer descriptor arrays

`storage_buffer` cases are generated from the main table and also appear in the SPIR-V minimum-`NonUniform` and no-runtime-array blocks ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4918)). Their implementation can perform vertex-stage writes when the device supports `vertexPipelineStoresAndAtomics`; verification for those writes reads back per-prime storage-buffer records and compares `cnew` against the expected color with a small threshold ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1786-L1788), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3015-L3048)).

### storage_buffer_dynamic — Dynamic storage-buffer descriptor arrays

`storage_buffer_dynamic` is registered only for the base, `_in_loop`, `_lifetime`, and `_in_loop_lifetime` combinations visible in the hierarchy, because update-after-bind and mipmap suffixes are filtered by the registration guards ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831)). Dynamic-buffer execution builds a dynamic-offset array whose size exactly matches the available descriptor count, using nonzero offsets only for prime-indexed valid descriptors before binding the descriptor set with all dynamic offsets ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3289-L3362)).

### storage_image — Storage-image descriptor arrays

`storage_image` cases are produced by the main matrix and by the minimum-`NonUniform` / no-runtime-array registration blocks ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4918)). Unlike the graphics-oriented image and buffer cases, the storage-image instance dispatches compute work, optionally updates descriptors after bind, copies prepared buffer data into images before dispatch, copies image results back afterward, and then reuses the common result verification path ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4166-L4195)).

### storage_texel_buffer — Storage texel-buffer descriptor arrays

`storage_texel_buffer` is included in the main descriptor table and in both the minimum-`NonUniform` and no-runtime-array registration blocks ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4918)). Its instance creates storage texel buffers and buffer views, stores test colors in texel-buffer-backed memory, and verifies vertex-write results by reading a texel from each prime-indexed valid descriptor and comparing to the expected color ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3100-L3184)).

### uniform_buffer — Uniform-buffer descriptor arrays

`uniform_buffer` cases are generated by the main matrix and are also part of the minimum-`NonUniform` and no-runtime-array blocks ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4918)). The instance creates uniform-buffer records aligned to `minUniformBufferOffsetAlignment`, writes one color record per valid descriptor, flushes the allocation, and records the alignment for later descriptor and dynamic-offset handling ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3051-L3098)).

### uniform_buffer_dynamic — Dynamic uniform-buffer descriptor arrays

`uniform_buffer_dynamic` follows the dynamic-buffer execution path and is registered only for the base, `_in_loop`, `_lifetime`, and `_in_loop_lifetime` combinations in the hierarchy ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831)). The shared dynamic-buffer loop binds one dynamic offset per available descriptor and then compares the rendered result to a reference image through the common verification path ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3289-L3362)).

### uniform_texel_buffer — Uniform texel-buffer descriptor arrays

`uniform_texel_buffer` participates in the main, minimum-`NonUniform`, and no-runtime-array registration blocks ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4918)). The file maps its descriptor type to `UniformTexelInstance` in the test-case factory switch, so the registered `uniform_texel_buffer*` names exercise the same descriptor-indexing framework through the texel-buffer read path rather than storage writes ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4251-L4262)).

## Parameter Dimensions

| Dimension | Observed values or rule | Evidence |
|---|---|---|
| Descriptor type | `storage_buffer`, `storage_texel_buffer`, `uniform_texel_buffer`, `storage_image`, `sampler`, `sampled_image`, `combined_image_sampler`, `uniform_buffer`, `storage_buffer_dynamic`, `uniform_buffer_dynamic`, `input_attachment` in the main table | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4791) |
| Stage mix | Per-entry `stageFlags`; buffers, texel buffers, sampled images, samplers, combined images, uniforms, dynamics, and input attachments use graphics-stage paths, while storage images use a compute path in the inspected registration table | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4791), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4166-L4195) |
| Update-after-bind suffix | `_after_bind` is added when the suffix loop enables it and `isUpdateAfterBindSupported(info.descriptorType)` permits it | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831) |
| Loop-computed index suffix | `_in_loop` adds descriptor-enumerator setup, a second descriptor-set layout, push constants for `lowerBound` / `upperBound`, and a second bound descriptor set | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1235-L1247), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1347-L1373) |
| Mipmap suffix | `_with_lod` is registered only for descriptor types where the registration guards allow mipmaps and the table marks `withMipMaps`; combined/sampled image implementations use mipmapped image extents when enabled | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3968-L4018) |
| Lifetime suffix | `_lifetime` causes unused descriptors to be populated at command-begin time and later destroyed through the common lifetime path | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1276-L1284), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4826-L4831) |
| Runtime descriptor arrays | Main and minimum-`NonUniform` cases set `usesRuntimeArray = true`; no-runtime-array cases set `usesRuntimeArray = false` and use minimal required descriptor count instead of computed maximum counts | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4890-L4918), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L511-L518) |
| Minimum `NonUniform` decoration | `_minNonUniform` cases use SPIR-V assembly sources instead of GLSL and are generated for selected descriptor types | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4838-L4897), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4390-L4455) |
| Descriptor count | Runtime-array cases compute an available descriptor count from descriptor-indexing properties and Vulkan limits, then cap selected resource classes to bounded test sizes | [`vktDescriptorSetsIndexingTestsUtils.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTestsUtils.cpp#L654-L776) |
| Valid descriptors | Only prime-indexed descriptors are treated as valid; `validDescriptorCount` is derived with `computePrimeCount(availableDescriptorCount)` | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1235-L1239), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3930-L3957) |

## Support / Feature Requirements

The main `DescriptorIndexingTestCase` first requires `runtimeDescriptorArray` when the test parameters say the case uses runtime arrays ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4283-L4288)). It then gates each descriptor type on the corresponding non-uniform indexing feature: storage buffers, uniform buffers, storage texel buffers, uniform texel buffers, storage-buffer dynamic descriptors, uniform-buffer dynamic descriptors, input attachments, sampled-image-family descriptors, and storage images each have explicit feature checks in the switch ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4290-L4387)).

Update-after-bind is descriptor-type-specific. Storage buffers, uniform buffers, storage texel buffers, uniform texel buffers, sampled-image-family descriptors, and storage images require their matching descriptor-binding update-after-bind feature when `updateAfterBind` is set; dynamic buffers and input attachments reject update-after-bind in this implementation ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4297-L4382)). Descriptor set layouts and pools also set update-after-bind flags when that parameter is enabled ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L540-L579)).

The shared helper [`DeviceProperties`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTestsUtils.cpp#L628-L652) queries `VkPhysicalDeviceDescriptorIndexingFeatures` and `VkPhysicalDeviceDescriptorIndexingProperties` through `getPhysicalDeviceFeatures2` and `getPhysicalDeviceProperties2`; its descriptor-count calculator uses descriptor-indexing update-after-bind properties when applicable and core descriptor limits otherwise ([`vktDescriptorSetsIndexingTestsUtils.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTestsUtils.cpp#L654-L776)).

The `non_uniform_atomics` case separately requires `shaderStorageBufferArrayNonUniformIndexing` and enough `maxPerStageResources`, `maxPerStageDescriptorStorageBuffers`, and `maxDescriptorSetStorageBuffers` for its fixed storage-buffer arrays ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4534-L4556)).

## Verification Methods

Most descriptor-type matrix cases build a reference result and compare it to the shader output through [`iterateVerifyResults`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1473-L1496). The common path reads the framebuffer for test output, synthesizes a reference image from the color scheme and valid descriptor count, and compares with either fuzzy or threshold float comparison ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1473-L1518)).

For graphics cases, the common iteration divides the render area into a 4x4 tile sweep, optionally updates descriptors after binding, draws, collects result and reference images, and returns pass only if the comparison succeeds ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1383-L1431)). Dynamic buffer cases use the same result comparison but bind descriptor sets with the full dynamic-offset array before each draw ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3289-L3362)). Storage-image cases dispatch compute work and copy image results back before common verification ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4166-L4195)).

When shader writes are enabled for storage buffers or storage texel buffers, extra verification reads descriptor-backed memory for prime-indexed descriptors and compares each value to the expected color component ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1490-L1493), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3015-L3048), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3151-L3184)). The `non_uniform_atomics` function case has a separate verification loop that invalidates output buffers and compares each index and counter value against CPU reference arrays, failing with log messages on any mismatch ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4651-L4708)).

## Test Principles Observed

- Sparse valid-descriptor coverage is intentional: descriptor arrays can be large, but valid descriptors are selected at prime indices and descriptors are marked `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT` in the layout binding flags ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L540-L551), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1235-L1239)).
- Runtime-array and no-runtime-array cases are separated so shader non-uniform indexing is tested both with `runtimeDescriptorArray` and without requiring that feature in the selected no-runtime-array cases ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4900-L4918)).
- Minimum-`NonUniform` cases use SPIR-V assembly generation to control exactly where `NonUniform` decorations are emitted, while ordinary cases generate GLSL sources ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4390-L4497)).
- Update-after-bind is exercised as a behavioral dimension, not only as a support bit: descriptor updates move after command-buffer binding when `updateAfterBind` is enabled ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1270-L1273), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1408-L1411)).
- Loop-index cases add a descriptor enumerator and push constants so the shader computes descriptor indices under per-pass bounds rather than using only direct vertex attribute indices ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1235-L1247), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1347-L1373)).

## Notes / Uncertainties

- The hierarchy includes the four delegated misc direct-root cases because they are added through the call at the end of [`descriptorIndexingDescriptorSetsCreateTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4923) and appear in the default mustpass list. Their implementation details are covered by the dedicated [`vktDescriptorIndexingMiscTests.md`](vktDescriptorIndexingMiscTests.md) page.
- The inspected source shows `non_uniform_atomics` as a direct function case, not as a nested `TestCaseGroup`; any audit should reject wording that treats it as a subgroup unless different source evidence is found.
