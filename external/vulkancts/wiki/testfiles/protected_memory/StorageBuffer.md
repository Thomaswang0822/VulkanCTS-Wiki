## Overview

**Core question:** Do SSBO reads, writes, and atomic updates produce the expected buffer contents from fragment and compute shaders under each supported protected-memory and pipeline-protection configuration?

- [`vktProtectedMemStorageBufferTests.cpp`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L63-L80) implements the `protected_memory.ssbo` test families `ssbo_read`, `ssbo_write`, and `ssbo_atomic`.
- Read and write cases move `uvec4` data between a host input and storage buffers. Atomic cases apply eight GLSL atomic operations to four `uint` elements and compare the resulting vector with a host-computed reference.
- Each family varies shader stage, protection group, pipeline flags, and static or base-seed-derived random data. The page explains the generated shaders, protected resource setup, synchronization, validation, and deliberate matrix pruning.

## Background Knowledge

For the shared concepts protected memory, protected submission, and resource validation boundaries, see [Background Knowledge](../../categories/protected_memory.md#background-knowledge) of the `protected_memory` page.

- A shader storage block exposes memory from a bound storage-buffer descriptor to GLSL loads, stores, and atomic operations. This is how a shader accesses buffer data that the host cannot map when the backing memory is protected.
- An atomic operation performs one indivisible read-modify-write on its target location. Its return value is the value that preceded the update, but a shader may ignore that return value when only the resulting buffer contents matter.

## Registration Hierarchy

```text
protected_memory.ssbo
├── ssbo_read
├── ssbo_write
└── ssbo_atomic
```

The category dispatcher routes these three registered families to this implementation file. Their public factory entry points are [`createReadStorageBufferTests`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L864-L872), [`createWriteStorageBufferTests`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L874-L882), and [`createAtomicStorageBufferTests`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L884-L984). The current Vulkan and Vulkan SC mustpass files contain the corresponding `protected_memory.ssbo.ssbo_read`, `ssbo_write`, and `ssbo_atomic` prefixes.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| SSBO operation family | `ssbo_read`, `ssbo_write`, `ssbo_atomic` | Selects the shader template, resource data flow, and host reference calculation. | [Factories](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L864-L905) |
| Protection group | `default`; `protected_access` on non-Vulkan SC builds | Selects whether the optional pipeline-protected-access feature is requested. | [`protectedAccess`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L730-L739) |
| Pipeline flags | `none`; `protected_access_only`; `no_protected_access` on non-Vulkan SC builds | Selects pipeline recording restrictions and, for `no_protected_access`, the unprotected execution mode. | [`flags` and mode selection](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L741-L750) |
| Shader stage | `fragment`, `compute` | Chooses the generated shader interface and the graphics draw or compute dispatch path. | [Shader generation](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L363-L383) |
| Data set | `static`; `random` | Static leaves use six read/write vectors or four atomic vectors; random leaves use ten base-seed-derived cases. | [Read/write data](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L864-L881), [random generation](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L714-L727), [atomic data](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L884-L970) |
| Atomic operation | `add`, `min`, `max`, `and`, `or`, `xor`, `exchange`, `compswap` | Selects the atomic GLSL call and expected `uvec4` transformation. | [Atomic operation table and reference calculation](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L793-L860) |

`ssbo_read` and `ssbo_write` use the same protection, flag, stage, and data-set dimensions. `ssbo_atomic` adds the atomic-operation dimension and uses four static or ten random cases for each operation, stage, protection group, and flag combination.

## Behavior Parameters

The primary behavioral axis is the SSBO operation family. It changes the shader's data flow and the expected result, while the other dimensions transport that behavior through different pipeline and execution configurations.

### ssbo_read - copy from a source storage buffer

The read shader loads `protectedTestBufferSource` from the binding-2 SSBO and stores it in `protectedTestResultBuffer` at binding 0. The host initializes the source buffer by copying the input uniform data before shader execution.

### ssbo_write - store uniform data into a storage buffer

The write shader reads `testInput` from the binding-1 uniform block and stores it in `protectedTestResultBuffer` at binding 0. The protected compute validator later compares the result with the original `uvec4` input.

### ssbo_atomic - update storage elements with an atomic operation

The atomic shader declares `uint protectedTestResultBuffer[4]` in a `std430` SSBO. It derives an element index from the invocation identifier and substitutes one of eight atomic calls. The host computes the expected vector using the same operation and, for `compswap`, `swapNdx % 4` to select the component.

## Shader Analysis

The read and write families share a stage-specialized generator; atomic cases replace the assignment with a selected atomic call and use a four-element array. The following compute read case shows the storage-buffer declarations and the device-side operation that carries the tested value.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.protected_memory.ssbo.ssbo_read.default.none.compute.static.read_1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `ssbo_read` | Selects the source-SSBO-to-result-SSBO copy shader. |
| `default` with `none` | Uses the default pipeline-protection group and no pipeline protected-access flag. |
| `compute` | Uses a compute shader with one local invocation. |
| `static.read_1` | Uses the first fixed input, `uvec4(0, 0, 0, 0)`. |

#### Purpose

This shader checks that a compute invocation can read the selected value from the source storage buffer and write the same value to the result storage buffer.

#### Structural Design

| Stage | Shader action |
|-------|---------------|
| Source declaration | Binding 2 exposes `protectedTestBufferSource` as a `uvec4`. |
| Result declaration | Binding 0 exposes `protectedTestResultBuffer` as a `uvec4`. |
| Copy | `main()` loads the source member and stores it in the result member. |
| Host check | `BufferValidator` compares the result buffer with the selected input. |

#### Shader Code

```glsl
#version 450
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

/// Binding 0 is the result SSBO written by this read shader.
layout(set=0, binding=0, std140) buffer ProtectedTestBuffer
{
    highp uvec4 protectedTestResultBuffer;
};

/// Binding 2 is the source SSBO initialized by the host-side transfer.
layout(set=0, binding=2, std140) buffer ProtectedTestBufferSource
{
    highp uvec4 protectedTestBufferSource;
};

void main (void)
{
    /// The device-side operation copies the source vector into the result vector.
    protectedTestResultBuffer = protectedTestBufferSource;
}
```

#### Additional Info

- `StorageBufferTestCase::initPrograms` selects this template for `SSBO_READ` and adds the compute local-size declaration ([shader generator](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L271-L386)).
- The host-side copy from the unprotected input uniform into the source buffer is recorded before the compute dispatch and is followed by a transfer-to-compute shader barrier ([buffer copy helper](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L124-L171), [compute setup](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L649-L655)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| SSBO operation family | `ssbo_write` replaces the source SSBO with a uniform `Data` block; `ssbo_atomic` replaces the vector assignment with an atomic call and a four-element array. | [Shader templates](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L286-L340) |
| Shader stage | Fragment cases add `vIndex`, a color output, and a fixed vertex shader; compute cases use `gl_GlobalInvocationID.x` where an invocation index is needed. | [Stage specialization](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L363-L383) |
| Protection group and pipeline flags | These values do not change the GLSL text, but they change the pipeline flags, resource memory requirement, and command-buffer protection mode around the shader. | [Mode and flag tables](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L173-L183), [resource setup](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L588-L600) |
| Data set | Static and random leaves change the input values; the read shader structure stays the same. | [Random data generation](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L714-L727) |

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
; Bound: 23
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %ProtectedTestBuffer "ProtectedTestBuffer"
               OpMemberName %ProtectedTestBuffer 0 "protectedTestResultBuffer"
               OpName %_ ""
               OpName %ProtectedTestBufferSource "ProtectedTestBufferSource"
               OpMemberName %ProtectedTestBufferSource 0 "protectedTestBufferSource"
               OpName %__0 ""
               OpDecorate %ProtectedTestBuffer BufferBlock
               OpMemberDecorate %ProtectedTestBuffer 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %ProtectedTestBufferSource BufferBlock
               OpMemberDecorate %ProtectedTestBufferSource 0 Offset 0
               OpDecorate %__0 Binding 2
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%ProtectedTestBuffer = OpTypeStruct %v4uint
%_ptr_Uniform_ProtectedTestBuffer = OpTypePointer Uniform %ProtectedTestBuffer
          %_ = OpVariable %_ptr_Uniform_ProtectedTestBuffer Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%ProtectedTestBufferSource = OpTypeStruct %v4uint
%_ptr_Uniform_ProtectedTestBufferSource = OpTypePointer Uniform %ProtectedTestBufferSource
        %__0 = OpVariable %_ptr_Uniform_ProtectedTestBufferSource Uniform
%_ptr_Uniform_v4uint = OpTypePointer Uniform %v4uint
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %17 = OpAccessChain %_ptr_Uniform_v4uint %__0 %int_0
         %18 = OpLoad %v4uint %17
         %19 = OpAccessChain %_ptr_Uniform_v4uint %_ %int_0
               OpStore %19 %18
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each test creates a host-visible, unprotected uniform buffer containing `m_testInput`. It creates `testBuffer` and `testBufferSource` with storage-buffer usage; protected execution requests protected memory, while `no_protected_access` selects unprotected mode ([fragment resources](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L397-L421), [compute resources](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L576-L600)).
- The descriptor set uses binding 0 for the result SSBO, binding 1 for the uniform buffer, and binding 2 for the source SSBO. Read and atomic cases copy input data into the selected storage buffer before shader execution ([descriptor updates](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L605-L634)).
- Fragment cases create a protected or unprotected 128 by 128 color image, record the image barriers, draw four vertices as a point list, and submit the command buffer with a fence. The color output is fixed; the result SSBO is the correctness signal ([fragment execution](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L460-L552)).
- Compute cases bind the compute pipeline and dispatch one workgroup for read and write, or four workgroups for atomic cases. The queue submission waits on a fence before validation ([compute dispatch](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L637-L665)).
- The operation submission fence establishes completion but is not the correctness oracle. `BufferValidator` uploads the expected `uvec4` to an unprotected reference uniform, resets a protected helper buffer, and dispatches a protected compute validator that performs an exact vector comparison. A mismatch enters a deliberately non-advancing loop, so the one-second validation submission times out and returns `false`; the host never maps the tested result buffer ([validator shader](../../../modules/vulkan/protected_memory/vktProtectedMemBufferValidator.cpp#L132-L194), [validator execution](../../../modules/vulkan/protected_memory/vktProtectedMemBufferValidator.hpp#L181-L324)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ssbo_read` | Protected-buffer read visibility, source-to-result storage-buffer access, transfer-to-shader synchronization, or host reference setup does not produce the expected vector. |
| `ssbo_write` | Protected-buffer write access, uniform-to-storage-buffer data flow, shader-stage pipeline access, or host reference setup does not produce the expected vector. |
| `ssbo_atomic` | Atomic operation semantics, selected component/indexing, protected storage access, initialization synchronization, or host atomic reference calculation does not produce the expected vector. |

### Cause Analysis

#### Read-path data or synchronization failures

**Possible failure symptoms:** When one or more result components differ from the selected `uvec4` input, the protected validator enters its error loop and its submission times out, causing `validateBuffer()` to return `false`.

**Possible implementation causes:** The source buffer may not expose the copied value to the shader at the required transfer-to-shader dependency, or the shader may load the wrong descriptor binding. The exact implementation cause requires investigation of the failing configuration and validation data.

#### Write-path descriptor or storage access failures

**Possible failure symptoms:** When the result SSBO does not equal the `testInput` uniform value, the protected validator submission times out and the case fails.

**Possible implementation causes:** The binding-1 uniform data may not reach the shader, or the binding-0 storage write may not update the selected protected or unprotected buffer. The exact implementation cause requires investigation of the failing configuration.

#### Atomic operation or reference calculation failures

**Possible failure symptoms:** When one or more result elements differ from the host-computed `add`, `min`, `max`, `and`, `or`, `xor`, `exchange`, or `compswap` reference value, the protected validator submission times out and the case fails.

**Possible implementation causes:** The selected atomic operation, array-element index, or protected storage access may behave differently from the operation encoded by the test. For `compswap`, a mismatch can also indicate that the selected component or compare value did not follow `swapNdx % 4`. The exact implementation cause requires investigation; the test source alone does not assign the failure to a particular hardware, driver, compiler, or host component.

#### Common submission and validation failures

**Possible failure symptoms:** The operation submission can fail before validation begins, or the later validator submission can fail to complete. A data mismatch specifically appears as the validator's one-second timeout rather than as a host-readable component-by-component mismatch report.

**Possible implementation causes:** The protected context, command-buffer protection mode, pipeline flags, descriptor updates, queue submission, or host-side reference setup may be inconsistent with the selected case. The exact failing layer requires investigation of the reported case and configuration.

## Case Pruning

### Requirement-based pruning

- Every generated case requires Vulkan 1.1, the `protectedMemory` feature, and a protected-capable queue. Unsupported implementations are rejected by the shared protected-context support check before execution ([support helper](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127)).
- Cases in the `protected_access` group additionally require the `pipelineProtectedAccess` feature from `VK_EXT_pipeline_protected_access` ([case support check](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L230-L235), [feature check](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L120-L124)).

### Design-based pruning

- Vulkan SC builds deliberately omit the `protected_access` group and both nonzero pipeline flag values at compile time ([guarded tables](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L730-L750)).
- The `default` group generates only the `none` flag. The two nonzero flags are generated only under `protected_access`, avoiding combinations that request pipeline recording restrictions without requesting the corresponding feature ([conditional skip](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L760-L768)).
- The matrix bounds value variation to six fixed plus ten generated vectors for read/write cases, and four fixed plus ten generated input/argument combinations per atomic operation. These fixed sample counts limit case growth without changing the operation mechanisms ([read/write registration](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L752-L790), [atomic registration](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L884-L970)).

## Key Takeaways

- The file tests three distinct SSBO behaviors: copying from a storage buffer, writing uniform data to a storage buffer, and applying one of eight atomic operations.
- The same operation families run in fragment and compute stages, with protected resource allocation and pipeline flags changing the execution environment around the generated GLSL.
- A protected compute validator checks the result SSBO exactly; a mismatch becomes a validator timeout rather than a direct host read of protected memory. The fixed fragment color and the operation-submission fence are not correctness oracles.
- The `protected_access` and pipeline-flag dimensions are conditional. Their absence in a Vulkan SC build is deliberate matrix pruning, not missing behavior.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| SSBO operation enums | [`SSBOTestType` and `SSBOAtomicType`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L63-L80) | Defines the behavior families and atomic operation names. |
| Buffer-copy barriers | [`addBufferCopyCmd`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L124-L171) | Records the host-to-transfer and transfer-to-shader dependencies. |
| Support and mode selection | [`checkSupport` and `getProtectionMode`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L173-L183) | Connects case parameters to protected-context support and execution mode. |
| Shader generator | [`StorageBufferTestCase::initPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L271-L386) | Emits the stage-specific read, write, and atomic GLSL. |
| Fragment runtime | [`executeFragmentTest`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L389-L565) | Creates graphics resources, submits the draw, and validates the result. |
| Compute runtime | [`executeComputeTest`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L568-L676) | Creates compute descriptors, dispatches workgroups, and validates the result. |
| Atomic reference calculation | [`calculateAtomicOpData`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L793-L860) | Produces the expected vector and shader call for each atomic operation. |
| Family registration | [`createReadStorageBufferTests`, `createWriteStorageBufferTests`, `createAtomicStorageBufferTests`](../../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L864-L984) | Builds the registered family, parameter, and test-case hierarchy. |
| Validator shader generation | [`initBufferValidatorPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemBufferValidator.cpp#L86-L194) | Generates the exact `uvec4` comparison and deliberate timeout-on-mismatch path. |
| Validator execution | [`BufferValidator::validateBuffer`](../../../modules/vulkan/protected_memory/vktProtectedMemBufferValidator.hpp#L181-L324) | Dispatches protected validation and converts a timeout into `false`. |
| Protected-context support | [`checkProtectedContextSupport`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127) | Checks the Vulkan version, protected-memory feature, optional pipeline-protected-access feature, and protected queue. |
| Protected-memory specification | [`Protected Memory`](../../../../vulkan-docs/src/chapters/memory.adoc#L5566-L5654) | Defines protected memory objects, queues, operations, and access rules. |
