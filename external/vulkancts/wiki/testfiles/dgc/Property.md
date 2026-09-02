## Overview

**Core question:** Do the advertised `VK_NV_device_generated_commands` properties support the limits and offsets that the implementation reports?

- [`vktDGCPropertyTests.cpp`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L53-L1271) implements the `dgc.nv.misc.properties` test family.
- The family checks `valid_limits`, command stream and token limits, command buffer offset alignment, and sequence count or index buffer alignment.
- The executable cases use generated compute commands that write push constant values into a host-visible storage buffer, then compare the results on the host.
- This page explains the registered values, support gates, generated compute shader, runtime checks, and failure meaning.

## Background Knowledge

- Device-generated commands use a command layout to interpret indirect command data. A layout can read push constant tokens and dispatch tokens from one or more indirect command streams.
- A sequence count buffer limits how many sequences execute, while a sequence index buffer selects the sequence data used for each execution. Their offsets are properties of the device-generated-command interface and must satisfy the reported alignment requirements.
- A host-visible buffer can carry indirect command data or receive shader output. The test flushes host writes before submission, waits for the queue, invalidates the output allocation, and then reads the result on the host.
- A support check that raises `NotSupportedError` means the case cannot run with the current extension, feature, or alignment support. A completed case that returns a failed `TestStatus` means the device ran the test but produced an unexpected result.

## Registration Hierarchy

```text
dgc.nv.misc.properties
├── maxIndirectCommandsStreamCount
├── maxIndirectCommandsStreamStrideRun
├── maxIndirectCommandsTokenCount
├── maxIndirectCommandsTokenOffset
├── minIndirectCommandsBufferOffsetAlignment_offset_256
├── minIndirectCommandsBufferOffsetAlignment_offset_4
├── minIndirectCommandsBufferOffsetAlignment_offset_8
├── minSequencesCountBufferOffsetAlignment
├── minSequencesIndexBufferOffsetAlignment
└── valid_limits
```

The root is attached below `dgc.nv.misc` by [`createTests()`](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L75-L93). The ten direct children are registered by [`createDGCPropertyTests()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1232-L1268), and the same paths are listed in the Vulkan default mustpass file [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L4578-L4587).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Advertised property checked by `valid_limits` | `maxGraphicsShaderGroupCount`, `maxIndirectSequenceCount`, `maxIndirectCommandsTokenCount`, `maxIndirectCommandsStreamCount`, `maxIndirectCommandsTokenOffset`, `maxIndirectCommandsStreamStride`, `minSequencesCountBufferOffsetAlignment`, `minSequencesIndexBufferOffsetAlignment`, `minIndirectCommandsBufferOffsetAlignment` | Verifies that reported values meet the ranges or upper bounds required by this test. | [`validLimits()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1193-L1227) |
| Command limit family | `maxIndirectCommandsTokenCount`, `maxIndirectCommandsStreamCount`, `maxIndirectCommandsTokenOffset`, `maxIndirectCommandsStreamStrideRun` | Selects which command stream or layout limit is exercised by the generated compute dispatch. | [`createDGCPropertyTests()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1238-L1245) |
| Indirect command stream offset | `4`, `8`, `256` in `minIndirectCommandsBufferOffsetAlignment_offset_4`, `minIndirectCommandsBufferOffsetAlignment_offset_8`, and `minIndirectCommandsBufferOffsetAlignment_offset_256` | Places the indirect command stream at the requested byte offset after the support check confirms that the offset is valid for `minIndirectCommandsBufferOffsetAlignment`. | [`createDGCPropertyTests()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1247-L1253), [`minIndirectCommandsBufferOffsetAlignmentRun()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L818-L952) |
| Sequence metadata source | `minSequencesCountBufferOffsetAlignment`, `minSequencesIndexBufferOffsetAlignment` | Chooses whether the test supplies a count buffer or an index buffer at the device-reported offset. | [`createDGCPropertyTests()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1256-L1268), [`minSequencesOffsetAlignmentsRun()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L955-L1191) |
| Sequence data volume | `totalValueCount = 512`; `countInBuffer = 256` for the count-buffer case and `512` for the index-buffer case | Provides enough command data to check both executed values and the untouched half of the output buffer when the count buffer reduces execution. | [`minSequencesOffsetAlignmentsRun()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L967-L990) |
| Bounded stress values | `kMaxTokens = 1024`, `kMaxValue = 1024`, `kHardMax = 1024u * 1024u` | Caps allocations and generated command counts while still exercising a reported limit when that limit is smaller than the cap. | [`maxIndirectCommandsTokenCountRun()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L163-L181), [`maxIndirectCommandsStreamCountRun()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L311-L333), [`maxIndirectCommandsTokenOffsetRun()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L522-L540), [`maxIndirectCommandsStreamStrideRun()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L689-L713) |

