# Understanding Brief: shader_object create test family

## One-Sentence Test Purpose

This test checks whether `vkCreateShadersEXT` handles legal multi-shader batches correctly: identical create infos must produce identical driver binaries whether each shader is created alone or together in one call, per-stage batches must survive the SPIR-V to binary to shader round-trip, and an unusable binary must make the call return `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT` with the documented result-handle contract.

## Background Knowledge

### Shader objects and one-call creation

With `VK_EXT_shader_object`, each programmable stage can be compiled into its own `VkShaderEXT` object and bound independently, instead of being baked into a `VkPipeline` at pipeline creation. `vkCreateShadersEXT` takes an array of `VkShaderCreateInfoEXT` structures and returns one `VkShaderEXT` handle per element. Each structure describes exactly one stage, and `nextStage` records which stages may logically follow that stage when drawing. The spec restricts stage uniqueness and uniform code type only for shaders created with `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT`, so a batch of unlinked same-stage shaders is legal input.

Why it matters here:
- the test always passes `flags = 0`, so it exercises only the unlinked creation path;
- it builds batches of 10 or 50 same-stage or mixed-stage shaders, legal precisely because the linkage rules do not apply.

### Two code types and the binary round-trip

`VkShaderCreateInfoEXT::codeType` selects between `VK_SHADER_CODE_TYPE_SPIRV_EXT` (portable SPIR-V) and `VK_SHADER_CODE_TYPE_BINARY_EXT` (an opaque, implementation-defined binary format specific to the physical device). `vkGetShaderBinaryDataEXT` returns that binary form for an existing shader: a size query with `pData = NULL`, then a data query with a buffer of that size. The spec guarantees that repeated queries of the same shader object return invariant data, and that the retrieved binary can be passed back to `vkCreateShadersEXT` on a compatible physical device to create a functionally equivalent shader. When the provided binary is not usable, the call must return `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT` (current CTS headers alias this name to `VK_INCOMPATIBLE_SHADER_BINARY_EXT`).

Why it matters here:
- the stage groups create shaders from SPIR-V, query their binaries, destroy the shaders, and create the same batch again from the queried binaries;
- the `fail` test case leaves truncate one binary to one byte, which must trigger the required return code.

### The result-array contract on failure

`vkCreateShadersEXT` must overwrite every element of `pShaders` with either `VK_NULL_HANDLE` or a valid handle before returning, whether or not the call succeeds. The first `VK_NULL_HANDLE` element identifies the shader the returned error refers to, and applications clean up by destroying every non-null element. The spec makes no promise about entries after the failing one: the driver may stop there, or it may have already completed later shaders before detecting the failure, so both states must be tolerated.

Why it matters here:
- the `fail` leaves pre-fill the result array with a garbage sentinel handle, then verify that entries before the failing index are real handles, the failing entry is `VK_NULL_HANDLE`, and every entry the driver actually wrote is destroyed.

## One Concrete Example

Reconstructed, simplified walk of the registered case `dEQP-VK.shader_object.create.comp.fail`. The real code is the loop in `ShaderObjectStageInstance::iterate`:

1. The case builds ten `VkShaderCreateInfoEXT` structures with `stage = VK_SHADER_STAGE_COMPUTE_BIT`. Each carries SPIR-V from a different prebuilt binary (`comp0` through `comp9`, each with a distinct index constant compiled into it), and each carries one storage-buffer descriptor set layout because the compute shader declares a buffer.
2. `vkCreateShadersEXT(device, 10, infos, nullptr, shaders)` must return `VK_SUCCESS`.
3. For each shader, the instance queries the binary size, allocates a host vector, queries the binary bytes, and then destroys all ten shaders.
4. All ten create infos are rewritten to `codeType = VK_SHADER_CODE_TYPE_BINARY_EXT` with the queried bytes as `pCode`. One deterministically chosen index (a seeded `de::Random` draw) gets `codeSize = 1` instead.
5. The result array is pre-filled with a garbage handle value and `vkCreateShadersEXT` runs again.
6. The call must return `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`. Entries before the failing index must be valid handles, the failing entry must be `VK_NULL_HANDLE`, and every entry that differs from the garbage value is destroyed.

## End-to-End Test Flow

Both flows are entirely host-side. No command buffers are recorded, nothing is submitted to a queue, and no shader is ever executed.

