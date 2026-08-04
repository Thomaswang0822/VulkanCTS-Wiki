# Understanding Brief: spirv_assembly.instruction.{compute,graphics}.8bit_storage

## One-Sentence Test Purpose

This test family checks whether a Vulkan implementation correctly loads, stores, and width-converts 8-bit integers across `StorageBuffer`, `Uniform`, and `PushConstant` storage classes when the `VK_KHR_8bit_storage` extension advertises one of the three 8-bit-storage capabilities (`StorageBuffer8BitAccess`, `UniformAndStorageBuffer8BitAccess`, `StoragePushConstant8`).

## Background Knowledge

### `VK_KHR_8bit_storage` and its three SPIR-V capabilities

`VK_KHR_8bit_storage` (promoted to Vulkan 1.1 core) introduces 8-bit integer types in shader-visible storage that previously held only 16/32/64-bit data. The extension exposes three orthogonal SPIR-V capabilities, each gating a different storage class:

- `StorageBuffer8BitAccess` permits 8-bit loads/stores in the `StorageBuffer` storage class (matches the `storageBuffer8BitAccess` Vulkan feature).
- `UniformAndStorageBuffer8BitAccess` permits 8-bit loads/stores in both `Uniform` and `StorageBuffer` storage classes (matches `uniformAndStorageBuffer8BitAccess`).
- `StoragePushConstant8` permits 8-bit loads from `PushConstant` storage class (matches `storagePushConstant8`).

Each test case enables exactly one of these three feature flags through [`get8BitStorageFeatures`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L140-L153), so a single case exercises exactly one capability gate at a time. The shader advertises the matching `OpCapability` and `OpExtension "SPV_KHR_8bit_storage"`.

### Width conversion opcodes

SPIR-V's `OpSConvert` and `OpUConvert` change the bit width of a scalar or vector of integers without changing its storage location. `OpSConvert` sign-extends; `OpUConvert` zero-extends. They are the only conversion opcodes exercised here — the data is loaded in one width, converted in registers, and stored back in another width. The test family crosses 32↔8, 16↔8, and 8↔8 widths to verify both directions of every legal pair.

### std140 vs std430 layout for 8-bit members

The struct-conversion branches of the test family exercise the layout rules for 8-bit members under both std140 (`Uniform` storage class default) and std430 (`StorageBuffer` storage class default). std140 rounds array strides and struct offsets up to a multiple of 16 bytes for any 8-bit vector or scalar; std430 permits tighter strides (1, 2, or 4 bytes depending on vector width). The two layouts share the same data fields but differ in padding. The `infoMixStd140`/`infoMixStd430` bitmasks in [`vktSpvAsm8bitStorageTests.cpp#L455-L573`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L455-L573) record which bytes hold data vs padding for each layout so the host-side comparator can compare only data bytes.

### `arrayStrideInBytesUniform = 16`

