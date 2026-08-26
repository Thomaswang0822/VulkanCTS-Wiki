## Overview

**Core question:** Can a compute shader receive a buffer device address through a push constant or an SSBO field, form a `PhysicalStorageBuffer` pointer from it, and dereference it with `OpLoad`/`OpStore` to copy 64 int32 elements between two buffers?

- [vktSpvAsmPhysicalStorageBufferPointerTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp) implements the `physical_storage_buffer` test family under `spirv_assembly.instruction.compute`.
- The factory ([createPhysicalStorageBufferTestGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L742-L763)) registers three test case leaves: `push_constants`, `push_constants_function`, and `addrs_in_ssbo`.
- Each case authors a SPIR-V assembly compute shader directly in a C++ string template. There is no GLSL or HLSL source; the assembly is the source of truth. The published assembly was assembled, validated, and disassembled with `spirv-as` → `spirv-val` → `spirv-dis` (see the spirv_assembly category deviation in `## Shader Analysis`).
- The core mechanism is the host producing two buffer device addresses with `vkGetBufferDeviceAddress`, handing them to the shader, and the shader dereferencing them as `PhysicalStorageBuffer` pointers. The pass criterion is a faithful element-by-element copy from a source buffer to a destination buffer.

## Background Knowledge

- **Physical storage buffer pointers.** The `PhysicalStorageBuffer` storage class holds pointers that reference device memory by 64-bit address instead of through a `VkBuffer`-backed variable. A shader can load a field declared as pointer-typed in SPIR-V, whose host-side bytes contain a device address, or convert a 64-bit unsigned integer with `OpConvertUToPtr`. Dereferences use the `Aligned` optional operand on `OpLoad`/`OpStore` to promise the access alignment. This is the SPIR-V analog of a raw device pointer in C.
- **Buffer device addresses on the host.** `VK_KHR_buffer_device_address` (core in Vulkan 1.2) exposes `vkGetBufferDeviceAddress`, which returns a 64-bit address for a buffer created with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT`. The CTS support helper accepts either `VK_KHR_buffer_device_address` or `VK_EXT_buffer_device_address`; after that gate, the host writes the returned 64-bit value into a push constant or SSBO field that the shader interprets as a `PhysicalStorageBuffer` pointer. The CTS feature gate is `bufferDeviceAddress`.
- **`OpConvertUToPtr` and `OpSelect` on pointers.** `OpConvertUToPtr` turns a 64-bit unsigned integer into a `PhysicalStorageBuffer` pointer. `OpSelect` chooses between two pointer-typed operands based on a boolean. SPIR-V 1.4 permits `OpSelect` on pointer operands. The `addrs_in_ssbo` case uses both so the same buffer address can be reached either as a pointer-typed SSBO field or as a `uint64` field converted at use time.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.physical_storage_buffer
├── push_constants
├── push_constants_function
└── addrs_in_ssbo
```

The three test case leaves are registered directly under `physical_storage_buffer` by [createPhysicalStorageBufferTestGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L742-L763). There are no intermediate nodes.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pass method | `push_constants`, `push_constants_function`, `addrs_in_ssbo` | How the two buffer device addresses are communicated to the shader. This is the primary behavioral axis and maps one-to-one to a test case leaf. | [PassMethod enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L55-L60) |
| Element count | `64` | Number of int32 elements to copy. Fixed for all three cases; not a behavioral axis. | [registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L758-L759) |
| SPIR-V target | `spirv1.4` | All three cases build with `vk::SPIRV_VERSION_1_4`; required for `OpSelect` on pointers and the physical-storage-buffer addressing model. | [build options](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L529-L530) |

## Behavior Parameters

The primary behavioral axis is the **test case leaf** (the pass method). Each leaf selects a distinct way of transporting the two buffer device addresses into the shader and a distinct dereference path.

### push_constants: addresses via push constants, inline copy loop

The host packs `{src, dst, cnt, use_fun}` into a push constant struct ([PushConstant](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L544-L550)). The shader loads the `src` and `dst` fields as `PhysicalStorageBuffer` pointers to a runtime array of int32 and, when `use_fun` is false, runs an inline loop copying `src[i]` to `dst[i]` with `OpLoad`/`OpStore Aligned 4`. Dispatch is `1×1×1`, so the single invocation copies all 64 elements. This is the baseline physical-storage-buffer dereference case.

