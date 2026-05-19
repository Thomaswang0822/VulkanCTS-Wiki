# vktTessellationUserDefinedIO.cpp

## Overview

[`vktTessellationUserDefinedIO.cpp`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1) registers [`user_defined_io`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1031-L1087), covering user-defined per-patch and per-vertex IO forms.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationUserDefinedIO.cpp`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.user_defined_io`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1).

```text
tessellation.user_defined_io
├── per_patch
├── per_patch_array
├── per_patch_block
├── per_patch_block_array
├── per_vertex
└── per_vertex_block
```

## Test Families

### per_patch — User Defined Io

Direct child groups correspond to [`IOType`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L70-L80) entries; each expands across vertex array-size cases and primitive types in [`createUserDefinedIOTests()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1035-L1083).

## Parameter Dimensions

Parameters include IO type, vertex IO array size, primitive type, generated struct/basic type traversal, and reference image path.

## Support / Feature Requirements

[`UserDefinedIOTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L792-L796) requires tessellation shaders and vertex-pipeline stores/atomics.

## Verification Methods

Generated shader comparisons set status and SSBO failure indices around [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L734-L750); rendered output is compared with [`tcu::fuzzyCompare()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L965-L966).

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
