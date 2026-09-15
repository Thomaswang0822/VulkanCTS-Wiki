# Wiki Rewrite Checklist

Track the rewrite + audit + publish progress of all 53 Vulkan CTS test categories.

A category is **done** when its `testfiles/<category>/` subdirectory contains at least one non-`vkt`-prefixed page (equivalently: `vkt_count != total_count`). A category is **todo** when every page is `vkt`-prefixed, or when its subdirectory is missing entirely. No category is currently in progress.

**L3 page counts**:
- For **done** categories, L3 counts the implementation-bearing Level-3 pages; registration-only and helper-only files are excluded.
- For **todo** categories, L3 = total file count in `testfiles/<category>/`.

- [x] 1. info — 2
- [x] 2. api — 52
- [x] 3. memory — 14
- [x] 4. pipeline — 63
- [x] 5. binding_model — 15
- [x] 6. spirv_assembly — 41
- [x] 7. glsl — 23
- [x] 8. renderpasses — 29
- [x] 9. ubo — 1
- [x] 10. dynamic_state — 10
- [x] 11. ssbo — 3
- [x] 12. query_pool — 7
- [x] 13. draw — 30
- [x] 14. compute — 7
- [x] 15. image — 24
- [x] 16. image_processing — 2
- [x] 17. wsi — 13
- [x] 18. synchronization — 16
- [x] 19. synchronization2 — shared with synchronization
- [x] 20. sparse_resources — 13
- [x] 21. tessellation — 16
- [x] 22. rasterization — 6
- [x] 23. clipping — 1
- [x] 24. fragment_operations — 5
- [x] 25. texture — 12
- [x] 26. geometry — 7
- [x] 27. robustness — 8
- [x] 28. multiview — 1
- [x] 29. subgroups — 19
- [x] 30. ycbcr — 9
- [x] 31. protected_memory — 14
- [x] 32. device_group — 1
- [x] 33. memory_model — 3
- [x] 34. conditional_rendering — 6
- [x] 35. graphicsfuzz — 1
- [x] 36. imageless_framebuffer — 1
- [x] 37. transform_feedback — 4
- [x] 38. descriptor_indexing — 3
- [x] 39. fragment_shader_interlock — 2
- [x] 40. fragment_shading_barycentric — 1
- [x] 41. fragment_shading_rate — 5
- [x] 42. drm_format_modifiers — 1
- [x] 43. ray_tracing_pipeline — 30
- [x] 44. ray_query — 14
- [x] 45. reconvergence — 2
- [x] 46. mesh_shader — 16
- [x] 47. depth — 1
- [x] 48. video — 6
- [x] 49. shader_object — 11
- [x] 50. dgc — 26
- [x] 51. cooperative_vector — 3
- [x] 52. tensor — 7
- [x] 53. data_graph — 4

**Summary**: 53 done, 0 todo.
