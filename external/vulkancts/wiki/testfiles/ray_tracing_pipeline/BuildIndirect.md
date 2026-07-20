## Overview

**Core question:** Does an acceleration structure built indirectly, where the build range count, primitive offset, first vertex, and transform offset come from a GPU-filled buffer rather than host-supplied parameters, produce the same hit/miss pattern as an equivalent direct build, for triangles (indexed and non-indexed), AABBs, and instances?

- [vktRayTracingBuildIndirectTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp) implements the single test family `indirect_acceleration_structure` under the `ray_tracing_pipeline` test category.
- All leaves share one scene shape (a `SQUARE_SIZE x SQUARE_SIZE` grid of primitives spread across `depth` geometries), one ray tracing pipeline with rgen/closest-hit/miss/intersection shaders, and one per-pixel result check. What varies is whether the acceleration structure is built once (`build`) or built-then-updated (`update`), and which `VkAccelerationStructureBuildRangeInfoKHR` field the leaf exercises.
- Each leaf populates a device-side indirect buffer by running a small rgen shader that writes a `VkAccelerationStructureBuildRangeInfoKHR` struct (primitive count, primitive offset, first vertex, transform offset), then builds the BLAS/TLAS with that indirect buffer, traces one ray per pixel straight down the -z axis, and compares the resulting per-pixel hit/miss values against an expected pattern derived from geometry placement.
- The page explains the build-versus-update axis, the per-field parameter matrix, the indirect-buffer generation mechanism, the offset arithmetic that backs each field, and what a failure of each field points to.

## Background Knowledge

