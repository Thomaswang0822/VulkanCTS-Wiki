## Overview

**Core question:** Does a basic non-indexed graphics draw produce the expected rectangle for both triangle topologies, including a non-zero `firstInstance` in instanced draws?

- This page covers the four direct test case leaves registered by `SimpleDrawTests` in `vktDrawSimpleTest.cpp`.
- The cases bind a vertex buffer, render into a 256×256 `VK_FORMAT_R8G8B8A8_UNORM` color target, and compare the result with a host-built blue-on-black reference image.
- The same leaves are registered under the render-pass path and the three non-nested dynamic-rendering command-buffer modes. VulkanSC contains only the render-pass path in the mustpass inventory.
- The implementation uses `VertexFetch.vert`/`VertexFetch.frag` for non-instanced cases and `VertexFetchInstancedFirstInstance.vert` with the same fragment shader for instanced cases ([case registration](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L412-L444)).

## Background Knowledge

- Vulkan primitive topology determines how fetched vertices are assembled into primitives. A triangle list consumes groups of three vertices; a triangle strip reuses adjacent vertices to form subsequent triangles.
- `firstVertex` and `firstInstance` are draw parameters visible to the vertex-processing stage. These tests deliberately use non-zero offsets so that fetching and instance-ID handling are exercised rather than only the default-zero path.
- A render pass instance may be recorded with a traditional `VkRenderPass`, or with dynamic rendering when the required feature is enabled. In both forms, draw commands are recorded inside the active render pass instance ([render-pass specification](../../../../vulkan-docs/src/chapters/renderpass.adoc#L7-L10)).

## Registration Hierarchy

The category dispatcher creates `simple_draw` under `draw.renderpass` and, when VulkanSC is not being built, under the three non-nested dynamic-rendering modes. `createChildren` does not add it to either nested-secondary mode because those modes set `nestedSecondaryCmdBuffer` and skip the simple-draw registration ([dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L100), [dynamic-rendering groups](../../../modules/vulkan/draw/vktDrawTests.cpp#L144-L198)). Each `simple_draw` family has the same four direct leaves:

```text
draw.renderpass.simple_draw
├── simple_draw_triangle_list
├── simple_draw_triangle_strip
├── simple_draw_instanced_triangle_list
└── simple_draw_instanced_triangle_strip

draw.dynamic_rendering.primary_cmd_buff.simple_draw
├── simple_draw_triangle_list
├── simple_draw_triangle_strip
├── simple_draw_instanced_triangle_list
└── simple_draw_instanced_triangle_strip

draw.dynamic_rendering.partial_secondary_cmd_buff.simple_draw
├── simple_draw_triangle_list
├── simple_draw_triangle_strip
├── simple_draw_instanced_triangle_list
└── simple_draw_instanced_triangle_strip

draw.dynamic_rendering.complete_secondary_cmd_buff.simple_draw
├── simple_draw_triangle_list
├── simple_draw_triangle_strip
├── simple_draw_instanced_triangle_list
└── simple_draw_instanced_triangle_strip
```

The nested dynamic-rendering roots are intentionally absent from this tree: their `nestedSecondaryCmdBuffer` setting prevents `createChildren` from adding `SimpleDrawTests`. The four leaves are created directly by `SimpleDrawTests::init` ([group construction](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L401-L445)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Primitive topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`, `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` | Selects the primitive assembly path and vertex count | [`SimpleDraw::draw`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L241-L249) |
| Draw mode | non-instanced, instanced | Selects the ordinary or `firstInstance`-sensitive execution path | [`SimpleDrawInstanced::iterate`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L273-L345) |
| Vertex range | `vertexCount=6` (list), `vertexCount=4` (strip); `firstVertex=2` | Skips two leading degenerate entries and exercises non-zero vertex offset | [`SimpleDraw::draw`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L241-L249) |
| Instance range | `instanceCount=1`, `firstInstance=0`; or `instanceCount=4`, `firstInstance=2` | Adds four instances and a non-zero first-instance offset in the instanced leaves | [`SimpleDrawInstanced::iterate`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L293-L325) |
| Rendering command path | render pass; dynamic rendering with primary, partial secondary, or complete secondary command buffers | Reuses the draw behavior across supported recording arrangements | [`SimpleDraw::iterate`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L131-L193), [dispatcher parameters](../../../modules/vulkan/draw/vktDrawTests.cpp#L157-L191) |

The source creates four leaves, and the mustpass inventory expands them to 4 render-pass leaves plus 12 dynamic-rendering leaves in `vk-default` (16 total). `vksc-default` contains the 4 render-pass leaves only. The dynamic-rendering branches are compiled out for VulkanSC ([conditional registration](../../../modules/vulkan/draw/vktDrawTests.cpp#L144-L199)).

## Behavior Parameters

The primary behavioral axis is the test case leaf: topology and instancing jointly determine the draw command and expected rectangle.

### `simple_draw_triangle_list` : Six-vertex list draw

The case uses six vertices starting at `firstVertex=2`, forming two triangles that cover the square from −0.3 to 0.3 in both axes ([vertex data](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L71-L88)).

### `simple_draw_triangle_strip` : Four-vertex strip draw

The case uses four vertices starting at `firstVertex=2`; the strip assembles the same rectangular coverage with fewer submitted vertices ([vertex data](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L89-L100)).

### `simple_draw_instanced_triangle_list` : Four-instance list draw

This uses the list topology with `vkCmdDraw(..., 6, 4, 2, 2)`. The non-zero `firstInstance=2` is part of the behavior under test ([draw command](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L241-L249), [instanced call](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L293-L295)).

### `simple_draw_instanced_triangle_strip` : Four-instance strip draw

This uses the strip topology with `vkCmdDraw(..., 4, 4, 2, 2)`, combining strip assembly with four instances and `firstInstance=2` ([draw command](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L241-L249), [instanced call](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L321-L325)).

## Shader Analysis

The shaders are selected by name during test registration and compiled through the shared draw base class. This page does not reconstruct or disassemble shader source: the tested distinction is the host draw topology/instance parameters, while the shader choice is the vertex-fetch variant recorded in the test specification ([pipeline shader loading](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L155-L172), [shader selections](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L414-L419)).

## Runtime Execution and Result Checking

- `DrawTestsBaseClass::initialize` creates the color target and view, a host-visible vertex buffer, the vertex-input descriptions, command buffers, and graphics pipeline. The target is 256×256, single-sampled, and uses `VK_FORMAT_R8G8B8A8_UNORM` ([base initialization](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L35-L50), [resources](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L51-L152)).
- Before drawing, the color image is transitioned and cleared to opaque black, followed by a transfer-to-color-attachment pipeline barrier ([pre-render barriers](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L198-L215)).
- The command buffer path is selected from `SharedGroupParams`: legacy render pass, primary dynamic rendering, or secondary command-buffer recording with the render pass either outside or completely inside the secondary buffer ([non-instanced recording](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L131-L195)).
- The submitted command buffer is waited on. The rendered color image is read back in `VK_IMAGE_LAYOUT_GENERAL`, and the host compares it against the generated reference with `tcu::fuzzyCompare` and threshold `0.05` ([comparison](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L225-L238)).
- The instanced path follows the same flow, using the instanced reference bounds and an explicit queue-idle check before constructing the reference ([instanced validation](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L345-L390)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `simple_draw_triangle_list` | Incorrect non-indexed vertex fetch, triangle-list assembly, rasterization, render-target setup, synchronization, or image comparison behavior. |
| `simple_draw_triangle_strip` | Incorrect non-indexed vertex fetch, triangle-strip assembly, rasterization, render-target setup, synchronization, or image comparison behavior. |
| `simple_draw_instanced_triangle_list` | Incorrect instance iteration or `firstInstance` handling in addition to the list-draw causes. |
| `simple_draw_instanced_triangle_strip` | Incorrect instance iteration or `firstInstance` handling in addition to the strip-draw causes. |

### Cause Analysis

#### Generated vertex data and vertex fetch

**Possible failure symptoms:** Pixels outside the expected blue rectangle differ, or the rectangle is displaced or missing in all variants.

**Possible implementation causes:** The vertex-input binding, attribute formats, shader module, or vertex-fetch behavior may not deliver the positions and colors described by the test's `VertexElementData`. The source creates two leading entries with `refVertexIndex=-1`, visible entries beginning at index 2, and a trailing degenerate entry ([vertex buffer setup](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L64-L120)).

#### Primitive assembly and draw parameters

**Possible failure symptoms:** Only list or strip cases fail, or one topology produces a shape different from the expected rectangle.

**Possible implementation causes:** The topology state, vertex count, or `firstVertex` argument may be mishandled. Instanced failures may additionally indicate incorrect `instanceCount` or `firstInstance` processing. The test does not isolate a single layer: a mismatch can involve pipeline state, generated shader behavior, resources, or host validation.

#### Render-pass and command-buffer execution

**Possible failure symptoms:** Failures correlate with legacy render-pass, primary dynamic-rendering, or secondary-command-buffer leaves while the other recording modes pass.

**Possible implementation causes:** The implementation may mishandle render-pass attachment state, dynamic-rendering setup, secondary command-buffer inheritance, command execution, or the required synchronization. Dynamic-rendering cases require `VK_KHR_dynamic_rendering` ([support check](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L393-L397)).

#### Image result comparison

**Possible failure symptoms:** The rendered image differs from the reference by more than the fuzzy threshold, producing a failed test status ([pass/fail assignment](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L230-L238)).

**Possible implementation causes:** The rasterized output, image transition/readback path, format conversion, or comparison implementation may be responsible. The comparison result alone does not identify which layer caused the difference.

## Case Pruning

### Requirement-based pruning

- Unsupported dynamic rendering is rejected by `checkSupport` when `useDynamicRendering` is true; the render-pass leaves do not require `VK_KHR_dynamic_rendering` ([support gate](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L393-L397)).

### Design-based pruning

- Under `CTS_USES_VULKANSC`, dynamic-rendering registration and recording are excluded by preprocessor guards, leaving the render-pass cases in the VulkanSC mustpass set ([dispatcher guard](../../../modules/vulkan/draw/vktDrawTests.cpp#L144-L199)).
- Nested secondary-command-buffer modes do not register `simple_draw` because `createChildren` skips the simple-draw family when `nestedSecondaryCmdBuffer` is true ([selection guard](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L82)).

## Key Takeaways

- The four leaves cover two primitive topologies crossed with ordinary and instanced non-indexed draws.
- Every case uses `firstVertex=2`; instanced cases also use `instanceCount=4` and `firstInstance=2`.
- The oracle is a fuzzy comparison of a host-generated blue rectangle against the rendered color attachment, not a direct shader-output scalar check.
- The leaves are repeated across render-pass and three non-nested dynamic-rendering modes; nested dynamic-rendering modes intentionally have no simple-draw leaves.

## Source Reference Appendix

- [Assigned implementation: `vktDrawSimpleTest.cpp`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L47-L120) : test classes and vertex data.
- [`SimpleDraw::iterate`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L123-L239) : non-instanced recording and image oracle.
- [`SimpleDrawInstanced::iterate`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L273-L391) : instanced recording and image oracle.
- [`SimpleDrawTests::init`](../../../modules/vulkan/draw/vktDrawSimpleTest.cpp#L401-L446) : exact leaf registration.
- [`DrawTestsBaseClass`](../../../modules/vulkan/draw/vktDrawBaseClass.hpp#L73-L160) and [initialization](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L35-L195) : shared resources and pipeline.
- [`createChildren`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L122) and [category roots](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L201) : category-qualified registration scope.
- [`vk-default/draw.txt`](../../../mustpass/main/vk-default/draw.txt#L2093-L2096) and [`vksc-default/draw.txt`](../../../mustpass/main/vksc-default/draw.txt#L1642-L1645) : mustpass evidence for representative paths.
- [Vulkan render-pass chapter](../../../../vulkan-docs/src/chapters/renderpass.adoc#L7-L10) : render pass instance requirement for draw commands.
