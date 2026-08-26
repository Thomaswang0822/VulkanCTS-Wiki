## Overview

**Core question:** Does `VK_EXT_custom_resolve` let a shader decide how a multisample attachment is resolved, and does that shader-driven resolve work across legacy render passes, render pass 2, dynamic rendering, pipeline-construction variants, and fragment density map interactions?

- This page covers [vktRenderPassCustomResolveTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp), the implementation file for the `custom_resolve` test family.
- The file registers the `custom_resolve` group directly under each rendering root (`renderpass1`, `renderpass2`, `dynamic_rendering`), then fans out into pipeline-construction intermediate nodes (`monolithic`, `fast_lib`, and, for dynamic rendering only, `shader_objects`) [createRenderPassCustomResolveTests](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6080-L6104).
- Unlike the core sub-variants in `vktRenderPassTests.cpp`, `custom_resolve` does not sit under the `suballocation`/`dedicated_allocation`/`no_draws` intermediate nodes. It attaches directly to the rendering root, and its own construction-type groups are the intermediate level [vktRenderPassTests.cpp attachment](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8502-L8546).
- The core idea: standard Vulkan multisample resolve averages samples or picks one automatically. `VK_EXT_custom_resolve` hands that decision to a shader. The test uploads known per-sample data into a multisample image, runs a resolve pass whose shader reads the input attachment samples and writes a chosen result (average, a fixed value, or one selected sample), and the host checks the resolved single-sample image against the expected output.
- Four distinct test mechanisms live in this file: the main `CustomResolveInstance` family, `FragmentRegionInstance`, `FDMInstance`, and the dynamic-rendering-only `single_sample_clear` case.

## Background Knowledge