- **Indirect acceleration structure builds.** `VK_KHR_acceleration_structure` allows a build to read its build range parameters from a device buffer instead of a host pointer. When `setIndirectBuildParameters` is used, `vkCmdBuildAccelerationStructuresIndirectKHR` reads one `VkAccelerationStructureBuildRangeInfoKHR` per geometry from the indirect buffer. The struct fields are `primitiveCount`, `primitiveOffset`, `firstVertex`, and `transformOffset`. This test requires the `accelerationStructureIndirectBuild` feature.
- **Build range fields.** `primitiveCount` limits how many primitives of the geometry are built. `primitiveOffset` is a byte offset into the vertex or AABB data. `firstVertex` is a vertex-index offset for indexed triangle geometry. `transformOffset` is a byte offset into the transform-data buffer. A correct indirect build must honor each field exactly as a host-supplied direct build would.
- **Acceleration structure updates.** A build with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR` can be rebuilt in-place with `vkCmdBuildAccelerationStructuresKHR` using the `VK_BUILD_ACCELERATION_STRUCTURE_MODE_UPDATE_KHR` mode. The `update` leaves build an intentionally wrong structure first, then update it so the indirect fields point at the correct geometry.
- **AABB expansion.** The Vulkan spec permits implementations to expand AABB geometries in an acceleration structure to mitigate precision issues, which can produce false-positive intersection reports. The AABB result check tolerates this.

## Registration Hierarchy

```text
ray_tracing_pipeline.indirect_acceleration_structure
├── build
└── update
```

The two direct children are registered by [createBuildIndirectTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1254-L1401). The `addIndirectTests` helper is called twice: once with `doUpdate == false` for the `build` child, and once with `doUpdate == true` for the `update` child. Each call registers the same four geometry-type groups (`triangles_indexed`, `triangles_no_index`, `aabbs`, `instances`) and the same field-intermediate nodes (`primitive_count`, `primitive_offset`, `first_vertex`, `transform_offset`) under each applicable geometry type.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Build/update mode | `build`, `update` | Direct child of the test family. `build` builds the structure once indirectly. `update` builds an intentionally wrong structure first, then rebuilds it in-place via an indirect update. This is the primary behavioral axis. | [createBuildIndirectTests](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1392-L1398) |
| Geometry type | `triangles_indexed`, `triangles_no_index`, `aabbs`, `instances` | Selects which BLAS geometry type is built indirectly, or whether the TLAS instance buffer is built indirectly. `triangles_no_index` uses the base `RayTracingBuildIndirectTestInstance`; `triangles_indexed` adds an index buffer; `aabbs` overrides `iterate`; `instances` overrides both TLAS and BLAS init. | [addIndirectTests groups](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1258-L1261) |
| Build range field | `primitive_count`, `primitive_offset`, `first_vertex`, `transform_offset` | Intermediate node selecting which `VkAccelerationStructureBuildRangeInfoKHR` field the leaf varies. `instances` uses `primitive_count` and `primitive_offset` against the instance buffer. `first_vertex` and `transform_offset` apply only to triangle geometry. | [field group construction](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1263-L1381) |
| Primitive count leaf | `5`, `10`, `15`, `20`, `25` | `primitiveCount` value, stepping down by `SQUARE_SIZE` from `SQUARE_SIZE*SQUARE_SIZE`. Fewer primitives means the back of the grid is not built and must miss. | [primCount loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1272-L1283) |
| Primitive offset leaf | `8`, `16`, `24`, `32`, `40`, `48` | `primitiveOffset` byte value for BLAS, stepping by 8. | [primOffset loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1311-L1321) |
| Instance offset leaf | `16`, `32`, `48`, `64`, `80`, `96`, `112`, `128` | `instancesOffset` byte value for TLAS, stepping by 16. | [instance primOffset loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1333-L1338) |
| First vertex leaf | `1` through `8` | `firstVertex` value for indexed triangle geometry, stepping by 1. | [firstVert loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1347-L1355) |
| Transform offset leaf | `16`, `32`, `48`, `64`, `80`, `96`, `112`, `128` | `transformOffset` byte value for triangle geometry, stepping by 16. | [transformOffset loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1368-L1377) |
| Instance count leaf | `1`, `2`, `3`, `4` | `instancesCount` for TLAS `primitive_count`, with `maxInstancesCount` fixed at 4. | [instancesCount loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1294-L1299) |
| SPIR-V target | `spirv1.4` | All generated shaders use `vk::SPIRV_VERSION_1_4`. | [ShaderBuildOptions](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L173) |

## Behavior Parameters

The primary behavioral axis is the build/update mode. Each value is a direct child of `ray_tracing_pipeline.indirect_acceleration_structure` and selects whether the acceleration structure is built once indirectly or built-then-updated indirectly. The geometry type, the field-intermediate node, and the leaf values are identical across the two modes; only the `doUpdate` flag differs.

### build - single indirect acceleration structure build

Builds the BLAS and TLAS once, with the indirect buffer supplying the `VkAccelerationStructureBuildRangeInfoKHR` fields. The vertex/index/AABB/instance data is laid out in a single buffer with the correct data at the offset the indirect field points at, plus padding vertices to keep the build within the buffer range. This is the baseline indirect path: if it fails, the indirect build is not honoring the field, or the shared trace pipeline and result check are suspect.

### update - indirect build followed by in-place update

Builds an intentionally wrong structure first - the indirect fields point at padding or fake geometry - then rebuilds it in-place with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR` so the fields point at the correct geometry. The first build and the update both use the same indirect buffer; for non-indexed triangle, AABB, and instance geometry the update shifts the resolved buffer address by one data block, while for indexed triangle geometry the index buffer address is unchanged and the update instead replaces the vertex buffer content (removing the padding vertices the first build inserted) so the resolved indices land on real vertices. This path exercises whether an indirect update correctly re-reads the indirect fields and rebuilds the structure to match the updated data. The expected result is identical to `build`; only the two-phase build differs.

## Shader Analysis

Shader code is not part of the tested behavior. Two rgen shaders (`wr-asb`, `wr-ast`) only write the `VkAccelerationStructureBuildRangeInfoKHR` struct into a storage buffer so the build can read it indirectly; their contents are baked from the case's `CaseDef` and do not vary the tested property. The probe rgen traces one ray per launch ID straight down the -z axis into the TLAS, and the closest-hit and miss shaders write a fixed `HIT` or `MISS` value into the result image. The intersection shader reports an intersection for AABB geometry. No shader text varies with the build range field or the build/update mode, so no representative shader walkthrough is needed.

## Runtime Execution and Result Checking

### Indirect buffer generation

