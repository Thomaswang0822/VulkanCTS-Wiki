# vktDGCGraphicsMultiviewTestsExt

## Overview

EXT graphics multiview tests vary view masks, pipeline construction, indirect vertex/index tokens, dynamic rendering, preprocessing, and indirect execution sets.

## Role of File

This is an implementation file for `dgc.ext.graphics.multiview`. The source is [vktDGCGraphicsMultiviewTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L1). Its registration evidence starts at [vktDGCGraphicsMultiviewTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L828).

## Registration Hierarchy

```text
dgc.ext.graphics.multiview
├── view_mask_1
├── view_mask_2
└── view_mask_3
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCGraphicsMultiviewTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L828).

- `view_mask_1` — registered direct child under this Level-3 root.
- `view_mask_2` — registered direct child under this Level-3 root.
- `view_mask_3` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCGraphicsMultiviewTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L819) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_EXT_graphics_pipeline_library");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L166)
- [context.requireDeviceFunctionality("VK_EXT_extended_dynamic_state");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L169)
- [context.requireDeviceFunctionality("VK_KHR_dynamic_rendering");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L172)
- [context.requireDeviceFunctionality("VK_KHR_multiview");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L174)

## Verification Methods

Verification compares color and depth layers for active multiview layers. Evidence is in the implementation around [vktDGCGraphicsMultiviewTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMultiviewTestsExt.cpp#L761).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
