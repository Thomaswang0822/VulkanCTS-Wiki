## Overview

**Core question:** Does Vulkan produce the specified clamped, out-of-range, and biased depth values in the Amber depth pipeline?

- This page covers the implementation in [`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L45-L166), its factory declaration in [`vktAmberDepthTests.hpp`](../../../modules/vulkan/amber/vktAmberDepthTests.hpp#L35-L35), and the eight Amber recipes in [`data/vulkan/amber/depth/`](../../../data/vulkan/amber/depth/).
- The `depth` test category registers eight direct test cases. They exercise viewport-range clamping, fragment-depth clamping, early fragment tests, depth bias, and the effect of `VK_EXT_depth_range_unrestricted`.
- Each recipe renders a 60 x 60 rectangle into an `R8G8B8A8_UNORM` color buffer and a `D32_SFLOAT` depth buffer. Selected recipes also store `gl_FragCoord.z` in a one-float storage buffer so the shader-visible and attachment-visible values can be compared.
- The page explains the depth transformations, the Amber artifacts that express them, the host-side runner, support gates, pruning, and what a mismatch tells you.

## Background Knowledge

- After rasterization produces a fragment depth, Vulkan applies the active viewport depth range and, when enabled, depth clamping before the depth test and depth write. With `VK_KHR_depth_clamp_zero_one` or `VK_EXT_depth_clamp_zero_one` enabled through `depthClampZeroOne`, the clamped value is limited to `[0, 1]` unless the floating-point attachment is used with `VK_EXT_depth_range_unrestricted`; the specification describes this sequence in [Depth Clamping and Range Adjustment](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-depth).
- Depth bias offsets fragment depth using constant and slope terms, with `depthBiasClamp` limiting the resulting offset. This test uses a zero slope factor, so its bias is controlled by the constant value in each Amber `BIAS` command. See [Depth Bias](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-depthbias).
- `gl_FragCoord.z` is the fragment shader's depth value. A storage-buffer write can therefore expose the value seen by the shader, while the depth attachment records the value that passes the fixed-function depth path. The distinction matters when the pipeline clamps or biases the attachment value.

## Registration Hierarchy

```text
depth
├── fs_clamp
├── out_of_range
├── ez_fs_clamp
├── bias_fs_clamp
├── bias_outside_range
├── bias_outside_range_fs_clamp
├── out_of_range_unrestricted
└── bias_outside_range_fs_clamp_unrestricted
```

The root is added to the Vulkan package by [`TestPackage::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1393-L1395). The eight direct-child names come from the `TestInfo` table and are mapped to `<name>.amber` in [`createDepthTestCase()` and `createTests()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L103-L156). The same eight executable paths appear in [`depth.txt`](../../../mustpass/main/vk-default/depth.txt#L1-L8).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case | `fs_clamp`, `out_of_range`, `ez_fs_clamp`, `bias_fs_clamp`, `bias_outside_range`, `bias_outside_range_fs_clamp`, `out_of_range_unrestricted`, `bias_outside_range_fs_clamp_unrestricted` | Selects the shader operation and fixed-function depth state being checked. | [`TestInfo` table](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L96-L149) |
| Viewport depth range | `0.1..0.9`; `0.1..0.5` for `bias_outside_range` | Sets the range used by viewport depth mapping and by ordinary depth clamping. | [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L50-L58), [`bias_outside_range.amber`](../../../data/vulkan/amber/depth/bias_outside_range.amber#L49-L56) |
| Depth source | Vertex `gl_Position.z = 2`; fragment `gl_FragDepth = 2.0`; fragment `gl_FragCoord.z` | Produces out-of-range vertex or fragment depth, or records the shader-observed depth for comparison. | [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L19-L40), [`out_of_range.amber`](../../../data/vulkan/amber/depth/out_of_range.amber#L17-L34) |
| Depth state | `CLAMP on`; depth test `equal`, `not_equal`, or default recipe comparison; depth writes enabled | Separates clamped attachment results from tests of an explicitly out-of-range fragment depth. | [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L50-L55), [`out_of_range.amber`](../../../data/vulkan/amber/depth/out_of_range.amber#L44-L49), [`out_of_range_unrestricted.amber`](../../../data/vulkan/amber/depth/out_of_range_unrestricted.amber#L45-L50) |
| Depth bias | Constant `1.0`, `2097152.0`, or `16777216.0`; slope `0.0`; optional `CLAMP on` | Moves the depth value before the depth test and write. Large constants probe behavior outside the ordinary depth range. | [`bias_fs_clamp.amber`](../../../data/vulkan/amber/depth/bias_fs_clamp.amber#L50-L55), [`bias_outside_range.amber`](../../../data/vulkan/amber/depth/bias_outside_range.amber#L49-L54) |
| Runtime requirements | `DepthClampZeroOneFeatures.depthClampZeroOne` for all; `depthClamp`, `fragmentStoresAndAtomics`, or `VK_EXT_depth_range_unrestricted` as selected | Controls whether a case may run and whether the unrestricted rerun uses the extension path. | [`createTests()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L124-L149) |

