## Overview

**Core question:** Can a compute shader preserve and reload a distinct value for every sample of a multisampled storage-image texel?

- [`vktImageMultisampleLoadStoreTests.cpp`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp) implements the `image.load_store_multisample` test family.
- Each case writes a coordinate- and sample-dependent value to every sample, reloads every sample in a second compute dispatch, and writes the number of matches to a checksum image.
- The page covers the registered matrix, the all-layer and single-layer array binding modes, generated shaders, host-side synchronization and readback, and the meaning of a checksum failure.

## Background Knowledge

For the shared concepts images, views, and formats; layouts and synchronization; and subresources and copies, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

### Explicit multisample storage-image access

A multisampled storage image holds several independent samples at one texel coordinate. The generated `imageStore` and `imageLoad` calls address a particular sample with an explicit integer sample index; they neither filter samples nor perform a Vulkan resolve. The test therefore checks the address `(texel coordinate, sample index)`, not a single resolved value per pixel.

## Registration Hierarchy

```text
image.load_store_multisample
├── 2d
└── 2d_array
```

Each image-type intermediate node contains format groups and `samples_<count>` test case leaves. In `2d_array`, each format has an all-layer group and a `<format>_single_layer` group.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image type | `2d`, `2d_array` | Chooses a one-layer 2D texture or a four-layer 2D-array texture. | [`textures`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L543-L549) |
| View binding | all layers; `<format>_single_layer` for `2d_array` | Chooses an array view and one z-sized dispatch, or a 2D view and one dispatch per layer. | [`insertImageViews()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L242-L264) |
| Sample count | `2`, `4`, `8`, `16`, `32`, `64` | Sets the number of `imageStore` and `imageLoad` operations each invocation performs. | [`samples`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L567-L570) |
| Format | `r32g32b32a32_sfloat`, `r16g16b16a16_sfloat`, `r32_sfloat`, `r32g32b32a32_uint`, `r16g16b16a16_uint`, `r8g8b8a8_uint`, `r32_uint`, `r32g32b32a32_sint`, `r16g16b16a16_sint`, `r8g8b8a8_sint`, `r32_sint`, `r8g8b8a8_unorm`, `r8g8b8a8_snorm`, and non-VulkanSC `a8_unorm` | Chooses image declaration type, value conversion, and comparison rule. | [`formats`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L551-L565) |

The factory fixes the 2D extent at 32x32x1 and the 2D-array extent at 32x32x4. The sample count and format groups are registered for every declared combination; the support check can skip a format/sample pair on a given device.

The default Vulkan mustpass file enumerates all 252 registered non-VulkanSC leaves: 84 `2d` cases and 168 `2d_array` cases, of which 84 use the `_single_layer` format-group suffix. The Vulkan SC mustpass file contains the corresponding 234 leaves after the six `a8_unorm` 2D and twelve `a8_unorm` array-mode cases are omitted by the `CTS_USES_VULKANSC` conditional.

## Behavior Parameters

The primary behavior parameter is image topology and array-view binding strategy. It changes the image-view type, dispatch shape, and source of the layer component of the pattern.

### `2d`: one 2D view

The case binds a 2D multisampled image view and dispatches `32 x 32 x 1` invocations. `gz` comes from `gl_GlobalInvocationID.z` and remains zero.

### `2d_array`: one all-layer array view

The case binds one 2D-array multisampled view covering four layers and dispatches `32 x 32 x 4` invocations. `gz` comes from `gl_GlobalInvocationID.z`, so the generated value differs by layer.

### `2d_array.<format>_single_layer`: one 2D view per layer

The host creates one 2D view, descriptor set, and constants-buffer slice per layer, then dispatches `32 x 32 x 1` once for each layer. The shader reads `u_layerNdx` at binding 0 for `gz`, preserving the same global pattern while exercising per-layer views and descriptors.

## Shader Analysis

The representative shader below is the store pass for `dEQP-VK.image.load_store_multisample.2d.r8g8b8a8_unorm.samples_4`. The load pass has the same coordinate and sample loop, but reads the image, compares each value with the generated expectation, and stores the success count in the checksum image.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.load_store_multisample.2d.r8g8b8a8_unorm.samples_4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `2d` | Uses an `image2DMS` and a one-layer `32 x 32 x 1` dispatch. |
| `r8g8b8a8_unorm` | Uses a formatted `rgba8` image declaration and scales the 0 through 31 pattern by `1 / 31`. |
| `samples_4` | Loops over sample indices 0 through 3 for every invocation. |

#### Purpose

The shader writes a different generated color to every sample of each 2D texel. The host later runs the generated load shader to verify that each explicit sample address returns the expected UNORM value.

#### Structural Design

| Phase | Shader action | Test relevance |
|-------|---------------|----------------|
| Address | Reads `gx`, `gy`, and `gz` from `gl_GlobalInvocationID`. | Chooses the texel; `gz` is zero in this 2D case. |
| Per-sample loop | Iterates `sampleNdx` from 0 to 3. | Selects every multisample location at the texel. |
| Pattern | Forms four XOR-based components, then scales them by `1 / 31`. | Gives samples and coordinates distinguishable, representable UNORM values. |
| Store | Calls `imageStore` with `ivec2(gx, gy)` and `sampleNdx`. | Performs the operation under test. |

#### Shader Code

```glsl
#version 450

layout(local_size_x = 1) in;
/// Binding 1 is the case-format multisampled storage image. The store pass writes each
/// addressed sample; the host creates it with VK_IMAGE_USAGE_STORAGE_BIT.
layout(set = 0, binding = 1, rgba8) writeonly uniform image2DMS u_msImage;

void main (void)
{
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);
    int gz = int(gl_GlobalInvocationID.z);

    /// The generated loop writes every sample of the current texel. Splitting sampleNdx
    /// into high and low bits keeps the red term in the intended range at 64 samples.
    for (int sampleNdx = 0; sampleNdx < 4; ++sampleNdx) {
        imageStore(u_msImage, ivec2(gx, gy), sampleNdx, vec4(gx^gy^gz^(sampleNdx >> 5)^(sampleNdx & 31), (31-gx)^gy^gz, gx^(31-gy)^gz, (31-gx)^(31-gy)^gz)*0.0322581);
    }
}
```

#### Additional Info

- The shader text follows the `initPrograms()` branch for a non-alpha-only, four-component UNORM 2D case. The scale is `1 / (32 - 1)` because the fixed texture extent has maximum dimension 32.
- Integer format cases use `ivec4` or `uvec4` and exact equality in the load shader. Float and normalized cases use the generated componentwise `< 0.02` comparison.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Format class | Changes the image type, image-format qualifier, scale/bias, and exact versus threshold comparison in the load shader. | [`initPrograms()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L89-L127) |
| Sample count | Changes the loop bound and therefore the number of explicit sample stores and loads. | [`initPrograms()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L146-L152) |
| All-layer versus single-layer array binding | Changes `image2DMSArray` to a 2D image type, changes the coordinate width, and substitutes `u_layerNdx` for `gl_GlobalInvocationID.z`. | [`initPrograms()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L83-L95) |
| `A8_UNORM_KHR` | Requires `GL_EXT_shader_image_load_formatted`, omits the qualifier, swaps red and alpha on store, and expects zero RGB on load. | [`initPrograms()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L91-L127) |

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
; Bound: 93
; Schema: 0
               OpCapability Shader
               OpCapability StorageImageMultisample
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %gx "gx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %gy "gy"
               OpName %gz "gz"
               OpName %sampleNdx "sampleNdx"
               OpName %u_msImage "u_msImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %u_msImage NonReadable
               OpDecorate %u_msImage Binding 1
               OpDecorate %u_msImage DescriptorSet 0
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
      %int_0 = OpConstant %int 0
      %int_4 = OpConstant %int 4
       %bool = OpTypeBool
      %float = OpTypeFloat 32
         %40 = OpTypeImage %float 2D 0 0 1 2 Rgba8
%_ptr_UniformConstant_40 = OpTypePointer UniformConstant %40
  %u_msImage = OpVariable %_ptr_UniformConstant_40 UniformConstant
      %v2int = OpTypeVector %int 2
      %int_5 = OpConstant %int 5
     %int_31 = OpConstant %int 31
    %v4float = OpTypeVector %float 4
%float_0_0322581008 = OpConstant %float 0.0322581008
      %int_1 = OpConstant %int 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %gx = OpVariable %_ptr_Function_int Function
         %gy = OpVariable %_ptr_Function_int Function
         %gz = OpVariable %_ptr_Function_int Function
  %sampleNdx = OpVariable %_ptr_Function_int Function
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
               OpStore %sampleNdx %int_0
               OpBranch %30
         %30 = OpLabel
               OpLoopMerge %32 %33 None
               OpBranch %34
         %34 = OpLabel
         %35 = OpLoad %int %sampleNdx
         %38 = OpSLessThan %bool %35 %int_4
               OpBranchConditional %38 %31 %32
         %31 = OpLabel
         %43 = OpLoad %40 %u_msImage
         %44 = OpLoad %int %gx
         %45 = OpLoad %int %gy
         %47 = OpCompositeConstruct %v2int %44 %45
         %48 = OpLoad %int %sampleNdx
         %49 = OpLoad %int %gx
         %50 = OpLoad %int %gy
         %51 = OpBitwiseXor %int %49 %50
         %52 = OpLoad %int %gz
         %53 = OpBitwiseXor %int %51 %52
         %54 = OpLoad %int %sampleNdx
         %56 = OpShiftRightArithmetic %int %54 %int_5
         %57 = OpBitwiseXor %int %53 %56
         %58 = OpLoad %int %sampleNdx
         %60 = OpBitwiseAnd %int %58 %int_31
         %61 = OpBitwiseXor %int %57 %60
         %62 = OpConvertSToF %float %61
         %63 = OpLoad %int %gx
         %64 = OpISub %int %int_31 %63
         %65 = OpLoad %int %gy
         %66 = OpBitwiseXor %int %64 %65
         %67 = OpLoad %int %gz
         %68 = OpBitwiseXor %int %66 %67
         %69 = OpConvertSToF %float %68
         %70 = OpLoad %int %gx
         %71 = OpLoad %int %gy
         %72 = OpISub %int %int_31 %71
         %73 = OpBitwiseXor %int %70 %72
         %74 = OpLoad %int %gz
         %75 = OpBitwiseXor %int %73 %74
         %76 = OpConvertSToF %float %75
         %77 = OpLoad %int %gx
         %78 = OpISub %int %int_31 %77
         %79 = OpLoad %int %gy
         %80 = OpISub %int %int_31 %79
         %81 = OpBitwiseXor %int %78 %80
         %82 = OpLoad %int %gz
         %83 = OpBitwiseXor %int %81 %82
         %84 = OpConvertSToF %float %83
         %86 = OpCompositeConstruct %v4float %62 %69 %76 %84
         %88 = OpVectorTimesScalar %v4float %86 %float_0_0322581008
               OpImageWrite %43 %47 %88 Sample %48
               OpBranch %33
         %33 = OpLabel
         %89 = OpLoad %int %sampleNdx
         %91 = OpIAdd %int %89 %int_1
               OpStore %sampleNdx %91
               OpBranch %30
         %32 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates the case-format multisampled image with `VK_IMAGE_USAGE_STORAGE_BIT`. It creates a single-sample `VK_FORMAT_R32_SINT` checksum image with storage and transfer-source usage.
- The descriptor-set layout contains binding 0 for a uniform buffer and bindings 1 and 2 for storage images. Binding 0 supplies one layer index for each `*_single_layer` dispatch; the store pass binds only the constants buffer and multisampled image.
- The first command buffer transitions both images from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_GENERAL` and runs the store pipeline. The host submits it and waits.
- The second command buffer uses a `VK_ACCESS_SHADER_WRITE_BIT` to `VK_ACCESS_SHADER_READ_BIT` image barrier at compute-shader stages for the multisampled image. It runs the load pipeline, which writes the number of matching samples to the checksum image. The host submits it and waits.
- The final command buffer transitions the checksum image from `GENERAL` to `TRANSFER_SRC_OPTIMAL`, copies all checksum layers to a host-visible transfer-destination buffer, and inserts a transfer-write to host-read buffer barrier.
- After invalidating the result allocation, the host scans every `int32_t`. A case passes only if every value equals the requested sample count. On the first mismatch, it logs `(x, y, layer)`, the observed checksum, and the expected checksum.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | Per-sample storage-image write/read addressing, generated value conversion/comparison, or the compute-to-compute visibility path. |
| `2d_array` | The `2d` causes, plus array image-view type or z-coordinate/layer addressing. |
| `2d_array.<format>_single_layer` | The `2d` causes, plus per-layer view range, descriptor-set selection, constants-buffer layer index, or repeated layer dispatch. |

### Cause Analysis

#### Per-sample storage-image access, value conversion, or visibility

**Possible failure symptoms:** One or more checksum values are below the requested sample count. The host reports the texel and layer where the aggregate count differed, but the shader does not retain the individual failing sample index.

**Possible implementation causes:** Source-level investigation must distinguish a failure in multisampled image access from a failure in the generated format conversion/comparison or the compute write-to-read dependency. The source checks all three through one checksum path.

#### Array image-view type or layer addressing

**Possible failure symptoms:** All-layer `2d_array` cases fail while comparable `2d` cases pass, or their failures differ by layer.

**Possible implementation causes:** The all-layer path uses an array image view, a three-component coordinate, and `gl_GlobalInvocationID.z`. An implementation or CTS investigation should examine those array-specific access and view parameters.

#### Per-layer view, descriptor, constants, or dispatch selection

**Possible failure symptoms:** `*_single_layer` cases fail while the all-layer array sibling passes, potentially at only some layers.

**Possible implementation causes:** This path changes the view to a one-layer 2D view, selects one descriptor set and constants-buffer range per layer, and repeats the dispatch. Investigation should inspect those per-layer bindings and the supplied `u_layerNdx`.

## Case Pruning

### Requirement-based pruning

- Every case requires `shaderStorageImageMultisample`.
- `checkSupport()` queries optimal-tiled 2D storage-image properties for the selected format. It skips the case if the format is unsupported or its `sampleCounts` mask lacks the requested count.
- Outside VulkanSC, `A8_UNORM_KHR` requires `VK_KHR_maintenance5` and the optimal-tiling `VK_FORMAT_FEATURE_2_STORAGE_READ_WITHOUT_FORMAT_BIT` and `VK_FORMAT_FEATURE_2_STORAGE_WRITE_WITHOUT_FORMAT_BIT` features.

### Design-based pruning

- The generator covers only 2D and 2D-array textures. It fixes the dimensions at 32x32 and uses four array layers because the color generator and layer-binding cases were designed for those extents.
- The single-layer binding variation appears only for the array texture because a one-layer 2D image has no alternate layer-view behavior to exercise.
- `A8_UNORM_KHR` is absent from VulkanSC registration through the source's `CTS_USES_VULKANSC` conditional.

## Key Takeaways

- This test checks explicit per-sample storage-image reads and writes. It does not test multisample resolving, filtering, or sampling.
- A single-sample integer checksum image compresses one comparison result per sample into a host-readable count per texel and layer.
- The all-layer and single-layer array cases use the same value model but exercise different view, descriptor, coordinate, and dispatch paths.
- Unsupported storage format/sample combinations are skipped before execution; an executed failure means at least one sample did not meet the test's generated expectation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Generated store and load shaders | [`initPrograms()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L81-L204) | Defines image declarations, the per-sample pattern, and the load-side comparison/checksum logic. |
| Support checks | [`checkSupport()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L206-L240) | Defines feature, format, sample-count, and alpha-only gates. |
| Array-view and descriptor helpers | [`insertImageViews()` and `insertDescriptorSets()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L242-L286) | Implements all-layer versus one-layer resource selection. |
| Runtime and verdict | [`test()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L288-L538) | Creates resources, records dispatches/barriers/copyback, and scans checksums. |
| Test registration | [`createImageMultisampleLoadStoreTests()`](../../../modules/vulkan/image/vktImageMultisampleLoadStoreTests.cpp#L543-L608) | Registers the texture, format, sample-count, and binding-mode matrix. |
| Image-test dispatcher | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L69) | Adds this factory below the `image` root as `image.load_store_multisample`. |
| Default Vulkan mustpass entries | [`load-store-multisample.txt`](../../../mustpass/main/vk-default/image/load-store-multisample.txt) | Lists the default-Vulkan executable test cases for this family. |
| Vulkan SC mustpass entries | [`load-store-multisample.txt`](../../../mustpass/main/vksc-default/image/load-store-multisample.txt) | Lists the Vulkan SC matrix, which omits `A8_UNORM_KHR` leaves. |
