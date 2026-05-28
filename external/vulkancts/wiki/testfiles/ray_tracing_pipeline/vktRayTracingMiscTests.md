# vktRayTracingMiscTests

This registered implementation file registers `misc` under `ray_tracing_pipeline`. The group construction is evidenced in [vktRayTracingMiscTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10904-L10908).

## Source Files

| Role | Link |
|------|------|
| Registration and implementation | [vktRayTracingMiscTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10904-L10924) |

## Registration Hierarchy

```text
ray_tracing_pipeline.misc
├── AS_stresstest_AABB
├── AS_stresstest_tri
├── NO_DUPLICATE_ANY_HIT_1TL1BL1G_AABB
├── NO_DUPLICATE_ANY_HIT_1TL1BL1G_tri
├── NO_DUPLICATE_ANY_HIT_1TL1BLnG_AABB
├── NO_DUPLICATE_ANY_HIT_1TL1BLnG_tri
├── NO_DUPLICATE_ANY_HIT_1TLnBL1G_AABB
├── NO_DUPLICATE_ANY_HIT_1TLnBL1G_tri
├── NO_DUPLICATE_ANY_HIT_1TLnBLnG_AABB
├── NO_DUPLICATE_ANY_HIT_1TLnBLnG_tri
├── OpIgnoreIntersectionKHR_AnyHitDynamically
├── OpIgnoreIntersectionKHR_AnyHitStatically
├── OpTerminateRayKHR_AnyHitDynamically
├── OpTerminateRayKHR_AnyHitStatically
├── OpTerminateRayKHR_IntersectionDynamically
├── OpTerminateRayKHR_IntersectionStatically
├── callableshaderstress_1TL1BL1G_AABB_dynamic
├── callableshaderstress_1TL1BL1G_AABB_static
├── callableshaderstress_1TL1BL1G_tri_dynamic
├── callableshaderstress_1TL1BL1G_tri_static
├── callableshaderstress_1TL1BLnG_AABB_dynamic
├── callableshaderstress_1TL1BLnG_AABB_static
├── callableshaderstress_1TL1BLnG_tri_dynamic
├── callableshaderstress_1TL1BLnG_tri_static
├── callableshaderstress_1TLnBL1G_AABB_dynamic
├── callableshaderstress_1TLnBL1G_AABB_static
├── callableshaderstress_1TLnBL1G_tri_dynamic
├── callableshaderstress_1TLnBL1G_tri_static
├── callableshaderstress_1TLnBLnG_AABB_dynamic
├── callableshaderstress_1TLnBLnG_AABB_static
├── callableshaderstress_1TLnBLnG_tri_dynamic
├── callableshaderstress_1TLnBLnG_tri_static
├── cullmask_AABB
├── cullmask_AABB_extrabits
├── cullmask_tri
├── cullmask_tri_extrabits
├── empty_pipeline_layout
├── maxrayhitattributesize_1TL1BL1G
├── maxrayhitattributesize_1TL1BLnG
├── maxrayhitattributesize_1TLnBL1G
├── maxrayhitattributesize_1TLnBLnG
├── maxrtinvocations_AABB
├── maxrtinvocations_tri
├── memory_access
├── mixedPrimTL
├── null_miss
├── raypayloadin_AABB
├── raypayloadin_tri
├── recursiveTraces_AABB_0
├── recursiveTraces_AABB_1
├── recursiveTraces_AABB_10
├── recursiveTraces_AABB_11
├── recursiveTraces_AABB_12
├── recursiveTraces_AABB_13
├── recursiveTraces_AABB_14
├── recursiveTraces_AABB_15
├── recursiveTraces_AABB_2
├── recursiveTraces_AABB_3
├── recursiveTraces_AABB_4
├── recursiveTraces_AABB_5
├── recursiveTraces_AABB_6
├── recursiveTraces_AABB_7
├── recursiveTraces_AABB_8
├── recursiveTraces_AABB_9
├── recursiveTraces_tri_0
├── recursiveTraces_tri_1
├── recursiveTraces_tri_10
├── recursiveTraces_tri_11
├── recursiveTraces_tri_12
├── recursiveTraces_tri_13
├── recursiveTraces_tri_14
├── recursiveTraces_tri_15
├── recursiveTraces_tri_2
├── recursiveTraces_tri_3
├── recursiveTraces_tri_4
├── recursiveTraces_tri_5
├── recursiveTraces_tri_6
├── recursiveTraces_tri_7
├── recursiveTraces_tri_8
├── recursiveTraces_tri_9
├── report_intersection_result
├── reuse_creation_buffer_bottom
├── reuse_creation_buffer_top
├── reuse_scratch_buffer
├── shaderRecordExplicitSTD430Offset_1
├── shaderRecordExplicitSTD430Offset_2
├── shaderRecordExplicitSTD430Offset_3
├── shaderRecordExplicitSTD430Offset_4
├── shaderRecordExplicitSTD430Offset_5
├── shaderRecordExplicitSTD430Offset_6
├── shaderRecordExplicitScalarOffset_1
├── shaderRecordExplicitScalarOffset_2
├── shaderRecordExplicitScalarOffset_3
├── shaderRecordExplicitScalarOffset_4
├── shaderRecordExplicitScalarOffset_5
├── shaderRecordExplicitScalarOffset_6
├── shaderRecordSTD430_1
├── shaderRecordSTD430_2
├── shaderRecordSTD430_3
├── shaderRecordSTD430_4
├── shaderRecordSTD430_5
├── shaderRecordSTD430_6
├── shaderRecordScalar_1
├── shaderRecordScalar_2
├── shaderRecordScalar_3
├── shaderRecordScalar_4
├── shaderRecordScalar_5
├── shaderRecordScalar_6
├── shaders_from_lib
├── update_empty_bottom
└── update_empty_top
```

