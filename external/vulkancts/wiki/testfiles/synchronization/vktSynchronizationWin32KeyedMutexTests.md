# vktSynchronizationWin32KeyedMutexTests

## Overview

Tests synchronization of Vulkan resources shared with Direct3D 11 via Win32 keyed mutex objects. These tests verify that Vulkan can correctly interoperate with DX11 by acquiring and releasing keyed mutex keys on shared memory, ensuring data consistency across API boundaries.

This is a **LEGACY-only** test file (non-SC). It is registered under the `synchronization` (LEGACY) category and is not included in the `synchronization2` category.

## Role of File

Provides the `win32_keyed_mutex` test group, which exercises the `VK_KHR_win32_keyed_mutex` and `VK_KHR_external_memory_win32` extensions. The tests create DX11 resources with keyed mutex, import their memory into Vulkan, write data from Vulkan, synchronize via keyed mutex acquire/release, copy data in DX11, then read back and verify in Vulkan.

## Source Code

- [vktSynchronizationWin32KeyedMutexTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationWin32KeyedMutexTests.cpp)

## Registration Hierarchy

```text
synchronization.win32_keyed_mutex
├── write_blit_image_read_blit_image
├── write_blit_image_read_copy_image
├── write_blit_image_read_copy_image_to_buffer
├── write_blit_image_read_image_compute
├── write_blit_image_read_image_compute_indirect
├── write_blit_image_read_image_fragment
├── write_blit_image_read_image_geometry
├── write_blit_image_read_image_tess_control
├── write_blit_image_read_image_tess_eval
├── write_blit_image_read_image_vertex
├── write_clear_attachments_read_blit_image
├── write_clear_attachments_read_copy_image
├── write_clear_attachments_read_copy_image_to_buffer
├── write_clear_attachments_read_image_compute
├── write_clear_attachments_read_image_compute_indirect
├── write_clear_attachments_read_image_fragment
├── write_clear_attachments_read_image_geometry
├── write_clear_attachments_read_image_tess_control
├── write_clear_attachments_read_image_tess_eval
├── write_clear_attachments_read_image_vertex
├── write_clear_color_image_read_blit_image
├── write_clear_color_image_read_copy_image
├── write_clear_color_image_read_copy_image_to_buffer
├── write_clear_color_image_read_image_compute
├── write_clear_color_image_read_image_compute_indirect
├── write_clear_color_image_read_image_fragment
├── write_clear_color_image_read_image_geometry
├── write_clear_color_image_read_image_tess_control
├── write_clear_color_image_read_image_tess_eval
├── write_clear_color_image_read_image_vertex
├── write_copy_buffer_read_copy_buffer
├── write_copy_buffer_read_copy_buffer_to_image
├── write_copy_buffer_read_ssbo_compute
├── write_copy_buffer_read_ssbo_compute_indirect
├── write_copy_buffer_read_ssbo_fragment
├── write_copy_buffer_read_ssbo_geometry
├── write_copy_buffer_read_ssbo_tess_control
├── write_copy_buffer_read_ssbo_tess_eval
├── write_copy_buffer_read_ssbo_vertex
├── write_copy_buffer_read_ubo_compute
├── write_copy_buffer_read_ubo_compute_indirect
├── write_copy_buffer_read_ubo_fragment
├── write_copy_buffer_read_ubo_geometry
├── write_copy_buffer_read_ubo_tess_control
├── write_copy_buffer_read_ubo_tess_eval
├── write_copy_buffer_read_ubo_texel_compute
├── write_copy_buffer_read_ubo_texel_compute_indirect
├── write_copy_buffer_read_ubo_texel_fragment
├── write_copy_buffer_read_ubo_texel_geometry
├── write_copy_buffer_read_ubo_texel_tess_control
├── write_copy_buffer_read_ubo_texel_tess_eval
├── write_copy_buffer_read_ubo_texel_vertex
├── write_copy_buffer_read_ubo_vertex
├── write_copy_buffer_read_vertex_input
├── write_copy_buffer_to_image_read_blit_image
├── write_copy_buffer_to_image_read_copy_image
├── write_copy_buffer_to_image_read_copy_image_to_buffer
├── write_copy_buffer_to_image_read_image_compute
├── write_copy_buffer_to_image_read_image_compute_indirect
├── write_copy_buffer_to_image_read_image_fragment
├── write_copy_buffer_to_image_read_image_geometry
├── write_copy_buffer_to_image_read_image_tess_control
├── write_copy_buffer_to_image_read_image_tess_eval
├── write_copy_buffer_to_image_read_image_vertex
├── write_copy_image_read_blit_image
├── write_copy_image_read_copy_image
├── write_copy_image_read_copy_image_to_buffer
├── write_copy_image_read_image_compute
├── write_copy_image_read_image_compute_indirect
├── write_copy_image_read_image_fragment
├── write_copy_image_read_image_geometry
├── write_copy_image_read_image_tess_control
├── write_copy_image_read_image_tess_eval
├── write_copy_image_read_image_vertex
├── write_copy_image_to_buffer_read_copy_buffer
├── write_copy_image_to_buffer_read_copy_buffer_to_image
├── write_copy_image_to_buffer_read_ssbo_compute
├── write_copy_image_to_buffer_read_ssbo_compute_indirect
├── write_copy_image_to_buffer_read_ssbo_fragment
├── write_copy_image_to_buffer_read_ssbo_geometry
├── write_copy_image_to_buffer_read_ssbo_tess_control
├── write_copy_image_to_buffer_read_ssbo_tess_eval
├── write_copy_image_to_buffer_read_ssbo_vertex
├── write_copy_image_to_buffer_read_ubo_compute
├── write_copy_image_to_buffer_read_ubo_compute_indirect
├── write_copy_image_to_buffer_read_ubo_fragment
├── write_copy_image_to_buffer_read_ubo_geometry
├── write_copy_image_to_buffer_read_ubo_tess_control
├── write_copy_image_to_buffer_read_ubo_tess_eval
├── write_copy_image_to_buffer_read_ubo_texel_compute
├── write_copy_image_to_buffer_read_ubo_texel_compute_indirect
├── write_copy_image_to_buffer_read_ubo_texel_fragment
├── write_copy_image_to_buffer_read_ubo_texel_geometry
├── write_copy_image_to_buffer_read_ubo_texel_tess_control
├── write_copy_image_to_buffer_read_ubo_texel_tess_eval
├── write_copy_image_to_buffer_read_ubo_texel_vertex
├── write_copy_image_to_buffer_read_ubo_vertex
├── write_copy_image_to_buffer_read_vertex_input
├── write_draw_indexed_indirect_read_blit_image
├── write_draw_indexed_indirect_read_copy_image
├── write_draw_indexed_indirect_read_copy_image_to_buffer
├── write_draw_indexed_indirect_read_image_compute
├── write_draw_indexed_indirect_read_image_compute_indirect
├── write_draw_indexed_indirect_read_image_fragment
├── write_draw_indexed_indirect_read_image_geometry
├── write_draw_indexed_indirect_read_image_tess_control
├── write_draw_indexed_indirect_read_image_tess_eval
├── write_draw_indexed_indirect_read_image_vertex
├── write_draw_indexed_read_blit_image
├── write_draw_indexed_read_copy_image
├── write_draw_indexed_read_copy_image_to_buffer
├── write_draw_indexed_read_image_compute
├── write_draw_indexed_read_image_compute_indirect
├── write_draw_indexed_read_image_fragment
├── write_draw_indexed_read_image_geometry
├── write_draw_indexed_read_image_tess_control
├── write_draw_indexed_read_image_tess_eval
├── write_draw_indexed_read_image_vertex
├── write_draw_indirect_read_blit_image
├── write_draw_indirect_read_copy_image
├── write_draw_indirect_read_copy_image_to_buffer
├── write_draw_indirect_read_image_compute
├── write_draw_indirect_read_image_compute_indirect
├── write_draw_indirect_read_image_fragment
├── write_draw_indirect_read_image_geometry
├── write_draw_indirect_read_image_tess_control
├── write_draw_indirect_read_image_tess_eval
├── write_draw_indirect_read_image_vertex
├── write_draw_read_blit_image
├── write_draw_read_copy_image
├── write_draw_read_copy_image_to_buffer
├── write_draw_read_image_compute
├── write_draw_read_image_compute_indirect
├── write_draw_read_image_fragment
├── write_draw_read_image_geometry
├── write_draw_read_image_tess_control
├── write_draw_read_image_tess_eval
├── write_draw_read_image_vertex
├── write_fill_buffer_read_copy_buffer
├── write_fill_buffer_read_copy_buffer_to_image
├── write_fill_buffer_read_ssbo_compute
├── write_fill_buffer_read_ssbo_compute_indirect
├── write_fill_buffer_read_ssbo_fragment
├── write_fill_buffer_read_ssbo_geometry
├── write_fill_buffer_read_ssbo_tess_control
├── write_fill_buffer_read_ssbo_tess_eval
├── write_fill_buffer_read_ssbo_vertex
├── write_fill_buffer_read_ubo_compute
├── write_fill_buffer_read_ubo_compute_indirect
├── write_fill_buffer_read_ubo_fragment
├── write_fill_buffer_read_ubo_geometry
├── write_fill_buffer_read_ubo_tess_control
├── write_fill_buffer_read_ubo_tess_eval
├── write_fill_buffer_read_ubo_texel_compute
├── write_fill_buffer_read_ubo_texel_compute_indirect
├── write_fill_buffer_read_ubo_texel_fragment
├── write_fill_buffer_read_ubo_texel_geometry
├── write_fill_buffer_read_ubo_texel_tess_control
├── write_fill_buffer_read_ubo_texel_tess_eval
├── write_fill_buffer_read_ubo_texel_vertex
├── write_fill_buffer_read_ubo_vertex
├── write_fill_buffer_read_vertex_input
├── write_image_compute_indirect_read_blit_image
├── write_image_compute_indirect_read_copy_image
├── write_image_compute_indirect_read_copy_image_to_buffer
├── write_image_compute_indirect_read_image_compute
├── write_image_compute_indirect_read_image_compute_indirect
├── write_image_compute_indirect_read_image_fragment
├── write_image_compute_indirect_read_image_geometry
├── write_image_compute_indirect_read_image_tess_control
├── write_image_compute_indirect_read_image_tess_eval
├── write_image_compute_indirect_read_image_vertex
├── write_image_compute_read_blit_image
├── write_image_compute_read_copy_image
├── write_image_compute_read_copy_image_to_buffer
├── write_image_compute_read_image_compute
├── write_image_compute_read_image_compute_indirect
├── write_image_compute_read_image_fragment
├── write_image_compute_read_image_geometry
├── write_image_compute_read_image_tess_control
├── write_image_compute_read_image_tess_eval
├── write_image_compute_read_image_vertex
├── write_image_fragment_read_blit_image
├── write_image_fragment_read_copy_image
├── write_image_fragment_read_copy_image_to_buffer
├── write_image_fragment_read_image_compute
├── write_image_fragment_read_image_compute_indirect
├── write_image_fragment_read_image_fragment
├── write_image_fragment_read_image_geometry
├── write_image_fragment_read_image_tess_control
├── write_image_fragment_read_image_tess_eval
├── write_image_fragment_read_image_vertex
├── write_image_geometry_read_blit_image
├── write_image_geometry_read_copy_image
├── write_image_geometry_read_copy_image_to_buffer
├── write_image_geometry_read_image_compute
├── write_image_geometry_read_image_compute_indirect
├── write_image_geometry_read_image_fragment
├── write_image_geometry_read_image_geometry
├── write_image_geometry_read_image_tess_control
├── write_image_geometry_read_image_tess_eval
├── write_image_geometry_read_image_vertex
├── write_image_tess_control_read_blit_image
├── write_image_tess_control_read_copy_image
├── write_image_tess_control_read_copy_image_to_buffer
├── write_image_tess_control_read_image_compute
├── write_image_tess_control_read_image_compute_indirect
├── write_image_tess_control_read_image_fragment
├── write_image_tess_control_read_image_geometry
├── write_image_tess_control_read_image_tess_control
├── write_image_tess_control_read_image_tess_eval
├── write_image_tess_control_read_image_vertex
├── write_image_tess_eval_read_blit_image
├── write_image_tess_eval_read_copy_image
├── write_image_tess_eval_read_copy_image_to_buffer
├── write_image_tess_eval_read_image_compute
├── write_image_tess_eval_read_image_compute_indirect
├── write_image_tess_eval_read_image_fragment
├── write_image_tess_eval_read_image_geometry
├── write_image_tess_eval_read_image_tess_control
├── write_image_tess_eval_read_image_tess_eval
├── write_image_tess_eval_read_image_vertex
├── write_image_vertex_read_blit_image
├── write_image_vertex_read_copy_image
├── write_image_vertex_read_copy_image_to_buffer
├── write_image_vertex_read_image_compute
├── write_image_vertex_read_image_compute_indirect
├── write_image_vertex_read_image_fragment
├── write_image_vertex_read_image_geometry
├── write_image_vertex_read_image_tess_control
├── write_image_vertex_read_image_tess_eval
├── write_image_vertex_read_image_vertex
├── write_ssbo_compute_indirect_read_copy_buffer
├── write_ssbo_compute_indirect_read_copy_buffer_to_image
├── write_ssbo_compute_indirect_read_ssbo_compute
├── write_ssbo_compute_indirect_read_ssbo_compute_indirect
├── write_ssbo_compute_indirect_read_ssbo_fragment
├── write_ssbo_compute_indirect_read_ssbo_geometry
├── write_ssbo_compute_indirect_read_ssbo_tess_control
├── write_ssbo_compute_indirect_read_ssbo_tess_eval
├── write_ssbo_compute_indirect_read_ssbo_vertex
├── write_ssbo_compute_indirect_read_ubo_compute
├── write_ssbo_compute_indirect_read_ubo_compute_indirect
├── write_ssbo_compute_indirect_read_ubo_fragment
├── write_ssbo_compute_indirect_read_ubo_geometry
├── write_ssbo_compute_indirect_read_ubo_tess_control
├── write_ssbo_compute_indirect_read_ubo_tess_eval
├── write_ssbo_compute_indirect_read_ubo_texel_compute
├── write_ssbo_compute_indirect_read_ubo_texel_compute_indirect
├── write_ssbo_compute_indirect_read_ubo_texel_fragment
├── write_ssbo_compute_indirect_read_ubo_texel_geometry
├── write_ssbo_compute_indirect_read_ubo_texel_tess_control
├── write_ssbo_compute_indirect_read_ubo_texel_tess_eval
├── write_ssbo_compute_indirect_read_ubo_texel_vertex
├── write_ssbo_compute_indirect_read_ubo_vertex
├── write_ssbo_compute_indirect_read_vertex_input
├── write_ssbo_compute_read_copy_buffer
├── write_ssbo_compute_read_copy_buffer_to_image
├── write_ssbo_compute_read_ssbo_compute
├── write_ssbo_compute_read_ssbo_compute_indirect
├── write_ssbo_compute_read_ssbo_fragment
├── write_ssbo_compute_read_ssbo_geometry
├── write_ssbo_compute_read_ssbo_tess_control
├── write_ssbo_compute_read_ssbo_tess_eval
├── write_ssbo_compute_read_ssbo_vertex
├── write_ssbo_compute_read_ubo_compute
├── write_ssbo_compute_read_ubo_compute_indirect
├── write_ssbo_compute_read_ubo_fragment
├── write_ssbo_compute_read_ubo_geometry
├── write_ssbo_compute_read_ubo_tess_control
├── write_ssbo_compute_read_ubo_tess_eval
├── write_ssbo_compute_read_ubo_texel_compute
├── write_ssbo_compute_read_ubo_texel_compute_indirect
├── write_ssbo_compute_read_ubo_texel_fragment
├── write_ssbo_compute_read_ubo_texel_geometry
├── write_ssbo_compute_read_ubo_texel_tess_control
├── write_ssbo_compute_read_ubo_texel_tess_eval
├── write_ssbo_compute_read_ubo_texel_vertex
├── write_ssbo_compute_read_ubo_vertex
├── write_ssbo_compute_read_vertex_input
├── write_ssbo_fragment_read_copy_buffer
├── write_ssbo_fragment_read_copy_buffer_to_image
├── write_ssbo_fragment_read_ssbo_compute
├── write_ssbo_fragment_read_ssbo_compute_indirect
├── write_ssbo_fragment_read_ssbo_fragment
├── write_ssbo_fragment_read_ssbo_geometry
├── write_ssbo_fragment_read_ssbo_tess_control
├── write_ssbo_fragment_read_ssbo_tess_eval
├── write_ssbo_fragment_read_ssbo_vertex
├── write_ssbo_fragment_read_ubo_compute
├── write_ssbo_fragment_read_ubo_compute_indirect
├── write_ssbo_fragment_read_ubo_fragment
├── write_ssbo_fragment_read_ubo_geometry
├── write_ssbo_fragment_read_ubo_tess_control
├── write_ssbo_fragment_read_ubo_tess_eval
├── write_ssbo_fragment_read_ubo_texel_compute
├── write_ssbo_fragment_read_ubo_texel_compute_indirect
├── write_ssbo_fragment_read_ubo_texel_fragment
├── write_ssbo_fragment_read_ubo_texel_geometry
├── write_ssbo_fragment_read_ubo_texel_tess_control
├── write_ssbo_fragment_read_ubo_texel_tess_eval
├── write_ssbo_fragment_read_ubo_texel_vertex
├── write_ssbo_fragment_read_ubo_vertex
├── write_ssbo_fragment_read_vertex_input
├── write_ssbo_geometry_read_copy_buffer
├── write_ssbo_geometry_read_copy_buffer_to_image
├── write_ssbo_geometry_read_ssbo_compute
├── write_ssbo_geometry_read_ssbo_compute_indirect
├── write_ssbo_geometry_read_ssbo_fragment
├── write_ssbo_geometry_read_ssbo_geometry
├── write_ssbo_geometry_read_ssbo_tess_control
├── write_ssbo_geometry_read_ssbo_tess_eval
├── write_ssbo_geometry_read_ssbo_vertex
├── write_ssbo_geometry_read_ubo_compute
├── write_ssbo_geometry_read_ubo_compute_indirect
├── write_ssbo_geometry_read_ubo_fragment
├── write_ssbo_geometry_read_ubo_geometry
├── write_ssbo_geometry_read_ubo_tess_control
├── write_ssbo_geometry_read_ubo_tess_eval
├── write_ssbo_geometry_read_ubo_texel_compute
├── write_ssbo_geometry_read_ubo_texel_compute_indirect
├── write_ssbo_geometry_read_ubo_texel_fragment
├── write_ssbo_geometry_read_ubo_texel_geometry
├── write_ssbo_geometry_read_ubo_texel_tess_control
├── write_ssbo_geometry_read_ubo_texel_tess_eval
├── write_ssbo_geometry_read_ubo_texel_vertex
├── write_ssbo_geometry_read_ubo_vertex
├── write_ssbo_geometry_read_vertex_input
├── write_ssbo_tess_control_read_copy_buffer
├── write_ssbo_tess_control_read_copy_buffer_to_image
├── write_ssbo_tess_control_read_ssbo_compute
├── write_ssbo_tess_control_read_ssbo_compute_indirect
├── write_ssbo_tess_control_read_ssbo_fragment
├── write_ssbo_tess_control_read_ssbo_geometry
├── write_ssbo_tess_control_read_ssbo_tess_control
├── write_ssbo_tess_control_read_ssbo_tess_eval
├── write_ssbo_tess_control_read_ssbo_vertex
├── write_ssbo_tess_control_read_ubo_compute
├── write_ssbo_tess_control_read_ubo_compute_indirect
├── write_ssbo_tess_control_read_ubo_fragment
├── write_ssbo_tess_control_read_ubo_geometry
├── write_ssbo_tess_control_read_ubo_tess_control
├── write_ssbo_tess_control_read_ubo_tess_eval
├── write_ssbo_tess_control_read_ubo_texel_compute
├── write_ssbo_tess_control_read_ubo_texel_compute_indirect
├── write_ssbo_tess_control_read_ubo_texel_fragment
├── write_ssbo_tess_control_read_ubo_texel_geometry
├── write_ssbo_tess_control_read_ubo_texel_tess_control
├── write_ssbo_tess_control_read_ubo_texel_tess_eval
├── write_ssbo_tess_control_read_ubo_texel_vertex
├── write_ssbo_tess_control_read_ubo_vertex
├── write_ssbo_tess_control_read_vertex_input
├── write_ssbo_tess_eval_read_copy_buffer
├── write_ssbo_tess_eval_read_copy_buffer_to_image
├── write_ssbo_tess_eval_read_ssbo_compute
├── write_ssbo_tess_eval_read_ssbo_compute_indirect
├── write_ssbo_tess_eval_read_ssbo_fragment
├── write_ssbo_tess_eval_read_ssbo_geometry
├── write_ssbo_tess_eval_read_ssbo_tess_control
├── write_ssbo_tess_eval_read_ssbo_tess_eval
├── write_ssbo_tess_eval_read_ssbo_vertex
├── write_ssbo_tess_eval_read_ubo_compute
├── write_ssbo_tess_eval_read_ubo_compute_indirect
├── write_ssbo_tess_eval_read_ubo_fragment
├── write_ssbo_tess_eval_read_ubo_geometry
├── write_ssbo_tess_eval_read_ubo_tess_control
├── write_ssbo_tess_eval_read_ubo_tess_eval
├── write_ssbo_tess_eval_read_ubo_texel_compute
├── write_ssbo_tess_eval_read_ubo_texel_compute_indirect
├── write_ssbo_tess_eval_read_ubo_texel_fragment
├── write_ssbo_tess_eval_read_ubo_texel_geometry
├── write_ssbo_tess_eval_read_ubo_texel_tess_control
├── write_ssbo_tess_eval_read_ubo_texel_tess_eval
├── write_ssbo_tess_eval_read_ubo_texel_vertex
├── write_ssbo_tess_eval_read_ubo_vertex
├── write_ssbo_tess_eval_read_vertex_input
├── write_ssbo_vertex_read_copy_buffer
├── write_ssbo_vertex_read_copy_buffer_to_image
├── write_ssbo_vertex_read_ssbo_compute
├── write_ssbo_vertex_read_ssbo_compute_indirect
├── write_ssbo_vertex_read_ssbo_fragment
├── write_ssbo_vertex_read_ssbo_geometry
├── write_ssbo_vertex_read_ssbo_tess_control
├── write_ssbo_vertex_read_ssbo_tess_eval
├── write_ssbo_vertex_read_ssbo_vertex
├── write_ssbo_vertex_read_ubo_compute
├── write_ssbo_vertex_read_ubo_compute_indirect
├── write_ssbo_vertex_read_ubo_fragment
├── write_ssbo_vertex_read_ubo_geometry
├── write_ssbo_vertex_read_ubo_tess_control
├── write_ssbo_vertex_read_ubo_tess_eval
├── write_ssbo_vertex_read_ubo_texel_compute
├── write_ssbo_vertex_read_ubo_texel_compute_indirect
├── write_ssbo_vertex_read_ubo_texel_fragment
├── write_ssbo_vertex_read_ubo_texel_geometry
├── write_ssbo_vertex_read_ubo_texel_tess_control
├── write_ssbo_vertex_read_ubo_texel_tess_eval
├── write_ssbo_vertex_read_ubo_texel_vertex
├── write_ssbo_vertex_read_ubo_vertex
├── write_ssbo_vertex_read_vertex_input
├── write_update_buffer_read_copy_buffer
├── write_update_buffer_read_copy_buffer_to_image
├── write_update_buffer_read_ssbo_compute
├── write_update_buffer_read_ssbo_compute_indirect
├── write_update_buffer_read_ssbo_fragment
├── write_update_buffer_read_ssbo_geometry
├── write_update_buffer_read_ssbo_tess_control
├── write_update_buffer_read_ssbo_tess_eval
├── write_update_buffer_read_ssbo_vertex
├── write_update_buffer_read_ubo_compute
├── write_update_buffer_read_ubo_compute_indirect
├── write_update_buffer_read_ubo_fragment
├── write_update_buffer_read_ubo_geometry
├── write_update_buffer_read_ubo_tess_control
├── write_update_buffer_read_ubo_tess_eval
├── write_update_buffer_read_ubo_texel_compute
├── write_update_buffer_read_ubo_texel_compute_indirect
├── write_update_buffer_read_ubo_texel_fragment
├── write_update_buffer_read_ubo_texel_geometry
├── write_update_buffer_read_ubo_texel_tess_control
├── write_update_buffer_read_ubo_texel_tess_eval
├── write_update_buffer_read_ubo_texel_vertex
├── write_update_buffer_read_ubo_vertex
└── write_update_buffer_read_vertex_input
```