### push_constants_function: addresses via push constants, function-call copy

This case shares the same shader as `push_constants`. The `use_fun` push-constant field is set to true ([host setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L567-L568)), so the shader takes the `OpFunctionCall %cpbuffs` branch and copies through a function whose parameters are `PhysicalStorageBuffer` pointers ([%cpbuffs](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L460-L485)). The structural difference from `push_constants` is exactly that the pointers cross a function-call boundary as `OpFunctionParameter` values.

### addrs_in_ssbo: addresses stored in an SSBO, pointer and uint representations

The host stores the two device addresses twice in an SSBO struct of four `uint64_t` members, `{srcAsBuff, srcAsUint, dstAsBuff, dstAsUint}` ([SSBO struct](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L707-L716)). SPIR-V declares members 0 and 2 as pointer-typed and members 1 and 3 as `uint64`; the shader loads the former directly and converts the latter with `OpConvertUToPtr`, then uses `OpSelect` to pick between the two representations per invocation based on `gid_x % 2`. Dispatch is `64×1×1`, so each invocation copies one element. The source comment notes the purpose is to show that `PhysicalStorageBuffer` and 64-bit integer values can coexist in one structure and the shader chooses how to interpret them ([comment](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L676-L681)).

## Shader Analysis

The shaders in this file are authored directly as SPIR-V assembly in C++ string templates; there is no GLSL or HLSL source. Under the temporary `spirv_assembly` category deviation, `#### Source Code` holds the extracted SPIR-V assembly verbatim (unfoldable), and the usual collapsed `#### SPIR-V` subsection is omitted because it would duplicate that assembly. The extracted assembly was assembled, validated, and disassembled with `spirv-as` → `spirv-val` → `spirv-dis`; the gate output is not published.

This page uses two walkthroughs. The first covers the shared push-constants shader used by `push_constants` and `push_constants_function`; it establishes the baseline physical-storage-buffer dereference and the function-call variant. The second covers the structurally different `addrs_in_ssbo` shader, which adds `OpConvertUToPtr` and `OpSelect` on pointers. `push_constants_function` does not get a separate walkthrough because it reuses the walkthrough-1 shader with a different `use_fun` push-constant value.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.physical_storage_buffer.push_constants
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `push_constants` | Two buffer device addresses are passed via a push constant struct; the shader dereferences them as `PhysicalStorageBuffer` pointers. |
| `use_fun == 0` | Takes the inline copy loop in `main`; setting `use_fun != 0` selects the `OpFunctionCall %cpbuffs` branch for the `push_constants_function` case. |
| `LocalSize 1 1 1`, dispatch `1×1×1` | One invocation copies all 64 elements via its loop. |
| `PhysicalStorageBuffer64` addressing model | Required for the `PhysicalStorageBuffer` pointer loads/stores. |
| SPIR-V 1.4 | `vk::SpirVAsmBuildOptions(..., vk::SPIRV_VERSION_1_4, true)`. |

#### Purpose

This shader checks that a `PhysicalStorageBuffer` pointer loaded from a push-constant field can be dereferenced with `OpLoad`/`OpStore Aligned 4` to copy a runtime array of int32 from source to destination, and that the same pointers can be passed as `OpFunctionParameter` values and dereferenced inside a callee.

#### Structural Design

