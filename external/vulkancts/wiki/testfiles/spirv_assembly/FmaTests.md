## Overview

**Core question:** Does `OpFmaKHR` produce an allowed correctly rounded fused `a * b + c` result for the selected floating-point width, vector shape, float-control contract, and input record?

- This page documents the `opfma` test family implemented by [`vktSpvAsmFmaTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L54-L1238). It exercises `VK_KHR_shader_fma` through CTS-authored compute SPIR-V that emits `OpFmaKHR`.
- The family registers 324 compute tests: three widths, four scalar/vector shapes, three rounding choices, three denorm choices, and three input modes. The Vulkan mustpass file lists the same 324 `dEQP-VK.spirv_assembly.instruction.compute.opfma.*` paths ([entries](../../../mustpass/main/vk-default/spirv-assembly.txt#L7620-L7943)).
- Each case loads three operands from storage buffers, executes one fused multiply-add per scalar or vector record, stores the result, and compares it with a CPU reference set that accounts for the requested rounding, denorm, and signed-zero rules.

## Background Knowledge

- A fused multiply-add performs `a * b + c` as one floating-point operation. Its single final rounding can differ from separately rounded multiplication followed by addition. Cancellation inputs such as `a * b - (a * b)` make that difference observable.
- `SPV_KHR_float_controls` lets a module request rounding, denorm, and signed-zero/infinity/NaN behavior for a selected floating-point width. This generator emits the matching SPIR-V capabilities/execution modes, while the CTS support check requires the corresponding Vulkan float-control extension and properties.
- A denormal (subnormal) value lies between zero and the smallest normal magnitude. A device may preserve such inputs/results or flush them to signed zero when the mode permits it, so the CTS verifier must accept the outcomes allowed by the selected mode.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.opfma
├── fp16
├── fp32
└── fp64
```

Each width intermediate node contains `scalar`, `vec2`, `vec3`, and `vec4`. Each shape contains the rounding intermediate nodes `rtz`, `rte`, and `undef`; each of those contains `denorm_preserve`, `denorm_flush`, and `denorm_none`; every final node registers `random`, `directed`, and `float_controls`. `denorm_none` is the registered name for `DENORM_UNDEF` ([name mapping](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L54-L126), [registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L1191-L1235)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Floating-point width | `fp16`, `fp32`, `fp64` | Chooses `OpTypeFloat 16`, `32`, or `64`, the FMA feature bit, the host reference type, and the relevant float-control properties. | [spec construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L939-L1000) |
| Operand shape | `scalar`, `vec2`, `vec3`, `vec4` | Chooses one scalar operation or one vector `OpFmaKHR` with 2, 3, or 4 components. | [assembly specialization](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L228-L295), [registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L1203-L1206) |
| Rounding mode | `rtz`, `rte`, `undef` | Requests `RoundingModeRTZ`, `RoundingModeRTE`, or leaves the mode unspecified. The verifier accepts toward-positive-infinity and toward-negative-infinity references for `undef`. | [mode mapping](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L54-L90), [reference selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L423-L489) |
| Denorm mode | `denorm_preserve`, `denorm_flush`, `denorm_none` | Requests preserve or flush-to-zero behavior, or leaves denorm behavior unspecified. The verifier enumerates the permitted flushed/non-flushed input and result outcomes. | [mode mapping](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L92-L126), [allowed values](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L366-L489) |
| Input mode | `random`, `directed`, `float_controls` | `random` supplies 768 deterministic random elements per operand buffer. `directed` uses signed special values and cancellation cases. `float_controls` uses the directed data while requesting `SignedZeroInfNanPreserve`. | [buffer selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L901-L931), [registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L1218-L1223) |

The full matrix is `3 × 4 × 3 × 3 × 3 = 324` registered test cases. Width is the primary behavioral axis because it changes the arithmetic representation, the requested FMA feature, and the optional-width support requirements. The other dimensions determine the execution-mode contract and the data path used to expose incorrect behavior.

## Behavior Parameters

### `fp16` - half-precision FMA

`fp16` emits `OpTypeFloat 16`, requests `shaderFmaFloat16` and `shaderFloat16`, and uses the `deFloat16` reference path. Its directed values include boundary, denormal, infinity, and NaN encodings, so the verifier covers half-precision rounding and denorm rules ([half special values](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L599-L646), [feature setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L981-L999)).

### `fp32` - single-precision FMA

`fp32` emits `OpTypeFloat 32` and requests `shaderFmaFloat32`. It is the baseline representation: it does not require the extra `shaderFloat16` or `shaderFloat64` feature request made by the narrower and wider variants. The float reference compares raw IEEE-754 bits except that two NaN values are accepted as equivalent ([comparison helper](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L303-L316)).

### `fp64` - double-precision FMA

`fp64` emits `OpTypeFloat 64`, requests `shaderFmaFloat64` and core `shaderFloat64`, and calculates expected results with `double`. The directed list reaches double-precision normal, subnormal, infinity, and NaN boundaries ([double special values](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L697-L736), [feature setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L981-L999)).

## Shader Analysis

The representative path `dEQP-VK.spirv_assembly.instruction.compute.opfma.fp32.scalar.rte.denorm_preserve.float_controls` shows the common compute structure with explicit float controls. The template inserts the selected width, vector size, rounding mode, denorm mode, and signed-zero/infinity/NaN preservation flag before returning the assembly string ([`getFmaCode`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L133-L300)).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.opfma.fp32.scalar.rte.denorm_preserve.float_controls
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `fp32` | The operand and result type is `%dat = OpTypeFloat 32`; each runtime-array element has stride 4. |
| `scalar` | Each invocation loads one value from each of the three input buffers and stores one result. |
| `rte` | The module declares `RoundingModeRTE` and requests round-to-nearest-even for 32-bit operations. |
| `denorm_preserve` | The module declares `DenormPreserve 32`; for an underflowing result, the verifier does not add the permitted flushed-zero alternatives. |
| `float_controls` | The module declares `SignedZeroInfNanPreserve 32` and the test requests the matching Vulkan property. |

#### Purpose

Each invocation calculates one `OpFmaKHR` result from buffers `a`, `b`, and `c`. The path checks a fused single-precision operation under an explicit round-to-nearest-even, denorm-preserving, and signed-zero/infinity/NaN-preserving contract.

#### Structural Design

| Phase | SPIR-V mechanism | Role |
|-------|------------------|------|
| Invocation index | `gl_GlobalInvocationID.x`, plus the scaled `y` component | Selects a logical vector record. The `y * 65536 + x` form supports directed input sets larger than one dispatch row. |
| Input | Three `OpAccessChain` plus `OpLoad` sequences | Reads one scalar from descriptor-set 0 bindings `0`, `1`, and `2`. |
| FMA | `OpFmaKHR %dat %val1 %val2 %val3` | Performs the tested fused expression. |
| Output | `OpAccessChain` plus `OpStore` | Writes the scalar result to descriptor-set 0 binding `3`. |

#### Source Code

The following CTS-authored specialization is reconstructed directly from the string pieces in `getFmaCode()` for the selected path. It was assembled, validated, and disassembled with `spirv-as`, `spirv-val`, and `spirv-dis` using the SPIR-V 1.0 target environment. The `spirv_assembly` page publishes the source assembly once, so it does not duplicate the disassembly.

<details>
<summary>Click to expand CTS-authored SPIR-V assembly for <code>fp32.scalar.rte.denorm_preserve.float_controls</code></summary>

```llvm
OpCapability Shader
OpCapability FMAKHR
OpCapability RoundingModeRTE
OpCapability DenormPreserve
OpCapability SignedZeroInfNanPreserve
OpExtension "SPV_KHR_fma"
OpExtension "SPV_KHR_float_controls"
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %main "main" %id
OpExecutionMode %main LocalSize 1 1 1
OpExecutionMode %main RoundingModeRTE 32
OpExecutionMode %main DenormPreserve 32
OpExecutionMode %main SignedZeroInfNanPreserve 32
OpName %main "main"
OpName %id   "gl_GlobalInvocationID"
OpDecorate %id BuiltIn GlobalInvocationId
OpDecorate %buf BufferBlock
OpDecorate %indata1 DescriptorSet 0
OpDecorate %indata1 Binding 0
OpDecorate %indata2 DescriptorSet 0
OpDecorate %indata2 Binding 1
OpDecorate %indata3 DescriptorSet 0
OpDecorate %indata3 Binding 2
OpDecorate %outdata DescriptorSet 0
OpDecorate %outdata Binding 3
OpDecorate %datarr ArrayStride 4
OpMemberDecorate %buf 0 Offset 0
%void      = OpTypeVoid
%voidf     = OpTypeFunction %void
%u32       = OpTypeInt 32 0
%i32       = OpTypeInt 32 1
%uvec3     = OpTypeVector %u32 3
%uvec3ptr  = OpTypePointer Input %uvec3
%dat       = OpTypeFloat 32
%datptr    = OpTypePointer Uniform %dat
%datarr    = OpTypeRuntimeArray %dat
%vec2      = OpTypeVector %dat 2
%vec3      = OpTypeVector %dat 3
%vec4      = OpTypeVector %dat 4
%buf       = OpTypeStruct %datarr
%bufptr    = OpTypePointer Uniform %buf
%indata1   = OpVariable %bufptr Uniform
%indata2   = OpVariable %bufptr Uniform
%indata3   = OpVariable %bufptr Uniform
%outdata   = OpVariable %bufptr Uniform
%id        = OpVariable %uvec3ptr Input
%zero      = OpConstant %i32 0
%one       = OpConstant %i32 1
%two       = OpConstant %i32 2
%three     = OpConstant %i32 3
%stride    = OpConstant %u32 65536
%vec_sz    = OpConstant %i32 1
%main      = OpFunction %void None %voidf
%label     = OpLabel
%idval     = OpLoad %uvec3 %id
%x         = OpCompositeExtract %u32 %idval 0
%y         = OpCompositeExtract %u32 %idval 1
%scale_y   = OpIMul %u32 %y %stride
%vec_idx   = OpIAdd %u32 %scale_y %x
%idx       = OpIMul %u32 %vec_idx %vec_sz
%loc1      = OpAccessChain %datptr %indata1 %zero %idx
%loc2      = OpAccessChain %datptr %indata2 %zero %idx
%loc3      = OpAccessChain %datptr %indata3 %zero %idx
%val1      = OpLoad %dat %loc1
%val2      = OpLoad %dat %loc2
%val3      = OpLoad %dat %loc3
%res       = OpFmaKHR %dat %val1 %val2 %val3
%outloc    = OpAccessChain %datptr %outdata %zero %idx
             OpStore %outloc %res
             OpReturn
             OpFunctionEnd
```

</details>

#### Additional Info

- `getComputeAsmShaderPreamble()` supplies `OpCapability Shader`, the logical GLSL450 memory model, the compute entry point, and `LocalSize 1 1 1`; `getFmaCode()` adds FMA and float-control capabilities, the extension declarations, and the remaining instructions ([preamble helper](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L65-L73), [specialization builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L133-L226)).
- The buffers use the legacy `BufferBlock`/`Uniform` representation. The generated `ComputeShaderSpec` defaults to SPIR-V 1.0, which is why the validation target for this source assembly is SPIR-V 1.0 ([default](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.hpp#L675-L720)).
- The scalar and vector paths both use exactly one `OpFmaKHR`. Vector paths load individual scalar components, construct `%vec2`, `%vec3`, or `%vec4`, execute the vector operation, then extract and store each component ([vector path](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L241-L295)).

#### Parameter Variation Summary

| Parameter dimension | Assembly-level variation from this shader | Evidence |
|---------------------|-------------------------------------------|----------|
| Width | Replaces `%dat` with a 16-, 32-, or 64-bit floating-point type; 16-bit and 64-bit variants add `Float16` or `Float64` capability. | [type/capability generation](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L154-L201) |
| Shape | Replaces the scalar load/FMA/store sequence with vector construction, one vector `OpFmaKHR`, component extraction, and one store per component. | [shape specialization](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L228-L295) |
| Rounding | Adds `RoundingModeRTZ` or `RoundingModeRTE` capability and execution mode. `undef` emits neither. | [rounding selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L138-L146) |
| Denorm | Adds `DenormPreserve` or `DenormFlushToZero` capability and execution mode. `denorm_none` emits neither. | [denorm selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L148-L152) |
| Input mode | Only `float_controls` adds `SignedZeroInfNanPreserve`; it reuses directed input generation. | [flag generation](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L154-L158), [case creation](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L1218-L1223) |

## Runtime Execution and Result Checking

- `createFmaTestSpec()` builds the selected assembly, requests `shaderFmaFloat16`, `shaderFmaFloat32`, or `shaderFmaFloat64`, and adds `shaderFloat16` for `fp16` or `shaderFloat64` for `fp64` ([spec setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L975-L1012)).
- `FillFloatControlsProps()` marks only the selected width's requested rounding, denorm, and signed-zero/infinity/NaN properties. `SpvAsmComputeShaderCase::checkSupport()` rejects the case as not supported when the float-controls extension or any marked property is unavailable ([property setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L939-L973), [support check](../../../modules/vulkan/spirv_assembly/vktSpvAsmUtils.cpp#L327-L399), [case gate](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderCase.cpp#L446-L507)).
- The `random` mode creates three reproducible 768-element buffers. The directed modes enumerate signed special values across the three operands and add cancellation records. The helper pads cancellation records to a vector-width-compatible count and, when needed, a valid two-dimensional dispatch size ([input creation](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L787-L931)).
- The test dispatches enough workgroups to cover every vector record. It uses at most 65,536 x-workgroups and increases y as needed; the shader reconstructs the record index from `GlobalInvocationID.x` and `.y` ([dispatch sizing](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L1002-L1010), [shader indexing](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L219-L226)).
- `verifyResult<T>()` regenerates the three input buffers, computes every allowed CPU reference value, and accepts a result if it matches any of them. It reports at most 16 mismatches with hexadecimal floating-point operands and expected values ([verification](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L505-L569)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fp16` | Incorrect half-precision `OpFmaKHR` arithmetic or 16-bit type/storage handling. Unsupported `shaderFmaFloat16` or `shaderFloat16` is a not-supported outcome, not an output mismatch. |
| `fp32` | Incorrect single-precision `OpFmaKHR` arithmetic or, for an explicit-mode leaf, 32-bit float-control application. |
| `fp64` | Incorrect double-precision `OpFmaKHR` arithmetic or 64-bit type/storage handling. Unsupported `shaderFmaFloat64` or `shaderFloat64` is a not-supported outcome, not an output mismatch. |
| Any `rtz` or `rte` path | The mismatch is consistent with ignoring or misapplying the requested rounding mode, but can also arise in arithmetic, data movement, or verification. |
| Any `denorm_preserve` or `denorm_flush` path | The mismatch is consistent with mishandling the selected denorm contract or a subnormal input/result, but is not a unique fault location. |
| Any `float_controls` path | The mismatch is consistent with failure to preserve signed zero, infinity, or NaN under the requested property and SPIR-V execution mode; the same output oracle also covers ordinary FMA correctness. |
| `directed` or `float_controls` path with cancellation records | The mismatch is consistent with evaluation that differs from fused FMA semantics, but does not by itself identify the lowering stage. |

### Cause Analysis

#### Wrong fused result or vector component result

**Possible failure symptoms:** `verifyResult<T>()` finds an output that matches none of its permitted references and logs `fma(a, b, c)`, the returned value, the expected value or set, and the element index. A failure restricted to `vec2`, `vec3`, or `vec4` while scalar passes is diagnostic evidence for component construction, extraction, indexing, or storage; it does not exclude the shared arithmetic or runtime path.

**Possible implementation causes:** the backend may lower `OpFmaKHR` as separate multiply and add operations, choose the wrong operand/component, or write a vector component at the wrong runtime-array location. The source does not identify a driver layer, so an investigation should compare the affected width and shape with the scalar reference path before assigning a specific implementation location.

#### Wrong rounding or denorm treatment

**Possible failure symptoms:** a mismatch appears only for a specified `rtz`, `rte`, `denorm_preserve`, or `denorm_flush` group, especially near a rounding boundary or for a subnormal operand/result. A preserved-denorm case rejects a flushed zero, while a mode that permits flushing accepts the explicitly generated zero alternatives.

**Possible implementation causes:** the device may ignore `RoundingModeRTZ`, `RoundingModeRTE`, `DenormPreserve`, or `DenormFlushToZero`, or advertise the matching Vulkan property but apply a different execution contract. The verifier deliberately includes all permitted input-flush combinations when preservation is not required, so a failure after that expansion indicates an outcome outside the tested contract ([reference construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L366-L489)).

#### Signed zero, infinity, or NaN preservation failure

**Possible failure symptoms:** a `float_controls` case mismatches on the sign of zero, an infinity, or a NaN-related result. In ordinary `random` and `directed` modes, the verifier skips an element if an input or allowed reference involves infinity or NaN because no preservation contract was requested.

**Possible implementation causes:** the implementation may not honor `SignedZeroInfNanPreserve` despite the selected width's requested property, capability, and execution mode. Without that mode, the verifier skips an element whose input or allowed reference is infinity or NaN, and accepts either zero sign for a zero result; it does not permit arbitrary results for every signed-zero case. A `float_controls` mismatch is evidence for the requested preservation path but does not exclude ordinary FMA, data-layout, or execution failures ([special-case check](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L524-L535)).

#### Incorrect cancellation behavior

**Possible failure symptoms:** directed cancellation records fail while broad random coverage passes. These records use operands shaped as `a`, `b`, and `-(a*b)`, where a fused operation can retain the multiplication rounding error instead of producing the separately rounded result.

**Possible implementation causes:** the compiler or hardware path may replace FMA with independently rounded multiplication and addition, or use an inaccurate width-specific FMA lowering. The source builds the cancellation operands from matching deterministic random streams so the three independent input buffers still form the intended triples ([cancellation generation](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L870-L895)).

## Case Pruning

### Requirement-based pruning

- Every leaf requests the matching `extFma.shaderFmaFloat16`, `shaderFmaFloat32`, or `shaderFmaFloat64` feature. `fp16` also requests `extFloat16Int8.shaderFloat16`; `fp64` requests core `shaderFloat64` ([feature requests](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L981-L992)).
- A case with explicit `rtz`, `rte`, `denorm_preserve`, `denorm_flush`, or `float_controls` marks the corresponding width-specific float-controls property. The shared support gate additionally requires `VK_KHR_shader_float_controls` whenever any such property is marked, then reports a missing extension or property as not supported ([property setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L939-L973), [float-controls support predicate](../../../modules/vulkan/spirv_assembly/vktSpvAsmUtils.cpp#L327-L399)).
- The `opfma` group is registered only in the non-VulkanSC compute block ([parent registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21361-L21449)).

### Design-based pruning

No parameter combinations are removed from the registered 3 x 4 x 3 x 3 x 3 matrix. `undef` and `denorm_none` are deliberate unspecified-mode variants rather than omissions: the generator leaves the corresponding execution mode out and the reference checker broadens the acceptable result set accordingly.

## Key Takeaways

- `opfma` covers 324 `OpFmaKHR` compute cases across three widths, four shapes, three rounding choices, three denorm choices, and three input modes.
- The directed data does more than sample ordinary values: it covers signed special values and deliberately constructed cancellation records that distinguish fused evaluation from separately rounded multiply-add behavior.
- The CPU verifier models permitted variation instead of assuming one universal answer. It expands valid references for unspecified rounding and permitted denorm flushing, while `float_controls` requires preservation-sensitive checks.
- Width, shape, float-control mode, and input mode narrow diagnosis, but this single output oracle does not uniquely localize a fault among arithmetic, storage/layout, mode application, and preservation behavior.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createOpFmaComputeGroup` | [`vktSpvAsmFmaTests.cpp#L1191-L1238`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L1191-L1238) | Registers the complete `opfma` hierarchy and its 324 leaves. |
| `getFmaCode` | [`vktSpvAsmFmaTests.cpp#L133-L300`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L133-L300) | Generates the parameterized CTS-authored SPIR-V assembly, including `OpFmaKHR`. |
| `getRefValues` | [`vktSpvAsmFmaTests.cpp#L366-L489`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L366-L489) | Produces the allowed CPU reference set for rounding, denorm, and signed-zero behavior. |
| `verifyResult` | [`vktSpvAsmFmaTests.cpp#L505-L569`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L505-L569) | Compares output elements with allowed references and emits mismatch diagnostics. |
| `DirectedBuffer` | [`vktSpvAsmFmaTests.cpp#L787-L899`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L787-L899) | Generates special-value cross products and FMA cancellation records. |
| `createFmaTestSpec` | [`vktSpvAsmFmaTests.cpp#L975-L1186`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFmaTests.cpp#L975-L1186) | Selects input buffers, feature/property requests, dispatch dimensions, and the specialized verifier callback. |
| Mustpass entries | [`spirv-assembly.txt#L7620-L7943`](../../../mustpass/main/vk-default/spirv-assembly.txt#L7620-L7943) | Lists the 324 `dEQP-VK.spirv_assembly.instruction.compute.opfma.*` test paths. |
