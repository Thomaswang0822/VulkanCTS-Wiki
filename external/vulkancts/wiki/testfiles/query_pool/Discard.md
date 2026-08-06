## Overview

**Core question:** Does an occlusion query reflect fragment discard, sample-mask evaluation, and alpha-to-coverage according to the normal and early-fragment ordering rules?

- This page covers the `query_pool.discard` test family implemented by [`vktQueryPoolDiscardTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L48-L67).
- Each case renders a 32 x 32 strip and compares an occlusion-query result with the expected visibility rule. It also checks the resolved color image so a query result cannot pass by coincidence.
- The matrix combines early or normal fragment tests, depth disabled or enabled, `none` or `precise` query control, and one of the discard mechanisms.
- The test targets the Vulkan ordering rules for sample-mask testing and multisample coverage, including the `VK_KHR_maintenance5` properties used by early-fragment cases.

## Background Knowledge

- An occlusion query counts samples that pass the relevant fragment operations. It does not count fragment shader invocations that later lose all coverage.
- `layout(early_fragment_tests) in;` permits depth and stencil tests to occur before fragment shading. Maintenance5 properties define when sample-mask testing and multisample coverage occur relative to sample counting for this execution mode. See [Fragment Operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops).
- Alpha-to-coverage converts fragment alpha into a multisample coverage mask. The alpha variants therefore use four color samples and resolve them into the single-sample image checked by the host.

## Registration Hierarchy

```text
query_pool.discard
├── normal
└── early
```

`normal` and `early` each expand to `no_depth` and `with_depth`, then `none` and `precise`, followed by the discard-mechanism test cases. The factory creates this Cartesian structure in [`createDiscardTests()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L538-L585). Non-SC builds add `alpha_to_coverage_dynamic`; Vulkan SC builds omit that leaf.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Early fragment mode | `normal`, `early` | Selects an ordinary fragment shader or one with `EarlyFragmentTests`. | [`TestParameters`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L56-L67), [`createDiscardTests()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L556-L560) |
| Depth mode | `no_depth`, `with_depth` | Enables both depth testing and depth writes with `VK_COMPARE_OP_LESS`. | [`createPipeline()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L299-L312) |
| Query control | `none`, `precise` | Selects no query-control flags or `VK_QUERY_CONTROL_PRECISE_BIT`. | [`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L364-L367) |
| Fragment mechanism | `discard`, `sample_mask`, `alpha_to_coverage`, `alpha_to_coverage_dynamic` | Chooses the operation that removes coverage on even X coordinates. The dynamic leaf is non-SC only. | [`DiscardType`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L48-L54), [`createDiscardTests()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L547-L553) |
| Rendering setup | 32 x 32, `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_D16_UNORM`, triangle strip, four vertices | Provides a full-screen draw and a fixed image for exact validation. Alpha variants use four samples plus a resolve attachment. | [`QueryPoolDiscardTestInstance`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L69-L83), [`createRenderPass()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L115-L131), [`createRenderPass()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L148-L159) |

The matrix has 32 leaves in non-SC builds and 24 in Vulkan SC builds. The source registers the leaves directly; the repository's registration validator confirms the `query_pool.discard`, `query_pool.discard.normal`, and `query_pool.discard.early` prefixes.

## Behavior Parameters

The primary behavioral axis is the fragment mechanism. The other dimensions change when or how its coverage contributes to the query.

### `discard`: terminate even-X fragment shader invocations

The fragment shader writes white first, then executes `discard;` when `uint(gl_FragCoord.x)` is even. Those invocations contribute no color output and no surviving sample coverage. The odd columns remain white.

### `sample_mask`: clear even-X sample coverage

The shader assigns `gl_SampleMask[0] = 0` for even X coordinates. The invocation continues, but the sample-mask test removes its coverage before the later operations defined by Vulkan. This distinguishes a coverage test from shader termination.

### `alpha_to_coverage`: derive coverage from zero alpha

For even X coordinates the shader writes alpha zero. The pipeline enables alpha-to-coverage and uses four color samples, so the alpha value changes the multisample coverage mask. The render pass resolves that attachment into the single-sample color image.

### `alpha_to_coverage_dynamic`: set alpha-to-coverage at draw time

This uses the same shader and four-sample path as `alpha_to_coverage`, but the pipeline declares `VK_DYNAMIC_STATE_ALPHA_TO_COVERAGE_ENABLE_EXT` and the command buffer enables it with `vkCmdSetAlphaToCoverageEnableEXT`. It is registered and supported only outside Vulkan SC.

`early` changes the ordering question for all mechanisms. With early fragment tests, the implementation must satisfy the applicable Maintenance5 ordering properties. `with_depth` uses the cleared depth value of 1.0 and a `LESS` comparison, while `no_depth` disables both depth testing and depth writes. Query precision changes validation, not shader behavior: precise cases require an exact count; `none` cases require only a non-zero result.

## Shader Analysis

