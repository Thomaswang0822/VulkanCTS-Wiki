# vktDGCComputeSubgroupTestsExt

## Overview

EXT compute subgroup tests validate subgroup builtin outputs across workgroup sizes, required subgroup sizes, DGC pipeline tokens, normal pipelines, and queue choices.

## Role of File

This is an implementation file for `dgc.ext.compute.subgroups`. The source is [vktDGCComputeSubgroupTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L1). Its registration evidence starts at [vktDGCComputeSubgroupTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L360).

## Registration Hierarchy

```text
dgc.ext.compute.subgroups
└── builtins
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputeSubgroupTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L360).

- `builtins` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputeSubgroupTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L365) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCComputeSubgroupTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L360).

## Verification Methods

Verification reads output buffers and checks each builtin-derived value against its reference. Evidence is in the implementation around [vktDGCComputeSubgroupTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTestsExt.cpp#L351).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
