# Descriptor Indexing Tests

The `descriptor_indexing` Vulkan CTS category verifies descriptor array indexing patterns that rely on descriptor-indexing features, especially non-uniform descriptor-array access, runtime descriptor arrays, update-after-bind variants, partially populated descriptor arrays, and selected no-runtime-array / minimum-`NonUniform` shader forms. The inspected registration path is unusual for a Vulkan CTS category: the category root contains many direct test cases rather than conventional named subgroups.

## Registration Entry Point

`descriptor_indexing` is added as a root Vulkan test category in both the Vulkan and Vulkan SC package registration paths ([`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1384), [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1451)). The category dispatcher creates the root group by forwarding to `descriptorIndexingDescriptorSetsCreateTests` through `createTestGroup` ([`vktDescriptorIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L32-L37)).

The dispatcher file does not include branch-specific headers; its local include list contains only its own header and `vktTestGroupUtil.hpp` ([`vktDescriptorIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L24-L25)). The actual direct children are appended by the delegated implementation in `vktDescriptorSetsIndexingTests.cpp`, which also calls the misc registration helper at the end ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4736-L4924)).

## Subgroup and Direct-Child Structure

No nested `TestCaseGroup` child names were observed in the inspected descriptor-indexing registration path. Instead, `descriptorIndexingDescriptorSetsCreateTests` receives the already-created category group and repeatedly calls `group->addChild(...)` for direct root cases ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831), [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4838-L4918)). The misc source likewise receives the category group and appends four direct cases through `mainGroup->addChild(...)` ([`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L587-L612)).