## Behavior Parameters

The primary behavioral axis is the registered test family. Each direct child selects a different property or alignment mechanism while using the same DGC compute support path where applicable.

### `valid_limits` | advertised property ranges

`valid_limits` performs no generated dispatch. It queries `context.getDeviceGeneratedCommandsProperties()` and checks the required minimums for command counts, token offset, and stream stride. It also accepts `maxGraphicsShaderGroupCount == 0`, which the source treats as the compute-only signal, and bounds each tested alignment property by `256`.

### `maxIndirectCommandsTokenCount` | number of tokens

The test chooses the smaller of the reported `maxIndirectCommandsTokenCount` and `1024`, then creates `chosenLimit - 1` push constant tokens followed by one dispatch token. The compute shader stores the last push constant value, so successful execution proves that the command layout accepted the selected token count and executed the final dispatch.

### `maxIndirectCommandsStreamCount` | number of streams

The test chooses the smaller of `maxIndirectCommandsStreamCount`, `maxIndirectCommandsTokenCount`, and `1024`. It puts one push constant token in each stream and a dispatch token in the final stream. The shader must receive the last push constant value through the separate streams.

### `maxIndirectCommandsTokenOffset` | token byte offset

The test places a push constant token after the indirect dispatch arguments. It selects an aligned offset no larger than `maxIndirectCommandsTokenOffset`, `maxIndirectCommandsStreamStride - sizeof(uint32_t)`, and `1024u * 1024u`. The dispatch reads the arguments at offset zero, while the push constant read occurs at the selected token offset.

### `maxIndirectCommandsStreamStrideRun` | sequence stride

The test uses two push constant records, `{0u, 555u}` and `{1u, 777u}`, followed by a dispatch command in each sequence. It rounds the smaller of `maxIndirectCommandsStreamStride` and `1024u * 1024u` down to a multiple of four and assigns that value as the stream stride. The shader writes each record's value to the output index from the same record.

### `minIndirectCommandsBufferOffsetAlignment_offset_256` | stream offset 256

The test writes a push constant and a `{1u, 1u, 1u}` dispatch command after `256` bytes of filler, then passes `256` as `VkIndirectCommandsStreamNV::offset`. The output must contain `777`.

### `minIndirectCommandsBufferOffsetAlignment_offset_4` | stream offset 4

This case uses the same push constant and dispatch sequence with a four-byte stream offset. `checkBufferOffsetAlignmentSupport()` rejects the case if the requested offset is not a multiple of the reported `minIndirectCommandsBufferOffsetAlignment`.

### `minIndirectCommandsBufferOffsetAlignment_offset_8` | stream offset 8

This case repeats the offset test with eight bytes of filler before the push constant and dispatch command. The shader result remains `777`; only the indirect stream placement changes.

### `minSequencesCountBufferOffsetAlignment` | count buffer offset

The test creates `512` push constant and dispatch records but writes `256` to a count buffer at `minSequencesCountBufferOffsetAlignment`. The first `256` output entries must contain `(i + 1u) * 1000u`; the remaining entries must stay zero because the count buffer limits execution.

### `minSequencesIndexBufferOffsetAlignment` | index buffer offset

The test creates `512` records and a shuffled index array generated with seed `1707306954u`. It places the index array at `minSequencesIndexBufferOffsetAlignment` and checks that every output entry receives the value associated with its selected record.

## Shader Analysis

