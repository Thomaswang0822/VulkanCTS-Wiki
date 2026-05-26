# vktSubgroupsBasicTests.cpp

## Overview

[`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1) documents the [`subgroups.basic`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2196-L2198) branch. It registers basic subgroup operation tests for elect and barrier-style operations across compute, graphics, framebuffer, ray-tracing, and mesh-oriented execution paths.

## Role

Implementation file that builds and registers the verified group name [`basic`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2196-L2198). Unlike the root dispatcher, this file also defines the operation enum, case parameters, shader generation, support checks, execution routing, and result callbacks used by its generated children.

## Source Code

- Primary source: [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1)
- Shared subgroup helper source: [`vktSubgroupsTestsUtils.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3990-L4173)
- Shared callback declarations: [`vktSubgroupsTestsUtils.hpp`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63)

## Registration Hierarchy

```text
subgroups.basic
├── graphics
├── compute
├── framebuffer
├── ray_tracing (non-VulkanSC only)
└── mesh (non-VulkanSC only)
```

## Test Families

### graphics

Registers one `VK_SHADER_STAGE_ALL_GRAPHICS` case per operation except `subgroupMemoryBarrierShared`, which is skipped before non-compute registration because shared memory is not available in non-compute shaders. Registration is visible in [`createSubgroupsBasicTests()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2259-L2274).

### compute

Registers compute cases for every operation and for both `requiredSubgroupSize == false` and `requiredSubgroupSize == true`; the generated names use the operation name plus `_requiredsubgroupsize` for the required-size variant, as shown in [`createSubgroupsBasicTests()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2219-L2237).

### framebuffer

Registers per-stage framebuffer cases over fragment, vertex, tessellation evaluation, tessellation control, and geometry shader stages, with `elect_fragment` intentionally skipped by the source comment at [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2289-L2303).

### ray_tracing

Registers one all-ray-tracing case per operation under non-VulkanSC builds after the non-compute shared-memory-barrier skip, using `SHADER_STAGE_ALL_RAY_TRACING` and the shared `supportedCheck`, `initPrograms`, and `test` callbacks at [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2276-L2287).

### mesh

Registers mesh and task shader cases under non-VulkanSC builds for every operation and for both required-subgroup-size settings; generated names append the shader stage name and optionally `_requiredsubgroupsize`, as shown in [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2239-L2257).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Operation type | `elect`, `subgroupBarrier`, `subgroupMemoryBarrier`, `subgroupMemoryBarrierBuffer`, `subgroupMemoryBarrierShared`, and `subgroupMemoryBarrierImage` from `OpType` in [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L43-L52). |
| Direct child group | `graphics`, `compute`, `framebuffer`, `ray_tracing`, and `mesh` groups are constructed in [`createSubgroupsBasicTests()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2198-L2203). |
| Framebuffer shader stage | Fragment, vertex, tessellation evaluation, tessellation control, and geometry stages are enumerated by `fbStages` in [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2204-L2210). |
| Mesh shader stage | Mesh and task shader stages are enumerated under `#ifndef CTS_USES_VULKANSC` in [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2211-L2216). |
| Required subgroup size | Compute and mesh registrations iterate `{false, true}` via `boolValues`; required-size cases append `_requiredsubgroupsize` in [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2217-L2237) and [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2239-L2257). |
| Required subgroup size sweep | Runtime execution loops over power-of-two sizes from `minSubgroupSize` to `maxSubgroupSize` for compute/mesh required-size cases in [`test()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1949-L1973) and [`test()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2010-L2034). |

## Support / Feature Requirements

The local [`supportedCheck()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1788-L1845) performs the support gating for this file. It requires subgroup support and `VK_SUBGROUP_FEATURE_BASIC_BIT` before any case runs, checks `VK_EXT_subgroup_size_control`, `subgroupSizeControl`, `computeFullSubgroups`, and `requiredSubgroupSizeStages` for required-size cases, records geometry/tessellation point-size support, and delegates shader-stage availability to [`supportedCheckShader()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L4151-L4172). For non-`elect` non-compute cases it also requires `VK_SUBGROUP_FEATURE_BALLOT_BIT`, and under non-VulkanSC it checks `VK_KHR_ray_tracing_pipeline` for ray-tracing stages and `VK_EXT_mesh_shader` plus `vertexPipelineStoresAndAtomics` for mesh/task stages; task-shader cases additionally require `taskShader` support.

## Verification Methods

Compute and mesh paths route through [`test()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1922-L2035), which calls [`makeComputeTest()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L4116-L4123) or [`makeMeshTest()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L4125-L4131). The helper submits dispatch or mesh tasks, reads back result buffers, invokes the supplied `CheckResultCompute` callback, and returns pass only when no iteration failed in [`makeComputeOrMeshTestRequiredSubgroupSize()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3990-L4064). The basic-file callbacks check elected invocations and barrier results through [`checkComputeOrMeshSubgroupElect()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L277-L283) and [`checkComputeOrMeshSubgroupBarriers()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L285-L294).

Graphics and ray-tracing all-stage paths are also routed through [`test()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2037-L2188). Graphics all-stage cases use `allStages()` with vertex-pipeline callbacks after checking fragment SSBO support, while ray-tracing cases use `allRayTracingStages()` with analogous elect/barrier callbacks; the relevant branches are visible in [`test()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2037-L2116) and [`test()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2118-L2185). Framebuffer children use [`noSSBOtest()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1847-L1919), which selects the appropriate framebuffer helper and no-SSBO result callback for vertex, fragment, geometry, and tessellation-stage cases.

## Test Principles Observed

- The file uses one `CaseDefinition` structure to carry operation type, shader-stage set, geometry point-size support storage, and required-subgroup-size mode into support, program-generation, and execution callbacks, as defined in [`vktSubgroupsBasicTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L54-L60).
- `subgroupMemoryBarrierShared` is generated for compute and mesh paths, but is skipped for graphics, framebuffer, and ray-tracing paths because the source explicitly continues before non-compute registration for that operation in [`createSubgroupsBasicTests()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2259-L2263).
- SPIR-V 1.4 is selected for ray-tracing or mesh-shading stages, while other paths use SPIR-V 1.3, as shown in [`initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1760-L1770).
- Compute and mesh required-size variants validate every supported power-of-two required subgroup size rather than checking only a single advertised value, as shown in [`test()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1953-L1971) and [`test()`](../../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2014-L2032).

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.basic`. Generated operation and stage leaves are documented in the test-family and parameter sections rather than expanded in the parseable tree.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`.
