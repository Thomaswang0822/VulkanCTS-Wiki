# vktMemoryModelMessagePassing.cpp

This document describes the main Vulkan CTS `memory_model` registration and the generated message-passing,
write-after-read, transitive visibility, padding, and shared-layout branches rooted in
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp).

## Overview

[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp) is the category
root implementation for `memory_model`: the package root registers `memory_model` with `MemoryModel::createTests`, and this
file defines `createTests(testCtx, name)` to construct the root group using the supplied name.

The dominant generated families stress Vulkan/SPIR-V memory-model synchronization. Extension-mode and transitive shaders emit
`#pragma use_vulkan_memory_model`, while the generated shaders use storage-class-specific payload/guard resources and a fail
buffer that records any invocation whose observed value violates the expected ordering.

## Role of File

- **Registration file and implementation file.** It constructs the category root group and registers most direct children,
  including `message_passing`, `write_after_read`, `transitive`, `padding`, and `shared`.
- It also delegates two direct children to separate files: `padding` from
  [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L360-L367) and `shared` from
  [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L287-L330).

## Source Code

| Purpose | Link |
|---------|------|
| Package root registration | [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1370-L1380) |
| Vulkan SC package root registration | [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1413-L1447) |
| Category factory declaration | [vktMemoryModelTests.hpp](../../../modules/vulkan/memory_model/vktMemoryModelTests.hpp#L30-L35) |
| Category factory and direct-child registration | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2060-L2415) |
| Core support gates | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L181-L328) |
| Shader verification logic | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L953-L1004) |
| Host fail-buffer verification | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1992-L2017) |

## Other Inspected Related Files

| File | Role |
|------|------|
| [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp) | Implements the delegated `padding` child. |
| [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp) | Registers the delegated `shared` child and randomized shared-memory layout cases. |
| [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp) | Helper implementation for `shared` cases; it does not register a separate group. |
| [CMakeLists.txt](../../../modules/vulkan/memory_model/CMakeLists.txt#L7-L24) | Shows the memory-model module source inventory. |

## Registration Hierarchy

```text
memory_model
├── message_passing
├── write_after_read
├── transitive
├── padding
└── shared
```

## Test Families

### message_passing — Payload-before-guard synchronization

`message_passing` creates a generated matrix under a direct child named `message_passing`; each final test writes a payload,
performs a selected release/acquire synchronization form through a guard variable or control barrier, then loads the partner
payload and flags failure if the acquired value is not the partner coordinate. The shader-side payload-store, guard sync, and
final payload check are generated in [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L749-L973).

For non-VulkanSC builds, this family also adds `permuted_index` Amber tests named `barrier`, `release_acquire`, and
`release_acquire_atomic_payload`, with support checks requiring compute workgroup count/size/invocations of at least 256 in
x/invocation dimensions [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2020-L2055).

### write_after_read — Read-before-partner-write hazard

`write_after_read` uses the same generated parameter matrix as `message_passing`, but it first reads the partner payload and
then writes its own payload only after synchronization indicates the partner has already read. It fails if the early read sees a
nonzero value [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L795-L814) and
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L975-L1004).

### transitive — Availability/visibility chain tests

`transitive` is a compute-only message-passing family that fixes test type to message passing, data type to `u32`, stage to
compute, and scope to device, then varies coherence, synchronization form, payload and guard placement, and whether visibility
is performed by invocation `(0,0)` or by the destination invocation. The generated cases are registered under `transitive` in
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2341-L2408), and the
shader construction explicitly uses `gl_SemanticsMakeAvailable` / `gl_SemanticsMakeVisible` paths
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1075-L1327).

### padding — Delegated structure-padding copy test

The `padding` child is added by this root file and implemented in
[vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L360-L367). It contains a single `test`
case and is documented separately in [vktMemoryModelPadding.md](vktMemoryModelPadding.md).

### shared — Delegated shared-memory layout tests

The `shared` child is added by this root file and implemented in
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L287-L330). It contains base,
`16bit`, and `8bit` randomized layout groups and is documented separately in
[vktMemoryModelSharedLayout.md](vktMemoryModelSharedLayout.md).

## Parameter Dimensions and Observed Values

The main generated matrix is declared as `TestGroupCase` arrays and nested loops in
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2070-L2167) and
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2169-L2339).

