## Overview

**Core question:** When a compute pipeline is built from the `basic`, `64b_indexing`, or `device_group` test families and dispatched under the dispatcher-selected pipeline-construction variant, do the resulting shader side effects, dispatch shapes, barriers, large-indexing paths, and device-group splits produce the host-expected per-element values?

- [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1) implements three test families rooted at the `compute` test category: `basic`, `64b_indexing`, and `device_group`. The three families share dispatcher setup, descriptor layout, and `ComputePipelineWrapper` plumbing.
- The `basic` family covers everyday compute execution: empty shaders and empty workgroup axes, max workgroup size, UBO→SSBO and SSBO→SSBO inverts, multi-group SSBO read/write, local and command-buffer SSBO barriers, shared variables and shared atomics, image copies, image atomics, image barriers, compute-only queues, replicated composites, Amber regression cases, undefined-value semantics, and dispatch sequencing.
- The `64b_indexing` family covers SSBOs whose total element count exceeds the 32-bit range and a hand-written SPIR-V untyped-pointer path. All cases are non-VulkanSC.
- The `device_group` family covers `cmdDispatchBase`, the maintenance5 variant of base dispatch, and the `gl_DeviceIndex` builtin across multiple physical devices.
- The page explains what each family checks and why a failure would point to a specific kind of driver or shader-compiler defect. The host validation is a per-element buffer or image comparison against an expected formula.

## Background Knowledge

- **One source file, three test families.** The structural reason for grouping `basic`, `64b_indexing`, and `device_group` into one page is that they share implementation plumbing. They are not grouped by behavior: each family stresses a different facet of compute dispatch, and a reader who only needs the buffer-copy test logic should still see the device-group and large-indexing contracts explained separately.
- **Compute pipeline construction variants.** The category dispatcher creates three roots (`pipeline`, `shader_object_spirv`, `shader_object_binary`) and runs the same child factories under each root. Each test class takes a `vk::ComputePipelineConstructionType` parameter. Only the Amber regression cases are skipped when the construction type is a shader object; the `replicated_composites_*` cases are registered under all three roots [vktComputeTests.cpp](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6154-L6224).
- **Dispatch shape.** The parameterized `basic` cases register explicit local and work sizes, while specialized cases such as empty shaders and max-size workgroups derive or hard-code their dispatches internally. The matrix explores single-invocation, single-workgroup, multi-invocation-per-group, and multi-group workloads, plus empty workgroup axes and per-axis max workgroup size. The buffer cases rely on `gl_NumWorkGroups`, `gl_WorkGroupSize`, and `gl_GlobalInvocationID` reaching each invocation exactly once [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6000-L6124).
- **Barriers.** Local barriers (`barrier()` plus `memoryBarrierShared()`) are intra-workgroup and do not need a `cmdPipelineBarrier`. Command-buffer barriers (`cmdPipelineBarrier` between dispatches) are required for cross-workgroup visibility. Image barriers need both an image-layout transition into `GENERAL` and a compute-to-host transfer barrier before copyback [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2361-L2605), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2838-L3083).
- **Large SSBO indexing.** The 64-bit indexing invert cases allocate 8 GB input and output SSBOs (512M `UVec4` elements apiece) and rely on `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT` (set when `bufferSizeBytes > 1 << 32`) or on the `#pragma shader_64bit_indexing` GLSL execution mode. The untyped-pointer case uses inline SPIR-V with `OpCapability UntypedPointersKHR` and `OpUntypedArrayLengthKHR` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1311-L1333), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1840-L1944), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6237-L6265).
- **Device-group dispatch.** `dispatch_base` uses `cmdDispatchBase` with explicit `(baseX, baseY, baseZ)` offsets and creates the pipeline with `VK_PIPELINE_CREATE_DISPATCH_BASE`. `dispatch_base_maintenance5` uses the `VK_PIPELINE_CREATE_2_DISPATCH_BASE_BIT_KHR` create-flag2 instead. `device_index` uses `gl_DeviceIndex` from `GL_EXT_device_group` together with a uniform buffer of base offsets, and the test iterates over every non-empty device mask [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3276-L4089).

## Registration Hierarchy

```text
compute.pipeline
├── basic
├── 64b_indexing
└── device_group
```

