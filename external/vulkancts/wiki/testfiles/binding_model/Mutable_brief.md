# Understanding Brief: `binding_model.mutable_descriptor`

## One-Sentence Test Purpose

This test checks whether mutable descriptor bindings can change active descriptor type, participate in writes and copies, and expose the correct resource through each generated shader while preserving the rules for descriptor arrays, pool type lists, update timing, and ordinary non-mutable bindings.

## Background Knowledge

### Mutable descriptor state and type lists

A non-mutable descriptor-set layout binding fixes one descriptor type. A mutable binding uses `VK_DESCRIPTOR_TYPE_MUTABLE_EXT` plus a `VkMutableDescriptorTypeListEXT` that lists its permitted active types. Each descriptor element has its own active type. A write changes the destination element's active type to the write's `descriptorType`; a copy transfers an active type under the mutable-copy rules. At consumption time, the shader's descriptor type must match that active type or the descriptor is undefined ([mutable descriptors](../../../../vulkan-docs/src/chapters/descriptors.adoc#L593-L637), [mutable writes](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3204-L3207), [mutable copies](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3927-L3946)).

Why it matters here:

- The source gives each mutable binding one ordered type list and rotates through it across iterations. A new shader, resource set, and descriptor update make the selected active types observable on every iteration.
- Pool type lists describe what mutable descriptors the pool can allocate. The layout's list must be a subset of a pool entry's list unless the pool entry omits a list, in which case it can allocate any supported mutable type ([mutable pool rules](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2249-L2280)).

