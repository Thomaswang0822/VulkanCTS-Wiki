# Understanding Brief: `binding_model.descriptorset_random`

## One-Sentence Test Purpose

This test checks whether randomly generated multi-set descriptor layouts, descriptor updates, and shader accesses keep the value assigned to each descriptor across several indexing modes and shader stages.

## Background Knowledge

### Descriptor set layouts and pipeline layouts

A descriptor set layout assigns a type, count, and visible shader stages to each binding. A pipeline layout combines an ordered sequence of those set layouts, so each shader declaration at a `set` and `binding` pair has a matching host-side resource interface. The Vulkan specification defines these roles in [Descriptor Set Layout](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L17-L27) and [Pipeline Layouts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1168-L1182).

Why it matters here:

- A generated shader fetches the intended value only when its declarations match the generated layouts and pipeline layout.
- Empty bindings, arrays, several descriptor types, and up to 32 sets make that mapping less regular than a hand-written layout.

### Descriptor indexing flags

Descriptor indexing adds controls such as update-after-bind and variable descriptor counts. An update-after-bind binding uses a descriptor written after command-buffer binding and before submission. A variable-count binding uses the layout count as an upper bound, while allocation chooses its available count. See [descriptor binding flag semantics](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L753-L816).

Why it matters here:

- The generator can place `VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT` on eligible bindings and split updates around `vkCmdBindDescriptorSets`.
- It can make the last eligible binding variable-sized. The shader generator does not access elements outside the allocated count.

## One Concrete Example

Use this executable leaf as the representative:

```text
dEQP-VK.binding_model.descriptorset_random.sets4.dynindexed.ubolimitlow.nosbo.nosampledimg.outimgonly.noiub.uab.comp.noia.0
```

The registration loop assigns this leaf internal seed `7512`; the final path component `0` is the leaf name within that parameter combination. The CTS `deRandom` replay produces 7, 18, 16, and 29 binding slots for sets 0 through 3. Most receive a zero descriptor count. The nonzero layout is:

| Set and binding | Descriptor | Count | Shader role |
|-----------------|------------|------:|-------------|
| set 0, binding 0 | `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE` | 1 | Fixed 8 by 8 result image. |
| set 1, binding 0 | `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` | 6 | UBO array containing descriptor numbers 1 through 6. |
| set 2, binding 10 | `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` | 1 | UBO array containing descriptor number 7. |
| set 3, binding 0 | `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` | 5 | UBO array containing descriptor numbers 8 through 12. |

The shader uses indexes such as `ubo1_0[accum + 1]`. A correct read leaves `accum` equal to zero. A wrong value changes `accum`, affects later dependent indexes, and makes the invocation write a zero result instead of one. The `uab` component makes eligible bindings candidates for update-after-bind; it does not require every generated binding to receive that flag.

## End-to-End Test Flow

