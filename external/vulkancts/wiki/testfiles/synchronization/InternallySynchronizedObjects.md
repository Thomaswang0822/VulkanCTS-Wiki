## Overview

**Core question:** Can multiple host threads create compute or graphics pipelines with the same internally synchronized `VkPipelineCache` and still execute every created pipeline correctly?

- [vktSynchronizationInternallySynchronizedObjectsTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp) implements the `synchronization.internally_synchronized_objects` test family.
- The family has two executable test case leaves: `pipeline_cache_compute` and `pipeline_cache_graphics`.
- Every worker receives the same pipeline cache. The test does not place an application mutex around pipeline creation; its mutex protects queue and command-buffer allocation instead.
- Each created pipeline writes the integer sequence `0..15` to a per-execution storage buffer. The host checks that sequence after the submitted work completes.
- The family appears in both the Vulkan and Vulkan SC synchronization mustpass lists. It is separate from `synchronization2.internally_synchronized_queues`.

## Background Knowledge

- Vulkan permits concurrent host calls unless a parameter or related object requires external synchronization. A pipeline cache without `VK_PIPELINE_CACHE_CREATE_EXTERNALLY_SYNCHRONIZED_BIT` is internally synchronized when pipeline-creation commands use it, so multiple threads may pass the same cache concurrently.
- A `VkPipelineCache` stores implementation-defined pipeline-creation data. It is not shader-visible memory. The shaders write separate storage buffers so the test can confirm that pipelines created during concurrent cache use remain executable.

## Registration Hierarchy

```text
synchronization.internally_synchronized_objects
├── pipeline_cache_compute
└── pipeline_cache_graphics
```

The factory registers these two test case leaves only under the legacy-named `synchronization` test category. The Vulkan SC mustpass uses the `dEQP-VKSC` package prefix but retains the same registered category and family path.

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|-----------|-------------------------------|----------------------|----------|
| Test case leaf | `pipeline_cache_compute`, `pipeline_cache_graphics` | Selects compute or graphics pipeline creation, queue requirements, shader stage, and execution commands. | [registration](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1351-L1360) |
| Shader variant | `compute_0`, `compute_1`, `compute_2`; `vert_0`, `vert_1`, `vert_2` | Varies how the shader produces the same `0..15` payload. These variants are cycled inside each executable case and are not registered leaves. | [shader generation](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1196-L1243), [graphics shader generation](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1271-L1335) |
| Worker count | Vulkan: logical-core count clamped to `4..32`; Vulkan SC: `2` | Sets the number of host threads sharing the pipeline cache. | [compute instance](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L765-L838), [graphics instance](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L898-L970) |
| Executions per worker | Vulkan: `100`; Vulkan SC: `10` | Repeats pipeline creation and execution while cycling through all three shader variants. | [constants and workers](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L82-L96), [worker loops](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L677-L763) |
| Checked payload | `16` signed 32-bit integers | Element `n` must equal `n`; the buffer occupies `64` bytes. | [compute check](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L366-L446), [graphics check](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L448-L553) |

## Behavior Parameters

The primary behavioral axis is the **test case leaf**. Both values test concurrent access to the same kind of object, but they exercise different pipeline-creation and execution paths.

### `pipeline_cache_compute` — concurrent compute-pipeline creation

Each worker calls compute-pipeline creation with the shared cache, choosing `compute_0`, `compute_1`, or `compute_2` by iteration index. It then acquires a compute-capable queue, dispatches the pipeline, and checks the result buffer. The three shaders produce the same sequence through 16 one-invocation workgroups, one looping invocation, or one 16-invocation workgroup.

### `pipeline_cache_graphics` — concurrent graphics-pipeline creation

Each worker creates a graphics pipeline with the shared cache, choosing one of three vertex shaders. It renders points into a `1x1` color attachment while the vertex shader writes the checked storage-buffer sequence. The variants use 16 vertex invocations, one forward loop, or one reverse loop; the fragment shader writes white, but the host does not inspect the color attachment.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.synchronization.internally_synchronized_objects.pipeline_cache_compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `pipeline_cache_compute` | Selects the compute-pipeline path, which creates pipelines concurrently with one shared internally synchronized `VkPipelineCache`. |
| `compute_0` | Selects the primary generated compute shader: 16 one-invocation workgroups write the complete `0..15` payload through `gl_GlobalInvocationID.x`. |
| `16` dispatch workgroups | The host executes `compute_0` with `vk.cmdDispatch(..., 16, 1, 1)`, producing one result element per global invocation. |

#### Purpose

This shader supplies a deterministic storage-buffer payload so the test can check that compute pipelines created while multiple host threads use the same pipeline cache execute correctly. The synchronization property is the pipeline-cache access, not shader-side synchronization.

#### Structural Design

| Phase | Shader operation | Observable result |
|-------|------------------|-------------------|
| Interface | Declare a runtime array of signed 32-bit integers at descriptor set `0`, binding `0`. | The host can bind its 64-byte storage buffer. |
| Index | Read `gl_GlobalInvocationID.x` into `ndx`. | Each invocation selects its own output element. |
| Write | Convert `ndx` to `int` and store it at `sb_out.result[ndx]`. | 16 dispatched invocations produce `result[n] = n`. |

