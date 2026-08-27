## Overview

**Core question:** When `vkCreateShadersEXT` processes legal batches of `VK_EXT_shader_object` shader objects, does it return the required result codes, satisfy the tested portions of the result-handle contract, and produce byte-identical driver binaries for identical inputs regardless of batching?

- [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L1) implements the whole `shader_object.create` test family: the `multiple` intermediate node and ten stage groups, 22 test case leaves in the main mustpass set.
- Registered paths: `shader_object.create.multiple.all` and `shader_object.create.multiple.all_with_mesh`, plus `shader_object.create.<stage>.succeed` and `shader_object.create.<stage>.fail` for `vert`, `tesc`, `tese`, `geom`, `frag`, `comp`, `mesh`, `task`, `all`, and `all_with_mesh`.
- The family runs two validation mechanisms. The `multiple` node creates the same set of shaders twice, once one call per shader and once in a single call, then compares the driver binaries byte for byte. Each stage group creates a batch from SPIR-V, queries the driver binaries, destroys the batch, and creates it again from those binaries; the `fail` leaves truncate one binary to one byte to exercise the documented incompatible-binary path.
- No shader is ever executed. Pass and fail come from return codes, handle values, and binary-data comparisons, all host-side.

## Background Knowledge

For the shared concepts shader objects, linked creation, and shader binaries, see [Background Knowledge](../../categories/shader_object.md#background-knowledge) of the `shader_object` page.

- **The result-array contract on an incompatible binary.** Before `vkCreateShadersEXT` returns, every element of `pShaders` must be overwritten with either `VK_NULL_HANDLE` or a valid handle, whether or not the call succeeds. The first `VK_NULL_HANDLE` identifies the shader the returned status refers to, and cleanup is done by destroying every non-null element. For an unusable binary, the current specification names the required status `VK_INCOMPATIBLE_SHADER_BINARY_EXT`; the CTS source compares its deprecated alias `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`, which has the same value.

## Registration Hierarchy

```text
shader_object.create
├── multiple
├── vert
├── tesc
├── tese
├── geom
├── frag
├── comp
├── mesh
├── task
├── all
└── all_with_mesh
```

Each stage group holds two test case leaves, `succeed` and `fail`, registered from the `failTests` table [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L858-L865). The `multiple` node holds the leaves `all` and `all_with_mesh` [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L833-L838). All 22 leaves appear in the mustpass set [create.txt](../../../mustpass/main/vk-default/shader-object/create.txt); the source mustpass entry is the wildcard `dEQP-VK.*` [main.txt](../../../mustpass/main/src/main.txt), and the only `shader_object` exclusion covers `performance`, not `create` [excluded-tests.txt](../../../mustpass/main/src/excluded-tests.txt). Note the name collision: `shader_object.create.all.succeed` is a stage-group leaf, while `shader_object.create.multiple.all` is a leaf of the `multiple` node.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Creation scenario | `multiple`, `vert`, `tesc`, `tese`, `geom`, `frag`, `comp`, `mesh`, `task`, `all`, `all_with_mesh` | Selects which creation mechanism runs: separate-versus-batch comparison for `multiple`, a same-stage batch for the eight single stages, a random mixed-stage batch for `all` and `all_with_mesh`. | [stageTests table](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L840-L856) |
| Expected outcome | `succeed`, `fail` | The test case leaf of every stage group: `succeed` requires both creation calls to return `VK_SUCCESS`; `fail` requires the second call to return `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT` and validates the result-array prefix through the failing slot. | [failTests table](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L858-L865) |
| Mesh-shader usage | off, on | Cases named `all_with_mesh`, plus the `mesh` and `task` stage groups, also create mesh and task shaders when the device reports the features. | [mesh/task appends](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L215-L258) |
| Batch size (source constant) | 10 for a fixed stage, 50 for `all` and `all_with_mesh` | How many shaders one `vkCreateShadersEXT` call creates in the stage groups. Not part of the registered path names. | [count selection](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L516) |
| Shader program entries (source constant) | 10 per stage | The six non-mesh stages compile the loop index into ten distinct SPIR-V inputs. The mesh and task loops create ten differently named program entries from identical source, so those same-stage batches repeat one input. Not registered. | [ten-entry loop](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L709-L825) |

## Behavior Parameters

The primary behavioral axis is the **creation scenario**, the intermediate node under the `create` test family. A second axis, the **expected outcome** leaf, applies inside every stage group.

### multiple: separate versus batch creation equivalence

The `multiple` node asks one question: does a shader compile the same way when it is created alone as when it is created together with the rest of the set? The test instance builds one create info per supported stage, creates every shader in its own `vkCreateShadersEXT` call, creates the whole set in one call, then compares the `vkGetShaderBinaryDataEXT` output of each pair, size first and bytes second [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L260-L302). This node never injects a failure and never checks creation return codes; the byte comparison is its only pass/fail signal.

### Single-stage stage groups: same-stage batches

The eight groups `vert`, `tesc`, `tese`, `geom`, `frag`, `comp`, `mesh`, and `task` each create ten same-stage shaders in one call, query their binaries, destroy them, and create the batch again from the queried binaries [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L481-L662). Each group repeats the same mechanism with a different stage, so the per-stage differences are the feature gates and the `nextStage` values:

| Stage | Feature gate | `nextStage` used |
|-------|--------------|------------------|
| `vert` | none | fragment, plus tessellation control and geometry when supported |
| `tesc` | `tessellationShader` | tessellation evaluation |
| `tese` | `tessellationShader` | fragment, plus geometry when supported |
| `geom` | `geometryShader` | fragment |
| `frag` | none | 0 |
| `comp` | none | 0, and the only stage carrying a descriptor set layout |
| `mesh` | `VK_EXT_mesh_shader` with `meshShader` | fragment in the stage groups; 0 in the `multiple` node |
| `task` | `VK_EXT_mesh_shader` with `taskShader` | mesh in the stage groups; 0 in the `multiple` node |

The `nextStage` values come from `getShaderObjectNextStages` and mirror the spec's legal stage chains [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L58-L94). A `nextStage` of zero means the stage must be the last one, so the mesh and task difference between the two mechanisms is a legal variation, not a contradiction.

### Mixed-stage stage groups: random stage mixes

The `all` and `all_with_mesh` groups run the same stage mechanism with 50 create infos instead of 10, choosing a stage per entry from the feature-supported list with a seeded `de::Random` generator [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L516-L553). The mix is deterministic across runs. `all` never includes mesh or task; `all_with_mesh` includes them when the features are reported. These groups exercise one `vkCreateShadersEXT` call containing many shaders of several different stages.

### succeed: both creation calls must succeed

The `succeed` leaf checks the whole round-trip. The first call creates 10 or 50 shaders from SPIR-V and must return `VK_SUCCESS` [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L555-L562). The test instance then queries each shader's binary data and destroys the batch. The second call, now with `codeType = VK_SHADER_CODE_TYPE_BINARY_EXT` and the queried bytes as `pCode`, must also return `VK_SUCCESS`. Any other result from either call fails the case immediately.

### fail: unusable binary must fail with the documented contract

The `fail` leaf performs the same round-trip but rewrites one create info at a deterministically chosen index to `codeSize = 1`, a one-byte binary [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L576-L590). The second call must return `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`. The result array was pre-filled with a garbage sentinel handle, so the test can tell which slots the driver actually wrote: entries before the failing index must be valid handles, the failing entry must be `VK_NULL_HANDLE`, and every entry that is no longer garbage is destroyed [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L592-L648). The test does not validate entries after the failing index: it accepts an untouched sentinel as well as `VK_NULL_HANDLE` or a valid handle. This is looser than the specification's all-elements overwrite rule; an implementation may stop compiling at the failure or complete later shaders first, but it must still overwrite every trailing result slot with null or a valid handle.

## Shader Analysis

This page has no representative shader walkthrough. The family creates shader objects but never binds, dispatches, or draws with them, and no validation reads any shader output. The GLSL sources are minimal per-stage boilerplate; the six non-mesh stages embed a variant index, while the ten mesh and task program entries repeat identical source [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L709-L825). Mesh and task sources build with SPIR-V 1.4 options [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L815-L823). The tested behavior is `vkCreateShadersEXT` legality, binary round-trip, and result-array handling, so a shader walkthrough would not clarify the test. The compute shaders even declare `layout(local_size_x=16, local_size_x=1, local_size_x=1)`, a repeated `local_size_x`, which is harmless because the shader never runs. Because shader code is incidental here, this page is recorded as a no-walkthrough exception for the `shader_object` category.

## Runtime Execution and Result Checking

- **No device work.** Everything happens in host API calls: creation, binary queries, comparisons, destruction. No command buffers, queues, draws, dispatches, or readback buffers are involved.
- **Stage set assembly.** Both mechanisms build their stage list from device features: vert, frag, and comp always; tesc, tese, and geom when the corresponding core features are present; mesh and task for mesh cases when the feature bits are reported [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L493-L514).
- **Deterministic randomness.** The stage mix for `all` and `all_with_mesh`, and the failing index for every `fail` leaf, come from `de::Random(102030)`, so both are stable across runs [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L493-L516).
- **Binary query pattern.** Every `vkGetShaderBinaryDataEXT` use follows the spec's two-step shape: query with `pData = NULL` for the size, then query again with a buffer of that size [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L269-L302) and [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L564-L571).
- **Cleanup.** Both mechanisms destroy their shaders on the successful path. In a `fail` leaf that receives the expected incompatible-binary status and passes its handle checks, cleanup visits every result entry that differs from the garbage sentinel, including entries after the failing index [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L641-L647).
- **Pass/fail.** The `multiple` node passes when all binary pairs match in size and bytes. The stage groups pass when both creation calls return the required codes, and the `fail` leaves additionally require valid handles before the failing index and `VK_NULL_HANDLE` at that index. They do not enforce the overwrite contract on trailing slots.

## Failure Meaning

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

### Cause Analysis

#### Separate and batched creation diverge

**Possible failure symptoms:** The `multiple` node logs a size mismatch ("Data size of shader created separately is X, but data size of shader created in the same call with others is Y") or a byte mismatch at a specific index, and the case fails. Because the node does not check creation return codes, a creation failure would also surface here, as a binary query on an unusable handle.

**Possible implementation causes:** The driver compiles the same create info differently depending on whether it was alone or part of a batch, for example through batch-level optimization passes, per-call caches keyed on the whole batch, or state carried between create infos within one call. The spec guarantees binary invariance only for repeated queries of the same shader object, so this test imposes a stricter byte-identity demand than that minimum: same input, same binary, regardless of batching. A mismatch demonstrates batch-dependent or otherwise varying binary generation under the CTS expectation; it does not by itself violate the specification's same-object query-invariance guarantee.

#### Legal batch creation fails

**Possible failure symptoms:** A stage group's first call returns anything other than `VK_SUCCESS`, logged as "vkCreateShadersEXT returned <result>", and the case fails immediately.

**Possible implementation causes:** The driver rejects a batch containing multiple same-stage shaders, mishandles `createInfoCount` greater than one, or mishandles the compute entries that carry a descriptor set layout. Creating ten unlinked same-stage shaders in one call is legal spec input, because the stage-uniqueness rule applies only to shaders created with `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT`, which this test never sets. A stage-specific failure, for example only `mesh` or `task` batches failing, would point at that stage's handling or feature gating.

#### Binary query or round-trip fails

**Possible failure symptoms:** A `succeed` leaf passes the first call but the second call, which feeds the queried bytes back with `VK_SHADER_CODE_TYPE_BINARY_EXT`, returns something other than `VK_SUCCESS`, and the case fails.

**Possible implementation causes:** The data returned by `vkGetShaderBinaryDataEXT` cannot recreate the shader it came from. The spec requires the binary of a shader to be usable to create a functionally equivalent shader on a compatible device, and requires repeated queries of the same object to be invariant. A driver that returns inconsistent data between its size query and its data query, or that embeds data its own creation path rejects, fails here. Because the test runs on the same device that produced the binaries, incompatibility across devices is not in scope for this failure.

#### Required incompatible-binary status or checked handle contract violated

**Possible failure symptoms:** A `fail` leaf reports one of three contract violations: the second call returned something other than `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT` for the one-byte binary; the entry at the failing index is not `VK_NULL_HANDLE` (either never written, still garbage, or unexpectedly created); or an entry before the failing index is garbage or `VK_NULL_HANDLE`, meaning the driver failed an earlier valid shader or skipped writing a slot.

**Possible implementation causes:** The driver accepts a one-byte binary as usable, or returns a different status instead of the incompatible-binary status required by the binary compatibility rules. Or it fails to write a valid handle before the failing index or `VK_NULL_HANDLE` at that index. Entries after the failing index are not checked by design: the source permits the garbage sentinel to remain there even though the specification requires every slot to be overwritten with null or a valid handle. Therefore this case cannot detect a trailing-only overwrite violation.

## Case Pruning

### Requirement-based pruning

- Every case in the family requires the `VK_EXT_shader_object` extension [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L338-L341) and [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L692-L694).
- `tesc` and `tese` groups require the `tessellationShader` core feature, and `geom` requires `geometryShader`; without the feature the group is not run [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L698-L702).
- The `mesh`, `task`, and `all_with_mesh` stage groups require `VK_EXT_mesh_shader`, and the `mesh` and `task` groups throw `NotSupportedError` when the `meshShader` or `taskShader` feature bit is absent [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L695-L706).
- Within a run, stages are dropped from the batch itself when features are absent: the `multiple` node and the mixed `all` groups build a smaller stage list instead of failing [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L156-L213) and [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L499-L514). `multiple.all_with_mesh` therefore still runs without `VK_EXT_mesh_shader`, with mesh and task omitted. The stage-group `all_with_mesh` leaves also omit either unsupported mesh stage, but unlike the `multiple` leaf they require the extension to be present.

### Design-based pruning

- No draws or dispatches exist anywhere in the family: creation is the whole test, and validation reads return codes, handles, and binary bytes only.
- The `multiple` node never injects a failure and never checks return codes, because its subject is binary equivalence between the two creation paths.
- The stage groups create only unlinked shaders (`flags = 0`), leaving linked creation to the `link` test family.
- Only compute entries carry a descriptor set layout, matching the compute shader's buffer declaration; all other stages pass no layouts [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L148-L149) and [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L533-L548).
- Ten indexed variants keep same-stage batches for vert, tesc, tese, geom, frag, and comp from being ten copies of one input. Mesh and task intentionally use ten copies of identical source, while the 50-entry mixed batches exercise one call covering many stages at once [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L525-L535) and [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L709-L825).

## Key Takeaways

- The `create` test family validates `vkCreateShadersEXT` mechanics: batch creation, the SPIR-V to binary to shader round-trip, failure reporting, and the result-array contract. Shader execution is never part of the check.
- The `multiple` node's byte-identity comparison between separately and batch-created shaders is stricter than the spec's minimum, which only promises per-object query invariance. A failure there establishes batch-dependent or otherwise varying binary generation under the CTS expectation, not by itself a violation of that specification guarantee.
- The `fail` leaves pin two things at once: the exact required return status for an unusable binary, and the result values through the failing slot. Trailing entries are deliberately left unchecked even though the specification's overwrite contract still applies to them.
- Stage coverage scales with device features, so the same registered case exercises a different number of stages on different hardware, and `multiple.all_with_mesh` degrades gracefully rather than being skipped.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `ShaderObjectCreateInstance::iterate`, separate versus batch creation | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L64-L313) | Core flow of the `multiple` intermediate node. |
| Binary size and byte comparison loop | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L269-L302) | The pass/fail condition of the `multiple` node. |
| `ShaderObjectStageInstance::iterate` | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L481-L662) | Core flow of every stage group: batch creation, round-trip, failure injection. |
| First creation result check | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L555-L562) | The `VK_SUCCESS` requirement for the SPIR-V batch. |
| Failure injection and result-array checks | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L576-L648) | The `fail` leaf mechanism, including the tolerated trailing entries. |
| Stage feature gates, `checkSupport` | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L692-L707) | Requirement-based pruning per stage. |
| Ten-variant shader generation, `initPrograms` | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L709-L825) | Distinct SPIR-V inputs per stage batch, including the SPIR-V 1.4 mesh and task builds. |
| Registration, `createShaderObjectCreateTests` | [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L829-L879) | Builds the `multiple` node and all ten stage groups. |
| `getShaderObjectNextStages` | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L58-L94) | The `nextStage` values, following the spec's legal stage chains. |
| `getShaderName` | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L31-L56) | Stage to program-binary name mapping used by the stage groups. |
| Parent registration, `createTests` | [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) | Attaches the `create` family under the `shader_object` test category. |
| Mustpass leaves | [create.txt](../../../mustpass/main/vk-default/shader-object/create.txt) | All 22 registered leaves of the family. |
