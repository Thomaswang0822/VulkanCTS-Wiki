## Overview

**Core question:** Does a Vulkan SC device report an empty fault set correctly and accept callback configuration with and without record storage?

- `vktFaultHandlingTests.cpp` implements and registers four leaves under `sc.fault_handling`: two fault queries and two device-creation checks.
- The query cases call `vkGetFaultData` with `VK_FAULT_QUERY_BEHAVIOR_GET_AND_CLEAR_ALL_FAULTS`. They expect an empty result and compare the return code, the unrecorded-fault flag, and the record count. The array case also checks two fields in each preinitialized record.
- The callback cases supply `VkFaultCallbackInfo` during creation of a custom device. They differ in whether they allocate fault-record storage. Their callback discards its arguments.
- This is a host-API test, not a fault-injection workload. The walkthroughs below trace the query's output checks and the callback configuration's route through the device-creation helper. Neither path runs a shader.

[Query and callback implementations](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L59-L219) · [registration](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L223-L284).

## Background Knowledge

- `VkFaultData` describes a fault through a `faultLevel` and `faultType`, together with the Vulkan structure header (`sType` and `pNext`). Initializing record fields to known values lets a caller detect changes to those fields after an API call. This is a field comparison, not a byte-for-byte memory comparison.
- `vkGetFaultData` has separate outputs for the unrecorded-fault flag, the record count, and optional record storage. The count and flag carry information even when the caller supplies no `pFaults` array. An allocated array does not imply that the implementation must return a record.
- A Vulkan `pNext` chain connects extra structures to a base structure. `VkFaultCallbackInfo` connects a callback function and its record-storage description to device creation. Supplying that structure and observing a callback invocation are different operations.
- Vulkan SC exposes `maxQueryFaultCount` and `maxCallbackFaultCount` as device properties. These are storage capacities used by the two interfaces; do not read their values as numbers of faults that must already exist.

These are the structures and output fields used by the [query setup](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L64-L85) and [callback-info setup](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L164-L188).

## Registration Hierarchy

```text
sc.fault_handling
├── get_fault_data
└── fault_callback_info
```

`createTests` names the parent group `sc`, and `createChildren` attaches `createFaultHandlingTests` to it. The fault-handling factory names its group `fault_handling`; it then adds the two children above. This establishes the path from the SC category to the implemented families without inferring a group name from a filename.

[SC parent registration](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L65) · [fault-handling factory](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L223-L284).

The query family adds the intermediate node `get_and_clear_all_faults`, then the leaves `null` and `array`. The callback family adds its two leaves directly. Registration order puts query cases before callback cases; the default mustpass lists callback cases first. That ordering difference does not change membership.

The exact default selection, in file order, is:

| Mustpass line | Complete case path |
|---|---|
| 141 | `dEQP-VKSC.sc.fault_handling.fault_callback_info.create_device_with_callback_with_fault_data` |
| 142 | `dEQP-VKSC.sc.fault_handling.fault_callback_info.create_device_with_callback_without_fault_data` |
| 143 | `dEQP-VKSC.sc.fault_handling.get_fault_data.get_and_clear_all_faults.array` |
| 144 | `dEQP-VKSC.sc.fault_handling.get_fault_data.get_and_clear_all_faults.null` |

