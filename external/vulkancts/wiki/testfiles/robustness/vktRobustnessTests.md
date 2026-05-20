# vktRobustnessTests.cpp

## Overview

This page documents the root dispatcher for the Vulkan CTS `robustness` category. The file creates the
category-level test group and attaches the directly registered robustness subgroups; detailed test-case generation and
verification logic are delegated to the implementation files it includes.

## Role of file

`vktRobustnessTests.cpp` is a registration / dispatcher file. Its `createTests()` entry point constructs the category
group from the caller-provided name and registers direct children under `robustness` by calling subgroup factory
functions from related robustness files.

The file also performs one small structural merge: after registering `buffer_access`, it searches for that child by name
and inserts the variable-pointer subgroup under `buffer_access`; if `buffer_access` is not present, it creates a
`buffer_access` group before inserting the variable-pointer subgroup.

## Source code link

- Source: [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L61-L99)
- Header declaration: [vktRobustnessTests.hpp](../../../modules/vulkan/robustness/vktRobustnessTests.hpp#L30-L36)
- Vulkan package root registration: [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1372-L1374)
- Vulkan SC package root registration: [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1438-L1441)

## Inspected related files

| File | Evidence used |
|------|---------------|
| [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L25-L34) | Root include list for directly delegated robustness families. |
| [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L61-L99) | Root `createTests()` registration order and Vulkan SC conditional children. |
| [vktRobustnessTests.hpp](../../../modules/vulkan/robustness/vktRobustnessTests.hpp#L30-L36) | Public declaration of the root robustness factory. |
| [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1372-L1374) | Standard Vulkan package attaches `robustness` to the root test package. |
| [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1438-L1441) | Vulkan SC package also attaches `robustness` to the root test package. |
| [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2097-L2122) | Group names for `buffer_access`, `pipeline_robustness_buffer_access`, and `descriptor_heap_buffer_access`. |
| [vktRobustnessVertexAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1290-L1296) | Group name for `vertex_access`. |
| [vktRobustnessIndexAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1132-L1171) | Group name and local parameter loops for `bind_index_buffer2`. |
| [vktRobustnessIndexAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1174-L1204) | Group name for `index_access`. |
| [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4358-L4372) | Group names for `robustness2`, `image_robustness`, and `pipeline_robustness`. |
| [vktNonRobustBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L57) | Group name and Vulkan SC behavior for `non_robust_buffer_access`. |
| [vktRobustness1VertexAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L943-L951) | Group name for `robustness1_vertex_access`. |
| [vktRobustnessOOBAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L965-L980) | Group name and initial generated dimensions for `oob_access`. |
| [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1897-L1914) | `through_pointers` subgroup inserted under `buffer_access`, not as a root child. |
| [robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L1-L42) | Mustpass evidence that the default Vulkan mustpass list contains direct robustness prefixes such as `bind_index_buffer2` and `buffer_access`. |

## Registration Hierarchy

```text
robustness
├── buffer_access
├── vertex_access
├── index_access
├── robustness2
├── image_robustness
├── pipeline_robustness (non-VulkanSC only)
├── non_robust_buffer_access
├── pipeline_robustness_buffer_access (non-VulkanSC only)
├── bind_index_buffer2 (non-VulkanSC only)
├── descriptor_heap_buffer_access (non-VulkanSC only)
├── robustness1_vertex_access
└── oob_access
```

The tree above lists only direct children registered by the root dispatcher. The `through_pointers` group is created by
`vktRobustBufferAccessWithVariablePointersTests.cpp`, but the dispatcher inserts it below `buffer_access` rather than
as a direct `robustness` child.

## Test Families

### buffer_access

Registered unconditionally by the root dispatcher via `createBufferAccessTests()`. The implementation constructs the
`buffer_access` group and populates buffer out-of-bounds access cases in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2097-L2103).
The root dispatcher then appends the `through_pointers` subgroup below this same child when it can find the existing
`buffer_access` node.

### vertex_access

Registered unconditionally via `createVertexAccessTests()`. The implementation constructs the `vertex_access` group and
adds vertex-format access tests in
[vktRobustnessVertexAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1290-L1296).

### index_access

Registered unconditionally via `createIndexAccessTests()`. The implementation constructs the `index_access` group and
creates indexed draw cases from visible mode names such as `draw_indexed`, `draw_indexed_indirect`,
`draw_indexed_indirect_count`, and `draw_multi_indexed` in
[vktRobustnessIndexAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1174-L1204).

### robustness2

Registered unconditionally via `createRobustness2Tests()`. The implementation creates the `robustness2` group through
`createTestGroup()` in
[vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4358-L4361) and populates it
through the shared robustness-extension builder in
[vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4311-L4321).

### image_robustness

Registered unconditionally via `createImageRobustnessTests()`. The implementation creates the `image_robustness` group
through `createTestGroup()` in
[vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4363-L4366) and populates it
through the shared robustness-extension builder in
[vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4324-L4327).

### pipeline_robustness

Registered by the root dispatcher only when `CTS_USES_VULKANSC` is not defined. The implementation creates the
`pipeline_robustness` group in
[vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4368-L4372), with nested
`robustness2` and `image_robustness` branches populated in
[vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4329-L4345).

### non_robust_buffer_access

Registered unconditionally by the root dispatcher. The implementation creates the `non_robust_buffer_access` group, but
its Amber test children are added only outside Vulkan SC builds in
[vktNonRobustBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L57).

### pipeline_robustness_buffer_access

Registered by the root dispatcher only when `CTS_USES_VULKANSC` is not defined. The implementation creates the
`pipeline_robustness_buffer_access` group and reuses the buffer-access builder with pipeline robustness enabled in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2106-L2114).

