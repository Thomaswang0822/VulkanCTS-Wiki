# vktDGCComputeSmokeTestsExt

## Overview

EXT compute smoke tests run generated dispatches with host-visible/device-local input, host/compute input generation, preprocess state choices, and queue choices.

## Role of File

This is an implementation file for `dgc.ext.compute.smoke`. The source is [vktDGCComputeSmokeTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L1). Its registration evidence starts at [vktDGCComputeSmokeTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L588).

## Registration Hierarchy

```text
dgc.ext.compute.smoke
├── 1024_sequences_device_local_from_compute_no_preprocess_compute_queue
├── 1024_sequences_device_local_from_compute_no_preprocess_universal_queue
├── 1024_sequences_device_local_from_compute_preprocess_state_same_compute_queue
├── 1024_sequences_device_local_from_compute_preprocess_state_same_universal_queue
├── 1024_sequences_device_local_from_compute_preprocess_state_separate_compute_queue
├── 1024_sequences_device_local_from_compute_preprocess_state_separate_universal_queue
├── 1024_sequences_device_local_from_host_no_preprocess_compute_queue
├── 1024_sequences_device_local_from_host_no_preprocess_universal_queue
├── 1024_sequences_device_local_from_host_preprocess_state_same_compute_queue
├── 1024_sequences_device_local_from_host_preprocess_state_same_universal_queue
├── 1024_sequences_device_local_from_host_preprocess_state_separate_compute_queue
├── 1024_sequences_device_local_from_host_preprocess_state_separate_universal_queue
├── 1024_sequences_host_visible_from_compute_no_preprocess_compute_queue
├── 1024_sequences_host_visible_from_compute_no_preprocess_universal_queue
├── 1024_sequences_host_visible_from_compute_preprocess_state_same_compute_queue
├── 1024_sequences_host_visible_from_compute_preprocess_state_same_universal_queue
├── 1024_sequences_host_visible_from_compute_preprocess_state_separate_compute_queue
├── 1024_sequences_host_visible_from_compute_preprocess_state_separate_universal_queue
├── 1024_sequences_host_visible_from_host_no_preprocess_compute_queue
├── 1024_sequences_host_visible_from_host_no_preprocess_universal_queue
├── 1024_sequences_host_visible_from_host_preprocess_state_same_compute_queue
├── 1024_sequences_host_visible_from_host_preprocess_state_same_universal_queue
├── 1024_sequences_host_visible_from_host_preprocess_state_separate_compute_queue
├── 1024_sequences_host_visible_from_host_preprocess_state_separate_universal_queue
├── 4_sequences_device_local_from_compute_no_preprocess_compute_queue
├── 4_sequences_device_local_from_compute_no_preprocess_universal_queue
├── 4_sequences_device_local_from_compute_preprocess_state_same_compute_queue
├── 4_sequences_device_local_from_compute_preprocess_state_same_universal_queue
├── 4_sequences_device_local_from_compute_preprocess_state_separate_compute_queue
├── 4_sequences_device_local_from_compute_preprocess_state_separate_universal_queue
├── 4_sequences_device_local_from_host_no_preprocess_compute_queue
├── 4_sequences_device_local_from_host_no_preprocess_universal_queue
├── 4_sequences_device_local_from_host_preprocess_state_same_compute_queue
├── 4_sequences_device_local_from_host_preprocess_state_same_universal_queue
├── 4_sequences_device_local_from_host_preprocess_state_separate_compute_queue
├── 4_sequences_device_local_from_host_preprocess_state_separate_universal_queue
├── 4_sequences_host_visible_from_compute_no_preprocess_compute_queue
├── 4_sequences_host_visible_from_compute_no_preprocess_universal_queue
├── 4_sequences_host_visible_from_compute_preprocess_state_same_compute_queue
├── 4_sequences_host_visible_from_compute_preprocess_state_same_universal_queue
├── 4_sequences_host_visible_from_compute_preprocess_state_separate_compute_queue
├── 4_sequences_host_visible_from_compute_preprocess_state_separate_universal_queue
├── 4_sequences_host_visible_from_host_no_preprocess_compute_queue
├── 4_sequences_host_visible_from_host_no_preprocess_universal_queue
├── 4_sequences_host_visible_from_host_preprocess_state_same_compute_queue
├── 4_sequences_host_visible_from_host_preprocess_state_same_universal_queue
├── 4_sequences_host_visible_from_host_preprocess_state_separate_compute_queue
└── 4_sequences_host_visible_from_host_preprocess_state_separate_universal_queue
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputeSmokeTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L588).

- `1024_sequences_device_local_from_compute_no_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_compute_no_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_compute_preprocess_state_same_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_compute_preprocess_state_same_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_compute_preprocess_state_separate_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_compute_preprocess_state_separate_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_host_no_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_host_no_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_host_preprocess_state_same_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_host_preprocess_state_same_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_host_preprocess_state_separate_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_host_preprocess_state_separate_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_compute_no_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_compute_no_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_compute_preprocess_state_same_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_compute_preprocess_state_same_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_compute_preprocess_state_separate_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_compute_preprocess_state_separate_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_host_no_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_host_no_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_host_preprocess_state_same_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_host_preprocess_state_same_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_host_preprocess_state_separate_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_host_preprocess_state_separate_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_compute_no_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_compute_no_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_compute_preprocess_state_same_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_compute_preprocess_state_same_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_compute_preprocess_state_separate_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_compute_preprocess_state_separate_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_host_no_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_host_no_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_host_preprocess_state_same_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_host_preprocess_state_same_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_host_preprocess_state_separate_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_host_preprocess_state_separate_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_compute_no_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_compute_no_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_compute_preprocess_state_same_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_compute_preprocess_state_same_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_compute_preprocess_state_separate_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_compute_preprocess_state_separate_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_host_no_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_host_no_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_host_preprocess_state_same_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_host_preprocess_state_same_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_host_preprocess_state_separate_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_host_preprocess_state_separate_universal_queue` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputeSmokeTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L600) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCComputeSmokeTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L588).

## Verification Methods

Verification rebuilds expected per-dispatch output ranges and fails on unexpected results. Evidence is in the implementation around [vktDGCComputeSmokeTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTestsExt.cpp#L579).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
