# vktRobustBufferAccessWithVariablePointersTests.cpp

## Overview

This page documents the Vulkan CTS robustness tests implemented in
[vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1-L36).
The file creates the nested registered group `robustness.buffer_access.through_pointers`, which checks robust storage
buffer access when SPIR-V variable pointers are used to perform reads or writes through pointer values that may address
only a descriptor-inaccessible part of a buffer or memory beyond the buffer allocation.

The test source builds SPIR-V assembly directly. The generated shaders declare `VariablePointersStorageBuffer` and
`SPV_KHR_variable_pointers`, then create selected load or store pointers with `OpSelect` so the accessed pointer is a
variable pointer rather than a simple static access chain
([MakeShader()](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L839-L869),
[read/write pointer generation](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1105-L1218)).

## Role of file

[vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp)
is an implementation-heavy registered subgroup file. It owns the `through_pointers` subgroup factory declared in
[vktRobustBufferAccessWithVariablePointersTests.hpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.hpp#L29-L35).
The root robustness dispatcher does not add this group at the `robustness` root. Instead, after `buffer_access` is
registered, the dispatcher searches for the existing `buffer_access` node and attaches
`createBufferAccessWithVariablePointersTests()` below it; if the node is absent, it creates `buffer_access` and then
adds the variable-pointer child
([vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L69-L82)).

The file also owns the per-case custom device setup, shader generation, buffer setup, descriptor setup, execution, and
result verification for this subgroup
([custom device setup](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L67-L87),
[instance setup](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1352-L1540),
[verification](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1589-L1848)).

## Source code link

- Source: [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1-L2005)
- Header declaration: [vktRobustBufferAccessWithVariablePointersTests.hpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.hpp#L29-L35)
- Root insertion: [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L69-L82)
- Mustpass examples: [robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L450-L590)

## Inspected related files

| File | Evidence used |
|------|---------------|
| [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L67-L87) | Custom device creation enabling robust buffer access together with variable-pointer feature chaining. |
| [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L160-L175) | Local shader-type and access-type enums. |
| [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L214-L224) | Common support checks for variable pointers and portability-subset robust-buffer-access support. |
| [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L839-L1239) | SPIR-V assembly generation, capabilities, storage-buffer declarations, `OpSelect` variable-pointer paths, and stage entry points. |
| [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1250-L1350) | Read/write test instance creation and SPIR-V program registration for compute and graphics cases. |
| [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1352-L1540) | Buffer creation, descriptor set setup, index selection, and compute/graphics environment setup. |
| [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1589-L1848) | Command submission, output invalidation, result verification, and final pass/fail status. |
| [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1897-L2001) | Registration hierarchy, direct child names, generated leaf names, and parameter arrays. |
| [vktRobustBufferAccessWithVariablePointersTests.hpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.hpp#L29-L35) | Public factory declaration for the subgroup. |
| [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L69-L82) | Evidence that `through_pointers` is inserted under `robustness.buffer_access`. |
| [vktRobustnessUtil.hpp](../../../modules/vulkan/robustness/vktRobustnessUtil.hpp#L41-L149) | Directly included shared helpers and environment classes used by the implementation. |
| [vktRobustnessUtil.cpp](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L166-L277) | Shared value predicates, vector out-of-bounds pattern checks, and deterministic input-buffer population used by this file. |
| [robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L450-L590) | Mustpass evidence for generated `through_pointers.compute` read/write leaves. |
| [robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L650-L720) | Mustpass evidence for generated `through_pointers.graphics.reads.fragment` leaves. |

## Registration Hierarchy

```text
robustness.buffer_access.through_pointers
├── graphics
└── compute
```

The `through_pointers` root group is constructed with the literal name `through_pointers`, then receives direct children
`graphics` and `compute` in the factory function
([group creation](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1897-L1908),
[child attachment](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1992-L1999)).
The canonical tree above lists only these direct children; nested `reads`, `writes`, `vertex`, and `fragment` groups are
covered below as generated test-family structure.

## Test Families

### graphics

The `graphics` child contains read and write cases that execute through graphics pipelines. The implementation creates
nested `reads.vertex`, `reads.fragment`, `writes.vertex`, and `writes.fragment` groups, assigns vertex-stage cases to the
vertex nested groups and fragment-stage cases to the fragment nested groups, then attaches the read/write groups to
`graphics`
([nested group construction](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1908-L1914),
[stage mapping](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1945-L1953),
[graphics attachment](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1986-L1993)).

For graphics cases, `initPrograms()` provides both vertex and fragment SPIR-V assembly. The tested stage receives the
variable-pointer shader, while the other stage is generated as an unused minimal pass-through shader
([read programs](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1278-L1294),
[write programs](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1334-L1350),
[unused-stage path](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L888-L913)).
Runtime setup creates a small vertex buffer and `GraphicsEnvironment` for non-compute stages
([graphics setup](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1500-L1538)).

### compute

The `compute` child contains read and write cases executed by a compute shader. It has nested `reads` and `writes` groups
created in the factory and receives all cases mapped to `VK_SHADER_STAGE_COMPUTE_BIT`
([compute group construction](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1903-L1906),
[stage mapping](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1945-L1953),
[compute attachment](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1995-L1999)).

For compute cases, `initPrograms()` registers a single `compute` SPIR-V assembly source whose entry point is generated as
`GLCompute` with local size `1,1,1`
([read compute source](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1278-L1284),
[write compute source](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1334-L1340),
[compute entry point](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L871-L876)).
Runtime setup selects `ComputeEnvironment` for `VK_SHADER_STAGE_COMPUTE_BIT`
([compute setup](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1495-L1499)).

### Generated read and write leaves

Both direct children ultimately use the same generated leaf-name matrix. The read loop creates `RobustReadTest` leaves,
and the write loop creates `RobustWriteTest` leaves. Each name has the form
`<size>B_<in_memory|out_of_memory>_with_<vec4|scalar>_<format-name>`
([read leaf creation](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1958-L1970),
[write leaf creation](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1972-L1984)).
Observed mustpass entries include examples such as
`robustness.buffer_access.through_pointers.compute.reads.16B_in_memory_with_scalar_f32` and
`robustness.buffer_access.through_pointers.graphics.reads.fragment.16B_in_memory_with_scalar_f32`
([compute mustpass examples](../../../mustpass/main/vk-default/robustness.txt#L450-L469),
[graphics mustpass examples](../../../mustpass/main/vk-default/robustness.txt#L650-L669)).

## Parameter dimensions and observed values

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Registered root | `robustness.buffer_access.through_pointers` | Root insertion under `buffer_access` in [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L69-L82) and literal subgroup name in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1897-L1902). |
| Direct children | `graphics`, `compute` | Direct child construction and attachment in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1903-L1908) and [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1992-L1999). |
| Nested access groups | `reads`, `writes` | Nested group construction and attachment in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1905-L1914) and [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1986-L1996). |
| Graphics tested stage | `vertex`, `fragment` under both `reads` and `writes` | Graphics nested groups and stage mapping in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1908-L1914) and [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1945-L1953). |
| Shader stages | `VK_SHADER_STAGE_VERTEX_BIT`, `VK_SHADER_STAGE_FRAGMENT_BIT`, `VK_SHADER_STAGE_COMPUTE_BIT` | `stages[]` array in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1945-L1953). |
| Shader copy type | `vec4`, `scalar` mapped to `SHADER_TYPE_VECTOR_COPY` and `SHADER_TYPE_SCALAR_COPY` | `types[]` array in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1933-L1943). |
| Formats / suffixes | `VK_FORMAT_R32_SINT` = `s32`; `VK_FORMAT_R32_UINT` = `u32`; `VK_FORMAT_R32_SFLOAT` = `f32`; `VK_FORMAT_R64_SINT` = `s64`; `VK_FORMAT_R64_UINT` = `u64` | `bufferFormats[]` in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1923-L1927). |
| Access sizes | `1B`, `3B`, `4B`, `16B`, `32B` | `rangeSizes[]` in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1929-L1931). |
| Backing-memory mode | `in_memory`, `out_of_memory` | `backingMemory[]` and `s != 0` flag passed to case constructors in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1955-L1969) and [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1972-L1983). |
| Test array size | `1024` elements | Static constant and SPIR-V array constant in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L199-L200) and [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1036-L1064). |
| Shader write footprint | `16 * sizeof(float)` = 64 bytes | `s_numberOfBytesAccessed` in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L199-L200). |

