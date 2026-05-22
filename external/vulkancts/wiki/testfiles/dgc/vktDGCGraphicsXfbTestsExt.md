# vktDGCGraphicsXfbTestsExt

## Overview

EXT graphics transform-feedback tests combine discard modes, geometry/tessellation stages, and shader-object variants.

## Role of File

This is an implementation file for `dgc.ext.graphics.xfb`. The source is [vktDGCGraphicsXfbTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L1). Its registration evidence starts at [vktDGCGraphicsXfbTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L887).

## Registration Hierarchy

```text
dgc.ext.graphics.xfb
├── discard
├── discard_geom
├── discard_geom_shader_objects
├── discard_shader_objects
├── discard_tess
├── discard_tess_geom
├── discard_tess_geom_shader_objects
├── discard_tess_shader_objects
├── nodiscard
├── nodiscard_geom
├── nodiscard_geom_shader_objects
├── nodiscard_shader_objects
├── nodiscard_tess
├── nodiscard_tess_geom
├── nodiscard_tess_geom_shader_objects
└── nodiscard_tess_shader_objects
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCGraphicsXfbTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L887).

- `discard` — registered direct child under this Level-3 root.
- `discard_geom` — registered direct child under this Level-3 root.
- `discard_geom_shader_objects` — registered direct child under this Level-3 root.
- `discard_shader_objects` — registered direct child under this Level-3 root.
- `discard_tess` — registered direct child under this Level-3 root.
- `discard_tess_geom` — registered direct child under this Level-3 root.
- `discard_tess_geom_shader_objects` — registered direct child under this Level-3 root.
- `discard_tess_shader_objects` — registered direct child under this Level-3 root.
- `nodiscard` — registered direct child under this Level-3 root.
- `nodiscard_geom` — registered direct child under this Level-3 root.
- `nodiscard_geom_shader_objects` — registered direct child under this Level-3 root.
- `nodiscard_shader_objects` — registered direct child under this Level-3 root.
- `nodiscard_tess` — registered direct child under this Level-3 root.
- `nodiscard_tess_geom` — registered direct child under this Level-3 root.
- `nodiscard_tess_geom_shader_objects` — registered direct child under this Level-3 root.
- `nodiscard_tess_shader_objects` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCGraphicsXfbTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L889) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_EXT_shader_object");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L120)
- [context.requireDeviceCoreFeature(DEVICE_CORE_FEATURE_GEOMETRY_SHADER);](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L123)
- [context.requireDeviceCoreFeature(DEVICE_CORE_FEATURE_TESSELLATION_SHADER);](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L126)

## Verification Methods

Verification compares transform-feedback output triangles and draw results against references. Evidence is in the implementation around [vktDGCGraphicsXfbTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsXfbTestsExt.cpp#L878).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