The category dispatcher replicates the same three children under each of its `pipeline`, `shader_object_spirv`, and `shader_object_binary` construction-mode roots. The Amber regression cases and replicated-composite subtree inside `basic` are skipped when the construction mode is a shader object; the mustpass coverage in `compute.txt` registers cases under `compute.pipeline.*`, `compute.shader_object_spirv.*`, and `compute.shader_object_binary.*` for this source file.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `basic`, `64b_indexing`, `device_group` | Selects which dispatch, synchronization, indexing, or device-group contract is exercised. | [createBasicComputeShaderTests](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5986-L6233), [create64bIndexingComputeShaderTests](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6237-L6265), [createBasicDeviceGroupComputeShaderTests](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6268-L6284) |
| Local and work sizes | Explicit `tcu::IVec3` pairs (e.g. `(1,1,1)`, `(3,2,5)`, `(2,4,1)` × `(1,1,1)`, `(2,2,4)`) | Chooses single-invocation, single-workgroup, multi-invocation, or multi-group dispatch. | [basic registrations](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6000-L6124) |
| Buffer size and bounds-check flag | `numValues` (256 or 1024 normally; 512 for `copy_ssbo_bounds`) plus `doBoundsCheck = true` for the bounds variant | Controls whether the host builds a robust-buffer-access device with a partial descriptor range. | [BufferToBufferInvertTest::checkSupport](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1311-L1333), [UBO/SSBO registrations](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6026-L6053) |
| 64-bit indexing mode | `numElems64b = 512M × UVec4`; pipeline create flag vs `#pragma shader_64bit_indexing` vs untyped-pointer SPIR-V | Decides which 64-bit indexing declaration path the compiler and pipeline create path must honor. | [64b_indexing registrations](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6245-L6262) |
| Composite type and instantiation mode | `vector`, `matrix`, `array`, `array_array`, `struct`, `struct_struct`, `coopmat` × `value`, `constant`, `specconstant` | Selects the replicated-composite shape and whether it is a regular local, a `const`, or a specialization-constant composite. | [replicated composites loop](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6154-L6180) |
| Device-group modes | `dispatch_base`, `dispatch_base_maintenance5`, `device_index` | Chooses legacy `VK_PIPELINE_CREATE_DISPATCH_BASE`, maintenance5 `VK_PIPELINE_CREATE_2_DISPATCH_BASE_BIT_KHR`, or `gl_DeviceIndex` driven per-device work. | [device_group registrations](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6273-L6282) |

## Behavior Parameters

The primary behavioral axis for this page is the **test family** rooted at `compute`. Each family changes the question the host is asking; sub-families under `basic` are documented in `## Case Pruning` and the parameter table, but they all run inside the same `basic` dispatch contract.

### basic — Everyday compute execution and shader-side effects

`basic` is the largest family. It bundles buffer-to-buffer inverts (UBO and SSBO forms), multi-invocation and multi-group SSBO reads and writes, shared-memory and shared-atomic coordination, image-to-buffer and buffer-to-image copies, image atomics and image barriers, max workgroup size, empty workgroup axes, secondary command buffers on a compute-only queue, replicated composites, Amber regression cases, undefined-value semantics, and dispatch sequencing. Resource layouts and synchronization are case-specific: buffer-invert cases use input and output buffer bindings plus a compute-to-host barrier, while image and multi-dispatch cases add their own image, transfer, or inter-dispatch barriers [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5986-L6233).

The expected per-element value depends on the case. Buffer-invert cases expect `output[i].x == ~input[i].x`. Shared-variable cases expect each invocation to write into a shared slot using a reversed local offset, then read out in natural order. Shared-atomic cases expect `output[i] == i + 1`. Image-atomic cases expect the per-pixel image value to equal the sum of the per-pixel input values. Replicated-composite cases expect the storage-buffer contents to match a host-known reference per composite type and instantiation mode. The full validation rule for `indirect_after_base_dispatch` expects the atomic counter to hold `1 + 3*3*1 == 10` after the chained `cmdDispatchBase` + `cmdDispatchIndirect` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1336-L1390), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3582-L3794), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5431-L5858).

The Amber regression cases are skipped when the construction type is a shader object. Replicated composites are non-VulkanSC. Several Amber cases have additional feature gates such as `shaderFloat64`, `shaderFloat16`, `storageBuffer16BitAccess`, and shader-denorm-preserve float16 properties [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6182-L6224).

### 64b_indexing — Large SSBOs and untyped pointers

`64b_indexing` uses the same `BufferToBufferInvertTest` SSBO branch as `basic.copy_ssbo_*`, but with `numElems64b = 512M` (8 GB per input or output buffer). The host allocates `sizeof(tcu::UVec4) * numElems64b` bytes for each buffer, uses local size `(1024, 1, 1)` and dispatch size `(1024, 1, 1)` workgroups, and walks every element after the readback barrier. The pipeline is built with `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT` whenever `bufferSizeBytes > 1 << 32`, except for `copy_ssbo_64b_execution_mode`, which instead emits `#extension GL_EXT_shader_64bit_indexing : enable` and `#pragma shader_64bit_indexing` in the GLSL [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6237-L6265).

The `untyped_pointers` case is different: it compiles inline SPIR-V assembly that uses `OpCapability UntypedPointersKHR`, `OpUntypedVariableKHR`, and `OpUntypedArrayLengthKHR`, declares a pipeline layout with a `STORAGE_BUFFER_DYNAMIC` binding, sets the same `64_BIT_INDEXING` create-flag2, and only checks that the pipeline builds successfully. It does not allocate or update a descriptor set and does not dispatch the shader; there is therefore no per-element host comparison [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1840-L1944).

All `64b_indexing` cases are non-VulkanSC. The 8 GB allocation can fail with `Out of memory`; the host maps that to `NotSupportedError` rather than failing the test [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1629-L1637).

### device_group — Device-group dispatch base, maintenance5, and per-device index

`device_group` registers three logical-device-group cases. `dispatch_base` and `dispatch_base_maintenance5` explicitly require `VK_KHR_device_group`; the latter additionally requires `VK_KHR_maintenance5`. They use `cmdDispatchBase` with explicit `(baseX, baseY, baseZ)` offsets and a smaller workgroup count, splitting the global workgrid across physical devices. The shader receives the global grid size through a uniform buffer, so the per-device partial grid produces correct offsets without recompilation. The test asserts `totalWorkloadSize == multiplyComponents(m_workSize)`, which catches missing dispatches or wrong device masks [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3413-L3560).

