## Overview

**Core question:** Does a logical device spanning a physical-device group produce the expected image when rendering or compute work is split between, or assigned alternately to, group members? The multi-device compute alternate-dispatch path currently has a test-side readback mask mismatch, so that path reports a comparison failure before its image can be checked.

- This page covers the rendering and compute test families registered by `vktDeviceGroupRendering.cpp` under the `device_group` test category.
- Rendering cases use a 256x256 `VK_FORMAT_R8G8B8A8_UNORM` image. They exercise split-frame rendering (SFR), alternate-frame rendering (AFR), memory placement, peer fetch, tessellation, and line polygon mode.
- Compute cases attempt to write the same 256x256 image with a compute shader. They exercise split dispatch, alternate dispatch, dedicated allocations, and peer memory; the multi-device alternate-dispatch readback currently does not execute because its command-buffer and submit masks select different devices.
- Each executable leaf creates a logical device from one enumerated physical-device group, runs the selected mode for each adjacent device pair, copies the result to host-visible memory, and compares it with an expected image.

## Background Knowledge

- A logical device created with `VkDeviceGroupDeviceCreateInfo` can contain multiple physical devices from one enumerated device group. Vulkan assigns each physical device an index. Device masks select which indices execute later command-buffer work ([device groups](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L2010-L2020), [logical-device creation](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L2638-L2688)).
- A device-group resource has an instance on each physical device. `VkBindImageMemoryDeviceGroupInfo` can map those instances to memory, or describe non-overlapping split-instance bind regions. For `N` physical devices, split-instance regions use an `N * N` array, where element `i * N + j` describes the region in resource instance `i` bound to memory instance `j` ([resource binding](../../../../vulkan-docs/src/chapters/resources.adoc#L9524-L9539), [split-instance binding](../../../../vulkan-docs/src/chapters/resources.adoc#L11039-L11127)).
- Peer memory is memory allocated for one physical device and accessed by another physical device in the same logical device. `vkGetDeviceGroupPeerMemoryFeatures` reports which accesses are supported. The test asks for `VK_PEER_MEMORY_FEATURE_GENERIC_SRC_BIT` before using peer fetch, and checks copy-source support separately for an SFR readback path ([peer memory](../../../../vulkan-docs/src/chapters/memory.adoc#L6095-L6105), [peer-access limits](../../../../vulkan-docs/src/chapters/memory.adoc#L6164-L6180)).
- The command-buffer device mask filters action and synchronization commands. The submit mask also matters, so a command executes on a physical device only when the relevant device bits survive both masks ([command-buffer device mask](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L3881-L3912), [`vkCmdSetDeviceMask`](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L3952-L3987)).

## Registration Hierarchy

```text
device_group
├── afr
├── afr_dedicated
├── afr_dedicated_peer
├── afr_sys
├── afr_tessellated
├── afr_tessellated_linefill
├── compute_alternate_dispatch
├── compute_alternate_dispatch_dedicated
├── compute_alternate_dispatch_peer
├── compute_split_dispatch
├── compute_split_dispatch_dedicated
├── compute_split_dispatch_peer
├── sfr
├── sfr_dedicated
├── sfr_dedicated_peer
├── sfr_sys
├── sfr_tessellated
└── sfr_tessellated_linefill
```

The direct children come from [`DeviceGroupTestRendering::init()`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2645-L2715). The default Vulkan mustpass file contains all 18 children ([`device-group.txt`](../../../mustpass/main/vk-default/device-group.txt#L1-L18)). Vulkan SC registers only the six AFR rendering children and the three alternate-dispatch compute children ([`device-group.txt`](../../../mustpass/main/vksc-default/device-group.txt#L1-L9)); the SFR and split-dispatch registrations are compiled out by `#ifndef CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Rendering schedule | `sfr`, `afr` | Selects split-frame rendering or alternate-frame rendering | [`TestModeType`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L71-L80), [rendering registrations](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2648-L2690) |
| Rendering memory placement | default, `*_sys`, `*_dedicated` | Uses device-local or host-visible image memory, or adds dedicated allocation information | [`DeviceGroupTestInstance` flags](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L168-L175), [image allocation](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L803-L826) |
| Rendering peer fetch | `sfr_dedicated_peer`, `afr_dedicated_peer`, tessellated peer variants | Binds vertex, index, uniform, and tessellation-level buffers with per-device indices so one device can fetch data allocated for its peer | [peer buffer binding](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L525-L548), [peer checks](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L1137-L1149) |
| Rendering geometry | triangle, `*_tessellated`, `*_tessellated_linefill` | Chooses a three-vertex triangle or a tessellated sphere; linefill uses `VK_POLYGON_MODE_LINE` | [`TestModeType`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L74-L80), [pipeline selection](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L998-L1048) |
| Compute schedule | `compute_split_dispatch`, `compute_alternate_dispatch` | Selects two half-width `vkCmdDispatchBase` calls or one full `vkCmdDispatch` call | [`ComputeTestModeType`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L1839-L1846), [dispatch recording](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2468-L2490) |
| Compute allocation | default, `*_dedicated` | Adds `VkMemoryDedicatedAllocateInfo` to the allocation chain | [compute allocation setup](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2161-L2181) |
| Compute peer memory | `compute_split_dispatch_peer`, `compute_alternate_dispatch_peer` | Uses device-indexed bindings for the uniform buffer and requires generic peer-source access | [compute registrations](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2693-L2714), [compute peer binding](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2226-L2249) |
| Image and work size | `256x256`, `VK_FORMAT_R8G8B8A8_UNORM`; compute local size `16x16` | Fixes the comparison image and makes compute dispatch counts 16 by 16 | [render parameters](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L370-L381), [compute shader source](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2611-L2622) |

The source defines `TEST_MODE_HOSTMEMORY` and `COMPUTE_TEST_MODE_HOSTMEMORY`, but no registered compute child sets the compute host-memory bit. The rendering `sfr_sys` and `afr_sys` children set the rendering host-memory bit.

## Behavior Parameters

The primary behavioral axis is the registered test family. The families fall into four device-group execution mechanisms.

### `sfr` and its rendering variants: split-frame rendering

SFR is intended to use a shared render target with split-instance bindings when the selected group has more than one physical device. The render pass supplies per-device render areas for the left and right 128-pixel-wide halves. The draw command runs with a mask containing the adjacent pair, and the image binding maps the halves through `pSplitInstanceBindRegions`. The one-device case uses the full image region. However, the current source first binds `renderImage` with `vkBindImageMemory` and later attempts the split-instance `vkBindImageMemory2` binding; Vulkan memory binding is immutable after the first bind, so this is a confirmed test-side invalid operation rather than a valid SFR setup.

`*_sys` changes the render-image allocation to host-visible memory. `*_dedicated` adds dedicated allocation information. `*_dedicated_peer` combines dedicated allocation with device-indexed buffer bindings and requires generic peer-source access. `sfr_tessellated` and `sfr_tessellated_linefill` use the same SFR schedule with a tessellated sphere instead of the triangle.

### `afr` and its rendering variants: alternate-frame rendering

AFR records one indexed draw with the mask for `secondDeviceID`, while the command buffer is submitted with the mask for both adjacent devices. The full image is rendered by that selected device. `*_sys`, `*_dedicated`, `*_dedicated_peer`, `afr_tessellated`, and `afr_tessellated_linefill` add the rendering variations described above.

AFR does not use split-instance image regions for the ordinary render target. If the result cannot be copied directly from the peer memory instance, the host-side path creates an alias image, copies the full image from the second device to the first device, and reads from the first device.

### `compute_split_dispatch*`: split dispatch

For a multi-device group, the test divides the 16x16 workgroup grid into two vertical halves. It records `vkCmdDispatchBase` with base X zero and a half-width count on `firstDeviceID`, then records a second call with base X at the midpoint and the same count on `secondDeviceID`. The storage image uses split-instance bind regions so the two devices write separate image halves. For a one-device group, the test uses one full `vkCmdDispatch` call.

The `_dedicated` child adds dedicated allocation information. The `_peer` child uses device-indexed bindings and requires generic peer-source support. The registration sets the peer bit without the dedicated bit, so `compute_split_dispatch_peer` is not a combined dedicated-plus-peer case.

### `compute_alternate_dispatch*`: alternate dispatch

The test sets the device mask to `secondDeviceID` and records one full 16 by 16 `vkCmdDispatch`. For a one-device group, the subsequent readback also uses that device. For a multi-device pair, however, the readback command buffer sets its mask to `secondDeviceID` while submission uses `1 << firstDeviceID`; because commands execute only on devices included in both masks, the image-to-buffer copy does not execute. The `_dedicated` and `_peer` children vary allocation and device-indexed uniform-buffer binding in the same way as their split-dispatch counterparts.

## Shader Analysis

The shaders provide fixed data movement for the rendering and compute checks, but shader logic is not the behavior under test. The rendering vertex shader passes `in_Position` to `gl_Position`, the fragment shader writes the bound uniform color, and the optional tessellation stages turn the fixed six-vertex sphere and tessellation level into the sphere image. The compute shader maps `gl_GlobalInvocationID` to an image coordinate and stores the uniform color. The device-group behavior comes from resource instances, memory bindings, command-buffer device masks, render areas, and dispatch bases. No representative shader walkthrough is included.

## Runtime Execution and Result Checking

The rendering and compute instances share the following host/device sequence:

- `[host]` Read the selected `VKDeviceGroupId` and `VKDeviceId` command-line values, enumerate physical-device groups, and use the selected group's physical devices in `VkDeviceGroupDeviceCreateInfo`.
- `[host]` Create a logical device and obtain a queue. Rendering uses the universal queue family; compute uses the compute queue family. The instance and device support checks require `VK_KHR_device_group_creation` and `VK_KHR_device_group`.
- `[host]` For each physical device, set `firstDeviceID` to that index and `secondDeviceID` to the next index modulo the group size. The test allocates resources with a mask for the pair when the group reports subset allocation, or with all group bits otherwise.
- `[host]` Create host-visible staging buffers and device resources. Rendering creates vertex and index buffers, a uniform buffer containing `drawColor`, a color attachment image, a read image, a render pass, descriptors, a graphics pipeline, and a readback buffer. Compute creates a uniform buffer, a storage image, a descriptor set, a compute pipeline, and a readback buffer.
- `[host]` Copy staging data into device-local buffers and use pipeline barriers to order transfer writes before vertex input, fragment reads, tessellation reads, or compute reads. Rendering transitions the image to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`; compute transitions the storage image to `VK_IMAGE_LAYOUT_GENERAL`.
- `[device]` Run the selected rendering or compute schedule under the selected device masks. Rendering clears the target to `(0.125, 0.25, 0.75, 1.0)` and writes yellow `(1.0, 1.0, 0.0, 1.0)` where the geometry covers pixels. Compute writes yellow to every invocation's image coordinate.
- `[host]` Transition the output to a transfer-source layout, copy the image into host-visible memory, submit the command buffer with the required device mask, wait for device idle, and invalidate the mapped allocation.
- `[host]` Compare the mapped 256x256 result. Triangle rendering builds a software reference from the triangle and uses `tcu::intThresholdPositionDeviationCompare()` with zero color threshold and one-pixel position deviation. Tessellated rendering loads `spherefilled.png` for filled polygons or `sphere.png` for line polygons and uses `tcu::fuzzyCompare()` with threshold `0.001`. Compute clears a reference image to yellow and uses `tcu::intThresholdPositionDeviationCompare()` with zero color and position deviation; in multi-device alternate-dispatch cases, the preceding readback copy is skipped by the mismatched masks, so this comparison reports failure rather than validating the dispatch output.
- `[host]` Return failure on the first failed pair comparison. A successful rendering instance returns `Device group verification passed`; a successful compute instance returns `Device group compute verification passed`.

The SFR path may read the split-bound render image directly when peer copy-source access is supported. Otherwise it copies the needed right half into an alias image bound with the opposite device indices before copying the complete result to the readback buffer. AFR copies the full image when that extra peer-image path is needed.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sfr` and its variants | Split-instance image binding, per-device render areas, paired device masks, peer fetch, or SFR copyback does not preserve the expected rendered image |
| `afr` and its variants | Alternate-device execution, multi-device resource visibility, or full-image peer copyback does not preserve the expected rendered image |
| `compute_split_dispatch*` | Split `vkCmdDispatchBase` coverage, split-instance storage-image binding, or per-device memory access produces a wrong image |
| `compute_alternate_dispatch*` | A full dispatch on the selected alternate device, its storage-image or uniform-buffer visibility, or the source readback mask mismatch produces a failed image check |
| Shared infrastructure | Logical-device creation, resource allocation, barriers, submission masks, readback, or reference comparison is incorrect |

### Cause Analysis

#### Split-frame rendering and split dispatch

**Possible failure symptoms:** The triangle or sphere is missing from one half of the image, the compute image has a blank or incorrect half, or the comparison reports pixels outside the expected half.

**Possible implementation causes:** The implementation may apply a device mask to only part of the recorded work, associate a split-instance rectangle with the wrong memory instance, or fail to make the image contents visible across the two device instances. The Vulkan rules for `pSplitInstanceBindRegions` require an `N * N` region mapping and non-overlapping regions for the same instance ([split-instance binding](../../../../vulkan-docs/src/chapters/resources.adoc#L11071-L11127)). For compute, an incorrect `vkCmdDispatchBase` base or count can leave a gap or overlap between the two halves ([`vkCmdDispatchBase`](../../../../vulkan-docs/src/chapters/dispatch.adoc#L177-L250)). Source-level investigation is needed to distinguish binding, mask, dispatch, and synchronization causes for a particular failure.

#### Alternate-device execution

**Possible failure symptoms:** An AFR or alternate-dispatch result is blank, contains the clear color, or differs from the corresponding single-device reference even though the work was recorded once.

**Possible implementation causes:** The implementation may ignore the command-buffer device mask for the draw or dispatch, use the wrong physical-device instance for the bound resource, or lose the selected device's writes when the host reads through the first device. The spec requires a command to execute only on physical devices included in both the command-buffer and submit masks ([command-buffer device mask](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L3909-L3912)). In the multi-device compute alternate-dispatch path, the source itself sets the readback command-buffer mask to `secondDeviceID` but submits with `1 << firstDeviceID`, whose intersection is empty; this confirmed test-side defect causes the readback copy to be skipped and the later comparison to fail. Other mask or resource-instance causes require source-level investigation for a particular failure.

#### Peer memory access

**Possible failure symptoms:** A `*_peer` case is skipped when generic peer access is unavailable, or, when it runs, the rendered geometry or compute color is wrong after one device reads data allocated for the other.

**Possible implementation causes:** The implementation may report or implement `VK_PEER_MEMORY_FEATURE_GENERIC_SRC_BIT` incorrectly, apply `pDeviceIndices` to the wrong buffer instance, or fail to preserve data visibility for a peer read. The test checks generic-source support for both directions before using peer fetch and checks copy-source support before selecting the direct SFR readback path. Source-level investigation is needed to attribute a failed image comparison to peer binding or synchronization rather than to rendering or dispatch.

#### Image and host readback

**Possible failure symptoms:** The GPU work appears to complete, but the copied image contains stale data, the wrong layout contents, or a result that differs from the expected image across all execution modes.

**Possible implementation causes:** The implementation may mishandle the image layout transition, transfer read, host-read barrier, device mask on the copy, or host-visible allocation invalidation. The test transitions rendering images from color-attachment output and compute images from shader writes before `vkCmdCopyImageToBuffer`, then waits for idle before mapping the buffer. The failure could also come from the test's resource or reference setup, so source-level investigation is needed before assigning it to a driver subsystem.

#### Reference comparison

**Possible failure symptoms:** Triangle cases fail the one-pixel position comparison, tessellated cases fail the archived PNG comparison, or compute cases fail the exact yellow-image comparison.

**Possible implementation causes:** The implementation may produce incorrect rasterization, tessellation, polygon mode, image writes, or transfer contents. A failure can also expose a mismatch between the software reference and the test setup, so the logged comparison and source setup must be checked before treating it as a device-group defect.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_device_group_creation` at instance level and `VK_KHR_device_group` at device level. Dedicated variants additionally require `VK_KHR_dedicated_allocation` ([support checks](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L1718-L1771)).
- The selected `VKDeviceGroupId` must identify an enumerated group, and `VKDeviceId` must be within that group's physical-device count. An invalid value raises `NotSupportedError` during support or initialization ([rendering support](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L1728-L1761), [compute initialization](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L1971-L2027)).
- Peer variants require at least two physical devices and then require generic peer-source access for the relevant memory heap. Unsupported peer access produces `NotSupportedError`, not an image-comparison failure ([rendering peer checks](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L525-L526), [compute peer checks](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2226-L2227)).
- SFR requires `VK_FORMAT_R8G8B8A8_UNORM` with color-attachment and transfer-source usage plus `VK_IMAGE_CREATE_SPLIT_INSTANCE_BIND_REGIONS_BIT` support. If the image-format query fails, the case raises `NotSupportedError` ([SFR format check](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L764-L783)).
- Tessellated cases require `tessellationShader`; linefill cases require `fillModeNonSolid` ([feature checks](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L1763-L1770)).
- `VK_KHR_bind_memory2` is required when the mode is not AFR or when the selected group has more than one physical device. The compute check uses the same condition with alternate dispatch in place of AFR ([rendering initialization](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L265-L269), [compute initialization](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L1996-L2003)).

These conditions mean that the case is not supported by the selected group or implementation. They do not indicate a failed rendering or compute result.

### Design-based pruning

- SFR and split-dispatch children are omitted from Vulkan SC builds by `#ifndef CTS_USES_VULKANSC`; the Vulkan SC mustpass file therefore contains only AFR and alternate-dispatch paths.
- The source registers only adjacent pairs, using `(firstDeviceID + 1) % m_physicalDeviceCount`, rather than every ordered pair of physical devices. The loop still visits every physical device as the first member of one pair.
- SFR and split dispatch divide the image or workgroup grid into two vertical halves even when the logical device contains more than two physical devices. The test varies the adjacent pair over the group instead of creating one region per physical device for a single execution.
- The registered matrix does not include compute host-memory cases even though the compute mode enum defines `COMPUTE_TEST_MODE_HOSTMEMORY`. It also does not combine `compute_split_dispatch_peer` or `compute_alternate_dispatch_peer` with the dedicated bit.

## Key Takeaways

- The page tests device-group resource instances and execution masks through observable image output. It does not test a shader algorithm.
- SFR and split dispatch divide a 256-pixel-wide image or a 16 by 16 workgroup grid between adjacent devices. AFR and alternate dispatch assign the whole operation to the second device in the pair.
- Dedicated allocation, host-visible rendering images, peer buffer binding, tessellation, and line polygon mode change resource or graphics setup while preserving the same device-group comparison.
- A `NotSupportedError` records a missing requirement or unsupported access mode. A rendered or computed image comparison failure means that the selected device-group execution path did not produce the expected image, subject to the specific comparison tolerance.
- The default Vulkan mustpass covers 18 direct children. Vulkan SC covers nine AFR and alternate-dispatch children because the source excludes SFR and split-dispatch registrations.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Rendering and compute registrations | [`DeviceGroupTestRendering::init()`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2645-L2715) | Defines all direct test-family names and their mode flags. |
| Package registration | [`createTests()`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2717-L2720), [`addRootChild("device_group", ...)`](../../../modules/vulkan/vktTestPackage.cpp#L1377-L1379) | Places the implementation under the `device_group` test category. |
| Rendering support and programs | [`DeviceGroupTestCase::checkSupport()`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L1700-L1771), [`initPrograms()`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L1774-L1837) | Defines feature gates and the fixed rendering shader stages. |
| Rendering execution and checking | [`DeviceGroupTestInstance::iterate()`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L370-L1697) | Creates resources, records masks and render areas, copies results, and compares images. |
| Compute support and resources | [`DeviceGroupComputeTestInstance::init()`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L1942-L2111) | Creates the logical device and compute queue and applies compute requirements. |
| Compute execution and checking | [`DeviceGroupComputeTestInstance::iterate()`](../../../modules/vulkan/device_group/vktDeviceGroupRendering.cpp#L2113-L2590) | Records split or alternate dispatch, reads back the storage image, and compares it. |
| Default Vulkan mustpass coverage | [`device-group.txt`](../../../mustpass/main/vk-default/device-group.txt#L1-L18) | Confirms the 18 registered direct children in the default Vulkan profile. |
| Vulkan SC mustpass coverage | [`device-group.txt`](../../../mustpass/main/vksc-default/device-group.txt#L1-L9) | Confirms the nine direct children available in Vulkan SC. |
| Device-group extension semantics | [`VK_KHR_device_group`](../../../../vulkan-docs/src/appendices/VK_KHR_device_group.adoc#L19-L25) | Defines the extension's logical-device, memory, binding, and masked-command scope. |
| Device masks and split bindings | [`cmdbuffers.adoc`](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L3881-L3987), [`resources.adoc`](../../../../vulkan-docs/src/chapters/resources.adoc#L11039-L11127) | Defines command execution filtering and `pSplitInstanceBindRegions`. |
| Render-pass device-group behavior | [`renderpass.adoc`](../../../../vulkan-docs/src/chapters/renderpass.adoc#L7711-L7762) | Defines render-pass device masks and per-device render areas. |
| Peer memory | [`memory.adoc`](../../../../vulkan-docs/src/chapters/memory.adoc#L6095-L6180) | Defines peer access queries and the generic-source capability used by peer variants. |
| Compute dispatch bases | [`dispatch.adoc`](../../../../vulkan-docs/src/chapters/dispatch.adoc#L177-L250) | Defines `vkCmdDispatchBase` and its base-plus-count behavior. |
