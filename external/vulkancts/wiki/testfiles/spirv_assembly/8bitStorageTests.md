## Overview

**Core question:** Does the implementation correctly load, store, and width-convert 8-bit integers across `StorageBuffer`, `Uniform`, and `PushConstant` storage classes when one of the three `VK_KHR_8bit_storage` capabilities is advertised?

- This page covers the `spirv_assembly.instruction.compute.8bit_storage` and `spirv_assembly.instruction.graphics.8bit_storage` test families registered by [`create8BitStorageComputeGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5087-L5117) and [`create8BitStorageGraphicsGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5119-L5146) in [`vktSpvAsm8bitStorageTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp).
- The C++ source builds SPIR-V assembly shader text directly in `tcu::StringTemplate` per case, specializing a small set of `${capability}`, `${stride}`, `${types}`, `${base32}`, `${base8}`, `${convert}` slots.
- The source registers ten compute and nine graphics direct-child families. Their generators select concrete type, layout, constant-index, and stage variants; the registered children are not an exhaustive Cartesian product of every storage class, conversion direction, and composite type.
- The page explains the capability matrix, the per-case SPIR-V template structure, the host-side verifiers, what a failure of each family means, and which design choices prune the matrix.

## Background Knowledge

- **`VK_KHR_8bit_storage` SPIR-V capabilities.** The extension exposes three orthogonal capabilities, each gating a different storage class: `StorageBuffer8BitAccess` (gates 8-bit loads/stores in `StorageBuffer`, matches the `storageBuffer8BitAccess` Vulkan feature); `UniformAndStorageBuffer8BitAccess` (gates 8-bit loads/stores in both `Uniform` and `StorageBuffer`, matches `uniformAndStorageBuffer8BitAccess`); `StoragePushConstant8` (gates 8-bit loads from `PushConstant`, matches `storagePushConstant8`). Each case enables exactly one of the three feature flags through [`get8BitStorageFeatures`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L140-L153), so a single case exercises exactly one capability gate.
- **`OpSConvert` and `OpUConvert`.** SPIR-V's width-conversion opcodes change the bit width of a scalar or vector of integers without changing its storage location. `OpSConvert` sign-extends; `OpUConvert` zero-extends. They are the only conversion opcodes exercised here; the data is loaded in one width, converted in registers, and stored back in another width.
- **std140 vs std430 layout for 8-bit members.** The struct-conversion branches exercise layout rules for 8-bit members under both std140 (the `Uniform` storage class default) and std430 (the `StorageBuffer` storage class default). std140 rounds array strides and struct offsets up to a multiple of 16 bytes for any 8-bit vector or scalar; std430 permits tighter strides (1, 2, or 4 bytes depending on vector width). The two layouts share data fields but differ in padding. The `info8bitStd140`/`info8bitStd430`/`infoMixStd140`/`infoMixStd430` bitmasks record which bytes hold data vs padding so the host-side comparator can compare only data bytes.
- **`arrayStrideInBytesUniform = 16`.** The std140 minimum array stride for any element in a `Uniform` buffer is 16 bytes. This constant forces the input buffer to be 16× larger than the actual 8-bit data in uniform-buffer cases; the host comparator steps by 16 bytes per element and skips the padding. See [vktSpvAsm8bitStorageTests.cpp#L80](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L80).

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.8bit_storage
├── storagebuffer_32_to_8
├── uniform_8_to_32
├── push_constant_8_to_32
├── storagebuffer_16_to_8
├── uniform_8_to_16
├── push_constant_8_to_16
├── uniform_8_to_8
├── uniform_8struct_to_32struct
├── storagebuffer_32struct_to_8struct
└── struct_mixed_types

spirv_assembly.instruction.graphics.8bit_storage
├── storagebuffer_int_32_to_8
├── uniform_int_8_to_32
├── push_constant_int_8_to_32
├── storagebuffer_int_16_to_8
├── uniform_int_8_to_16
├── push_constant_int_8_to_16
├── 8struct_to_32struct
├── 32struct_to_8struct
└── struct_mixed_types
```

The compute and graphics families share their conceptual structure but use different child names. Graphics child names carry an `_int_` infix on the scalar/vector conversion families (e.g., `storagebuffer_int_32_to_8` vs `storagebuffer_32_to_8`) and drop the `_int_` infix on the struct families. Each graphics case expands to `{vert, tesc, tese, geom, frag}` leaves via `createTestsForAllStages`. The compute mustpass leaves are at [spirv-assembly.txt#L740-L770](../../../mustpass/main/vk-default/spirv-assembly.txt#L740-L770); the graphics leaves span [spirv-assembly.txt#L22474-L22883](../../../mustpass/main/vk-default/spirv-assembly.txt#L22474-L22883).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Capability | `storage_buffer`, `uniform`, `push_constant` | SPIR-V capability controlling buffer access mode and the matching `ext8BitStorage` feature flag. Selects `StorageBuffer8BitAccess`, `UniformAndStorageBuffer8BitAccess`, or `StoragePushConstant8`. | [CAPABILITIES array](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L111-L114), [get8BitStorageFeatures](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L140-L153) |
| Conversion direction | `32_to_8`, `8_to_32`, `16_to_8`, `8_to_16`, `8_to_8`, `8struct_to_32struct`, `32struct_to_8struct`, `mixed_types` | Selects which `OpSConvert`/`OpUConvert` direction is exercised, or whether struct↔struct conversion is the focus. | [addCompute8bitStorage32To8Group](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L928-L1084) and siblings |
| CompositeType | `scalar_sint`, `scalar_uint`, `vector_sint`, `vector_uint` | Data type variant for scalar/vector conversion cases. Selects `OpSConvert`/`OpUConvert` and the scalar vs `v2i*`/`v4i*` type. | [CompositeType cTypes](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1042-L1051) |
| ShaderTemplate | `STRIDE8BIT_STD140`, `STRIDE32BIT_STD140`, `STRIDEMIX_STD140`, `STRIDE8BIT_STD430`, `STRIDE32BIT_STD430`, `STRIDEMIX_STD430` | Layout/packing mode for the struct tests. Six combinations of {8-bit, 32-bit, mixed} members × {std140, std430} layout. | [getStructShaderComponet](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L738-L892), [getStructSize](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L118-L138) |
| Pipeline stage | compute / `vert` / `tesc` / `tese` / `geom` / `frag` | Pipeline stage under test. Compute cases dispatch a compute shader; graphics cases build one pipeline per stage in `{vert, tesc, tese, geom, frag}`. | [createTestsForAllStages invocation](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5080-L5081) |

## Behavior Parameters

The primary behavioral axis is the combination of capability and conversion direction. Each registered test family under `8bit_storage` selects one capability and one conversion direction; together they fix the SPIR-V capability, the storage class of the input buffer, the `OpSConvert`/`OpUConvert` opcode, and the host-side verifier.

### `storagebuffer_32_to_8` / `storagebuffer_int_32_to_8`: 32-bit to 8-bit narrowing in `StorageBuffer`

Tests narrowing of 32-bit integers to 8-bit integers in a `StorageBuffer` under the `StorageBuffer8BitAccess` capability. The shader loads `i32`/`u32` (or `v2i32`/`v2u32` for the vector variants) from a `StorageBuffer` input, applies `OpSConvert`/`OpUConvert` to produce `i8`/`u8`, and stores the result into a second `StorageBuffer`. Host-side [`computeCheckBuffers`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L155-L161) compares the original input bytes against the device output allocation. Compute group registered at [`addCompute8bitStorage32To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L928-L1084); graphics group at [`addGraphics8BitStorageUniformInt32To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L2663-L2873).

### `uniform_8_to_32` / `uniform_int_8_to_32`: 8-bit to 32-bit widening from `Uniform`

Tests widening of 8-bit integers loaded from a `Uniform` buffer to 32-bit integers in a `StorageBuffer` under the `UniformAndStorageBuffer8BitAccess` capability. The shader uses `OpSConvert`/`OpUConvert` to widen the loaded `i8`/`u8` to `i32`/`u32`. Host-side [`checkUniformsArray`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L672-L703) skips the 16-byte std140 stride padding when comparing. Compute group at [`addCompute8bitUniform8To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1086-L1200); graphics group at [`addGraphics8BitStorageUniformInt8To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L2875-L3137).

### `push_constant_8_to_32` / `push_constant_int_8_to_32`: 8-bit push constant to 32-bit

Tests loading 8-bit values from a `PushConstant` buffer and converting them to 32-bit under the `StoragePushConstant8` capability. The host computes expected `int32_t` outputs by `0xffff0000` sign-extension of the high bit; a mismatch between host and device on sign extension is the typical failure mode. Compute group at [`addCompute8bitStoragePushConstant8To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1243-L1403); graphics group at [`addGraphics8BitStoragePushConstantInt8To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L3139-L3458).

### `storagebuffer_16_to_8` / `storagebuffer_int_16_to_8`: 16-bit to 8-bit narrowing

Tests narrowing of 16-bit integers to 8-bit integers in a `StorageBuffer`. Requires both `StorageBuffer8BitAccess` and `StorageUniform16` capabilities (and the matching `VK_KHR_16bit_storage` extension). Compute group at [`addCompute8bitStorage16To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1405-L1560); graphics group at [`addGraphics8BitStorageUniformInt16To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L3460-L3681).

### `uniform_8_to_16` / `uniform_int_8_to_16`: 8-bit to 16-bit widening from `Uniform`

Tests widening of 8-bit integers loaded from a `Uniform` buffer to 16-bit integers. Requires `UniformAndStorageBuffer8BitAccess` and `StorageUniform16`. Compute group at [`addCompute8bitUniform8To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1562-L1722); graphics group at [`addGraphics8BitStorageUniformInt8To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L3683-L3952).

### `push_constant_8_to_16` / `push_constant_int_8_to_16`: 8-bit push constant to 16-bit

Tests loading 8-bit values from a `PushConstant` and converting them to 16-bit. Requires `StoragePushConstant8` and `StorageUniform16`. Compute group at [`addCompute8bitStoragePushConstant8To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1724-L1889); graphics group at [`addGraphics8BitStoragePushConstantInt8To16Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L3954-L4282).

### `uniform_8_to_8`: 8-bit to 8-bit stress test

A single registered case `spirv_assembly.instruction.compute.8bit_storage.uniform_8_to_8.stress_test` exercises 8-bit pass-through in `StorageBuffer` with `Coherent`-decorated members. Each invocation writes both `data[x]` and `data[y]`, dispatching `(128, 128, 1)` workgroups; because both writers read the same input slot for a given output index, the host byte comparison checks repeated same-value stores, not whether competing values are serialized. No graphics variant. Registered at [`addCompute8bitStorageBuffer8To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1891-L1972).

### `uniform_8struct_to_32struct` / `8struct_to_32struct`: 8-bit struct to 32-bit struct

Tests loading a struct of 8-bit members from a `Uniform` or `StorageBuffer` and converting each member to 32-bit before storing into a `StorageBuffer` struct of 32-bit members. Both std140 and std430 layouts appear. Verified by [`checkStruct<int8_t, int32_t, ...>`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L654-L670) which filters bytes through the `infoXStdY` bitmasks. Compute group at [`addCompute8bitStorageUniform8StructTo32StructGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1974-L2194); graphics group at [`addGraphics8BitStorageUniformStruct8To32Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L4284-L4562).

### `storagebuffer_32struct_to_8struct` / `32struct_to_8struct`: 32-bit struct to 8-bit struct

Tests the inverse direction: loading 32-bit struct members and narrowing each to 8-bit before storing into a `StorageBuffer` struct of 8-bit members. Compute group at [`addCompute8bitStorageUniform32StructTo8StructGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L2196-L2422); graphics group at [`addGraphics8BitStorageUniformStruct32To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L4564-L4842).

### `struct_mixed_types`: mixed 8-bit and 32-bit struct layout

Tests structs containing both 8-bit and 32-bit members under std140 and std430 layouts. The input storage class toggles between `Uniform` (std140) and `StorageBuffer` (std430) based on capability; the output is always `StorageBuffer` (std430). The mixed layout uses `${InOut}` to share one decoration fragment between input and output. Verified by `checkStruct<int8_t, int8_t, ...>` which uses the `infoMixStd140`/`infoMixStd430` bitmasks. Compute group at [`addCompute8bitStorage8bitStructMixedTypesGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L2424-L2661); graphics group at [`addGraphics8bitStorage8bitStructMixedTypesGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L4844-L5083).

## Shader Analysis

Each compute case shares the same SPIR-V template structure: a `StorageBuffer` block for input, a `StorageBuffer` (or `Uniform` or `PushConstant`) block for output, a `LocalSize 1 1 1` compute entry point, an `OpAccessChain` into both blocks at index `x = GlobalInvocationId.x`, an `OpLoad`, a single `OpSConvert`/`OpUConvert`, and an `OpStore`. The graphics cases wrap the same conversion logic inside a `%test_code` function that returns the parametr color and writes the converted data into an output `StorageBuffer` from whichever stage `createTestsForAllStages` builds. The walkthrough below uses the simplest compute case, `storagebuffer_32_to_8.storage_buffer_scalar_sint`, because it exposes the template structure with the least layout noise; the Parameter Variation Summary covers the rest.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.8bit_storage.storagebuffer_32_to_8.storage_buffer_scalar_sint
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| Capability `StorageBuffer8BitAccess` | Gated by `storageBuffer8BitAccess` Vulkan feature; permits 8-bit loads/stores in `StorageBuffer`. |
| `scalar_sint` composite type | Loads `i32`, narrows to `i8` with `OpSConvert`. Vector cases use `v2i32`→`v2i8` with the same opcode. |
| `numElements = 128`, `LocalSize 1 1 1` | 128 workgroups of 1 invocation each; one element per invocation. |
| Input `SSBO32` (binding 0) | 128 random `int32_t` values generated by `getInt32s(rnd, 128)`. |
| Output `SSBO8` (binding 1) | 128 `int8_t` slots, expected `static_cast<int8_t>(0xff & inputs[i])`. |
| Verifier | [`computeCheckBuffers`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L155-L161): byte-level `deMemCmp` of input bytes vs output allocation. |

#### Purpose

The shader narrows one `i32` per invocation to `i8` using `OpSConvert`, copying `SSBO32[i]` into `SSBO8[i]`. The host then compares the byte representation of the original input against the device-written output; the case passes only when every byte matches.

#### Structural Design

```mermaid
flowchart TD
    A[Host: 128 random int32 inputs] --> B[Bind SSBO32 set 0 binding 0<br/>SSBO8 set 0 binding 1]
    B --> C[Dispatch 128 1 1<br/>= 128 invocations]
    C --> D[i = GlobalInvocationId.x]
    D --> E[val32 = OpLoad i32 from SSBO32[i]]
    E --> F[val8 = OpSConvert i8 val32]
    F --> G[OpStore SSBO8[i] = val8]
    G --> H[Host: deMemCmp input bytes<br/>vs output allocation]
```

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- **Capability and feature binding.** `OpCapability StorageBuffer8BitAccess` is the SPIR-V side of the `storageBuffer8BitAccess` Vulkan feature. The host sets this feature through [`get8BitStorageFeatures("storage_buffer")`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L140-L153) and the test framework skips the case when the device does not advertise it.
- **Storage class.** The shader uses `StorageBuffer` for both input and output, which requires `OpExtension "SPV_KHR_storage_buffer_storage_class"` on Vulkan 1.0 (the extension is core in Vulkan 1.1+).
- **Array strides.** `i32arr ArrayStride 4` and `i8arr ArrayStride 1` are the natural strides for 4-byte and 1-byte elements. The `uniform_*` cases use `ArrayStride 16` on the 8-bit array because std140 forces a 16-byte minimum stride on any `Uniform` member.
- **Unused vector types.** The `sintTypes` string declares `v2i8`, `v4i8`, `v2i32`, `v4i32` and their arrays even though the `scalar_sint` case only uses `i8`, `i32`, and their pointers. This is a side effect of sharing one `types` slot across the four composite-type cases in the same `cTypes` group. The unused declarations are harmless and the validator does not flag them.

#### Parameter Variation Summary

The other three composite-type variants in [`addCompute8bitStorage32To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1042-L1051) reuse the same SPIR-V template with different slot values:

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Signedness (`scalar_sint` → `scalar_uint`) | Replaces signed `i32`/`i8` types with unsigned `u32`/`u8` types and changes `OpSConvert` to `OpUConvert`; scalar array strides remain 4 bytes and 1 byte. | [`cTypes` scalar rows](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1042-L1046) |
| Composite width (`scalar_sint` → `vector_sint`) | Replaces scalar `i32`/`i8` operands with two-component `v2i32`/`v2i8` operands, changes array strides from 4/1 bytes to 8/2 bytes, and halves the workgroup count so each invocation converts two values. | [`cTypes` signed scalar/vector rows](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1042-L1048), [`spec.numWorkGroups`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1072-L1073) |
| Signedness plus composite width (`scalar_sint` → `vector_uint`) | Uses unsigned two-component `v2u32`/`v2u8` operands with `OpUConvert`, 8-byte/2-byte array strides, and half as many workgroups as the scalar case. | [`cTypes` scalar/vector rows](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1042-L1050), [`spec.numWorkGroups`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1072-L1073) |

The vector cases dispatch `(64, 1, 1)` workgroups because each invocation handles one `v2i*` element (two `i32` values). The `uniform_8_to_32` family swaps the binding order (`ssbo8` becomes the `Uniform` input at binding 0, `ssbo32` becomes the `StorageBuffer` output at binding 1) and uses `OpTypePointer Uniform` for the 8-bit pointers, but the load-convert-store skeleton is identical. The `push_constant_8_to_32` family replaces the `Uniform` input with a `PushConstant` variable and uses `OpTypePointer PushConstant` for the 8-bit pointer. The struct families replace the bare array block with `OpTypeStruct %i8StructArr7` (or its 32-bit or mixed counterpart) and use `getStructShaderComponet` to emit the appropriate `OpMemberDecorate … Offset` and `OpDecorate … ArrayStride` lines for the chosen std140/std430 × 8/32/mixed variant. The mixed-struct cases additionally use [`beginLoop`/`endLoop`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L899-L926) to iterate the inner `v2b8[11]` and `b32[11]` nested arrays with a runtime index, since the struct layout has 11 nested elements per outer struct.

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
               OpCapability StorageBuffer8BitAccess
               OpExtension "SPV_KHR_storage_buffer_storage_class"
               OpExtension "SPV_KHR_8bit_storage"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %1 "main" %gl_GlobalInvocationID
               OpExecutionMode %1 LocalSize 1 1 1
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_arr_int_int_128 ArrayStride 4
               OpDecorate %_arr_char_int_128 ArrayStride 1
               OpDecorate %_struct_5 Block
               OpDecorate %_struct_6 Block
               OpMemberDecorate %_struct_5 0 Offset 0
               OpMemberDecorate %_struct_6 0 Offset 0
               OpDecorate %7 DescriptorSet 0
               OpDecorate %8 DescriptorSet 0
               OpDecorate %7 Binding 0
               OpDecorate %8 Binding 1
       %bool = OpTypeBool
       %void = OpTypeVoid
         %11 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
      %float = OpTypeFloat 32
     %v3uint = OpTypeVector %uint 3
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%_ptr_StorageBuffer_int = OpTypePointer StorageBuffer %int
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
     %int_16 = OpConstant %int 16
     %int_32 = OpConstant %int 32
     %int_64 = OpConstant %int 64
    %int_128 = OpConstant %int 128
%_arr_int_int_128 = OpTypeArray %int %int_128
%_arr_float_int_128 = OpTypeArray %float %int_128
       %char = OpTypeInt 8 1
%_ptr_StorageBuffer_char = OpTypePointer StorageBuffer %char
%_arr_char_int_128 = OpTypeArray %char %int_128
     %v2char = OpTypeVector %char 2
     %v4char = OpTypeVector %char 4
      %v2int = OpTypeVector %int 2
      %v4int = OpTypeVector %int 4
%_ptr_StorageBuffer_v2char = OpTypePointer StorageBuffer %v2char
%_ptr_StorageBuffer_v2int = OpTypePointer StorageBuffer %v2int
%_arr_v2char_int_64 = OpTypeArray %v2char %int_64
%_arr_v2int_int_64 = OpTypeArray %v2int %int_64
  %_struct_5 = OpTypeStruct %_arr_int_int_128
  %_struct_6 = OpTypeStruct %_arr_char_int_128
%_ptr_StorageBuffer__struct_5 = OpTypePointer StorageBuffer %_struct_5
%_ptr_StorageBuffer__struct_6 = OpTypePointer StorageBuffer %_struct_6
          %7 = OpVariable %_ptr_StorageBuffer__struct_5 StorageBuffer
          %8 = OpVariable %_ptr_StorageBuffer__struct_6 StorageBuffer
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
          %1 = OpFunction %void None %11
         %39 = OpLabel
         %40 = OpLoad %v3uint %gl_GlobalInvocationID
         %41 = OpCompositeExtract %uint %40 0
         %42 = OpAccessChain %_ptr_StorageBuffer_int %7 %int_0 %41
         %43 = OpLoad %int %42
         %44 = OpSConvert %char %43
         %45 = OpAccessChain %_ptr_StorageBuffer_char %8 %int_0 %41
               OpStore %45 %44
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Host-side data generation.** Each compute case seeds a `de::Random` with `deStringHash(group->getName())` so input data is deterministic per family. Scalar/vector cases generate 128 (or 64 for vector) random `int32_t` inputs; the expected `int8_t` outputs are computed by truncation (`0xff & inputs[i]`) for `storagebuffer_32_to_8` and by `0xffff0000` sign-extension for `push_constant_8_to_32`. Struct cases call `data8bit(SHADERTEMPLATE_…)` or `data32bit(...)` to generate `getStructSize(...)` bytes of random data plus the matching `infoXStdY` bitmask.
- **Buffer binding.** Input and output buffers are pushed onto `spec.inputs` and `spec.outputs` with the matching `VkDescriptorType` (`VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` or `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER`). Push-constant cases attach the input to `spec.pushConstants`. Graphics cases attach a `GraphicsResources` struct and let `createTestsForAllStages` build the per-stage pipeline.
- **Dispatch / draw.** Compute cases dispatch `(N, 1, 1)` workgroups where `N` is the element count (or `N/2` for vector cases, or `(structArraySize, nestedArraySize, 1) = (7, 11, 1)` for the mixed-struct case). Graphics cases issue one draw per stage; the test function returns the parameter color so the framebuffer matches `defaultColors` when no error has corrupted state.
- **Result readback.** The framework copies the output allocation back to host-visible memory after the dispatch or draw completes.
- **Verification.** The case-specific `spec.verifyIO` callback scans the readback:
  - `computeCheckBuffers` for the simple narrowing cases (byte-level `deMemCmp` of original input vs output allocation).
  - `checkUniformsArray<originType, resultType, compositCount>` for the uniform-buffer cases (skips std140 stride padding).
  - `checkUniformsArrayConstNdx<…, ndxConts>` for cases that index a fixed slot inside each 16-byte stride.
  - `checkStruct<originType, resultType, funcOrigin, funcResult>` for the struct↔struct and mixed-struct cases (filters bytes through `infoXStdY` bitmasks before comparing as `int8_t`).
- **Pass/fail.** Each case reports its own pass/fail; there is no aggregation across cases or across stages. A graphics case that runs in five stages produces five independent pass/fail results.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `storagebuffer_32_to_8` / `storagebuffer_int_32_to_8` | Wrong `OpSConvert`/`OpUConvert` narrowing in `StorageBuffer`; wrong `StorageBuffer8BitAccess` capability advertisement; wrong `ArrayStride 1` on the 8-bit array. |
| `uniform_8_to_32` / `uniform_int_8_to_32` | Wrong 8-bit load from `Uniform` storage; wrong `UniformAndStorageBuffer8BitAccess` capability; std140 stride mishandled (host comparator expected to skip 16-byte slots). |
| `push_constant_8_to_32` / `push_constant_int_8_to_32` | Wrong 8-bit load from `PushConstant`; wrong `StoragePushConstant8` capability; sign-extension mismatch between host expectation and device `OpSConvert`. |
| `storagebuffer_16_to_8` / `uniform_8_to_16` / `push_constant_8_to_16` | Wrong 16↔8 width conversion; missing `StorageUniform16` capability in addition to the 8-bit capability; sign/zero extension disagreement between host and device. |
| `uniform_8_to_8` | Wrong 8-bit→8-bit pass-through in `StorageBuffer` with `Coherent` decoration; race between `OpStore` to `%x` and `OpStore` to `%y` slots when workgroup size is `(128, 128, 1)`. |
| `uniform_8struct_to_32struct` / `storagebuffer_32struct_to_8struct` / `8struct_to_32struct` / `32struct_to_8struct` | Wrong struct member offset under std140 or std430; wrong `ArrayStride` on nested arrays; wrong sign-extension when converting each member. |
| `struct_mixed_types` | Wrong layout when 8-bit and 32-bit members share one struct under std140 or std430; wrong nested-struct stride; wrong per-data-byte extraction by `checkStruct`. |
| Graphics-only `*_int_*` variants | Wrong `vertexPipelineStoresAndAtomics` / `fragmentStoresAndAtomics` feature handling; conversion or store lowered incorrectly in the vertex or fragment stage. |

### Cause Analysis

#### Wrong `OpSConvert`/`OpUConvert` narrowing or widening

**Possible failure symptoms:** `computeCheckBuffers` reports a `deMemCmp` mismatch between the host-held input bytes and the device-written output allocation. For narrowing cases, the mismatch appears as wrong low-byte values (the high bytes are correct because they were never written). For widening cases, the output `i32`/`i32` slot shows a wrong sign-extended value (e.g., `0xffffff80` instead of `0x00000080` for an unsigned widening of `0x80`).

**Possible implementation causes:** `OpSConvert` and `OpUConvert` are scalar/vector width converters that must sign-extend or zero-extend respectively. A driver that lowers them through a generic truncation path without honoring the signedness operand, or that miscomputes the target width, would produce this symptom. The SPIR-V spec defines these opcodes as bitcast-free width changes, so any value transformation beyond width change is a bug. Pinpointing the exact cause requires source-level investigation of the driver's `OpSConvert`/`OpUConvert` lowering.

#### Wrong 8-bit storage class handling

**Possible failure symptoms:** The case fails during pipeline construction with a validation error, or it runs but produces zero outputs (the output `StorageBuffer` is never written). For push-constant cases, the output values are all zero, suggesting the 8-bit push-constant load returned zero.

**Possible implementation causes:** Each of the three capabilities (`StorageBuffer8BitAccess`, `UniformAndStorageBuffer8BitAccess`, `StoragePushConstant8`) gates a different storage class. If the implementation advertises the feature but does not support 8-bit loads/stores in that storage class, the load or store silently produces zero or fails validation. The host sets the matching `ext8BitStorage` flag through [`get8BitStorageFeatures`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L140-L153); if the device's feature query is inconsistent with its actual shader support, the case reaches execution and fails. Pinpointing the exact cause requires source-level investigation of the driver's 8-bit storage class support.

#### Wrong std140/std430 layout for struct members

**Possible failure symptoms:** `checkStruct` reports that the data bytes match but the offsets do not. The comparator walks both buffers with the `infoXStdY` bitmask and finds the data at wrong byte positions in the device output. The symptom is unique to the struct↔struct and mixed-struct cases.

**Possible implementation causes:** SPIR-V's `OpMemberDecorate … Offset` and `OpDecorate … ArrayStride` are authoritative for `Uniform` and `StorageBuffer` layouts. A driver that uses its own layout rules instead of the decorated offsets (e.g., always applying std430 even when the storage class is `Uniform`) would place members at the wrong bytes. The std140 cases are the most sensitive because the 8-bit array stride is forced to 16 bytes; a driver that uses the natural 1-byte stride would pack data densely and fail the byte-level comparison. Pinpointing the exact cause requires source-level investigation of the driver's layout handling.

#### Wrong push-constant sign extension

**Possible failure symptoms:** Only `push_constant_8_to_32` (or its graphics variant) fails, and the failing `int32_t` slots differ from the host expectation exactly where the input `int8_t` had its high bit set. The unsigned widening cases (`push_constant_8_to_32.scalar_uint`) pass, but the signed ones (`scalar_sint`) fail.

**Possible implementation causes:** The host computes expected `int32_t` outputs by `0xffff0000` sign-extension of the high bit at [vktSpvAsm8bitStorageTests.cpp#L1367-L1374](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1367-L1374). If the device's `OpSConvert` zero-extends instead of sign-extending, the high 24 bits will be `0x00` instead of `0xff` for negative inputs. This is a specific instance of the wrong-`OpSConvert` cause above, but isolated to the push-constant path because the storage-buffer cases use the host's truncation rule which is symmetric with sign or zero extension.

#### Wrong coherence for `uniform_8_to_8.stress_test`

**Possible failure symptoms:** The `stress_test` case reports a byte mismatch in the output allocation. Its repeated writes target the same value for each output index, so this result does not by itself establish a race-ordering failure or distinguish a coherence defect from a lost or corrupted store.

**Possible implementation causes:** The test declares `OpMemberDecorate %SSBO_IN 0 Coherent` and `OpMemberDecorate %SSBO_OUT 0 Coherent` and dispatches `(128, 128, 1)` workgroups, so each output slot is written twice, once through each global-ID component. Both writes load the same input slot and store the same value. A mismatch can indicate incorrect 8-bit load/store handling or a failure to make a repeated coherent store visible, but this test cannot prove that competing writes were improperly ordered. Pinpointing the exact cause requires source-level investigation of the driver's `Coherent` decoration and 8-bit access handling.

#### Graphics-only stage handling

**Possible failure symptoms:** The compute variant of a family passes, but one or more graphics stages (typically `vert` or `frag`) fail with the same data mismatch. The compute-style SSBO output is wrong only for the failing stages.

**Possible implementation causes:** Graphics cases enable both `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics` core features at [vktSpvAsm8bitStorageTests.cpp#L5076-L5078](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5076-L5078). If the implementation advertises these features but does not support 8-bit stores from the vertex or fragment stage, the store is dropped or corrupted. The tessellation and geometry stages inherit the vertex-pipeline feature, so a vertex-pipeline bug would affect `vert`, `tesc`, `tese`, and `geom` together while `frag` passes. Pinpointing the exact cause requires source-level investigation of the driver's per-stage 8-bit store support.

## Case Pruning

### Requirement-based pruning

- **`VK_KHR_8bit_storage` extension.** All cases advertise this extension through `spec.extensions` and the matching `ext8BitStorage` feature through `spec.requestedVulkanFeatures`. The framework skips cases whose advertised feature is unsupported.
- **`VK_KHR_storage_buffer_storage_class` extension.** The shaders declare `SPV_KHR_storage_buffer_storage_class` because they use the `StorageBuffer` storage class. Compute cases add the matching Vulkan extension to `spec.extensions`; graphics generators declare the SPIR-V extension in their fragments but add only `VK_KHR_8bit_storage` to their host extension list.
- **`VK_KHR_16bit_storage` extension and `StorageUniform16` capability.** Required only by the 16↔8 conversion families; the shader declares the additional capability and the host sets the matching `ext16BitStorage` flag.
- **`vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics` core features.** Required only by the graphics families, because the graphics shader stages need store/atomic support to write the converted values into the output `StorageBuffer`. The host enables both features at [vktSpvAsm8bitStorageTests.cpp#L5077-L5078](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5077-L5078).
- **Vulkan SC coverage.** These groups are registered without a `CTS_USES_VULKANSC` guard, and `vksc-default/spirv-assembly.txt` contains the same 439 `8bit_storage` leaves as the default mustpass list. They are not pruned from Vulkan SC.

### Design-based pruning

- **No matrix multiplication variants exercised.** The `${matrix_decor:opt}`, `${matrix_types:opt}`, `${matrix_prefix:opt}`, `${matrix_store:opt}`, and `${index0:opt}` slots are present in the SPIR-V template but expand to empty for the scalar/vector conversion cases. The matrix variants exist as commented-out code paths in the source but are not registered as test cases; the test family's design focuses on scalar/vector width conversion plus struct layout, not matrix arithmetic.
- **No 64-bit variant.** The test family does not exercise 64-bit↔8-bit conversion. That direction is out of scope for `VK_KHR_8bit_storage` (which only adds 8-bit storage, not 64-bit operations).
- **No float variant.** The `f32` and `fvec3` types are declared in the shared template but never used by any registered case; they are leftover scaffolding from the matrix variant. The test family focuses on integer storage and conversion.
- **`uniform_8_to_8` is a single repeated-store case.** The family registers one leaf (`stress_test`) rather than the four composite-type leaves used by the other conversion families. It exercises 8-bit pass-through with repeated same-value `Coherent` stores; its oracle does not independently validate atomic ordering between different values.

## Key Takeaways

- The `8bit_storage` test family is a capability matrix: three SPIR-V capabilities (`StorageBuffer8BitAccess`, `UniformAndStorageBuffer8BitAccess`, `StoragePushConstant8`) × multiple conversion directions (32↔8, 16↔8, 8↔8, struct↔struct, mixed struct), each gated by the matching `ext8BitStorage` feature flag.
- Every compute case shares the same SPIR-V template skeleton (load from input, `OpSConvert`/`OpUConvert`, store to output) and varies only the storage class, types, and conversion opcode. The struct cases add `OpMemberDecorate`/`OpDecorate ArrayStride` lines from `getStructShaderComponet` and use `beginLoop`/`endLoop` to iterate nested arrays.
- The host-side verifier scales with the case: `computeCheckBuffers` for the simple cases, `checkUniformsArray` for std140-padded uniform cases, `checkStruct` for struct cases (filtering bytes through `infoXStdY` bitmasks).
- Graphics cases reuse the compute SPIR-V logic but wrap it in a `testfun` fragment and expand one case into `{vert, tesc, tese, geom, frag}` leaves via `createTestsForAllStages`. They additionally require `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`.
- See `## Failure Meaning` for the failure interpretation: a wrong-narrowing symptom points to `OpSConvert`/`OpUConvert` lowering; a wrong-struct-offset symptom points to std140/std430 layout handling; a graphics-only failure points to per-stage store support; a `stress_test` mismatch is limited to repeated same-value coherent-store/pass-through observability and does not prove a race-ordering defect.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Compute factory `create8BitStorageComputeGroup` | [vktSpvAsm8bitStorageTests.cpp#L5087-L5117](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5087-L5117) | Registers the 10 compute children under `8bit_storage`. |
| Graphics factory `create8BitStorageGraphicsGroup` | [vktSpvAsm8bitStorageTests.cpp#L5119-L5146](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5119-L5146) | Registers the 9 graphics children under `8bit_storage`. |
| Capability table `CAPABILITIES[]` | [vktSpvAsm8bitStorageTests.cpp#L111-L114](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L111-L114) | Maps `storage_buffer`/`uniform` to SPIR-V capability and descriptor type. |
| Feature gate helper `get8BitStorageFeatures` | [vktSpvAsm8bitStorageTests.cpp#L140-L153](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L140-L153) | Translates a capability name into a `VulkanFeatures.ext8BitStorage` flag. |
| Compute buffer verifier `computeCheckBuffers` | [vktSpvAsm8bitStorageTests.cpp#L155-L161](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L155-L161) | Byte-level `deMemCmp` used by simple conversion cases. |
| Uniform array verifiers `checkUniformsArray` / `checkUniformsArrayConstNdx` | [vktSpvAsm8bitStorageTests.cpp#L672-L736](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L672-L736) | Skip std140 stride padding when comparing uniform-buffer outputs. |
| Struct verifier `checkStruct` | [vktSpvAsm8bitStorageTests.cpp#L654-L670](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L654-L670) | Filters bytes through `infoXStdY` bitmasks before comparing as `int8_t`. |
| Struct size calculator `getStructSize` | [vktSpvAsm8bitStorageTests.cpp#L118-L138](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L118-L138) | Returns the byte size of each `ShaderTemplate` variant. |
| Layout decoration fragments `getStructShaderComponet` | [vktSpvAsm8bitStorageTests.cpp#L738-L892](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L738-L892) | Six `ShaderTemplate` variants encoding std140/std430 × 8/32/mixed struct layouts. |
| Loop helpers `beginLoop` / `endLoop` | [vktSpvAsm8bitStorageTests.cpp#L899-L926](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L899-L926) | Emit `OpLoopMerge` blocks for the nested-array iteration in struct cases. |
| Representative compute case `addCompute8bitStorage32To8Group` | [vktSpvAsm8bitStorageTests.cpp#L928-L1084](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L928-L1084) | Source of the SPIR-V template and 4 composite-type cases analyzed in the walkthrough. |
| Compute push-constant case `addCompute8bitStoragePushConstant8To32Group` | [vktSpvAsm8bitStorageTests.cpp#L1243-L1403](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1243-L1403) | Source of the host-side sign-extension expectation at lines 1367-1374. |
| Compute stress test `addCompute8bitStorageBuffer8To8Group` | [vktSpvAsm8bitStorageTests.cpp#L1891-L1972](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L1891-L1972) | The `uniform_8_to_8.stress_test` case with `Coherent` decorations. |
| Compute mixed-struct case `addCompute8bitStorage8bitStructMixedTypesGroup` | [vktSpvAsm8bitStorageTests.cpp#L2424-L2661](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L2424-L2661) | Uses `${InOut}` placeholder and `beginLoop`/`endLoop` for nested arrays. |
| Graphics stage expansion `createTestsForAllStages` | [vktSpvAsm8bitStorageTests.cpp#L5080-L5081](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5080-L5081) | Builds one pipeline per stage in `{vert, tesc, tese, geom, frag}`. |
| Graphics feature gates | [vktSpvAsm8bitStorageTests.cpp#L5076-L5078](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5076-L5078) | Enables `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics` for graphics cases. |
| Mustpass entry range (compute) | [spirv-assembly.txt#L740-L770](../../../mustpass/main/vk-default/spirv-assembly.txt#L740-L770) | Mirrors registered `dEQP-VK.spirv_assembly.instruction.compute.8bit_storage.*` cases. |
| Mustpass entry range (graphics) | [spirv-assembly.txt#L22474-L22883](../../../mustpass/main/vk-default/spirv-assembly.txt#L22474-L22883) | Covers all registered `dEQP-VK.spirv_assembly.instruction.graphics.8bit_storage.*` leaves. |
