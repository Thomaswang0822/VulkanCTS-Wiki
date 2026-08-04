## Overview

**Core question:** Does the implementation correctly execute signed, unsigned, and mixed-signedness integer dot products, including accumulating saturating forms, across the registered operand-format and width matrix?

- Source file: [`vktSpvAsmIntegerDotProductTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L36-L42), an implementation-bearing file for six direct children of `spirv_assembly.instruction.compute`.
- Test category: `spirv_assembly`; page scope: the integer-dot-product instruction families under `instruction.compute`.
- Core test idea: C++ generates a SPIR-V compute module and host reference data for each combination of operation, signedness, packing, vector shape, element width, output width, and input range. Each invocation processes one vector pair and writes one scalar result.
- The page describes the generated instruction form, runtime buffers and oracle, feature-based pruning, and what a failed family can localize.

## Background Knowledge

- `VK_KHR_shader_integer_dot_product` exposes `shaderIntegerDotProduct`, which permits shader modules to declare `DotProductInputAllKHR`, `DotProductInput4x8BitKHR`, `DotProductInput4x8BitPackedKHR`, and `DotProductKHR` capabilities ([feature definition](../../../../vulkan-docs/src/chapters/features.adoc#L6695-L6728)).
- `OpSDotKHR`, `OpUDotKHR`, and `OpSUDotKHR` select signed, unsigned, and mixed signed/unsigned dot-product semantics. Their `AccSat` counterparts also consume an addend and return a result clamped to the selected signed or unsigned output range rather than a wrapped final sum.
- Packed operands represent exactly four 8-bit components in one scalar and use `PackedVectorFormat4x8BitKHR`. Unpacked vectors use storage-buffer array strides appropriate to their element width. Three-component host vectors occupy a four-element-aligned slot, with the unused component set to zero.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute
├── opsdotkhr
├── opudotkhr
├── opsudotkhr
├── opsdotaccsatkhr
├── opudotaccsatkhr
└── opsudotaccsatkhr
```

The tree expands the direct children implemented by this source file. Each family generates its executable test-case leaves from the parameter matrix below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Instruction form | `OpSDotKHR`, `OpUDotKHR`, `OpSUDotKHR`, `OpSDotAccSatKHR`, `OpUDotAccSatKHR`, `OpSUDotAccSatKHR` | Selects signedness semantics and whether an addend is accumulated with saturation. | [`generateIntegerDotProductCode`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L354-L528) |
| Input range | `all`, `small`, `limits`, `limits-neg`, `small-neg`, `small-nosat`, `nosat` | Controls randomized operand ranges and, for AccSat cases, whether the addend is near the maximum or minimum limit. | [`createOp*Dot*KHRComputeGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1175-L1320) |
| Packing and operand signs | unpacked/packed plus `ss`, `su`, `us`, `uu` | Selects ordinary vectors or the 4×8-bit packed representation and the signedness of each encoded input. | [`dotProductPacking`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L222-L225) |
| Vector shape | `v2i8`, `v3i8`, `v4i8`, `v2i16`, `v3i16`, `v4i16`, `v2i32`, `v3i32`, `v4i32` | Changes operand element width and the number of multiplicands in each dot product. | [`dotProductVector*`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L227-L244) |
| Result width | `out8`, `out16`, `out32` where permitted | Changes the scalar result type and its saturation limits for AccSat cases. | [`getDotProductTestName`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L533-L539) |
| Workload size | `200` elements | Sets one compute invocation and one result per generated vector pair. | [`addOpSDotKHRComputeTests`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L569-L611) |

## Behavior Parameters

The behavior parameter is the direct instruction-family child under `spirv_assembly.instruction.compute`. The first three families test non-accumulating dot products; the latter three test the matching accumulating, saturating operations.

### opsdotkhr: signed dot product

`opsdotkhr` emits `OpSDotKHR`, selecting signed dot-product semantics. The generated matrix covers `all` and 8-bit `small` ranges, unpacked vectors across 8/16/32-bit elements, and packed 4×8-bit combinations. For packed cases, the common `dotProductPacking` matrix still supplies `ss`, `su`, `us`, and `uu` encoded-input variants; the expected value is the host-computed signed dot product.

### opudotkhr: unsigned dot product

`opudotkhr` emits `OpUDotKHR`, selecting unsigned dot-product semantics. Its construction matches `opsdotkhr`; its unpacked inputs and instruction interpretation are unsigned, while the packed cases retain the common encoded-input signedness matrix.

### opsudotkhr: signed-LHS, unsigned-RHS dot product

`opsudotkhr` emits `OpSUDotKHR`, selecting mixed signed/unsigned dot-product semantics. Its unpacked left operand is signed and its unpacked right operand is unsigned, so that path targets the mixed-signedness rule rather than merely a different set of random values; packed cases retain the common encoded-input signedness matrix.

### opsdotaccsatkhr: signed accumulating saturating dot product

`opsdotaccsatkhr` emits `OpSDotAccSatKHR`. It adds a third input buffer containing near-limit signed addends. The `all`, `limits`, `limits-neg`, `small`, and `small-neg` registrations exercise ordinary values and both saturation directions.

### opudotaccsatkhr: unsigned accumulating saturating dot product

`opudotaccsatkhr` emits `OpUDotAccSatKHR`. It uses `all`, `limits`, `small`, `small-nosat`, and `nosat` ranges to distinguish expected saturation from inputs selected to avoid it.

### opsudotaccsatkhr: mixed-signedness accumulating saturating dot product

`opsudotaccsatkhr` emits `OpSUDotAccSatKHR`, combining a signed LHS, unsigned RHS, and a signed result/addend. Its `limits-neg` and `small-neg` variants use a near-minimum addend to test lower-bound saturation.

## Shader Analysis

These tests author SPIR-V assembly directly in C++ rather than compiling GLSL or HLSL. The representative shape is `dEQP-VK.spirv_assembly.instruction.compute.opsdotkhr.small_ss_v4i8_out32`; it is generated by [`generateIntegerDotProductCode`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L354-L528). The published walkthrough explains the source generator rather than duplicating a hand-specialized assembly fence.

### Representative shader walkthrough 1: `opsdotkhr.small_ss_v4i8_out32`

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.opsdotkhr.small_ss_v4i8_out32
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `OpSDotKHR` | Uses signed dot-product semantics without an accumulator. |
| `small` | Both 8-bit signed input buffers are randomized in `[-20, 20]`. |
| `ss` | Both generated operands are signed. |
| `v4i8` | Each invocation reads four signed 8-bit components from each input buffer. |
| `out32` | The result storage buffer holds one signed 32-bit scalar per invocation. |
| unpacked | The instruction takes two 4-component vectors, not packed 4×8-bit scalar operands. |

#### Purpose

This case checks the ordinary signed four-component 8-bit dot-product path with a result type wide enough for the selected small-range products. It isolates `OpSDotKHR` without saturation while retaining the vector-input capability path used by the wider matrix.

#### Structural Design

| Generated assembly phase | Representative specialization | Why it matters |
|--------------------------|-------------------------------|----------------|
| Capabilities and extension | `OpCapability DotProductInput4x8BitKHR`, `OpCapability DotProductKHR`, and `OpExtension "SPV_KHR_integer_dot_product"` | Declares that this module consumes four-component 8-bit vectors and uses the dot-product instruction family. |
| Bindings | LHS input at binding 0, RHS input at binding 1, output at binding 2 | Separates the two operand arrays from the scalar result array. |
| Types and strides | Signed 8-bit vector arrays plus signed 32-bit scalar output array | Makes each invocation's vector load and result store addressable by `GlobalInvocationId.x`. |
| Main body | Load ID, load LHS/RHS vectors, execute `OpSDotKHR`, store the scalar result | Encodes one independent dot product per invocation. |

The generator emits the packed sibling by changing the input capability to `DotProductInput4x8BitPackedKHR`, choosing scalar packed operand types, and passing `PackedVectorFormat4x8BitKHR` to the instruction. AccSat siblings add the input-addend binding and replace the instruction name with an `AccSat` form.

#### Source Code

The assembly is generated from C++ string fragments, so the source of truth is [`generateIntegerDotProductCode`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L354-L528), specialized by the `opsdotkhr` builder. It is intentionally not reproduced as a hand-written SPIR-V fence: the function emits type declarations and capability lines conditionally for every matrix combination.

#### Additional Info

- The 4×8-bit packed cases are only generated for `v4i8`; the loops explicitly skip packed choices for every other vector shape.
- The source emits `DotProductInputAllKHR` unless the vector is 4-wide 8-bit. It then chooses `DotProductInput4x8BitKHR` or `DotProductInput4x8BitPackedKHR` from the packing flag.
- For `v3` inputs, the host allocates an aligned four-component slot and sets component four to zero. The generated type remains a three-component vector, so the padding does not become a fourth multiplicand.

#### Parameter Variation Summary

| Parameter dimension | Assembly-level change from this representative | Evidence |
|---------------------|------------------------------------------------|----------|
| Instruction family | Replaces `OpSDotKHR` with `OpUDotKHR`, `OpSUDotKHR`, or an `AccSat` variant; signedness changes type selection. | [`generateIntegerDotProductCode`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L354-L528) |
| Packed 4×8-bit | Uses packed scalar operand types, `DotProductInput4x8BitPackedKHR`, and `PackedVectorFormat4x8BitKHR`. | [`generateIntegerDotProductCode`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L369-L377) |
| Element/result width | Adds required `Int8`/`Int16` capabilities, changes scalar/vector types and array strides, and requests the matching storage features. | [`addDotProductExtensionAndFeatures`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L198-L220) |
| Accumulation | Adds input binding 2 for the addend, shifts output to binding 3, loads the addend, and supplies it to the `AccSat` instruction. | [`generateIntegerDotProductCode`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L428-L525) |

The CTS authors the SPIR-V assembly as C++ string-template output, not reconstructed GLSL or HLSL. This page deliberately does not publish an extracted, specialized assembly fence, so it makes no claim of an `spirv-as`/`spirv-val`/`spirv-dis` generation-time gate or audit-time semantic validation; its shader discussion is source-generator analysis.

## Runtime Execution and Result Checking

- **Input generation.** Each family seeds `de::Random` from the group name. It generates 200 LHS and RHS vectors for each selected range. For a three-component vector, the fourth element of each aligned host slot is set to zero.
- **Non-accumulating reference.** [`fillDotProductOutputs`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L493-L531) groups each invocation's operands, calls the host `dotProduct` helper, and writes one expected output scalar.
- **AccSat setup.** The AccSat builders create a third input buffer. `useMaxAddend` fills it near `numeric_limits<AddendT>::max()`, while false fills it near the minimum. The input-range registrations select which of those cases runs.
- **Dispatch.** The builders attach two input buffers and one output buffer for ordinary operations, or three inputs plus one output for AccSat operations. They dispatch `IVec3(numElements, 1, 1)`, so 200 invocations each write one scalar result.
- **Result checking.** Ordinary cases use the compute harness's bytewise expected-output comparison. AccSat cases install [`compareDotProductAccSat`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L94-L183). For each addend/output slot, it splits the operands into same-sign and opposite-sign contributions, forms two `int64_t` partial dot products, and compares the saturated add only when both partial products are within the `AddendT` range. If either partial product is outside that range, the callback performs no comparison for that slot and continues; therefore an AccSat pass does not establish correctness for skipped slots.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `opsdotkhr` | Signed dot-product lowering, signed operand interpretation, vector/packed operand decoding, or ordinary output-buffer comparison is wrong. |
| `opudotkhr` | Unsigned dot-product lowering or unsigned operand interpretation is wrong, including packed 4×8-bit decoding. |
| `opsudotkhr` | The implementation mishandles mixed signedness between the signed LHS and unsigned RHS, or lowers `OpSUDotKHR` as a same-signedness operation. |
| `opsdotaccsatkhr` | Signed accumulate-and-saturate semantics, addend handling, signed range limits, or the AccSat result path is wrong. |
| `opudotaccsatkhr` | Unsigned accumulate-and-saturate semantics, addend handling, unsigned range limits, or the AccSat result path is wrong. |
| `opsudotaccsatkhr` | Mixed-signedness accumulation or saturation is wrong, especially near the selected upper and lower addend limits. |

### Cause Analysis

#### Incorrect signed, unsigned, or mixed-signedness interpretation

**Possible failure symptoms:** A non-accumulating family reports `Output doesn't match with expected`. The mismatch is limited to one signedness family or to input values with the high bit set; for example, `opsudotkhr` fails while same-signedness families pass.

**Possible implementation causes:** The generated modules use distinct `OpSDotKHR`, `OpUDotKHR`, and `OpSUDotKHR` instructions and corresponding signed/unsigned SPIR-V types. A compiler could lower one instruction with the wrong operand interpretation, or a packed/unpacked input could be decoded with the wrong signedness. The test result alone cannot distinguish compiler lowering from the host/device buffer path; source-level investigation is needed after identifying the failing matrix cells.

#### Incorrect packed-vector format or vector-layout handling

**Possible failure symptoms:** Packed 4×8-bit cases fail while their unpacked `v4i8` counterparts pass, or `v3` cases fail while `v2` and `v4` cases pass. The output mismatch appears in the ordinary buffer comparison or the AccSat callback.

**Possible implementation causes:** Packed cases pass `PackedVectorFormat4x8BitKHR` and use the packed input capability, while `v3` host data uses an aligned four-element storage slot with an explicit zero padding element. An implementation may mishandle packed byte order, packed signedness, array stride, or the three-component vector load. The source establishes those distinct assembly forms; it does not identify a driver-internal fault location.

#### Incorrect accumulation or saturation

**Possible failure symptoms:** An `AccSat` family fails for `limits`, `limits-neg`, `small-neg`, or a `nosat` variant while the corresponding non-accumulating operation passes. The callback found a mismatched saturated-add result in a slot for which both sign-separated partial products fit the output type. A passing AccSat case does not cover slots the callback skips after either partial product falls outside that range.

**Possible implementation causes:** The operation may omit the addend, clamp in the wrong direction, wrap before the final clamp, or apply signed limits to an unsigned result. `compareDotProductAccSat` separates same-sign and opposite-sign contributions and applies its host saturation rule only to the slots it compares. A mismatch establishes disagreement with that conditional oracle; it does not by itself identify instruction lowering, arithmetic hardware, or another execution path.

#### Missing or inconsistent width-dependent support

**Possible failure symptoms:** Cases requiring 8-bit or 16-bit operands fail during setup or shader execution while 32-bit cases pass. Failures can correlate with `out8`, `out16`, unpacked 8-bit input, or 16-bit input/output selections.

**Possible implementation causes:** The builder requests `shaderIntegerDotProduct` for every case and conditionally requests `shaderInt8` plus `storageBuffer8BitAccess`, or `shaderInt16` plus 16-bit storage features. A mismatch may reflect inconsistent feature advertisement, a missing capability/extension handling path, or incorrect lowering for a narrow integer storage type. The test does not use acceleration-property bits as a pass criterion.

## Case Pruning

### Requirement-based pruning

- Every case requests `VK_KHR_shader_integer_dot_product` and `shaderIntegerDotProduct` through [`addDotProductExtensionAndFeatures`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L198-L220).
- An unpacked 8-bit operand or an 8-bit output also requests `shaderInt8`, `storageBuffer8BitAccess`, and `VK_KHR_8bit_storage`.
- A 16-bit element or output requests `shaderInt16`, `storageBuffer16BitAccess`, `uniformAndStorageBuffer16BitAccess`, and `VK_KHR_16bit_storage`.
- The legacy page records this source as non-VulkanSC only; its registrations are not available in VulkanSC builds.

### Design-based pruning

- Packed cases are skipped unless the selected vector is exactly 4-wide with 8-bit elements.
- The source states that 64-bit integer results are not covered. The registered output-width matrix therefore stops at `out32`.
- The test uses 200 randomized vectors for every generated case rather than exhaustively enumerating the integer domain.
- The `nosat` and `small-nosat` registrations do not remove the AccSat instruction. They select ranges and addends intended to avoid saturation, which distinguishes an ordinary accumulated result from a clamped one.

## Key Takeaways

- This source implements six direct instruction families: signed, unsigned, and mixed-signedness dot products, each with an accumulating saturating counterpart.
- The generated leaf name encodes the behavior-relevant matrix: input range, packed/unpacked representation, LHS/RHS signedness, vector shape, element width, and result width.
- The source generates SPIR-V assembly directly. It selects the instruction, capabilities, buffer types, bindings, and optional packed-vector operand from the same parameter record used to name each case.
- Ordinary cases byte-compare against host-generated dot products. AccSat cases use a separate conditional saturation-aware callback: it can establish a mismatch for compared slots, but skips slots whose sign-separated partial products are outside the output range.
- A failing family localizes the tested instruction form and parameter combination, but it does not by itself identify whether the defect is in feature reporting, shader compilation, arithmetic execution, or host/device buffer infrastructure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `compareDotProductAccSat` | [`vktSpvAsmIntegerDotProductTests.cpp#L94-L183](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L94-L183) | Conditional saturation-aware host verifier used by all AccSat families; it skips slots whose sign-separated partial products are outside the output range. |
| `addDotProductExtensionAndFeatures` | [`vktSpvAsmIntegerDotProductTests.cpp#L198-L220`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L198-L220) | Requests the core feature and width-dependent storage prerequisites. |
| `dotProductPacking` / `dotProductVector*` | [`vktSpvAsmIntegerDotProductTests.cpp#L222-L244`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L222-L244) | Defines packed/signedness combinations and 8/16/32-bit vector shapes. |
| `generateIntegerDotProductCode` | [`vktSpvAsmIntegerDotProductTests.cpp#L354-L528`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L354-L528) | Generates the SPIR-V assembly and selects each instruction form. |
| `fillDotProductOutputs` / `getDotProductTestName` | [`vktSpvAsmIntegerDotProductTests.cpp#L493-L539`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L493-L539) | Builds ordinary references and exact registered leaf names. |
| `createOpSDotKHRComputeGroup` | [`vktSpvAsmIntegerDotProductTests.cpp#L1175-L1190`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1175-L1190) | Registers signed non-accumulating ranges. |
| `createOpUDotKHRComputeGroup` / `createOpSUDotKHRComputeGroup` | [`vktSpvAsmIntegerDotProductTests.cpp#L1192-L1227`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1192-L1227) | Registers unsigned and mixed-signedness non-accumulating ranges. |
| `createOpSDotAccSatKHRComputeGroup` | [`vktSpvAsmIntegerDotProductTests.cpp#L1229-L1256`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1229-L1256) | Registers signed saturation ranges. |
| `createOpUDotAccSatKHRComputeGroup` / `createOpSUDotAccSatKHRComputeGroup` | [`vktSpvAsmIntegerDotProductTests.cpp#L1258-L1320`](../../../modules/vulkan/spirv_assembly/vktSpvAsmIntegerDotProductTests.cpp#L1258-L1320) | Registers unsigned and mixed-signedness saturation ranges. |
| Vulkan feature contract | [`features.adoc#L6695-L6728`](../../../../vulkan-docs/src/chapters/features.adoc#L6695-L6728) | Defines `shaderIntegerDotProduct` and the permitted dot-product capabilities. |
| Mustpass leaf population | [`spirv-assembly.txt#L8152-L9624`](../../../mustpass/main/vk-default/spirv-assembly.txt#L8152-L9624) | Contains the 1,392 executable leaves for these six families. |
