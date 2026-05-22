# vktDGCGraphicsDrawTestsExt

## Overview

EXT graphics draw tests exercise token_draw and token_draw_indexed generated draws with pipeline construction modes, execution sets, extra stages, preprocessing, unordered sequences, and draw-parameter checks.

## Role of File

This is an implementation file for `dgc.ext.graphics.draw`. The source is [vktDGCGraphicsDrawTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L1). Its registration evidence starts at [vktDGCGraphicsDrawTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2074).

## Registration Hierarchy

```text
dgc.ext.graphics.draw
├── token_draw
└── token_draw_indexed
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCGraphicsDrawTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2074).

- `token_draw` — registered direct child under this Level-3 root.
- `token_draw_indexed` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCGraphicsDrawTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2112) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceCoreFeature(DEVICE_CORE_FEATURE_TESSELLATION_SHADER);](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L389)
- [context.requireDeviceCoreFeature(DEVICE_CORE_FEATURE_GEOMETRY_SHADER);](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L392)
- [context.requireDeviceFunctionality("VK_KHR_shader_draw_parameters");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L395)
- [context.requireDeviceFunctionality("VK_EXT_graphics_pipeline_library");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L400)
- [context.requireDeviceFunctionality("VK_EXT_shader_object");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L407)

## Verification Methods

Verification compares rendered color output against a reference image or buffer expectations. Evidence is in the implementation around [vktDGCGraphicsDrawTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsDrawTestsExt.cpp#L2066).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
