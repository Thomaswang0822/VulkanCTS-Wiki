# vktTessellationMiscDrawTests.cpp

## Overview

[`vktTessellationMiscDrawTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1) registers [`misc_draw`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1859-L2080), a broad draw-result subgroup.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationMiscDrawTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1)

## Registration Hierarchy

The documented root is [`tessellation.misc_draw`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1).

```text
tessellation.misc_draw
├── fill_cover_quads_equal_spacing_draw
├── fill_cover_quads_equal_spacing_draw_indirect
├── fill_cover_quads_fractional_even_spacing_draw
├── fill_cover_quads_fractional_even_spacing_draw_indirect
├── fill_cover_quads_fractional_odd_spacing_draw
├── fill_cover_quads_fractional_odd_spacing_draw_indirect
├── fill_cover_triangles_equal_spacing_draw
├── fill_cover_triangles_equal_spacing_draw_indirect
├── fill_cover_triangles_fractional_even_spacing_draw
├── fill_cover_triangles_fractional_even_spacing_draw_indirect
├── fill_cover_triangles_fractional_odd_spacing_draw
├── fill_cover_triangles_fractional_odd_spacing_draw_indirect
├── fill_overlap_quads_equal_spacing_draw
├── fill_overlap_quads_equal_spacing_draw_indirect
├── fill_overlap_quads_fractional_even_spacing_draw
├── fill_overlap_quads_fractional_even_spacing_draw_indirect
├── fill_overlap_quads_fractional_odd_spacing_draw
├── fill_overlap_quads_fractional_odd_spacing_draw_indirect
├── fill_overlap_triangles_equal_spacing_draw
├── fill_overlap_triangles_equal_spacing_draw_indirect
├── fill_overlap_triangles_fractional_even_spacing_draw
├── fill_overlap_triangles_fractional_even_spacing_draw_indirect
├── fill_overlap_triangles_fractional_odd_spacing_draw
├── fill_overlap_triangles_fractional_odd_spacing_draw_indirect
├── isolines_equal_spacing_draw
├── isolines_equal_spacing_draw_indirect
├── isolines_fractional_even_spacing_draw
├── isolines_fractional_even_spacing_draw_indirect
├── isolines_fractional_odd_spacing_draw
├── isolines_fractional_odd_spacing_draw_indirect
├── quads_instances
├── quads_no_patches
├── switch_domain_origin_lower_left_to_upper_left
├── switch_domain_origin_lower_left_to_upper_left_fast_lib
├── switch_domain_origin_lower_left_to_upper_left_shader_objects
├── switch_domain_origin_lower_left_to_upper_left_with_geom_shader
├── switch_domain_origin_lower_left_to_upper_left_with_geom_shader_fast_lib
├── switch_domain_origin_lower_left_to_upper_left_with_geom_shader_shader_objects
├── switch_domain_origin_upper_left_to_lower_left
├── switch_domain_origin_upper_left_to_lower_left_fast_lib
├── switch_domain_origin_upper_left_to_lower_left_shader_objects
├── switch_domain_origin_upper_left_to_lower_left_with_geom_shader
├── switch_domain_origin_upper_left_to_lower_left_with_geom_shader_fast_lib
├── switch_domain_origin_upper_left_to_lower_left_with_geom_shader_shader_objects
├── switch_out_vertices_3_to_4
├── switch_out_vertices_3_to_4_fast_lib
├── switch_out_vertices_3_to_4_shader_objects
├── switch_out_vertices_3_to_4_with_geom_shader
├── switch_out_vertices_3_to_4_with_geom_shader_fast_lib
├── switch_out_vertices_3_to_4_with_geom_shader_shader_objects
├── switch_out_vertices_4_to_3
├── switch_out_vertices_4_to_3_fast_lib
├── switch_out_vertices_4_to_3_shader_objects
├── switch_out_vertices_4_to_3_with_geom_shader
├── switch_out_vertices_4_to_3_with_geom_shader_fast_lib
├── switch_out_vertices_4_to_3_with_geom_shader_shader_objects
├── switch_primitive_quads_to_triangles
├── switch_primitive_quads_to_triangles_fast_lib
├── switch_primitive_quads_to_triangles_shader_objects
├── switch_primitive_quads_to_triangles_with_geom_shader
├── switch_primitive_quads_to_triangles_with_geom_shader_fast_lib
├── switch_primitive_quads_to_triangles_with_geom_shader_shader_objects
├── switch_primitive_triangles_to_quads
├── switch_primitive_triangles_to_quads_fast_lib
├── switch_primitive_triangles_to_quads_shader_objects
├── switch_primitive_triangles_to_quads_with_geom_shader
├── switch_primitive_triangles_to_quads_with_geom_shader_fast_lib
├── switch_primitive_triangles_to_quads_with_geom_shader_shader_objects
├── switch_spacing_mode_equal_spacing_to_fractional_even_spacing
├── switch_spacing_mode_equal_spacing_to_fractional_even_spacing_fast_lib
├── switch_spacing_mode_equal_spacing_to_fractional_even_spacing_shader_objects
├── switch_spacing_mode_equal_spacing_to_fractional_even_spacing_with_geom_shader
├── switch_spacing_mode_equal_spacing_to_fractional_even_spacing_with_geom_shader_fast_lib
├── switch_spacing_mode_equal_spacing_to_fractional_even_spacing_with_geom_shader_shader_objects
├── switch_spacing_mode_equal_spacing_to_fractional_odd_spacing
├── switch_spacing_mode_equal_spacing_to_fractional_odd_spacing_fast_lib
├── switch_spacing_mode_equal_spacing_to_fractional_odd_spacing_shader_objects
├── switch_spacing_mode_equal_spacing_to_fractional_odd_spacing_with_geom_shader
├── switch_spacing_mode_equal_spacing_to_fractional_odd_spacing_with_geom_shader_fast_lib
├── switch_spacing_mode_equal_spacing_to_fractional_odd_spacing_with_geom_shader_shader_objects
├── switch_spacing_mode_fractional_even_spacing_to_equal_spacing
├── switch_spacing_mode_fractional_even_spacing_to_equal_spacing_fast_lib
├── switch_spacing_mode_fractional_even_spacing_to_equal_spacing_shader_objects
├── switch_spacing_mode_fractional_even_spacing_to_equal_spacing_with_geom_shader
├── switch_spacing_mode_fractional_even_spacing_to_equal_spacing_with_geom_shader_fast_lib
├── switch_spacing_mode_fractional_even_spacing_to_equal_spacing_with_geom_shader_shader_objects
├── switch_spacing_mode_fractional_even_spacing_to_fractional_odd_spacing
├── switch_spacing_mode_fractional_even_spacing_to_fractional_odd_spacing_fast_lib
├── switch_spacing_mode_fractional_even_spacing_to_fractional_odd_spacing_shader_objects
├── switch_spacing_mode_fractional_even_spacing_to_fractional_odd_spacing_with_geom_shader
├── switch_spacing_mode_fractional_even_spacing_to_fractional_odd_spacing_with_geom_shader_fast_lib
├── switch_spacing_mode_fractional_even_spacing_to_fractional_odd_spacing_with_geom_shader_shader_objects
├── switch_spacing_mode_fractional_odd_spacing_to_equal_spacing
├── switch_spacing_mode_fractional_odd_spacing_to_equal_spacing_fast_lib
├── switch_spacing_mode_fractional_odd_spacing_to_equal_spacing_shader_objects
├── switch_spacing_mode_fractional_odd_spacing_to_equal_spacing_with_geom_shader
├── switch_spacing_mode_fractional_odd_spacing_to_equal_spacing_with_geom_shader_fast_lib
├── switch_spacing_mode_fractional_odd_spacing_to_equal_spacing_with_geom_shader_shader_objects
├── switch_spacing_mode_fractional_odd_spacing_to_fractional_even_spacing
├── switch_spacing_mode_fractional_odd_spacing_to_fractional_even_spacing_fast_lib
├── switch_spacing_mode_fractional_odd_spacing_to_fractional_even_spacing_shader_objects
├── switch_spacing_mode_fractional_odd_spacing_to_fractional_even_spacing_with_geom_shader
├── switch_spacing_mode_fractional_odd_spacing_to_fractional_even_spacing_with_geom_shader_fast_lib
├── switch_spacing_mode_fractional_odd_spacing_to_fractional_even_spacing_with_geom_shader_shader_objects
├── tess_factor_barrier_bug
├── triangles_instances
└── triangles_no_patches
```

## Test Families

### fill_cover_quads_equal_spacing_draw — Misc Draw

Cases include fill/overlap draw and draw-indirect variants, isoline variants, instancing, no-patch behavior, and state-switch combinations visible in [`createMiscDrawTests()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1859-L2080).

## Parameter Dimensions

Parameters include primitive type, spacing mode, draw type, instanced type, domain origin, output vertices, geometry-shader usage, fast-library usage, and shader-object variants.

## Support / Feature Requirements

[`TessStateSwitchCase::checkSupport()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L660-L669) requires tessellation shaders, optionally geometry shaders, and `VK_KHR_maintenance2` for non-default domain origin; instanced draw requires tessellation support at [`TessInstancedDrawTestCase::checkSupport()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1249-L1252).

## Verification Methods

Verification uses [`tcu::fuzzyCompare()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L354-L355), [`tcu::floatThresholdCompare()`](../../../modules/vulkan/tessellation/vktTessellationMiscDrawTests.cpp#L1095-L1096), and reference/result image checks for state switching.

## Test Principles Observed
- Case generation is table- or loop-driven in the registration function.
- Verification is tied to observed rendered, queried, or buffered results.

## Notes / Uncertainties

- This page summarizes behavior observed in inspected tessellation source files; deeper generated cases are described where visible in source loops or arrays.
