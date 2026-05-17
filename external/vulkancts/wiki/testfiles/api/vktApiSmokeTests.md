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

## Registration Hierarchy

```text
api.smoke
├── create_sampler
├── create_shader
├── triangle
├── asm_triangle
├── asm_triangle_no_opname
└── unused_resolve_attachment
```

Evidence:
- `smoke` group created at [`createSmokeTests()`](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L864)
- test cases added at [lines 868-874](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L868)

## Test Families

### create_sampler — Sampler creation and Move assignment

Registered at [line 868](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L868) via `addFunctionCase(smokeTests.get(), "create_sampler", createSamplerTest)`. Creates a `VkSampler` with NEAREST filtering and tests `Move<VkSampler>` assignment. Passes if `createSampler` succeeds and Move assignment works ([line 99](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L99)). No shader programs required.

### create_shader — Shader module creation from GLSL

Registered at [line 869](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L869) via `addFunctionCaseWithPrograms(smokeTests.get(), "create_shader", createShaderProgs, createShaderModuleTest)`. Creates a `VkShaderModule` from compiled GLSL. Passes if `createShaderModule` succeeds ([line 115](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L115)). Uses a GLSL vertex shader.

### triangle — Triangle rendering with GLSL shaders

Registered at [line 870](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L870) via `addFunctionCaseWithPrograms(smokeTests.get(), "triangle", createTriangleProgs, renderTriangleTest)`. Full rendering pipeline with image comparison using GLSL vertex and fragment shaders. Creates a 256x256 R8G8B8A8_UNORM image, vertex buffer, and readback buffer; records a render pass that clears to (0.125, 0.25, 0.75, 1.0) and draws a triangle; copies image to buffer and reads back pixels; renders a reference triangle using the rr software renderer ([lines 307-323](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L307)); compares using `intThresholdPositionDeviationCompare` with zero threshold and 1-pixel position deviation ([lines 563-566](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L563)).

### asm_triangle — Triangle rendering with SPIR-V assembly

Registered at [line 871](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L871) via `addFunctionCaseWithPrograms(smokeTests.get(), "asm_triangle", createTriangleAsmProgs, renderTriangleTest)`. Same rendering pipeline as `triangle` but uses SPIR-V assembly vertex and fragment shaders instead of GLSL. Uses the same `renderTriangleTest` function and the same verification method (`intThresholdPositionDeviationCompare` with zero color threshold and 1-pixel position deviation, comparing against a software-rendered reference at [lines 563-566](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L563)).

### asm_triangle_no_opname — SPIR-V assembly without OpName

Registered at [line 872](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L872) via `addFunctionCaseWithPrograms(smokeTests.get(), "asm_triangle_no_opname", createProgsNoOpName, renderTriangleTest)`. Tests SPIR-V without debug names. Uses the same `renderTriangleTest` function with SPIR-V assembly shaders that lack OpName instructions. Same verification method as `triangle` and `asm_triangle`.

### unused_resolve_attachment — Render pass with unused resolve attachment

Registered at [lines 873-874](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L873) via `addFunctionCaseWithPrograms(smokeTests.get(), "unused_resolve_attachment", createTriangleProgs, renderTriangleUnusedResolveAttachmentTest)`. Similar to the `triangle` test but creates a render pass with `VK_ATTACHMENT_UNUSED` in the resolve attachment reference ([line 670](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L670)). Uses GLSL vertex and fragment shaders. The test at [line 581](../../../modules/vulkan/api/vktApiSmokeTests.cpp#L581) does not use non-zero memory offsets unlike the main `triangle` test.

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
