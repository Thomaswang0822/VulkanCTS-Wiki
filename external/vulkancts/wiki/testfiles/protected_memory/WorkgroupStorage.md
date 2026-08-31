## Overview

**Core question:** Can protected compute workgroups exchange image data through `shared` storage and preserve the expected result for each tested storage size?

- This page covers the implementation in `vktProtectedMemWorkgroupStorageTests.cpp` and the `protected_memory.workgroupstorage` test family.
- The six test case leaves use `sharedMemorySize` values of `1`, `4`, `5`, `60`, `101`, and `503`.
- Each case generates one compute shader, dispatches one protected local workgroup, and checks a cyclic permutation of an RGBA8 image.
- The page explains the generated shader, the protected image setup, limit-based pruning, and how the validator turns a mismatch into a test failure.

## Background Knowledge

- A compute local workgroup is a set of shader invocations that can exchange data through GLSL `shared` variables. A barrier supplies the control-flow and memory ordering needed before invocations read values written by other invocations. See the Vulkan description of [local workgroups and shared variables](../../../../vulkan-docs/src/chapters/shaders.adoc#L2419-L2429).
- `maxComputeSharedMemorySize` limits the total bytes available to compute-shader Workgroup storage, while `maxComputeWorkGroupInvocations` limits the number of invocations in one local workgroup. The test checks both limits before dispatch. See the Vulkan [compute limits](../../../../vulkan-docs/src/chapters/limits.adoc#L499-L510).
- Protected images and a protected queue keep the compute work inside the protected execution path. The source setup uses an unprotected image only as a staging source before copying its contents into the protected source image.

## Registration Hierarchy

```text
protected_memory.workgroupstorage
├── memsize_1
├── memsize_4
├── memsize_5
├── memsize_60
├── memsize_101
└── memsize_503
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `sharedMemorySize` | `1`, `4`, `5`, `60`, `101`, `503` | Sets the length of `sharedData`, the cyclic-index modulus, and the minimum image area | [`createWorkgroupStorageTests()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L370-L383) |
| Generated image width | `1`, `2`, `4`, `8`, `16`, `32` | Alternates with height doubling until the image area covers the selected shared-memory size | [`Params` constructor](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L58-L80) |
| Generated image height | `1`, `1`, `2`, `8`, `8`, `16` | Determines the local workgroup's Y dimension and the source/destination image extent | [`Params` constructor](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L64-L79) |
| Local workgroup invocations | `1`, `4`, `8`, `64`, `128`, `512` | One invocation handles one image coordinate; the value is checked against `maxComputeWorkGroupInvocations` | [`Params` and limit checks](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L58-L80) and [`iterate()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L225-L231) |
| Workgroup storage footprint | `16`, `64`, `80`, `960`, `1616`, `8048` bytes | `sharedData` contains `vec4` values, so the source check multiplies the element count by 16 bytes | [`initPrograms()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L137-L146) and [`iterate()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L225-L227) |
| Image format | `VK_FORMAT_R8G8B8A8_UNORM` | Gives both protected images four normalized 8-bit channels and selects the validator format | [`WorkgroupStorageTestCase`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L103-L129) and [`iterate()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L233-L243) |

## Behavior Parameters

The primary behavioral axis is `sharedMemorySize`. It changes the shader's Workgroup storage declaration and the image-to-shared-memory mapping. The dimensions are derived execution parameters, not separate behavior choices.

### `1` (Single-element workgroup storage)

The shader uses a 1x1 local workgroup and one `vec4` shared element. The successor index wraps to the same element, so this case checks the smallest legal shared-memory path and the barrier even though the source and output coordinate are the same.

### `4` (Exact 2x2 mapping)

The 2x2 local workgroup has exactly four invocations and four shared elements. Every invocation writes one element, and the output reads the next element in row-major linear order.

### `5` (Non-square mapping with unused slots)

The derived grid is 4x2, giving eight invocations for five shared elements. Invocations with `idx0 >= 5` skip the write, while every invocation reads an index in `[0, 4]` because `idx1` is computed modulo five. This case exercises the guard and the non-square grid together.

### `60` (Larger 8x8 mapping)

The 8x8 grid provides 64 invocations for 60 shared elements. The shader uses the same guarded write and cyclic read as the smaller cases, but with a larger Workgroup storage declaration.

### `101` (16x8 mapping)

The 16x8 grid provides 128 invocations for 101 shared elements. The case keeps the same shader algorithm while extending both the storage footprint and the number of local invocations.

### `503` (32x16 mapping)

The 32x16 grid provides 512 invocations for 503 shared elements. This is the largest registered storage and invocation path in the family.

## Shader Analysis

The shader is generated by `WorkgroupStorageTestCase::initPrograms()`. The representative walkthrough uses the smallest registered case because it shows the complete path without a large generated declaration. The other values preserve the same control flow while changing the local size and array length.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.protected_memory.workgroupstorage.memsize_1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `sharedMemorySize = 1` | Emits `shared vec4 sharedData[1]` and makes the cyclic successor read wrap to element zero |
| `imageWidth = 1`, `imageHeight = 1` | Emits a 1x1 local workgroup and one source and destination coordinate |
| `VK_FORMAT_R8G8B8A8_UNORM` | Matches the storage-image declarations and the host validator format |

#### Purpose

The compute shader copies a source image value into Workgroup storage, synchronizes the local workgroup, and writes the successor shared element to the protected destination image. With one element, the successor is the same element, making this the smallest direct check of the generated path.

#### Structural Design

| Phase | Shader operation | Observable role |
|-------|------------------|-----------------|
| Address | Read `gl_GlobalInvocationID` and calculate `idx0` | Maps the invocation to a source and destination texel |
| Load | `imageLoad(u_srcImage, ivec2(gx, gy))` | Gets the source RGBA value |
| Publish | Write `sharedData[idx0]` when `idx0 < s` | Places the value in Workgroup storage |
| Synchronize | `barrier()` | Orders the shared write before the shared read |
| Rotate | Read `sharedData[idx1]`, where `idx1 = (idx0 + 1) % s` | Selects the cyclic successor value |
| Store | `imageStore(u_resultImage, ivec2(gx, gy), outColor)` | Writes the result image |

#### Shader Code

```glsl
#version 450
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 is the protected destination storage image. The shader writes one RGBA8 value per invocation.
layout(set = 0, binding = 0, rgba8) writeonly uniform highp image2D u_resultImage;
/// Binding 1 is the protected source storage image. The shader reads the source value before publishing it to shared storage.
layout(set = 0, binding = 1, rgba8) readonly uniform highp image2D u_srcImage;
/// This shader-local array has one vec4 element for the representative case. It is not a descriptor-backed resource.
shared vec4 sharedData[1];

void main() {
    /// The generated local size makes these coordinates the only image coordinate in this case.
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);
    int s = 1;
    int idx0 = gy * 1 + gx;
    int idx1 = (idx0 + 1) % s;
    vec4 color = imageLoad(u_srcImage, ivec2(gx, gy));
    /// Guarded writes are retained for cases whose image area is larger than sharedMemorySize.
    if (idx0 < s)
    {
        sharedData[idx0] = color;
    }
    /// The barrier makes the cross-invocation shared-memory handoff visible before the read.
    barrier();
    vec4 outColor = sharedData[idx1];
    imageStore(u_resultImage, ivec2(gx, gy), outColor);
}
```

#### Additional Info

- The displayed GLSL is reconstructed from the C++ string builder. The test does not load a standalone shader source file.
- The source-generated comments preceding the builder are preserved in the source evidence: the shared array receives source image data, and the output uses data written by another invocation.
- The compiler target used for the representative artifact is SPIR-V 1.0 because this `SourceCollections` path supplies no explicit `ShaderBuildOptions` target.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `sharedMemorySize` | Changes the `sharedData` array length, integer modulus, and the storage-limit check | [`initPrograms()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L137-L168) |
| Derived image dimensions | Changes `local_size_x`, `local_size_y`, the row-major `idx0` multiplier, and image extent | [`Params` constructor](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L64-L79) |
| Oversized image area | Causes guarded writes for invocations whose `idx0` is outside the shared array, while `idx1` remains modulo `s` | [`initPrograms()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L148-L165) |

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
; Bound: 74
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %gx "gx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %gy "gy"
               OpName %s "s"
               OpName %idx0 "idx0"
               OpName %idx1 "idx1"
               OpName %color "color"
               OpName %u_srcImage "u_srcImage"
               OpName %sharedData "sharedData"
               OpName %outColor "outColor"
               OpName %u_resultImage "u_resultImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %u_srcImage NonWritable
               OpDecorate %u_srcImage Binding 1
               OpDecorate %u_srcImage DescriptorSet 0
               OpDecorate %u_resultImage NonReadable
               OpDecorate %u_resultImage Binding 0
               OpDecorate %u_resultImage DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
      %int_1 = OpConstant %int 1
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %39 = OpTypeImage %float 2D 0 0 0 2 Rgba8
%_ptr_UniformConstant_39 = OpTypePointer UniformConstant %39
 %u_srcImage = OpVariable %_ptr_UniformConstant_39 UniformConstant
      %v2int = OpTypeVector %int 2
       %bool = OpTypeBool
%_arr_v4float_uint_1 = OpTypeArray %v4float %uint_1
%_ptr_Workgroup__arr_v4float_uint_1 = OpTypePointer Workgroup %_arr_v4float_uint_1
 %sharedData = OpVariable %_ptr_Workgroup__arr_v4float_uint_1 Workgroup
%_ptr_Workgroup_v4float = OpTypePointer Workgroup %v4float
     %uint_2 = OpConstant %uint 2
   %uint_264 = OpConstant %uint 264
%u_resultImage = OpVariable %_ptr_UniformConstant_39 UniformConstant
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %gx = OpVariable %_ptr_Function_int Function
         %gy = OpVariable %_ptr_Function_int Function
          %s = OpVariable %_ptr_Function_int Function
       %idx0 = OpVariable %_ptr_Function_int Function
       %idx1 = OpVariable %_ptr_Function_int Function
      %color = OpVariable %_ptr_Function_v4float Function
   %outColor = OpVariable %_ptr_Function_v4float Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %16 = OpLoad %uint %15
         %17 = OpBitcast %int %16
               OpStore %gx %17
         %20 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %21 = OpLoad %uint %20
         %22 = OpBitcast %int %21
               OpStore %gy %22
               OpStore %s %int_1
         %26 = OpLoad %int %gy
         %27 = OpIMul %int %26 %int_1
         %28 = OpLoad %int %gx
         %29 = OpIAdd %int %27 %28
               OpStore %idx0 %29
         %31 = OpLoad %int %idx0
         %32 = OpIAdd %int %31 %int_1
         %33 = OpLoad %int %s
         %34 = OpSMod %int %32 %33
               OpStore %idx1 %34
         %42 = OpLoad %39 %u_srcImage
         %43 = OpLoad %int %gx
         %44 = OpLoad %int %gy
         %46 = OpCompositeConstruct %v2int %43 %44
         %47 = OpImageRead %v4float %42 %46
               OpStore %color %47
         %48 = OpLoad %int %idx0
         %49 = OpLoad %int %s
         %51 = OpSLessThan %bool %48 %49
               OpSelectionMerge %53 None
               OpBranchConditional %51 %52 %53
         %52 = OpLabel
         %57 = OpLoad %int %idx0
         %58 = OpLoad %v4float %color
         %60 = OpAccessChain %_ptr_Workgroup_v4float %sharedData %57
               OpStore %60 %58
               OpBranch %53
         %53 = OpLabel
               OpControlBarrier %uint_2 %uint_2 %uint_264
         %64 = OpLoad %int %idx1
         %65 = OpAccessChain %_ptr_Workgroup_v4float %sharedData %64
         %66 = OpLoad %v4float %65
               OpStore %outColor %66
         %68 = OpLoad %39 %u_resultImage
         %69 = OpLoad %int %gx
         %70 = OpLoad %int %gy
         %71 = OpCompositeConstruct %v2int %69 %70
         %72 = OpLoad %v4float %outColor
               OpImageWrite %68 %71 %72
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkProtectedContextSupport()` requires Vulkan 1.1, the protected-memory feature, and a queue with `VK_QUEUE_PROTECTED_BIT`. This family does not request YCbCr conversion or pipeline protected access.
- `createTestTexture2D()` allocates an RGBA8 texture with the derived dimensions and fills it with deterministic random color tiles using `deInt32Hash(sharedMemorySize)` as the seed.
- The test creates protected source and destination images with transfer, sampled, and storage usage. It uploads the host texture to an unprotected image, copies that image into the protected source image, and clears the protected destination image.
- Two storage-image descriptors are bound at set 0, bindings 0 and 1. Binding 0 is `u_resultImage`; binding 1 is `u_srcImage`. The test builds a compute pipeline, records one `cmdDispatch(1, 1, 1)`, and submits it on the protected queue.
- `calculateRef()` constructs the expected cyclic mapping on the host. It stores the source pixels in a vector of `sharedMemorySize` elements and sets each reference pixel to the element at `(y * width + x + 1) % sharedMemorySize`.
- `validateResult()` samples four deterministic normalized coordinates from the reference texture with nearest filtering. `ImageValidator` runs a protected compute validation pass and compares the destination image against those four values with a component threshold of `0.1`.
- A successful comparison returns `Pass`. A mismatch returns `Result validation failed`; an unsupported limit or support gate produces a not-supported result instead of executing the case.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `1` | Incorrect Workgroup storage declaration or access, barrier handling, protected image binding, or result validation for the 1x1 case |
| `4` | Incorrect Workgroup storage sizing, 2x2 invocation indexing, barrier handling, protected image binding, or result validation |
| `5` | Incorrect non-square grid handling or cyclic indexing when the 4x2 grid has more invocations than shared elements |
| `60` | Incorrect larger shared-memory declaration, 8x8 grid handling, protected dispatch, or result validation |
| `101` | Incorrect 16x8 grid handling, shared-memory sizing, protected dispatch, or result validation |
| `503` | Incorrect 32x16 grid handling, shared-memory sizing, protected dispatch, or result validation |
| Any value | A failure in protected resource creation, transfer synchronization, descriptor setup, queue submission, or the shared `ImageValidator` path |

### Cause Analysis

#### Workgroup storage or barrier behavior

**Possible failure symptoms:** The destination image contains a value other than the expected cyclic successor, so one or more of the four validator samples exceeds the `0.1` per-component threshold.

**Possible implementation causes:** The shader compiler or implementation may mishandle the Workgroup storage declaration, the `barrier()` control and memory operation, or the Workgroup pointer accesses. The source and SPIR-V show a Workgroup array, a guarded store, an `OpControlBarrier`, and a later Workgroup load. Further source-level investigation is needed to assign a failure to a particular implementation layer.

#### Grid dimensions and cyclic indexing

**Possible failure symptoms:** Failures cluster in `memsize_5`, `memsize_60`, `memsize_101`, or `memsize_503`, where the derived image area is larger than the shared element count, or the output samples do not match the host reference permutation.

**Possible implementation causes:** A mismatch between generated local dimensions, `idx0`, the `idx0 < s` guard, or the modulo calculation can skip the wrong writes or read the wrong shared element. The host reference uses the same row-major and modulo rules, so a discrepancy requires source-level investigation of shader generation, compilation, or dispatch indexing.

#### Protected resource and submission path

**Possible failure symptoms:** Image validation cannot obtain the expected protected destination contents, or the protected dispatch does not complete successfully before validation. The validator can return false on timeout or on a failed comparison.

**Possible implementation causes:** The protected feature or queue support is checked before execution. After that gate, a failure could involve protected image creation, image layout and transfer synchronization, storage-image descriptor updates, protected command submission, or completion of the protected queue. The inspected source identifies these operations but does not isolate a particular implementation cause.

#### Host reference or validator path

**Possible failure symptoms:** The test reports `Result validation failed` even when the compute output appears correct, or validation times out while running its protected checking dispatch.

**Possible implementation causes:** The reference image uses deterministic random tiles, nearest sampling, four generated coordinates, and a `0.1` threshold. A mismatch can therefore come from the host's expected permutation, coordinate or format handling, the shared `ImageValidator`, or the image contents. Distinguishing these requires inspecting the logged coordinates and values and then comparing the protected image at those samples.

## Case Pruning

### Requirement-based pruning

- `checkProtectedContextSupport()` rejects devices using an API version below Vulkan 1.1, devices without `protectedMemory`, and devices without a protected queue.
- Before resources are created, `iterate()` rejects a case when `maxComputeSharedMemorySize` is less than `sharedMemorySize * 4 * 4` bytes.
- `iterate()` also rejects a case when `maxComputeWorkGroupInvocations` is less than `imageWidth * imageHeight`.

### Design-based pruning

- The registered values are the complete six-element array `{1, 4, 5, 60, 101, 503}`. The source does not generate every possible shared-memory size.
- One dispatch is used for each case. The derived image area is rounded up to an alternating power-of-two grid, and invocations whose linear index is outside the selected shared-memory range intentionally skip the guarded write.

## Key Takeaways

- `sharedMemorySize` is the behavior axis because it changes the shader's Workgroup array and the cyclic mapping under test.
- The shader uses `barrier()` between the shared-memory write and read, then writes the successor value to a protected storage image.
- The non-power-of-two values test the guard and modulo behavior when the image has more invocations than shared elements.
- The host reference follows the same cyclic mapping, while `ImageValidator` checks four deterministic samples in the protected destination image.
- A pass covers generated shader construction, Workgroup storage access, the protected dispatch path, and the sampled result check together. See `## Failure Meaning` for how to separate those failure mechanisms during investigation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `Params` and `getSeedValue()` | [`parameter construction`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L58-L85) | Derives image dimensions and deterministic input generation |
| `WorkgroupStorageTestCase::initPrograms()` | [`compute shader generator`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L131-L169) | Emits the local size, storage images, Workgroup array, indexing, barrier, and stores |
| `WorkgroupStorageTestCase::checkSupport()` | [`support entry point`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L120-L124) | Connects the family to the protected-memory support checks |
| `WorkgroupStorageTestInstance::iterate()` | [`protected execution setup`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L194-L325) | Creates images and descriptors, dispatches protected compute work, and invokes validation |
| `WorkgroupStorageTestInstance::calculateRef()` | [`reference permutation`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L328-L343) | Computes the expected cyclic output |
| `WorkgroupStorageTestInstance::validateResult()` | [`result sampling`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L345-L366) | Chooses reference samples and maps the validator result to pass or fail |
| `createWorkgroupStorageTests()` | [`registration`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L370-L383) | Registers the six exact test case leaves |
| `checkProtectedContextSupport()` | [`protected support gate`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127) | Checks API version, protected memory, and protected queue support |
| `ImageValidator::validateImage()` | [`protected image validator`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L263) | Runs the protected validation shader and handles timeout and comparison results |
| Vulkan workgroup model | [`shader execution model`](../../../../vulkan-docs/src/chapters/shaders.adoc#L2419-L2429) | Defines shared variables and barriers within a local workgroup |
| Vulkan workgroup limit | [`compute shared-memory limit`](../../../../vulkan-docs/src/chapters/limits.adoc#L499-L510) | Defines the device limits used for pruning |
| Vulkan mustpass registration | [`vk-default protected-memory.txt`](../../../mustpass/main/vk-default/protected-memory.txt#L5995-L6000) | Lists all six `dEQP-VK.protected_memory.workgroupstorage` leaves |
| Vulkan SC mustpass registration | [`vksc-default protected-memory.txt`](../../../mustpass/main/vksc-default/protected-memory.txt#L4803-L4808) | Lists all six `dEQP-VKSC.protected_memory.workgroupstorage` leaves |
