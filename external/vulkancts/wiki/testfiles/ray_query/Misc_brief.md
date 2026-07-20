# Understanding Brief: ray_query misc (and helper_invocations)

## One-Sentence Test Purpose

This test checks whether a `VK_KHR_ray_query` implementation correctly handles a bag of ray-query corner cases that do not fit the larger matrices: dynamic indexing into an array of `rayQueryEXT` objects, reusing one scratch buffer across multiple BLAS builds, building and updating an empty acceleration structure in place, and tracing one ray per workgroup invocation with a varying workgroup size, plus a separate `helper_invocations` family that verifies inline ray queries inside fragment-shader helper invocations alongside `dFdx`/`dFdy` derivatives.

## Background Knowledge

### Multiple families, one source file

`vktRayQueryMiscTests.cpp` registers two direct children of the `ray_query` test category: `misc` and `helper_invocations`. The grouping reason is purely that they share one implementation file; the failure mechanisms are unrelated. `misc` itself is heterogeneous: `dynamic_indexing`, `dynamic_indexing_use_first`, `reuse_scratch_buffer`, `update_empty_bottom`, `update_empty_top`, and a `ray_per_inv_*` matrix. `helper_invocations` is one coherent matrix.

### Dynamic indexing of `rayQueryEXT`

A shader can declare an array of `rayQueryEXT` objects and index it with a runtime variable. The Vulkan spec allows this, but a SPIR-V processor or driver must keep per-element query state coherent across `rayQueryInitializeEXT`, `rayQueryProceedEXT`, and `rayQueryGetIntersectionTypeEXT`. The `dynamic_indexing_use_first` variant makes the use of the queries appear textually before the initialization loop in the GLSL source, which stresses the SPIR-V lowering's handling of forward references and query lifetime.

### In-place AS update of an empty AS

`VK_KHR_acceleration_structure` permits an in-place update (`VK_BUILD_ACCELERATION_STRUCTURE_MODE_UPDATE_KHR`) when the source AS was built with `VK_BUILD_ACCELERATION_STRUCTURE_ALLOW_UPDATE_BIT_KHR`. `update_empty_bottom` and `update_empty_top` deliberately build an AS with `primitiveCount = 0` (or a single NULL-address instance for the top), then perform an in-place update that also has `primitiveCount = 0`, then trace a ray query against it. The expected result is a miss. The scratch buffer and AS storage buffer are pre-filled with random bytes to expose drivers that read uninitialized memory or skip the build entirely.

### Helper invocations and derivatives

In a fragment shader, helper invocations are fragments whose results are discarded but whose side effects (such as derivatives) are needed by neighboring fragments. `dFdx`, `dFdy`, `dFdxCoarse`, `dFdyCoarse`, `dFdxFine`, `dFdyFine` are computed from a quad of fragments, including helper invocations. The test uses an inline ray query inside the fragment shader, calls `rayQueryProceedEXT` and `rayQueryConfirmIntersectionEXT` only when a triangle candidate is found, then writes a color computed from both the analytic derivative of the surface function and the screen-space derivative of `coord`. The host verifies that no pixel has a negative `.z` or `.w` channel.

### Reusable scratch buffer for multiple BLAS builds

`reuse_scratch_buffer` builds two BLASes back-to-back through a `BottomLevelAccelerationStructurePool`, with the pool configured to allocate the build scratch buffer as host-visible (a single shared scratch buffer). Each BLAS contains a different set of triangle rows from a 256x256 grid that is masked by a pseudorandom coverage pattern. The fragment shader traces one ray query per fragment from `(gl_FragCoord.xy, 0)` along `+Z` and writes blue on hit, black on miss. The host compares against a reference generated directly from the coverage mask.

### Per-invocation ray counts

`ray_per_inv_*` runs a compute shader with `local_size_x` chosen from `{61, 64, 127, 128, 251, 256, 509, 512, 1021, 1024, 0}` where `0` means "use `limits.maxComputeWorkGroupSize[0]`". Each invocation traces a ray from `(invocationIndex + 0.5, 0, 0)` along `+Z`. The host pseudorandomly places a quad for some invocations and not others. The expected output is `2` if the invocation ran a query and hit a triangle, `1` if it ran a query and missed, and `0` if it did not run a query. The `_single_*` variants gate the query on `gl_LocalInvocationIndex == k` for first / last / middle, exercising the case where most invocations skip the query.

