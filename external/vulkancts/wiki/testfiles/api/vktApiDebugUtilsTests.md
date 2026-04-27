# [vktApiDebugUtilsTests.cpp](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L1)

## Overview

[`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L1) implements the `api/debug_utils` subgroup registered by [`createApiTests()`](../../../../../modules/vulkan/api/vktApiTests.cpp#L91). The file is compact and focused: every registered case exercises very long debug-utils names/labels against a queue-family configuration, then submits a command buffer to ensure the operations complete without failure.

## Role of File

Implementation-heavy test file for the `api/debug_utils` subgroup.

## Source Code

- Primary source: [vktApiDebugUtilsTests.cpp](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L1)
- Header: [vktApiDebugUtilsTests.hpp](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../../../modules/vulkan/api/vktApiTests.cpp#L91)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
  api
  +-- createApiTests(apiTests)
      +-- createDebugUtilsTests(testCtx)
          +-- debug_utils
              +-- long_labels_graphics
              +-- long_labels_transfer
              +-- long_labels_video_decode  (not in Vulkan SC)
```

Evidence:
- `debug_utils` group created at [`createDebugUtilsTests()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L146)
- `long_labels_graphics` added at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L151)
- `long_labels_transfer` added at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L155)
- `long_labels_video_decode` added under `#ifndef CTS_USES_VULKANSC` at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L162)

## Test Hierarchy

```text
api
+-- debug_utils
    +-- long_labels_graphics
    +-- long_labels_transfer
    +-- long_labels_video_decode  (excluded for Vulkan SC)
```

Source: [`createDebugUtilsTests()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L144).

## Test Families

### 1. Long debug label/object-name handling across queue classes

All visible cases in [`createDebugUtilsTests()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L144) reuse the same execution function, [`testLongDebugLabelsTest()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L50), with different [`TestParams`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L44) values.

Inside the test body, the file:

- creates a custom instance with `VK_EXT_debug_utils` explicitly enabled at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L56)
- chooses a queue family matching required/excluded flags at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L60)
- creates a `64 * 1024 + 1` character string at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L97)
- assigns that long string as a debug object name for a buffer via [`setDebugUtilsObjectNameEXT()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L108)
- inserts the same long string as a command-buffer label via [`cmdInsertDebugUtilsLabelEXT()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L120)
- inserts the long label on the queue via [`queueInsertDebugUtilsLabelEXT()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L127)
- submits the command buffer and waits for completion at [`submitCommandsAndWait()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L129)

This supports an evidence-backed summary that the family is about tolerance of extremely long debug-utils labels/names under different queue-family environments.

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Required queue flags | `VK_QUEUE_GRAPHICS_BIT` at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L149), `VK_QUEUE_TRANSFER_BIT` at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L154), `VK_QUEUE_VIDEO_DECODE_BIT_KHR` at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L160) |
| Excluded queue flags | `0` for graphics at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L150); `VK_QUEUE_GRAPHICS_BIT \| VK_QUEUE_COMPUTE_BIT` for transfer/video-decode at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L155) |
| Case names | `long_labels_graphics`, `long_labels_transfer`, `long_labels_video_decode` from [`createDebugUtilsTests()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L151) |
| Long label length | `64 * 1024 + 1` characters in [`testLongDebugLabelsTest()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L97) |
| Debug-utils target objects | buffer object naming at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L104), command-buffer label insertion at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L110), queue label insertion at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L127) |
| Command content variation | buffer fill command only emitted when required flags overlap graphics/compute/transfer at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L121) |

## Support / Feature Requirements

- every case requires the instance functionality `VK_EXT_debug_utils` through [`checkDebugUtilsSupport()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L134)
- every case requires a queue family matching the provided required/excluded flag mask via [`findQueueFamilyIndexWithCaps()`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L138)
- the `long_labels_video_decode` case is omitted entirely for Vulkan SC builds via [`#ifndef CTS_USES_VULKANSC`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L159)
- Vulkan SC builds inject reservation-related `pNext` structures for device and command-pool creation under [`#ifdef CTS_USES_VULKANSC`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L71)

## Verification Methods

The visible verification style is execution-based rather than result-buffer comparison:

- the test performs debug-utils name/label API calls on a real instance/device/queue/command buffer at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L108)
- it records and submits a command buffer successfully at [`vktApiDebugUtilsTests.cpp`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L119)
- it returns pass unconditionally after successful completion via [`tcu::TestStatus::pass("Pass")`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L131)

From the inspected code, the pass criterion is "operations complete without throwing/failing earlier," not content verification.

## Test Principles Observed

- Stress an API with oversized but valid-looking inputs
- Reuse one core test body with queue-family parameterization via [`TestParams`](../../../../../modules/vulkan/api/vktApiDebugUtilsTests.cpp#L44)
- Exercise multiple debug-utils attachment points: buffer object names, command-buffer labels, and queue labels
- Tie debug metadata to executable work: the command buffer is actually submitted

## Notes / Uncertainties

- The inspected file does not assert an upper bound from spec text; it only demonstrates that a `64 * 1024 + 1` character label is attempted in code.
- The test does not inspect callback output or read back stored names, so no stronger claim about debug-label persistence or truncation behavior is made here.