The std140 minimum array stride for any element in a `Uniform` buffer is 16 bytes. This constant appears throughout the uniform-buffer cases and forces the input buffer to be 16× larger than the actual 8-bit data, with the host comparator stepping by 16 bytes per element. See [vktSpvAsm8bitStorageTests.cpp#L80](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L80).

## One Concrete Example

Take the simplest compute case, `spirv_assembly.instruction.compute.8bit_storage.storagebuffer_32_to_8.storage_buffer_scalar_sint`, registered by [`addCompute8bitStorage32To8Group`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L928-L1084):

- The shader declares two `StorageBuffer` blocks `%SSBO32` (128 × `i32`) and `%SSBO8` (128 × `i8`), bound to descriptor set 0 binding 0 and 1.
- For invocation `x = GlobalInvocationId.x`, it loads `%val32 = OpLoad %i32` from `SSBO32[x]`, narrows it with `%val8 = OpSConvert %i8 %val32`, and stores the 8-bit result into `SSBO8[x]`.
- Host side: 128 random `int32_t` inputs are generated; the expected `int8_t` outputs are `static_cast<int8_t>(0xff & inputs[numNdx])`. After dispatch of `(128, 1, 1)` workgroups, [`computeCheckBuffers`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L155-L161) does a byte-level `deMemCmp` between the host-held input bytes and the device-written output allocation.

This shape (input SSBO → load → width-convert → store → output SSBO → byte compare) is the template for every compute conversion case; only the storage class, conversion opcode, and direction change.

## End-to-End Test Flow

```text
[host] pick the capability axis (storage_buffer / uniform / push_constant) and the conversion direction (32→8, 8→32, 16→8, 8→16, 8→8, struct↔struct, mixed struct)
[host] enable the matching VulkanFeatures.ext8BitStorage flag via get8BitStorageFeatures
[host] for graphics cases, also enable vertexPipelineStoresAndAtomics and fragmentStoresAndAtomics core features
[host] generate random input data (int32 / int16 / int8 / struct data with known padding bitmasks)
[host] compute expected output by truncating / sign-extending / zero-extending / byte-comparing on the host
[host] specialize the SPIR-V StringTemplate with the chosen capability, stride decorations, types, conversion opcode
[host] bind input and output buffers (storage buffer / uniform buffer / push constant) at descriptor set 0
[host] dispatch compute (1×N×1 workgroups) or render a graphics pipeline (vertex + tess + geom + frag via createTestsForAllStages)
[device] each invocation loads from input, OpSConvert/OpUConvert to the target width, stores to output
[host] read back output allocation
[host] run the case-specific verifier: computeCheckBuffers, checkUniformsArray, checkUniformsArrayConstNdx, or checkStruct<...>
[host] decide pass/fail per case
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline SPIR-V assembly text built by `tcu::StringTemplate` per case. The template carries `${capability}`, `${stride}`, `${types}`, `${base32}`, `${base8}`, `${convert}` slots that the per-case `specs` map fills in.
- Layout decoration fragments from [`getStructShaderComponet`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L738-L892) — six `ShaderTemplate` variants encode the std140/std430 × 8-bit/32-bit/mixed struct layouts. The mixed layout uses `${InOut}` to share one fragment between the input and output structs.
- Loop helpers [`beginLoop`/`endLoop`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L899-L926) for the struct cases that iterate over a nested array of 11 elements.
- For graphics cases, fragment collections (`pre_main`, `decoration`, `testfun`, `capability`, `extension`) are passed to `createTestsForAllStages`, which builds one graphics pipeline per stage in `{vert, tesc, tese, geom, frag}`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---------|------------------------------|---------------|--------------------------|--------------------|----------------|
| Input SSBO/UBO/push constant | yes, random data | yes (descriptor set 0, binding 0) | read by shader | no | Source of 32/16/8-bit values to convert |
| Output SSBO | yes, zero-initialized | yes (descriptor set 0, binding 1) | written by shader | yes | Receives converted 8/16/32-bit results |
| Push constant buffer (push_constant cases) | yes | yes (PushConstant storage class) | read by shader | no | Carries 8-bit values that exercise `StoragePushConstant8` |
| Graphics color attachments | yes | yes (render pass) | written by fragment stage | yes | `createTestsForAllStages` reads back color output and compares against `defaultColors` |
| Uniform array stride padding | yes, implicit in `arrayStrideInBytesUniform = 16` | yes | occupies 16-byte slots | yes | Forces std140 stride on uniform 8-bit arrays; host comparator must skip padding |
| Struct data bitmasks (`info8bitStd140` etc.) | yes, host-only | no | no | yes | Tell `checkStruct` which bytes are data vs padding so it compares only data bytes |

## What Is Checked

- **Compute buffer comparison** ([`computeCheckBuffers`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L155-L161)): byte-level `deMemCmp` of original input bytes against the device output allocation. Used by the simplest 32→8, 16→8, 8→8 cases where the expected output is just the truncated input.
- **Uniform array comparison** ([`checkUniformsArray<originType, resultType, compositCount>`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L672-L703) and [`checkUniformsArrayConstNdx`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L705-L736)): compares only the data bytes inside each 16-byte std140 array slot, skipping the padding.
- **Struct comparison** ([`checkStruct<originType, resultType, funcOrigin, funcResult>`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L654-L670)): walks both buffers with the appropriate `infoXStdY` bitmask, extracts only data bytes, and compares them as `int8_t`. Used by all struct↔struct and mixed-struct cases.
- **Graphics verification**: `createTestsForAllStages` renders one draw per stage and compares color-attachment output against `defaultColors`. The shader's `testfun` writes converted values to the output SSBO and returns the parameter color; if conversion corrupts state, the color check fails alongside the buffer check.
- Each case reports its own pass/fail. There is no aggregation across cases.

## Behavior Parameter Identification

> **Behavior parameter:** `capability + conversion direction` (the combination that selects both the SPIR-V capability and the OpConvert opcode exercised)
>
> **Candidate values:** `storagebuffer_32_to_8`, `uniform_8_to_32`, `push_constant_8_to_32`, `storagebuffer_16_to_8`, `uniform_8_to_16`, `push_constant_8_to_16`, `uniform_8_to_8`, `uniform_8struct_to_32struct`, `storagebuffer_32struct_to_8struct`, `struct_mixed_types` (compute); `storagebuffer_int_32_to_8`, `uniform_int_8_to_32`, `push_constant_int_8_to_32`, `storagebuffer_int_16_to_8`, `uniform_int_8_to_16`, `push_constant_int_8_to_16`, `8struct_to_32struct`, `32struct_to_8struct`, `struct_mixed_types` (graphics).

A secondary axis is **composite type** (`scalar_sint`, `scalar_uint`, `vector_sint`, `vector_uint`) inside the scalar/vector conversion cases. It selects `OpSConvert`/`OpUConvert` and the scalar vs `v2i*`/`v4i*` type, but does not change the storage class or capability.

A third axis is **graphics pipeline stage** (`vert`, `tesc`, `tese`, `geom`, `frag`) for the graphics variants, selected by `createTestsForAllStages`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `storagebuffer_32_to_8` / `storagebuffer_int_32_to_8` | Wrong `OpSConvert`/`OpUConvert` narrowing in `StorageBuffer`; wrong `StorageBuffer8BitAccess` capability advertisement; wrong `ArrayStride 1` on the 8-bit array. |
| `uniform_8_to_32` / `uniform_int_8_to_32` | Wrong 8-bit load from `Uniform` storage; wrong `UniformAndStorageBuffer8BitAccess` capability; std140 stride mishandled (host comparator expected to skip 16-byte slots). |
| `push_constant_8_to_32` / `push_constant_int_8_to_32` | Wrong 8-bit load from `PushConstant`; wrong `StoragePushConstant8` capability; sign-extension mismatch between host expectation and device `OpSConvert`. |
| `storagebuffer_16_to_8` / `uniform_8_to_16` / `push_constant_8_to_16` | Wrong 16↔8 width conversion; missing `StorageUniform16` capability in addition to the 8-bit capability; sign/zero extension disagreement between host and device. |
| `uniform_8_to_8` | Wrong 8-bit→8-bit pass-through in `StorageBuffer` with `Coherent` decoration; race between `OpStore` to `%x` and `OpStore` to `%y` slots when workgroup size is `(128, 128, 1)`. |
| `uniform_8struct_to_32struct` / `storagebuffer_32struct_to_8struct` / `8struct_to_32struct` / `32struct_to_8struct` | Wrong struct member offset under std140 or std430; wrong `ArrayStride` on nested arrays; wrong sign-extension when converting each member. |
| `struct_mixed_types` | Wrong layout when 8-bit and 32-bit members share one struct under std140 or std430; wrong nested-struct stride; wrong per-data-byte extraction by `checkStruct`. |
| Graphics-only `*_int_*` variants | Wrong `vertexPipelineStoresAndAtomics` / `fragmentStoresAndAtomics` feature handling; conversion or store lowered incorrectly in the vertex or fragment stage. |

### Cause Analysis (deferred to final rewrite)

The detailed `### Cause Analysis` subsections are written fresh during the Level-3 rewrite, not in this brief.

## Important Variations and Special Cases

- **Compute vs graphics split.** Compute cases live under `spirv_assembly.instruction.compute.8bit_storage.*` and use `SpvAsmComputeShaderCase`. Graphics cases live under `spirv_assembly.instruction.graphics.8bit_storage.*` and use `createTestsForAllStages`, which expands one case into `{vert, tesc, tese, geom, frag}` leaves. Graphics child test names use an `_int_` infix (e.g., `storagebuffer_int_32_to_8`) that the compute children do not.
- **`uniform_8_to_8` is a stress test.** The single registered case `spirv_assembly.instruction.compute.8bit_storage.uniform_8_to_8.stress_test` dispatches `(128, 128, 1)` workgroups and uses `Coherent`-decorated SSBO members so each invocation writes both `data[x]` and `data[y]`. It exists to stress atomicity and coherence of 8-bit stores, not conversion correctness.
- **Mixed struct layout uses `${InOut}` placeholder.** [`getStructShaderComponet(SHADERTEMPLATE_STRIDEMIX_STD140)`](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L838-L862) shares one decoration fragment between input (`In`) and output (`Out`) by parameterizing the type names. The output is always std430 (`StorageBuffer`); only the input storage class toggles between `Uniform` (std140) and `StorageBuffer` (std430) based on capability.
- **Push constant 8-to-32 sign extension.** The host computes expected `int32_t` outputs by `0xffff0000` sign-extension of the high bit. Mismatch between host and device on sign extension is the typical failure mode for this subgroup.
- **Graphics struct cases.** Graphics struct cases (`8struct_to_32struct`, `32struct_to_8struct`, `struct_mixed_types`) build graphics-pipeline variants of the compute struct cases. The shader logic is the same; only the pipeline wrapper and stage coverage differ.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Compute factory `create8BitStorageComputeGroup` | [vktSpvAsm8bitStorageTests.cpp#L5087-L5117](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5087-L5117) | Registers the 10 compute children under `8bit_storage`. |
| Graphics factory `create8BitStorageGraphicsGroup` | [vktSpvAsm8bitStorageTests.cpp#L5119-L5146](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L5119-L5146) | Registers the 9 graphics children under `8bit_storage`. |
| Capability table | [vktSpvAsm8bitStorageTests.cpp#L111-L114](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L111-L114) | Maps `storage_buffer`/`uniform` to SPIR-V capability and descriptor type. |
| Feature gate helper | [vktSpvAsm8bitStorageTests.cpp#L140-L153](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L140-L153) | Translates a capability name into a `VulkanFeatures.ext8BitStorage` flag. |
| Compute buffer verifier | [vktSpvAsm8bitStorageTests.cpp#L155-L161](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L155-L161) | Byte-level `deMemCmp` used by simple conversion cases. |
| Struct verifier | [vktSpvAsm8bitStorageTests.cpp#L654-L670](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L654-L670) | `checkStruct<originType, resultType, funcOrigin, funcResult>` template; filters bytes through `infoXStdY` bitmasks. |
| Layout decoration fragments | [vktSpvAsm8bitStorageTests.cpp#L738-L892](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L738-L892) | Six `ShaderTemplate` variants encoding std140/std430 × 8/32/mixed struct layouts. |
| Representative compute case `storagebuffer_32_to_8` | [vktSpvAsm8bitStorageTests.cpp#L928-L1084](../../../modules/vulkan/spirv_assembly/vktSpvAsm8bitStorageTests.cpp#L928-L1084) | Simplest conversion group; SPIR-V template and 4 composite-type cases. |
| Mustpass entry range (compute) | [spirv-assembly.txt#L740-L770](../../../external/vulkancts/mustpass/main/vk-default/spirv-assembly.txt#L740-L770) | Mirrors registered `dEQP-VK.spirv_assembly.instruction.compute.8bit_storage.*` cases. |
| Mustpass entry range (graphics) | [spirv-assembly.txt#L22460-L22560](../../../external/vulkancts/mustpass/main/vk-default/spirv-assembly.txt#L22460-L22560) | Mirrors registered `dEQP-VK.spirv_assembly.instruction.graphics.8bit_storage.*` cases (one leaf per stage × type × direction). |

## Questions / Risk Points for User Audit

- Is the choice of `storagebuffer_32_to_8.storage_buffer_scalar_sint` as the representative walkthrough acceptable, or should the walkthrough cover a struct case instead?
- Is the behavior parameter axis (`capability + conversion direction`) the right primary axis, or should it be just `capability` with conversion direction as a sub-axis?
- The mixed-struct cases rely on host-side bitmasks (`infoMixStd140` etc.) to skip padding. Are the bitmask contents accurate enough that a struct-case failure can be attributed to the device rather than to a host-side mask bug? This is worth flagging in `### Cause Analysis`.
- The `uniform_8_to_8.stress_test` case is the only `Coherent`-decorated 8-bit case. Does it need a separate walkthrough, or is one walkthrough sufficient for the whole page?

## Conversion Notes for Final Wiki Rewrite

- The brief's `## Background Knowledge` should distill to a Level-3 bullet list covering: the three SPIR-V capabilities and their feature gates; `OpSConvert`/`OpUConvert`; std140 vs std430 for 8-bit members; `arrayStrideInBytesUniform = 16`.
- The representative walkthrough is the `storagebuffer_32_to_8.storage_buffer_scalar_sint` compute case. The extracted SPIR-V assembly lives under `#### Source Code` (unfoldable). The `#### SPIR-V` subsection is omitted per the spirv_assembly category deviation.
- The `### Failure Cause Mapping` table is copied directly into the final page's `### Failure Cause Mapping`.
- The `### Cause Analysis` is written fresh during the rewrite, with one `####` subsection per cause family (capability advertisement, conversion opcode, layout/stride, push-constant sign extension, coherence stress, graphics stage handling).
- Source entry points move to the `## Source Reference Appendix` as a focused table.