## Behavior Parameters

The primary behavioral axis is the registered test case. Each direct child chooses a distinct depth-source or fixed-function combination.

### `fs_clamp`: clamp rasterized depth to the viewport range

The vertex shader places the primitive at clip-space `z = 2`, and the pipeline enables depth clamp with viewport range `0.1..0.9`. The recipe expects the depth attachment to contain `0.9`, while the fragment shader stores `gl_FragCoord.z` as `1.7`, exposing the post-viewport value before the attachment's zero-one clamp.

### `out_of_range`: preserve an out-of-range fragment depth without unrestricted range

The fragment shader writes `gl_FragDepth = 2.0`. The pipeline uses an `equal` depth comparison after clearing the attachment to `1.0`, and the recipe expects the color to be green and the depth attachment to remain `1.0`. This checks the defined handling of the out-of-range fragment depth in the non-unrestricted path.

### `ez_fs_clamp`: apply the same clamp with early fragment tests

This case follows the `fs_clamp` depth setup but declares `layout(early_fragment_tests) in;`. Its expected attachment and storage values are `0.9` and `1.7`, respectively. The added execution qualifier checks that the depth behavior remains correct when fragment tests run early.

### `bias_fs_clamp`: clamp a biased depth value

The vertex shader again produces a depth above the ordinary range. A constant bias of `1.0` is applied with slope factor `0.0` and depth clamp enabled. The expected depth attachment is `0.9`, and the storage buffer records `1.7`, so the case checks both bias interaction and the active clamp limit.

### `bias_outside_range`: apply a large bias with a narrower viewport range

The viewport range is `0.1..0.5`, and the constant bias is `2097152.0` without `CLAMP on`. The expected attachment and shader-observed values are both `0.625`. The case probes depth bias outside the ordinary viewport range while retaining a floating-point depth attachment.

### `bias_outside_range_fs_clamp`: clamp a large biased value to zero-one

This recipe uses viewport range `0.1..0.9`, constant bias `16777216.0`, and no explicit `CLAMP on` in the Amber depth block. It expects the attachment to be `1.0` and the storage buffer to be `1.9`, distinguishing the value observed by the fragment shader from the value stored by the depth path.

### `out_of_range_unrestricted`: retain an out-of-range depth with unrestricted range

This rerun enables `VK_EXT_depth_range_unrestricted` and writes `gl_FragDepth = 2.0`. The `not_equal` comparison against the cleared depth value allows the draw to update the attachment, and the expected depth is `2.0`. The case targets the floating-point attachment behavior when the extension leaves the out-of-range value unchanged.

### `bias_outside_range_fs_clamp_unrestricted`: combine large bias and unrestricted range

This recipe enables `VK_EXT_depth_range_unrestricted`, applies constant bias `16777216.0`, and uses the same viewport endpoints as `bias_outside_range_fs_clamp`. Both the depth attachment and `fs_depth` are expected to contain `1.9`, checking that the unrestricted rerun does not apply the non-extension zero-one result.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.depth.fs_clamp
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `fs_clamp` | Selects the recipe in which the vertex shader produces clip-space `z = 2`, depth clamp is enabled, and the fragment shader records `gl_FragCoord.z`. |
| `D32_SFLOAT` depth attachment | Keeps the attachment value in floating-point form so the expected `0.9` can be compared with the shader-side `1.7`. |
| Viewport depth range `0.1..0.9` | Supplies the range used by the recipe's viewport and the expected clamped attachment endpoint. |

#### Purpose

The fragment shader records the depth value available through `gl_FragCoord.z` and writes green color. The recipe then compares that shader-side value with the depth attachment value produced by the fixed-function depth path.

#### Structural Design

