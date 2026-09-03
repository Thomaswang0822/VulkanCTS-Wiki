# Understanding Brief: EXT mesh shader API draw tests

## One-Sentence Test Purpose

This test checks whether the `VK_EXT_mesh_shader` draw, indirect draw, and indirect-count commands correctly launch the requested mesh workgroups from direct parameters, buffers, or device addresses.

## Background Knowledge

### Mesh and task workgroups

A mesh draw assembles a global workgroup grid from three group counts. Without a task shader, those workgroups run the mesh shader directly. With a task shader, each task invocation emits mesh workgroups through `EmitMeshTasksEXT`; the payload can carry per-draw and per-row information to the mesh shader. The EXT specification describes both the task-to-mesh relationship and the `OpSetMeshOutputsEXT` contract in [mesh.adoc](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L12-L19).

Why it matters here:
- The test moves the group count between direct command arguments and indirect command structures.
- The task path must preserve the draw number and workgroup coordinate while emitting one mesh workgroup per row.

### Indirect command addressing

`vkCmdDrawMeshTasksIndirectEXT` reads `VkDrawMeshTasksIndirectCommandEXT` structures from a buffer. `drawCount` selects how many structures the command reads and `stride` separates them; a zero stride is meaningful only when at most one draw is read. The count form reads a 32-bit count from another indirect buffer and executes the smaller of that value and `maxDrawCount`. The device-address forms use address ranges instead of buffer handles. See [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2519-L2579) and [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2634-L2717).

Why it matters here:
- Offset, stride, count-buffer offset, and maximum-count combinations exercise the address calculations and bounds rules.
- The device-address variants test the same draw semantics through `VkDrawIndirect2InfoKHR` and `VkDrawIndirectCount2InfoKHR`.

## One Concrete Example

For `dEQP-VK.mesh_shader.ext.api.draw.draw_count_1.no_indirect_args.no_count_limit.no_count_offset.no_task_shader`, the command issues one mesh workgroup. The mesh shader uses 32 local invocations, sets 96 vertices and 32 triangle primitives, and puts one triangle around each of the 32 framebuffer columns. It colors each primitive with its normalized row and column. Since there is no task shader, the mesh workgroup coordinate supplies the row directly.

The test uses a 32 by 64 `VK_FORMAT_R8G8B8A8_UNORM` color attachment. The host reference image expects the first row for `draw_count_1` to contain the generated colors and all remaining rows to retain the clear color.

## End-to-End Test Flow

```text
[host] choose draw type, draw count, indirect layout, task mode, command-buffer mode, and seed
[host] create a 32x64 color image, framebuffer, block-size storage buffer, descriptor set, pipeline layout, and graphics pipeline
[host] generate the EXT task shader when requested, plus the mesh and fragment shaders
[host] build indirect and count buffers when the selected command needs them; query device addresses for address commands
[host] begin a render pass and record bindings, push constants, and one direct, indirect, or indirect-count mesh draw
[host] optionally record the draw in a render-pass-continuing secondary command buffer and execute it from the primary
[device] run task workgroups when enabled, then run mesh workgroups and rasterize the generated triangles
[host] copy the color image into a host-visible buffer and wait for queue completion
[host] construct the expected image and compare every pixel with a 0.005 threshold
[host] return pass or fail based on the image comparison
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms` emits GLSL for an optional `TaskEXT` stage, a `MeshEXT` stage, and a fragment stage. `getMinMeshEXTBuildOptions` targets SPIR-V 1.4.
- The task shader uses `EmitMeshTasksEXT(pc.one, pc.one, pc.one)` and writes `gl_DrawID` plus the selected workgroup coordinate into `taskPayloadSharedEXT`.
- The mesh shader reads the payload only in task cases. Without a task shader it uses `gl_DrawID` as the block number and the mesh workgroup coordinate as the row.
- The host creates indirect command structures from randomized block sizes. Each block partitions the 64 framebuffer rows, and the extra indirect-buffer padding keeps the final addressable range valid.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `colorBuffer` image and view | yes | yes, as color attachment | written by rasterization | copied to `outBuffer` | Captures the per-row and per-column colors. |
| `blockSizesBuffer` | yes | yes, descriptor set 0 binding 0 | read by the mesh shader | no | Maps each draw block to its first framebuffer row. |
| indirect buffer | yes, indirect cases | yes, as indirect input | read by the command processor | no | Stores `VkDrawMeshTasksIndirectCommandEXT` records at the selected offset and stride. |
| count buffer | yes, count cases | yes, as indirect input | read by the command processor | no | Stores the selected count at the selected count offset. |
| push constants | yes | yes, mesh and optionally task stages | read by shaders | no | Carries extent, selected coordinate dimension, and the task emission count. |
| `outBuffer` | yes | transfer destination | written by image copy | yes | Supplies pixels for the host comparison. |
| `taskPayloadSharedEXT td` | no, shader-local workgroup payload | passed from task to mesh | written by task, read by mesh | no | Carries draw number and row coordinate; it is not a host-created descriptor resource. |

## What Is Checked

