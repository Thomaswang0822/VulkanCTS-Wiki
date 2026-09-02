## Overview

**Core question:** Does each graphics state or shader-interface variation produce the result required when Vulkan device-generated commands drive it?

- This page covers the implementation in [`vktDGCGraphicsMiscTestsExt.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L1-L25) and the registered `dgc.ext.graphics.misc` test family.
- The file combines focused checks for vertex input, pipeline and shader-object interfaces, draw reuse, fragment-stage state, tessellation and geometry push constants, ray queries, and related DGC tokens.
- Each test constructs a small graphics workload, executes it through one DGC variation, and compares a host-readable result with a reference.
- The matrix below explains which dimensions change execution and which names are only combinations of those dimensions.

## Background Knowledge

- Device-generated commands let the implementation execute command sequences described by GPU-visible data. These tests compare that path with the result expected from the same graphics operation.
- An execution set stores pipeline or shader-object state that a generated command can select. A preprocess case generates or preprocesses the command sequence before execution, so it checks the same behavior across a different command lifetime.
- Dynamic state and shader objects move selected graphics state out of a fixed pipeline. The test must distinguish a state value that is changed by a generated command from one that remains in ordinary command state.
- A color, depth, storage-image, or expanded color-buffer comparison turns device work into a deterministic host-side pass/fail result.

## Registration Hierarchy

```text
dgc.ext.graphics.misc
├── dynamic_vertex_input_fast_lib
├── dynamic_vertex_input_fast_lib_execution_set
├── dynamic_vertex_input_monolithic
├── dynamic_vertex_input_monolithic_execution_set
├── dynamic_vertex_input_optimized_lib
├── dynamic_vertex_input_optimized_lib_execution_set
├── dynamic_vertex_input_unlinked_spirv
├── dynamic_vertex_input_unlinked_spirv_execution_set
├── early_fragment_tests
├── early_fragment_tests_preprocess
├── fast_lib_dynamic_a2c_disabled
├── fast_lib_dynamic_a2c_disabled_ies
├── fast_lib_dynamic_a2c_disabled_ies_preprocess
├── fast_lib_dynamic_a2c_disabled_ies_preprocess_sample_mask
├── fast_lib_dynamic_a2c_disabled_ies_sample_mask
├── fast_lib_dynamic_a2c_disabled_preprocess
├── fast_lib_dynamic_a2c_disabled_preprocess_sample_mask
├── fast_lib_dynamic_a2c_disabled_sample_mask
├── fast_lib_dynamic_a2c_enabled
├── fast_lib_dynamic_a2c_enabled_ies
├── fast_lib_dynamic_a2c_enabled_ies_preprocess
├── fast_lib_dynamic_a2c_enabled_ies_preprocess_sample_mask
├── fast_lib_dynamic_a2c_enabled_ies_sample_mask
├── fast_lib_dynamic_a2c_enabled_preprocess
├── fast_lib_dynamic_a2c_enabled_preprocess_sample_mask
├── fast_lib_dynamic_a2c_enabled_sample_mask
├── fast_lib_dynamic_fsr_sample_shading_first
├── fast_lib_dynamic_fsr_sample_shading_first_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_first_ies
├── fast_lib_dynamic_fsr_sample_shading_first_ies_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_first_ies_multisample
├── fast_lib_dynamic_fsr_sample_shading_first_ies_multisample_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_first_ies_preprocess
├── fast_lib_dynamic_fsr_sample_shading_first_ies_preprocess_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_first_ies_preprocess_multisample
├── fast_lib_dynamic_fsr_sample_shading_first_ies_preprocess_multisample_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_first_multisample
├── fast_lib_dynamic_fsr_sample_shading_first_multisample_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_first_preprocess
├── fast_lib_dynamic_fsr_sample_shading_first_preprocess_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_first_preprocess_multisample
├── fast_lib_dynamic_fsr_sample_shading_first_preprocess_multisample_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_second
├── fast_lib_dynamic_fsr_sample_shading_second_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_second_ies
├── fast_lib_dynamic_fsr_sample_shading_second_ies_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_second_ies_multisample
├── fast_lib_dynamic_fsr_sample_shading_second_ies_multisample_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_second_ies_preprocess
├── fast_lib_dynamic_fsr_sample_shading_second_ies_preprocess_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_second_ies_preprocess_multisample
├── fast_lib_dynamic_fsr_sample_shading_second_ies_preprocess_multisample_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_second_multisample
├── fast_lib_dynamic_fsr_sample_shading_second_multisample_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_second_preprocess
├── fast_lib_dynamic_fsr_sample_shading_second_preprocess_dynamic_sample_count
├── fast_lib_dynamic_fsr_sample_shading_second_preprocess_multisample
├── fast_lib_dynamic_fsr_sample_shading_second_preprocess_multisample_dynamic_sample_count
├── ies_add
├── ies_add_shader_objects
├── ies_increase_vtx_bindings_fast_lib
├── ies_increase_vtx_bindings_fast_lib_indirect_vtx_binds
├── ies_increase_vtx_bindings_fast_lib_indirect_vtx_binds_with_holes
├── ies_increase_vtx_bindings_fast_lib_with_holes
├── ies_increase_vtx_bindings_monolithic
├── ies_increase_vtx_bindings_monolithic_indirect_vtx_binds
├── ies_increase_vtx_bindings_monolithic_indirect_vtx_binds_with_holes
├── ies_increase_vtx_bindings_monolithic_with_holes
├── ies_increase_vtx_bindings_optimized_lib
├── ies_increase_vtx_bindings_optimized_lib_indirect_vtx_binds
├── ies_increase_vtx_bindings_optimized_lib_indirect_vtx_binds_with_holes
├── ies_increase_vtx_bindings_optimized_lib_with_holes
├── ies_increase_vtx_bindings_unlinked_spirv
├── ies_increase_vtx_bindings_unlinked_spirv_indirect_vtx_binds
├── ies_increase_vtx_bindings_unlinked_spirv_indirect_vtx_binds_with_holes
├── ies_increase_vtx_bindings_unlinked_spirv_with_holes
├── ies_replace
├── ies_replace_shader_objects
├── indexed_draws_with_draw_index_base_instance
├── indexed_draws_with_draw_index_base_instance_count
├── interface_matching
├── interface_matching_shader_objects
├── mix_normal_dgc
├── mix_normal_dgc_mesh
├── mix_normal_dgc_mesh_preprocess
├── mix_normal_dgc_mesh_preprocess_with_ies
├── mix_normal_dgc_mesh_with_ies
├── mix_normal_dgc_preprocess
├── mix_normal_dgc_preprocess_with_ies
├── mix_normal_dgc_preprocess_with_ies_with_vbo_token
├── mix_normal_dgc_preprocess_with_vbo_token
├── mix_normal_dgc_shader_objects
├── mix_normal_dgc_shader_objects_mesh
├── mix_normal_dgc_shader_objects_mesh_preprocess
├── mix_normal_dgc_shader_objects_mesh_preprocess_with_ies
├── mix_normal_dgc_shader_objects_mesh_with_ies
├── mix_normal_dgc_shader_objects_preprocess
├── mix_normal_dgc_shader_objects_preprocess_with_ies
├── mix_normal_dgc_shader_objects_preprocess_with_ies_with_vbo_token
├── mix_normal_dgc_shader_objects_preprocess_with_vbo_token
├── mix_normal_dgc_shader_objects_with_ies
├── mix_normal_dgc_shader_objects_with_ies_with_vbo_token
├── mix_normal_dgc_shader_objects_with_vbo_token
├── mix_normal_dgc_with_ies
├── mix_normal_dgc_with_ies_with_vbo_token
├── mix_normal_dgc_with_vbo_token
├── monolithic_dynamic_a2c_disabled
├── monolithic_dynamic_a2c_disabled_ies
├── monolithic_dynamic_a2c_disabled_ies_preprocess
├── monolithic_dynamic_a2c_disabled_ies_preprocess_sample_mask
├── monolithic_dynamic_a2c_disabled_ies_sample_mask
├── monolithic_dynamic_a2c_disabled_preprocess
├── monolithic_dynamic_a2c_disabled_preprocess_sample_mask
├── monolithic_dynamic_a2c_disabled_sample_mask
├── monolithic_dynamic_a2c_enabled
├── monolithic_dynamic_a2c_enabled_ies
├── monolithic_dynamic_a2c_enabled_ies_preprocess
├── monolithic_dynamic_a2c_enabled_ies_preprocess_sample_mask
├── monolithic_dynamic_a2c_enabled_ies_sample_mask
├── monolithic_dynamic_a2c_enabled_preprocess
├── monolithic_dynamic_a2c_enabled_preprocess_sample_mask
├── monolithic_dynamic_a2c_enabled_sample_mask
├── monolithic_dynamic_fsr_sample_shading_first
├── monolithic_dynamic_fsr_sample_shading_first_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_first_ies
├── monolithic_dynamic_fsr_sample_shading_first_ies_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_first_ies_multisample
├── monolithic_dynamic_fsr_sample_shading_first_ies_multisample_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_first_ies_preprocess
├── monolithic_dynamic_fsr_sample_shading_first_ies_preprocess_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_first_ies_preprocess_multisample
├── monolithic_dynamic_fsr_sample_shading_first_ies_preprocess_multisample_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_first_multisample
├── monolithic_dynamic_fsr_sample_shading_first_multisample_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_first_preprocess
├── monolithic_dynamic_fsr_sample_shading_first_preprocess_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_first_preprocess_multisample
├── monolithic_dynamic_fsr_sample_shading_first_preprocess_multisample_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_second
├── monolithic_dynamic_fsr_sample_shading_second_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_second_ies
├── monolithic_dynamic_fsr_sample_shading_second_ies_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_second_ies_multisample
├── monolithic_dynamic_fsr_sample_shading_second_ies_multisample_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_second_ies_preprocess
├── monolithic_dynamic_fsr_sample_shading_second_ies_preprocess_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_second_ies_preprocess_multisample
├── monolithic_dynamic_fsr_sample_shading_second_ies_preprocess_multisample_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_second_multisample
├── monolithic_dynamic_fsr_sample_shading_second_multisample_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_second_preprocess
├── monolithic_dynamic_fsr_sample_shading_second_preprocess_dynamic_sample_count
├── monolithic_dynamic_fsr_sample_shading_second_preprocess_multisample
├── monolithic_dynamic_fsr_sample_shading_second_preprocess_multisample_dynamic_sample_count
├── optimized_lib_dynamic_a2c_disabled
├── optimized_lib_dynamic_a2c_disabled_ies
├── optimized_lib_dynamic_a2c_disabled_ies_preprocess
├── optimized_lib_dynamic_a2c_disabled_ies_preprocess_sample_mask
├── optimized_lib_dynamic_a2c_disabled_ies_sample_mask
├── optimized_lib_dynamic_a2c_disabled_preprocess
├── optimized_lib_dynamic_a2c_disabled_preprocess_sample_mask
├── optimized_lib_dynamic_a2c_disabled_sample_mask
├── optimized_lib_dynamic_a2c_enabled
├── optimized_lib_dynamic_a2c_enabled_ies
├── optimized_lib_dynamic_a2c_enabled_ies_preprocess
├── optimized_lib_dynamic_a2c_enabled_ies_preprocess_sample_mask
├── optimized_lib_dynamic_a2c_enabled_ies_sample_mask
├── optimized_lib_dynamic_a2c_enabled_preprocess
├── optimized_lib_dynamic_a2c_enabled_preprocess_sample_mask
├── optimized_lib_dynamic_a2c_enabled_sample_mask
├── optimized_lib_dynamic_fsr_sample_shading_first
├── optimized_lib_dynamic_fsr_sample_shading_first_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_first_ies
├── optimized_lib_dynamic_fsr_sample_shading_first_ies_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_first_ies_multisample
├── optimized_lib_dynamic_fsr_sample_shading_first_ies_multisample_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_first_ies_preprocess
├── optimized_lib_dynamic_fsr_sample_shading_first_ies_preprocess_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_first_ies_preprocess_multisample
├── optimized_lib_dynamic_fsr_sample_shading_first_ies_preprocess_multisample_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_first_multisample
├── optimized_lib_dynamic_fsr_sample_shading_first_multisample_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_first_preprocess
├── optimized_lib_dynamic_fsr_sample_shading_first_preprocess_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_first_preprocess_multisample
├── optimized_lib_dynamic_fsr_sample_shading_first_preprocess_multisample_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_second
├── optimized_lib_dynamic_fsr_sample_shading_second_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_second_ies
├── optimized_lib_dynamic_fsr_sample_shading_second_ies_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_second_ies_multisample
├── optimized_lib_dynamic_fsr_sample_shading_second_ies_multisample_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_second_ies_preprocess
├── optimized_lib_dynamic_fsr_sample_shading_second_ies_preprocess_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_second_ies_preprocess_multisample
├── optimized_lib_dynamic_fsr_sample_shading_second_ies_preprocess_multisample_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_second_multisample
├── optimized_lib_dynamic_fsr_sample_shading_second_multisample_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_second_preprocess
├── optimized_lib_dynamic_fsr_sample_shading_second_preprocess_dynamic_sample_count
├── optimized_lib_dynamic_fsr_sample_shading_second_preprocess_multisample
├── optimized_lib_dynamic_fsr_sample_shading_second_preprocess_multisample_dynamic_sample_count
├── ray_query
├── ray_query_ies
├── rebind_normal_state
├── rebind_normal_state_with_execution_set
├── reuse_dgc_for_normal_fast_lib_order_dgc_normal
├── reuse_dgc_for_normal_fast_lib_order_dgc_normal_execution_set
├── reuse_dgc_for_normal_fast_lib_order_normal_dgc
├── reuse_dgc_for_normal_fast_lib_order_normal_dgc_execution_set
├── reuse_dgc_for_normal_monolithic_order_dgc_normal
├── reuse_dgc_for_normal_monolithic_order_dgc_normal_execution_set
├── reuse_dgc_for_normal_monolithic_order_normal_dgc
├── reuse_dgc_for_normal_monolithic_order_normal_dgc_execution_set
├── reuse_dgc_for_normal_optimized_lib_order_dgc_normal
├── reuse_dgc_for_normal_optimized_lib_order_dgc_normal_execution_set
├── reuse_dgc_for_normal_optimized_lib_order_normal_dgc
├── reuse_dgc_for_normal_optimized_lib_order_normal_dgc_execution_set
├── reuse_dgc_for_normal_unlinked_spirv_order_dgc_normal
├── reuse_dgc_for_normal_unlinked_spirv_order_dgc_normal_execution_set
├── reuse_dgc_for_normal_unlinked_spirv_order_normal_dgc
├── reuse_dgc_for_normal_unlinked_spirv_order_normal_dgc_execution_set
├── robust_vbo
├── robust_vbo_preprocess
├── robust_vbo_shader_objects
├── robust_vbo_shader_objects_preprocess
├── sample_id_state_0_fast_lib
├── sample_id_state_0_monolithic
├── sample_id_state_0_optimized_lib
├── sample_id_state_0_preprocess_fast_lib
├── sample_id_state_0_preprocess_monolithic
├── sample_id_state_0_preprocess_optimized_lib
├── sample_id_state_0_preprocess_unlinked_spirv
├── sample_id_state_0_unlinked_spirv
├── sample_id_state_1_fast_lib
├── sample_id_state_1_monolithic
├── sample_id_state_1_optimized_lib
├── sample_id_state_1_preprocess_fast_lib
├── sample_id_state_1_preprocess_monolithic
├── sample_id_state_1_preprocess_optimized_lib
├── sample_id_state_1_preprocess_unlinked_spirv
├── sample_id_state_1_unlinked_spirv
├── sequence_index_token
├── sequence_index_token_descriptor_heap
├── sparse_vbo_token
├── tg_push_constants_geom
├── tg_push_constants_geom_descriptor_heap
├── tg_push_constants_geom_partial
├── tg_push_constants_geom_partial_descriptor_heap
├── tg_push_constants_tess
├── tg_push_constants_tess_descriptor_heap
├── tg_push_constants_tess_partial
├── tg_push_constants_tess_partial_descriptor_heap
├── vbo_update_0001
├── vbo_update_0010
├── vbo_update_0100
├── vbo_update_1000
└── vbo_update_1111
```

The root is registered by `createDGCGraphicsMiscTestsExt`; the direct children are built from explicit loops and fixed cases rather than inferred from class names. The page groups those children by the behavior dimensions that generate their names.

## Parameter Dimensions and Observed Values

The registration matrix uses these exact dimensions:

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Pipeline construction | `monolithic`, `fast_lib`, `optimized_lib`, `unlinked_spirv` | Selects the pipeline or shader-object construction path used by dynamic vertex input, draw reuse, sample-ID state, alpha-to-coverage, and fragment shading rate cases. | [`constructionTypes`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8470-L8479) |
| DGC execution mode | base case, `_preprocess`, `_with_ies`, `_execution_set` | Separates direct execution, preprocessing, and execution-set state selection. | [`createDGCGraphicsMiscTestsExt`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8397-L8413) |
| Shader and mesh path | no suffix, `_shader_objects`, `_mesh` | Chooses pipeline shaders versus shader objects and, where enabled, mesh graphics stages. | [`NormalDGCMixCase` registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8397-L8413) |
| Vertex input variation | `vbo_update_0001`, `vbo_update_0010`, `vbo_update_0100`, `vbo_update_1000`, `vbo_update_1111`; `with_holes`; `indirect_vtx_binds` | Changes which vertex bindings are updated or selected, including unused binding slots. | [`VBOUpdateInstance::Params`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L64-L115), [`IESInputBindings` registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8481-L8493) |
| Fragment-state variation | `_dynamic_a2c_enabled` or `_dynamic_a2c_disabled`, `_sample_mask`, `_dynamic_fsr_sample_shading_first` or `_second`, `_multisample`, `_dynamic_sample_count` | Changes alpha-to-coverage, sample-mask, sample-shading order, multisampling, and dynamic sample-count state. | [`DynamicA2C` registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8591-L8611), [`DynamicFSR` registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8614-L8642) |
| Interface operation | `interface_matching`, `ies_replace`, `ies_add`, each with optional `_shader_objects` | Checks a single execution, replacement, or addition of interface state. | [`MultiIface` registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8425-L8444) |
| Specialized behavior | `sequence_index_token`, `ray_query`, `early_fragment_tests`, `tg_push_constants_tess`, `tg_push_constants_geom`, `indexed_draws_with_draw_index_base_instance`, `sparse_vbo_token`, and their exact suffix variants | Selects one token or graphics-stage behavior that does not fit the larger combinatorial loops. | [`specialized registrations`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8446-L8532) |

The suffix order is part of the registered identifier. For example, dynamic alpha-to-coverage appends construction type, enabled state, execution-set marker, preprocess marker, and sample-mask marker in the order emitted by the source. The registration loop skips `mesh && useVBOToken`, because the source calls that combination unsupported by the test shape rather than registering it.

## Behavior Parameters

The primary behavioral axis is the registered test family. Its values select the property being checked; suffixes then vary how DGC supplies the relevant state.

### Vertex input updates and bindings

`vbo_update_*` changes one or all of the four bindings represented by `POSITION`, `RED_COLOR`, `GREEN_COLOR`, and `BLUE_COLOR`. The shader passes those attributes through to a color result. The `ies_increase_vtx_bindings_*` families vary construction type, indirect vertex-binding commands, and holes in the binding sequence.

### Mixing normal and generated draws

`mix_normal_dgc*` and `reuse_dgc_for_normal_*` place ordinary and generated draws in different orders. Their suffixes select preprocessing, execution sets, mesh rendering, shader objects, and the VBO token. The result checks whether state from one path is correctly established before the next draw.

### Robust and dynamic vertex input

`robust_vbo*` exercises a null or sparse vertex-buffer path. `dynamic_vertex_input_*` changes vertex-input state through each supported construction type, with or without an execution set. These cases check the generated state that the vertex stage consumes, not only the draw call itself.

### Interface execution-set operations

`interface_matching*` checks interface matching for one execution. `ies_replace*` replaces interface state, while `ies_add*` adds it. The optional `_shader_objects` cases use the corresponding shader-object path.

### Tokens and stage behavior

`sequence_index_token*` checks sequence-index use, including the descriptor-heap variant. `ray_query` and `ray_query_ies` execute a ray query with or without an execution set. `early_fragment_tests` and `early_fragment_tests_preprocess` check early-fragment-tests behavior across direct and preprocessed execution.

The `tg_push_constants_tess*` and `tg_push_constants_geom*` families exercise tessellation and geometry shader push constants. `_partial` changes the partial push-constant case, and `_descriptor_heap` selects the descriptor-heap resource path. `indexed_draws_with_draw_index_base_instance` and its `_count` variant check indexed draw values with the draw-index, base-instance, and optional count token path. `sparse_vbo_token` checks sparse vertex-buffer addressing.

### Sample and fragment shading state

`sample_id_state_0_*` and `sample_id_state_1_*` vary whether the alternating generated sequences start with the fragment shader that does not use or does use `gl_SampleID`, respectively; `_preprocess` varies explicit preprocessing. Dynamic alpha-to-coverage cases vary enabled versus disabled state, execution sets, preprocessing, and sample masks. Dynamic fragment shading rate cases vary multisampling, whether sample shading is set first or second, execution sets, preprocessing, and dynamic sample count.

## Shader Analysis

The source generates representative vertex and fragment programs for the vertex-input cases. The walkthrough below follows the `vbo_update_1000` path, where only the position binding varies. Other families use different stage programs, so their shader-specific details remain in the source appendix.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path: `dEQP-VK.dgc.ext.graphics.misc.vbo_update_1000`

```text
dEQP-VK.dgc.ext.graphics.misc.vbo_update_1000
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `vbo_update_1000` | Varies the `POSITION` binding while the three color bindings retain their default variation. |

#### Purpose

The vertex shader copies its position and three color attributes to the fragment shader. The fragment shader writes the three attributes as RGB values. The case therefore exposes a vertex-input update through the rendered color.

#### Structural Design

| Stage | Operation | Observable effect |
|---|---|---|
| Vertex | Read `inPos`, `inRed`, `inGreen`, and `inBlue`; copy them to outputs | Carries vertex-buffer data into the fragment stage. |
| Fragment | Write `vec4(inRed, inGreen, inBlue, 1.0)` | Produces the color image checked by the host. |

#### Shader Code

##### Vertex Shader

```glsl
#version 460

layout(location=0) in vec4 inPos;
layout(location=1) in float inRed;
layout(location=2) in float inGreen;
layout(location=3) in float inBlue;

layout(location=0) out float outRed;
layout(location=1) out float outGreen;
layout(location=2) out float outBlue;

void main(void) {
    gl_Position = inPos;
    outRed = inRed;
    outGreen = inGreen;
    outBlue = inBlue;
}
```

##### Fragment Shader

```glsl
#version 460

layout(location=0) in float inRed;
layout(location=1) in float inGreen;
layout(location=2) in float inBlue;

layout(location=0) out vec4 outColor;

void main(void) {
    outColor = vec4(inRed, inGreen, inBlue, 1.0);
}
```

#### Additional Info

- The source builds these programs in [`VBOUpdateCase::initPrograms`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L162-L196).
- The vertex stage supplies the interpolated color components consumed by the fragment stage; both stages are shown because that interface is the observed path.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| `vbo_update_*` | The shader interface stays fixed while the generated vertex-input binding variation changes which buffer state supplies the attributes. | [`VBOUpdateInstance::Params`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L64-L115) |

#### SPIR-V

##### Vertex SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 32
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %inPos %outRed %inRed %outGreen %inGreen %outBlue %inBlue
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %inPos "inPos"
               OpName %outRed "outRed"
               OpName %inRed "inRed"
               OpName %outGreen "outGreen"
               OpName %inGreen "inGreen"
               OpName %outBlue "outBlue"
               OpName %inBlue "inBlue"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %inPos Location 0
               OpDecorate %outRed Location 0
               OpDecorate %inRed Location 1
               OpDecorate %outGreen Location 1
               OpDecorate %inGreen Location 2
               OpDecorate %outBlue Location 2
               OpDecorate %inBlue Location 3
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
      %inPos = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Output_float = OpTypePointer Output %float
     %outRed = OpVariable %_ptr_Output_float Output
%_ptr_Input_float = OpTypePointer Input %float
      %inRed = OpVariable %_ptr_Input_float Input
   %outGreen = OpVariable %_ptr_Output_float Output
    %inGreen = OpVariable %_ptr_Input_float Input
    %outBlue = OpVariable %_ptr_Output_float Output
     %inBlue = OpVariable %_ptr_Input_float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpLoad %v4float %inPos
         %20 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %20 %18
         %25 = OpLoad %float %inRed
               OpStore %outRed %25
         %28 = OpLoad %float %inGreen
               OpStore %outGreen %28
         %31 = OpLoad %float %inBlue
               OpStore %outBlue %31
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment SPIR-V

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
; Bound: 19
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor %inRed %inGreen %inBlue
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpName %main "main"
               OpName %outColor "outColor"
               OpName %inRed "inRed"
               OpName %inGreen "inGreen"
               OpName %inBlue "inBlue"
               OpDecorate %outColor Location 0
               OpDecorate %inRed Location 0
               OpDecorate %inGreen Location 1
               OpDecorate %inBlue Location 2
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_float = OpTypePointer Input %float
      %inRed = OpVariable %_ptr_Input_float Input
    %inGreen = OpVariable %_ptr_Input_float Input
     %inBlue = OpVariable %_ptr_Input_float Input
    %float_1 = OpConstant %float 1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpLoad %float %inRed
         %14 = OpLoad %float %inGreen
         %16 = OpLoad %float %inBlue
         %18 = OpCompositeConstruct %v4float %12 %14 %16 %float_1
               OpStore %outColor %18
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each case first checks DGC support for the shader stages it binds. It then adds feature checks for the selected variant, such as `VK_EXT_shader_object`, `VK_EXT_mesh_shader`, `VK_EXT_vertex_input_dynamic_state`, or descriptor-heap support.
- The instance creates the framebuffer or storage target, vertex and indirect buffers, descriptors, and any execution-set state required by its parameters. Preprocess cases execute the preprocessing step before the generated commands.
- The command sequence binds the selected construction path and executes a draw, indexed draw, mesh draw, or ray-query workload. Some cases repeat the operation with normal Vulkan commands to test state reuse and ordering.
- The instance copies or maps the result for the host. Most families use `tcu::floatThresholdCompare`; integer results use `tcu::intThresholdCompare`; depth and stencil use `tcu::dsThresholdCompare`. The expanded color check uses a threshold of `0.005f`.
- A comparison failure returns `tcu::TestStatus::fail` or calls `TCU_FAIL` after logging the mismatching result. A passing comparison returns `tcu::TestStatus::pass("Pass")`.
- Depending on the family, the check covers a color buffer, depth buffer, storage image, framebuffer and storage result together, a multisample color buffer, or an expanded color buffer. The host does not treat missing optional features as a functional failure. `checkSupport` prunes those cases before execution.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Vertex input updates and bindings | Generated vertex-input state, binding offsets or strides, execution-set selection, or vertex fetch behavior produced a different attribute result. |
| Mixing normal and generated draws | DGC and ordinary command state was not preserved or rebound correctly across the selected order, preprocessing, mesh, shader-object, or VBO-token variant. |
| Robust and dynamic vertex input | The null, sparse, or dynamically described vertex input did not produce the reference vertex data. |
| Interface execution-set operations | Interface matching, replacement, or addition selected incompatible or stale shader state. |
| Tokens and stage behavior | The sequence index, ray-query, early-fragment-tests, push-constant, indexed-draw, or sparse-VBO path produced an incorrect observable result. |
| Sample and fragment shading state | Alpha-to-coverage, sample mask, sample ID, sample shading order, or fragment shading rate state differed from the requested variant. |

### Cause Analysis

#### Generated state or vertex fetch

**Possible failure symptoms:** The color or expanded color comparison differs from its reference, or a specialized vertex-input case reports an unexpected result.

**Possible implementation causes:** The source sets binding and dynamic-state parameters explicitly, so the symptom can come from incorrect generated-state interpretation, vertex-buffer addressing, or state selection. The exact implementation cause requires investigation of the failing variant and logged comparison.

#### Pipeline, shader-object, and interface state

**Possible failure symptoms:** A normal/DGC reuse case, interface case, or construction-type variant produces the wrong framebuffer or storage result.

**Possible implementation causes:** The implementation may retain the wrong pipeline, shader object, execution-set entry, interface operation, or dynamic state between commands. The test source establishes the expected state transitions, but a failure does not identify one layer without the failing case and log.

#### Fragment, depth, and specialized stage behavior

**Possible failure symptoms:** Color, depth, stencil, storage-image, multisample, or expanded-buffer comparison fails in a case that selects a fragment or shader-stage feature.

**Possible implementation causes:** The selected stage state, push constant value, ray-query result, sample operation, or draw-index value may not reach the shader or fixed-function test in the form requested. Source-level and Vulkan-spec investigation is needed to distinguish command encoding, shader compilation, and device behavior.

## Case Pruning

### Requirement-based pruning

`checkSupport` requires the DGC extension and the stage capabilities needed by each case. It additionally gates variants on the exact identifiers used by the source: `VK_EXT_extended_dynamic_state`, `VK_EXT_shader_object`, `VK_EXT_mesh_shader`, `VK_EXT_DESCRIPTOR_HEAP_EXTENSION_NAME`, `VK_KHR_acceleration_structure`, `VK_KHR_ray_query`, `VK_EXT_vertex_input_dynamic_state`, `VK_KHR_fragment_shading_rate`, and `VK_EXT_extended_dynamic_state3`. Unsupported features, shader stages, descriptor-heap paths, mesh paths, ray-query paths, and dynamic sample-count paths are skipped by support checks, not reported as failed results.

### Design-based pruning

The registration loops intentionally omit `mesh && useVBOToken`, because the source marks that combination as invalid for the mix-normal-DGC test. Shader-object construction types are excluded from the dynamic alpha-to-coverage and dynamic fragment-shading-rate loops because the source notes that their state is already dynamic. Other suffixes represent fixed boolean choices, so the matrix registers only the combinations emitted by the loops, not every textual permutation.

## Key Takeaways

- The page covers a matrix of DGC graphics behaviors, but each registered child selects one concrete property and one concrete state-delivery path.
- The suffixes encode execution mode, construction type, shader path, resource path, or fragment-state choice. They are part of the test identity.
- Host-side comparisons convert shader and graphics-stage observations into the pass/fail result. A mismatch points to the selected behavior path, but the result log is needed to localize the cause.
- Support checks and intentional loop exclusions have different meanings. One removes an unavailable case; the other keeps an invalid or redundant design combination out of the matrix.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `VBOUpdateInstance::Params` | [`binding variation encoding`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L64-L115) | Defines the four-binding bit-string names. |
| `createDGCGraphicsMiscTestsExt` | [`registration and matrix loops`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8375-L8645) | Registers every direct test family and suffix combination. |
| Support checks | [`feature gates`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L153-L160) | Shows the common DGC and dynamic-stride requirements. |
| Ray-query support | [`ray-query feature gates`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L3189-L3197) | Defines the acceleration-structure and ray-query requirements. |
| Vertex-input support | [`dynamic vertex-input feature gates`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L5232-L5249) | Distinguishes shader-object and dynamic vertex-input support. |
| Result comparisons | [`family result checks`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L204-512) | Shows reference construction and threshold comparison for a representative family. |
| Fragment-state result checks | [`framebuffer and storage checks`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L7030-L7059) | Shows paired result comparisons and failure handling. |
| Expanded result check | [`expanded color comparison`](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8362-L8370) | Shows the `0.005f` threshold and final failure path. |
