# vktSpvAsmFromHlslTests

## Overview

Tests SPIR-V Assembly indexing with access chain operations originating from HLSL shaders, specifically testing cbuffer packing corner cases that GLSL shaders cannot exhibit.

## Role

Implementation file

## Source

- [vktSpvAsmFromHlslTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.hlsl_cases
└── cbuffer_packing
```

## Test Families

### cbuffer_packing — Tests HLSL cbuffer packing with scalar block layout

Tests an HLSL packing corner case where an array `foo[2]` has an ArrayStride of 16, and a second member `bar` is placed at `packoffset(c1.y)` — effectively at byte offset 20, which falls within the stride of the `foo` array. This is valid HLSL with the `VK_EXT_scalar_block_layout` extension. The shader reads `bar` and writes it to an output buffer. The test manually creates input/output buffers, descriptor sets, and pipeline, then verifies the output value matches the expected test value. Source: `vktSpvAsmFromHlslTests.cpp#L59-L219`.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Test type | `TT_CBUFFER_PACKING` | Only one test type defined in this file |

## Support Requirements

- `VK_EXT_scalar_block_layout` extension (checked in `checkSupport` at `vktSpvAsmFromHlslTests.cpp#L221-L224`)
- `FLAG_ALLOW_SCALAR_OFFSETS` shader build option

## Verification Methods

The `HlslTest::iterate()` method (`vktSpvAsmFromHlslTests.cpp#L98-L219`) manually:
1. Creates a 32-byte input buffer with `testValue` (5) at offset 20 (index 5)
2. Creates a 4-byte output buffer
3. Dispatches the compute shader
4. Reads back the output and compares against `testValue`

## Notes

- This is the only test file in the SPIR-V assembly suite that uses HLSL source rather than hand-written SPIR-V assembly
- The `Programs::init` method uses `dst.hlslSources.add()` with `FLAG_ALLOW_SCALAR_OFFSETS` to enable the scalar offset packing