| Shader operation | Observable output | Expected `fs_clamp` value |
|-----------------|-------------------|----------------------------|
| Read `gl_FragCoord.z` | `fs_depth` storage buffer | `1.7` |
| Write `vec4(0, 1, 0, 1)` | `framebuffer0` | Green for the 60 x 60 rectangle |
| Fixed-function depth processing | `depth0` attachment | `0.9` after clamping |

#### Shader Code

```glsl
#version 430
/// Binding 0 exposes the fragment depth to the Amber EXPECT check.
layout (binding=0) buffer B {
    float d;
};

layout(location = 0) out highp vec4 frag_out;
void main()
{
    /// This is the shader-observed depth, before the attachment comparison.
    d = gl_FragCoord.z;
    frag_out = vec4(0, 1, 0, 1);
}
```

#### Additional Info

- The vertex stage is fixed for this representative case and supplies `gl_Position = vec4(position_in, 2, 1)`, which places the rasterized depth above the ordinary viewport range. [Vertex shader in `fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L19-L27)
- The `fs_depth` buffer is a host-visible Amber comparison artifact, while `depth0` is the depth attachment. Their different expected values are intentional. [Pipeline and expectations](../../../data/vulkan/amber/depth/fs_clamp.amber#L43-L76)

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Fragment depth source | `fs_clamp` and its bias variants use `gl_FragCoord.z`; the `out_of_range` variants instead write `gl_FragDepth = 2.0`. | [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L29-L40), [`out_of_range.amber`](../../../data/vulkan/amber/depth/out_of_range.amber#L27-L34) |
| Early fragment tests | `ez_fs_clamp` adds `layout(early_fragment_tests) in;`; the ordinary `fs_clamp` fragment source does not. | [`ez_fs_clamp.amber`](../../../data/vulkan/amber/depth/ez_fs_clamp.amber#L29-L42) |
| Bias and unrestricted range | These choices leave the fragment source unchanged and alter Amber depth state or device requirements around it. | [`bias_fs_clamp.amber`](../../../data/vulkan/amber/depth/bias_fs_clamp.amber#L49-L55), [`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L126-L148) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from the `fs_clamp` Amber recipe
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 27
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %frag_out
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 430
               OpName %main "main"
               OpName %B "B"
               OpMemberName %B 0 "d"
               OpName %_ ""
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %frag_out "frag_out"
               OpDecorate %B BufferBlock
               OpMemberDecorate %B 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %frag_out Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
          %B = OpTypeStruct %float
%_ptr_Uniform_B = OpTypePointer Uniform %B
          %_ = OpVariable %_ptr_Uniform_B Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_ptr_Input_float = OpTypePointer Input %float
