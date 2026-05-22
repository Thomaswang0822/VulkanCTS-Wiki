# vktDGCPropertyTests

## Overview

NV property tests verify advertised DGC limits and property-dependent generated command behavior.

## Role of File

This is an implementation file for `dgc.nv.misc.properties`. The source is [vktDGCPropertyTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1). Its registration evidence starts at [vktDGCPropertyTests registration](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1236).

## Registration Hierarchy

```text
dgc.nv.misc.properties
├── maxIndirectCommandsStreamCount
├── maxIndirectCommandsStreamStrideRun
├── maxIndirectCommandsTokenCount
├── maxIndirectCommandsTokenOffset
├── minIndirectCommandsBufferOffsetAlignment_offset_256
├── minIndirectCommandsBufferOffsetAlignment_offset_4
├── minIndirectCommandsBufferOffsetAlignment_offset_8
├── minSequencesCountBufferOffsetAlignment
├── minSequencesIndexBufferOffsetAlignment
└── valid_limits
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCPropertyTests registration](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1236).

- `maxIndirectCommandsStreamCount` — registered direct child under this Level-3 root.
- `maxIndirectCommandsStreamStrideRun` — registered direct child under this Level-3 root.
- `maxIndirectCommandsTokenCount` — registered direct child under this Level-3 root.
- `maxIndirectCommandsTokenOffset` — registered direct child under this Level-3 root.
- `minIndirectCommandsBufferOffsetAlignment_offset_256` — registered direct child under this Level-3 root.
- `minIndirectCommandsBufferOffsetAlignment_offset_4` — registered direct child under this Level-3 root.
- `minIndirectCommandsBufferOffsetAlignment_offset_8` — registered direct child under this Level-3 root.
- `minSequencesCountBufferOffsetAlignment` — registered direct child under this Level-3 root.
- `minSequencesIndexBufferOffsetAlignment` — registered direct child under this Level-3 root.
- `valid_limits` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCPropertyTests case generation](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1237) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCPropertyTests registration](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1236).

## Verification Methods

Verification covers valid-limit assertions plus output-buffer checks for limit-sensitive generated-command cases. Evidence is in the implementation around [vktDGCPropertyTests verification](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1170).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
