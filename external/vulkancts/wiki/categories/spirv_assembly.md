## Overview

The `spirv_assembly` test category checks Vulkan implementations by executing CTS-authored SPIR-V modules that exercise instruction, type, capability, interface, memory, and execution-mode behavior. Most families build assembly text directly in C++ templates; the `hlsl_cases` test family is the explicit high-level-language exception, and the Amber-backed families load literal SPIR-V test data from Amber scripts.

## Background Knowledge

- **SPIR-V modules and validation.** A SPIR-V module declares capabilities, types, storage classes, entry points, decorations, and instructions. C++-templated families author assembly directly, while Amber-backed families preserve literal Amber assembly rather than reconstructing a source shader.
- **Vulkan shader interfaces and resources.** Descriptor-set and binding decorations connect SPIR-V variables to Vulkan resources. Graphics families additionally rely on stage interfaces, locations, components, built-ins, and execution modes to connect producer and consumer stages.
- **Data layout and pointer semantics.** Array and member offsets, matrix strides, storage classes, logical pointers, physical storage-buffer addresses, access chains, and memory models determine which bytes an instruction reads or writes.
- **Capabilities, extensions, and feature gates.** A module's declared SPIR-V capability is only one part of support. CTS also checks the relevant Vulkan extension, core-version feature, and device feature before executing a leaf, so a skipped case is not an instruction-result failure.
- **Host-side oracles.** Most compute cases read an output buffer and compare typed values, while graphics cases compare rendered outputs or interface effects. Some families use operation-specific comparison rules for floating-point values, NaNs, packed integers, termination, or intentionally ignored marker fields.

## Category Structure

```text
spirv_assembly
├── instruction
└── type
```

The implementation-bearing Level-3 pages below cover the registered families under these branches. A page may cover one family with many intermediate nodes and executable leaves; the navigation table names the concrete family page rather than expanding every leaf at category level.

## How the Families Fit Together

The category varies the point at which SPIR-V behavior is stressed:

