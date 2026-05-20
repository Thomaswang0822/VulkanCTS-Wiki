# spirv_assembly

## Overview

The `spirv_assembly` category tests SPIR-V assembly instructions, types, and features by constructing shaders directly in SPIR-V assembly text. Unlike GLSL-based test categories that rely on the GLSL-to-SPIR-V compiler, these tests hand-write SPIR-V modules to precisely control instruction sequences, decorations, and module structure. This enables targeted testing of individual SPIR-V opcodes, capabilities, and edge cases that are difficult or impossible to trigger through high-level shading languages.

## Registration Entry Point

- [vktSpvAsmTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmTests.cpp): `createTests()` registers the `spirv_assembly` group with two direct children: `instruction` and `type`.

## Subgroup Structure

```text
spirv_assembly
├── instruction
│   ├── compute
│   ├── graphics
│   ├── amd_trinary_minmax
│   ├── function_params (non-VulkanSC only)
│   ├── image_query (non-VulkanSC only)
│   ├── maint9_vectorization
│   ├── spirv1p4 (non-VulkanSC only)
│   └── terminate_invocation (non-VulkanSC only)
└── type
    ├── scalar
    ├── vec1 (non-VulkanSC only)
    ├── vec2
    ├── vec3
    ├── vec4
    ├── vec8 (non-VulkanSC only)
    └── vec12 (non-VulkanSC only)
```

### instruction — SPIR-V instruction tests

The largest subgroup, organized by pipeline type:

- **instruction.compute**: Tests using compute shaders via `SpvAsmComputeShaderCase`. Contains ~90 subgroups covering individual SPIR-V instructions and features.
- **instruction.graphics**: Tests using graphics pipelines (vertex + fragment, optionally geometry/tessellation) via `SpvAsmGraphicsShaderTestUtil`. Contains ~60 subgroups.
- **instruction.amd_trinary_minmax**: AMD trinary min/max extension operations.
- **instruction.spirv1p4**: SPIR-V 1.4 new features (non-VulkanSC).
- **instruction.maint9_vectorization**: VK_KHR_maintenance9 vectorized bit operations.
- **instruction.terminate_invocation**: VK_KHR_shader_terminate_invocation (non-VulkanSC).
- **instruction.function_params**: Function parameter passing (non-VulkanSC).
- **instruction.image_query**: Image query operations (non-VulkanSC).

### type — Integer type operation tests

Systematic testing of integer operations across all widths (8/16/32/64-bit) and signedness, with scalar and vector forms. Uses a templated `SpvAsmTypeTests<T>` framework.

## File Inventory

### Registration/aggregator files

| File | Role | Level-3 Doc |
|------|------|-------------|
| vktSpvAsmTests.cpp | Root registration | (covered by this doc) |
| vktSpvAsmInstructionTests.cpp | Instruction aggregator + inline tests | [vktSpvAsmInstructionTests.md](../testfiles/spirv_assembly/vktSpvAsmInstructionTests.md) |
| vktSpvAsmTypeTests.cpp | Type aggregator + inline tests | [vktSpvAsmTypeTests.md](../testfiles/spirv_assembly/vktSpvAsmTypeTests.md) |

### Implementation files