The `mutableDescriptorType` feature guarantees support for any combination of sampled image, storage image, uniform texel buffer, storage texel buffer, uniform buffer, and storage buffer types. The implementation may support more types, and the test asks `vkGetDescriptorSetLayoutSupport` about each selected layout before execution ([mutable descriptor feature](../../../../vulkan-docs/src/chapters/features.adoc#L5552-L5605)).

### Aliased declarations, validity, and descriptor indexing

An array binding can hold elements with different active types during one iteration. The generator then emits several typed GLSL arrays at the same set and binding, but reads only the array element whose active type matches each declaration. Vulkan associates shader resource variables with descriptor-set and binding decorations; arrays keep one binding value ([resource binding assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1575-L1611)). Multiple resource variables may share those decorations. Variables with unsupported declared types cannot be statically used, and accesses that alias need the relevant SPIR-V aliasing treatment ([shared set and binding declarations](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1694-L1715)).

The source marks aliased bindings `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT`. That flag requires validity only for dynamically used elements. Runtime-sized arrays use `VK_DESCRIPTOR_BINDING_VARIABLE_DESCRIPTOR_COUNT_BIT`, and set allocation supplies the actual count ([binding flags](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L775-L814), [descriptor population](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2581-L2589)).

### Update-after-bind and shader-visible validity

`VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT` permits an application to update a supported descriptor class after it binds the set. The pool, layout, and binding flags must agree, and the device needs the class-specific feature ([layout and pool contract](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L363-L375), [per-type features](../../../../vulkan-docs/src/chapters/features.adoc#L2078-L2121)). The `maxUpdateAfterBindDescriptorsInAllPools` property bounds the descriptors allocated across all pools with the update-after-bind flag ([descriptor indexing property](../../../../vulkan-docs/src/chapters/limits.adoc#L2523-L2531)). This permission does not relax descriptor type matching. A consumed mutable descriptor remains valid only when its active type matches the consuming shader type ([descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4596-L4619)).

## One Concrete Example

Consider the registered case:

```text
dEQP-VK.binding_model.mutable_descriptor.one_array.constant_size.aliasing.update_write.no_source.no_source.pool_same_types.update_after_bind.index_constant.comp
```

It creates one six-element mutable array. The allowed list contains the six mandatory types in this order: sampled image, storage image, uniform texel buffer, storage texel buffer, uniform buffer, and storage buffer. Each array element starts from a rotated copy of that list. On iteration 0, element 0 is a sampled image, element 1 is a storage image, and the remaining elements follow the other four types. On later iterations, every element advances to the next type in its own rotation ([mandatory list](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L193-L211), [aliased array construction](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4123-L4164)).

For iteration 0, the generator emits six typed arrays at `set=0, binding=0`. It reads index 0 through the sampled-image declaration, index 1 through the storage-image declaration, and so on. The host binds the descriptor set before writing those six descriptors because the case selects `update_after_bind`. A `1 x 1 x 1` compute dispatch then checks the resource values. The shader changes result element 0 from `0` to `1` with `atomicCompSwap`, and adds one only if all reads match, so success leaves `2` ([shader generation](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2384-L2640), [bind and update ordering](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3632-L3667)).

## End-to-End Test Flow

```text
[host] select one registered family, binding layout, update path, pool strategy, update moment, array access form, and shader stage
[host] reject cases whose extensions, features, shader stages, dynamic indexing, descriptor indexing, or descriptor-set layout are unsupported
[host] derive the iteration count from the longest mutable type list
[host] create a mutable destination layout and pool, plus an optional mutable or non-mutable source set for copy cases
[host] create deterministic resources for the active type of every descriptor element in the current iteration
[host] generate one type-specific shader and pipeline for that iteration
[host] write the destination directly, or write a source set and copy it to the destination
[host] order update before bind for pre_update, or bind before update for update_after_bind
[host] dispatch, draw, or trace one unit of work
[device] let one invocation read every selected descriptor, record type-specific writeback for writable resources, and set its result element to 2 only when all checks pass
[host] wait, read the result element, then read back each writable storage resource
[host] pass only if every iteration reports 2 and every storage write contains the expected mask
```

The sequence repeats for every active-type iteration. Copy cases rebuild the source layout and set because a mutable destination can receive a mutable source, while a compatible non-mutable source fixes the iteration's active type ([source conversion](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1575-L1588), [iteration loop](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3425-L3748)).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `MutableTypesTest::initPrograms()` emits one GLSL module named `iteration-N` for each active-type iteration. The selected descriptor types determine the resource declarations and checks ([program generation](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2384-L2640)).
- Compute uses a `1 x 1 x 1` local size. Graphics variants place the checks in vertex, tessellation control, tessellation evaluation, geometry, or fragment stages and add fixed passthrough stages as needed. Ray variants place them in ray generation, intersection, any-hit, closest-hit, miss, or callable stages and add the required ray-generation or miss path ([stage-specific shader construction](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2411-L2735)).
- Ordinary compute and graphics shaders use the CTS baseline SPIR-V 1.0 target. Cases that use a ray-tracing stage or ray query request SPIR-V 1.4 ([build-option selection](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2384-L2394), [baseline target](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052)).
- Array cases generate either fixed-size arrays or runtime-sized arrays. `index_push_constant` adds a zero-valued push constant to each otherwise fixed element index so the access uses dynamic indexing without changing the selected element ([array declaration and index generation](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1134-L1217)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Destination descriptor set at set 0 | yes | yes | read, with storage classes also written | indirectly through resources | Holds the mutable and non-mutable bindings under test. |
| Optional copy source set | yes | no shader access | no | no | Exercises copies from mutable or per-iteration non-mutable bindings, including host-only source layouts. |
| Per-descriptor sampler, image, buffer, buffer view, or acceleration structure | yes | yes through set 0 | read; storage buffer, image, and texel buffer also written | writable resources only | Makes each active descriptor type visible through its real shader operation. |
| Output storage buffer at set 1 binding 0 | yes | yes | atomic read and write | yes | Stores one result uint per active-type iteration. |
| External sampled image | only when a sampler type is present | yes in set 1 | sampled | no | Gives a standalone sampler a fixed image to sample. |
| External sampler | only when a sampled-image type is present | yes in set 1 | used for sampling | no | Gives a standalone sampled image a fixed sampler. |
| Extra acceleration structure | only for non-ray-generation ray stages | yes in set 1 | used by the passthrough ray-generation shader | no | Invokes the selected ray stage so that stage can run its descriptor checks. |
| Push constant `zero` | always configured; used by `index_push_constant` shaders | yes | read when generated | no | Turns constant element indices into dynamically uniform expressions without changing their values. |

Resource construction initializes descriptor contents with `0x5aIIBBDD`, where `II` is the iteration, `BB` the binding, and `DD` the array element. Storage-capable resources must finish with the top-byte mask `0xFF000000` applied ([numeric value scheme](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L142-L173), [resource creation](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L619-L930)).

## What Is Checked

- Every generated shader reads each descriptor through the GLSL type selected for that iteration. Samplers, images, buffers, texel buffers, input attachments, and acceleration structures use separate checks ([declarations and checks](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1134-L1350)).
- The first invocation to claim an iteration's result slot changes it from `0` to `1`. If every type-specific check succeeds, it adds one, so the host requires exactly `2` ([shader result protocol](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2561-L2580), [host result check](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3695-L3708)).
- Storage buffers, storage images, and storage texel buffers write back the read value ORed with `0xFF000000`. The host reads each such resource and requires that exact value ([shader writes](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1269-L1310), [host writeback check](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3710-L3747)).
- Direct-write cases check `VkWriteDescriptorSet` active-type changes. Copy cases check mutable-to-mutable and non-mutable-to-mutable descriptor transfers, with normal or host-only sources. `pre_update` and `update_after_bind` change whether the update happens before or after binding ([variant generation](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3755-L3928)).
- `misc` also checks pool allocation when the mutable pool type-list entry is beyond `mutableDescriptorTypeListCount`; the specification requires such an out-of-range entry to act like an omitted list and support any mutable type ([corner-case construction](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4296-L4342), [pool rule](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2249-L2268)).

## Behavior Parameter Identification

> **Behavior parameter:** top-level test family
>
> **Candidate values:** `single`, `single_nonmutable`, `one_array`, `multiple_arrays`, `multiple_arrays_mixed`, `single_and_array`, `multiple`, `misc`

The test family is the primary behavioral axis because it changes the descriptor-set shape and the relationship between mutable and non-mutable bindings. Update method, source strategy, pool strategy, update moment, access form, stage, and resource type are important secondary dimensions applied inside those shapes.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single` | Single-element active-type selection, descriptor write or copy, type switching, shader access, or selected-stage execution failure. |
| `single_nonmutable` | Mutable or non-mutable source-copy compatibility failure, ordinary fixed-type descriptor update failure, or shader access failure. |
| `one_array` | Mutable array active-type mapping, aliased declaration, descriptor indexing, partially-bound handling, variable-count allocation, or array access failure. |
| `multiple_arrays` | Independent type rotation across several mutable arrays, multi-binding layout, descriptor indexing, or shader access failure. |
| `multiple_arrays_mixed` | Interleaved mutable and non-mutable array layout, update or copy, active-type mapping, or shader access failure. |
| `single_and_array` | Extended mutable type-list handling across scalar and array bindings, aliased array access, or descriptor update and shader access failure. |
| `multiple` | Independent switching across several mutable scalar bindings, mutable and non-mutable interleaving, or multi-binding update and access failure. |
| `misc` | Out-of-range mutable pool type-list interpretation, pool allocation, storage-buffer descriptor update, or compute verification failure. |

## Important Variations and Special Cases

- The mandatory list contains sampled image, storage image, uniform texel buffer, storage texel buffer, uniform buffer, and storage buffer. `single` also covers sampler, combined image sampler, input attachment, and acceleration structure. `single_and_array` adds those non-mandatory legal types to the mandatory list, except input attachments, which the source does not place in arrays.
- `single.switches` constructs every ordered pair of distinct basic types. Two iterations make the same mutable slot change from the first type to the second.
- Aliasing arrays give different elements different active types in one iteration and emit several typed GLSL arrays over one binding. Non-aliasing arrays give every element the same active type for that iteration and need one declaration.
- `unbounded` applies only to the last binding. It uses variable descriptor count allocation. `aliasing` uses partially-bound bindings because each typed declaration reads only the matching elements.
- Direct writes have no source set. Copy variants use a mutable or non-mutable source set and can allocate that source from a normal or host-only pool. The generator removes non-mutable-source cases when an array needs per-element type aliasing because one fixed-type source binding cannot represent the mixed active types.
- Update-after-bind cases bind first and update second. Input attachments exclude that mode, and input-attachment cases run only in fragment shaders.
- `allStages` spans compute, the five graphics stages represented here, and six ray-tracing stages. Array-heavy families use compute only. `single_nonmutable` and `all_mandatory` use compute, vertex, fragment, and ray generation.
- The entire `mutable_descriptor` test family is absent from Vulkan SC registration ([category registration](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L71)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Binding-model attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L71) | Attaches `mutable_descriptor` for Vulkan but not Vulkan SC. |
| Family construction | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3953-L4344) | Creates the eight top-level test families and their descriptor shapes. |
| Mutable and array model | [`BindingInterface`, `SingleBinding`, and `ArrayBinding`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L934-L1530) | Defines type rotation, resources, GLSL declarations, array aliasing, and shader checks. |
| Pool and layout type lists | [`DescriptorSet`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1536-L2075) | Builds mutable pools and layouts, update-after-bind flags, partially-bound flags, and variable-count bindings. |
| Parameter record | [`TestParams`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2077-L2305) | Maps update, source, pool, moment, access, and stage selections to Vulkan flags. |
| Shader generator | [`MutableTypesTest::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2384-L2735) | Emits type-specific iteration shaders and passthrough stages. |
| Support and pruning | [`MutableTypesTest::checkSupport()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2808-L3056) | Applies extension, feature, descriptor-indexing, layout, stage, and dynamic-indexing gates. |
| Runtime and validation | [`MutableTypesInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3236-L3751) | Creates resources, orders update and bind, submits work, and checks result and storage writeback. |
| Variant generator | [`createMutableTestVariants()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3755-L3928) | Expands and prunes the secondary dimensions. |
| Mustpass inventory | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L46192-L60501) | Confirms 14,310 registered leaves across all eight families. |
| Mutable descriptor semantics | [Mutable descriptors](../../../../vulkan-docs/src/chapters/descriptors.adoc#L593-L652) | Defines allowed and active types plus consumption validity. |
| Mutable descriptor feature contract | [Mutable descriptor feature](../../../../vulkan-docs/src/chapters/features.adoc#L5552-L5605) | Defines the mandatory supported type combination and descriptor-indexing interactions. |
| Mutable list and pool rules | [Descriptor set layouts and pools](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L179-L335), [pool lists](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2249-L2280) | Defines list validity, layout association, and pool subset or omitted-list behavior. |
| Update-after-bind property | [`maxUpdateAfterBindDescriptorsInAllPools`](../../../../vulkan-docs/src/chapters/limits.adoc#L2523-L2531) | Bounds descriptors allocated across all update-after-bind pools. |
| Copy and descriptor validity rules | [Mutable descriptor copies](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3927-L4046), [descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4596-L4619) | Defines active-type transfer and matching at consumption. |
| Shader resource interface | [Set and binding assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1575-L1611), [shared declarations](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1694-L1715) | Defines shader-visible descriptor mapping and shared binding declarations. |

## Questions / Risk Points for User Audit

- **Resolved:** The behavior parameter is the top-level family because each value changes the descriptor-set shape. The large variant suffix changes update, allocation, access, or execution details within that shape.
- **Resolved:** `aliasing` refers to several typed shader declarations over one mutable array binding, with different array elements active as different types. It does not mean that the backing Vulkan memory objects alias each other.
- **Resolved:** `misc` still uses the generated compute shader and storage-buffer writeback; its unique target is the pool rule for a mutable type list whose index is out of range.
- **Resolved:** The selected representative shader is `one_array.constant_size.aliasing...comp`, iteration 0. It exposes all six mandatory active types, shader resource aliasing, partially-bound requirements, post-bind update timing, and both device and host checks in one compact case.
- **Resolved:** Ray-query and ray-tracing shaders need SPIR-V 1.4. The representative compute case has no explicit build options and therefore uses the CTS baseline SPIR-V 1.0 target.

## Conversion Notes for Final Wiki Rewrite

- Keep the active-type, aliasing, validity, and update-after-bind prerequisites, but shorten their teaching scaffolding.
- Use the eight top-level test families as `## Behavior Parameters` subsections.
- Preserve the full dimension table because the secondary suffixes explain why the mustpass inventory is large and how one descriptor shape reaches different implementation paths.
- Use the concrete aliased `one_array` compute case for the single representative shader walkthrough. Include iteration 0 only, then explain later type rotations in the variation table.
- Move most class and helper details to `## Source Reference Appendix`.
- Copy the `### Failure Cause Mapping` table byte for byte into `Mutable.md`. Write `### Cause Analysis` from the runtime checks and specification contracts.
