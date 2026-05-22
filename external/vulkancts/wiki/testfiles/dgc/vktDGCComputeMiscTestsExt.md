# vktDGCComputeMiscTestsExt

## Overview

EXT compute miscellaneous tests cover many dispatches/sequences, scratch space, push-constant ranges, multiple sets, inline uniform blocks, descriptor-buffer push descriptors, and null set-layout info.

## Role of File

This is an implementation file for `dgc.ext.compute.misc`. The source is [vktDGCComputeMiscTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1). Its registration evidence starts at [vktDGCComputeMiscTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2523).

## Registration Hierarchy

```text
dgc.ext.compute.misc
├── descriptor_buffer_push_descriptor
├── descriptor_buffer_push_descriptor_with_ies
├── execute_many_1024_compute_queue
├── execute_many_1024_universal_queue
├── execute_many_64_compute_queue
├── execute_many_64_universal_queue
├── execute_many_8192_compute_queue
├── execute_many_8192_universal_queue
├── iubs
├── iubs_cq
├── iubs_multiset
├── iubs_multiset_cq
├── iubs_with_ies
├── iubs_with_ies_cq
├── iubs_with_ies_multiset
├── iubs_with_ies_multiset_cq
├── many_sequences_1024_compute_queue
├── many_sequences_1024_universal_queue
├── many_sequences_131072_compute_queue
├── many_sequences_131072_universal_queue
├── many_sequences_64_compute_queue
├── many_sequences_64_universal_queue
├── many_sequences_8192_compute_queue
├── many_sequences_8192_universal_queue
├── max_pc_range_128_full
├── max_pc_range_128_full_cq
├── max_pc_range_128_full_preprocess
├── max_pc_range_128_full_preprocess_cq
├── max_pc_range_128_full_preprocess_push_descriptor
├── max_pc_range_128_full_preprocess_push_descriptor_cq
├── max_pc_range_128_full_preprocess_with_execution_set
├── max_pc_range_128_full_preprocess_with_execution_set_cq
├── max_pc_range_128_full_preprocess_with_execution_set_push_descriptor
├── max_pc_range_128_full_preprocess_with_execution_set_push_descriptor_cq
├── max_pc_range_128_full_push_descriptor
├── max_pc_range_128_full_push_descriptor_cq
├── max_pc_range_128_full_with_execution_set
├── max_pc_range_128_full_with_execution_set_cq
├── max_pc_range_128_full_with_execution_set_push_descriptor
├── max_pc_range_128_full_with_execution_set_push_descriptor_cq
├── max_pc_range_128_partial
├── max_pc_range_128_partial_cq
├── max_pc_range_128_partial_preprocess
├── max_pc_range_128_partial_preprocess_cq
├── max_pc_range_128_partial_preprocess_push_descriptor
├── max_pc_range_128_partial_preprocess_push_descriptor_cq
├── max_pc_range_128_partial_preprocess_with_execution_set
├── max_pc_range_128_partial_preprocess_with_execution_set_cq
├── max_pc_range_128_partial_preprocess_with_execution_set_push_descriptor
├── max_pc_range_128_partial_preprocess_with_execution_set_push_descriptor_cq
├── max_pc_range_128_partial_push_descriptor
├── max_pc_range_128_partial_push_descriptor_cq
├── max_pc_range_128_partial_with_execution_set
├── max_pc_range_128_partial_with_execution_set_cq
├── max_pc_range_128_partial_with_execution_set_push_descriptor
├── max_pc_range_128_partial_with_execution_set_push_descriptor_cq
├── max_pc_range_256_full
├── max_pc_range_256_full_cq
├── max_pc_range_256_full_preprocess
├── max_pc_range_256_full_preprocess_cq
├── max_pc_range_256_full_preprocess_push_descriptor
├── max_pc_range_256_full_preprocess_push_descriptor_cq
├── max_pc_range_256_full_preprocess_with_execution_set
├── max_pc_range_256_full_preprocess_with_execution_set_cq
├── max_pc_range_256_full_preprocess_with_execution_set_push_descriptor
├── max_pc_range_256_full_preprocess_with_execution_set_push_descriptor_cq
├── max_pc_range_256_full_push_descriptor
├── max_pc_range_256_full_push_descriptor_cq
├── max_pc_range_256_full_with_execution_set
├── max_pc_range_256_full_with_execution_set_cq
├── max_pc_range_256_full_with_execution_set_push_descriptor
├── max_pc_range_256_full_with_execution_set_push_descriptor_cq
├── max_pc_range_256_partial
├── max_pc_range_256_partial_cq
├── max_pc_range_256_partial_preprocess
├── max_pc_range_256_partial_preprocess_cq
├── max_pc_range_256_partial_preprocess_push_descriptor
├── max_pc_range_256_partial_preprocess_push_descriptor_cq
├── max_pc_range_256_partial_preprocess_with_execution_set
├── max_pc_range_256_partial_preprocess_with_execution_set_cq
├── max_pc_range_256_partial_preprocess_with_execution_set_push_descriptor
├── max_pc_range_256_partial_preprocess_with_execution_set_push_descriptor_cq
├── max_pc_range_256_partial_push_descriptor
├── max_pc_range_256_partial_push_descriptor_cq
├── max_pc_range_256_partial_with_execution_set
├── max_pc_range_256_partial_with_execution_set_cq
├── max_pc_range_256_partial_with_execution_set_push_descriptor
├── max_pc_range_256_partial_with_execution_set_push_descriptor_cq
├── max_pc_range_4096_full
├── max_pc_range_4096_full_cq
├── max_pc_range_4096_full_preprocess
├── max_pc_range_4096_full_preprocess_cq
├── max_pc_range_4096_full_preprocess_push_descriptor
├── max_pc_range_4096_full_preprocess_push_descriptor_cq
├── max_pc_range_4096_full_preprocess_with_execution_set
├── max_pc_range_4096_full_preprocess_with_execution_set_cq
├── max_pc_range_4096_full_preprocess_with_execution_set_push_descriptor
├── max_pc_range_4096_full_preprocess_with_execution_set_push_descriptor_cq
├── max_pc_range_4096_full_push_descriptor
├── max_pc_range_4096_full_push_descriptor_cq
├── max_pc_range_4096_full_with_execution_set
├── max_pc_range_4096_full_with_execution_set_cq
├── max_pc_range_4096_full_with_execution_set_push_descriptor
├── max_pc_range_4096_full_with_execution_set_push_descriptor_cq
├── max_pc_range_4096_partial
├── max_pc_range_4096_partial_cq
├── max_pc_range_4096_partial_preprocess
├── max_pc_range_4096_partial_preprocess_cq
├── max_pc_range_4096_partial_preprocess_push_descriptor
├── max_pc_range_4096_partial_preprocess_push_descriptor_cq
├── max_pc_range_4096_partial_preprocess_with_execution_set
├── max_pc_range_4096_partial_preprocess_with_execution_set_cq
├── max_pc_range_4096_partial_preprocess_with_execution_set_push_descriptor
├── max_pc_range_4096_partial_preprocess_with_execution_set_push_descriptor_cq
├── max_pc_range_4096_partial_push_descriptor
├── max_pc_range_4096_partial_push_descriptor_cq
├── max_pc_range_4096_partial_with_execution_set
├── max_pc_range_4096_partial_with_execution_set_cq
├── max_pc_range_4096_partial_with_execution_set_push_descriptor
├── max_pc_range_4096_partial_with_execution_set_push_descriptor_cq
├── multiple_sets
├── multiple_sets_cq
├── multiple_sets_preprocess
├── multiple_sets_preprocess_cq
├── null_set_layouts_info
├── scratch_space
├── two_cmd_buffers
├── two_cmd_buffers_cq
├── two_cmd_buffers_cq_with_ies
└── two_cmd_buffers_with_ies
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputeMiscTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2523).

- `descriptor_buffer_push_descriptor` — registered direct child under this Level-3 root.
- `descriptor_buffer_push_descriptor_with_ies` — registered direct child under this Level-3 root.
- `execute_many_1024_compute_queue` — registered direct child under this Level-3 root.
- `execute_many_1024_universal_queue` — registered direct child under this Level-3 root.
- `execute_many_64_compute_queue` — registered direct child under this Level-3 root.
- `execute_many_64_universal_queue` — registered direct child under this Level-3 root.
- `execute_many_8192_compute_queue` — registered direct child under this Level-3 root.
- `execute_many_8192_universal_queue` — registered direct child under this Level-3 root.
- `iubs` — registered direct child under this Level-3 root.
- `iubs_cq` — registered direct child under this Level-3 root.
- `iubs_multiset` — registered direct child under this Level-3 root.
- `iubs_multiset_cq` — registered direct child under this Level-3 root.
- `iubs_with_ies` — registered direct child under this Level-3 root.
- `iubs_with_ies_cq` — registered direct child under this Level-3 root.
- `iubs_with_ies_multiset` — registered direct child under this Level-3 root.
- `iubs_with_ies_multiset_cq` — registered direct child under this Level-3 root.
- `many_sequences_1024_compute_queue` — registered direct child under this Level-3 root.
- `many_sequences_1024_universal_queue` — registered direct child under this Level-3 root.
- `many_sequences_131072_compute_queue` — registered direct child under this Level-3 root.
- `many_sequences_131072_universal_queue` — registered direct child under this Level-3 root.
- `many_sequences_64_compute_queue` — registered direct child under this Level-3 root.
- `many_sequences_64_universal_queue` — registered direct child under this Level-3 root.
- `many_sequences_8192_compute_queue` — registered direct child under this Level-3 root.
- `many_sequences_8192_universal_queue` — registered direct child under this Level-3 root.
- `max_pc_range_128_full` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_preprocess` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_preprocess_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_preprocess_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_preprocess_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_preprocess_with_execution_set` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_preprocess_with_execution_set_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_preprocess_with_execution_set_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_preprocess_with_execution_set_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_with_execution_set` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_with_execution_set_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_with_execution_set_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_128_full_with_execution_set_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_preprocess` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_preprocess_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_preprocess_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_preprocess_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_preprocess_with_execution_set` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_preprocess_with_execution_set_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_preprocess_with_execution_set_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_preprocess_with_execution_set_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_with_execution_set` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_with_execution_set_cq` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_with_execution_set_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_128_partial_with_execution_set_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_full` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_preprocess` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_preprocess_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_preprocess_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_preprocess_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_preprocess_with_execution_set` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_preprocess_with_execution_set_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_preprocess_with_execution_set_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_preprocess_with_execution_set_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_with_execution_set` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_with_execution_set_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_with_execution_set_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_256_full_with_execution_set_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_partial` — registered direct child under this Level-3 root.
- `max_pc_range_256_partial_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_partial_preprocess` — registered direct child under this Level-3 root.
- `max_pc_range_256_partial_preprocess_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_partial_preprocess_push_descriptor` — registered direct child under this Level-3 root.
- `max_pc_range_256_partial_preprocess_push_descriptor_cq` — registered direct child under this Level-3 root.
- `max_pc_range_256_partial_preprocess_with_execution_set` — registered direct child under this Level-3 root.
- `max_pc_range_256_partial_preprocess_with_execution_set_cq` — registered direct child under this Level-3 root.
- Additional direct children: 50 more names are listed in the hierarchy tree above.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputeMiscTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2525) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_EXT_shader_object");](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L87)
- [context.requireDeviceFunctionality("VK_KHR_push_descriptor");](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1223)
- [context.requireDeviceFunctionality("VK_EXT_inline_uniform_block");](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L1757)
- [context.requireDeviceFunctionality("VK_EXT_descriptor_buffer");](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2198)
- [context.requireDeviceFunctionality("VK_KHR_push_descriptor");](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2199)

## Verification Methods

Verification uses output-buffer comparisons for each specialized miscellaneous case. Evidence is in the implementation around [vktDGCComputeMiscTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTestsExt.cpp#L2514).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