The default mustpass list confirms the direct-root shape as `dEQP-VK.descriptor_indexing.<case>` entries rather than subgroup-qualified paths ([`descriptor-indexing.txt`](../../mustpass/main/vk-default/descriptor-indexing.txt#L1-L114)). At category level, the direct children can be summarized as:

| Direct-child family | Representative names | Evidence |
|---|---|---|
| Main descriptor-type matrix | `storage_buffer`, `sampled_image_after_bind_in_loop_with_lod_lifetime`, `uniform_buffer_dynamic_in_loop_lifetime` | Descriptor-type table and suffix loops in [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4831) |
| Minimum `NonUniform` SPIR-V assembly cases | `storage_buffer_minNonUniform`, `combined_image_sampler_with_lod_minNonUniform` | Minimum-`NonUniform` case table and name construction in [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4838-L4897) |
| No-runtime-array cases | `storage_image_no_runtime_array`, `uniform_buffer_no_runtime_array` | No-runtime-array loop in [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4900-L4918) |
| Function case | `non_uniform_atomics` | Direct function-case registration in [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4920-L4921) |
| Misc sampled-image-array cases | `misc_common_nonuniform_index_arraysize_{8,64}_at_{0,mid}` | Nested misc registration loops in [`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L591-L612) |

## File Inventory

| File | Role in this category | Notes |
|---|---|---|
| [`vktDescriptorIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L1) | Dispatcher / root registration file | Defines the category factory and delegates child population; it does not implement support checks or pass/fail verification ([`vktDescriptorIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L32-L37)). |
| [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1) | Main implementation-heavy registration and execution file | Generates most direct root cases, implements descriptor-type feature gates, shader generation, common result comparison, and `non_uniform_atomics` ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4736-L4924)). |
| [`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L1) | Misc implementation file with direct-root registrations | Adds four sampled-image-array cases and implements their compute shader and CPU comparison ([`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L131-L165), [`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L541-L582)). |
| [`vktDescriptorSetsIndexingTestsUtils.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTestsUtils.cpp#L628-L776) | Helper evidence, not a standalone registered test page | Queries descriptor-indexing feature/property structures and computes descriptor-count limits used by the main implementation. No standalone registration was observed in the inspected evidence. |

## Recurring Test Families and Themes

- **Descriptor-type coverage:** The main table covers storage buffers, storage texel buffers, uniform texel buffers, storage images, samplers, sampled images, combined image samplers, uniform buffers, dynamic storage buffers, dynamic uniform buffers, and input attachments ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4791)).
- **Sparse valid descriptors:** Main cases use descriptor-set layout binding flags with `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT`, then derive valid descriptor coverage from prime-indexed descriptors (`computePrimeCount`) rather than populating every descriptor ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L540-L551), [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1235-L1239)).
- **Update-after-bind behavior:** Cases with `_after_bind` enable descriptor-set layout / pool update-after-bind flags and move descriptor updates after command-buffer binding in the iteration path ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L553-L579), [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1408-L1411)).
- **Loop-computed descriptor indices:** `_in_loop` cases add a descriptor enumerator and extra descriptor-set layout so shaders can compute descriptor indices within bounds rather than using only direct attribute-derived indices ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1235-L1247)).
- **Shader-form variation:** Ordinary cases generate GLSL sources, while `_minNonUniform` cases use SPIR-V assembly generation to control minimum `NonUniform` decoration placement ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4390-L4497)).
- **Dedicated compute atomics:** `non_uniform_atomics` uses two arrays of storage-buffer descriptors and non-uniform indexing in a compute shader, then checks both index writes and atomic counters ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4500-L4531), [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4651-L4708)).
- **Common sampled-image-array misc pattern:** Misc cases use three runtime sampled-image descriptor arrays indexed with `nonuniformEXT`, compute `a * b + c`, and compare each output element to CPU reference data ([`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L131-L165), [`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L541-L582)).

## Recurring Parameter Dimensions

| Dimension | Observed values or rules | Evidence |
|---|---|---|
| Descriptor type | Main matrix uses 11 descriptor-type base names, with descriptor-specific guard filtering for suffixes | [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4831) |
| Shader stage path | Storage images use compute; other main-table descriptor types use vertex and fragment stage flags in the registration table | [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4819-L4822) |
| Suffix dimensions | `_after_bind`, `_in_loop`, `_with_lod`, `_lifetime`; update-after-bind and mipmap suffixes are filtered by descriptor-type helper checks | [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831) |
| Runtime array mode | Main and minimum-`NonUniform` cases use runtime descriptor arrays; no-runtime-array cases set `usesRuntimeArray = false` | [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4884-L4893), [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4900-L4918) |
| Descriptor count | Helper code queries descriptor-indexing features/properties and caps resource-class descriptor counts for bounded tests | [`vktDescriptorSetsIndexingTestsUtils.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTestsUtils.cpp#L628-L776) |
| Valid descriptor subset | Valid descriptors are counted from prime indices within the available descriptor count | [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1235-L1239) |
| Misc array size and coordinate | Misc cases combine array sizes `8` and `64` with coordinates named `0` and `mid` | [`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L591-L612) |
| Misc image format and layout shape | Misc cases use `VK_FORMAT_R32G32B32A32_UINT`, three sampled-image arrays, and one output/sampler set | [`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L602-L605), [`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L407-L417) |

## Support and Feature Gates

Main descriptor-type cases first require `runtimeDescriptorArray` when the parameters use runtime arrays ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4283-L4288)). The support switch then checks descriptor-type-specific non-uniform indexing features for storage buffers, uniform buffers, texel buffers, dynamic buffers, input attachments, sampler / sampled-image-family descriptors, and storage images ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4290-L4387)).

Update-after-bind is also descriptor-type-specific: supported descriptor classes require matching `descriptorBinding*UpdateAfterBind` feature bits, while dynamic buffers and input attachments reject update-after-bind in this implementation ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4297-L4382)). Descriptor-count decisions are based on queried descriptor-indexing properties for update-after-bind cases and core descriptor limits otherwise ([`vktDescriptorSetsIndexingTestsUtils.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTestsUtils.cpp#L654-L776)).

`non_uniform_atomics` separately requires `VK_EXT_descriptor_indexing`, `runtimeDescriptorArray`, `shaderStorageBufferArrayNonUniformIndexing`, and enough per-stage / descriptor-set storage-buffer resources for its fixed arrays ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4534-L4556)). Misc sampled-image-array cases require `VK_EXT_descriptor_indexing`, `runtimeDescriptorArray`, `shaderSampledImageArrayNonUniformIndexing`, enough sampled-image descriptors for `3 * arraySize`, and image-format support for the selected sampled-image usage ([`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L100-L128)).

## Verification Methods

Most descriptor-type matrix cases render or dispatch into outputs, build a reference result, and compare through `iterateVerifyResults`, which performs fuzzy or float-threshold image comparison and optionally verifies vertex-write side effects ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1383-L1431), [`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1473-L1496)). The common reference image is generated from the color scheme and valid descriptor count ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1498-L1518)).

`non_uniform_atomics` validates host-visible storage buffers after compute dispatch: it invalidates output buffers, constructs reference index and counter arrays, logs mismatches, and fails if any result differs ([`vktDescriptorSetsIndexingTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4651-L4708)). Misc sampled-image-array cases validate by synchronizing the output buffer, recomputing the same sampled-image arithmetic on the CPU, and comparing each `UVec4` with `deMemCmp` ([`vktDescriptorIndexingMiscTests.cpp`](../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L523-L582)).

## Level-3 Documentation

| Page | Focus |
|---|---|
| [`vktDescriptorIndexingTests.md`](../testfiles/descriptor_indexing/vktDescriptorIndexingTests.md) | Category dispatcher, package registration, and direct-root registration shape. |
| [`vktDescriptorSetsIndexingTests.md`](../testfiles/descriptor_indexing/vktDescriptorSetsIndexingTests.md) | Main descriptor-type matrix, suffix dimensions, feature gates, shader generation, common verification, and `non_uniform_atomics`. |
| [`vktDescriptorIndexingMiscTests.md`](../testfiles/descriptor_indexing/vktDescriptorIndexingMiscTests.md) | Four misc common non-uniform sampled-image-array cases and their compute verification path. |

## Notes and Uncertainties

- The category page intentionally does not present factory symbols such as `descriptorIndexingDescriptorSetsCreateTests` or `createDescriptorIndexingMiscTests` as subgroup names; those symbols are implementation entry points, while the inspected registered children are direct root test cases.
- `vktDescriptorSetsIndexingTestsUtils.cpp` is treated as helper evidence only. A standalone Level-3 page would require separate registration evidence, which was not observed in the inspected files.