%_ptr_Uniform_float = OpTypePointer Uniform %float
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %frag_out = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %26 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_2
         %19 = OpLoad %float %18
         %21 = OpAccessChain %_ptr_Uniform_float %_ %int_0
               OpStore %21 %19
               OpStore %frag_out %26
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `DepthTestCase` builds an Amber test case with the recipe path `vulkan/amber/<category>/<filename>`. For this page, the category is `depth` and the filename is the exact registered name plus `.amber` ([`createDepthTestCase()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L103-L121)).
- The test parses the recipe before execution, loads the inline vertex and fragment GLSL stages, and adds them to the CTS GLSL source collection. The shared runner uses the recipe's shader names and compiles them with the selected SPIR-V target ([`parse()` and `initPrograms()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L489)).
- Amber creates the graphics pipeline, binds the color and `D32_SFLOAT` depth attachments, clears color to `(0, 0, 0, 0)` and depth to `1.0`, then draws a 60 x 60 rectangle. Cases with `fs_depth` bind a storage buffer at descriptor set `0`, binding `0` and read its checked float after execution ([`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L43-L75)).
- Each recipe uses `EXPECT` commands as its result check. Color must be green for the full rectangle. Depth checks compare exact values for attachment samples, and `fs_depth` checks use a tolerance of `1.0e-6` where specified ([`bias_outside_range_fs_clamp_unrestricted.amber`](../../../data/vulkan/amber/depth/bias_outside_range_fs_clamp_unrestricted.amber#L68-L75)).
- The shared Amber instance creates a Vulkan engine configuration, executes the recipe, logs an Amber error on failure, and returns CTS pass or fail from the Amber result ([`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fs_clamp` | Incorrect viewport depth mapping, depth clamp zero-one behavior, or depth attachment write. |
| `out_of_range` | Incorrect handling of an out-of-range `gl_FragDepth` value in the non-unrestricted path, depth comparison, or depth write. |
| `ez_fs_clamp` | Incorrect ordering or interaction between early fragment tests and the tested depth clamp path. |
| `bias_fs_clamp` | Incorrect constant depth bias, clamp ordering, or attachment conversion. |
| `bias_outside_range` | Incorrect large-bias arithmetic or depth-range handling for a floating-point depth attachment. |
| `bias_outside_range_fs_clamp` | Incorrect distinction between shader-observed depth and the clamped depth attachment value. |
| `out_of_range_unrestricted` | Incorrect `VK_EXT_depth_range_unrestricted` behavior, depth comparison, or floating-point depth write. |
| `bias_outside_range_fs_clamp_unrestricted` | Incorrect interaction between unrestricted depth range, large depth bias, and the depth attachment write. |

A shared failure across cases can also indicate Amber parsing, shader compilation, pipeline creation, resource binding, synchronization, or result-checking infrastructure rather than the depth operation selected by one case.

### Cause Analysis

#### Viewport clamp and depth-range handling

**Possible failure symptoms:** A case expecting `0.9`, `1.0`, or another range-derived depth reports a different `depth0` value, or the color rectangle is not green because the depth test rejects the draw.

**Possible implementation causes:** The implementation may apply the viewport transform, zero-one clamp, or floating-point unrestricted rule incorrectly. The recipes compare both attachment contents and, in storage-buffer cases, the fragment shader's `gl_FragCoord.z`, which helps separate the two observed stages but does not identify a unique driver component.

#### Fragment depth and early-test behavior

**Possible failure symptoms:** `out_of_range` or `ez_fs_clamp` fails while the corresponding color and depth expectations do not match the recipe. `ez_fs_clamp` can fail only when its early-fragment-tests declaration changes the depth-test timing.

**Possible implementation causes:** The failure may involve `gl_FragDepth` handling, the order in which fragment tests use shader or rasterized depth, or the interaction between early fragment tests and depth writes. The source does not isolate a narrower cause.

#### Depth bias and attachment write

**Possible failure symptoms:** A bias case reports a value other than `0.625`, `0.9`, `1.0`, or `1.9`, or the storage buffer and depth attachment disagree in a way not allowed by that recipe.

**Possible implementation causes:** The implementation may calculate constant bias incorrectly, apply it at the wrong point relative to clamping, or convert the resulting value incorrectly for the `D32_SFLOAT` attachment. The source sets slope factor to `0.0`, so slope-dependent behavior is outside this page's coverage.

#### Unrestricted extension path

**Possible failure symptoms:** An `_unrestricted` case fails with an attachment value of `1.0` or another clamped result when the recipe expects `2.0` or `1.9`, or the unrestricted and non-unrestricted cases produce the same result where the recipes expect different values.

**Possible implementation causes:** The extension may not affect the depth-range step as required, the floating-point attachment path may still clamp to `[0, 1]`, or the custom-device selection may not preserve the intended extension distinction. Source-level investigation is needed to distinguish capability setup from depth processing.

#### Amber execution and result checking

**Possible failure symptoms:** The recipe cannot parse, an inline shader fails to compile, an attachment or buffer cannot be created, or an `EXPECT` command reports a mismatch before a depth-specific comparison can identify the affected value.

**Possible implementation causes:** The issue may be in the Amber interpreter, shader compiler, pipeline or resource setup, synchronization, or result readback. The shared runner returns a generic CTS failure after logging the Amber error, so the test result alone does not localize this class of failure.

## Case Pruning

### Requirement-based pruning

- Every case requires `DepthClampZeroOneFeatures.depthClampZeroOne`, which the shared Amber support code recognizes as a feature requirement. Missing requirements cause `NotSupportedError` before execution ([`DepthTestCase::initDeviceCapabilities()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L79-L88), [`AmberTestCase::checkSupport()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286)).
- `fs_clamp`, `ez_fs_clamp`, and `bias_fs_clamp` additionally require `Features.depthClamp` and `Features.fragmentStoresAndAtomics`. The other storage-buffer cases require `Features.fragmentStoresAndAtomics`; `out_of_range` and `out_of_range_unrestricted` do not use a storage buffer ([`TestInfo` table](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L126-L148)).
- The two `_unrestricted` cases require `VK_EXT_depth_range_unrestricted`. The wrapper marks them as unrestricted and uses the normal device, while the other cases use a custom-device path intended to keep that extension disabled ([`createDepthTestCase()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L103-L121), [`DepthTestCase::getInstanceCapabilitiesId()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L56-L76)).
- The non-unrestricted custom-device path enables either `VK_KHR_depth_clamp_zero_one` or `VK_EXT_depth_clamp_zero_one`, plus the requested feature bits. A device that lacks a required feature or extension skips the case rather than treating unsupported behavior as a failure ([`initDeviceCapabilities()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L79-L88)).

