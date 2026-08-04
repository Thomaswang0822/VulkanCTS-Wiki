# Understanding Brief: pipeline interface matching

## One-Sentence Test Purpose

This test checks whether graphics-pipeline shader stages match user-defined input and output interfaces correctly when vector sizes, decorations, declaration forms, or unused outputs vary.

## Background Knowledge

### Stage-interface matching

A graphics pipeline passes user-defined output variables from one shader stage to the next. Matching uses decorations and types, with defined exceptions. An output vector may satisfy a shorter input vector with `maintenance4` enabled, and a later stage may omit an input for an output that an earlier stage writes. The Vulkan specification defines these rules in [Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L119-L181).

Why it matters here:
- The generated cases change the relationship between one producing interface and one consuming interface without changing the rendering target.
- `skip_output_variable` checks the allowed omission case rather than an undefined read from a missing output.

### Locations and components

`Location` selects a four-component interface slot and `Component` selects positions within it. Width changes how many component slots a value consumes, which is why the delegated layout test covers 16-, 32-, and 64-bit declarations. See [Location and Component Assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#L194-L258).

Why it matters here:
- `COMPONENT0` participates in a decoration-mismatch matrix.
- The delegated `shader_layout_component_matching` test family exercises packed component layouts rather than only whole-vector type matching.

## One Concrete Example

In `misc.skip_output_variable`, the vertex shader writes `v0`, `v1`, and `v2` at locations 0, 1, and 2. The fragment shader declares only `v0` and `v2`, then writes `v0 + v2` to the color attachment. It should receive the values from locations 0 and 2, not shift the location-2 input into the unused location-1 slot. The generated GLSL appears in [`MiscInterfaceMatchingTestCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1208-L1238).

## End-to-End Test Flow

```text
[host] select a pipeline construction type and interface parameters
[host] generate vertex, optional tessellation or geometry, and fragment shader sources
[host] build the graphics pipeline and a color target
[host] record and submit one draw, then wait for completion
[device] match stage interfaces and execute the generated shaders
[device] write shader verification data to the color target
[host] copy the target to host-visible memory and inspect the expected pixels
[host] mark the test case pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`InterfaceMatchingTestCase` generates shader declarations and input-side comparisons from `TestParams`; the input comparison uses equality for integer vectors and an absolute-error threshold of `0.001` for floating-point vectors ([`genInVerification()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L862-L894)). The source creates cases for vector-size and decoration relationships in [`createInterfaceMatchingTests()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1254-L1357).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color image | yes | color attachment | written by fragment shader | copied to buffer | Carries the shader's success color. |
| Result buffer | yes | transfer destination | written by image copy | yes | Lets the host inspect rendered pixels. |
| Vertex buffer | yes | vertex input | read by draw | no | Supplies geometry for the regular generated cases. |

## What Is Checked

- `vector_length` and `decoration_mismatch` shaders encode their input-side checks into two pixels. The host passes the test only when both selected red channels exceed 254 ([result check](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L385-L400)).
- `skip_output_variable` expects every pixel to contain `(0, 1, 1, 1)` and counts any component outside its byte tolerance as a wrong fragment ([result check](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1160-L1176)).
- The separately implemented `shader_layout_component_matching` family has its own page and verification path.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate test-family branch
>
> **Candidate values:** `vector_length`, `decoration_mismatch`, `shader_layout_component_matching`, `misc.skip_output_variable`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vector_length` | Vector interface matching with `maintenance4`, declaration-form handling, or stage-interface propagation produced a failed shader check. |
| `decoration_mismatch` | Decoration matching or pipeline-library interpolation-decoration handling produced a failed shader check. |
| `shader_layout_component_matching` | Component and location packing, width-specific layout handling, or stage-interface matching in the delegated family failed. |
| `misc.skip_output_variable` | The implementation did not preserve location-based matching when the fragment shader omitted the location-1 input. |

## Important Variations and Special Cases

- The vector-length generator retains only pairs where the output vector is at least as long as the input vector. Different lengths require `VK_KHR_maintenance4` ([support check](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L919-L924)).
- The decoration matrix tests `NONE`, `FLAT`, `NO_PERSPECTIVE`, and `COMPONENT0`. `COMPONENT0` cases use only loose variables or block members ([registration loop](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1315-L1343)).
- Pipeline-library cases that involve `FLAT` or `NO_PERSPECTIVE` skip when `graphicsPipelineLibraryIndependentInterpolationDecoration` is unavailable ([support check](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L896-L917)).
- The parent file registers `shader_layout_component_matching` only outside Vulkan SC and delegates its implementation to [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1172-L1215).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter model | [`TestType` through `TestParams`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L57-L133) | Defines the generated vector, decoration, stage, and declaration-form inputs. |
| Generated interface checks | [`genInVerification()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L862-L894) | Shows the shader-side comparison rule. |
| Feature checks | [`InterfaceMatchingTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L896-L946) | Applies construction, extension, and stage-feature gates. |
| Miscellaneous case | [`MiscInterfaceMatchingTestCase`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1202-L1249) | Defines the skipped-output shader pair. |
| Registration | [`createInterfaceMatchingTests()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1254-L1357) | Builds the four direct branches. |

## Questions / Risk Points for User Audit

- Does the distinction between a permitted unused output and an undefined input remain clear?
- Does the page identify the delegated component-layout family without duplicating its technical documentation?
- Does the behavior-axis grouping make the failure mapping useful for a reader triaging a failing test?

## Conversion Notes for Final Wiki Rewrite

- Keep the brief's four-row failure-cause table unchanged in the final page.
- Distill the two prerequisite concepts into short final-page bullets.
- Use `misc.skip_output_variable` as the formal representative shader explanation, because its source is explicit and it isolates location-based matching.
- Keep `shader_layout_component_matching` as a delegated test family and link to its preserved page until that family receives its own rewritten page.
