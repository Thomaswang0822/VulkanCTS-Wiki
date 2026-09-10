## Overview

**Core question:** Can the implementation complete the long-name and label paths of debug utils and the name/tag/marker path of debug marker?

- Source file covered: [`vktApiDebugUtilsTests.cpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L1).
- Test category: `api`. Test family: `debug_utils`. Test case leaves: `long_labels_graphics`, `long_labels_transfer`, `long_labels_video_decode`, `debug_marker_graphics`.
- Core test idea: exercise the debug-utils long-label path and the debug-marker name/tag and begin/insert/end commands.
- The remaining sections cover the registered leaves, their parameters, execution, and pass/failure meaning.

## Background Knowledge

- **`VK_EXT_debug_utils` instance extension.** The extension provides host-callable entry points for attaching human-readable names to Vulkan objects (`vkSetDebugUtilsObjectNameEXT`), inserting debug label regions into command buffers (`vkCmdInsertDebugUtilsLabelEXT`), and inserting labels on queues (`vkQueueInsertDebugUtilsLabelEXT`). These calls are metadata; they do not change execution results. The extension must be enabled at instance creation, which the test does through a custom instance rather than the default context instance.
- **Object name and label strings.** The extension treats `pObjectName` and `pLabelName` as null-terminated C strings with no specified maximum length. The test deliberately uses a string longer than typical fixed-size internal buffers (`64 * 1024 + 1` characters) to exercise how the implementation handles oversized but spec-valid input.
- **Queue family capability masks.** `VkQueueFlags` exposes bits such as `VK_QUEUE_GRAPHICS_BIT`, `VK_QUEUE_COMPUTE_BIT`, `VK_QUEUE_TRANSFER_BIT`, and `VK_QUEUE_VIDEO_DECODE_BIT_KHR`. A queue family may expose any combination of these bits. The test selects a queue family by requiring some bits and excluding others, so each leaf exercises the same label stress path against a different queue capability profile.

## Registration Hierarchy

```text
api.debug_utils
├── long_labels_graphics
├── long_labels_transfer
├── long_labels_video_decode
└── debug_marker_graphics
```

The [factory](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L187-L215) registers three long-label leaves and `debug_marker_graphics`. The debug-marker and video-decode leaves are excluded from Vulkan SC.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `long_labels_graphics`, `long_labels_transfer`, `long_labels_video_decode` | Each leaf selects a different queue family capability profile for the shared long-label stress path. | [`createDebugUtilsTests()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L144-L167) |
| Required queue flags | `VK_QUEUE_GRAPHICS_BIT`, `VK_QUEUE_TRANSFER_BIT`, `VK_QUEUE_VIDEO_DECODE_BIT_KHR` | Selects which queue capability the queue family must expose. | [`vktApiDebugUtilsTests.cpp#L149-L162`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L149-L162) |
| Excluded queue flags | `0` for graphics; `VK_QUEUE_GRAPHICS_BIT \| VK_QUEUE_COMPUTE_BIT` for transfer and video decode | Restricts the queue family selection so transfer and video decode leaves run on non-graphics, non-compute queues when such a family exists. | [`vktApiDebugUtilsTests.cpp#L150-L161`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L150-L161) |
| Long label length | `64 * 1024 + 1` characters of `'x'` | One character longer than 64 KiB, intended to exceed typical fixed-size internal buffers. | [`vktApiDebugUtilsTests.cpp#L97`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L97) |
| Debug-utils target | buffer object name, command-buffer label, queue label | Exercises three attachment points on the same long string within a single test body. | [`vktApiDebugUtilsTests.cpp#L104-L127`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L104-L127) |
| Command content | `vkCmdFillBuffer` emitted only when `params.required` overlaps `VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT | VK_QUEUE_TRANSFER_BIT` | The graphics and transfer leaves record a fill command; the video decode leaf does not, because video decode queues are not in that overlap mask. | [`vktApiDebugUtilsTests.cpp#L121-L124`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L121-L124) |

## Behavior Parameters

The primary behavioral axis is the leaf: three select queue profiles for debug-utils labels, while `debug_marker_graphics` selects a different extension and command sequence.

