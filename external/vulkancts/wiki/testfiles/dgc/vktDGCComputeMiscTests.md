# vktDGCComputeMiscTests

## Overview

NV compute miscellaneous tests cover repeated execution, full replay, and scratch-space behavior.

## Role of File

This is an implementation file for `dgc.nv.compute.misc`. The source is [vktDGCComputeMiscTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L1). Its registration evidence starts at [vktDGCComputeMiscTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L737).

## Registration Hierarchy

```text
dgc.nv.compute.misc
├── execute_many_1024_primary_cmd_compute_queue
├── execute_many_1024_primary_cmd_universal_queue
├── execute_many_1024_secondary_cmd_compute_queue
├── execute_many_1024_secondary_cmd_universal_queue
├── execute_many_64_primary_cmd_compute_queue
├── execute_many_64_primary_cmd_universal_queue
├── execute_many_64_secondary_cmd_compute_queue
├── execute_many_64_secondary_cmd_universal_queue
├── execute_many_8192_primary_cmd_compute_queue
├── execute_many_8192_primary_cmd_universal_queue
├── execute_many_8192_secondary_cmd_compute_queue
├── execute_many_8192_secondary_cmd_universal_queue
├── full_replay
└── scratch_space
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputeMiscTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L737).

- `execute_many_1024_primary_cmd_compute_queue` — registered direct child under this Level-3 root.
- `execute_many_1024_primary_cmd_universal_queue` — registered direct child under this Level-3 root.
- `execute_many_1024_secondary_cmd_compute_queue` — registered direct child under this Level-3 root.
- `execute_many_1024_secondary_cmd_universal_queue` — registered direct child under this Level-3 root.
- `execute_many_64_primary_cmd_compute_queue` — registered direct child under this Level-3 root.
- `execute_many_64_primary_cmd_universal_queue` — registered direct child under this Level-3 root.
- `execute_many_64_secondary_cmd_compute_queue` — registered direct child under this Level-3 root.
- `execute_many_64_secondary_cmd_universal_queue` — registered direct child under this Level-3 root.
- `execute_many_8192_primary_cmd_compute_queue` — registered direct child under this Level-3 root.
- `execute_many_8192_primary_cmd_universal_queue` — registered direct child under this Level-3 root.
- `execute_many_8192_secondary_cmd_compute_queue` — registered direct child under this Level-3 root.
- `execute_many_8192_secondary_cmd_universal_queue` — registered direct child under this Level-3 root.
- `full_replay` — registered direct child under this Level-3 root.
- `scratch_space` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputeMiscTests case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L739) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCComputeMiscTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L737).

## Verification Methods

Verification reads output buffers and fails when expected values or replay properties do not match. Evidence is in the implementation around [vktDGCComputeMiscTests verification](../../../modules/vulkan/device_generated_commands/vktDGCComputeMiscTests.cpp#L728).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
