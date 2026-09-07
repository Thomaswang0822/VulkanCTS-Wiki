## Overview

**Core question:** Do shader objects preserve independently specified descriptor-set layouts across graphics stage combinations, linked and unlinked creation, and SPIR-V and binary shader inputs?

- The `m11_independent_sets` family is registered by [createShaderObjectIndependentSetsTests()](../../../modules/vulkan/shader_object/vktShaderObjectIndependentSetsTests.cpp#L33-L47) and uses the shared independent-sets implementation in [vktIndependentSetsUtil.cpp](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1880-L1995).
- It creates 1,440 cases: four construction forms, twelve shader-stage combinations, ten seeded cases, and two descriptor-set ordering variants, with an additional `_no_maint11` variant where applicable.
- Each shader stage receives a separately shaped descriptor-set layout. The shaders copy descriptor values into an IO storage buffer, and the host compares the copied values exactly.

## Background Knowledge

For the shared concepts shader objects, per-stage binding, and dynamic rendering, see [Background Knowledge](../../categories/shader_object.md#background-knowledge) of the `shader_object` page.

- **Independent descriptor-set layouts.** `VK_PIPELINE_LAYOUT_CREATE_INDEPENDENT_SETS_BIT_EXT` allows shader stages to use independently specified set layouts. The test assembles a union layout for binding and stage-specific layouts for individual shader objects.
- **Descriptor-to-IO verification.** Each descriptor contains a known value. A shader reads it and stores the value in a common IO buffer, which gives the host a direct comparison target.

## Registration Hierarchy

```text
shader_object.m11_independent_sets
├── unlinked_spirv
├── unlinked_binary
├── linked_spirv
└── linked_binary
```

Each construction branch contains twelve stage groups. The classic groups are `vert`, `vert_frag`, `vert_geom`, `vert_geom_frag`, `vert_tesc_tese`, `vert_tesc_tese_frag`, `vert_tesc_tese_geom`, and `vert_tesc_tese_geom_frag`; the mesh groups are `mesh`, `mesh_frag`, `task_mesh`, and `task_mesh_frag`. Each group contains ten `case_N` leaves, ten `_io_ssbo_first` leaves, and, for shader-object cases without the IO-first ordering, ten `_no_maint11` leaves [case generation](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1905-L1988). The default mustpass file contains 1,440 paths [m11-independent-sets.txt](../../../mustpass/main/vk-default/shader-object/m11-independent-sets.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Construction form | `unlinked_spirv`, `unlinked_binary`, `linked_spirv`, `linked_binary` | Selects whether shader objects are linked and whether their shader code comes from SPIR-V or a binary. | [construction types](../../../modules/vulkan/shader_object/vktShaderObjectIndependentSetsTests.cpp#L37-L43) |
| Stage combination | Eight classic groups and four mesh groups listed above | Selects which shader stages receive independent descriptor-set layouts. | [stage registration](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1905-L1988) |
| Seeded case | `case_0` through `case_9` | Selects one pseudorandom descriptor layout and value arrangement. | [case loop](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1928-L1943) |
| IO set order | base case or `_io_ssbo_first` | Places the IO storage-buffer set at the first or last set position. | [ordering loop](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1930-L1934) |
| Maintenance11 path | base case or `_no_maint11` | Tests the shader-object independent-set path with or without the Maintenance11 requirement where the registration permits it. | [variant loop](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1934-L1942) |

## Behavior Parameters

The primary behavioral axis is the construction form. Stage combinations, seeded descriptor layouts, and IO-set order vary the layout arrangement exercised by each form.

### `unlinked_spirv` and `unlinked_binary`: independent layouts per stage

These branches create separate shader objects for the selected stages. The SPIR-V and binary branches use the same descriptor-value comparison while exercising different shader-object input representations.

### `linked_spirv` and `linked_binary`: linked stage creation with independent layouts

These branches create linked shader objects. They retain the per-stage layout variation, so a pass requires both linked creation and independent descriptor access to agree on the stage-specific layouts.

### Stage combinations and seeded cases

Classic combinations cover vertex-only, optional tessellation, optional geometry, and optional fragment stages. Mesh combinations cover mesh-only, mesh plus fragment, task plus mesh, and task plus mesh plus fragment. Each of the ten seeds changes the generated descriptor arrangement without changing the comparison rule.

### `_io_ssbo_first` and `_no_maint11`

`_io_ssbo_first` moves the common IO buffer set to the first set index. `_no_maint11` avoids the Maintenance11-dependent shader-create path for eligible shader-object cases; the support logic then requires graphics pipeline library for the alternate layout path [support checks](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L353-L365).

## Shader Analysis

The family uses generated stage shaders from the shared independent-sets utility. A representative walkthrough is not included because the behavior under test is the descriptor-set layout and host comparison matrix, not a single shader algorithm.

## Runtime Execution and Result Checking

- The support checks require Maintenance11 for ordinary shader-object variants unless `_no_maint11` is selected. The alternate path requires `VK_EXT_graphics_pipeline_library`; mesh, tessellation, and geometry combinations add their corresponding feature requirements [support checks](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L353-L409).
- The utility builds stage-specific descriptor-set layouts and a union pipeline layout. For eligible shader-object cases it sets `VK_PIPELINE_LAYOUT_CREATE_INDEPENDENT_SETS_BIT_EXT`, and it applies the independent-sets shader-create flag when Maintenance11 is used [layout construction](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1274-L1291), [shader setup](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1344-L1369), [shader flags](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1398-L1403).
- It binds the descriptor sets with the union layout, draws one point or one mesh task, and copies storage-image results when image descriptors are present [descriptor binding and draw](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1705-L1751), [copy and synchronization](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1758-L1826).
- The host compares every descriptor value with the corresponding IO-buffer value using a zero threshold. The first mismatch is logged with set, binding, descriptor, expected, actual, and threshold data, then the test fails [result comparison](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1828-L1877).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any construction form | Shader-object creation, linked-stage handling, binary input, or descriptor layout assembly is inconsistent. |
| A classic stage combination | A stage-specific layout or descriptor access path is wrong for the selected vertex, tessellation, geometry, or fragment stages. |
| A mesh stage combination | Mesh/task stage layout handling or mesh execution is wrong. |
| `case_N` | The seeded descriptor layout or one descriptor access is wrong. |
| `_io_ssbo_first` | The implementation mishandles the IO set when it occupies the first set index. |
| `_no_maint11` | The alternate independent-layout path or its graphics-pipeline-library setup is wrong. |

### Cause Analysis

#### Descriptor value differs from the IO buffer

**Possible failure symptoms:** The log reports a set, binding, descriptor index, descriptor value, IO-buffer value, and zero threshold, followed by a test failure [comparison](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1857-L1875).

**Possible implementation causes:** The implementation may associate a shader stage with the wrong descriptor-set layout, apply the wrong set index, bind the union layout incorrectly, or read a different descriptor than the one the host initialized. The comparison identifies the resource location but does not distinguish pipeline-layout construction from descriptor binding without further investigation.

#### Failures limited to linked or binary variants

**Possible failure symptoms:** The same stage and seed pass for SPIR-V or unlinked creation but fail for a linked or binary branch.

**Possible implementation causes:** The failure may involve linked shader-object stage metadata, binary shader recreation, or propagation of descriptor-layout information during shader creation. The source comparison does not establish which implementation layer is responsible.

#### Failures limited to mesh or optional stages

**Possible failure symptoms:** Vertex-only cases pass while tessellation, geometry, task, or mesh groups fail.

**Possible implementation causes:** The selected stage's independent layout may not be attached to the correct shader, or the stage-specific descriptor access and execution path may disagree about set numbering. Feature support and stage-specific shader generation also need investigation.

## Case Pruning

### Requirement-based pruning

- Maintenance11, graphics pipeline library, mesh shader, tessellation, geometry, descriptor-set-count, push-descriptor, and dynamic-rendering-local-read requirements are applied only when the selected construction and descriptor/stage arrangement needs them [support checks](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L353-L409).
- Cases exceeding `maxBoundDescriptorSets` are not run.

### Design-based pruning

- The generator uses ten seeds per stage group and two IO-set orders rather than an unbounded random matrix [case generation](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1897-L1943).
- The `_no_maint11` variant is added only for shader-object cases when the IO set is not first. This keeps the alternate path distinct without duplicating the IO-first combination [variant generation](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1930-L1942).

## Key Takeaways

- The family checks descriptor-set independence through the values copied by shader stages, not through an API query alone.
- All four shader-object construction forms use the same seeded layout/value comparison, which makes differences between linked, unlinked, SPIR-V, and binary paths visible.
- Stage combinations and IO-set ordering expose errors that a vertex-only, single-layout test would miss.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Shader-object family registration | [vktShaderObjectIndependentSetsTests.cpp#L33-L47](../../../modules/vulkan/shader_object/vktShaderObjectIndependentSetsTests.cpp#L33-L47) | Selects the four shader-object construction forms. |
| Case generation | [vktIndependentSetsUtil.cpp#L1880-L1995](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1880-L1995) | Defines construction, stage, seed, ordering, and variant paths. |
| Support checks | [vktIndependentSetsUtil.cpp#L353-L409](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L353-L409) | Applies feature, extension, and descriptor-set limits. |
| Independent pipeline layouts | [vktIndependentSetsUtil.cpp#L1274-L1291](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1274-L1291) | Builds the union layout and independent-set flags. |
| Stage shader layout setup | [vktIndependentSetsUtil.cpp#L1344-L1369](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1344-L1369) | Assigns per-stage descriptor layouts. |
| Descriptor binding and draw | [vktIndependentSetsUtil.cpp#L1705-L1751](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1705-L1751) | Binds descriptors and executes the selected stage combination. |
| Result comparison | [vktIndependentSetsUtil.cpp#L1828-L1877](../../../modules/vulkan/util/vktIndependentSetsUtil.cpp#L1828-L1877) | Compares descriptor contents with the IO buffer. |
| Mustpass inventory | [m11-independent-sets.txt](../../../mustpass/main/vk-default/shader-object/m11-independent-sets.txt) | Lists the 1,440 registered paths. |
