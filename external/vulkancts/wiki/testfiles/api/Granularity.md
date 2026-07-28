## Overview

**Core question:** does the implementation return a valid, stable render-area granularity across attachment configurations and across both supported query entry points?

- Covers the `granularity` test family under the `api` test category, implemented entirely in [`vktApiGranularityTests.cpp`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L1).
- Exercises `vkGetRenderAreaGranularity` and `vkGetRenderingAreaGranularityKHR` (`VK_KHR_maintenance5`) across format sweeps, attachment counts, and three render-pass states.
- Each test case leaf is named after one `VkFormat` value; the family registers one leaf per format per intermediate node.
- The page explains what each intermediate node changes about the query, how the host validates the result, and what a failure implies.

## Background Knowledge

- **Render-area granularity.** A `VkExtent2D` returned by `vkGetRenderAreaGranularity` or `vkGetRenderingAreaGranularityKHR` that describes the implementation's preferred alignment for the render area of a render pass or dynamic rendering instance. Larger values mean the implementation can collapse more tile-aligned work; the spec only requires the result to be a valid extent that is consistent for a given set of attachments.
- **Two query entry points.** `vkGetRenderAreaGranularity` takes a `VkRenderPass` handle and reflects attachments declared in that render pass. `vkGetRenderingAreaGranularityKHR` takes a `VkRenderingAreaInfoKHR` describing the attachment formats directly, without requiring a `VkRenderPass` object, and is the dynamic-rendering counterpart introduced by `VK_KHR_maintenance5` (Vulkan 1.4 core).
- **Attachment-info shape.** Each attachment is described in the test by a `VkFormat` plus a `VkExtent3D`. The format determines whether the attachment is color, depth, or depth/stencil, which in turn determines the aspect mask and image usage flag the test sets when creating the backing image.

## Registration Hierarchy

```text
api.granularity
├── single
├── multi
├── random
├── in_render_pass
└── in_dynamic_render_pass (non-VulkanSC only)
```

