# Understanding Brief: Ballot Broadcast

## One-Sentence Test Purpose

This test checks whether subgroup broadcast operations return the selected active invocation's value across supported data types, shader stages, subgroup sizes, and the legacy ballot extension path.

## Background Knowledge

### Subgroup broadcast and active invocations

A Vulkan subgroup is a set of shader invocations that can exchange data efficiently. Ballot operations describe which invocations are active, while broadcast operations distribute one invocation's value to the other active invocations in the subgroup.

Why it matters here:
- `subgroupBroadcast` selects an invocation by ID, and the non-constant variant additionally relies on a dynamically uniform ID.
- `subgroupBroadcastFirst` selects the first active invocation, so the expected source can change when control flow makes an invocation inactive.

### Core and extension forms

Core subgroup operations use `subgroupBallot`, `subgroupBroadcast`, and `subgroupBroadcastFirst`. The legacy `VK_EXT_shader_subgroup_ballot` path uses `ballotARB`, `readInvocationARB`, and `readFirstInvocationARB`, with a 64-bit ballot mask. Vulkan 1.2 superseded most of that extension functionality and introduced `subgroupBroadcastDynamicId` for dynamically uniform broadcast IDs.

Why it matters here:
- The two forms expose the same broad data-movement idea through different GLSL and SPIR-V operations.
- The extension path is limited to scalar `int`, `uint`, and `float` inputs by this test's registration logic.

## One Concrete Example

For `dEQP-VK.subgroups.ballot_broadcast.compute.subgroupbroadcast_bool`, every compute invocation reads its own `bool` value from the input buffer. The generated shader broadcasts that value once for each constant source ID from 0 through 127, then compares the result for every active source ID below the runtime subgroup size with `data[id]`. Each invocation writes `3` only if all comparisons succeed.

This case is a compact representative because it uses the core constant-ID path, the ordinary compute harness, and a type whose host representation must still compare correctly as GLSL `bool`.

## End-to-End Test Flow

```text
[host] select operation, data type, shader stage path, extension mode, and optional required subgroup size
[host] generate GLSL with the operation-specific body and common stage wrapper
[host] allocate and initialize a nonzero input buffer plus a uint result buffer
[host] build the pipeline, bind descriptors, and choose each harness local size
[host] dispatch, draw, or trace the selected stage path
[device] form an active-lane ballot and perform the selected broadcast checks
[device] write a per-invocation uint result code
[host] make shader writes visible, wait, invalidate mapped memory, and scan every expected result element
[host] pass only if every tested iteration contains the reference value 3
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms` selects SPIR-V 1.3 for constant-ID and first-active core cases, SPIR-V 1.5 for dynamic-ID cases, and SPIR-V 1.4 for ray tracing or mesh unless the dynamic-ID case already requires 1.5.
- `getExtHeader` emits either the core ballot extension or the legacy ARB ballot, subgroup-basic, and 64-bit integer extensions, plus any extension required by the selected data type.
- `getTestSrc` emits one of three operation bodies: constant source ID, dynamic source ID, or first active source.
- `initStdPrograms` wraps the body in stage-specific GLSL and adds result and input declarations. Compute local sizes are specialization constants 0, 1, and 2.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `result[]` storage buffer | yes | yes, binding 0 in compute and mesh paths | written | yes | Holds one `uint` result code per invocation. |
| `data[]` input buffer | yes | yes, binding 1 in the representative compute path | read | no for validation | Supplies distinct, seeded nonzero values indexed by subgroup invocation ID. |
| framebuffer color target and readback buffer | yes | yes | written by rendering and copy | yes | Carries result codes for framebuffer variants without shader storage writes in the tested stage. |
| ballot mask and `ops[]` | no | no | shader-local values | no | Track active source invocations and constant-ID broadcast results. |

## What Is Checked

- Constant-ID `subgroupbroadcast` starts at `3` and clears the result to `0` if any active source ID returns a value different from `data[id]`.
- `subgroupbroadcast_nonconst` checks every runtime loop ID, then checks an ID that is uniform only among the active invocations in the selected half-subgroup control-flow region.
- `subgroupbroadcastfirst` sets bit 0 for the first check and bit 1 for a second check after the original first active invocation is excluded. The required result is therefore `3`.
- The common host callbacks require every produced result element to equal `3`; any failed harness iteration makes the test case fail.