The source generates a small vertex shader and a fragment shader. The fragment stage is the tested shader logic, so one representative walkthrough is sufficient. The same generated shape applies to the three mechanisms; only the even-X branch changes.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.query_pool.discard.normal.no_depth.precise.discard
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `normal` | The fragment shader has no `EarlyFragmentTests` execution mode. |
| `no_depth` | Depth testing does not affect which fragments reach the query. |
| `precise` | The host checks the exact occlusion count. |
| `discard` | Even-X invocations execute `discard`; odd-X invocations write white. |

#### Purpose

The shader creates an observable half-width pattern while the query counts only surviving samples. The host can therefore compare the query result with the image pattern.

#### Structural Design

| Shader phase | Result |
|---|---|
| Initialize coverage and color | Set all sample-mask bits and write white. |
| Select columns | Convert `gl_FragCoord.x` to an unsigned integer and test its low bit. |
| Even X | Execute `discard`. |
| Odd X | Return with the white output intact. |

#### Shader Code

```glsl
#version 450
layout(location=0) out vec4 outColor;
void main() {
    /// Start with all samples covered and a white fragment output.
    gl_SampleMask[0] = ~0;
    outColor = vec4(1.0f);
    /// The test removes every even-X column with the selected mechanism.
    if ((uint(gl_FragCoord.x) & 1u) == 0u) {
       discard;
    }
}
```

#### Additional Info

- The `early` representative adds `layout(early_fragment_tests) in;` before the output declaration.
- `sample_mask` replaces `discard` with `gl_SampleMask[0] = 0;`; alpha variants replace it with `outColor = vec4(1.0f, 1.0f, 1.0f, 0.0f);`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Early fragment mode | Adds `layout(early_fragment_tests) in;`. | [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L504-L517) |
| Fragment mechanism | Changes only the even-X statement. | [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L518-L529) |
| Depth mode | Does not change shader text; it changes fixed-function depth state. | [`createPipeline()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L299-L312) |
| Query control | Does not change shader text; it changes `vkCmdBeginQuery` flags. | [`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L364-L367) |

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
; Bound: 35
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_SampleMask %outColor %gl_FragCoord
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_SampleMask "gl_SampleMask"
               OpName %outColor "outColor"
               OpName %gl_FragCoord "gl_FragCoord"
               OpDecorate %gl_SampleMask BuiltIn SampleMask
               OpDecorate %outColor Location 0
               OpDecorate %gl_FragCoord BuiltIn FragCoord
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_int_uint_1 = OpTypeArray %int %uint_1
%_ptr_Output__arr_int_uint_1 = OpTypePointer Output %_arr_int_uint_1
%gl_SampleMask = OpVariable %_ptr_Output__arr_int_uint_1 Output
      %int_0 = OpConstant %int 0
     %int_n1 = OpConstant %int -1
%_ptr_Output_int = OpTypePointer Output %int
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %float_1 = OpConstant %float 1
         %21 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
       %bool = OpTypeBool
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpAccessChain %_ptr_Output_int %gl_SampleMask %int_0
               OpStore %15 %int_n1
               OpStore %outColor %21
         %26 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %27 = OpLoad %float %26
         %28 = OpConvertFToU %uint %27
         %29 = OpBitwiseAnd %uint %28 %uint_1
         %31 = OpIEqual %bool %29 %uint_0
               OpSelectionMerge %33 None
               OpBranchConditional %31 %32 %33
         %32 = OpLabel
               OpKill
         %33 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test creates an occlusion query pool with one `VK_QUERY_TYPE_OCCLUSION` query, a command pool, the render pass, pipeline, and a host-visible color readback buffer.
- It resets the query, begins it with either no flags or `VK_QUERY_CONTROL_PRECISE_BIT`, clears color to black and depth to 1.0, draws four vertices as a triangle strip, ends the render pass, and ends the query.
- It inserts an image barrier, copies the single-sample color image to the host-visible buffer, submits the command buffer to the universal queue, waits, invalidates the allocation, and reads the query with `VK_QUERY_RESULT_WAIT_BIT`. See [`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L331-L409).
- Precise cases compare against an exact expected value. Start with 1024 pixels. Normal discard and sample-mask cases expect 512 because even columns lose coverage. Early cases expect 1024 because the required Maintenance5 ordering places the tested sample-mask operation before sample counting. Alpha-to-coverage cases multiply by four for the four samples, giving 2048 for normal and 4096 for early. The source applies this formula for both static and dynamic alpha-to-coverage.
- Non-precise cases require a non-zero query result. The host then checks every pixel: even X must be black and odd X must be white. See [`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L411-L454).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `discard` | Fragment termination, sample counting, or color readback does not match the expected even-X coverage. |
| `sample_mask` | Sample-mask output handling or the Maintenance5 sample-mask ordering does not match the expected query count. |
| `alpha_to_coverage` | Alpha-to-coverage coverage generation, multisample counting, resolve behavior, or color readback is incorrect. |
| `alpha_to_coverage_dynamic` | Dynamic alpha-to-coverage state, multisample counting, resolve behavior, or color readback is incorrect. |

All behavior values also share setup, synchronization, query-result retrieval, and image-validation failure causes.

### Cause Analysis

#### Fragment operation or sample-count ordering