`device_index` builds a single shader that reads `gl_DeviceIndex` from `GL_EXT_device_group` and combines it with a uniform array of base offsets. The test allocates the SBO with `VK_MEMORY_ALLOCATE_DEVICE_MASK_BIT` and a device mask covering every physical device, then iterates over all non-empty device masks. After each dispatch, the host copies the SBO into a per-device check buffer and expects `bufferPtr[i] == constantValPerLoop + uniformInputData[4 * (physDevIdx + 1)]` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3796-L4089).

`basic.indirect_after_base_dispatch` exercises the same `cmdDispatchBase` path chained with `cmdDispatchIndirect`, verifying that the atomic counter holds the sum of both dispatches' invocations [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3582-L3794).

## Shader Analysis

The shaders in this file are generated as GLSL strings inline in each test class's `initPrograms(SourceCollections&)` method, except for `untyped_pointers` (inline SPIR-V assembly) and the Amber regression cases (external `.amber` files). This page uses one walkthrough because the canonical `basic.copy_ssbo_*` shader captures the dispatch, descriptor, barrier, and host-readback contract that the rest of the page refers to.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.compute.basic.copy_ssbo_single_invocation
```

The same generated shader source also backs `copy_ssbo_multiple_invocations` and `copy_ssbo_multiple_groups`; the variants differ only in the registered `m_localSize` and `m_workSize` arguments.

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `basic` test family | The shader sits in the `basic` subtree, which exercises the everyday compute dispatch contract rather than device-group or 64-bit-indexing paths. |
| `copy_ssbo_*` rather than `ubo_to_ssbo_*` | `BufferToBufferInvertTest` uses the `BUFFER_TYPE_SSBO` branch, so both bindings are `STORAGE_BUFFER` and the input is a runtime-sized SSBO. The SSBO branch is reused by `64b_indexing` for the 8 GB cases. |
| `single_invocation` shape | Local size `(1,1,1)` and one workgroup keeps the shader trivially serial; the host can pinpoint any per-element mismatch to a shader bug rather than a multi-invocation race. |
| `numValues == 256` | The host writes `numValues * sizeof(UVec4)` bytes into both buffers, pre-fills the output with `0xBEBEBEBE`, and walks 256 elements in the verification loop. |
| `doBoundsCheck == false`, `deviceLocal == false`, `use64bExecutionMode == false` | These are the default flags for `CopyInvertSSBOCase(...)`; the bounds-check variant gates on `VK_EXT_robustness2` and the 64-bit-execution-mode variant enables the `#pragma shader_64bit_indexing` path used by `64b_indexing.copy_ssbo_64b_execution_mode`. |

#### Purpose

The shader must produce, for each element in a `std140` SSBO, the bitwise complement of the corresponding element in a second `std140` SSBO, mapped from a single global invocation index. The host verification relies on every assigned element being written; invocation ordering is irrelevant because the invocation slices do not overlap. A missing write leaves the `0xBEBEBEBE` sentinel intact and produces a precise per-element mismatch.

#### Structural Design

| Phase | What the shader does | Inputs read | Outputs written |
|-------|----------------------|-------------|-----------------|
| Setup | Compute the global workgrid size, derive the per-invocation offset, and walk `numValuesPerInv` consecutive elements. | `gl_NumWorkGroups`, `gl_WorkGroupSize`, `gl_GlobalInvocationID`, `sb_in.values.length()`, `sb_out.values.length()` | n/a |
| Loop body | Bitwise-invert the input element and write the result into the output slot. | `sb_in.values[offset + ndx]` | `sb_out.values[offset + ndx]` |

The shader uses two unsized runtime arrays (`uint values[]`) so the same generator code also covers the 8 GB large-indexing cases; the offset arithmetic itself stays in `uint`, with 64-bit indexing declared through the pipeline create flag rather than through the GLSL.

#### Shader Code

```glsl
#version 310 es
// Generated by BufferToBufferInvertTest::initPrograms, SSBO branch (m_bufferType == BUFFER_TYPE_SSBO).
// Selected dimensions: local_size = (1,1,1), workgroups = (1,1,1), numValues = 256, use64bExecutionMode = false.
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 is the input SSBO; the descriptor declares an unsized `uint values[]` so the same shader can read
/// either the 256-element test case or the 8 GB 64-bit-indexing case. The host fills this buffer with random u32 data.
layout(binding = 0, std140) readonly buffer Input {
    uint values[];
} sb_in;
/// Binding 1 is the output SSBO. The host pre-fills it with 0xBEBEBEBE through cmdFillBuffer so missed writes are visible.
layout (binding = 1, std140) writeonly buffer Output {
    uint values[];
} sb_out;
void main (void) {
    uvec3 size           = gl_NumWorkGroups * gl_WorkGroupSize;
    uint numValuesPerInv = uint(sb_out.values.length()) / (size.x*size.y*size.z);
    uint groupNdx        = size.x*size.y*gl_GlobalInvocationID.z + size.x*gl_GlobalInvocationID.y + gl_GlobalInvocationID.x;
    uint offset          = numValuesPerInv*groupNdx;

    for (uint ndx = 0u; ndx < numValuesPerInv; ndx++)
        sb_out.values[offset + ndx] = ~sb_in.values[offset + ndx];
}
```

