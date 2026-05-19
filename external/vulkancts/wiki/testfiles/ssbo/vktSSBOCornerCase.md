# vktSSBOCornerCase.cpp

## Overview

[`vktSSBOCornerCase.cpp`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L1) registers the `ssbo.corner_case` subgroup and one physical-storage-buffer stress case named `long_shader_bitwise_and`. The registered shader uses `GL_EXT_buffer_reference`, a buffer-reference block with an unsized `ivec4` array, and a generated loop of comparisons whose count is controlled by `m_testSize` in [`CornerCase`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L46-L60) and [`useCornerCaseShader()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L62-L99).

## Role

Implementation-heavy registered subgroup file. It does not own the `ssbo` root; the root file adds this subgroup through [`createTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2252), and [`createSSBOCornerCaseTests()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334) constructs the actual displayed group name `corner_case`.

## Source Code

- Primary source: [`vktSSBOCornerCase.cpp`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L1)
- Public factory declaration: [`vktSSBOCornerCase.hpp`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.hpp#L29-L34)
- Parent registration: [`vktSSBOLayoutTests.cpp`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2235-L2255)

## Registration Hierarchy

```text
ssbo.corner_case
└── long_shader_bitwise_and
```

## Test Families

### long_shader_bitwise_and — Buffer-reference long comparison shader

[`createSSBOCornerCaseTests()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334) creates a `corner_case` group and adds one [`CornerCase`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L46-L60) named `long_shader_bitwise_and`. The generated compute shader enables `GL_EXT_buffer_reference`, declares `BlockA` as a `std430` buffer-reference block with `ivec4 a[]`, declares an auxiliary storage buffer at binding `0`, and repeatedly bitwise-ANDs comparison results for generated `ivec4` constants in [`useCornerCaseShader()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L62-L99).

## Parameter Dimensions

| Dimension | Evidence-backed values |
|---|---|
| Loop/comparison count | [`m_testSize`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L57-L60) is `589`; the comment states this is the minimum value that caused a crash in the targeted regression. |
| Shader extension and storage forms | [`useCornerCaseShader()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L67-L78) emits `#extension GL_EXT_buffer_reference : enable`, a `std430` buffer-reference block, a `std140` storage buffer at binding `0`, and a push constant containing the buffer-reference pointer. |
| Reference data | [`useCornerCaseShader()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L65-L90) uses deterministic `de::Random rnd(1)` values to generate the `ivec4` constants tested in each comparison expression. |

## Support / Feature Requirements

[`CornerCase::createInstance()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L317-L322) requires buffer-device-address support through `context.isBufferDeviceAddressSupported()` and throws `NotSupportedError` when physical storage buffer pointers are unavailable.

## Verification Methods

The runtime path allocates a storage buffer for `ac_numIrrelevant`, creates and binds another storage buffer used with buffer-device-address, dispatches one compute workgroup, and submits the command buffer in [`SSBOCornerCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L168-L307). The explicit pass criterion is crash-oriented: after dispatch completion, the test returns pass with the message `Test did not cause a crash` in [`SSBOCornerCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L300-L307).

## Test Principles Observed

- This is a regression-style stress test rather than a data-comparison layout test: the source explicitly states that it passes if the generated shader dispatch does not cause a crash in [`SSBOCornerCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L306-L307).
- The generated shader intentionally keeps an auxiliary storage-buffer side effect so the comparison chain is not optimized away, as indicated by the `ac_numIrrelevant` comment and increment in [`useCornerCaseShader()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L73-L95).

## Notes / Uncertainties

- Mustpass inspection confirms `dEQP-VK.ssbo.corner_case.long_shader_bitwise_and` in [`vk-default/ssbo.txt`](../../../mustpass/main/vk-default/ssbo.txt#L1) and `dEQP-VKSC.ssbo.corner_case.long_shader_bitwise_and` in [`vksc-default/ssbo.txt`](../../../mustpass/main/vksc-default/ssbo.txt#L1).
- [`doc/testspecs/VK/apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc) was searched for `SSBO`, `Shader Storage`, `storage buffer`, and `Storage Buffer`; no category-specific SSBO test-plan section was found.
