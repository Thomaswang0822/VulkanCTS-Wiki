# Understanding Brief: NV mesh-shader synchronization

## One-Sentence Test Purpose

This test checks whether Vulkan memory dependencies make a value written by one selected stage available to the next selected stage when NV mesh-shader work uses buffers or images.

## Background Knowledge

### Execution and memory dependencies

Vulkan separates execution ordering from memory visibility. A memory dependency combines an execution dependency with availability and visibility operations. The source stage makes its writes available, and the destination stage can then see them through the destination access scope. The synchronization chapter describes this model in [Execution and Memory Dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-dependencies).

Why it matters here:
- The test names the source and destination stages explicitly, then supplies matching source and destination access masks.
- A missing or incorrectly scoped dependency can leave the destination stage reading a stale value even when command order is defined.

### NV mesh-shader stages and resources

The implementation treats `host`, `transfer`, `task`, `mesh`, and `frag` as the stage vocabulary. Task and mesh shaders use `VK_NV_mesh_shader`; a task shader emits one mesh workgroup and passes a `TaskData` value to the mesh shader. The resource is one descriptor at set 0, binding 0: a uniform buffer, storage buffer, storage image, or sampled image.

The test uses a real buffer or image for the synchronization target. The task-to-mesh and other shader-to-shader cases use render-pass subpass dependencies because both accesses occur in shader stages. A regular pipeline barrier carries the selected stage and access masks for the other cases. Vulkan describes global memory barriers, buffer memory barriers, image memory barriers, and render-pass dependencies in the [synchronization chapter](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-pipeline-barriers).

## One Concrete Example

Consider `dEQP-VK.mesh_shader.nv.synchronization.host_to_mesh.uniform_buffer.memory_barrier.host_write_uniform_read`:

1. The host writes `1628510124u` into a host-visible uniform buffer and flushes its allocation.
2. The command buffer records a global memory barrier from `VK_PIPELINE_STAGE_HOST_BIT` and `VK_ACCESS_HOST_WRITE_BIT` to the mesh stage and `VK_ACCESS_UNIFORM_READ_BIT`.
3. The mesh shader reads `ub.value` when `pc.readVal` is enabled, places that value in `primitiveValue[0]`, and emits one triangle.
4. The fragment shader writes the flat primitive value to a one-pixel `VK_FORMAT_R32_UINT` color attachment.
5. The host copies the color attachment to a host-coherent verification buffer and compares the first `uint32_t` with the test value.

This is a concrete source-backed case. The source emits the resource declaration and read statement in [TestParams](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L416-L515), generates the mesh and fragment shaders in [initPrograms](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L620-L698), and records the selected barrier in [iterate](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1093-L1127).

## End-to-End Test Flow