The implementation generates a compute shader for every case that uses `addFunctionCaseWithPrograms()`. The shader is part of the tested data path, so this page includes one representative walkthrough. The selected case uses the indexed push constant form shared by `maxIndirectCommandsStreamStrideRun` and the sequence alignment cases.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.nv.misc.properties.maxIndirectCommandsStreamStrideRun
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `maxIndirectCommandsStreamStrideRun` | Selects the two-field push constant shader generated by [`storePushConstantWithIndexProgram()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L96-L104). |
| Push constants `{0u, 555u}` and `{1u, 777u}` | The host writes one record per sequence. The shader uses `index` as the output position and `value` as the stored value. | 
| `maxIndirectCommandsStreamStride` | The host sets the command layout stride to `de::roundDown(std::min(1024u * 1024u, maxIndirectCommandsStreamStride), sizeof(uint32_t))`. | 

#### Purpose

This shader checks that a generated command sequence can read both fields of a push constant record and write the value to the indexed position in a storage buffer. The host later compares the two output entries with `555` and `777`.

#### Structural Design

| Shader phase | Operation | Result |
|--------------|-----------|--------|
| Interface setup | Declare a runtime `uint` array at descriptor set `0`, binding `0`, and a two-field push constant block. | The shader can write one result for each generated sequence. |
| Generated command input | The DGC layout supplies `index` and `value` through a push constant token. | The selected stream stride determines where the next sequence begins. |
| Device write | Execute `outputBuffer.values[pc.index] = pc.value`. | Each sequence writes its record value to its indexed slot. |
| Host check | Invalidate the output allocation and compare it with the original `pcValues` array. | A mismatch fails the test. |

#### Shader Code

```glsl
#version 460
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
/// The storage buffer receives one value at the index selected by the generated command.
layout (set=0, binding=0, std430) buffer OutputBlock { uint values[]; } outputBuffer;
/// The generated push constant token supplies the output index and value for this sequence.
layout (push_constant, std430) uniform PushConstantBlock { uint index; uint value; } pc;
void main (void) { outputBuffer.values[pc.index] = pc.value; }
```

#### Additional Info

- The source uses the same generated shader for `minSequencesCountBufferOffsetAlignment` and `minSequencesIndexBufferOffsetAlignment`; those cases change the command metadata buffers and host-side selection, not the shader text.
- The source-generated shader uses `#version 460`, a one-by-one-by-one compute workgroup, one storage-buffer binding, and a two-`uint` push constant block.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `maxIndirectCommandsStreamStrideRun` | Uses the indexed push constant generator and writes `pc.value` at `pc.index`. | [`storePushConstantWithIndexProgram()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L96-L104) |
| `minSequencesCountBufferOffsetAlignment` and `minSequencesIndexBufferOffsetAlignment` | Reuse the same shader generator. The count or index buffer changes which sequences execute or which records are selected, while the shader interface stays fixed. | [`storePushConstantWithIndexAlignmentProgram()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L107-L109), [`minSequencesOffsetAlignmentsRun()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1073-L1129) |
| `maxIndirectCommandsTokenCount`, `maxIndirectCommandsStreamCount`, `maxIndirectCommandsTokenOffset`, and `minIndirectCommandsBufferOffsetAlignment_offset_*` | Use the scalar push constant generator, whose shader writes `pc.value` to one output element. | [`storePushConstantProgram()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L79-L88), [`storePushConstantProgramWithOffset()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L90-L93) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 27
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %OutputBlock "OutputBlock"
               OpMemberName %OutputBlock 0 "values"
               OpName %outputBuffer "outputBuffer"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "index"
               OpMemberName %PushConstantBlock 1 "value"
               OpName %pc "pc"
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %OutputBlock BufferBlock
               OpMemberDecorate %OutputBlock 0 Offset 0
               OpDecorate %outputBuffer Binding 0
               OpDecorate %outputBuffer DescriptorSet 0
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpMemberDecorate %PushConstantBlock 1 Offset 4
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
%OutputBlock = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_OutputBlock = OpTypePointer Uniform %OutputBlock
%outputBuffer = OpVariable %_ptr_Uniform_OutputBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%PushConstantBlock = OpTypeStruct %uint %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
      %int_1 = OpConstant %int 1
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %17 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %18 = OpLoad %uint %17
         %20 = OpAccessChain %_ptr_PushConstant_uint %pc %int_1
         %21 = OpLoad %uint %20
         %23 = OpAccessChain %_ptr_Uniform_uint %outputBuffer %int_0 %18
               OpStore %23 %21
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The generated-command cases create a host-visible storage buffer for shader output, initialize it, build a descriptor set with that buffer at binding `0`, and create a compute pipeline from the generated `comp` shader.
- Each case creates an `IndirectCommandsLayoutNV`, a host-visible indirect command buffer, and a preprocess buffer. The command buffer binds the descriptor set and compute pipeline, calls `cmdExecuteGeneratedCommandsNV`, inserts a shader-write to host-read barrier, submits, and waits.
- `maxIndirectCommandsTokenCount` creates `chosenLimit - 1` push constant tokens and a dispatch token. It expects the output value to equal `pcCmdsCount`.
- `maxIndirectCommandsStreamCount` places one push constant token in each stream and expects the output value to equal `pcCmdsCount`.
- `maxIndirectCommandsTokenOffset` stores `{1u, 1u, 1u}` dispatch arguments at stream offset zero and `777u` at the selected push constant offset. It expects `777u` in the output buffer.
- `maxIndirectCommandsStreamStrideRun` executes two sequences. It expects output index `0` to equal `555u` and output index `1` to equal `777u`.
- Each `minIndirectCommandsBufferOffsetAlignment_offset_*` case passes the registered byte offset in `makeIndirectCommandsStreamNV()` and expects `777u`.
- `minSequencesCountBufferOffsetAlignment` executes `256` of `512` prepared sequences and expects the other `256` output entries to remain zero.
- `minSequencesIndexBufferOffsetAlignment` shuffles `512` indices with `de::Random rnd(1707306954u)` and checks every output entry against the corresponding indexed push constant record.
- `valid_limits` reports `Pass` after all property predicates succeed. The generated cases report `Pass` only after their output comparisons succeed.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `valid_limits` | The implementation reports a DGC property outside the range checked by `validLimits()`. |
| `maxIndirectCommandsTokenCount` | The command layout or generated-command execution does not handle the selected token count, or the final push constant does not reach the shader. |
| `maxIndirectCommandsStreamCount` | The implementation does not process the selected number of streams or does not combine stream data correctly. |
| `maxIndirectCommandsTokenOffset` | The implementation does not read a push constant token at the selected offset while still reading dispatch arguments at offset zero. |
| `maxIndirectCommandsStreamStrideRun` | The implementation does not advance between sequences by the selected stream stride or does not pass the indexed push constant record correctly. |
| `minIndirectCommandsBufferOffsetAlignment_offset_256` | The indirect command stream offset `256` is accepted incorrectly or the generated command reads the wrong data. |
| `minIndirectCommandsBufferOffsetAlignment_offset_4` | The indirect command stream offset `4` is accepted incorrectly or the generated command reads the wrong data. |
| `minIndirectCommandsBufferOffsetAlignment_offset_8` | The indirect command stream offset `8` is accepted incorrectly or the generated command reads the wrong data. |
| `minSequencesCountBufferOffsetAlignment` | The count buffer offset or count value is mishandled, or the implementation executes a different number of sequences than requested. |
| `minSequencesIndexBufferOffsetAlignment` | The index buffer offset or index selection is mishandled, so output values no longer match the shuffled records. |

Support failures are separate from these result failures. `checkDGCSupport()` requires `VK_NV_device_generated_commands`; the compute cases require `VK_NV_device_generated_commands_compute`; and the buffer-offset cases also require the requested offset to be a multiple of `minIndirectCommandsBufferOffsetAlignment`.

### Cause Analysis

#### Advertised property range failure

**Possible failure symptoms:** `valid_limits` returns a failed test status with a message naming the property whose value is outside the checked range.

**Possible implementation causes:** The queried `VkPhysicalDeviceDeviceGeneratedCommandsPropertiesNV` values do not satisfy the minimum or maximum predicates encoded in [`validLimits()`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1193-L1227). The test does not identify whether the value came from hardware, a driver property query, or another implementation layer.

#### Generated command interpretation failure

**Possible failure symptoms:** The compute dispatch completes, but the mapped output buffer contains a value different from the expected push constant or sequence-derived value. For the sequence tests, the log identifies the failing output index.

**Possible implementation causes:** The implementation may interpret the `IndirectCommandsLayoutNV`, stream offsets, token offsets, stream stride, count buffer, or index buffer differently from the contract exercised by the case. The source establishes the expected command data and host comparison, but a more specific implementation cause requires investigation of the failing property and Vulkan validation evidence.

#### Support or alignment rejection

**Possible failure symptoms:** The case exits with `NotSupportedError` before command execution because the required DGC extension, compute extension, or requested offset alignment is unavailable.

**Possible implementation causes:** The device does not expose the required extension or feature, or the requested offset is not a multiple of the device-reported `minIndirectCommandsBufferOffsetAlignment`. This is a support result, not evidence that a completed generated-command execution failed.

## Case Pruning

### Requirement-based pruning

- `valid_limits` requires `VK_NV_device_generated_commands` through `checkDGCSupport()`.
- All generated compute cases require `VK_NV_device_generated_commands_compute` through `checkBasicDGCComputeSupport()`.
- The three `minIndirectCommandsBufferOffsetAlignment_offset_*` cases run only when their registered offset is a multiple of `minIndirectCommandsBufferOffsetAlignment`.
- The generated cases reject only the reported limits needed for their construction: the token-count and stream-count cases require at least one token or stream; the token-offset case requires `maxIndirectCommandsStreamStride >= 16` and `maxIndirectCommandsTokenOffset >= 12`; and the stream-stride case requires `maxIndirectCommandsStreamStride >= 24`. The alignment cases obtain their offsets directly from the reported properties and do not add a separate minimum-limit check.

### Design-based pruning

- The command-limit cases cap selected values at `1024` or `1024u * 1024u` to avoid allocating unbounded host-visible buffers while retaining the reported property when it is below the cap.
- The stream-count case uses the minimum of the stream and token limits because it uses one token per stream, with the final stream's token being the dispatch token.
- The sequence alignment cases allocate space for `512` records. The count-buffer variant executes half of them and checks that the unused half remains zero; this keeps the count-buffer behavior visible without creating a second matrix dimension.
- `valid_limits` accepts `maxGraphicsShaderGroupCount == 0` as the source's compute-only compatibility case rather than registering a separate graphics property test.

## Key Takeaways

- `valid_limits` checks the reported NV DGC property ranges directly; the other nine cases use generated compute commands to exercise individual limit or alignment properties.
- The command-limit cases construct layouts at the selected boundary, then use a small shader result buffer to show whether the generated commands delivered the intended push constant data.
- `maxIndirectCommandsStreamStrideRun` checks sequence spacing with two indexed records, while the count and index alignment cases use `512` records to test metadata offsets and selection.
- A support skip means the device cannot run the requested case. A failed result after submission means the generated command path produced data that did not match the host reference.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDGCPropertyTests()` | [`registration`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1232-L1271) | Registers the `properties` group and all ten exact direct child names. |
| `storePushConstantProgram()` and `storePushConstantWithIndexProgram()` | [`shader generators`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L79-L104) | Define the two generated compute shader forms used by the cases. |
| `checkBasicDGCComputeSupport()` and alignment checks | [`support helpers`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L53-L76) | Gate generated cases on the NV compute extension and offset alignment. |
| `maxIndirectCommandsTokenCountRun()` | [`token count`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L112-L257) | Builds many push constant tokens and validates the final output value. |
| `maxIndirectCommandsStreamCountRun()` | [`stream count`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L259-L461) | Places one command token in each stream and validates the result. |
| `maxIndirectCommandsTokenOffsetRun()` | [`token offset`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L463-L622) | Separates the dispatch arguments from the push constant token by the selected offset. |
| `maxIndirectCommandsStreamStrideRun()` | [`stream stride`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L624-L816) | Uses two indexed records and the selected sequence stride. |
| `minIndirectCommandsBufferOffsetAlignmentRun()` | [`buffer offset alignment`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L818-L953) | Tests stream offsets `4`, `8`, and `256`. |
| `minSequencesOffsetAlignmentsRun()` | [`sequence metadata alignment`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L955-L1191) | Tests count and index buffer offsets, sequence selection, and output comparison. |
| `validLimits()` | [`property verification`](../../../modules/vulkan/device_generated_commands/vktDGCPropertyTests.cpp#L1193-L1227) | Checks the advertised DGC property ranges. |
| `checkDGCSupport()` and `checkDGCComputeSupport()` | [`DGC support utilities`](../../../modules/vulkan/device_generated_commands/vktDGCUtil.cpp#L40-L56) | Define the extension and feature requirements used by this file. |
| `dgc.nv.misc.properties` mustpass paths | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L4578-L4587) | Confirms the ten registered test paths in the default Vulkan profile. |
