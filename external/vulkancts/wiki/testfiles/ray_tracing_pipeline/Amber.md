## Overview

**Core question:** Do the 12 Amber-scripted ray tracing scenarios produce the exact expected output buffer values when run through the Amber test runner with the required ray tracing features?

- [vktRayTracingAmberTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp) registers a single test family `amber` under the `ray_tracing_pipeline` test category. The file is registration-only: it creates one Amber test case per script and attaches feature and extension requirements.
- All test logic, including shaders, acceleration structures, pipeline configuration, ray dispatch, and output-buffer expectations, lives in 12 Amber scripts under the `ray_tracing` data directory at [external/vulkancts/data/vulkan/amber/ray_tracing/](../../../data/vulkan/amber/ray_tracing/).
- The C++ side does no shader generation, no host-side result checking, and no custom resource setup. Each Amber script declares its own `DEVICE_EXTENSION` and `DEVICE_FEATURE` requirements, its own `PIPELINE`, and its own `EXPECT` assertions against an output image or buffer.
- The page explains the registration mechanism, the behavioral axis formed by the 12 Amber scripts, the three functional clusters those scripts fall into, the Amber-level validation model, and the failure meaning for each cluster.

## Background Knowledge

- **Amber test cases in CTS.** The CTS Amber framework ([vktAmberTestCase.hpp](../../../modules/vulkan/amber/vktAmberTestCase.hpp)) wraps an Amber script into a `tcu::TestCase`. The C++ registration code calls `cts_amber::createAmberTestCase` with a data directory and a script filename, then attaches requirement strings via `addRequirement`. At runtime the Amber runner parses the script, builds the declared Vulkan resources, runs the pipeline, and evaluates the `EXPECT` assertions. The C++ test class does not see the shader source or the result buffer.
- **Amber script structure.** Each `.amber` script is a declarative recipe: `DEVICE_EXTENSION` and `DEVICE_FEATURE` lines gate support; `SHADER` blocks define GLSL stage source; `ACCELERATION_STRUCTURE` blocks define BLAS and TLAS geometry; `PIPELINE` blocks bind descriptors and assemble shader groups into a shader binding table (SBT); `RUN` dispatches the raygen launch; `EXPECT` compares output image or buffer values against literal expected values.
- **Requirement arrays.** The C++ registration attaches three requirement arrays. `stdRayTracingList` covers the base three KHR extensions and three feature bits. `libRayTracingList` adds `VK_KHR_pipeline_library`. `extRayTracingList` adds `VK_KHR_deferred_host_operations`. The Amber scripts also redeclare their own `DEVICE_EXTENSION` and `DEVICE_FEATURE` lines, so both layers enforce the same requirements.

## Registration Hierarchy

```text
ray_tracing_pipeline.amber
├── barycentrics
├── basic
├── basic2
├── basic_lib
├── different-payload-sizes
├── divergent-as
├── flags-accept-first
├── flags-culling
├── flags-force-non-opaque
├── flags-force-opaque
├── flags-skip-chit
└── rt-sample
```