```text
[host] choose one registered stage pair, resource, barrier form, and access pair
[host] create the one-byte-value buffer or 1x1 R32_UINT image and descriptor
[host] write the test value directly or place it in an auxiliary host-coherent buffer
[host] record any host-to-transfer or image-layout barrier needed for setup
[host] record the selected memory, buffer, or image dependency; shader-to-shader cases use a render-pass subpass dependency and two draws
[device] task or mesh shader writes or reads the resource when controlled by push constants
[device] fragment shader or transfer command carries the observed value toward a check buffer
[host] wait for submission, invalidate non-coherent allocations when needed, and read the selected result buffer
[host] compare the observed uint32 value with the case's test value and decide pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The case generates a task shader only when the stage pair contains `task`. It sets `gl_TaskCountNV = 1u` and passes `TaskData.value` to mesh.
- The mesh shader always exists. It emits one triangle and reads or writes the selected resource only when mesh participates in the pair.
- The fragment shader always exists. It writes the per-primitive value to `outColor`, and it reads the selected resource only when `frag` is the destination.
- A push-constant block contains `writeVal` and `readVal`. Ordinary cases set both to 1; shader-to-shader cases use one draw with only write enabled, a generic barrier, then one draw with only read enabled.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Uniform buffer | yes | yes, set 0 binding 0 | read by shader only | no | Tests uniform-read visibility; it cannot receive a shader write. |
| Storage buffer | yes | yes, set 0 binding 0 | read or written by transfer/task/mesh/frag as allowed | yes for transfer or host destinations | Carries the scalar value through buffer barriers and host-visible checks. |
| Storage image | yes, 1x1 `VK_FORMAT_R32_UINT` | yes, set 0 binding 0 | read or written by transfer/task/mesh/frag as allowed | yes through image-to-buffer copy | Exercises image layout and image memory barriers. |
| Sampled image | yes, 1x1 `VK_FORMAT_R32_UINT` plus sampler | yes, set 0 binding 0 | transfer writes it; shader samples it | indirectly through color verification | Exercises transfer-to-shader visibility using a sampled-image read. |
| Auxiliary host-coherent buffer | yes, only when either endpoint is transfer | no descriptor in the shader | transfer source or destination | yes | Avoids adding a non-coherent host flush/invalidate dependency to transfer cases. |
| Color attachment and color verification buffer | yes for shader destinations other than host or transfer | color attachment, then transfer destination | fragment output is copied to the buffer | yes | Provides the observable result for task, mesh, and fragment destinations. |

## What Is Checked

- The test value is a per-case `uint32_t`, starting at `1628510124u` and incremented as registration cases are built.
- A transfer destination is checked in the auxiliary host-coherent buffer after `vkCmdCopyBuffer` or `vkCmdCopyImageToBuffer` and a transfer-to-host barrier.
- A host destination is checked in the resource buffer after invalidation.
- A task, mesh, or fragment destination is checked in the color verification buffer after a color-attachment-to-transfer barrier and image copy.
- Every selected result must equal the case's test value. Any mismatch produces `Unexpected value ... found ... and expected ...` and fails the test.

## Behavior Parameter Identification

> **Behavior parameter:** stage-pair/resource/barrier/access combination
>
> **Candidate values:** `host_to_task`, `host_to_mesh`, `transfer_to_task`, `transfer_to_mesh`, `task_to_mesh`, `task_to_frag`, `task_to_transfer`, `task_to_host`, `mesh_to_frag`, `mesh_to_transfer`, `mesh_to_host`; resources `uniform_buffer`, `storage_buffer`, `storage_image`, `sampled_image`; barriers `memory_barrier`, `specific_barrier`; registered access-pair leaves such as `host_write_uniform_read`, `transfer_write_shader_read`, `shader_write_shader_read`, `shader_write_transfer_read`, and `shader_write_host_read`.

The primary behavioral axis is the complete synchronization scenario, with the stage pair choosing the producer and consumer and the remaining registered dimensions selecting the resource and synchronization scope being exercised.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `host_to_task`, `host_to_mesh` | Host-domain write not made visible to the selected shader access; incorrect host-to-device stage or access scope; resource setup problem. |
| `transfer_to_task`, `transfer_to_mesh` | Transfer write not made visible to shader or uniform access; incorrect image layout or transfer barrier; copy setup problem. |
| `task_to_mesh`, `task_to_frag` | Shader-to-shader dependency or render-pass subpass dependency does not make the task write visible to the consumer. |
| `task_to_transfer`, `mesh_to_transfer` | Shader write is not visible to the copy, or the image/buffer copy and transfer-to-host path is incorrect. |
| `task_to_host`, `mesh_to_host` | Shader write is not visible to the host, or host invalidation/readback is incorrect. |
| `mesh_to_frag` | Mesh write is not visible to the fragment read, or the fragment/color readback path is incorrect. |


## Important Variations and Special Cases

- Host writes can target only uniform and storage buffers. Host reads can target only uniform and storage buffers.
- Task and mesh shaders can write only storage buffers and storage images. Fragment is a read destination in the registered stage pairs, not a writer in the matrix.
- Shader stages accept `shader_read` or `uniform_read`; only a uniform buffer accepts `uniform_read`.
- Shader-to-shader combinations use two draws and a generic memory barrier inside one render pass. Specific buffer or image barriers are pruned because Vulkan validity rules forbid those barrier forms inside this render-pass position for the tested resources.
- The implementation keeps images in `GENERAL` when shader writes, storage images, or generic barriers make that choice necessary; otherwise it uses shader-read-only or transfer layouts as appropriate.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Stage, resource, barrier, and access enums | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L57-L228) | Defines exact implementation dimensions and Vulkan flag mappings. |
| Combination legality and auxiliary-result rules | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L230-L365) | Shows support for each stage/resource/access and result location. |
| Support gates and generated shaders | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L610-L698) | Shows NV extension, task/mesh feature, shader-write feature, and emitted code. |
| Render-pass dependency and barriers | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L722-L795) | Shows shader-to-shader subpass dependency and host/transfer helper barriers. |
| Resource setup and execution | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L797-L1277) | Shows images, buffers, descriptors, layout transitions, draws, copies, and submit. |
| Result checks | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1279-L1327) | Shows exact host-side comparisons and failure messages. |
| Registration matrix and pruning | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332-L1453) | Shows the 11 stage pairs, four resources, barriers, accesses, and skip predicates. |
| NV support helper | [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L124) | Requires `VK_NV_mesh_shader` and requested task/mesh features. |
| Vulkan synchronization model | [synchronization.adoc](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-dependencies) | Defines execution, availability, visibility, and access scopes. |
| Pipeline barriers | [synchronization.adoc](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-pipeline-barriers) | Defines global, buffer, and image barrier behavior. |

## Questions / Risk Points for User Audit

- Is the complete synchronization scenario the right primary behavior axis, rather than stage pair alone?
- Is the distinction between a real resource and the auxiliary host-coherent copy buffer clear?
- Does the two-draw shader-to-shader explanation make the subpass-dependency placement clear?
- Are the duplicate mapping rows for transfer and host destinations useful, or should the final page merge them?
- Should the final page include one representative host-to-mesh shader walkthrough and shorter source-backed walkthroughs for transfer-to-mesh and task-to-mesh?

## Conversion Notes for Final Wiki Rewrite

- Distill the dependency model to a short prerequisite list and keep the concrete host-to-mesh example in the final page as the first representative walkthrough.
- Keep the full registered hierarchy in one compact tree, then move the large matrix to the parameter section.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write fresh cause analysis for each distinct destination/check path.
- Explain support gates and pruning together with the exact registration predicates, including the shader-to-shader specific-barrier exclusion.
- Include at most three source-backed walkthroughs. Prefer host-to-mesh uniform read, transfer-to-task sampled-image read, and task-to-mesh storage-buffer write/read as the three distinct flows if the generated shader artifacts remain practical.
