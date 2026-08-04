# Understanding Brief: spirv_assembly.instruction.{compute,graphics}.16bit_storage

## One-Sentence Test Purpose

This test checks whether an implementation that advertises `VK_KHR_16bit_storage` can correctly load, convert, and store 16-bit float and integer values through each of the four SPIR-V storage classes the extension enables — storage/uniform buffers, push constants, and shader input/output interfaces — using hand-authored SPIR-V assembly that exercises `OpFConvert`/`OpSConvert`/`OpUConvert` in both widening and narrowing directions.

## Background Knowledge

### VK_KHR_16bit_storage and its four SPIR-V capabilities

`VK_KHR_16bit_storage` (promoted to Vulkan 1.1 core) lets a shader use 16-bit scalar types — `OpTypeFloat 16`, `OpTypeInt 16 0`, `OpTypeInt 16 1` — as leaf members in resources that Vulkan otherwise lays out at 32-bit granularity. The extension is exposed through four independent SPIR-V capabilities, each gated by its own `VkPhysicalDevice16BitStorageFeatures` bit, and each unlocking one storage class:

- `StorageUniformBufferBlock16` → `storageBuffer16BitAccess` — 16-bit members in `BufferBlock`-decorated storage buffers (SSBOs).
- `StorageUniform16` → `uniformAndStorageBuffer16BitAccess` — 16-bit members in `Block`-decorated uniform buffers (UBOs). Implementations advertising this must also support the SSBO form.
- `StoragePushConstant16` → `storagePushConstant16` — 16-bit members in the `PushConstant` storage class.
- `StorageInputOutput16` → `storageInputOutput16` — 16-bit members in the `Input` and `Output` storage classes (shader stage interfaces, graphics only).

Why it matters here:
- The test matrix is built directly from these four capabilities. Each test family name encodes which capability and storage class is exercised, and each capability maps to a distinct feature bit that `checkSupport`/`requestedVulkanFeatures` enables.
- A device may support some capabilities and not others, so the test deliberately exercises them independently rather than treating the extension as a single on/off switch.

### Float narrowing and `FPRoundingMode`

Converting a 32-bit or 64-bit float to 16-bit is a narrowing operation: many representable 32/64-bit values fall between two representable 16-bit values, so the result depends on the rounding rule. SPIR-V lets a shader state the rule explicitly with `OpDecorate %result FPRoundingMode RTE|RTZ` on the narrowing store, where RTE is round-to-nearest-even and RTZ is round-toward-zero. If no `FPRoundingMode` is given, the implementation picks either.

Why it matters here:
- The narrowing test families (`32_to_16`, `64_to_16`) cannot compare against a single precomputed expected value, because the spec leaves the result implementation-defined when the rounding mode is unspecified. The host checker therefore re-derives the expected 16-bit value from the original wide float using the rounding mode the case selected, and accepts the result only if it matches that derivation.
- The widening direction (`16_to_32`, `16_to_64`) has no such ambiguity: every 16-bit value maps to exactly one 32/64-bit value, so the checker just compares against a precomputed expected buffer.

### std140, std430, and 16-bit struct layout

`std140` and `std430` are the standard uniform/storage-buffer layout rules. `std140` rounds every member up to a 16-byte boundary (vec4 alignment), which wastes space for 16-bit members. `std430` relaxes the rule so each member is aligned to its own scalar size. The struct test families deliberately mix 16-bit and 32-bit members under both layouts and under a "mixed" layout that interleaves them, to catch stride and offset miscalculation.

Why it matters here:
- The struct families (`uniform_16struct_to_32struct`, `uniform_32struct_to_16struct`, `struct_mixed_types`) are not about conversion arithmetic; they are about whether the shader compiler computes the same `Offset`/`ArrayStride`/`MatrixStride` decorations the host used to pack the input buffer. A wrong stride on either side produces a misaligned read that no arithmetic check would catch.

## One Concrete Example

Representative compute case: `dEQP-VK.spirv_assembly.instruction.compute.16bit_storage.uniform_16_to_32.uniform_buffer_block_scalar_float`.

