## Overview

**Core question:** Does a partially resident multisampled storage image return the selected sample count from bound tiles and zero from its unbound tile row?

- `vktSparseResourcesMultisampledImageSparseResidency.cpp` registers the `sparse_resources.multisampled_image_sparse_residency` test family.
- Each test case uses a 2D `256x512x1` image, one mip level, one array layer, one of 11 formats, and 2, 4, 8, or 16 samples.
- The test binds every sparse tile except the lowest row. A compute shader writes the sample count, loads the image with sparse residency operations, and records either that value or zero in an `r32ui` result image.
- The host copies the result image to a buffer and checks the bound and unbound regions separately.

## Background Knowledge

- Sparse image residency allows an image to exist while only selected image tiles have memory bound. This test relies on `residencyNonResidentStrict`, which requires nonresident accesses to have the strict behavior checked here.
- A multisampled storage image stores multiple samples per pixel. The shader addresses sample 0 of an `image2DMS`; the selected sample count is still the value written and expected in the bound region.
- `sparseImageLoadARB` returns a residency status as well as the loaded value. The generated shader uses `sparseTexelsResidentARB` to turn a nonresident load into zero before writing the result image.

## Registration Hierarchy

```text
sparse_resources.multisampled_image_sparse_residency
├── rgba32f
├── rgba16f
├── r32f
├── rgba32ui
├── rgba16ui
├── rgba8ui
├── r32ui
├── rgba32i
├── rgba16i
├── rgba8i
└── r32i
```

Each format group contains `samples_2`, `samples_4`, `samples_8`, and `samples_16` test cases.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Format | `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R16G16B16A16_SFLOAT`, `VK_FORMAT_R32_SFLOAT`, the four listed `UINT` formats, and the four listed `SINT` formats | Selects the storage-image type and format-specific GLSL prefix. | [`createSparseResourcesMultisampledImageResidencyCommonTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L769-L801) |
| Sample count | `samples_2`, `samples_4`, `samples_8`, `samples_16` | Selects the multisample count and the matching sparse-residency feature. | [`getDeviceCoreFeature`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L71-L89), [`createSparseResourcesMultisampledImageResidencyCommonTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L780-L797) |
| Image shape | `256x512x1`, 2D, one mip level, one array layer | Fixes the image and result-buffer extents for every case. | [`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L343-L360) |
| Residency layout | All tiles except the lowest row are bound | Separates resident values from strict nonresident values. | [`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L383-L444) |

## Behavior Parameters

The behavioral axis is the registered format/sample-count test case. Format changes the typed multisampled image access; sample count changes both the required device feature and the value expected in resident elements. Every combination uses the same image shape and partial-residency layout.

### Format groups

Floating-point groups are `rgba32f`, `rgba16f`, and `r32f`. Unsigned integer groups are `rgba32ui`, `rgba16ui`, `rgba8ui`, and `r32ui`. Signed integer groups are `rgba32i`, `rgba16i`, `rgba8i`, and `r32i`. The generated shader uses no GLSL type prefix for floating-point formats, `u` for unsigned formats, and `i` for signed formats.

### Sample-count groups

Each format has `samples_2`, `samples_4`, `samples_8`, and `samples_16`. The shader writes the selected count to sample 0. Resident result elements therefore contain `2`, `4`, `8`, or `16` after conversion to the `r32ui` result image.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.sparse_resources.multisampled_image_sparse_residency.rgba32ui.samples_4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `rgba32ui` | Selects an unsigned four-component multisampled storage image, so the generated declaration is `uimage2DMS`, the payload variable is `uvec4`, and binding 0 uses the `rgba32ui` format qualifier. |
| `samples_4` | Selects four samples per pixel and emits `uvec4(4)` as the value written to sample 0 and expected from resident pixels. |
| `256x512x1` | Selects the fixed image extent and a matching 256×512×1 dispatch. With a 1×1×1 local size, each invocation addresses one pixel. |

#### Purpose

The compute shader writes the selected sample-count value to sample 0 of a partially resident multisampled image, loads that sample with sparse residency reporting, and writes either the loaded value or explicit zero to a fully backed result image. This makes resident and strict nonresident behavior visible to the host in one output.

#### Structural Design