| File | Groups Created | Level-3 Doc |
|------|---------------|-------------|
| vktSpvAsm8bitStorageTests.cpp | compute/graphics `8bit_storage` | [vktSpvAsm8bitStorageTests.md](../testfiles/spirv_assembly/vktSpvAsm8bitStorageTests.md) |
| vktSpvAsm16bitStorageTests.cpp | compute/graphics `16bit_storage` | [vktSpvAsm16bitStorageTests.md](../testfiles/spirv_assembly/vktSpvAsm16bitStorageTests.md) |
| vktSpvAsm64bitCompareTests.cpp | compute/graphics `64bit_compare` | [vktSpvAsm64bitCompareTests.md](../testfiles/spirv_assembly/vktSpvAsm64bitCompareTests.md) |
| vktSpvAsmCompositeInsertTests.cpp | compute/graphics `composite_insert` | [vktSpvAsmCompositeInsertTests.md](../testfiles/spirv_assembly/vktSpvAsmCompositeInsertTests.md) |
| vktSpvAsmComputeShaderDerivativesTests.cpp | compute `compute_shader_derivatives` | [vktSpvAsmComputeShaderDerivativesTests.md](../testfiles/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.md) |
| vktSpvAsmConditionalBranchTests.cpp | compute/graphics `conditional_branch` | [vktSpvAsmConditionalBranchTests.md](../testfiles/spirv_assembly/vktSpvAsmConditionalBranchTests.md) |
| vktSpvAsmCrossStageInterfaceTests.cpp | graphics `cross_stage` | [vktSpvAsmCrossStageInterfaceTests.md](../testfiles/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.md) |
| vktSpvAsmEmptyStructTests.cpp | compute `empty_struct` | [vktSpvAsmEmptyStructTests.md](../testfiles/spirv_assembly/vktSpvAsmEmptyStructTests.md) |
| vktSpvAsmFloatControls2Tests.cpp | compute/graphics `float_controls2` | [vktSpvAsmFloatControls2Tests.md](../testfiles/spirv_assembly/vktSpvAsmFloatControls2Tests.md) |
| vktSpvAsmFloatControlsExtensionlessTests.cpp | compute `float_controls_extensionless` | [vktSpvAsmFloatControlsExtensionlessTests.md](../testfiles/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.md) |
| vktSpvAsmFloatControlsTests.cpp | compute/graphics `float_controls` | [vktSpvAsmFloatControlsTests.md](../testfiles/spirv_assembly/vktSpvAsmFloatControlsTests.md) |
| vktSpvAsmFmaTests.cpp | compute `opfma` | [vktSpvAsmFmaTests.md](../testfiles/spirv_assembly/vktSpvAsmFmaTests.md) |
| vktSpvAsmFromHlslTests.cpp | compute `hlsl_cases` | [vktSpvAsmFromHlslTests.md](../testfiles/spirv_assembly/vktSpvAsmFromHlslTests.md) |
| vktSpvAsmImageSamplerTests.cpp | compute/graphics `image_sampler` | [vktSpvAsmImageSamplerTests.md](../testfiles/spirv_assembly/vktSpvAsmImageSamplerTests.md) |
| vktSpvAsmIndexingTests.cpp | compute/graphics `indexing` | [vktSpvAsmIndexingTests.md](../testfiles/spirv_assembly/vktSpvAsmIndexingTests.md) |
| vktSpvAsmIntegerDotProductTests.cpp | compute `opsdotkhr`/`opudotkhr`/`opsudotkhr`/`opsdotaccsatkhr`/`opudotaccsatkhr`/`opsudotaccsatkhr` | [vktSpvAsmIntegerDotProductTests.md](../testfiles/spirv_assembly/vktSpvAsmIntegerDotProductTests.md) |
| vktSpvAsmLdexpTests.cpp | compute `ldexp` | [vktSpvAsmLdexpTests.md](../testfiles/spirv_assembly/vktSpvAsmLdexpTests.md) |
| vktSpvAsmMaint9VectorizationTests.cpp | `maint9_vectorization` | [vktSpvAsmMaint9VectorizationTests.md](../testfiles/spirv_assembly/vktSpvAsmMaint9VectorizationTests.md) |
| vktSpvAsmMultipleShadersTests.cpp | compute `multiple_shaders_extended` | [vktSpvAsmMultipleShadersTests.md](../testfiles/spirv_assembly/vktSpvAsmMultipleShadersTests.md) |
| vktSpvAsmNonSemanticInfoTests.cpp | compute `non_semantic_info` | [vktSpvAsmNonSemanticInfoTests.md](../testfiles/spirv_assembly/vktSpvAsmNonSemanticInfoTests.md) |
| vktSpvAsmPhysicalStorageBufferPointerTests.cpp | compute `physical_storage_buffer` | [vktSpvAsmPhysicalStorageBufferPointerTests.md](../testfiles/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.md) |
| vktSpvAsmPointerParameterTests.cpp | compute/graphics `pointer_parameter` | [vktSpvAsmPointerParameterTests.md](../testfiles/spirv_assembly/vktSpvAsmPointerParameterTests.md) |
| vktSpvAsmPtrAccessChainTests.cpp | compute `ptr_access_chain` | [vktSpvAsmPtrAccessChainTests.md](../testfiles/spirv_assembly/vktSpvAsmPtrAccessChainTests.md) |
| vktSpvAsmRawAccessChainTests.cpp | compute `raw_access_chain` | [vktSpvAsmRawAccessChainTests.md](../testfiles/spirv_assembly/vktSpvAsmRawAccessChainTests.md) |
| vktSpvAsmRelaxedWithForwardReferenceTests.cpp | compute `relaxed_with_forward_reference` | [vktSpvAsmRelaxedWithForwardReferenceTests.md](../testfiles/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.md) |
| vktSpvAsmSignedIntCompareTests.cpp | compute `signed_int_compare` | [vktSpvAsmSignedIntCompareTests.md](../testfiles/spirv_assembly/vktSpvAsmSignedIntCompareTests.md) |
| vktSpvAsmSignedOpTests.cpp | compute `signed_op` | [vktSpvAsmSignedOpTests.md](../testfiles/spirv_assembly/vktSpvAsmSignedOpTests.md) |
| vktSpvAsmSpirvVersion1p4Tests.cpp | `spirv1p4` | [vktSpvAsmSpirvVersion1p4Tests.md](../testfiles/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.md) |
| vktSpvAsmSpirvVersionTests.cpp | compute/graphics `spirv_version` | [vktSpvAsmSpirvVersionTests.md](../testfiles/spirv_assembly/vktSpvAsmSpirvVersionTests.md) |
| vktSpvAsmTerminateInvocationTests.cpp | `terminate_invocation` | [vktSpvAsmTerminateInvocationTests.md](../testfiles/spirv_assembly/vktSpvAsmTerminateInvocationTests.md) |
| vktSpvAsmTrinaryMinMaxTests.cpp | `amd_trinary_minmax` | [vktSpvAsmTrinaryMinMaxTests.md](../testfiles/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.md) |
| vktSpvAsmUboMatrixPaddingTests.cpp | compute/graphics `ubo_padding` | [vktSpvAsmUboMatrixPaddingTests.md](../testfiles/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.md) |
| vktSpvAsmUntypedPointersTests.cpp | compute `untyped_pointers` | [vktSpvAsmUntypedPointersTests.md](../testfiles/spirv_assembly/vktSpvAsmUntypedPointersTests.md) |
| vktSpvAsmVariableInitTests.cpp | compute/graphics `variable_init` | [vktSpvAsmVariableInitTests.md](../testfiles/spirv_assembly/vktSpvAsmVariableInitTests.md) |
| vktSpvAsmVariablePointersTests.cpp | compute/graphics `variable_pointers`, compute `physical_pointers` | [vktSpvAsmVariablePointersTests.md](../testfiles/spirv_assembly/vktSpvAsmVariablePointersTests.md) |
| vktSpvAsmVaryingNameTests.cpp | graphics `varying_name` | [vktSpvAsmVaryingNameTests.md](../testfiles/spirv_assembly/vktSpvAsmVaryingNameTests.md) |
| vktSpvAsmVectorShuffleTests.cpp | compute `vector_shuffle` | [vktSpvAsmVectorShuffleTests.md](../testfiles/spirv_assembly/vktSpvAsmVectorShuffleTests.md) |
| vktSpvAsmWorkgroupMemoryTests.cpp | compute `workgroup_memory` | [vktSpvAsmWorkgroupMemoryTests.md](../testfiles/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.md) |

