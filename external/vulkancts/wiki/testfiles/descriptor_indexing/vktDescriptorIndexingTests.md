# vktDescriptorIndexingTests.cpp

## Overview

[`vktDescriptorIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L24-L37) is the top-level dispatcher source for the `descriptor_indexing` Vulkan CTS category. The global Vulkan and Vulkan SC package registration adds the category name `descriptor_indexing` and routes it to [`DescriptorIndexing::createTests`](../../../modules/vulkan/vktTestPackage.cpp#L1384) / [`DescriptorIndexing::createTests`](../../../modules/vulkan/vktTestPackage.cpp#L1451). This dispatcher then creates the category test group by forwarding child population to [`descriptorIndexingDescriptorSetsCreateTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L32-L37).

Unlike many category dispatchers, this file does not include branch-specific headers. Its include section contains only its own header and [`vktTestGroupUtil.hpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L24-L25), so the visible category children come from the delegated registration function rather than from local `addChild()` calls in this file.

## Role

Registration / dispatcher file.

## Source Code

| Role | File |
|---|---|
| Primary dispatcher | [`vktDescriptorIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L1) |
| Dispatcher declaration | [`vktDescriptorIndexingTests.hpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.hpp#L31-L37) |
| Root package registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1384) and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1451) |
| Delegated main registration | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4736-L4923) |
| Delegated misc registration | [`vktDescriptorIndexingMiscTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L587-L612) |
| Mustpass cross-check | [`descriptor-indexing.txt`](../../../mustpass/main/vk-default/descriptor-indexing.txt#L1-L114) |

## Registration Hierarchy

This parseable tree uses `descriptor_indexing` as the Level-3 root because the package registration names that category directly. The children below are direct registered test-case names observed from the delegated registration functions and cross-checked against the default mustpass list. This overlaps with the child tree that an implementation page for `vktDescriptorSetsIndexingTests.cpp` should also explain, but the role differs: this page documents how the category dispatcher reaches those children, while the implementation page should document the parameter matrix and execution logic behind them.

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

### combined_image_sampler — Combined image sampler descriptor-indexing cases

The `combined_image_sampler` children are generated from the main `casesAfterBindAndLoop` descriptor-type table and suffix loops in [`descriptorIndexingDescriptorSetsCreateTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4831). The additional `combined_image_sampler_minNonUniform`, `combined_image_sampler_with_lod_minNonUniform`, and `combined_image_sampler_no_runtime_array` cases come from the SPIR-V minimum-non-uniform and no-runtime-array registration blocks in the same delegated function ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4842-L4918)).

### input_attachment — Input attachment descriptor-indexing cases

The `input_attachment` children come from the main descriptor table and suffix loops, but only suffix combinations that survive the visible guards are registered. In particular, update-after-bind and mipmap suffixes are filtered by descriptor-type helper checks before [`group->addChild`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4801-L4831).

### misc_common_nonuniform_index_arraysize_8_at_0 — Misc common non-uniform array indexing cases

`misc_common_nonuniform_index_arraysize_8_at_0` and the other three `misc_common_nonuniform_index_arraysize_*` children are appended by [`createDescriptorIndexingMiscTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L587-L612), which is called from the delegated main registration function after `non_uniform_atomics` ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4920-L4923)). The exact sibling names are listed in the hierarchy tree above.

### misc_common_nonuniform_index_arraysize_8_at_mid — Misc sibling case

This direct child shares the same delegated misc registration loop as `misc_common_nonuniform_index_arraysize_8_at_0`; see the dedicated misc Level-3 page for parameter and verification details.

### misc_common_nonuniform_index_arraysize_64_at_0 — Misc sibling case

This direct child shares the same delegated misc registration loop as `misc_common_nonuniform_index_arraysize_8_at_0`; see the dedicated misc Level-3 page for parameter and verification details.

### misc_common_nonuniform_index_arraysize_64_at_mid — Misc sibling case

This direct child shares the same delegated misc registration loop as `misc_common_nonuniform_index_arraysize_8_at_0`; see the dedicated misc Level-3 page for parameter and verification details.