The C++ builder [`addCompute16bitStorageUniform16To32Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1128-L1504) holds a `tcu::StringTemplate` with `${...}` placeholders. For the `uniform_buffer_block` capability and the `scalar` float composite type, the host fills the template with:

- `${capability}` = `StorageUniformBufferBlock16`
- `${storage}` = `BufferBlock` (so the 16-bit input is an SSBO)
- `${base16}` = `f16`, `${base32}` = `f32`
- `${convert}` = `OpFConvert`
- `${arrayindex}` = `x` (the dynamic `GlobalInvocationId.x`)

The specialized SPIR-V declares two SSBOs: `%ssbo16` (a struct wrapping `f16 x 128`) at binding 0 and `%ssbo32` (a struct wrapping `f32 x 128`) at binding 1. The entry point loads `%ssbo16` at index `x`, runs `OpFConvert %f32 %val16`, and stores the result into `%ssbo32` at the same index. Each compute invocation converts one element; the host dispatches `128` work groups.

The host fills `%ssbo16` with random `deFloat16` values, precomputes the expected `%ssbo32` content by widening each `deFloat16` to `float` with `deFloat16To32`, and after dispatch checks the readback with [`check32BitFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L341-L362), an exact float comparison.

## End-to-End Test Flow

The compute and graphics paths share the same logical sequence; the graphics path adds a render pass and per-stage shaders.

```text
[host] pick capability, conversion direction, composite type, and (graphics) rounding mode
[host] generate random input data sized to the chosen composite type
[host] precompute expected output buffer (exact for widening, rounding-mode-derived for narrowing)
[host] specialize the StringTemplate SPIR-V assembly and register it as the shader source
[host] create input buffer (16-bit or wide, per direction) and output buffer (wide or 16-bit, per direction)
[host] for push-constant families: bind input as push constants; otherwise bind input/output as descriptor set 0
[host] for graphics I/O families: pack input as vertex attributes / stage inputs, output as stage outputs read back from a color attachment or SSBO
[host] dispatch (compute) or draw (graphics)
[device] each invocation loads from the 16-bit-capable resource, converts via OpFConvert/OpSConvert/OpUConvert, stores to the wide (or 16-bit) sink
[host] copy back the output allocation
[host] run the direction-specific verifyIO callback: check32BitFloats / check64BitFloats / computeCheck16BitFloats<RoundingMode> / computeCheck16BitFloats64 / computeCheckBuffersFloats
[host] pass only if every element matches the expected buffer (with the rounding rule honored for narrowing)
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- **Specialized SPIR-V assembly text.** Every test family holds a `tcu::StringTemplate` in C++ and specializes it per case via a `map<string,string>` of placeholders (`${capability}`, `${storage}`, `${base16}`, `${base32}`, `${convert}`, `${stride}`, `${types}`, `${matrix_*}`, etc.). The specialized text is registered with `dst.spirvAsmSources.add("comp")` (compute) or through `createTestsForAllStages` (graphics). There is no GLSL or HLSL source anywhere in this file.
- **`FPRoundingMode` decorations (graphics I/O narrowing only).** The 32-to-16 and 64-to-16 input/output families inject `OpDecorate %ret0 FPRoundingMode RTZ|RTE` or leave it unspecified; the `unspecified_rnd_mode` case lets the implementation pick either and the checker accepts both.
- **Per-stage graphics fragments.** Graphics families use `passthruFragments()` plus `pre_main`, `testfun`, `decoration`, and `post_interface_op_*` fragment maps that `createTestsForAllStages` stitches into vertex, tessellation, geometry, and fragment shaders.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input SSBO/UBO (`%ssbo16` or `%ssbo32`) | yes, filled with random `deFloat16`/`float`/`int16` data | yes, descriptor set 0 binding 0 (or binding 1 for the wide input in narrowing cases) | read by shader | no | Carries the source values for conversion; its descriptor type (STORAGE_BUFFER vs UNIFORM_BUFFER) tracks the capability under test. |
| Output SSBO (`%ssbo32`/`%ssbo16`/`%ssbo64`) | yes, allocated zeroed | yes, descriptor set 0 binding 1 | written by shader | yes | Sink for converted results; read back and checked by the host. |
| Push constant block (`%pc16`) | yes, filled with 16-bit input data | yes, push constant range | read by shader | no | Replaces the input descriptor for `push_constant_*` families; exercises `StoragePushConstant16`. |
| Vertex attributes / stage I/O (graphics) | yes, packed via `GraphicsInterfaces::setInputOutput` | yes, as vertex input or stage interface | read/written across stages | yes, via color attachment or SSBO | Exercises `StorageInputOutput16` end to end across vert/tess/geom/frag. |
| Expected output buffer (host-only) | yes, precomputed | no | no | n/a | Compared against readback by the `verifyIO` callback. |

## What Is Checked

- The host `verifyIO` callback compares every element of the readback buffer against the expected buffer. The callback is chosen per family based on the conversion direction and data type:
  - Widening to 32-bit float: [`check32BitFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L341-L362) — exact `float` comparison.
  - Widening to 64-bit float: [`check64BitFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L314-L335) — exact `double` comparison.
  - Narrowing to 16-bit float from 32-bit: [`computeCheck16BitFloats<RoundingMode>`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L261-L284) / [`graphicsCheck16BitFloats<RoundingMode>`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L189-L212) — re-derives the expected 16-bit value from the original 32-bit float using the case's rounding mode.
  - Narrowing to 16-bit float from 64-bit: `computeCheck16BitFloats64`/`graphicsCheck16BitFloats64` — same idea, from `double`.
  - 16-to-16 pass-through: [`computeCheckBuffersFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L238-L259) — exact `uint16_t` comparison with NaN-equality fallback.
  - Integers: exact `int32_t`/`uint32_t` comparison with sign-extension handled on the host side.
