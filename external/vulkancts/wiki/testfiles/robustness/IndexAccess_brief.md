# Understanding Brief: indexed-draw robustness

## One-Sentence Test Purpose

This test checks whether indexed drawing handles out-of-range index-buffer accesses according to robustness2 and index-binding-size rules across direct, indirect, multi-draw, and device-address command paths.

## Background Knowledge

### Robust index fetches

An indexed draw reads an index, then uses that value to fetch vertex data. An access can become invalid because the draw starts beyond the bound index range, the index value addresses unavailable vertex data, or the bound index-buffer size excludes bytes that the draw tries to read.

Why it matters here:
- `robustBufferAccess2` defines deterministic behavior for the out-of-bounds index fetch used by `index_access`.
- `vkCmdBindIndexBuffer2` supplies an explicit binding size, so offset and size jointly define the accessible index range.

## One Concrete Example

For `robustness.index_access.draw_indexed_2`, the host prepares a six-point indexed draw but sets `firstIndex` near `UINT32_MAX`. The resulting index fetch is out of bounds. With robustness2 enabled, the fetched index must behave as zero, producing one fragment in the expected middle-top image region.

## End-to-End Test Flow

```text
[host] select the draw mode, binding mode, offset, and out-of-range condition
[host] create deterministic vertex/index data and a color target
[host] bind buffers by handle or device address
[host] record the selected direct, indirect, indirect-count, or multi-indexed draw
[device] perform indexed fetches and rasterize any surviving triangles
[host] copy the color image to readable memory
[host] inspect expected sample locations or the expected-color fragment count
[host] report pass only when the observed image matches the selected robustness condition
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The cases use simple graphics shaders and vary command recording rather than shader behavior. Indirect modes additionally populate draw-command buffers; indirect-count modes provide count data.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | read | no | Supplies deterministic positions and colors. |
| Index buffer | yes | yes | read | no | Carries the deliberately out-of-range access condition. |
| Indirect command/count buffers | yes | yes | read | no | Select command parameters for indirect variants. |
| Color attachment and readback storage | yes | yes | written | yes | Makes robust index-fetch behavior observable. |

## What Is Checked

- `index_access` requires the robustness2 case to produce exactly one expected-color fragment in the middle-top region.
- `bind_index_buffer2` samples three image locations. `oo_none` must draw the robustness-sensitive quadrant; `oo_index`, `oo_size`, and `oo_whole_size` must leave it clear while preserving the required valid draw.

## Behavior Parameter Identification

> **Behavior parameter:** test family and out-of-range type
>
> **Candidate values:** `index_access`, `oo_none`, `oo_index`, `oo_size`, `oo_whole_size`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `index_access` | Out-of-bounds `firstIndex` handling did not produce the robustness2 zero-index result, or the selected command path used incorrect draw parameters. |
| `oo_none` | A valid sized binding failed to preserve the expected indexed draw. |
| `oo_index` | An out-of-range index value was not suppressed as required. |
| `oo_size` | The explicit binding size was not honored when determining the accessible index range. |
| `oo_whole_size` | `VK_WHOLE_SIZE` handling did not derive the usable range correctly from the binding offset. |

## Important Variations and Special Cases

- `index_access` covers direct, indirect, indirect-count, and multi-indexed draws; non-VulkanSC non-multi modes also have `_device_address` variants.
- `bind_index_buffer2` uses `offset_0` and `offset_100`, with device-address variants only for selected `offset_100` non-multi cases.
- Indirect-count, multi-draw, robustness2, maintenance5, and device-address variants are pruned when their required extensions or features are unavailable.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `index_access` execution and checking | [`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L165-L461) | Builds the out-of-bounds draw and validates the image. |
| `bind_index_buffer2` execution and checking | [`BindIndexBuffer2Instance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L787-L1113) | Applies offset/size/index conditions and samples the result. |
| `bind_index_buffer2` registration | [`createCmdBindIndexBuffer2Tests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1116-L1172) | Defines offsets, modes, out-of-range types, and address variants. |
| `index_access` registration | [`createIndexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1174-L1205) | Defines the seven direct test case leaves. |

## Questions / Risk Points for User Audit

- Is the distinction between an out-of-bounds `firstIndex` and an explicitly restricted index-buffer binding clear?
- Are the sampled image outcomes sufficient to explain each `oo_*` condition without shader detail?
- Should device-address command variants receive more explanation than their shared observable result requires?

## Conversion Notes for Final Wiki Rewrite

Keep the final page centered on index-access conditions and image validation. Treat command mode, offsets, and address-based binding as matrix dimensions; use test family/out-of-range type as the behavioral axis. The shaders are fixed observation machinery, so no representative shader walkthrough is needed.