- Before the build, two small rgen shaders run on the device to fill the indirect buffers. `wr-asb` writes one `VkAccelerationStructureBuildRangeInfoKHR` per BLAS geometry into a storage buffer, baking `primitiveCount`, `primitiveOffset`, `firstVertex`, and `transformOffset` from the case's `CaseDef` [initProgramsHelper wr-asb](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L174-L211). `wr-ast` writes a single struct for the TLAS, baking `instancesCount` and `instancesOffset` [initProgramsHelper wr-ast](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L212-L242).
- The indirect buffers are created with `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT | VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` and are host-visible. `prepareBuffer` builds a one-group ray tracing pipeline, records `cmdTraceRays(1,1,1)`, and submits it to fill the buffer [prepareBuffer](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L933-L999).
- The BLAS indirect buffer holds `geometriesGroupCount` structs and the TLAS indirect buffer holds one struct, both with stride `sizeof(VkAccelerationStructureBuildRangeInfoKHR)` [initIndirectBottomAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1173-L1182) [initIndirectTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1163-L1171).

### Geometry layout and offset arithmetic

- The scene is a `SQUARE_SIZE x SQUARE_SIZE` grid of primitives. Each primitive covers one cell. A deterministic rule (`primId % 7 == 5`) marks certain cells as miss cells by placing their geometry out of the ray path [isMissTriangle](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L59-L63).
- For `primitive_count`, only the first `primitiveCount` primitives are built. Cells whose linear index `n >= primitiveCount` must miss, so the expected value is `MISS` for them [primitive_count loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1272-L1283).
- For `primitive_offset`, the vertex or AABB data is laid out with the real geometry at a byte offset into the buffer. The test negates the offset when setting the buffer address (`setVertexBufferAddressOffset(-m_data.primitiveOffset)`) so the resolved address lands on the real geometry, and adds padding primitives behind it to keep the build in range [non-indexed BLAS offset](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L572-L603) [AABB BLAS offset](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L766-L795).
- For `first_vertex`, the indexed triangle geometry is laid out with fake triangles before the real vertices, and the index values are shifted by `firstVertexReminder` so the resolved `firstVertex` lands on the correct vertices [indexed BLAS firstVertex](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L657-L687).
- For `transform_offset`, the transform-data buffer is laid out with the real transform at a byte offset, and `setTransformBufferAddressOffset(-m_data.transformOffset)` resolves the address [transform offset](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L571) [transform offset loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1368-L1377).
- For `instances`, the TLAS holds `2 * maxInstancesCount + 1` instance slots. Only the first `instancesCount` instances are built via the indirect `primitiveCount`, and the real instances are placed at a byte offset resolved by negating `instancesOffset` [instances TLAS](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L831-L875).

### Update path

- For `update`, the first build points the indirect field at padding or fake geometry. The `doUpdate` flag adds `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR`, builds the wrong structure, then either adjusts the buffer address offset by one data block (non-indexed triangle, AABB, instances) or replaces the geometry via `updateGeometry` to remove the padding vertices (indexed triangle), and calls `build` again in update mode so the field resolves to the correct geometry [non-indexed update](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L615-L624) [indexed update](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L699-L742) [AABB update](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L800-L808) [instances update](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L860-L869).

### Trace and result copyback

- The result image is a 3D `r32ui` storage image sized `width x height x depth`. It is cleared to `(5,5,5,255)` and transitioned to `GENERAL` before the trace [runTest image setup](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1053-L1097).
- `cmdTraceRays` launches `width x height x depth` rays. Each raygen invocation traces one ray down -z into the TLAS; the closest-hit or miss shader writes the per-pixel result into the image [trace dispatch](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1125-L1127).
- After the trace, a `SHADER_WRITE` -> `TRANSFER_READ` barrier, `cmdCopyImageToBuffer`, and a `TRANSFER_WRITE` -> `HOST_READ` barrier move the image into a host-visible buffer [copyback](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1129-L1135).

### Per-pixel result check

