# vktDGCComputePreprocessTests

## Overview

NV compute preprocess tests vary preprocess method, count-buffer use, queue ownership transitions, and zero-count handling.

## Role of File

This is an implementation file for `dgc.nv.compute.preprocess`. The source is [vktDGCComputePreprocessTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L1). Its registration evidence starts at [vktDGCComputePreprocessTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L502).

## Registration Hierarchy

```text
dgc.nv.compute.preprocess
├── parallel_preprocessing_compute
├── parallel_preprocessing_compute_with_count_buffer
├── parallel_preprocessing_compute_with_count_buffer_zero_count
├── parallel_preprocessing_compute_with_universal_exec
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer
├── parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count
├── parallel_preprocessing_universal
├── parallel_preprocessing_universal_with_compute_exec
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer
├── parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count
├── parallel_preprocessing_universal_with_count_buffer
└── parallel_preprocessing_universal_with_count_buffer_zero_count
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputePreprocessTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L502).

- `parallel_preprocessing_compute` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_count_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_count_buffer_zero_count` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_universal_exec` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_universal_exec_with_count_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_compute_with_universal_exec_with_count_buffer_zero_count` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_compute_exec` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_compute_exec_with_count_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_compute_exec_with_count_buffer_zero_count` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_count_buffer` — registered direct child under this Level-3 root.
- `parallel_preprocessing_universal_with_count_buffer_zero_count` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputePreprocessTests case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L529) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCComputePreprocessTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L502).

## Verification Methods

Verification reads per-run output buffers and compares each value against its reference. Evidence is in the implementation around [vktDGCComputePreprocessTests verification](../../../modules/vulkan/device_generated_commands/vktDGCComputePreprocessTests.cpp#L491).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
