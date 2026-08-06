## Overview

**Core question:** Do occlusion queries report the expected visible-sample state through every result, reset, and rendering path exercised by `query_pool.occlusion_query`?

- [`vktQueryPoolOcclusionTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp) implements the `occlusion_query` test family declared by [`vktQueryPoolOcclusionTests.hpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.hpp).
- The family covers focused smoke cases, a functional matrix, result-buffer layout cases, and two function-style no-attachment cases.
- Tests compare query values and availability after host reads or device-side copies. They also cover host reset, recorded reset, clear operations, blit, resolve, and Vulkan SC-specific registration differences.

## Background Knowledge

- A Vulkan query pool stores asynchronous query state. The host can read it with `vkGetQueryPoolResults`, or device commands can copy it to a buffer with `vkCmdCopyQueryPoolResults`. A result also has an availability state. See the Vulkan [Queries](../../../../vulkan-docs/src/chapters/queries.adoc) chapter.
- `VK_QUERY_CONTROL_PRECISE_BIT` requests precise occlusion results when `occlusionQueryPrecise` is enabled. Conservative queries still distinguish zero visibility from a positive result, but do not require one exact positive count in the matrix.
- A result element contains a 32-bit or 64-bit value and can optionally contain an availability value. `stride` determines the spacing between elements in the result destination.

## Registration Hierarchy

```text
query_pool.occlusion_query
├── basic_conservative
├── basic_precise
├── stride_zero
├── stride_max
├── clear_attachments_only
├── clear_attachments_with_draw
├── blit
├── resolve
├── no_attachments_single_sample
└── no_attachments_multisample
```

The same test family also registers the generated functional and stride matrices as direct children. [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1691-L2040) is the authoritative registration point.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Query control | `conservative`, `precise` | Chooses non-exact-positive or precise validation. | [`init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1771-L1777) |
| Primitive topology | `points`, `triangles` | Changes the coverage pattern and expected counts. | [`init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1779-L1784) |
| Result size | `32`, `64` | Selects the result element width. | [`init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1786-L1789) |
| Wait mode | `queue`, `query` in the registered main matrix; the implementation also defines `none` for an unavailable-result path, but `init()` does not register it | Selects queue-idle synchronization, query-result wait, or (for the unregistered path) an allowed unavailable read. | [`init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1792-L1805), [`OcclusionQueryTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L920-L923) |
| Results mode | `get`, `get_reset`, `get_create_reset`, `copy`, `copy_reset` | Selects host read, host reset, create-time reset, device copy, or reset before copy. | [`init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1797-L1803) |
| Availability | `without`, `with` | Adds an availability value after each result. | [`init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1814-L1818) |
| Draw variant | `points`, `triangles`, optional `_discard` | Selects rasterization coverage and the fragment-discard path. | [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1524-L1545) |
| Result layout | stride `0`, `1x`, `2x`, `3x`, `4x`, `5x`, `13x`, `1024x`; optional `_dstoffset` | Exercises result spacing and a nonzero first destination offset. | [`init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1932-L2035) |

## Behavior Parameters

The page has two related behavioral axes. The first changes what coverage is measured. The second changes how the same observations are retrieved and laid out.

### Basic cases: `basic_conservative` and `basic_precise`

