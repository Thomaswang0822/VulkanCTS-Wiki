# Understanding Brief: ray_query builtin + advanced

## One-Sentence Test Purpose

This test checks whether the `VK_KHR_ray_query` built-in result-query functions return the values the implementation is required to expose for a candidate or committed intersection, and whether two advanced cases (a null acceleration-structure descriptor and a SPIR-V wrapper function around a ray query) still produce the correct result.

## Background Knowledge

### Acceleration structures: TLAS and BLAS

Ray tracing must find which primitive a ray hits without testing every triangle or AABB in the scene. An acceleration structure is the bounding-volume hierarchy (BVH) that does this: primitives are wrapped in leaf AABBs and merged bottom-up into a root AABB, then traversal walks that tree top-down, pruning subtrees the ray misses. This is the single-tree model most readers already know.

Vulkan splits that tree into two levels so heavy data is never duplicated. A **bottom-level acceleration structure (BLAS)** is the BVH built once from a single object's triangles or AABBs, in that object's local space. A **top-level acceleration structure (TLAS)** is a cheaper, shallower BVH built not from primitives but from *instances*. A ray enters the TLAS; when it reaches an instance leaf it applies that instance's transform and descends into the referenced BLAS, where the familiar primitive BVH walk continues. The TLAS device address is the starting point for traversal.

This mirrors instance rendering: one expensive mesh (here, one BLAS) is reused across many placements (here, many instances). Moving an object updates only one instance transform plus a fast TLAS rebuild, instead of rebuilding millions of triangles. Both Vulkan and DirectX expose the same two-level shape because vendors build traversal hardware around it. These definitions are in the [`accelstructures.adoc`](../../../../vulkan-docs/src/chapters/accelstructures.adoc) chapter.

### Instances

An instance is one entry in the TLAS instance array: one placement of one BLAS. Each instance record carries:

- a 3x4 **transform** matrix placing the referenced BLAS in the world (the source of the `objectToWorld` / `worldToObject` matrices several built-ins query);
- an **accelerationStructureReference**, the device address of the BLAS this instance points at (the TLAS-to-BLAS link);
- a 24-bit **instanceCustomIndex** exposed to shaders as `InstanceCustomIndexKHR`;
- an 8-bit visibility **mask** (the instance is hit only if `rayCullMask & instance.mask != 0`);
- a 24-bit **instanceShaderBindingTableRecordOffset** selecting which hit-group shaders run for this instance;
- 8 bits of per-instance **flags** (force-opaque, force-no-opaque, cull-disable, etc.).

The instance's position in the array is its `InstanceId`, distinct from its `instanceCustomIndex`. The Builtin test uses these fields as checkable values: distinct per-instance transforms, custom indices, and SBT offsets make the corresponding built-ins return different, verifiable numbers per cell.

### Ray query object and traversal control flow

A ray query is a shader-visible object created with `rayQueryInitializeEXT`. Unlike pipeline ray tracing (`OpTraceRayKHR`), traversal is driven **inline** by the shader through `rayQueryProceedEXT`, which returns `true` while there is a candidate intersection to inspect and `false` once traversal finishes.

Traversal has two states. A **candidate** is an intersection the traversal found but the shader has not yet decided about. A **committed** intersection is the one the shader accepted. While a candidate is present, the shader inspects its type with `rayQueryGetIntersectionTypeEXT(rayQuery, committed)`:

- candidate (`committed == false`): `gl_RayQueryCandidateIntersectionAABBEXT` or `gl_RayQueryCandidateIntersectionTriangleEXT`;
- committed (`committed == true`): `none`, `triangle`, or `generated`.

For a triangle candidate the shader calls `rayQueryConfirmIntersectionEXT` to commit it as a `triangle`. For an AABB candidate the shader calls `rayQueryGenerateIntersectionEXT(t)` to commit it as a `generated` intersection at distance `t` (AABBs have no implicit hit point, so the shader supplies one). If neither is called, the candidate is dropped and the next `proceed` continues. `rayQueryTerminateEXT` stops traversal early. These candidate/committed/confirm/generate semantics are specified in the [`raytraversal.adoc`](../../../../vulkan-docs/src/chapters/raytraversal.adoc) chapter.

### Opaque and non-opaque geometry

Geometry and instances carry an opaque flag. Opaque means the hit is accepted without giving the shader a chance to reject it. Non-opaque means the shader must explicitly confirm a triangle candidate (or generate one for an AABB) before it commits. The `flow` test deliberately uses `gl_RayFlagsNoOpaqueEXT` so the confirm path is exercised; most value-returning built-ins also rely on the candidate/committed distinction that the opaque flag controls.