Registered in the LEGACY synchronization path via [`createWin32KeyedMutexTest()`](../../../modules/vulkan/synchronization/vktSynchronizationWin32KeyedMutexTests.cpp#L1863) added to the `synchronization` group in [vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp) (line 141). This group is not included in the `synchronization2` path.

The 424 direct children are operation pair groups generated from the Cartesian product of `s_writeOps` and `s_readOps` from [`vktSynchronizationOperationTestData`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp), filtered by resource compatibility (`isResourceSupported`). Only non-empty groups (those with at least one compatible resource/handle-type combination) are registered.

## Test Families

### write_blit_image_read_blit_image — Operation pair groups (424 groups total)

Each direct child is an operation pair group named `<writeOp>_<readOp>`, containing leaf test cases named `<resource><handleSuffix>`.

- **Operation pair groups**: Named `<writeOp>_<readOp>` (e.g., `write_copy_buffer_read_copy_buffer`, `write_blit_image_read_copy_image`). Iterates over `s_writeOps` x `s_readOps` from [`vktSynchronizationOperationTestData`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp).
- **Leaf tests**: Named `<resource><handleSuffix>` where `<resource>` comes from `s_resourcesWin32KeyedMutex` and `<handleSuffix>` is `_nt` or `_kmt`.

Each leaf test is a [Win32KeyedMutexTestCase](../../../modules/vulkan/synchronization/vktSynchronizationWin32KeyedMutexTests.cpp#L1781) that creates DX11 resources with keyed mutex, imports into Vulkan, writes via Vulkan, copies via DX11, reads back via Vulkan, and verifies data integrity.

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Write Operation | `s_writeOps` from operation test data | `vktSynchronizationOperationTestData` |
| Read Operation | `s_readOps` from operation test data | `vktSynchronizationOperationTestData` |
| Resource Type | Buffer (16 KiB, 256 KiB), Image 2D (128x128 in R8_UNORM, R16_UINT, R8G8B8A8_UNORM, R16G16B16A16_UINT, R32G32B32A32_SFLOAT) | `s_resourcesWin32KeyedMutex` |
| Handle Type | NT handle (`_nt`, D3D11 texture only), KMT handle (`_kmt`, opaque Win32 KMT for buffers, D3D11 texture KMT for images) | `cases` array in `createTests()` |

## Support/Feature Requirements

| Requirement | Type | Notes |
|-------------|------|-------|
| VK_KHR_external_memory_win32 | Device Extension | Required |
| VK_KHR_win32_keyed_mutex | Device Extension | Required |
| VK_KHR_get_physical_device_properties2 | Instance Extension | Required |
| VK_KHR_external_memory_capabilities | Instance Extension | Required |
| VK_KHR_external_memory | Device Extension | Required if not core |
| VK_KHR_dedicated_allocation | Device Extension | Required if not core |
| VK_KHR_get_memory_requirements2 | Device Extension | Required if not core |
| Windows OS | Platform | Entire test is gated by `DE_OS == DE_OS_WIN32` |
| D3D11 runtime | System Library | d3d11.dll, dxgi.dll, d3dcompiler loaded at runtime |
| deviceLUIDValid | Physical Device Property | Must be true for DX11 adapter matching |
| External memory importable | Feature | Checked per format/handle type |

## Verification Methods

1. **Data comparison**: After Vulkan writes, DX11 copies, and Vulkan reads back, the test compares the write operation output data with the read operation input data byte-by-byte using `deMemCmp`. On mismatch, the first differing byte offset is logged along with expected and actual byte sequences (up to 256 bytes).
2. **Queue iteration**: The test iterates over all queue families, running the same test on each, and aggregates results via `tcu::ResultCollector`.
3. **Keyed mutex protocol**: Uses a 5-key protocol (INIT=0, VK_WRITE=1, DX_COPY=2, VK_VERIFY=3, DONE=4) via `VkWin32KeyedMutexAcquireReleaseInfoKHR` chained into `VkSubmitInfo`.

## Test Principles

1. **Cross-API synchronization**: Validates that Vulkan and DX11 can share resources through Win32 keyed mutex, with correct acquire/release semantics ensuring data visibility across API boundaries.
2. **Handle type coverage**: Tests both NT handles (modern, D3D11 texture only) and KMT handles (legacy, both buffers and textures) to cover the two Win32 external memory handle types.
3. **Resource variety**: Tests both buffer and image resources with multiple formats and sizes to ensure the keyed mutex mechanism works across different resource types.
4. **Operation pair coverage**: Combines various write and read operations (copy, clear, draw, etc.) to exercise different pipeline stages and access patterns.

## Notes/Uncertainties

- **Platform-specific**: The entire test file is only compiled and run on Windows (`DE_OS == DE_OS_WIN32`). On other platforms, `TCU_THROW(NotSupportedError, "OS not supported")` is triggered.
- **Singleton instance/device**: Uses a shared `InstanceAndDevice` singleton across all test cases in the group, destroyed in `cleanupGroup()`. This is an optimization to avoid recreating the DX11 device for every test case.
- **NT handles and buffers**: NT handles (`VK_EXTERNAL_MEMORY_HANDLE_TYPE_D3D11_TEXTURE_BIT`) are not supported for buffers because D3D11 `CreateBuffer()` does not support `SHARED_NTHANDLE`. This is enforced by skipping buffer tests with the `_nt` suffix.
- **Windows version check**: NT handle type for images requires Windows 8+ (`IsWindows8OrGreater()`); KMT handle for opaque Win32 buffers also requires Windows 8+.
- **Non-SC only**: The test is excluded from Vulkan SC builds (`#ifndef CTS_USES_VULKANSC`).
- **LEGACY only**: Registered only in the `synchronization` (LEGACY) path, not in `synchronization2`.