### non_uniform_atomics — Function case with programs

`non_uniform_atomics` is registered as a direct function case with program generation, support check, and run function callbacks in the delegated registration function ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4920-L4921)).

### sampled_image — Descriptor-type generated cases

`sampled_image` represents the remaining descriptor-type families generated by combining descriptor-type base names with the visible suffix dimensions `_after_bind`, `_in_loop`, `_with_lod`, `_lifetime`, `_minNonUniform`, and `_no_runtime_array` where the delegated registration code permits each combination ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4918)). The dispatcher file itself does not define the descriptor semantics; it only routes the category group to that generator.

### sampler — Descriptor-type generated cases

`sampler` is another exact direct child from the delegated descriptor-type registration matrix. Its related suffix variants are visible in the hierarchy tree above.

### storage_buffer — Descriptor-type generated cases

`storage_buffer` is another exact direct child from the delegated descriptor-type registration matrix. Its related suffix, minimum-`NonUniform`, and no-runtime-array variants are visible in the hierarchy tree above.

### storage_image — Descriptor-type generated cases

`storage_image` is another exact direct child from the delegated descriptor-type registration matrix. Its related suffix, minimum-`NonUniform`, and no-runtime-array variants are visible in the hierarchy tree above.

### storage_texel_buffer — Descriptor-type generated cases

`storage_texel_buffer` is another exact direct child from the delegated descriptor-type registration matrix. Its related suffix, minimum-`NonUniform`, and no-runtime-array variants are visible in the hierarchy tree above.

### uniform_buffer — Descriptor-type generated cases

`uniform_buffer` is another exact direct child from the delegated descriptor-type registration matrix. Its related suffix, minimum-`NonUniform`, and no-runtime-array variants are visible in the hierarchy tree above.

### uniform_texel_buffer — Descriptor-type generated cases

`uniform_texel_buffer` is another exact direct child from the delegated descriptor-type registration matrix. Its related suffix, minimum-`NonUniform`, and no-runtime-array variants are visible in the hierarchy tree above.

## Parameter Dimensions

This dispatcher file does not define parameter structs, arrays, or loops. It delegates all child construction through [`createTestGroup`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L34-L37). The observed child-name dimensions are defined in the delegated implementation: descriptor-type base names are listed in [`casesAfterBindAndLoop`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4791), suffix loops and guards are visible in [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4831), and misc array-size / coordinate-name loops are visible in [`vktDescriptorIndexingMiscTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L596-L611).

## Support / Feature Requirements

No support checks are implemented in this dispatcher. The dispatcher only forwards category construction to [`descriptorIndexingDescriptorSetsCreateTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L32-L37). Support checks for the registered cases are implemented in delegated implementation files rather than in this source file.

## Verification Methods

No pass/fail validation is implemented in this dispatcher. Verification methods belong to the delegated descriptor-indexing test cases and function cases. This page therefore does not claim a category-wide verification algorithm beyond the observed registration routing.

## Test Principles Observed

- The root package registration gives the user-facing category path `descriptor_indexing`, and both Vulkan and Vulkan SC package creation paths register it to the same dispatcher symbol ([`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1384), [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1451)).
- The dispatcher isolates category group creation from implementation-heavy registration by using [`createTestGroup`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L34-L37) with a forward-declared callback ([`vktDescriptorIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L32)).
- The category has no locally visible branch-header fan-out in this file; child discovery must follow the delegated function and, where practical, mustpass evidence ([`vktDescriptorIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingTests.cpp#L24-L25), [`descriptor-indexing.txt`](../../../mustpass/main/vk-default/descriptor-indexing.txt#L1-L114)).

## Notes / Uncertainties

- A search of [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc) for descriptor-indexing-specific terms did not identify a relevant inspected section, so this page relies on source and mustpass evidence rather than forcing test-plan context.
- This dispatcher page intentionally avoids implementation-heavy details such as per-descriptor feature gates and result comparison logic; those belong in the delegated implementation pages.
- The direct-child list is long because the category root contains direct test cases rather than named nested subgroups in the inspected registration path.
