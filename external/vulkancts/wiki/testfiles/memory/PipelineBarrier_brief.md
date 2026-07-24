# Understanding Brief: `memory.pipeline_barrier`

## One-Sentence Test Purpose

The test family checks whether legal pipeline barriers, host cache operations, and image layout transitions preserve data across randomized host and device access sequences that use one Vulkan memory allocation through buffers and images.

## Background Knowledge

### Availability, visibility, and execution order

A Vulkan memory dependency combines execution ordering with availability and visibility operations. Availability makes prior writes available to a memory domain; visibility makes those values visible to later access types. Stage masks define the execution scopes, while access masks define the memory-access scopes. Host access to non-coherent memory also needs explicit flush or invalidate operations.

### One allocation, several resource views

The test binds temporary buffers or optimal-tiled RGBA8 images to one selected device-memory allocation. A reference-memory model follows each write, copy, draw, and host access. Barriers may be global, buffer-specific, or image-specific; image barriers can also change layout.

## One Concrete Example

For `dEQP-VK.memory.pipeline_barrier.host_write_storage_buffer.1024`, a randomized sequence can map the 1024-byte allocation, write a deterministic byte pattern, flush it when required, create and bind a storage buffer, issue a pipeline barrier whose source and destination scopes cover the pending dependency, and draw with a shader that reads packed positions from that buffer. The rendered pixels encode the bytes observed by the shader and are checked against the reference model.

## End-to-End Test Flow

1. Registration selects a usage set, allocation size, and, where needed, vertex stride.
2. The instance walks every compatible, non-protected memory type. Host-access cases require host-visible memory.
3. For each memory type, five deterministic seeds each generate 50 legal operations from a state machine.
4. Commands create, bind, map, write, copy, render, transition layouts, flush, invalidate, wait, and insert global, buffer, or image pipeline barriers.
5. The state model permits a read only after the required execution and memory dependencies have made the expected data valid for that access.
6. Commands execute, the device becomes idle, and each command updates or checks a host reference model.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`AddPrograms::init()` adds vertex and fragment programs only for usages that require graphics-pipeline reads. It covers vertex and index fetch, uniform and storage buffers, uniform and storage texel buffers, storage images, and sampled images. Cases with only host and transfer access do not use shaders. No explicit `vk::ShaderBuildOptions` appears, so these programs use the `vk::SourceCollections` baseline SPIR-V target, SPIR-V 1.0.

### Bound resources and memory objects

- One `VkDeviceMemory` allocation uses the selected memory type and registered byte size.
- Temporary buffers expose the enabled transfer, vertex, index, uniform, storage, or texel-buffer usages.
- Optimal-tiled `VK_FORMAT_R8G8B8A8_UNORM` images expose enabled transfer, storage-image, or sampled-image usages when the allocation can support them.
- Render targets convert shader-observed data into pixels that command verification can compare with reference pixels.
- Descriptor set binding 0 carries uniform buffers, storage buffers, texel-buffer views, storage images, or combined image samplers in the relevant graphics commands.

## What Is Checked

Every read command compares observed bytes or pixels with the reference state produced by preceding writes and transformations. Host reads compare mapped bytes. Transfer readback and rendering commands compare copied or rendered data. Preparation, execution, or verification exceptions also fail the result collector. The case passes only after all supported memory types and all five randomized iterations finish without a mismatch or command failure.

## Behavior Parameter Identification

> **Proposed primary behavioral axis:** access-domain and consumer-mechanism group (a behavioral grouping of the registered usage-pair intermediate nodes, plus `all` and `all_device`)
>
> **Candidate values:** `host-to-host`, `host-to-device`, `device-to-host`, `device-to-device`, `all`, `all_device`

The registered usage-pair names remain exact inventory values. This grouping is the useful behavior axis because it changes the required memory-domain handoff and the mechanism that consumes the data; size and vertex stride change stress or data layout without changing the synchronization question.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `host-to-host` | Host cache management or host-stage dependency does not preserve the expected bytes. |
| `host-to-device` | Host writes do not become available and visible to the selected transfer, vertex-input, or shader read. |
| `device-to-host` | Device transfer writes do not become visible to the host read after submission and invalidation. |
| `device-to-device` | Transfer writes do not become visible to the selected transfer, vertex-input, or shader read. |
| `all` | A mixed host/device command sequence fails in barrier scope, cache maintenance, image layout handling, or resource interpretation. |
| `all_device` | A device-only mixed command sequence fails in barrier scope, image layout handling, or resource interpretation. |

## Important Variations and Special Cases

- Pair groups combine `HOST_WRITE` or `TRANSFER_DST` with ten read usages. `usageToName()` orders tokens by its table, so `host_read_transfer_dst` still means a transfer destination write followed by host reads.
- `all` enables the twelve registered usages, including host access. `all_device` removes host read and write while retaining all device usages.
- Vertex-input cases register strides 2 and 4. Other pair groups register only the byte size.
- The generator can choose global, buffer, and image barriers and legal image layout transitions. This broadens the same visibility model rather than defining separate registered families.
- `USAGE_INDIRECT_BUFFER`, color attachment, input attachment, and depth/stencil attachment exist in implementation enums but are absent from the registered `usages` array. The `all` groups therefore do not cover them.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Usage-to-stage/access mapping | [`usageToStageFlags()` and `usageToAccessFlags()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L413-L494) | Defines the scopes enabled by each registered usage. |
| Random operation legality and cache model | [`State` and `getAvailableOps()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L8024-L8370) | Restricts generation to operations whose dependencies are valid. |
| Barrier generation | [`createCmdCommand()` barrier cases](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L8936-L9053) | Builds layout transitions and global, buffer, or image barriers. |
| Iteration and verification | [`MemoryTestInstance`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9407-L9669) | Iterates memory types and seeds, executes commands, and collects failures. |
| Shader generation | [`AddPrograms::init()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9672-L10105) | Generates graphics programs for shader-visible reads. |
| Registration | [`createPipelineBarrierTests()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L10126-L10250) | Defines exact intermediate nodes and leaves. |
| Parent registration | [`createMemoryTests()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L50-L82) | Attaches the family below `memory`. |
| Vulkan memory dependency semantics | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L114-L147) | Defines availability, visibility, and memory dependencies. |

## Questions / Risk Points for User Audit

- Resolved: `all` contains only the twelve entries in the local `usages` array; it does not include every value in the broader `Usage` enum.
- Resolved: shader programs participate in shader-readable groups, but synchronization remains the tested property; shader arithmetic turns observed memory into verifiable pixels.
- Resolved: the random masks are constrained by the source-side cache model and illegal access bits are removed before recording a barrier.
- No unresolved semantic risk remains for the rewrite.

## Conversion Notes for Final Wiki Rewrite

Use the six access-domain/consumer groups as the behavior axis. Keep the complete registered intermediate-node inventory in registration and parameter sections. Carry the failure table unchanged. Include one shader walkthrough for `host_write_storage_buffer.1024`; explain other shader consumers in the variation summary rather than adding walkthroughs.
