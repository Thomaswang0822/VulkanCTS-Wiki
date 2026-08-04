## Overview

**Core question:** Can graphics pipelines produce the required depth-side effects when they omit the Fragment Shader or run a Fragment Shader with no outputs?

- [`vktPipelineEmptyFSTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L45-L830) implements the `empty_fs` test family in the `pipeline` test category.
- Six basic test case leaves combine a final pre-rasterization-stage choice with either no Fragment Shader or an empty `frag` program. Two selective-update leaves omit the Fragment Shader and make depth/sample effects observable through depth readback, an occlusion query, or a compute readback path.
- The page separates the registered labels from the source behavior. In particular, the `geom_*` labels are registered with `VK_SHADER_STAGE_VERTEX_BIT`, so the present source executes the vertex path for those leaves rather than creating a geometry module.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- [Fragment operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops) include the sample-mask and depth-test work that can affect a depth/stencil attachment. A pipeline without a Fragment Shader has no fragment-shader invocation, but the test can still observe the resulting depth data.
- A [sample mask](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-samplemask) selects covered samples before later per-fragment processing. For multisampling, a bit in the mask corresponds to one sample.
- An [occlusion query](../../../../vulkan-docs/src/chapters/queries.adoc#queries-occlusion) records samples that pass the per-fragment tests. The precise-query feature controls whether CTS requires the exact count or only a nonzero result.

## Registration Hierarchy

```text
pipeline.monolithic.empty_fs
├── vert_no_fs
├── vert_empty_fs
├── tess_no_fs
├── tess_empty_fs
├── geom_no_fs
├── geom_empty_fs
├── primitive_discard
└── masked_samples
```

`createEmptyFSTests()` registers these eight test case leaves for each pipeline-construction type. The Vulkan default mustpass split contains eight leaves in each of `monolithic/monolithic.txt`, `pipeline-library.txt`, `fast-linked-library.txt`, `shader-object-linked-spirv.txt`, `shader-object-linked-binary.txt`, `shader-object-unlinked-binary.txt`, and `shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt`: 56 entries total. Vulkan SC has the same eight leaves under its monolithic root.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Pipeline construction type | `monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_linked_spirv`, `shader_object_linked_binary`, `shader_object_unlinked_binary`, `shader_object_unlinked_spirv` | Repeats the same test-family behavior through each Vulkan default construction route. | [`createTests()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L224-L240) and mustpass files listed above |
| Basic leaf label | `vert`, `tess`, `geom` | Chooses the registered basic-leaf prefix. `tess` passes a tessellation-evaluation stage flag; `vert` and the current `geom` registration pass the vertex-stage flag. | [`vertexStages`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L804-L821) |
| Fragment Shader choice | `_no_fs`, `_empty_fs` | `_no_fs` supplies an empty shader wrapper. `_empty_fs` loads `frag`, whose `main` has inputs but no declared outputs. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L675-L795) |
| Selective-update mechanism | `primitive_discard`, `masked_samples` | Chooses cull-distance-based primitive selection with depth copyback, or four-sample depth selection with compute and SSBO checking. | [`EmptyFSSelectiveDSUpdateInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L266-L577) |

The test case leaf is the primary behavioral axis because each leaf chooses the mechanism and oracle, not only a pipeline setting.

## Behavior Parameters

### vert_no_fs: vertex path with no Fragment Shader

This leaf draws four small depth-valued triangles with a vertex program and does not create a Fragment Shader module. CTS copies the 2 x 2 depth attachment and compares every depth value with its reference.

### vert_empty_fs: vertex path with an empty Fragment Shader

This leaf uses the same depth oracle as `vert_no_fs`, but it creates `frag`. The generated `main` accepts the two interpolated inputs and has no outputs, so the distinction is the presence of a no-output Fragment Shader module.

### tess_no_fs: tessellation path with no Fragment Shader

This leaf adds pass-through tessellation-control and tessellation-evaluation programs, selects patch-list topology, and omits the Fragment Shader. The support check requires tessellation support before execution.

### tess_empty_fs: tessellation path with an empty Fragment Shader

This leaf uses the tessellation programs and the no-output `frag` program. Its depth copyback remains the oracle, so it tests the pipeline combination rather than color output.

### geom_no_fs: registered `geom` label with no Fragment Shader

The registration loop names this leaf `geom_no_fs`, but it supplies `VK_SHADER_STAGE_VERTEX_BIT` for the corresponding parameters. Since `lastIsGeometry()` recognizes only `VK_SHADER_STAGE_GEOMETRY_BIT`, the present source does not create `geom`; this leaf follows the vertex basic path without a Fragment Shader.

### geom_empty_fs: registered `geom` label with an empty Fragment Shader

This leaf has the same registration mismatch as `geom_no_fs`, with `emptyFS` set true. The present source therefore loads the empty `frag` module while retaining the vertex basic path.

### primitive_discard: cull-distance-selected depth updates

This leaf has no Fragment Shader. Its vertex program writes `gl_CullDistance`, and the indexed draw selects two surviving triangles. CTS checks the four depth-buffer quadrant centers and the occlusion-query result.

### masked_samples: sample-mask-selected depth updates

This leaf has no Fragment Shader and uses four depth samples with sample mask `0x5`, selecting samples 0 and 2. A compute shader reads all four samples at each pixel, writes the difference between the selected and unselected pairs into an SSBO, and CTS also checks the occlusion query.

## Shader Analysis

Two generated programs directly support distinct observability paths. The empty `frag` program distinguishes `_empty_fs` from `_no_fs`, while the `masked_samples` compute program checks the four multisample depth values. The walkthrough below uses the latter because it exposes the resource bindings, selected samples, and the SSBO oracle. The source collection uses no explicit `ShaderBuildOptions`, so this reconstruction uses the CTS baseline `spirv1.0` target.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.empty_fs.masked_samples
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `masked_samples` | Selects the four-sample depth attachment and the compute readback program. |
| `0x5` | Enables depth samples 0 and 2, which makes their sum differ from samples 1 and 3. |
| `comp` | Reads the multisampled depth image and writes one result per 8 x 8 invocation grid. |

#### Purpose

The compute program verifies the sample-mask result after graphics rendering without a Fragment Shader. It writes `2.0` when samples 0 and 2 contain depth `1.0` and samples 1 and 3 retain the cleared depth `0.0`.

#### Structural Design

| Phase | Operation | Observable result |
|---|---|---|
| Address | Convert `gl_GlobalInvocationID.xy` to pixel coordinate `uv`. | One invocation addresses one 8 x 8 depth pixel. |
| Read selected pair | Fetch samples 0 and 2 from `inputImage`. | Their red components sum to `2.0`. |
| Read unselected pair | Fetch samples 1 and 3. | Their red components sum to `0.0`. |
| Record | Store the difference in `v[gl_LocalInvocationIndex]`. | The host later requires each SSBO float to be within `[1.99, 2.01]`. |

#### Shader Code

```glsl
#version 460
#extension GL_EXT_samplerless_texture_functions : enable
layout(local_size_x = 8, local_size_y = 8) in;
/// Binding 0 is the four-sample depth image produced by the graphics draw.
layout(set = 0, binding = 0) uniform texture2DMS inputImage;
/// Binding 1 is a host-visible SSBO with one float per local invocation.
layout(set = 0, binding = 1) buffer Data { float v[]; };
void main()
{
  ivec2 uv = ivec2(gl_GlobalInvocationID.xy);
  float samplesOne  = texelFetch(inputImage, uv, 0).r +
                      texelFetch(inputImage, uv, 2).r;
  float samplesZero = texelFetch(inputImage, uv, 1).r +
                      texelFetch(inputImage, uv, 3).r;
  v[gl_LocalInvocationIndex] = samplesOne - samplesZero; // we expect 2 - 0 = 2
}
```

#### Additional Info

- The graphics pipeline has no Fragment Shader for this leaf. The compute program is a separate pipeline used only after a depth-write to shader-read barrier.
- `gl_LocalInvocationIndex` ranges over the 8 x 8 local workgroup, matching the 64-float SSBO allocation.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| `primitive_discard` versus `masked_samples` | `primitive_discard` generates only a vertex program and copies depth to the host; `masked_samples` also generates this compute program. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L626-L672) |
| Fragment Shader choice | The basic leaves optionally generate `frag`; this compute program is independent of that no-output program. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L675-L795) |

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
; Bound: 64
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID %gl_LocalInvocationIndex
               OpExecutionMode %main LocalSize 8 8 1
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_samplerless_texture_functions"
               OpName %main "main"
               OpName %uv "uv"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %samplesOne "samplesOne"
               OpName %inputImage "inputImage"
               OpName %samplesZero "samplesZero"
               OpName %Data "Data"
               OpMemberName %Data 0 "v"
               OpName %_ ""
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %inputImage Binding 0
               OpDecorate %inputImage DescriptorSet 0
               OpDecorate %_runtimearr_float ArrayStride 4
               OpDecorate %Data BufferBlock
               OpMemberDecorate %Data 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
         %21 = OpTypeImage %float 2D 0 0 1 1 Unknown
%_ptr_UniformConstant_21 = OpTypePointer UniformConstant %21
 %inputImage = OpVariable %_ptr_UniformConstant_21 UniformConstant
      %int_0 = OpConstant %int 0
    %v4float = OpTypeVector %float 4
     %uint_0 = OpConstant %uint 0
      %int_2 = OpConstant %int 2
      %int_1 = OpConstant %int 1
      %int_3 = OpConstant %int 3
%_runtimearr_float = OpTypeRuntimeArray %float
       %Data = OpTypeStruct %_runtimearr_float
%_ptr_Uniform_Data = OpTypePointer Uniform %Data
          %_ = OpVariable %_ptr_Uniform_Data Uniform
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
%_ptr_Uniform_float = OpTypePointer Uniform %float
     %uint_8 = OpConstant %uint 8
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_8 %uint_8 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %uv = OpVariable %_ptr_Function_v2int Function
 %samplesOne = OpVariable %_ptr_Function_float Function
%samplesZero = OpVariable %_ptr_Function_float Function
         %15 = OpLoad %v3uint %gl_GlobalInvocationID
         %16 = OpVectorShuffle %v2uint %15 %15 0 1
         %17 = OpBitcast %v2int %16
               OpStore %uv %17
         %24 = OpLoad %21 %inputImage
         %25 = OpLoad %v2int %uv
         %28 = OpImageFetch %v4float %24 %25 Sample %int_0
         %30 = OpCompositeExtract %float %28 0
         %31 = OpLoad %21 %inputImage
         %32 = OpLoad %v2int %uv
         %34 = OpImageFetch %v4float %31 %32 Sample %int_2
         %35 = OpCompositeExtract %float %34 0
         %36 = OpFAdd %float %30 %35
               OpStore %samplesOne %36
         %38 = OpLoad %21 %inputImage
         %39 = OpLoad %v2int %uv
         %41 = OpImageFetch %v4float %38 %39 Sample %int_1
         %42 = OpCompositeExtract %float %41 0
         %43 = OpLoad %21 %inputImage
         %44 = OpLoad %v2int %uv
         %46 = OpImageFetch %v4float %43 %44 Sample %int_3
         %47 = OpCompositeExtract %float %46 0
         %48 = OpFAdd %float %42 %47
               OpStore %samplesZero %48
         %55 = OpLoad %uint %gl_LocalInvocationIndex
         %56 = OpLoad %float %samplesOne
         %57 = OpLoad %float %samplesZero
         %58 = OpFSub %float %56 %57
         %60 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %55
               OpStore %60 %58
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Basic leaves allocate a 2 x 2 color image and a `VK_FORMAT_D16_UNORM` depth image, clear depth to `0.0`, then draw one triangle per pixel with depths `0`, `1/4`, `2/4`, and `3/4`. They copy the depth image to its host-visible buffer after the render pass.
- The basic pipeline always enables depth testing and depth writes with `VK_COMPARE_OP_ALWAYS`. The resulting depth image, rather than a color attachment, is the pass/fail oracle.
- `primitive_discard` uses an 8 x 8 depth/stencil image with one sample. The attachment is cleared to depth `0.0`; after the indexed draw and occlusion query, CTS copies depth to host-visible memory and requires the two surviving quadrant centers to have depth near `1.0` while the two culled quadrants remain near `0.0`.
- `masked_samples` uses a four-sample depth/stencil image and a sample mask of `0x5`. CTS inserts a depth-write to compute-shader-read barrier, dispatches the compute program, then inserts a compute-write to host-read barrier before invalidating and scanning the SSBO.
- A precise occlusion query must return `32` for `primitive_discard` or `128` for `masked_samples`; without precise-query support, CTS requires a nonzero count. The return value from `vkGetQueryPoolResults` is not checked separately, so an API error is reported only indirectly through the initialized or returned query count and the generic test failure. The basic leaves use `dsThresholdCompare` with threshold `0.000025`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `vert_no_fs`, `vert_empty_fs` | Pipeline construction without a color-producing Fragment Shader, vertex-path depth writes, depth copyback, or depth comparison is incorrect. |
| `tess_no_fs`, `tess_empty_fs` | Tessellation-stage setup or execution, the absent/empty Fragment Shader path, depth writes, or readback is incorrect. |
| `geom_no_fs`, `geom_empty_fs` | The registered `geom` parameters currently select the vertex path; failure can involve that registration/selection, the absent/empty Fragment Shader path, depth writes, or readback. |
| `primitive_discard` | `gl_CullDistance` primitive selection, surviving depth coverage, occlusion-query accounting, or depth readback is incorrect. |
| `masked_samples` | The sample mask, multisampled depth writes, compute sample reads, SSBO result, or occlusion-query accounting is incorrect. |

### Cause Analysis

#### Basic path construction and depth observation

**Possible failure symptoms:** One or more basic leaves return a depth image that differs from the 2 x 2 reference after a missing or no-output Fragment Shader configuration.

**Possible implementation causes:** Pipeline creation may handle the selected pre-rasterization modules or an absent/no-output Fragment Shader incorrectly. The result can also arise in depth attachment writes, depth-image copyback, or host comparison. The test does not inspect color data, so it cannot localize a failure to color output handling.

#### Tessellation path construction

**Possible failure symptoms:** `tess_no_fs` or `tess_empty_fs` fails its depth comparison while the vertex-labeled basic leaves pass.

**Possible implementation causes:** The source adds tessellation-control and tessellation-evaluation modules, patch-list topology, and feature gates only for this path. A defect can occur in that stage configuration, in the same depth-write/readback path used by basic leaves, or in handling the selected Fragment Shader state. Further source-level investigation is needed to isolate a specific implementation component.

#### Registered `geom` label selection

**Possible failure symptoms:** A `geom_*` leaf fails even though the vertex-labeled basic path passes.

**Possible implementation causes:** The registration array assigns `VK_SHADER_STAGE_VERTEX_BIT` to `geom`, while `lastIsGeometry()` requires `VK_SHADER_STAGE_GEOMETRY_BIT` before it creates `geom`. The observed behavior therefore cannot establish geometry-stage execution. Investigate the registration parameter and the shared vertex/empty-Fragment-Shader path before attributing the failure to geometry processing.

#### Primitive discard and query observation

**Possible failure symptoms:** The expected pair of depth-buffer quadrants remains unchanged or the precise query does not equal `32`.

**Possible implementation causes:** The vertex program's `gl_CullDistance` values, primitive selection, depth updates, depth transfer, or occlusion-query accounting can produce this result. The final image and count cover the whole draw, so they do not distinguish those stages by themselves. Because the test ignores the `vkGetQueryPoolResults` return value, a query-retrieval error can be masked as a generic count mismatch rather than reported directly.

#### Sample-mask compute observation

**Possible failure symptoms:** An SSBO float falls outside `[1.99, 2.01]`, or a precise query does not equal `128`.

**Possible implementation causes:** The graphics sample mask may select the wrong samples, the multisampled depth write may be incorrect, the depth-to-compute barrier may not make the data readable, or the compute fetch/SSBO path may be wrong. The query can also fail independently of the SSBO comparison, and its retrieval status is not checked, so source-level investigation should compare both observations and the API result.

## Case Pruning

### Requirement-based pruning

- `tess_*` leaves call `requireDeviceCoreFeature` for tessellation shader support and tessellation/geometry point-size support.
- The `lastIsGeometry()` support gate requires `geometryShader`, but the current registration does not pass the geometry stage flag for `geom_*` leaves.
- `primitive_discard` requires `shaderCullDistance`.
- Every leaf calls `checkPipelineConstructionRequirements` for its selected construction type. Precise occlusion-query support changes the acceptance rule instead of skipping a leaf.

### Design-based pruning

- The basic leaves keep the attachment format, depth state, 2 x 2 reference shape, and vertex data fixed so that stage selection and Fragment Shader presence remain the variables under test.
- Selective-update leaves always omit the Fragment Shader. They use dedicated observability mechanisms rather than multiplying every basic stage/Fragment Shader combination by cull-distance and sample-mask cases.

## Key Takeaways

- The `empty_fs` family observes depth-side effects rather than color output, so a passing leaf proves the tested depth path but does not validate color results.
- `_no_fs` and `_empty_fs` differ in module construction: the former supplies no Fragment Shader module, while the latter supplies `frag` with no outputs.
- `primitive_discard` and `masked_samples` add independent depth/query or depth/compute/SSBO oracles to test selective fragment effects without a Fragment Shader.
- The source currently registers `geom_*` with the vertex-stage flag; documentation must preserve that distinction instead of calling those leaves executed geometry-stage tests.

## Source Reference Appendix

| Topic | Evidence | Why it matters |
|---|---|---|
| Basic pipeline, draw, and depth comparison | [`EmptyFSInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L101-L248) | Defines the 2 x 2 depth oracle and optional `frag` module use. |
| Selective depth/sample execution and result checks | [`EmptyFSSelectiveDSUpdateInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L266-L577) | Defines the render pass, sample mask, queries, barriers, copyback, and pass conditions. |
| Feature and construction checks | [`EmptyFSCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L606-L622) | States the feature gates and construction-type requirement. |
| Generated shader programs | [`EmptyFSCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L624-L795) | Generates the empty `frag`, `gl_CullDistance` vertex program, and compute readback program. |
| Registration and `geom` parameter | [`createEmptyFSTests()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L800-L829) | Registers the exact eight leaves and shows the `geom` vertex-stage assignment. |
| Pipeline construction roots | [`createTests()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L224-L240) | Creates the construction-type roots that repeat `empty_fs`. |
| Vulkan fragment operations | [fragment operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops) | Defines the depth and sample-mask operations relevant to the observed depth effects. |
| Vulkan occlusion queries | [occlusion queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries-occlusion) | Defines the query result used by the selective-update leaves. |
| Vulkan default monolithic mustpass | [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt#L33409-L33416) | Shows the eight monolithic `empty_fs` leaves. |
| Vulkan SC monolithic mustpass | [`monolithic.txt`](../../../mustpass/main/vksc-default/pipeline/monolithic.txt#L26517-L26524) | Shows the eight Vulkan SC monolithic leaves. |
