# vktRobustnessIndexAccessTests

## Overview

This page documents two Vulkan CTS robustness roots implemented by [`vktRobustnessIndexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1-L1207): `robustness.index_access` and, for non-VulkanSC builds, `robustness.bind_index_buffer2`. Both roots exercise indexed drawing with intentionally out-of-range index-buffer situations. The `index_access` root focuses on robustness2 behavior for out-of-bounds `firstIndex`; the `bind_index_buffer2` root focuses on index binding size, offset, and index-value out-of-range behavior through `vkCmdBindIndexBuffer2` or device-address command variants.

## Role of file

[`vktRobustnessIndexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1174-L1205) is an implementation and registration file for `index_access`. The same source also registers `bind_index_buffer2` in [`createCmdBindIndexBuffer2Tests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1116-L1172). The category root adds `index_access` unconditionally and `bind_index_buffer2` only outside `CTS_USES_VULKANSC` ([`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L65-L68), [`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L91-L94)). The header exposes both factories ([`vktRobustnessIndexAccessTests.hpp`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.hpp#L30-L37)).

## Source code link

- Source: [`vktRobustnessIndexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1-L1207)
- Header: [`vktRobustnessIndexAccessTests.hpp`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.hpp#L1-L41)

## Inspected related files

| File | Evidence used |
|------|---------------|
| [`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L61-L99) | Category root registration and VulkanSC guard for `bind_index_buffer2`. |
| [`vktRobustnessIndexAccessTests.hpp`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.hpp#L35-L36) | Factory declarations for both documented roots. |
| [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L1-L41) | Default mustpass entries for `bind_index_buffer2`. |
| [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13746-L13752) | Default mustpass entries for `index_access`. |

## Registration Hierarchy

### `robustness.index_access`

```text
robustness.index_access
├── draw_indexed_2
├── draw_indexed_2_device_address
├── draw_indexed_indirect_2
├── draw_indexed_indirect_2_device_address
├── draw_indexed_indirect_count_2
├── draw_indexed_indirect_count_2_device_address
└── draw_multi_indexed_2
```

The root group name is `index_access`, and its direct children are generated from four draw modes plus non-VulkanSC device-address variants for all modes except multi-draw ([`createIndexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1174-L1205)). The inspected mustpass file confirms the seven direct leaves ([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13746-L13752)).

### `robustness.bind_index_buffer2`

```text
robustness.bind_index_buffer2
├── offset_0
└── offset_100
```

The root group name is `bind_index_buffer2`, and it expands directly to the two offset groups generated from `offsets[] = {0, 100}` ([`createCmdBindIndexBuffer2Tests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1116-L1172)). The category root registers this group only in non-VulkanSC builds ([`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L91-L94)).

## Test Families

### `draw_indexed_2`, `draw_indexed_indirect_2`, `draw_indexed_indirect_count_2`, `draw_multi_indexed_2`

These `index_access` leaves construct a six-point indexed draw, set `firstIndex` to a very large value (`max uint32 - 100`), and expect robustBufferAccess2 behavior to fetch index 0 for the out-of-bounds access ([`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L165-L212), [`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L317-L340)). The draw command varies by leaf: direct indexed draw, indirect indexed draw, indirect-count indexed draw, and `VK_EXT_multi_draw` indexed draw ([`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L323-L340)).

### `*_device_address` leaves under `index_access`

For non-VulkanSC builds, the direct, indirect, and indirect-count modes add device-address-command variants. These bind vertex/index buffers by address and use `vkCmdDrawIndexedIndirect2KHR` or `vkCmdDrawIndexedIndirectCount2KHR` for indirect variants ([`createIndexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1195-L1201), [`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L343-L388)). The multi-draw mode is excluded from this variant in the generator ([`createIndexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1195-L1201)).

### `offset_0` and `offset_100` under `bind_index_buffer2`

Each offset group contains draw-mode subgroups for direct, indirect, indirect-count, and multi-indexed drawing. Each draw-mode subgroup contains out-of-range type leaves `oo_none`, `oo_index`, `oo_size`, and `oo_whole_size`; selected `offset_100` non-multi leaves also add `_device_address` variants ([`createCmdBindIndexBuffer2Tests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1118-L1168)). The implementation populates leading indices according to the offset, binds from `bindingOffset = leadingCount * 6 * sizeof(uint32_t)`, then changes the index data or binding size according to the out-of-range type ([`BindIndexBuffer2Instance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L831-L860)).

## Parameter dimensions and observed values

