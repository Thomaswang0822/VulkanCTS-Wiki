# Understanding Brief: query_pool.discard

## One-Sentence Test Purpose

This test checks whether Vulkan occlusion queries count surviving samples correctly when fragment discard, shader sample masks, or alpha-to-coverage interact with early fragment tests and depth state.

## Background Knowledge

### Fragment coverage and sample counting

Rasterization starts each fragment with a coverage mask. Fragment operations can remove samples from that mask; if no bits remain, the fragment is discarded and later operations do not run. Occlusion queries count passing samples, so the point at which sample counting occurs matters when an early fragment shader changes coverage. See [Fragment Operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops).

### Early fragment tests and multisampling

`layout(early_fragment_tests) in;` changes when depth and stencil tests occur relative to fragment shading. Maintenance5 exposes `earlyFragmentSampleMaskTestBeforeSampleCounting` and `earlyFragmentMultisampleCoverageAfterSampleCounting`, which constrain the ordering tested here. Alpha-to-coverage uses four samples and derives a coverage mask from fragment alpha.

## One Concrete Example

For `query_pool.discard.normal.no_depth.precise.discard`, the generated fragment shader writes white and sets all sample-mask bits. On even `gl_FragCoord.x`, it executes `discard`; odd columns keep the output. The host therefore expects black even columns, white odd columns, and an exact query count of 512 from the 1024-pixel image.

## End-to-End Test Flow

```text
[host] choose early/depth/precision/discard parameters
[host] generate vertex and fragment GLSL
[host] create the occlusion query pool, attachments, render pass, pipeline, and readback buffer
[host] reset and begin the query, begin the render pass, bind the pipeline, and draw four vertices
[device] execute the fragment shader and the selected fixed-function coverage/depth operations
[host] end the query, transition and copy the color image, submit, wait, and read the query result
[host] compare the query result and every copied pixel with the expected values
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms()` generates a vertex shader that maps `gl_VertexIndex` to a full-screen quad.
- It generates a fragment shader with optional `EarlyFragmentTests`, an output at location 0, an all-covered `gl_SampleMask`, and one even-X mechanism: `discard`, zero sample mask, or zero alpha.
- `createPipeline()` selects one-sample or four-sample multisampling, enables static alpha-to-coverage for the static alpha leaf, and adds `VK_DYNAMIC_STATE_ALPHA_TO_COVERAGE_ENABLE_EXT` for the dynamic leaf.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Color image | yes | yes, as color attachment | written by the draw and read by transfer | indirectly through buffer | Stores the black/white pattern; alpha variants use a separate four-sample image and resolve to this image. |
| Depth image | yes | yes when the render pass includes it | cleared and used by depth testing | no | Distinguishes `no_depth` from `with_depth`; alpha variants use four depth samples. |
| Query pool | yes | yes | receives occlusion sample counts | yes, via `vkGetQueryPoolResults` | Supplies the precise or non-zero query check. |
| Host-visible color buffer | yes | transfer destination | receives the copied color image | yes | Lets the host check every pixel. |

## What Is Checked

- Precise cases require an exact occlusion result. The base is 1024 samples. Normal discard and sample-mask cases halve it; early cases retain 1024 under the gated Maintenance5 ordering. Alpha-to-coverage multiplies the corresponding value by four.
- Non-precise cases require a non-zero query result.
- Every pixel must be black at even X and white at odd X.

## Behavior Parameter Identification

> **Behavior parameter:** fragment mechanism (`discardType`)
>
> **Candidate values:** `discard`, `sample_mask`, `alpha_to_coverage`, `alpha_to_coverage_dynamic`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `discard` | Fragment termination, sample counting, or color readback does not match the expected even-X coverage. |
| `sample_mask` | Sample-mask output handling or the Maintenance5 sample-mask ordering does not match the expected query count. |
| `alpha_to_coverage` | Alpha-to-coverage coverage generation, multisample counting, resolve behavior, or color readback is incorrect. |
| `alpha_to_coverage_dynamic` | Dynamic alpha-to-coverage state, multisample counting, resolve behavior, or color readback is incorrect. |

## Important Variations and Special Cases

- `early` adds `layout(early_fragment_tests) in;` and is gated by Maintenance5 properties in non-SC builds. Vulkan SC rejects the early branch.
- `with_depth` enables depth testing and writing with `VK_COMPARE_OP_LESS`; `no_depth` disables both.
- `precise` requires `occlusionQueryPrecise` and checks an exact value. `none` does not require that feature and checks only non-zero query output.
- `alpha_to_coverage_dynamic` is non-SC only and requires `extendedDynamicState3AlphaToCoverageEnable`.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Test parameters and resources | [`vktQueryPoolDiscardTests.cpp#L48-L99`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L48-L99) | Defines the matrix and image formats. |
| Render pass and multisample setup | [`createRenderPass()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L101-L266) | Shows the alpha-to-coverage resolve path. |
| Pipeline state | [`createPipeline()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L268-L329) | Shows depth, alpha-to-coverage, and dynamic-state configuration. |
| Query and image checks | [`iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L331-L455) | Defines execution and pass/fail rules. |
| Support gates | [`checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L477-L502) | Defines feature and Maintenance5 requirements. |
| Generated shaders | [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L504-L534) | Defines the exact GLSL branches. |
| Fragment-operation specification | [Fragment Operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops) | Grounds early tests, sample masks, coverage, and sample counting. |
| Occlusion-query specification | [Queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries-occlusion) | Grounds the query type and result semantics. |

## Questions / Risk Points for User Audit

- Does the distinction between `discard`, sample-mask clearing, and alpha-to-coverage remain clear?
- Is the reason for the 512, 1024, 2048, and 4096 precise results clear?
- Are the Maintenance5 gates and Vulkan SC exclusions stated accurately?
- Is the dynamic-state difference from static alpha-to-coverage clear?

## Conversion Notes for Final Wiki Rewrite

- Keep the fragment mechanism as the primary behavior parameter and carry its mapping table directly into `Discard.md`.
- Distill the coverage and early-test explanations into the final Background Knowledge section.
- Use the discard case as the representative shader walkthrough; summarize sample-mask and alpha changes in the variation table.
- Keep the exact query formula, image check, support gates, and alpha resolve setup in the final page.
- The Vulkan spec links belong near the fragment-operation explanation and in the source appendix.
