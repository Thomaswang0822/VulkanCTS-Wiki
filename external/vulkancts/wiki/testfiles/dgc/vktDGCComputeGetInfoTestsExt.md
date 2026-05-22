# vktDGCComputeGetInfoTestsExt

## Overview

EXT compute get-info tests check generated-command memory requirements across basic, pipeline, unordered, count-growth, and max-sequence-count cases.

## Role of File

This is an implementation file for `dgc.ext.compute.get_info`. The source is [vktDGCComputeGetInfoTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L1). Its registration evidence starts at [vktDGCComputeGetInfoTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L260).

## Registration Hierarchy

```text
dgc.ext.compute.get_info
├── constant_cmd_memory_requirements_basic_case
├── constant_cmd_memory_requirements_basic_case_with_pipeline
├── constant_cmd_memory_requirements_ignore_unordered_flag
├── constant_cmd_memory_requirements_increase_count
└── constant_cmd_memory_requirements_max_sequence_count
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputeGetInfoTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L260).

- `constant_cmd_memory_requirements_basic_case` — registered direct child under this Level-3 root.
- `constant_cmd_memory_requirements_basic_case_with_pipeline` — registered direct child under this Level-3 root.
- `constant_cmd_memory_requirements_ignore_unordered_flag` — registered direct child under this Level-3 root.
- `constant_cmd_memory_requirements_increase_count` — registered direct child under this Level-3 root.
- `constant_cmd_memory_requirements_max_sequence_count` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputeGetInfoTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L279) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCComputeGetInfoTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L260).

## Verification Methods

Verification compares memory requirement size, alignment, and type bits across input variants. Evidence is in the implementation around [vktDGCComputeGetInfoTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L279).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
