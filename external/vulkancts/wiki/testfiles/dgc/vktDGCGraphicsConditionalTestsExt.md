# vktDGCGraphicsConditionalTestsExt

## Overview

EXT graphics conditional-rendering tests combine generated graphics commands with conditional rendering, count buffers, inverted conditions, and preprocess cases.

## Role of File

This is an implementation file for `dgc.ext.graphics.conditional_rendering`. The source is [vktDGCGraphicsConditionalTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L1). Its registration evidence starts at [vktDGCGraphicsConditionalTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L510).

## Registration Hierarchy

```text
dgc.ext.graphics.conditional_rendering
├── general
└── preprocess
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCGraphicsConditionalTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L510).

- `general` — registered direct child under this Level-3 root.
- `preprocess` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCGraphicsConditionalTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L514) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_EXT_conditional_rendering");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L72)

## Verification Methods

Verification checks rendered output against the expected conditional-rendering reference. Evidence is in the implementation around [vktDGCGraphicsConditionalTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsConditionalTestsExt.cpp#L501).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