- Struct families additionally use an `info` bitmask (built by [`addInfo`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L364-L368)) to skip padding bytes during comparison, since std140/std430 padding is not part of the tested data.
- Graphics I/O `unspecified_rnd_mode` cases accept either RTE or RTZ results; the rounding-mode flags passed to `interfaces.setRoundingMode()` are `ROUNDINGMODE_RTE | ROUNDINGMODE_RTZ`.
- Each case is checked independently; there is no aggregation across the matrix.

## Behavior Parameter Identification

> **Behavior parameter:** storage class / capability group (the SPIR-V capability and storage class under test)
>
> **Candidate values:**
> - `uniform_and_storage_buffer` — `StorageUniformBufferBlock16` (SSBO) and `StorageUniform16` (UBO), exercised together through the `CAPABILITIES[]` table; conversion in both directions across float/int scalar/vector/matrix.
> - `push_constant` — `StoragePushConstant16`; 16-bit input read from a push constant block, converted and written to an SSBO.
> - `input_output_interface` — `StorageInputOutput16`; 16-bit values cross the shader stage interface (graphics only), with explicit `FPRoundingMode` for narrowing.

Secondary dimensions (covered in `## Parameter Dimensions and Observed Values` on the final page, not as separate behavior axes): conversion direction (`16_to_32`, `32_to_16`, `16_to_64`, `64_to_16`, `16_to_16`), data type (float/int, scalar/vector/matrix), access index (dynamic `x` vs constant `5`/`8`), pipeline stage (compute vs graphics, and which graphics stages), struct layout (std140/std430/mixed).

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `uniform_and_storage_buffer` (SSBO/UBO load or store of 16-bit members) | 16-bit member offset/stride miscalculation in the shader compiler; descriptor binding or storage-class mismatch; `OpFConvert`/`OpSConvert`/`OpUConvert` lowering bug; feature flag not actually wired to the load/store path. |
| `push_constant` | Push-constant range upload or alignment for 16-bit members; `StoragePushConstant16` capability not honored at the pipeline layout; same conversion/stride causes as above. |
| `input_output_interface` (graphics) | Stage-interface matching for 16-bit locations; `FPRoundingMode` decoration ignored on a narrowing store; 16-bit location component packing; rasterization/interpolation of 16-bit varyings. |
| All values (shared infrastructure) | Host-side expected-buffer precomputation mismatch; rounding-mode flag mismatch between shader decoration and checker; descriptor/barrier setup in the shared compute/graphics harness. |

## Important Variations and Special Cases

