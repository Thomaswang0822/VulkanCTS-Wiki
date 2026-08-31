## Overview

**Core question:** Do shader image operations produce the four expected validation samples under each tested protection mode?

- `vktProtectedMemShaderImageAccessTests.cpp` implements the `protected_memory.image.access` test family documented here.
- Its fragment and compute pipelines exercise sampled-image reads, texel fetches, storage-image loads and stores, and signed or unsigned image atomics.
- The matrix checks ordinary pipelines, pipelines restricted by `VK_EXT_pipeline_protected_access`, and two maintenance5 pipeline-flag cases.
- Results are sampled on the device, so protected pixels never need to become host-visible. A protected compute validator turns a mismatch into a timeout that the host can observe.

## Background Knowledge

For the shared concepts protected memory, protected submission, and device-side validation boundaries, see [Background Knowledge](../../categories/protected_memory.md#background-knowledge) of the `protected_memory` page.

- **Sampled and storage images:** `texture` and `texelFetch` use a combined image sampler. `imageLoad`, `imageStore`, and image atomics use storage images with format-qualified GLSL declarations and `VK_IMAGE_LAYOUT_GENERAL`.
- **Pipeline access restrictions:** With `pipelineProtectedAccess`, `VK_PIPELINE_CREATE_PROTECTED_ACCESS_ONLY_BIT_EXT` restricts a pipeline to protected command buffers, while `VK_PIPELINE_CREATE_NO_PROTECTED_ACCESS_BIT_EXT` restricts it to unprotected command buffers.

## Registration Hierarchy

```text
protected_memory.image.access
├── fragment
├── compute
└── misc
```

`fragment` and `compute` own the generated access matrix. The non-Vulkan-SC `misc` branch contains two maintenance5 cases.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Shader stage | `fragment`, `compute` | Selects a graphics draw or a one-invocation-per-texel compute dispatch using the case's protection mode. | [shader-stage registration](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1255-L1264) |
| Pipeline access mode | `default`, `protected_access` | `protected_access` requests `VK_EXT_pipeline_protected_access`; `default` uses the ordinary protected-memory path. | [mode registration](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1293-L1302), [instance construction](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L526-L533) |
| Pipeline flag | `none`, `protected_access_only`, `no_protected_access` | Restricts where the pipeline can be bound. `no_protected_access` also selects unprotected resources, command buffers, and submission. | [flag registration and protection mode](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L112-L129), [flag values](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1303-L1313) |
| Access type | `sampling`, `texelfetch`, `imageload`, `imagestore`, `imageatomics` | Changes shader instructions, descriptors, layouts, resource topology, and expected image contents. | [access registration](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1266-L1281) |
| Image format | `rgba8`, `r32i`, `r32ui` | Controls the Vulkan format, GLSL image/sampler type, output vector type, and comparison values. | [format registration](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1283-L1291), [shader type specialization](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L347-L355) |
| Atomic operation | `add`, `min`, `max`, `and`, `or`, `xor`, `exchange` | Selects the image atomic instruction and the matching CPU reference calculation. | [operation names and shader functions](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L138-L184), [reference calculation](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L186-L209) |
| Maintenance5 case | `maintenance5_protected_access`, `maintenance5_no_protected_access` | Creates compute image-load pipelines with flags supplied through `VkPipelineCreateFlags2CreateInfoKHR`. | [misc registration](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1389-L1401), [flags2 pipeline creation](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L777-L797) |

The Vulkan mustpass list contains 198 paths for this family: 104 fragment cases, 92 compute cases, and two `misc` cases. Image atomics account for 112 paths because seven operations are crossed with signed and unsigned formats.

## Behavior Parameters

The primary behavioral axis is the access type. It changes the image instruction being tested and the route by which the shader result becomes an image that the validator can sample.

### `sampling`: normalized sampled-image lookup

The shader calls `texture` through a combined image sampler with nearest filtering. Fragment cases write the sampled value to the color attachment; compute cases store it in a result storage image.

### `texelfetch`: integer-coordinate sampled-image lookup

The shader calls `texelFetch` at LOD zero. The fragment path receives texel-scale coordinates from the quad, while the compute path uses the global invocation coordinate.

### `imageload`: storage-image read

The shader reads a format-qualified storage image with `imageLoad`. Fragment output goes to the color attachment; compute output goes to a separate storage image.

### `imagestore`: storage-image copy

The fragment shader loads one storage image and stores the value into another, with both resources using the case's protection mode. Compute `imagestore` is intentionally omitted because another protected-memory test covers that operation; the compute image-load path already writes its loaded value to a result image.

### `imageatomics`: in-place storage-image update

Each shader invocation applies one of seven atomic operations to the red component of the case's source/result image at its coordinate, using `x*x + y*y` as the argument. The operation runs on `r32i` or `r32ui`; the host applies the same operation to its reference texture before validation.

## Shader Analysis

One compute signed atomic-add case represents the most demanding single shader path: it performs coherent read-modify-write access directly on a protected storage image, maps every invocation to one texel, and has an exact CPU-side reference. The fragment and non-atomic branches use the same generator and validation framework; their differences appear in the variation table.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.protected_memory.image.access.compute.default.none.imageatomics.add.r32i
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | A `128 × 128 × 1` dispatch runs one local-size-one invocation for every texel. |
| `default.none` | The case uses the ordinary protected pipeline path without a pipeline access restriction flag. |
| `imageatomics.add.r32i` | The shader performs signed 32-bit `imageAtomicAdd` on a coherent `r32i` storage image. |

#### Purpose

This shader checks that a compute invocation can atomically add a coordinate-derived signed value to each texel of a protected storage image. The resulting protected image must match the host-computed reference at the validator's sampled coordinates.

#### Structural Design

| Phase | Shader action | Observable consequence |
|-------|---------------|------------------------|
| Address | Read `gl_GlobalInvocationID.x/y` as `gx` and `gy`. | Each invocation selects one unique image coordinate. |
| Compute | Form `gx*gx + gy*gy` as a signed integer. | The atomic argument is deterministic and coordinate-dependent. |
| Update | Call `imageAtomicAdd` on `u_resultImage`. | The protected source image is modified in place for later validation. |

#### Shader Code

```glsl
#version 450
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 is the protected r32i storage image. Each invocation atomically updates one texel in place.
layout(set = 0, binding = 0, r32i) coherent uniform highp iimage2D u_resultImage;

void main() {
    /// The 128 x 128 dispatch uses one invocation per texel.
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);
    /// The signed atomic-add argument matches the host reference calculation for coordinate (gx, gy).
    imageAtomicAdd(u_resultImage, ivec2(gx, gy), int(gx*gx + gy*gy));
}
```

#### Additional Info

- `ImageAccessTestCase::initPrograms()` uses the default `vk::SourceCollections` build target for this shader, so the disassembly target is SPIR-V 1.0.
- The shader ignores the atomic instruction's returned old value. Validation checks the final protected image after every texel has received exactly one update.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Shader stage | Fragment cases use interpolated `v_texCoord`, write `o_color`, and may use a separate destination image; a fixed vertex shader supplies the quad coordinates. | [fragment generator](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L359-L449) |
| Access type | `sampling` emits `texture`; `texelfetch` emits `texelFetch`; `imageload` emits `imageLoad`; `imagestore` emits paired `imageLoad`/`imageStore`; atomics substitute the selected image atomic function. | [fragment access branches](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L383-L438), [compute access branches](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L460-L509) |
| Image format | `rgba8` uses `image2D`/`sampler2D` and `vec4`; `r32i` uses signed image/sampler types and `ivec4`; `r32ui` uses unsigned types and `uvec4`. | [format/type specialization](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L347-L355), [qualifier helpers](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L211-L295) |
| Atomic operation | The generated call changes among `imageAtomicAdd`, `Min`, `Max`, `And`, `Or`, `Xor`, and `Exchange`; the coordinate-derived argument stays the same. | [atomic function mapping](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L162-L184), [generated calls](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L425-L432) |
| Pipeline mode and flag | These choices do not change GLSL. They change pipeline creation flags, required extension support, resource protection mode, and command-buffer/submission protection. | [support and instance setup](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L329-L340), [compute pipeline creation](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L777-L811) |

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
; Bound: 41
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
               OpName %u_resultImage "u_resultImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %u_resultImage Coherent
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
         %23 = OpTypeImage %int 2D 0 0 0 2 R32i
%_ptr_UniformConstant_23 = OpTypePointer UniformConstant %23
%u_resultImage = OpVariable %_ptr_UniformConstant_23 UniformConstant
      %v2int = OpTypeVector %int 2
%_ptr_Image_int = OpTypePointer Image %int
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %gx = OpVariable %_ptr_Function_int Function
         %gy = OpVariable %_ptr_Function_int Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %16 = OpLoad %uint %15
         %17 = OpBitcast %int %16
               OpStore %gx %17
         %20 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %21 = OpLoad %uint %20
         %22 = OpBitcast %int %21
               OpStore %gy %22
         %26 = OpLoad %int %gx
         %27 = OpLoad %int %gy
         %29 = OpCompositeConstruct %v2int %26 %27
         %30 = OpLoad %int %gx
         %31 = OpLoad %int %gx
         %32 = OpIMul %int %30 %31
         %33 = OpLoad %int %gy
         %34 = OpLoad %int %gy
         %35 = OpIMul %int %33 %34
         %36 = OpIAdd %int %32 %35
         %38 = OpImageTexelPointer %_ptr_Image_int %u_resultImage %29 %uint_0
         %39 = OpAtomicIAdd %int %38 %uint_1 %uint_0 %36
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a deterministic `128 × 128` CPU texture. Atomic cases use red-channel values in a reduced range; other cases use the format's value range.
- It uploads that texture to an unprotected image, then copies the image into the protected or unprotected source selected by the case's protection mode. Sampled accesses use `SHADER_READ_ONLY_OPTIMAL`; storage accesses use `GENERAL`.
- Compute cases bind a result storage image at binding 0 and the source sampler or storage image at binding 1. Atomic cases bind only the in-place source/result image at binding 0. The host dispatches `128 × 128 × 1` workgroups.
- Fragment cases render a four-vertex triangle strip into a color attachment created with the case's protection mode. Sampling and fetch cases bind a combined sampler; storage loads bind one storage image; stores bind source and destination storage images; atomics bind the in-place image.
- `imageatomics` cases update the CPU reference with the same operation and `x*x + y*y` argument used by the shader.
- The result image is the compute destination, fragment color attachment, fragment store destination, or atomically updated source, depending on the access type.
- `validateResult()` chooses four deterministic normalized coordinates and expected samples. `ImageValidator` samples the result image at those coordinates and compares every component with threshold `0.1`.
- A mismatch calls `error()`, whose zero-increment loop prevents the validation dispatch from finishing. A one-second queue-submission timeout returns failure; a completed submission passes.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sampling` | Sampled-image access in the selected protection mode, normalized-coordinate sampling, descriptor/layout handling, or result validation produced unexpected values. |
| `texelfetch` | Sampled-image texel fetch in the selected protection mode, integer coordinate handling, descriptor/layout handling, or result validation produced unexpected values. |
| `imageload` | Storage-image reads in the selected protection mode, storage-image format/descriptor handling, result writes, or validation produced unexpected values. |
| `imagestore` | The fragment path failed to copy values between storage images using the selected protection mode, or the destination image was not made available for validation. |
| `imageatomics` | A storage-image atomic operation in the selected protection mode, coherent image access, format-specific signedness, or CPU reference calculation disagreed with the validated image. |

### Cause Analysis

#### Sampled-image access or coordinate failure

**Possible failure symptoms:** `sampling` or `texelfetch` times out during validation because one of the four sampled result values differs from the reference by more than `0.1`. Failures may separate normalized sampling from integer texel fetch, or may affect one format or shader stage.

**Possible implementation causes:** The sampled-image instruction, descriptor interpretation, image layout transition, sampler state, or fragment/compute coordinate path may return the wrong texel. Vulkan requires protected data to remain device-only, but protected image sampling must still obey the ordinary image and sampler semantics used by a valid protected operation.

#### Storage-image load, store, or result visibility failure

**Possible failure symptoms:** `imageload` produces an incorrect color/result image, or fragment `imagestore` leaves the destination image different from the source at a validated coordinate.

**Possible implementation causes:** A storage-image format qualifier or descriptor may be handled incorrectly, the generated image load/store may target the wrong binding or coordinate, or synchronization may fail to make shader writes visible to the later protected validator. The source uses `GENERAL` layout for storage access and selects the actual destination image for validation.

#### Image atomic or signedness failure

**Possible failure symptoms:** One or more atomic operations fail only for `r32i` or `r32ui`, or the final red component does not equal the operation applied to the initial value and `x*x + y*y`.

**Possible implementation causes:** The image atomic instruction may implement the wrong operation, signed/unsigned comparison behavior for `min` or `max` may be wrong, coherent storage-image access may be mishandled, or shader lowering may use an incorrect image format/type. A broad failure shared by all atomic cases can also originate in the in-place result-image path or validator input rather than the atomic ALU operation itself.

#### Pipeline protection-mode or maintenance5 failure

**Possible failure symptoms:** Cases differ by `default`, `protected_access_only`, `no_protected_access`, or the maintenance5 `flags2` path even though their image operation and expected pixels match.

**Possible implementation causes:** Pipeline access flags may be applied incorrectly, a pipeline may be bound to a command buffer with the wrong protection status, or the CTS runtime path may create resources/submissions inconsistent with `Params::protectionMode`. Maintenance5-only failures point to pipeline flag transport through `VkPipelineCreateFlags2CreateInfoKHR`; source-level investigation is needed to distinguish CTS setup from implementation handling.

#### Protected validation-path failure

**Possible failure symptoms:** Many unrelated access types time out together, including cases whose shader operations differ, because the four-point validator does not complete.

**Possible implementation causes:** The protected validator's sampled-image descriptor, protected helper SSBO, reference uniform, protected submission, or timeout signaling may be wrong. Since the host observes only completion or timeout and does not read the result pixels, a shared validator failure can mask a correct access shader.

## Case Pruning

### Requirement-based pruning

- All cases require protected-context support. Cases whose pipeline uses protected-access restrictions also require `VK_EXT_pipeline_protected_access` through the protected test instance.
- The two `misc` cases require `VK_KHR_maintenance5` and are absent from Vulkan SC.
- Image atomics use only `VK_FORMAT_R32_SINT` and `VK_FORMAT_R32_UINT`; `rgba8` is not registered for atomic operations.
- Vulkan SC registers only `default.none` paths because extension pipeline-access modes and flags are compiled out.

### Design-based pruning

- A pipeline flag other than `none` is not combined with the `default` access mode. Restriction flags are meaningful only in the `protected_access` branch.
- Compute `imagestore` is omitted because the source marks it as already covered by other tests. The compute `imageload` path still uses `imageStore` to expose the loaded value in its result image.
- Non-atomic accesses do not add an atomic-operation intermediate node. Atomic cases add exactly one of seven operations and then the signed or unsigned format leaf.
- The `misc` maintenance5 branch fixes stage, access type, and format to compute image-load with `rgba8`; it isolates the pipeline-flags2 mechanism instead of duplicating the full matrix.

## Key Takeaways

- `vktProtectedMemShaderImageAccessTests.cpp` generates both shader paths and registers the complete family.
- Access type controls the shader instruction, descriptor and layout model, result image, and expected-value calculation.
- Pipeline access flags change pipeline and submission compatibility rather than GLSL. The maintenance5 cases test pipeline flag transport through `VkPipelineCreateFlags2CreateInfoKHR`.
- Image atomic cases update one texel per invocation and compare against a CPU calculation of the same signed or unsigned operation.
- The validator reports an image mismatch through a timeout instead of copying result pixels to the host; this keeps protected results device-only while using one observation path for both protection modes. See `## Failure Meaning` when unrelated cases share that symptom.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter definitions and helpers | [vktProtectedMemShaderImageAccessTests.cpp#L57-L295](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L57-L295) | Defines access types, atomic operations, image qualifiers, and protection mode. |
| Shader builder | [ImageAccessTestCase::initPrograms()](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L347-L524) | Generates fragment, compute, and fixed vertex GLSL. |
| Compute runtime | [executeComputeTest()](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L574-L824) | Creates resources and descriptors, dispatches, and chooses the compute result image. |
| Fragment runtime | [executeFragmentTest()](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L826-L1208) | Creates the graphics path, draws, synchronizes, and chooses the fragment result image. |
| Reference and final check | [calculateAtomicRef() and validateResult()](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1210-L1247) | Computes atomic expectations and selects four validation samples. |
| Registration and pruning | [createShaderImageAccessTests()](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1251-L1404) | Builds the exact Vulkan and Vulkan SC hierarchy. |
| Validator shader generation | [ImageValidator::initPrograms()](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Generates comparison and timeout-signaling shaders. |
| Validator runtime | [ImageValidator::validateImage()](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Binds validation resources and maps timeout to failure. |
| Protected transfer and submission helpers | [vktProtectedMemUtils.cpp#L460-L495](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L495), [vktProtectedMemUtils.cpp#L748-L839](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L748-L839) | Marks protected submissions and copies uploaded data into the target image. |
| Protected memory specification | [memory.adoc#L5564-L5653](../../../../vulkan-docs/src/chapters/memory.adoc#L5564-L5653) | Defines protected memory, command, queue, and access rules. |
| Pipeline access restrictions | [pipelines.adoc#L758-L763](../../../../vulkan-docs/src/chapters/pipelines.adoc#L758-L763) | Defines where protected-only and no-protected-access pipelines may be bound. |
| Vulkan mustpass paths | [protected-memory.txt#L407-L604](../../../mustpass/main/vk-default/protected-memory.txt#L407-L604) | Lists the 198 registered Vulkan cases in this family. |
