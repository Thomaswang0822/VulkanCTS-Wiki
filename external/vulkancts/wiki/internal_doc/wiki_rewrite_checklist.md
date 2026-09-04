# Wiki Rewrite Checklist

Track the rewrite + audit + publish progress of all 53 Vulkan CTS test categories.

A category is **done** when its `testfiles/<category>/` subdirectory contains at least one non-`vkt`-prefixed page (equivalently: `vkt_count != total_count`). A category is **todo** when every page is `vkt`-prefixed, or when its subdirectory is missing entirely. No category is currently in progress.

**L3 page counts**:
- For **done** categories, L3 excludes `_brief.md` Understanding Briefs (UB). UB count is shown in parentheses for reference.
- For **todo** categories, L3 = total file count in `testfiles/<category>/` (UB concept not yet introduced).

- [x] 1. info — 2 (UB: 1)
- [x] 2. api — 52 (UB: 11)
- [x] 3. memory — 14 (UB: 11)
- [x] 4. pipeline — 62 (UB: 62)
- [x] 5. binding_model — 15 (UB: 15)
- [x] 6. spirv_assembly — 40 (UB: 27)
- [x] 7. glsl — 23 (UB: 0)
- [x] 8. renderpasses — 29 (UB: 0)
- [x] 9. ubo — 1 (UB: 1)
- [x] 10. dynamic_state — 10 (UB: 0)
- [x] 11. ssbo — 3 (UB: 2)
- [x] 12. query_pool — 7 (UB: 5)
- [x] 13. draw — 30 (UB: 24)
- [x] 14. compute — 7 (UB: 4)
- [x] 15. image — 24 (UB: 17)
- [x] 16. image_processing — 2 (UB: 1)
- [x] 17. wsi — 13 (UB: 10)
- [x] 18. synchronization — 16 (UB: 16)
- [x] 19. synchronization2 — shared with synchronization (UB: shared)
- [x] 20. sparse_resources — 13 (UB: 11)
- [x] 21. tessellation — 16 (UB: 15)
- [x] 22. rasterization — 6 (UB: 5)
- [x] 23. clipping — 1 (UB: 1)
- [x] 24. fragment_operations — 5 (UB: 5)
- [x] 25. texture — 12 (UB: 12)
- [x] 26. geometry — 7 (UB: 7)
- [x] 27. robustness — 8 (UB: 8)
- [x] 28. multiview — 1
- [x] 29. subgroups — 19 (UB: 19)
- [x] 30. ycbcr — 9 (UB: 8)
- [x] 31. protected_memory — 14 (UB: 14)
- [x] 32. device_group — 1
- [x] 33. memory_model — 3 (UB: 2)
- [x] 34. conditional_rendering — 6
- [x] 35. graphicsfuzz — 1
- [x] 36. imageless_framebuffer — 1
- [x] 37. transform_feedback — 4 (UB: 4)
- [x] 38. descriptor_indexing — 3
- [x] 39. fragment_shader_interlock — 2
- [x] 40. fragment_shading_barycentric — 1
- [x] 41. fragment_shading_rate — 5
- [x] 42. drm_format_modifiers — 1
- [x] 43. ray_tracing_pipeline — 30 (UB: 18)
- [x] 44. ray_query — 14 (UB: 8)
- [x] 45. reconvergence — 2 (UB: 2)
- [x] 46. mesh_shader — 16 (UB: 11)
- [x] 47. depth — 1
- [x] 48. video — 6 (UB: 6)
- [x] 49. shader_object — 10 (UB: 8)
- [x] 50. dgc — 26 (UB: 22)
- [x] 51. cooperative_vector — 3
- [x] 52. tensor — 7
- [x] 53. data_graph — 4

**Summary**: 53 done, 0 todo.
