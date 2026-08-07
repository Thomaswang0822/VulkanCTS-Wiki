## Understanding Brief

### Scope

`DepthClampTests` exercises depth clamping in the draw pipeline. The implementation is `vktDrawDepthClampTests.cpp`; the obsolete page is retained as a historical navigation aid, but the source and registration code are authoritative.

### Registration and expansion

The test factory creates `depth_clamp` below the render-pass draw group and, in non-Vulkan SC builds, below dynamic-rendering command-buffer modes. The same case factory is reused with `SharedGroupParams`; dynamic rendering changes the render target command path, not the depth-clamp parameters. The checked-in mustpass evidence covers render-pass, primary dynamic-rendering, partial-secondary, and complete-secondary roots; nested secondary modes are source-dispatched variants but are not listed in the inspected mustpass file.

The source expands a format name with each enabled parameter suffix. A parameter set with user-defined clamp control also creates a second leaf with `_dynamic`, because the dynamic variant calls `vkCmdSetDepthClampRangeEXT`. Cases requiring `VK_EXT_depth_range_unrestricted` or `VK_EXT_depth_clamp_control` are compiled out for Vulkan SC by `#ifndef CTS_USES_VULKANSC`. UNORM and SNORM formats are skipped for out-of-[0,1] viewport/clamp cases.

### Parameter matrix

| Axis | Source-backed values and effect |
|---|---|
| Depth/stencil format | `D16_UNORM`, `X8_D24_UNORM_PACK32`, `D32_SFLOAT`, `D16_UNORM_S8_UINT`, `D24_UNORM_S8_UINT`, `D32_SFLOAT_S8_UINT`; each format has its own comparison epsilon. |
| Input depth | `0.3` baseline; `-1e6` negative excursion; `1e6` positive excursion. |
| Viewport range | `[0,1]` baseline; `[-1.5,1]` and `[0,1.5]` for `VK_EXT_depth_range_unrestricted`; four independent ranges for `clamp_four_viewports`. |
| Clamp-control mode | Viewport-range mode, or user-defined range `[0.1,0.9]`, `[-1.4,0.9]`, or `[0.1,1.4]`. |
| Depth bias | Disabled, or enabled with constant factor `-2e11` or `2e11`. |
| State-setting path | Static pipeline state; for user-defined clamp control, an additional `_dynamic` case sets `VK_EXT_depth_clamp_control` state with `vkCmdSetDepthClampRangeEXT`. |
| Rendering path | Render pass, or non-Vulkan-SC dynamic rendering in primary and secondary-command-buffer modes. Secondary modes reduce the matrix to `D16_UNORM`. |

### Expected-value rules

The source supplies expected values explicitly. Normal clamping maps large negative and positive inputs to the viewport endpoints `0.0` and `1.0`. User-defined control maps them to its configured clamp endpoints. Unrestricted cases preserve values outside `[0,1]`, while unrestricted user-defined cases clamp to the configured endpoint. The four-viewport case checks `0.35`, `1.0`, `0.95`, and `0.66` in four viewports.

### Runtime and result check

Each instance creates a 256x256 depth image, clears it to `0.5`, builds a graphics pipeline with `depthClampEnable = VK_TRUE`, and draws a full-screen triangle strip. The vertex shader passes positions through. A geometry shader is generated only for the four-viewport case; it broadcasts the primitive and supplies each viewport's fixed depth value. The fragment shader is empty, so the depth attachment is the observable output.

The command path transitions and clears the depth image, renders, transitions it to transfer-source layout, reads the depth aspect back, and checks every pixel in each viewport rectangle. A failure reports the expected and observed depth and pixel coordinates and logs the result image. Comparison uses the format-specific epsilon, so a rendered image mismatch can arise from state setup, command recording, vertex/geometry processing, viewport selection or transformation, depth attachment operations, readback, or comparison—not from shader execution alone.

### Support and skip behavior

Every case requires the core depth-clamp feature. Extension cases require the exact extension names stored in `requiredExtensions`. Multi-viewport cases require the core multi-viewport feature and geometry-shader support. Unsupported depth-image usage/format combinations and missing dynamic-rendering functionality are reported as not supported. Format filtering is performed before registration, so skipped format combinations do not become executable leaves.

### Evidence limits

The checked-in source and dispatcher establish the registration and behavior described here. Mustpass files in this checkout do not contain a `depth_clamp` entry in the inspected `draw.txt` files, so this brief does not claim a current mustpass inclusion path. No shader analyzer or SPIR-V disassembly was run; shader discussion is limited to the GLSL source generated in the C++ implementation.

### References

- [Depth clamp implementation](../../../modules/vulkan/draw/vktDrawDepthClampTests.cpp)
- [Depth clamp declaration](../../../modules/vulkan/draw/vktDrawDepthClampTests.hpp)
- [Draw dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp)
- [Mustpass draw lists](../../../mustpass/main/vk-default/draw.txt)
- [Vulkan depth range unrestricted extension](https://registry.khronos.org/vulkan/specs/latest/html/chapters/viewport.html)
- [Vulkan depth clamp control extension](https://registry.khronos.org/vulkan/specs/latest/html/chapters/viewport.html)
