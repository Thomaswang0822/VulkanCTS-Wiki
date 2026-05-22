# vktDGCComputeConditionalTests

## Overview

NV compute conditional-rendering tests combine pipeline-token/classic bind modes, count buffers, condition values, inverted flags, and preprocess-only flows.

## Role of File

This is an implementation file for `dgc.nv.compute.conditional_rendering`. The source is [vktDGCComputeConditionalTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L1). Its registration evidence starts at [vktDGCComputeConditionalTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L619).

## Registration Hierarchy

```text
dgc.nv.compute.conditional_rendering
├── general
└── preprocess
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputeConditionalTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L619).

- `general` — registered direct child under this Level-3 root.
- `preprocess` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputeConditionalTests case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L652) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_EXT_conditional_rendering");](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L81)

## Verification Methods

Verification checks output buffers for expected conditional execution results. Evidence is in the implementation around [vktDGCComputeConditionalTests verification](../../../modules/vulkan/device_generated_commands/vktDGCComputeConditionalTests.cpp#L584).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
