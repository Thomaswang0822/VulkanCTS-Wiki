# Understanding Brief: WSI maintenance1 tests

## One-Sentence Test Purpose

This test family checks whether a Vulkan WSI implementation handles present fences, compatible present mode changes, presentation scaling, deferred swapchain image allocation, and explicit release of acquired swapchain images.

## Background Knowledge

### Swapchain image ownership and presentation

`vkAcquireNextImageKHR` gives the application an image that it can use, while `vkQueuePresentKHR` releases the presented image to the presentation engine. `vkReleaseSwapchainImagesKHR` supplies a second release path for acquired images that the application will not present. The release call requires the image to be out of device use, so the test waits on a submission fence before releasing images when needed.

Why it matters here:
- The release tests exercise both the ordinary present path and the explicit release path.
- Window changes can retire a swapchain while acquired images still belong to it.

### Maintenance1 extension contracts

The maintenance1 extensions add structures to surface capability queries, swapchain creation, and `VkPresentInfoKHR`. A present fence signals when a present operation completes. A present mode list attached at swapchain creation defines the modes that `VkSwapchainPresentModeInfoKHR` may select later. Deferred allocation allows an implementation to delay backing a swapchain image until `vkAcquireNextImageKHR` returns its index.

Why it matters here:
- The tests must enable the maintenance feature before using these structures or the deferred allocation flag.
- The implementation must honor the relationships between queried capabilities, configured swapchains, and later present operations.

## One Concrete Example

A representative `present_modes` case queries the compatible modes for `VK_PRESENT_MODE_FIFO_KHR`, creates a swapchain with that list, and submits repeated presents. On most iterations it attaches `VkSwapchainPresentModeInfoEXT` to `VkPresentInfoKHR` and selects one of the modes returned by the query. The test accepts the mode change when the present call and per-swapchain result return success.

A representative `release_images` iteration acquires several images, chooses one for presentation, and puts the remaining indices in `VkReleaseSwapchainImagesInfoEXT`. The test shuffles the release order, optionally resizes the window, waits for submitted work when necessary, and calls `vkReleaseSwapchainImagesKHR` before or after presentation.

## End-to-End Test Flow

```text
[host] choose a WSI type, present mode, maintenance extension preference, and family-specific parameters
[host] enumerate extensions, create a surface and window, and create the device with the required feature chain
[host] query surface formats, capabilities, supported present modes, and maintenance1 capability structures
[host] create one or more swapchains, optionally with scaling, compatible modes, deferred allocation, or bound images
[host] acquire swapchain images and record transfer commands that clear or fill the selected images
[host] submit the commands and queue presentation, optionally attaching present fences, a present mode selection, or release work
[device] execute the transfer and presentation operations
[host] wait for fences, inspect fence ordering and query results, recreate a swapchain after an out-of-date result, and release images when selected
[host] report failure for an invalid query result, failed WSI result, broken fence ordering, or unexpected swapchain/image state
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The tests do not generate GLSL, HLSL, or SPIR-V. They record transfer commands with `vkCmdClearColorImage` or `vkCmdCopyBufferToImage`, then present the resulting swapchain images. The test matrix comes from C++ arrays of present modes, scaling flags, gravity flags, resize modes, and release choices.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkSurfaceKHR` and native windows | yes | indirectly | presentation engine uses the surface | no | Supplies the WSI target and resize events. |
| `VkSwapchainKHR` and its `VkImage` objects | yes | yes | transfer commands write acquired images | no | Carries the image ownership, scaling, deferred allocation, and retirement behavior under test. |
| Host-visible color buffers in `scalingTest` | yes | yes | `vkCmdCopyBufferToImage` reads them | no | Fill the four swapchain quadrants with fixed colors. |
| Command buffers, semaphores, and fences | yes | yes | queue submission and presentation use them | fence status is queried by host | Establish operation completion and present ordering. |
| `VkDeviceMemory` for deferred `bind_image` cases | yes, through `SimpleAllocator` | yes | backs manually bound swapchain-compatible images | no | Tests lazy binding after an acquired image index becomes available. |

The color buffers and transfer commands provide observable work for presentation, but the scaling family does not capture the displayed image. The source records this limitation in a TODO comment at `vktWsiMaintenance1Tests.cpp#L1909`.

## What Is Checked

