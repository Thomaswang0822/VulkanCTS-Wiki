# vktRasterizationFragShaderSideEffectsTests.cpp

## Overview

[`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L1) implements the `frag_side_effects` subgroup, registered by [`createFragSideEffectsTests()`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L684). The file tests whether storage-buffer side effects from fragment shaders remain observable when the fragment color output is killed, demoted, terminated, masked, rejected by tests, or subject to alpha/depth-bounds conditions.

## Role

Implementation file.

## Source Code

- Primary source: [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L1)
- Header: [`vktRasterizationFragShaderSideEffectsTests.hpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.hpp#L35)

## Registration Hierarchy

```text
rasterization.frag_side_effects
├── color_at_beginning
└── color_at_end
```

## Test Families

### color_at_beginning — Color output before side-effect path

The `color_at_beginning` child is one of the two `kColorOrders[]` registrations at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L692-L705). Under it, the file registers `kill`, `demote`, `terminate_invocation`, `sample_mask_before`, `sample_mask_after`, `stencil_never`, `depth_never`, `alpha_coverage_before`, `alpha_coverage_after`, and `depth_bounds` at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L708-L770).

### color_at_end — Color output after side-effect path

The `color_at_end` child uses the same case set as `color_at_beginning`, but with `colorAtEnd` set from `kColorOrders[]` at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L696-L706). This explicitly varies whether the fragment output assignment is placed at the start or end of the shader.

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Color-output placement | `color_at_beginning` and `color_at_end` from [`kColorOrders[]`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L692-L701) |
| Case type | Kill, demote, terminate invocation, sample-mask before/after, stencil never, depth never, alpha-coverage before/after, and depth-bounds cases registered at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L708-L770) |
| Clear / draw colors | Default clear color `(0,0,0,1)` and draw color `(0,0,1,1)` from [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L688-L689), with alpha-coverage using alpha zero at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L751-L762) |
| Depth-bounds values | min `0.25`, max `0.5`, draw depth `0.75` at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L765-L768) |

## Support / Feature Requirements

The support check requires `fragmentStoresAndAtomics` for all cases at [`FragSideEffectsTestCase::checkSupport()`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L162-L168). Depth-bounds cases require `depthBounds` at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L169-L173), demote cases require `VK_EXT_shader_demote_to_helper_invocation` at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L174-L177), and terminate-invocation cases require `VK_KHR_shader_terminate_invocation` at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L178-L181).

## Verification Methods

The test invalidates and checks every SSBO element, requiring value `1` for each framebuffer pixel at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L622-L636). It then checks the color attachment against one or two expected colors and logs an error mask if any pixel is unexpected at [`vktRasterizationFragShaderSideEffectsTests.cpp`](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L639-L676).

## Test Principles Observed

- **Side effects independent of visibility**: the SSBO check verifies shader side effects even when color output may remain clear due to kill, masks, or failed tests.
- **Shader-order variation**: the two direct children vary whether the color assignment appears before or after the side-effect path.
- **Feature-specific gates**: only cases requiring depth bounds, demotion, or termination request the corresponding feature or extension.

## Notes / Uncertainties

- The page describes registered groups and observed checks in this source file only; it does not infer compiler optimization behavior beyond the file's SSBO and color-buffer verification.
