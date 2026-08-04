# Understanding Brief: `pipeline.depth_range_unrestricted`

## One-Sentence Test Purpose

This test family checks whether `VK_EXT_depth_range_unrestricted` allows depth clear, viewport, and depth-bounds values outside the normal `[0, 1]` range, while preserving the expected depth-test result for each selected state combination.

## Background Knowledge

### Unrestricted depth range

`VK_EXT_depth_range_unrestricted` permits values outside `[0, 1]` where the extension applies to depth clear, viewport depth range, and depth bounds. The test selects negative and greater-than-one values, then checks the rendered result against a host-side reference.

Why it matters here:

- `clear_value` isolates out-of-range depth-buffer clear values.
- `viewport` and `depthbounds` apply symmetric negative and positive ranges through static or dynamic state.

### Depth clamping and depth comparison

Depth clamping controls whether primitives whose depth lies outside the normal clip range are clamped instead of clipped. Depth comparison and, when enabled, depth-bounds testing decide which points update the depth and color attachments. The `depthclampingdisabled` branch disables depth clamping to cover the clipping behavior separately.

## One Concrete Example

Consider a `viewport` case with `D32_SFLOAT`, `VK_COMPARE_OP_LESS_OR_EQUAL`, clear depth `-3.0`, and viewport depths `-2.0` to `2.0`.

The test renders its fixed point set with depth clamping enabled, reads back the color and depth images, and builds the same expected result on the host. A mismatch shows that the device did not apply the unrestricted viewport range or selected comparison state as the reference does. [`DepthRangeUnrestrictedTestInstance::verifyTestResult()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L850-L1025) performs that comparison.

## End-to-End Test Flow

```text
[host] select a test family, depth format, compare operation, clear value, and unrestricted range values
[host] check format support, selected pipeline construction, and required depthClamp or depthBounds features
[host] create color/depth attachments, pass-through shaders, pipeline state, and point vertices
[host] record a render pass, static or dynamic viewport/depth-bounds commands, and the draw
[device] apply clipping or clamping, depth comparison, optional depth-bounds testing, and attachment writes
[host] submit work, read back the color/depth images, build a reference image, and compare the results
```

## Generated Test Artifacts and Bound Resources

### Generated program artifacts

`DepthRangeUnrestrictedTest::initPrograms()` emits a vertex shader that forwards position and color, and a fragment shader that writes that color. The shaders supply point data only; fixed-function depth state is under test. [`DepthRangeUnrestrictedTest::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1326-L1347) defines both programs.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Depth attachment | Yes | Yes | Cleared, depth-tested, and written | Yes | Stores the unrestricted depth-range result. |
| Color attachment | Yes | Yes | Written when a point passes | Yes | Makes depth-test visibility observable. |
| Vertex buffer | Yes | Yes | Read by the vertex stage | No | Supplies the point positions and colors used by the reference path. |
| Reference image | Yes, host-side | No | No | Yes | Holds the expected color result for comparison. |

## What Is Checked

- Ordinary branches submit one draw and compare the readback color and depth results with the generated host reference. [`DepthRangeUnrestrictedTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L838-L848) and [`DepthRangeUnrestrictedTestInstance::verifyTestResult()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L850-L1025) implement this path.
- For non-floating depth formats, the reference clamps the clear value to `[0, 1]`, matching the stored-format behavior noted in the source. [`DepthRangeUnrestrictedTestInstance::verifyTestResult()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L860-L867) contains that handling.
- `depthbounds` renders the scene twice because the first draw changes depth-buffer contents used by the second depth-bounds evaluation; it verifies both results. [`DepthBoundsRangeUnrestrictedTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1094-L1110) starts the two-pass path.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `clear_value`, `viewport`, `depthbounds`, `depthclampingdisabled`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `clear_value` | An out-of-range depth clear value is stored, clamped, or compared incorrectly for the selected depth format. |
| `viewport` | Static or dynamic viewport minimum/maximum depth outside `[0, 1]` is handled incorrectly, or the selected depth comparison is wrong. |
| `depthbounds` | Unrestricted depth-bounds values, dynamic depth-bounds state, retained depth data between draws, or depth comparison is handled incorrectly. |
| `depthclampingdisabled` | Primitives outside the clip range are clipped or compared incorrectly when depth clamping is disabled. |

## Important Variations and Special Cases

- The registration loops use `VK_FORMAT_D32_SFLOAT`, `VK_FORMAT_D24_UNORM_S8_UINT`, and `VK_FORMAT_D16_UNORM`; support is checked per selected format.
- `clear_value` uses `2.0`, `-3.0`, `6.0`, and `-7.0` with `VK_COMPARE_OP_LESS_OR_EQUAL`.
- `viewport` uses symmetric ranges based on `2.0`, `6.0`, and `12.0`, and covers static plus dynamic viewport state.
- `depthbounds` combines those viewport ranges with symmetric depth bounds based on `2.0`, `4.0`, and `8.0`; it covers static state, dynamic depth bounds, and dynamic viewport plus depth bounds.
- `depthclampingdisabled` uses static viewport/depth-bounds state and varies the vertex `w` coordinate with `2.0`, `6.0`, and `12.0`.
- The source excludes Vulkan SC through `CTS_USES_VULKANSC` guards.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test parameters and test-name construction | [`DepthRangeUnrestrictedParam`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L70-L84) and [`generateTestName()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L97-L120) | Defines the state dimensions represented by each registered case. |
| Runtime resources and ordinary iteration | [`DepthRangeUnrestrictedTestInstance`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L413-L452) and [`iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L838-L848) | Shows the attachments, pipeline resources, command submission, and result path. |
| Reference comparison | [`verifyTestResult()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L850-L1025) | Builds the expected image and compares color/depth results. |
| Two-pass depth-bounds execution | [`DepthBoundsRangeUnrestrictedTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1094-L1110) | Explains why `depthbounds` checks two draw results. |
| Program generation and support gates | [`DepthRangeUnrestrictedTest`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1306-L1372) | Emits pass-through shaders and checks format, depth-clamp, depth-bounds, and construction support. |
| Family registration | [`createDepthRangeUnrestrictedTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1375-L1530) | Defines the four families and their parameter loops. |

## Questions / Risk Points for User Audit

- The behavior axis is the registered test family; each family changes where unrestricted depth values enter the pipeline or whether depth clamping is enabled.
- The shaders are supporting inputs rather than the behavior under test, so the final page should keep `## Shader Analysis` without a representative shader walkthrough or SPIR-V artifact.
- The visible registration tree uses `pipeline.monolithic.depth_range_unrestricted` as the representative root; the implementation receives a `PipelineConstructionType` when registering the group.

## Conversion Notes for Final Wiki Rewrite

- Use the test family as the final page's behavior parameter.
- Copy the four-row Failure Cause Mapping table into the final page.
- Keep unrestricted depth range and depth clamping as concise prerequisites.
- Put the parameter loops, two-pass depth-bounds behavior, and host reference comparison in their dedicated final-page sections.
