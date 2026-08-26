## Overview

**Core question:** Does the implementation's occlusion query correctly count samples that survive the per-fragment test pipeline when scissor, depth, and stencil operations modify which fragments pass, under both conservative (any non-zero) and precise (exact count) query modes?

- The source file [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L1) implements and registers the `occlusion_query` test family under [`fragment_operations`](../../categories/fragment_operations.md).
- Each test case draws a full-screen quad inside an active occlusion query, with optional scissor clipping, mid-pass depth/stencil clears, and occluder draws that write depth or stencil values. The query result is then checked against a precision-dependent pass rule.
- Conservative variants begin the query without `VK_QUERY_CONTROL_PRECISE_BIT` and accept any non-zero sample count. Precise variants begin with that bit set and require an exact expected count computed from the geometry and active modifiers.
- The test family generates 64 test case leaves: 32 `conservative_*` and 32 `precise_*` variants from a shared case table of modifier combinations.

## Background Knowledge

For the shared concept of per-fragment testing and sample coverage, see [Background Knowledge](../../categories/fragment_operations.md#background-knowledge) of the `fragment_operations` page.

- **Occlusion query precision modes.** Without `VK_QUERY_CONTROL_PRECISE_BIT`, the implementation may return any non-zero value when at least one sample passes; with the bit set, the result must match the actual number of passing samples. The `occlusionQueryPrecise` device feature gates precise queries. See the Vulkan specification's [Occlusion Queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries-occlusion) section for these semantics.

## Registration Hierarchy

```text
fragment_operations.occlusion_query
├── conservative_test_scissors_clear_color
├── conservative_test_scissors_depth_clear
├── conservative_test_scissors_depth_write
├── conservative_test_scissors_depth_clear_depth_write
├── conservative_test_scissors_stencil_clear
├── conservative_test_scissors_stencil_write
├── conservative_test_scissors_stencil_clear_stencil_write
├── conservative_test_scissors_depth_clear_stencil_clear
├── conservative_test_scissors_depth_write_stencil_clear
├── conservative_test_scissors_depth_clear_stencil_write
├── conservative_test_scissors_depth_write_stencil_write
├── conservative_test_scissors_depth_clear_stencil_clear_depth_write
├── conservative_test_scissors_depth_clear_stencil_clear_stencil_write
├── conservative_test_scissors_depth_clear_depth_write_stencil_write
├── conservative_test_scissors_depth_write_stencil_clear_stencil_write
├── conservative_test_scissors_test_all
├── conservative_test_clear_color
├── conservative_test_depth_clear
├── conservative_test_depth_write
├── conservative_test_depth_clear_depth_write
├── conservative_test_stencil_clear
├── conservative_test_stencil_write
├── conservative_test_stencil_clear_stencil_write
├── conservative_test_depth_clear_stencil_clear
├── conservative_test_depth_write_stencil_clear
├── conservative_test_depth_clear_stencil_write
├── conservative_test_depth_write_stencil_write
├── conservative_test_depth_clear_stencil_clear_depth_write
├── conservative_test_depth_clear_stencil_clear_stencil_write
├── conservative_test_depth_clear_depth_write_stencil_write
├── conservative_test_depth_write_stencil_clear_stencil_write
├── conservative_test_test_all
├── precise_test_scissors_clear_color
├── precise_test_scissors_depth_clear
├── precise_test_scissors_depth_write
├── precise_test_scissors_depth_clear_depth_write
├── precise_test_scissors_stencil_clear
├── precise_test_scissors_stencil_write
├── precise_test_scissors_stencil_clear_stencil_write
├── precise_test_scissors_depth_clear_stencil_clear
├── precise_test_scissors_depth_write_stencil_clear
├── precise_test_scissors_depth_clear_stencil_write
├── precise_test_scissors_depth_write_stencil_write
├── precise_test_scissors_depth_clear_stencil_clear_depth_write
├── precise_test_scissors_depth_clear_stencil_clear_stencil_write
├── precise_test_scissors_depth_clear_depth_write_stencil_write
├── precise_test_scissors_depth_write_stencil_clear_stencil_write
├── precise_test_scissors_test_all
├── precise_test_clear_color
├── precise_test_depth_clear
├── precise_test_depth_write
├── precise_test_depth_clear_depth_write
├── precise_test_stencil_clear
├── precise_test_stencil_write
├── precise_test_stencil_clear_stencil_write
├── precise_test_depth_clear_stencil_clear
├── precise_test_depth_write_stencil_clear
├── precise_test_depth_clear_stencil_write
├── precise_test_depth_write_stencil_write
├── precise_test_depth_clear_stencil_clear_depth_write
├── precise_test_depth_clear_stencil_clear_stencil_write
├── precise_test_depth_clear_depth_write_stencil_write
├── precise_test_depth_write_stencil_clear_stencil_write
└── precise_test_test_all
```

Source: [`createOcclusionQueryTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L706-L767).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Query precision mode | `conservative`, `precise` | Determines whether the query uses `VK_QUERY_CONTROL_PRECISE_BIT` and whether the pass rule checks for non-zero or exact count | [`createOcclusionQueryTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L755-L763) |
| Scissor modifier | `TEST_SCISSOR` present or absent | When present, the scissor rectangle clips to the central quarter of the render area, reducing expected passing samples to 1/4 of the image | [`makeGraphicsPipeline()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L101-L106) |
| Depth clear modifier | `TEST_DEPTH_CLEAR` present or absent | Clears the bottom half of the depth attachment mid-pass, causing those fragments to fail the depth test | [`commandClearDepthAttachment()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L152-L168) |
| Depth write modifier | `TEST_DEPTH_WRITE` present or absent | Draws a small occluder that writes depth values causing part of the main geometry to fail the depth test | [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L463-L467) |
| Stencil clear modifier | `TEST_STENCIL_CLEAR` present or absent | Clears the right half of the stencil attachment mid-pass, changing stencil test behavior for those fragments | [`commandClearStencilAttachment()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L170-L186) |
| Stencil write modifier | `TEST_STENCIL_WRITE` present or absent | Draws a small occluder with a write-enabled pipeline that writes stencil values causing part of the main geometry to fail the stencil test | [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L469-L475) |
| Combined modifier | `TEST_ALL` | Activates depth clear, depth write, stencil clear, and stencil write simultaneously | [`enum Flags`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L234) |
| Render size | 32 x 32 | Fixed render area used for all cases; determines the base expected sample count of 1024 for precise variants | [`createOcclusionQueryTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L758-L763) |
| Depth/stencil format | combined DS format, `VK_FORMAT_S8_UINT`, or `VK_FORMAT_D16_UNORM` | Selected based on which modifiers are active: combined DS when both depth and stencil tests run, stencil-only when only stencil, depth-only otherwise | [`pickSupportedDepthStencilFormat()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L211-L224) |

## Behavior Parameters

The primary behavioral axis is the query precision mode. Each value changes how the query is issued and how the result is validated.

### `conservative`: boolean occlusion check

The query begins without `VK_QUERY_CONTROL_PRECISE_BIT` at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L483-L485). The Vulkan spec permits the implementation to return any non-zero value when at least one sample passes the per-fragment tests. The pass rule at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L572-L573) accepts any non-zero count (`sampleCounts[0] > 0`). These variants verify that the query correctly reports "some fragments passed" without requiring an exact count. They do not depend on the `occlusionQueryPrecise` feature.

### `precise`: exact sample count check

The query begins with `VK_QUERY_CONTROL_PRECISE_BIT` at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L479-L482). The pass rule at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L572-L573) requires the result to match an expected count computed from the render size and active modifiers (`sampleCounts[0] == expResult`). The expected count is computed at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L502-L555) by starting from the full image area (or 1/4 when scissor is active) and subtracting fractions for each active occluder draw and clear region. These variants require the `occlusionQueryPrecise` feature, checked in [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L689-L694).

## Shader Analysis

Shader code is not part of the tested behavior. The vertex shader is a trivial pass-through (`gl_Position = position`), and the fragment shader writes a color derived from `gl_FragCoord`. The test targets fixed-function fragment operations and query pool mechanics, not shader logic. Source: [`OcclusionQueryTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L627-L666).

## Runtime Execution and Result Checking

- A query pool of type `VK_QUERY_TYPE_OCCLUSION` with one query slot is created at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L288-L299).
- The command buffer resets the query pool before use at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L446).
- The render pass begins with a known color clear (black); when a depth/stencil attachment is present, its clear values are depth 0.5 and stencil 1 at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L433-L449).
- Active modifiers issue mid-pass clears and occluder draws before the main geometry: depth clear (bottom half to value 1), stencil clear (right half to value 0), depth occluder draw, stencil occluder draw with a separate write-enabled pipeline at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L454-L475).
- The main full-screen quad is drawn inside `cmdBeginQuery` / `cmdEndQuery` at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L479-L489). The precise bit is applied or omitted based on the variant.
- After submission and wait, `vk.getQueryPoolResults()` reads the 64-bit result with wait flag at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L557-L559).
- The pass/fail rule at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L572-L573): conservative passes if count is non-zero; precise passes if count equals the expected value.
- On failure, the color attachment is copied back and logged as an image at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L579-L587).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `conservative` (any modifier) | Query result retrieval returns zero when samples should pass; query begin/end mismatch; scissor/depth/stencil state over-culls all fragments |
| `precise` (any modifier) | Expected count computation does not match device behavior; per-fragment test interaction kills or passes the wrong fragments; implementation does not count precisely despite `VK_QUERY_CONTROL_PRECISE_BIT` |