The 12 direct children are registered by [createAmberTests](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L33-L98), which iterates the `amberTests` array. Each entry pairs a script name with a requirement array. The dispatcher at [createTests](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69) adds the `amber` group as the first child of the `ray_tracing_pipeline` test category. All 12 leaves appear in the mustpass at [ray-tracing-pipeline.txt](../../../mustpass/main/vk-default/ray-tracing-pipeline.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Amber script (test case leaf) | `barycentrics`, `basic`, `basic2`, `basic_lib`, `different-payload-sizes`, `divergent-as`, `flags-accept-first`, `flags-culling`, `flags-force-non-opaque`, `flags-force-opaque`, `flags-skip-chit`, `rt-sample` | Each leaf is a self-contained Amber script that exercises a distinct ray tracing scenario. This is the primary behavioral axis. | [amberTests array](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L65-L78) |
| Requirement array | `stdRayTracingList`, `libRayTracingList`, `extRayTracingList` | Selects which KHR extensions and features are attached to the Amber test case. `basic_lib`, `different-payload-sizes`, and `divergent-as` use pipeline library; `rt-sample` uses deferred host operations; the rest use the standard set. | [requirement arrays](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L38-L60) |
| Build scope | Vulkan SC excluded | The entire `amberTests` array is inside `#ifndef CTS_USES_VULKANSC`, so no Amber cases register on Vulkan SC builds. | [createAmberTests](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L37) |

## Behavior Parameters

The primary behavioral axis is the Amber script, which is the test case leaf. The 12 leaves cluster into three functional groups by what aspect of ray tracing they exercise. The C++ registration treats all 12 identically. The behavioral differences live entirely in the Amber scripts.

### Pipeline infrastructure tests - basic, basic2, basic_lib, rt-sample

These scripts exercise the structural assembly of a ray tracing pipeline: shader group assembly, SBT layout, multi-group pipelines, and pipeline libraries. They verify that the Amber-declared pipeline builds and runs, and that the result buffer holds the expected values. The specific property differs per script:

- [`basic.amber`](../../../data/vulkan/amber/ray_tracing/basic.amber) traces a 2x2 raygen grid and stores a computed launch-ID value per pixel. The raygen shader writes directly to the result image without calling `traceRayEXT`, so it tests the basic raygen launch and image store path. The expected output is `1 2 257 258` ([EXPECT line](../../../data/vulkan/amber/ray_tracing/basic.amber#L109)).
- [`basic2.amber`](../../../data/vulkan/amber/ray_tracing/basic2.amber) builds two complete pipeline configurations (two raygen, two miss, two hit groups, two callable) sharing one TLAS with multiple BLAS instances that carry instance offsets, transforms, masks, and flags. It dispatches a 1920x1080 raygen grid. This script exercises multi-group SBT construction and instance configuration. It has no `EXPECT` line, so it only checks that the pipeline builds and the dispatch completes without a crash.
- [`basic_lib.amber`](../../../data/vulkan/amber/ray_tracing/basic_lib.amber) builds three pipeline stages chained via `USE_LIBRARY`: a bottom library (`my_rtlib_bottom`) with miss3, a middle library (`my_rtlib`) that uses the bottom library and adds miss2, and a final pipeline (`my_rtpipeline`) that uses the middle library and adds raygen, miss1, and the hit group. The raygen shader traces three rays with miss indices 0, 1, 2, so the SBT must contain all three miss shaders contributed by the three pipeline stages. The expected output is `1 2 3` ([EXPECT line](../../../data/vulkan/amber/ray_tracing/basic_lib.amber#L156)). This script requires `VK_KHR_pipeline_library`.
- [`rt-sample.amber`](../../../data/vulkan/amber/ray_tracing/rt-sample.amber) traces four rays from x offsets 0 through 3 into a triangle BLAS with four triangle primitives at increasing z depths. The raygen sets payload to 1, the any-hit shader adds `10 * gl_PrimitiveID`, the closest-hit shader adds 100, and the miss shader adds 1000. Rays 0 through 2 hit triangles (primitive IDs 0, 1, 2) and ray 3 misses. The expected output is `101 111 121 1001` ([EXPECT line](../../../data/vulkan/amber/ray_tracing/rt-sample.amber#L112)). This script requires `VK_KHR_deferred_host_operations`.

### Ray flag semantics tests - flags-force-opaque, flags-force-non-opaque, flags-skip-chit, flags-accept-first, flags-culling

These scripts exercise specific `gl_RayFlags*EXT` flags and verify that the implementation honors them. Each traces the same geometry twice with different flags and checks that the output differs as expected:

- [`flags-force-opaque.amber`](../../../data/vulkan/amber/ray_tracing/flags-force-opaque.amber) traces a triangle BLAS with no opacity flags twice. The first ray uses `gl_RayFlagsOpaqueEXT`, which should suppress the any-hit shader. The second ray uses `gl_RayFlagsNoneEXT`, which should invoke the any-hit shader. The any-hit shader writes `1` at the payload index. Expected output `0 1` ([EXPECT line](../../../data/vulkan/amber/ray_tracing/flags-force-opaque.amber#L76)): index 0 stays 0 (AHS skipped), index 1 becomes 1 (AHS ran).
- [`flags-force-non-opaque.amber`](../../../data/vulkan/amber/ray_tracing/flags-force-non-opaque.amber) traces a BLAS instance marked `FORCE_OPAQUE` twice. The first ray uses `gl_RayFlagsNoOpaqueEXT`, which overrides the instance flag and should invoke the any-hit shader. The second ray uses `gl_RayFlagsNoneEXT`, which leaves the instance opaque and should suppress the any-hit shader. Expected output `1 0` ([EXPECT line](../../../data/vulkan/amber/ray_tracing/flags-force-non-opaque.amber#L80)): index 0 becomes 1 (AHS ran), index 1 stays 0 (AHS skipped). This is the inverse of `flags-force-opaque`.
- [`flags-skip-chit.amber`](../../../data/vulkan/amber/ray_tracing/flags-skip-chit.amber) traces a triangle BLAS twice. The first ray uses `gl_RayFlagsNoneEXT` and should invoke the closest-hit shader, which writes `1` at the payload index. The second ray uses `gl_RayFlagsSkipClosestHitShaderEXT` and should skip the closest-hit shader, leaving the output at 0. Expected output `1 0` ([EXPECT line](../../../data/vulkan/amber/ray_tracing/flags-skip-chit.amber#L74)).
- [`flags-accept-first.amber`](../../../data/vulkan/amber/ray_tracing/flags-accept-first.amber) uses a procedural AABB with an intersection shader that calls `reportIntersectionEXT` twice: first at t=0.6, then at t=0.5. The first ray uses `gl_RayFlagsNoneEXT`, so both candidates compete and the closest (t=0.5) wins. The second ray uses `gl_RayFlagsTerminateOnFirstHitEXT`, so the first reported hit (t=0.6) is accepted immediately and traversal terminates before the t=0.5 report. The closest-hit shader stores `gl_HitTEXT` at the payload index. Expected output `0.5 0.6` ([EXPECT line](../../../data/vulkan/amber/ray_tracing/flags-accept-first.amber#L89)).
- [`flags-culling.amber`](../../../data/vulkan/amber/ray_tracing/flags-culling.amber) traces four triangles in one BLAS: a front-facing opaque triangle, a back-facing triangle, another back-facing triangle, and a front-facing opaque triangle, arranged at two x positions. Six rays exercise `gl_RayFlagsCullFrontFacingTrianglesEXT`, `gl_RayFlagsCullOpaqueEXT`, `gl_RayFlagsCullBackFacingTrianglesEXT`, and `gl_RayFlagsCullNoOpaqueEXT`. The closest-hit shader stores `round(gl_HitTEXT)`. Expected output `3 4 4 3 4 4` ([EXPECT line](../../../data/vulkan/amber/ray_tracing/flags-culling.amber#L114)), where the hit t values are 3 or 4 depending on which triangle survives culling.

### Specialized behavior tests - barycentrics, different-payload-sizes, divergent-as

These scripts exercise distinct ray tracing properties outside the pipeline-infrastructure and ray-flag clusters:

- [`barycentrics.amber`](../../../data/vulkan/amber/ray_tracing/barycentrics.amber) launches an 8x8 grid of rays at a single triangle and stores the rounded barycentric x-coordinate (`round(barycentrics.x * 100)`) per pixel. The closest-hit shader reads the `hitAttributeEXT vec2 barycentrics` built-in. Miss pixels store 0. The expected output is an 8x8 array with tolerance 1, encoding the barycentric coordinate distribution across the triangle ([EXPECT lines](../../../data/vulkan/amber/ray_tracing/barycentrics.amber#L104-L111)). This script verifies that the implementation reports correct barycentric hit attributes for triangle geometry.
- [`different-payload-sizes.amber`](../../../data/vulkan/amber/ray_tracing/different-payload-sizes.amber) traces two rays that miss, each using a different payload location and type: location 0 is `uint` (4 bytes), location 1 is `uvec4` (16 bytes). The miss shaders write 1 and 2 respectively. Expected output `1 2` ([EXPECT line](../../../data/vulkan/amber/ray_tracing/different-payload-sizes.amber#L87)). This script requires `VK_KHR_pipeline_library` and verifies that multiple payload locations with different sizes coexist in one pipeline.
- [`divergent-as.amber`](../../../data/vulkan/amber/ray_tracing/divergent-as.amber) binds two TLASes (one at z=1, one translated to z=-2) and dispatches six rays. Rays with launch ID divisible by 3 (`index % 3 == 0`) trace into `topLevelAS1` and hit; the rest trace into `topLevelAS2` and miss. The miss shader sets payload to 10, the closest-hit shader sets it to 20. The raygen stores `payload + index`. Expected output `20 11 12 23 14 15` ([EXPECT line](../../../data/vulkan/amber/ray_tracing/divergent-as.amber#L101)): index 0 hits (20+0=20), indices 1 and 2 miss (10+1=11, 10+2=12), index 3 hits (20+3=23), indices 4 and 5 miss (10+4=14, 10+5=15). This script requires `VK_KHR_pipeline_library` and tests divergent acceleration-structure selection across invocations.

## Shader Analysis

Shader code is part of the tested behavior, but it lives entirely in the Amber scripts, not in CTS C++ source. The [`shader-analyzer`](../../../../../.agents/skills/shader-analyzer/SKILL.md) skill operates on CTS builder functions that generate GLSL or SPIR-V from C++, and these tests have no such C++ builder. Each Amber script embeds its own GLSL `SHADER` blocks inline. No representative shader walkthrough subsections are created, because there is no CTS-managed shader compilation path to analyze.

The key shader behaviors exercised across the 12 scripts are: raygen launch-ID computation and `traceRayEXT` dispatch; intersection-shader `reportIntersectionEXT` with candidate hit ordering; any-hit shader invocation and suppression by opacity flags; closest-hit shader `gl_HitTEXT` and `hitAttributeEXT` barycentric reads; miss shader payload writes; and callable shader declaration without invocation. These behaviors are described per script in `## Behavior Parameters` above.

## Runtime Execution and Result Checking

- **Amber runner as the execution engine.** The CTS Amber test case delegates all execution to the Amber runner. The runner parses the `.amber` script, enables the declared extensions and features, compiles the GLSL shader blocks to SPIR-V, builds the declared acceleration structures, assembles the pipeline and SBT, and dispatches the `RUN` command. The C++ test class does not participate in any of these steps.
- **Requirement attachment.** [createAmberTests](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L86-L92) iterates the requirement array for each test and calls `addRequirement` for each non-empty entry. The Amber runner checks these requirements alongside the script's own `DEVICE_EXTENSION` and `DEVICE_FEATURE` declarations before running.
- **Pass/fail via `EXPECT` assertions.** Ten of the twelve scripts include `EXPECT` lines that compare output image or buffer values against literal expected values. `basic2.amber` has no `EXPECT` line, so it passes if the pipeline builds and the raygen dispatch completes without a device loss or crash. The `EXPECT` semantics support exact equality (`EQ`) and tolerance-based comparison (`TOLERANCE n EQ`). `barycentrics.amber` uses tolerance 1 to allow rounding slack.
- **No host-side result scan.** The C++ test class does not read back or compare any result buffer. All result checking is inside the Amber script's `EXPECT` assertions, which the Amber runner evaluates after the `RUN` dispatch. A test case passes only if every `EXPECT` assertion matches, or if the script has no `EXPECT` and the dispatch completes without error.
- **Vulkan SC exclusion.** The entire `amberTests` array sits inside `#ifndef CTS_USES_VULKANSC` ([createAmberTests](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L37)), so no Amber cases register on Vulkan SC builds. On non-SC builds, all 12 cases register unconditionally.
- **Data directory resolution.** The C++ registration passes `dataDir = "ray_tracing"` to `createAmberTestCase` ([data directory](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L80)). The Amber runner resolves this relative to the Vulkan data root, landing at `external/vulkancts/data/vulkan/amber/ray_tracing/` where all 12 `.amber` files reside.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Raygen launch-ID computation or image-store path produced wrong output values; or the basic raygen grid dispatch failed. |
| `basic2` | Multi-group SBT construction, instance offset/transform/mask/flag handling, or pipeline build with multiple shader groups failed or crashed. |
| `basic_lib` | Pipeline library chaining did not contribute shader groups correctly, so the final pipeline was missing miss shaders from the library stages. |
| `rt-sample` | Any-hit `gl_PrimitiveID` reporting, closest-hit payload accumulation, or miss routing produced wrong per-ray payload values. |
| `flags-force-opaque` | `gl_RayFlagsOpaqueEXT` did not suppress the any-hit shader, or the default-opacity any-hit invocation was wrong. |
| `flags-force-non-opaque` | `gl_RayFlagsNoOpaqueEXT` did not override the instance `FORCE_OPAQUE` flag, or the any-hit invocation was wrong. |
| `flags-skip-chit` | `gl_RayFlagsSkipClosestHitShaderEXT` did not skip the closest-hit shader, or the closest-hit ran when it should not have. |
| `flags-accept-first` | `gl_RayFlagsTerminateOnFirstHitEXT` did not accept the first reported intersection, or candidate-hit ordering produced the wrong t value. |
| `flags-culling` | One of the cull flags (`CullFrontFacing`, `CullBackFacing`, `CullOpaque`, `CullNoOpaque`) culled the wrong triangle, or face determination was wrong. |
| `barycentrics` | The `hitAttributeEXT vec2 barycentrics` hit attribute reported wrong barycentric coordinates for triangle geometry. |
| `different-payload-sizes` | Multiple payload locations with different sizes were not handled independently, or miss-index routing delivered the payload to the wrong miss shader. |
| `divergent-as` | Divergent acceleration-structure selection across invocations did not route rays to the correct TLAS, or the two TLAS transforms were not distinguished. |

All 12 scripts share the Amber runner, the CTS Amber test case wrapper, the requirement attachment mechanism, and the Vulkan data directory resolution. A failure common to multiple scripts across different clusters points at shared Amber runner infrastructure or the CTS Amber test case setup, not at any single script's logic.

### Cause Analysis

#### Pipeline infrastructure failures

**Possible failure symptoms:** One of `basic`, `basic2`, `basic_lib`, or `rt-sample` fails. For `basic`, `basic_lib`, and `rt-sample`, the `EXPECT` assertion reports a mismatch between the output buffer and the expected values. For `basic2`, which has no `EXPECT`, the failure is a device loss, pipeline build error, or crash during the 1920x1080 dispatch.

**Possible implementation causes:** These scripts test the structural correctness of pipeline assembly. `basic_lib` chains three pipeline stages via `USE_LIBRARY`, so a failure there points at the `VK_KHR_pipeline_library` implementation not contributing shader groups from library stages to the final pipeline's SBT. The Vulkan spec requires that shader groups in a library pipeline are available in the pipeline that links it; if the final pipeline's SBT is missing miss2 or miss3, that is a library-linking bug. `rt-sample` adds `VK_KHR_deferred_host_operations` to its requirements, and the `EXPECT` values encode `1 + 10 * gl_PrimitiveID + 100` (hit) or `1 + 1000` (miss), so a wrong primitive ID or a miss routed to the closest-hit path would produce a wrong value. `basic2` tests multi-group SBT construction with instance configuration including `OFFSET`, `MASK`, `TRANSFORM`, and `FLAGS`, so a crash or build failure there points at instance offset or flag handling. Source-level investigation of the driver's pipeline library or SBT construction logic would be needed to confirm the exact cause.

#### Ray flag semantics failures

**Possible failure symptoms:** One of the five `flags-*` scripts fails its `EXPECT` assertion. Each script traces the same geometry twice with different flags and expects different results, so the symptom is that the two output values are swapped, identical when they should differ, or both incorrect.

**Possible implementation causes:** The Vulkan spec defines that `gl_RayFlagsOpaqueEXT` forces the geometry to be treated as opaque, suppressing the any-hit shader, and `gl_RayFlagsNoOpaqueEXT` forces it to be non-opaque, enabling the any-hit shader even if the instance is marked `FORCE_OPAQUE`. If `flags-force-opaque` produces `1 1` instead of `0 1`, the any-hit shader ran when it should have been suppressed. If `flags-force-non-opaque` produces `0 0` instead of `1 0`, the `NoOpaque` flag did not override the instance `FORCE_OPAQUE` flag. The `flags-accept-first` script is sensitive to the order in which `reportIntersectionEXT` calls are processed: with `TerminateOnFirstHit`, the first reported hit (t=0.6) should be accepted immediately, so a result of `0.5 0.5` would mean the implementation continued traversal and accepted the second report. The `flags-culling` script depends on correct front/back-facing triangle determination and on the four cull flags selecting the right surviving triangle. Grounded investigation should check the specific flag combination that failed against the Vulkan ray culling rules in the `VK_KHR_ray_tracing_pipeline` specification.

#### Specialized behavior failures

**Possible failure symptoms:** One of `barycentrics`, `different-payload-sizes`, or `divergent-as` fails its `EXPECT` assertion. `barycentrics` reports a per-pixel barycentric value mismatch. `different-payload-sizes` reports `1 2` expected but wrong values. `divergent-as` reports `20 11 12 23 14 15` expected but wrong values.

**Possible implementation causes:** The `barycentrics` script reads the `hitAttributeEXT vec2 barycentrics` built-in in the closest-hit shader and stores `round(barycentrics.x * 100)`. The expected output encodes a specific barycentric distribution across an 8x8 grid hitting a single triangle, so a mismatch points at the implementation reporting wrong barycentric hit attributes for triangle geometry. The Vulkan spec requires that the intersection barycentrics are the vertex weights of the hit primitive; a systematic offset or swapped components would be a hit-attribute reporting bug. The `different-payload-sizes` and `divergent-as` scripts both require `VK_KHR_pipeline_library` and test payload and dispatch divergence respectively. `divergent-as` uses two TLASes bound at descriptor set bindings 0 and 1, and the raygen selects between them based on `index % 3`, so a wrong output at indices 0 and 3 (which should hit) points at the rays at multiples of 3 being routed to the wrong TLAS. Source-level investigation of the descriptor binding or payload location handling would be needed to confirm the exact cause for these two scripts.

## Case Pruning

### Requirement-based pruning

- All 12 Amber cases require `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`, and `VK_KHR_buffer_device_address` with their corresponding feature bits (`accelerationStructure`, `rayTracingPipeline`, `bufferDeviceAddress`). These are declared both in the Amber scripts' `DEVICE_EXTENSION` and `DEVICE_FEATURE` lines and in the C++ requirement arrays [stdRayTracingList](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L38-L44).
- `basic_lib`, `different-payload-sizes`, and `divergent-as` additionally require `VK_KHR_pipeline_library` [libRayTracingList](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L45-L52).
- `rt-sample` additionally requires `VK_KHR_deferred_host_operations` [extRayTracingList](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L53-L60).
- The entire test family is excluded from Vulkan SC builds via `#ifndef CTS_USES_VULKANSC` [createAmberTests](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L37).

### Design-based pruning

- No parameter matrix is generated. The 12 Amber scripts are a fixed, hand-authored set with no generated variants. The C++ registration loops over the `amberTests` array once and registers each script as a single test case [amberTests array](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L65-L78).

## Key Takeaways

- The `amber` test family is registration-only from the CTS perspective: the C++ file creates 12 Amber test cases and attaches requirements, but all shaders, geometry, pipeline configuration, and result checking live in the 12 `.amber` scripts.
- The primary behavioral axis is the Amber script itself. The 12 leaves cluster into three functional groups: pipeline infrastructure (`basic`, `basic2`, `basic_lib`, `rt-sample`), ray flag semantics (`flags-force-opaque`, `flags-force-non-opaque`, `flags-skip-chit`, `flags-accept-first`, `flags-culling`), and specialized behavior (`barycentrics`, `different-payload-sizes`, `divergent-as`).
- Three requirement tiers exist: the standard set, the pipeline-library set, and the deferred-host-operations set. Each script's tier is determined by its C++ requirement array assignment.
- Pass/fail is driven entirely by Amber `EXPECT` assertions, which compare output image or buffer values against literal expected values. One script (`basic2`) has no `EXPECT` and passes if the dispatch completes without error.
- A failure isolated to one cluster points at that cluster's specific mechanism (pipeline library linking, ray flag handling, or hit-attribute and dispatch divergence). A failure common to scripts across clusters points at shared Amber runner infrastructure. See `## Failure Meaning` for the per-cause analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createAmberTests` | [vktRayTracingAmberTests.cpp#L33-L98](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L33-L98) | Registration of the `amber` test group and all 12 Amber test cases |
| Requirement arrays | [vktRayTracingAmberTests.cpp#L38-L60](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L38-L60) | Three feature and extension requirement tiers: standard, pipeline library, deferred host operations |
| `amberTests` array | [vktRayTracingAmberTests.cpp#L65-L78](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L65-L78) | Pairs each script name with its requirement array |
| Requirement attachment loop | [vktRayTracingAmberTests.cpp#L86-L92](../../../modules/vulkan/ray_tracing/vktRayTracingAmberTests.cpp#L86-L92) | Iterates requirement strings and calls `addRequirement` |
| Amber script directory | [external/vulkancts/data/vulkan/amber/ray_tracing/](../../../data/vulkan/amber/ray_tracing/) | All 12 `.amber` script files with shaders, geometry, pipelines, and `EXPECT` assertions |
| Category dispatcher | [vktRayTracingTests.cpp#L69](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L69) | `createAmberTests` is the first child added to the `ray_tracing_pipeline` test category |
| Mustpass evidence | [ray-tracing-pipeline.txt](../../../mustpass/main/vk-default/ray-tracing-pipeline.txt) | All 12 `amber.*` leaves listed in the default ray-tracing-pipeline mustpass |