#### Additional Info

- The shader is one of several flavors built by `BufferToBufferInvertTest::initPrograms`. The other flavors (UBO input, `use64bExecutionMode`) substitute the input binding type or prepend the `#pragma shader_64bit_indexing` block; the rest of the shader text is identical.
- `numValuesPerInv` is `sb_out.values.length()` divided by the total invocation count. For the 256-element single-invocation case the invocation count is `1`, so the invocation walks all 256 elements. Multi-invocation cases assign each invocation one non-overlapping slice.
- The `bufferSizeBytes` passed to the host setup is `sizeof(tcu::UVec4) * m_numValues` (16 bytes per element), so the descriptor range and barrier sizes match a 4096-byte buffer for `m_numValues == 256`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Buffer type | `BUFFER_TYPE_UNIFORM` substitutes the input binding with `readonly uniform Input { uint values[N]; }` and adds a `std140` qualifier on the output binding. The host-side descriptor type becomes `UNIFORM_BUFFER`/`STORAGE_BUFFER`. | [vktComputeBasicComputeShaderTests.cpp#L1339-L1360](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1339-L1360), [vktComputeBasicComputeShaderTests.cpp#L6026-L6038](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6026-L6038) |
| `use64bExecutionMode` | When true, the generator prepends `#extension GL_EXT_shader_64bit_indexing : enable` and `#pragma shader_64bit_indexing` before the local-size layout. The `m_use64bExecutionMode` flag is otherwise ignored on the C++ side, where the create-flag variant selects `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT`. | [vktComputeBasicComputeShaderTests.cpp#L1363-L1368](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1363-L1368) |
| `doBoundsCheck` | The shader itself does not change. The host builds a robust-buffer-access device, shrinks the input descriptor range to `3/4` and the output descriptor range to `7/8` of `bufferSizeBytes`, and expects the out-of-range elements to retain the `0xBEBEBEBE` sentinel. | [vktComputeBasicComputeShaderTests.cpp#L1420-L1427](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1420-L1427), [vktComputeBasicComputeShaderTests.cpp#L1528-L1529](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1528-L1529) |
| Dispatch shape | `m_localSize` and `m_workSize` flow into the `layout (local_size_*)` qualifiers and into `gl_NumWorkGroups * gl_WorkGroupSize` size math at runtime. Variants such as `copy_ssbo_multiple_invocations` (`local_size = (1,1,1)`, `workgroups = (2,4,1)`) reuse the same compiled shader. | [vktComputeBasicComputeShaderTests.cpp#L6042-L6049](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6042-L6049) |
| Pipeline construction type | The shader does not change. `ComputePipelineWrapper` chooses between `vkCreateComputePipelines` (pipeline root) and shader-object creation (shader-object roots) at pipeline build time. | [vktComputeBasicComputeShaderTests.cpp#L1544-L1554](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1544-L1554) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 90
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource ESSL 310
               OpName %main "main"
               OpName %size "size"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %numValuesPerInv "numValuesPerInv"
               OpName %Output "Output"
               OpMemberName %Output 0 "values"
               OpName %sb_out "sb_out"
               OpName %groupNdx "groupNdx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %offset "offset"
               OpName %ndx "ndx"
               OpName %Input "Input"
               OpMemberName %Input 0 "values"
               OpName %sb_in "sb_in"
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %_runtimearr_uint ArrayStride 16
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %sb_out NonReadable
               OpDecorate %sb_out Binding 1
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_uint_0 ArrayStride 16
               OpDecorate %Input BufferBlock
               OpMemberDecorate %Input 0 NonWritable
               OpMemberDecorate %Input 0 Offset 0
               OpDecorate %sb_in NonWritable
               OpDecorate %sb_in Binding 0
               OpDecorate %sb_in DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Function_v3uint = OpTypePointer Function %v3uint
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
%_ptr_Function_uint = OpTypePointer Function %uint
%_runtimearr_uint = OpTypeRuntimeArray %uint
     %Output = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
     %sb_out = OpVariable %_ptr_Uniform_Output Uniform
        %int = OpTypeInt 32 1
     %uint_0 = OpConstant %uint 0
     %uint_2 = OpConstant %uint 2
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
       %bool = OpTypeBool
      %int_0 = OpConstant %int 0
%_runtimearr_uint_0 = OpTypeRuntimeArray %uint
      %Input = OpTypeStruct %_runtimearr_uint_0
%_ptr_Uniform_Input = OpTypePointer Uniform %Input
      %sb_in = OpVariable %_ptr_Uniform_Input Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
       %size = OpVariable %_ptr_Function_v3uint Function
%numValuesPerInv = OpVariable %_ptr_Function_uint Function
   %groupNdx = OpVariable %_ptr_Function_uint Function
     %offset = OpVariable %_ptr_Function_uint Function
        %ndx = OpVariable %_ptr_Function_uint Function
         %12 = OpLoad %v3uint %gl_NumWorkGroups
         %15 = OpIMul %v3uint %12 %gl_WorkGroupSize
               OpStore %size %15
         %22 = OpArrayLength %uint %sb_out 0
         %24 = OpBitcast %int %22
         %25 = OpBitcast %uint %24
         %27 = OpAccessChain %_ptr_Function_uint %size %uint_0
         %28 = OpLoad %uint %27
         %29 = OpAccessChain %_ptr_Function_uint %size %uint_1
         %30 = OpLoad %uint %29
         %31 = OpIMul %uint %28 %30
         %33 = OpAccessChain %_ptr_Function_uint %size %uint_2
         %34 = OpLoad %uint %33
         %35 = OpIMul %uint %31 %34
         %36 = OpUDiv %uint %25 %35
               OpStore %numValuesPerInv %36
         %38 = OpAccessChain %_ptr_Function_uint %size %uint_0
         %39 = OpLoad %uint %38
         %40 = OpAccessChain %_ptr_Function_uint %size %uint_1
         %41 = OpLoad %uint %40
         %42 = OpIMul %uint %39 %41
         %45 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %46 = OpLoad %uint %45
         %47 = OpIMul %uint %42 %46
         %48 = OpAccessChain %_ptr_Function_uint %size %uint_0
         %49 = OpLoad %uint %48
         %50 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %51 = OpLoad %uint %50
         %52 = OpIMul %uint %49 %51
         %53 = OpIAdd %uint %47 %52
         %54 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %55 = OpLoad %uint %54
         %56 = OpIAdd %uint %53 %55
               OpStore %groupNdx %56
         %58 = OpLoad %uint %numValuesPerInv
         %59 = OpLoad %uint %groupNdx
         %60 = OpIMul %uint %58 %59
               OpStore %offset %60
               OpStore %ndx %uint_0
               OpBranch %62
         %62 = OpLabel
               OpLoopMerge %64 %65 None
               OpBranch %66
         %66 = OpLabel
         %67 = OpLoad %uint %ndx
         %68 = OpLoad %uint %numValuesPerInv
         %70 = OpULessThan %bool %67 %68
               OpBranchConditional %70 %63 %64
         %63 = OpLabel
         %72 = OpLoad %uint %offset
         %73 = OpLoad %uint %ndx
         %74 = OpIAdd %uint %72 %73
         %79 = OpLoad %uint %offset
         %80 = OpLoad %uint %ndx
         %81 = OpIAdd %uint %79 %80
         %83 = OpAccessChain %_ptr_Uniform_uint %sb_in %int_0 %81
         %84 = OpLoad %uint %83
         %85 = OpNot %uint %84
         %86 = OpAccessChain %_ptr_Uniform_uint %sb_out %int_0 %74
               OpStore %86 %85
               OpBranch %65
         %65 = OpLabel
         %87 = OpLoad %uint %ndx
         %89 = OpIAdd %uint %87 %int_1
               OpStore %ndx %89
               OpBranch %62
         %64 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Resource setup.** Resource-using tests create the buffers, images, layouts, pools, and descriptor sets needed by their individual contracts, generally with `BufferWithMemory` and the standard descriptor builders. Image tests additionally create a `r32ui` storage image with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_STORAGE_BIT` and an image view in `VK_IMAGE_LAYOUT_GENERAL` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L227-L250), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2700-L2767).
- **Pipeline build.** For the generated-shader tests, `ComputePipelineWrapper` builds either a pipeline object (pipeline root) or a shader object (shader-object roots) from `m_context.getBinaryCollection().get("comp")`. The compute pipeline construction type flows in from the category dispatcher and distinguishes the three roots; Amber cases use their external-script path instead [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1544-L1554).
- **Dispatch.** Local and work sizes come from the registered test parameters. Empty workgroup cases pass `(0, 2, 3)`, `(2, 0, 3)`, `(2, 3, 0)`, or `(0, 0, 0)`. Device-group cases split the dispatch with `cmdDispatchBase`; `indirect_after_base_dispatch` chains `cmdDispatchBase` with `cmdDispatchIndirect` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6000-L6012), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3753-L3764).
- **Barriers.** A `cmdPipelineBarrier(PIPELINE_STAGE_HOST_BIT → PIPELINE_STAGE_COMPUTE_SHADER_BIT)` before dispatch makes the host-written input visible to the shader. A second `cmdPipelineBarrier(PIPELINE_STAGE_COMPUTE_SHADER_BIT → PIPELINE_STAGE_HOST_BIT)` (or `→ TRANSFER_BIT` for image copyback) makes the shader output visible to the host. Local `barrier()` and `memoryBarrierShared()` calls live in the shader itself [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1573-L1577), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L170-L199).
- **Result checking.** Buffer tests walk the output buffer in host code and compare `output[i]` against the expected formula. Image tests copy the image into a host-visible buffer and compare against the per-pixel input sum. Device-group tests copy the SBO into a per-device check buffer for each physical device in the mask [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1614-L1628), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2812-L2835), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4072-L4085].
- **Special pre-fills.** Buffer-to-buffer inverts call `cmdFillBuffer` with `0xBEBEBEBE` so missed writes produce a clear sentinel value rather than a zero. Empty workgroup cases zero-initialize the verification buffer and assert it equals `1` after a follow-up `cmdDispatch(1, 1, 1)` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1500-L1504), [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4637-L4696).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Wrong per-invocation mapping between global invocation ID and buffer element; missing or weak workgroup/barrier synchronization; missing barrier between host write and shader read (or between shader write and host read); wrong image layout transition or image barrier between dispatches; wrong max-workgroup-size specialization constants; pipeline construction (pipeline vs shader object) mishandling; Amber-script regressions; undefined-value propagation from struct assignments; wrong counter accumulation in dispatch-sequencing cases; queue-priority ordering mis-observed in `concurrent_compute`; missing `robustBufferAccess2` handling in bounds-check variants; replicated-composites compiler pass failing for one or more composite types; cooperative-matrix replicated-composites failing when `VK_COMPONENT_TYPE_FLOAT16_KHR` is not available. |
| `64b_indexing` | Buffer descriptor or arithmetic exceeding the 32-bit element range without the correct 64-bit indexing pipeline create flag or execution-mode pragma; `VK_EXT_shader_64bit_indexing` feature missing on the implementation; out-of-memory failure when allocating an 8 GB buffer; `VK_KHR_shader_untyped_pointers` capability not supported; pipeline create flag conflict between `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT` and the chosen pipeline construction mode. |
| `device_group` | `cmdDispatchBase` skipping a chunk of the workgrid; wrong per-device work distribution across `m_splitWorkSize`; uniform-buffer grid size not propagated correctly to the shader; maintenance5 create-flag2 path differing from the legacy `VK_PIPELINE_CREATE_DISPATCH_BASE` flag; `gl_DeviceIndex` builtin producing the wrong value per device; cross-device visibility not honored for the device-mask SBO; per-device readback missing a physical device in the mask; fence-based ordering between `cmdDispatchBase` and `cmdDispatchIndirect` violating expected completion order. |

### Cause Analysis

#### `basic` family failures

**Possible failure symptoms:** A specific `output[i]` mismatch reported as `Comparison failed for Output.values[<i>]`; an image pixel mismatch reported as `Comparison failed for pixel <i>`; a `ConcurrentCompute` `Failed waiting for low-priority queue fence` or `Comparison failed for counter value`; an `EmptyWorkGroup` `Unexpected value found in buffer: <v> while expecting 1`; a `MaxWorkGroupSize` `Found invalid value for invocation index <i>: expected 1u and found <v>`; an `UndefinedValues` `Unexpected values in output structure: a=<...> c=<v>`.

**Possible implementation causes:** A shader compiler that drops a `barrier()` or weakens memory semantics for a workgroup-coordination pattern would produce off-by-one or zero values in shared-memory or shared-atomic cases. A driver that mis-handles `cmdPipelineBarrier(PIPELINE_STAGE_COMPUTE_SHADER_BIT → PIPELINE_STAGE_HOST_BIT)` would leave shader writes invisible to the host and produce the sentinel value. An image-atomic compiler that does not pair `imageStore` with a `memoryBarrierImage()` + `barrier()` would lose cross-invocation accumulation. The replicated-composites optimization (`#pragma use_replicated_composites`) is sensitive to compiler pass selection; one missing pass produces a partial-write or wrong-element pattern. The `concurrent_compute` queue-priority ordering check requires the driver to honor queue priorities and a fence-based wait; if the low-priority queue can run ahead, the test fails with `ERROR_WAIT`. Amber regressions are external regressions and may fail for many reasons; without source-level investigation, the exact root cause must be flagged.

#### `64b_indexing` family failures

**Possible failure symptoms:** An `Out of memory` exception converted to `NotSupportedError` for the 8 GB allocation (this is not a test failure, but a real failure would surface as a buffer-readback mismatch); a `BufferToBufferInvertTest` `Comparison failed for Output.values[<i>]` for an index that exceeds the 32-bit element range when the create-flag variant is not honored; a `UntypedPointerTest` pipeline-build error when the implementation lacks `VK_KHR_shader_untyped_pointers` or `OpUntypedArrayLengthKHR` support.

**Possible implementation causes:** Without `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT`, large-indexing SSBO descriptors cannot be addressed beyond the 32-bit range, and a missing implementation of the create-flag2 path produces per-element mismatches for the 8 GB case. Without `#pragma shader_64bit_indexing`, the GLSL execution-mode path is rejected by the shader compiler or the pipeline compiler. The untyped-pointer capability requires both `VK_KHR_shader_untyped_pointers` and `VK_EXT_shader_64bit_indexing`; missing either feature throws `NotSupportedError`. The 8 GB allocation can be refused by the device memory allocator; the host maps `vk::OutOfMemoryError` to `NotSupportedError` when `bufferSizeBytes >= (1ULL << 32)`. Other failure sources require source-level investigation.

#### `device_group` family failures

**Possible failure symptoms:** A `Not covering the entire workload` error if `totalWorkloadSize != multiplyComponents(m_workSize)`; a `Comparison failed on physical device <dev> ( deviceMask <mask> ) for InOut.values[<i>]` mismatch in `device_index`; a `Comparison failed for counter value. Got: <v>. Expected: <v>` for `indirect_after_base_dispatch`.

**Possible implementation causes:** A driver that mis-splits the workgrid across physical devices produces `totalWorkloadSize` mismatches. A driver that fails to honor `VK_MEMORY_ALLOCATE_DEVICE_MASK_BIT` with the full device mask produces empty or wrong values on at least one device in the mask. A shader compiler that does not lower `gl_DeviceIndex` correctly produces a fixed value per invocation rather than the per-device index, which surfaces as `bufferPtr[i] != constantValPerLoop + uniformInputData[4 * (physDevIdx + 1)]`. The maintenance5 create-flag2 path is a separate code path from the legacy `VK_PIPELINE_CREATE_DISPATCH_BASE` flag; if the legacy flag is left set under maintenance5 the implementation can take a different dispatch path. The `cmdDispatchBase` / `cmdDispatchIndirect` ordering check assumes the dispatch order in the command buffer is honored; a driver that reorders dispatches produces the wrong counter.

## Case Pruning

### Requirement-based pruning

- `VK_EXT_robustness2` with `robustBufferAccess2` is required for `copy_ssbo_bounds`, `copy_ssbo_64b_bounds`, and `copy_ssbo_64b_bounds_local`; without it the test throws `NotSupportedError` and is not registered for that device [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1322-L1333).
- `VK_EXT_shader_64bit_indexing` with `shader64BitIndexing` is required for any case whose SSBO size exceeds `(1U << (32 - 4))` (= 256M elements) [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1315-L1321).
- `VK_KHR_shader_untyped_pointers` plus `VK_EXT_shader_64bit_indexing` are required for `64b_indexing.untyped_pointers` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1857-L1862).
- `VK_KHR_device_group` is explicitly required by both `dispatch_base` variants and by `indirect_after_base_dispatch`; `VK_KHR_maintenance5` is additionally required for `dispatch_base_maintenance5`. `device_index` has no corresponding explicit extension request in its `checkSupport()` method [vktComputeBasicComputeShaderTests.cpp#L3330-L3337](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3330-L3337), [vktComputeBasicComputeShaderTests.cpp#L3622-L3627](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3622-L3627), [vktComputeBasicComputeShaderTests.cpp#L3838-L3842](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3838-L3842).
- `VK_EXT_shader_replicated_composites` with `shaderReplicatedComposites` is required for every `replicated_composites_*` case. `VK_KHR_cooperative_matrix` plus a `VK_COMPONENT_TYPE_FLOAT16_KHR` subgroup-scope property is required for `replicated_composites_coopmat_*` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5380-L5428).
- `computePipelineConstructionType == SHADER_OBJECT_SPIRV|SHADER_OBJECT_BINARY` excludes the Amber regression cases (skipped when `isComputePipelineConstructionTypeShaderObject(...)` is true). The non-VulkanSC `replicated_composites_*` subtree is not inside that shader-object condition and executes under all three construction roots [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6154-L6224).
- Several Amber cases add `shaderFloat64`, `shaderFloat16`, `storageBuffer16BitAccess`, `uniformAndStorageBuffer16BitAccess`, `shaderInt16`, and `shaderDenormPreserveFloat16` requirements [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6192-L6222).
- `UndefinedValues` requires Vulkan API version 1.2 or higher [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5864-L5868).
- `ConcurrentCompute` requires two queue families (or one with two queues) that support `VK_QUEUE_COMPUTE_BIT`; without them the test throws `NotSupportedError` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4198-L4213).
- `secondary_compute_only_queue` requires a queue family that supports `VK_QUEUE_COMPUTE_BIT` without `VK_QUEUE_GRAPHICS_BIT` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5031-L5062).
- `MaxWorkGroupSize` requires `maxStorageBufferRange / sizeof(uint32_t) >= maxComputeWorkGroupSize[axis]`; otherwise the test throws `NotSupportedError` [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4816-L4828).

### Design-based pruning

- The replicated-composites subtree combines seven composite types with three instantiation modes, but the COOPMAT variant is excluded when `VK_KHR_cooperative_matrix` is unavailable, narrowing the matrix to six composite types for devices without that feature.
- The buffer-invert matrix intentionally chooses `numValues == 256` for `single_invocation` and `numValues == 1024` for multi-invocation and multi-group shapes so that each variant covers a clean multiple of the workgroup size [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1289-L1290).
- `device_group.dispatch_base_maintenance5` is non-VulkanSC because `VK_KHR_maintenance5` is not part of the VulkanSC umbrella; `device_group.dispatch_base` and `device_group.device_index` run on both regular and VulkanSC builds [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6276-L6280).
- `64b_indexing.copy_ssbo_64b_execution_mode` keeps `m_use64bExecutionMode = true` so the shader emits the GLSL pragma, but the C++ side still sets `m_doBoundsCheck = false` and `m_deviceLocal = false`. The execution-mode variant intentionally does not set the `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT` create flag (the host code only sets it when `bufferSizeBytes > (uint64_t{1} << 32) && !m_use64bExecutionMode`), so the two declarations are mutually exclusive [vktComputeBasicComputeShaderTests.cpp](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1547-L1554).

## Key Takeaways

- `basic` is the everyday compute contract: dispatch shape, local-size limits, SSBO and image side effects, local and command-buffer barriers, shared memory and shared atomics, replicated composites, compute-only queues, Amber regressions, undefined values, and chained dispatch sequencing.
- `64b_indexing` tests SSBOs whose total element count exceeds the 32-bit range, with two parallel declaration paths (pipeline create flag vs GLSL execution-mode pragma) plus a hand-written SPIR-V untyped-pointer path.
- `device_group` tests `cmdDispatchBase` (legacy and maintenance5 create-flag2 variants) and the `gl_DeviceIndex` builtin with per-device uniform offsets. The chained `cmdDispatchBase` + `cmdDispatchIndirect` case is registered separately under `basic`.
- The host verification is per-element: a buffer-to-buffer comparison for buffer cases, a per-pixel image readback for image cases, and a per-device copyback for `device_index`. A missed write leaves the `0xBEBEBEBE` sentinel intact and produces a precise mismatch.
- The shader-object construction roots omit the Amber regression cases but retain the replicated-composites subtree; `compute.txt` contains replicated-composite entries under the pipeline and both shader-object roots.
- See `## Failure Meaning` for per-family failure analysis grounded in the test's validation logic.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createBasicComputeShaderTests` | [vktComputeBasicComputeShaderTests.cpp#L5986-L6233](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5986-L6233) | Registers the `basic` family, including buffer/image tests, Amber regression cases, undefined values, and indirect-after-base dispatch. |
| `create64bIndexingComputeShaderTests` | [vktComputeBasicComputeShaderTests.cpp#L6237-L6265](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6237-L6265) | Registers the `64b_indexing` family (large-SSBO and untyped-pointer cases, non-VulkanSC). |
| `createBasicDeviceGroupComputeShaderTests` | [vktComputeBasicComputeShaderTests.cpp#L6268-L6284](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6268-L6284) | Registers the `device_group` family (dispatch base, maintenance5 variant, device index). |
| `BufferToBufferInvertTest` (UBO/SSBO) | [vktComputeBasicComputeShaderTests.cpp#L1222-L1638](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1222-L1638) | Core buffer-to-buffer copy/invert semantics, optional bounds check, optional 64-bit indexing flag. |
| `SharedVarTest`, `SharedVarAtomicOpTest` | [vktComputeBasicComputeShaderTests.cpp#L123-L497](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L123-L497) | Workgroup-shared memory and atomics. |
| `EmptyWorkGroupCase` | [vktComputeBasicComputeShaderTests.cpp#L4553-L4696](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4553-L4696) | Empty workgroup axes. |
| `MaxWorkGroupSizeTest` | [vktComputeBasicComputeShaderTests.cpp#L4698-L4980](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4698-L4980) | Maximum workgroup size limits with specialization constants. |
| `SSBOBarrierTest` | [vktComputeBasicComputeShaderTests.cpp#L2361-L2605](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2361-L2605) | SSBO command-buffer barrier between dispatches. |
| `ImageAtomicOpTest` | [vktComputeBasicComputeShaderTests.cpp#L2606-L2837](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2606-L2837) | Image atomics across invocations. |
| `ImageBarrierTest` | [vktComputeBasicComputeShaderTests.cpp#L2838-L3083](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2838-L3083) | Image barrier across dispatches. |
| `UntypedPointerTest` | [vktComputeBasicComputeShaderTests.cpp#L1840-L1944](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1840-L1944) | Inline SPIR-V untyped pointers + 64-bit indexing flag. |
| `WriteToMultipleSSBOTest`, `InvertSSBOInPlaceTest`, `ReadUnboundSSBOTest` | [vktComputeBasicComputeShaderTests.cpp#L1640-L2359](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1640-L2359) | Multiple SSBO writes and SSBO read-while-bound. |
| `ConcurrentCompute` | [vktComputeBasicComputeShaderTests.cpp#L4091-L4551](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4091-L4551) | Concurrent compute queue ordering. |
| `ReplicatedCompositesTest` | [vktComputeBasicComputeShaderTests.cpp#L5339-L5858](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5339-L5858) | Replicated composites per composite type and instantiation mode. |
| `DispatchBaseTest`, `DeviceIndexTest`, `SequentialDispatchTest` | [vktComputeBasicComputeShaderTests.cpp#L3276-L4089](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3276-L4089), [vktComputeBasicComputeShaderTests.cpp#L3582-L3794](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3582-L3794) | Device-group dispatch base, maintenance5 variant, device index, dispatch sequencing. |
| `SecondaryCommandBufferComputeOnlyTest` | [vktComputeBasicComputeShaderTests.cpp#L5137-L5338](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5137-L5338) | Compute-only queue with secondary command buffers. |
| `UndefinedValues` | [vktComputeBasicComputeShaderTests.cpp#L5861-L5982](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5861-L5982) | Defined/undefined values via struct assignment in a 1.2+ shader. |
| `EmptyShaderTest` | [vktComputeBasicComputeShaderTests.cpp#L4982-L5029](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4982-L5029) | Empty shader dispatch smoke. |
| Category dispatcher | [vktComputeTests.cpp#L48-L85](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85) | `pipeline` / `shader_object_spirv` / `shader_object_binary` roots. |
| Header | [vktComputeBasicComputeShaderTests.hpp#L37-L42](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.hpp#L37-L42) | Factory declarations for the three families. |