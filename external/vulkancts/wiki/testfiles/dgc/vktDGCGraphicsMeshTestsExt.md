# vktDGCGraphicsMeshTestsExt

## Overview

EXT graphics mesh tests cover mesh generated draws, draw-count variants, mesh-specific miscellaneous cases, and a nested conditional-rendering subgroup.

## Role of File

This is an implementation file for `dgc.ext.graphics.mesh`. The source is [vktDGCGraphicsMeshTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L1). Its registration evidence starts at [vktDGCGraphicsMeshTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2324).

## Registration Hierarchy

```text
dgc.ext.graphics.mesh
├── conditional_rendering
├── misc
├── token_draw
└── token_draw_count
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCGraphicsMeshTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2324).

- `conditional_rendering` — registered direct child under this Level-3 root.
- `misc` — registered direct child under this Level-3 root.
- `token_draw` — registered direct child under this Level-3 root.
- `token_draw_count` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCGraphicsMeshTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2354) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_EXT_mesh_shader");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L354)
- [context.requireDeviceFunctionality("VK_EXT_shader_object");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L358)
- [context.requireDeviceFunctionality("VK_EXT_mesh_shader");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2124)

## Verification Methods

Verification checks color or output buffers for mesh-draw and mesh-dispatch expectations. Evidence is in the implementation around [vktDGCGraphicsMeshTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshTestsExt.cpp#L2315).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