The basic instance uses a two-query pool. One query surrounds no draw work, and the other surrounds a clear and/or a three-vertex point draw. The conservative case accepts a positive result where visibility is expected; the precise case requires the exact source-defined value. [`BasicOcclusionQueryTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L468-L680) performs the focused checks.

### Functional coverage: points and triangles

The functional instance records three queries for all, partially occluded, and fully occluded geometry. Point-list cases expect `3`, `1`, and `0` samples for those slots. Triangle-list cases use the 128x128 render area and source-defined tolerance ranges. A `_discard` triangle case expects about half the normal covered area because the fragment shader discards alternating pixel positions.

### Result transport: `get`, `get_reset`, `get_create_reset`, `copy`, and `copy_reset`

Host-read modes call `vkGetQueryPoolResults`. Copy modes write a host-visible result buffer with `vkCmdCopyQueryPoolResults`, or with `vkCmdCopyQueryPoolResultsToMemoryKHR` for sampled `_device_address` cases. `get_reset` reads results, resets the pool from the host, then checks that a second read returns `VK_NOT_READY` and clears availability when requested. `copy_reset` resets before copying and checks availability rather than the result value.

### Rendering and layout variants

`clear_color` and `clear_depth` ensure internal clear operations do not count as occlusion samples. `no_color_attachments` uses a depth-only render pass. `blit` and `resolve` place the additional image operation before the measured draw. The stride matrix varies result width, availability, stride, and destination offset. Registration removes combinations whose element does not fit a nonzero stride, and uses zero stride only with command-copy mode.

## Shader Analysis

The shaders are small and do not store query results. The fragment stage supplies coverage by either running to its color write or executing `discard`; the query hardware observes the resulting samples.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.query_pool.occlusion_query.copy_results_precise_size_64_wait_queue_with_availability_draw_triangles_discard
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `precise` | The query result must fall within the precise expected range. |
| `triangles_discard` | Triangle coverage is measured while alternating fragment positions are discarded. |
| `size_64_with_availability` | Each copied element contains a 64-bit result and an availability value. |
| `copy_results` | The device writes the query results into the destination buffer. |

#### Purpose

The fragment shader writes a constant color for surviving fragments and discards alternating pixel positions. The query therefore measures rasterized samples that survive fragment processing; it does not consume shader output data.

#### Structural Design

| Phase | Shader action | Query consequence |
|---|---|---|
| 1 | Write the constant color | The fragment is eligible to contribute. |
| 2 | Compare the integer x and y fragment coordinates modulo two | Alternating pixel positions select the discard branch. |
| 3 | Execute `discard` on matching positions | Those fragments do not contribute to the visible-sample count. |

#### Shader Code

```glsl
#version 400
layout(location = 0) out vec4 out_FragColor;
void main()
{
    out_FragColor = vec4(0.07, 0.48, 0.75, 1.0);
    /// Keep alternating fragment coordinates out of the query's visible sample count.
    if ((int(gl_FragCoord.x) % 2) == (int(gl_FragCoord.y) % 2))
        discard;
}
```

#### Additional Info

- The vertex shader passes the source vertex positions to `gl_Position`; it also sets `gl_PointSize` to `1.0` for point-list variants. See [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1538-L1545).
- The host uses the discard branch only for triangle variants. Registration excludes `_discard` from point-list cases because a one-pixel point does not provide a useful half-coverage comparison.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| `discardHalf` | Adds the coordinate-parity `discard` branch. | [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1524-L1536) |
| `primitiveTopology` | Changes how the fixed vertex shader input is rasterized; the fragment source stays the same. | [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L293-L307) |
| no-attachment cases | Uses separate version 460 vertex and fragment sources without the discard branch. | [`initNoAttachmentsPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1561-L1577) |

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
; Bound: 36
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %out_FragColor %gl_FragCoord
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 400
               OpName %main "main"
               OpName %out_FragColor "out_FragColor"
               OpName %gl_FragCoord "gl_FragCoord"
               OpDecorate %out_FragColor Location 0
               OpDecorate %gl_FragCoord BuiltIn FragCoord
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
%out_FragColor = OpVariable %_ptr_Output_v4float Output
%float_0_0700000003 = OpConstant %float 0.0700000003
%float_0_479999989 = OpConstant %float 0.479999989
 %float_0_75 = OpConstant %float 0.75
    %float_1 = OpConstant %float 1
         %14 = OpConstantComposite %v4float %float_0_0700000003 %float_0_479999989 %float_0_75 %float_1
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
        %int = OpTypeInt 32 1
      %int_2 = OpConstant %int 2
     %uint_1 = OpConstant %uint 1
       %bool = OpTypeBool
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %out_FragColor %14
         %20 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %21 = OpLoad %float %20
         %23 = OpConvertFToS %int %21
         %25 = OpSMod %int %23 %int_2
         %27 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %28 = OpLoad %float %27
         %29 = OpConvertFToS %int %28
         %30 = OpSMod %int %29 %int_2
         %32 = OpIEqual %bool %25 %30
               OpSelectionMerge %34 None
               OpBranchConditional %32 %33 %34
         %33 = OpLabel
               OpKill
         %34 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The regular path creates 128x128 color and depth resources, a graphics pipeline, a host-visible vertex buffer, and a two- or three-query `VK_QUERY_TYPE_OCCLUSION` pool. The no-color-attachment branch creates only the depth attachment.