#### Shader Code

```glsl
#version 310 es

/// One invocation is launched per workgroup; the host dispatches 16 workgroups for this variant.
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

/// Host-provided storage buffer at descriptor set 0, binding 0; it contains the 16 checked int values.
layout(set = 0, binding = 0, std430) buffer Output
{
    int result[];
} sb_out;

void main (void)
{
    /// Global invocation X is the output index because this variant uses one invocation per workgroup.
    highp uint ndx = gl_GlobalInvocationID.x;
    /// The host later invalidates the allocation and requires each element to equal its index.
    sb_out.result[ndx] = int(ndx);
}
```

#### Additional Info

- `PipelineCacheComputeTest::initPrograms` creates `compute_0`, `compute_1`, and `compute_2`; the worker loop cycles through those three pipeline descriptions, while this walkthrough uses `compute_0` as the primary representative shader. [Source](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1196-L1244)
- `executeComputePipeline` binds the storage buffer at binding `0`, dispatches the selected execution count, inserts a compute-to-host barrier, and checks all 16 values for `ptr[ndx] == ndx`. [Source](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L366-L446)

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Shader variant | `compute_0` uses `gl_GlobalInvocationID.x` with 16 workgroups; `compute_1` uses one local invocation that loops over all 16 elements; `compute_2` uses 16 local invocations in one workgroup and reads `gl_LocalInvocationID.x`. All write the same `0..15` sequence. | [shader generation and execution counts](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1196-L1252) |
| Registered case | `pipeline_cache_compute` uses compute shader modules, a compute pipeline, and `vk.cmdDispatch`; the sibling `pipeline_cache_graphics` instead uses vertex variants plus a fixed fragment shader and a graphics draw. | [case registration](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1351-L1358) |
| Build configuration | Vulkan uses an empty pipeline-cache create flag set; Vulkan SC adds read-only application-storage cache flags and supplied initial cache data. The generated GLSL for this case is unchanged. | [pipeline-cache setup](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L799-L814) |

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
; Bound: 29
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource ESSL 310
               OpName %main "main"
               OpName %ndx "ndx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %Output "Output"
               OpMemberName %Output 0 "result"
               OpName %sb_out "sb_out"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_int ArrayStride 4
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %sb_out Binding 0
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
        %int = OpTypeInt 32 1
%_runtimearr_int = OpTypeRuntimeArray %int
     %Output = OpTypeStruct %_runtimearr_int
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
     %sb_out = OpVariable %_ptr_Uniform_Output Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_int = OpTypePointer Uniform %int
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
        %ndx = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %15 = OpLoad %uint %14
               OpStore %ndx %15
         %22 = OpLoad %uint %ndx
         %23 = OpLoad %uint %ndx
         %24 = OpBitcast %int %23
         %26 = OpAccessChain %_ptr_Uniform_int %sb_out %int_0 %22
               OpStore %26 %24
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each case creates a custom device exposing every queue from every family that supports the required compute or graphics flag. `MultiQueues` owns one resettable command pool per queue and uses a mutex when reserving or releasing a queue and its command buffer. That mutex never protects the pipeline cache.
- The case creates one pipeline cache and one initial pipeline, then executes that initial pipeline once. The source discards this warm-up execution's returned `TestStatus`.
- The case launches all workers with the same pipeline-cache handle and the same pipeline descriptions. Every worker repeatedly creates a fresh pipeline with that cache before executing it.
- Each execution allocates its own host-visible storage buffer and descriptor resources. The graphics path also creates its own color image, view, and framebuffer.
- Compute dispatches use `16`, `1`, and `1` workgroups for their three variants. Graphics draws use `16`, `1`, and `1` points.
- A pipeline barrier makes shader writes available to host reads. The test submits the command buffer, waits for completion, releases the queue, invalidates the allocation, and compares all 16 values with their indices.
- `ThreadGroup` catches worker exceptions, joins every worker, and combines their `ResultCollector` results. Any worker pipeline-creation exception, execution failure, or buffer mismatch makes the case fail.
- Vulkan SC uses read-only application-storage pipeline-cache data, two workers, and ten iterations. Its spin barrier coordinates per-iteration pipeline-pool reservation collection; it does not serialize cache access in the subprocess run.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `pipeline_cache_compute` | Incorrect concurrent handling of the shared `VkPipelineCache` during compute-pipeline creation; compute pipeline compilation or dispatch failure; storage-buffer visibility or result-production failure; host-side result-checking or queue-management failure. |
| `pipeline_cache_graphics` | Incorrect concurrent handling of the shared `VkPipelineCache` during graphics-pipeline creation; graphics pipeline, render-pass, or vertex-pipeline execution failure; storage-buffer visibility or result-production failure; host-side result-checking or queue-management failure. |

### Cause Analysis

#### Shared pipeline-cache concurrency failure

**Possible failure symptoms:** Pipeline creation throws or returns an error in one or more workers, or a pipeline created during concurrent cache use later produces an incorrect storage-buffer value.