- `blockSizes` partitions the 64 rows. The mesh shader computes `row = startOfBlock(blockNumber) + blockRow` and writes a color whose red component is the row center and whose green component is the column center.
- For `draw_count_0`, or for rows beyond `draw_count` in a direct draw, the reference remains the clear color. Indirect and indirect-count cases use their generated command records to cover the full image whenever the selected draw count is nonzero.
- The host invalidates the readback allocation and compares the complete image with `tcu::floatThresholdCompare` using a `0.005` threshold. A mismatch returns `Image comparison failed; check log for details`; otherwise the case passes.

## Behavior Parameter Identification

> **Behavior parameter:** draw command family and its command-data source
>
> **Candidate values:** `draw`, `draw_indirect`, `draw_indirect_count`, with ordinary buffer forms and selected `VK_KHR_device_address_commands` forms

The direct, indirect, and indirect-count families change how the device obtains workgroup counts. Task use, secondary command buffers, offset/stride, count source, and device-address use are execution variants layered over that primary axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `draw` | Direct EXT mesh-task group-count handling, task/no-task launch behavior, or mesh output and image validation. |
| `draw_indirect` | Indirect command-buffer offset, stride, multi-draw, or device-address interpretation. |
| `draw_indirect_count` | Count-buffer or count-address interpretation, `maxDrawCount` limiting, indirect layout, or device-address count handling. |

## Important Variations and Special Cases

- `draw_count_0`, `draw_count_1`, `draw_count_2`, `draw_count_32`, and `draw_count_64` are the registered count values. The direct family uses these as task/workgroup counts; indirect families use them as the number of indirect draw records or the maximum count.
- Indirect records use offset `0` or `20`, and stride `0`, `sizeof(VkDrawMeshTasksIndirectCommandEXT)`, or `2 * sizeof(VkDrawMeshTasksIndirectCommandEXT) + 4`. The source filters stride zero when more than one record is consumed and for all indirect-count cases.
- Indirect-count cases use count-buffer offsets `0` or `20` and either the buffer value or `maxDrawCount` as the limiting source. The buffer-value case stores `drawCount`; the max-count case stores `drawCount + 1` and limits execution to `drawCount`.
- Every ordinary case has `no_task_shader` or `with_task_shader`, and an inline or `_secondary_cmd` recording path. Device-address cases are deliberately sampled rather than added to every combination.
- For sampled address cases, the source sets valid address flags. The indirect form uses `VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR` for multiple draws and `VK_ADDRESS_COMMAND_FULLY_BOUND_BIT_KHR` otherwise. The count form varies flags for the indirect and count ranges, omitting some flags in task cases or single-draw cases.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registered matrix | [createMeshShaderApiTestsEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L783-L951) | Defines all dimensions, filters, names, and address-case sampling. |
| Parameters and shader branches | [TestParams and initPrograms](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L98-L341) | Defines the behavioral inputs and generated task/mesh/fragment stages. |
| Support gates | [MeshApiCase::checkSupport](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L343-L359) | Requires EXT mesh support, draw-indirect-count support, multi-draw-indirect when needed, and device-address commands when selected. |
| Resources and command recording | [MeshApiInstance::iterate](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L422-L744) | Creates resources, records all five command paths, and submits them. |
| Image checking | [reference image comparison](../../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L746-L778) | Defines clear-color behavior, tolerance, and pass/fail. |
| EXT mesh semantics | [Mesh shading](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L12-L166) | Specifies task emission, payload transfer, and mesh output rules. |
| Draw command semantics | [mesh draw commands](../../../../vulkan-docs/src/chapters/drawing.adoc#L2484-L2717) | Specifies direct, indirect, count, and address-range behavior. |
| Indirect validity | [draw count rules](../../../../vulkan-docs/src/chapters/commonvalidity/draw_indirect_drawcount.adoc#L7-L12), [count rules](../../../../vulkan-docs/src/chapters/commonvalidity/draw_indirect_count_common.adoc#L7-L25) | Grounds multi-draw, alignment, count, and bounds constraints. |

## Questions / Risk Points for User Audit

- Does the distinction between `drawCount` as a direct group count, indirect record count, and count-command maximum remain clear?
- Is the intentional sampling of device-address cases clear enough without implying that every matrix combination has an address variant?
- Should the final page include a full generated shader walkthrough, or is the compact shader summary sufficient for this host/API-focused page?
- Does the 2026 Android mustpass reduction need to be called out separately from the canonical `vk-default` coverage?

## Conversion Notes for Final Wiki Rewrite

- Keep `## Background Knowledge` to the mesh task/mesh relationship and indirect address semantics; move concrete dimensions to the parameter section.
- Carry the behavior axis and the failure mapping table into the final page unchanged.
- Include one representative mesh shader walkthrough for a direct draw. The source-generated fragment shader is fixed and can remain in the runtime explanation rather than receiving a second walkthrough.
- Explain the matrix as dimensions plus exact default coverage, not as a 540-row listing.
- Keep support gates, secondary command-buffer recording, address flags, image comparison, and the source appendix linked to the implementation ranges.