| Phase | Shader operation | Result observed by the host |
|-------|------------------|-----------------------------|
| Coordinate mapping | Convert `gl_GlobalInvocationID.xy` to an `ivec2` | One invocation addresses one of the 256×512 pixels. |
| Multisample store | Write `uvec4(4)` to sample 0 of `u_msImage` | Resident pixels retain the selected sample-count payload. |
| Sparse reads | Issue the two generated `sparseImageLoadARB` calls; the second call supplies the final `color` and `code` | The returned status distinguishes backed pixels from the unbound lowest sparse-block row. |
| Residency decision | Replace `color` with `uvec4(0)` when `sparseTexelsResidentARB(code)` is false | Nonresident accesses become explicit zero rather than exposing the sparse-load value. |
| Result store | Convert/store `color` to the `r32ui` result image | Host readback expects `4` in the bound prefix and `0` in the unbound row. |

#### Shader Code

```glsl
#version 450

#extension GL_ARB_sparse_texture2 : require

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

/// Binding 0, set 0 is the host-created partially bound multisampled storage image. The rgba32ui format
/// makes each sample a uvec4; this representative case addresses sample 0 of every 256x512 pixel.
layout (set = 0, binding = 0, rgba32ui) uniform uimage2DMS u_msImage;
/// Binding 1, set 0 is a fully backed r32ui storage image. One uint per pixel carries the shader's
/// resident payload or explicit nonresident zero into host readback.
layout (set = 0, binding = 1, r32ui)  writeonly uniform uimage2D  u_resultImage;

void main (void)
{
    /// The 1x1x1 local size and 256x512x1 dispatch map one invocation directly to one pixel.
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);
    int gz = int(gl_GlobalInvocationID.z);

    /// Write the selected sample-count payload to sample 0. The unbound lowest sparse-block row has
    /// no backing allocation, while all rows above it are resident.
    imageStore(u_msImage, ivec2(gx, gy), 0,uvec4(4));
    uvec4 color;
    /// Preserve both generated sparse loads: the first result is discarded, and the second supplies
    /// the residency code and color used by the explicit resident/nonresident decision.
    sparseImageLoadARB(u_msImage, ivec2(gx, gy), 0, color);
    int code = sparseImageLoadARB(u_msImage, ivec2(gx, gy), 0, color);
    if (!sparseTexelsResidentARB(code)) {
        color = uvec4(0);
    }
    /// The host expects 4 in resident pixels and 0 in the unbound lowest sparse-block row.
    imageStore(u_resultImage, ivec2(gx, gy), uvec4(color));
}
```

#### Additional Info