| Step | Where | Pointers used | Expected effect |
|------|-------|---------------|-----------------|
| 1 | `main` | Load `%src` and `%dst` as `%buf_ptr` (`PhysicalStorageBuffer` pointer to `%int_arr`) from push-constant fields 0 and 1; load `%cnt` and `%use_fun` from fields 2 and 3. | The two device addresses become shader pointers. |
| 2 | `main` (branch on `%use_fun`) | `OpINotEqual %use_fun 0` selects `%copy` (function call) or `%loop` (inline loop). | `push_constants` takes `%loop`; `push_constants_function` takes `%copy`. |
| 3a | `%loop` (inline) | `OpAccessChain %int_ptr %src %vi` and `%dst %vi`, then `OpLoad Aligned 4` / `OpStore Aligned 4` for `vi` in `0..cnt-1`. | Copies all elements in the calling invocation. |
| 3b | `%cpbuffs` (function call) | `%src_buf` and `%dst_buf` are `OpFunctionParameter %buf_ptr`; the same access-chain + aligned load/store runs in the callee. | Copies all elements through pointer parameters. |

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- The push-constant layout is `{uint64_t src; uint64_t dst; int32_t cnt; bool use_fun;}` on the host ([PushConstant](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L544-L550)); the SPIR-V block matches with offsets 0, 8, 16, and 20.
- `%uzero`, `%uint_ptr`, and `%uint_fptr` are declared but unused in this shader; they are kept verbatim from the CTS template.
- The `Restrict` decoration on `%src_buf` and `%dst_buf` asserts the two pointers do not alias; the test relies on source and destination being distinct buffers.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `push_constants_function` | Same shader; the host sets `use_fun` to true, so the `OpFunctionCall %cpbuffs` branch runs and the pointers cross a function-call boundary as `OpFunctionParameter` values. | [use_fun assignment](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L567-L568) |
| `addrs_in_ssbo` | Different shader: addresses come from an SSBO, with `OpConvertUToPtr` for the uint fields and `OpSelect` between pointer and uint-converted representations. | [SSBO shader](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L588-L670) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 67
; Schema: 0
               OpCapability Shader
               OpCapability PhysicalStorageBufferAddresses
               OpExtension "SPV_KHR_physical_storage_buffer"
               OpMemoryModel PhysicalStorageBuffer64 GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %3
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %source "source"
               OpName %destination "destination"
               OpName %source_0 "source"
               OpName %destination_0 "destination"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_struct_8 Block
               OpMemberDecorate %_struct_8 0 Offset 0
               OpMemberDecorate %_struct_8 1 Offset 8
               OpMemberDecorate %_struct_8 2 Offset 16
               OpMemberDecorate %_struct_8 3 Offset 20
               OpDecorate %source_0 Restrict
               OpDecorate %destination_0 Restrict
               OpDecorate %_runtimearr_int ArrayStride 4
        %int = OpTypeInt 32 1
%_ptr_PhysicalStorageBuffer_int = OpTypePointer PhysicalStorageBuffer %int
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
       %uint = OpTypeInt 32 0
%_ptr_Input_uint = OpTypePointer Input %uint
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
     %uint_0 = OpConstant %uint 0
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_runtimearr_int = OpTypeRuntimeArray %int
%_ptr_PhysicalStorageBuffer__runtimearr_int = OpTypePointer PhysicalStorageBuffer %_runtimearr_int
  %_struct_8 = OpTypeStruct %_ptr_PhysicalStorageBuffer__runtimearr_int %_ptr_PhysicalStorageBuffer__runtimearr_int %int %int
%_ptr_PushConstant__struct_8 = OpTypePointer PushConstant %_struct_8
          %3 = OpVariable %_ptr_PushConstant__struct_8 PushConstant
%_ptr_PushConstant__ptr_PhysicalStorageBuffer__runtimearr_int = OpTypePointer PushConstant %_ptr_PhysicalStorageBuffer__runtimearr_int
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
       %bool = OpTypeBool
       %void = OpTypeVoid
         %29 = OpTypeFunction %void
         %30 = OpTypeFunction %void %_ptr_PhysicalStorageBuffer__runtimearr_int %_ptr_PhysicalStorageBuffer__runtimearr_int %int
         %31 = OpFunction %void None %30
   %source_0 = OpFunctionParameter %_ptr_PhysicalStorageBuffer__runtimearr_int
%destination_0 = OpFunctionParameter %_ptr_PhysicalStorageBuffer__runtimearr_int
         %32 = OpFunctionParameter %int
         %33 = OpLabel
         %34 = OpVariable %_ptr_Function_int Function
               OpStore %34 %int_0
               OpBranch %35
         %35 = OpLabel
         %36 = OpLoad %int %34
         %37 = OpULessThan %bool %36 %32
               OpLoopMerge %38 %39 None
               OpBranchConditional %37 %40 %38
         %40 = OpLabel
         %41 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %source_0 %36
         %42 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %destination_0 %36
         %43 = OpLoad %int %41 Aligned 4
               OpStore %42 %43 Aligned 4
               OpBranch %39
         %39 = OpLabel
         %44 = OpIAdd %int %36 %int_1
               OpStore %34 %44
               OpBranch %35
         %38 = OpLabel
               OpReturn
               OpFunctionEnd
       %main = OpFunction %void None %29
         %45 = OpLabel
         %46 = OpVariable %_ptr_Function_int Function
               OpStore %46 %int_0
         %47 = OpAccessChain %_ptr_PushConstant__ptr_PhysicalStorageBuffer__runtimearr_int %3 %int_0
         %48 = OpAccessChain %_ptr_PushConstant__ptr_PhysicalStorageBuffer__runtimearr_int %3 %int_1
         %49 = OpAccessChain %_ptr_PushConstant_int %3 %int_2
         %50 = OpAccessChain %_ptr_PushConstant_int %3 %int_3
     %source = OpLoad %_ptr_PhysicalStorageBuffer__runtimearr_int %47
