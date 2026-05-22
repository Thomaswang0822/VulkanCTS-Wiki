# vktDGCComputeLayoutTestsExt

## Overview

EXT compute layout tests exercise dispatch layouts with push constants, execution sets, shader objects, dynamic pipeline layouts, descriptor heaps, and compute/universal queues.

## Role of File

This is an implementation file for `dgc.ext.compute.layout`. The source is [vktDGCComputeLayoutTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L1). Its registration evidence starts at [vktDGCComputeLayoutTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L1161).

## Registration Hierarchy

```text
dgc.ext.compute.layout
├── complementary_push_dispatch
├── complementary_push_dispatch_cq
├── complementary_push_dispatch_cq_descriptor_heap
├── complementary_push_dispatch_cq_dynamic_pipeline_layout
├── complementary_push_dispatch_cq_dynamic_pipeline_layout_descriptor_heap
├── complementary_push_dispatch_descriptor_heap
├── complementary_push_dispatch_dynamic_pipeline_layout
├── complementary_push_dispatch_dynamic_pipeline_layout_descriptor_heap
├── complementary_push_dispatch_shader_objects
├── complementary_push_dispatch_shader_objects_cq
├── complementary_push_dispatch_shader_objects_cq_descriptor_heap
├── complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout
├── complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap
├── complementary_push_dispatch_shader_objects_descriptor_heap
├── complementary_push_dispatch_shader_objects_dynamic_pipeline_layout
├── complementary_push_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap
├── complementary_push_index_dispatch
├── complementary_push_index_dispatch_cq
├── complementary_push_index_dispatch_cq_descriptor_heap
├── complementary_push_index_dispatch_cq_dynamic_pipeline_layout
├── complementary_push_index_dispatch_cq_dynamic_pipeline_layout_descriptor_heap
├── complementary_push_index_dispatch_descriptor_heap
├── complementary_push_index_dispatch_dynamic_pipeline_layout
├── complementary_push_index_dispatch_dynamic_pipeline_layout_descriptor_heap
├── complementary_push_index_dispatch_shader_objects
├── complementary_push_index_dispatch_shader_objects_cq
├── complementary_push_index_dispatch_shader_objects_cq_descriptor_heap
├── complementary_push_index_dispatch_shader_objects_cq_dynamic_pipeline_layout
├── complementary_push_index_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap
├── complementary_push_index_dispatch_shader_objects_descriptor_heap
├── complementary_push_index_dispatch_shader_objects_dynamic_pipeline_layout
├── complementary_push_index_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap
├── execution_set_complementary_push_dispatch
├── execution_set_complementary_push_dispatch_cq
├── execution_set_complementary_push_dispatch_cq_descriptor_heap
├── execution_set_complementary_push_dispatch_cq_dynamic_pipeline_layout
├── execution_set_complementary_push_dispatch_cq_dynamic_pipeline_layout_descriptor_heap
├── execution_set_complementary_push_dispatch_descriptor_heap
├── execution_set_complementary_push_dispatch_dynamic_pipeline_layout
├── execution_set_complementary_push_dispatch_dynamic_pipeline_layout_descriptor_heap
├── execution_set_complementary_push_dispatch_shader_objects
├── execution_set_complementary_push_dispatch_shader_objects_cq
├── execution_set_complementary_push_dispatch_shader_objects_cq_descriptor_heap
├── execution_set_complementary_push_dispatch_shader_objects_cq_destroy_ies_set_layout
├── execution_set_complementary_push_dispatch_shader_objects_cq_destroy_ies_set_layout_descriptor_heap
├── execution_set_complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout
├── execution_set_complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap
├── execution_set_complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout
├── execution_set_complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap
├── execution_set_complementary_push_dispatch_shader_objects_descriptor_heap
├── execution_set_complementary_push_dispatch_shader_objects_destroy_ies_set_layout
├── execution_set_complementary_push_dispatch_shader_objects_destroy_ies_set_layout_descriptor_heap
├── execution_set_complementary_push_dispatch_shader_objects_dynamic_pipeline_layout
├── execution_set_complementary_push_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap
├── execution_set_complementary_push_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout
├── execution_set_complementary_push_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap
├── execution_set_dispatch
├── execution_set_dispatch_cq
├── execution_set_dispatch_cq_descriptor_heap
├── execution_set_dispatch_cq_dynamic_pipeline_layout
├── execution_set_dispatch_cq_dynamic_pipeline_layout_descriptor_heap
├── execution_set_dispatch_descriptor_heap
├── execution_set_dispatch_dynamic_pipeline_layout
├── execution_set_dispatch_dynamic_pipeline_layout_descriptor_heap
├── execution_set_dispatch_shader_objects
├── execution_set_dispatch_shader_objects_cq
├── execution_set_dispatch_shader_objects_cq_descriptor_heap
├── execution_set_dispatch_shader_objects_cq_destroy_ies_set_layout
├── execution_set_dispatch_shader_objects_cq_destroy_ies_set_layout_descriptor_heap
├── execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout
├── execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap
├── execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout
├── execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap
├── execution_set_dispatch_shader_objects_descriptor_heap
├── execution_set_dispatch_shader_objects_destroy_ies_set_layout
├── execution_set_dispatch_shader_objects_destroy_ies_set_layout_descriptor_heap
├── execution_set_dispatch_shader_objects_dynamic_pipeline_layout
├── execution_set_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap
├── execution_set_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout
├── execution_set_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap
├── execution_set_index_push_dispatch
├── execution_set_index_push_dispatch_cq
├── execution_set_index_push_dispatch_cq_descriptor_heap
├── execution_set_index_push_dispatch_cq_dynamic_pipeline_layout
├── execution_set_index_push_dispatch_cq_dynamic_pipeline_layout_descriptor_heap
├── execution_set_index_push_dispatch_descriptor_heap
├── execution_set_index_push_dispatch_dynamic_pipeline_layout
├── execution_set_index_push_dispatch_dynamic_pipeline_layout_descriptor_heap
├── execution_set_index_push_dispatch_shader_objects
├── execution_set_index_push_dispatch_shader_objects_cq
├── execution_set_index_push_dispatch_shader_objects_cq_descriptor_heap
├── execution_set_index_push_dispatch_shader_objects_cq_destroy_ies_set_layout
├── execution_set_index_push_dispatch_shader_objects_cq_destroy_ies_set_layout_descriptor_heap
├── execution_set_index_push_dispatch_shader_objects_cq_dynamic_pipeline_layout
├── execution_set_index_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap
├── execution_set_index_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout
├── execution_set_index_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap
├── execution_set_index_push_dispatch_shader_objects_descriptor_heap
├── execution_set_index_push_dispatch_shader_objects_destroy_ies_set_layout
├── execution_set_index_push_dispatch_shader_objects_destroy_ies_set_layout_descriptor_heap
├── execution_set_index_push_dispatch_shader_objects_dynamic_pipeline_layout
├── execution_set_index_push_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap
├── execution_set_index_push_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout
├── execution_set_index_push_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap
├── execution_set_push_dispatch
├── execution_set_push_dispatch_cq
├── execution_set_push_dispatch_cq_descriptor_heap
├── execution_set_push_dispatch_cq_dynamic_pipeline_layout
├── execution_set_push_dispatch_cq_dynamic_pipeline_layout_descriptor_heap
├── execution_set_push_dispatch_descriptor_heap
├── execution_set_push_dispatch_dynamic_pipeline_layout
├── execution_set_push_dispatch_dynamic_pipeline_layout_descriptor_heap
├── execution_set_push_dispatch_shader_objects
├── execution_set_push_dispatch_shader_objects_cq
├── execution_set_push_dispatch_shader_objects_cq_descriptor_heap
├── execution_set_push_dispatch_shader_objects_cq_destroy_ies_set_layout
├── execution_set_push_dispatch_shader_objects_cq_destroy_ies_set_layout_descriptor_heap
├── execution_set_push_dispatch_shader_objects_cq_dynamic_pipeline_layout
├── execution_set_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap
├── execution_set_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout
├── execution_set_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap
├── execution_set_push_dispatch_shader_objects_descriptor_heap
├── execution_set_push_dispatch_shader_objects_destroy_ies_set_layout
├── execution_set_push_dispatch_shader_objects_destroy_ies_set_layout_descriptor_heap
├── execution_set_push_dispatch_shader_objects_dynamic_pipeline_layout
├── execution_set_push_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap
├── execution_set_push_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout
├── execution_set_push_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap
├── multi_push_dispatch
├── multi_push_dispatch_cq
├── multi_push_dispatch_cq_descriptor_heap
├── multi_push_dispatch_cq_dynamic_pipeline_layout
├── multi_push_dispatch_cq_dynamic_pipeline_layout_descriptor_heap
├── multi_push_dispatch_descriptor_heap
├── multi_push_dispatch_dynamic_pipeline_layout
├── multi_push_dispatch_dynamic_pipeline_layout_descriptor_heap
├── multi_push_dispatch_shader_objects
├── multi_push_dispatch_shader_objects_cq
├── multi_push_dispatch_shader_objects_cq_descriptor_heap
├── multi_push_dispatch_shader_objects_cq_dynamic_pipeline_layout
├── multi_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap
├── multi_push_dispatch_shader_objects_descriptor_heap
├── multi_push_dispatch_shader_objects_dynamic_pipeline_layout
├── multi_push_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap
├── offset_execution_set_dispatch
├── offset_execution_set_dispatch_cq
├── offset_execution_set_dispatch_cq_descriptor_heap
├── offset_execution_set_dispatch_cq_dynamic_pipeline_layout
├── offset_execution_set_dispatch_cq_dynamic_pipeline_layout_descriptor_heap
├── offset_execution_set_dispatch_descriptor_heap
├── offset_execution_set_dispatch_dynamic_pipeline_layout
├── offset_execution_set_dispatch_dynamic_pipeline_layout_descriptor_heap
├── offset_execution_set_dispatch_shader_objects
├── offset_execution_set_dispatch_shader_objects_cq
├── offset_execution_set_dispatch_shader_objects_cq_descriptor_heap
├── offset_execution_set_dispatch_shader_objects_cq_destroy_ies_set_layout
├── offset_execution_set_dispatch_shader_objects_cq_destroy_ies_set_layout_descriptor_heap
├── offset_execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout
├── offset_execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap
├── offset_execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout
├── offset_execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap
├── offset_execution_set_dispatch_shader_objects_descriptor_heap
├── offset_execution_set_dispatch_shader_objects_destroy_ies_set_layout
├── offset_execution_set_dispatch_shader_objects_destroy_ies_set_layout_descriptor_heap
├── offset_execution_set_dispatch_shader_objects_dynamic_pipeline_layout
├── offset_execution_set_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap
├── offset_execution_set_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout
├── offset_execution_set_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap
├── push_dispatch
├── push_dispatch_cq
├── push_dispatch_cq_descriptor_heap
├── push_dispatch_cq_dynamic_pipeline_layout
├── push_dispatch_cq_dynamic_pipeline_layout_descriptor_heap
├── push_dispatch_descriptor_heap
├── push_dispatch_dynamic_pipeline_layout
├── push_dispatch_dynamic_pipeline_layout_descriptor_heap
├── push_dispatch_shader_objects
├── push_dispatch_shader_objects_cq
├── push_dispatch_shader_objects_cq_descriptor_heap
├── push_dispatch_shader_objects_cq_dynamic_pipeline_layout
├── push_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap
├── push_dispatch_shader_objects_descriptor_heap
├── push_dispatch_shader_objects_dynamic_pipeline_layout
└── push_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputeLayoutTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L1161).

- `complementary_push_dispatch` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_cq` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_cq_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_cq_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_cq_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_shader_objects` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_shader_objects_cq` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_shader_objects_cq_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_shader_objects_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_shader_objects_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_cq` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_cq_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_cq_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_cq_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_shader_objects` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_shader_objects_cq` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_shader_objects_cq_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_shader_objects_cq_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_shader_objects_descriptor_heap` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_shader_objects_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `complementary_push_index_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_cq` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_cq_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_cq_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_cq_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_cq` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_cq_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_cq_destroy_ies_set_layout` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_cq_destroy_ies_set_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_destroy_ies_set_layout` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_destroy_ies_set_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout` — registered direct child under this Level-3 root.
- `execution_set_complementary_push_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch` — registered direct child under this Level-3 root.
- `execution_set_dispatch_cq` — registered direct child under this Level-3 root.
- `execution_set_dispatch_cq_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_cq_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `execution_set_dispatch_cq_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `execution_set_dispatch_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_cq` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_cq_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_cq_destroy_ies_set_layout` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_cq_destroy_ies_set_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_cq_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_destroy_ies_set_layout` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_destroy_ies_set_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_dynamic_pipeline_layout` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_dynamic_pipeline_layout_descriptor_heap` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout` — registered direct child under this Level-3 root.
- `execution_set_dispatch_shader_objects_dynamic_pipeline_layout_destroy_ies_set_layout_descriptor_heap` — registered direct child under this Level-3 root.
- Additional direct children: 104 more names are listed in the hierarchy tree above.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputeLayoutTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L1179) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_EXT_shader_object");](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L228)
- [context.requireDeviceFunctionality(VK_EXT_DESCRIPTOR_HEAP_EXTENSION_NAME);](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L249)

## Verification Methods

Verification checks shader-written output values for each generated dispatch sequence. Evidence is in the implementation around [vktDGCComputeLayoutTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTestsExt.cpp#L1152).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
