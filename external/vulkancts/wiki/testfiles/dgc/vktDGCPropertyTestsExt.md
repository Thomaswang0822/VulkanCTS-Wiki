# vktDGCPropertyTestsExt

## Overview

EXT property tests validate EXT DGC limits and property-sensitive compute/graphics generated-command scenarios.

## Role of File

This is an implementation file for `dgc.ext.misc.properties`. The source is [vktDGCPropertyTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTestsExt.cpp#L1). Its registration evidence starts at [vktDGCPropertyTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTestsExt.cpp#L817).

## Registration Hierarchy

```text
dgc.ext.misc.properties
├── maxIndirectCommandsStreamIndirect
├── maxIndirectCommandsTokenCount_16
├── maxIndirectCommandsTokenCount_32
├── maxIndirectCommandsTokenOffset
├── maxIndirectSequenceCount
└── valid_limits
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCPropertyTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTestsExt.cpp#L817).

- `maxIndirectCommandsStreamIndirect` — registered direct child under this Level-3 root.
- `maxIndirectCommandsTokenCount_16` — registered direct child under this Level-3 root.
- `maxIndirectCommandsTokenCount_32` — registered direct child under this Level-3 root.
- `maxIndirectCommandsTokenOffset` — registered direct child under this Level-3 root.
- `maxIndirectSequenceCount` — registered direct child under this Level-3 root.
- `valid_limits` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCPropertyTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTestsExt.cpp#L818) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCPropertyTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTestsExt.cpp#L817).

## Verification Methods

Verification includes explicit limit checks and buffer/image comparisons. Evidence is in the implementation around [vktDGCPropertyTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTestsExt.cpp#L808).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
