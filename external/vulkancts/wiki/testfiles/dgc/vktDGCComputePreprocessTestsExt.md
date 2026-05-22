# vktDGCComputePreprocessTestsExt

## Overview

EXT compute preprocess tests vary preprocess and execute queues, count buffers, zero counts, and separate state command buffers.

## Role of File

This is an implementation file for `dgc.ext.compute.preprocess`. The source is [vktDGCComputePreprocessTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L1). Its registration evidence starts at [vktDGCComputePreprocessTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L531).

## Registration Hierarchy

```text
dgc.ext.compute.preprocess
├── parallel_preprocessing_compute
├── parallel_preprocessing_compute_separate_state_cmd_buffer
├── parallel_preprocessing_compute_with_count_buffer
├── parallel_preprocessing_compute_with_count_buffer_separate_state_cmd_buffer
├── parallel_preprocessing_compute_with_count_buffer_zero_count
├── parallel_preprocessing_compute_with_count_buffer_zero_count_separate_state_cmd_buffer
├── parallel_preprocessing_compute_with_universal_exec
├── parallel_preprocessing_compute_with_universal_exec_separate_state_cmd_buffer
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer_separate_state_cmd_buffer
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count_separate_state_cmd_buffer
├── parallel_preprocessing_universal
├── parallel_preprocessing_universal_separate_state_cmd_buffer
├── parallel_preprocessing_universal_with_compute_exec
├── parallel_preprocessing_universal_with_compute_exec_separate_state_cmd_buffer
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer_separate_state_cmd_buffer
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count_separate_state_cmd_buffer
├── parallel_preprocessing_universal_with_count_buffer
├── parallel_preprocessing_universal_with_count_buffer_separate_state_cmd_buffer
├── parallel_preprocessing_universal_with_count_buffer_zero_count
└── parallel_preprocessing_universal_with_count_buffer_zero_count_separate_state_cmd_buffer
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputePreprocessTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L531).

- `parallel_preprocessing_compute` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_count_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_count_buffer_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_count_buffer_zero_count` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_count_buffer_zero_count_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_universal_exec` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_universal_exec_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_universal_exec_with_count_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_universal_exec_with_count_buffer_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_compute_exec` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_compute_exec_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_compute_exec_with_count_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_compute_exec_with_count_buffer_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_count_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_count_buffer_separate_state_cmd_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_count_buffer_zero_count` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_count_buffer_zero_count_separate_state_cmd_buffer` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputePreprocessTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L563) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCComputePreprocessTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L531).

## Verification Methods

Verification compares each output buffer value with the expected reference after preprocessing and execution. Evidence is in the implementation around [vktDGCComputePreprocessTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTestsExt.cpp#L521).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