- The functional instance records reset and query commands, renders all, partially occluded, and fully occluded geometry, and optionally records a clear, blit, resolve, or result copy. Copy modes add a buffer barrier before host inspection. See [`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L821-L942) and [`cmdCopyQueryPoolResults()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1016-L1032).
- `WAIT_QUEUE` waits for the queue before reading. `WAIT_QUERY` sets `VK_QUERY_RESULT_WAIT_BIT`. `WAIT_NONE` allows an unavailable result, but the validator still checks every available result.
- Precise cases compare the result against the expected bounds. Conservative cases require a nonzero result for positive-coverage slots. A fully occluded slot must remain exactly zero.
- The no-attachment cases render into a 2x2 framebuffer with a half-width scissor. They expect half of the framebuffer samples, using one or four samples per pixel for the single-sample and multisample variants. See [`noAttachmentsTest()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1591-L1682).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `basic_conservative` | Basic query begin/end or conservative result retrieval does not report the required zero/non-zero observations. |
| `basic_precise` | Precise occlusion counting or precise-feature handling is incorrect. |
| `get`, `get_reset`, `get_create_reset` | Host result retrieval, host reset, or query-pool create-reset behavior is incorrect. |
| `copy`, `copy_reset` | Device-side result copy, copy reset, or result-buffer synchronization is incorrect. |
| points / triangles / `_discard` | Sample coverage, depth testing, primitive rasterization, or fragment discard handling is incorrect. |
| clear / no color attachments / blit / resolve | The tested render-pass or additional-operation path changes query accounting incorrectly. |
| 32/64-bit, availability, stride, destination offset, device address | Result element width, availability placement, stride addressing, offset handling, or the optional device-address copy path is incorrect. |

### Cause Analysis

#### Query begin/end or result retrieval

**Possible failure symptoms:** A basic query returns a nonzero result for the empty slot, a zero result for visible work, or `VK_NOT_READY` after the test has waited for completion.

**Possible implementation causes:** Source inspection is needed to determine whether the defect lies in query state tracking, command execution, or host result retrieval. The Vulkan common-validity rules require unavailable queries at `vkCmdBeginQuery` and graphics-capable command-pool support for occlusion queries.

#### Precise counting

**Possible failure symptoms:** A precise result falls outside the source-defined exact value or tolerance range, or the device rejects a precise query without the required feature.

**Possible implementation causes:** The implementation may mishandle occlusion sample accounting, depth coverage, or the `occlusionQueryPrecise` feature path. The test source does not identify a specific faulty layer.

#### Result transport and reset

**Possible failure symptoms:** A host read or device copy returns the wrong value, availability is zero when the test waited, reset results remain available, or a `copy_reset` result has nonzero availability.

**Possible implementation causes:** Source-level investigation is needed for synchronization, reset ordering, result width, availability placement, stride addressing, or device-address command handling. The test separates host and device paths to expose these behaviors.

#### Rendering and fragment coverage

**Possible failure symptoms:** All, partially occluded, and fully occluded slots do not follow their expected zero, positive, or bounded coverage rules. Clear, no-attachment, blit, and resolve variants can fail independently.

**Possible implementation causes:** The failure may come from rasterization, depth testing, fragment discard, render-pass handling, or query accounting around the additional operation. The test evidence does not support assuming one implementation component.

## Case Pruning

- The registration loop omits `WAIT_QUERY` with `RESULTS_MODE_GET_RESET` because the second read after reset may not return in finite time.
- `RESULTS_MODE_COPY_RESET` requires availability so the test can check that reset cleared it.
- Point-list `_discard` combinations are omitted.
- Nonzero strides smaller than the result element are omitted. Zero stride is limited to `copy` and does not use `_dstoffset`.
- `_device_address` cases are sampled only for copy and copy-reset modes, and are compiled out under `CTS_USES_VULKANSC`.
- `get_create_reset` and host-reset cases require the corresponding functionality. Precise cases require `occlusionQueryPrecise`; resolve requires 4x support for the transfer source format. The no-attachment cases require the relevant `framebufferNoAttachmentsSampleCounts` bit.

## Key Takeaways

- The family tests both occlusion visibility semantics and the ways applications retrieve, reset, and lay out query results.
- Precise mode uses bounded coverage checks, while conservative positive cases require only a nonzero result. Fully occluded cases still require zero.
- The fragment shader's optional discard branch changes expected triangle coverage, but the query result is checked on the host after result retrieval or copyback.
- Registration evidence in the Vulkan and Vulkan SC mustpass files covers the smoke cases, generated matrices, stride variants, and no-attachment cases. Non-SC mustpass entries include the sampled `_device_address` cases.

## Source Reference Appendix

- [`QueryPoolOcclusionTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1691-L2040): registration, matrix dimensions, exclusions, and support variants.
- [`OcclusionQueryTestVector`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L329-L396): complete implementation parameter vector.
- [`StateObjects::StateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L105-L317): render targets, no-color-attachment render pass, blit/resolve images, and graphics pipeline.
- [`BasicOcclusionQueryTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L468-L680): focused cases and host `vkGetQueryPoolResults` checks.
- [`OcclusionQueryTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L821-L942): functional submission, waits, copyback, and status.
- [`captureResults()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1215-L1335) and [`validateResults()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1357-L1472): result decoding, availability, reset, and expected-value rules.
- [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1524-L1545) and [`noAttachmentsTest()`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1591-L1682): generated shaders and function-style no-attachment coverage.
- [`query-pool.txt`](../../../mustpass/main/vk-default/query-pool.txt) and [`query-pool.txt`](../../../mustpass/main/vksc-default/query-pool.txt): mustpass coverage for Vulkan and Vulkan SC.
- [`Queries`](../../../../vulkan-docs/src/chapters/queries.adoc), [`query_begin_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/query_begin_common.adoc), and [`query_results_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/query_results_common.adoc): query state, begin-query constraints, and result-layout validity.