## Test Families

### misc — Registered branch

Miscellaneous tests cover callable stress, cull masks, recursion, shader-record layouts, empty pipeline layouts, null miss, memory access, and related edge cases. The registered group name is created in [vktRayTracingMiscTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10908-L10911). Direct children observed in mustpass/source include `AS_stresstest_AABB`, `AS_stresstest_tri`, `NO_DUPLICATE_ANY_HIT_1TL1BL1G_AABB`, `NO_DUPLICATE_ANY_HIT_1TL1BL1G_tri`, `NO_DUPLICATE_ANY_HIT_1TL1BLnG_AABB`, `NO_DUPLICATE_ANY_HIT_1TL1BLnG_tri`, `NO_DUPLICATE_ANY_HIT_1TLnBL1G_AABB`, `NO_DUPLICATE_ANY_HIT_1TLnBL1G_tri` and additional direct children.

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| `misc` direct children | `AS_stresstest_AABB`, `AS_stresstest_tri`, `NO_DUPLICATE_ANY_HIT_1TL1BL1G_AABB`, `NO_DUPLICATE_ANY_HIT_1TL1BL1G_tri`, `NO_DUPLICATE_ANY_HIT_1TL1BLnG_AABB`, `NO_DUPLICATE_ANY_HIT_1TL1BLnG_tri`, `NO_DUPLICATE_ANY_HIT_1TLnBL1G_AABB`, `NO_DUPLICATE_ANY_HIT_1TLnBL1G_tri`, `NO_DUPLICATE_ANY_HIT_1TLnBLnG_AABB`, `NO_DUPLICATE_ANY_HIT_1TLnBLnG_tri`, `OpIgnoreIntersectionKHR_AnyHitDynamically`, `OpIgnoreIntersectionKHR_AnyHitStatically` ... | [vktRayTracingMiscTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L10908-L10928) |

## Support / Feature Requirements

Support is checked in this file; observed gates include ray tracing pipeline and related feature/extension checks at [vktRayTracingMiscTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L8420-L8424).

## Verification Methods

The inspected implementation creates an empty-layout ray tracing pipeline and passes if creation does not crash in [vktRayTracingMiscTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingMiscTests.cpp#L8753-L8765).

## Test Principles

The file registers focused ray tracing pipeline scenarios and varies only the dimensions visible in its registration loops or child-group construction. Claims above are limited to inspected registration code and mustpass-observed path components.

## Notes
