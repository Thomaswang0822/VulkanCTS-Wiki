## Overview

The `subgroups` test category collects tests that check subgroup built-ins, collective operations, data exchange, execution control, and subgroup-aware resource access across Vulkan shader stages.

## Background Knowledge

- **Subgroup identity and active invocations.** A subgroup is an implementation-defined set of shader invocations that can perform subgroup operations together. Each invocation has a subgroup-local ID, and each operation observes the invocations that are active when it executes.
- **Ballots and masks.** A ballot represents a Boolean contribution from each participating invocation as a bit mask. CTS uses ballots both as results under test and as reference data for determining which invocation IDs should contribute to another subgroup operation.
- **Collective result shapes.** Election chooses one active invocation. Votes combine Boolean conditions. Reductions combine all selected values, while inclusive and exclusive scans combine ordered prefixes. Shuffle and broadcast operations move one invocation's value to others.
- **Quad and clustered partitions.** Quad operations use quad scope instances associated with four subgroup invocations; the exact grouping depends on the shader execution model, and many tested non-fragment paths expose consecutive groups of four subgroup-local IDs. Clustered operations divide a subgroup into consecutive power-of-two partitions and compute a result inside each partition.
- **Subgroup-size control.** An implementation reports supported subgroup sizes and stages. Eligible pipelines can request a power-of-two subgroup size and, for selected stages, full subgroups in which all launched invocations are active.

## Category Structure

```text
subgroups
├── builtin_var
├── builtin_mask_var
├── basic
├── vote
├── ballot
├── ballot_broadcast
├── ballot_other
├── arithmetic
├── clustered
├── partitioned
├── shuffle
├── quad
├── shape
├── ballot_mask
├── multiple_dispatches
├── size_control
├── subgroup_uniform_control_flow
├── uniform_descriptor_indexing
└── shader_quad_control
```

The dispatcher registers all 19 test families. `partitioned`, `subgroup_uniform_control_flow`, `uniform_descriptor_indexing`, and `shader_quad_control` are omitted from Vulkan SC builds by the registration guards in [`vktSubgroupsTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L46) and [`createChildren()`](../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L68-L81).

## How the Families Fit Together

The families divide subgroup conformance by the kind of value or execution property being observed.

- The built-in, vote, ballot, arithmetic, shuffle, quad, and shape families check shader-visible subgroup state and collective operations.
- `basic`, `size_control`, `multiple_dispatches`, `subgroup_uniform_control_flow`, and `shader_quad_control` check synchronization or execution conditions that affect subgroup participation and size.
- `partitioned` and `clustered` restrict collective arithmetic to selected invocation sets, while `uniform_descriptor_indexing` uses subgroup-uniform values to select descriptor-array elements.

The navigation below describes test intent. A family page may also document deliberate coverage limits or a source-side support-gating defect found during audit; those notes belong to the exact implementation path and do not redefine Vulkan requirements for the category as a whole.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `builtin_var` | [BuiltinVar.md](../testfiles/subgroups/BuiltinVar.md) | Subgroup size, invocation, subgroup, and workgroup built-ins. |
| `builtin_mask_var` | [BuiltinMaskVar.md](../testfiles/subgroups/BuiltinMaskVar.md) | Relational subgroup masks and ray-tracing repacking. |
| `basic` | [Basic.md](../testfiles/subgroups/Basic.md) | Election, barriers, memory semantics, and required subgroup-size variants. |
| `vote` | [Vote.md](../testfiles/subgroups/Vote.md) | All, any, and all-equal vote operations. |
| `ballot` | [Ballot.md](../testfiles/subgroups/Ballot.md) | Core and legacy ballot-mask generation. |
| `ballot_broadcast` | [BallotBroadcast.md](../testfiles/subgroups/BallotBroadcast.md) | Broadcast by invocation ID and broadcast-first behavior. |
| `ballot_other` | [BallotOther.md](../testfiles/subgroups/BallotOther.md) | Ballot tests, bit counts, prefix counts, and set-bit searches. |
| `arithmetic` | [Arithmetic.md](../testfiles/subgroups/Arithmetic.md) | Subgroup reductions and inclusive or exclusive scans. |
| `clustered` | [Clustered.md](../testfiles/subgroups/Clustered.md) | Arithmetic within consecutive power-of-two clusters. |
| `partitioned` | [Partitioned.md](../testfiles/subgroups/Partitioned.md) | `VK_NV_shader_subgroup_partitioned` masks, reductions, and scans. |
| `shuffle` | [Shuffle.md](../testfiles/subgroups/Shuffle.md) | Shuffle, XOR, up, down, rotate, and clustered-rotate data exchange. |
| `quad` | [Quad.md](../testfiles/subgroups/Quad.md) | Values exchanged within four-invocation quads. |
| `shape` | [Shape.md](../testfiles/subgroups/Shape.md) | Membership rules for clustered and quad operation shapes. |
| `ballot_mask` | [BallotMasks.md](../testfiles/subgroups/BallotMasks.md) | Legacy equality and relational ballot-mask built-ins. |
| `multiple_dispatches` | [MultipleDispatchesUniformSubgroupSize.md](../testfiles/subgroups/MultipleDispatchesUniformSubgroupSize.md) | Subgroup-size uniformity within each compute dispatch. |
| `size_control` | [SizeControl.md](../testfiles/subgroups/SizeControl.md) | Advertised, required, varying, and full subgroup sizes. |
| `subgroup_uniform_control_flow` | [UniformControlFlow.md](../testfiles/subgroups/UniformControlFlow.md) | Amber reconvergence cases for full, partial, controlled, and discard variants. |
| `uniform_descriptor_indexing` | [UniformDescriptorIndexing.md](../testfiles/subgroups/UniformDescriptorIndexing.md) | Subgroup-uniform indexing across nine descriptor classes. |
| `shader_quad_control` | [QuadControl.md](../testfiles/subgroups/QuadControl.md) | Quad derivatives, full quads, divergence, and terminated invocations. |
