## Overview

**Core question:** Does the implementation correctly execute render passes and dynamic rendering across legacy render-pass objects, render pass 2, and dynamic rendering, producing pixel results that match a host-side software reference renderer for every attachment, load/store operation, and layout transition?

- This page covers the hybrid dispatcher + core implementation file [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp), which owns both the `createRenderPassesTests()` category entry point and the core sub-variants shared by every rendering type.
- This file registers the three top-level groups `renderpass1`, `renderpass2`, and `dynamic_rendering`, then routes them through the shared `createRenderPassTestsInternal()` builder that fans out into `suballocation`, `dedicated_allocation`, and `no_draws` intermediate nodes.
- The core sub-variants implemented here are `simple`, `formats`, `attachment`, `attachment_write_mask`, and `attachment_allocation`, plus the single-case `no_draw_clear_load_store` leaf. These are the families every other implementation file in the test category plugs into.
- All cases validate by software reference rendering: the host computes an expected image per attachment, the device renders, and the two are compared pixel by pixel with format-dependent epsilon tolerance.

## Background Knowledge

- **Render pass object versus dynamic rendering.** A traditional Vulkan render pass is an explicit `VkRenderPass` object describing attachments, subpasses, and dependencies, paired with a `VkFramebuffer`. Dynamic rendering (`VK_KHR_dynamic_rendering`, core in 1.3) replaces the object with `vkCmdBeginRendering` / `vkCmdEndRendering` and per-draw attachment information. The core sub-variants in this file run unchanged across both models, selected only by the `GroupParams::renderingType` field.
- **Load and store operations.** Each attachment aspect has a load operation (`CLEAR`, `LOAD`, `DONT_CARE`) applied at first use inside the render pass, and a store operation (`STORE`, `DONT_CARE`) applied when the render pass or rendering instance ends. `DONT_CARE` as a load op leaves the corresponding pixels undefined inside the render area, which the reference renderer marks specially; `DONT_CARE` as a store op lets the attachment's contents be discarded after the render pass ends.
- **Software reference rendering.** Rather than relying on a second GPU render for the expected result, this test family computes the expected per-pixel values entirely on the host. The host walks each subpass in order, applies clear/load/draw operations to a `vector<PixelValue>` grid, and produces one reference image per attachment. Undefined pixels are filled with a fixed 3×3 grid pattern so that undefined regions are visually distinct in the test log.
- **Lazy versus strict image memory.** The `IMAGEMEMORY_LAZY` flag selects lazily-allocated memory (typically `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT`), which restricts the set of initial/final layouts that can be exercised because lazy memory has fewer valid usage paths. `IMAGEMEMORY_STRICT` exercises the full layout set.

## Registration Hierarchy

