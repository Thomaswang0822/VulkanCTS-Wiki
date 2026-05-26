# spirv_assembly

## Overview

The [`spirv_assembly`](../../modules/vulkan/spirv_assembly/vktSpvAsmTests.cpp#L50-L53) category verifies SPIR-V
assembly modules by constructing shader text directly instead of relying on a high-level shader-language compiler. The root
Vulkan package registers the category as `spirv_assembly` in both default Vulkan and Vulkan SC package construction paths at
[`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1352) and
[`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1420). The category root then delegates to the
`instruction` and `type` subgroups in [`createChildren()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTests.cpp#L38-L46).

The source tree is intentionally broad: the shared Vulkan/Vulkan SC source list covers core SPIR-V assembly infrastructure
and many instruction/type files, while the Vulkan-only list adds newer or non-SC feature areas such as `float_controls2`,
`fma`, integer dot product, untyped pointers, compute shader derivatives, `ldexp`, and the OpSelect stride helper at
[`CMakeLists.txt`](../../modules/vulkan/spirv_assembly/CMakeLists.txt#L8-L108).

## Registration Entry Point

The category entry point is [`createTests()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTests.cpp#L50-L53), which returns
`createTestGroup()` with [`createChildren()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTests.cpp#L38-L46). The direct
children registered under `spirv_assembly` are:

```text
spirv_assembly
├── instruction
└── type
```

Source: [`createChildren()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTests.cpp#L38-L46).

## File Inventory

| File | Role | Registered group(s) / notes | Level-3 doc |
|---|---|---|---|
| [`vktSpvAsmTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTests.cpp#L1) | Root registration | Adds `instruction` and `type` | Covered by this page |
| [`vktSpvAsmTests.hpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTests.hpp#L29-L35) | Category header | Declares the category factory used by package registration | Covered by this page |
| [`vktSpvAsmInstructionTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21311-L21545) | Instruction aggregator + inline tests | Builds `instruction`, `instruction.compute`, `instruction.graphics`, and several top-level instruction children | [`vktSpvAsmInstructionTests.md`](../testfiles/spirv_assembly/vktSpvAsmInstructionTests.md) |
| [`vktSpvAsmTypeTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L4278-L4445) | Type aggregator + generated integer-operation tests | Builds `type` scalar/vector groups and populates signed/unsigned integer operation tests | [`vktSpvAsmTypeTests.md`](../testfiles/spirv_assembly/vktSpvAsmTypeTests.md) |
| [`CMakeLists.txt`](../../modules/vulkan/spirv_assembly/CMakeLists.txt#L8-L131) | Build inventory | Separates shared Vulkan/Vulkan SC sources from Vulkan-only sources | No Level-3 doc |

## Level-3 Documents

| Source file | Primary registered group(s) / role | Wiki document |
|---|---|---|
| [`vktSpvAsm8bitStorageTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L928-L1084) | `8bit_storage` compute/graphics storage and conversion cases | [`vktSpvAsm8bitStorageTests.md`](../testfiles/spirv_assembly/vktSpvAsm8bitStorageTests.md) |
| [`vktSpvAsm16bitStorageTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8620-L8651) | `16bit_storage` compute/graphics cases | [`vktSpvAsm16bitStorageTests.md`](../testfiles/spirv_assembly/vktSpvAsm16bitStorageTests.md) |
| [`vktSpvAsm64bitCompareTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1777-L1807) | `64bit_compare` compute/graphics comparisons | [`vktSpvAsm64bitCompareTests.md`](../testfiles/spirv_assembly/vktSpvAsm64bitCompareTests.md) |
| [`vktSpvAsmCompositeInsertTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmCompositeInsertTests.cpp#L660-L675) | `composite_insert` compute/graphics matrix and composite insertion tests | [`vktSpvAsmCompositeInsertTests.md`](../testfiles/spirv_assembly/vktSpvAsmCompositeInsertTests.md) |
| [`vktSpvAsmComputeShaderDerivativesTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3730-L4176) | `compute_shader_derivatives` compute/mesh/task derivative cases | [`vktSpvAsmComputeShaderDerivativesTests.md`](../testfiles/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.md) |
| [`vktSpvAsmConditionalBranchTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L222-L236) | `conditional_branch` compute/graphics same-label branch tests | [`vktSpvAsmConditionalBranchTests.md`](../testfiles/spirv_assembly/vktSpvAsmConditionalBranchTests.md) |
| [`vktSpvAsmCrossStageInterfaceTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2717-L2743) | `cross_stage` graphics interface compatibility tests | [`vktSpvAsmCrossStageInterfaceTests.md`](../testfiles/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.md) |
| [`vktSpvAsmEmptyStructTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmEmptyStructTests.cpp#L39-L61) | `empty_struct` compute cases using empty structures | [`vktSpvAsmEmptyStructTests.md`](../testfiles/spirv_assembly/vktSpvAsmEmptyStructTests.md) |
| [`vktSpvAsmFloatControls2Tests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControls2Tests.cpp#L3333-L3356) | `float_controls2` compute/graphics float-control-2 cases | [`vktSpvAsmFloatControls2Tests.md`](../testfiles/spirv_assembly/vktSpvAsmFloatControls2Tests.md) |
| [`vktSpvAsmFloatControlsExtensionlessTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L240-L276) | `float_controls_extensionless` compute cases | [`vktSpvAsmFloatControlsExtensionlessTests.md`](../testfiles/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.md) |
| [`vktSpvAsmFloatControlsTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L5383-L5426) | `float_controls` compute/graphics operation and settings cases | [`vktSpvAsmFloatControlsTests.md`](../testfiles/spirv_assembly/vktSpvAsmFloatControlsTests.md) |
| [`vktSpvAsmFmaTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L579-L612) | `opfma` fused multiply-add cases | [`vktSpvAsmFmaTests.md`](../testfiles/spirv_assembly/vktSpvAsmFmaTests.md) |
| [`vktSpvAsmFromHlslTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L221-L235) | `hlsl_cases` imported HLSL-layout style compute cases | [`vktSpvAsmFromHlslTests.md`](../testfiles/spirv_assembly/vktSpvAsmFromHlslTests.md) |
| [`vktSpvAsmImageSamplerTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L2466-L2502) | `image_sampler` compute/graphics image and sampler instruction cases | [`vktSpvAsmImageSamplerTests.md`](../testfiles/spirv_assembly/vktSpvAsmImageSamplerTests.md) |
| [`vktSpvAsmIndexingTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L761-L780) | `indexing` compute/graphics indexing cases | [`vktSpvAsmIndexingTests.md`](../testfiles/spirv_assembly/vktSpvAsmIndexingTests.md) |
| [`vktSpvAsmIntegerDotProductTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1240-L1305) | Integer dot-product operation families | [`vktSpvAsmIntegerDotProductTests.md`](../testfiles/spirv_assembly/vktSpvAsmIntegerDotProductTests.md) |
| [`vktSpvAsmLdexpTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmLdexpTests.cpp#L35-L143) | `ldexp` Amber cases | [`vktSpvAsmLdexpTests.md`](../testfiles/spirv_assembly/vktSpvAsmLdexpTests.md) |
| [`vktSpvAsmMaint9VectorizationTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1291-L1349) | `maint9_vectorization` vectorized bit-operation cases | [`vktSpvAsmMaint9VectorizationTests.md`](../testfiles/spirv_assembly/vktSpvAsmMaint9VectorizationTests.md) |
| [`vktSpvAsmMultipleShadersTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L449-L461) | `multiple_shaders_extended` multi-entry-point compute cases | [`vktSpvAsmMultipleShadersTests.md`](../testfiles/spirv_assembly/vktSpvAsmMultipleShadersTests.md) |
| [`vktSpvAsmNonSemanticInfoTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmNonSemanticInfoTests.cpp#L319-L338) | `non_semantic_info` cases | [`vktSpvAsmNonSemanticInfoTests.md`](../testfiles/spirv_assembly/vktSpvAsmNonSemanticInfoTests.md) |
| [`vktSpvAsmPhysicalStorageBufferPointerTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L742-L760) | `physical_storage_buffer` pointer/addressing cases | [`vktSpvAsmPhysicalStorageBufferPointerTests.md`](../testfiles/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.md) |
| [`vktSpvAsmPointerParameterTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1082-L1105) | `pointer_parameter` compute/graphics pointer-parameter cases | [`vktSpvAsmPointerParameterTests.md`](../testfiles/spirv_assembly/vktSpvAsmPointerParameterTests.md) |
| [`vktSpvAsmPtrAccessChainTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L73-L78) | `ptr_access_chain` Amber cases | [`vktSpvAsmPtrAccessChainTests.md`](../testfiles/spirv_assembly/vktSpvAsmPtrAccessChainTests.md) |
| [`vktSpvAsmRawAccessChainTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1000-L1204) | `raw_access_chain` generated load/store matrix | [`vktSpvAsmRawAccessChainTests.md`](../testfiles/spirv_assembly/vktSpvAsmRawAccessChainTests.md) |
| [`vktSpvAsmRelaxedWithForwardReferenceTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.cpp#L280-L286) | `relaxed_with_forward_reference` compute cases | [`vktSpvAsmRelaxedWithForwardReferenceTests.md`](../testfiles/spirv_assembly/vktSpvAsmRelaxedWithForwardReferenceTests.md) |
| [`vktSpvAsmSignedIntCompareTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L74-L79) | `signed_int_compare` Amber cases | [`vktSpvAsmSignedIntCompareTests.md`](../testfiles/spirv_assembly/vktSpvAsmSignedIntCompareTests.md) |
| [`vktSpvAsmSignedOpTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L89-L94) | `signed_op` Amber cases | [`vktSpvAsmSignedOpTests.md`](../testfiles/spirv_assembly/vktSpvAsmSignedOpTests.md) |
| [`vktSpvAsmSpirvVersion1p4Tests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L128-L136) | `spirv1p4` Amber cases | [`vktSpvAsmSpirvVersion1p4Tests.md`](../testfiles/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.md) |
| [`vktSpvAsmSpirvVersionTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L321-L332) | `spirv_version` compute/graphics version-capability checks | [`vktSpvAsmSpirvVersionTests.md`](../testfiles/spirv_assembly/vktSpvAsmSpirvVersionTests.md) |
| [`vktSpvAsmTerminateInvocationTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L110-L165) | `terminate_invocation` Amber cases | [`vktSpvAsmTerminateInvocationTests.md`](../testfiles/spirv_assembly/vktSpvAsmTerminateInvocationTests.md) |
| [`vktSpvAsmTrinaryMinMaxTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L979-L1043) | `amd_trinary_minmax` operation/type/vector matrix | [`vktSpvAsmTrinaryMinMaxTests.md`](../testfiles/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.md) |
| [`vktSpvAsmUboMatrixPaddingTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L277-L291) | `ubo_padding` compute/graphics matrix-padding cases | [`vktSpvAsmUboMatrixPaddingTests.md`](../testfiles/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.md) |
| [`vktSpvAsmUntypedPointersTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12702-L12710) | `untyped_pointers` Vulkan/GLSL memory-model subtrees | [`vktSpvAsmUntypedPointersTests.md`](../testfiles/spirv_assembly/vktSpvAsmUntypedPointersTests.md) |
| [`vktSpvAsmVariableInitTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L658-L674) | `variable_init` compute/graphics initialization cases | [`vktSpvAsmVariableInitTests.md`](../testfiles/spirv_assembly/vktSpvAsmVariableInitTests.md) |
| [`vktSpvAsmVariablePointersTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2747-L2809) | `variable_pointers` and `physical_pointers` compute/graphics cases | [`vktSpvAsmVariablePointersTests.md`](../testfiles/spirv_assembly/vktSpvAsmVariablePointersTests.md) |
| [`vktSpvAsmVaryingNameTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmVaryingNameTests.cpp#L234-L242) | `varying_name` graphics interface-name cases | [`vktSpvAsmVaryingNameTests.md`](../testfiles/spirv_assembly/vktSpvAsmVaryingNameTests.md) |
| [`vktSpvAsmVectorShuffleTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L68-L73) | `vector_shuffle` Amber cases | [`vktSpvAsmVectorShuffleTests.md`](../testfiles/spirv_assembly/vktSpvAsmVectorShuffleTests.md) |
| [`vktSpvAsmWorkgroupMemoryTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L141-L230) | `workgroup_memory` compute cases | [`vktSpvAsmWorkgroupMemoryTests.md`](../testfiles/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.md) |

## Subgroup Structure and Major Themes

### `instruction` — SPIR-V instruction, capability, module, and execution-mode coverage

The `instruction` group is created by [`createInstructionTests()`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21311-L21317).
It registers large `compute` and `graphics` children, then appends top-level instruction children including `spirv1p4`,
`function_params`, `image_query`, `amd_trinary_minmax`, `terminate_invocation`, and `maint9_vectorization` at
[`vktSpvAsmInstructionTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21535-L21545). The
compute branch includes module/version checks, debug instructions, constants, atomics, memory access, conversions, storage
extensions, pointer families, image/sampler cases, workgroup memory, raw access chains, and other generated families at
[`vktSpvAsmInstructionTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21319-L21449). The
graphics branch covers analogous graphics-stage families plus cross-stage interfaces, execution modes, early-fragment tests,
fragment behavior, and graphics variants for several storage/pointer/image groups at
[`vktSpvAsmInstructionTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21451-L21533).

### `type` — Generated integer scalar/vector operation coverage

The `type` group is created by [`createTypeTests()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L4278-L4285).
It builds scalar and vector-size containers, creates signed and unsigned integer test builders for 8-, 16-, 32-, and 64-bit
integer widths, then populates arithmetic, shifts, bitwise operations, comparisons, constants, and variable/specialization
constant initializer families through macro-expanded `createTests()` calls at
[`vktSpvAsmTypeTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L4313-L4428). The source adds scalar
signed/unsigned groups first and then attaches vector-width groups at
[`vktSpvAsmTypeTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L4430-L4445).

### Compute/graphics paired families

Several implementation files intentionally expose similarly named compute and graphics groups. Examples include
`8bit_storage`, `16bit_storage`, `float_controls`, `ubo_padding`, `composite_insert`, `variable_init`, `conditional_branch`,
`indexing`, `variable_pointers`, `image_sampler`, `pointer_parameter`, and `64bit_compare`, each registered in the compute
and graphics branches by [`createInstructionTests()`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21393-L21434)
and [`createInstructionTests()`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21492-L21519). The
implementation files then provide separate factories where needed, such as
[`createPointerParameterComputeGroup()`](../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1082-L1092)
and [`createPointerParameterGraphicsGroup()`](../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1095-L1105).

### Amber-backed instruction leaves

Some instruction leaves are imported from Amber scripts rather than generated only from C++ string templates. Examples
include signed integer compare at [`vktSpvAsmSignedIntCompareTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmSignedIntCompareTests.cpp#L74-L79),
signed operations at [`vktSpvAsmSignedOpTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmSignedOpTests.cpp#L89-L94),
SPIR-V 1.4 at [`vktSpvAsmSpirvVersion1p4Tests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L128-L136),
`ptr_access_chain` at [`vktSpvAsmPtrAccessChainTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L73-L78),
`vector_shuffle` at [`vktSpvAsmVectorShuffleTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L68-L73),
and `terminate_invocation` at [`vktSpvAsmTerminateInvocationTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L110-L165).

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Pipeline path | `instruction.compute` and `instruction.graphics` are separate direct children at [`vktSpvAsmInstructionTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21315-L21317), populated by the compute branch at [`vktSpvAsmInstructionTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21319-L21449) and the graphics branch at [`vktSpvAsmInstructionTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21451-L21533) |
| Integer width and signedness | The type framework creates signed and unsigned 8-, 16-, 32-, and 64-bit builders at [`vktSpvAsmTypeTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L4297-L4310); integer dot-product and signed-operation pages document narrower instruction-specific matrices |
| Vector size | The type framework creates `scalar`, `vec1`, `vec2`, `vec3`, `vec4`, `vec8`, and `vec12` containers at [`vktSpvAsmTypeTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L4281-L4295), while trinary min/max iterates scalar through `vec4` at [`vktSpvAsmTrinaryMinMaxTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L1003-L1008) |
| Storage class and descriptor style | 8-bit storage cases distinguish storage-buffer and uniform/storage-buffer capabilities in `CAPABILITIES[]` at [`vktSpvAsm8bitStorageTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L98-L114); pointer and untyped-pointer families include storage buffer, uniform, push constant, and workgroup concepts in source enums and generated groups at [`vktSpvAsmUntypedPointersTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L123-L130) |
| Pointer/addressing mode | Variable-pointer tests switch between logical variable pointers and physical-storage-buffer pointers at [`vktSpvAsmVariablePointersTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L859-L869), while raw access-chain cases generate combinations for variable pointers, descriptor indexing, physical buffers, 64-bit indexing, bounds checks, qualifiers, stride, component size, and alignment at [`vktSpvAsmRawAccessChainTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L1000-L1196) |
| Memory model | Untyped-pointer tests create separate `vulkan_memory_model` and `glsl_memory_model` children at [`vktSpvAsmUntypedPointersTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12702-L12710) |
| Operation family | Type tests macro-expand arithmetic, extended GLSL.std.450 min/max/clamp, shifts, bitwise operations, comparisons, constants, variable initializers, and specialization constants at [`vktSpvAsmTypeTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L4313-L4428); trinary min/max iterates min/max/mid operations over base types and widths at [`vktSpvAsmTrinaryMinMaxTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L984-L1035) |
| Vulkan/Vulkan SC availability | Shared sources are in `DEQP_VK_VKSC_SPIRV_ASSEMBLY_SRCS`, while Vulkan-only source files are listed in `DEQP_VK_SPIRV_ASSEMBLY_SRCS` at [`CMakeLists.txt`](../../modules/vulkan/spirv_assembly/CMakeLists.txt#L8-L108); additional non-SC registration guards appear inside [`createInstructionTests()`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21361-L21369) and [`createInstructionTests()`](../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21429-L21449) |

## Recurring Support Requirements

Support is driven by per-case feature requests, extension lists, Amber requirements, and explicit `checkSupport()` methods.
Representative observed gates include:

| Requirement area | Observed source evidence |
|---|---|
| 8-bit and 16-bit storage | 8-bit storage cases emit `SPV_KHR_8bit_storage` / storage-buffer storage extensions and request 8-bit storage features at [`vktSpvAsm8bitStorageTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1072-L1080); 16-bit storage uses custom 16-bit comparison and feature paths in [`vktSpvAsm16bitStorageTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L4227-L4293) |
| Float controls | Float-controls tests require `VK_KHR_shader_float_controls` for independence settings at [`verifyIndependenceSettings()`](../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3877-L3881), and operation builders select per-output verification callbacks at [`vktSpvAsmFloatControlsTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L4272-L4283) |
| Float-controls extensionless and SPIR-V 1.4 | Extensionless cases require `VK_KHR_spirv_1_4` for relevant SPIR-V versions and request float16/int8 or float64 features as needed at [`SpvAsmFloatControlsExtensionlessCase::checkSupport()`](../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsExtensionlessTests.cpp#L206-L233) |
| Compute shader derivatives and mesh/task paths | Compute derivative cases require `VK_KHR_compute_shader_derivatives`, and mesh/task variants require `VK_EXT_mesh_shader` at [`ComputeShaderDerivativeCase::checkSupport()`](../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2831-L2860) |
| Variable and physical pointers | Pointer-parameter tests request `VK_KHR_variable_pointers` and variable-pointer features for buffer-memory variable-pointer paths at [`vktSpvAsmPointerParameterTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1069-L1077); variable/physical pointer tests switch between `SPV_KHR_variable_pointers` and `SPV_KHR_physical_storage_buffer` assembly paths at [`vktSpvAsmVariablePointersTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L859-L869) |
| Raw access chains | Raw access-chain cases require `VK_NV_raw_access_chains`, and conditionally require variable pointers, buffer-device address, shader float16/int8, shader int16, and shader int64 according to the generated spec flags at [`SpvAsmRawAccessChainTestCase::checkSupport()`](../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L448-L487) |
| Maintenance9 vectorization | Maintenance9 vectorization cases conditionally require `VK_KHR_maintenance9`, `shaderInt64`, and `shaderInt16` based on parameters at [`M9V_Case::checkSupport()`](../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L282-L313) |
| Trinary min/max | AMD trinary min/max cases require `VK_AMD_shader_trinary_minmax` and supporting storage-buffer/8-bit/16-bit/64-bit gates depending on selected type size at [`TrinaryMinMaxCase::checkSupport()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L584-L616) |
| Terminate invocation | Terminate-invocation Amber cases add `VK_KHR_shader_terminate_invocation` and case-specific requirements at [`vktSpvAsmTerminateInvocationTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L91-L99) |
| Untyped pointers | Untyped-pointer cooperative-matrix interaction cases require `VK_KHR_shader_untyped_pointers` and `VK_KHR_cooperative_matrix` in the inspected support path at [`CooperativeMatrixInteractionTestCase::checkSupport()`](../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12224-L12235) |

## Recurring Verification Methods

| Method | Description | Evidence |
|---|---|---|
| Compute output-buffer comparison | Compute shader cases commonly write storage-buffer outputs and compare against expected packed bytes or custom callbacks | Shared compute verification uses `verifyOutputWithEpsilon()` and `verifyOutput()` in [`vktSpvAsmComputeShaderTestUtil.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L32-L140) |
| Graphics color and resource verification | Graphics tests compare rendered colors and, when `verifyIO` is provided, validate output resources after execution | Graphics utility code checks corner pixels and output resources at [`vktSpvAsmGraphicsShaderTestUtil.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L4575-L4589) and [`vktSpvAsmGraphicsShaderTestUtil.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L4721-L4734) |
| Custom numeric comparison | Storage and float-control families use custom comparison callbacks for rounding, NaN, and width-sensitive results | Examples include 16-bit comparison helpers in [`vktSpvAsm16bitStorageTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L93-L107), float-control byte comparison in [`vktSpvAsmFloatControlsTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmFloatControlsTests.cpp#L3416-L3577), and workgroup-memory NaN-aware float64 verification in [`vktSpvAsmWorkgroupMemoryTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L115-L139) |
| Type-framework result callbacks | Type tests select default and vec3-aware output verification callbacks and also contain switch-test handling | [`SpvAsmTypeTests<T>::createStageTests()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1687-L1836), [`verifyResult()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2030-L2092), and switch-test comments at [`vktSpvAsmTypeTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2484-L2496) |
| Byte-for-byte generated-output checks | Raw access-chain and trinary min/max cases compare generated reference buffers against shader output bytes | Raw access-chain iteration uses `deMemCmp()` at [`vktSpvAsmRawAccessChainTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmRawAccessChainTests.cpp#L398-L404); trinary min/max uses `OperationManager::compareResults()` and `deMemCmp()` at [`vktSpvAsmTrinaryMinMaxTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTrinaryMinMaxTests.cpp#L510-L525) |
| SPIR-V binary inspection | Some graphics utility paths allow a per-test `verifyBinary` hook before execution | [`vktSpvAsmGraphicsShaderTestUtil.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L3974-L4001) |
| Amber execution/probe checks | Amber-backed groups rely on the Amber test-case wrapper plus script-local probes and requirements | Representative group factories identify Amber data directories in [`vktSpvAsmPtrAccessChainTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L73-L78), [`vktSpvAsmVectorShuffleTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmVectorShuffleTests.cpp#L68-L73), and [`vktSpvAsmTerminateInvocationTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L110-L165) |

## Notes and Scope

- The page summarizes the category-level structure; detailed parameter matrices and per-file uncertainties are documented in
the Level-3 pages under [`spirv_assembly/`](../testfiles/spirv_assembly/).
- The source uses both C++-generated SPIR-V assembly and Amber script-backed tests. The Level-3 pages distinguish those paths
for each file.
- Vulkan SC availability is not uniform across the category. Shared source membership in
[`DEQP_VK_VKSC_SPIRV_ASSEMBLY_SRCS`](../../modules/vulkan/spirv_assembly/CMakeLists.txt#L8-L91) and `#ifndef
CTS_USES_VULKANSC` guards in registration code should be treated as the evidence for SC inclusion/exclusion, rather than
assuming every instruction family is available in every build.
- Utility files such as [`vktSpvAsmComputeShaderCase.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderCase.cpp#L1),
[`vktSpvAsmComputeShaderTestUtil.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L1),
[`vktSpvAsmGraphicsShaderTestUtil.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L1), and
[`vktSpvAsmUtils.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmUtils.cpp#L1) provide shared infrastructure but do not
serve as separate Level-3 documentation units in this wiki batch.
