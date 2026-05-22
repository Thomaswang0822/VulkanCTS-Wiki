# vktDGCGraphicsTessStateTestsExt

## Overview

EXT graphics tessellation-state tests vary construction type, primitive type, spacing mode, patch size, preprocessing, and dynamic patch-control-points state.

## Role of File

This is an implementation file for `dgc.ext.graphics.tess_state`. The source is [vktDGCGraphicsTessStateTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1). Its registration evidence starts at [vktDGCGraphicsTessStateTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1162).

## Registration Hierarchy

```text
dgc.ext.graphics.tess_state
├── dynamic_states
├── fast_lib
├── monolithic
└── shader_objects
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCGraphicsTessStateTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1162).

- `dynamic_states` — registered direct child under this Level-3 root.
- `fast_lib` — registered direct child under this Level-3 root.
- `monolithic` — registered direct child under this Level-3 root.
- `shader_objects` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCGraphicsTessStateTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1174) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceCoreFeature(DEVICE_CORE_FEATURE_TESSELLATION_SHADER);](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L216)
- [context.requireDeviceFunctionality("VK_EXT_shader_viewport_index_layer");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L220)

## Verification Methods

Verification compares rendered tessellation results and dynamic-state reference/resolution buffers. Evidence is in the implementation around [vktDGCGraphicsTessStateTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1154).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