Observed generation size from the visible loops is three stages × two access directions × two shader copy types × five
formats × five access sizes × two backing-memory modes, with graphics split into vertex and fragment nested groups and
compute placed directly under `compute.reads` or `compute.writes`
([nested loops](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1958-L1984)).
This page summarizes the source-generation dimensions rather than enumerating every generated leaf.

## Support / feature requirements

- The common support check requires `variablePointersStorageBuffer`; if it is absent, the test throws `NotSupportedError`
  for the `VariablePointersStorageBuffer` SPIR-V capability
  ([checkSupport()](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L214-L219)).
- When `VK_KHR_portability_subset` is supported, the implementation must also expose `robustBufferAccess`; otherwise the
  test is reported unsupported
  ([checkSupport()](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L220-L224)).
- Per-case execution creates a custom device with `features2.features.robustBufferAccess = VK_TRUE` and chains the
  context-provided variable-pointer feature structure
  ([custom device setup](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L67-L87)).
- Cases using `VK_FORMAT_R64_SINT` or `VK_FORMAT_R64_UINT` require `shaderInt64`; the generated SPIR-V also adds the
  `Int64` capability for those formats
  ([runtime support check](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1387-L1393),
  [SPIR-V capability](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L859-L865)).
- Vertex-stage and fragment-stage cases require `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`,
  respectively, because the shaders write through storage buffers in those stages
  ([stage store checks](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1395-L1409)).