## Behavior Parameter Identification

> **Behavior parameter:** `broadcast operation` (test case leaf prefix)
>
> **Candidate values:** `subgroupbroadcast`, `subgroupbroadcast_nonconst`, `subgroupbroadcastfirst`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupbroadcast` | Constant source invocation selection or broadcast value propagation is incorrect for an active source lane. |
| `subgroupbroadcast_nonconst` | Dynamic source ID handling, dynamically uniform ID recognition, or broadcast value propagation is incorrect. |
| `subgroupbroadcastfirst` | First-active invocation selection or reconvergence after control-flow changes is incorrect. |

All values can also expose incorrect data-type lowering, stage-specific subgroup support, required subgroup-size handling, or result transport and readback.

## Important Variations and Special Cases

- The core path spans scalar, vector, and long-vector integer, floating-point, and Boolean formats. Ray tracing uses a smaller format list.
- The legacy extension path registers only scalar `int`, `uint`, and `float`, but still runs compute, graphics, framebuffer, and mesh variants.
- Compute and mesh cases add required subgroup-size leaves for powers of two from 1 through 128. Support checks prune sizes outside the device's advertised range or unsupported for the selected stage.
- Framebuffer variants use vertex, tessellation control, tessellation evaluation, and geometry stages with a uniform input buffer. Graphics variants exercise all available graphics subgroup stages with storage buffers.
- Non-constant broadcast uses SPIR-V 1.5 and requires `subgroupBroadcastDynamicId`. Constant-ID and first-active core cases use SPIR-V 1.3 unless their stage requires 1.4.
- No `ballot_broadcast` entry appears in `mustpass/main/src/test-issues.txt`; the file lists no applicable issue exclusion for this family.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Operation body generation | [`getTestSrc`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L101-L207) | Defines all three broadcast checks and their result bits. |
| Program generation | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L242-L262) | Selects the SPIR-V target and passes the body to the shared stage generator. |
| Support and feature gates | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L264-L347) | Enforces subgroup, ballot, format, extension, dynamic-ID, size-control, and stage requirements. |
| Runtime path selection | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L379-L454) | Defines input layout and selects compute, mesh, graphics, or ray tracing helpers. |
| Registration loops | [`createSubgroupsBallotBroadcastTests`](../../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L461-L693) | Generates operation, format, stage, extension, and required-size leaves. |
| Compute GLSL wrapper | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1434) | Adds descriptors, invocation indexing, specialization-controlled local size, and result writes. |
| Compute execution and readback | [`makeComputeOrMeshTestRequiredSubgroupSize`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3762-L4063) | Creates resources, dispatches each local-size variant, synchronizes, and calls the checker. |
| Result scan | [`checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Requires every result element to match the reference value. |
| Registered representative case | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L12111) | Confirms the exact compute `subgroupbroadcast_bool` executable path. |
| Vulkan subgroup and ballot semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3220-L3247) | Defines subgroup scope and stage support. |
| Ballot broadcast behavior | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3514-L3523) | States that broadcast distributes an invocation's value across the group. |
| Dynamic broadcast ID feature | [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#L951-L957) | Defines constant versus dynamically uniform source-ID support. |
| Legacy ballot extension mapping | [`VK_EXT_shader_subgroup_ballot.adoc`](../../../../vulkan-docs/src/appendices/VK_EXT_shader_subgroup_ballot.adoc#L21-L79) | Maps the ARB functions and explains supersession by core subgroup operations. |

## Questions / Risk Points for User Audit

- Is the operation prefix the clearest primary behavior axis, rather than stage family or extension mode?
- Does the first-active explanation make clear why two result bits are required?
- Are the extension and required subgroup-size variants separated cleanly from the core behavior?
- The source and mustpass mapping are resolved, and no semantic blocker remains for the final page.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.subgroups.ballot_broadcast.compute.subgroupbroadcast_bool` for the representative shader walkthrough, sourced from `vktSubgroupsBallotBroadcastTests.cpp` through `initPrograms`.
- Carry the `broadcast operation` axis and its three exact values into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table exactly into the final page.
- Distill subgroup, active-invocation, and dynamic-ID concepts into short prerequisite bullets.
- Keep detailed registration loops and helper mechanics in the source appendix.
