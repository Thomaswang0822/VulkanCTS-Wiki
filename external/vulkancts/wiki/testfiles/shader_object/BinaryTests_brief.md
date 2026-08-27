# Understanding Brief: shader_object binary test family

## One-Sentence Test Purpose

This test checks whether the binary form of an `VK_EXT_shader_object` shader object behaves as a stable artifact: `vkGetShaderBinaryDataEXT` must return data that is invariant across repeated queries, identical across re-created shaders and re-created logical devices, unaffected by which device features are enabled, correctly reported as `VK_INCOMPLETE` when the buffer is too small, and rejected with `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT` when corrupt data is submitted for creation.

## Background Knowledge

### Binary shader data and the query contract

`vkGetShaderBinaryDataEXT` returns the binary shader code of a `VkShaderEXT` object in two steps: a call with `pData = NULL` writes the byte size into `pDataSize`, and a second call with a buffer of that size writes the bytes. The spec deviates from the usual getter pattern on purpose: because shader binary data is only usable in its entirety, a too-small buffer must cause nothing to be written, `*pDataSize` must be overwritten with the amount of data actually written (zero), and `VK_INCOMPLETE` must be returned instead of `VK_SUCCESS`. Partial data is never returned.

Why it matters here:
- every query case first takes the size, then the bytes, so the tests exercise the documented two-step shape;
- the `half_size` leaf of the `incompatible` node tests exactly the too-small buffer contract: no writes, `*pDataSize` set to 0, result `VK_INCOMPLETE`.

### The binary round-trip and the compatibility identity

Binary shader code retrieved with `vkGetShaderBinaryDataEXT` can be passed back to `vkCreateShadersEXT` with `codeType = VK_SHADER_CODE_TYPE_BINARY_EXT`. The spec guarantees two things: repeated queries of the same `VkShaderEXT` return invariant data for the object's lifetime, and the binary can create a shader on a "compatible physical device". That compatibility is observable through `VkPhysicalDeviceShaderObjectPropertiesEXT`: `shaderBinaryUUID` identifies one or more implementations whose shader binaries are guaranteed to be compatible with each other, and `shaderBinaryVersion` counts backwards-compatible differences between implementations sharing the UUID. Logical devices created from the same physical device therefore share one binary compatibility identity.

Why it matters here:
- the query node compares binaries across different `VkShaderEXT` objects and across newly created logical devices on the same physical device, which goes beyond the spec's per-object invariance guarantee and turns the UUID compatibility model into a byte-level determinism demand;
- no special creation flag is needed to make a shader's binary queryable. Early drafts of `VK_EXT_shader_object` carried `VK_SHADER_CREATE_ALLOW_DERIVATIVES_BIT_EXT` and a capture flag, but neither exists in the current spec or in this checkout's headers; the tests query binaries of ordinary shaders created with `flags = 0` or `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT`.

### The incompatible-binary result code

When a binary submitted with `VK_SHADER_CODE_TYPE_BINARY_EXT` is not compatible with the device, `vkCreateShadersEXT` returns `VK_INCOMPATIBLE_SHADER_BINARY_EXT`. The current registry classifies this value (1000482000) as a success code, and `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT` is its legacy alias; the CTS headers define the error name as an alias of the new name, so the two spellings denote one value.

Why it matters here:
- the `incompatible` node submits corrupted and truncated buffers and requires exactly this value from `vkCreateShadersEXT`;
- the page should name the constant the way the test does (`VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`) and note the alias once.

## One Concrete Example

Reconstructed, simplified walk of the registered case `dEQP-VK.shader_object.binary.query.vert.linked.shader_from_binary`. The real code is `ShaderObjectBinaryQueryInstance::iterate` [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L270-L395):

1. The case builds a descriptor set layout with one storage-buffer binding for compute stages; `vert` passes no layout, so `layout = VK_NULL_HANDLE`.
2. `createShader` with `linked = true` creates a linked set in one `vkCreateShadersEXT` call: vertex and fragment always, tessellation control and evaluation when `tessellationShader` is supported, geometry when `geometryShader` is supported, all with `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT`. Only the vertex shader handle is kept; the other stages are destroyed [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L131-L246).
3. The instance queries the binary size of that vertex shader, allocates a byte vector, and queries the bytes.
4. Ten comparison rounds follow. In each round of this leaf, `vk::createShaderFromBinary` creates a new unlinked vertex shader from those bytes with `codeType = VK_SHADER_CODE_TYPE_BINARY_EXT` and `flags = 0` [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L96-L120).
5. Each round queries the new shader's binary size and bytes and requires size equality and byte equality with the original data. Any difference fails the case ("Size not matching" or "Data not matching").