## Verification methods

The test initializes input, output, and index buffers, executes one compute dispatch or graphics draw through the shared
environment, invalidates the output allocation, and then checks the output contents
([buffer setup](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1411-L1425),
[descriptor setup](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1439-L1479),
[command submission and invalidation](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1589-L1624)).

Input buffers are filled with deterministic values derived from the selected format, while output buffers are filled with
`0xBA` bytes so unchanged values can be identified
([input value filler](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L138-L150),
[expected-value check](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1546-L1578),
[unchanged-output check](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1580-L1587)).
The index buffer selects zero offsets for normal descriptor-inaccessible cases and an index near the end of the 1024-entry
array for `out_of_memory` read or write cases
([index selection](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1416-L1425)).

[AccessInstance::verifyResult()](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1632-L1848)
checks each output element-sized slot:

- Bytes beyond the shader's intended write footprint must remain unchanged, unless an out-of-bounds write produced an
  allowed value from the input allocation or zero
  ([post-footprint check](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1653-L1663)).
- The verifier determines whether the current element is out of bounds by comparing the element offset and operand size
  against the relevant max access range, with special handling for the explicit `out_of_memory` mode
  ([out-of-bounds classification](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1667-L1707)).
- Partially out-of-bounds accesses check the in-range and out-of-range byte portions separately
  ([partial access verification](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1709-L1757)).
- Out-of-bounds reads must produce a value from the backing input allocation or zero, with an additional accepted vec4
  pattern delegated to `verifyOutOfBoundsVec4()`
  ([read verification](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1760-L1806)).
- Out-of-bounds writes must leave output bytes unchanged or write an allowed value from the input allocation or zero
  ([write verification](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1765-L1777)).
- In-bounds reads must match deterministic input values, while in-bounds outputs after write tests must contain values
  from the accessible input range or zero
  ([in-bounds verification](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1816-L1834)).
- If an 8-byte check fails, the verifier retries as split 32-bit accesses, matching the local comment about decomposed
  non-atomic storage-buffer accesses
  ([split-access retry](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1841-L1845)).

The final status is `pass("All values OK")` or `fail("Invalid value(s) found")` according to `verifyResult()`
([iterate() result](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1626-L1629)).

## Test principles observed in the file

- Exercise variable-pointer robustness explicitly by generating SPIR-V assembly with `VariablePointersStorageBuffer`,
  `SPV_KHR_variable_pointers`, and selected load/store pointers built through `OpSelect`
  ([capabilities](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L859-L869),
  [variable-pointer selection](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1119-L1148)).
- Use the same source-generation matrix for read and write tests, but place the variable pointer on the load side for
  read tests and on the store side for write tests
  ([scalar read/write path](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1119-L1148),
  [vector read/write path](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1162-L1182)).
- Cover both compute and graphics execution paths while preserving the same descriptor layout and verification model
  ([environment selection](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1495-L1538)).
- Test two kinds of invalid access: memory within the buffer allocation but outside the descriptor-accessible range
  (`in_memory`) and memory selected beyond the backing buffer allocation (`out_of_memory`)
  ([file note](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L24-L34),
  [backing-memory dimension](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1955-L1969)).
- Keep accepted results constrained to values explicitly allowed by local robustness checks: expected in-bounds data,
  zero, unchanged output, values from the accessible input allocation, or the local vec4 out-of-bounds pattern
  ([verification body](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1632-L1848)).

## Notes / uncertainties

- The source contains `SHADER_TYPE_MATRIX_COPY`, but the registered `types[]` array for this subgroup includes only
  `vec4` and `scalar`; no matrix leaves were observed in the inspected registration loop
  ([enum](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L158-L167),
  [registered types](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1933-L1943)).
- The header brief mentions uniform/storage buffers and texel buffers, but the inspected implementation for this subgroup
  registers storage-buffer cases only; descriptor bindings are storage buffer, storage buffer, and uniform buffer for
  indices, with no texel-buffer case matrix in the inspected factory
  ([header brief](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.hpp#L21-L25),
  [descriptor layout](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1439-L1479)).
- Mustpass evidence was sampled from the default Vulkan `robustness.txt` around the `through_pointers` block. The page
  relies primarily on source loops for full parameter dimensions rather than trying to enumerate every mustpass leaf.
- Vulkan SC-specific mustpass files were not inspected for this subtask. Vulkan SC statements are limited to conditional
  code paths visible in this source, mainly custom device and driver creation guarded by `CTS_USES_VULKANSC`
  ([read instance creation](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1250-L1276),
  [write instance creation](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1306-L1332)).
