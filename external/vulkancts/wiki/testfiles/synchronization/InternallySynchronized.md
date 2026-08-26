## Overview

**Core question:** Can four host threads submit different operations to one queue created with `VK_DEVICE_QUEUE_CREATE_INTERNALLY_SYNCHRONIZED_BIT_KHR` without an application-side queue mutex?

- [`vktSynchronizationInternallySynchronizedTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp) implements the `synchronization2.internally_synchronized_queues` test family.
- The family generates 183 test case leaves in the default synchronization2 mustpass: 49 without WSI and 134 with a WSI platform prefix.
- Threads 1 and 2 always run legacy-submit image draws. Threads 3 and 4 independently run a synchronization2 submit, sparse binding, WSI, debug-utils, performance-query, low-latency, or device-idle operation.
- The page explains the generated dimensions, queue setup, concurrent execution, result checks, support gates, and the current result-propagation behavior.

## Background Knowledge

- Vulkan normally requires the application to externally synchronize queue access. `VK_DEVICE_QUEUE_CREATE_INTERNALLY_SYNCHRONIZED_BIT_KHR` creates a queue that does not require that external synchronization. The feature and queue flag must be enabled together; see [`VkDeviceQueueCreateInfo` requirements](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L3621-L3627).
- `vkQueueSubmit` and `vkQueueSubmit2` express queue submission through different structures. This family uses the legacy form for the fixed `small` and `large` draws and selects the synchronization2 form for `small2` and `large2`.
- A queue wait idle call waits for previously submitted work on that queue to finish. Draw workers use it before host reads; sparse workers wait on fences before inspecting their output.

## Registration Hierarchy

The family is registered only in the synchronization2 category.

```text
synchronization2.internally_synchronized_queues
└── small2_small2 (testType1/testType2, optional WSI platform, and WSI operation order vary)
```

The generated forms are `<testType1>_<testType2>` and `<wsiPlatform>_<testType1>_<testType2>` when either operation is `wsi`.

- `<testType1>` takes `small2`, `large2`, `bind_sparse`, `wsi`, `debug_utils`, `performance_configuration`, `out_of_band`, or `device_wait_idle`.
- `<testType2>` takes the same eight values.
- `<wsiPlatform>` takes `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, or `xlib`.

The dispatcher adds [`createInternallySynchronizedTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L140) only to the synchronization2 group and excludes it from Vulkan SC builds. The legacy `synchronization.internally_synchronized_objects` family belongs to [`InternallySynchronizedObjects.md`](InternallySynchronizedObjects.md) and tests a different object.

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|---|---|---|---|
| Fixed worker operation | `small`, `large` | Threads 1 and 2 always render the small and large images through `vkQueueSubmit`. | [`CaseThread::run()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L588-L620) |
| Variable operation 3 | `small2`, `large2`, `bind_sparse`, `wsi`, `debug_utils`, `performance_configuration`, `out_of_band`, `device_wait_idle` | Selects the operation executed by thread 3 and contributes the generated case name. | [`TestType` and `getTestName()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L47-L90) |
| Variable operation 4 | The same eight values as variable operation 3 | Selects the operation executed by thread 4. The generator visits the 8 by 8 Cartesian product. | [`tests` and nested generation loops](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1666-L1688) |
| WSI type | `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, `xlib` in the default mustpass | Adds the platform prefix when either variable operation is `wsi`. The exact available list comes from the build's WSI enumeration. | [`wsi::TYPE_LAST` generation](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1690-L1705) |
| Queue creation | `QUEUE_CREATION_SINGLE_QUEUE`, `QUEUE_CREATION_FIRST_INTERN_SYNCED`, `QUEUE_CREATION_LAST_INTERN_SYNCED`, `QUEUE_CREATION_TWO_INTERN_SYNCED_USE_FIRST`, `QUEUE_CREATION_TWO_INTERN_SYNCED_USE_LAST` | Selects which queue-create entry carries the internal-synchronization flag and which queue `vkGetDeviceQueue2` retrieves. | [`QueueCreationType`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L92-L99), [queue setup](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1428-L1566) |
| Queue-family relation | Same or different queue family | Controls whether the requested queues come from one family or two families. | [`sameQueueFamily`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1679-L1686) |
| Execution count | Draw: 1,000 iterations for small forms and 50 for large forms; WSI: 700; sparse: 500; performance and device idle: 1,000 | Repeats each operation while other threads use the same queue. | [`CaseThread::run()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L588-L620) |
| Default registration coverage | 49 non-WSI leaves and 134 WSI leaves | Counts registered names, not cases guaranteed to execute on every device. | [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt) |

## Behavior Parameters

The primary behavioral axis is the pair of variable operation values, `testType3` and `testType4`. Their values change the Vulkan operations issued concurrently; queue creation and queue-family dimensions configure the same concurrency property.

### `small2` and `large2`: synchronization2 image draws

These operations use `vkQueueSubmit2` instead of `vkQueueSubmit`. `small2` renders and checks an 8x8 image; `large2` renders and checks a 4096x4096 image. The fixed `small` and `large` threads provide concurrent legacy-submit work on the same queue.

### `bind_sparse`: sparse binding and copy

The worker binds sparse buffer or image memory with `vkQueueBindSparse`, submits copy work, and checks the copied data. It requires sparse binding and sparse residency for 2D images.

### `wsi`: acquire, draw, and present

The worker acquires a swapchain image, submits a draw that waits for the acquire semaphore and signals a present semaphore, presents the image, and waits for the queue. The generated case name includes the selected WSI platform.

### `debug_utils`: queue debug labels

The worker places debug-utils labels around queue work and inserts a label after submission. It also performs the ordinary draw result check. The case requires `VK_EXT_debug_utils`.

### `performance_configuration`: Intel performance configuration

The worker initializes the Intel performance API, resets and brackets a query, sets a performance configuration on the queue, submits the command buffer, waits for the queue, and releases the configuration. The case requires `VK_INTEL_performance_query`.

### `out_of_band`: NV low-latency notification

The worker calls `vkQueueNotifyOutOfBandNV` with the render queue type before drawing, then checks the draw result. The case requires `VK_NV_low_latency2`.

### `device_wait_idle`: device-wide wait during queue use

The worker submits a 16 MiB buffer copy and calls `vkDeviceWaitIdle`. The operation tests this device wait while other threads submit work to the same internally synchronized queue.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.synchronization2.internally_synchronized_queues.small2_small2
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `testType1=small`, `testType2=large` | The first two worker threads use the fixed legacy-submit draw operations; `small` renders an 8x8 image and `large` renders a 4096x4096 image. |
| `testType3=small2`, `testType4=small2` | Both variable worker threads use the synchronization2 draw path, so the case exercises two concurrent `vkQueueSubmit2` calls alongside the fixed legacy draws. |
| `queueCreation=QUEUE_CREATION_SINGLE_QUEUE`, `sameQueueFamily=true` | For the first pair in the generator, `(i + j) % 5` selects the single-queue mode and `i % 2 == 0` selects the same-family arrangement; the retrieved queue carries `VK_DEVICE_QUEUE_CREATE_INTERNALLY_SYNCHRONIZED_BIT_KHR`. |

#### Purpose

This representative shader pair produces the deterministic 8x8 color gradient that the draw worker copies back and validates while four host threads use one internally synchronized queue. The shader itself is intentionally simple; the synchronization2 queue submission and concurrent execution are the tested property.

#### Structural Design

| Stage | Input / computation | Output and validation role |
|---|---|---|
| Vertex | `gl_VertexIndex` selects one of four corners, producing `(0,0)`, `(1,0)`, `(0,1)`, or `(1,1)`. | Passes the corner coordinate through location 0 and maps it to clip space for a full-rectangle draw. |
| Fragment | Reads the interpolated location-0 `texCoord`. | Writes `(texCoord.x, texCoord.y, 0, 1)` to the color attachment; the host-side 8x8 result scan checks the red and green channels. |

#### Shader Code

##### Vertex Shader

```glsl
#version 450

/// Location 0 carries the corner coordinate to the fragment stage.
layout (location=0) out vec2 texCoord;

void main()
{
    /// The four-vertex draw uses the two low index bits as the rectangle corners.
    texCoord = vec2(gl_VertexIndex & 1u, (gl_VertexIndex >> 1u) & 1u);
    /// Convert the 0..1 corner coordinate into clip-space position.
    gl_Position = vec4(texCoord * 2.0f - 1.0f, 0.0f, 1.0f);
}
```

##### Fragment Shader

```glsl
#version 450

/// The color attachment receives the gradient payload checked by runDraw().
layout (location=0) out vec4 out_color;
/// This is the interpolated corner coordinate generated by the vertex stage.
layout (location=0) in vec2 texCoord;

void main()
{
    /// Preserve the interpolated coordinates in red and green; blue is zero and alpha is one.
    out_color = vec4(texCoord, 0.0f, 1.0f);
}
```

#### Additional Info

- The vertex shader is fixed for all draw variants; it matters here because its location-0 output is the source of the fragment shader's red/green validation payload. [`initPrograms()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1632-L1643) emits this exact pair.
- For `small2_small2`, `runDraw()` selects `vkQueueSubmit2` for both variable workers, while the fixed `small` and `large` workers use `vkQueueSubmit`; all four workers nevertheless use the same retrieved queue. [`runDraw()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1145-L1333)
- The host checker samples the copied 8x8 output and permits a one-byte red/green tolerance; the source returns `Pass` after joining the workers without consulting `hasFailed()`. [`iterate()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1420-L1584)

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| `testType3`, `testType4` | `small2` and `large2` share this shader pair; the draw extent changes from 8x8 to 4096x4096, while `small2`/`large2` select `vkQueueSubmit2` instead of `vkQueueSubmit`. The other operation values change the concurrent host operation, not the generated shader text. | [`initPrograms()` and `runDraw()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1145-L1333) |
| Fixed draw workers | `testType1=small` and `testType2=large` always use the same vertex/fragment sources; only their render extent and sampling stride differ. | [`getRenderArea()` and `runDraw()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1310-L1347) |
| Queue creation and family selection | These dimensions alter queue creation, feature setup, and the queue selected by `vkGetDeviceQueue2`; they do not alter either shader declaration or shader control flow. | [`iterate()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1428-L1566) |

#### SPIR-V

##### Vertex Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 43
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %texCoord %gl_VertexIndex %_
               OpSource GLSL 450
               OpName %main "main"
               OpName %texCoord "texCoord"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpDecorate %texCoord Location 0
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Output_v2float = OpTypePointer Output %v2float
   %texCoord = OpVariable %_ptr_Output_v2float Output
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
    %v4float = OpTypeVector %float 4
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
    %float_2 = OpConstant %float 2
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %13 = OpLoad %int %gl_VertexIndex
         %15 = OpBitcast %uint %13
         %17 = OpBitwiseAnd %uint %15 %uint_1
         %18 = OpConvertUToF %float %17
         %19 = OpLoad %int %gl_VertexIndex
         %20 = OpShiftRightArithmetic %int %19 %uint_1
         %21 = OpBitcast %uint %20
         %22 = OpBitwiseAnd %uint %21 %uint_1
         %23 = OpConvertUToF %float %22
         %24 = OpCompositeConstruct %v2float %18 %23
               OpStore %texCoord %24
         %31 = OpLoad %v2float %texCoord
         %33 = OpVectorTimesScalar %v2float %31 %float_2
         %35 = OpCompositeConstruct %v2float %float_1 %float_1
         %36 = OpFSub %v2float %33 %35
         %38 = OpCompositeExtract %float %36 0
         %39 = OpCompositeExtract %float %36 1
         %40 = OpCompositeConstruct %v4float %38 %39 %float_0 %float_1
         %42 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %42 %40
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 19
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %out_color %texCoord
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %out_color "out_color"
               OpName %texCoord "texCoord"
               OpDecorate %out_color Location 0
               OpDecorate %texCoord Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
   %texCoord = OpVariable %_ptr_Input_v2float Input
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %13 = OpLoad %v2float %texCoord
         %16 = OpCompositeExtract %float %13 0
         %17 = OpCompositeExtract %float %13 1
         %18 = OpCompositeConstruct %v4float %16 %17 %float_0 %float_1
               OpStore %out_color %18
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each case creates a custom device because the default context device does not create the requested queue flags. It enables `VK_KHR_internally_synchronized_queues` and `VK_KHR_synchronization2`, then enables `internallySynchronizedQueues` and `synchronization2` through the feature chain in [`iterate()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1515-L1551).
- The source first looks for a graphics queue family. Sparse cases add `VK_QUEUE_SPARSE_BINDING_BIT` to the required flags. When the requested queue count or two-family arrangement is unavailable, the source falls back to one queue where possible; when no suitable queue exists, it reports not supported. The fallback condition at [lines 1462-1475](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1462-L1475) accepts any overlap with the required flags instead of requiring all flags, so a sparse case can select a queue that lacks either graphics or sparse-binding support.
- `vkGetDeviceQueue2` retrieves the queue with `VK_DEVICE_QUEUE_CREATE_INTERNALLY_SYNCHRONIZED_BIT_KHR` in `VkDeviceQueueInfo2`. Four `CaseThread` objects then start and join around that same queue.
- Draw workers submit command buffers, wait for the queue, and compare sampled red and green channels against the generated gradient with a one-byte tolerance. Large-image workers sample fewer pixels by using a larger stride.
- Sparse workers alternate sparse buffer and sparse image binding, submit copies, and wait on fences. The current checker has two source-level inconsistencies: the buffer path copies 4,096 bytes but checks 4,096 `uint32_t` elements, and the image path initializes a byte pattern but compares packed `uint32_t` elements with `j % 255`.
- WSI workers issue acquire, submit, present, and queue-wait operations, but the source does not inspect their return values. Performance workers wrap performance-configuration acquisition, queue configuration, and release with `VK_CHECK`, while their queue submit and wait calls are unchecked. Device-idle workers likewise do not inspect the return values from queue submit or `vkDeviceWaitIdle`.
- `CaseThread` records draw and sparse mismatches in `m_failed`, and `iterate()` joins all four workers before returning `tcu::TestStatus::pass("Pass")`. The current source does not inspect `CaseThread::hasFailed()` after joining, so those recorded mismatches do not change the reported CTS result. Calls wrapped in `VK_CHECK` throw on error instead of setting `m_failed`; `CaseThread` and the `de::Thread` trampoline do not catch those exceptions.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `small2` or `large2` | Synchronization2 queue submission, concurrent draw execution, image-to-buffer copy, or host pixel checking failed. |
| `bind_sparse` | Sparse memory binding, sparse image support, copy ordering, output-data checking, or the source's sparse queue-selection/checking defects were encountered. |
| `wsi` | WSI surface or swapchain acquisition, draw submission, presentation, or queue completion malfunctioned; these return values are not inspected by the current worker. |
| `debug_utils` | Debug-utils queue-label calls, concurrent draw submission, or draw result checking malfunctioned. |
| `performance_configuration` | Intel performance-query initialization, configuration, or release failed; queue submit and wait results are unchecked. |
| `out_of_band` | NV low-latency notification, concurrent draw submission, or draw result checking malfunctioned. |
| `device_wait_idle` | Device-wide wait, buffer-copy submission, or concurrent queue use malfunctioned; queue submit and device-wait results are unchecked. |
| Any value with a recorded draw or sparse mismatch | The worker observed incorrect output, but the current `iterate()` implementation does not propagate `hasFailed()` into the final test status. |

### Cause Analysis

#### Internally synchronized queue access is incorrect

**Possible failure symptoms:** Vulkan queue operations fail, a worker cannot complete, or a combination of operations behaves differently when four threads use the same queue concurrently.

**Possible implementation causes:** The implementation may fail to provide the queue's required internal synchronization or may mishandle the `VK_DEVICE_QUEUE_CREATE_INTERNALLY_SYNCHRONIZED_BIT_KHR` flag when several host threads call queue functions. The failing operation and queue-creation combination are needed to separate queue synchronization from the operation-specific behavior.

#### Operation-specific execution or completion is incorrect

**Possible failure symptoms:** A sparse copy returns unexpected data, a WSI operation fails, a performance configuration call returns an error, or a device wait does not complete. Draw and sparse workers can also set `m_failed` after an output mismatch.

**Possible implementation causes:** The selected operation may have an independent extension, feature, submission, resource, or completion defect. The source does not identify a fixed hardware, driver, or host location for these failures; investigation should follow the failing operation and its support path.

#### Draw or sparse result observation is incorrect

**Possible failure symptoms:** A sampled draw pixel differs from the generated gradient by more than one byte per channel, or sparse output differs from `0x12345678` or the `j % 255` pattern.

**Possible implementation causes:** The failure could arise from rendering or sparse-copy execution, image or buffer synchronization, host-visible memory handling, or the test's result scan. The sparse checker itself has byte-versus-`uint32_t` size and pattern mismatches. Because `iterate()` ignores `CaseThread::hasFailed()`, a recorded mismatch does not appear as a failed CTS result; source-level investigation is needed to determine the observed outcome.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_internally_synchronized_queues`, `VK_KHR_synchronization2`, and the `internallySynchronizedQueues` and `synchronization2` features.
- WSI cases require the selected platform surface support and `VK_KHR_swapchain`.
- `debug_utils` requires `VK_EXT_debug_utils`; `performance_configuration` requires `VK_INTEL_performance_query`; and `out_of_band` requires `VK_NV_low_latency2`.
- `bind_sparse` requires sparse binding, sparse residency for 2D images, a graphics queue with sparse-binding support, and a sparse image format supported by the implementation.
- Missing required queue families or queue counts produce a not-supported result. The source falls back to a single queue when a requested multi-queue arrangement is unavailable.

### Design-based pruning

- Threads 1 and 2 are fixed to `small` and `large`; the generator varies only the eight operation types assigned to threads 3 and 4.
- WSI names are generated for each supported WSI type. The generator omits the Android double-WSI combination because the CTS activity does not support multiple concurrent WSI windows.
- The generator selects one of five queue-creation modes with `(i + j) % queueCreation.size()`, rather than registering every queue-mode and queue-family combination as a separate case.
- The factory is excluded from Vulkan SC builds, so this family has no Vulkan SC registration.

## Key Takeaways

- The family tests concurrent host access to one queue created with the internally synchronized queue flag, not the legacy pipeline-cache behavior in `internally_synchronized_objects`.
- The two variable operation dimensions combine synchronization2 submission, sparse binding, WSI, debug labels, performance configuration, low-latency notification, and device idle with fixed legacy-submit draws.
- Queue creation and queue-family variants change which internally synchronized queue is used; they do not create separate registered hierarchy levels.
- Draw and sparse workers contain concrete output checks, but the current source returns pass after joining without reading `CaseThread::hasFailed()`. The sparse checker and sparse-queue fallback also contain the source inconsistencies described above, and several WSI, queue-submit, queue-wait, and device-wait return values are unchecked. These CTS source defects remain unresolved and are not repaired by this documentation page.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `createInternallySynchronizedTests()` | [test-family registration](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1657-L1717) | Defines the family, the eight variable operations, WSI naming, and generated leaves. |
| `createTestsInternal()` | [synchronization2 dispatcher](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L140) | Shows that this factory belongs to synchronization2 and is excluded from Vulkan SC. |
| `InternallySynchronizedQueuesTestInstance::iterate()` | [custom device and queue setup](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1420-L1584) | Selects queue families, enables features, retrieves the queue, starts workers, and returns the current result. |
| `InternallySynchronizedQueuesTestCase::checkSupport()` | [support checks](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1607-L1630) | Defines extension, feature, and queue-operation requirements. |
| `CaseThread::run()` | [worker iteration counts](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L588-L620) | Selects repetition counts for each operation type. |
| `runQueueBindSparse()` | [sparse binding and checks](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L936-L1060) | Binds sparse buffer or image memory and validates copied data. |
| `runPerformanceConfiguration()`, `runDeviceWaitIdle()` | [queue operation workers](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1062-L1143) | Implements the performance-query and device-idle paths. |
| `runDraw()` | [draw, submit, WSI, and pixel checks](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1145-L1333) | Implements labels, out-of-band notification, acquire/present, submission, and draw validation. |
| `de::Thread` trampoline | [thread entry and join](../../../../../framework/delibs/decpp/deThread.cpp#L69-L107) | Shows that the thread wrapper invokes `run()` directly and does not transport worker exceptions through `join()`. |
| Internally synchronized queue semantics | [Vulkan queue flags](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L3641-L3647) | Defines the queue flag's no-external-synchronization meaning. |
| Default registration coverage | [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt) | Confirms the 183 registered synchronization2 paths. |
| Synchronization2 category context | [category Background Knowledge](../../categories/synchronization2.md#background-knowledge) | Places this family in the synchronization2 category and distinguishes it from the legacy family. |