- The host scans every pixel across all `depth` slices. The expected value is `HIT` for valid cells whose linear index `n` is not a miss cell and `n < primitiveCount`; otherwise `MISS` [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1195-L1209).
- For triangle geometry, a mismatched pixel always counts as a failure. For AABB geometry, a mismatched pixel is only a failure if the expected value was `HIT` and the observed value was not `HIT`; this tolerates implementation AABB expansion that reports a hit where the test expected a miss [AABB iterate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1235-L1243).
- Pass condition: `failures == 0` [iterate pass/fail](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1211-L1214).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `build` | Indirect build did not honor a `VkAccelerationStructureBuildRangeInfoKHR` field (count or offset), so the built structure does not match the equivalent direct build and the hit/miss pattern is wrong. |
| `update` | Indirect update did not re-read the fields or did not rebuild the structure to match the updated data, so the post-update structure still reflects the intentionally wrong first build. |

All leaves share the indirect-buffer generation, the scene construction, the trace pipeline, and the per-pixel result check, so a failure common to both `build` and `update` for the same geometry type and field points at shared infrastructure (indirect buffer fill, geometry data layout, offset arithmetic, SBT, image copyback, expected-value rule) rather than an update-specific issue. A failure common to all fields for one geometry type points at that geometry type's BLAS or TLAS init path.

### Cause Analysis

#### Indirect build range field ignored or misapplied

**Possible failure symptoms:** A `build` leaf failure where the result image has mismatched pixels. The specific pattern depends on the field. A `primitive_count` failure shows hits where the back of the grid should have been unbuilt (cells with `n >= primitiveCount` report `HIT` instead of `MISS`), or misses across the whole grid if the count was applied to the wrong buffer region. A `primitive_offset` or `transform_offset` failure shows a shifted or empty hit pattern, because the resolved address landed on padding vertices, the wrong transform, or out-of-range memory. A `first_vertex` failure shows hits at wrong cells or a completely empty grid, because the resolved index stream pointed at fake vertices. A `primitive_offset` failure for `instances` shows the wrong number of instances or instances at wrong transforms. The failure count is nonzero.

**Possible implementation causes:** The indirect build reads `VkAccelerationStructureBuildRangeInfoKHR` from the device buffer supplied via `setIndirectBuildParameters`. A grounded investigation should check whether the driver resolved the indirect buffer's device address and stride correctly when recording `vkCmdBuildAccelerationStructuresIndirectKHR`, whether each field was read with the right type and units (`primitiveOffset` and `transformOffset` are byte offsets; `firstVertex` is a vertex index; `primitiveCount` is a primitive count), and whether the resolved vertex/index/AABB/instance/transform buffer addresses plus the field value landed inside the allocated buffer range. The spec ties indirect builds to the `accelerationStructureIndirectBuild` feature; if that feature is reported but the build ignores or misapplies a field, the cause is in the indirect build implementation. If `build` and `update` both fail at the same field and geometry type, the cause is shared offset arithmetic or data layout rather than the build path. If only one field fails, source-level investigation of that field's offset setup in the corresponding `initBottomAccelerationStructure` or `initTopAccelerationStructure` override is needed.

#### Indirect update not re-reading fields or not rebuilding

**Possible failure symptoms:** An `update` leaf failure where the corresponding `build` leaf with the same geometry type and field passes. The result image reflects the intentionally wrong first build rather than the corrected geometry: cells that should be `HIT` are `MISS` (or vice versa), or the whole grid is empty because the first build pointed at padding or fake geometry and the update did not move it. The failure count is nonzero.

**Possible implementation causes:** The `update` path sets `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR` on the first build, then calls `build` again in `VK_BUILD_ACCELERATION_STRUCTURE_MODE_UPDATE_KHR` after either adjusting the buffer address offset (non-indexed triangle, AABB, instances) or replacing the geometry via `updateGeometry` to remove the padding vertices (indexed triangle). The update must re-read the indirect fields and rebuild the structure so the traversal result matches the corrected data. A grounded investigation should check whether the update re-read the indirect buffer at all or reused the first build's resolved parameters, whether the updated buffer address offset (or replaced geometry, for indexed triangle) was applied before the update build, and whether the update mode produced a structure equivalent to a fresh build. The spec states an update rebuilds the structure in-place using the same size and flags; if the implementation treats an indirect update as a no-op or fails to re-resolve the indirect parameters, the post-update structure stays wrong. If `build` passes but `update` fails, the cause is update-path-specific and source-level investigation of the update sequence in the corresponding `initBottomAccelerationStructure` or `initTopAccelerationStructure` override is needed.

