# vktSubgroupsBuiltinVarTests.cpp

## Overview

[`vktSubgroupsBuiltinVarTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1) documents the [`subgroups.builtin_var`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1948) branch. It covers built-in scalar subgroup variables such as subgroup size, invocation id, number of subgroups, and subgroup id.

## Role

Implementation file that registers tests under the verified group name [`builtin_var`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1948).

## Source Code

- Primary source: [`vktSubgroupsBuiltinVarTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1)
- Related helper source: [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2429-L2638)
- Related helper declarations: [`vktSubgroupsTestsUtils.hpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63)

## Registration Hierarchy

```text
subgroups.builtin_var
├── graphics
├── compute
├── framebuffer
├── ray_tracing (non-VulkanSC only)
└── mesh (non-VulkanSC only)
```

## Test Families

### graphics

Registered direct child of `builtin_var`; generated leaves and parameter matrices are summarized from the source registration loops.
### compute

Registered direct child of `builtin_var`; generated leaves and parameter matrices are summarized from the source registration loops.
### framebuffer

Registered direct child of `builtin_var`; generated leaves and parameter matrices are summarized from the source registration loops.
### ray_tracing

Registered direct child of `builtin_var`; generated leaves and parameter matrices are summarized from the source registration loops.
### mesh

Registered direct child of `builtin_var`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- `TestType` names and compute-only built-ins are declared near the file start, observed in [`vktSubgroupsBuiltinVarTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1948-L2098).
- Shared subgroup harness dimensions include framebuffer, compute, mesh, and ray-tracing execution helpers where a child group registers those stage families. The helper callback interfaces carry width/height/workgroup/local-size and `subgroupSize` data through [`CheckResult` declarations](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63).

## Support / Feature Requirements

Subgroup support, optional subgroup-size-control requirements, ray-tracing pipeline, mesh shader, and stage support, with support code starting at [`vktSubgroupsBuiltinVarTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1630) when this file defines a local check. Shared stage support is delegated to utilities such as [`supportedCheckShader()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L979-L996).

## Verification Methods

The checks compare shader-written built-in values against `subgroupSize`, invocation-hit counts, computed subgroup counts, and subgroup ids, evidenced by local verification or test execution code in [`vktSubgroupsBuiltinVarTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1738-L1901) and by common helper pass/fail logic in [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2622-L2637).

## Test Principles Observed

- The file registers a stable direct-child tree and generates deeper leaves from loops, enum values, arrays, or case lists.
- Compute-like tests generally read back SSBO/image data and call a result callback with the observed subgroup size.
- Graphics, framebuffer, mesh, and ray-tracing branches reuse common helpers so the same operation semantics are checked across supported shader stages.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.builtin_var`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`.
