## Overview

**Core question:** Does tessellation winding, together with the tessellation domain origin, agree with Vulkan back-face culling and viewport orientation?

- `vktTessellationWindingTests.cpp` implements the `tessellation.winding` test family.
- Each test case combines a tessellation domain origin, `triangles` or `quads`, GLSL or HLSL, `ccw` or `cw` winding, and an optional viewport Y flip.
- The test renders with both static `frontFace` pipeline states, copies the 64x64 color image to host-visible memory, and checks whether the expected primitive survived culling.
- The page covers the relationship between the shader's winding qualifier, domain origin, rasterizer state, and image check.

## Background Knowledge

- A tessellation control or tessellation evaluation shader can request `VertexOrderCw` or `VertexOrderCcw`. Vulkan applies that order to triangles generated in `Triangles` and `Quads` modes. The order is defined in normalized tessellation domain space, not by the order in which an implementation happens to emit primitives. See [`tessellation-vertex-winding-order`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-vertex-winding-order).
- The tessellation domain origin changes the sign convention used to interpret that order. With an upper-left origin, negative signed area is counter-clockwise; with a lower-left origin, positive signed area is counter-clockwise. If the pipeline omits `VkPipelineTessellationDomainOriginStateCreateInfo`, Vulkan uses upper-left origin. See [`tessellation.adoc#tessellation-pipeline-state`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-pipeline-state).
- Vulkan classifies a polygon from its framebuffer-space area. `VK_FRONT_FACE_COUNTER_CLOCKWISE` treats positive area as front-facing, `VK_FRONT_FACE_CLOCKWISE` treats negative area as front-facing, and `VK_CULL_MODE_BACK_BIT` discards the other orientation. See [`primsrast-polygons-basic`](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-polygons-basic).

## Registration Hierarchy

```text
tessellation.winding
├── default_domain
├── lower_left_domain
└── upper_left_domain
```

The three children are intermediate nodes that select the domain-origin configuration. `default_domain` uses Vulkan's default upper-left origin; the other two pass an explicit origin to pipeline creation. The test family has no deeper registered intermediate nodes. The remaining dimensions appear in the generated test-case names.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Domain origin | `default_domain`, `lower_left_domain`, `upper_left_domain` | Selects the tessellation-domain coordinate origin used to interpret `VertexOrderCw` and `VertexOrderCcw`. | [`createWindingTests()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L610-L624) |
| Primitive type | `triangles`, `quads` | Selects the tessellation primitive mode and the shape expected in the image. | [`populateWindingGroup()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L582-L604) |
| Shader language | `glsl`, `hlsl` | Selects the source collection and the syntax used to express the tessellation domain and winding. | [`WindingTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L227-L365) |
| Winding | `ccw`, `cw` | Selects the generated triangles' requested domain-space orientation. This is the primary behavior axis. | [`WindingTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L265-L277) |
| Viewport orientation | absent, `yflip` | Uses a positive or negative viewport height. The verifier adjusts the expected triangle orientation for the flip. | [`WindingTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L528-L535) |

The Vulkan default mustpass list contains all 48 combinations: three domain-origin nodes times two primitive types, two shader languages, two winding values, and two Y orientations. For example, the default-domain GLSL triangle cases are listed in [`tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L1056-L1071).

## Behavior Parameters

The primary behavioral axis is **tessellation winding**. Domain origin, primitive type, language, and viewport orientation condition the interpretation or observation of that axis.

### `ccw`: counter-clockwise generated triangles

The verifier does not always equate the requested winding with the matching `frontFace` value. For each domain origin and viewport orientation, it expects visibility when `((frontFaceWinding == winding) == (domainOrigin == VK_TESSELLATION_DOMAIN_ORIGIN_UPPER_LEFT)) != yFlip`; the other `frontFace` pipeline must cull the primitive. Thus a requested `ccw` case is kept by the `COUNTER_CLOCKWISE` pipeline only for the upper-left, non-flipped combination (or the lower-left, Y-flipped combination), with the corresponding inverse relationship for the other combinations. The domain-origin choice determines the tessellation-space-to-framebuffer orientation sign, and the viewport Y transform can invert it.

