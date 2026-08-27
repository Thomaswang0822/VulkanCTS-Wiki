## Overview

**Core question:** Does a shader object's binary data stay byte-identical across repeated queries, re-created shaders, and re-created logical devices, and does the implementation return `VK_INCOMPLETE` and `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT` at the two points where the spec requires them?

- [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L1) implements the whole `shader_object.binary` test family: the `query`, `incompatible`, and `device_features` intermediate nodes, 437 test case leaves in the main mustpass set.
- The family treats the binary form of a shader as the object under test. The `query` node asks whether binary data is invariant and reproducible, the `incompatible` node asks whether malformed binaries are rejected with the documented result codes, and the `device_features` node asks whether the binary depends on which features the logical device has enabled.
- No shader is ever bound, dispatched, or drawn. Pass and fail come from return codes, buffer contents, and byte comparisons, all host-side.

## Background Knowledge

For the shared concept shader binaries, see [Background Knowledge](../../categories/shader_object.md#background-knowledge) of the `shader_object` page.

- **Binary shader data and the two-step query.** `vkGetShaderBinaryDataEXT` returns the binary shader code of a `VkShaderEXT` object in two steps: a call with `pData = NULL` writes the byte size into `pDataSize`, and a second call with a buffer of that size writes the bytes. The spec deviates from the usual getter pattern on purpose. Because shader binary data is only usable in its entirety, a too-small buffer must produce no writes, `*pDataSize` must be overwritten with the amount of data actually written (zero), and `VK_INCOMPLETE` must be returned instead of `VK_SUCCESS`.
- **The binary round-trip and the compatibility identity.** Retrieved binary data can be passed back to `vkCreateShadersEXT` with `codeType = VK_SHADER_CODE_TYPE_BINARY_EXT` on a compatible physical device, and repeated queries of the same `VkShaderEXT` return invariant data for the object's lifetime. Compatibility is observable through `VkPhysicalDeviceShaderObjectPropertiesEXT`: `shaderBinaryUUID` identifies implementations whose shader binaries are guaranteed to be compatible with each other, and `shaderBinaryVersion` counts backwards-compatible differences between implementations sharing that UUID. Logical devices created from one physical device share this identity. No special creation flag is needed to query a shader's binary; the capture-style flags from early drafts of the extension do not exist in the shipped spec or in this checkout's headers.
- **The incompatible-binary result code.** When a submitted binary is not compatible with the device, `vkCreateShadersEXT` returns `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`. Current CTS headers alias this name to `VK_INCOMPATIBLE_SHADER_BINARY_EXT`, one value that the current registry classifies as a success code. This page uses the spelling the test compares against.

## Registration Hierarchy

```text
shader_object.binary
├── query
├── incompatible
└── device_features
```

`createShaderObjectBinaryTests` builds all three nodes [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L836-L946). Inside each node, every stage has a subgroup (`vert`, `tesc`, `tese`, `geom`, `frag`, `comp`); `query` and `device_features` add a `linked`/`unlinked` level below the stage, skipping linked compute. The `query` node registers five query-type leaves per stage and link combination, 55 leaves; `incompatible` registers its five modes directly under each stage, 30 leaves; `device_features` registers index leaves `0` through `31` per stage and link combination, 352 leaves. All 437 leaves appear in the mustpass set [binary.txt](../../../mustpass/main/vk-default/shader-object/binary.txt); the source mustpass entry is the wildcard `dEQP-VK.*` [main.txt](../../../mustpass/main/src/main.txt), and the only `shader_object` exclusion covers `performance`, not `binary` [excluded-tests.txt](../../../mustpass/main/src/excluded-tests.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Shader stage | `vert`, `tesc`, `tese`, `geom`, `frag`, `comp` | Every node repeats its mechanism for each stage, so failures can be localized to one stage's binary handling. | [stageTests table](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L840-L851) |
| Linked state | `linked`, `unlinked` | Whether the source shader is created alone (`flags = 0`) or as part of a linked stage set; linked compute is not registered. | [linkedTests loop](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L853-L872) |
| Query type | `same_shader`, `new_shader`, `shader_from_binary`, `new_device`, `device_no_exts_features` | Where each comparison round gets its second binary blob: the same object, a fresh compile, a from-binary recreation, or one of two custom logical devices. | [queryTypeTests table](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L858-L860) |
| Corruption mode | `half_size`, `garbage_data`, `garbage_second_half`, `create_from_half_size`, `create_from_half_size_garbage` | How the synthetic buffer is derived from a real size query: truncated size, random bytes in all or half of the buffer, or a truncated size with garbage written past it. | [incompatibleTests table](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L887-L906) |
| Device-feature index | `0`..`31` | A five-bit pattern selecting which of five core-feature blocks stay enabled on the comparison devices. | [index loop](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L931-L935) |

## Behavior Parameters

The primary behavioral axis is the **intermediate node** under the `binary` test family: `query`, `incompatible`, and `device_features` each test a different property of shader binaries. Inside each node, the leaf is a second axis: the query type, the corruption mode, or the feature-block index.

### query: binary determinism and reproducibility

Each case creates the stage's shader, queries its binary size and bytes, then runs ten comparison rounds. Every round must reproduce the original size and bytes, and the leaves differ only in the source of the comparison data [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L270-L395):

| Leaf | Comparison source |
|------|-------------------|
| `same_shader` | Re-query the same `VkShaderEXT`. |
| `new_shader` | A second shader compiled from the same SPIR-V on the same device. |
| `shader_from_binary` | A new shader created from the queried bytes with `VK_SHADER_CODE_TYPE_BINARY_EXT`. |
| `new_device` | A new logical device with identical features and extensions. |
| `device_no_exts_features` | A new logical device with only `VK_EXT_shader_object` enabled and only the tessellation and geometry core features kept. |

`same_shader` matches the spec's per-object invariance guarantee. The other leaves go further: they demand that the driver produce the same bytes for the same input regardless of object identity, creation path, or logical device, which turns the `shaderBinaryUUID` compatibility model into a byte-level determinism requirement. In the `shader_from_binary` leaf the recreation is always unlinked with `flags = 0` [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L96-L120), even when the source shader was linked. The source and recreation can also declare different `nextStage` values: the local creation helper picks a single following stage while the util helper ORs every eligible one [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L73-L99), so a vertex shader on a device with both tessellation and geometry carries `TESC` as source and `TESC|GEOM|FRAG` as recreation. Byte equality is required either way.

### incompatible: malformed binaries must be rejected

The case creates one unlinked shader, queries only the binary size, and fills a buffer of that size with the constant 123; no real binary content is ever loaded [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L457-L555). The leaves then split into two mechanisms:

- `half_size` halves the size variable and calls `vkGetShaderBinaryDataEXT` with the small value. The call must return `VK_INCOMPLETE`, leave every buffer byte untouched, and set `*pDataSize` to 0. This pins the all-or-nothing query contract.
- The other four leaves overwrite part of the buffer with values from a seeded `de::Random(102030)` generator, halve the size for the `create_from_*` modes, and call `vkCreateShadersEXT` with `codeType = VK_SHADER_CODE_TYPE_BINARY_EXT`. `garbage_data` submits a fully random buffer at full size, `garbage_second_half` a half-corrupted one, and the two `create_from_*` modes a truncated buffer. All four must return `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`.

One detail is visible in the source: `create_from_half_size_garbage` writes garbage into the second half of the original buffer and then halves `codeSize`, so the submitted bytes are the untouched first half, identical to what `create_from_half_size` submits. The garbage never reaches the call.

### device_features: feature enablement must not change binaries

Each case queries the binary of its shader on the context device, then builds comparison devices whose feature sets differ [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L634-L764). Core features are treated as five blocks of ten booleans covering the first 50 of the 55 `VkPhysicalDeviceFeatures` fields; the leaf index bits select which blocks stay enabled, and the 32 leaves cover every combination. The 200 extension feature structures declared in [vkDeviceFeaturesForShaderObject.inl](../../../framework/vulkan/generated/vulkan/vkDeviceFeaturesForShaderObject.inl#L207-L408) are grouped into blocks of thirty, and an inner loop over 64 combinations selects which blocks enter the `VkPhysicalDeviceFeatures2` pNext chain, always headed by the shader object feature structure. A block's structs are only chained when the same structure type appears in the device's queried feature chain, so unsupported extensions are never requested. For each of the 64 devices, the same shader is created and its binary must equal the context device's bytes. The expectation: the binary is a property of the shader and the physical device, not of feature enablement.

## Shader Analysis

This page has no representative shader walkthrough. The family never binds, dispatches, or draws with any shader, and no validation reads shader output. All three nodes use the shared basic per-stage sources from `addBasicShaderObjectShaders` [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211) as creation input only; the tested behavior is the query contract, the creation result code, and byte equality of binary data. The compute source even declares `layout(local_size_x=16, local_size_x=1, local_size_x=1)`, a repeated `local_size_x`, which is harmless because the shader never runs. Because shader code is incidental here, this page is recorded as a no-walkthrough exception for the `shader_object` category.

## Runtime Execution and Result Checking

- **Host-only execution.** No command buffers, queues, draws, dispatches, or readback buffers. Every check is a return code, a buffer inspection, or a byte comparison.
- **Source shader creation.** Unlinked cases create one shader with `flags = 0`. Linked cases create a full linked set with `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT` (vertex and fragment always, tessellation stages and geometry per feature support), keep only the target stage's handle, and destroy the rest [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L101-L250). Compute is the only stage whose create info carries a descriptor set layout, matching its buffer declaration.
- **Binary query pattern.** Every real query follows the two-step shape: size with `pData = NULL`, then bytes into a buffer of that size.
- **Query node rounds.** Ten rounds per case, each producing `otherData` from the leaf's source and comparing size and bytes against the original data. The two device leaves create a fresh logical device per round through `createCustomDevice`, ten devices per case, and rebuild the compute descriptor set layout on each new device because layout handles are device-specific [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L325-L384). A mismatch fails with "Size not matching" or "Data not matching".
- **Incompatible node buffers.** The size query is the only real one; the buffer is synthetic. `half_size` expects `VK_INCOMPLETE`, an untouched buffer, and `*pDataSize = 0`, failing with "Result was not VK_INCOMPLETE", "Data was modified", or "Data size was not 0". The creation leaves fail with "Fail" when the result is anything other than `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT` [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L500-L552).
- **Device features node loop.** Each of the 64 iterations resets the core features before disabling blocks, rebuilds the pNext chain from the selected feature blocks, restores `tessellationShader` and `geometryShader` because the created stage set depends on them, and forces the mesh features `multiviewMeshShader` and `primitiveFragmentShadingRateMeshShader` off because they depend on other features [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L709-L739). The shader is then created on the custom device with the original feature values, so its structure stays identical while only the device differs. The comparison is the same size and byte check as the query node.
- **Final pass condition.** A case passes when all its rounds or iterations reproduce the original binary data, or when the incompatible leaves observe the required result codes and an untouched, zero-sized query state.

## Failure Meaning

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

### Cause Analysis

#### Binary queries are not invariant or not reproducible

**Possible failure symptoms:** A `same_shader`, `new_shader`, or `shader_from_binary` leaf fails with "Size not matching" or "Data not matching" in one of its ten rounds. The leaf identity narrows the defect: `same_shader` failing means one object returns different bytes across queries; `new_shader` means two compiles of the same input diverge; `shader_from_binary` means the round-trip through `VK_SHADER_CODE_TYPE_BINARY_EXT` does not reproduce its own input.

**Possible implementation causes:** The driver compiles nondeterministically, for example through a cache keyed on object identity or creation order, or its query path re-encodes data per call. The spec guarantees invariance only for repeated queries of one `VkShaderEXT`, so the cross-object equality this test demands is a stricter conformance expectation grounded in the `shaderBinaryUUID` compatibility model: one physical device should produce one binary for one input. A size-only mismatch points to the implementation appending or omitting variable-length sections between queries.

#### Cross-device binary data differs

**Possible failure symptoms:** A `new_device` or `device_no_exts_features` leaf fails with "Size not matching" or "Data not matching" on some round. All shaders involved were created from the same SPIR-V with the same structure, on logical devices of the same physical device.

**Possible implementation causes:** The driver bakes logical-device state into the binary, such as enabled extension lists, feature masks, device handles, or per-device cache identifiers, instead of keying the binary on the shader and the physical device. `device_no_exts_features` isolates this: its device enables one extension and almost no features, so any difference there points at feature- or extension-dependent compilation, the same defect class the `device_features` node probes systematically. Both leaves stay within one physical device, so cross-vendor incompatibility is not in scope.

#### Too-small buffer handling violates the query contract

**Possible failure symptoms:** The `half_size` leaf reports one of three violations: the query returned something other than `VK_INCOMPLETE`, a buffer byte changed from the constant fill ("Data was modified"), or `*pDataSize` was left nonzero ("Data size was not 0").

**Possible implementation causes:** The driver writes partial data before checking the buffer size, returns `VK_SUCCESS` with truncation the way other getter commands do, or leaves `*pDataSize` at the passed-in value instead of overwriting it with the number of bytes written. The spec is explicit that shader binary data is only usable in its entirety, so partial writes and silent truncation are both nonconforming.

#### Corrupt binaries are not rejected

**Possible failure symptoms:** A `garbage_data`, `garbage_second_half`, `create_from_half_size`, or `create_from_half_size_garbage` leaf fails with "Fail" because `vkCreateShadersEXT` returned a code other than `VK_ERROR_INCOMPATIBLE_SHADER_BINARY_EXT`, including an unexpected `VK_SUCCESS` with a live handle.

**Possible implementation causes:** The driver accepts arbitrary bytes without validating its own binary format or header, or it maps an unusable binary to a different error code such as `VK_ERROR_OUT_OF_HOST_MEMORY` or `VK_ERROR_INITIALIZATION_FAILED`. A truncated buffer accepted as valid would also surface here, and the truncated `codeSize` values in the `create_from_*` leaves specifically catch implementations that trust a size field inside the payload over the size they were given.

#### Feature-dependent binary compilation

**Possible failure symptoms:** A `device_features` leaf fails with "Size not matching" or "Data not matching" for one of its 64 feature combinations. Because every leaf uses the same shader and only the device differs, the failing combination itself is diagnostic evidence: it names the feature blocks whose enablement changed the output.

**Possible implementation causes:** The driver's compilation depends on enabled features, for example lowering shader operations differently when a feature is off, or embedding feature-derived state into the binary even when the shader does not use the feature. The comparison device keeps tessellation and geometry features unchanged, so a failure is not explainable by the stage structure changing; it points at compilation or serialization that reads device feature state the shader never uses. Source-level investigation of a specific driver would be needed beyond this classification.

## Case Pruning

### Requirement-based pruning

- Every case in the family requires the `VK_EXT_shader_object` extension, checked separately by the three case classes [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L420-L429), [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L584-L593), and [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L794-L803).
- `tesc` and `tese` stage subgroups require the `tessellationShader` core feature, and `geom` requires `geometryShader`; without the feature the cases are not run.

### Design-based pruning

- Linked compute is not registered in `query` and `device_features`: a linked set chains logically adjacent graphics stages, and compute has no adjacent stage [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L866-L869).
- The `incompatible` node has no linked level at all; its source shader is always created unlinked with `flags = 0`.
- Exhaustive feature combinations are infeasible, so features are tested in blocks: five core blocks of ten and six extension blocks of thirty, giving 32 registered leaves times 64 devices each rather than every individual feature pattern [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L700-L709).
- The last five core feature booleans are never disabled, because the size constant stops at 50 of the 55 fields.
- Each query case repeats its comparison ten times to catch nondeterminism that a single round might miss.
- `device_no_exts_features` provides a minimal baseline device, the opposite anchor to `new_device`'s identical device.
- `create_from_half_size_garbage` submits the same bytes as `create_from_half_size` because its garbage is written beyond the halved `codeSize`; the overlap is documented in the corruption mode subsection.
- The `QueryType` enumeration contains an `ALL_FEATURE_COMBINATIONS` value, but no case is registered for it and the name helper asserts if asked; it is an unused placeholder [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L47-L55).

## Key Takeaways

- The `binary` test family treats shader binaries as stable artifacts: only the `incompatible` node feeds deliberately malformed input, and everything else is byte equality between real queries.
- The cross-object and cross-device equality demanded by the `query` node goes beyond the spec's per-object invariance guarantee. It is a determinism requirement grounded in the `shaderBinaryUUID` compatibility identity, which all logical devices of one physical device share.
- `half_size` is the only place that pins the all-or-nothing query contract: no partial writes, `*pDataSize` overwritten with zero, `VK_INCOMPLETE` returned.
- The `device_features` node runs 32 leaf patterns against 64 feature-chain combinations per case, up to 2048 custom devices per stage and link combination, and requires that none of them change one byte of the binary.
- `create_from_half_size_garbage` submits identical bytes to `create_from_half_size`; the registered redundancy is a fact of the source, documented here rather than fixed in it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `ShaderObjectBinaryQueryInstance::iterate` | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L270-L395) | Core flow of the `query` node: ten comparison rounds per leaf. |
| `createShader` helper | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L101-L250) | Unlinked and linked source shader creation for all nodes. |
| Custom device paths, `new_device` and `device_no_exts_features` | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L325-L384) | The two cross-device comparison leaves. |
| `ShaderObjectIncompatibleBinaryInstance::iterate` | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L457-L555) | Too-small buffer contract and corrupt-binary rejection. |
| `ShaderObjectDeviceFeaturesBinaryInstance::iterate` | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L634-L764) | Feature-block manipulation and per-device comparison. |
| Feature block constants and chain assembly | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L700-L739) | The 5-times-10 core grouping and 30-step pNext grouping. |
| Support checks of the three case classes | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L420-L429) | Extension and stage feature gates. |
| Registration, `createShaderObjectBinaryTests` | [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L836-L946) | Builds `query`, `incompatible`, and `device_features`. |
| `createShaderFromBinary` | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L96-L120) | The unlinked binary recreation used by `shader_from_binary`. |
| `getShaderObjectNextStages` and `getShaderName` | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L31-L94) | Stage chain and program binary name mapping. |
| `addBasicShaderObjectShaders` | [vktShaderObjectCreateUtil.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L122-L211) | The shared creation input for all six stages. |
| Extension feature structure list | [vkDeviceFeaturesForShaderObject.inl](../../../framework/vulkan/generated/vulkan/vkDeviceFeaturesForShaderObject.inl#L207-L408) | The 200 pNext feature structures of the `device_features` node. |
| Parent registration, `createTests` | [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) | Attaches `binary` under the `shader_object` test category. |
| Mustpass leaves | [binary.txt](../../../mustpass/main/vk-default/shader-object/binary.txt) | All 437 registered leaves of the family. |
