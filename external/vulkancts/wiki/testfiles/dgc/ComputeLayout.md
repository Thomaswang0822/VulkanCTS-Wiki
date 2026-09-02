## Overview

**Core question:** Do NV generated-command layouts deliver the right per-dispatch state to each compute dispatch?

- This page covers `vktDGCComputeLayoutTests.cpp`, which implements `dgc.nv.compute.layout`.
- The tests combine push-constant, pipeline, and dispatch tokens. They also cover partial push updates, complementary host push constants, 4-byte token-offset alignment for pipeline layouts, compute-queue execution, and pipeline-address capture/replay.
- Four generated sequences write distinct values to a host-visible storage buffer. The host checks every invocation against the values selected by that sequence's tokens and dispatch dimensions.
- The page explains the registered NV families, the token layout and byte encoding, the runtime flow, and what each mismatch can mean.

## Background Knowledge

- A `VkIndirectCommandsLayoutNV` defines the order and byte ranges of token data in an indirect command stream. The generated-command implementation reads each sequence according to those ranges and strides.
- A pipeline token selects a pipeline through a device address. A push-constant token copies stream data into a declared shader-visible range. A dispatch token consumes `VkDispatchIndirectCommand` dimensions and starts the compute work.
- A compute shader with `local_size_x = 64` runs 64 invocations in each workgroup. `gl_LocalInvocationIndex` identifies an invocation within that workgroup, while `gl_WorkGroupID` identifies the workgroup.

## Registration Hierarchy

```text
dgc.nv.compute.layout
├── complementary_push_dispatch
├── complementary_push_dispatch_cq
├── partial_push_dispatch
├── partial_push_dispatch_cq
├── pipeline_complementary_push_dispatch
├── pipeline_complementary_push_dispatch_cq
├── pipeline_dispatch
├── pipeline_dispatch_align4
├── pipeline_dispatch_align4_cq
├── pipeline_dispatch_cq
├── pipeline_push_dispatch
├── pipeline_push_dispatch_align4
├── pipeline_push_dispatch_align4_cq
├── pipeline_push_dispatch_capture_replay
├── pipeline_push_dispatch_capture_replay_cq
├── pipeline_push_dispatch_cq
├── push_dispatch
└── push_dispatch_cq
```

