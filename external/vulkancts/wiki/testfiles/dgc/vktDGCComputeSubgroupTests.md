# vktDGCComputeSubgroupTests

## Overview

NV compute subgroup tests validate subgroup builtin observations under generated-command and normal-pipeline dispatch paths.

## Role of File

This is an implementation file for `dgc.nv.compute.subgroups`. The source is [vktDGCComputeSubgroupTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L1). Its registration evidence starts at [vktDGCComputeSubgroupTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L363).

## Registration Hierarchy

```text
dgc.nv.compute.subgroups
└── builtins
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputeSubgroupTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L363).

- `builtins` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputeSubgroupTests case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L382) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCComputeSubgroupTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L363).

## Verification Methods

Verification compares output values for subgroup builtins and reports unexpected buffer contents. Evidence is in the implementation around [vktDGCComputeSubgroupTests verification](../../../modules/vulkan/device_generated_commands/vktDGCComputeSubgroupTests.cpp#L351).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
