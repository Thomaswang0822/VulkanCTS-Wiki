## Overview

The `image_processing` category covers the `VK_QCOM_image_processing` API contract plus functional block matching, box-filter sampling, and weight-image sampling across compute and graphics paths. The category dispatcher is [`vktImageProcessingTests.cpp`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43-L85).

## Background Knowledge

- A Vulkan physical-device property query can attach an extension-specific structure to `VkPhysicalDeviceProperties2` through `pNext`. The returned fields describe implementation limits rather than the result of executing an image operation.
- Block matching compares a rectangular target image region with a reference region and produces an error metric. SAD sums absolute differences; SSD sums squared differences. The block-matching tests compare that device-produced metric with a CPU-built reference.
- A Vulkan image view defines how an image is interpreted by shader accesses, including component mapping, while a sampler contributes address and reduction behavior. Those states are part of the image-processing test matrix because they affect values consumed by the block-match operation.

## Category Structure

```text
image_processing
├── api
├── compute
│   ├── block_matching
│   ├── box_filter_sampling
│   └── weight_image_sampling
└── graphics
    ├── fast_lib
    ├── monolithic
    └── shader_objects
```

`graphics` contains `fast_lib`, `monolithic`, and `shader_objects` intermediate nodes. Each construction branch contains the functional families registered by the corresponding factory. The implementation-bearing families are documented in [ApiTests.md](../testfiles/image_processing/ApiTests.md), [BlockMatching.md](../testfiles/image_processing/BlockMatching.md), [BoxFilterSampling.md](../testfiles/image_processing/BoxFilterSampling.md), and [WeightImageSampling.md](../testfiles/image_processing/WeightImageSampling.md).

## How the Families Fit Together

- **API:** operation-specific feature and property-limit checks.
- **Block matching:** SAD and SSD operations with target/reference images and CPU reference comparison.
- **Box filtering:** `textureBoxFilterQCOM` coverage across compute and graphics shader paths.
- **Weight-image sampling:** `textureWeightedSampleQCOM` coverage for weighted, min, and max reduction behavior, filter shape, image state, and descriptor conditions.

The mustpass inventory in [`image-processing.txt`](../../mustpass/main/vk-default/image-processing.txt) is the authoritative list of current registered paths.

## Level-3 Pages Navigation

| Area | Page |
|---|---|
| API properties | [ApiTests.md](../testfiles/image_processing/ApiTests.md) |
| SAD/SSD block matching | [BlockMatching.md](../testfiles/image_processing/BlockMatching.md) |
| Box-filter sampling | [BoxFilterSampling.md](../testfiles/image_processing/BoxFilterSampling.md) |
| Weight-image sampling | [WeightImageSampling.md](../testfiles/image_processing/WeightImageSampling.md) |