**Possible failure symptoms:** A precise query returns a value other than 512 or 1024 for the discard and sample-mask cases, or a non-precise query returns zero. The image check may also find a non-black even column or a non-white odd column.

**Possible implementation causes:** The implementation may apply fragment discard, sample-mask evaluation, early tests, or sample counting in a way that does not satisfy the Vulkan fragment-operation rules. For early cases, the relevant `earlyFragmentSampleMaskTestBeforeSampleCounting` property controls the required sample-mask ordering. The test source and [Fragment Operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops) provide the evidence; a more specific driver or hardware cause needs source-level investigation.

#### Multisample coverage and alpha-to-coverage

**Possible failure symptoms:** An alpha case returns a count other than 2048 in `normal` or 4096 in `early`, or the resolved image does not contain the expected stripe pattern.

**Possible implementation causes:** The implementation may generate multisample coverage from alpha incorrectly, count samples at the wrong point, or resolve the multisampled attachment incorrectly. In early cases, `earlyFragmentMultisampleCoverageAfterSampleCounting` selects the required ordering tested by this family. A more specific implementation cause needs source-level investigation.

#### Fixed-function depth state

**Possible failure symptoms:** Cases with depth enabled produce a different query count or image than the corresponding `no_depth` case.

**Possible implementation causes:** The depth test or depth write state, cleared depth value, or interaction between depth testing and the tested fragment operation may be wrong. The source sets `LESS`, enables depth writes when `with_depth` is selected, and clears depth to 1.0. A specific fault location requires further investigation.

#### Dynamic alpha-to-coverage state

**Possible failure symptoms:** `alpha_to_coverage_dynamic` fails while the static alpha case passes, including a mismatch in query count or the resolved stripe pattern.

**Possible implementation causes:** The implementation may fail to apply `vkCmdSetAlphaToCoverageEnableEXT` to the bound pipeline or may mishandle the dynamic state while processing multisample coverage. The test requires `extendedDynamicState3AlphaToCoverageEnable`; a more specific cause needs source-level investigation.

#### Host-side result checking

**Possible failure symptoms:** The query value is correct but the case fails while checking the copied color image, or the query read returns an unexpected value after the wait.

**Possible implementation causes:** The command sequence may expose an image layout, transfer, host visibility, or query-result retrieval problem. The test uses explicit image and buffer barriers, waits for submission, invalidates host-visible memory, and reads one 32-bit result. A specific host or implementation cause needs further investigation.

## Case Pruning

### Requirement-based pruning

- `precise` cases require the `occlusionQueryPrecise` device feature.
- `alpha_to_coverage_dynamic` requires `extendedDynamicState3AlphaToCoverageEnable` and is not compiled or registered for Vulkan SC.
- Every `early` non-SC case requires `earlyFragmentSampleMaskTestBeforeSampleCounting`.
- Early alpha-to-coverage cases also require `earlyFragmentMultisampleCoverageAfterSampleCounting`.
- Vulkan SC rejects all `early` cases in `checkSupport()`.

These checks are in [`QueryPoolDiscardTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L477-L502).

### Design-based pruning

The factory does not remove combinations of the four ordinary axes. It registers both depth modes, both query-control modes, both early-fragment modes, and each mechanism compiled for the build. The only registered matrix-size difference is the non-SC `alpha_to_coverage_dynamic` leaf. Vulkan SC rejects the already registered `early` cases during support checking.

## Key Takeaways

- The family compares two observables: an occlusion count and a resolved black/white stripe image.
- `precise` checks exact counts. `none` checks only that the query is non-zero, while the image check remains exact.
- Normal and early branches intentionally exercise different ordering rules. Maintenance5 properties gate the early branches rather than allowing them to run with ambiguous ordering.
- Alpha-to-coverage changes the resource setup to four samples plus a resolve attachment, so its expected precise count is four times the corresponding single-sample count.
- Static and dynamic alpha-to-coverage share shader behavior; the dynamic case adds a pipeline-state command and a feature gate.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Parameter and test-instance definitions | [`vktQueryPoolDiscardTests.cpp#L48-L99`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L48-L99) | Defines the four behavior dimensions and resources. |
| Render pass construction | [`createRenderPass()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L101-L266) | Shows single-sample and four-sample resolve attachments. |
| Pipeline construction | [`createPipeline()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L268-L329) | Shows depth state, alpha-to-coverage, and dynamic state. |
| Draw and validation flow | [`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L331-L455) | Records the query and draw, copies the image, and checks both results. |
| Feature and property gates | [`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L477-L502) | Defines precise, dynamic-state, Maintenance5, and Vulkan SC support rules. |
| Shader generation | [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L504-L534) | Generates the vertex and fragment shader variants. |
| Test registration | [`createDiscardTests()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L538-L585) | Builds the exact hierarchy and matrix. |
| Vulkan fragment-operation semantics | [Fragment Operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops) | Defines sample-mask, multisample-coverage, sample-counting, and Maintenance5 ordering. |
| Vulkan query semantics | [Queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries) | Defines asynchronous query pools and occlusion queries. |