```text
[host] select one registered parameter combination and assign its deterministic internal seed
[host] replay the seed to generate descriptor-set layouts, array sizes, variable-count choices, and GLSL checks
[host] create layouts, pools, sets, the pipeline layout, stage-specific pipeline, descriptor resources, and result image
[host] initialize readable descriptors with their global descriptor numbers and shader-write targets with -1
[host] update ordinary bindings, bind each descriptor set, then update bindings selected for update-after-bind
[host] clear the result image, issue the stage-specific dispatch, draw, mesh launch, or ray trace, and submit
[device] read or write selected descriptors and record one result texel for each of 64 logical invocations
[host] wait, copy image results and writable image data to host-visible buffers, and invalidate mapped memory
[host] require all 64 result texels to equal 1 and every generated shader write to contain its expected descriptor number
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `generateRandomLayout` builds a deterministic `RandomLayout` from the internal seed, set count, per-type limits, indexing mode, and stage.
- `initPrograms` emits resource declarations and read or write checks for the descriptors selected by `CheckDecider`. It selects at least the first three and last array elements, plus a bounded random sample in larger arrays.
- The selected stage chooses the surrounding shader and execution path. The descriptor check expression uses the same global descriptor-number contract.
- The current `vk-default` mustpass list has 35,148 leaves: 14,106 under `sets4`, and 7,014 each under `sets8`, `sets16`, and `sets32`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Descriptor sets and pipeline layout | yes | yes | used for access | no | Connect generated shader declarations to resources across 4, 8, 16, or 32 sets. |
| Shared descriptor-data buffer | yes | yes | read and sometimes written | write targets only | Supplies one integer equal to each descriptor's global number. |
| Storage and input-attachment images | yes | yes | read or written | writable storage images | Cover image descriptors with the same descriptor-number contract. |
| Output storage image | yes | yes | written | yes | Holds 64 pass or fail texels. |
| Push constants | for `unifindexed` | yes | read | no | Supply identity array indexes for that indexing mode. |
| Acceleration structures and shader binding tables | for ray-tracing stages | yes | used to invoke the selected stage | no | Route execution through ray-generation, hit, miss, intersection, or callable shaders. |

## What Is Checked

- Each generated read compares the fetched integer with that descriptor's global number and ORs any difference into `accum`.
- Each logical invocation writes 1 to its result texel only when all reads selected for that shader returned expected values.
- The host scans all 64 copied result values and counts every value other than 1 as a failure.
- For descriptors selected as shader-write targets, one invocation writes the descriptor number. The host compares the copied or mapped value with that number.
- The case passes when the combined failure count is zero.

## Behavior Parameter Identification

> **Behavior parameter:** descriptor indexing mode (the first intermediate node below each `sets*` node)
>
> **Candidate values:** `noarray`, `constant`, `unifindexed`, `dynindexed`, `runtimesize`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `noarray` | Scalar descriptor layout, update, or binding mismatch. |
| `constant` | Constant-index descriptor-array access failure. |
| `unifindexed` | Push-constant-driven descriptor-array access failure. |
| `dynindexed` | Dependent dynamically uniform descriptor-array access failure. |
| `runtimesize` | Runtime-sized or variable-count descriptor-array failure. |

A failure in any value can also come from the shared descriptor-resource setup, execution, synchronization, or readback path.

## Important Variations and Special Cases

- `sets4`, `sets8`, `sets16`, and `sets32` change pipeline-layout width. Low-limit `sets4` combinations get 10 generated seeds; other combinations get one.
- `comp`, `frag`, and `vert` are present in Vulkan and Vulkan SC. Vulkan adds NV or KHR ray-tracing stages plus task and mesh stages.
- The generator places input attachments under `frag`. Ray-tracing paths add an acceleration structure at set 0, binding 1.
- `uab` makes each eligible binding a random update-after-bind candidate. The code applies matching layout and pool flags and writes selected descriptors after binding.
- `runtimesize` emits unsized descriptor arrays. When variable descriptor counts are unsupported, the test allocates the full declared count.
- Random writable storage descriptors add a second check: the shader must store the descriptor number and the host must observe it.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Support checks | [`DescriptorSetRandomTestCase::checkSupport`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L347-L477) | Gates stages, indexing modes, descriptor limits, inline uniform blocks, set count, and runtime arrays. |
| Random layout generation | [`generateRandomLayout`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L512-L788) | Chooses binding counts, types, arrays, write targets, and variable descriptor counts. |
| Shader generation | [`DescriptorSetRandomTestCase::initPrograms`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L832-L1449) | Emits declarations, indexing expressions, checks, and stage-specific GLSL with a SPIR-V 1.4 target. |
| Runtime setup and descriptor updates | [`DescriptorSetRandomTestInstance::iterate`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L1472-L2492) | Creates resources, writes descriptor data, updates and binds descriptor sets, and handles update-after-bind. |
| Execution and host checks | [command recording and verification](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L2946-L3145) | Executes the selected stage, copies results, and computes the final failure count. |
| Registration matrix | [`createDescriptorSetRandomTests`](../../../modules/vulkan/binding_model/vktBindingDescriptorSetRandomTests.cpp#L3150-L3435) | Defines exact registered values, pruning, leaf names, and internal seed order. |
| Representative leaf | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L28091) | Confirms the exact executable path used for the walkthrough. |
| Descriptor layout contract | [Descriptor Set Layout](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L17-L27) | Defines the type, count, and stage interface of each binding. |
| Indexing flag contract | [`VkDescriptorBindingFlagBits`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L753-L816) | Defines update-after-bind and variable descriptor count behavior. |

## Questions / Risk Points for User Audit

- The behavioral axis is the registered descriptor indexing mode because it changes declaration shape and each generated access expression. Set count controls scale.
- The representative path is present in mustpass, and deterministic replay resolves internal seed `7512` to the documented layout and shader.
- The artifact and resource sections separate generated program text from host-created GPU resources.
- No unresolved source question changes the walkthrough, validation rule, or failure mapping.

## Conversion Notes for Final Wiki Rewrite

- Keep descriptor layout, pipeline layout, update-after-bind, and variable descriptor count as short prerequisites.
- Use the seed-7512 compute shader as the single representative walkthrough and include compiler-produced SPIR-V 1.4.
- Carry the descriptor indexing mode into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table unchanged.
- Keep the complete parameter inventory and mustpass counts, but move source-navigation detail to the appendix.
