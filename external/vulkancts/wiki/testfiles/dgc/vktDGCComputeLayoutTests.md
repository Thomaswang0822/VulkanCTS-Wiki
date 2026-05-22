# vktDGCComputeLayoutTests

## Overview

NV compute layout tests exercise token layouts that combine pipeline, push-constant, index, and dispatch tokens.

## Role of File

This is an implementation file for `dgc.nv.compute.layout`. The source is [vktDGCComputeLayoutTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L1). Its registration evidence starts at [vktDGCComputeLayoutTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L756).

## Registration Hierarchy

```text
dgc.nv.compute.layout
├── complementary_push_dispatch
├── complementary_push_dispatch_cq
├── partial_push_dispatch
├── partial_push_dispatch_cq
├── pipeline_complementary_push_dispatch
├── pipeline_complementary_push_dispatch_cq
├── pipeline_dispatch
├── pipeline_dispatch_align4
├── pipeline_dispatch_align4_cq
├── pipeline_dispatch_cq
├── pipeline_push_dispatch
├── pipeline_push_dispatch_align4
├── pipeline_push_dispatch_align4_cq
├── pipeline_push_dispatch_capture_replay
├── pipeline_push_dispatch_capture_replay_cq
├── pipeline_push_dispatch_cq
├── push_dispatch
└── push_dispatch_cq
```

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCComputeLayoutTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L756).

- `complementary_push_dispatch` — registered direct child under this Level-3 root.
- `complementary_push_dispatch_cq` — registered direct child under this Level-3 root.
- `partial_push_dispatch` — registered direct child under this Level-3 root.
- `partial_push_dispatch_cq` — registered direct child under this Level-3 root.
- `pipeline_complementary_push_dispatch` — registered direct child under this Level-3 root.
- `pipeline_complementary_push_dispatch_cq` — registered direct child under this Level-3 root.
- `pipeline_dispatch` — registered direct child under this Level-3 root.
- `pipeline_dispatch_align4` — registered direct child under this Level-3 root.
- `pipeline_dispatch_align4_cq` — registered direct child under this Level-3 root.
- `pipeline_dispatch_cq` — registered direct child under this Level-3 root.
- `pipeline_push_dispatch` — registered direct child under this Level-3 root.
- `pipeline_push_dispatch_align4` — registered direct child under this Level-3 root.
- `pipeline_push_dispatch_align4_cq` — registered direct child under this Level-3 root.
- `pipeline_push_dispatch_capture_replay` — registered direct child under this Level-3 root.
- `pipeline_push_dispatch_capture_replay_cq` — registered direct child under this Level-3 root.
- `pipeline_push_dispatch_cq` — registered direct child under this Level-3 root.
- `push_dispatch` — registered direct child under this Level-3 root.
- `push_dispatch_cq` — registered direct child under this Level-3 root.

## Parameter Dimensions

The registration loop or case construction near [vktDGCComputeLayoutTests case generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L776) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- Case-level support checks call DGC helper functions in the implementation associated with [vktDGCComputeLayoutTests registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L756).

## Verification Methods

Verification checks every output value produced by generated dispatches against expected sequence/workgroup data. Evidence is in the implementation around [vktDGCComputeLayoutTests verification](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L745).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
