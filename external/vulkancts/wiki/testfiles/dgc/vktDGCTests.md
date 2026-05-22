# vktDGCTests

## Overview

Builds the DGC category root, separates NV and EXT branches, and attaches compute, graphics, misc, and ray tracing groups.

## Role of File

This is a registration dispatcher file for `dgc`. The source is [vktDGCTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L1). Its registration evidence starts at [vktDGCTests registration](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L70).

## Registration Hierarchy

```text
dgc
├── ext
└── nv
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCTests registration](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L70).

- `ext` — registered direct child under this Level-3 root.
- `nv` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCTests case generation](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L82) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- No `checkSupport()` payload is defined in this dispatcher file; support checks are implemented in the child test files it attaches under the `nv` and `ext` branches.

## Verification Methods

This dispatcher does not execute a test payload; its observable behavior is the root group construction and `addChild()` hierarchy assembly shown near [vktDGCTests registration](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L70-L120).

## Test Principles

- Construct the `dgc` root and attach the `nv` and `ext` branches.
- Attach child compute, graphics, misc, and ray-tracing groups with explicit `addChild()` calls.
- Leave payload execution and support gates to the child test files.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
