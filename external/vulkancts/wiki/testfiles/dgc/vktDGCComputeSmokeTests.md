# vktDGCComputeSmokeTests

## Overview

NV compute smoke tests dispatch generated commands over sequence counts, memory visibility modes, preprocessing modes, and queue choices.

## Role of File

This is an implementation file for `dgc.nv.compute.smoke`. The source is [vktDGCComputeSmokeTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L1). Its registration evidence starts at [vktDGCComputeSmokeTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L558).

## Registration Hierarchy

```text
dgc.nv.compute.smoke
├── 1024_sequences_device_local_from_compute_explicit_preprocess_compute_queue
├── 1024_sequences_device_local_from_compute_explicit_preprocess_universal_queue
├── 1024_sequences_device_local_from_compute_implicit_preprocess_compute_queue
├── 1024_sequences_device_local_from_compute_implicit_preprocess_universal_queue
├── 1024_sequences_device_local_from_host_explicit_preprocess_compute_queue
├── 1024_sequences_device_local_from_host_explicit_preprocess_universal_queue
├── 1024_sequences_device_local_from_host_implicit_preprocess_compute_queue
├── 1024_sequences_device_local_from_host_implicit_preprocess_universal_queue
├── 1024_sequences_host_visible_from_compute_explicit_preprocess_compute_queue
├── 1024_sequences_host_visible_from_compute_explicit_preprocess_universal_queue
├── 1024_sequences_host_visible_from_compute_implicit_preprocess_compute_queue
├── 1024_sequences_host_visible_from_compute_implicit_preprocess_universal_queue
├── 1024_sequences_host_visible_from_host_explicit_preprocess_compute_queue
├── 1024_sequences_host_visible_from_host_explicit_preprocess_universal_queue
├── 1024_sequences_host_visible_from_host_implicit_preprocess_compute_queue
├── 1024_sequences_host_visible_from_host_implicit_preprocess_universal_queue
├── 4_sequences_device_local_from_compute_explicit_preprocess_compute_queue
├── 4_sequences_device_local_from_compute_explicit_preprocess_universal_queue
├── 4_sequences_device_local_from_compute_implicit_preprocess_compute_queue
├── 4_sequences_device_local_from_compute_implicit_preprocess_universal_queue
├── 4_sequences_device_local_from_host_explicit_preprocess_compute_queue
├── 4_sequences_device_local_from_host_explicit_preprocess_universal_queue
├── 4_sequences_device_local_from_host_implicit_preprocess_compute_queue
├── 4_sequences_device_local_from_host_implicit_preprocess_universal_queue
├── 4_sequences_host_visible_from_compute_explicit_preprocess_compute_queue
├── 4_sequences_host_visible_from_compute_explicit_preprocess_universal_queue
├── 4_sequences_host_visible_from_compute_implicit_preprocess_compute_queue
├── 4_sequences_host_visible_from_compute_implicit_preprocess_universal_queue
├── 4_sequences_host_visible_from_host_explicit_preprocess_compute_queue
├── 4_sequences_host_visible_from_host_explicit_preprocess_universal_queue
├── 4_sequences_host_visible_from_host_implicit_preprocess_compute_queue
└── 4_sequences_host_visible_from_host_implicit_preprocess_universal_queue
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputeSmokeTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L558).

- `1024_sequences_device_local_from_compute_explicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_compute_explicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_compute_implicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_compute_implicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_host_explicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_host_explicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_host_implicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_device_local_from_host_implicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_compute_explicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_compute_explicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_compute_implicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_compute_implicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_host_explicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_host_explicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_host_implicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `1024_sequences_host_visible_from_host_implicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_compute_explicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_compute_explicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_compute_implicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_compute_implicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_host_explicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_host_explicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_host_implicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_device_local_from_host_implicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_compute_explicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_compute_explicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_compute_implicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_compute_implicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_host_explicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_host_explicit_preprocess_universal_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_host_implicit_preprocess_compute_queue` — registered direct child under this Level-3 root.
- `4_sequences_host_visible_from_host_implicit_preprocess_universal_queue` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputeSmokeTests case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L560) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCComputeSmokeTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L558).

## Verification Methods

Verification invalidates the result buffer, reconstructs expected per-workgroup counters, and fails on unexpected values. Evidence is in the implementation around [vktDGCComputeSmokeTests verification](../../../modules/vulkan/device_generated_commands/vktDGCComputeSmokeTests.cpp#L549).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