%destination = OpLoad %_ptr_PhysicalStorageBuffer__runtimearr_int %48
         %51 = OpLoad %int %49
         %52 = OpLoad %int %50
         %53 = OpINotEqual %bool %52 %int_0
               OpSelectionMerge %54 None
               OpBranchConditional %53 %55 %56
         %55 = OpLabel
         %57 = OpFunctionCall %void %31 %source %destination %51
               OpBranch %54
         %56 = OpLabel
         %58 = OpLoad %int %46
         %59 = OpSLessThan %bool %58 %51
               OpLoopMerge %60 %61 None
               OpBranchConditional %59 %62 %60
         %62 = OpLabel
         %63 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %source %58
         %64 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %destination %58
         %65 = OpLoad %int %63 Aligned 4
               OpStore %64 %65 Aligned 4
               OpBranch %61
         %61 = OpLabel
         %66 = OpIAdd %int %58 %int_1
               OpStore %46 %66
               OpBranch %56
         %60 = OpLabel
               OpBranch %54
         %54 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.physical_storage_buffer.addrs_in_ssbo
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `addrs_in_ssbo` | The host writes each device address twice as `uint64_t`; SPIR-V declares one copy of each address as a pointer-typed member and the other as a `uint64` member. |
| `Int64` capability | Required because the SSBO stores the addresses as `uint64` fields; gated by `shaderInt64`. |
| `LocalSize 1 1 1`, dispatch `64×1×1` | 64 invocations; each copies one element indexed by `GlobalInvocationID.x`. |
| `gid_x % 2` selector | Alternates between pointer-typed and uint-converted address representations per invocation. |
| SPIR-V 1.4 | `vk::SpirVAsmBuildOptions(..., vk::SPIRV_VERSION_1_4, true)`. |

#### Purpose

This shader checks that a `PhysicalStorageBuffer` pointer can be obtained both by loading a pointer-typed SSBO field and by converting a `uint64` SSBO field with `OpConvertUToPtr`, and that `OpSelect` can choose between the two representations per invocation while still copying the correct element.

#### Structural Design

| `gid_x` parity | `src` selected from | `dst` selected from | Effect |
|----------------|---------------------|---------------------|--------|
| even | `%src_buff_p` (pointer-typed field) | `%dst_buff_v` (`OpConvertUToPtr` of the uint field) | Source uses pointer rep, destination uses uint rep. |
| odd | `%src_buff_v` (`OpConvertUToPtr` of the uint field) | `%dst_buff_p` (pointer-typed field) | Source uses uint rep, destination uses pointer rep. |

