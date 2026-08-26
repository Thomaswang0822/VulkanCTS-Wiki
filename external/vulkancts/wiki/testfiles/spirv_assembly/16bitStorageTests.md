## Overview

**Core question:** does the implementation correctly load, convert, and store 16-bit float and integer values through each storage class that `VK_KHR_16bit_storage` enables: storage/uniform buffers, push constants, and shader input/output interfaces?

- Source file: [`vktSpvAsm16bitStorageTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp).
- Registered roots: `spirv_assembly.instruction.compute.16bit_storage` and `spirv_assembly.instruction.graphics.16bit_storage`.
- The test builds SPIR-V assembly directly in C++ `tcu::StringTemplate` strings, one template per storage class and conversion direction, then specializes each template across capability, composite type, access index, and (for float narrowing) rounding mode.
- Each case loads 16-bit data from the resource the extension unlocked, converts it with `OpFConvert`/`OpSConvert`/`OpUConvert`, and writes the result to a wide (or 16-bit) sink; the host checks the readback with a direction-specific callback.
- The page covers the four SPIR-V capabilities the extension introduces, the conversion-direction matrix, the struct-layout families, the `FPRoundingMode` mechanism used by float-narrowing families, and what each failure points at.

## Background Knowledge

- `VK_KHR_16bit_storage` (promoted to Vulkan 1.1 core) lets a shader use `OpTypeFloat 16`, `OpTypeInt 16 0`, and `OpTypeInt 16 1` as leaf members in resources Vulkan otherwise lays out at 32-bit granularity. It is exposed through four independent SPIR-V capabilities, each gated by its own `VkPhysicalDevice16BitStorageFeatures` bit: `StorageUniformBufferBlock16` (`storageBuffer16BitAccess`, SSBOs), `StorageUniform16` (`uniformAndStorageBuffer16BitAccess`, UBOs), `StoragePushConstant16` (`storagePushConstant16`, push constants), and `StorageInputOutput16` (`storageInputOutput16`, shader stage I/O, graphics only). A device may support some and not others, so the test exercises each capability independently.
- Converting a 32-bit or 64-bit float to 16-bit is a narrowing operation: many representable wide values fall between two representable 16-bit values, so the result depends on the rounding rule. SPIR-V lets the shader state the rule with `OpDecorate %result FPRoundingMode RTE|RTZ` on the narrowing store (RTE = round-to-nearest-even, RTZ = round-toward-zero); if no mode is decorated, the implementation picks either. Widening (`16_to_32`, `16_to_64`) has no such ambiguity because every 16-bit value maps to exactly one wide value. This distinction drives the checker design: narrowing cases re-derive the expected 16-bit value from the original wide float using the case's rounding mode, while widening cases compare against a precomputed expected buffer.
- `std140` and `std430` are the standard uniform/storage-buffer layout rules. In `std140`, arrays and structures have 16-byte base-alignment rounding, which can add padding around 16-bit members; `std430` relaxes that array/structure rounding where the layout rules allow it. The struct families deliberately mix 16-bit and 32-bit members under both layouts to catch `Offset`/`ArrayStride`/`MatrixStride` miscalculation, since a wrong stride on either side produces a misaligned read that no arithmetic check would catch.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.16bit_storage
├── uniform_64_to_16
├── uniform_32_to_16
├── uniform_16_to_32
├── uniform_16_to_64
├── push_constant_16_to_32
├── push_constant_16_to_64
├── uniform_16struct_to_32struct
├── uniform_32struct_to_16struct
├── struct_mixed_types
├── uniform_16_to_16
└── uniform_16_to_32_chainaccess

spirv_assembly.instruction.graphics.16bit_storage
├── uniform_float_64_to_16
├── uniform_float_32_to_16
├── uniform_float_16_to_32
├── uniform_float_16_to_64
├── uniform_int_32_to_16
├── uniform_int_16_to_32
├── input_output_float_64_to_16
├── input_output_float_32_to_16
├── input_output_float_16_to_32
├── input_output_float_16_to_16
├── input_output_float_16_to_64
├── input_output_float_16_to_16x2
├── input_output_int_16_to_16x2
├── input_output_int_32_to_16
├── input_output_int_16_to_32
├── input_output_int_16_to_16
├── push_constant_float_16_to_32
├── push_constant_float_16_to_64
├── push_constant_int_16_to_32
├── uniform_16struct_to_32struct
├── uniform_32struct_to_16struct
└── struct_mixed_types
```

The `instruction` ancestor and its `compute`/`graphics` children are registered by [`vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp); this page does not expand them. The two `16bit_storage` test families (one under `compute`, one under `graphics`) are registered by [`create16BitStorageComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8620-L8648) and [`create16BitStorageGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8650-L8701). Each visible child is a test family implemented by a dedicated `add*Group` builder in the same source file.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| SPIR-V capability | `StorageUniformBufferBlock16`, `StorageUniform16`, `StoragePushConstant16`, `StorageInputOutput16` | Selects which storage class gets 16-bit access and which `ext16BitStorage` feature bit is required. Drives the `OpCapability` line and the descriptor/push-constant/interface resource kind. | [`CAPABILITIES[]`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L126-L129), [`get16BitStorageFeatures()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L149-L160) |
| Conversion direction | `16_to_32`, `32_to_16`, `16_to_64`, `64_to_16`, `16_to_16`, `16struct_to_32struct`, `32struct_to_16struct` | Sets which side holds the 16-bit data and which `Op*Convert` opcode runs. Narrowing directions force the rounding-mode-aware checker; widening directions use exact comparison. | [`addCompute16bitStorageUniform16To32Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1128-L1504) and siblings |
| Composite type | `scalar`, `vector`, `matrix` (float only) | Changes the SPIR-V type (`f16`/`v2f16`/`m4v2f16`), the `ArrayStride`, and the workgroup count. The matrix case adds `ColMajor`/`MatrixStride` decorations and a multi-column store sequence. | [`cTypes` table](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1228-L1250) |
| Data type | float, sint, uint | Selects `OpFConvert`/`OpSConvert`/`OpUConvert` and the host-side buffer kind. Integers sign-extend on the host during expected-buffer precomputation. | [`cTypes` integer table](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1391-L1427) |
| Access index | dynamic (`x`), constant (`5`, `8`) | `scalar_const_idx_5`/`scalar_const_idx_8` replace the dynamic `OpAccessChain` index with `%c_i32_ci`, isolating constant-index lowering from dynamic-index lowering. | [`useConstantIndex` field](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1222-L1225) |
| Pipeline stage | compute, vertex/tessellation/geometry/fragment | Compute uses a single GLCompute entry point; graphics families run through `createTestsForAllStages` and add a render pass. The `input_output_*` families are graphics-only because they exercise stage interfaces. | [`addGraphics16BitStorageInputOutputFloat32To16Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3637-L3804) |
| Rounding mode (float narrowing) | `rtz`, `rte`, `unspecified_rnd_mode` | Compute uniform-buffer, graphics uniform-buffer, and graphics I/O float-narrowing builders decorate the narrowing result with `FPRoundingMode RTZ`/`RTE`, or omit the decoration so the checker accepts either permitted result for the unspecified case. | [compute `RndMode` table](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L2417-L2422), [graphics I/O `RndMode` table](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3663-L3673) |
| Struct layout | `STRIDE16BIT_STD140`, `STRIDE16BIT_STD430`, `STRIDE32BIT_STD140`, `STRIDE32BIT_STD430`, `STRIDEMIX_STD140`, `STRIDEMIX_STD430` | Sets the `Offset`/`ArrayStride` rules the shader compiler must match; `STRIDEMIX_*` interleaves 16-bit and 32-bit members in one struct. | [`ShaderTemplate` enum](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L83-L92), [`getStructSize()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L162-L182) |

## Behavior Parameters

The primary behavioral axis is the **storage class / capability group**, the SPIR-V capability and storage class under test. It maps directly to the four feature bits the extension introduces and explains why the test families split the way they do. Conversion direction, composite type, and access index are secondary dimensions exercised within each group.

### uniform and storage buffer 16-bit access: `StorageUniformBufferBlock16` and `StorageUniform16`

The uniform-buffer families iterate the [`CAPABILITIES[]`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L126-L129) table, so every case runs twice: once with `StorageUniformBufferBlock16` (input is an SSBO, `BufferBlock` decoration, `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER`) and once with `StorageUniform16` (input is a UBO, `Block` decoration, `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER`). The 32-bit output sink is always an SSBO. Each conversion direction (`16_to_32`, `32_to_16`, `16_to_64`, `64_to_16`, `16_to_16`) has its own builder that specializes a shared `StringTemplate` over float/int and scalar/vector/matrix composites. The `uniform_16_to_32_chainaccess` family uses a deeper `OpAccessChain` path to reach nested members, and the struct families (`uniform_16struct_to_32struct`, `uniform_32struct_to_16struct`, `struct_mixed_types`) swap the flat array for a struct wrapping nested arrays and mixed-width members.

### push constant 16-bit access: `StoragePushConstant16`

The `push_constant_16_to_32` and `push_constant_16_to_64` families replace the input descriptor with a push constant block (`%pc16` in the `PushConstant` storage class). The SPIR-V template is otherwise the same load-convert-store shape, but the input arrives through `OpVariable %pp_PC16 PushConstant` and the host binds the 16-bit input data as the pipeline's push constant range. Only the float and (for `16_to_32`) integer directions are registered; there is no push-constant narrowing or struct family.

### shader input/output interface 16-bit access: `StorageInputOutput16`

The `input_output_*` families are graphics-only. They use `passthruFragments()` plus per-stage `post_interface_op_*` fragments stitched by `createTestsForAllStages`, so the 16-bit value crosses the vertex-to-fragment interface (and tessellation/geometry when those stages run). The narrowing families (`32_to_16`, `64_to_16`) decorate the store with `FPRoundingMode RTZ`/`RTE` or leave it unspecified; the `16_to_16x2` variant writes one 16-bit input to two 16-bit outputs through [`addShaderCode16BitStorageInputOutput16To16x2()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L4022-L4226), testing that a single interface location can fan out without corruption. This is the only group where the 16-bit value is not in a buffer or push constant at all.

## Shader Analysis

The page uses one representative walkthrough. The compute uniform-buffer `16_to_32` case is the simplest instance of the core mechanism: load a 16-bit member from a 16-bit-storage-capable resource, convert it, store the wide result. The push-constant and input/output-interface groups reuse the same load-convert-store shape with a different storage class; their differences are covered in `#### Parameter Variation Summary`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.16bit_storage.uniform_16_to_32.uniform_buffer_block_scalar_float
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `uniform_buffer_block` capability | Selects `StorageUniformBufferBlock16` and `storageBuffer16BitAccess`; the 16-bit input is an SSBO decorated `BufferBlock`. |
| `uniform_16_to_32` direction | 16-bit float input, 32-bit float output; widening, so the host uses exact `check32BitFloats` comparison with no rounding-mode ambiguity. |
| `scalar` composite type | Input is a flat `f16 x 128` array; one compute invocation converts one element. |
| `float` data type | Conversion runs through `OpFConvert %f32 %val16`. |
| dynamic access index `x` | `OpAccessChain %f16ptr %ssbo16 %zero %x` uses `GlobalInvocationId.x`, the default dynamic-index path. |

#### Purpose

The shader widens one 16-bit float per invocation from a 16-bit-capable SSBO into a 32-bit SSBO. The arithmetic (`OpFConvert` widening) is unambiguous; the test is whether the implementation honors the `StorageUniformBufferBlock16` capability end to end: the 16-bit `ArrayStride`, the 16-bit member offset, and the 16-bit load through the `Uniform` storage class.

#### Structural Design

| Phase | What happens | Why it matters for the tested property |
|-------|--------------|----------------------------------------|
| Capability + extension | `OpCapability StorageUniformBufferBlock16` + `OpExtension "SPV_KHR_16bit_storage"`. | Gates the whole test on the feature under examination. |
| SSBO declarations | `%ssbo16` wraps `f16 x 128` (ArrayStride 2) at binding 0; `%ssbo32` wraps `f32 x 128` (ArrayStride 4) at binding 1. | The 16-bit input stride is the load-bearing decoration; the 32-bit sink is the readback target. |
| Dispatch | `LocalSize 1 1 1`, 128 work groups. | One invocation per element; invocation `x` touches only index `x`. |
| Body | `OpLoad %f16` → `OpFConvert %f32` → `OpStore` into `%ssbo32` at the same index. | The load-convert-store triplet is the entire tested behavior. |

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- The host fills `%ssbo16` with 128 random `deFloat16` values and precomputes the expected `%ssbo32` content by widening each with `deFloat16To32`; the dispatch runs 128 work groups of size `(1,1,1)` ([composite-data setup](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1275-L1283)).
- The `verifyIO` callback for this case is [`check32BitFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L341-L362), an exact `float` comparison; widening has no rounding ambiguity, so no rounding mode is parameterized.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Capability (`uniform` vs `uniform_buffer_block`) | Swaps `OpCapability StorageUniform16` for `StorageUniformBufferBlock16`, decorates `%ssbo16` as `Block` instead of `BufferBlock`, and binds the input as `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER`. | [`CAPABILITIES table`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L126-L129) |
| Composite type `vector` | Replaces `%f16`/`%f32` with `%v2f16`/`%v2f32`, doubles the `ArrayStride`, halves the workgroup count, and uses the `v2f16ptr`/`v2f32ptr` access chains. | [`cTypes` float table](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1228-L1250) |
| Composite type `matrix` | Adds `%m4v2f16`/`%m4v2f32` with `ColMajor`/`MatrixStride` decorations and a `matrix_store` block that writes three extra columns per invocation. | [`matrix_store` spec](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1294-L1322) |
| Access index `scalar_const_idx_5`/`_8` | Replaces `%x` with `%c_i32_ci` in the input `OpAccessChain`, and the host precomputes the expected buffer by indexing the input at the constant. | [`useConstantIndex` branch](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1267-L1270) |
| Direction `32_to_16` / `64_to_16` | Reverses source and sink: the wide buffer becomes input, the 16-bit buffer becomes output, and float-narrowing variants specialize `FPRoundingMode RTE or RTZ` (or omit it for `unspecified_rnd_mode`). | [`addCompute16bitStorageUniform32To16Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L2324-L2601) |
| Push-constant storage class | Replaces `%ssbo16` with `%pc16 = OpVariable %pp_PC16 PushConstant` and binds the input as a push constant range; the output SSBO stays. | [`addCompute16bitStoragePushConstant16To32Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1703-L2000) |
| Graphics I/O interface | Removes the input buffer entirely; the 16-bit value enters as a stage input and leaves as a stage output through `passthruFragments()` + `createTestsForAllStages`. | [`addGraphics16BitStorageInputOutputFloat32To16Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3637-L3804) |
| Integer data type | Swaps `OpFConvert` for `OpSConvert`/`OpUConvert` and uses `i16`/`u16` types; the host sign-extends signed results during expected-buffer precomputation. | [`cTypes` integer table](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1391-L1427) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 46
; Schema: 0
               OpCapability Shader
               OpCapability StorageBuffer16BitAccess
               OpExtension "SPV_KHR_16bit_storage"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %1 "main" %gl_GlobalInvocationID
               OpExecutionMode %1 LocalSize 1 1 1
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_arr_float_int_128 ArrayStride 4
               OpDecorate %_arr_half_int_128 ArrayStride 2
               OpMemberDecorate %_struct_5 0 Offset 0
               OpMemberDecorate %_struct_6 0 Offset 0
               OpDecorate %_struct_5 BufferBlock
               OpDecorate %_struct_6 BufferBlock
               OpDecorate %7 DescriptorSet 0
               OpDecorate %8 DescriptorSet 0
               OpDecorate %7 Binding 1
               OpDecorate %8 Binding 0
       %bool = OpTypeBool
       %void = OpTypeVoid
         %11 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
      %float = OpTypeFloat 32
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%_ptr_Uniform_int = OpTypePointer Uniform %int
%_ptr_Uniform_float = OpTypePointer Uniform %float
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
     %int_16 = OpConstant %int 16
     %int_32 = OpConstant %int 32
     %int_64 = OpConstant %int 64
    %int_128 = OpConstant %int 128
    %int_0_0 = OpConstant %int 0
%_arr_int_int_128 = OpTypeArray %int %int_128
%_arr_float_int_128 = OpTypeArray %float %int_128
       %half = OpTypeFloat 16
%_ptr_Uniform_half = OpTypePointer Uniform %half
%_arr_half_int_128 = OpTypeArray %half %int_128
     %v2half = OpTypeVector %half 2
    %v2float = OpTypeVector %float 2
%_ptr_Uniform_v2half = OpTypePointer Uniform %v2half
%_ptr_Uniform_v2float = OpTypePointer Uniform %v2float
%_arr_v2half_int_64 = OpTypeArray %v2half %int_64
%_arr_v2float_int_64 = OpTypeArray %v2float %int_64
  %_struct_5 = OpTypeStruct %_arr_float_int_128
  %_struct_6 = OpTypeStruct %_arr_half_int_128
%_ptr_Uniform__struct_5 = OpTypePointer Uniform %_struct_5
%_ptr_Uniform__struct_6 = OpTypePointer Uniform %_struct_6
          %7 = OpVariable %_ptr_Uniform__struct_5 Uniform
          %8 = OpVariable %_ptr_Uniform__struct_6 Uniform
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
          %1 = OpFunction %void None %11
         %39 = OpLabel
         %40 = OpLoad %v3uint %gl_GlobalInvocationID
         %41 = OpCompositeExtract %uint %40 0
         %42 = OpAccessChain %_ptr_Uniform_half %8 %int_0 %41
         %43 = OpLoad %half %42
         %44 = OpFConvert %float %43
         %45 = OpAccessChain %_ptr_Uniform_float %7 %int_0 %41
               OpStore %45 %44
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host generates random input data sized to the chosen composite type: `getFloat16s`/`getFloat32s`/`getInt16s` seeded from `deStringHash(group->getName())` so the matrix is deterministic per family ([seed setup](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1131)).
- For widening cases the host precomputes the expected output by converting each input value with `deFloat16To32` (or the integer sign-extension rule); for narrowing cases the expected value is re-derived inside the `verifyIO` callback from the original wide float and the case's rounding mode, not precomputed ([narrowing checker](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L261-L284)).
- The input buffer is bound at descriptor set 0 binding 0 (or binding 1 for the wide input in narrowing cases); the output SSBO is bound at the other binding. Push-constant families bind the input as a push constant range instead. Graphics I/O families pack input through `GraphicsInterfaces::setInputOutput` and read the result from a color attachment or SSBO.
- The shared `SpvAsmComputeShaderCase` / `createTestsForAllStages` harness records the dispatch or draw, a device-to-host barrier, and the readback. The harness also runs `checkSupport`/`requestedVulkanFeatures` to enable the right `ext16BitStorage` bit (plus `shaderFloat64` for the 64-bit families, and `vertexPipelineStoresAndAtomics`/`fragmentStoresAndAtomics` for graphics uniform writes).
- The pass condition is per-element: every element of the readback buffer must match the expected value under the direction-specific callback. There is no aggregation or tolerance across the matrix; one mismatched element fails the case.
- Struct families additionally build an `info` bitmask with [`addInfo`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L364-L368) that marks which bytes are real data versus std140/std430 padding, and the comparison skips padding bytes.
- The 16-to-16 pass-through case uses [`computeCheckBuffersFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L238-L259), which compares raw `uint16_t` values and treats any two NaN encodings as equal.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `uniform_and_storage_buffer` (SSBO/UBO load or store of 16-bit members) | 16-bit member offset/stride miscalculation in the shader compiler; descriptor binding or storage-class mismatch; `OpFConvert`/`OpSConvert`/`OpUConvert` lowering bug; feature flag not actually wired to the load/store path. |
| `push_constant` | Push-constant range upload or alignment for 16-bit members; `StoragePushConstant16` capability not honored at the pipeline layout; same conversion/stride causes as above. |
| `input_output_interface` (graphics) | Stage-interface matching for 16-bit locations; `FPRoundingMode` decoration ignored on a narrowing store; 16-bit location component packing; rasterization/interpolation of 16-bit varyings. |
| All values (shared infrastructure) | Host-side expected-buffer precomputation mismatch; rounding-mode flag mismatch between shader decoration and checker; descriptor/barrier setup in the shared compute/graphics harness. |

### Cause Analysis

#### 16-bit offset and stride miscalculation

**Possible failure symptoms:** the readback matches the expected buffer at some indices but not others, or every element is shifted by a fixed offset. Struct families may fail only under one layout (std140 vs std430) or only in the mixed-layout case.

**Possible implementation causes:** the shader compiler computes a different `Offset`, `ArrayStride`, or `MatrixStride` for a 16-bit member than the host used to pack the input buffer. A likely form is falling back to a 32-bit stride for a 16-bit array (`ArrayStride 4` instead of `2`), which would make invocation `x` read the bytes the host packed for invocation `x/2`. The std140 case is prone to this: the rule rounds 16-bit members up to a 16-byte boundary, so a compiler that ignores the extension's relaxation would lay out the struct as if all members were 32-bit. Confirming a specific compiler path needs source-level investigation.

#### Conversion opcode lowering

**Possible failure symptoms:** the readback values are consistently wrong in the low bits (for `OpSConvert`/`OpUConvert` sign or zero extension) or in the mantissa/exponent (for `OpFConvert`), while the offsets appear correct.

**Possible implementation causes:** the shader compiler lowers `OpFConvert`/`OpSConvert`/`OpUConvert` incorrectly for the 16-to-32 or 32-to-16 direction. For integers, a signed `OpSConvert` that uses zero-extension instead of sign-extension would produce wrong negative values; the host precomputes signed outputs with `signExtendMask = 0xffff0000`, so a sign-extension bug shows up as every negative input mapping to a small positive output. For floats, an `OpFConvert` that rounds the wrong way on a narrowing store would be caught only by the rounding-mode-aware checker. Claiming a specific lowering bug needs source-level investigation.

#### `FPRoundingMode` decoration ignored (graphics I/O narrowing)

**Possible failure symptoms:** the `rtz` or `rte` graphics I/O narrowing case fails while the widening cases pass, and the failing value is off by one unit in the last place, the difference between RTE and RTZ.

**Possible implementation causes:** the shader decorated the narrowing store with `OpDecorate %ret0 FPRoundingMode RTZ` (or `RTE`), but the implementation applied the other rounding rule. The `unspecified_rnd_mode` case accepts either, so a failure there points somewhere else; a failure on only the explicit-mode cases points at `FPRoundingMode` handling. The same distinction is also exercised by compute and graphics uniform-buffer float-narrowing builders, which decorate `%val16`; this subsection scopes the symptom to the graphics I/O families.

#### Push-constant range and alignment

**Possible failure symptoms:** the `push_constant_16_to_*` families fail while the equivalent uniform-buffer families pass, with the readback showing zero or stale data.

**Possible implementation causes:** the pipeline layout's push-constant range does not cover the 16-bit members, or the driver uploads the range with 32-bit alignment so the 16-bit values land at the wrong offsets. The SPIR-V declares `%pc16 = OpVariable %pp_PC16 PushConstant` with `OpDecorate %PC16 Block` and `OpMemberDecorate %PC16 0 Offset 0`; a driver that ignores `StoragePushConstant16` and treats the range as 32-bit-only would read garbage or zeros.

#### Stage-interface matching for 16-bit locations (graphics I/O)

**Possible failure symptoms:** only the `input_output_*` families fail, and only when more than one stage is active (e.g., the case passes in vertex-only but fails when tessellation or geometry is inserted).

**Possible implementation causes:** the producing and consuming stages disagree on the 16-bit location's component packing, so the value read by the consumer is shifted or truncated relative to what the producer wrote. The `16_to_16x2` dual-output case is a targeted probe for this: it writes one input to two outputs, so a packing mismatch tends to corrupt the second output. The `createTestsForAllStages` harness runs each case across vert/tess/geom/frag, so a stage-specific mismatch surfaces as a failure on only some stage combinations.

#### Shared harness and expected-buffer bugs

**Possible failure symptoms:** failures are spread across all capability groups and directions, or the failure pattern does not track any SPIR-V-level distinction.

**Possible implementation causes:** the host-side expected buffer was precomputed with the wrong conversion rule (e.g., `deFloat16To32` applied to a `64_to_16` case), or the rounding-mode flag passed to `interfaces.setRoundingMode()` does not match the `FPRoundingMode` decoration in the shader. These are test-harness causes rather than driver causes; the CTS source wires them per family, so a regression here would typically fail an entire family at once. The shared compute/graphics descriptor and barrier setup is the same code path used by other `vktSpvAsm*` families, so a failure isolated to `16bit_storage` is unlikely to originate there.

## Case Pruning

### Requirement-based pruning

- Every case requires the `VK_KHR_16bit_storage` extension and the specific `ext16BitStorage` feature bit for its capability: `storageBuffer16BitAccess` (`StorageUniformBufferBlock16`), `uniformAndStorageBuffer16BitAccess` (`StorageUniform16`), `storagePushConstant16` (`StoragePushConstant16`), or `storageInputOutput16` (`StorageInputOutput16`). Devices missing the relevant feature cannot run the case ([`get16BitStorageFeatures()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L149-L160)).
- The `64_to_16` and `16_to_64` families additionally require `coreFeatures.shaderFloat64 = VK_TRUE` ([feature request](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8610-L8611)).
- Graphics uniform-buffer write cases require `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics` for the stages that write to the SSBO ([graphics uniform support](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L2161-L2167)).

