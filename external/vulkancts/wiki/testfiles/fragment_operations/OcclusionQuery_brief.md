# Understanding Brief: `fragment_operations.occlusion_query`

## One-Sentence Test Purpose

This test checks whether an implementation's occlusion query correctly reports samples passing the per-fragment tests while scissor, depth clear, depth write, stencil clear, stencil write, and combined modifiers interact with those fragment tests, under both conservative (any non-zero result) and precise (exact count) query modes.

## Background Knowledge

### Occlusion queries

An occlusion query counts samples that pass all per-fragment tests (scissor, stencil, depth) for draw calls recorded between `vkCmdBeginQuery` and `vkCmdEndQuery`. The Vulkan spec (chapter "Occlusion Queries") defines two precision modes:

- Without `VK_QUERY_CONTROL_PRECISE_BIT` (conservative): the implementation may return any non-zero value when at least one sample passes. The result is effectively a boolean "did anything pass?" signal. Some implementations return only zero or one regardless of the actual sample count.
- With `VK_QUERY_CONTROL_PRECISE_BIT` (precise): the result must match the actual number of samples that passed the per-fragment tests.

The `occlusionQueryPrecise` device feature gates whether `VK_QUERY_CONTROL_PRECISE_BIT` is legal. Results are retrieved via `vk.getQueryPoolResults()` with `VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT`.

Why it matters here:
- The test exercises both modes: conservative variants accept any non-zero count; precise variants require an exact expected count computed from the test geometry.
- The precise feature gate is checked in `checkSupport()` before execution.

### Per-fragment test interaction

The occlusion query counts samples surviving the full fragment-test pipeline. Scissor clipping, depth test failures, and stencil test failures all reduce the surviving sample count. Depth and stencil clear operations (via `vkCmdClearAttachments`) modify the depth/stencil buffer mid-render-pass, changing which subsequent fragments pass their tests. Depth and stencil writes (occluder draws) write values into the buffer that cause later fragments to fail the depth or stencil test.

Why it matters here:
- The test uses a known geometry layout where the expected passing sample count can be computed arithmetically from the render size and which modifiers are active.
- The modifiers shift the expected count by predictable fractions of the image, making an exact-count check possible for the precise variants.

## One Concrete Example

Consider `conservative_test_scissors_clear_color`. The render target is 32x32. The scissor rectangle covers the central 16x16 region (from `renderSize/4` to `renderSize*3/4` in each axis). A full-screen triangle pair is drawn. Only fragments inside the scissor rectangle survive, so the occlusion query returns a non-zero count. Because this is a conservative variant, any non-zero count passes.

The precise counterpart `precise_test_scissors_clear_color` uses the same geometry but begins the query with `VK_QUERY_CONTROL_PRECISE_BIT`. The expected count is `imageSize / 4` (the scissor area is a quarter of the full image). The precise pass rule requires `sampleCounts[0] == expResult`.

## End-to-End Test Flow