Both representations resolve to the same buffer address because the host fills the SSBO with the same address twice ([SSBO fill](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L714-L716)).

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- The host SSBO struct is `{uint64_t srcAsBuff; uint64_t srcAsUint; uint64_t dstAsBuff; uint64_t dstAsUint;}` ([SSBO struct](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L707-L713)), initialized with `{src, src, dst, dst}`. SPIR-V interprets members 0 and 2 as pointer-typed and members 1 and 3 as `uint64`, so each pair contains the same device-address bits under both representations.
- The `gid_x % 2` selector means even-indexed elements exercise pointer-typed source plus uint-converted destination, and odd-indexed elements exercise the opposite. A mis-handled representation produces a stable every-other-slot mismatch instead of a uniform failure.
- The `%uint_in` pointer type and `%gid_x` are 32-bit unsigned; the `%mod2`/`%even` computation uses signed `%int` constants, matching the CTS-authored assembly verbatim.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Address transport | The push-constants shader takes addresses from a push constant and has no `OpConvertUToPtr`/`OpSelect`; this shader takes them from an SSBO and selects between two representations. | [push-constants shader](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L400-L527) |
| Capability set | This shader adds `Int64`; the push-constants shader needs only `PhysicalStorageBufferAddresses`. | [capability declarations](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L589-L591) |
| Dispatch shape | This shader is dispatched `64×1×1` (one element per invocation); the push-constants shader is dispatched `1×1×1` (one invocation copies all elements). | [dispatch](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L730) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 44
; Schema: 0
               OpCapability Shader
               OpCapability Int64
               OpCapability PhysicalStorageBufferAddresses
               OpExtension "SPV_KHR_physical_storage_buffer"
               OpMemoryModel PhysicalStorageBuffer64 GLSL450
               OpEntryPoint GLCompute %1 "main" %gl_GlobalInvocationID %3
               OpExecutionMode %1 LocalSize 1 1 1
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_struct_4 Block
               OpMemberDecorate %_struct_4 0 Offset 0
               OpMemberDecorate %_struct_4 1 Offset 8
               OpMemberDecorate %_struct_4 2 Offset 16
               OpMemberDecorate %_struct_4 3 Offset 24
               OpDecorate %3 DescriptorSet 0
               OpDecorate %3 Binding 0
               OpDecorate %_runtimearr_int ArrayStride 4
       %bool = OpTypeBool
        %int = OpTypeInt 32 1
       %uint = OpTypeInt 32 0
      %ulong = OpTypeInt 64 0
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
     %v3uint = OpTypeVector %uint 3
%_runtimearr_int = OpTypeRuntimeArray %int
%_ptr_PhysicalStorageBuffer__runtimearr_int = OpTypePointer PhysicalStorageBuffer %_runtimearr_int
  %_struct_4 = OpTypeStruct %_ptr_PhysicalStorageBuffer__runtimearr_int %ulong %_ptr_PhysicalStorageBuffer__runtimearr_int %ulong
%_ptr_StorageBuffer__struct_4 = OpTypePointer StorageBuffer %_struct_4
          %3 = OpVariable %_ptr_StorageBuffer__struct_4 StorageBuffer
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__runtimearr_int = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer__runtimearr_int
%_ptr_PhysicalStorageBuffer_int = OpTypePointer PhysicalStorageBuffer %int
%_ptr_StorageBuffer_ulong = OpTypePointer StorageBuffer %ulong
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
       %void = OpTypeVoid
         %23 = OpTypeFunction %void
          %1 = OpFunction %void None %23
         %24 = OpLabel
         %25 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %int_0
         %26 = OpLoad %uint %25
         %27 = OpSMod %int %26 %int_2
         %28 = OpIEqual %bool %27 %int_0
         %29 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__runtimearr_int %3 %int_0
         %30 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer__runtimearr_int %3 %int_2
         %31 = OpLoad %_ptr_PhysicalStorageBuffer__runtimearr_int %29
         %32 = OpLoad %_ptr_PhysicalStorageBuffer__runtimearr_int %30
         %33 = OpAccessChain %_ptr_StorageBuffer_ulong %3 %int_1
         %34 = OpLoad %ulong %33
         %35 = OpConvertUToPtr %_ptr_PhysicalStorageBuffer__runtimearr_int %34
         %36 = OpAccessChain %_ptr_StorageBuffer_ulong %3 %int_3
         %37 = OpLoad %ulong %36
         %38 = OpConvertUToPtr %_ptr_PhysicalStorageBuffer__runtimearr_int %37
         %39 = OpSelect %_ptr_PhysicalStorageBuffer__runtimearr_int %28 %31 %35
         %40 = OpSelect %_ptr_PhysicalStorageBuffer__runtimearr_int %28 %38 %32
         %41 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %39 %26
         %42 = OpLoad %int %41 Aligned 4
         %43 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %40 %26
               OpStore %43 %42 Aligned 4
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Resource setup.** Each case creates two `ut::TypedBuffer<int32_t>` buffers of 64 elements with `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT | VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` ([src/dst](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L561-L562), [ssbo variant](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L704-L705)). Buffers are host-visible and coherent.
- **Initialization.** `src.iota(m_params->elements, true)` fills the source with `64, 65, ..., 127` and flushes; `dst.zero(true)` zeroes the destination and flushes ([push](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L564-L565), [ssbo](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L723-L724)).
- **Address query.** `src.getDeviceAddress()` and `dst.getDeviceAddress()` call `vkGetBufferDeviceAddress` ([getDeviceAddress](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L181-L194)).
- **Pipeline and bindings.** The push-constants cases build a pipeline layout with one push-constant range and no descriptor set; `cmdPushConstants` writes the `{src, dst, cnt, use_fun}` struct ([pipeline setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L552-L559), [push](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L572)). The `addrs_in_ssbo` case builds a single storage-buffer descriptor set and binds it ([descriptor setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L693-L721)).
- **Dispatch.** `cmdDispatch(1, 1, 1)` for the push-constants cases ([dispatch](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L573)); `cmdDispatch(m_params->elements, 1, 1)` for `addrs_in_ssbo` ([dispatch](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L730)).
- **Result comparison.** After submit and wait, the case calls `dst.invalidate()` before reading the host-visible destination allocation, then returns pass iff `std::equal(src.begin(), src.end(), dst.begin())` ([push](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L578-L580), [ssbo](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L735-L737)). The allocation was requested coherent at creation; invalidation does not make it coherent. There is no tolerance.
- **Pass/fail rule.** A case passes only when every destination element matches the corresponding source element. A mismatch establishes that this case's end-to-end copy did not produce the expected bytes; the selected address transport and physical-pointer dereference path are central candidates, but the comparison alone does not localize the fault.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `push_constants` | Push-constant transport of 64-bit device addresses broken, or `PhysicalStorageBuffer` pointer formed from a push-constant field dereferenced incorrectly (`OpAccessChain` + `OpLoad Aligned 4`/`OpStore Aligned 4`). |
| `push_constants_function` | Same as `push_constants`, plus passing `PhysicalStorageBuffer` pointers as `OpFunctionParameter` values and dereferencing them inside the callee. |
| `addrs_in_ssbo` | `OpConvertUToPtr` on a 64-bit SSBO field mis-handled, `OpSelect` between pointer-typed and uint-converted pointers mis-handled, or `Int64` capability handling for the `uint64` address fields. |

