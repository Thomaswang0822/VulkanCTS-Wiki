# [vktApiSmokeTests.cpp](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L1)

## Overview

Simple smoke tests that verify basic Vulkan object creation and rendering operations. Tests include creating a sampler, creating a shader module, rendering a triangle with GLSL, rendering a triangle with SPIR-V assembly, rendering without OpName, and rendering with an unused resolve attachment.

## Role of File

Implementation-heavy. Contains multiple independent test functions, reference rendering, and registration logic.

## Source Code

| File | Description |
|------|-------------|
| [vktApiSmokeTests.cpp](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L1) | Test implementation and registration |
| [vktApiSmokeTests.hpp](../../../modules/vulkan/api/vktApiSmokeTests.hpp#L1) | Declares `createSmokeTests` |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L94) | Parent registration: `apiTests->addChild(createSmokeTests(testCtx))` |

## Registration Path

```
api
  +-- smoke
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
  |    Creates a VkSampler and tests Move assignment
  +-- create_shader
  |    Creates a VkShaderModule from GLSL
  +-- triangle
  |    Renders a triangle with GLSL shaders, compares against reference
  +-- asm_triangle
  |    Renders a triangle with SPIR-V assembly shaders
  +-- asm_triangle_no_opname
  |    Renders a triangle with SPIR-V assembly lacking OpName
  +-- unused_resolve_attachment
       Renders with VK_ATTACHMENT_UNUSED resolve attachment
```

## Test Families

### smoke

Group name verified at [vktApiSmokeTests.cpp:866](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L866): `new tcu::TestCaseGroup(testCtx, "smoke")`.

Six test cases added at [lines 868-874](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L868):

| Test Name | Function | Programs | Description |
|-----------|----------|----------|-------------|
| `create_sampler` | createSamplerTest | None | Creates a VkSampler with NEAREST filtering, tests Move assignment |
| `create_shader` | createShaderModuleTest | GLSL vertex | Creates a VkShaderModule from compiled GLSL |
| `triangle` | renderTriangleTest | GLSL vert+frag | Full rendering pipeline with image comparison |
| `asm_triangle` | renderTriangleTest | SPIR-V asm vert+frag | Same rendering using SPIR-V assembly |
| `asm_triangle_no_opname` | renderTriangleTest | SPIR-V asm without OpName | Tests SPIR-V without debug names |
| `unused_resolve_attachment` | renderTriangleUnusedResolveAttachmentTest | GLSL vert+frag | Render pass with VK_ATTACHMENT_UNUSED resolve |

The rendering tests (`triangle`, `asm_triangle`, `asm_triangle_no_opname`) at [line 325](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L325):
1. Create a 256x256 R8G8B8A8_UNORM image, vertex buffer, and readback buffer
2. Record a render pass that clears to (0.125, 0.25, 0.75, 1.0) and draws a triangle
3. Copy image to buffer and read back pixels
4. Render a reference triangle using the rr software renderer ([lines 307-323](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L307))
5. Compare using `intThresholdPositionDeviationCompare` with zero threshold and 1-pixel position deviation ([lines 563-566](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L563))

The `unused_resolve_attachment` test at [line 581](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L581) is similar but creates a render pass with `VK_ATTACHMENT_UNUSED` in the resolve attachment reference ([line 670](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L670)).

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Render size | 256x256 | Hard-coded at [line 333](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L333) |
| Color format | VK_FORMAT_R8G8B8A8_UNORM | Hard-coded |
| Clear color | (0.125, 0.25, 0.75, 1.0) | Hard-coded at [line 335](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L335) |
| Shader source | GLSL, SPIR-V asm | Varies by test |
| Memory offset | Non-zero alignment offsets | Exercises non-zero offsets in buffer/image binding |

## Support / Feature Requirements

No explicit extension requirements. These are basic smoke tests that should work on any Vulkan 1.0 implementation.

## Verification Methods

- **create_sampler**: Passes if `createSampler` succeeds and Move assignment works ([line 99](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L99))
- **create_shader**: Passes if `createShaderModule` succeeds ([line 115](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L115))
- **Rendering tests**: Uses `tcu::intThresholdPositionDeviationCompare` with zero color threshold and 1-pixel position deviation, comparing against a software-rendered reference ([lines 563-566](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L563))

## Test Principles Observed

- Smoke testing: validates that basic Vulkan operations work end-to-end
- Reference comparison: rendering tests compare against a software reference renderer
- Non-zero offset coverage: buffer and image memory bindings use non-zero offsets to exercise alignment

## Notes / Uncertainties

- The `create_sampler` test exercises Move<VkSampler> assignment which tests the CTS framework's move semantics, not a Vulkan feature
- The rendering tests use `SimpleAllocator` directly rather than the context's default allocator
- The `unused_resolve_attachment` test does not use non-zero memory offsets unlike the main `triangle` test