```text
[host] create occlusion query pool (VK_QUERY_TYPE_OCCLUSION, 1 query)
[host] create color attachment image (R8G8B8A8_UNORM, 32x32)
[host] select depth/stencil format based on active modifiers (combined DS, S8_UINT, or D16_UNORM)
[host] create depth/stencil attachment image if any depth or stencil modifier is active
[host] create three vertex buffers: main full-screen quad, depth occluder, stencil occluder
[host] build graphics pipeline(s) with scissor, depth test, stencil test configured per modifiers
[host] begin command buffer
[host] vkCmdResetQueryPool to zero the query slot
[host] begin render pass, clearing color/depth/stencil to known values
[host] optional: vkCmdClearAttachments to clear depth (bottom half) or stencil (right half) to pass-enabling values
[host] optional: draw depth occluder (writes depth values that cause later fragments to fail)
[host] optional: draw stencil occluder with write pipeline (writes stencil values that cause later fragments to fail)
[host] vkCmdBeginQuery (with or without VK_QUERY_CONTROL_PRECISE_BIT)
[host] vkCmdDraw main full-screen geometry
[host] vkCmdEndQuery
[host] end render pass, copy color image to host-visible buffer
[host] submit and wait
[host] vk.getQueryPoolResults to read the sample count
[host] compute expected count from geometry and modifier combination (precise only)
[host] pass if conservative: count > 0; precise: count == expected
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Vertex shader (`vert`): a trivial pass-through that writes `gl_Position = position`. Source: [`OcclusionQueryTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L629-L648).
- Fragment shader (`frag`): writes a color derived from `gl_FragCoord`. Source: [`OcclusionQueryTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L650-L666).

These shaders are not part of the tested behavior. The test targets fixed-function fragment operations (scissor, depth, stencil) and query pool mechanics, not shader logic.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color attachment image (R8G8B8A8_UNORM, 32x32) | yes | yes | written by fragment shader | copied to buffer on failure for logging | Render target; fragments passing all tests write here |
| Depth/stencil attachment image | yes | yes | written by depth/stencil tests and clears | no | Modifier-dependent: depth/stencil tests and clears/writes change which fragments pass |
| Query pool (1 occlusion query) | yes | yes | incremented by device per passing sample | read back via `vk.getQueryPoolResults()` | The primary measurement object under test |
| Main vertex buffer (full-screen quad, 6 verts) | yes | yes | consumed by vertex shader | no | Draws geometry covering the full render area |
| Depth occluder vertex buffer (small quad, 6 verts) | yes | yes | consumed by vertex shader | no | Writes depth values that occlude part of the main geometry |
| Stencil occluder vertex buffer (small quad, 6 verts) | yes | yes | consumed by vertex shader | no | Writes stencil values that occlude part of the main geometry |
| Color readback buffer | yes | yes | written by copy command | read by host on failure | Used only for logging the rendered image when the test fails |

## What Is Checked

The test checks the occlusion query result:

- Conservative variants: the query result must be non-zero (`sampleCounts[0] > 0`). Any positive value passes.
- Precise variants: the query result must equal the expected count (`sampleCounts[0] == expResult`). The expected count is computed from the render size (32x32), the scissor mode (reduces to 1/4 of image area when active), and which occluder draws and clears are active.

The check is on the host after `vk.getQueryPoolResults()` returns. On failure, the color attachment is copied back and logged as an image for debugging.

## Behavior Parameter Identification

> **Behavior parameter:** query precision mode (conservative versus precise)
>
> **Candidate values:** `conservative` (query without `VK_QUERY_CONTROL_PRECISE_BIT`, accept any non-zero count), `precise` (query with `VK_QUERY_CONTROL_PRECISE_BIT`, require exact expected count)

The secondary behavioral axis is the modifier set (scissor, depth clear, depth write, stencil clear, stencil write, test_all). These are test case leaves within each precision mode, not a separate top-level axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `conservative` (any modifier) | Query pool result retrieval returns zero when samples should pass; occlusion query never started or ended incorrectly; scissor/depth/stencil state over-culls all fragments |
| `precise` (any modifier) | Expected count computation does not match device behavior; per-fragment test interaction (scissor, depth clear/write, stencil clear/write) kills or passes the wrong fragments; implementation does not count precisely despite `VK_QUERY_CONTROL_PRECISE_BIT` |

## Important Variations and Special Cases

### Scissor modifier (`TEST_SCISSOR`)

When active, the scissor rectangle covers the central quarter of the render area (`renderSize/4` to `renderSize*3/4`). This reduces the expected passing sample count to 1/4 of the full image in precise mode. The scissor is applied through pipeline dynamic state in `makeGraphicsPipeline()`.

### Depth clear modifier (`TEST_DEPTH_CLEAR`)

Uses `vkCmdClearAttachments` to clear the bottom half of the depth attachment to 1.0, which causes those fragments to fail the depth test (depth compare op is `VK_COMPARE_OP_LESS` against the cleared value 0.5 set in render pass clear). This halves the expected count in precise mode.

### Depth write modifier (`TEST_DEPTH_WRITE`)

Draws a small occluder quad that writes depth values causing a portion of the main geometry to fail the depth test. The occluder covers `imageSize / 64` pixels. This subtracts from the expected count.

### Stencil clear modifier (`TEST_STENCIL_CLEAR`)

Uses `vkCmdClearAttachments` to clear the right half of the stencil attachment to 0, which changes stencil test behavior for those fragments.

### Stencil write modifier (`TEST_STENCIL_WRITE`)

Draws a small occluder quad with a separate pipeline that writes stencil values causing a portion of the main geometry to fail the stencil test. Uses a dedicated `pipelineStencilWrite` with `VK_STENCIL_OP_REPLACE` and `VK_COMPARE_OP_ALWAYS`.

### Combined modifier (`TEST_ALL`)

Sets all modifier flags (`TEST_DEPTH_CLEAR | TEST_DEPTH_WRITE | TEST_STENCIL_CLEAR | TEST_STENCIL_WRITE`). All depth and stencil clears and writes are active simultaneously. The expected count reflects all interactions combined.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Case table generation | [`createOcclusionQueryTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L706-L767) | Builds the 32-case table and instantiates conservative and precise variants |
| Modifier flags enum | [`enum Flags`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L226-L236) | Defines `TEST_SCISSOR`, `TEST_DEPTH_WRITE`, etc. |
| Pipeline construction with scissor/depth/stencil | [`makeGraphicsPipeline()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L94-L150) | Configures per-modifier pipeline state |
| Depth/stencil clear helpers | [`commandClearDepthAttachment()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L152-L168), [`commandClearStencilAttachment()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L170-L186) | Mid-pass attachment clears for modifiers |
| Query begin/end with precise bit | [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L479-L489) | Where `VK_QUERY_CONTROL_PRECISE_BIT` is applied |
| Expected count computation | [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L502-L555) | Arithmetic for precise expected results |
| Result retrieval and pass/fail | [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L557-L588) | `vk.getQueryPoolResults()` and the conservative/precise pass rules |
| Support check | [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L675-L701) | Format support and `occlusionQueryPrecise` feature gate |

## Questions / Risk Points for User Audit

- Is the core test purpose clear? (The test verifies occlusion query results under fragment-operation modifiers and both precision modes.)
- Is the expected-count arithmetic correctly attributed to the source lines 502-555?
- Is the distinction between conservative (boolean) and precise (exact count) the primary behavioral axis?
- Are the modifier interactions (clear halves the image, write occluders subtract fixed pixel areas) explained at the right depth?
- Should the depth clear direction (bottom half vs right half for stencil) be stated explicitly?

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge into a compact prerequisite list: occlusion query conservative vs precise modes, `occlusionQueryPrecise` feature gate, per-fragment test interaction with query counting.
- The concrete example should become a brief overview bullet, not a full walkthrough.
- Copy the Failure Cause Mapping table directly into the final page.
- Write Cause Analysis fresh, grounded in the pass/fail rules.
- Move source links to the appendix; keep only evidence links in the body.
- The primary behavioral axis is precision mode (conservative vs precise). The modifier set is a secondary dimension documented in Parameter Dimensions.