### Utility/infrastructure files (no Level-3 docs)

| File | Purpose |
|------|---------|
| vktSpvAsmComputeShaderCase.cpp/.hpp | Compute shader test case infrastructure |
| vktSpvAsmComputeShaderTestUtil.cpp/.hpp | Compute shader test utilities |
| vktSpvAsmGraphicsShaderTestUtil.cpp/.hpp | Graphics shader test utilities |
| vktSpvAsmUtils.cpp/.hpp | General SPIR-V assembly utilities |
| vktSpvAsmLoopDepInfTests.cpp/.hpp | Loop control dependency-infinite test case (added by vktSpvAsmInstructionTests.cpp) |
| vktSpvAsmLoopDepLenTests.cpp/.hpp | Loop control dependency-length test case (added by vktSpvAsmInstructionTests.cpp) |
| vktSpvAsmOpSelectDifferentStridesTests.cpp/.hpp | OpSelect stride test case (added by vktSpvAsmVariablePointersTests.cpp) |

## Cross-file Recurring Test Families

### Compute vs. Graphics pipeline variants

The most prominent structural pattern: many test groups exist under both `instruction.compute` and `instruction.graphics` with similar test logic but different shader infrastructure. Files like `vktSpvAsm8bitStorageTests.cpp`, `vktSpvAsmFloatControlsTests.cpp`, and others provide separate `createXxxComputeGroup` and `createXxxGraphicsGroup` factory functions.

### SPIR-V instruction testing

The core testing pattern across the category: construct a SPIR-V assembly module that exercises a specific instruction, provide input data, run the shader, and verify the output matches a CPU-computed reference.

### Debug instruction testing

