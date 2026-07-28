# Understanding Brief: Descriptor Update Acceleration Structure Tests

## One-Sentence Test Purpose

This test checks whether four descriptor-update mechanisms expose the intended top-level acceleration structure to ray-query and ray-tracing shaders across every registered stage.

## Background Knowledge

### Acceleration-structure descriptors and traversal

A `VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR` binding supplies a top-level acceleration structure (TLAS), which is the starting point for traversal. The TLAS contains instances that refer to bottom-level acceleration structures (BLASes) holding geometry ([top-level acceleration structures](../../../../vulkan-docs/src/chapters/accelstructures.adoc#L127-L137)).

Why it matters here:

- Each case writes one TLAS handle to set 0, binding 0. A wrong descriptor value changes which geometry the shader traverses.
- Ray query starts traversal inside a shader with `rayQueryProceedEXT`; ray tracing starts it with `traceRayEXT`. Vulkan permits ray query in any shader stage with the feature enabled, while pipeline tracing uses a ray-tracing pipeline ([ray traversal entry points](../../../../vulkan-docs/src/chapters/raytraversal.adoc#L4-L24)).

### Four ways to supply the same descriptor

The matrix uses a regular write, an update template, a push descriptor, or a push-descriptor template. A regular acceleration-structure write takes its source from `VkWriteDescriptorSetAccelerationStructureKHR` in the `pNext` chain of `VkWriteDescriptorSet` ([acceleration-structure descriptor writes](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3094-L3100), [source-data rule](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3161-L3167)). An update template describes how Vulkan reads the same descriptor data from application memory; a push form records descriptor contents in command-buffer state ([descriptor update templates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4104-L4133), [template types](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4179-L4209)).

Why it matters here:

- All four methods must make the same TLAS visible to the shader.
- The non-push methods update an allocated descriptor set before command recording. The push methods write set 0 while recording the command buffer.

## One Concrete Example

Consider `dEQP-VK.binding_model.descriptor_update.acceleration_structure.ray_query.regular.comp`. The host builds a sloped square from two triangles, writes its TLAS to set 0, binding 0 with `vkUpdateDescriptorSets`, and dispatches a `16 x 16 x 1` compute grid. Each invocation casts a +Z ray through one sample position, converts the candidate triangle distance to a fixed-point integer, and stores it in an `R32_SINT` image. The host calculates the same plane-intersection distance for all 256 pixels. A descriptor that refers to the wrong TLAS, or no usable TLAS, cannot reproduce that field of expected values ([geometry and TLAS creation](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L588-L625), [ray-query shader body](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2283-L2315), [host verification](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L642-L723)).

The `ray_tracing` path needs a second mental model. Its selected `rgen`, `chit`, or `miss` stage reads the descriptor under test through `traceRayEXT`. For the `chit` and `miss` leaves, that shader launches a second ray, and a fixed closest-hit shader writes `gl_HitTEXT` to the result image. This extra pipeline recursion is why those leaves require `maxRayRecursionDepth >= 2` ([ray-tracing shader construction](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1958-L2097), [recursion-depth gate](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1938-L1955)).

## End-to-End Test Flow

```text
[host] select ray_query or ray_tracing, one update method, and one registered stage
[host] create the 16 x 16 R32_SINT result image and host-visible readback buffer
[host] create and build the sloped BLAS/TLAS referenced by the descriptor under test
[host] create set 0 for the acceleration structure and set 1 for the result image
[host] apply one regular/template update, or record one push/push-template update
[host] build any service acceleration structure and shader binding tables required by a ray-tracing pipeline
[host] record a draw, dispatch, or trace command after the acceleration-structure build barrier
[device] ray_query traverses the descriptor directly, or ray_tracing follows it through traceRayEXT
[device] write the fixed-point hit distance to one result-image texel per launch position
[host] copy the image to the readback buffer, wait, invalidate mapped memory, and scan 256 integers
[host] pass only when every retrieved value equals the analytical plane-intersection value
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Every generated GLSL program uses GLSL 4.60 and `SPIRV_VERSION_1_4` ([compute generator](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1316-L1348), [ray-pipeline generators](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1473-L1683)).
- `ray_query` injects the same traversal-and-store body into graphics, compute, or ray-tracing stages. Helper stages provide the draw or outer ray needed to invoke the selected stage.
- `ray_tracing` builds two shader-group sets. The selected stage traces through the descriptor under test; fixed `*0` shaders handle the secondary ray and output path ([program generation](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1958-L2097), [shader groups](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2099-L2219)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Sloped BLAS and TLAS under test | yes | yes, set 0 binding 0 | read by traversal | no | The test updates this acceleration-structure descriptor value. |
| Service BLAS/TLAS | yes, for ray-pipeline cases | yes, set 2 binding 0 | read to invoke the selected ray stage | no | It routes execution to the selected stage without replacing the descriptor under test. |
| `R32_SINT` result image | yes | yes, set 1 binding 0 | shader writes 256 fixed-point distances | copied through the result buffer | It records the shader-observed traversal result. |
| Host-visible result buffer | yes | transfer destination | receives image copy | yes | The host scans this buffer for exact equality. |
| Descriptor set or push-descriptor state | yes | yes | shader consumes set 0 | no | It carries the TLAS through the selected update method. |
| Shader binding tables | yes, for ray-pipeline cases | used by `vkCmdTraceRaysKHR` | select ray shader groups | no | They route ray-generation, hit, miss, and callable execution. |

## What Is Checked

- The shared host checker expects 256 signed integers. For pixel `(x, y)`, it computes the sloped plane's hit distance and multiplies by `1048576` ([expected-value calculation](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L642-L666)).
- `ray_query` records the candidate triangle's `t` value. `ray_tracing` records `gl_HitTEXT` from the hit reached through the descriptor under test.
- Every retrieved pixel value must equal its expected integer. The host logs the first nine mismatches, then prints the expected and retrieved grids. The comparison allows no tolerance ([result scan](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L668-L723)).
- The host also requires the set 0 update count to equal one. Any other count raises `Invalid descriptor update` before result checking ([update paths and count](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L441-L486), [push paths and count check](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L511-L575)).

## Behavior Parameter Identification

> **Behavior parameter:** `traversal mechanism` (the `ray_query` / `ray_tracing` intermediate-node axis)
>
> **Candidate values:** `ray_query`, `ray_tracing`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ray_query` | The updated acceleration-structure descriptor is not exposed to ray-query traversal in the selected stage, or the traversal/result path returns the wrong candidate distance. |
| `ray_tracing` | The updated acceleration-structure descriptor is not exposed to pipeline ray tracing in the selected stage, or recursive shader-group routing and hit-result recording produce the wrong distance. |

All values also depend on the selected `regular`, `with_template`, `with_push`, or `with_push_template` update method. A method-wide pattern can point to descriptor encoding, template interpretation, push-descriptor state, or command-recording errors shared by both traversal mechanisms.

## Important Variations and Special Cases

- `ray_query` has 48 leaves: four update methods times 12 stages (`vert`, `tesc`, `tese`, `geom`, `frag`, `comp`, `rgen`, `ahit`, `chit`, `miss`, `sect`, `call`). The traversal body stays the same, but its invocation source and pipeline differ.
- `ray_tracing` has 12 leaves: four update methods times `rgen`, `chit`, and `miss`. Registration excludes the other stages by design because the source marks these three as `rayTracing = true` ([matrix construction](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566-L2662)).
- Push forms use a descriptor-set layout created with `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` and do not allocate set 0. Template forms create a one-entry template for one acceleration-structure descriptor ([layout choice](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L304-L318), [template construction](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L451-L486)).
- The whole `acceleration_structure` branch is absent from Vulkan SC builds because its parent excludes it from `CTS_USES_VULKANSC` builds ([parent registration](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateTests.cpp#L1907-L1918)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shared resource, update, execution, and verification path | [`BindingAcceleratioStructureTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L373-L586) | Applies one selected update, executes the pipeline, copies the image, and returns pass/fail. |
| Test geometry and expected values | [geometry creation and `verify()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L588-L723) | Connects traversal output to the exact host oracle. |
| Ray-query compute representative | [`BindingAcceleratioStructureComputeTestInstance`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1316-L1368) | Reconstructs the compact representative shader and dispatch shape. |
| Ray-query ray-pipeline stages | [`BindingAcceleratioStructureRayTracingTestInstance`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1370-L1842) | Shows how ray query runs in ray-generation, hit, miss, intersection, and callable stages. |
| Pipeline ray-tracing behavior | [`BindingAcceleratioStructureRayTracingRayTracingTestInstance`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L1844-L2281) | Builds the two ray paths, shader groups, SBTs, and service TLAS. |
| Shader bodies | [`getRayQueryShaderBodyText()` and `getRayTracingShaderBodyText()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2283-L2328) | Defines the two distinct traversal observation mechanisms. |
| Support and instance selection | [`checkSupport()` and `createInstance()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2355-L2476) | Applies feature gates and routes each behavior/stage to its implementation. |
| Exact registration matrix | [`createDescriptorUpdateASTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorUpdateASTests.cpp#L2566-L2662) | Registers 60 leaves across two traversal mechanisms. |
| Default mustpass inventory | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L10898-L10957) | Confirms all 60 registered paths. |

## Questions / Risk Points for User Audit

- Does the document identify the `ray_query` / `ray_tracing` axis as the behavior parameter, with update method and shader stage as secondary dimensions?
- Does the two-step `ray_tracing` path make clear that the selected stage reads the descriptor under test and a fixed secondary hit stage records the distance?
- Are the four descriptor-update methods distinguished without implying that they change shader code?
- Are the service TLAS and the TLAS under test kept separate in the resource model?

The inspected registration, shader builders, runtime path, generated SPIR-V, and host checker resolve these points; no semantic risk remains open for the final rewrite.

## Conversion Notes for Final Wiki Rewrite

- Keep `ray_query` and `ray_tracing` as the two `## Behavior Parameters` values and copy the Failure Cause Mapping table unchanged.
- Preserve two representative shader walkthroughs because the source uses different traversal instructions and pipeline structures. Use `ray_query.regular.comp` for the direct query path and `ray_tracing.with_template.chit` for the recursive pipeline path.
- Keep the four update methods and stage inventories in the parameter table. Move builder-function detail to the source appendix.
- Distill Background Knowledge to TLAS descriptor meaning, the two traversal entry points, and descriptor update versus push/template state.
