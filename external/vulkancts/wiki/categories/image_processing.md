## Overview

The `image_processing` test category collects tests that check the `VK_QCOM_image_processing` extension's advertised limits and block-matching operations in graphics and compute pipelines.

## Background Knowledge

- A Vulkan physical-device property query can attach an extension-specific structure to `VkPhysicalDeviceProperties2` through `pNext`. The returned fields describe implementation limits rather than the result of executing an image operation.
- Block matching compares a rectangular target image region with a reference region and produces an error metric. SAD sums absolute differences; SSD sums squared differences. The block-matching tests compare that device-produced metric with a CPU-built reference.
- A Vulkan image view defines how an image is interpreted by shader accesses, including component mapping, while a sampler contributes address and reduction behavior. Those states are part of the image-processing test matrix because they affect values consumed by the block-match operation.

## Category Structure

```text
image_processing
├── graphics
├── api
└── compute
```

`graphics` contains `monolithic`, `fast_lib`, and `shader_objects` intermediate nodes, each with a `block_matching` test family. `compute` contains `block_matching`; `api` contains the fixed `properties` test case. The registration-only dispatcher [`vktImageProcessingTests.cpp`](../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43-L85) is folded into this category page rather than represented by a separate rewritten technical page.

## How the Families Fit Together

The category separates the extension contract from the functional block-matching workload and then repeats the workload across execution paths:

- **API limits:** `api.properties` checks the minimum values reported in `VkPhysicalDeviceImageProcessingPropertiesQCOM`.
- **Graphics execution:** `graphics` runs block matching through three pipeline-construction branches. The monolithic branch adds the extended image, sampler, shader-stage, and descriptor variations.
- **Compute execution:** `compute.block_matching` runs the same SAD/SSD operations in a compute shader and adds `self` cases that compare two regions of one image.

The API page establishes the reported capability floor; the block-matching page checks functional results under the registered resource and pipeline conditions.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `api.properties` | [ApiTests.md](../testfiles/image_processing/ApiTests.md) | Extension property-query support, minimum limits, repeated queries, and failure meaning. |
| `graphics.*.block_matching`, `compute.block_matching` | [BlockMatching.md](../testfiles/image_processing/BlockMatching.md) | SAD/SSD operation selection, graphics and compute setup, parameter groups, shader shape, result checking, and pruning. |

## Category Notes

- The current registration table adds only `sad` and `ssd` block-matching operations, although the shared base contains support branches for other image-processing operations ([operation registration](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1881-L1898); [shared support branches](../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L102-L161)).
- Candidate formats are supplied by a fixed list, but per-device format features and image-format usage are checked before each block-matching case executes ([format list](../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L408-L435); [block-match support](../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L141-L213)).