| Dimension | Observed values / ranges | Evidence |
|-----------|--------------------------|----------|
| Registered roots | `index_access`, `bind_index_buffer2` | [`createIndexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1174-L1205), [`createCmdBindIndexBuffer2Tests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1116-L1172) |
| Draw modes | `draw_indexed`, `draw_indexed_indirect`, `draw_indexed_indirect_count`, `draw_multi_indexed` | [`TestMode`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L61-L67), mode arrays in [`createCmdBindIndexBuffer2Tests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1118-L1123) and [`createIndexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1179-L1184) |
| `index_access` robustness version suffix | `2` | `params.robustnessVersion = 2` and name construction in [`createIndexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1186-L1193) |
| Device-address-command variants | `*_device_address` for `index_access` non-multi modes; for `bind_index_buffer2`, offset `100`, non-multi modes, and non-`oo_whole_size` out-of-range types | [`createIndexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1195-L1201), [`createCmdBindIndexBuffer2Tests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1153-L1164) |
| Out-of-range types for `bind_index_buffer2` | `oo_none`, `oo_index`, `oo_size`, `oo_whole_size` | [`OutOfTypes`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1125-L1130) |
| Offsets for `bind_index_buffer2` | `offset_0`, `offset_100` | [`offsets`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1132-L1140) |
| Render sizes | `16 x 16` for `index_access`; `64 x 64` for `bind_index_buffer2` | [`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L168-L170), [`BindIndexBuffer2Instance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L787-L790) |

## Support / feature requirements

- Portability-subset devices must support `robustBufferAccess`, otherwise both test-case classes reject execution through the inherited support path ([`DrawIndexedTestCase::checkSupport()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L492-L497)).
- Indirect-count modes require `VK_KHR_draw_indirect_count`; multi-indexed modes require `VK_EXT_multi_draw` ([`DrawIndexedTestCase::checkSupport()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L499-L502)).
- `index_access` uses robustness version 2 and requires either `VK_KHR_robustness2` or `VK_EXT_robustness2` plus `robustBufferAccess2` ([`DrawIndexedTestCase::checkSupport()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L503-L520)).
- Device-address-command variants require `VK_KHR_device_address_commands`; device creation enables the related device-address and command features when those variants are used ([`DrawIndexedTestCase::checkSupport()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L521-L523), [`DrawIndexedTestCase::createDeviceAndDriver()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L547-L583)).
- `bind_index_buffer2` additionally requires `VK_KHR_maintenance5` through `DEPENDENT_MAINTENANCE_5_EXTENSION_NAME` ([`BindIndexBuffer2TestCase::checkSupport()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L728-L738)).

## Verification methods

- `index_access` submits a draw with an out-of-bounds index-buffer `firstIndex`; for robustness versions below 2 it only checks that execution completes, while robustness2 cases read the color image and require exactly one expected-color fragment in the middle-top region ([`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L415-L461)).
- `bind_index_buffer2` renders triangles with known quadrants, reads back the image, samples three representative pixels, and sets the verdict to require clear color in locations that should not be drawn and drawn color in the required third-quarter location ([`BindIndexBuffer2Instance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1080-L1113)).
- For `oo_none`, `bind_index_buffer2` expects the sampled robustness-sensitive quadrant to be drawn; for the other out-of-range types it expects that quadrant to remain clear ([`BindIndexBuffer2Instance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1100-L1109)).

## Test principles

- Use small deterministic vertex/index buffers, then make the indexing operation out of range by manipulating `firstIndex`, index values, binding size, or binding offset ([`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L182-L212), [`BindIndexBuffer2Instance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L831-L860)).
- Compare robust and non-error outcomes through rendered-image observations rather than validation-layer messages ([`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L420-L461), [`BindIndexBuffer2Instance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1080-L1113)).
- Exercise both classic buffer handles and newer address-based command paths when the generator enables `_device_address` variants ([`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L317-L388), [`BindIndexBuffer2Instance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L981-L1063)).

## Notes / uncertainties

- The `bind_index_buffer2` parseable hierarchy intentionally expands only one level below the root, so `draw_indexed` and `oo_*` descendants are described in Test Families rather than included in the tree.
- `bind_index_buffer2` is documented as non-VulkanSC because the category root places its factory inside `#ifndef CTS_USES_VULKANSC` ([`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L91-L95)).
- The inspected default mustpass file confirms `bind_index_buffer2` entries near the start and `index_access` entries near line 13746; other mustpass profiles were not inspected.
