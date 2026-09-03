# Understanding Brief: EXT mesh-shader synchronization

## One-Sentence Test Purpose

This test checks whether `VK_EXT_mesh_shader` synchronization makes a value written by one host, transfer, or shader stage observable at a later task, mesh, fragment, transfer, or host stage when the selected barrier and access masks describe that handoff.

## Background Knowledge

### Memory dependencies and access scopes

A Vulkan memory dependency combines execution ordering with availability and visibility. The source stage and source access mask identify writes that become available; the destination stage and destination access mask identify later accesses that can see them. A pipeline barrier applies this relationship to commands before and after it, while a subpass dependency applies it between render-pass subpasses. An image dependency also carries an old-to-new layout transition.

Why it matters here:
- The test deliberately changes both stage masks and access masks, so a barrier with the wrong pair is a different case, not interchangeable boilerplate.
- The tested resource can be a buffer or image. Image layout is part of the synchronization contract.

### Mesh-shader graphics execution

A task shader can launch mesh work through `EmitMeshTasksEXT`; a mesh shader emits primitives for rasterization; a fragment shader can produce the final color. The EXT test can also place a resource operation in a transfer or host operation, so not every stage in a case is a shader stage.

Why it matters here:
- A task-to-mesh or mesh-to-fragment case can run in one graphics pipeline, whereas reverse shader order such as mesh-to-task requires two pipelines.
- A fragment-to-task or fragment-to-mesh case uses a first pipeline for the write and a second pipeline for the read, with passthrough stages supplying the rest of the graphics path.

## One Concrete Example

Consider `dEQP-VK.mesh_shader.ext.synchronization.host_to_task.storage_buffer.memory_barrier.host_write_shader_read`. The host writes `1628510124` to a host-visible storage buffer and flushes the allocation. The command buffer records a host-to-task memory barrier. The task shader reads `sb.value` when its push constant enables reading, copies it to task payload, and launches one mesh workgroup. The mesh shader passes the payload to a fragment shader, which writes it into the `VK_FORMAT_R32_UINT` color attachment. The test copies the 1x1 color image to a host-coherent verification buffer and compares the returned `uint32_t` with the original value.

The example is a concrete CTS path, not a substitute for the other stage, resource, barrier, and access combinations.

## End-to-End Test Flow

```text
[host] select one registered stage pair, resource type, barrier type, write access, and read access
[host] create the 1x1 resource image or 4-byte host-visible resource buffer, descriptor set, render pass, framebuffer, and generated task/mesh/fragment programs
[host] write or transfer the test value into the source resource and record any required source layout transition
[host] record the main memory, buffer, image, or render-pass dependency with the selected stage and access masks
[device] execute one or two graphics pipelines and one or two render-pass subpasses as required by the stage order and barrier form
[device] read or write the selected resource at the destination stage and route the value to a host, transfer, or color-buffer result
[host] submit the primary command buffer and wait for completion
[host] invalidate or read the host-visible result and compare it with the selected test value
[host] report pass or fail
```

The `other` family has a separate flow:

