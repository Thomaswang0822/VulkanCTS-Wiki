# protected_memory

## Overview

The [`protected_memory`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L50-L104) category verifies protected-memory behavior across attachment operations, image transfers and shader image access, buffer transfer operations, storage-buffer shader access, WSI swapchain interaction, YCbCr conversion, workgroup storage, and stack storage. The category is registered by [`createTests()`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L50-L104), which assembles named branch groups from implementation factories included at [`vktProtectedMemTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L30-L43).

## Registration Entry Point

```text
protected_memory
├── attachment
├── image
├── buffer
├── ssbo
├── interaction
├── workgroupstorage
└── stack
```

The WSI child of `interaction` is guarded out for Vulkan SC builds at [`vktProtectedMemTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L92-L98). The top-level group names above are constructed explicitly in [`vktProtectedMemTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L54-L102).

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktProtectedMemTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L1) | Registration | Category dispatcher and top-level branch grouping |
| [`vktProtectedMemAttachmentLoadTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L216-L350) | Implementation | Attachment load-op static/random cases |
| [`vktProtectedMemAttachmentClearTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L404-L410) | Implementation | Attachment clear-op primary/secondary command-buffer cases |
| [`vktProtectedMemCopyImageTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemCopyImageTests.cpp#L467-L474) | Implementation | Protected image copy cases |
| [`vktProtectedMemBlitImageTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L470-L475) | Implementation | Protected image blit cases |
| [`vktProtectedMemClearColorImageTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L387-L392) | Implementation | Protected clear-color-image cases |
| [`vktProtectedMemCopyBufferToImageTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L431-L436) | Implementation | Protected buffer-to-image copy cases |
| [`vktProtectedMemCopyImageToBufferTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L400-L405) | Implementation | Protected image-to-buffer copy cases |
| [`vktProtectedMemFillUpdateCopyBufferTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L616-L647) | Implementation | Fill, update, and copy buffer roots |
| [`vktProtectedMemStorageBufferTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L864-L905) | Implementation | SSBO read, write, and atomic roots |
| [`vktProtectedMemShaderImageAccessTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1251-L1400) | Implementation | Shader image access matrix |
| [`vktProtectedMemWsiSwapchainTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L1461-L1471) | Implementation | Non-VulkanSC WSI swapchain interaction |
| [`vktProtectedMemYCbCrConversionTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L1230-L1349) | Implementation | Protected YCbCr conversion matrix |
| [`vktProtectedMemWorkgroupStorageTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L370-L381) | Implementation | Shared-memory-size workgroup-storage cases |
| [`vktProtectedMemStackTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L409-L421) | Implementation | Stack-size cases |
| [`vktProtectedMemUtils.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L50-L125) | Helper | Protected-context support and command-buffer-name helpers |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktProtectedMemAttachmentClearTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemAttachmentClearTests.cpp#L1) | [`vktProtectedMemAttachmentClearTests.md`](../testfiles/protected_memory/vktProtectedMemAttachmentClearTests.md) |
| [`vktProtectedMemAttachmentLoadTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L1) | [`vktProtectedMemAttachmentLoadTests.md`](../testfiles/protected_memory/vktProtectedMemAttachmentLoadTests.md) |
| [`vktProtectedMemBlitImageTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemBlitImageTests.cpp#L1) | [`vktProtectedMemBlitImageTests.md`](../testfiles/protected_memory/vktProtectedMemBlitImageTests.md) |
| [`vktProtectedMemClearColorImageTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemClearColorImageTests.cpp#L1) | [`vktProtectedMemClearColorImageTests.md`](../testfiles/protected_memory/vktProtectedMemClearColorImageTests.md) |
| [`vktProtectedMemCopyBufferToImageTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemCopyBufferToImageTests.cpp#L1) | [`vktProtectedMemCopyBufferToImageTests.md`](../testfiles/protected_memory/vktProtectedMemCopyBufferToImageTests.md) |
| [`vktProtectedMemCopyImageTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemCopyImageTests.cpp#L1) | [`vktProtectedMemCopyImageTests.md`](../testfiles/protected_memory/vktProtectedMemCopyImageTests.md) |
| [`vktProtectedMemCopyImageToBufferTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemCopyImageToBufferTests.cpp#L1) | [`vktProtectedMemCopyImageToBufferTests.md`](../testfiles/protected_memory/vktProtectedMemCopyImageToBufferTests.md) |
| [`vktProtectedMemFillUpdateCopyBufferTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L1) | [`vktProtectedMemFillUpdateCopyBufferTests.md`](../testfiles/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.md) |
| [`vktProtectedMemShaderImageAccessTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1) | [`vktProtectedMemShaderImageAccessTests.md`](../testfiles/protected_memory/vktProtectedMemShaderImageAccessTests.md) |
| [`vktProtectedMemStackTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L1) | [`vktProtectedMemStackTests.md`](../testfiles/protected_memory/vktProtectedMemStackTests.md) |
| [`vktProtectedMemStorageBufferTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L1) | [`vktProtectedMemStorageBufferTests.md`](../testfiles/protected_memory/vktProtectedMemStorageBufferTests.md) |
| [`vktProtectedMemTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L1) | [`vktProtectedMemTests.md`](../testfiles/protected_memory/vktProtectedMemTests.md) |
| [`vktProtectedMemWorkgroupStorageTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L1) | [`vktProtectedMemWorkgroupStorageTests.md`](../testfiles/protected_memory/vktProtectedMemWorkgroupStorageTests.md) |
| [`vktProtectedMemWsiSwapchainTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L1) | [`vktProtectedMemWsiSwapchainTests.md`](../testfiles/protected_memory/vktProtectedMemWsiSwapchainTests.md) |
| [`vktProtectedMemYCbCrConversionTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L1) | [`vktProtectedMemYCbCrConversionTests.md`](../testfiles/protected_memory/vktProtectedMemYCbCrConversionTests.md) |

## Subgroup Structure and Major Themes

- [`attachment`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L54-L60): load-op and clear-op tests with static and random reference data.
- [`image`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L62-L70): copy, blit, clear-color, buffer-to-image transfer, and shader image access tests.
- [`buffer`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L73-L80): fill, update, copy, and image-to-buffer transfer tests.
- [`ssbo`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L83-L89): protected storage-buffer read, write, and atomic operations across shader stages and pipeline-protection variants.
- [`interaction`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L92-L98): WSI swapchain tests outside Vulkan SC and protected YCbCr conversion tests.
- [`workgroupstorage`](../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L370-L381) and [`stack`](../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L409-L421): compute-shader storage-size sweeps validated through image output.

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Command-buffer type | `primary` and `secondary` from [`getCmdBufferTypeStr()`](../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L575-L584) |
| Static vs random data | Attachment, image-transfer, and buffer-transfer files create fixed data plus 10 seeded random cases |
| Protection/pipeline access | `default`, `protected_access`, `protected_access_only`, and `no_protected_access` groups in SSBO and image-access files |
| Shader stage | Fragment and compute branches in shader image access, SSBO, and YCbCr conversion files |
| Storage sizes | Workgroup sizes `(1, 4, 5, 60, 101, 503)` and stack sizes `(32, 64, 128, 256, 512)` |
| YCbCr conversion axes | Format, shader type, color model, color range, chroma location, optimal tiling, and disjoint flag |

## Recurring Support Requirements

The common support gate is [`checkProtectedContextSupport()`](../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L124), which checks Vulkan 1.1, protected-memory feature support, optional YCbCr support, and optional pipeline-protected-access support. Several secondary-command-buffer tests include Vulkan SC property checks. YCbCr conversion additionally checks format features in [`checkSupport()`](../../modules/vulkan/protected_memory/vktProtectedMemYCbCrConversionTests.cpp#L148-L215), and fill/update/copy buffer device-address cases require `VK_KHR_device_address_commands` at [`vktProtectedMemFillUpdateCopyBufferTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L104-L109).

## Recurring Verification Methods

Observed verification uses image validation after protected rendering or transfer work, buffer validation after protected buffer operations, WSI swapchain creation/render helpers, and YCbCr shader conversion validation. Image-output validation is visible in files such as [`vktProtectedMemShaderImageAccessTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1227-L1245), and buffer validation is visible in [`vktProtectedMemFillUpdateCopyBufferTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L331-L335) and [`vktProtectedMemStorageBufferTests.cpp`](../../modules/vulkan/protected_memory/vktProtectedMemStorageBufferTests.cpp#L671-L675).

## Relationship to the Test Plan

[`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L191-L267) describes general memory-management themes such as allocation, mapping, cache control, and binding. The inspected test-plan text does not provide protected-memory-category-specific coverage, so this category page relies primarily on the inspected source under [`modules/vulkan/protected_memory/`](../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L25-L43).

## Notes / Uncertainties

- The documentation scope includes source files that register tests; helper-only files such as validators, context, and utilities are cited as supporting evidence but do not receive Level-3 pages.
- Some implementation files register multiple sibling roots. Their Level-3 pages use one canonical parseable hierarchy tree and document additional roots in prose to satisfy the one-tree hierarchy contract.
