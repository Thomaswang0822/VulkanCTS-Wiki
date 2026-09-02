## Overview

**Core question:** Do overlapping fragment invocations update one shared value without losing a primitive's bit when the selected fragment-shader interlock mode orders their critical sections?

- [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L200-L334) generates the vertex and fragment shaders for the `fragment_shader_interlock.basic` test family.
- The `basic` test family covers `nodiscard` and `discard` branches. Each leaf also selects an image or SSBO destination, an interlock mode, a sample count, sample shading, and a square extent.
- The fragment shader maps each invocation to a result location, enters `beginInvocationInterlockARB()` / `endInvocationInterlockARB()`, and ORs a bitmask into the selected image or storage buffer.
- Ordered modes require all lower primitive bits to be present before adding the current bit. Unordered modes add the bit without that check.
- The page explains the generated matrix, one concrete fragment shader, the host resource and copyback flow, and how a failed comparison narrows the possible cause.

## Background Knowledge

- **Fragment shader interlock.** The `VK_EXT_fragment_shader_interlock` capabilities let a fragment shader execute a critical section for a selected rasterization region. This lets the shader perform a load, modify, and store on per-pixel data without a conflicting invocation entering the same region at the same time. See [`VK_EXT_fragment_shader_interlock`](../../../../vulkan-docs/src/appendices/VK_EXT_fragment_shader_interlock.adoc#L24-L45).
- **Ordered and unordered regions.** An ordered qualifier adds an ordering condition to the interlock region; an unordered qualifier provides mutual exclusion without requiring a particular primitive order. Pixel and sample qualifiers select different conflict scopes. Shading-rate qualifiers use the coarse fragment region selected by fragment shading rate.
- **Sample coverage.** `gl_SampleMaskIn[0]` records the covered samples for a fragment. The test stores that mask in the pixel and shading-rate paths, while sample interlock stores one bit per sample invocation. This distinction explains the separate coordinate and `bitsPerQuad` calculations.

## Registration Hierarchy

```text
fragment_shader_interlock.basic
├── nodiscard
└── discard
```

`vktFragmentShaderInterlockTests.cpp` dispatches the `basic` test family. [`createBasicTests()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L777-L864) expands the two direct children into the generated matrix; the executable leaves are the extent names at the bottom of each path.

## Parameter Dimensions and Observed Values

The source creates these dimensions with nested `TestGroupCase` arrays. The Vulkan mustpass contains 576 leaves, and the Vulkan SC mustpass contains 384 leaves. Vulkan SC omits the two shading-rate interlock values through the `CTS_USES_VULKANSC` guard.

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Discard behavior | `nodiscard`, `discard` | Chooses whether odd result coordinates take the discard paths before, inside, and after the interlock. | [`killCases[]`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L797-L800), [`discard` branches](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L296-L304), [`discard` exit](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L327-L330) |
| Destination resource | `image`, `ssbo` | Selects an `r32ui` storage image or a `uint` array in a `std430` storage buffer for the read-modify-write. | [`resCases[]`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L792-L795), [`resource access`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L305-L325) |
| Interlock mode | `pixel_ordered`, `pixel_unordered`, `sample_ordered`, `sample_unordered`, `shading_rate_ordered`, `shading_rate_unordered` | Selects the conflict region and whether the shader checks lower primitive bits before storing the current bit. The shading-rate values are absent from Vulkan SC registration. | [`intCases[]`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L812-L821), [`qualifier generation`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L225-L247) |
| Sample count | `1xaa`, `4xaa` | Selects one or four rasterization samples. The image is widened in the x direction for sample-interlock cases. | [`sampCases[]`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L802-L805), [`image extent`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L428-L449) |
| Sample shading | `no_sample_shading`, `sample_shading` | Selects per-fragment or per-sample shading in the multisample pipeline. The source skips `sample_shading` with `1xaa`. | [`ssCases[]`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L807-L810), [`matrix skip`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L847-L850) |
| Render extent | `8x8`, `16x16`, `32x32`, `64x64`, `128x128`, `256x256`, `512x512`, `1024x1024` | Sets the square framebuffer extent and the row stride used by SSBO addressing. | [`dimCases[]`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L787-L790), [`framebuffer setup`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L539-L551) |

## Behavior Parameters

The primary behavioral axis is the **interlock mode**. It selects the overlap unit and the ordered or unordered update rule. `nodiscard` versus `discard`, `image` versus `ssbo`, sample count, sample shading, and extent select the invocation, storage, and addressing paths used to observe that rule.

### `pixel_ordered` and `pixel_unordered` | Per-pixel critical sections

Pixel modes use the integer fragment coordinate as the result location. Ordered mode tests that all lower primitive bits already exist before it adds the current bit. Unordered mode only ORs the current bit into the loaded value. With `1xaa`, `bitsPerQuad` is 1, so 32 fullscreen instances provide one bit each in a 32-bit result.

### `sample_ordered` and `sample_unordered` | Per-sample critical sections

Sample modes spread sample results across x: `coordxy.x = coordxy.x * samples + gl_SampleID`, and they multiply the row stride by the sample count. They use one bit per primitive because each sample invocation writes its own result location. The ordered variant applies the same lower-bit check as the pixel ordered path.

### `shading_rate_ordered` and `shading_rate_unordered` | Coarse fragment regions

Shading-rate modes divide the fragment coordinate and stride by two because the pipeline sets a 2x2 fragment size. They use the fragment sample mask and set `bitsPerQuad` to four times the sample count, so each coarse result can record the mask contributed by a fullscreen quad. The host enables `VkPipelineFragmentShadingRateStateCreateInfoKHR` only for these modes.

### `nodiscard` and `discard` | Keep or remove selected writes

`nodiscard` lets every invocation continue through the interlock and store. `discard` rejects odd x coordinates in the top quarter before entering the interlock, rejects remaining odd coordinates after entering it, and discards again after the store. The result scan expects odd entries to stay zero in this branch.

### `image` and `ssbo` | Select the storage path

The image path loads and stores `image0` at `coordxy`. The SSBO path computes `coord = coordxy.y * stride + coordxy.x` and accesses `buf1.x[coord]`. Both paths use the same bitmask rule; only the destination and host copy operation differ.

## Shader Analysis

The fragment shader is generated in [`FSITestCase::initPrograms()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L216-L334). The walkthrough below uses the exact Vulkan mustpass case `dEQP-VK.fragment_shader_interlock.basic.nodiscard.image.pixel_ordered.1xaa.no_sample_shading.8x8`. It selects the image destination, pixel ordered interlock, one sample, no sample shading, and an 8x8 extent.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.fragment_shader_interlock.basic.nodiscard.image.pixel_ordered.1xaa.no_sample_shading.8x8
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `nodiscard` | All fragments take the normal path and reach the interlock and store. |
| `image` | The shader reads and writes the `r32ui` storage image at binding 0. |
| `pixel_ordered` | The interlock conflict scope is a pixel, and each invocation checks lower primitive bits before storing. |
| `1xaa` + `no_sample_shading` | `gl_SampleMaskIn[0]` contributes one covered-sample bit, and the fragment shader runs without per-sample shading. |
| `8x8` | The host uses an 8x8 framebuffer and the generated SSBO stride constant is 8, although this image case does not use the SSBO address. |

#### Purpose

This fragment shader records which fullscreen primitive instances reached each pixel. Pixel ordered interlock should let each instance observe the bits from earlier instances before it adds its own bit.

#### Structural Design

| Phase | Shader operation | Result |
|---|---|---|
| Coordinate | Convert `gl_FragCoord.xy` to integer `coordxy`. | Select one image texel. |
| Mask construction | Shift `gl_SampleMaskIn[0]` by `primID * bitsPerQuad`; derive `previousMask` from lower primitive bits. | Give each instance a distinct bit and define the ordered prerequisite. |
| Critical section | Begin the interlock, load the texel, check or OR the mask, then store the new value. | Serialize the read-modify-write for the selected pixel. |
| Completion | End the interlock. | Make the updated value available to later work in the test's command sequence. |

#### Shader Code

Reconstructed GLSL for this path:

```glsl
#version 450 core
#extension GL_ARB_fragment_shader_interlock : enable
#extension GL_NV_shading_rate_image : enable
/// Binding 0 is an r32ui storage image. The host creates it with width dim * samples and height dim.
layout(r32ui, set = 0, binding = 0) coherent uniform uimage2D image0;
/// Binding 1 is a coherent std430 uint storage buffer. It is bound for the common shader interface, but this image case uses image0.
layout(std430, set = 0, binding = 1) coherent buffer B1 { uint x[]; } buf1;
/// The vertex shader supplies the fullscreen instance index as a flat primitive identifier.
layout(location = 0) flat in int primID;
/// Pixel ordered interlock serializes conflicting fragment invocations for one pixel and adds the ordered predecessor check.
layout(pixel_interlock_ordered) in;
void main()
{
  ivec2 coordxy = ivec2(gl_FragCoord.xy);
  uint stride = 8;
  uint bitsPerQuad = 1;
  /// One bit identifies this primitive for the covered sample in the pixel.
  uint mask = gl_SampleMaskIn[0] << (primID * bitsPerQuad);
  /// Ordered mode requires every lower primitive bit before it accepts this update.
  uint previousMask = (1 << (primID * bitsPerQuad))-1;
  beginInvocationInterlockARB();
  uint temp = imageLoad(image0, coordxy).x;
  if ((temp & previousMask) == previousMask) temp |= mask; else temp = 0;
  imageStore(image0, coordxy, uvec4(temp, 0, 0, 0));
  endInvocationInterlockARB();
}
```

#### Additional Info

- The vertex shader draws a four-vertex `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` fullscreen quad for each instance and writes `gl_InstanceIndex` to `primID` [`vertex generation`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L204-L214), [`draw`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L708-L718).
- The generator emits both resource declarations for all cases, then selects only the image or SSBO access in the body [`resource declarations`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L218-L223), [`resource access`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L305-L325).
- The source notes that the triangle-strip diagonal does not distinguish primitive order between samples within one pixel. This is why the oracle checks the resulting mask rather than requiring a total order for those internal diagonal samples [`generator note`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L249-L258).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Discard behavior | `discard` adds an odd-coordinate discard before the interlock, another after `beginInvocationInterlockARB()`, and a final discard after `endInvocationInterlockARB()`. | [`discard branches`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L296-L304), [`discard exit`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L327-L330) |
| Destination resource | `image` uses `imageLoad` / `imageStore`; `ssbo` computes a linear coordinate and reads / writes `buf1.x[coord]`. | [`resource access`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L305-L325) |
| Interlock mode | The qualifier selects pixel, sample, or shading-rate interlock. Sample modes use `gl_SampleID`; shading-rate modes divide coordinates by two. | [`qualifier and coordinate branches`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L225-L281) |
| Sample count and shading | Sample count changes the sample-coordinate spread and mask geometry. Sample shading changes pipeline invocation frequency; the source skips its 1x case. | [`sample coordinate`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L269-L275), [`pipeline multisampling`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L588-L603), [`matrix skip`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L847-L850) |
| Render extent | The generated `stride` constant and host framebuffer dimensions use `dim`; the shader's control flow does not change with extent. | [`shader dimension`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L260-L267), [`extent cases`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L787-L790) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 78
; Schema: 0
               OpCapability Shader
               OpCapability FragmentShaderPixelInterlockEXT
               OpExtension "SPV_EXT_fragment_shader_interlock"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %gl_SampleMaskIn %primID
               OpExecutionMode %main OriginUpperLeft
               OpExecutionMode %main PixelInterlockOrderedEXT
               OpSource GLSL 450
               OpSourceExtension "GL_ARB_fragment_shader_interlock"
               OpSourceExtension "GL_NV_shading_rate_image"
               OpName %main "main"
               OpName %coordxy "coordxy"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %stride "stride"
               OpName %bitsPerQuad "bitsPerQuad"
               OpName %mask "mask"
               OpName %gl_SampleMaskIn "gl_SampleMaskIn"
               OpName %primID "primID"
               OpName %previousMask "previousMask"
               OpName %temp "temp"
               OpName %image0 "image0"
               OpName %B1 "B1"
               OpMemberName %B1 0 "x"
               OpName %buf1 "buf1"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %gl_SampleMaskIn BuiltIn SampleMask
               OpDecorate %gl_SampleMaskIn Flat
               OpDecorate %primID Flat
               OpDecorate %primID Location 0
               OpDecorate %image0 Coherent
               OpDecorate %image0 Binding 0
               OpDecorate %image0 DescriptorSet 0
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %B1 BufferBlock
               OpMemberDecorate %B1 0 Coherent
               OpMemberDecorate %B1 0 Offset 0
               OpDecorate %buf1 Coherent
               OpDecorate %buf1 Binding 1
               OpDecorate %buf1 DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
    %v2float = OpTypeVector %float 2
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_8 = OpConstant %uint 8
     %uint_1 = OpConstant %uint 1
%_arr_int_uint_1 = OpTypeArray %int %uint_1
%_ptr_Input__arr_int_uint_1 = OpTypePointer Input %_arr_int_uint_1
%gl_SampleMaskIn = OpVariable %_ptr_Input__arr_int_uint_1 Input
      %int_0 = OpConstant %int 0
%_ptr_Input_int = OpTypePointer Input %int
     %primID = OpVariable %_ptr_Input_int Input
      %int_1 = OpConstant %int 1
         %49 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_49 = OpTypePointer UniformConstant %49
     %image0 = OpVariable %_ptr_UniformConstant_49 UniformConstant
     %v4uint = OpTypeVector %uint 4
     %uint_0 = OpConstant %uint 0
       %bool = OpTypeBool
%_runtimearr_uint = OpTypeRuntimeArray %uint
         %B1 = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_B1 = OpTypePointer Uniform %B1
       %buf1 = OpVariable %_ptr_Uniform_B1 Uniform
       %main = OpFunction %void None %3
          %5 = OpLabel
    %coordxy = OpVariable %_ptr_Function_v2int Function
     %stride = OpVariable %_ptr_Function_uint Function
%bitsPerQuad = OpVariable %_ptr_Function_uint Function
       %mask = OpVariable %_ptr_Function_uint Function
%previousMask = OpVariable %_ptr_Function_uint Function
       %temp = OpVariable %_ptr_Function_uint Function
         %15 = OpLoad %v4float %gl_FragCoord
         %16 = OpVectorShuffle %v2float %15 %15 0 1
         %17 = OpConvertFToS %v2int %16
               OpStore %coordxy %17
               OpStore %stride %uint_8
               OpStore %bitsPerQuad %uint_1
         %30 = OpAccessChain %_ptr_Input_int %gl_SampleMaskIn %int_0
         %31 = OpLoad %int %30
         %33 = OpLoad %int %primID
         %34 = OpBitcast %uint %33
         %35 = OpLoad %uint %bitsPerQuad
         %36 = OpIMul %uint %34 %35
         %37 = OpShiftLeftLogical %int %31 %36
         %38 = OpBitcast %uint %37
               OpStore %mask %38
         %41 = OpLoad %int %primID
         %42 = OpBitcast %uint %41
         %43 = OpLoad %uint %bitsPerQuad
         %44 = OpIMul %uint %42 %43
         %45 = OpShiftLeftLogical %int %int_1 %44
         %46 = OpISub %int %45 %int_1
         %47 = OpBitcast %uint %46
               OpStore %previousMask %47
               OpBeginInvocationInterlockEXT
         %52 = OpLoad %49 %image0
         %53 = OpLoad %v2int %coordxy
         %55 = OpImageRead %v4uint %52 %53
         %57 = OpCompositeExtract %uint %55 0
               OpStore %temp %57
         %58 = OpLoad %uint %temp
         %59 = OpLoad %uint %previousMask
         %60 = OpBitwiseAnd %uint %58 %59
         %61 = OpLoad %uint %previousMask
         %63 = OpIEqual %bool %60 %61
               OpSelectionMerge %65 None
               OpBranchConditional %63 %64 %69
         %64 = OpLabel
         %66 = OpLoad %uint %mask
         %67 = OpLoad %uint %temp
         %68 = OpBitwiseOr %uint %67 %66
               OpStore %temp %68
               OpBranch %65
         %69 = OpLabel
               OpStore %temp %uint_0
               OpBranch %65
         %65 = OpLabel
         %70 = OpLoad %49 %image0
         %71 = OpLoad %v2int %coordxy
         %72 = OpLoad %uint %temp
         %73 = OpCompositeConstruct %v4uint %72 %uint_0 %uint_0 %uint_0
               OpImageWrite %70 %71 %73
               OpEndInvocationInterlockEXT
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates one descriptor set with binding 0 as a storage image and binding 1 as a storage buffer. It allocates a local buffer sized for `dim * dim * sizeof(uint32_t) * 4` and a host-visible cached copy buffer of the same size [`descriptor bindings`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L353-L403), [`copy buffer`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L423-L426).
- The image has format `VK_FORMAT_R32_UINT`, one mip level, one array layer, and extent `(dim * samples, dim, 1)`. The image uses storage and transfer-src/dst usage. The shader still sees a 2D image with a single-sample Vulkan image; sample-interlock cases lay samples out in x instead of making the image multisampled [`image creation`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L428-L449).
- The host clears the image and buffer, transitions the image to `VK_IMAGE_LAYOUT_GENERAL`, and makes transfer writes visible to the shader stages before rendering [`initialization and barrier`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L647-L677).
- The graphics pipeline uses a triangle-strip fullscreen quad, no vertex input, a `dim` by `dim` viewport and scissor, and `m_data.samples` rasterization samples. It enables sample shading for `sample_shading`. Shading-rate modes attach a 2x2 `VkPipelineFragmentShadingRateStateCreateInfoKHR` [`pipeline state`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L553-L606), [`shading-rate state`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L586-L604).
- The host draws `N = 32 / bitsPerQuad(m_data)` instances. Each instance supplies one primitive bit, or a sample mask shifted by `bitsPerQuad` in pixel and shading-rate modes [`draw and oracle`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L708-L718).
- After the render pass, the host adds a shader-to-transfer barrier, copies either the image or the SSBO into the host-visible buffer, adds a transfer-to-host barrier, submits the command buffer, invalidates the allocation, and scans the copy [`copyback`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L719-L772).
- The case passes when every copied word equals `0xFFFFFFFF`. In `discard` cases, odd entries must equal zero instead. Any mismatch returns `QP_TEST_RESULT_FAIL`; unsupported feature combinations throw `NotSupportedError` before execution [`result scan`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L753-L772), [`support checks`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L154-L185).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `pixel_ordered` | Pixel interlock scope or ordered predecessor handling, fragment mask generation, image/SSBO access, or result comparison. |
| `pixel_unordered` | Pixel interlock exclusion, fragment mask generation, image/SSBO access, or result comparison. |
| `sample_ordered` | Sample interlock scope, sample coordinate mapping, ordered predecessor handling, image/SSBO access, or result comparison. |
| `sample_unordered` | Sample interlock scope, sample coordinate mapping, image/SSBO access, or result comparison. |
| `shading_rate_ordered` | Shading-rate interlock scope, 2x2 coordinate mapping, ordered predecessor handling, image/SSBO access, or result comparison. |
| `shading_rate_unordered` | Shading-rate interlock scope, 2x2 coordinate mapping, image/SSBO access, or result comparison. |

`nodiscard` and `discard`, destination resource, sample count, sample shading, and extent further identify the path that produced the mismatch.

### Cause Analysis

#### Interlock scope or ordering

**Possible failure symptoms:** An output word lacks one or more expected primitive bits, or an ordered case clears a word after it observes a missing lower bit. The mismatch may be limited to pixel, sample, or coarse shading-rate coordinates.

**Possible implementation causes:** The selected interlock capability or qualifier may cover the wrong rasterization region, or the ordered critical section may fail to exclude a conflicting invocation during its load and store. The test result cannot distinguish the interlock implementation from a compiler lowering error without additional inspection.

#### Coordinate and sample-mask mapping

**Possible failure symptoms:** Pixel cases pass while sample or shading-rate cases contain wrong locations or incomplete masks. A four-sample case can show errors only in the widened x range or in coarse 2x2 regions.

**Possible implementation causes:** The fragment shader may expose a wrong `gl_SampleID` or `gl_SampleMaskIn[0]`, or the pipeline may apply sample shading or fragment shading rate differently from the selected case. The source establishes the coordinate formulas and pipeline state, but a specific failure needs an API trace or implementation investigation.

#### Storage access and copyback

**Possible failure symptoms:** Image and SSBO variants disagree, or the final host buffer contains stale, truncated, or misplaced values even when the shader path is the same.

**Possible implementation causes:** The descriptor binding, storage-image layout, storage-buffer access, transfer copy, or host visibility operation may not match the resource used by the shader. The result scan identifies the observed word, not the layer that supplied it.

#### Discard and invocation frequency

**Possible failure symptoms:** `discard` cases contain nonzero odd entries, while sample-shading cases contain missing or extra sample contributions. The host reports a value other than zero for an excluded discard entry or a value other than `0xFFFFFFFF` for an expected entry.

**Possible implementation causes:** The implementation may handle discard relative to the interlock region incorrectly, or may produce a different fragment invocation and coverage pattern for sample shading. The exact source of a failed combination needs investigation against the selected shader and pipeline state.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_fragment_shader_interlock`.
- Pixel modes require `fragmentShaderPixelInterlock`; sample modes require `fragmentShaderSampleInterlock`.
- Shading-rate modes require `fragmentShaderShadingRateInterlock`, `pipelineFragmentShadingRate`, and `fragmentShadingRateWithFragmentShaderInterlock`. The source compiles these checks out for Vulkan SC registration [`checkSupport()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L154-L182).
- Sample interlock and sample-shading cases require the core `sampleRateShading` feature [`checkSupport()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L184-L185).

### Design-based pruning

- The source skips `sample_shading` when `samples == 1`, because per-sample shading has no additional sample dimension in a one-sample case [`matrix skip`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L847-L850).
- Shading-rate interlock uses a fixed 2x2 fragment size and changes both the shader coordinate mapping and the host copy extent. The source does not register those modes for Vulkan SC [`shading-rate pipeline state`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L504-L506), [`intCases[]`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L812-L821).
- The matrix keeps the same eight square extents across resource, interlock, discard, and sample settings. Extent changes stress addressing and copyback size without creating a separate synchronization mechanism.

## Key Takeaways

- The `basic` test family uses a 32-bit bitmask as its oracle for overlapping fullscreen fragment updates.
- Ordered modes require the lower primitive bits before accepting the current update; unordered modes test mutual exclusion without that predecessor condition.
- Sample interlock changes the result coordinate per sample. Shading-rate interlock changes it per 2x2 coarse region and uses a larger bit allocation per quad.
- Image and SSBO cases exercise the same shader rule through different storage objects. The host checks the copied words, so a failed case needs the selected resource and synchronization path for interpretation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Category dispatch | [`createChildren()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockTests.cpp#L37-L54) | Places `basic` under the `fragment_shader_interlock` test category. |
| Matrix registration | [`createBasicTests()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L777-L864) | Creates `nodiscard` and `discard` and all generated parameter dimensions. |
| Shader generation | [`FSITestCase::initPrograms()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L200-L334) | Emits the vertex shader, interlock qualifiers, coordinate formulas, resource operations, and discard branches. |
| Support checks | [`FSITestCase::checkSupport()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L154-L185) | Separates unsupported extension and feature combinations from executed failures. |
| Host setup and pipeline | [`FSITestInstance::iterate()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L342-L677) | Creates descriptors, resources, image layout transitions, and the graphics pipeline. |
| Draw, copyback, and result scan | [`FSITestInstance::iterate()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L708-L772) | Draws the instances, copies the selected destination, and compares the host-visible words. |
| Vulkan mustpass | [`fragment-shader-interlock.txt`](../../../mustpass/main/vk-default/fragment-shader-interlock.txt#L1-L576) | Lists the 576 Vulkan leaves for the category. |
| Vulkan SC mustpass | [`fragment-shader-interlock.txt`](../../../mustpass/main/vksc-default/fragment-shader-interlock.txt#L1-L384) | Lists the 384 Vulkan SC leaves, which omit shading-rate interlock modes. |
| Interlock semantics | [`VK_EXT_fragment_shader_interlock`](../../../../vulkan-docs/src/appendices/VK_EXT_fragment_shader_interlock.adoc#L24-L45) | Describes fragment interlock capabilities and critical-section use. |