The parent registration at [`vktApiTests.cpp#L114`](../../../modules/vulkan/api/vktApiTests.cpp#L114) adds the `granularity` test family to the `api` test category via [`createGranularityQueryTests`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L463-L593). The factory builds the five intermediate nodes shown above and attaches one test case leaf per `VkFormat` integer value `1` through `VK_FORMAT_D32_SFLOAT_S8_UINT` (value `130`) to each node, using the lowercased format name without the `VK_FORMAT_` prefix as the leaf name. The `in_dynamic_render_pass` intermediate node is compiled out under `CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `single`, `multi`, `random`, `in_render_pass`, `in_dynamic_render_pass` | Selects attachment set shape and which query entry point / render-pass state is exercised | [`vktApiGranularityTests.cpp#L463-L593`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L463-L593) |
| Test case leaf | one per `VkFormat` value `1`..`130` | Names the primary format used for the first attachment of every case | [`vktApiGranularityTests.cpp#L531-L581`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L531-L581) |
| `TestMode` | `NO_RENDER_PASS`, `USE_RENDER_PASS`, `USE_DYNAMIC_RENDER_PASS` | Internal enum that picks the query entry point and whether a render pass is begun between the two queries | [`vktApiGranularityTests.cpp#L57-L62`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L57-L62) |
| Attachment count | `1` for `single`, `in_render_pass`, `in_dynamic_render_pass`; `2`-`10` for `multi`; `1 + 2`-`10` for `random` | Changes how many attachment descriptions are passed to the render pass or rendering-info struct | [`vktApiGranularityTests.cpp#L527-L529`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L527-L529) |
| Image extent | randomized `1`-`500` per axis, per attachment | Varies the framebuffer extent used for image creation; the render area itself stays at `1x1` | [`vktApiGranularityTests.cpp#L527`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L527), [`vktApiGranularityTests.cpp#L538-L565`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L538-L565) |
| Random seed | `215` | Fixed seed for `de::Random` so attachment counts, extents, and `random` companion formats are deterministic across runs | [`vktApiGranularityTests.cpp#L475`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L475) |
| `mandatoryFormats` pool | 47 formats listed in source | Companion attachment pool used by the `random` node | [`vktApiGranularityTests.cpp#L477-L525`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L477-L525) |

## Behavior Parameters

The primary behavioral axis is the intermediate node. Each node picks a different attachment-set shape and query state, so each one tests a different aspect of the granularity query contract.

### `single` — one attachment, queried outside any render pass

One attachment is created in the primary format, then `vkGetRenderAreaGranularity` is called twice against the constructed `VkRenderPass` without beginning the render pass. This node exercises the baseline single-attachment query and the trivial consistency check that two consecutive queries on the same render pass return the same value. Registered at [`vktApiGranularityTests.cpp#L536-L542`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L536-L542) using `TestMode::NO_RENDER_PASS`.

### `multi` — multiple attachments of the same format

Between 2 and 10 attachments are created, all with the same primary format and the same extent. The node verifies that the granularity query reflects the attachment set rather than only the first attachment, since repeating the same format can change the tiling preference reported by some implementations. Registered at [`vktApiGranularityTests.cpp#L544-L552`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L544-L552).

### `random` — primary format plus randomized mandatory-format attachments

One attachment in the primary format is combined with 2 to 10 attachments drawn from the `mandatoryFormats` array. Each extra attachment uses an independently randomized extent. This tests mixed-format attachment sets and produces the largest variation in attachment description input. Registered at [`vktApiGranularityTests.cpp#L554-L568`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L554-L568).

### `in_render_pass` — query before and during a traditional render pass

One attachment in the primary format is used, with `TestMode::USE_RENDER_PASS`. The test queries `vkGetRenderAreaGranularity` once before `vkCmdBeginRenderPass` and once inside the render pass, then compares the two results. This is the only node among the `vkGetRenderAreaGranularity` users that begins the render pass between the two queries, so it is the only one that can detect a query result that depends on whether the render pass is active. Registered at [`vktApiGranularityTests.cpp#L570-L574`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L570-L574).

### `in_dynamic_render_pass` — query before and during dynamic rendering

Registered only when `CTS_USES_VULKANSC` is not defined, with `TestMode::USE_DYNAMIC_RENDER_PASS`. The test fills a `VkRenderingAreaInfoKHR` with the attachment formats, queries `vkGetRenderingAreaGranularityKHR` once before `vkCmdBeginRendering` and once after, then compares the two values. This node is the only path that exercises the `VK_KHR_maintenance5` entry point. Registered at [`vktApiGranularityTests.cpp#L576-L579`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L576-L579); support is gated by [`GranularityCase::checkSupport`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L452-L453).

## Shader Analysis

No shader is involved in this test family. The test only queries implementation-reported granularity values and validates them on the host; no pipeline is built, no shader module is created, and no draw or dispatch is recorded into the command buffer.

## Runtime Execution and Result Checking

Host-side flow per test case leaf, in order:

- `GranularityCase::checkSupport` is called before instance creation. It throws `NotSupportedError` if every attachment format lacks both `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` and `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` in `optimalTilingFeatures`, and requires `VK_KHR_maintenance5` for the dynamic-rendering node. See [`vktApiGranularityTests.cpp#L437-L454`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L437-L454).
- `GranularityInstance::initAttachmentDescriptions` builds one `VkAttachmentDescription` per attachment with `loadOp`/`storeOp` set to `VK_ATTACHMENT_LOAD_OP_DONT_CARE` / `VK_ATTACHMENT_STORE_OP_DONT_CARE` and `finalLayout` of `VK_IMAGE_LAYOUT_GENERAL`. See [`vktApiGranularityTests.cpp#L119-L138`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L119-L138).
- `initImages` creates one `VkImage` and `VkImageView` per attachment with `VK_IMAGE_TILING_OPTIMAL`, single-sample, and usage derived from the format's depth, stencil, or color aspect. See [`vktApiGranularityTests.cpp#L140-L217`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L140-L217).
- `initObjects` creates the `VkRenderPass` and `VkFramebuffer` for non-dynamic modes (with a single no-op subpass that references no attachments), then allocates a primary command buffer. See [`vktApiGranularityTests.cpp#L219-L280`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L219-L280).
- `iterate` begins the command buffer, then branches on `TestMode`:
  - For `USE_DYNAMIC_RENDER_PASS`, it inserts per-attachment layout transitions into `VK_IMAGE_LAYOUT_GENERAL`, fills `VkRenderingAreaInfoKHR`, calls `vkGetRenderingAreaGranularityKHR` for `prePassGranularity`, calls `vkCmdBeginRendering`, and calls `vkGetRenderingAreaGranularityKHR` again for `granularity`. See [`vktApiGranularityTests.cpp#L295-L381`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L295-L381).
  - For `NO_RENDER_PASS` and `USE_RENDER_PASS`, it calls `vkGetRenderAreaGranularity` for `prePassGranularity`, optionally calls `vkCmdBeginRenderPass`, then calls `vkGetRenderAreaGranularity` again for `granularity`. See [`vktApiGranularityTests.cpp#L383-L391`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L383-L391).
- Validation runs three `TCU_CHECK` assertions on `granularity` and `prePassGranularity`:
  - `granularity.width >= 1 && granularity.height >= 1`
  - `prePassGranularity.width == granularity.width && prePassGranularity.height == granularity.height`
  - `granularity.width <= maxFramebufferWidth && granularity.height <= maxFramebufferHeight`

  See [`vktApiGranularityTests.cpp#L393-L396`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L393-L396).
- The render pass or dynamic rendering is ended, the command buffer is ended and submitted, and the case logs the reported width and height before returning `pass`. See [`vktApiGranularityTests.cpp#L398-L411`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L398-L411).

The render area passed to `vkCmdBeginRenderPass` and `vkCmdBeginRendering` is fixed at `1x1` ([`vktApiGranularityTests.cpp#L287`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L287)); the test never inspects whether the granularity divides the render area, only that the reported value itself is valid, stable, and within device limits.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single` | Granularity validity, stability, or limits check failed for a single-attachment `vkGetRenderAreaGranularity` query |
| `multi` | Granularity did not remain valid, stable, or within limits when multiple same-format attachments are present |
| `random` | Granularity did not remain valid, stable, or within limits for a mixed-format attachment set |
| `in_render_pass` | The pre-pass and in-pass `vkGetRenderAreaGranularity` results disagree, or the reported value is invalid or out of limits |
| `in_dynamic_render_pass` | The pre-pass and in-pass `vkGetRenderingAreaGranularityKHR` results disagree, the reported value is invalid or out of limits, or the entry point mishandles the `VkRenderingAreaInfoKHR` attachment format list |

### Cause Analysis

#### Invalid granularity value

**Possible failure symptoms:** the first `TCU_CHECK` fails because the implementation returns a `VkExtent2D` whose `width` or `height` is less than `1`. The reported value is observable in the test log line written at the end of `iterate`.

**Possible implementation causes:** the spec requires the returned granularity to be a valid `VkExtent2D` whose width and height are at least `1`. A driver that returns `0` for either dimension, or that leaves the struct uninitialized when no render-pass-specific granularity applies, would fail this check. Source-level investigation is needed to distinguish a driver bug from a query-routing problem if the value is exactly `0`.

#### Pre-pass and in-pass results disagree

**Possible failure symptoms:** the second `TCU_CHECK` fails because `prePassGranularity` differs from the `granularity` value queried after `vkCmdBeginRenderPass` or `vkCmdBeginRendering`.

**Possible implementation causes:** for `in_render_pass`, the spec defines `vkGetRenderAreaGranularity` as a function of the render pass's attachment descriptions and does not make the result depend on whether the render pass is currently begun; an implementation that recomputes granularity using additional runtime state after `vkCmdBeginRenderPass` would fail this consistency check. For `in_dynamic_render_pass`, `vkGetRenderingAreaGranularityKHR` takes a `VkRenderingAreaInfoKHR` and is not supposed to inspect command-buffer state, so a driver that routes the call through the active dynamic-rendering instance (or that fails to populate the result consistently when called twice with the same `VkRenderingAreaInfoKHR`) would fail. Source-level investigation is needed to confirm whether a discrepancy is caused by a query implementation bug or by an unintended dependency on command-buffer state.

#### Granularity exceeds device limits

**Possible failure symptoms:** the third `TCU_CHECK` fails because the reported `width` exceeds `maxFramebufferWidth` or the reported `height` exceeds `maxFramebufferHeight`.

**Possible implementation causes:** the spec does not require the granularity to be smaller than the framebuffer limits, but CTS enforces this as a sanity bound. A driver that returns the framebuffer's full extent or that clamps the granularity to a tile size larger than the reported `maxFramebufferWidth`/`maxFramebufferHeight` would trip this check. Source-level investigation is needed to determine whether the failure reflects a real bug or a large granularity that the implementation should have reported differently.

## Case Pruning

### Requirement-based pruning

- A test case leaf is skipped with `NotSupportedError` when its primary format (and any companion format in the `random` node) lacks both `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` and `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` in `optimalTilingFeatures`. See [`vktApiGranularityTests.cpp#L441-L450`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L441-L450). The check accepts a format if either bit is present, so pure sampled-image or storage-image formats are pruned out.
- The `in_dynamic_render_pass` intermediate node requires `VK_KHR_maintenance5`, requested through `context.requireDeviceFunctionality` in [`GranularityCase::checkSupport`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L452-L453). Implementations without the extension skip every leaf under that node.
- The `in_dynamic_render_pass` node is absent entirely from VulkanSC builds because the registration is wrapped in `#ifndef CTS_USES_VULKANSC`. See [`vktApiGranularityTests.cpp#L576-L579`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L576-L579) and [`vktApiGranularityTests.cpp#L588-L590`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L588-L590).

### Design-based pruning

- The format sweep stops at `VK_FORMAT_D32_SFLOAT_S8_UINT` (integer value `130`). It does not cover extension formats such as ASTC HDR, PVRTC, or the 16-bit depth/stencil packed formats, which sit above that enum value and are intentionally out of scope for this test family. See [`vktApiGranularityTests.cpp#L531`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L531).
- The `mandatoryFormats` pool used by the `random` node is a fixed 47-format list. It does not include every format in the sweep, so the random companion attachments are bounded to a curated set rather than the full `VkFormat` range.
- The render area passed into `vkCmdBeginRenderPass` and `vkCmdBeginRendering` is fixed at `1x1`, so no test case leaf exercises non-`1x1` render areas. The granularity value itself, not its relationship to a chosen render area, is what the test validates.

## Key Takeaways

- The family tests three properties of render-area granularity queries: the reported value is at least `1x1`, it is stable across consecutive queries against the same attachment set, and it does not exceed `maxFramebufferWidth` / `maxFramebufferHeight`.
- `single`, `multi`, and `random` all use `vkGetRenderAreaGranularity` outside any active render pass and only differ in attachment-set shape; the consistency check between two consecutive queries against the same `VkRenderPass` is trivial for these nodes.
- `in_render_pass` is the only `vkGetRenderAreaGranularity` node that actually begins the render pass between the two queries, so it is the only node that can detect a query that depends on render-pass-active state.
- `in_dynamic_render_pass` is the only node that exercises `vkGetRenderingAreaGranularityKHR` and the `VK_KHR_maintenance5` code path, including the `VkRenderingAreaInfoKHR` attachment-format list and the `vkCmdBeginRendering` interaction.
- All randomization is deterministic because `de::Random` is seeded with `215`; the attachment counts, extents, and `random` companion formats are reproducible across runs.
- See `## Failure Meaning` for how to interpret a failure, including which causes are grounded in spec semantics and which would need source-level investigation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createGranularityQueryTests` | [`vktApiGranularityTests.cpp#L463-L593`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L463-L593) | Builds the `granularity` test family and registers all five intermediate nodes with their per-format test case leaves |
| `TestMode` enum | [`vktApiGranularityTests.cpp#L57-L62`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L57-L62) | Picks the query entry point and whether a render pass is begun between the two queries |
| `mandatoryFormats` array | [`vktApiGranularityTests.cpp#L477-L525`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L477-L525) | Companion attachment pool used by the `random` node |
| `GranularityInstance::iterate` | [`vktApiGranularityTests.cpp#L282-L411`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L282-L411) | Runs the two granularity queries and the three `TCU_CHECK` assertions |
| `GranularityInstance::initImages` | [`vktApiGranularityTests.cpp#L140-L217`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L140-L217) | Creates the `VkImage` and `VkImageView` per attachment with optimal tiling and aspect-derived usage |
| `GranularityInstance::initObjects` | [`vktApiGranularityTests.cpp#L219-L280`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L219-L280) | Creates the render pass, framebuffer, command pool, and command buffer for non-dynamic modes |
| `GranularityCase::checkSupport` | [`vktApiGranularityTests.cpp#L437-L454`](../../../modules/vulkan/api/vktApiGranularityTests.cpp#L437-L454) | Prunes cases whose formats lack attachment features and requires `VK_KHR_maintenance5` for the dynamic node |
| Header | [`vktApiGranularityTests.hpp`](../../../modules/vulkan/api/vktApiGranularityTests.hpp#L1) | Declares `createGranularityQueryTests` |
| Parent registration | [`vktApiTests.cpp#L114`](../../../modules/vulkan/api/vktApiTests.cpp#L114) | Adds the `granularity` test family to the `api` test category |