- The duplicate sparse load is present in the CTS generator: the first status is discarded, while the second load overwrites `color` and returns the `code` used by the residency branch.
- `initPrograms` supplies no explicit `ShaderBuildOptions`, so the source collection baseline selects SPIR-V 1.0 for this shader.
- The result image is cleared before dispatch and fully memory-backed; zeros in its copied output therefore represent the shader's explicit nonresident branch for dispatched pixels.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Format | Changes the image format qualifier and the generated type prefix: floating-point formats use `image2DMS`/`vec4`, unsigned formats use `uimage2DMS`/`uvec4`, and signed formats use `iimage2DMS`/`ivec4`. The final store always converts the selected vector to `uvec4` for the `r32ui` result image. | [`getFormatPrefix`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L159-L182), [`MultisampledImageSparseResidencyCase::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L272-L307) |
| Sample count | Changes the scalar literal replicated into the stored vector from `4` to `2`, `8`, or `16`; all variants continue to address sample 0 and use the same sparse-load decision. | [`MultisampledImageSparseResidencyCase::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L292-L303), [`createSparseResourcesMultisampledImageResidencyCommonTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L769-L801) |
| Image extent and residency layout | Do not vary across registered cases, so the local size, coordinate construction, bindings, and control flow remain unchanged. | [`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L343-L444) |

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
               OpCapability StorageImageMultisample
               OpCapability SparseResidency
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_ARB_sparse_texture2"
               OpName %main "main"
               OpName %gx "gx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %gy "gy"
               OpName %gz "gz"
               OpName %u_msImage "u_msImage"
               OpName %color "color"
               OpName %ResType "ResType"
               OpName %code "code"
               OpName %u_resultImage "u_resultImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %u_msImage Binding 0
               OpDecorate %u_msImage DescriptorSet 0
               OpDecorate %u_resultImage NonReadable
               OpDecorate %u_resultImage Binding 1
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
     %uint_2 = OpConstant %uint 2
         %28 = OpTypeImage %uint 2D 0 0 1 2 Rgba32ui
%_ptr_UniformConstant_28 = OpTypePointer UniformConstant %28
  %u_msImage = OpVariable %_ptr_UniformConstant_28 UniformConstant
      %v2int = OpTypeVector %int 2
      %int_0 = OpConstant %int 0
     %v4uint = OpTypeVector %uint 4
     %uint_4 = OpConstant %uint 4
         %39 = OpConstantComposite %v4uint %uint_4 %uint_4 %uint_4 %uint_4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
    %ResType = OpTypeStruct %int %v4uint
       %bool = OpTypeBool
         %64 = OpConstantComposite %v4uint %uint_0 %uint_0 %uint_0 %uint_0
         %65 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_65 = OpTypePointer UniformConstant %65
%u_resultImage = OpVariable %_ptr_UniformConstant_65 UniformConstant
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %gx = OpVariable %_ptr_Function_int Function
         %gy = OpVariable %_ptr_Function_int Function
         %gz = OpVariable %_ptr_Function_int Function
      %color = OpVariable %_ptr_Function_v4uint Function
       %code = OpVariable %_ptr_Function_int Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %16 = OpLoad %uint %15
         %17 = OpBitcast %int %16
               OpStore %gx %17
         %20 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %21 = OpLoad %uint %20
         %22 = OpBitcast %int %21
               OpStore %gy %22
         %25 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %26 = OpLoad %uint %25
         %27 = OpBitcast %int %26
               OpStore %gz %27
         %31 = OpLoad %28 %u_msImage
         %32 = OpLoad %int %gx
         %33 = OpLoad %int %gy
         %35 = OpCompositeConstruct %v2int %32 %33
               OpImageWrite %31 %35 %39 Sample %int_0
         %40 = OpLoad %28 %u_msImage
         %41 = OpLoad %int %gx
         %42 = OpLoad %int %gy
         %43 = OpCompositeConstruct %v2int %41 %42
         %47 = OpImageSparseRead %ResType %40 %43 Sample %int_0
         %48 = OpCompositeExtract %v4uint %47 1
               OpStore %color %48
         %49 = OpCompositeExtract %int %47 0
         %51 = OpLoad %28 %u_msImage
         %52 = OpLoad %int %gx
         %53 = OpLoad %int %gy
         %54 = OpCompositeConstruct %v2int %52 %53
         %55 = OpImageSparseRead %ResType %51 %54 Sample %int_0
         %56 = OpCompositeExtract %v4uint %55 1
               OpStore %color %56
         %57 = OpCompositeExtract %int %55 0
               OpStore %code %57
         %58 = OpLoad %int %code
         %60 = OpImageSparseTexelsResident %bool %58
         %61 = OpLogicalNot %bool %60
               OpSelectionMerge %63 None
               OpBranchConditional %61 %62 %63
         %62 = OpLabel
               OpStore %color %64
               OpBranch %63
         %63 = OpLabel
         %68 = OpLoad %65 %u_resultImage
         %69 = OpLoad %int %gx
         %70 = OpLoad %int %gy
         %71 = OpCompositeConstruct %v2int %69 %70
         %72 = OpLoad %v4uint %color
               OpImageWrite %68 %71 %72
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. The case checks `sparseBinding`, `sparseResidencyImage2D`, the feature matching its sample count, `shaderStorageImageMultisample`, and `shaderResourceResidency`. It also requires `residencyNonResidentStrict`, a supported 2D image size and format, and a sparse image memory footprint within `sparseAddressSpaceSize` ([`MultisampledImageSparseResidencyCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L235-L270), [`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L362-L390)).
2. The instance creates separate sparse-binding and compute queues, then creates the 2D image with `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT | VK_IMAGE_CREATE_SPARSE_BINDING_BIT` and `VK_IMAGE_USAGE_STORAGE_BIT`.
3. It queries sparse image granularity and binds tiles through the image granularity range except for the lowest row. A sparse-bind semaphore and an empty sparse-queue submission provide completion before compute work ([`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L392-L457)).
4. The compute submission clears the result image, transitions both images to `VK_IMAGE_LAYOUT_GENERAL`, binds the descriptor set and compute pipeline, and dispatches `imgSize.x`, `imgSize.y`, and `imgSize.z` workgroups.
5. The submission transitions the result image for transfer, copies it to a host-visible buffer, waits for the compute queue, and invalidates the allocation before reading it back ([`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L509-L597)).
6. The test expects every element in the bound prefix to equal `m_params.sampleCount` and every element in the unbound lowest-row suffix to equal zero. A single mismatch returns `tcu::TestStatus::fail("Failed")` ([`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L598-L621)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any format with `samples_2`, `samples_4`, `samples_8`, or `samples_16` | Sparse multisampled image creation or binding, sample-count support, storage-image access, sparse shader load, synchronization, result copyback, or host validation does not produce the expected values. |
| Floating-point format value | Format-specific storage-image or conversion behavior may affect the value written to the `r32ui` result image. |
| Unsigned or signed integer format value | Format-specific shader type selection, storage-image access, or conversion to the unsigned result image may be incorrect. |

### Cause Analysis

#### Sparse binding or image access

**Possible failure symptoms:** A resident result element is not equal to the selected sample count, or a nonresident result element is not zero.

**Possible implementation causes:** The sparse bind may cover the wrong tile range or image subresource. The image layout transition, sparse-queue completion, compute access, or result-image copy may also expose incorrect data. The failing case and test log are needed to identify the exact layer.

#### Sample-count feature or multisampled storage-image support

**Possible failure symptoms:** A case is rejected during support checks, or its resident values fail for one sample-count group while other groups pass.

**Possible implementation causes:** The implementation may report image format sample counts or sample-count-specific sparse residency features incorrectly, or may mishandle multisampled storage-image access for the selected count. The exact cause requires the device feature and format-property report.

#### Format-specific shader access or result conversion

**Possible failure symptoms:** Failures are limited to floating-point, unsigned-integer, or signed-integer format groups while the residency layout and sample count otherwise pass.

**Possible implementation causes:** The generated GLSL type prefix, typed `image2DMS` access, conversion to `uimage2D`, or format handling may produce a value different from the expected unsigned result. The failing format identifies the relevant typed-access path, but source-level investigation and the test log are needed to locate the defect.

## Case Pruning

### Requirement-based pruning

Support checks remove cases when the device lacks sparse binding, 2D sparse image residency, the feature for the selected sample count, multisampled storage-image support, shader resource residency, strict nonresident behavior, supported image format or size, sparse image support for the requested create info, or enough sparse address space. A case also fails support when no suitable memory type is available ([`MultisampledImageSparseResidencyCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L235-L270), [`MultisampledImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L362-L399)).

### Design-based pruning

The matrix deliberately fixes the image to one 2D extent, one mip level, and one array layer. It tests sample counts from 2 through 16 and leaves one complete lowest tile row unbound instead of generating fully resident or other partial layouts. The source registers no `samples_1` case.

## Key Takeaways

- The test checks resident and strict nonresident behavior in one multisampled storage-image access path.
- The sample count is both a feature-gating dimension and the expected value in resident result elements.
- The format groups exercise floating-point, unsigned-integer, and signed-integer typed image accesses through the same residency layout.
- A failure can come from sparse binding, multisampled image access, shader residency handling, queue synchronization, copyback, or host validation; the failing format and sample-count case narrow the investigation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `createSparseResourcesMultisampledImageResidencyCommonTests` | [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L769-L803) | Registers the 11 format groups and four sample-count cases per format. |
| `MultisampledImageSparseResidencyCase::checkSupport` | [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L235-L270) | Defines the feature, format, size, and strict-residency gates. |
| `MultisampledImageSparseResidencyCase::initPrograms` | [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L272-L307) | Generates the sparse multisampled-image compute shader. |
| `MultisampledImageSparseResidencyInstance::iterate` | [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L321-L621) | Creates resources, binds partial residency, dispatches compute, copies back, and checks results. |
| Shared sparse helpers | [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L161-L204), [`vktSparseResourcesBase.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.hpp#L59-L114) | Provide sparse-resource support and instance infrastructure used by the test. |