```text
[host] fill and flush host-visible output and verification buffers
[host] record compute work in one secondary command buffer, followed by a compute-to-task memory barrier
[host] record task and mesh work in a graphics secondary command buffer
[host] execute both secondary command buffers from a primary command buffer, then record a task-to-host barrier
[device] compute writes each index, and task reads it and writes 1 or 0 to the verification buffer
[host] invalidate the verification buffer and compare every element with 1
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Regular cases generate task, mesh, and fragment GLSL strings with `VK_EXT_mesh_shader`. The task shader is included only when the stage pair uses task execution. Passthrough task, mesh, and fragment modules fill stages that are not the selected producer or consumer.
- The graphics setup uses one pipeline for ordinary forward or host/transfer cases. Shader-to-shader cases can use two pipelines; a dependency barrier uses two subpasses, while other barrier forms can use two render passes.
- The `other` case generates a compute shader, a task shader, and a zero-output mesh shader. Its compute local size is 128 and it dispatches 16,384 workgroups.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Main resource buffer | yes | yes, binding 0 | uniform or storage read; storage write where legal | directly for host destination cases | Carries the 32-bit synchronization value for buffer cases. |
| Main resource image | yes, 1x1 `VK_FORMAT_R32_UINT` | yes, binding 0 | storage-image or sampled-image read/write where legal | copied through an auxiliary buffer for transfer destinations | Exercises image access masks and layout transitions. |
| Auxiliary host-coherent buffer | yes, only when transfer is a source or destination | yes for copy commands | transfer read/write | yes | Keeps host preparation or copyback outside the main synchronization signal. |
| Color attachment and verification buffer | yes, for shader destinations | color attachment, then transfer destination | fragment output writes; copy reads | yes | Carries a shader-stage result back to the host. |
| `other` output and verification buffers | yes, host-visible storage buffers | bindings 0 and 1 | compute writes output; task reads output and writes verification | yes | Makes every compute-to-task observation independently checkable. |
| Descriptor set and push constants | yes | yes | shaders read the resource and `writeVal`/`readVal` controls | no | Binding 0 exposes the selected resource; push constants gate read/write instructions for self-dependency draws. |

## What Is Checked

- The regular test uses the value `1628510124` initially, increments it for each generated case, and expects the same value at the destination.
- A host destination reads the host-visible resource buffer after invalidation. A transfer destination reads an auxiliary host-coherent buffer after a transfer-to-host barrier. A shader destination copies the 1x1 `R32_UINT` color attachment to a host-coherent buffer and compares its first `uint32_t`.
- The `other` case expects `1` in all `128 * 16384` verification entries. Each task invocation writes `1` only when the compute-produced index equals `gl_GlobalInvocationID.x`.
- Any mismatch raises a CTS failure with an unexpected-value message. A successful command submission alone is not enough; the observable value must match.

## Behavior Parameter Identification

> **Behavior parameter:** stage pair, the primary axis for this multi-family page
>
> **Candidate values:** `host_to_task`, `host_to_mesh`, `transfer_to_task`, `transfer_to_mesh`, `task_to_mesh`, `task_to_frag`, `task_to_transfer`, `task_to_host`, `mesh_to_frag`, `mesh_to_transfer`, `mesh_to_host`, `mesh_to_task`, `frag_to_task`, `frag_to_mesh`, and the separate `other` family

The stage pair changes which operation produces the value, which operation consumes it, which shader pipeline is needed, and where the result becomes observable. Resource, barrier, and access dimensions refine that behavior. The `other` family is a fixed secondary-command-buffer case rather than a member of the regular Cartesian matrix.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `host_to_task`, `host_to_mesh` | Host flush, host-to-shader dependency, descriptor/resource visibility, or task/mesh read path failure. |
| `transfer_to_task`, `transfer_to_mesh` | Host-to-transfer preparation, transfer-to-shader dependency, image layout, descriptor/resource visibility, or shader read path failure. |
| `task_to_mesh`, `task_to_frag`, `mesh_to_frag` | Shader write-to-read dependency, render-pass dependency, storage resource access, or stage-specific shader path failure. |
| `task_to_transfer`, `mesh_to_transfer` | Shader-to-transfer dependency, image copy/layout handling, or auxiliary readback path failure. |
| `task_to_host`, `mesh_to_host` | Shader-to-host dependency, host-visible storage-buffer writeback, or host invalidation/readback failure. |
| `mesh_to_task`, `frag_to_task`, `frag_to_mesh` | Two-pipeline ordering, reverse-stage dependency, or passthrough/selected shader path failure. |
| `other.barrier_across_secondary` | Secondary-command-buffer execution ordering, compute-to-task barrier, task verification writes, or task-to-host readback failure. |

## Important Variations and Special Cases

- `memory_barrier`, `specific_barrier`, and `subpass_dependency` select a general memory barrier, a buffer/image-specific barrier, or a render-pass dependency. The dependency form is generated only for shader-to-shader pairs.
- Uniform buffers cannot be shader-written, and only uniform-buffer cases accept `uniform_read`. Host stages accept only uniform or storage buffers; shader stages can read all four resource kinds, but shader writes accept only storage buffers and storage images.
- Transfer source or destination cases allocate a host-visible, host-coherent auxiliary buffer. This avoids adding an extra host-memory synchronization step to the behavior being tested.
- Shader-to-shader cases that run in reverse pipeline order or use a barrier rather than a dependency require two pipelines. A dependency form can instead use two subpasses and a self-dependency general barrier where Vulkan forbids buffer/image-specific barriers inside the render pass.
- All regular cases require `VK_EXT_mesh_shader`, mesh support, and task support when the pair uses a task stage. Shader writes also require the core vertex-pipeline-stores-and-atomics feature. The `other` case requires both task and mesh support plus that same core feature.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Regular parameter enums and legality predicates | [stage/resource/access helpers](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L58-L411) | Defines the supported stages, resources, barriers, access types, and legal combinations. |
| Generated regular shaders | [regular shader generation](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L657-L799) | Shows task payload, resource declarations, reads, writes, and passthrough stages. |
| Regular render-pass and pipeline selection | [render-pass construction](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L832-L905), [pipeline selection](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1142-L1215) | Shows dependency subpasses, two-pipeline rules, and stage-specific modules. |
| Regular execution and checks | [regular iterate](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L919-L1539) | Shows resource setup, barriers, command recording, submission, copyback, and comparisons. |
| Secondary-command-buffer case | [secondary case](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1542-L1768) | Shows compute-to-task synchronization across secondary buffers and full-buffer checking. |
| Registration and pruning | [EXT registration](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772-L1918) | Shows exact stage/resource/barrier/access loops, pruning predicates, test value generation, and `other`. |
| Mustpass | [vk-default mesh-shader mustpass](../../../mustpass/main/vk-default/mesh-shader.txt#L26810-L26890) | Confirms the exact 81 EXT synchronization paths present in the default mustpass. |
| Synchronization semantics | [Vulkan synchronization](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-dependencies-memory) | Defines availability, visibility, access scopes, and memory dependencies. |
| Pipeline barriers | [pipeline barriers](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-pipeline-barriers) | Defines before/after command scopes for `vkCmdPipelineBarrier`. |
| Subpass dependency semantics | [VkSubpassDependency](../../../../vulkan-docs/src/chapters/renderpass.adoc#vksubpassdependency) | Defines source/destination subpass, stage, and access scopes. |

## Questions / Risk Points for User Audit

- Is the stage pair clear as the primary behavior axis while the `other` family remains visibly separate?
- Are the buffer versus image result paths and the host/transfer auxiliary-buffer role clear?
- Are the two-pipeline and subpass-dependency exceptions understandable without reading the implementation?
- Should a final page include a second walkthrough for the two-pipeline reverse-stage path, or is the regular task read path sufficient?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page explanation-first. Use the regular stage-pair matrix as the primary behavior axis and preserve `other` as an auxiliary fixed family.
- Distill the memory-dependency and mesh-pipeline background to short prerequisite bullets.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write fresh cause analysis with observable symptoms and source/spec-grounded possible implementation causes.
- Use the concrete `host_to_task` path for a single shader walkthrough. A second walkthrough is optional only if the two-pipeline reverse-order path materially improves the reader's understanding.
- Keep exact registered names and the 81-case default-mustpass count; do not expand every generated leaf in the hierarchy tree.