## One Concrete Example

Representative case: `dEQP-VK.ray_query.misc.dynamic_indexing`. Reconstructed from [`DynamicIndexingCase::initPrograms`](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L128-L196) with `useFirst = false`:

```glsl
#version 460
#extension GL_EXT_ray_query : require
#extension GL_EXT_ray_tracing : require

layout (local_size_x=48, local_size_y=1, local_size_z=1) in;

struct InputData {
    uint goodQueryIndex;
    uint proceedQueryIndex;
};

layout (set=0, binding=0) uniform accelerationStructureEXT topLevelAS;
layout (set=0, binding=1, std430) buffer InputBlock {
    InputData inputData[];
} inputBlock;
layout (set=0, binding=2, std430) buffer OutputBlock {
    uint outputData[];
} outputBlock;

void main()
{
    const uint numQueries = 48u;
    const uint rayFlags = 0u;
    const uint cullMask = 0xFFu;
    const float tmin = 0.1;
    const float tmax = 10.0;
    const vec3 direct = vec3(0, 0, 1);

    rayQueryEXT rayQueries[numQueries];
    vec3 origin;

    InputData inputValues = inputBlock.inputData[gl_LocalInvocationID.x];

    // Initialize all queries. Only goodQueryIndex will have the right origin for a hit.
    for (int i = 0; i < numQueries; i++) {
        origin = ((i == inputValues.goodQueryIndex) ? vec3(0, 0, 0) : vec3(5, 5, 0));
        rayQueryInitializeEXT(rayQueries[i], topLevelAS, rayFlags, cullMask, origin, tmin, direct, tmax);
    }

    // Attempt to proceed with the good query to confirm a hit.
    while (rayQueryProceedEXT(rayQueries[inputValues.proceedQueryIndex]))
        outputBlock.outputData[gl_LocalInvocationID.x] = 1u;
}
```

The host seeds a 48-element `InputData` array with random `goodQueryIndex` values from `[0, 47]`, sets `proceedQueryIndex = goodQueryIndex`, dispatches one workgroup, and asserts every entry of the output buffer equals `1`. The triangle BLAS is at z=1 spanning `[-1, 1] × [-1, 1]`, so only the query whose origin is `(0, 0, 0)` will hit. A correct implementation must:

1. Index `rayQueries[goodQueryIndex]` correctly during both initialization and `proceed`.
2. Initialize all 48 query objects without corrupting each other.
3. Confirm a triangle candidate when the good query is proceeded.

## End-to-End Test Flow

The `misc` and `helper_invocations` families run separate flows. Both share the same `checkRayQuerySupport` extension gate.