### Cause Analysis

#### Query returns zero when samples should pass (conservative)

**Possible failure symptoms:** The conservative variant reports `sampleCounts[0] == 0` despite a full-screen quad being drawn inside the active query. The test logs "Passed Samples: 0 / 0" and fails with the color attachment image.

**Possible implementation causes:** The query pool may not have been correctly reset or the query may not have been active during the draw. Pipeline state (scissor rectangle, depth compare, stencil reference) may be misconfigured such that no fragments survive the per-fragment tests. A driver or hardware bug in occlusion query activation or result writing could also produce a zero result. The test exercises basic query begin/end wrapping of a single draw, so a zero result on the no-modifier base case (`conservative_test_clear_color`) would point to fundamental query pool or draw mechanics.

#### Expected count mismatch (precise)

**Possible failure symptoms:** The precise variant reports a count that differs from the expected value computed at [`iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L502-L555). The test logs "Passed Samples: N / M" where N differs from M, then fails.

**Possible implementation causes:** The expected-count arithmetic assumes specific geometric coverage from the occluder quads, clear regions (bottom half for depth, right half for stencil), and scissor rectangle. If the implementation's per-fragment test behavior differs from these assumptions (for example, a depth clear region that is off by one row, or a stencil test that passes where it should fail), the count will not match. The Vulkan spec notes that some implementations may kill fragments in pre-rasterization shader stages, and those killed fragments do not contribute to the query result, which could cause a mismatch. An implementation that claims `occlusionQueryPrecise` support but does not return a precise count would also fail. Source-level investigation may be needed to determine whether the mismatch stems from the expected-count arithmetic or from device behavior.

## Case Pruning

### Requirement-based pruning

- Precise variants require the `occlusionQueryPrecise` device feature. [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L689-L694) throws `NotSupportedError` when the feature is not present.
- The selected depth/stencil format is checked for support for every variant, including the color-only cases: [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L675-L701) queries `vkGetPhysicalDeviceImageFormatProperties` and throws `NotSupportedError` when the selected format is unsupported. The combined depth/stencil format is selected from `VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, or `VK_FORMAT_D32_SFLOAT_S8_UINT` by [`pickSupportedDepthStencilFormat()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L211-L224).

### Design-based pruning

- The case table does not exhaustively cross every modifier combination. It selects representative combinations: individual modifiers, scissor-crossed variants, key pairs (depth clear + depth write, stencil clear + stencil write), select triples, and the `test_all` aggregate. This keeps the matrix focused on meaningful per-fragment test interactions without redundant permutations.

## Key Takeaways

- The test verifies that occlusion query results correctly reflect samples surviving scissor, depth, and stencil fragment tests, under both conservative (boolean) and precise (exact count) query modes.
- Conservative variants validate that the query reports non-zero when fragments pass, without requiring exact counts or the `occlusionQueryPrecise` feature.
- Precise variants validate an exact expected count computed from render geometry and modifier interactions, requiring the `occlusionQueryPrecise` feature.
- The modifier matrix (scissor, depth clear/write, stencil clear/write, test_all) exercises the per-fragment test pipeline's effect on query counting by changing which fragments pass.
- See `## Failure Meaning` for analysis of what a failed result indicates about the implementation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Case table and registration | [`createOcclusionQueryTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L706-L767) | Builds the 32-case table and instantiates conservative and precise variants |
| Modifier flags enum | [`enum Flags`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L226-L236) | Defines `TEST_SCISSOR`, `TEST_DEPTH_CLEAR`, `TEST_DEPTH_WRITE`, `TEST_STENCIL_CLEAR`, `TEST_STENCIL_WRITE`, `TEST_ALL`, `TEST_PRECISE_BIT` |
| Pipeline construction | [`makeGraphicsPipeline()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L94-L150) | Configures scissor, depth test, stencil test per modifier combination |
| Depth/stencil clear helpers | [`commandClearDepthAttachment()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L152-L168), [`commandClearStencilAttachment()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L170-L186) | Mid-pass attachment clears that shift expected passing sample counts |
| Format selection | [`pickSupportedDepthStencilFormat()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L211-L224) | Selects a supported combined or single aspect depth/stencil format |
| Test instance iteration | [`OcclusionQueryTestInstance::iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L275-L590) | Full render, query, readback, and pass/fail logic |
| Expected count computation | [`iterate()` expected count block](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L502-L555) | Arithmetic for precise-mode expected results |
| Support check | [`OcclusionQueryTest::checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L675-L701) | Format support and `occlusionQueryPrecise` feature gate |
| Shader generation | [`OcclusionQueryTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L627-L666) | Trivial vertex and fragment shaders; not part of tested behavior |
| Header | [`vktFragmentOperationsOcclusionQueryTests.hpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.hpp) | Declares `createOcclusionQueryTests()` |
| Mustpass | [`fragment-operations.txt`](../../../mustpass/main/vk-default/fragment-operations.txt) | Registered test case paths for this family |