These are the exact direct children registered by `createDGCComputeLayoutTests()`. The `_cq` suffix selects the compute queue. The `_align4` suffix applies to the pipeline address alignment variants, and `pipeline_push_dispatch_capture_replay` adds the capture/replay address path. The corresponding mustpass entries are listed in [`dgc.txt`](../../../mustpass/main/vk-default/dgc.txt#L4462-L4479).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `TestType` | `PUSH_DISPATCH`, `COMPLEMENTARY_PUSH_DISPATCH`, `PARTIAL_PUSH_DISPATCH`, `PIPELINE_DISPATCH`, `PIPELINE_PUSH_DISPATCH`, `PIPELINE_COMPLEMENTARY_PUSH_DISPATCH` | Selects the state tokens, shader constant transport, and indirect payload format. | [`TestType`](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L53-L67) |
| Queue selection | default queue, `_cq` | Chooses `ctx.queue` or the device compute queue and its family. | [`TestParams` and queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L84-L98) |
| Pipeline address alignment | native address stride, `align4` | With `align4`, support requires `minIndirectCommandsBufferOffsetAlignment <= 4`; otherwise each stream stride is rounded to `sizeof(VkDeviceAddress)`. | [`checkSupport()` and stream stride](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L184-L201), [`makeCommandsLayout()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L431-L439) |
| Pipeline address mode | ordinary, `captureReplay` | The capture/replay family obtains pipeline indirect addresses from temporary pipelines, then reuses them for the active pipelines. | [`createPipelines()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L339-L374) |
| Generated sequences | `4` | Gives each sequence independent workgroup counts and specialization data. | [`kSequenceCount` and generation](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L109-L110), [`iterate()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L553-L580) |
| Workgroup count per sequence | random integer in `1..16`, inclusive | Changes the number of output values checked for that sequence. | [`iterate()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L553-L565) |
| Local invocations | `64` | Fixes the number of invocations per workgroup and the output index stride. | [`kLocalInvocations` and shader](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L109-L110), [`initPrograms()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L252-L271) |

The registration table combines nine base names with the two queue choices. The base names are `push_dispatch`, `complementary_push_dispatch`, `partial_push_dispatch`, `pipeline_dispatch`, `pipeline_push_dispatch`, `pipeline_push_dispatch_capture_replay`, `pipeline_dispatch_align4`, `pipeline_push_dispatch_align4`, and `pipeline_complementary_push_dispatch`.

## Behavior Parameters

`TestType` is the primary behavioral axis. Its values change which state the generated command stream updates before the final dispatch action.

### `PUSH_DISPATCH` and `push_dispatch` | complete generated push state

The layout has one push-constant token covering the three `uint` values `dispatchOffset`, `skipIndex`, and `valueOffset`, followed by the dispatch token. Each sequence writes those three values to the indirect stream, then writes a `VkDispatchIndirectCommand` with its workgroup count.

### `COMPLEMENTARY_PUSH_DISPATCH` and `complementary_push_dispatch` | generated state plus one host push

The stream carries the three per-sequence values. Before executing the generated commands, the host pushes `valueOffset2`, which equals `64`. The pipeline layout reserves space for that extra constant, and the host push offset follows the generated token data. The shader adds `valueOffset2` to the stored value.

### `PARTIAL_PUSH_DISPATCH` and `partial_push_dispatch` | overlapping partial updates

The layout uses two push-constant tokens. The first covers constants 0 and 1, and the second starts at constant 1 and covers constants 1 and 2. The indirect stream first supplies `dispatchOffset`, an intentionally bad `skipIndex`, and then the correct `skipIndex` and `valueOffset`. This makes the middle constant overlap and tests both partial updates and their order.

### `PIPELINE_DISPATCH` and `pipeline_dispatch` | pipeline token with specialization

The layout has a pipeline token followed by dispatch. The test creates one specialized pipeline per sequence. Specialization IDs 0, 1, and 2 carry `dispatchOffset`, `skipIndex`, and `valueOffset`, so the stream contains the pipeline device address and dispatch dimensions rather than push-constant values.

### `PIPELINE_PUSH_DISPATCH` and `pipeline_push_dispatch` | pipeline selection plus generated push

The layout has a pipeline token, a push-constant token covering `dispatchOffset` and `skipIndex`, and the final dispatch token. Each pipeline specializes `valueOffset` with constant ID 2. The indirect payload stores the pipeline address, the two push values, and the dispatch dimensions.

### `PIPELINE_COMPLEMENTARY_PUSH_DISPATCH` and `pipeline_complementary_push_dispatch` | pipeline, generated push, and host push

This form is like `PIPELINE_PUSH_DISPATCH`, but the pipeline layout declares `valueOffset2` before `dispatchOffset` and `skipIndex`. The host pushes `valueOffset2` at offset 0, while the generated push token begins after it. The shader combines the specialized `valueOffset`, generated values, and the host value.

Every layout adds `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DISPATCH` last. For pipeline layouts without `align4`, the test manually rounds each stream stride up to `sizeof(VkDeviceAddress)`, adding padding after the dispatch payload when needed. With `align4`, the test permits the smaller device property value and does not add that address-sized stride padding.

## Shader Analysis

The test generates one compute shader named `comp` in `initPrograms()`. The shader declares a storage buffer at set 0, binding 0 and uses `layout (local_size_x=64, local_size_y=1, local_size_z=1)`. For the push-constant form, its relevant calculation is:

```glsl
const uint valueIndex = pc.dispatchOffset + workGroupIndex * gl_WorkGroupSize.x + gl_LocalInvocationIndex;
const uint storageValue = pc.valueOffset + (workGroupIndex << 10) + gl_LocalInvocationIndex;
if (pc.skipIndex != gl_LocalInvocationIndex)
    storageBuffer.values[valueIndex] = storageValue;
```

The pipeline variants use specialization-constant identifiers in place of the corresponding `pc` members, and the mixed variants use push constants for `dispatchOffset` and `skipIndex` while specializing `valueOffset`.

The generated compute shader is central to the test: its push-constant, specialization, and validation branches determine whether each token layout delivers the state expected by the host result scan.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dgc.nv.compute.layout.push_dispatch
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `push_dispatch` | Uses a generated push-constant token followed by a dispatch token, so all three arithmetic inputs come from the generated stream. |
| Four generated sequences with 64 local invocations | Gives each sequence an independent dispatch offset and value range while preserving a fixed invocation shape for the checker. |

#### Purpose

This compute shader checks that generated push constants and indirect dispatch dimensions select the correct output region for every invocation. One invocation per workgroup is intentionally skipped, providing a zero-valued check alongside the written values.

#### Structural Design

| Shader phase | Data and effect |
|--------------|-----------------|
| Interface and state | A set-0, binding-0 runtime storage buffer receives results; the push-constant block supplies `dispatchOffset`, `skipIndex`, and `valueOffset`. |
| Workgroup flattening | `gl_WorkGroupID` and `gl_NumWorkGroups` are flattened into `workGroupIndex`, so the checker handles the dispatch dimensions without assuming a single row. |
| Address and expected value | `dispatchOffset` selects the output region, while `valueOffset + (workGroupIndex << 10) + gl_LocalInvocationIndex` creates a sequence- and workgroup-specific pattern. |
| Validation write | The invocation whose local index equals `skipIndex` leaves its initialized zero untouched; all other invocations write the computed value. |

#### Shader Code

```glsl
#version 460
layout (local_size_x=64, local_size_y=1, local_size_z=1) in;
/// Binding 0 is the host-visible std430 storage buffer checked after generated-command execution.
layout (set=0, binding=0, std430) buffer StorageBlock { uint values[]; } storageBuffer;
/// The generated push token supplies the dispatch base, one invocation to skip, and the value base.
layout (push_constant, std430) uniform PushConstantBlock {
    uint dispatchOffset;
    uint skipIndex;
    uint valueOffset;
} pc;
void main (void) {
    /// Flatten the workgroup coordinates so each sequence writes a contiguous output region.
    const uint workGroupIndex = gl_NumWorkGroups.x * gl_NumWorkGroups.y * gl_WorkGroupID.z + gl_NumWorkGroups.x * gl_WorkGroupID.y + gl_WorkGroupID.x;
    /// The dispatch token dimensions determine the number of workgroups; the push token selects the output base.
    const uint valueIndex = pc.dispatchOffset + workGroupIndex * gl_WorkGroupSize.x + gl_LocalInvocationIndex;
    /// Each workgroup receives a distinct value range, making token or dispatch mix-ups visible to the host scan.
    const uint storageValue = pc.valueOffset + (workGroupIndex << 10) + gl_LocalInvocationIndex
        ;
    /// One invocation is intentionally left at the initialized zero value for the validation oracle.
    if (pc.skipIndex != gl_LocalInvocationIndex) {
        storageBuffer.values[valueIndex] = storageValue;
    }
}
```

#### Additional Info

- The selected `push_dispatch` branch emits the push-constant block in the order `dispatchOffset`, `skipIndex`, `valueOffset`; the host writes the same three values before the dispatch payload.
- `workGroupIndex << 10` is equivalent to multiplying the workgroup index by 1024, while the output index advances by 64 invocations per workgroup; this separation makes both dispatch placement and per-workgroup values observable.
- The representative path uses the default queue and native address-alignment setting. `_cq`, `align4`, capture/replay, partial-update, and pipeline-token registrations exercise nearby host or layout branches rather than changing this shader's arithmetic.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `TestType` | Push-only cases declare all three values as push constants; pipeline-only cases replace them with specialization constants, and mixed cases split the declarations between the two transports. | [`initPrograms()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L203-L272) |
| Queue selection | The shader source stays fixed; the `_cq` dimension changes the queue family used to execute the same compute stage. | [`iterate()` queue selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L545-L550) |
| Generated sequences | The shader stays fixed while each sequence receives distinct `dispatchOffset`, `skipIndex`, and `valueOffset` values, making state selection visible in the output. | [`iterate()` specialization data](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L566-L580) |
| Workgroup count | The dispatch token changes `gl_NumWorkGroups.x`; the flattening expression and per-workgroup value formula therefore cover the selected number of workgroups. | [`makeIndirectCommands()`](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L451-L477) |

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
; Bound: 77
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_WorkGroupID %gl_LocalInvocationIndex
               OpExecutionMode %main LocalSize 64 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %workGroupIndex "workGroupIndex"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %valueIndex "valueIndex"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "dispatchOffset"
               OpMemberName %PushConstantBlock 1 "skipIndex"
               OpMemberName %PushConstantBlock 2 "valueOffset"
               OpName %pc "pc"
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpName %storageValue "storageValue"
               OpName %StorageBlock "StorageBlock"
               OpMemberName %StorageBlock 0 "values"
               OpName %storageBuffer "storageBuffer"
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpMemberDecorate %PushConstantBlock 1 Offset 4
               OpMemberDecorate %PushConstantBlock 2 Offset 8
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %StorageBlock BufferBlock
               OpMemberDecorate %StorageBlock 0 Offset 0
               OpDecorate %storageBuffer Binding 0
               OpDecorate %storageBuffer DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%PushConstantBlock = OpTypeStruct %uint %uint %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
    %uint_64 = OpConstant %uint 64
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
      %int_2 = OpConstant %int 2
     %int_10 = OpConstant %int 10
      %int_1 = OpConstant %int 1
       %bool = OpTypeBool
%_runtimearr_uint = OpTypeRuntimeArray %uint
%StorageBlock = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_StorageBlock = OpTypePointer Uniform %StorageBlock
%storageBuffer = OpVariable %_ptr_Uniform_StorageBlock Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_64 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%workGroupIndex = OpVariable %_ptr_Function_uint Function
 %valueIndex = OpVariable %_ptr_Function_uint Function
%storageValue = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %15 = OpLoad %uint %14
         %17 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_1
         %18 = OpLoad %uint %17
         %19 = OpIMul %uint %15 %18
         %22 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %23 = OpLoad %uint %22
         %24 = OpIMul %uint %19 %23
         %25 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %26 = OpLoad %uint %25
         %27 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %28 = OpLoad %uint %27
         %29 = OpIMul %uint %26 %28
         %30 = OpIAdd %uint %24 %29
         %31 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %32 = OpLoad %uint %31
         %33 = OpIAdd %uint %30 %32
               OpStore %workGroupIndex %33
         %41 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %42 = OpLoad %uint %41
         %43 = OpLoad %uint %workGroupIndex
         %45 = OpIMul %uint %43 %uint_64
         %46 = OpIAdd %uint %42 %45
         %48 = OpLoad %uint %gl_LocalInvocationIndex
         %49 = OpIAdd %uint %46 %48
               OpStore %valueIndex %49
         %52 = OpAccessChain %_ptr_PushConstant_uint %pc %int_2
         %53 = OpLoad %uint %52
         %54 = OpLoad %uint %workGroupIndex
         %56 = OpShiftLeftLogical %uint %54 %int_10
         %57 = OpIAdd %uint %53 %56
         %58 = OpLoad %uint %gl_LocalInvocationIndex
         %59 = OpIAdd %uint %57 %58
               OpStore %storageValue %59
         %61 = OpAccessChain %_ptr_PushConstant_uint %pc %int_1
         %62 = OpLoad %uint %61
         %63 = OpLoad %uint %gl_LocalInvocationIndex
         %65 = OpINotEqual %bool %62 %63
               OpSelectionMerge %67 None
               OpBranchConditional %65 %66 %67
         %66 = OpLabel
         %72 = OpLoad %uint %valueIndex
         %73 = OpLoad %uint %storageValue
         %75 = OpAccessChain %_ptr_Uniform_uint %storageBuffer %int_0 %72
               OpStore %75 %73
               OpBranch %67
         %67 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `iterate()` chooses the default queue unless `computeQueue` is true, in which case it uses `getComputeQueueFamilyIndex()` and `getComputeQueue()`.
- The test seeds `de::Random` with `0xff0000u | static_cast<uint32_t>(m_params.testType)`. It generates four workgroup counts from `1` through `16`, then creates one `SpecializationData` record per sequence. `dispatchOffset` is the number of preceding workgroups multiplied by 64, `skipIndex` is in `0..63`, and `valueOffset` is `(sequence index + 1) << 20`.
- It allocates a zeroed host-visible storage buffer sized for `totalNumWorkGroups * 64` `uint32` values. A descriptor set binds this buffer at binding 0.
- `createPipelines()` creates one compute pipeline for push-only cases. Pipeline-token cases create one specialized `DGCComputePipeline` per sequence. For capture/replay, temporary pipelines provide the addresses used when the active pipelines are created.
- `makeCommandsLayout()` builds the state-token layout and appends the dispatch token. `makeIndirectCommands()` writes the matching payload format: push values for push cases, pipeline addresses for pipeline cases, and three dispatch dimensions with `.y = 1` and `.z = 1`. It adds `0xA1B2C3D4` as explicit padding when the native-address stride requires it.
- The test creates a `PreprocessBuffer`, binds the descriptor set, binds the single pipeline when present, or updates each indirect pipeline buffer with `vkCmdUpdatePipelineIndirectBufferNV`. It then calls `cmdExecuteGeneratedCommandsNV` with one stream and four sequences.
- A shader-write to host-read memory barrier precedes submission completion. The host invalidates the output allocation and checks each element. For every workgroup and invocation, it expects zero at `skipIndex`; otherwise it expects `valueOffset + (workGroupIndex << 10) + invocationIndex`, plus `valueOffset2` for complementary forms.
- A mismatch logs the flat index, expected and actual values, dispatch index, workgroup index, invocation index, and relevant offsets. Any mismatch returns `Unexpected output values found; check log for details`; otherwise the test returns `Pass`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `push_dispatch` | Push-constant token range or payload decoding was wrong; the dispatch token was decoded at the wrong stream offset. |
| `complementary_push_dispatch` | The externally pushed `valueOffset2` was applied at the wrong push-constant offset or combined with generated data incorrectly; dispatch data was decoded incorrectly. |
| `partial_push_dispatch` | One of the overlapping push-constant updates was applied at the wrong offset, size, or order. |
| `pipeline_dispatch` | The pipeline token selected the wrong specialized pipeline, its address was decoded incorrectly, or dispatch data was decoded incorrectly. |
| `pipeline_push_dispatch` | Pipeline selection, specialization of `valueOffset`, generated push-constant updates, or dispatch decoding was wrong. |
| `pipeline_complementary_push_dispatch` | Pipeline selection, generated push constants, or the externally pushed `valueOffset2` was applied at the wrong offset; dispatch data was decoded incorrectly. |

### Cause Analysis

#### Generated push-constant ranges and payloads

**Possible failure symptoms:** The output scan finds a wrong value, or the invocation selected by `skipIndex` is nonzero. The log identifies the affected sequence, workgroup, invocation, and offsets.

**Possible implementation causes:** The implementation may decode a push-constant token with the wrong offset or size, apply overlapping updates in the wrong order, or read the indirect stream at the wrong stride. The source identifies the expected ranges and payloads but does not isolate a failing implementation to a particular driver, compiler, or hardware component. Further source-level investigation is needed.

#### Complementary host push constant

**Possible failure symptoms:** A complementary case can produce values missing the expected `valueOffset2` contribution, or a host push applied at the wrong offset can corrupt another push-constant field and select the wrong output region.

**Possible implementation causes:** The implementation may apply `cmdPushConstants` at the wrong offset, or combine the external value with generated push data incorrectly. The source establishes the two declaration and push offsets but does not identify which implementation layer would fail.

#### Pipeline token and specialization

**Possible failure symptoms:** A sequence produces values belonging to another sequence, uses the wrong `skipIndex`, or fails across pipeline-token cases while push-only cases pass.

**Possible implementation causes:** The implementation may decode a pipeline device address incorrectly, select the wrong per-sequence pipeline, or apply specialization data to the wrong pipeline. The result scan can expose the mismatch but cannot assign it to the driver, compiler, or hardware without additional investigation.

#### Stream stride and address alignment

**Possible failure symptoms:** `pipeline_dispatch_align4` or `pipeline_push_dispatch_align4` can fail while their non-`align4` counterparts pass, with errors at later sequences where a miscomputed stride changes token locations.

**Possible implementation causes:** The implementation may interpret a stream using the wrong stride or fail to honor the declared alignment requirements. The test gates `align4` on `minIndirectCommandsBufferOffsetAlignment <= 4` and otherwise rounds the stride to `sizeof(VkDeviceAddress)`, so an unsupported property is skipped rather than reported as a failure.

#### Queue selection and host visibility

**Possible failure symptoms:** Failures limited to `_cq` cases may show missing or stale values after execution, while the default-queue variants pass. Any result mismatch still appears in the per-element log.

**Possible implementation causes:** The queue submission or synchronization path may mishandle compute-queue execution, or shader writes may not become visible to the host as required by the barrier and allocation invalidation. The source specifies the synchronization sequence but does not prove a more specific cause.

## Case Pruning

### Requirement-based pruning

- `checkDGCComputeSupport()` gates all cases. Pipeline-token cases request pipeline support, and capture/replay cases request capture/replay support.
- `align4` cases are supported only when `minIndirectCommandsBufferOffsetAlignment <= 4`; otherwise `checkSupport()` throws `NotSupportedError` and the case is skipped.
- `_cq` cases require an available compute queue. The queue lookup throws `NotSupportedError` when no such queue exists.
- Capture/replay is asserted to require a pipeline-switching `TestType`, so only the registered pipeline push case uses it.

### Design-based pruning

- The test always uses four generated sequences and random workgroup counts from 1 through 16. This keeps each sequence independently identifiable while exercising multiple stream records.
- The dispatch-only layout is covered by the compute smoke tests. These layout cases add push-constant and pipeline state tokens, including overlapping updates and address alignment.
- Complementary push cases add an external constant only where the shader and pipeline layout declare it. The registration table does not create complementary variants for `PARTIAL_PUSH_DISPATCH` or `PIPELINE_DISPATCH`.

## Key Takeaways

- `TestType` changes the state tokens and the transport of `dispatchOffset`, `skipIndex`, and `valueOffset`; it is the page's primary behavioral axis.
- The generated command layout always ends with `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DISPATCH`. Earlier tokens must place the state consumed by that dispatch at the declared byte ranges.
- Push-only cases test complete and partial updates. Pipeline cases test device-address selection and per-sequence specialization. Complementary cases add one host push constant outside the generated stream.
- The result buffer gives each sequence and workgroup a distinct expected pattern. A mismatch points to the failing variant's token decoding, state selection, dispatch payload, alignment, queue, synchronization, or shader specialization behavior.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestType` and `TestParams` | [`TestType` and parameters](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L53-L110) | Defines the six behavior types and Boolean dimensions. |
| `LayoutTestCase::checkSupport()` | [support checks](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L184-L201) | Defines DGC, alignment, capture/replay, and queue requirements. |
| `LayoutTestCase::initPrograms()` | [shader generator](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L203-L273) | Emits the compute shader and token-dependent constant declarations. |
| `LayoutTestInstance::createPipelines()` | [pipeline construction](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L280-L388) | Creates single or per-sequence pipelines and capture/replay addresses. |
| `LayoutTestInstance::makeCommandsLayout()` | [token layout builder](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L390-L443) | Defines token order, ranges, offsets, and stream stride. |
| `LayoutTestInstance::makeIndirectCommands()` | [indirect payload encoding](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L445-L542) | Encodes state payloads, addresses, padding, and dispatch dimensions. |
| `LayoutTestInstance::iterate()` | [runtime execution](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L545-L699) | Creates resources, preprocesses commands, submits work, and synchronizes readback. |
| Result scan | [validation](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L701-L747) | Defines expected values, diagnostics, and pass/fail behavior. |
| `createDGCComputeLayoutTests()` | [registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeLayoutTests.cpp#L752-L784) | Builds the registered NV families and `_cq` variants. |
| Mustpass coverage | [`dgc.txt`](../../../mustpass/main/vk-default/dgc.txt#L4462-L4479) | Lists the exact NV compute layout paths. |
| Vulkan DGC semantics | [Device-Generated Commands](../../../../vulkan-docs/src/chapters/device_generated_commands/generatedcommands.adoc#device-generated-commands) | Defines generated layout, preprocessing, pipeline update, and execution semantics. |
| Vulkan dispatch semantics | [Dispatching Commands](../../../../vulkan-docs/src/chapters/dispatch.adoc#dispatching-commands) | Defines indirect dispatch dimensions and compute workgroup behavior. |
