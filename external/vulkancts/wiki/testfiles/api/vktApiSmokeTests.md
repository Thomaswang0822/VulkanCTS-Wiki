# [vktApiSmokeTests.cpp](../../modules/vulkan/api/vktApiSmokeTests.cpp#L1)

## Overview

Basic smoke tests that verify fundamental Vulkan operations work correctly: sampler creation, shader module creation, and triangle rendering via both GLSL and SPIR-V assembly shaders. Also tests rendering with an unused resolve attachment. These tests serve as minimal end-to-end validation of the graphics pipeline.

## Role of File

Implementation-heavy. Contains multiple standalone test functions with full Vulkan pipeline setup, command buffer recording, rendering, and image comparison against reference images rendered with the rr (reference renderer) library.

## Source Code

- Implementation: [vktApiSmokeTests.cpp](../../modules/vulkan/api/vktApiSmokeTests.cpp#L1)
- Header: [vktApiSmokeTests.hpp](../../modules/vulkan/api/vktApiSmokeTests.hpp#L1)
- Parent registration: `createSmokeTests()` declared at [L34](../../modules/vulkan/api/vktApiSmokeTests.hpp#L34)

## Registration Path

```
api
  +-- smoke   (non-VKSC only)
        +-- create_sampler
        +-- create_shader
        +-- triangle
        +-- asm_triangle
        +-- asm_triangle_no_opname
        +-- unused_resolve_attachment
```

## Test Hierarchy

```
smoke
  +-- create_sampler
  +-- create_shader
  +-- triangle
  +-- asm_triangle
  +-- asm_triangle_no_opname
  +-- unused_resolve_attachment
```

## Test Families

### create_sampler

Creates a `VkSampler` with basic nearest-filtering and clamp-to-edge addressing, then tests Move assignment semantics by moving the handle into a Unique wrapper. Verifies that sampler creation succeeds without errors.

- Function: `createSamplerTest()` at [L64](../../modules/vulkan/api/vktApiSmokeTests.cpp#L64)

### create_shader

Compiles a minimal GLSL vertex shader from source, creates a `VkShaderModule` from the compiled SPIR-V, and verifies creation succeeds.

- Function: `createShaderModuleTest()` at [L109](../../modules/vulkan/api/vktApiSmokeTests.cpp#L109)
- Shader programs: `createShaderProgs()` at [L102](../../modules/vulkan/api/vktApiSmokeTests.cpp#L102)

### triangle

Renders a triangle using GLSL vertex and fragment shaders. Creates a full graphics pipeline with vertex buffer, render pass, framebuffer, and command buffer. Reads back the rendered image and compares it against a reference image rendered with the rr library using `tcu::intThresholdPositionDeviationCompare` with zero threshold and 1-pixel position deviation tolerance.

- Function: `renderTriangleTest()` at [L325](../../modules/vulkan/api/vktApiSmokeTests.cpp#L325)
- Shader programs: `createTriangleProgs()` at [L182](../../modules/vulkan/api/vktApiSmokeTests.cpp#L182)
- Reference renderer: `renderReferenceTriangle()` at [L307](../../modules/vulkan/api/vktApiSmokeTests.cpp#L307)

### asm_triangle

Same as `triangle` but uses hand-written SPIR-V assembly shaders instead of GLSL. Uses the same `renderTriangleTest()` function.

- Shader programs: `createTriangleAsmProgs()` at [L118](../../modules/vulkan/api/vktApiSmokeTests.cpp#L118)

### asm_triangle_no_opname

Same as `asm_triangle` but the SPIR-V assembly shaders omit `OpName` instructions. Tests that the implementation handles shaders without debug names correctly.

- Shader programs: `createProgsNoOpName()` at [L192](../../modules/vulkan/api/vktApiSmokeTests.cpp#L192)

### unused_resolve_attachment

Renders a triangle with a render pass that specifies a resolve attachment set to `VK_ATTACHMENT_UNUSED`. Verifies that the unused resolve attachment does not affect rendering correctness. Compares output against a reference image.

- Function: `renderTriangleUnusedResolveAttachmentTest()` at [L581](../../modules/vulkan/api/vktApiSmokeTests.cpp#L581)
- Resolve attachment: `VK_ATTACHMENT_UNUSED` at [L670](../../modules/vulkan/api/vktApiSmokeTests.cpp#L670)

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Render size | 256x256 | [L333](../../modules/vulkan/api/vktApiSmokeTests.cpp#L333) |
| Color format | VK_FORMAT_R8G8B8A8_UNORM | [L334](../../modules/vulkan/api/vktApiSmokeTests.cpp#L334) |
| Clear color | (0.125, 0.25, 0.75, 1.0) | [L335](../../modules/vulkan/api/vktApiSmokeTests.cpp#L335) |
| Triangle color | (1.0, 0.0, 1.0, 1.0) | Fragment shader at [L188](../../modules/vulkan/api/vktApiSmokeTests.cpp#L188) |
| Comparison threshold | 0 (exact) | [L557](../../modules/vulkan/api/vktApiSmokeTests.cpp#L557) |
| Position deviation | (1, 1, 0) | [L558](../../modules/vulkan/api/vktApiSmokeTests.cpp#L558) |
| Non-zero memory offsets | Yes (alignment-based) | [L352](../../modules/vulkan/api/vktApiSmokeTests.cpp#L352) |

## Support / Feature Requirements

| Requirement | Gate | Notes |
|-------------|------|-------|
| None explicit | No `checkSupport` callbacks | Tests rely on core Vulkan 1.0 functionality |

## Verification Methods

- **Sampler creation**: `createSampler()` returns without error at [L91](../../modules/vulkan/api/vktApiSmokeTests.cpp#L91)
- **Shader module creation**: `createShaderModule()` returns without error at [L113](../../modules/vulkan/api/vktApiSmokeTests.cpp#L113)
- **Image comparison**: `tcu::intThresholdPositionDeviationCompare()` with zero threshold and 1-pixel deviation at [L563](../../modules/vulkan/api/vktApiSmokeTests.cpp#L563)
- **VK_CHECK macros**: All Vulkan API calls wrapped in `VK_CHECK` throughout

## Test Principles Observed

- **End-to-end validation**: Full pipeline from shader compilation through rendering to pixel comparison
- **Reference comparison**: Uses the rr reference renderer for ground-truth image generation
- **Non-zero offsets**: Deliberately uses non-zero memory offsets to exercise alignment handling at [L352](../../modules/vulkan/api/vktApiSmokeTests.cpp#L352)
- **SPIR-V assembly coverage**: Tests both GLSL-compiled and hand-written SPIR-V assembly shaders

## Notes / Uncertainties

- The `create_sampler` test exercises Move semantics on `Move<VkSampler>` at [L94](../../modules/vulkan/api/vktApiSmokeTests.cpp#L94), which is testing the C++ wrapper rather than Vulkan behavior per se.
- The `triangle` and `unused_resolve_attachment` tests use `SimpleAllocator` directly rather than `context.getDefaultAllocator()`, which is a different pattern from most other tests.
- The `unused_resolve_attachment` test does not use non-zero memory offsets (unlike the `triangle` test), binding at offset 0 at [L611](../../modules/vulkan/api/vktApiSmokeTests.cpp#L611).
- The `asm_triangle_no_opname` test uses SPIR-V that writes to two output locations (location 0 and location 2) and reads from location 2 in the fragment shader, which is an unusual pattern for a simple triangle test.