Groups like `opline`, `opnoline`, `opsource`, `opsourcecontinued`, `opmoduleprocessed`, `opname`, `opmembername` test debug information instructions that should not affect shader execution behavior.

## Cross-file Recurring Parameter Dimensions

| Dimension | Description | Files |
|-----------|-------------|-------|
| Integer width | 8/16/32/64-bit | TypeTests, 8bit/16bit Storage, IntegerDotProduct, SignedOp |
| Float width | 16/32/64-bit | FloatControls, FloatControls2, TrinaryMinMax |
| Vector size | scalar/vec2/vec3/vec4/vec8/vec12 | TypeTests, TrinaryMinMax, ComputeShaderDerivatives |
| Storage class | Uniform, StorageBuffer, PushConstant, Workgroup | 8bit/16bit Storage, VariablePointers |
| SPIR-V version | 1.0 through latest | SpirvVersionTests, SpirvVersion1p4Tests |
| Memory model | Vulkan, GLSL | UntypedPointers |

## Cross-file Recurring Support Requirements

| Requirement | Affected Files |
|-------------|----------------|
| `shaderInt8` | TypeTests (i8/u8), 8bitStorage, IntegerDotProduct, SignedOp |
| `shaderInt16` | TypeTests (i16/u16), 16bitStorage, IntegerDotProduct |
| `shaderInt64` | TypeTests (i64/u64), 64bitCompare, VariablePointers |
| `shaderFloat16` | FloatControls, FloatControls2, TrinaryMinMax |
| `shaderFloat64` | FloatControls, FloatControls2, 64bitCompare, TrinaryMinMax |
| `VK_KHR_8bit_storage` | 8bitStorage |
| `VK_KHR_16bit_storage` | 16bitStorage |
| `VK_KHR_shader_float_controls` | FloatControls, FloatControlsExtensionless |
| `VK_KHR_shader_float_controls2` | FloatControls2 |
| `VK_KHR_variable_pointers` | VariablePointers |
| `VK_KHR_vulkan_memory_model` | InstructionTests (volatile atomics) |
| `VK_KHR_maintenance4` | InstructionTests (localsize_id), MultipleShaders |
| `VK_KHR_maintenance8` | InstructionTests (maintenance8 subgroups) |
| `VK_KHR_maintenance9` | Maint9Vectorization |
| `VK_KHR_shader_terminate_invocation` | TerminateInvocation |
| `VK_KHR_compute_shader_derivatives` | ComputeShaderDerivatives |
| `VK_KHR_shader_untyped_pointers` | UntypedPointers |
| `VK_KHR_shader_integer_dot_product` | IntegerDotProduct |
| `VK_AMD_shader_trinary_minmax` | TrinaryMinMax |
| `VK_AMD_shader_early_and_late_fragment_tests` | InstructionTests (early_and_late_fragment) |
| `VK_NV_raw_access_chains` | RawAccessChain |
| `VK_EXT_mesh_shader` | ComputeShaderDerivatives (mesh/task subgroups) |

## Cross-file Recurring Verification Methods

| Method | Description | Files |
|--------|-------------|-------|
| Compute buffer comparison | Write results to storage buffer, compare against CPU reference | Most compute tests |
| Graphics color comparison | Render full-screen quad, compare output RGBA against expected | Most graphics tests |
| Binary verification | Inspect compiled SPIR-V binary for expected instructions | OpModuleProcessed |
| Amber test framework | Declarative test specification via Amber | EarlyFragment, ExecutionMode, TerminateInvocation, SpirvVersion1p4, PtrAccessChain, FunctionParams, ImageQuery, OpArrayLength, MixedRelaxedPrecision |
| Precision-sensitive comparison | Use values where fused operations produce different results | NoContraction |
| Multi-option result | Accept one of multiple valid results (e.g., NaN handling) | NMin/NMax/NClamp, OpQuantizeToF16 |

## Notes

- The `spirv_assembly` category is one of the largest in Vulkan CTS, with the `instruction` subgroup alone containing over 150 subgroups across compute and graphics pipelines
- Many groups exist under both `compute` and `graphics` with similar test logic but different shader infrastructure, leading to a large total test count
- The `vktSpvAsmInstructionTests.cpp` file is over 21,000 lines and serves as both aggregator and implementation for the majority of inline instruction tests
- Non-VulkanSC guards (`#ifndef CTS_USES_VULKANSC`) exclude several groups (float_controls2, integer_dot_product, compute_shader_derivatives, fma, spirv1p4, etc.) from Vulkan SC builds
