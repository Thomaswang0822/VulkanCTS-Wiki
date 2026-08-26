## Overview

**Core question:** Does Vulkan apply the pipeline scissor rectangle to the samples produced by each tested primitive and viewport?

This page covers the implementation and registration rooted at `fragment_operations.scissor`:

- `points`, `lines`, and `triangles` draw geometry with one viewport and compare the result from a full scissor with the result from the case scissor.
- `multi_viewport` is registered here but implemented by the nested helper. Read [ScissorMultiViewport.md](ScissorMultiViewport.md) for its per-viewport tests.
- The direct cases use a 128x128 `VK_FORMAT_R8G8B8A8_UNORM` color target, generated GLSL 4.50 vertex and fragment shaders, and pipeline-defined scissor state.
- The host builds the expected direct image by applying the same rectangle to the full-scissor image, then compares images with a per-channel threshold of `0.02`.

## Background Knowledge

For the shared concept of viewport and scissor selection by `ViewportIndex`, see [Background Knowledge](../../categories/fragment_operations.md#background-knowledge) of the `fragment_operations` page.

- Scissor rectangles are graphics pipeline state in these cases. The test does not exercise clear operations, because scissor state affects drawing commands rather than independent color, depth, or stencil clears.

## Registration Hierarchy

```text
fragment_operations.scissor
├── points
├── lines
├── triangles
└── multi_viewport (registration only)
```

The root is created by [`createScissorTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L581-L584). The first three test families are built in [`createTestsInGroup()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L496-L571). The `multi_viewport` child is delegated through [`createScissorMultiViewportTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L573-L576) and is documented in [ScissorMultiViewport.md](ScissorMultiViewport.md).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `points`, `lines`, `triangles`, `multi_viewport` | Selects the primitive coverage path or the delegated multi-viewport path. | [`createTestsInGroup()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L496-L576) |
| Coverage relation | `inside`, `partially_inside`, `outside`, `crossing` | Chooses whether generated geometry lies inside, overlaps, avoids, or crosses the scissor rectangle. `crossing` is used by lines and triangles. | [`TestSpec` tables](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L512-L565) |
| Render/scissor area | `areaFull`, `areaCropped`, `areaCroppedMore`, `areaLeftHalf`, `areaRightHalf` | Defines the normalized render region and the pipeline `VkRect2D` after conversion to framebuffer pixels. | [`area*` definitions](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L506-L510), [`getAreaRect()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L262-L269) |
| Primitive generation | 50 points, 30 short lines, 20 small triangles, one big line, one big triangle | Changes the amount and shape of geometry reaching rasterization. | [`genVertices()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L183-L239) |
| Input topology | `VK_PRIMITIVE_TOPOLOGY_POINT_LIST`, `VK_PRIMITIVE_TOPOLOGY_LINE_LIST`, `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` | Matches each direct primitive kind to the Vulkan draw topology. | [`getTopology()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L241-L259) |
| Multi-viewport count | `scissor_1` through `scissor_16` | Selects the number of matching viewports and grid scissors in the delegated family. | [`createScissorMultiViewportTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L442-L448) |

## Behavior Parameters

The primary behavioral axis is the registered test family. Each family selects a different coverage workload, while the direct case leaves vary the relation between that workload and the scissor rectangle.

### `points`: point coverage

`inside` uses the full render and scissor areas. `partially_inside` generates 50 points across the full render area and clips them to `areaCropped`. `outside` generates points in the left half while the scissor rectangle selects the right half, so no point should contribute to the target.

### `lines`: line coverage

`inside`, `partially_inside`, and `outside` use 30 short lines. `crossing` uses one large line spanning the selected render area and a smaller scissor rectangle, so the test checks clipping on both sides of a line that crosses the rectangle.

### `triangles`: triangle coverage

`inside`, `partially_inside`, and `outside` use 20 small triangles. `crossing` uses one large triangle spanning the selected render area and clips it with `areaCroppedMore`.

### `multi_viewport`: delegated per-viewport scissor coverage

This test family is registered by this page's root but its implementation lives in [ScissorMultiViewport.md](ScissorMultiViewport.md). The helper creates one test for each count from 1 through 16. A geometry shader writes `gl_ViewportIndex` from `gl_PrimitiveIDIn`, so each emitted fullscreen quad uses the corresponding viewport and scissor rectangle.

## Shader Analysis

The shaders carry vertex colors into the fragment output. The direct vertex shader writes `gl_Position` and, for points, `gl_PointSize = 1.0`; the fragment shader writes the input color. The scissor behavior is fixed-function pipeline state, so the shader source does not decide which samples survive. The delegated family adds a geometry shader that selects a viewport with `gl_ViewportIndex`; its detailed walkthrough belongs in [ScissorMultiViewport.md](ScissorMultiViewport.md).

## Runtime Execution and Result Checking

- The direct renderer creates a 128x128 `VK_FORMAT_R8G8B8A8_UNORM` color image and view, a host-visible vertex buffer, shader modules, a render pass, a framebuffer, a pipeline layout, and a command buffer.
- It converts normalized area values `(origin-x, origin-y, width, height)` to integer framebuffer rectangles. The pipeline uses one viewport and one `VkRect2D` scissor. Because the scissor is not dynamic, the renderer creates a pipeline for each scissor used by a draw.
- For each direct test, the renderer draws the same generated vertices twice: once with the full rectangle `(0.0, 0.0, 1.0, 1.0)` and once with the case rectangle. Each draw clears the color target, binds the pipeline and vertex buffer, issues `vkCmdDraw`, copies the image to a host-visible buffer, and waits for completion.
- The host treats the full-scissor copy as the reference, changes pixels outside the case rectangle to the clear color `(0.5, 0.5, 1.0, 1.0)`, and compares it with the case-scissor copy. `tcu::floatThresholdCompare()` uses `Vec4(0.02f)` and returns failure as `Rendered image is not correct` when the images do not match.
- The delegated helper uses the same 128x128 color format. It arranges `numViewports` scissor rectangles in a grid, assigns each rectangle a distinct color, draws one vertex per viewport, and lets the geometry shader emit one fullscreen quad per input point. The host creates a gray-cleared reference image and fills the grid rectangles with their expected colors before comparing images.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `points` | Incorrect scissor coverage for point rasterization; direct image setup or comparison failure. |
| `lines` | Incorrect scissor coverage for line rasterization; direct image setup or comparison failure. |
| `triangles` | Incorrect scissor coverage for triangle rasterization; direct image setup or comparison failure. |
| `multi_viewport` | Incorrect association of `ViewportIndex`, viewport, and scissor rectangle; missing required multi-viewport support; delegated image setup or comparison failure. |

### Cause Analysis

#### Scissor coverage or direct image mismatch

**Possible failure symptoms:** The rendered direct image differs from the full-scissor reference after the host masks pixels outside the case rectangle. The test reports `Rendered image is not correct`.

**Possible implementation causes:** The implementation may assign coverage incorrectly at the scissor rectangle's half-open boundaries, use the wrong pipeline scissor state, or mishandle scissor clipping for the tested point, line, or triangle rasterization path. The comparison can also expose a mismatch in the draw, image-to-buffer copy, or host-side reference setup; the test does not identify which component caused the first difference.

#### Viewport-to-scissor selection mismatch

**Possible failure symptoms:** A `multi_viewport.scissor_N` image does not match the expected colored grid, so a rectangle is missing, misplaced, or has the wrong color.

**Possible implementation causes:** The geometry shader's `ViewportIndex` may not select the matching viewport and scissor state, or the implementation may mishandle the per-viewport scissor rectangles. The helper requires geometry shaders and `multiViewport`; unsupported implementations are rejected as not supported before execution. The test does not by itself distinguish a rasterization error from a setup or copyback error.

## Case Pruning

### Requirement-based pruning

- Direct cases use core graphics pipeline functionality and do not have a dedicated support gate in the inspected direct registration path.
- The delegated `multi_viewport` cases call `checkSupport()`. They require `DEVICE_CORE_FEATURE_GEOMETRY_SHADER`, `DEVICE_CORE_FEATURE_MULTI_VIEWPORT`, and `context.getDeviceProperties().limits.maxViewports >= 16`. Unsupported implementations receive `NotSupportedError` rather than a rendered result.

### Design-based pruning

- The direct family keeps one workload for each primitive class and uses a small set of area relationships instead of enumerating every possible rectangle.
- The direct `crossing` cases use a single full-span line or triangle; the other leaves use deterministic collections of smaller primitives.
- The multi-viewport helper fixes the count range at 1 through 16, matching the minimum limit it requires, and arranges rectangles as a grid.
- Clear-only color, depth, and stencil cases are absent because scissor state applies to drawing commands, not those independent clear operations.

## Key Takeaways

- The direct families test the same fixed-function rule across point, line, and triangle rasterization, including geometry that is fully inside, partly inside, outside, or crossing the scissor rectangle.
- The direct reference is produced from an unrestricted draw, then masked in host memory. That makes the expected effect of scissor state explicit.
- `multi_viewport` checks that a fragment's `ViewportIndex` selects the matching scissor rectangle. Its implementation and detailed cases are documented separately in [ScissorMultiViewport.md](ScissorMultiViewport.md).

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Root registration | [`createScissorTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L581-L584) | Creates `fragment_operations.scissor`. |
| Direct registration | [`createTestsInGroup()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L496-L576) | Creates `points`, `lines`, `triangles`, and delegates `multi_viewport`. |
| Direct primitive generation | [`genVertices()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L183-L239) | Generates the point, line, and triangle workloads. |
| Direct pipeline construction | [`makeGraphicsPipeline()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L114-L175) | Binds one viewport and one scissor rectangle to the graphics pipeline. |
| Direct result check | [`test()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L439-L491) | Performs both draws, applies the host reference mask, and compares images. |
| Multi-viewport helper | [`createScissorMultiViewportTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L431-L450) | Registers `scissor_1` through `scissor_16` and checks support. |
| Multi-viewport pipeline and shader behavior | [`makeGraphicsPipeline()` and `initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L94-L128) | Binds per-viewport scissors; the generated geometry shader selects `ViewportIndex`. |
| Multi-viewport result check | [`test()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L380-L428) | Builds the grid reference and checks the rendered image. |
| Header entry point | [`vktFragmentOperationsScissorTests.hpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.hpp#L30-L40) | Declares the root factory. |
| Mustpass coverage | [`fragment-operations.txt`](../../../mustpass/main/vk-default/fragment-operations.txt#L119-L145) | Lists all direct leaves and `multi_viewport.scissor_1` through `scissor_16`. |
| Vulkan scissor semantics | [Scissor Test](../../../../vulkan-docs/src/chapters/fragops.adoc#L426-L445) | Defines rectangle membership and coverage-zero behavior. |
| Vulkan multi-viewport feature | [`multiViewport`](../../../../vulkan-docs/src/chapters/features.adoc#L351-L359) | Defines the single-viewport restrictions when the feature is disabled. |
| Vulkan viewport limit | [`maxViewports`](../../../../vulkan-docs/src/chapters/limits.adoc#L568-L579) | Defines the maximum active viewport count used by the helper's support check. |