### Two acceleration-structure bindings in ray-tracing-pipeline cases

In the graphics and compute stages there is only one acceleration-structure descriptor: the ray-query TLAS the inline query traces against. In the ray-tracing-pipeline stage variants the test binds two AS descriptors. Binding 1 is the "regular" TLAS used by `traceRayEXT` to land in a hit shader; binding 2 is the "ray-query TLAS" that the inline `rayQueryInitializeEXT` inside that hit shader traces against. They are separate descriptor slots because the two traversal mechanisms are distinct: pipeline tracing invokes hit/miss shader stages through the shader binding table, while a ray query runs inline in whichever stage called it. This is a CTS binding arrangement, not a Vulkan concept.

## One Concrete Example

Representative case: `dEQP-VK.ray_query.builtin.flow.comp.triangles` (compute stage, triangle geometry). The shader body generated by [`TestConfigurationFlow::getShaderBodyText`](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L1986) for triangles is, reconstructed and simplified:

```glsl
uint rayFlags = gl_RayFlagsNoOpaqueEXT;   // candidate requires confirm
uint cullMask = 0xFF;
float tmin     = 0.0;
float tmax     = 9.0;
vec3  origin   = vec3((float(pos.x) + 0.5) / float(size.x), (float(pos.y) + 0.5) / float(size.y), 0.0);
vec3  direct   = vec3(0.0, 0.0, -1.0);
uint  value    = 4;                         // expected on full success
rayQueryEXT rayQuery;

rayQueryInitializeEXT(rayQuery, rayQueryTopLevelAccelerationStructure, rayFlags, cullMask, origin, tmin, direct, tmax);

if (rayQueryProceedEXT(rayQuery))           // value 4 -> 3: a candidate appeared
{
  value--;
  if (rayQueryGetIntersectionTypeEXT(rayQuery, false) == gl_RayQueryCandidateIntersectionTriangleEXT)
  {
    value--;                                 // 3 -> 2: it is a triangle candidate
    rayQueryConfirmIntersectionEXT(rayQuery);
    rayQueryProceedEXT(rayQuery);
    if (rayQueryGetIntersectionTypeEXT(rayQuery, true) == gl_RayQueryCommittedIntersectionTriangleEXT)
      value--;                               // 2 -> 1: committed as triangle
  }
}

imageStore(result, pos, ivec4(value, 0, 0, 0));
```

Expected output is `1` for every cell. Each decrement is gated on a distinct, spec-defined traversal event, so a wrong `value` localizes which built-in misbehaved.

## End-to-End Test Flow

