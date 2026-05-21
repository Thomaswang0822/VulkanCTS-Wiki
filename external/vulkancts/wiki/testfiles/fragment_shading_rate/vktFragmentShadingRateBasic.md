# vktFragmentShadingRateBasic.cpp

This page documents the broad generated basic test families contributed by [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L1).

## Overview

The file registers many direct families into each applicable `fragment_shading_rate` pipeline permutation through [`createBasicTests()`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L3594-L4085). It covers baseline fragment shading rate behavior, sample masks, conservative rasterization, depth/stencil writes, layered rendering, multiview, interlock, sample locations, multipass, maintenance, sample-mask output, and selected miscellaneous cases.

## Role of File

- Implementation-heavy registered subgroup contributor.
- It does not create a wrapper group named after the source file; instead, it appends its generated group names directly to the parent group passed by [`vktFragmentShadingRateTests.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L534-L548).

## Registration Hierarchy

```text
fragment_shading_rate.renderpass2.monolithic.basic
├── dynamic
└── static
```

## Test Families

### dynamic — Dynamic fragment shading rate state

The `dynamic` child comes from `dynCases[]` with count `1` at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L3668-L3671). Under this child, the generator combines attachment usage, shader-rate output, combiner operations, extents, sample counts, and shader-stage paths for the `basic` family and for the other families listed in `groupCases[]` at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L3614-L3666).

### static — Static fragment shading rate state

The `static` child comes from `dynCases[]` with count `0` at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L3668-L3673). The same nested parameter tables are generated below this child when skip conditions allow the combination.

The same file also contributes sibling top-level families next to `basic` in each applicable parent permutation: `apisamplemask`, `samplemaskin`, `conservativeunder`, `conservativeover`, `fragdepth`, `fragstencil`, `multiviewport`, `colorlayered`, `srlayered`, `multiview`, `multiviewsrlayered`, `multiviewcorrelation`, `interlock`, `samplelocations`, `sampleshadingenable`, `sampleshadinginput`, non-Vulkan SC `fragdepth_early_late` and `fragstencil_early_late`, `fragdepth_clear`, `fragstencil_clear`, `fragdepth_baselevel`, `fragstencil_baselevel`, `multipass`, `multipass_fragdepth`, `multipass_fragstencil`, non-Vulkan SC `maintenance6`, `samplemaskout`, and `misc_tests`, as listed in `groupCases[]` and the later `misc_tests` block at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L3614-L3666) and [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L3944-L4085). These sibling family names are described in prose rather than included in this page's canonical tree because the parseable tree is rooted at the `basic` registered group.

Selected sibling family semantics visible in the verification code include:

- `samplemaskin` verifies sample-mask consistency in copied results at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L2850-L2879).
- `fragdepth` verifies depth writes against expected per-primitive depth values at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L2742-L2758).
- `fragstencil` verifies stencil values against primitive IDs at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L2761-L2777).
- `multiviewport`, `colorlayered`, and `multiview` verify viewport/scissor routing, output layer choice, and matching primitive IDs in paired layers at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L2779-L2831).
- `samplelocations` has coverage checks conditioned on fragment shading rate with custom sample locations at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L2881-L2896).

## Parameter Dimensions

The main matrix uses family names from `groupCases[]`, dynamic/static shading-rate state, four attachment-usage states, shader-rate enablement, two combiner operations, five framebuffer extents, five sample counts, and vertex/geometry/non-SC mesh shader paths at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L3614-L3719). Several skip conditions limit invalid combinations, including dynamic-rendering attachment-pointer variants, attachment-no-image-view variants, geometry shader static-state cases, layered shading-rate attachment cases without an attachment, and multipass/depth-clear restrictions at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L3743-L3878).

## Support / Feature Requirements

Support checks are per `FSRTestCase` in this file. The inspected registration and verification code show conditional dependencies on fragment shading rate features and optional interactions such as conservative rasterization, fragment shader interlock, sample locations, multiview, layered rendering, dynamic rendering, graphics pipeline library, and maintenance features; the page avoids treating those as unconditional for every family.

## Verification Methods

The verification scans copied color/depth/stencil results. It fails on nonzero shader error codes, checks the observed rate against the mask simulated from pipeline, primitive, and attachment rates, checks depth/stencil/multiview/layer expectations, and compares samples within the same fragment for matching rate and atomic value when the primitive matches at [`vktFragmentShadingRateBasic.cpp`](../../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L2641-L2920).

## Test Principles

The file stresses how pipeline, primitive, and attachment shading-rate inputs combine under different rendering paths and state choices, with explicit skip rules for combinations that the source marks invalid or unsupported.

## Notes / Uncertainties

The canonical hierarchy tree uses `fragment_shading_rate.renderpass2.monolithic` because this file contributes groups into multiple parent permutations rather than owning a single wrapper subgroup.