**Possible implementation causes:** The implementation may fail to synchronize simultaneous internal reads or updates of the shared pipeline cache. This interpretation applies only after excluding failures in pipeline compilation, execution, and result observation. The cache is created without `VK_PIPELINE_CACHE_CREATE_EXTERNALLY_SYNCHRONIZED_BIT`, so the application does not owe cache-access serialization.

#### Pipeline creation or execution failure

**Possible failure symptoms:** A worker cannot create or run a compute or graphics pipeline, command submission fails, or the expected `0..15` sequence is incomplete or incorrect for one shader variant.

**Possible implementation causes:** The failing path may involve shader compilation, compute dispatch, graphics pipeline state, render-pass execution, or vertex-shader storage writes rather than cache locking itself. Comparing the failing leaf and shader variant is necessary before assigning the cause to cache concurrency.

#### Storage-buffer visibility or host observation failure

**Possible failure symptoms:** GPU work completes, but one or more mapped elements remain zero or contain a value other than their index.

**Possible implementation causes:** The shader-write-to-host-read barrier, memory invalidation, host-visible allocation handling, or result scan may be wrong. The same symptom can also come from a pipeline that executed incorrectly, so the final buffer alone does not isolate the failing layer.

#### Queue or worker-management failure

**Possible failure symptoms:** A worker cannot acquire or release a queue, throws an exception, or contributes a non-pass result when `ThreadGroup` joins the workers.

**Possible implementation causes:** The CTS queue bookkeeping, command-pool ownership, or worker aggregation path may fail independently of `VkPipelineCache`. Source-level investigation is needed if the failure occurs before or after the concurrent pipeline-creation call.

## Case Pruning

### Requirement-based pruning

- `pipeline_cache_compute` requires at least one queue family with `VK_QUEUE_COMPUTE_BIT`.
- `pipeline_cache_graphics` requires at least one queue family with `VK_QUEUE_GRAPHICS_BIT` and the `vertexPipelineStoresAndAtomics` feature.
- A missing required queue or feature produces a not-supported result rather than a test failure.
- Vulkan SC requires the offline cache and reservation data supplied through the CTS resource interface; the SC build also reduces the worker and iteration counts.

### Design-based pruning

The source registers only compute and graphics pipeline-cache cases. The three shader forms remain internal variants because they all produce the same checked payload and do not change the cache-synchronization contract. The file does not register a `synchronization2` counterpart and does not test caches created with `VK_PIPELINE_CACHE_CREATE_EXTERNALLY_SYNCHRONIZED_BIT`, because that flag would move serialization responsibility to the application.

## Key Takeaways

- Both registered leaves share one pipeline cache across concurrent host pipeline-creation calls without an application cache mutex.
- Compute and graphics paths use different queues, stages, and pipeline state, but both reduce execution correctness to the same exact `0..15` storage-buffer check.
- Queue allocation, command completion, and host visibility remain synchronized; those mechanisms support the test without serializing the object under test.
- The Vulkan and Vulkan SC mustpass lists own the same two registered paths. `synchronization2.internally_synchronized_queues` tests a different object and contract.
- The initial warm-up execution performs the normal result comparison, but its returned status is currently ignored by both `iterate()` implementations. Worker executions still cycle through every variant and determine the reported result.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `MultiQueues`, `createQueues()` | [queue management and custom-device setup](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L98-L364) | Shows the mutex boundary and the pool of matching queues. |
| `executeComputePipeline()` | [compute execution and check](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L366-L446) | Shows per-execution resources, dispatch, barrier, wait, and exact payload comparison. |
| `executeGraphicPipeline()` | [graphics execution and check](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L448-L553) | Shows the render path, vertex-stage storage writes, barrier, and comparison. |
| `ThreadGroup`, `CreateComputeThread`, `CreateGraphicThread` | [worker control](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L555-L763) | Shows exception aggregation, shared-cache ownership, repeated creation, and Vulkan SC barriers. |
| Test instances | [compute](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L765-L897), [graphics](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L898-L1166) | Creates the cache, runs the unchecked warm-up, and launches workers. |
| Test definitions and factory | [cases and registration](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedObjectsTests.cpp#L1182-L1360) | Defines shader variants, support checks, exact test names, and the family root. |
| Vulkan pipeline-cache semantics | [Pipeline Cache Objects](../../../../vulkan-docs/src/chapters/pipelines.adoc#L8050-L8075) | States that pipeline-creation use is internally synchronized unless the externally synchronized flag changes the contract. |
| Vulkan host-threading semantics | [Threading Behavior](../../../../vulkan-docs/src/chapters/fundamentals.adoc#L693-L732) | Defines application responsibility for externally synchronized parameters. |
| Vulkan mustpass | [default synchronization list](../../../mustpass/main/vk-default/synchronization.txt#L32244-L32245) | Confirms both `dEQP-VK.synchronization.internally_synchronized_objects` leaves. |
| Vulkan SC mustpass | [default synchronization list](../../../mustpass/main/vksc-default/synchronization.txt#L30-L31) | Confirms both `dEQP-VKSC.synchronization.internally_synchronized_objects` leaves. |
