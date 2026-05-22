# vktDGCGraphicsDrawCountTestsExt

## Overview

EXT graphics draw-count tests exercise token_draw_count and token_draw_indexed_count with execution sets, shader objects, preprocessing, unordered sequences, and draw-parameter checks.

## Role of File

This is an implementation file for `dgc.ext.graphics.draw_count`. The source is [vktDGCGraphicsDrawCountTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1). Its registration evidence starts at [vktDGCGraphicsDrawCountTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1471).

## Registration Hierarchy

```text
dgc.ext.graphics.draw_count
├── token_draw_count
└── token_draw_indexed_count
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCGraphicsDrawCountTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1471).

- `token_draw_count` — registered direct child under this Level-3 root.
- `token_draw_indexed_count` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCGraphicsDrawCountTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1496) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_EXT_shader_object");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L202)
- [context.requireDeviceFunctionality("VK_KHR_shader_draw_parameters");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L209)

## Verification Methods

Verification compares the color attachment against expected covered and uncovered pixel regions. Evidence is in the implementation around [vktDGCGraphicsDrawCountTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawCountTestsExt.cpp#L1464).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
