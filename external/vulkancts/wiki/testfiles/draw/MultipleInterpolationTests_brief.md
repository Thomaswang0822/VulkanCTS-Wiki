## One-Sentence Test Purpose

This brief explains how `multiple_interpolation` checks that several interpolation decorations can coexist on independently addressed fragment inputs without changing one another's results.

## Background Knowledge

### Fragment-input interpolation

Rasterization supplies each fragment shader input from values written by primitive vertices. An undecorated floating-point input uses perspective-correct interpolation; `noperspective` uses linear screen-space interpolation, and `flat` takes the provoking vertex value. `centroid` chooses an interpolation position within primitive coverage, while `sample` uses the sample position for the fragment invocation.

Why it matters here:
- The same vertex color reaches five fragment inputs through those distinct rules.
- Edge coverage and multisampling make the interpolation-position rules observable.

### Interface blocks and member decorations

GLSL can carry the inputs as separate interface variables or as members of an `InterfaceBlock`. The structured form requires `GL_ARB_enhanced_layouts` in this generated shader so the test can place interpolation decorations on block members.

Why it matters here:
- The `structured` test family checks the SPIR-V/member-decoration representation, not merely a different GLSL spelling.

## One Concrete Example

Consider `dEQP-VK.draw.renderpass.multiple_interpolation.separate.with_sample_decoration.4_samples`.

The vertex shader writes one per-vertex color to five outputs at locations 0 through 4. The fragment shader receives matching `smooth`, `flat`, `noperspective`, `centroid`, and `sample` inputs. A push constant selects one array element, so one draw of the multi-input shader produces the selected interpolation result. The test compares that image with a separate draw that declares only the selected qualifier.

The source uses the same mechanism for `structured`, but the variables become members of an `InterfaceBlock` and accesses gain the `ifb.` prefix.

## End-to-End Test Flow

```text
[host] choose interface form, sample-decoration set, and sample count
[host] generate one multi-input GLSL program and one single-input reference program per qualifier
[host] create the vertex buffer, color target, optional multisample target, pipeline, and one uint push-constant range
[host] render the multi-input program once for each selectable qualifier
[device] interpolate the selected fragment input and resolve the color attachment when multisampling is enabled
[host] render the single-input references, including sample-rate-shading references when `sample` is present
[host] read back the 128 × 128 images and compare every channel with integer tolerance 1
[host] reject wrong same-qualifier results, unexpected non-MSAA equivalence, or unexpected distinctness failures
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`DrawTestCase::initPrograms` emits `vert_multi` and `frag_multi`, then emits matching single-qualifier vertex and fragment programs for `smooth`, `flat`, `noperspective`, and `centroid`; it adds `sample` programs only for `with_sample_decoration`. The multi fragment shader gathers its inputs in an array and uses `pc.interpolationIndex` to choose the output. The source branch that selects blocks versus separate variables also adds `GL_ARB_enhanced_layouts` only for the block form.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | read by vertex shader | no | Supplies three positions and colors that expose interpolation differences. |
| Single-sample color image | yes | attachment | written by fragment output and resolve | yes | Holds each result or reference image. |
| Multisample color image | for sample counts above 1 | attachment | written before resolve | no | Makes per-sample and centroid positions observable. |
| Fragment push constant | yes | yes | read by fragment shader | no | Selects the multi-program input under test. |

## What Is Checked

- For each active qualifier, the selected multi-input image must match the corresponding single-input reference within an integer per-channel threshold of 1.
- For `with_sample_decoration`, the selected image may instead match the reference rendered with sample-rate shading, because that is an accepted result for the `sample` case.
- Without multisampling, `smooth`, `centroid`, and `sample` must match each other.
- Apart from the explicitly permitted `smooth`/`centroid`/`sample` pairs, different qualifier results must not compare equal.

## Behavior Parameter Identification

> **Behavior parameter:** interface representation and included interpolation set
>
> **Candidate values:** `separate`, `structured`; `no_sample_decoration`, `with_sample_decoration`

The sample-count test case leaf changes the conditions under which the same behavior is observed. It is a configuration axis rather than the primary behavior axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `separate` | Incorrect independent interpolation decoration, location matching, generated multi-program selection, or image comparison for standalone variables. |
| `structured` | Incorrect interpolation decoration handling on interface-block members, block member matching, or the same shared rendering and checking path. |
| `no_sample_decoration` | Incorrect handling of `smooth`, `flat`, `noperspective`, or `centroid`, including the non-multisample equivalence rule. |
| `with_sample_decoration` | Incorrect `sample` interpolation or sample-rate-shading handling, or missing `sampleRateShading` feature gating. |

## Important Variations and Special Cases

- The test registers `1_sample`, `2_samples`, `4_samples`, `8_samples`, `16_samples`, `32_samples`, and `64_samples` beneath every interface and decoration combination.
- `with_sample_decoration` requires `sampleRateShading`; all leaves require their chosen count to appear in `framebufferColorSampleCounts`.
- Dynamic-rendering registrations require `VK_KHR_dynamic_rendering`; the source also supports legacy render-pass recording and the draw category's primary and secondary command-buffer configurations.
- The source permits `smooth`, `centroid`, and `sample` to compare equal in the cases stated above because smooth interpolation uses an implementation-defined position while centroid and sample constrain that position differently.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Generated multi and reference shaders | [initPrograms](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L151-L293) | Builds the decorated interfaces and selected-reference programs. |
| Feature and rendering-path checks | [checkSupport](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L295-L305) | Defines sample-count, sample-rate-shading, and dynamic-rendering support boundaries. |
| Resource setup and drawing | [render](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L312-L624) | Creates attachments, pipeline state, draws, and reads back output. |
| Result comparison and acceptance rules | [compare and iterate](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L626-L829) | Defines threshold, same-qualifier, equivalence, and distinctness checks. |
| Registered matrix | [createTests](../../../modules/vulkan/draw/vktDrawMultipleInterpolationTests.cpp#L831-L895) | Defines interface, decoration, and sample-count dimensions. |
| Vulkan interpolation rules | [Interpolation Decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2879-L2949) | Grounds the qualifier meanings and position constraints. |

## Questions / Risk Points for User Audit

- Does the distinction between comparing a multi-input program and a single-input reference make the test purpose clear?
- Does the brief make clear that `structured` targets decoration placement on block members?
- Are the allowed equivalence cases and the special sample-rate-shading reference described at the right depth?
- Should the final page retain a reconstructed fragment-shader walkthrough, or does the generated-shader summary provide enough detail?

## Conversion Notes for Final Wiki Rewrite

- Keep the interface representation and decoration set as the primary behavior parameters, and copy the failure-cause mapping table unchanged.
- Use a compact prerequisite list for interpolation decorations and interface blocks.
- Preserve the image-comparison flow, support gates, and reference-render distinction.
- Include one representative `with_sample_decoration` fragment-shader walkthrough only if it can include compiler-produced SPIR-V generated through the shader-analysis workflow; otherwise keep `Shader Analysis` as a source-grounded generated-shader summary without a hand-written walkthrough.