### long_labels_graphics — Long debug labels on a graphics-capable queue

Tests the long-name and long-label path on a queue family selected with `required = VK_QUEUE_GRAPHICS_BIT` and `excluded = 0`. Because the required flag overlaps the graphics/compute/transfer mask, the recorded command buffer also contains a `vkCmdFillBuffer` call against the test buffer. This is the only leaf with no exclusion mask and the only leaf that always finds a queue family on any Vulkan-conformant device, since graphics support is mandatory.

### long_labels_transfer — Long debug labels on a transfer-only queue

Tests the same shared path on a queue family selected with `required = VK_QUEUE_TRANSFER_BIT` and `excluded = VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT`, so the chosen family must support transfer but must not advertise graphics or compute. The fill command is still recorded because `VK_QUEUE_TRANSFER_BIT` is in the overlap mask. The leaf is skipped at the support check when no such dedicated transfer queue family exists on the device.

### long_labels_video_decode — Long debug labels on a video-decode queue

Tests the same shared path on a queue family selected with `required = VK_QUEUE_VIDEO_DECODE_BIT_KHR` and `excluded = VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT`. Because `VK_QUEUE_VIDEO_DECODE_BIT_KHR` is not in the overlap mask, this leaf records only the debug label insertion into the command buffer and the queue label insertion; no `vkCmdFillBuffer` is emitted. The leaf is registered only under `#ifndef CTS_USES_VULKANSC` and is skipped at the support check when no video-decode-capable queue family exists.

### debug_marker_graphics: legacy debug-marker commands

The test assigns a long name and a four-byte tag to a 256-byte buffer, then records begin, insert, and end markers around a fill on the context's universal queue. It checks completion without readback; name/tag return values are not checked ([body](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L114-L168)).

## Shader Analysis

No shaders run. The commands are label/marker operations and buffer fills; no readback or shader-output oracle is used.

## Runtime Execution and Result Checking

The long-label leaves share [`testLongDebugLabelsTest()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L50-L110). The support check [`checkDebugUtilsSupport()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L170-L176) requires `VK_EXT_debug_utils` and a matching queue family. The body creates a custom instance and device, names a buffer, records debug labels, submits, and returns pass when the calls complete. It does not read back the buffer or verify stored names or labels.