#### Shared infrastructure failure

**Possible failure symptoms:** Both `build` and `update` fail for the same geometry type and field with the same pixel pattern, or all fields fail for one geometry type regardless of the field value.

**Possible implementation causes:** The indirect-buffer fill (`wr-asb`/`wr-ast`), the scene construction, the trace pipeline, the SBT, the result image clear and copyback, and the expected-value rule are identical across `build` and `update` and across fields. A failure common to both modes points at this shared setup. A grounded investigation should check whether the `wr-asb`/`wr-ast` rgen shader wrote the `VkAccelerationStructureBuildRangeInfoKHR` struct with the correct field values, whether the indirect buffer's device address was passed correctly to `setIndirectBuildParameters`, whether the deterministic miss-cell placement (`primId % 7 == 5`) produced the expected z-offsets, and whether the per-pixel expected-value rule in `iterate` matches the geometry placement. For `instances`, check that the TLAS instance count and offset arithmetic in `RayTracingBuildInstances::initTopAccelerationStructure` produced the expected valid-instance set. Source-level inspection of `initProgramsHelper` and `iterate` is needed to confirm the indirect-buffer and expected-value correspondence.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline`, with the `accelerationStructure` and `rayTracingPipeline` feature bits set. If either is not set, the test throws `NotSupportedError` [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L519-L529).
- All leaves additionally require `accelerationStructureIndirectBuild`; otherwise the test throws `NotSupportedError` [indirect build feature gate](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L531-L533).
- At instance time, the test checks ray tracing property limits: `maxPrimitiveCount` must cover the case's `primitiveCount`, `maxGeometryCount` must cover `geometriesGroupCount`, and `maxInstanceCount` must cover `instancesCount`. Any shortfall throws `NotSupportedError` [checkSupportInInstance](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1147-L1161).

### Design-based pruning

- `first_vertex` and `transform_offset` are registered only under `triangles_indexed` and `triangles_no_index`, because those fields are triangle-geometry-specific. `aabbs` and `instances` do not receive those field groups [field group registration](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1341-L1381).
- `instances` uses `primitive_count` (instance count) and `primitive_offset` (instance offset) against the TLAS instance buffer, not the BLAS primitive fields, so its field-intermediate nodes have instance-specific semantics [instances field loops](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1288-L1300) [instance primOffset loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1326-L1339).
- The `primitive_count` leaf values step downward from the full grid (`SQUARE_SIZE * SQUARE_SIZE`) by `SQUARE_SIZE`, so the smallest count (`SQUARE_SIZE`) leaves most of the grid unbuilt and must miss. This confirms that `primitiveCount` is honored, rather than only testing a full build [primCount loop](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1272-L1273).

## Key Takeaways