### `cw`: clockwise generated triangles

The tessellation evaluation shader requests clockwise vertex order. The expected visible/cull relationship is the inverse of `ccw` for the same domain origin, primitive type, and viewport orientation. The HLSL branch expresses the equivalent topology through the hull-shader `outputtopology` attribute.

## Shader Analysis

The test generates four stages, but one representative tessellation evaluation shader captures the behavior-specific source change. The fixed vertex, tessellation-control, and fragment stages are summarized in `Additional Info`; the full representative walkthrough below was reconstructed from the exact GLSL branch of `WindingTest::initPrograms()` and compiled, validated, and disassembled with the shader-analyzer/shader-disassembler CCVDO workflow.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.winding.default_domain.glsl_triangles_ccw
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `default_domain` | The pipeline omits an explicit domain-origin structure, so the spec default is upper-left. |
| `glsl_triangles_ccw` | The GLSL evaluation shader uses triangle tessellation and counter-clockwise domain-space order. |
| no `yflip` | The viewport has positive height, so the verifier uses the non-inverted image orientation. |

#### Purpose

This shader maps generated triangle-domain coordinates into clip space while requesting `VertexOrderCcw`. The rasterizer then tests that order against each static `frontFace` pipeline.

#### Structural Design

| Stage | Generated behavior | Relevance to winding |
|-------|--------------------|----------------------|
| Tessellation control | Emits one control point and sets both inner levels and all four outer levels to `5.0`. | Produces a non-degenerate tessellated domain. |
| Tessellation evaluation | Declares `layout(triangles, ccw) in` and maps `gl_TessCoord.xy` to clip space. | Supplies the tested order and the positions whose orientation reaches rasterization. |
| Rasterizer | Uses `VK_CULL_MODE_BACK_BIT`; the host tests both `VK_FRONT_FACE_COUNTER_CLOCKWISE` and `VK_FRONT_FACE_CLOCKWISE`. | Keeps only the pipeline-selected facing. |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require

/// The selected tessellation primitive and VertexOrderCcw execution mode come from the case parameters.
layout(triangles, ccw) in;