### Design-based pruning

- The source intentionally registers one fixed Amber recipe for each behavior combination. There is no generated parameter matrix, randomization, or format sweep in `vktAmberDepthTests.cpp`.
- The unrestricted cases are explicit reruns only for `out_of_range` and `bias_outside_range_fs_clamp`, because the source marks those tests as producing different results with `VK_EXT_depth_range_unrestricted` ([`createTests()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L137-L148)).
- All recipes use a 60 x 60 framebuffer and a `D32_SFLOAT` depth attachment. The narrow setup keeps the comparison focused on depth-range semantics rather than format coverage or command-recording variants.

## Key Takeaways

- The eight test cases compare the shader-observed depth value with the value that reaches the `D32_SFLOAT` attachment when the relevant recipe provides `fs_depth`.
- `CLAMP on`, `gl_FragDepth`, viewport endpoints, and large constant bias values select different points in the depth path. The expected values make those distinctions visible.
- The `_unrestricted` cases are separate registrations, not a runtime toggle inside one case. They require `VK_EXT_depth_range_unrestricted` and use the ordinary device path.
- A failed `EXPECT` proves that the rendered artifact differs from the recipe's expected result. It does not, by itself, identify whether the cause is shader compilation, fixed-function depth processing, resource setup, or readback.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Depth test registration table | [`TestInfo` values and `createTests()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L96-L156) | Defines the eight direct children, their recipe filenames, and their feature/extension requirements. |
| Custom device and capability setup | [`DepthTestCase::initDeviceCapabilities()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L56-L92) | Shows the extension and feature setup and the intended separation of unrestricted reruns. |
| Amber recipe loading | [`createDepthTestCase()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L103-L121) | Maps a registered child to `vulkan/amber/depth/<name>.amber`. |
| Representative clamp recipe | [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L15-L76) | Shows shader stages, resources, clamp state, viewport range, draw, and expected values. |
| Early-test recipe | [`ez_fs_clamp.amber`](../../../data/vulkan/amber/depth/ez_fs_clamp.amber#L15-L77) | Adds `layout(early_fragment_tests) in;` while retaining the clamp expectations. |
| Out-of-range recipes | [`out_of_range.amber`](../../../data/vulkan/amber/depth/out_of_range.amber#L15-L67), [`out_of_range_unrestricted.amber`](../../../data/vulkan/amber/depth/out_of_range_unrestricted.amber#L15-L68) | Contrast `gl_FragDepth = 2.0` with and without `VK_EXT_depth_range_unrestricted`. |
| Bias recipes | [`bias_fs_clamp.amber`](../../../data/vulkan/amber/depth/bias_fs_clamp.amber#L15-L76), [`bias_outside_range.amber`](../../../data/vulkan/amber/depth/bias_outside_range.amber#L15-L74), [`bias_outside_range_fs_clamp.amber`](../../../data/vulkan/amber/depth/bias_outside_range_fs_clamp.amber#L15-L74), [`bias_outside_range_fs_clamp_unrestricted.amber`](../../../data/vulkan/amber/depth/bias_outside_range_fs_clamp_unrestricted.amber#L15-L75) | Define constant-bias values, optional clamp state, and attachment/storage-buffer expectations. |
| Shared Amber execution | [`AmberTestCase::parse()`, `initPrograms()`, and `AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L615) | Explains recipe parsing, GLSL compilation, Vulkan execution, and CTS status conversion. |
| Required-feature checking | [`AmberTestCase::checkSupport()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286) | Shows that missing declared requirements produce unsupported status before execution. |
| Vulkan depth semantics | [Depth test and clamping](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-depth) and [depth bias](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-depthbias) | Provides the normative order and meaning of depth clamping, range handling, and bias. |
| Mustpass coverage | [`depth.txt`](../../../mustpass/main/vk-default/depth.txt#L1-L8) | Lists the same eight executable `dEQP-VK.depth.*` paths. |
