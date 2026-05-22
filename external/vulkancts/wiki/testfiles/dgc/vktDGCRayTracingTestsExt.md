# vktDGCRayTracingTestsExt

## Overview

EXT ray tracing tests exercise generated ray tracing commands with/without execution sets, preprocessing, unordered sequences, and compute-queue execution.

## Role of File

This is an implementation file for `dgc.ext.ray_tracing`. The source is [vktDGCRayTracingTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1). Its registration evidence starts at [vktDGCRayTracingTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1996).

## Registration Hierarchy

```text
dgc.ext.ray_tracing
├── no_execution_set
├── no_execution_set_cq
├── no_execution_set_preprocess
├── no_execution_set_preprocess_cq
├── no_execution_set_preprocess_unordered
├── no_execution_set_preprocess_unordered_cq
├── no_execution_set_unordered
├── no_execution_set_unordered_cq
├── with_execution_set
├── with_execution_set_cq
├── with_execution_set_preprocess
├── with_execution_set_preprocess_cq
├── with_execution_set_preprocess_unordered
├── with_execution_set_preprocess_unordered_cq
├── with_execution_set_unordered
└── with_execution_set_unordered_cq
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCRayTracingTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1996).

- `no_execution_set` — registered direct child under this Level-3 root.
- `no_execution_set_cq` — registered direct child under this Level-3 root.
- `no_execution_set_preprocess` — registered direct child under this Level-3 root.
- `no_execution_set_preprocess_cq` — registered direct child under this Level-3 root.
- `no_execution_set_preprocess_unordered` — registered direct child under this Level-3 root.
- `no_execution_set_preprocess_unordered_cq` — registered direct child under this Level-3 root.
- `no_execution_set_unordered` — registered direct child under this Level-3 root.
- `no_execution_set_unordered_cq` — registered direct child under this Level-3 root.
- `with_execution_set` — registered direct child under this Level-3 root.
- `with_execution_set_cq` — registered direct child under this Level-3 root.
- `with_execution_set_preprocess` — registered direct child under this Level-3 root.
- `with_execution_set_preprocess_cq` — registered direct child under this Level-3 root.
- `with_execution_set_preprocess_unordered` — registered direct child under this Level-3 root.
- `with_execution_set_preprocess_unordered_cq` — registered direct child under this Level-3 root.
- `with_execution_set_unordered` — registered direct child under this Level-3 root.
- `with_execution_set_unordered_cq` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCRayTracingTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1998) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_KHR_acceleration_structure");](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L384)
- [context.requireDeviceFunctionality("VK_KHR_ray_tracing_pipeline");](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L385)
- [context.requireDeviceFunctionality("VK_KHR_ray_tracing_maintenance1");](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L386)

## Verification Methods

Verification compares ray payload, shader-record-buffer, transform, launch, and hit attributes. Evidence is in the implementation around [vktDGCRayTracingTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCRayTracingTestsExt.cpp#L1988).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
