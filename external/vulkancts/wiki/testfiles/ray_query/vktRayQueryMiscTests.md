# vktRayQueryMiscTests

This file registers two direct category children: `misc` and `helper_invocations`. The `misc` group is created in [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2207-L2211), and the helper-invocation group is created in [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2142-L2173).

## Source Files

| Role | Link |
|------|------|
| Misc and helper-invocation implementation | [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp) |

## Registration Hierarchy

```text
ray_query
├── misc
└── helper_invocations
```

## Test Families

### misc — Miscellaneous ray-query behavior

The `misc` branch registers `dynamic_indexing`, `dynamic_indexing_use_first`, `reuse_scratch_buffer`, `update_empty_bottom`, `update_empty_top`, and generated `ray_per_inv_*` cases [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2207-L2270). The `ray_per_inv_*` names combine workgroup sizes, all-vs-single invocation mode, and first/last/middle single-invocation suffixes [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2232-L2266).

### helper_invocations — Helper-invocation behavior

The `helper_invocations` branch crosses build path (`gpu`, `cpu`), derivative style (`regular`, `coarse`, `fine`), several mode names, screen dimensions, and model dimensions [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2142-L2203).

## Parameter Dimensions

| Branch | Observed dimensions | Evidence |
|--------|---------------------|----------|
| `misc` | dynamic-indexing use-first flag, scratch-buffer reuse, empty bottom/top updates, workgroup sizes, all/single invocation, single first/last/middle position | [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2212-L2267) |
| `helper_invocations` | CPU/GPU build, derivative style, mode, screen size, model size | [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2142-L2203) |

## Support Requirements

Common ray-query support requires `VK_KHR_acceleration_structure` and `VK_KHR_ray_query` [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L64-L67). Dynamic-indexing cases also check ray-query and acceleration-structure feature bits [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L198-L208). Helper-invocation CPU builds require `accelerationStructureHostCommands` [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L575-L590).

## Verification Methods

Dynamic indexing reads an output buffer and expects each value to equal one [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L380-L398). Helper invocations call a dedicated `verifyResult()` path and convert it to pass/fail [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L944-L1078). Empty-AS update cases read output colors and expect the miss-shader blue payload [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1653-L1668) and [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1887-L1902). Per-invocation ray tests compare SSBO values against references and fail when unexpected values are logged [vktRayQueryMiscTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1937-L2138).

## Test Principles

The file targets ray-query corner cases that do not fit the larger matrices, using direct buffer or color checks to confirm dynamic indexing, helper-invocation, empty-AS update, and per-invocation behavior.