`debug_marker_graphics` is registered separately under `#ifndef CTS_USES_VULKANSC` and requires `VK_EXT_debug_marker` through [`checkDebugMarkerSupport()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L184-L188). [`testDebugMarker()`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L113-L172) creates a 256-byte transfer buffer, sets a long object name and a tag, records `cmdDebugMarkerBeginEXT`, `cmdDebugMarkerInsertEXT`, and `cmdDebugMarkerEndEXT` around `vkCmdFillBuffer`, submits the command buffer, and returns pass. It performs no readback and does not check the name or tag values after setting them; the name/tag return codes are likewise not independently inspected.

The debug-marker leaf is absent from Vulkan SC builds. The numbered sequence below applies to the long-label leaves.

1. Create a custom instance with `VK_EXT_debug_utils` enabled, regardless of whether validation is active, so the debug-utils entry points are present ([`vktApiDebugUtilsTests.cpp#L53-L59`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L53-L59)).
2. Select a queue family through `findQueueFamilyIndexWithCaps(vki, physicalDevice, params.required, params.excluded)` ([`vktApiDebugUtilsTests.cpp#L60`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L60)). A failure here is reported by the support check, not by the test body.
3. Create a device through the custom instance wrapper and use that device's driver and allocator ([setup](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L53-L76)). Local explicit SC reservation chains are no longer present in this function.
4. Construct the long string `longName(64 * 1024 + 1, 'x')` ([`vktApiDebugUtilsTests.cpp#L97`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L97)).
5. Create a 1024-byte host-visible buffer with `VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_TRANSFER_SRC_BIT` and attach the long string as its object name through `vkSetDebugUtilsObjectNameEXT` ([`vktApiDebugUtilsTests.cpp#L99-L108`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L99-L108)).
6. Create a command pool with `VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT`, allocate a primary command buffer, begin recording, insert the long string as a command-buffer label through `vkCmdInsertDebugUtilsLabelEXT`, conditionally record `vkCmdFillBuffer(*testBuffer, 0, VK_WHOLE_SIZE, 1985)` when the required flag overlaps the graphics/compute/transfer mask, and end recording ([`vktApiDebugUtilsTests.cpp#L110-L125`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L110-L125)).
7. Insert the long string as a queue label through `vkQueueInsertDebugUtilsLabelEXT`, then submit the command buffer and wait for completion through `submitCommandsAndWait` ([`vktApiDebugUtilsTests.cpp#L127-L129`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L127-L129)).
8. Return `tcu::TestStatus::pass("Pass")` ([`vktApiDebugUtilsTests.cpp#L131`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L131)).

Pass condition: every Vulkan call in the sequence returns without error and the command buffer submission completes. The body does not read back the buffer contents, does not register a `VK_EXT_debug_utils` messenger callback, and does not verify that the long string was stored, echoed, or surfaced to external tooling. A pass only confirms that the implementation accepted the long name and label strings through the recorded and submitted path.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `long_labels_graphics` | Long-name or long-label rejection on the graphics queue path, or command buffer recording and submission failure with the inserted label. |
| `debug_marker_graphics` | Marker/name/tag handling causes a crash or recording/submission failure; stored metadata and fill contents are not verified. |
| `long_labels_transfer` | Long-name or long-label rejection on a dedicated transfer queue, or failure to find a transfer-only queue family. |
| `long_labels_video_decode` | Long-name or long-label rejection on a video-decode queue, failure to find a video-decode queue family, or Vulkan SC build omitting the leaf entirely. |

### Cause Analysis

#### Long-name or long-label rejection

**Possible failure symptoms:** `vkSetDebugUtilsObjectNameEXT`, `vkCmdInsertDebugUtilsLabelEXT`, or `vkQueueInsertDebugUtilsLabelEXT` returns a non-`VK_SUCCESS` result, or command buffer recording fails after the label insertion.

**Possible implementation causes:** the driver's debug-utils implementation copies or stores the input string through a fixed-size internal buffer that does not accommodate `64 * 1024 + 1` characters, or the implementation rejects the string outright instead of storing or ignoring it. The `VK_EXT_debug_utils` specification does not define a maximum length for `pObjectName` or `pLabelName`, so a rejection of an otherwise valid null-terminated string is a conformance issue. Source-level investigation is needed to confirm whether the failure occurs at name assignment, command recording, queue submission, or internally during string handling.

#### Command buffer recording or submission failure with inserted label

**Possible failure symptoms:** `beginCommandBuffer`, `endCommandBuffer`, or `submitCommandsAndWait` returns a non-`VK_SUCCESS` result, or the wait for the submitted command buffer reports an error.

**Possible implementation causes:** the implementation's command buffer encoder mishandled the inserted label region when the label string is oversized, or the fill command failed to execute because the long label disrupted command recording. This cause applies only to the `long_labels_graphics` and `long_labels_transfer` leaves, since `long_labels_video_decode` does not record `vkCmdFillBuffer`. A failure isolated to the two leaves that record the fill command, while `long_labels_video_decode` passes, points to the interaction between the label and the fill command rather than to the label entry points alone.

#### Queue family selection failure

**Possible failure symptoms:** the support check `findQueueFamilyIndexWithCaps` throws a `tcu::NotSupportedError` because no queue family matches the required and excluded mask.

**Possible implementation causes:** the device exposes no queue family with `VK_QUEUE_TRANSFER_BIT` and without `VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT` for `long_labels_transfer`, or no queue family with `VK_QUEUE_VIDEO_DECODE_BIT_KHR` for `long_labels_video_decode`. A `NotSupportedError` here is a skip, not a failure; it indicates that the device does not expose the queue capability profile the leaf targets. The `long_labels_video_decode` leaf is also absent from Vulkan SC builds because the registration itself is guarded by `#ifndef CTS_USES_VULKANSC`.

## Case Pruning

### Requirement-based pruning

- The three long-label leaves require instance functionality `VK_EXT_debug_utils`; `debug_marker_graphics` instead requires device functionality `VK_EXT_debug_marker` ([callbacks](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L171-L183)).
- Every leaf requires a queue family matching its required and excluded mask through `findQueueFamilyIndexWithCaps`. Devices without a dedicated transfer-only queue family skip `long_labels_transfer`; devices without a video-decode-capable queue family skip `long_labels_video_decode`.
- The `long_labels_video_decode` leaf is omitted entirely from Vulkan SC builds by the `#ifndef CTS_USES_VULKANSC` guard at [`vktApiDebugUtilsTests.cpp#L159-L164`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L159-L164).
- Both `debug_marker_graphics` and `long_labels_video_decode` are excluded from Vulkan SC ([registration](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L196-L213)).

### Design-based pruning

The family contains three long-label leaves and a separate debug-marker leaf. Each uses fixed strings and buffer sizes rather than a generated size matrix.

## Key Takeaways

- The `debug_utils` family stresses the `VK_EXT_debug_utils` name and label entry points with a single oversized (`64 * 1024 + 1` character) string; it does not test messenger callbacks, label region nesting, or label visibility to external tools.
- All three leaves share one host-side body. Differences in pass or fail behavior between leaves point to the queue family capability profile each leaf selects, not to a difference in the label-handling code path.
- The `vkCmdFillBuffer` call is recorded only when the required queue flag overlaps graphics, compute, or transfer. The `long_labels_video_decode` leaf records only label insertions, so it isolates label handling from any fill-command interaction.
- The pass criterion is unconditional pass after successful submission; there is no buffer readback, no callback inspection, and no string round-trip check. A pass confirms only that the implementation accepted the long name and label strings through the recorded and submitted path.
- See `## Failure Meaning` for the cause analysis behind long-name rejection and command buffer submission failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDebugUtilsTests()` | [`vktApiDebugUtilsTests.cpp#L144-L167`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L144-L167) | Family registration and leaf case additions. |
| Parent attach | [`vktApiTests.cpp#L91`](../../../modules/vulkan/api/vktApiTests.cpp#L91) | Attaches the `debug_utils` family to the `api` test category. |
| `TestParams` | [`vktApiDebugUtilsTests.cpp#L44-L48`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L44-L48) | Holds the required and excluded queue flag mask per leaf. |
| `testLongDebugLabelsTest()` | [`vktApiDebugUtilsTests.cpp#L50-L132`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L50-L132) | Shared test body used by all three leaves. |
| Long string construction | [`vktApiDebugUtilsTests.cpp#L97`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L97) | `64 * 1024 + 1` character input string. |
| Buffer object name | [`vktApiDebugUtilsTests.cpp#L104-L108`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L104-L108) | `vkSetDebugUtilsObjectNameEXT` on the test buffer. |
| Command-buffer label | [`vktApiDebugUtilsTests.cpp#L119-L125`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L119-L125) | `vkCmdInsertDebugUtilsLabelEXT` and conditional `vkCmdFillBuffer`. |
| Queue label | [`vktApiDebugUtilsTests.cpp#L127`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L127) | `vkQueueInsertDebugUtilsLabelEXT` before submission. |
| Submission and pass | [`vktApiDebugUtilsTests.cpp#L129-L131`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L129-L131) | `submitCommandsAndWait` and unconditional pass return. |
| `checkDebugUtilsSupport()` | [`vktApiDebugUtilsTests.cpp#L134-L140`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L134-L140) | Extension and queue family support check; produces `NotSupportedError` skips. |
| Vulkan SC guard | [`vktApiDebugUtilsTests.cpp#L159-L164`](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L159-L164) | Conditionally omits the `long_labels_video_decode` leaf. |
| Debug-marker execution | [testDebugMarker](../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L114-L168) | Names/tags a buffer and submits begin/insert/end markers without readback. |
| Header | [`vktApiDebugUtilsTests.hpp`](../../../modules/vulkan/api/vktApiDebugUtilsTests.hpp#L1) | Declares `createDebugUtilsTests`. |
