# vktDGCGraphicsMiscTestsExt

## Overview

EXT graphics miscellaneous tests cover vertex-input, mixed DGC/normal draws, indirect execution sets, ray query, early fragment tests, tessellation/geometry push constants, sparse VBOs, dynamic alpha-to-coverage, and fragment shading rate scenarios.

## Role of File

This is an implementation file for `dgc.ext.graphics.misc`. The source is [vktDGCGraphicsMiscTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L1). Its registration evidence starts at [vktDGCGraphicsMiscTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8379).

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

## Test Families

The direct registered children below are derived from the mustpass `dgc` paths and the file registration code at [vktDGCGraphicsMiscTestsExt registration](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8379).

- `dynamic_vertex_input_fast_lib` — registered direct child under this Level-3 root.
- `dynamic_vertex_input_fast_lib_execution_set` — registered direct child under this Level-3 root.
- `dynamic_vertex_input_monolithic` — registered direct child under this Level-3 root.
- `dynamic_vertex_input_monolithic_execution_set` — registered direct child under this Level-3 root.
- `dynamic_vertex_input_optimized_lib` — registered direct child under this Level-3 root.
- `dynamic_vertex_input_optimized_lib_execution_set` — registered direct child under this Level-3 root.
- `dynamic_vertex_input_unlinked_spirv` — registered direct child under this Level-3 root.
- `dynamic_vertex_input_unlinked_spirv_execution_set` — registered direct child under this Level-3 root.
- `early_fragment_tests` — registered direct child under this Level-3 root.
- `early_fragment_tests_preprocess` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_disabled` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_disabled_ies` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_disabled_ies_preprocess` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_disabled_ies_preprocess_sample_mask` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_disabled_ies_sample_mask` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_disabled_preprocess` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_disabled_preprocess_sample_mask` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_disabled_sample_mask` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_enabled` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_enabled_ies` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_enabled_ies_preprocess` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_enabled_ies_preprocess_sample_mask` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_enabled_ies_sample_mask` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_enabled_preprocess` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_enabled_preprocess_sample_mask` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_a2c_enabled_sample_mask` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_ies` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_ies_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_ies_multisample` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_ies_multisample_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_ies_preprocess` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_ies_preprocess_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_ies_preprocess_multisample` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_ies_preprocess_multisample_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_multisample` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_multisample_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_preprocess` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_preprocess_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_preprocess_multisample` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_first_preprocess_multisample_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_ies` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_ies_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_ies_multisample` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_ies_multisample_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_ies_preprocess` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_ies_preprocess_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_ies_preprocess_multisample` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_ies_preprocess_multisample_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_multisample` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_multisample_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_preprocess` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_preprocess_dynamic_sample_count` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_preprocess_multisample` — registered direct child under this Level-3 root.
- `fast_lib_dynamic_fsr_sample_shading_second_preprocess_multisample_dynamic_sample_count` — registered direct child under this Level-3 root.
- `ies_add` — registered direct child under this Level-3 root.
- `ies_add_shader_objects` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_fast_lib` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_fast_lib_indirect_vtx_binds` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_fast_lib_indirect_vtx_binds_with_holes` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_fast_lib_with_holes` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_monolithic` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_monolithic_indirect_vtx_binds` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_monolithic_indirect_vtx_binds_with_holes` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_monolithic_with_holes` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_optimized_lib` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_optimized_lib_indirect_vtx_binds` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_optimized_lib_indirect_vtx_binds_with_holes` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_optimized_lib_with_holes` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_unlinked_spirv` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_unlinked_spirv_indirect_vtx_binds` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_unlinked_spirv_indirect_vtx_binds_with_holes` — registered direct child under this Level-3 root.
- `ies_increase_vtx_bindings_unlinked_spirv_with_holes` — registered direct child under this Level-3 root.
- `ies_replace` — registered direct child under this Level-3 root.
- `ies_replace_shader_objects` — registered direct child under this Level-3 root.
- `indexed_draws_with_draw_index_base_instance` — registered direct child under this Level-3 root.
- `indexed_draws_with_draw_index_base_instance_count` — registered direct child under this Level-3 root.
- Additional direct children: 178 more names are listed in the hierarchy tree above.

## Parameter Dimensions

The registration loop or case construction near [vktDGCGraphicsMiscTestsExt case generation](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8389) defines the observed parameter combinations for these tests. The documented direct child names above are not inferred from factory symbols; they are visible in registered paths and registration/group construction.

## Support and Feature Requirements

- [context.requireDeviceFunctionality("VK_EXT_extended_dynamic_state");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L159)
- [context.requireDeviceFunctionality("VK_EXT_shader_object");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L592)
- [context.requireDeviceFunctionality("VK_EXT_mesh_shader");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L595)
- [context.requireDeviceFunctionality("VK_EXT_shader_object");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L1423)
- [context.requireDeviceFunctionality("VK_EXT_shader_object");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L1930)
- [context.requireDeviceFunctionality(VK_EXT_DESCRIPTOR_HEAP_EXTENSION_NAME);](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L2976)
- [context.requireDeviceFunctionality("VK_KHR_acceleration_structure");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L3195)
- [context.requireDeviceFunctionality("VK_KHR_ray_query");](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L3196)

## Verification Methods

Verification uses color, depth, storage image, and expanded color-buffer comparisons depending on the family. Evidence is in the implementation around [vktDGCGraphicsMiscTestsExt verification](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsMiscTestsExt.cpp#L8370).

## Test Principles

- Construct generated-command state from explicit parameters in the file.
- Execute through the registered DGC path and verify the externally visible results described in the verification section for this file.
- Treat optional features as support gates rather than expected failures.

## Notes and Uncertainties

- This page summarizes evidence inspected in the DGC source directory and the `dgc.txt` mustpass list.
- The official API test plan does not provide DGC-specific detail in the inspected prerequisite section, so implementation code is the primary evidence source.