```text
[host] check VK_KHR_acceleration_structure + VK_KHR_ray_query feature bits

=== dynamic_indexing (and dynamic_indexing_use_first) ===
[host] seed RNG, generate InputData array (goodQueryIndex == proceedQueryIndex per invocation)
[host] build a triangle BLAS at z=1 covering [-1,1] x [-1,1]
[host] build a TLAS with one instance of that BLAS
[host] dispatch one workgroup of 48 (or 2 for use_first) invocations
[device] initialize all 48 (or 2) ray queries with per-i origins
[device] proceed the single good query; on triangle candidate write outputData[lid] = 1
[host] invalidate output buffer, scan all entries, expect 1 in every slot

=== reuse_scratch_buffer ===
[host] generate 256x256 coverage mask with seeded RNG
[host] build a pool of 2 BLASes using a shared host-visible scratch buffer, each covering half the rows
[host] build a TLAS with both BLASes as instances
[host] draw a full-screen quad; frag shader traces one ray query per fragment from (fragCoord.xy, 0) along +Z
[device] write blue on hit, black on miss
[host] copy image to buffer, build reference from coverage mask, floatThresholdCompare with zero threshold

=== update_empty_bottom / update_empty_top ===
[host] allocate AS storage + scratch buffers; pre-fill with random bytes
[host] build empty AS (primitiveCount=0 for bottom; one NULL-address instance for top) with ALLOW_UPDATE_BIT
[host] in-place update with the same primitive count
[host] build TLAS for the bottom variant (one instance of the empty BLAS)
[host] dispatch one compute invocation that traces a ray query and writes vec4(0,0,1,1) for miss, vec4(1,0,0,1) for hit
[device] expected: no candidate ever appears; outBuffer.color = (0,0,1,1)
[host] read back storage buffer, assert expected color exactly

=== ray_per_inv_* ===
[host] choose workgroup size (one of 61, 64, 127, 128, 251, 256, 509, 512, 1021, 1024, or device max)
[host] choose single mode (all invocations, or first / last / middle)
[host] pseudorandomly decide per-invocation whether a triangle quad exists at z=1
[host] build a single BLAS with the union of all quads, build a TLAS over it
[host] dispatch one workgroup with specialization constants setting local_size
[device] if (condition) initialize and proceed a single ray query per invocation, write 2 (hit) or 1 (miss)
[device] if (!condition) skip the query, leave ssbo[index] = 0
[host] read back SSBO, compare per-invocation to expected (0 / 1 / 2)

=== helper_invocations ===
[host] for each (build, style, mode, screen, model): generate a parametric surface mesh
[host] build a triangle BLAS over the surface's coord vertices, then a TLAS over it
[host] set up a graphics pipeline with vert + frag shaders, push constants for fun_x / fun_y / width / height
[host] clear color image to (0.1, 0.2, 0.3, 0.4); draw the surface
[device] frag shader: initialize ray query from (center.x, center.y, -1) along +Z; on triangle candidate compute analytic + screen-space derivatives; write (cx, cy, sign(dx-abs(cx)), sign(dy-abs(cy)))
[host] copy color image to buffer, scan all pixels
[host] pass if no pixel has .z < 0 or .w < 0
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL compute shader for `dynamic_indexing` and `dynamic_indexing_use_first`, specialized on `local_size_x` and `numQueries` ([vktRayQueryMiscTests.cpp:128-L196](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L128-L196)).
- Inline GLSL vertex + fragment shaders for `reuse_scratch_buffer` ([vktRayQueryMiscTests.cpp:1080-L1121](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1080-L1121)).
- Inline GLSL compute shader for `update_empty_bottom` and `update_empty_top` ([vktRayQueryMiscTests.cpp:1304-L1332](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1304-L1332)).
- Inline GLSL compute shader for `ray_per_inv_*`, specialized on whether the single-invocation condition is active and on which invocation index it gates ([vktRayQueryMiscTests.cpp:1935-L1979](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1935-L1979)).
- Inline GLSL vertex + fragment shaders for `helper_invocations`, with `${DFDX}` / `${DFDY}` template specialization on `dFdx`/`dFdy` vs `dFdxCoarse`/`dFdyCoarse` vs `dFdxFine`/`dFdyFine` ([vktRayQueryMiscTests.cpp:593-L711](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L593-L711)).
- All GLSL is fed through `updateRayTracingGLSL()` (identity passthrough in this CTS version) and built with `vk::ShaderBuildOptions` targeting `SPIRV_VERSION_1_4`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| TLAS / BLAS for the dynamic_indexing triangle scene | yes | yes (b0 in comp) | traversed | no | provides the triangle candidate the good query must hit |
| `InputBlock` SSBO (`misc.dynamic_indexing`) | yes | yes (b1 in comp) | read | no | per-invocation `goodQueryIndex` / `proceedQueryIndex` |
| `OutputBlock` SSBO (`misc.dynamic_indexing`) | yes | yes (b2 in comp) | written | yes | one `uint` per invocation, host asserts all are `1` |
| Coverage mask + BLAS pool + TLAS (`misc.reuse_scratch_buffer`) | yes | yes | traversed | no | the shared scratch buffer is the test target; the mask drives the reference |
| Color image + readback buffer (`misc.reuse_scratch_buffer`) | yes | yes | written by frag | yes | `tcu::floatThresholdCompare` against the reference built from the mask |
| AS storage buffer + scratch build buffer + scratch update buffer (`misc.update_empty_*`) | yes, pre-filled with random bytes | yes | read/written by build commands | no | random pre-fill exposes drivers that skip the build or read uninitialized scratch |
| Storage buffer with one `vec4` (`misc.update_empty_*`) | yes | yes (b1 in comp) | written | yes | holds the miss/hit color the host checks |
| Per-invocation quad triangles + BLAS + TLAS (`misc.ray_per_inv_*`) | yes | yes | traversed | no | drives the per-invocation hit/miss expectation |
| SSBO of `uint` per invocation (`misc.ray_per_inv_*`) | yes | yes (b1 in comp) | written | yes | per-invocation `0` / `1` / `2` value the host scans |
| Surface vertex / coord / center buffers (`helper_invocations`) | yes | yes (VB) | read by vert | no | drives the parametric surface and the per-fragment `coord` and `center` |
| Color image + readback buffer (`helper_invocations`) | yes | yes | written by frag | yes | host scans `.z` / `.w` for negativity |

## What Is Checked

- `misc.dynamic_indexing` / `dynamic_indexing_use_first`: every entry of the output SSBO equals `1`. Anything else fails the case ([vktRayQueryMiscTests.cpp:380-L398](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L380-L398)).
- `misc.reuse_scratch_buffer`: `tcu::floatThresholdCompare` with threshold `(0,0,0,0)` between the rendered color buffer and the reference built directly from the coverage mask ([vktRayQueryMiscTests.cpp:1296-L1301](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1296-L1301)).
- `misc.update_empty_bottom` / `update_empty_top`: the output `vec4` exactly equals `(0, 0, 1, 1)`, the miss color ([vktRayQueryMiscTests.cpp:1653-L1668](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1653-L1668), [L1887-L1902](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1887-L1902)).
- `misc.ray_per_inv_*`: each SSBO entry equals `0` if the invocation did not run a query, `1` if it ran and missed, `2` if it ran and hit ([vktRayQueryMiscTests.cpp:2114-L2135](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2114-L2135)).
- `helper_invocations.*`: every pixel of the color buffer has `.z >= 0` and `.w >= 0`. A negative value in either channel marks a fragment where the analytic and screen-space derivatives disagreed past the sign-check threshold ([vktRayQueryMiscTests.cpp:944-L965](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L944-L965)).

## Behavior Parameter Identification

> **Behavior parameter:** test family (the page's primary axis is which `misc` subfamily or `helper_invocations` matrix is exercised, because each subfamily targets a distinct failure mechanism)
>
> **Candidate values:** `misc.dynamic_indexing`, `misc.dynamic_indexing_use_first`, `misc.reuse_scratch_buffer`, `misc.update_empty_bottom`, `misc.update_empty_top`, `misc.ray_per_inv_*`, `helper_invocations.*`

The reason test family is the primary behavioral axis: each subfamily targets an unrelated implementation property. Within `helper_invocations`, secondary axes are build path (`gpu`/`cpu`), derivative style (`regular`/`coarse`/`fine`), surface mode (`linear_quadratic`/`linear_cubic`/`cubic_quadratic`), screen size, and model size. Within `ray_per_inv_*`, secondary axes are workgroup size, single vs all, and which single invocation.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `misc.dynamic_indexing` | Dynamic indexing into the `rayQueryEXT` array misroutes initialize or proceed to the wrong query object, or the SPIR-V lowering corrupts per-element query state. |
| `misc.dynamic_indexing_use_first` | The SPIR-V lowering does not preserve query state when the use site precedes the initialization site textually in the GLSL source. |
| `misc.reuse_scratch_buffer` | A shared host-visible scratch buffer reused across two BLAS builds is overwritten mid-build, or one build's scratch use trashes the other's. |
| `misc.update_empty_bottom` | An in-place update of an empty bottom-level AS produces an AS that traversal treats as non-empty, or the build reads uninitialized scratch/storage bytes that the host pre-filled with random data. |
| `misc.update_empty_top` | Same as `update_empty_bottom`, but for the top-level AS built from one NULL-address instance. |
| `misc.ray_per_inv_*` (`_all`) | Per-invocation query state is corrupted when every invocation in a large workgroup issues a query, especially near `limits.maxComputeWorkGroupSize[0]`. |
| `misc.ray_per_inv_*` (`_single_*`) | The single-invocation condition is applied to the wrong `gl_LocalInvocationIndex`, or the unused invocations corrupt the SSBO. |
| `helper_invocations.*` | Helper invocations skip the ray query, or the screen-space derivative is computed without including helper-invocation results, producing a negative `.z` or `.w` channel. |

## Important Variations and Special Cases

- **`useFirst` ordering.** `dynamic_indexing_use_first` reduces the workgroup to 2 invocations and 2 queries, and emits the use loop textually before the initialization loop inside a `for (i = 0; i < 2; ++i)` wrapper that runs the use site on iteration 1 and the init site on iteration 0. The SPIR-V must trace query state across the loop body. The `_use_first` variant exercises the same invariance as `dynamic_indexing` but with a deliberately hostile source order.
- **Random pre-fill of AS buffers.** `update_empty_bottom` and `update_empty_top` deliberately fill the AS storage buffer, the build scratch buffer, and (for the bottom variant) the update scratch buffer with pseudorandom bytes before the build. The kPaddingFactor of 8 multiplies the reported sizes so the buffer is larger than strictly needed. A driver that skips the build because the input is empty would leave the random bytes in place, but the spec requires the build to write a valid empty BVH; a driver that reads uninitialized scratch would expose itself through visible corruption.
- **Specialization constants for `ray_per_inv_*`.** The compute shader declares `layout (local_size_x_id=0, local_size_y_id=1, local_size_z_id=2) in;` and the host supplies the actual workgroup size through `VkSpecializationInfo`. The `_0` leaves the choice to `limits.maxComputeWorkGroupSize[0]`, which makes the case device-dependent.
- **Single-invocation gating.** `_single_first` gates on `gl_LocalInvocationIndex == 0`, `_single_last` on `== totalInvs - 1`, `_single_middle` on `== wgSize / 2`. The host's expected-value loop mirrors the same condition so the test isolates the case where most invocations skip the query entirely.
- **CPU build path.** `helper_invocations.cpu.*` builds the BLAS and TLAS through `VK_ACCELERATION_STRUCTURE_BUILD_TYPE_HOST_KHR`, requiring `accelerationStructureFeaturesKHR.accelerationStructureHostCommands`. The GPU path uses the device build.
- **Derivative style.** `regular` uses `dFdx`/`dFdy`; `coarse` uses `dFdxCoarse`/`dFdyCoarse`; `fine` uses `dFdxFine`/`dFdyFine`. The shader computes `dfx = dzx / dx` and `dfy = dzy / dy`, then `cx = dfx - vx`, `cy = dfy - vy`. The final color's `.z` is `sign(dx - abs(cx))` and `.w` is `sign(dy - abs(cy))`. A negative channel means the screen-space derivative diverged from the analytic derivative by more than its own magnitude.
- **Surface mode.** Three modes are enabled (`linear_quadratic`, `linear_cubic`, `cubic_quadratic`). Each combines two of `linear`, `quadratic`, `cubic` for the X and Y axes of the surface. The `ENABLE_ALL_HELPER_COMBINATIONS` compile-time flag would enable nine modes, but the default build uses three.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `checkRayQuerySupport` | [vktRayQueryMiscTests.cpp:63-L67](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L63-L67) | Common extension gate for `VK_KHR_acceleration_structure` + `VK_KHR_ray_query`. |
| `DynamicIndexingParams` | [vktRayQueryMiscTests.cpp:69-L82](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L69-L82) | Defines `useFirst`, `getLocalSizeX`, `getNumQueries`. |
| `DynamicIndexingCase::initPrograms` | [vktRayQueryMiscTests.cpp:128-L196](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L128-L196) | Generates the compute shader, including the `useFirst` ordering variant. |
| `DynamicIndexingInstance::iterate` | [vktRayQueryMiscTests.cpp:233-L399](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L233-L399) | Host setup, dispatch, output verification. |
| `initReuseScratchBufferPrograms` + `reuseScratchBufferInstance` | [vktRayQueryMiscTests.cpp:1080-L1302](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1080-L1302) | Vert/frag shaders, BLAS pool with shared scratch, reference image, comparison. |
| `initEmptyASPrograms` | [vktRayQueryMiscTests.cpp:1304-L1332](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1304-L1332) | Compute shader that writes miss color on no candidate, hit color otherwise. |
| `updateEmptyBottomASInstance` | [vktRayQueryMiscTests.cpp:1348-L1668](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1348-L1668) | Empty BLAS build, in-place update, dispatch, miss-color check. |
| `updateEmptyTopASInstance` | [vktRayQueryMiscTests.cpp:1670-L1902](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1670-L1902) | Same for the TLAS built from one NULL-address instance. |
| `RayPerInvParams` + `RayPerInvPrograms` + `RayPerInvRun` | [vktRayQueryMiscTests.cpp:1904-L2138](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L1904-L2138) | Specialized compute shader, per-invocation gating, SSBO verification. |
| `HelperInvocationsCase::initPrograms` | [vktRayQueryMiscTests.cpp:593-L711](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L593-L711) | Vert + frag shaders, derivative-style template specialization. |
| `HelperInvocationsInstance::iterate` + `verifyResult` | [vktRayQueryMiscTests.cpp:976-L1078](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L976-L1078), [L944-L965](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L944-L965) | Surface mesh generation, graphics pipeline, draw, color-buffer scan. |
| `addHelperInvocationsTests` | [vktRayQueryMiscTests.cpp:2142-L2205](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2142-L2205) | Registers `helper_invocations` matrix. |
| `createMiscTests` | [vktRayQueryMiscTests.cpp:2207-L2271](../../../modules/vulkan/ray_query/vktRayQueryMiscTests.cpp#L2207-L2271) | Registers the `misc` family. |
| Vulkan spec: ray traversal | [raytraversal.adoc](../../../../vulkan-docs/src/chapters/raytraversal.adoc) | `rayQueryProceedEXT` / candidate / committed semantics. |
| Vulkan spec: acceleration structures | [accelstructures.adoc](../../../../vulkan-docs/src/chapters/accelstructures.adoc) | Build modes, `ALLOW_UPDATE_BIT_KHR`, in-place update. |

## Questions / Risk Points for User Audit

- Is `dEQP-VK.ray_query.misc.dynamic_indexing` the right representative walkthrough? It is the simplest case that exercises the unique behavior (dynamic indexing of `rayQueryEXT` arrays). `dynamic_indexing_use_first` would also be a valid choice, but its body is harder to follow because the use site precedes the init site textually.
- Is the `helper_invocations` family correctly described as a single family with multiple secondary axes, or should the page treat it as a co-equal behavior axis with `misc`? The brief treats `misc` and `helper_invocations` as siblings under one page because the task assigns them together; the failure mechanisms are unrelated.
- The `helper_invocations` failure check is a per-pixel negativity scan, not a per-pixel equality comparison. Does that match the user's expectation? The source confirms it: `verifyResult` returns `false` when any pixel has `.z < 0` or `.w < 0`.
- The `update_empty_top` case builds the TLAS from a single geometry whose `instances.data.deviceAddress = 0ull`, with `primitiveCount = 1u` and a build range of `0u`. Is the spec-grounded reading "an empty top-level AS" the right framing? The source comment says "by empty we mean a single NULL-address instance"; the spec calls this an inactive instance.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.ray_query.misc.dynamic_indexing` as the default `## Shader Analysis` walkthrough. It is the smallest case that exercises dynamic indexing of `rayQueryEXT` arrays and yields a clean SPIR-V.
- The brief's `## Background Knowledge` should distill into a short unordered list in the final page (dynamic indexing of `rayQueryEXT`; in-place AS update of an empty AS; helper invocations and derivatives; reusable scratch buffer; per-invocation ray counts and specialization constants).
- `### Failure Cause Mapping` table copies verbatim. `### Cause Analysis` is written fresh, grounded in the specific verification logic of each subfamily.
- Move per-subfamily source-range detail into the source appendix.
- The `helper_invocations` matrix has 2 (builds) x 3 (styles) x 3 (modes) x 2 (screens) x 2 (models) = 72 cases. Document the matrix shape, but do not enumerate every case.
- The `ray_per_inv_*` matrix has 11 (workgroup sizes) x 4 (single modes) - 1 (duplicate _all pruning) = 43 cases. Document the matrix shape, but do not enumerate.
- The page should mention that `helper_invocations` and `misc` are siblings only because they share one source file; their failure mechanisms are unrelated.