```text
1. multiple family (ShaderObjectCreateInstance::iterate)
[host] collect SPIR-V binaries for vert, frag, comp, and feature-gated tesc, tese, geom, mesh, task
[host] build one VkShaderCreateInfoEXT per stage (only comp carries a descriptor set layout)
[host] create every shader alone, one vkCreateShadersEXT call per create info
[host] create the same shaders again in a single vkCreateShadersEXT call
[host] for each pair, query binary size and bytes with vkGetShaderBinaryDataEXT
[host] fail if sizes differ or any byte differs between separately and batch created shaders
[host] destroy both sets of shaders

2. stage family (ShaderObjectStageInstance::iterate)
[host] build the stage list supported by the device, plus mesh and task when the case uses them and the features are present
[host] build 10 create infos (fixed stage) or 50 (mixed stage, drawn from a seeded de::Random)
[host] create the batch from SPIR-V; anything other than VK_SUCCESS fails the case
[host] query each shader's binary data (size, then bytes) and destroy the batch
[host] rewrite every create info to VK_SHADER_CODE_TYPE_BINARY_EXT with the queried bytes
[host] fail leaves only: set codeSize to 1 at one deterministic index
[host] pre-fill the result array with a garbage handle and call vkCreateShadersEXT again
[host] fail leaf: require VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT, valid handles before the failing index, VK_NULL_HANDLE at it, destroy everything written
[host] succeed leaf: require VK_SUCCESS and destroy every shader
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- GLSL sources for all eight stages, generated in `initPrograms()` as string streams. The `multiple` family generates one variant per stage. The stage family generates ten variants per stage, with the loop index `i` compiled into a constant so the ten SPIR-V inputs per stage stay distinct. Mesh and task sources are built with `vk::SPIRV_VERSION_1_4` build options.
- The CTS build compiles these sources into SPIR-V program binaries named `vert`, `vert0` through `vert9`, `comp`, `comp0` through `comp9`, and so on. The instance code fetches them from the binary collection.
- Driver-side binary blobs (`std::vector<uint8_t>`), queried at run time from the first batch of created shaders. These are the artifacts that get compared (multiple family) or fed back as `VK_SHADER_CODE_TYPE_BINARY_EXT` code (stage family).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Descriptor set layout (one storage-buffer binding, compute stage) | yes | referenced by `pSetLayouts` for compute entries only | no | no | Exercises the descriptor layout fields of creation. No descriptor pool, descriptor set, or actual buffer is ever created. |
| SPIR-V program binaries | generated by the CTS build | passed as `pCode` | compiled by the driver inside `vkCreateShadersEXT` | no | The creation input. |
| Driver binary blobs | queried via `vkGetShaderBinaryDataEXT` | no | no | yes | Round-trip input and comparison material. |
| Garbage sentinel handle | written into the result array by the test | no | no | compared on host | Detects which result slots the driver actually wrote. |

No storage buffers, images, framebuffers, samplers, push constants, or command buffers are involved. The compute shader's `buffer_out` declaration exists only so the descriptor set layout has something to match.

## What Is Checked

- `multiple` (leaves `all`, `all_with_mesh`): for every shader in the set, the binary data of the separately created shader and the batch created shader must have equal size and equal bytes. This comparison is the only pass/fail signal; the return codes of the creation calls themselves are not checked.
- Stage groups, `succeed` leaf: the first batch creation from SPIR-V must return `VK_SUCCESS`, and the second creation from the queried binaries must also return `VK_SUCCESS`.
- Stage groups, `fail` leaf: the second creation must return `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`, entries before the failing index must be valid handles, the failing entry must be `VK_NULL_HANDLE`, and every written entry must be destroyable.
- All checks are host-side comparisons of return codes and handle values. There is no device-side output to inspect.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node under the `create` test family (the creation scenario), with the test case leaf (`succeed` / `fail`) as a second axis for the stage groups.
>
> **Candidate values:** `multiple` (leaves `all`, `all_with_mesh`), single-stage stage groups `vert`, `tesc`, `tese`, `geom`, `frag`, `comp`, `mesh`, `task` (leaves `succeed`, `fail`), and mixed-stage stage groups `all`, `all_with_mesh` (leaves `succeed`, `fail`).

## What Failure Means

### Failure Cause Mapping

Creation scenario axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `multiple` (leaves `all`, `all_with_mesh`) | Separate and batched creation compile the same input differently, or creation leaves unusable handles that break the binary queries. |
| Single-stage stage groups (`vert`, `tesc`, `tese`, `geom`, `frag`, `comp`, `mesh`, `task`) | The driver rejects a legal same-stage batch, or the per-stage binary query and round-trip fails. |
| Mixed-stage stage groups (`all`, `all_with_mesh`) | The driver mishandles a mixed-stage batch, or the binary query and round-trip fails. |

Expected outcome axis (leaves of every stage group):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `succeed` | The first call rejects valid SPIR-V batches, or the queried binaries cannot recreate the shaders. |
| `fail` | The driver does not return `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT` for an unusable binary, or it violates the result-array overwrite contract. |

## Important Variations and Special Cases

- `multiple.all_with_mesh` requires only `VK_EXT_shader_object` in `checkSupport`. Mesh and task create infos are appended only when the mesh and task feature bits are reported, so on mesh-less devices the case degrades to the base stage set instead of being skipped. The stage-family `mesh`, `task`, and `all_with_mesh` cases, in contrast, require `VK_EXT_mesh_shader` outright.
- The stage-family `all` and `all_with_mesh` cases choose a random stage per entry from the supported list with a fixed seed (`de::Random(102030)`), and use 50 entries instead of 10. The stage mix is deterministic across runs.
- The failing index in `fail` leaves is drawn from the same seeded generator, so the injected one-byte binary lands at a stable index for each case.
- Entries after the failing index are deliberately not checked: the source comment notes the driver may have completed later shaders before detecting the error. Both early-stop and full-write behaviors are accepted, and everything written is destroyed.
- The compute stage is the only stage that carries a descriptor set layout, matching the compute shader's buffer declaration. All other stages pass no layouts.
- The `multiple` family sets `nextStage = 0` for mesh and task create infos, while the stage family passes mesh to fragment and task to mesh through `getShaderObjectNextStages`. Both are legal: `nextStage` zero means the stage must be the last one.
- The generated GLSL contains a quirk: the compute shaders declare `layout(local_size_x=16, local_size_x=1, local_size_x=1)`, repeating `local_size_x` instead of using `local_size_y` and `local_size_z`. Because no shader is ever executed, this has no effect on the result; it is further evidence that shader content is incidental here.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Separate versus batch creation and binary comparison | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L64-L313) | Core flow of the `multiple` intermediate node. |
| Binary size and byte comparison loop | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L269-L302) | The pass/fail condition of the `multiple` family. |
| Stage batch creation, round-trip, and failure checks | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L481-L662) | Core flow of every stage group. |
| First creation result check | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L555-L562) | The `VK_SUCCESS` requirement for the SPIR-V batch. |
| Failure injection and result-array contract checks | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L576-L648) | The `fail` leaf mechanism, including the tolerated trailing entries. |
| Stage feature gates | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L692-L707) | Requirement-based pruning per stage. |
| Ten-variant shader generation | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L709-L825) | Distinct SPIR-V inputs per stage batch. |
| Registration of the create family | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L829-L879) | The `multiple` node and all stage groups. |
| nextStage mapping | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L58-L94) | `nextStage` values follow the spec's legal stage chains. |
| Stage to binary-name mapping | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L31-L56) | How the stage family picks program binaries. |
| Parent registration | [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) | Attaches `create` under the `shader_object` test category. |
| Mustpass evidence | [create.txt](../../../mustpass/main/vk-default/shader-object/create.txt) | All 22 registered leaves of the family. |

## Questions / Risk Points for User Audit

- The `multiple` family requires byte-identical binaries from separately and batch created shaders. The spec guarantees invariance only for repeated queries of the same shader object, and its identical-binary wording appears in the descriptor heap mapping context. Is the byte-identity expectation intended as a stronger CTS determinism demand, and should the page present it that way?
- The test compares against `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`, which current headers alias to `VK_INCOMPATIBLE_SHADER_BINARY_EXT` (a positive code in the current registry). The page should name the constant the way the test does and note the alias once. Is that acceptable?
- `multiple` does not check the return codes of its two creation calls. A driver-side creation failure would surface only through the binary queries. Worth stating in the page, not fixing in the test.
- Walkthrough decision: no shader is ever executed and shader content is incidental (the never-run compute shaders even carry a duplicate `local_size_x` declaration). I intend to record a no-walkthrough exception for this page. Confirm.
- The stage family tolerates any state for result entries after the failing index. The page will present this as designed tolerance, not as an oversight.

## Conversion Notes for Final Wiki Rewrite

- Distill Background Knowledge into three page-local prerequisite bullets: one-call creation of unlinked shader objects, the two code types and the binary round-trip, and the result-array overwrite contract. No Level-2 page exists yet, so the section stays self-contained.
- The concrete example becomes the prose flow in `## Runtime Execution and Result Checking`; do not carry the numbered list verbatim.
- Copy the two Failure Cause Mapping tables into the page's `### Failure Cause Mapping` unchanged; write `### Cause Analysis` fresh with four causes matching the mapping.
- Record the no-walkthrough justification in `## Shader Analysis` and add `CreateTests.md` under `shader_object` in the walkthrough exception registry.
- The resource table shrinks to a short paragraph: one descriptor set layout, program binaries, and driver-queried blobs; no real GPU resources are bound.
- Keep the registered-name collision visible: `shader_object.create.all.succeed` (stage group leaf) versus `shader_object.create.multiple.all` (leaf of the `multiple` node).