All three cases share the same final host comparison; any destination element that differs from the corresponding source element fails the case.

### Cause Analysis

#### Push-constant transport or physical-storage-buffer dereference broken

**Possible failure symptoms:** A `push_constants` case produces a destination buffer that does not match the source. The mismatch may be total (all elements wrong or zeroed) or partial (a subset of elements wrong if the loop count or indexing drifted).

**Possible implementation causes:** The host writes two 64-bit device addresses into a push constant at offsets 0 and 8, and the shader loads them as `%buf_ptr` (`OpTypePointer PhysicalStorageBuffer %int_arr`) via `OpAccessChain` into the push-constant block. A failure points at push-constant 64-bit value transport, the `PhysicalStorageBuffer64` addressing model, or `OpLoad`/`OpStore Aligned 4` on a `PhysicalStorageBuffer` pointer. The `Restrict` decoration on the two pointers asserts they do not alias; a compiler that ignored the distinct-buffer assumption could not cause a copy failure here because the test never aliases them. A cause not explained by 64-bit push-constant transport or aligned physical-storage-buffer access needs source-level investigation.

#### Physical-storage-buffer pointer function parameter handling broken

**Possible failure symptoms:** `push_constants_function` fails while `push_constants` passes. The destination buffer does not match the source, but only on the function-call path.

**Possible implementation causes:** This case reuses the walkthrough-1 shader with `use_fun` set to true, so `%src` and `%dst` are passed to `%cpbuffs` as `OpFunctionParameter %buf_ptr` values and dereferenced inside the callee with the same `OpAccessChain` + `OpLoad Aligned 4`/`OpStore Aligned 4` sequence. A failure isolated to this case points at SPIR-V function-call argument passing for `PhysicalStorageBuffer` pointers, or at the compiler lowering a pointer-typed parameter into the callee's dereference. Because the inline loop and the function body perform the same accesses, a divergence between the two paths is the discriminating signal.

#### `OpConvertUToPtr` or `OpSelect` on pointers mis-handled

**Possible failure symptoms:** An `addrs_in_ssbo` case produces a destination buffer with a stable every-other-slot mismatch: even-indexed elements wrong while odd-indexed elements are correct, or the reverse, depending on which representation the implementation mis-handled. A total failure (all elements wrong) points at SSBO address loading or `Int64` support as a whole, not at a single representation.