### bind_index_buffer2

Registered by the root dispatcher only when `CTS_USES_VULKANSC` is not defined. The implementation creates the
`bind_index_buffer2` group for `vkCmdBindIndexBuffer2` / device-address-command index-buffer access cases in
[vktRobustnessIndexAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1132-L1171).

### descriptor_heap_buffer_access

Registered by the root dispatcher only when `CTS_USES_VULKANSC` is not defined. The implementation creates the
`descriptor_heap_buffer_access` group and reuses the buffer-access builder with descriptor-heap behavior enabled in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2116-L2122).

### robustness1_vertex_access

Registered unconditionally via `createRobustness1VertexAccessTests()`. The implementation constructs the
`robustness1_vertex_access` group and adds one test per entry in `robustness1Tests` in
[vktRobustness1VertexAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L943-L951).

### oob_access

Registered unconditionally via `createOOBAccessTests()`. The implementation constructs the `oob_access` group and begins
building dimensions for robust-on/off, access type, and robustness level in
[vktRobustnessOOBAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L965-L980).

## Parameter dimensions

This root dispatcher does not define data-driven runtime parameters for individual test cases. Its observable dimensions
are structural:

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Direct root children | `buffer_access`, `vertex_access`, `index_access`, `robustness2`, `image_robustness`, `pipeline_robustness`, `non_robust_buffer_access`, `pipeline_robustness_buffer_access`, `bind_index_buffer2`, `descriptor_heap_buffer_access`, `robustness1_vertex_access`, `oob_access` | Root `addChild()` calls in [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L65-L97). |
| Build profile | Standard Vulkan includes all listed root children; Vulkan SC omits the root children guarded by `#ifndef CTS_USES_VULKANSC`. | Conditional blocks in [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L86-L95). |
| Variable-pointer placement | `through_pointers` is inserted under `buffer_access`, not under `robustness` directly. | Child search and insertion in [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L69-L82), with group creation in [vktRobustBufferAccessWithVariablePointersTests.cpp](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1897-L1902). |

Subgroup-specific parameter matrices are owned by the corresponding implementation files. For example,
`bind_index_buffer2` uses offsets `0` and `100`, draw modes, out-of-bounds types, and a non-VulkanSC device-address
variant in [vktRobustnessIndexAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1132-L1164),
while `oob_access` begins with robust-on/off, access-type, and robustness-level dimensions in
[vktRobustnessOOBAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L969-L980).

## Support / feature requirements

The root dispatcher itself does not call Vulkan feature queries or device capability checks. It records build-profile
support only through `CTS_USES_VULKANSC` guards:

- `pipeline_robustness` is registered only for non-VulkanSC builds in
  [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L84-L88).
- `pipeline_robustness_buffer_access`, `bind_index_buffer2`, and `descriptor_heap_buffer_access` are registered only
  for non-VulkanSC builds in
  [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L91-L95).
- `non_robust_buffer_access` is registered by the root dispatcher in all builds, but its implementation adds Amber test
  children only outside Vulkan SC builds in
  [vktNonRobustBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L48-L55).

Any Vulkan feature requirements for individual tests are delegated to the registered implementation files and are not
established by this root dispatcher.

## Verification methods

No per-test verification method is implemented in `vktRobustnessTests.cpp`; it only constructs the test tree. Verification
criteria are implemented in the delegated test-family files. As examples of verification logic outside the dispatcher,
`oob_access` checks that out-of-bounds reads return zero or that out-of-bounds writes leave image data unchanged in
[vktRobustnessOOBAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L930-L948), while
other families should be documented on their own Level-3 pages.

## Test principles

- Keep the category root shallow: direct children are registered by factory functions, and detailed generation stays in
  implementation-specific files.
- Preserve the existing `buffer_access` branch when adding variable-pointer coverage by locating the already-created
  child and appending `through_pointers` below it.
- Use compile-time Vulkan SC guards at the dispatcher level only for families that are not registered as root children in
  Vulkan SC builds.
- Reuse implementation builders for related families, such as pipeline-robustness buffer-access and descriptor-heap
  buffer-access variants, instead of generating those cases in the root dispatcher.

## Notes / uncertainties

- This page intentionally covers only the root registration / dispatcher file. It does not attempt to document full
  parameter matrices or feature gates for every child family.
- The default mustpass file contains observed direct prefixes for the registered standard Vulkan robustness children,
  including `bind_index_buffer2`, `buffer_access`, `descriptor_heap_buffer_access`, `image_robustness`, `index_access`,
  `non_robust_buffer_access`, `oob_access`, `pipeline_robustness`, `pipeline_robustness_buffer_access`,
  `robustness1_vertex_access`, `robustness2`, and `vertex_access`; the file order is lexical/test-list order rather
  than dispatcher registration order.
- Vulkan SC mustpass coverage was not inspected for this subtask; Vulkan SC statements here are limited to the visible
  `CTS_USES_VULKANSC` guards in the inspected source files.