- **Constant vs. dynamic access index.** The `scalar_const_idx_5` / `scalar_const_idx_8` variants replace the dynamic `OpAccessChain %... %ssbo16 %zero %x` index with a constant `%c_i32_ci`. This isolates constant-index lowering from dynamic-index lowering; a failure on only the constant-index variant points at the compiler's constant-index path.
- **Matrix composite type.** Float families include a `matrix` case using `%m4v2f16`/`%m4v2f32` with `ColMajor` and `MatrixStride` decorations, plus a multi-column store sequence (`matrix_store`). The host pads each 2-element column to 8 f16 slots to match the matrix layout. This is a float-only variant; there is no integer matrix case.
- **64-bit float source/sink.** The `64_to_16` and `16_to_64` families require `coreFeatures.shaderFloat64 = VK_TRUE` in addition to the 16-bit-storage feature bit. They reuse the same SPIR-V template shape but swap `OpTypeFloat 64` in and use the `*Floats64` checkers.
- **`16_to_16x2` dual-output pass-through (graphics I/O).** `addShaderCode16BitStorageInputOutput16To16x2` builds a shader that writes one 16-bit input to two 16-bit outputs, testing that a single interface location can fan out to multiple outputs without corruption.
- **Struct mixed layouts.** `struct_mixed_types` uses `SHADERTEMPLATE_STRIDEMIX_STD140`/`STRIDEMIX_STD430`, where a struct interleaves `i16` and `i32` members plus a nested struct array (`structData = {7, 11}` — 7 outer structs, 11 nested). `getStructSize()` returns a different byte count per layout, and the host zeroes an output buffer sized to the layout before dispatch.
- **`unspecified_rnd_mode` (graphics I/O narrowing).** When no `FPRoundingMode` is decorated, the checker accepts either RTE or RTZ, mirroring the spec's implementation-defined behavior.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `CAPABILITIES[]` table | [`vktSpvAsm16bitStorageTests.cpp#L126-L129`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L126-L129) | Defines the two uniform/storage capabilities iterated by every uniform-buffer family. |
| `get16BitStorageFeatures()` | [`vktSpvAsm16bitStorageTests.cpp#L149-L160`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L149-L160) | Maps capability name to the `ext16BitStorage` feature bit. |
| Compute uniform 16-to-32 builder | [`addCompute16bitStorageUniform16To32Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1128-L1504) | Representative SPIR-V `StringTemplate` and the float/int composite matrices. |
| Compute push-constant builder | [`addCompute16bitStoragePushConstant16To32Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L1703-L2000) | Push-constant SPIR-V template (`%pc16`, `PushConstant` storage class). |
| Graphics I/O 32-to-16 builder | [`addGraphics16BitStorageInputOutputFloat32To16Group()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3637-L3804) | `StorageInputOutput16`, `FPRoundingMode`, `createTestsForAllStages`. |
| Struct mixed-types builder | [`addCompute16bitStructMixedTypesGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L3053-L3275) | Nested struct + mixed 16/32 layout with `addInfo` bitmask comparison. |
| Narrowing checkers | [`computeCheck16BitFloats`/`graphicsCheck16BitFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L189-L284) | Rounding-mode-aware re-derivation of expected 16-bit values. |
| Widening checkers | [`check32BitFloats`/`check64BitFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L314-L362) | Exact comparison for unambiguous widening. |
| `16_to_16x2` builder | [`addShaderCode16BitStorageInputOutput16To16x2()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L4022-L4226) | Dual-output pass-through shader. |
| Registration entry points | [`create16BitStorageComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8620-L8648), [`create16BitStorageGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm16bitStorageTests.cpp#L8650-L8701) | Map test family names to builder functions. |

## Questions / Risk Points for User Audit

- Is the **storage class / capability group** the right primary behavioral axis, or should the conversion direction (`16_to_32` vs `32_to_16` etc.) be the axis instead? My choice reflects that the extension's four capabilities are the structural distinction the test is built around; conversion direction is secondary.
- The `uniform` capability uses `uniformAndStorageBuffer16BitAccess`, which strictly requires the SSBO form too. The source iterates both `CAPABILITIES[]` entries for every uniform-buffer family, so each family is run twice (once as SSBO, once as UBO). Is it acceptable to describe these as one behavior-parameter value rather than splitting them?
- The vulkan-docs spec chapters are not present in this checkout, so the Background Knowledge is grounded in the SPIR-V capability names, the C++ feature mapping, and the well-known semantics of `VK_KHR_16bit_storage` rather than a direct spec quote. Is that acceptable, or should I flag the missing spec reference explicitly on the final page?
- The representative walkthrough will specialize the compute `uniform_16_to_32` template for `uniform_buffer_block_scalar_float`. Is one walkthrough enough, or should a second cover the graphics I/O `StorageInputOutput16` + `FPRoundingMode` path? My plan is one walkthrough plus a Parameter Variation Summary that covers the I/O distinction.

## Conversion Notes for Final Wiki Rewrite

- Distill the four-capability Background Knowledge into a tight unordered list; keep the `FPRoundingMode` and std140/std430 bullets because they directly explain the checker design and the struct families.
- Use the compute `uniform_16_to_32` case as the single representative walkthrough (extract its specialized SPIR-V assembly under `#### Source Code`; omit `#### SPIR-V` per the spirv_assembly deviation).
- Carry the **storage class / capability group** identification into `## Behavior Parameters` with three subsections: uniform & storage buffer, push constant, input/output interface.
- Copy the `### Failure Cause Mapping` table above directly into the final page's `### Failure Cause Mapping`.
- Move the per-builder source links into the Source Reference Appendix; keep only the load-bearing inline links in the page body.
- Write `### Cause Analysis` fresh during the rewrite; do not copy analysis prose from this brief.
- The graphics I/O `FPRoundingMode` mechanism, the constant-index variants, the matrix case, the `16_to_16x2` dual-output, and the struct mixed-layout case belong in `## Behavior Parameters` / Parameter Variation Summary, not in the walkthrough.