- The `indirect_acceleration_structure` family isolates the indirect build path as the behavioral axis: a single indirect build (`build`) versus an indirect build followed by an in-place update (`update`). The geometry type, the build range field, and the leaf values are identical across both modes.
- The per-field matrix exercises each `VkAccelerationStructureBuildRangeInfoKHR` field independently (`primitiveCount`, `primitiveOffset`, `firstVertex`, and `transformOffset`) against triangles (indexed and non-indexed), AABBs, and instances, so a failure can be attributed to a specific field and geometry type.
- The indirect buffer is filled on the device by two rgen shaders, so the test covers the full device-side indirect path: GPU writes the build range info, the driver reads it during `vkCmdBuildAccelerationStructuresIndirectKHR`, and the result is compared against an expected pattern derived from geometry placement.
- The result check compares a deterministic hit/miss pattern; for AABB geometry it tolerates implementation AABB expansion that produces an extra hit, but not a miss where a hit was expected.
- A failure isolated to `build` points at the indirect build not honoring a field; a failure isolated to `update` points at the update not re-reading the fields; a failure common to both points at shared indirect-buffer or scene infrastructure. See `## Failure Meaning` for the per-mode cause analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `CaseDef` struct | [vktRayTracingBuildIndirectTests.cpp#L74-L89](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L74-L89) | Per-case parameters: primitive count, offsets, first vertex, instance counts, doUpdate |
| `isMissTriangle` | [vktRayTracingBuildIndirectTests.cpp#L59-L63](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L59-L63) | Deterministic miss-cell placement rule |
| `initProgramsHelper` | [vktRayTracingBuildIndirectTests.cpp#L171-L315](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L171-L315) | Generated rgen/chit/miss/rint shaders, including the indirect-buffer writer shaders |
| `RayTracingBuildIndirectTestInstance` | [vktRayTracingBuildIndirectTests.cpp#L398-L427](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L398-L427) | Base instance: non-indexed triangle BLAS, TLAS, indirect buffer setup, iterate |
| `RayTracingBuildTrianglesIndexed` | [vktRayTracingBuildIndirectTests.cpp#L441-L451](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L441-L451) | Indexed triangle BLAS override with first_vertex and index buffer offset |
| `RayTracingBuildAABBs` | [vktRayTracingBuildIndirectTests.cpp#L453-L463](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L453-L463) | AABB BLAS override with AABB-tolerant iterate |
| `RayTracingBuildInstances` | [vktRayTracingBuildIndirectTests.cpp#L465-L479](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L465-L479) | Instance TLAS/BLAS override with instance count and offset |
| `checkSupport` | [vktRayTracingBuildIndirectTests.cpp#L518-L534](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L518-L534) | Feature gates for acceleration structure, ray tracing pipeline, indirect build |
| `initTopAccelerationStructure` (base) | [vktRayTracingBuildIndirectTests.cpp#L536-L555](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L536-L555) | Base TLAS init with indirect build parameters |
| `initBottomAccelerationStructure` (base) | [vktRayTracingBuildIndirectTests.cpp#L557-L632](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L557-L632) | Non-indexed triangle BLAS with primitive/first-vertex/transform offset arithmetic |
| `initBottomAccelerationStructure` (indexed) | [vktRayTracingBuildIndirectTests.cpp#L634-L750](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L634-L750) | Indexed triangle BLAS with first_vertex and index buffer offset |
| `initBottomAccelerationStructure` (AABBs) | [vktRayTracingBuildIndirectTests.cpp#L752-L817](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L752-L817) | AABB BLAS with primitive offset arithmetic |
| `initTopAccelerationStructure` (instances) | [vktRayTracingBuildIndirectTests.cpp#L819-L878](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L819-L878) | Instance TLAS with count and offset arithmetic |
| `initBottomAccelerationStructure` (instances) | [vktRayTracingBuildIndirectTests.cpp#L880-L931](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L880-L931) | Instance BLAS shared by the instances group |
| `prepareBuffer` | [vktRayTracingBuildIndirectTests.cpp#L933-L999](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L933-L999) | Device-side indirect buffer fill via one-group rgen trace |
| `runTest` | [vktRayTracingBuildIndirectTests.cpp#L1001-L1145](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1001-L1145) | AS build, trace dispatch, and result copyback |
| `checkSupportInInstance` | [vktRayTracingBuildIndirectTests.cpp#L1147-L1161](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1147-L1161) | Runtime property-limit pruning |
| `iterate` (base) | [vktRayTracingBuildIndirectTests.cpp#L1184-L1215](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1184-L1215) | Per-pixel expected-value rule and pass/fail condition |
| `iterate` (AABBs) | [vktRayTracingBuildIndirectTests.cpp#L1217-L1250](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1217-L1250) | AABB-expansion-tolerant result check |
| `addIndirectTests` | [vktRayTracingBuildIndirectTests.cpp#L1256-L1387](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1256-L1387) | Per-geometry-type and per-field matrix generation |
| `createBuildIndirectTests` | [vktRayTracingBuildIndirectTests.cpp#L1254-L1401](../../../modules/vulkan/ray_tracing/vktRayTracingBuildIndirectTests.cpp#L1254-L1401) | Registration of the build and update direct children |