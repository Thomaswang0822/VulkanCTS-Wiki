# Understanding Brief: image layout transition tests

## One-Sentence Test Purpose

These synchronization2-only tests check that image layout barriers preserve contents when a transition is intentionally a no-op and correctly move a multisample image between universal and compute queues before compute reads it.

## Background Knowledge

An image layout describes how Vulkan accesses an image. An image memory barrier can also establish execution and memory dependencies between stages and accesses. When both `oldLayout` and `newLayout` are `VK_IMAGE_LAYOUT_UNDEFINED`, Vulkan permits the implementation to skip the layout transition; it must nevertheless preserve the contents in this test's scenario. Synchronization2 expresses the barrier through `VkImageMemoryBarrier2` inside `VkDependencyInfo` and records it with `vkCmdPipelineBarrier2` (or the KHR spelling for Vulkan SC).

Queue-family ownership is separate from layout. The compute cases submit barriers on a universal queue, then a compute queue, then the universal queue again. The image is multisampled and is read by a compute shader either through `sampler2DMS` or `image2DMS`.

## One Concrete Example

`no_op` first clears a 64x64 `VK_FORMAT_R8G8B8A8_UNORM` image and draws a yellow, alpha-blended full-screen quad. It records a synchronization2 barrier whose old and new layouts are both `UNDEFINED`, draws the quad again, copies the image to a host-visible buffer, and compares every pixel with the expected blended color. If the implementation treats the no-op barrier as content destruction, the image comparison fails.

## End-to-End Test Flow

```text
no_op:
[universal queue] clear image to transparent black and transition to COLOR_ATTACHMENT_OPTIMAL
[universal queue] draw, issue UNDEFINED -> UNDEFINED synchronization2 barrier, draw again
[host] copy the image to a buffer and compare against the blended-color reference

compute_transition / compute_transition_storage:
[universal queue] UNDEFINED -> COLOR_ATTACHMENT_OPTIMAL
[compute queue] COLOR_ATTACHMENT_OPTIMAL -> TRANSFER_DST_OPTIMAL
[universal queue] clear image blue, transition to shader-read layout, dispatch one compute workgroup
[host] compare every sampled/stored multisample value with blue
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`no_op` generates a vertex shader that passes positions through and a fragment shader that outputs `vec4(1.0, 1.0, 0.0, 0.4)`. The compute cases generate one GLSL compute shader with an 8x8x4 local workgroup. It uses `texelFetch` from `sampler2DMS` for `compute_transition`, or `imageLoad` from `image2DMS` for `compute_transition_storage`, and writes `vec4` values to a storage buffer.

### Bound resources and memory objects

| Resource | Configured values | Device use | Host observation |
|---|---|---|---|
| `no_op` image | 64x64, `R8G8B8A8_UNORM`, one sample | Color attachment, then transfer source | Copied to host-visible buffer |
| Compute image | 8x8, `R8G8B8A8_UNORM`, four samples | Color attachment, transfer destination, sampled or storage image | Read through output buffer |
| Vertex buffer | Full-screen quad positions | Graphics vertex input | Not read back |
| Storage buffer | `R32G32B32A32_SFLOAT` output | Compute shader writes one value per sample | Invalidated and compared by host |

## Registration and Mustpass Coverage

The source creates the shortened group `layout_transition` and exactly three leaves:

```text
synchronization2.layout_transition
├── compute_transition
├── compute_transition_storage
└── no_op
```

The group is synchronization2-only; there is no `synchronization.layout_transition` registration. The default synchronization2 mustpass file contains all three leaves. See the [exact mustpass entries](../../../mustpass/main/vk-default/synchronization2.txt#L32027-L32029) and the [factory](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L744-L757). The synchronization2 category dispatch is visible in [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L128-L132).

## What Is Checked

- `no_op`: image contents survive the `UNDEFINED` to `UNDEFINED` barrier and the two blended draws match with a `0.01` per-component threshold.
- `compute_transition`: four-sample image data read with `sampler2DMS` is exactly the blue clear color.
- `compute_transition_storage`: the same check through `image2DMS` storage-image access.

## Behavior Parameter Identification

> **Behavior parameter:** `layout transition scenario` (behavioral group)
>
> **Candidate values:** `no-op undefined transition`, `cross-queue sampled read`, `cross-queue storage-image read`

## What Failure Means

| If this value fails | Possible failure cause(s) |
|---|---|
| `no-op undefined transition` | Incorrect preservation of image contents or execution dependency handling for an `UNDEFINED`/`UNDEFINED` synchronization2 barrier |
| `cross-queue sampled read` | Incorrect queue-family/layout transition, multisample sampling, or shader-read visibility |
| `cross-queue storage-image read` | Incorrect queue-family/layout transition, multisample storage-image access, or format support handling |

## Important Variations and Special Cases

- Every case requires `VK_KHR_synchronization2`; compute cases also require a compute queue.
- The storage-image case is skipped when the physical device does not support the requested multisample storage-image format/usage combination.
- Values are fixed rather than generated: the graphics image is 64x64 and single-sample; compute images are 8x8 and four-sample; all use `VK_FORMAT_R8G8B8A8_UNORM`.
- The code selects core synchronization2 commands unless `CTS_USES_VULKANSC` requires the KHR command name. This is command spelling support, not a second registration path.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| No-op graphics flow and comparison | [graphics test](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L170-L337) | Defines the barrier, draws, copy, and expected-color check |
| No-op support and shaders | [graphics case](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L339-L383) | Defines synchronization2 requirement and generated GLSL |
| Compute parameters and support | [compute case](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L385-L489) | Defines fixed image values, queue requirement, and storage-format gate |
| Compute barriers and verification | [compute flow](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L520-L739) | Defines queue sequence, shader read, and exact blue comparison |
| Test registration | [factory](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L744-L757) | Defines the three registered leaves |

## Questions / Risk Points for User Audit

- Does the distinction between preserving contents in `no_op` and changing layouts across queues in the compute cases remain clear?
- Is the explicit absence of a legacy `synchronization.layout_transition` family clear enough?
- Should the page include Vulkan specification links in addition to the source and mustpass evidence?

## Conversion Notes for Final Wiki Rewrite

Keep the synchronization2-only scope and exact three-leaf tree prominent. Use `layout transition scenario` as the behavior parameter, retain the failure mapping, and describe the two compute read modes without implying that they are runtime-generated variants.
