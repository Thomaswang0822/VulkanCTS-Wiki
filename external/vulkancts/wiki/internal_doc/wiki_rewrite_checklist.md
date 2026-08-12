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
- [ ] 16. image_processing — 3
- [x] 17. wsi — 13 (UB: 10)
- [ ] 18. synchronization — 17
- [ ] 19. synchronization2 (should be done together with synchronization)
- [ ] 20. sparse_resources — 14
- [ ] 21. tessellation — 17
- [x] 22. rasterization — 6 (UB: 5)
- [ ] 23. clipping — 1
- [ ] 24. fragment_operations — 5
- [ ] 25. texture — 13
- [x] 26. geometry — 7 (UB: 7)
- [ ] 27. robustness — 9
- [ ] 28. multiview — 2
- [ ] 29. subgroups — 20
- [ ] 30. ycbcr — 10
- [ ] 31. protected_memory — 15
- [ ] 32. device_group — 1
- [x] 33. memory_model — 3 (UB: 2)
- [ ] 34. conditional_rendering — 7
- [ ] 35. graphicsfuzz — 1
- [ ] 36. imageless_framebuffer — 1
- [ ] 37. transform_feedback — 5
- [ ] 38. descriptor_indexing — 3
- [ ] 39. fragment_shader_interlock — 2
- [ ] 40. fragment_shading_barycentric — 1
- [ ] 41. fragment_shading_rate — 5
- [ ] 42. drm_format_modifiers — 1
- [x] 43. ray_tracing_pipeline — 30 (UB: 18)
- [x] 44. ray_query — 14 (UB: 8)
- [ ] 45. reconvergence — 2
- [ ] 46. mesh_shader — 17
- [ ] 47. depth — 1
- [ ] 48. video — 6
- [ ] 49. shader_object — 11
- [ ] 50. dgc — 27
- [ ] 51. cooperative_vector — 3
- [ ] 52. tensor — 7
- [ ] 53. data_graph — 4

**Summary**: 21 done, 32 todo.
