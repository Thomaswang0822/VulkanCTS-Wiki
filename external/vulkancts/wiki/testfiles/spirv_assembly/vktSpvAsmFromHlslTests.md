# vktSpvAsmFromHlslTests

## Overview

Tests SPIR-V Assembly indexing behavior for an HLSL cbuffer-packing corner case that the source comments identify as not expressible in GLSL; the HLSL source places `bar` at `packoffset(c1.y)` and enables scalar offsets during shader build ([Programs::init()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L59-L79)).

## Role

Implementation file

## Source

- [vktSpvAsmFromHlslTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L228)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.hlsl_cases
└── cbuffer_packing
```

## Test Families

### cbuffer_packing — Tests HLSL cbuffer packing with scalar block layout

Tests an HLSL packing corner case where an array `foo[2]` has an ArrayStride of 16, and a second member `bar` is placed at `packoffset(c1.y)` — effectively at byte offset 20, which falls within the stride of the `foo` array. This is valid HLSL with the `VK_EXT_scalar_block_layout` extension. The shader reads `bar` and writes it to an output buffer. The test manually creates input/output buffers, descriptor sets, and pipeline, then verifies the output value matches the expected test value. Source: [Programs::init()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L59-L79) and [HlslTest::iterate()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L98-L219).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Test type | `TT_CBUFFER_PACKING` | Only test type enum value and registered case in this file ([TestType](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L46-L48), [createHlslComputeGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L228-L235)) |

## Support Requirements

- `VK_EXT_scalar_block_layout` extension, checked in [`checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L221-L224)
- `FLAG_ALLOW_SCALAR_OFFSETS` shader build option used when adding the HLSL source ([Programs::init()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L77-L79))

## Verification Methods

The [`HlslTest::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L98-L219) method manually:
1. Creates a 32-byte input buffer with `testValue` (5) at offset 20 (index 5) ([HlslTest::iterate()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L105-L122))
2. Creates a 4-byte output buffer ([HlslTest::iterate()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L125-L132))
3. Dispatches the compute shader after binding the compute pipeline and descriptors ([HlslTest::iterate()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L195-L205))
4. Reads back the output and compares against `testValue` ([HlslTest::iterate()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L213-L218))

## Notes

- This page documents an HLSL-source path: `Programs::init()` adds an HLSL compute source with scalar-offset build options ([Programs::init()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L59-L79))
- The `Programs::init()` method uses `dst.hlslSources.add()` with `FLAG_ALLOW_SCALAR_OFFSETS` to enable scalar offset packing ([Programs::init()](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L77-L79))
