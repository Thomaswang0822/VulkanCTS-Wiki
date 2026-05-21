# vktFragmentShadingRateMiscTests.cpp

This page documents the additional miscellaneous fragment shading rate cases contributed by [`vktFragmentShadingRateMiscTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L1).

## Overview

The file contributes function-style tests into the existing `misc` group through [`createFragmentShadingRateMiscTests()`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L1497-L1530). Renderpass-style permutations receive attachment enable/disable, no-fragment-shader, and out-of-bounds attachment tests; dynamic-rendering permutations receive an explicit/implicit enable test outside Vulkan SC.

## Role of File

- Registered implementation contributor under an existing `misc` group.
- It does not create the `misc` wrapper; the wrapper is created by [`createMiscTests()`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L514-L531).

## Registration Hierarchy

```text
fragment_shading_rate.renderpass2.monolithic.misc
├── limits
├── shading_rates
├── enable_disable_attachment
├── no_frag_shader
├── test_oob_attachment
└── test_oob_attachment_robustness2
```

## Test Families

### limits — Fragment shading rate property limits

This child is registered by the parent file before the misc-extension helper is called at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L518-L523).

### shading_rates — Reported shading-rate list validation

This child is registered by the parent file at [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L521-L522).

### enable_disable_attachment — Attachment enable/disable transition

This renderpass-style case tests drawing with variable rate shading enabled by an attachment and then disabled, as indicated by the registration comment and function-case call at [`vktFragmentShadingRateMiscTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L1499-L1506).

### no_frag_shader — VRS without a fragment shader

This renderpass-style case is registered at [`vktFragmentShadingRateMiscTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L1507-L1511).

### test_oob_attachment — Out-of-bounds shading-rate attachment behavior

This case is registered with `useRobustness2 = false` at [`vktFragmentShadingRateMiscTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L1512-L1515).

### test_oob_attachment_robustness2 — Out-of-bounds attachment behavior with robustness2

This case toggles `useRobustness2 = true` before registration at [`vktFragmentShadingRateMiscTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L1516-L1518).

## Parameter Dimensions

The helper branches on `groupParams->useDynamicRendering`: renderpass-style paths register four tests, while the dynamic-rendering path registers `explicit_and_implicit_enable` outside Vulkan SC at [`vktFragmentShadingRateMiscTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L1499-L1528). The canonical tree above documents the renderpass2 monolithic root; the dynamic-rendering-only child is described but not included in that one canonical tree.

## Support / Feature Requirements

`checkShadingRateSupport()` requires `VK_KHR_fragment_shading_rate` and selected feature bits according to the caller's booleans at [`vktFragmentShadingRateMiscTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L83-L96). The enable/disable and explicit/implicit-enable checks require pipeline and attachment fragment shading rate support, and the dynamic-rendering explicit/implicit test also requires `VK_KHR_dynamic_rendering` at [`vktFragmentShadingRateMiscTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L98-L108). Out-of-bounds cases require physical-device-properties2, pipeline and attachment fragment shading rate support, robust fragment shading rate attachment access, and either robustness2 features or `VK_EXT_image_robustness` depending on the parameter at [`vktFragmentShadingRateMiscTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L739-L775).

## Verification Methods

One visible verification path constructs expected depth values and uses `tcu::dsThresholdCompare`, failing on unexpected depth contents at [`vktFragmentShadingRateMiscTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L719-L736). The out-of-bounds tests and enable/disable tests perform branch-specific rendering and validation in their function bodies; this page only claims the comparison method where inspected lines show it directly.

## Test Principles

The file isolates edge cases around enabling/disabling attachment-driven VRS, absent fragment shaders, dynamic-rendering enablement semantics, and out-of-bounds shading-rate attachment access.

## Notes / Uncertainties

The canonical hierarchy tree includes `limits` and `shading_rates` because they are direct children of the same documented `misc` root, but their implementations live in [`vktFragmentShadingRateTests.cpp`](vktFragmentShadingRateTests.md).