void main (void)
{
    /// Map the generated (u,v) domain coordinates into the clip-space viewport.
    gl_Position = vec4(gl_TessCoord.xy*2.0 - 1.0, 0.0, 1.0);
}
```

#### Additional Info

- The tessellation control shader writes `5.0` to `gl_TessLevelInner[0]`, `gl_TessLevelInner[1]`, and all four `gl_TessLevelOuter` entries. It does not provide vertex inputs.
- The fragment shader writes opaque white to location 0. The render pass clears the same attachment to red, so the image separates rasterized coverage from culled coverage.
- The GLSL source uses the ESSL 3.10 branch emitted by the CTS. The disassembler target is SPIR-V 1.0, the baseline target used when no explicit shader build target overrides it.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Primitive type | Changes the evaluation layout between `triangles` and `quads`; the HLSL branch also changes `SV_DOMAINLOCATION` from `float3` to `float2`. | [`WindingTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L265-L277) |
| Shader language | GLSL uses the evaluation-shader layout qualifier; HLSL uses hull-shader `domain` and `outputtopology` attributes. | [`WindingTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L227-L365) |
| Winding | Changes `ccw` to `cw` in GLSL and selects the corresponding HLSL output topology. | [`WindingTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L265-L277), [`getOutputTopologyName()`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L285-L300) |
| Domain origin | Does not change the shader text. It changes pipeline tessellation state and the spec interpretation of the generated order. | [`WindingTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L447-L471), [`tessellation.adoc#tessellation-vertex-winding-order`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-vertex-winding-order) |
| `yflip` | Does not change the shader text. It changes the viewport's Y transform and the expected image orientation. | [`WindingTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L528-L535), [`verifyResultImage()`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L83-L193) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `tese`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 30
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %_ %gl_TessCoord
               OpExecutionMode %main Triangles
               OpExecutionMode %main SpacingEqual
               OpExecutionMode %main VertexOrderCcw
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_EXT_tessellation_shader"
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %gl_TessCoord "gl_TessCoord"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %gl_TessCoord BuiltIn TessCoord
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
    %v2float = OpTypeVector %float 2
    %float_2 = OpConstant %float 2
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %17 = OpLoad %v3float %gl_TessCoord
         %18 = OpVectorShuffle %v2float %17 %17 0 1
         %20 = OpVectorTimesScalar %v2float %18 %float_2
         %22 = OpCompositeConstruct %v2float %float_1 %float_1
         %23 = OpFSub %v2float %20 %22
         %25 = OpCompositeExtract %float %23 0
         %26 = OpCompositeExtract %float %23 1
         %27 = OpCompositeConstruct %v4float %25 %26 %float_0 %float_1
         %29 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %29 %27
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [host] `WindingTestInstance` requires `FEATURE_TESSELLATION_SHADER`. A Y-flipped case also requires `VK_KHR_maintenance1`; an explicit domain origin requires `VK_KHR_maintenance2`. Unsupported functionality raises `NotSupportedError` before rendering.
- [host] The instance creates a 64x64 `VK_FORMAT_R8G8B8A8_UNORM` image with color-attachment and transfer-source usage, an image view, render pass, framebuffer, and host-visible transfer-destination buffer.
- [host] It builds two graphics pipelines. Both use back-face culling and the generated four-stage program. One pipeline uses `VK_FRONT_FACE_COUNTER_CLOCKWISE`, the other `VK_FRONT_FACE_CLOCKWISE`; both receive the selected tessellation domain origin.
- [host] For each pipeline, it transitions the attachment to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`, begins a render pass with red clear color, sets a 64x64 viewport and scissor, issues `vkCmdDraw(..., 1, 1, 0, 0)`, copies the image to the buffer, submits the command buffer, and waits for completion.
- [device] The tessellation stages turn the one abstract input vertex into the selected domain. The evaluation shader maps domain coordinates to clip space, the rasterizer applies `frontFace` and back-face culling, and the fragment shader writes white to surviving coverage.
- [host] After invalidating the readback allocation, `verifyResultImage()` counts exact red and white pixels. Other colors fail. A visible triangle must cover about half the image, within `5 * max(width, height)` pixels, and its top and bottom filled spans must match the Y orientation. A visible quad must cover every pixel. A culled primitive must leave zero white pixels.
- [host] The case passes only when both front-face pipeline runs satisfy the check.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ccw` | Incorrect `VertexOrderCcw` or HLSL counter-clockwise topology lowering; wrong domain-origin interpretation; incorrect rasterizer `frontFace`/back-face culling behavior; or viewport-Y/readback orientation handling that makes a visible triangle fail its shape check. |
| `cw` | Incorrect `VertexOrderCw` or HLSL clockwise topology lowering; wrong domain-origin interpretation; incorrect rasterizer `frontFace`/back-face culling behavior; or viewport-Y/readback orientation handling that makes a visible triangle fail its shape check. |

### Cause Analysis

#### Shader winding or tessellation-domain interpretation

**Possible failure symptoms:** The run may cull both images, show white coverage with the wrong pipeline, or report an incorrectly oriented triangle. A quad may fail by showing red pixels where the matching orientation should fill the viewport.

**Possible implementation causes:** The tessellation shader's `VertexOrderCw`/`VertexOrderCcw` execution mode, the HLSL output-topology lowering, or the domain-origin state may disagree with the Vulkan rules for generated triangle orientation. The relevant spec semantics are the tessellator winding-order rules and the default/explicit domain-origin state.

#### Rasterizer front-face and culling state

**Possible failure symptoms:** The selected front-face pipeline may discard the expected primitive, while the opposite pipeline may keep it. The image check then reports missing white coverage or unexpected white pixels.

**Possible implementation causes:** The implementation may classify the framebuffer-space area incorrectly, interpret `VK_FRONT_FACE_COUNTER_CLOCKWISE` or `VK_FRONT_FACE_CLOCKWISE` incorrectly, or apply `VK_CULL_MODE_BACK_BIT` to the wrong facing. The test creates both pipelines to separate shader winding from the static rasterizer state.

#### Viewport transform or image validation

**Possible failure symptoms:** A triangle can have the expected coverage area but fail the top/bottom span check, especially only in `yflip` cases. Any pixel other than exact red or white also fails.

**Possible implementation causes:** The viewport's negative height may be applied incorrectly, or the host-side expected orientation may not match the framebuffer coordinate transform. A color-attachment transition, copy, invalidation, or readback problem can also produce colors outside the two values the verifier accepts. The source does not establish a more specific implementation location without further investigation.

## Case Pruning

### Requirement-based pruning

- The test requires `FEATURE_TESSELLATION_SHADER`.
- The `yflip` cases require `VK_KHR_maintenance1`; the test reports `NotSupportedError` when the device lacks that functionality.
- `lower_left_domain` and `upper_left_domain` require `VK_KHR_maintenance2`; `default_domain` remains available through the default upper-left origin.
- The test registers only `Triangles` and `Quads`. It omits isolines because the tested winding/culling relationship concerns generated triangles.

### Design-based pruning

- The case matrix fixes the tessellation levels at `5.0` so the image contains a stable, non-degenerate primitive while the test varies winding and its conditioning dimensions.
- The two `frontFace` states run inside every test instance instead of becoming separate registered dimensions. This keeps the registered matrix focused on the shader/domain behavior while still checking both culling decisions.
- GLSL and HLSL express the same property through different source constructs. The test keeps both language variants to check equivalent shader-language paths without adding another behavior axis.

## Key Takeaways

- `ccw` and `cw` describe tessellator output order in domain space; the domain origin controls how that order maps to the orientation rule.
- The test pairs each generated shader with both static `frontFace` values and uses back-face culling to make the expected relationship visible.
- Red/white image checks distinguish culled from surviving primitives, while the triangle coverage and edge-span checks catch an orientation error that a simple non-empty-pixel check would miss.
- A failure points to the specific winding value's shader/domain/culling relationship, with viewport and readback handling also relevant for Y-flipped orientation failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `verifyResultImage()` | [`vktTessellationWindingTests.cpp#L83-L193`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L83-L193) | Defines the red/white pixel contract, triangle tolerance, quad coverage, and Y-flip orientation check. |
| `WindingTest::initPrograms()` | [`vktTessellationWindingTests.cpp#L227-L365`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L227-L365) | Generates the GLSL and HLSL program stages and varies the winding representation. |
| `WindingTestInstance::iterate()` | [`vktTessellationWindingTests.cpp#L406-L572`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L406-L572) | Creates the pipelines, records the draw/copy flow, and invokes image verification. |
| `populateWindingGroup()` | [`vktTessellationWindingTests.cpp#L582-L604`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L582-L604) | Produces the primitive, language, winding, and Y-flip matrix. |
| `createWindingTests()` | [`vktTessellationWindingTests.cpp#L610-L624`](../../../modules/vulkan/tessellation/vktTessellationWindingTests.cpp#L610-L624) | Registers the three domain-origin intermediate nodes. |
| Tessellator vertex winding order | [`tessellation.adoc#tessellation-vertex-winding-order`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-vertex-winding-order) | Specifies `VertexOrderCw`/`VertexOrderCcw` and the origin-dependent area sign. |
| Tessellation domain origin | [`tessellation.adoc#tessellation-pipeline-state`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-pipeline-state) | Specifies explicit origins and the upper-left default. |
| Polygon facing and culling | [`primsrast.adoc#primsrast-polygons-basic`](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-polygons-basic) | Specifies framebuffer-space facing, `frontFace`, and `cullMode`. |
| Mustpass matrix | [`tessellation.txt#L1056-L1103`](../../../mustpass/main/vk-default/tessellation.txt#L1056-L1103) | Confirms the registered winding case coverage. |