So the leaf demands that a shader created from binary data reproduces exactly the binary data it was created from, even when the source was a linked shader and the recreation is unlinked.

## End-to-End Test Flow

All three nodes are entirely host-side. No command buffers are recorded, nothing is submitted to a queue, and no shader is ever executed.

```text
1. query family (ShaderObjectBinaryQueryInstance::iterate)
[host] build the stage's shader: unlinked single create, or a linked set from which only the target stage is kept
[host] query binary size with pData = NULL, then query the binary bytes
[host] repeat 10 rounds, obtaining otherData from a source selected by the query type leaf:
       same_shader            -> re-query the same shader object
       new_shader             -> create a second shader from the same SPIR-V and query it
       shader_from_binary     -> create a shader from the queried bytes (BINARY code type) and query it
       new_device             -> create a new logical device with identical features and extensions,
                                 create the shader there, query there
       device_no_exts_features-> create a logical device with only VK_EXT_shader_object enabled,
                                 only tessellationShader/geometryShader core features kept,
                                 create the shader there, query there
[host] each round: fail if sizes differ or any byte differs

2. incompatible family (ShaderObjectIncompatibleBinaryInstance::iterate)
[host] create one unlinked shader from the stage's SPIR-V
[host] query only the binary size; fill a same-size buffer with the constant 123
[host] half_size: halve the size variable, call vkGetShaderBinaryDataEXT with the small size
       require VK_INCOMPLETE, an untouched buffer, and *pDataSize == 0
[host] other leaves: overwrite part of the buffer with seeded random bytes (de::Random(102030)),
       halve the size variable for the create_from_* leaves
[host] call vkCreateShadersEXT with codeType = VK_SHADER_CODE_TYPE_BINARY_EXT and the buffer
       require VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT

3. device_features family (ShaderObjectDeviceFeaturesBinaryInstance::iterate)
[host] create the stage's shader on the context device and query its binary size and bytes
[host] collect ~200 extension feature structures and the core features the device was created with
[host] for each of 64 feature-chain combinations:
       disable core feature blocks of ten according to the leaf index bits (0..31)
       include pNext feature blocks of thirty according to the loop counter bits
       keep tessellationShader and geometryShader unchanged
       create a custom logical device, create the same shader there, query its binary
       fail if sizes differ or any byte differs
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- GLSL sources for the six stages (`vert`, `tesc`, `tese`, `geom`, `frag`, `comp`), generated once by `addBasicShaderObjectShaders` and shared by all three nodes [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211). The CTS build compiles them into SPIR-V program binaries. Shader content never affects the outcome beyond being creation input.
- Driver-side binary blobs (`std::vector<uint8_t>`), queried at run time. These are the artifacts under test: compared across queries, shaders, and devices in the `query` node, and the size reference for the synthetic buffers in the `incompatible` node.
- Synthetic buffers in the `incompatible` node: a byte vector filled with the constant 123, partly overwritten with values from `de::Random(102030)`. No real binary content is ever loaded into them; only their size derives from a real query.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Descriptor set layout (one storage-buffer binding, compute stage) | yes | referenced by `pSetLayouts` for compute shaders only | no | no | Matches the compute shader's buffer declaration; rebuilt per logical device because layout handles are device-specific. |
| SPIR-V program binaries | generated by the CTS build | passed as `pCode` | compiled inside `vkCreateShadersEXT` | no | The creation input. |
| Driver binary blobs | queried via `vkGetShaderBinaryDataEXT` | no | no | yes | The compared artifact of the `query` and `device_features` nodes. |
| Custom logical devices | created with `createCustomDevice` | n/a | n/a | n/a | Give the cross-device comparisons a fresh device with controlled features and extensions. |

No storage buffers, images, framebuffers, samplers, push constants, or command buffers are involved. The compute shader's `buffer_out` declaration exists only so the descriptor set layout has something to match.

## What Is Checked

- `query` node, all five leaves: the binary size and bytes obtained in each of ten rounds must equal the original query's size and bytes. The leaves differ only in where the comparison data comes from: the same object, a fresh compile, a from-binary recreation, a fresh logical device, or a minimal-feature logical device.
- `incompatible` node, `half_size` leaf: a `vkGetShaderBinaryDataEXT` call whose `*pDataSize` is half the real size must return `VK_INCOMPLETE`, must not modify the buffer, and must set `*pDataSize` to 0.
- `incompatible` node, the other four leaves: `vkCreateShadersEXT` with `VK_SHADER_CODE_TYPE_BINARY_EXT` and a corrupted or truncated buffer must return `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`.
- `device_features` node, all 32 leaves: for every one of the 64 feature-chain combinations, the binary data of the same shader created on a custom device must equal the binary data from the context device.
- All checks are host-side: return codes, buffer contents, and byte comparisons. There is no device-side output to inspect.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node under the `binary` test family (`query`, `incompatible`, `device_features`), with a leaf axis inside each node: the query type (`same_shader`, `new_shader`, `shader_from_binary`, `new_device`, `device_no_exts_features`), the corruption mode (`half_size`, `garbage_data`, `garbage_second_half`, `create_from_half_size`, `create_from_half_size_garbage`), and the feature-block index (`0` through `31`).
>
> **Candidate values:** `query` (55 leaves), `incompatible` (30 leaves), `device_features` (352 leaves); stage (`vert`, `tesc`, `tese`, `geom`, `frag`, `comp`) and linked state (`linked`, `unlinked`) are coverage dimensions inside every node.

## What Failure Means

### Failure Cause Mapping

Intermediate node axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `query` | Binary queries are not invariant, or binary data is not reproducible across creations and logical devices. |
| `incompatible` | Malformed binary data is mishandled: the size query violates the too-small buffer contract, or creation accepts corrupt data instead of returning `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`. |
| `device_features` | Shader binary data depends on which device features are enabled. |

Query type axis (leaves of every stage and linked subgroup under `query`):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `same_shader` | Repeated queries of the same shader object return different data. |
| `new_shader` | Compiling identical SPIR-V twice produces different binaries. |
| `shader_from_binary` | A shader created from binary data does not reproduce the binary it was created from. |
| `new_device` | Binary data differs between logical devices created with identical features and extensions. |
| `device_no_exts_features` | Binary data differs when the creating device enables only `VK_EXT_shader_object` and minimal features. |

Corruption mode axis (leaves of every stage subgroup under `incompatible`):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `half_size` | The too-small size query writes data, returns the wrong code, or leaves `*pDataSize` nonzero. |
| `garbage_data` | Creation accepts a fully random buffer as a shader binary. |
| `garbage_second_half` | Creation accepts a buffer whose second half is corrupted. |
| `create_from_half_size` | Creation accepts a truncated, constant-filled buffer. |
| `create_from_half_size_garbage` | Same cause as `create_from_half_size`; the generated garbage lies beyond the submitted `codeSize`. |

Feature-block index axis (leaves of every stage and linked subgroup under `device_features`):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any index `0`..`31` | The same shader's binary changes when core feature blocks are disabled; the index only selects which blocks. |

## Important Variations and Special Cases

- Linked compute is skipped in the `query` and `device_features` nodes: a linked set is a graphics stage chain, and compute has no stage to link with [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L866-L869). The `incompatible` node has no linked level at all; its source shader is always created unlinked with `flags = 0`.
- The `shader_from_binary` recreation always uses `getShaderObjectNextStages`, which ORs every eligible following stage, while the source shader created by the local `createShader` helper uses `getNextStage`, which picks a single following stage [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L73-L99). For a vertex shader on a device with both tessellation and geometry, the source carries `nextStage = TESC` and the recreation carries `TESC|GEOM|FRAG`; byte equality is still required. The same asymmetry exists between the `query`/`device_features` source shaders and their util-built counterparts.
- In the `incompatible` node, `create_from_half_size_garbage` writes garbage into the second half of the original buffer and then halves `codeSize`, so the submitted bytes are the first half, still the constant 123. The submitted input is identical to `create_from_half_size`; the garbage never enters the call. This looks like an unintended overlap and is reported as a risk point below.
- The `device_features` node does not test every feature combination. Core features are treated as five blocks of ten `VkBool32` values (the first 50 fields of `VkPhysicalDeviceFeatures`), and the leaf index bits select which blocks stay enabled; the last five core fields are never disabled. The roughly 200 extension feature structures are grouped into blocks of thirty, and an inner loop over 64 combinations selects which blocks enter the `pNext` chain. Only structs found in the device's queried feature chain are included, so unsupported extensions are skipped [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L700-L736).
- `tessellationShader` and `geometryShader` are restored to their original values before each custom device creation, because the created stage set depends on them [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L734-L736). The mesh shader feature fields `multiviewMeshShader` and `primitiveFragmentShadingRateMeshShader` are forced off because they depend on other features.
- The `QueryType` enumeration contains `ALL_FEATURE_COMBINATIONS`, but no case is registered for it and `getName` would assert on it; it is a dead placeholder [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L47-L55).
- The basic compute shader declares `layout(local_size_x=16, local_size_x=1, local_size_x=1)`, repeating `local_size_x` instead of using `local_size_y` and `local_size_z` [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L196-L203). No shader is ever executed, so this has no effect; it is further evidence that shader content is incidental to this family.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Query node flow, ten comparison rounds | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L270-L395) | Core flow of the `query` intermediate node. |
| `createShader` helper, unlinked and linked creation | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L101-L250) | How the source shader of every node is built. |
| Custom device creation for `new_device` / `device_no_exts_features` | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L325-L384) | The two cross-device comparison paths. |
| Incompatible node flow | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L457-L555) | Too-small buffer contract and corrupt-binary rejection. |
| Device features node flow | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L634-L764) | Feature-block manipulation and per-device comparison. |
| Feature block constants | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L700-L736) | The 5-times-10 core and 30-step pNext grouping. |
| Feature struct list | [vkDeviceFeaturesForShaderObject.inl](../../../framework/vulkan/generated/vulkan/vkDeviceFeaturesForShaderObject.inl#L207-L408) | The ~200 extension feature structures entering the pNext chain. |
| Support checks of the three nodes | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L420-L429) | `VK_EXT_shader_object` plus stage feature gates. |
| Registration | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L836-L946) | Builds `query`, `incompatible`, and `device_features`. |
| `createShaderFromBinary` | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L96-L120) | The unlinked binary recreation used by `shader_from_binary`. |
| Basic shader sources | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211) | The shared creation input for all six stages. |
| Parent registration | [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) | Attaches `binary` under the `shader_object` test category. |
| Mustpass leaves | [binary.txt](../../../mustpass/main/vk-default/shader-object/binary.txt) | All 437 registered leaves of the family. |

## Questions / Risk Points for User Audit

- `create_from_half_size_garbage` submits bytes identical to `create_from_half_size`, because the garbage is written to the second half of the original buffer and then `codeSize` is halved. The case name suggests truncated-plus-corrupted input, but the corruption never reaches `vkCreateShadersEXT`. Suspected test-design defect, reported unresolved; the page will document the submitted input factually.
- The `query` node demands byte equality across different shader objects and different logical devices. The spec guarantees invariance only for repeated queries of the same object, plus usability on a compatible physical device. The page should present the cross-object and cross-device equality as a CTS determinism demand grounded in the `shaderBinaryUUID` compatibility model, not as an explicit spec requirement.
- For `shader_from_binary`, source and recreation can differ in `nextStage` (single stage from `getNextStage` versus the OR of all eligible stages from `getShaderObjectNextStages`). Byte equality is still required, so the test effectively demands that the binary not depend on this difference. Worth a factual sentence in the page.
- `std::vector<uint8_t>` buffers are passed as `pData` to `vkGetShaderBinaryDataEXT`, whose valid usage requires 16-byte alignment when `pData` is not NULL. Default allocations satisfy this in practice on the supported platforms, but the guarantee comes from the allocator, not the type. Minor observation; no fix proposed.
- Walkthrough decision: no shader is ever bound, dispatched, or drawn, and validation is entirely host-side. Shader code is incidental, including the never-executed compute shader with its duplicate `local_size_x` declaration. I intend to record a no-walkthrough exception for this page. Confirm.
- The result code is named `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT` in the test and aliased to `VK_INCOMPATIBLE_SHADER_BINARY_EXT` in current headers (value 1000482000, a success code in the current registry). The page will use the test's spelling and note the alias once.

## Conversion Notes for Final Wiki Rewrite

- Distill Background Knowledge into three page-local prerequisite bullets: the two-step binary query and its too-small buffer contract, the binary round-trip with the `shaderBinaryUUID` compatibility identity, and the incompatible-binary result code with its alias note. No Level-2 page exists yet, so the section stays self-contained.
- The concrete example becomes the `shader_from_binary` explanation inside Behavior Parameters; do not carry the numbered list verbatim.
- Copy all four Failure Cause Mapping tables into the page's `### Failure Cause Mapping` unchanged; write `### Cause Analysis` fresh with causes matching the mapping (query determinism, cross-device reproducibility, too-small buffer handling, corrupt-binary rejection, feature-dependent binaries).
- Record the no-walkthrough justification in `## Shader Analysis` and add `BinaryTests.md` under `shader_object` in the walkthrough exception registry.
- Keep the `create_from_half_size_garbage` observation factual and short, in the corruption-mode subsection and in design-based pruning; the defect report goes to the user, not the page.
- Carry the `nextStage` asymmetry into the `shader_from_binary` subsection as one sentence.
- Mention registration shape and mustpass counts in Registration Hierarchy prose: 55 query leaves, 30 incompatible leaves, 352 device_features leaves, 437 total, with the wildcard source `dEQP-VK.*` and the performance-only exclusion.