- **Custom resolve.** In standard Vulkan, multisample resolve is a fixed-function step: the implementation averages samples or selects sample zero when a render pass or dynamic rendering instance ends. `VK_EXT_custom_resolve` replaces that with `VK_RESOLVE_MODE_CUSTOM_BIT_EXT`, which lets the application shader perform the resolve by reading the multisample input attachment and writing to the resolve target. The spec calls `vkCmdBeginCustomResolveEXT` between `vkCmdBeginRendering` and the draw that does the resolve work [renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L1079-L1108).
- **Resolve attachment becomes undefined.** When `VK_RENDERING_CUSTOM_RESOLVE_BIT_EXT` is set and an attachment uses `VK_RESOLVE_MODE_CUSTOM_BIT_EXT`, the contents of the resolve attachment become undefined at the time `vkCmdBeginCustomResolveEXT` is called. The spec also mandates an implicit store for these attachments [renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#L1080-L1090). The `single_sample_clear` test probes whether an implementation over-clears that attachment outside the resolve region.
- **Upload and resolve passes.** The test separates writing known per-sample data ("upload" passes) from reading and combining it ("resolve" passes). An upload pass draws a scaled quad into a covered area of the multisample attachment, writing one color, depth, or stencil value per sample from a storage buffer. A resolve pass reads those samples back through input attachments and writes the resolved result. This split lets the test verify the resolve logic in isolation from how the data got there.
- **Three resolve strategies.** Each resolve can average all samples, write a fixed value, or copy one selected sample. Average mirrors the default hardware resolve, so the fixed-value and selected-sample strategies are what actually distinguish a custom resolve from an automatic one.

## Registration Hierarchy

The `custom_resolve` group is attached directly to each rendering root by `createRenderPassesTests()` and dispatched through `createRenderPassTestsInternal()` [attachment points](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8502-L8546). It is non-SC only and skips the complete-secondary-command-buffer dynamic-rendering variant. The representative tree below shows the `renderpass1` children; `renderpass2` and `dynamic_rendering` share the same construction-type intermediate nodes, with `dynamic_rendering` adding `shader_objects`.

```text
renderpasses.renderpass1.custom_resolve
├── monolithic
└── fast_lib
```

Construction-type intermediate nodes under each rendering root:

- `monolithic` and `fast_lib` appear under `renderpass1`, `renderpass2`, and `dynamic_rendering`.
- `shader_objects` appears only under `dynamic_rendering` [construction-type loop](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6108-L6112).
- `single_sample_clear` appears only under `dynamic_rendering`, once per construction-type intermediate node [registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7094-L7098).
- `fragment_region` cases appear under `renderpass1` and `dynamic_rendering` (not `renderpass2`) [registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7021-L7035).
- `fdm` cases appear under `renderpass2` and `dynamic_rendering` (not `renderpass1`) [registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7037-L7092).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline construction type | `monolithic`, `fast_lib`, `shader_objects` | Selects monolithic pipelines, fast-linked graphics pipeline libraries, or unlinked SPIR-V shader objects. `shader_objects` is dynamic-rendering only. | [constructionTypeCases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6092-L6096) |
| Depth/stencil formats | `d16`, `d24`, `d32`, `s8`, `d16s8`, `d24s8`, `d32s8` | Drives the depth-only, stencil-only, and combined depth/stencil resolve cases. Each format is checked for sample-count support before registration. | [dsFormatNames](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6098-L6106) |
| Resolve type | `AVERAGE`, `FIXED_VALUE`, `SELECTED_SAMPLE` | The three shader-side resolve strategies. Average mirrors hardware resolve; fixed-value and selected-sample prove the shader controls the output. | [ResolveType enum](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L124-L129) |
| Color formats | `R8G8B8A8_UNORM`, `R16G16B16A16_UNORM` | Used alone and in format-change cases where the upload format differs from the resolve format. | [format_change cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6643-L6664) |
| Attachment count | 1 to 4 | Ranges from single-attachment simple cases to complex multi-attachment cases mixing color, depth/stencil, and single-sample attachments. | [complex cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6665-L6714) |
| Covered area | full, top half, bottom half, partial quadrant | Each upload and resolve pass specifies a `CoveredArea` (scale and offset) that controls which pixels receive data. | [CoveredArea struct](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L70-L82) |

## Behavior Parameters

The primary behavioral axis is the **test mechanism**: the file implements four distinct mechanisms that each test a different facet of `VK_EXT_custom_resolve`. Within each mechanism, the construction-type intermediate node (`monolithic`, `fast_lib`, `shader_objects`) is a secondary axis that changes pipeline construction, not the tested resolve property.

### main resolve cases: shader-driven multisample resolve

The bulk of the registered cases use `CustomResolveInstance`. Each case configures a set of multisample attachments, one or more upload passes that write known per-sample data, and one or more resolve passes that read those samples and write a resolved result using one of the three strategies [TestParams struct](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L275-L291).

The case matrix grows from simple to complex:

- `simple_average`, `simple_fixed`, `simple_sample_2`: one `R8G8B8A8_UNORM` 4x attachment, one full-area upload, one resolve using each strategy [simple cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6120-L6151).
- Depth-only, stencil-only, and combined depth/stencil cases across all depth/stencil formats, including variants with disabled depth writes, disabled stencil export, and separate upload passes for each aspect [depth/stencil cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6175-L6431).
- Format-change cases where the upload format differs from the resolve format, for depth, stencil, and combined depth/stencil [format-change cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6432-L6615).
- Attachment-index-change cases that prevent upload and resolve pass merging in dynamic rendering, including location remapping via `vkCmdSetRenderingAttachmentLocations` [att_index_change](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6616-L6642).
- Color format-change cases and complex multi-attachment, multi-upload, multi-resolve cases that mix color, single-sample, and depth/stencil attachments with format and index changes [complex cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6665-L6841).
- Unused-attachment cases (dynamic rendering only) that vary which attachments are marked unused in the pipeline and rendering info, testing `VK_EXT_dynamic_rendering_unused_attachments` interactions [unused cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6891-L7018).

### fragment_region: fragment density region interaction

`FragmentRegionInstance` checks that `VK_RENDERING_FRAGMENT_REGION_BIT_EXT` behaves correctly: a render pass using that flag can access samples not covered by its `SampleMask` [FragmentRegionParams](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3487-L3515). Each case uses two multisample color images and a single-sample result image that is horizontally expanded by the sample count. The `close` parameter controls whether writes to the critical region happen last (immediately followed by reads) or first (followed by writes and reads elsewhere), and the `large` parameter switches between 255x256 and 1023x1024 framebuffers [registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7021-L7035).

### fdm: fragment density map variants

`FDMInstance` combines custom resolve with `VK_EXT_fragment_density_map`, `VK_EXT_fragment_density_map2`, and optionally `VK_EXT_fragment_density_map_offset`. Each case fills a multisample image with per-sample data, resolves it using a custom resolve shader, and verifies the single-sample result accounts for the fragment density map's subsampled or non-subsampled rendering. Parameters include subsampled images, multilayer, multiview, custom-resolve info omission flags, framebuffer size, and density-map offset [FDMParams](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L4290-L4305), [registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7037-L7092).

### single_sample_clear: unnecessary clear detection (dynamic rendering only)

`single_sample_clear` verifies that custom resolve does not needlessly clear the single-sample resolve attachment outside the rendered region [SingleSampleClearIterate](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5812-L6070). The test creates a 4x MSAA image and a single-sample image, clears the single-sample image to color A, then begins a custom resolve render pass with clear color B. A scissor restricts drawing to one quadrant. The scissor region must match color B. If the bottom-right corner (outside the scissor) also matches color B, the test emits a `QualityWarning` because the implementation likely cleared the single-sample attachment unnecessarily, even though the spec says its contents become undefined and need not be cleared [spec undefined contents](../../../../vulkan-docs/src/chapters/renderpass.adoc#L1080-L1090).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.renderpasses.renderpass1.custom_resolve.monolithic.color_multi_upload_multi_resolve_complex
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `renderpass1.custom_resolve.monolithic` | The legacy render-pass path uses a monolithic graphics pipeline. The shader generator is shared with the dynamic-rendering and shader-object variants; those variants change host-side construction, not this generated GLSL resolve algorithm. |
| `color_multi_upload_multi_resolve_complex` | The case has two 4-sample color attachments, two upload passes, and two resolve passes. Attachment 0 is resolved first with `SELECTED_SAMPLE` sample 3 and its resolve location is 1, exposing both sample selection and output-location remapping. |
| `frag_resolve_0` | This is the first resolve fragment stage. It reads attachment 0 through a multisample input attachment and writes the selected sample to color output location 1. |

#### Purpose

This resolve shader demonstrates that `VK_EXT_custom_resolve` lets the fragment stage choose a particular multisample value instead of relying on fixed-function averaging. For the selected case, sample 3 from attachment 0 is copied to the resolve output, and the host later compares that result with the same sample from its generated per-sample reference data.

#### Structural Design

| Phase | Shader operation | Why it matters |
|-------|------------------|----------------|
| Interface | Declare an input attachment for multisample color data and a color output at location 1. | The input attachment index follows the legacy render-pass attachment index; the output location follows `AttachmentInfo::resolveLocation`, which is 1 for attachment 0 in this case. |
| Resolve | `subpassLoad(inColor0, 3)` reads one sample from the multisample input attachment. | The selected-sample strategy is shader-controlled and does not average the four samples. |
| Store | Assign the returned `vec4` to `outColor1`. | The resolved value is written to the single-sample attachment at the remapped color location. |

#### Shader Code

```glsl
#version 460

/// Binding 0 is a host-created std430 storage buffer for attachment 0. Its
/// extent.w member carries the runtime sample count; this representative
/// selected-sample branch does not need to load it because the sample index
/// is emitted as the compile-time literal 3.
layout (set=0, binding=0, std430) readonly buffer AttInfoBlk0 {
    ivec4 extent; // .xyz is the size and should be the same for all, .w is the sample count
} attInfo0;

/// Set 1 binding 0 is the multisample input attachment for legacy render-pass
/// attachment 0. The generator uses input_attachment_index 0 for this path.
layout (set=1, binding=0, input_attachment_index=0) uniform subpassInputMS inColor0;

/// Attachment 0's resolveLocation is 1 in the representative case, so the
/// selected sample is written to color location 1 of the resolve pipeline.
layout (location=1) out vec4 outColor1;

void main (void) {
    /// ResolveType::SELECTED_SAMPLE with sampleIndex 3 becomes a direct
    /// multisample input-attachment read; no loop or arithmetic is generated.
    outColor1 = subpassLoad(inColor0, 3);
}
```

#### Additional Info

- `frag_upload_0` and `frag_upload_1` are the producer stages for the two upload passes. They read per-sample `vec4` values from set 0 storage buffers, compute `p = y * extent.x + x` and `i = p * extent.w + gl_SampleID`, and write those values into the multisample attachments before the resolve stages run [upload shader generation](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L802-L857). They are not reproduced here because the selected-sample resolve stage is the shader logic central to this representative walkthrough.
- The host records the custom-resolve operation as the second subpass for the legacy render-pass path; dynamic rendering uses `vkCmdBeginCustomResolveEXT` before the same resolve draw [resolve recording](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3032-L3068).
- The generated source includes the `AttInfoBlk0` declaration even though this selected-sample branch does not read `extent.w`; average branches use that member as the loop bound and fixed-value branches likewise retain the common per-attachment declaration.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| `ResolveType` | `AVERAGE` emits a loop over `attInfo*.extent.w` samples and division by the sample count; `FIXED_VALUE` emits a constant; `SELECTED_SAMPLE` emits one `subpassLoad` with the selected literal index. | [resolve strategy generation](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L933-L956) |
| `resolveLocation` / attachment remapping | The output declaration uses the attachment's resolve location, while the legacy input attachment index remains the attachment index. Dynamic rendering can instead use the resolve-pass index when location remapping is enabled. | [input and output location generation](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L894-L917), [output declaration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L933-L935) |
| Resolve aspect | Color uses `subpassInputMS` and a color output; depth uses `gl_FragDepth`; stencil uses `usubpassInputMS` and, unless disabled, `gl_FragStencilRefARB` with `GL_ARB_shader_stencil_export`. | [aspect-specific declarations and stores](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L919-L1006) |
| Upload/resolve coverage | Push-constant `CoveredArea` changes the rectangle rasterized by the common vertex shader; it does not change the resolve fragment code shown here. | [common vertex shader](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L782-L800), [push-constant recording](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L2668-L2676) |
| Attachment formats and sample count | Host-generated attachment formats and sample counts change descriptor data and render-pass/pipeline state. The selected-sample shader still uses the literal selected index; support checks ensure the index is valid for the attachment's sample count. | [attachment and resolve parameters](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L275-L338), [support checks](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L615-L780) |

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
; Bound: 24
; Schema: 0
               OpCapability Shader
               OpCapability InputAttachment
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor1
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpName %main "main"
               OpName %outColor1 "outColor1"
               OpName %inColor0 "inColor0"
               OpName %AttInfoBlk0 "AttInfoBlk0"
               OpMemberName %AttInfoBlk0 0 "extent"
               OpName %attInfo0 "attInfo0"
               OpDecorate %outColor1 Location 1
               OpDecorate %inColor0 Binding 0
               OpDecorate %inColor0 DescriptorSet 1
               OpDecorate %inColor0 InputAttachmentIndex 0
               OpDecorate %AttInfoBlk0 BufferBlock
               OpMemberDecorate %AttInfoBlk0 0 NonWritable
               OpMemberDecorate %AttInfoBlk0 0 Offset 0
               OpDecorate %attInfo0 NonWritable
               OpDecorate %attInfo0 Binding 0
               OpDecorate %attInfo0 DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %outColor1 = OpVariable %_ptr_Output_v4float Output
         %10 = OpTypeImage %float SubpassData 0 0 1 2 Unknown
%_ptr_UniformConstant_10 = OpTypePointer UniformConstant %10
   %inColor0 = OpVariable %_ptr_UniformConstant_10 UniformConstant
        %int = OpTypeInt 32 1
      %int_3 = OpConstant %int 3
      %int_0 = OpConstant %int 0
      %v2int = OpTypeVector %int 2
         %18 = OpConstantComposite %v2int %int_0 %int_0
      %v4int = OpTypeVector %int 4
%AttInfoBlk0 = OpTypeStruct %v4int
%_ptr_Uniform_AttInfoBlk0 = OpTypePointer Uniform %AttInfoBlk0
   %attInfo0 = OpVariable %_ptr_Uniform_AttInfoBlk0 Uniform
       %main = OpFunction %void None %3
          %5 = OpLabel
         %13 = OpLoad %10 %inColor0
         %19 = OpImageRead %v4float %13 %18 Sample %int_3
               OpStore %outColor1 %19
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Main resolve cases

Each `CustomResolveInstance::iterate()` run follows this sequence:

- The host creates multisample images and single-sample resolve images for every attachment in `attachmentList`, plus input-attachment views for depth and stencil aspects where needed.
- The host generates per-sample pixel data using a seed derived from the test parameters [getRandomSeed](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L318-L339), uploads it into storage buffers, and records upload-pass draw calls that write the data into the multisample images.
- The host records resolve-pass draw calls. For dynamic rendering, each resolve pass begins a rendering instance with `VK_RENDERING_CUSTOM_RESOLVE_BIT_EXT`, calls `vkCmdBeginCustomResolveEXT`, binds the resolve pipeline, and draws. For legacy render passes, the resolve is expressed through subpass resolve attachments and `VK_RESOLVE_MODE_CUSTOM_BIT_EXT`.
- After all passes, the host copies each single-sample resolve image to a host-visible buffer.
- The host computes reference values per pixel by applying the same resolve strategy to the uploaded per-sample data [reference computation](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3289-L3374).
- Color results are compared with `tcu::floatThresholdCompare` using a threshold derived from the lower-precision of the upload and resolve formats, widened by 2x for sRGB [color compare](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3416-L3468).
- Depth results are compared with `tcu::dsThresholdCompare` using format-dependent thresholds (D16: 0.000025, D32: 0.0000002) [depth compare](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3377-L3404).
- Stencil results are compared with `tcu::dsThresholdCompare` using a zero threshold (exact match) [stencil compare](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3406-L3413).
- Resolve attachment store operations use `VK_ATTACHMENT_STORE_OP_DONT_CARE`; the spec overrides this to an implicit store for custom-resolve attachments.

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Multisample images | Yes | Color/depth/stencil/input attachments | Written by upload passes, read by resolve passes | No | Carry per-sample data between upload and resolve. |
| Single-sample resolve images | Yes | Resolve attachments | Written by resolve passes | Copied to buffer | Hold resolved results checked by the host. |
| Per-sample pixel buffers | Yes | Storage buffers (descriptor set 0) | Read by upload shaders | No | Feed known per-sample values into upload passes. |
| Input attachment views | Yes | Descriptor set 1 | Read by resolve shaders | No | Let resolve shaders read multisample samples. |
| Verification buffers | Yes | Transfer destination | Filled by image-to-buffer copy | Yes | Host-visible storage for pixel comparison. |

### Fragment region cases

Each `FragmentRegionInstance::iterate()` run creates two multisample color images and one single-sample result image whose width is expanded by the sample count [iterate](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3679-L3738). The test records a custom resolve render pass that reads from the multisample images and writes to the result, then compares the result against a reference computed from the known per-sample data using `tcu::floatThresholdCompare` with a threshold of 0.005.

### FDM cases

Each `FDMInstance::iterate()` run sets up a fragment density map, fills a multisample color image with per-sample gradient data, resolves it, and validates the single-sample result with a custom per-pixel check that accounts for the density map's subsampling [FDM validation](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5597-L5766). Unlike the main and fragment-region cases, FDM does not use a single `tcu::floatThresholdCompare`. Each pixel must have alpha exactly 1.0, red/green values within `redGreenThreshold(0.010f)` of the expected gradient, and enough identical neighbors to match the fragment size decoded from the blue channel (`neighborThreshold` of `0.0038f` for RG, `0.005f` for B). A limited number of border pixels per layer are tolerated via `acceptedLayerFailures`.

### single_sample_clear case

See `### single_sample_clear` in Behavior Parameters. The scissor region is compared with `tcu::floatThresholdCompare` at zero threshold, and the out-of-scissor corner check emits a `QualityWarning` if it matches the resolve clear color [verification](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6054-L6068).

## Failure Meaning

### Failure Cause Mapping

The failure causes below are indexed by test mechanism, the primary behavioral axis. A second table covers the construction-type secondary axis.

| If this test mechanism fails | Possible failure cause(s) |
|------------------------------|---------------------------|
| main resolve cases | Incorrect custom-resolve shader execution, input-attachment sample read, resolve-strategy application, format-change handling, or attachment-index/layout handling. |
| fragment_region | Incorrect `VK_RENDERING_FRAGMENT_REGION_BIT_EXT` handling for custom resolve sample access outside `SampleMask`. |
| fdm | Incorrect interaction between custom resolve and fragment density map subsampling, multilayer, or multiview. |
| single_sample_clear | Incorrect (or over-aggressive) clearing of the single-sample resolve attachment outside the rendered region. |

| If this construction-type value fails | Possible failure cause(s) |
|---------------------------------------|---------------------------|
| `monolithic` | Incorrect monolithic pipeline creation or resolve pipeline state for custom resolve. |
| `fast_lib` | Incorrect fast-linked graphics pipeline library construction for custom resolve pipelines. |
| `shader_objects` | Incorrect unlinked SPIR-V shader object setup for custom resolve (dynamic rendering only). |

### Cause Analysis

#### Incorrect custom-resolve shader execution or input-attachment read

**Possible failure symptoms:** A main resolve case produces a single-sample resolve image that does not match the host-computed reference after applying the selected resolve strategy. The mismatch appears in color, depth, or stencil pixels within the resolved area [reference computation and compare](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3289-L3470).

**Possible implementation causes:** The resolve shader reads multisample samples through `subpassLoad` and writes the result. A failure can come from the driver or hardware returning wrong sample data from the input attachment, from incorrect `vkCmdBeginCustomResolveEXT` handling that does not set up the resolve path, from the implicit store not firing for `VK_RESOLVE_MODE_CUSTOM_BIT_EXT` attachments, or from the resolve attachment layout transition being incorrect. For format-change cases, a failure can also come from incorrect format conversion between the upload and resolve formats. The spec defines the custom-resolve store and undefined-contents semantics in the [render pass chapter](../../../../vulkan-docs/src/chapters/renderpass.adoc#L1079-L1108).

#### Incorrect fragment region handling

**Possible failure symptoms:** A `fragment_region` case produces a result image that does not match the reference, indicating the render pass did not correctly access samples outside its `SampleMask` when `VK_RENDERING_FRAGMENT_REGION_BIT_EXT` was set [FragmentRegionInstance::iterate](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3679).

**Possible implementation causes:** The flag tells the implementation that the fragment shader may read samples not covered by the rasterized fragments. A failure points to the driver or hardware not preserving or exposing those samples to the custom resolve shader when the flag is set. Source-level investigation of the specific failing `close`/`large` combination is needed to narrow the cause further.

#### Incorrect fragment density map interaction

**Possible failure symptoms:** An `fdm` case produces a single-sample result that does not match the reference after accounting for the density map's subsampling [FDM reference and compare](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L4275-L4285).

**Possible implementation causes:** The fragment density map changes how many fragments are generated and where. Combined with custom resolve, a failure can come from incorrect density-map-driven fragment placement during the fill pass, incorrect resolve readback of subsampled data, or incorrect handling of multilayer or multiview with both features active. The density map offset extension adds another variable when `useOffset` is true.

#### Incorrect single-sample clear behavior

**Possible failure symptoms:** The `single_sample_clear` case either fails the scissor-region comparison (the resolved quadrant does not match color B), or emits a `QualityWarning` because the out-of-scissor bottom-right corner matches color B [single_sample_clear verification](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6054-L6068).

**Possible implementation causes:** The spec says the resolve attachment contents become undefined when `vkCmdBeginCustomResolveEXT` is called [spec](../../../../vulkan-docs/src/chapters/renderpass.adoc#L1080-L1090). A scissor-region failure means the resolve itself did not write the expected result. A `QualityWarning` means the implementation likely cleared the entire single-sample attachment with the multisample clear value, which is unnecessary work even though it is not a spec violation. The warning is a quality signal, not a hard failure.

## Case Pruning

### Requirement-based pruning

- All cases require the `customResolve` feature from `VkCustomResolveFeaturesEXT` [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L593-L595).
- Dynamic rendering cases require `dynamicRenderingLocalRead` [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L605-L607).
- The `single_sample_clear` case requires both `customResolve` and `dynamicRenderingLocalRead` [SingleSampleClearCheckSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5768-L5776).
- Cases with unused attachments require `VK_EXT_dynamic_rendering_unused_attachments` [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L663-L667).
- Cases using stencil aspects require `VK_EXT_shader_stencil_export` unless `disableStencilExport` is set [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L669-L692).
- Depth and stencil resolve cases require `VK_RESOLVE_MODE_CUSTOM_BIT_EXT` in the supported resolve modes [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L763-L779).
- Each format and sample count is checked against `vkGetPhysicalDeviceImageFormatProperties2` before registration [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L629-L660).
- Color attachment count must not exceed `limits.maxColorAttachments`, and input attachment count must not exceed `limits.maxPerStageDescriptorInputAttachments` [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L699-L761).
- `shader_objects` is skipped for non-dynamic-rendering rendering types [construction loop](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6110-L6112).
- `renderpass2` skips the main resolve cases, fragment region, and single-sample-clear cases; it only runs FDM cases [RP2 guard](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6118).
- Multiview FDM cases skip shader objects [registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7047-L7049).
- `dynamic_rendering` and its subgroups are non-SC only [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8521-L8548).

### Design-based pruning

- The main resolve case matrix is only generated when the rendering type is not `RENDERPASS2` [RP2 skip](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6118). Render pass 2 gets only the FDM family because the core custom-resolve render-pass object path uses legacy render passes internally (see the `DE_ASSERT(m_params.getRenderingType() == RENDERING_TYPE_RENDERPASS_LEGACY)` at [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L611-L613)).
- The custom-resolve-info omission flags (`uploadCustomResolveFragOutOnly`, `emptyCustomResolveInFragShader`, `unusedAttNoUploadCustomInfo`) are only exercised for dynamic rendering with fast-linked libraries [omission cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6153-L6172).
- Unused-attachment cases are dynamic-rendering only [unused registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6891).
- FDM cases skip the `multiLayer && multiView` combination [registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7044-L7045).
- FDM custom-resolve-info omission flags are only exercised for dynamic rendering with fast-linked libraries [registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7054-L7059).
- Location remapping (`att_index_change_with_remap`) is dynamic-rendering only [registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6637-L6641).

## Key Takeaways

- `VK_EXT_custom_resolve` moves the multisample resolve decision from fixed-function hardware into a shader. The test proves this by uploading known per-sample data and checking that the resolved output matches the strategy the shader applied (average, fixed value, or selected sample).
- The file implements four mechanisms: the main shader-driven resolve matrix, fragment-region interaction, fragment density map interaction, and the dynamic-rendering-only unnecessary-clear detection case.
- `renderpass2` gets only the FDM family. The core custom-resolve path uses legacy render-pass objects internally; render pass 2 is not exercised for the main matrix.
- The three resolve strategies are deliberate: average mirrors what hardware does automatically, while fixed-value and selected-sample prove the shader, not the hardware, decided the output.
- The `single_sample_clear` case uses a `QualityWarning`, not a hard failure, to flag implementations that clear the resolve attachment outside the render region. The spec allows the contents to become undefined, so clearing is unnecessary work but not a violation.
- See `## Failure Meaning` for how to interpret a failing case by mechanism and construction type.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family registration | [createRenderPassCustomResolveTests](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6080-L6104) | Creates the `custom_resolve` group and construction-type intermediate nodes. |
| Attachment to rendering roots | [vktRenderPassTests.cpp#L8502-L8546](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8502-L8546) | Attaches `custom_resolve` under `renderpass1`, `renderpass2`, and `dynamic_rendering`. |
| Test parameters | [TestParams struct](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L275-L291) | Defines attachment list, upload passes, resolve passes, and feature flags. |
| Resolve type enum | [ResolveType](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L124-L129) | The three shader-side resolve strategies. |
| Support checks | [CustomResolveCase::checkSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L589-L780) | Feature, extension, format, sample-count, and limit gating. |
| Shader generation | [CustomResolveCase::initPrograms](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L782-L1000) | Generates upload and resolve fragment shaders per case. |
| Main runtime and verification | [CustomResolveInstance::iterate](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L553) | Creates resources, records passes, computes reference, compares results. |
| Reference value computation | [reference loop](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3289-L3374) | Host-side application of resolve strategies to per-sample data. |
| Color verification | [floatThresholdCompare](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3416-L3468) | Format-adaptive threshold comparison for color attachments. |
| Depth/stencil verification | [dsThresholdCompare](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3377-L3413) | Depth and stencil comparison with format-dependent thresholds. |
| Fragment region test | [FragmentRegionInstance::iterate](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L3679) | Tests `VK_RENDERING_FRAGMENT_REGION_BIT_EXT` with custom resolve. |
| FDM test | [FDMInstance](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L4314-L4326) | Tests custom resolve with fragment density map. |
| FDM support checks | [FDMCase::checkSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L4389) | Fragment density map feature and extension gating. |
| single_sample_clear test | [SingleSampleClearIterate](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5812-L6070) | Detects unnecessary single-sample attachment clearing. |
| single_sample_clear support | [SingleSampleClearCheckSupport](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L5768-L5776) | Feature gating for the clear-detection case. |
| Simple case registration | [simple cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6120-L6151) | One-attachment cases for each resolve strategy. |
| Depth/stencil case registration | [depth/stencil cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6175-L6431) | Depth-only, stencil-only, and combined depth/stencil cases. |
| Format-change case registration | [format-change cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6432-L6615) | Cases where upload and resolve formats differ. |
| Complex multi-attachment registration | [complex cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6665-L6841) | Multi-attachment, multi-upload, multi-resolve cases. |
| Unused attachment registration | [unused cases](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L6891-L7018) | Dynamic-rendering unused-attachment interaction cases. |
| Fragment region registration | [fragment_region registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7021-L7035) | Fragment region case loop. |
| FDM registration | [fdm registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7037-L7092) | FDM case loop. |
| single_sample_clear registration | [single_sample_clear registration](../../../modules/vulkan/renderpass/vktRenderPassCustomResolveTests.cpp#L7094-L7098) | Dynamic-rendering-only clear detection registration. |
| Spec reference | [renderpass.adoc custom resolve](../../../../vulkan-docs/src/chapters/renderpass.adoc#L1079-L1108) | Spec semantics for custom resolve, undefined contents, and implicit store. |
| Mustpass entries | [renderpasses.txt](../../../mustpass/main/vk-default/renderpasses.txt) | VK default mustpass for the `renderpasses` category. |