### Design-based pruning

- There is no integer `matrix` composite type; the matrix case is float-only because the SPIR-V `OpTypeMatrix` is meaningful for floats in this test's conversion shape.
- The push-constant group registers only `16_to_32` and `16_to_64` (widening); there is no push-constant narrowing or struct family, because the extension's push-constant capability is exercised adequately through widening and the struct-layout questions are covered by the uniform-buffer group.
- The `input_output_int_*` families omit the `64_to_16` and `16_to_64` directions that the float I/O families include; integer 64-bit values are not part of the I/O interface matrix.
- The `uniform` and `uniform_buffer_block` capabilities are iterated together for every uniform-buffer family rather than registered as separate families; this doubles the case count per family but keeps the conversion-direction grouping clean.

## Key Takeaways

- The test is built from the four SPIR-V capabilities `VK_KHR_16bit_storage` introduces, each gated by its own feature bit and exercised through a distinct storage class (SSBO/UBO, push constant, or shader I/O). A device may pass one capability group and fail another.
- Narrowing directions (`32_to_16`, `64_to_16`) cannot use a single precomputed expected value because the spec leaves the rounding result implementation-defined without `FPRoundingMode`; the host checker re-derives the expected 16-bit value from the original wide float using the case's rounding mode. Widening directions use exact comparison.
- The struct families test layout, not arithmetic: a wrong `Offset`/`ArrayStride`/`MatrixStride` produces a misaligned read that no conversion check would catch, so they pair 16-bit and 32-bit members under std140, std430, and mixed layouts.
- The graphics I/O group is the only place 16-bit values cross a stage interface; the `16_to_16x2` variant specifically probes dual-output fan-out. `FPRoundingMode` is also decorated by the compute and graphics uniform-buffer float-narrowing variants.
- See `## Failure Meaning` for the offset/stride, conversion-lowering, `FPRoundingMode`, push-constant, and stage-interface failure points.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CAPABILITIES[]` table | [`vktSpvAsm16bitStorageTests.cpp#L126-L129`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L126-L129) | Defines the two uniform/storage capabilities iterated by every uniform-buffer family. |
| `get16BitStorageFeatures()` | [`vktSpvAsm16bitStorageTests.cpp#L149-L160`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L149-L160) | Maps capability name to the `ext16BitStorage` feature bit. |
| `ShaderTemplate` enum | [`vktSpvAsm16bitStorageTests.cpp#L83-L92`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L83-L92) | Lists the struct layout modes (std140/std430/mixed, 16-bit/32-bit). |
| `getStructSize()` | [`vktSpvAsm16bitStorageTests.cpp#L162-L182`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L162-L182) | Returns the per-layout byte count used to size the struct output buffer. |
| Compute uniform 16-to-32 builder | [`addCompute16bitStorageUniform16To32Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1128-L1504) | Representative SPIR-V `StringTemplate` and the float/int composite matrices. |
| Compute push-constant builder | [`addCompute16bitStoragePushConstant16To32Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1703-L2000) | Push-constant SPIR-V template (`%pc16`, `PushConstant` storage class). |
| Compute struct mixed-types builder | [`addCompute16bitStructMixedTypesGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3053-L3275) | Nested struct + mixed 16/32 layout with `addInfo` bitmask comparison. |
| Graphics uniform 32-to-16 builder | [`addGraphics16BitStorageUniformFloat32To16Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3277-L3635) | Graphics uniform narrowing with `createTestsForAllStages`. |
| Graphics I/O 32-to-16 builder | [`addGraphics16BitStorageInputOutputFloat32To16Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3637-L3804) | `StorageInputOutput16`, `FPRoundingMode`, `createTestsForAllStages`. |
| `16_to_16x2` builder | [`addShaderCode16BitStorageInputOutput16To16x2()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L4022-L4226) | Dual-output pass-through shader. |
| Narrowing checkers | [`computeCheck16BitFloats`/`graphicsCheck16BitFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L189-L284) | Rounding-mode-aware re-derivation of expected 16-bit values. |
| Widening checkers | [`check32BitFloats`/`check64BitFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L314-L362) | Exact comparison for unambiguous widening. |
| `computeCheckBuffersFloats` | [`vktSpvAsm16bitStorageTests.cpp#L238-L259`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L238-L259) | 16-to-16 pass-through checker with NaN-equality fallback. |
| `addInfo` | [`vktSpvAsm16bitStorageTests.cpp#L364-L368`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L364-L368) | Builds the padding-vs-data bitmask for struct comparison. |
| Registration entry points | [`create16BitStorageComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8620-L8648), [`create16BitStorageGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8650-L8701) | Map test family names to builder functions. |