| Dimension | Registered values | Evidence |
|-----------|-------------------|----------|
| Test type | `message_passing`, `write_after_read` | [ttCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2070-L2073) |
| API/memory-model mode | `core11`, `ext` | [core11Cases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2075-L2080) |
| Data type | `u32`, `u64`, `f32`, `f64` | [dtCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2082-L2091) |
| Payload coherence | `coherent`, `noncoherent` | [cohCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2093-L2098) |
| Synchronization form | `fence_fence`, `fence_atomic`, `atomic_fence`, `atomic_atomic`, `control_barrier`, `control_and_memory_barrier` | [stCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2100-L2113) |
| Atomic operation kind | `atomicwrite`, `atomicrmw` | [rmwCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2115-L2118) |
| Scope | `device`, `queuefamily`, `workgroup`, `subgroup` | [scopeCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2120-L2125) |
| Payload locality | `payload_nonlocal`, `payload_local` | [plCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2127-L2132) |
| Payload storage | `buffer`, `image`, `workgroup`, `physbuffer` | [pscCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2134-L2143) |
| Guard locality | `guard_nonlocal`, `guard_local` | [glCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2145-L2150) |
| Guard storage | `buffer`, `image`, `workgroup`, `physbuffer` | [gscCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2152-L2161) |
| Shader stage | `comp`, `vert`, `frag` | [stageCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2163-L2167) |
| Transitive visibility | `nontransvis`, `transvis` | [transVisCases](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2341-L2346) |

The registration loops intentionally prune unsupported or redundant combinations, including Vulkan 1.1 `core11` exclusions,
non-compute workgroup-scope cases, workgroup-memory locality restrictions, control barriers outside workgroup/compute usage,
RMW atomics outside `atomic_atomic`, non-32-bit atomic testing outside `atomic_atomic`, and 64-bit image restrictions
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2235-L2313).

## Support / Feature Requirements

Support gates observed in the main memory-model case include:

- Vulkan 1.1 is required for every generated `MemoryModelTestCase`
  [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L181-L186).
- `ext` cases require the Vulkan memory model feature, and device-scope `ext` cases additionally require
  `vulkanMemoryModelDeviceScope` [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L188-L199).
- Subgroup-scope cases require basic, ballot, and shuffle subgroup operations and stage support for the selected shader stage
  [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L201-L239).
- `u64` cases require shader `int64` support and the relevant 64-bit atomic features for buffer/physical-buffer or shared
  guard storage [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L241-L255).
- `f32` and `f64` atomic cases require `VK_EXT_shader_atomic_float` plus the selected storage-class atomic features; `f64`
  image payload/guard combinations are rejected [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L258-L305).
- Transitive cases require `vulkanMemoryModelAvailabilityVisibilityChains`
  [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L308-L309).
- Physical storage buffer cases require buffer-device-address support
  [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L311-L313).
- Vertex and fragment cases require `vertexPipelineStoresAndAtomics` or `fragmentStoresAndAtomics`, respectively
  [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L315-L328).

## Verification Methods

The generated shaders write to a `fail` storage buffer only when an invocation observes an unexpected value. For message
passing, the test compares the loaded partner payload with `partnerBufferCoord`; for write-after-read, the test expects the
pre-synchronization read to remain zero [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L953-L1004).

The host repeatedly clears payload/guard resources, dispatches or draws the selected shader stage 50 times per submit across
four submits, copies the fail buffer to host-visible memory, and fails the case if any fail-buffer element is nonzero
[vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1881-L2017).

## Test Principles Observed

- Exercise release/acquire synchronization through both explicit memory barriers and atomic operations.
- Cover buffer, image, workgroup, and physical-buffer storage classes where the generated filters allow them.
- Compare compute, vertex, and fragment shader behavior for supported scopes and storage-class combinations.
- Treat skipped races explicitly in shader code through `skip` paths so the host failure criterion remains a simple fail-buffer
  scan.

## Notes / Uncertainties

- The inspected API test plan does not contain a dedicated `memory_model` section; this page relies on the inspected source and
  mustpass evidence rather than test-plan prose.
- VulkanSC mustpass coverage was not observed for `dEQP-VKSC.memory_model` in the inspected mustpass search; the source still
  registers `memory_model` for VulkanSC package initialization.
