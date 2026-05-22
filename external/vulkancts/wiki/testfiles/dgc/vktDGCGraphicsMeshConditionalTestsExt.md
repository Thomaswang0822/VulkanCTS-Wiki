# vktDGCGraphicsMeshConditionalTestsExt

## Overview

EXT mesh conditional-rendering tests attach under the mesh group and exercise mesh DGC conditional rendering for general and preprocess paths.

## Role of File

This is a nested implementation file for `dgc.ext.graphics.mesh.conditional_rendering`. The source is [vktDGCGraphicsMeshConditionalTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L1). Its registration evidence starts at [vktDGCGraphicsMeshConditionalTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L680).

## Registration Hierarchy

```text
dgc.ext.graphics.mesh.conditional_rendering
├── general
└── preprocess
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCGraphicsMeshConditionalTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L680).

- `general` — registered direct child under this Level-3 root.
- `preprocess` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCGraphicsMeshConditionalTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L704) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_EXT_mesh_shader");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L96)
- [context.requireDeviceFunctionality("VK_EXT_conditional_rendering");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L97)

## Verification Methods

Verification checks color/output buffers for condition-controlled mesh execution. Evidence is in the implementation around [vktDGCGraphicsMeshConditionalTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMeshConditionalTestsExt.cpp#L726).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
