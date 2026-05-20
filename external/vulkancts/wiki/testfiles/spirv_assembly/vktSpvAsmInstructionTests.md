# vktSpvAsmInstructionTests

## Overview

Central aggregator and implementation file for the `spirv_assembly.instruction` test hierarchy. Creates the `instruction` group with `compute` and `graphics` pipeline variants, plus several direct subgroups. Contains inline definitions for the majority of SPIR-V instruction-level test groups, while delegating larger feature areas to separate implementation files.

## Role

Registration file and implementation file. Aggregates all instruction-test subgroups and defines many inline test groups directly.

## Source

- [vktSpvAsmInstructionTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction
├── compute
├── graphics
├── amd_trinary_minmax
├── function_params (non-VulkanSC only)
├── image_query (non-VulkanSC only)
├── maint9_vectorization
├── spirv1p4 (non-VulkanSC only)
└── terminate_invocation (non-VulkanSC only)
```

## Test Families

### compute — Compute-pipeline instruction tests

Container for all instruction tests that use the compute pipeline. Contains both inline groups defined in this file and groups delegated to separate implementation files.

**Inline groups under compute** (defined in this file):

| Group | Description | Key Requirements |
|-------|-------------|------------------|
| `spirv_version` | SPIR-V version support checks per compute operation | — |
| `localsize` | LocalSize execution mode with workgroup size variants | — |
| `localsize_id` | LocalSizeId execution mode (SPIR-V 1.5) | `VK_KHR_maintenance4` |
| `opnop` | OpNop instruction in compute function body | — |
| `opfunord` | OpFUnord* comparisons (equal, less, lessequal, greater, greaterequal, notequal) | — |
| `opfunord_nan` | OpFUnord* comparisons with NaN operands | `VK_KHR_shader_float_controls`, `shaderSignedZeroInfNanPreserveFloat32` |
| `opatomic` | Atomic operations (IAdd, ISub, IIncrement, IDecrement, Load, Store, CompareExchange) | — |
| `opatomic_storage_buffer` | Atomic ops using StorageBuffer decoration | `VK_KHR_storage_buffer_storage_class` |
| `opatomic_return_values` | Atomic operation return value validation | — |
| `opatomic_storage_buffer_volatile` | Volatile atomic ops with StorageBuffer | `VK_KHR_vulkan_memory_model`, SPIR-V 1.3 |
| `opline` | OpLine debug instruction in compute shaders | — |
| `opmoduleprocessed` | OpModuleProcessed debug instruction | SPIR-V 1.3 |
| `opnoline` | OpNoLine debug instruction in compute shaders | — |
| `opconstantnull` | OpConstantNull with scalar/vector/matrix/array/struct/pointer types | — |
| `opconstantcomposite` | OpConstantComposite with vector/matrix/struct/array types | — |
| `opconstantnullcomposite` | OpConstantNull with composite types used in arithmetic | — |
| `opspecconstantop` | OpSpecConstantOp with various operations (arithmetic, shift, bitwise, comparison, logical, composite) | Varies per case |
| `opsource` | OpSource/OpSourceContinued with various languages, filenames, source strings | — |
| `opsourceextension` | OpSourceExtension with various extension strings | — |
| `decoration_group` | OpDecorationGroup, OpGroupDecorate, OpGroupMemberDecorate | — |
| `opphi` | OpPhi with switch, induction, swap, wide, nested patterns | — |
| `loop_control` | OpLoopMerge control hints (Unroll, DontUnroll, dependency_length, dependency_infinite) | — |
| `function_control` | OpFunction control hints (Inline, DontInline, Pure, Const) | — |
| `selection_control` | OpSelectionMerge control hints (Flatten, DontFlatten) | — |
| `block_order` | Basic block ordering in compute shaders | — |
| `multiple_shaders` | Multiple entry points in a single SPIR-V module | — |
| `memory_access` | Memory access qualifiers (Volatile, Aligned, Nontemporal) on Load/Store/CopyMemory | — |
| `opcopymemory` | OpCopyMemory with vec4, array, struct, float types | — |
| `opcopyobject` | OpCopyObject with float, vec3, mat3x3, array, struct | — |
| `nocontraction` | NoContraction decoration preventing fused multiply-add | — |
| `opundef` | OpUndef with bool, scalars, vectors, matrices, images, samplers, pointers, arrays, structs | Varies per type |
| `opunreachable` | OpUnreachable in unreachable code paths | — |
| `opquantize` | OpQuantizeToF16 scalar form (infinities, NaNs, flush-to-zero, exact, rounded) | — |
| `opquantize_vec4` | OpQuantizeToF16 vec4 form | — |
| `opfrem` | OpFRem (floating-point remainder, sign follows dividend) | — |
| `opsrem` | OpSRem with 32-bit integers (positive and all-operand cases) | — |
| `opsrem64` | OpSRem with 64-bit integers | `shaderInt64` |
| `opsmod` | OpSMod with 32-bit integers (sign follows divisor) | — |
| `opsmod64` | OpSMod with 64-bit integers | `shaderInt64` |
| `sconvert` | OpSConvert type conversion tests | Varies per case |
| `uconvert` | OpUConvert type conversion tests | Varies per case |
| `fconvert` | OpFConvert type conversion tests | Varies per case |
| `convertstof` | OpConvertSToF type conversion tests | Varies per case |
| `convertftos` | OpConvertFToS type conversion tests | Varies per case |
| `convertutof` | OpConvertUToF type conversion tests | Varies per case |
| `convertftou` | OpConvertFToU type conversion tests | Varies per case |
| `opcompositeinsert` | OpCompositeInsert with vectors, matrices, structs by number type | — |
| `opinboundsaccesschain` | OpInBoundsAccessChain with struct member access | — |
| `shader_default_output` | Default output values (initialized/uninitialized) by number type | — |
| `opnmin` | GLSL.std.450 NMin with NaN handling | — |
| `opnmax` | GLSL.std.450 NMax with NaN handling | — |
| `opnclamp` | GLSL.std.450 NClamp with NaN handling | — |
| `float16` | Float16 operations (constants, logical, func, vector, composite, arithmetic) | Float16, 16-bit storage |
| `float32` | Float32 comparison operations | non-VulkanSC |
| `bool` | Boolean type with mixed bit sizes | — |
| `spirv_ids_abuse` | Sparse and large SPIR-V ID allocation | — |
| `unused_variables` | Unused variables and functions in compute shaders | — |
| `opname` | OpName debug instruction (entry points, abuse cases) | — |
| `opmembername` | OpMemberName debug instruction (abuse cases) | — |
| `mul_extended` | OpSMulExtended and OpUMulExtended with 8/16/32/64-bit widths | Varies per case; non-VulkanSC |
| `android` | OpSRem/OpSMod with quality-warning severity for negative operands | — |
| `maintenance8` | OpSRem/OpSMod with VK_KHR_maintenance8 (negative operands are errors) | `VK_KHR_maintenance8`; non-VulkanSC |

**Groups delegated to separate files** (under compute):

| Group | Source File |
|-------|-------------|
| `8bit_storage` | [vktSpvAsm8bitStorageTests.md](vktSpvAsm8bitStorageTests.md) |
| `16bit_storage` | [vktSpvAsm16bitStorageTests.md](vktSpvAsm16bitStorageTests.md) |
| `64bit_compare` | [vktSpvAsm64bitCompareTests.md](vktSpvAsm64bitCompareTests.md) |
| `float_controls` | [vktSpvAsmFloatControlsTests.md](vktSpvAsmFloatControlsTests.md) |
| `float_controls2` | [vktSpvAsmFloatControls2Tests.md](vktSpvAsmFloatControls2Tests.md) |
| `float_controls_extensionless` | [vktSpvAsmFloatControlsExtensionlessTests.md](vktSpvAsmFloatControlsExtensionlessTests.md) |
| `ubo_padding` | [vktSpvAsmUboMatrixPaddingTests.md](vktSpvAsmUboMatrixPaddingTests.md) |
| `composite_insert` | [vktSpvAsmCompositeInsertTests.md](vktSpvAsmCompositeInsertTests.md) |
| `variable_init` | [vktSpvAsmVariableInitTests.md](vktSpvAsmVariableInitTests.md) |
| `conditional_branch` | [vktSpvAsmConditionalBranchTests.md](vktSpvAsmConditionalBranchTests.md) |
| `indexing` | [vktSpvAsmIndexingTests.md](vktSpvAsmIndexingTests.md) |
| `variable_pointers` | [vktSpvAsmVariablePointersTests.md](vktSpvAsmVariablePointersTests.md) |
| `physical_pointers` | [vktSpvAsmVariablePointersTests.md](vktSpvAsmVariablePointersTests.md) |
| `image_sampler` | [vktSpvAsmImageSamplerTests.md](vktSpvAsmImageSamplerTests.md) |
| `pointer_parameter` | [vktSpvAsmPointerParameterTests.md](vktSpvAsmPointerParameterTests.md) |
| `workgroup_memory` | [vktSpvAsmWorkgroupMemoryTests.md](vktSpvAsmWorkgroupMemoryTests.md) |
| `signed_int_compare` | [vktSpvAsmSignedIntCompareTests.md](vktSpvAsmSignedIntCompareTests.md) |
| `signed_op` | [vktSpvAsmSignedOpTests.md](vktSpvAsmSignedOpTests.md) |
| `ptr_access_chain` | [vktSpvAsmPtrAccessChainTests.md](vktSpvAsmPtrAccessChainTests.md) |
| `vector_shuffle` | [vktSpvAsmVectorShuffleTests.md](vktSpvAsmVectorShuffleTests.md) |
| `hlsl_cases` | [vktSpvAsmFromHlslTests.md](vktSpvAsmFromHlslTests.md) |
| `empty_struct` | [vktSpvAsmEmptyStructTests.md](vktSpvAsmEmptyStructTests.md) |
| `physical_storage_buffer` | [vktSpvAsmPhysicalStorageBufferPointerTests.md](vktSpvAsmPhysicalStorageBufferPointerTests.md) |
| `raw_access_chain` | [vktSpvAsmRawAccessChainTests.md](vktSpvAsmRawAccessChainTests.md) |
| `untyped_pointers` | [vktSpvAsmUntypedPointersTests.md](vktSpvAsmUntypedPointersTests.md) |
| `compute_shader_derivatives` | [vktSpvAsmComputeShaderDerivativesTests.md](vktSpvAsmComputeShaderDerivativesTests.md) |
| `non_semantic_info` | [vktSpvAsmNonSemanticInfoTests.md](vktSpvAsmNonSemanticInfoTests.md) |
| `relaxed_with_forward_reference` | [vktSpvAsmRelaxedWithForwardReferenceTests.md](vktSpvAsmRelaxedWithForwardReferenceTests.md) |
| `multiple_shaders_extended` | [vktSpvAsmMultipleShadersTests.md](vktSpvAsmMultipleShadersTests.md) |
| `oparraylength` | (inline Amber test, non-VulkanSC) |
| `opfma` | [vktSpvAsmFmaTests.md](vktSpvAsmFmaTests.md) |
| `opsdotkhr` through `opsudotaccsatkhr` | [vktSpvAsmIntegerDotProductTests.md](vktSpvAsmIntegerDotProductTests.md) |
| `ldexp` | [vktSpvAsmLdexpTests.md](vktSpvAsmLdexpTests.md) |

### graphics — Graphics-pipeline instruction tests

Container for all instruction tests that use the graphics pipeline (vertex + fragment, sometimes geometry/tessellation). Contains both inline groups and groups delegated to separate files.

**Inline groups under graphics** (defined in this file):

| Group | Description | Key Requirements |
|-------|-------------|------------------|
| `spirv_version` | SPIR-V version support checks in graphics pipeline | — |
| `opnop` | OpNop in graphics shaders across all stages | — |
| `opsource` | OpSource with various source languages in graphics shaders | — |
| `opsourcecontinued` | OpSourceContinued in graphics shaders | — |
| `opmoduleprocessed` | OpModuleProcessed in graphics shaders | SPIR-V 1.3 |
| `opline` | OpLine in graphics shaders with various filenames | — |
| `opnoline` | OpNoLine in graphics shaders | — |
| `opconstantnull` | OpConstantNull with various types in graphics shaders | — |
| `opconstantcomposite` | OpConstantComposite in graphics shaders | — |
| `opmemoryaccess` | Memory access qualifiers in graphics shaders | — |
| `opundef` | OpUndef with various types in graphics shaders | Varies per type |
| `selection_block_order` | Selection block ordering in graphics shaders | — |
| `module` | Combined SPIR-V modules across multiple shader stages | Geometry/tessellation for some |
| `unused_variables` | Unused variables/functions across graphics stages | Varies per stage |
| `switch_block_order` | OpSwitch block ordering in graphics shaders | — |
| `opphi` | OpPhi in graphics shaders with various control flow patterns | Variable pointers for some |
| `nocontraction` | NoContraction decoration in graphics shaders | — |
| `opquantize` | OpQuantizeToF16 in graphics shaders | — |
| `loop` | Loop constructs (single_block, multi_block, nested) in graphics shaders | — |
| `opspecconstantop` | OpSpecConstantOp in graphics shaders | Varies per case |
| `opspecconstantop_opquantize` | OpSpecConstantOp with QuantizeToF16 in graphics shaders | — |
| `barrier` | OpControlBarrier/OpMemoryBarrier in tessellation control shaders | Tessellation shader |
| `decoration_group` | OpDecorationGroup in graphics shaders | — |
| `frem` | OpFRem in graphics shaders | — |
| `srem` | OpSRem in graphics shaders | — |
| `smod` | OpSMod in graphics shaders | — |
| `opname` | OpName in graphics shaders | — |
| `opname_abuse` | OpName abuse cases (empty, long, UTF-8, special chars) | — |
| `opmembername_abuse` | OpMemberName abuse cases | — |
| `sconvert` through `convertftou` | Type conversion instructions in graphics shaders | Varies per case |
| `float16` | Float16 operations in graphics shaders | Float16, 16-bit storage |
| `float32` | Float32 comparison operations in graphics shaders | non-VulkanSC |
| `spirv_ids_abuse` | SPIR-V ID space abuse in graphics shaders | — |
| `early_fragment` | EarlyFragmentTests execution mode with depth comparisons | non-VulkanSC |
| `early_and_late_fragment` | VK_AMD_shader_early_and_late_fragment_tests | `VK_AMD_shader_early_and_late_fragment_tests`; non-VulkanSC |
| `execution_mode` | DepthLess/DepthGreater/DepthUnchanged execution modes | non-VulkanSC |
| `mixed_relaxed_precision_operands` | OpSelect with mixed RelaxedPrecision operands | non-VulkanSC |
| `android` | OpSRem/OpSMod with quality-warning severity | — |
| `maintenance8` | OpSRem/OpSMod with VK_KHR_maintenance8 | `VK_KHR_maintenance8`; non-VulkanSC |

**Groups delegated to separate files** (under graphics):

| Group | Source File |
|-------|-------------|
| `cross_stage` | [vktSpvAsmCrossStageInterfaceTests.md](vktSpvAsmCrossStageInterfaceTests.md) |
| `8bit_storage` | [vktSpvAsm8bitStorageTests.md](vktSpvAsm8bitStorageTests.md) |
| `16bit_storage` | [vktSpvAsm16bitStorageTests.md](vktSpvAsm16bitStorageTests.md) |
| `64bit_compare` | [vktSpvAsm64bitCompareTests.md](vktSpvAsm64bitCompareTests.md) |
| `float_controls` | [vktSpvAsmFloatControlsTests.md](vktSpvAsmFloatControlsTests.md) |
| `float_controls2` | [vktSpvAsmFloatControls2Tests.md](vktSpvAsmFloatControls2Tests.md) |
| `ubo_padding` | [vktSpvAsmUboMatrixPaddingTests.md](vktSpvAsmUboMatrixPaddingTests.md) |
| `composite_insert` | [vktSpvAsmCompositeInsertTests.md](vktSpvAsmCompositeInsertTests.md) |
| `variable_init` | [vktSpvAsmVariableInitTests.md](vktSpvAsmVariableInitTests.md) |
| `conditional_branch` | [vktSpvAsmConditionalBranchTests.md](vktSpvAsmConditionalBranchTests.md) |
| `indexing` | [vktSpvAsmIndexingTests.md](vktSpvAsmIndexingTests.md) |
| `variable_pointers` | [vktSpvAsmVariablePointersTests.md](vktSpvAsmVariablePointersTests.md) |
| `image_sampler` | [vktSpvAsmImageSamplerTests.md](vktSpvAsmImageSamplerTests.md) |
| `pointer_parameter` | [vktSpvAsmPointerParameterTests.md](vktSpvAsmPointerParameterTests.md) |
| `varying_name` | [vktSpvAsmVaryingNameTests.md](vktSpvAsmVaryingNameTests.md) |

### amd_trinary_minmax — AMD trinary min/max operations

Tests AMD_shader_trinary_minmax extension operations (FMin3, FMax3, FMid3, SMin3, SMax3, SMid3, UMin3, UMax3, UMid3) with various data types and vector widths. Delegated to [vktSpvAsmTrinaryMinMaxTests.md](vktSpvAsmTrinaryMinMaxTests.md).

### function_params — Function parameter tests

Tests function parameter passing with combined image samplers. Contains a single Amber test `sampler_param`. Non-VulkanSC only.

### image_query — Image query tests

Tests image query operations on storage images. Contains `samples_storage` Amber test requiring `shaderStorageImageMultisample`. Non-VulkanSC only.

### maint9_vectorization — Maintenance 9 vectorized bit operations

Tests VK_KHR_maintenance9 vectorization of bit operations (OpBitCount, OpBitReverse, OpBitFieldInsert, OpBitFieldSExtract, OpBitFieldUExtract). Delegated to [vktSpvAsmMaint9VectorizationTests.md](vktSpvAsmMaint9VectorizationTests.md).

### spirv1p4 — SPIR-V 1.4 features

Tests SPIR-V 1.4 new features including OpCopyLogical, selective image operands, and entry point changes. Non-VulkanSC only. Delegated to [vktSpvAsmSpirvVersion1p4Tests.md](vktSpvAsmSpirvVersion1p4Tests.md).

### terminate_invocation — OpTerminateInvocation tests

Tests VK_KHR_shader_terminate_invocation, verifying that OpTerminateInvocation prevents subsequent operations. Non-VulkanSC only. Delegated to [vktSpvAsmTerminateInvocationTests.md](vktSpvAsmTerminateInvocationTests.md).

## Parameter Dimensions

### Pipeline variant

The `compute` vs `graphics` split is the primary structural dimension. Many test groups exist under both variants with similar logic but different shader infrastructure:
- **Compute**: Uses `SpvAsmComputeShaderCase` infrastructure; tests run as compute dispatches
- **Graphics**: Uses `SpvAsmGraphicsShaderTestUtil` infrastructure; tests run as graphics pipelines with vertex/fragment (and optionally geometry/tessellation) stages

### SPIR-V version

Some groups test version-specific features:
- `spirv_version` iterates over SPIR-V 1.0 through latest
- `spirv1p4` targets SPIR-V 1.4 features
- `localsize_id` requires SPIR-V 1.5

### Data type dimensions

Many inline groups iterate over data types:
- Integer widths: 8-bit, 16-bit, 32-bit, 64-bit
- Float widths: 16-bit, 32-bit, 64-bit
- Vector widths: scalar, vec2, vec3, vec4
- Composite types: matrices, arrays, structs

## Support Requirements

Recurring requirements across inline groups:

| Requirement | Groups Affected |
|-------------|----------------|
| `shaderInt64` | opsrem64, opsmod64, opundef (int64 types), mul_extended (64-bit) |
| `shaderInt16` | Various conversion tests |
| `shaderInt8` | mul_extended (8-bit) |
| `Float16` / `shaderFloat16` | float16 groups |
| `VK_KHR_shader_float_controls` | opfunord_nan |
| `VK_KHR_vulkan_memory_model` | opatomic_storage_buffer_volatile |
| `VK_KHR_maintenance4` | localsize_id |
| `VK_KHR_maintenance8` | maintenance8 subgroups |
| `VK_KHR_maintenance9` | maint9_vectorization |
| `VK_KHR_shader_terminate_invocation` | terminate_invocation |
| `VK_AMD_shader_early_and_late_fragment_tests` | early_and_late_fragment |
| `VK_KHR_storage_buffer_storage_class` | opatomic_storage_buffer |
| `shaderStorageImageMultisample` | image_query |
| Tessellation shader | barrier |
| Geometry shader | module (some sub-tests) |

## Verification Methods

- **Compute shader verification**: Most compute tests use `SpvAsmComputeShaderCase` which writes results to a storage buffer and compares against expected values ([vktSpvAsmComputeShaderCase.cpp#L1](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderCase.cpp))
- **Graphics shader verification**: Graphics tests render a full-screen quad and compare the output color against expected RGBA values using `RGBA()` comparison
- **Binary verification**: Groups like `opmoduleprocessed` verify that the compiled SPIR-V binary contains expected instructions
- **Amber test cases**: Some groups (early_fragment, execution_mode, mixed_relaxed_precision_operands, function_params, image_query, oparraylength) use Amber test framework
- **Precision-sensitive verification**: `nocontraction` tests use carefully chosen floating-point values where fused multiply-add would produce a different result than separate multiply and add

## Notes

- This file is the single largest source file in the spirv_assembly category at over 21,000 lines
- The `compute`/`graphics` split means many SPIR-V instructions are tested under both pipeline types, often with similar test logic but different shader infrastructure
- Some groups under `compute` have no `graphics` counterpart (e.g., `opatomic*`, `bool`, `shader_default_output`) and vice versa (e.g., `barrier`, `cross_stage`, `early_fragment`, `execution_mode`)
- The `android` sub-groups under both `compute` and `graphics` relax the expected result for negative-operand division/modulo from PASS to QUALITY_WARNING
- The `maintenance8` sub-groups test VK_KHR_maintenance8 behavior where negative-operand OpSRem/OpSMod must FAIL instead of being undefined