```text
[host] choose TestType (which built-in to query) from the builtin/advanced arrays
[host] compute expected result vector m_expected from geometry/instance/transform parameters
       - integer built-ins: exact int32 expected per cell
       - float built-ins: quantized as int32 = float * FIXED_POINT_DIVISOR
[host] build bottom-level AS (triangles or AABBs), with per-instance transforms / IDs / SBT offsets
[host] build top-level AS over the bottom-level AS instances
[host] create result storage image (R32_SINT) and readback buffer
[host] write descriptor set: result image (b0), TLAS (b1), ray-query TLAS (b2)
[host] generate GLSL (or, for using_wrapper_function, SPIR-V) containing the per-TestType shader body
[host] build pipeline for the selected stage (graphics / compute / ray-tracing) and dispatch/trace
[device] shader executes rayQueryInitializeEXT then proceed/confirm/generate per the TestType body
[device] imageStore of the queried built-in value (or the flow counter) into the result image
[host] copy result image to host-visible buffer, map it
[host] verify(): compare result vs m_expected, exact for int built-ins, tolerance for fixed-point
[host] pass only if failures == 0
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL shader source strings, one per `TestType`, produced by `getShaderBodyText`-family functions. Each string is spliced into a stage-specific boilerplate wrapper by `GraphicsConfiguration::initPrograms`, `ComputeConfiguration::initPrograms`, or `RayTracingConfiguration::initPrograms`.
- For `using_wrapper_function` only: the shader body is assembled directly as SPIR-V (`isSPIRV == true`) and added via `spirvAsmSources`, because the test specifically exercises a hand-written SPIR-V wrapper function around the ray-query calls. This case is limited to compute.
- Per-stage pipelines (graphics / compute / ray-tracing) and, for ray-tracing, a shader binding table.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| result storage image (`VK_FORMAT_R32_SINT`) | yes | yes (descriptor b0) | written by `imageStore` | yes (copy to buffer) | single channel carries the per-cell queried built-in value |
| top-level acceleration structure (TLAS) | yes | yes (descriptor b1) | traversed | no | geometry/instances used for the regular pipeline-traced reference in ray-tracing cases |
| ray-query TLAS (`rayQueryTopLevelAccelerationStructure`) | yes | yes (descriptor b2) | traversed by `rayQueryInitializeEXT` | no | the AS the ray query actually traces against |
| bottom-level AS (triangles or AABBs) | yes | folded into TLAS | traversed indirectly | no | carries the per-cell geometry whose hit supplies the queried values |
| result readback buffer | yes | yes | copied into by `vkCmdCopyImageToBuffer` | yes | host maps it for `verify()` |

## What Is Checked

- Per cell `(x,y)` of the 8x8 result grid, the shader stores the value returned by the `TestType`-selected built-in (or the `flow` counter).
- Host `verify()` compares the stored int32 against `m_expected`, computed from the same geometry/instance parameters.
- Integer built-ins (`primitiveid`, `instanceid`, `instancecustomindex`, `getraytmin`, intersection type enums, `getintersection*index`, SBT record offset): exact equality.
- Fixed-point built-ins (origin/direction vectors, barycentrics, transforms): `|retrieved - expected| <= FIXED_POINT_ALLOWED_ERROR` after dividing by `FIXED_POINT_DIVISOR`.
- For vector built-ins (`TestConfigurationVector`), strict component matching is on by default; matrix built-ins use `TestConfigurationMatrix` with a 4x4 component layout.
- A case passes only when the total `failures` count is zero.

## Behavior Parameter Identification

> **Behavior parameter:** `TestType` (the built-in / advanced query under test)
>
> **Candidate values:** `flow`, `primitiveid`, `instanceid`, `instancecustomindex`, `intersectiont`, `objectrayorigin`, `objectraydirection`, `objecttoworld`, `worldtoobject`, `getraytmin`, `getworldrayorigin`, `getworldraydirection`, `getintersectioncandidateaabbopaque`, `getintersectionfrontfaceCandidate`, `getintersectionfrontfaceCommitted`, `getintersectiongeometryindexCandidate`, `getintersectiongeometryindexCommitted`, `getintersectionbarycentricsCandidate`, `getintersectionbarycentricsCommitted`, `getintersectioninstanceshaderbindingtablerecordoffsetCandidate`, `getintersectioninstanceshaderbindingtablerecordoffsetCommitted`, `rayqueryterminate`, `getintersectiontypeCandidate`, `getintersectiontypeCommitted`, plus the two advanced values `null_as` and `using_wrapper_function`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `flow` | Ray-query traversal control-flow built-ins (`proceed`/`confirm`/`generate`/`terminate`/`getIntersectionType`) report wrong candidate or committed state. |
| `primitiveid`, `instanceid`, `instancecustomindex`, `getintersection*index*` | Identifier-returning built-ins report a wrong per-geometry or per-instance integer value. |
| `intersectiont`, `getraytmin` | Parametric-distance / `tmin` built-ins report a wrong float (encoded as fixed-point). |
| `objectrayorigin`, `objectraydirection`, `getworldrayorigin`, `getworldraydirection` | Ray origin/direction built-ins report a wrong vector in world or object space. |
| `objecttoworld`, `worldtoobject` | Per-instance transform matrix built-ins report a wrong 3x4 matrix. |
| `getintersectioncandidateaabbopaque` | Candidate-AABB opacity built-in reports a wrong opaque flag. |
| `getintersectionfrontface*` | Front-face built-in reports a wrong facing flag for the candidate/committed triangle. |
| `getintersectionbarycentrics*` | Barycentric built-in reports wrong candidate/committed triangle barycentrics. |
| `getintersectioninstanceshaderbindingtablerecordoffset*` | SBT-record-offset built-in reports a wrong instance offset for candidate/committed. |
| `rayqueryterminate` | `rayQueryTerminateEXT` does not stop traversal as required. |
| `getintersectiontype*` | Intersection-type built-in reports a wrong candidate/committed enum value. |
| `null_as` (advanced) | Null acceleration-structure descriptor is not treated as empty traversal. |
| `using_wrapper_function` (advanced) | Ray-query calls inside a hand-written SPIR-V wrapper function misbehave (compute only). |

## Important Variations and Special Cases

- **Candidate vs. committed pairs.** Several built-ins (`frontface`, `geometryindex`, `barycentrics`, `instanceshaderbindingtablerecordoffset`, `intersectiontype`) are registered twice: once querying the *candidate* and once querying the *committed* intersection. They are separate `TestType` values so a failure localizes to one of the two states.
- **Geometry-dependent pruning.** `getintersectioncandidateaabbopaque` is only run with AABB geometry; `frontface`, `barycentrics` candidate/committed are only run with triangles. Other built-ins run with both.
- **`single` scenes.** Many built-ins use a single geometry/instance (`instancesGroupCount=1`, `geometriesGroupCount=1`); the multi-geometry/multi-instance built-ins (`primitiveid`, `instanceid`, `instancecustomindex`, intersection indices, SBT offset) use `2` instances and `8` geometries to make the expected values differ per cell.
- **`null_as` feature gating.** This case additionally requires `VK_EXT_robustness2` with `nullDescriptor`, `VK_KHR_buffer_device_address`, and a distinct capabilities id (`_null_acceleration`) so it runs on devices that support the null-descriptor path.
- **`using_wrapper_function` stage restriction.** Limited to compute (`VK_SHADER_STAGE_COMPUTE_BIT`) and uses SPIR-V assembly rather than generated GLSL.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `TestType` enum and geometry types | [vktRayQueryBuiltinTests.cpp:61](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L61) | Defines which built-in each case queries. |
| `TestParams` and fixed-point constants | [vktRayQueryBuiltinTests.cpp:187](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L187) | Carries per-case config and the fixed-point encoding constants. |
| `flow` shader body (triangles + AABBs) | [vktRayQueryBuiltinTests.cpp:1986](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L1986) | Representative traversal control-flow counter. |
| `TestConfigurationFlow` expected init | [vktRayQueryBuiltinTests.cpp:1928](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L1928) | Expected `value==1` for the flow counter. |
| `TestConfiguration::verify` (int) | [vktRayQueryBuiltinTests.cpp:1591](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L1591) | Exact int32 comparison and failure counting. |
| `TestConfigurationFloat::verify` | [vktRayQueryBuiltinTests.cpp:1649](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L1649) | Fixed-point tolerance comparison. |
| `RayQueryBuiltinTestCase::checkSupport` | [vktRayQueryBuiltinTests.cpp:6052](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6052) | Ray-query + acceleration-structure feature gates and per-stage support. |
| `null_as` capability setup | [vktRayQueryBuiltinTests.cpp:6083](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6083) | Robustness2 / nullDescriptor requirements for the advanced null-AS case. |
| `createBuiltinTests` registration | [vktRayQueryBuiltinTests.cpp:6291](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6291) | 24 built-in `TestType` values crossed with stages and geometry. |
| `createAdvancedTests` registration | [vktRayQueryBuiltinTests.cpp:6419](../../../modules/vulkan/ray_query/vktRayQueryBuiltinTests.cpp#L6419) | `null_as` + `using_wrapper_function` advanced cases. |
| Vulkan spec: ray query traversal | [raytraversal.adoc:623](../../../../vulkan-docs/src/chapters/raytraversal.adoc) | Candidate/committed/confirm/generate/terminate semantics. |
| Vulkan spec: null descriptor | [VK_KHR_ray_query appendix](../../../../vulkan-docs/src/appendices/VK_KHR_ray_query.adoc) | Ray query extension and null-descriptor interaction. |

## Questions / Risk Points for User Audit

- Is the `flow` case the right default representative walkthrough, or should a value-returning built-in (e.g. `primitiveid` or `getintersectionbarycentricsCommitted`) be the default instead? `flow` best exercises the traversal control-flow built-ins, which underpin all the value built-ins.
- Is the candidate-vs-committed split correctly framed as the key special-case variation? The brief treats candidate/committed pairs as separate `TestType` values rather than a behavior axis, because the axis is the built-in under test, not the candidate/committed state.
- The `null_as` case binds `VK_NULL_HANDLE` as the AS descriptor. I grounded the "empty traversal" expectation in the robustness2 null-descriptor model; should the page also cite an explicit spec line if one exists beyond the appendix?
- Are the fixed-point tolerance details (`FIXED_POINT_DIVISOR`, `FIXED_POINT_ALLOWED_ERROR`) worth keeping in the final page, or should they be condensed?

## Conversion Notes for Final Wiki Rewrite

- Use `flow` (compute, triangles) as the default representative shader walkthrough; it is the cleanest single case that exercises the traversal state machine that every other built-in depends on.
- Carry the Behavior Parameter Identification (`TestType`) and the Failure Cause Mapping table directly into the final page's `## Behavior Parameters` and `### Failure Cause Mapping` sections.
- Keep the candidate-vs-committed split as an Important Variations item, not as a separate behavior axis.
- Condense the fixed-point encoding into one or two sentences in the final page rather than repeating the full constant breakdown.