[`mustpass/main/vksc-default/sc.txt#L141-L144`](../../../mustpass/main/vksc-default/sc.txt#L141-L144) contains all four leaves. It is the selection used here, rather than a Vulkan non-SC mustpass or a name inferred from another page.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Family | `get_fault_data`, `fault_callback_info` | Changes the observed operation from a query on the context device to creation of a custom device. | [Factory](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L228-L280) |
| Query behavior | `get_and_clear_all_faults` | Selects `VK_FAULT_QUERY_BEHAVIOR_GET_AND_CLEAR_ALL_FAULTS`; the behavior array has no other entry. | [Behavior array](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L233-L239) |
| Query output form | `null`, `array` | Maps to `FHF_NULL` and `FHF_ARRAY`, changing the final query argument and whether the test scans record fields. | [Output-form array](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L241-L259) |
| Callback storage | `create_device_with_callback_with_fault_data`, `create_device_with_callback_without_fault_data` | Maps to `allocateFaultData == true` or `false`. Controls vector population and `pFaults`, while both cases supply `testFaultCallback`. | [Callback parameters](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L266-L278) |
| Query capacity | Runtime `maxQueryFaultCount` | Sets the initial `faultCount`, vector length, and array-validation loop bound. It is not a path component. | [Initialization](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L64-L79), [scan](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L127-L129) |
| Callback capacity | Runtime `maxCallbackFaultCount` | Sets vector length when storage allocation is enabled. It does not create more leaves. | [Allocation](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L164-L184) |

The nested registration loops combine one query behavior with two output forms. The callback registrations use two explicit Boolean parameter values. These are separate families, not a Cartesian product of query forms and callback forms.

`FHF_UNUSED` appears in the C++ enum, but no case uses it. Passing an unrecognized `faultValue` would reach an `InternalError`; that defensive branch is not a registered negative test. [Enum and parameters](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L46-L57) · [switch default](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L137-L138).

## Behavior Parameters

The family is the main behavioral choice: it determines whether CTS validates returned query data or checks that device creation accepts a supplied callback description. Within each family, the storage form changes the exercised API path.

### `get_fault_data` — query an empty fault set

Both leaves expect no recorded or unrecorded faults. The source performs no fault injection before querying the existing context device. It also performs no initial clearing query to establish an empty baseline. The empty state is the expectation tested by the call, rather than a state demonstrated by an earlier preparation step.

The behavior name includes “clear,” but this test never places a known record in the fault set and then checks its removal. A passing case therefore gives no evidence about clearing a non-empty set or about ordering records across repeated queries. [Complete query function](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L59-L142).

#### `null`

`pFaults` is `nullptr`, so the test observes the return code, flag, and count without receiving an array of records. The function still constructs its local vector before the switch; it simply does not pass that vector to the driver or scan it in this branch. This leaf is not the first step of a count-query/allocate/re-query sequence. It ends after one call and the three scalar checks. [Null branch](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L64-L105).

#### `array`

`pFaults` is `faults.data()`. The vector contains `maxQueryFaultCount` initialized structures. Alongside the three scalar checks, CTS compares each record's `faultLevel` and `faultType` with their original unassigned values. The comparison uses the allocated capacity as its loop bound, not the returned count of zero; that distinction makes unintended record-field changes observable. [Array branch](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L106-L135).

### `fault_callback_info` — create a device with callback configuration

These cases exercise the supplied `VkFaultCallbackInfo` through a custom device-creation call. Both set `pfnFaultCallback` to `testFaultCallback`. The storage Boolean changes the array description, not whether a callback function exists. [Callback-info construction](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L157-L188).

#### `create_device_with_callback_with_fault_data`

When `allocateFaultData` is true, CTS populates the vector with `maxCallbackFaultCount` records and supplies its size and `data()` pointer. Each record has the expected structure type, a null `pNext`, and unassigned level and type. Unlike the query array branch, this case never compares those record fields after device creation. Initialization alone is not a callback-data validation check. [Storage initialization](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L164-L186) · [creation and return](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L216-L218).

#### `create_device_with_callback_without_fault_data`

When `allocateFaultData` is false, CTS leaves the vector empty and sets `faultCount` to zero and `pFaults` to `nullptr`. It still supplies the same callback. The function contains no alternate expected error for this leaf: both configurations take the checked device-creation route and return `Pass` after it succeeds. [Parameter-to-structure mapping](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L167-L188) · [shared return](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L216-L218).

## Shader Analysis

No shader participates. These host-side cases query fault data or configure a device callback; they create no shader module or pipeline and submit no shader workload.

## Runtime Execution and Result Checking

- Query cases use the context device and host-allocated vectors. The test makes one query per leaf and converts explicit comparisons into a CTS `Pass` or `Fail`.
- Callback cases create an `InstanceWrapper` and a custom device. They supply no command workload and make no explicit payload comparison.
- The device-creation wrapper matters: it preserves an existing callback structure while supplying missing SC creation structures. The leaf's initial create info is not the whole chain ultimately passed to the driver.

### Host walkthrough: `get_fault_data.get_and_clear_all_faults.array`

This leaf exercises every explicit comparison in the query function. Use `N` below for the value read from `maxQueryFaultCount`; no particular hardware value is assumed.

1. CTS obtains the context's `DeviceInterface` and `VkDevice`.
2. It sets `unrecordedFaults = VK_TRUE` and `faultCount = N`.
3. It constructs `N` records. Each begins as `{VK_STRUCTURE_TYPE_FAULT_DATA, nullptr, VK_FAULT_LEVEL_UNASSIGNED, VK_FAULT_TYPE_UNASSIGNED}`.
4. It sets the local result accumulator `isOK` to true and `faultsModified` to false.
5. The registered `FHF_ARRAY` parameter selects the array branch and supplies the vector address to `getFaultData`.

[Setup](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L59-L80) · [call](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L106-L107).

The following call shape abbreviates the actual C++ statement; it is not a recorded driver trace:

```cpp
result = vk.getFaultData(device, testParams.queryBehaviour,
                         &unrecordedFaults, &faultCount, faults.data());
```

The input/output expectations are:

| Item | Before the call | Required afterwards | Check scope |
|---|---|---|---|
| Return code | No previous query result | `VK_SUCCESS` | Exact enum comparison |
| `unrecordedFaults` | `VK_TRUE` | `VK_FALSE` | Exact flag comparison |
| `faultCount` | `N` | `0u` | Exact count comparison |
| `faults[i].faultLevel` | `VK_FAULT_LEVEL_UNASSIGNED` | Same sentinel | All `i` from zero to `N - 1` |
| `faults[i].faultType` | `VK_FAULT_TYPE_UNASSIGNED` | Same sentinel | All `i` from zero to `N - 1` |

CTS checks the return code, then the flag, then the count, then the array fields. These are independent checks: a failed return-code comparison does not bypass the remaining comparisons. Each failure sets `isOK` to false. The scan sets `faultsModified` if either field differs in any record and emits one aggregate array-modification message afterwards. [Checks](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L109-L135).

The initial true flag makes an omitted flag write detectable. A missing count write is detectable when the initial capacity is nonzero; do not assume the initialization alone makes it detectable for every possible numeric value. The code contains no explicit minimum-capacity check. If the loop bound were zero, there would be no record-field comparisons. This describes the C++ control flow, not a claim that zero is a conformant device-property value.

The scope of “unchanged array” needs care. CTS initializes `sType` and `pNext`, but does not compare them after the call. It also performs no whole-structure `memcmp` or padding-byte comparison. The explicit oracle covers `faultLevel` and `faultType`, plus the scalar outputs. A changed header field alone would not trigger `faultsModified`. [Initialization](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L69-L76) · [actual comparison](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L127-L129).

Finally, `isOK` selects `tcu::TestStatus::pass("Pass")` or `tcu::TestStatus::fail("Fail")`. There is no second query to verify the cleared state and no callback observation attached to this result. [Final return](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L137-L142).

For the `null` sibling, replace the last call argument with `nullptr` and omit the array scan. The initial vector allocation and scalar starting values stay the same. Both leaves expect the same empty-result scalar values. [Null path](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L84-L105).

### Host walkthrough: callback configuration with fault data

The exact representative leaf is `dEQP-VKSC.sc.fault_handling.fault_callback_info.create_device_with_callback_with_fault_data`. Its Boolean parameter is true. It represents callback configuration with caller storage; the no-storage sibling changes the size and pointer fields described below.

1. CTS constructs `InstanceWrapper(context)` and initializes its local chain-head variable `pNext` to null.
2. It reads `maxCallbackFaultCount` from the context's SC properties and populates a local vector to that length.
3. It builds `VkFaultCallbackInfo`, assigning the vector length to `faultCount`, `faults.data()` to `pFaults`, and `testFaultCallback` to `pfnFaultCallback`.
4. It sets `faultCallBackInfo.pNext` to the previous chain head, then makes `&faultCallBackInfo` the new head.
5. It places that head in `VkDeviceCreateInfo::pNext` and calls `instance.createCustomDevice(&deviceCreateInfo)`.

[Callback setup and chain](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L157-L188) · [device-create info](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L190-L216).

The test supplies these device-creation fields:

| Field or structure | Value supplied by the leaf | Interpretation |
|---|---|---|
| Queue family | `0` | The source hardcodes this index; it does not search queue families here. |
| Queue count and priority | One queue, priority `1.0f` | Device creation requests a queue, but the leaf never submits work to it. |
| Device flags | `0u` | No extra create flag varies between callback cases. |
| Layers and extensions | Counts zero, name pointers null | The leaf does not request a layer or extension list. |
| `pEnabledFeatures` | `nullptr` | This base-structure field is null; the wrapper can still add an SC feature structure through `pNext`. |
| Initial `pNext` | Address of the local `VkFaultCallbackInfo` | The supplied callback structure enters the helper as part of the chain. |

[Queue and base create info](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L192-L214).

The helper selects a physical device with `vk::chooseDevice`, then uses the checked overload of `createCustomDevice`. That overload wraps `createDeviceInternal` in `VK_CHECK`. A creation error prevents it from returning a usable custom device to the leaf. [Checked helper](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L442-L462).

Inside `createDeviceInternal`, the helper copies the base create info. Under `CTS_USES_VULKANSC`, it performs three missing-structure checks:

| Structure | Helper behavior | Effect for these callback leaves |
|---|---|---|
| `VkFaultCallbackInfo` | Adds the context callback only if the chain has no fault callback info. | The leaf already supplied one, so the helper preserves `testFaultCallback` rather than replacing it. |
| `VkDeviceObjectReservationCreateInfo` | Adds default reservation info if absent. | The leaf supplied only callback info, so this SC setup joins the chain. |
| `VkPhysicalDeviceVulkanSC10Features` | Adds default SC feature info if absent. | A null base `pEnabledFeatures` does not mean the final call has no SC feature structure. |

The helper then calls `m_driver->createDevice` with the resulting create info. This is why callback creation can fail in shared setup as well as in callback-info handling. [SC chain completion and driver call](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L499-L535).

Back in the leaf, CTS stores the returned custom device in `resultingDevice` and returns `Pass`. It does not call `getFaultData` on that new device, submit a fault-producing workload, or inspect the vector. The local vector and callback-info structure remain in scope across the checked creation call. [Creation and return](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L216-L219).

In the no-storage sibling, the vector stays empty, `faultCount` is zero, and the ternary expression supplies a literal null `pFaults`. The supplied callback and helper route stay the same. For the with-storage form, describe the pointer as `faults.data()` rather than promising a non-null address independently of vector size. [Storage mapping](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L167-L186).

### Exact diagnostics and result limits

| Diagnostic text | Condition that emits it | Applies to |
|---|---|---|
| `Result is not VK_SUCCESS` | Query result differs from `VK_SUCCESS`. | Both query leaves |
| `unrecordedFaults is not VK_FALSE` | Output flag differs from `VK_FALSE`. | Both query leaves |
| `faultCount is not 0` | Output count differs from zero. | Both query leaves |
| `pFaults have been modified` | At least one level or type field differs from its sentinel. | Array query only |

[Null diagnostics](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L87-L104) · [array diagnostics](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L109-L135).

The query messages do not print the actual return code, flag, count, record index, or changed field value. Multiple messages can appear for one invocation because the checks do not stop after the first mismatch. The callback leaves provide no analogous local diagnostic table: their checked creation helper supplies the error path, and their normal return is `Pass`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `get_fault_data` / `null` | Empty-state reporting or scalar-output handling; the null destination is the distinguishing argument. |
| `get_fault_data` / `array` | The same query-output problems, or writes that change initialized record level/type fields. |
| `fault_callback_info` / `create_device_with_callback_with_fault_data` | Creation with the supplied callback/storage description, or a failure in shared instance/device setup. |
| `fault_callback_info` / `create_device_with_callback_without_fault_data` | Creation with zero record count and null storage while a callback is supplied, or shared setup failure. |

These are investigation areas derived from the exercised calls and comparisons. A failing leaf name alone does not establish a driver root cause.

### Cause Analysis

#### Empty-state or scalar-output handling

**Possible failure symptoms:** One or more of the three scalar query messages appears. The test may see a non-success result, an unrecorded-fault flag other than false, or a nonzero record count. [Scalar checks](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L87-L125).

**Possible implementation causes:** Output marshalling may fail to update a scalar, the null-destination query path may differ from the array path, or fault bookkeeping may expose a non-empty state. The source makes no preparatory clearing call and does not inject a known fault, so it cannot distinguish an unexpected existing fault from incorrect reporting. Obtain the actual outputs and fault history before attributing the failure to one of these areas.

#### Unexpected record-field changes

**Possible failure symptoms:** The array leaf logs `pFaults have been modified`. This means a level or type field changed somewhere in the capacity-sized vector; it does not identify which record or field. A header-only change is outside this comparison. [Sentinel scan](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L127-L135).

**Possible implementation causes:** The query path may write or initialize record fields even when returning an empty set. A non-empty response can also change fields and produce both the count diagnostic and the array diagnostic. Inspect the complete set of messages and the returned count before interpreting this as an isolated overwrite with zero returned records.

#### Callback-info creation and shared setup

**Possible failure symptoms:** The checked custom-device creation fails before the leaf reaches its `Pass` return, or setup fails before that call. The leaf has no callback invocation counter or payload assertion that could independently fail. [Leaf return](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L216-L218) · [checked creation](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L442-L462).

**Possible implementation causes:** Processing of the supplied callback structure, its count/pointer relationship, or the surrounding device setup may fail. The final call also includes default SC reservation and feature structures, and the queue request uses family index zero. Compare the two storage variants and inspect the failing creation result before isolating the callback-info path. Neither a pass nor a creation failure measures callback delivery or correctness of `incompleteFaultData`. [Creation inputs](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L180-L214) · [helper additions](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L501-L535).

## Case Pruning

### Requirement-based pruning

The fault-handling factory registers all four leaves without a support callback, a feature gate, or a property-dependent branch. The test bodies read the SC capacities but contain no per-leaf `NotSupported` or capacity-based skip. This is a statement about this source, not a guarantee that framework instance/device setup succeeds on any environment. [Factory](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L223-L284) · [test bodies](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L59-L219).

`maxQueryFaultCount` and `maxCallbackFaultCount` control runtime allocation, not registration membership. The source does not generate below-limit, at-limit, and above-limit variants, nor does it negotiate a different queue family inside the callback leaf.

### Design-based pruning

The implemented matrix contains one query behavior with two output forms and two callback-storage choices. It contains no fault injection, non-empty fault-record oracle, repeated get/clear sequence, callback invocation check, or incomplete-callback-data comparison. The inert callback discards all its parameters. These are coverage limits visible in the implementation; the source does not state a design rationale for omitting each alternative. [Registration matrix](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L233-L278) · [callback](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L144-L150).

The default SC mustpass lists exactly these four leaves. Do not count the query behavior group as another executable case or treat `FHF_UNUSED` as a missing default leaf. [Default selection](../../../mustpass/main/vksc-default/sc.txt#L141-L144).

## Key Takeaways

- The query oracle is an empty result: `VK_SUCCESS`, a false unrecorded-fault flag, and zero records. It does not demonstrate clearing a known non-empty set.
- The array leaf scans the whole allocated capacity, but checks only fault level and type. “Storage unchanged” without that qualification overstates the test.
- Both callback leaves supply a callback. They differ in record storage, and successful checked creation is their local acceptance condition.
- The helper preserves the supplied callback and adds missing SC creation structures. The leaf's initial `pNext` chain is only the starting point.
- These four leaves contain no shader workload or callback-payload validation. A failure needs the query diagnostics or creation error for useful localization.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Query parameters and initialization | [`vktFaultHandlingTests.cpp#L46-L80`](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L46-L80) | Separates enum values from registered cases and establishes initial outputs and records. |
| Null query | [`testGetFaultData#L82-L105`](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L82-L105) | Shows one call, three scalar checks, and exact messages. |
| Array query and final status | [`testGetFaultData#L106-L142`](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L106-L142) | Establishes the capacity-sized level/type scan and pass/fail reduction. |
| Callback body | [`testFaultCallback#L144-L150`](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L144-L150) | Proves that callback arguments are unused. |
| Callback storage and chain | [`testCreateDeviceWithFaultCallbackInfo#L152-L188`](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L152-L188) | Maps the Boolean parameter to count, pointer, and callback fields. |
| Device request and result | [`testCreateDeviceWithFaultCallbackInfo#L190-L219`](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L190-L219) | Queue family zero, one queue, checked helper call, and normal `Pass` return. |
| Custom-device helper | [`InstanceWrapper#L442-L462`](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L442-L462) | Device selection and checked creation failure propagation. |
| Final SC creation chain | [`createDeviceInternal#L499-L535`](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L499-L535) | Preserves existing callback info and adds missing reservation/features before the driver call. |
| Fault-handling registration | [`createFaultHandlingTests#L223-L284`](../../../modules/vulkan/sc/vktFaultHandlingTests.cpp#L223-L284) | Exact groups, behavior array, output forms, and four leaves. |
| SC parent | [`vktSafetyCriticalTests.cpp#L45-L65`](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L65) | Attaches the implementation group beneath `sc`. |
| Default SC mustpass | [`sc.txt#L141-L144`](../../../mustpass/main/vksc-default/sc.txt#L141-L144) | Confirms complete four-leaf default membership and exact package-prefixed paths. |
