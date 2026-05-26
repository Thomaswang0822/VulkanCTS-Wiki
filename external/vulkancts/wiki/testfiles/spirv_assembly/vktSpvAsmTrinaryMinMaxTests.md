# vktSpvAsmTrinaryMinMaxTests

## Overview

Tests for the `VK_AMD_shader_trinary_minmax` extension, covering the registered `min3`, `max3`, and `mid3` operation groups and their generated signed, unsigned, and floating-point type cases ([group registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L979-L988), [type loops](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L990-L1040)).

## Role

Implementation file

## Source

- [vktSpvAsmTrinaryMinMaxTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L979)

## Registration Hierarchy

```text
spirv_assembly.instruction.amd_trinary_minmax
├── min3
├── mid3
└── max3
```

## Test Families

### min3 — Tests FMin3AMD/SMin3AMD/UMin3AMD operations

Tests the trinary minimum operation across the registered base types (`i`, `u`, `f`), bit sizes (`8`, `16`, `32`, `64`), and aggregation types (`scalar`, `vec2`, `vec3`, `vec4`) ([dimension lists](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L984-L1008)). For each type/size combination, a type subgroup contains one test case for each aggregation type, and 8-bit float combinations are skipped because the source explicitly excludes them ([generation loop](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L1010-L1040)).

### max3 — Tests FMax3AMD/SMax3AMD/UMax3AMD operations

Uses the same generated type and aggregation structure as `min3`, with `OperationType::MAX` registered as the `max3` operation group ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L984-L988)).

### mid3 — Tests FMid3AMD/SMid3AMD/UMid3AMD operations

Uses the same generated type and aggregation structure as `min3`, with `OperationType::MID` registered as the `mid3` operation group ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L984-L988)).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Operation | `MIN`, `MAX`, `MID` | Registered as `min3`, `max3`, and `mid3` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L60-L65), [registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L984-L988)) |
| Base type | `TYPE_INT`, `TYPE_UINT`, `TYPE_FLOAT` | Generates `i`, `u`, and `f` type-prefix groups ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L67-L72), [registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L990-L994)) |
| Type size | `SIZE_8BIT`, `SIZE_16BIT`, `SIZE_32BIT`, `SIZE_64BIT` | Generates `8`, `16`, `32`, and `64` suffixes; float-8 is skipped ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L74-L81), [skip](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L1014-L1023)) |
| Aggregation | `SCALAR`, `VEC2`, `VEC3`, `VEC4` | Registered as `scalar`, `vec2`, `vec3`, and `vec4` cases ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L83-L90), [registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L1003-L1035)) |
| Random seed | Incrementing `seed` | Each generated `TestParams` receives the current seed and then increments it ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L981-L982), [assignment](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L1027-L1033)) |

## Support Requirements

- `VK_KHR_get_physical_device_properties2`, `VK_KHR_storage_buffer_storage_class`, and `VK_AMD_shader_trinary_minmax` are always required by `TrinaryMinMaxCase::checkSupport()` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L584-L590)).
- 8-bit cases require `VK_KHR_8bit_storage`, `storageBuffer8BitAccess`, and `shaderInt8` for integer base types ([storage](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L596-L603), [shader integer gate](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L612-L620)).
- 16-bit cases require `VK_KHR_16bit_storage` and `storageBuffer16BitAccess`; integer cases require `shaderInt16`, and float cases require `shaderFloat16` ([storage](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L604-L610), [shader gates](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L612-L628)).
- 64-bit integer and floating-point cases require `shaderInt64` and `shaderFloat64`, respectively ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L612-L628)).

## Verification Methods

The `TrinaryMinMaxInstance::iterate()` path dispatches a compute shader, invalidates the output allocation, compares GPU output against CPU reference data through `opMan.compareResults`, and reports operation/component mismatch details on failure ([dispatch](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L944-L963), [comparison](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L964-L974)). CPU reference operations are implemented by helper functions that apply `min3`, `max3`, or `mid3` to three inputs ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L226-L249)).

## Notes

- The source emits SPIR-V capabilities for integer and floating-point widths according to the generated parameters ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L632-L650)).
- The generated hierarchy is `{min3,max3,mid3}` → `{i8,u8,f16,i16,u16,f32,u32,f64,i64,u64}` with no `f8` group → `{scalar,vec2,vec3,vec4}` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L1010-L1040)).