The category root `renderpasses` is registered by `createRenderPassesTests()` in [vktTestPackage.cpp#L1354](../../../modules/vulkan/vktTestPackage.cpp#L1354). Its three rendering roots are documented as separate trees below. The direct children shown are the branches represented in the default mustpass file; the shared `suballocation`, `dedicated_allocation`, and `no_draws` branches are implemented by this page.

```text
renderpasses.renderpass1
├── custom_resolve
├── dedicated_allocation
├── depth_stencil_write_conditions
├── dithering
├── fragment_density_map
├── multiple_subpasses_multiple_command_buffers
├── nested_command_buffers
├── no_draws
├── performance_counters_by_region
├── remaining_array_layers
└── suballocation

renderpasses.renderpass2
├── custom_resolve
├── dedicated_allocation
├── depth_stencil_resolve
├── dithering
├── fragment_density_map
├── multiview_per_view
├── nested_command_buffers
├── no_draws
├── performance_counters_by_region
├── remaining_array_layers
└── suballocation

renderpasses.dynamic_rendering
├── complete_secondary_cmd_buff
├── graphics_pipeline_library
├── partial_secondary_cmd_buff
└── primary_cmd_buff
```

The `dynamic_rendering` group has four direct children, `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff`, and `graphics_pipeline_library`, that differ only in their `GroupParams` (command-buffer level and pipeline construction type), not in the core test groups they contain [createDynamicRenderingTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8638-L8679).

Each rendering root expands into shared and rendering-type-specific branches. The source also creates registration branches such as `multisample`, `multisample_resolve`, `sampleread`, `unused_attachment`, `unused_clear_attachments`, `attachment_sparse_filling`, `clear_some_attachments`, `sparserendertarget`, `load_store_op_none`, `subpass_merge_feedback`, and `subpass_dependencies`; render pass 2 additionally has `depth_stencil_resolve` and `multiview_per_view`, while dynamic rendering additionally creates `basic`, `random`, `unused_attachments`, `local_read`, `local_read_maint10`, and `multiview_clear`. These are registration-only context for this page and are documented in their owning pages.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| RenderingType | `RENDERING_TYPE_RENDERPASS_LEGACY`, `RENDERING_TYPE_RENDERPASS2`, `RENDERING_TYPE_DYNAMIC_RENDERING` | Selects the render-pass model exercised. Changes how the render pass object (or its absence) is created and how subpass transitions are recorded. | [vktRenderPassGroupParams.hpp#L34-L39](../../../modules/vulkan/renderpass/vktRenderPassGroupParams.hpp#L34-L39) |
| AllocationKind | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` | Selects whether attachment backing memory is suballocated from a larger pool or given a dedicated allocation. Exercises `VK_KHR_dedicated_allocation`. | [vktRenderPassTests.cpp#L147-L151](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L147-L151) |
| Command buffer mode | primary only, secondary (partial), secondary (complete) | For dynamic rendering only: whether draws go in the primary command buffer, a secondary command buffer that does not own the render-pass scope, or a secondary command buffer that completely contains `vkCmdBeginRendering`/`vkCmdEndRendering`. | [vktRenderPassGroupParams.hpp#L48-L63](../../../modules/vulkan/renderpass/vktRenderPassGroupParams.hpp#L48-L63) |
| Pipeline construction type | `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`, `PIPELINE_CONSTRUCTION_TYPE_FAST_LINKED_LIBRARY` | Selects monolithic pipelines or fast-linked graphics pipeline libraries. The `graphics_pipeline_library` dynamic-rendering variant uses the latter. | [createDynamicRenderingTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8669-L8676) |
| Color formats | 48 core formats plus `VK_FORMAT_A8_UNORM_KHR` | Drives the `formats` sub-variant: each format gets load-op and render-type cases, plus input-attachment self-dependency cases. | [s_coreColorFormats](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6314-L6361) |
| Depth/stencil formats | `D16_UNORM`, `X8_D24_UNORM_PACK32`, `D32_SFLOAT`, `D24_UNORM_S8_UINT`, `D32_SFLOAT_S8_UINT` | Used by `simple`, `formats`, and `attachment` when a depth/stencil aspect is selected. | [s_coreDepthStencilFormats](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6363-L6367) |
| LoadOps | `CLEAR`, `LOAD`, `DONT_CARE` | Applied per attachment aspect at first use. `DONT_CARE` produces undefined pixels inside the render area. | [addAttachmentTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6372-L6373) |
| StoreOps | `STORE`, `DONT_CARE` | Applied per attachment aspect at render-pass end. Only `STORE` attachments are checked on readback. | [addAttachmentTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6375) |
| RenderTypes | `NONE`, `CLEAR`, `DRAW`, `CLEAR|DRAW` | Selects whether the subpass records no work, only `vkCmdClearAttachments`, only draws, or both. `NONE` exercises pure load/store behavior. | [TestConfig::RenderTypes](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L806-L811) |
| CommandBufferTypes | `INLINE`, `SECONDARY`, `INLINE|SECONDARY` | Selects whether subpass work is recorded inline in the primary command buffer or delegated to a secondary command buffer. | [TestConfig::CommandBufferTypes](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L813-L817) |
| ImageMemory | `STRICT`, `LAZY`, `STRICT|LAZY` | Selects strict or lazy allocation per attachment and restricts the initial/final layout set accordingly. | [TestConfig::ImageMemory](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L819-L823) |

## Behavior Parameters

The primary behavioral axis is the core sub-variant group: `simple`, `formats`, `attachment`, `attachment_write_mask`, `attachment_allocation`, and `no_draw_clear_load_store`. Each sub-variant exercises a distinct aspect of render-pass correctness. The intermediate-node axis (`suballocation` / `dedicated_allocation` / `no_draws`) is a secondary axis that changes memory allocation strategy, not the tested render-pass property.

### simple: single-attachment baseline cases

Nine hand-written cases that exercise one attachment at a time across the basic attachment-type combinations: `color`, `depth`, `stencil`, `depth_stencil`, `color_depth`, `color_stencil`, `color_depth_stencil`, `no_attachments`, and `color_unused_omit_blend_state` [addSimpleTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7353-L7577). Each uses a fixed 64×64 target with `CLEAR`/`STORE` load/store ops and a single draw. The `color_unused_omit_blend_state` case (legacy and render pass 2 only) uses two subpasses: the first writes the color attachment, the second marks it `VK_ATTACHMENT_UNUSED` and omits color blend state, checking that an unused attachment with omitted blend state does not interfere.

### formats: per-format load/store and input-attachment coverage

Iterates every core color format (plus `VK_FORMAT_A8_UNORM_KHR` on non-SC) and every core depth/stencil format [addFormatTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7589). For each color format it registers load-op groups (`clear`, `load`, `dont_care`) and within each a render-type group (`clear`, `draw`, `clear_draw`). A separate `input` group uses two subpasses with a `BY_REGION` dependency: the first subpass writes the format under test, the second reads it back as an input attachment and copies it to a second color attachment. This exercises the input-attachment self-dependency path and the `VK_KHR_maintenance2` input-aspect mechanism via the `use_input_aspect` variant (legacy only).

### attachment: randomly generated multi-attachment cases

Generates 100 cases for 1 attachment and 200 cases each for 3, 4, and 8 attachments [addAttachmentTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6369-L6582). Each case randomly chooses per-attachment format, load/store ops, initial/final layouts, subpass layout, and whether to add a depth/stencil attachment; it also randomly selects render type, command-buffer type, image memory mode, target size, render position, and render size. The random seed is fixed (`1433774382u`) so the generated matrix is deterministic across runs.

### attachment_write_mask: color write mask with independent blend

Tests `VK_COLOR_COMPONENT_*` write masking across 1, 2, 3, 4, and 8 attachments [addAttachmentWriteMaskTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6584). Each case clears all attachments, then a rotating draw start index means each draw writes a different subset of attachments while the rest keep their cleared value. The test requires `DEVICE_CORE_FEATURE_INDEPENDENT_BLEND` because each attachment uses a different write mask.

### attachment_allocation: multi-subpass allocation patterns

Exercises how attachment allocation evolves across multiple subpasses using six allocation patterns: `grow`, `shrink`, `roll`, `grow_shrink`, `input_output_chain`, and `input_output` [addAttachmentAllocationTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6674). Each pattern defines a different way the set of active attachments changes between subpasses, for example `grow` adds one attachment per subpass, `roll` drops one and picks up a new one, and `input_output_chain` chains single-input/single-output subpasses. The `input_output` pattern (`ALLOCATIONTYPE_IO_GENERIC`) generates 4 to 34 attachments and 4 to 34 subpasses (`4u + rng.getUint32() % 31u` each) with random input and color attachment counts per subpass, including occasional depth/stencil attachments.

### no_draw_clear_load_store: clear-only load/store without draws

A single leaf case (`no_draw_clear_load_store`) that clears a 1×1 color attachment with `LOAD_OP_CLEAR` / `STORE_OP_STORE`, records no draws, and checks that the readback pixel equals the clear color [RenderPassNoDrawLoadStoreTestInstance::iterate](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6152-L6312). This isolates the clear-and-store path from any draw-side behavior, verifying that a render pass with only a clear operation stores the cleared value correctly.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.renderpasses.renderpass1.suballocation.formats.r8g8b8a8_unorm.input.clear.dont_care.self_dep_clear_draw
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `renderpass1.suballocation` | Uses a legacy `VkRenderPass` and the default suballocator. |
| `formats.r8g8b8a8_unorm.input` | Uses one 64×64, single-sampled `VK_FORMAT_R8G8B8A8_UNORM` attachment as both input attachment 0 and color attachment 0 in the second subpass. |
| `clear.dont_care` | Selects `VK_ATTACHMENT_LOAD_OP_CLEAR` and `VK_ATTACHMENT_STORE_OP_DONT_CARE` for the color aspect. |
| `self_dep_clear_draw` | Selects the two-subpass input/output-aliasing configuration and records both `vkCmdClearAttachments` and a draw in each subpass; no multisample or input-aspect suffix is selected. |

#### Purpose

This fragment shader is the input-attachment stage generated for subpass 1. It reads the same color attachment that it writes after a by-region color-write-to-input-read self-dependency, then converts the loaded values and coordinate parity into the deterministic booleans mirrored by the software reference renderer.

#### Structural Design

| Phase | Shader-visible operation | Runtime relationship |
|-------|--------------------------|----------------------|
| Input/output alias | `i_color0` is input attachment index 0 at set 0, binding 0; `o_color0` is location 0. | Both references select attachment 0 in subpass 1. |
| Visibility | No shader instruction performs synchronization. | Before the draw, the command recorder clears attachment 0 and issues a `VK_DEPENDENCY_BY_REGION_BIT` image barrier from color-attachment writes to input-attachment reads. |
| Input classification | Four `subpassLoad` calls test whether R, G, B, and A equal `1.0`. | The host reference renderer consumes the same four attachment-component values. |
| Output mapping | Every component begins with `(x is odd) && (y is even)`, then compares that result with its corresponding input predicate. | `boolOpFromIndex(1)` selects `AND`; one input component is assigned to each output component. |
| Result | The four booleans become normalized `0.0` or `1.0` color components. | The selected store op is `DONT_CARE`, so this exact case executes the dataflow but does not read back attachment 0 after the render pass. |

#### Shader Code

```glsl
#version 450
/// Input attachment 0 aliases color attachment 0 in this self-dependency subpass; binding 0 supplies the descriptor read by subpassLoad.
layout(input_attachment_index = 0, set=0, binding=0) uniform highp subpassInput i_color0;
/// Location 0 writes the same R8G8B8A8_UNORM attachment after the input read has been made visible by the by-region self-dependency.
layout(location = 0) out highp vec4 o_color0;
void main (void) {
	/// Convert the four loaded channels into exact-one boolean predicates, matching the host reference renderer input tests.
	bool inputs[4];
	bool outputs[4];
	inputs[0] = 1.0 == float(subpassLoad(i_color0).x);
	inputs[1] = 1.0 == float(subpassLoad(i_color0).y);
	inputs[2] = 1.0 == float(subpassLoad(i_color0).z);
	inputs[3] = 1.0 == float(subpassLoad(i_color0).w);
	/// Subpass index 1 and attachment index 0 select AND for every component; each parity result is then compared with its loaded channel predicate.
	outputs[0] = (int(gl_FragCoord.x) % 2 == 1) && (int(gl_FragCoord.y) % 2 == 0);
	outputs[0] = outputs[0] == inputs[0];
	outputs[1] = (int(gl_FragCoord.x) % 2 == 1) && (int(gl_FragCoord.y) % 2 == 0);
	outputs[1] = outputs[1] == inputs[1];
	outputs[2] = (int(gl_FragCoord.x) % 2 == 1) && (int(gl_FragCoord.y) % 2 == 0);
	outputs[2] = outputs[2] == inputs[2];
	outputs[3] = (int(gl_FragCoord.x) % 2 == 1) && (int(gl_FragCoord.y) % 2 == 0);
	outputs[3] = outputs[3] == inputs[3];
	/// Store comparison results as normalized 0/1 color components for host-side image verification.
	o_color0 = vec4(outputs[0], outputs[1], outputs[2], outputs[3]);
}
```

#### Additional Info

- [The case builder](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7772-L7835) gives subpass 1 the same attachment at input and color index 0 and adds both a `0 -> 1` dependency and a `1 -> 1` self-dependency with `VK_DEPENDENCY_BY_REGION_BIT`.
- [The command recorder](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L2798-L2885) emits the matching in-subpass image barrier after clear commands and before the draw. [The host renderer](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L4196-L4304) reproduces the input-to-output boolean mapping.
- `initPrograms()` supplies no explicit `vk::ShaderBuildOptions`, so the source-collection baseline target is SPIR-V 1.0. Because this representative selects `STORE_OP_DONT_CARE`, [image verification](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L4665-L4794) does not compare attachment 0 after execution.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Format | Integer formats select `isubpassInput`/`ivec4` or `usubpassInput`/`uvec4`; floating and normalized formats, including this case, select `subpassInput`/`vec4`. The format channel count controls how many input predicates and mapped output components are generated. | [input/output type helpers](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L4865-L4920), [input branch](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5813-L5968) |
| Sample count | The `_ms` variants use `subpassInputMS` and call `subpassLoad(i_color0, gl_SampleID)` instead of the single-sample form shown here. | [sample-count registration](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7625-L7629), [load generation](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5901-L5914) |
| Render type | `draw` and `clear_draw` generate the same fragment program, while `clear` records no draw and therefore needs no shader program; adding `clear` changes the values visible to the input load through runtime commands rather than declarations. | [render-type registration](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7611-L7617), [program gate](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5679-L5685) |
| Load/store ops and input-aspect flag | These choices do not alter this GLSL. They change attachment operations or legacy render-pass input-aspect metadata around it. | [input-case construction](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7672-L7835) |

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
; Bound: 150
; Schema: 0
               OpCapability Shader
               OpCapability InputAttachment
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %o_color0
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %inputs "inputs"
               OpName %i_color0 "i_color0"
               OpName %outputs "outputs"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %o_color0 "o_color0"
               OpDecorate %i_color0 Binding 0
               OpDecorate %i_color0 DescriptorSet 0
               OpDecorate %i_color0 InputAttachmentIndex 0
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %o_color0 Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %bool = OpTypeBool
       %uint = OpTypeInt 32 0
     %uint_4 = OpConstant %uint 4
%_arr_bool_uint_4 = OpTypeArray %bool %uint_4
%_ptr_Function__arr_bool_uint_4 = OpTypePointer Function %_arr_bool_uint_4
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
      %float = OpTypeFloat 32
    %float_1 = OpConstant %float 1
         %16 = OpTypeImage %float SubpassData 0 0 0 2 Unknown
%_ptr_UniformConstant_16 = OpTypePointer UniformConstant %16
   %i_color0 = OpVariable %_ptr_UniformConstant_16 UniformConstant
      %v2int = OpTypeVector %int 2
         %21 = OpConstantComposite %v2int %int_0 %int_0
    %v4float = OpTypeVector %float 4
     %uint_0 = OpConstant %uint 0
%_ptr_Function_bool = OpTypePointer Function %bool
      %int_1 = OpConstant %int 1
     %uint_1 = OpConstant %uint 1
      %int_2 = OpConstant %int 2
     %uint_2 = OpConstant %uint 2
      %int_3 = OpConstant %int 3
     %uint_3 = OpConstant %uint 3
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
%_ptr_Input_float = OpTypePointer Input %float
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %o_color0 = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
       %main = OpFunction %void None %3
          %5 = OpLabel
     %inputs = OpVariable %_ptr_Function__arr_bool_uint_4 Function
    %outputs = OpVariable %_ptr_Function__arr_bool_uint_4 Function
         %19 = OpLoad %16 %i_color0
         %23 = OpImageRead %v4float %19 %21
         %25 = OpCompositeExtract %float %23 0
         %26 = OpFOrdEqual %bool %float_1 %25
         %28 = OpAccessChain %_ptr_Function_bool %inputs %int_0
               OpStore %28 %26
         %30 = OpLoad %16 %i_color0
         %31 = OpImageRead %v4float %30 %21
         %33 = OpCompositeExtract %float %31 1
         %34 = OpFOrdEqual %bool %float_1 %33
         %35 = OpAccessChain %_ptr_Function_bool %inputs %int_1
               OpStore %35 %34
         %37 = OpLoad %16 %i_color0
         %38 = OpImageRead %v4float %37 %21
         %40 = OpCompositeExtract %float %38 2
         %41 = OpFOrdEqual %bool %float_1 %40
         %42 = OpAccessChain %_ptr_Function_bool %inputs %int_2
               OpStore %42 %41
         %44 = OpLoad %16 %i_color0
         %45 = OpImageRead %v4float %44 %21
         %47 = OpCompositeExtract %float %45 3
         %48 = OpFOrdEqual %bool %float_1 %47
         %49 = OpAccessChain %_ptr_Function_bool %inputs %int_3
               OpStore %49 %48
         %54 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %55 = OpLoad %float %54
         %56 = OpConvertFToS %int %55
         %57 = OpSMod %int %56 %int_2
         %58 = OpIEqual %bool %57 %int_1
               OpSelectionMerge %60 None
               OpBranchConditional %58 %59 %60
         %59 = OpLabel
         %61 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %62 = OpLoad %float %61
         %63 = OpConvertFToS %int %62
         %64 = OpSMod %int %63 %int_2
         %65 = OpIEqual %bool %64 %int_0
               OpBranch %60
         %60 = OpLabel
         %66 = OpPhi %bool %58 %5 %65 %59
         %67 = OpAccessChain %_ptr_Function_bool %outputs %int_0
               OpStore %67 %66
         %68 = OpAccessChain %_ptr_Function_bool %outputs %int_0
         %69 = OpLoad %bool %68
         %70 = OpAccessChain %_ptr_Function_bool %inputs %int_0
         %71 = OpLoad %bool %70
         %72 = OpLogicalEqual %bool %69 %71
         %73 = OpAccessChain %_ptr_Function_bool %outputs %int_0
               OpStore %73 %72
         %74 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %75 = OpLoad %float %74
         %76 = OpConvertFToS %int %75
         %77 = OpSMod %int %76 %int_2
         %78 = OpIEqual %bool %77 %int_1
               OpSelectionMerge %80 None
               OpBranchConditional %78 %79 %80
         %79 = OpLabel
         %81 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %82 = OpLoad %float %81
         %83 = OpConvertFToS %int %82
         %84 = OpSMod %int %83 %int_2
         %85 = OpIEqual %bool %84 %int_0
               OpBranch %80
         %80 = OpLabel
         %86 = OpPhi %bool %78 %60 %85 %79
         %87 = OpAccessChain %_ptr_Function_bool %outputs %int_1
               OpStore %87 %86
         %88 = OpAccessChain %_ptr_Function_bool %outputs %int_1
         %89 = OpLoad %bool %88
         %90 = OpAccessChain %_ptr_Function_bool %inputs %int_1
         %91 = OpLoad %bool %90
         %92 = OpLogicalEqual %bool %89 %91
         %93 = OpAccessChain %_ptr_Function_bool %outputs %int_1
               OpStore %93 %92
         %94 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %95 = OpLoad %float %94
         %96 = OpConvertFToS %int %95
         %97 = OpSMod %int %96 %int_2
         %98 = OpIEqual %bool %97 %int_1
               OpSelectionMerge %100 None
               OpBranchConditional %98 %99 %100
         %99 = OpLabel
        %101 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
        %102 = OpLoad %float %101
        %103 = OpConvertFToS %int %102
        %104 = OpSMod %int %103 %int_2
        %105 = OpIEqual %bool %104 %int_0
               OpBranch %100
        %100 = OpLabel
        %106 = OpPhi %bool %98 %80 %105 %99
        %107 = OpAccessChain %_ptr_Function_bool %outputs %int_2
               OpStore %107 %106
        %108 = OpAccessChain %_ptr_Function_bool %outputs %int_2
        %109 = OpLoad %bool %108
        %110 = OpAccessChain %_ptr_Function_bool %inputs %int_2
        %111 = OpLoad %bool %110
        %112 = OpLogicalEqual %bool %109 %111
        %113 = OpAccessChain %_ptr_Function_bool %outputs %int_2
               OpStore %113 %112
        %114 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
        %115 = OpLoad %float %114
        %116 = OpConvertFToS %int %115
        %117 = OpSMod %int %116 %int_2
        %118 = OpIEqual %bool %117 %int_1
               OpSelectionMerge %120 None
               OpBranchConditional %118 %119 %120
        %119 = OpLabel
        %121 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
        %122 = OpLoad %float %121
        %123 = OpConvertFToS %int %122
        %124 = OpSMod %int %123 %int_2
        %125 = OpIEqual %bool %124 %int_0
               OpBranch %120
        %120 = OpLabel
        %126 = OpPhi %bool %118 %100 %125 %119
        %127 = OpAccessChain %_ptr_Function_bool %outputs %int_3
               OpStore %127 %126
        %128 = OpAccessChain %_ptr_Function_bool %outputs %int_3
        %129 = OpLoad %bool %128
        %130 = OpAccessChain %_ptr_Function_bool %inputs %int_3
        %131 = OpLoad %bool %130
        %132 = OpLogicalEqual %bool %129 %131
        %133 = OpAccessChain %_ptr_Function_bool %outputs %int_3
               OpStore %133 %132
        %136 = OpAccessChain %_ptr_Function_bool %outputs %int_0
        %137 = OpLoad %bool %136
        %139 = OpSelect %float %137 %float_1 %float_0
        %140 = OpAccessChain %_ptr_Function_bool %outputs %int_1
        %141 = OpLoad %bool %140
        %142 = OpSelect %float %141 %float_1 %float_0
        %143 = OpAccessChain %_ptr_Function_bool %outputs %int_2
        %144 = OpLoad %bool %143
        %145 = OpSelect %float %144 %float_1 %float_0
        %146 = OpAccessChain %_ptr_Function_bool %outputs %int_3
        %147 = OpLoad %bool %146
        %148 = OpSelect %float %147 %float_1 %float_0
        %149 = OpCompositeConstruct %v4float %139 %142 %145 %148
               OpStore %o_color0 %149
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

Each `RenderPassTestInstance::iterate()` run follows the same host-driven sequence [iterate](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5355-L5480):

- The host initializes per-attachment laziness, image clear values, image usage flags, render-pass clear values, and per-subpass render information from the fixed random seed [initialization helpers](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5375-L5383).
- Attachment images and views are created with the selected `AllocationKind`; the `dedicated_allocation` path uses `allocateDedicated` for each image and buffer, while `suballocation` uses the default suballocator [allocateImage](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L190-L210).
- Three command buffers are recorded: one initializes images to their clear values, one records the render pass or dynamic-rendering commands (begin, per-subpass clears and draws, end), and one copies attachment images back to host-visible buffers.
- The three command buffers are submitted as a batch and the host waits on a fence [queue submit](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5461-L5467).
- The host computes reference values with `renderReferenceValues()`, walking each subpass in order and applying load ops, clears, and draw patterns to a `PixelValue` grid per attachment [renderReferenceValues](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L3981-L4081). Undefined pixels (from `LOAD_OP_DONT_CARE` or out-of-render-area regions) are marked and later filled with a 3×3 grid pattern in the reference image.
- `logAndVerifyImages()` compares each non-lazy attachment against its reference [logAndVerifyImages](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L4665-L4794):
  - color attachments use `tcu::floatThresholdCompare` with a format-dependent epsilon;
  - depth attachments use `verifyDepthAttachment` with `requiredDepthEpsilon(format)`;
  - stencil attachments use `verifyStencilAttachment`, which requires an exact match against `0x00` or `0xFF`.
- Only attachments with `STORE_OP_STORE` are checked; `STORE_OP_DONT_CARE` attachments are not validated because their contents are permitted to be discarded.
- On failure, the test logs the output attachment image, the reference image, and a red/green error mask per aspect.

The `no_draw_clear_load_store` case uses a simpler path: it clears a 1×1 `R8G8B8A8_UNORM` image, copies it to a host-visible buffer, and checks the single pixel equals `(1.0, 0.0, 1.0, 1.0)` [no-draw check](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6300-L6309).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Attachment images | Yes | As framebuffer / rendering attachments | Written by clears and draws | Copied to buffer, then read | Primary render targets checked against reference images. |
| Attachment readback buffers | Yes | Transfer destination | Filled by image-to-buffer copy | Yes | Host-visible storage for pixel comparison. |
| Input attachment views | Yes | Descriptor binding 0 | Read by `subpassLoad` in later subpasses | No | Feeds previous-subpass output into the next subpass's shader. |
| Render pass object / framebuffer | Yes (legacy and RP2 only) | Pipeline state | N/A | No | Defines attachments, subpasses, and dependencies for the non-dynamic-rendering path. |

## Failure Meaning

### Failure Cause Mapping

Because the intermediate-node axis (`suballocation` / `dedicated_allocation` / `no_draws`) changes allocation strategy rather than the tested property, the failure causes below are indexed by the core sub-variant. A second small table covers the allocation-strategy axis.

| If this core sub-variant fails | Possible failure cause(s) |
|--------------------------------|---------------------------|
| `simple` | Incorrect single-attachment clear/store/draw for a basic attachment type, or incorrect unused-attachment-with-omitted-blend-state handling. |
| `formats` | Incorrect per-format rendering, load/store op application, layout transition, or input-attachment self-dependency for a specific format. |
| `attachment` | Incorrect randomly configured multi-attachment load/store, layout transition, clear/draw interaction, or secondary-command-buffer recording. |
| `attachment_write_mask` | Incorrect per-attachment color write mask enforcement, or missing `independentBlend` support. |
| `attachment_allocation` | Incorrect multi-subpass attachment allocation/deallocation, input/output chaining, or subpass-to-subpass data flow. |
| `no_draw_clear_load_store` | Incorrect clear-only load/store path when no draws are recorded. |

| If this allocation-strategy value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `suballocation` | Incorrect suballocated memory binding or layout for attachment images. |
| `dedicated_allocation` | Incorrect dedicated allocation binding, or missing `VK_KHR_dedicated_allocation` support. |
| `no_draws` | Incorrect clear/store path when the render pass contains no draw calls. |

### Cause Analysis

#### Incorrect single-attachment clear/store/draw or unused-attachment handling

**Possible failure symptoms:** One of the nine `simple` cases produces a color, depth, or stencil attachment that does not match the reference image after a single clear and draw, or the `color_unused_omit_blend_state` case produces unexpected output in the second (unused-attachment, blend-state-omitted) subpass [addSimpleTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7353-L7577).

**Possible implementation causes:** A failure here points to the driver's handling of a basic single-attachment render pass: incorrect clear value application, incorrect store of the rendered content, incorrect depth/stencil write or test for the selected format, or incorrect behavior when a subpass omits color blend state for an unused attachment. Source-level investigation of the specific failing case is needed to narrow the cause further.

#### Incorrect per-format rendering, load/store, layout, or input-attachment behavior

**Possible failure symptoms:** A specific format under `formats` produces a mismatch in its color output, its depth/stencil aspect, or its input-attachment readback subpass [addFormatTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7589).

**Possible implementation causes:** The cause is format-specific. It can be incorrect format rendering or blending for the failing format, incorrect application of `LOAD_OP_LOAD` (which must preserve prior content) or `LOAD_OP_DONT_CARE` (which may produce undefined content the reference renderer marks as such), an invalid layout transition to or from the initial/final layout chosen for that case, or an incorrect input-attachment read in the second subpass. For the `use_input_aspect` legacy variant, a failure can also come from incorrect `VK_KHR_maintenance2` input-aspect handling. The Vulkan spec defines load/store semantics in the [render pass load and store operations](../../../../vulkan-docs/src/chapters/renderpass.adoc); a mismatch between the implementation and those semantics is the likely root cause.

#### Incorrect multi-attachment configuration or secondary command buffer recording

**Possible failure symptoms:** A randomly generated `attachment` case with 1, 3, 4, or 8 attachments produces one or more attachments whose stored content does not match the reference after the configured clear/draw and load/store operations [addAttachmentTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6369-L6582).

**Possible implementation causes:** Because each case combines many randomly chosen dimensions (format, load/store, layout, render type, command-buffer type, image memory, geometry), the failure can come from any combination the driver mishandles. Common candidates are incorrect layout transitions for the randomly chosen initial/final layout pair, incorrect interaction between `vkCmdClearAttachments` and `LOAD_OP_CLEAR`, or incorrect secondary-command-buffer execution when `CommandBufferTypes::SECONDARY` is selected. The fixed seed means the exact configuration is reproducible from the test log.

#### Incorrect color write mask enforcement or independent blend

**Possible failure symptoms:** An `attachment_write_mask` case produces a color attachment whose masked channels were written even though the corresponding `VK_COLOR_COMPONENT_*` bit was clear, or whose unmasked channels did not receive the draw output [addAttachmentWriteMaskTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6584).

**Possible implementation causes:** The write mask is applied per attachment and each attachment uses a different mask, so a failure points to the driver not honoring the per-target color write mask or not supporting `independentBlend` correctly. The test requires `DEVICE_CORE_FEATURE_INDEPENDENT_BLEND`, so a `NotSupportedError` rather than a pixel mismatch indicates the feature is simply unavailable.

#### Incorrect multi-subpass attachment allocation or data flow

**Possible failure symptoms:** An `attachment_allocation` case under `grow`, `shrink`, `roll`, `grow_shrink`, `input_output_chain`, or `input_output` produces an attachment whose content does not match the reference after the multi-subpass sequence [addAttachmentAllocationTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6674).

**Possible implementation causes:** These cases stress how the driver allocates and tracks attachment resources across many subpasses. A failure can come from incorrect attachment lifetime handling when the active set grows, shrinks, or rolls between subpasses, incorrect input-attachment data flow in the `input_output_chain` and `input_output` patterns, or incorrect preservation of attachments not referenced by a given subpass. For dynamic rendering, the `input_output_chain` and `input_output` patterns are skipped because their generated cases always include at least one attachment with a `DONT_CARE` load or store op, which permits random data in unused attachments on tiling GPUs.

#### Incorrect clear-only load/store path

**Possible failure symptoms:** The `no_draw_clear_load_store` case reads back a pixel that is not the clear color `(1.0, 0.0, 1.0, 1.0)` despite the render pass containing only `LOAD_OP_CLEAR` and `STORE_OP_STORE` with no draws [RenderPassNoDrawLoadStoreTestInstance::iterate](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6152-L6312).

**Possible implementation causes:** Because no draws are recorded, the only device-side work is the clear and the store. A failure points to the clear value not being applied, the cleared content not being stored, or the image-to-buffer copy and layout transition around the store being incorrect.

#### Incorrect allocation-strategy binding

**Possible failure symptoms:** A case passes under `suballocation` but fails under `dedicated_allocation` (or vice versa) with identical render-pass configuration [allocateImage](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L190-L210).

**Possible implementation causes:** The two allocation paths differ only in how backing memory is bound. A dedicated-allocation-only failure points to the `VK_KHR_dedicated_allocation` memory binding path or to memory layout differences in dedicated allocations; a suballocation-only failure points to the default suballocator. If both fail identically, the cause is in the render-pass logic, not the allocation strategy.

## Case Pruning

### Requirement-based pruning

- `renderpass2` requires `VK_KHR_create_renderpass2` [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5522-L5523).
- `dynamic_rendering` requires `VK_KHR_dynamic_rendering`, and multi-subpass dynamic-rendering cases additionally require `VK_KHR_dynamic_rendering_local_read` [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5525-L5532).
- `VK_FORMAT_A8_UNORM_KHR` requires `VK_KHR_maintenance5` [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5514-L5519).
- `dedicated_allocation` requires `VK_KHR_dedicated_allocation` [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5577-L5581).
- Input-aspect cases require `VK_KHR_maintenance2` [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5583-L5587).
- `attachment_write_mask` requires `DEVICE_CORE_FEATURE_INDEPENDENT_BLEND` [requiredFeatures](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5665-L5666).
- Vulkan 1.4 devices without `dynamicRenderingLocalReadDepthStencilAttachments` or `dynamicRenderingLocalReadMultisampledAttachments` skip the corresponding depth/stencil or multisampled input-attachment dynamic-rendering cases [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5541-L5572).
- `dynamic_rendering` and its subgroups are non-SC only [createChildren](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8687-L8689).
- Each subpass is checked against `limits.maxColorAttachments` [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5671-L5676).

### Design-based pruning

- `simple` and `formats` are not repeated when `secondaryCmdBufferCompletelyContainsDynamicRenderpass` is set, because those cases do not use secondary command buffers [addRenderPassTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8443-L8449).
- `attachment_write_mask` is similarly skipped for the complete-secondary-command-buffer variant [addRenderPassTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8454-L8457).
- `attachment_allocation` is skipped for the complete-secondary variant because `dynamic_rendering_local_read` cannot be combined with `begin/endRendering` in each secondary command buffer [addRenderPassTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8459-L8462).
- `addRenderPassTests` returns early for the partial-secondary-command-buffer variant because those cases already include their own secondary-command-buffer coverage [addRenderPassTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8437-L8438).
- Dynamic-rendering cases that rely on render-pass automatic layout transitions are skipped because dynamic rendering would need additional barriers that add no coverage; the generator still consumes the random numbers so that dynamic-rendering case names match their render-pass counterparts [addAttachmentTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6440-L6485).
- For dynamic rendering, `STORE_OP_DONT_CARE` input-attachment cases in `formats` are skipped because tiling GPUs may store random data to unused attachments [addFormatTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7679-L7684).
- The `input_output_chain` and `input_output` allocation patterns are skipped for dynamic rendering for the same tiling-GPU reason [addAttachmentAllocationTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6754-L6760).
- The `graphics_pipeline_library` dynamic-rendering variant repeats only a subset of multi-pass tests because fast-linked libraries are the variable under test, not the full matrix [createRenderPassTestsInternal](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8524-L8525).

## Key Takeaways

- This file is the hybrid heart of the `renderpasses` test category: it owns the dispatcher and the core sub-variants that every other implementation file plugs into through the `suballocation` / `dedicated_allocation` / `no_draws` intermediate nodes.
- The three rendering types (legacy, render pass 2, dynamic rendering) and the four dynamic-rendering command-buffer/pipeline variants all run the same core cases, differing only in `GroupParams`. A failure scoped to one variant points to that variant's recording or construction path, not to the core logic.
- Validation is always host-side software reference rendering with format-dependent epsilon. The shaders are deterministic pattern generators, not the subject under test.
- `STORE_OP_DONT_CARE` attachments are never checked; `LOAD_OP_DONT_CARE` regions are marked undefined and filled with a grid pattern so they are visually distinguishable in the log.
- Dynamic rendering deliberately skips cases that would require layout transitions or `STORE_OP_DONT_CARE` handling that render-pass objects provide automatically, because those cases would add no coverage and could produce implementation-specific results on tiling GPUs.
- See `## Failure Meaning` for how to interpret a failing case by sub-variant and allocation strategy.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category entry point | [createRenderPassesTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8692-L8695) | Registers the `renderpasses` root and delegates to `createChildren`. |
| Top-level group registration | [createChildren](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8681-L8690) | Adds `renderpass1`, `renderpass2`, and `dynamic_rendering` (non-SC only). |
| Shared internal builder | [createRenderPassTestsInternal](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8486-L8612) | Fans out into `suballocation`, `dedicated_allocation`, `no_draws`, and delegated groups; the single function all three rendering types share. |
| Dynamic-rendering sub-variant construction | [createDynamicRenderingTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8638-L8679) | Creates the four dynamic-rendering sub-variants with distinct `GroupParams`. |
| Core group registration | [addRenderPassTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8431-L8463) | Adds `simple`, `formats`, `attachment`, `attachment_write_mask`, `attachment_allocation` to each allocation node. |
| Allocation node factories | [createSuballocationTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8465-L8473), [createDedicatedAllocationTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8475-L8484) | Create the `suballocation` and `dedicated_allocation` intermediate nodes. |
| `simple` cases | [addSimpleTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7353-L7577) | Nine single-attachment baseline cases. |
| `formats` cases | [addFormatTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L7589) | Per-format load/store and input-attachment coverage. |
| `attachment` cases | [addAttachmentTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6369-L6582) | Randomly generated multi-attachment cases. |
| `attachment_write_mask` cases | [addAttachmentWriteMaskTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6584) | Color write mask with independent blend. |
| `attachment_allocation` cases | [addAttachmentAllocationTests](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6674) | Six multi-subpass allocation patterns. |
| `no_draw_clear_load_store` case | [RenderPassNoDrawLoadStoreTestInstance::iterate](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L6152-L6312) | Clear-only load/store validation without draws. |
| Software reference renderer | [renderReferenceValues](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L3981-L4081) | Host-side computation of expected per-pixel values. |
| Image verification | [logAndVerifyImages](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L4665-L4794) | Compares GPU output to reference images with epsilon tolerance. |
| Depth verification | [verifyDepthAttachment](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L4584-L4623) | Depth-aspect comparison with `requiredDepthEpsilon`. |
| Stencil verification | [verifyStencilAttachment](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L4625-L4663) | Stencil-aspect exact match against `0x00` / `0xFF`. |
| Shader generation | [RenderPassTestCase::initPrograms](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5679) | Generates deterministic per-subpass vertex and fragment shaders. |
| Runtime iteration | [RenderPassTestInstance::iterate](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5355-L5480) | Creates resources, records and submits command buffers, runs verification. |
| Support checks | [RenderPassTestCase::checkSupport](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L5504-L5677) | Extension, feature, format, and limit gating. |
| Allocation strategy | [AllocationKind enum](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L147-L151), [allocateImage](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L190-L210) | Suballocation versus dedicated allocation selection. |
| Group parameters | [vktRenderPassGroupParams.hpp#L34-L63](../../../modules/vulkan/renderpass/vktRenderPassGroupParams.hpp#L34-L63) | `RenderingType`, `SynchronizationType`, and `GroupParams` shared by all renderpass tests. |
| Render-pass utilities | [vktRenderPassTestsUtil.cpp](../../../modules/vulkan/renderpass/vktRenderPassTestsUtil.cpp) | `Attachment`, `Subpass`, `SubpassDependency`, `RenderPass` structs and `createRenderPass` helpers used by this file and every delegated implementation file. |
| Mustpass entries | [renderpasses.txt](../../../mustpass/main/vk-default/renderpasses.txt) | VK default mustpass for the `renderpasses` category. |
| Category registration | [vktTestPackage.cpp#L1354](../../../modules/vulkan/vktTestPackage.cpp#L1354) | Attaches `createRenderPassesTests` under the `renderpasses` root. |