- **Instruction and type families** check individual instructions or tightly related instruction matrices, including arithmetic, comparisons, composite operations, image access, control flow, FMA, dot products, and vectorization; the direct `type` branch runs the generated scalar- and vector-type operation matrix.
- **Memory, storage, and pointer families** check representation and addressing: 8/16-bit storage, raw and typed access chains, variable and untyped pointers, physical storage-buffer pointers, pointer parameters, workgroup memory, and UBO matrix padding.
- **Module and execution families** check module structure and execution semantics, including multiple entry points, SPIR-V versions, forward references, non-semantic information, variable initialization, termination, and empty structures.
- **Graphics-interface families** check cross-stage compatibility, varying-name behavior, indexing across stages, image/sampler use, and graphics variants of storage and comparison operations.
- **Amber-backed families** use literal SPIR-V assembly embedded in Amber scripts. They cover `ldexp`, signed operations and comparisons, vector shuffle, SPIR-V 1.4 features, `OpPtrAccessChain`, and invocation termination without pretending that a GLSL/HLSL source shader exists.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `8bit_storage` | [`8bitStorageTests.md`](../testfiles/spirv_assembly/8bitStorageTests.md) | 8-bit storage, conversion, and feature-gated resource cases |
| `16bit_storage` | [`16bitStorageTests.md`](../testfiles/spirv_assembly/16bitStorageTests.md) | 16-bit storage and comparison behavior |
| `64bit_compare` | [`64bitCompareTests.md`](../testfiles/spirv_assembly/64bitCompareTests.md) | Signed, unsigned, and floating-point 64-bit comparisons |
| `composite_insert` | [`CompositeInsertTests.md`](../testfiles/spirv_assembly/CompositeInsertTests.md) | Vector, matrix, and nested-composite insertion |
| `compute_shader_derivatives` | [`ComputeShaderDerivativesTests.md`](../testfiles/spirv_assembly/ComputeShaderDerivativesTests.md) | Compute, mesh, and task derivative behavior |
| `conditional_branch` | [`ConditionalBranchTests.md`](../testfiles/spirv_assembly/ConditionalBranchTests.md) | SPIR-V conditional branches with shared labels |
| `cross_stage` | [`CrossStageInterfaceTests.md`](../testfiles/spirv_assembly/CrossStageInterfaceTests.md) | Graphics-stage interface compatibility |
| `empty_struct` | [`EmptyStructTests.md`](../testfiles/spirv_assembly/EmptyStructTests.md) | Empty `OpTypeStruct` copies, pointers, and calls |
| `float_controls` | [`FloatControlsTests.md`](../testfiles/spirv_assembly/FloatControlsTests.md) | Floating-point operation and control-setting matrices |
| `float_controls2` | [`FloatControls2Tests.md`](../testfiles/spirv_assembly/FloatControls2Tests.md) | Second-generation float-control behavior |
| `float_controls_extensionless` | [`FloatControlsExtensionlessTests.md`](../testfiles/spirv_assembly/FloatControlsExtensionlessTests.md) | Extensionless float-control capability paths |
| `opfma` | [`FmaTests.md`](../testfiles/spirv_assembly/FmaTests.md) | Fused multiply-add operation cases |
| `hlsl_cases` | [`FromHlslTests.md`](../testfiles/spirv_assembly/FromHlslTests.md) | The category's explicit HLSL-layout import cases |
| `image_sampler` | [`ImageSamplerTests.md`](../testfiles/spirv_assembly/ImageSamplerTests.md) | Image, sampler, and descriptor instruction families |
| `indexing` | [`IndexingTests.md`](../testfiles/spirv_assembly/IndexingTests.md) | Compute and graphics access-chain indexing |
| Integer dot product families | [`IntegerDotProductTests.md`](../testfiles/spirv_assembly/IntegerDotProductTests.md) | Ordinary, packed, and saturating integer dot products |
| `maint9_vectorization` | [`Maint9VectorizationTests.md`](../testfiles/spirv_assembly/Maint9VectorizationTests.md) | Maintenance 9 vectorized bit operations |
| `multiple_shaders_extended` | [`MultipleShadersTests.md`](../testfiles/spirv_assembly/MultipleShadersTests.md) | Multiple entry points and distinct interfaces in one module |
| `non_semantic_info` | [`NonSemanticInfoTests.md`](../testfiles/spirv_assembly/NonSemanticInfoTests.md) | Non-semantic extended instructions |
| `physical_storage_buffer` | [`PhysicalStorageBufferPointerTests.md`](../testfiles/spirv_assembly/PhysicalStorageBufferPointerTests.md) | Physical-storage-buffer pointer addressing |
| `pointer_parameter` | [`PointerParameterTests.md`](../testfiles/spirv_assembly/PointerParameterTests.md) | Pointer parameters across compute and graphics |
| `ptr_access_chain` | [`PtrAccessChainTests.md`](../testfiles/spirv_assembly/PtrAccessChainTests.md) | Amber `OpPtrAccessChain` workgroup cases |
| `raw_access_chain` | [`RawAccessChainTests.md`](../testfiles/spirv_assembly/RawAccessChainTests.md) | Generated raw access-chain matrix |
| `relaxed_with_forward_reference` | [`RelaxedWithForwardReferenceTests.md`](../testfiles/spirv_assembly/RelaxedWithForwardReferenceTests.md) | Relaxed forward-reference module behavior |
| `signed_int_compare` | [`SignedIntCompareTests.md`](../testfiles/spirv_assembly/SignedIntCompareTests.md) | Signed comparisons on integer bit patterns |
| `signed_op` | [`SignedOpTests.md`](../testfiles/spirv_assembly/SignedOpTests.md) | Signed GLSL.std.450 operations |
| `spirv1p4` | [`SpirvVersion1p4Tests.md`](../testfiles/spirv_assembly/SpirvVersion1p4Tests.md) | Amber SPIR-V 1.4 feature cases |
| `spirv_version` | [`SpirvVersionTests.md`](../testfiles/spirv_assembly/SpirvVersionTests.md) | Version and capability checks |
| `terminate_invocation` | [`TerminateInvocationTests.md`](../testfiles/spirv_assembly/TerminateInvocationTests.md) | Invocation termination semantics |
| `amd_trinary_minmax` | [`TrinaryMinMaxTests.md`](../testfiles/spirv_assembly/TrinaryMinMaxTests.md) | AMD trinary minimum and maximum operations |
| `ubo_padding` | [`UboMatrixPaddingTests.md`](../testfiles/spirv_assembly/UboMatrixPaddingTests.md) | Matrix padding, stride, and layout behavior |
| `untyped_pointers` | [`UntypedPointersTests.md`](../testfiles/spirv_assembly/UntypedPointersTests.md) | Untyped-pointer memory-model cases |
| `variable_init` | [`VariableInitTests.md`](../testfiles/spirv_assembly/VariableInitTests.md) | Variable initialization across storage classes |
| `variable_pointers` / `physical_pointers` | [`VariablePointersTests.md`](../testfiles/spirv_assembly/VariablePointersTests.md) | Logical and physical pointer selection |
| `varying_name` | [`VaryingNameTests.md`](../testfiles/spirv_assembly/VaryingNameTests.md) | Interface matching by location rather than name |
| `vector_shuffle` | [`VectorShuffleTests.md`](../testfiles/spirv_assembly/VectorShuffleTests.md) | Amber vector shuffle and undef components |
| `workgroup_memory` | [`WorkgroupMemoryTests.md`](../testfiles/spirv_assembly/WorkgroupMemoryTests.md) | Workgroup storage, barriers, and result exchange |
| Type operation matrix | [`TypeTests.md`](../testfiles/spirv_assembly/TypeTests.md) | Generated scalar and vector type operations |
| Core instruction aggregation | [`InstructionTests.md`](../testfiles/spirv_assembly/InstructionTests.md) | Shared instruction branch and inline registrations |
| Float exponent operation | [`LdexpTests.md`](../testfiles/spirv_assembly/LdexpTests.md) | Amber `OpExtInst Ldexp` combinations |

## Category Notes

The `spirv_assembly` category intentionally does not use ordinary GLSL/HLSL shader reconstruction for its SPIR-V-centered families. C++-templated pages publish extracted authored assembly under `#### Source Code`; where documented, an assembler, validator, and disassembler round trip is audit-time validation of that published assembly rather than a claimed generation-time gate. Amber-backed pages publish literal Amber assembly and document its provenance directly; they do not claim a generated round trip. `FromHlslTests.md` remains the narrow, explicit exception where HLSL-style source behavior is the subject of the test.
