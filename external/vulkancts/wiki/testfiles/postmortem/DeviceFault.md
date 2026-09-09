## Overview

**Core question:** Does Vulkan fault reporting preserve the count, wait, capacity, ordering, and optional-binary contracts around a controlled device loss?

- This page documents the implementation in `vktPostmortemCoreDeviceFaultTests.cpp`, registered as `postmortem.device_fault`, plus the separately packaged `VK_EXT_device_fault` implementation in `vktPostmortemDeviceFaultTests.cpp`.
- The KHR family tests an idle device, then a device deliberately lost by `abortEXT`. It checks report counts, timeout results, fill-query behavior, report ordering, one-at-a-time draining, asynchronous waiting, and vendor-binary bounds.
- The EXT family has two leaves, `real` and `fake`. `real` calls the extension through a custom device; `fake` replaces the interfaces with deterministic data. Both exercise the EXT count-then-fill call path, but the test logs the returned records instead of comparing every diagnostic field.
- The loss trigger uses a compute shader, so the shader is part of test setup and is analyzed below. Its store is not the correctness oracle. The host checks the device-fault API after the trigger returns `VK_ERROR_DEVICE_LOST`.
- The regular package selects the KHR factory and lists its paths in the default postmortem mustpass. The EXT factory is selected by the experimental package and is not part of that standard list ([package selection](../../../modules/vulkan/postmortem/vktPostmortemTests.cpp#L41-L65), [KHR registration](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L1088-L1163), [EXT registration](../../../modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp#L492-L507), [mustpass](../../../mustpass/main/vk-default/postmortem.txt#L1-L24)).

## Background Knowledge

- **Device loss:** `VK_ERROR_DEVICE_LOST` tells the application that the logical device can no longer be used for normal work. A fault report is diagnostic data collected by the implementation; querying it does not repair the device or identify a unique root cause for a failing GPU instruction.
- **Count-then-fill APIs:** An output query commonly has a discovery call that writes a count, followed by a fill call that receives caller-owned storage. The count returned by the first call is a capacity plan, not necessarily a promise about the contents of each record. This page checks both calls and the result code for boundary cases.
- **Timeouts:** The KHR report query receives a timeout in nanoseconds. `0` means do not wait; the source also uses `1` ns and `1` s to distinguish an immediately unavailable report from a bounded blocking wait.
- **Optional feature bits:** Enabling an extension name does not enable every feature exposed by it. The implementation queries `VkPhysicalDeviceFaultFeaturesKHR` or `VkPhysicalDeviceFaultFeaturesEXT`; vendor-binary tests additionally require `deviceFaultVendorBinary`.
- **Terminal report flag:** `VK_DEVICE_FAULT_FLAG_DEVICE_LOST_KHR` marks the report associated with device loss. The KHR ordering case requires at most one such record and requires it to be the last record when present.

## Registration Hierarchy

```text
postmortem.device_fault
├── no_fault
├── with_fault_base
├── with_fault_waitidle
├── real (experimental registration)
└── fake (experimental registration)
```

The first tree is the standard KHR factory. Each `with_fault_*` family contains the same six report-query leaves and four vendor-binary leaves; `waitidle` adds `USE_DEVICE_WAIT_IDLE` after the loss trigger. The second tree is the experimental EXT factory and is a separate package path ([KHR factory](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L1088-L1163), [EXT factory](../../../modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp#L492-L507)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| KHR fault state | `no_fault`, `with_fault_base`, `with_fault_waitidle` | Selects idle queries or queries after an induced loss; `waitidle` waits for device idle as an additional setup step. | [factory](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L1094-L1116) |
| KHR report operation | `max_fault_property_atleast_one`, `counts_query`, `very_short_timeout`, `blocking_query`, `zero_report_query`, `blocking_query_no_more_faults_after_device_lost`, `blocking_query_more_than_available`, `drain_query`, `async_query` | Selects property, count, timeout, fill capacity, ordering, draining, or concurrency behavior. | [report registration](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L1100-L1140) |
| KHR vendor operation | `vendor_binary_size_query`, `vendor_binary_data`, `vendor_binary_not_enough_space`, `vendor_binary_more_enough_space` | Selects size discovery, exact fill, undersized storage, or extra-capacity protection. | [vendor registration](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L1142-L1158) |
| EXT implementation | `real`, `fake` | Selects the real extension path or synthetic interfaces. | [EXT registration](../../../modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp#L492-L507) |
| Wait duration | `0`, `1` ns, `1` s | Separates nonblocking queries, a very short timeout, and bounded polling after loss. | [constants and conversion](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L58-L60) |

The KHR `with_fault_*` groups repeat the report leaves intentionally. The repeated cases change only the post-loss setup option, so a result can be compared without changing the query being tested.

## Behavior Parameters

The primary behavioral axis is the registered KHR report operation. Vendor operations form a second group because they query `vkGetDeviceFaultDebugInfoKHR`, while `real` and `fake` use the distinct EXT API.

### `max_fault_property_atleast_one` — usable report capacity

The idle case reads `maxDeviceFaultCount` from `VkPhysicalDeviceFaultPropertiesKHR` and fails if it is less than one. It does not demand a particular implementation-reported count ([property check](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L468-L482)).

### `counts_query` — idle count result

With no submitted work and a zero timeout, the test expects `VK_TIMEOUT`, a count different from the sentinel, and a count of zero. This checks that a timeout still updates the output count ([count query](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L484-L510)).

### `very_short_timeout` — short wait result

The same idle state is queried with a one-nanosecond timeout. The expected result is `VK_TIMEOUT`, and the count must be zero. The test does not treat a timeout as a failure when no report exists; it treats the wrong result or stale count as a failure ([short timeout](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L512-L533)).

### `blocking_query` — count followed by fill

The test induces loss, polls with a one-second timeout up to 100 times until the query returns `VK_SUCCESS`, and requires a nonzero count. It then allocates that many initialized `VkDeviceFaultInfoKHR` records and fills them with a zero-timeout query that must also return `VK_SUCCESS` ([blocking query](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L535-L590)).

### `zero_report_query` — no caller capacity

After obtaining a nonzero report count, the test passes a zero report count and one initialized record. It expects `VK_INCOMPLETE`. This is a capacity boundary test; it does not require the zero-capacity call to return the records ([zero capacity](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L592-L635)).

### `blocking_query_no_more_faults_after_device_lost` — terminal ordering

The test fills all available reports, counts records carrying `VK_DEVICE_FAULT_FLAG_DEVICE_LOST_KHR`, and requires exactly one. It also requires the flagged record to be last. The preceding records may vary; the source does not compare their text, addresses, or number ([ordering check](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L637-L699)).

### `blocking_query_more_than_available` — excess record protection

The first query discovers `faultCounts`. The fill query supplies five additional initialized records. The test requires success and compares every slot after the original count with its initialized copy. Those extra slots must remain unchanged ([excess capacity](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L701-L757)).

### `drain_query` — one-record consumption

The test repeatedly asks for one report. A result of `VK_INCOMPLETE` means more reports remain; `VK_SUCCESS` ends the fill sequence. After each call it performs a count-only query and checks that the presence or absence of remaining reports agrees with the fill result. The processed total must equal the initial count ([draining](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L760-L864)).

### `async_query` — wait concurrent with loss

A worker thread repeatedly performs a one-second count query. The main test waits briefly, induces loss, waits again, stops the worker, and returns its status. The worker passes only after it obtains a nonzero count and successfully fills the reports ([asynchronous query](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L866-L911)). The sleeps bound the test choreography; they do not define a required publication latency for implementations.

### Vendor binary operations — byte capacity

`vendor_binary_size_query` asks for `VkDeviceFaultDebugInfoKHR` with no destination and checks that `vendorBinarySize` is written. In the idle variant, the expected size is zero; in the loss variant, the sentinel must be replaced ([size query](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L916-L948)).

`vendor_binary_data` repeats the size query, allocates exactly the reported number of bytes, fills it, and checks the version-one header. A zero-size binary produces a quality warning because there is no payload to inspect, not a conformance failure ([binary fill](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L951-L990)).

`vendor_binary_not_enough_space` advertises one byte less than the reported size. It expects `VK_ERROR_NOT_ENOUGH_SPACE_KHR` and checks that the destination remains filled with `0xFE` ([undersized binary](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L993-L1035)). `vendor_binary_more_enough_space` adds 16 bytes, expects success, and checks that bytes beyond the original size remain `0xFE` ([extra binary capacity](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L1037-L1084)).

### EXT `real` and `fake` — count and fill

Both EXT leaves first call `getDeviceFaultInfoEXT` with `pFaultInfo == nullptr`. The call returns counts for address records, vendor records, and the binary size. The test then allocates arrays, enables the binary destination only when the feature bit is set, and performs the fill call. `VK_SUCCESS` is the pass condition. The fake interface returns two address records, two vendor records, and a deterministic version-one header; those values are logged rather than individually asserted ([fake data](../../../modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp#L196-L347), [EXT execution](../../../modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp#L444-L487)).

## Shader Analysis

The KHR loss cases do use a compute shader, so the trigger is not omitted from this page. `initProgram` emits the exact one-workgroup GLSL shown below only when `USE_SHADER_ABORT` is set. The shader writes `1` to a storage-buffer element and then calls `abortEXT`; the host does not read that value. The EXT source has no shader. This boundary matters: the walkthrough explains how the test reaches device loss, while the report fields and capacity rules remain host/API checks ([program generation](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L448-L464)).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.postmortem.device_fault.with_fault_base.blocking_query
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `with_fault_base` | Uses the KHR loss setup without the extra device-idle option. |
| `blocking_query` | Requires a count query after induced loss, followed by a fill query. |
| `USE_SHADER_ABORT` | Enables `VK_KHR_shader_abort` and emits the compute program that calls `abortEXT`. |

#### Purpose

This program creates the controlled `VK_ERROR_DEVICE_LOST` state needed by the KHR report tests. The store exercises the bound resource, but the test's pass condition begins with the host observing the loss and successfully retrieving reports.

#### Structural Design

| Phase | Shader action | Test consequence |
|---|---|---|
| Launch | One local invocation in one workgroup | The host submits exactly one dispatch. |
| Store | Write `1` at `data.outp[0]` | Confirms the shader has a valid storage-buffer access before termination; the value is not read back. |
| Abort | Call `abortEXT` with a fixed message | The implementation should enter the device-loss state used by the report query. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_abort : require
/// One invocation is requested by the source's execution layout.
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1)
/// Set 0, binding 0 is a host-created four-byte storage buffer; the host does not read it back.
layout(std430, set = 0, binding = 0) writeonly buffer Data { uint outp[]; } data;
void main()
{
  /// Store a value before aborting; this value is not the test oracle.
  data.outp[0] = 1;
  /// Deliberately request abnormal termination to exercise fault-report retrieval.
  abortEXT("Manually producing device faults!");
}
```

#### Additional Info

- The source adds `VK_KHR_SHADER_ABORT_EXTENSION_NAME` and chains `VkPhysicalDeviceShaderAbortFeaturesKHR` only for loss-triggering cases ([device creation](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L227-L264)).
- The generated program is stored in the `comp` collection entry and uses the source's default shader build target, SPIR-V 1.0. The default target is supplied by the CTS shader-program collection.
- The host allocates a host-visible storage buffer, descriptor set, compute pipeline, command buffer, and fence before the dispatch ([trigger setup](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L333-L412)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| `no_fault` versus `with_fault_*` | `no_fault` does not emit or execute `comp`; both loss groups emit this same compute program. | [program guard](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L448-L463) |
| `base` versus `waitidle` | The shader text is unchanged; the host either returns the induced loss state directly or calls `deviceWaitIdle` after waiting on the fence. | [submit path](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L405-L412) |
| Report operation | All KHR loss leaves use the same shader. The operation changes only the host query and its validation. | [loss registration](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L1113-L1160) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: comp
- Target SPIRV version: spirv1.0

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 25
; Schema: 0
               OpCapability Shader
               OpCapability Int8
               OpCapability AbortKHR
               OpCapability ConstantDataKHR
               OpExtension "SPV_KHR_abort"
               OpExtension "SPV_KHR_constant_data"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_abort"
               OpName %main "main"
               OpName %Data "Data"
               OpMemberName %Data 0 "outp"
               OpName %data "data"
               OpName %abortMessageLoadType "abortMessageLoadType"
               OpName %abortMessage "abortMessage"
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Data BufferBlock
               OpMemberDecorate %Data 0 NonReadable
               OpMemberDecorate %Data 0 Offset 0
               OpDecorate %data NonReadable
               OpDecorate %data Binding 0
               OpDecorate %data DescriptorSet 0
               OpDecorate %_arr_char_uint_36 UTFEncodedKHR
               OpDecorate %_arr_char_uint_36_0 UTFEncodedKHR
               OpMemberDecorate %abortMessageLoadType 0 Offset 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
       %Data = OpTypeStruct %_runtimearr_uint
%_ptr_Uniform_Data = OpTypePointer Uniform %Data
       %data = OpVariable %_ptr_Uniform_Data Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %uint_1 = OpConstant %uint 1
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
       %char = OpTypeInt 8 1
    %uint_36 = OpConstant %uint 36
%_arr_char_uint_36 = OpTypeArray %char %uint_36
%_arr_char_uint_36_0 = OpTypeArray %char %uint_36
         %20 = OpConstantDataKHR %_arr_char_uint_36 1970168141 2037148769 1869770784 1768125796 1679845230 1667855973 1634082917 1937009781 33
%abortMessageLoadType = OpTypeStruct %_arr_char_uint_36_0
%abortMessage = OpTypeStruct %_arr_char_uint_36
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpAccessChain %_ptr_Uniform_uint %data %int_0 %int_0
               OpStore %15 %uint_1
         %23 = OpCompositeConstruct %abortMessage %20
               OpAbortKHR %abortMessageLoadType %23
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The KHR support callback requires `VK_KHR_device_fault` and the `deviceFault` feature. Vendor-binary cases additionally require `deviceFaultVendorBinary`. Loss cases require `VK_KHR_shader_abort` and `shaderAbort`; unsupported cases are pruned as not supported ([support checks](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L415-L446)).
- `ContextWrapper` queries fault properties and features, creates a custom device with the KHR extension, and chains the shader-abort feature only when requested ([feature queries and device creation](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L95-L265)).
- The loss trigger obtains a universal queue, allocates a host-visible four-byte storage buffer, binds it at set 0/binding 0, builds the `comp` shader and compute pipeline, records `vkCmdDispatch(1, 1, 1)`, submits it with a fence, and waits. The source returns `VK_ERROR_DEVICE_LOST` for the base option; the waitidle option calls `deviceWaitIdle` and expects that call to report the loss ([submission](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L333-L412)).
- Count queries pass `pFaultReports == nullptr` and initialize their count to `DUMMY_VALUE` so failure to write the output is visible. Fill queries initialize each `VkDeviceFaultInfoKHR`, including `sType`, `pNext`, and a description sentinel, before passing storage to the driver ([initialization](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L85-L93)).
- Blocking cases use at most 100 one-second queries. This bounds the CTS loop while allowing fault records to become available after the loss. The asynchronous case uses a future and bounded sleeps; it stops the worker before collecting its result.
- Report text, addresses, instruction addresses, group identifiers, and vendor fields are logged. The KHR tests require only the explicitly checked count, result, terminal flag, and untouched-memory properties; they do not prescribe a particular vendor description or number of nonterminal records.
- For binary retrieval, the first debug-info call supplies the required size. The second call receives a caller-owned byte array. Exact size, one-byte-short, and 16-byte-extra arrays expose distinct capacity contracts.
- The EXT `iterate` path obtains counts, suppresses the binary destination when the feature bit is false, allocates the returned arrays, performs the fill call, logs them, and passes only when the fill result is `VK_SUCCESS` ([EXT iterate](../../../modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp#L444-L487)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `max_fault_property_atleast_one` | Invalid KHR fault-property reporting or unusable advertised report capacity. |
| `counts_query`, `very_short_timeout` | Incorrect idle timeout/result behavior or failure to write a zero count. |
| `blocking_query`, `async_query` | Fault publication, wait handling, or count-to-fill behavior after device loss. |
| `zero_report_query` | Incorrect `VK_INCOMPLETE` handling when caller capacity is zero. |
| `blocking_query_no_more_faults_after_device_lost` | Incorrect terminal flag count or report ordering. |
| `blocking_query_more_than_available` | Writing records beyond the available report count. |
| `drain_query` | Incorrect consumption or disagreement between fill and remaining-count queries. |
| `vendor_binary_size_query` | Failure to write the required binary size in idle or lost state. |
| `vendor_binary_data` | Incorrect binary fill or version-one header reporting. |
| `vendor_binary_not_enough_space` | Failure to reject undersized storage or modification of the destination before rejection. |
| `vendor_binary_more_enough_space` | Writing beyond the advertised payload. |
| EXT `real` or `fake` | Feature-chain, count/fill, pointer, or interface dispatch behavior. |

### Cause Analysis

#### Fault publication and timeout results

**Possible failure symptoms:** A sentinel count remains unchanged, an idle query returns something other than `VK_TIMEOUT`, a one-nanosecond query reports a nonzero count, or a post-loss blocking query never reaches `VK_SUCCESS`.

**Possible implementation causes:** The implementation may publish records later than the bounded polling permits, mishandle the timeout value, or fail to update the count on a timeout. The source does not identify which internal subsystem owns a bad result, so a failure needs investigation of the device-fault publication and query path.

#### Count-to-fill and report capacity

**Possible failure symptoms:** A successful count query is followed by a failed fill, the zero-capacity query does not return `VK_INCOMPLETE`, or initialized records after the available range change.

**Possible implementation causes:** The count and fill paths may disagree about available records, or the fill path may validate capacity after writing. The extra-slot comparison is specifically a caller-memory safety check; it does not prove that the returned records have semantically correct diagnostic fields.

#### Terminal ordering and draining

**Possible failure symptoms:** No record carries `VK_DEVICE_FAULT_FLAG_DEVICE_LOST_KHR`, multiple records carry it, the flagged record is not last, or the number processed one at a time differs from the initial count.

**Possible implementation causes:** Report assembly may violate the terminal-record rule, or successive queries may expose inconsistent consumption state. These cases localize the symptom to report bookkeeping and API behavior, not to a particular GPU instruction.

#### Vendor-binary bounds and header

**Possible failure symptoms:** `vendorBinarySize` remains a sentinel, the version-one header is not reported, an undersized query returns success or changes the `0xFE` destination, or extra bytes change.

**Possible implementation causes:** The implementation may calculate the required size incorrectly, copy before checking capacity, or copy beyond the payload it reports. A zero-size binary is recorded as a quality warning in data cases because the test has no bytes to inspect; it is not evidence that a nonzero vendor blob is universally required.

#### EXT interface path

**Possible failure symptoms:** The EXT fill call fails after the count call, including with the deterministic fake interface.

**Possible implementation causes:** Feature reporting, structure initialization, returned counts, pointer setup, or dispatch through the selected interface may be wrong. The fake path proves the caller's handling of synthetic records, but it does not validate real-driver diagnostic content.

## Case Pruning

### Requirement-based pruning

- All standard KHR cases require `VK_KHR_device_fault`, the `deviceFault` feature, and the instance properties-query functionality.
- Vendor-binary cases require `deviceFaultVendorBinary`; without it, the case is unsupported rather than a failed binary check.
- Loss-triggering cases require `VK_KHR_shader_abort` and `shaderAbort` so the test can create its controlled loss state.
- The EXT `real` case requires `VK_EXT_device_fault`; the fake case uses fake interfaces but still checks the reported fault feature through its fake instance interface ([EXT support](../../../modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp#L369-L394)).

### Design-based pruning

- The `base` and `waitidle` KHR variants repeat the same query matrix with one post-submission difference. This isolates the effect of the idle wait.
- Idle report cases do not emit the abort shader. The source guard in `initProgram` keeps the program collection empty when `USE_SHADER_ABORT` is not set ([program guard](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L448-L463)).
- The shader writes one buffer element before aborting because the trigger is a valid compute submission, not because the buffer value is an oracle. Passing does not establish coverage for spontaneous hardware faults or arbitrary fault causes.
- The regular package selects `createDeviceFaultTestsKHR`; the experimental `real` and `fake` leaves are a separate registration and package boundary ([package split](../../../modules/vulkan/postmortem/vktPostmortemTests.cpp#L41-L65)).

## Key Takeaways

- The standard family tests the host-visible contract around `vkGetDeviceFaultReportsKHR` and `vkGetDeviceFaultDebugInfoKHR`, not a particular vendor's fault diagnosis.
- `VK_TIMEOUT`, `VK_INCOMPLETE`, and `VK_ERROR_NOT_ENOUGH_SPACE_KHR` each describe a different boundary and are expected in different leaves.
- The device-loss report must be present exactly once and last when the ordering case succeeds.
- Count-to-fill queries must respect the caller's report and byte capacities, including leaving excess initialized storage untouched.
- The compute shader is a controlled loss trigger. Its `abortEXT` call is why shader analysis is included, but no shader output is used as the pass/fail result.
- The KHR and EXT implementations share a category label but use different APIs, registration factories, feature structures, and package coverage.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| KHR feature and property queries | [query helpers](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L85-L143) | Defines the feature/property structures and sentinel initialization. |
| KHR device setup | [ContextWrapper](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L145-L265) | Shows extension enabling and conditional shader-abort chaining. |
| Controlled loss trigger | [submitShaderAbortDeviceFault](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L333-L412) | Creates the buffer, pipeline, dispatch, fence, and expected loss result. |
| Shader program | [initProgram](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L448-L464) | Provides the exact compute source and the abort-only generation guard. |
| Idle KHR reports | [property/count/timeout cases](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L468-L533) | Checks properties, zero counts, and timeout outputs. |
| Loss KHR reports | [blocking and ordering cases](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L535-L757) | Checks retrieval, zero capacity, terminal ordering, and excess slots. |
| Stateful and concurrent retrieval | [drain and async cases](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L760-L911) | Checks one-record consumption and waiting from another thread. |
| KHR vendor binary | [debug-info cases](../../../modules/vulkan/postmortem/vktPostmortemCoreDeviceFaultTests.cpp#L916-L1084) | Checks size, header, undersized storage, and extra capacity. |
| EXT fake implementation | [fake interfaces](../../../modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp#L196-L347) | Supplies deterministic counts, records, and binary data. |
| EXT execution and support | [EXT case](../../../modules/vulkan/postmortem/vktPostmortemDeviceFaultTests.cpp#L369-L487) | Shows real/fake selection, count-then-fill, logging, and pass condition. |
| Registration and package boundary | [factories and package selection](../../../modules/vulkan/postmortem/vktPostmortemTests.cpp#L41-L65) | Distinguishes standard KHR and experimental EXT coverage. |