**Possible implementation causes:** This shader loads the same buffer address twice from the SSBO, once as a pointer-typed field and once as a `uint64` field converted with `OpConvertUToPtr`, then selects between them with `OpSelect` based on `gid_x % 2`. An even/odd pattern of wrong slots points at one of the two representations: either `OpConvertUToPtr` produced a wrong pointer from the `uint64` field, or `OpSelect` did not forward the selected pointer to the dereference. A uniform failure points at `Int64` capability handling for the `uint64` fields or at SSBO block layout. The `PhysicalStorageBuffer64` addressing model and `Aligned 4` access are shared with the push-constants shader, so a failure common to both cases would not isolate to this shader's unique instructions.

## Case Pruning

### Requirement-based pruning

- All three cases require `VK_KHR_get_physical_device_properties2` for feature queries and the `bufferDeviceAddress` feature, checked through `isBufferDeviceAddressSupported()` ([checkSupport](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L350-L362)).
- `addrs_in_ssbo` additionally requires `shaderInt64` because its SSBO stores the addresses as `uint64` fields ([shaderInt64 check](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L357-L361)).
- All three cases require the `PhysicalStorageBufferAddresses` SPIR-V capability, the `SPV_KHR_physical_storage_buffer` extension, the `PhysicalStorageBuffer64` addressing model, and SPIR-V 1.4 build options ([build options](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L529-L530)).
- Buffers must be created with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` so `vkGetBufferDeviceAddress` succeeds ([Buffer constructor](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L160-L162)).

### Design-based pruning

- The element count is fixed at 64 for all three cases; no parameter matrix varies it ([registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L758-L759)).
- `push_constants` and `push_constants_function` are registered as separate cases even though they share one shader, because the `use_fun` push-constant value selects a structurally different copy path (inline loop versus `OpFunctionCall`).
- `addrs_in_ssbo` is registered separately because its shader, dispatch shape, capability set, and address-transport mechanism differ from the push-constants cases.
- There are no graphics variants; physical-storage-buffer pointer tests are compute-only in this family.

## Key Takeaways

- The tested property is narrow: a buffer device address produced on the host must survive the round trip into a shader and dereference correctly as a `PhysicalStorageBuffer` pointer. Each case changes only how the address is transported and how the pointer is formed.
- `push_constants` and `push_constants_function` share one shader; the only structural difference is whether the copy runs inline in `main` or through `%cpbuffs` with the pointers as `OpFunctionParameter` values.
- `addrs_in_ssbo` is the only case that exercises `OpConvertUToPtr` and `OpSelect` on pointers. Its even/odd selector means a mis-handled representation shows up as a stable every-other-slot mismatch instead of a uniform failure.
- All three cases share the same final host comparison (`std::equal` with no tolerance), so any destination element that differs from the source fails the case.
- The `PhysicalStorageBuffer64` addressing model, the `PhysicalStorageBufferAddresses` capability, and SPIR-V 1.4 are common prerequisites; `Int64` and `shaderInt64` are unique to `addrs_in_ssbo`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `PassMethod` enum and `TestParams` | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L55-L66](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L55-L66) | Defines the three pass methods and the element count. |
| Push-constant shader template | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L400-L527](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L400-L527) | Shared SPIR-V assembly for `push_constants` and `push_constants_function`. |
| Push-constant host setup and comparison | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L533-L581](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L533-L581) | Builds buffers, queries device addresses, pushes constants, dispatches `1×1×1`, compares. |
| SSBO shader template | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L588-L670](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L588-L670) | SPIR-V assembly for `addrs_in_ssbo` with `OpConvertUToPtr` and `OpSelect`. |
| SSBO host setup and comparison | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L682-L738](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L682-L738) | Builds the SSBO, binds it, dispatches `64×1×1`, compares. |
| `ut::Buffer` / `ut::TypedBuffer` helpers | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L73-L294](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L73-L294) | Manage buffer creation with optional device-address support, `iota`, `zero`, `flush`, `invalidate`. |
| `getDeviceAddress` | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L181-L194](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L181-L194) | Wraps `vkGetBufferDeviceAddress`. |
| Support checks | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L350-L362](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L350-L362) | `bufferDeviceAddress`, `shaderInt64`, instance extension gates. |
| SPIR-V 1.4 build options | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L529-L530](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L529-L530) | `vk::SpirVAsmBuildOptions(..., vk::SPIRV_VERSION_1_4, true)`. |
| Registration factory | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L742-L763](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L742-L763) | Registers the three test case leaves under `physical_storage_buffer`. |