- Compatible mode queries return supported modes, include the queried mode when the list is nonempty, contain no duplicates, and remain stable across count-only, undersized, correctly sized, and oversized queries.
- Scaling capability queries report only the defined scaling and gravity bits. Compatible modes report the same scaling and gravity capabilities.
- Present calls return acceptable WSI results. Present fences eventually signal, and ordering cases reject an unsignaled earlier fence after a later fence has signaled.
- Deferred allocation cases acquire and present images. Bind-image variants bind the image associated with an acquired index before commands use it.
- Release cases return successfully for the selected acquired indices and continue the acquire, present, resize, and swapchain-retirement sequence.
- A test returns a failure status for invalid returned data, inconsistent counts, duplicate modes, invalid WSI results, or an internal image-count invariant violation.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `present_fence`, `present_modes`, `scaling`, `deferred_alloc`, `release_images`

The page covers five implemented test families in one source file. Present mode, scaling, gravity, resize, and release settings change cases within those families, but the family determines the maintenance1 contract being checked.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `present_fence` | Incorrect present-fence signaling or ordering, invalid multi-swapchain/null-handle handling, or a failed present operation. |
| `present_modes` | Incorrect compatible-mode query results or an invalid dynamic present-mode transition. |
| `scaling` | Invalid capability bits, inconsistent capabilities across compatible modes, or a failed scaling configuration/present operation. |
| `deferred_alloc` | The implementation allocated or exposed swapchain image memory at the wrong time, or failed a deferred bind/present sequence. |
| `release_images` | The implementation rejected a valid release sequence, mishandled released ownership during resize or retirement, or returned an unexpected WSI result. |

## Important Variations and Special Cases

- The source supports both the KHR and EXT names. `chooseExt` honors the requested preference when both names are available and falls back to the available version when only one exists.
- The source repeats present mode values `immediate`, `mailbox`, `fifo`, `fifo_relaxed`, `demand`, `continuous`, and `fifo_latest_ready`. Runtime support checks remove unsupported modes.
- Multi-swapchain cases are omitted for Android, direct DRM, and direct display WSI types because the WSI wrapper cannot support the required setup there.
- `deferred_alloc.bind_image` excludes `demand` and `continuous` because the source deliberately omits those cases. `release_images` uses `no_scaling` and `stretch`; `scaling` also covers `one_to_one` and `aspect_stretch`.
- FIFO cases use fewer iterations than non-vsync cases. Resize-heavy loops reduce the count further because window resizing is slow. `release_images` uses a deterministic random generator to vary acquire count, presentation choice, release order, and resize occurrence.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Extension preference and instance/device setup | [chooseExt and WSI setup](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L83-L262) | Shows KHR/EXT fallback, required extensions, and the `swapchainMaintenance1` feature chain. |
| Present fence execution and ordering | [presentFenceTest](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L770-L1154) | Creates swapchains, submits presents, checks results, and verifies fence order. |
| Present fence registration | [populatePresentFenceGroup](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1156-L1221) | Defines present modes and the `basic`, `ordering`, multi-swapchain, and `null_handles` cases. |
| Compatible mode query | [presentModesQueryTest](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1231-L1391) | Defines the query validation contract. |
| Scaling behavior | [scalingTest](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1546-L1925) | Configures scaling and gravity and presents quadrant-filled images. |
| Deferred allocation registration | [populateDeferredAllocGroup](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2099-L2157) | Defines basic, bind-image, and multi-swapchain deferred cases. |
| Image release execution | [releaseImagesTest](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2179-L2567) | Exercises acquire, release, resize, present, out-of-date, and retirement paths. |
| Family registration | [createMaintenance1Tests](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2661-L2673) | Registers the five page-scope test families. |
| Vulkan WSI ownership rules | [Vulkan WSI chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc) | Defines acquire, present, release, deferred allocation, and maintenance1 structure semantics. |

## Questions / Risk Points for User Audit

- The scaling cases write colored quadrants but do not capture the displayed image. The page must describe capability/configuration coverage, not claim pixel-level scaling validation.
- The source uses EXT-suffixed structure and function names even when the KHR extension is selected. The page preserves the source identifiers while explaining the KHR/EXT fallback.
- The complete generated matrix is much larger than the visible hierarchy. The final page should describe dimensions and representative case names without listing every leaf.
- The mustpass files contain platform-specific subsets. Registration validation should use the source-derived hierarchy, while mustpass examples should make clear that unsupported platform combinations are pruned.

## Conversion Notes for Final Wiki Rewrite

- Keep the final page focused on five maintenance1 contracts and use the family as the primary behavior axis.
- Preserve the brief's failure mapping table verbatim in the final page, then write fresh cause analysis from the source checks and Vulkan WSI semantics.
- Distill the ownership, scaling, and deferred allocation explanations into short Background Knowledge bullets. Move concrete setup into Runtime Execution.
- Keep `## Shader Analysis`, but state that the tests contain no shader code and do not need a shader-analyzer or shader-disassembler walkthrough.
- Use the registration tree only through the five direct children. Put present mode, scaling, gravity, resize, and release values in parameter tables.
