## Overview

**Core question:** Does a graphics pipeline deliver a producer stage's user-defined interface values to the intended inputs of later stages when declarations differ in allowed or deliberately mismatched ways?

- This page covers the `interface_matching` test family implemented by [`vktPipelineInterfaceMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L57-L1358).
- `vector_length` and `decoration_mismatch` generate graphics-pipeline cases over stage arrangements and declaration forms. `misc.skip_output_variable` supplies one focused location-based case.
- The source also registers the non-VulkanSC `shader_layout_component_matching` test family, but delegates its implementation to [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1172-L1215).
- The sections below separate the generated dimensions from the four behaviors, then follow the draw and readback path that determines the CTS result.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A user-defined output in one graphics shader stage must interface-match the corresponding input in a later stage. Matching depends on decorations and types. The specification permits a longer output vector to match a shorter input vector when `maintenance4` is enabled, and permits an output that no later stage reads ([Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L119-L181)).
- `Location` identifies a four-component interface slot; `Component` identifies positions within that slot. Component packing changes with 16-, 32-, and 64-bit values ([Location and Component Assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#L194-L258)).

## Registration Hierarchy

```text
pipeline.monolithic.interface_matching
├── vector_length
├── decoration_mismatch
├── shader_layout_component_matching (registration only; non-VulkanSC)
└── misc
```

The pipeline mustpass configuration is split across seven construction-mode files under [`mustpass/main/vk-default/pipeline/`](../../../mustpass/main/vk-default/pipeline/): monolithic, pipeline-library, fast-linked-library, and four shader-object variants (linked or unlinked, with binary or SPIR-V shader sources). Each contains 1,589 `interface_matching` leaves, for 11,123 leaves total. Per construction mode, those leaves comprise 972 `vector_length` cases, 360 `decoration_mismatch` cases, 256 delegated `shader_layout_component_matching` cases, and the single `misc.skip_output_variable` case.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Interface behavior | `VECTOR_LENGTH`, `DECORATION_MISMATCH`, `SKIP_OUTPUT_VARIABLE` | Selects the generated vector rule, decoration rule, or focused skipped-output case. | [`TestType`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L57-L64) |
| Vector type | `VEC2` through `VEC4`, `IVEC2` through `IVEC4`, `UVEC2` through `UVEC4` | Selects scalar kind and output/input component counts for `vector_length`. | [`VecType`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L66-L77) |
| Decoration | `NONE`, `FLAT`, `NO_PERSPECTIVE`, `COMPONENT0` | Forms the producer and consumer decoration pair in `decoration_mismatch`. | [`DecorationType`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L79-L85) |
| Stage arrangement | Nine `PipelineType` values from `VERT_OUT_FRAG_IN` to `VERT_TESC_TESE_GEOM_OUT_FRAG_IN` | Places the producer-consumer relationship across vertex, tessellation, geometry, and fragment stages. | [`PipelineType`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L87-L106) |
| Declaration form | `LOOSE_VARIABLE`, `MEMBER_OF_BLOCK`, `MEMBER_OF_STRUCTURE`, `MEMBER_OF_ARRAY_OF_STRUCTURES`, `MEMBER_OF_STRUCTURE_IN_BLOCK`, `MEMBER_OF_ARRAY_OF_STRUCTURES_IN_BLOCK` | Checks matching through direct declarations and nested aggregate forms. | [`DefinitionType`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L108-L116) |
| Pipeline construction | monolithic, pipeline-library, fast-linked-library, and shader-object mustpass roots | Exercises the same interface behavior through different construction paths. | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L118-L131), [mustpass files](../../../mustpass/main/vk-default/pipeline/) |

The generator retains vector pairs only when the output has at least as many components as the input. It uses nine stage arrangements, six declaration forms, three scalar kinds, and the valid output/input vector-size combinations. The decoration generator uses eight explicit pairs and limits `COMPONENT0` to loose variables and block members ([generation loops](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1257-L1343)).

## Behavior Parameters

The primary behavioral axis is the registered branch below `interface_matching`. Each branch changes the interface property under test rather than only its declaration configuration.

### vector_length - Longer producer vectors

This branch checks the `maintenance4` rule that allows an output vector with more components to match an input vector with the same component type and fewer components. Generated consumer code checks every declared input component against the producer's known value; it never asks the consumer to read a component it did not declare.

### decoration_mismatch - Producer and consumer decorations

This branch changes the input and output interpolation or component decorations while holding the vector type at `vec4`. It tests mismatched pairs involving `NONE`, `FLAT`, `NO_PERSPECTIVE`, and `COMPONENT0`; the generated consumer comparison reports whether the received value follows the interface declaration path.

### shader_layout_component_matching - Packed component layouts

This delegated test family covers component-decorated layouts across stage flows, declaration modes, bit widths, location counts, and packing patterns. It remains a registration-only area on this page; readers should use the rewritten [component-layout page](ShaderComponentDecoratedLayoutMatching.md) for its implementation details.

### misc.skip_output_variable - Omitted location-1 input

The vertex shader writes `v0`, `v1`, and `v2` at locations 0, 1, and 2. The fragment shader declares inputs only at locations 0 and 2 and adds them. The test checks that location 2 still supplies `v2`, as interface matching uses locations rather than compacts variables around the omitted location-1 input ([generated shader pair](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1208-L1238)).

## Shader Analysis

The source generates GLSL for the vector and decoration matrices. Its input-side verification generator emits an equality check for integer components and an absolute-error check below `0.001` for floating-point components, then writes the combined result through the fragment stage ([`genInVerification()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L862-L894)).

For the concrete `misc.skip_output_variable` case, the vertex shader assigns `(0, 1, 0, 0)` to location 0, `(1, 0, 0, 1)` to location 1, and `(0, 0, 1, 1)` to location 2. The fragment shader declares locations 0 and 2 only, then writes `v0 + v2`. A correct match therefore produces `(0, 1, 1, 1)`. This page does not embed reconstructed GLSL or SPIR-V because the test's generated program text remains authoritative in the CTS source.

## Runtime Execution and Result Checking

- The test creates a color image, a host-visible result buffer, and a command buffer. It transitions the image to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`, renders a single triangle, and copies the image to the result buffer ([draw and copy](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L354-L383)).
- For the generated vector and decoration cases, the fragment-stage check writes success into two selected pixels. After queue completion and allocation invalidation, the host passes only when both selected red channels exceed 254 ([host check](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L385-L400)).
- For `skip_output_variable`, the host scans the full image after the copy. It expects each pixel to encode `(0, 1, 1, 1)` within the byte thresholds in the source and logs the image on failure ([full-image check](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1160-L1176)).
- The support check requires the selected pipeline-construction path, requests `VK_KHR_maintenance4` for unequal vector lengths, and rejects stage arrangements without required tessellation or geometry features ([support checks](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L896-L946)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vector_length` | Vector interface matching with `maintenance4`, declaration-form handling, or stage-interface propagation produced a failed shader check. |
| `decoration_mismatch` | Decoration matching or pipeline-library interpolation-decoration handling produced a failed shader check. |
| `shader_layout_component_matching` | Component and location packing, width-specific layout handling, or stage-interface matching in the delegated family failed. |
| `misc.skip_output_variable` | The implementation did not preserve location-based matching when the fragment shader omitted the location-1 input. |

### Cause Analysis

#### Vector interface matching and declaration propagation

**Possible failure symptoms:** One or both selected red channels are at most 254, so the generated input-side comparison evaluated false.

**Possible implementation causes:** The implementation may reject or mislink the `maintenance4` longer-output/shorter-input rule, propagate the wrong component values across a stage boundary, or handle one of the tested block, structure, or array declaration forms incorrectly. The specification permits the vector relationship only with `maintenance4` enabled ([interface rule](../../../../vulkan-docs/src/chapters/interfaces.adoc#L140-L158)); source-level investigation is needed to localize a particular failing declaration form.

#### Decoration matching and library construction

**Possible failure symptoms:** The generated decoration case fails its shader-side value check and the host reports a failed selected pixel.

**Possible implementation causes:** The compiler or linker may apply a decoration relationship incorrectly, or a separate graphics-pipeline-library path may handle differing interpolation decorations incorrectly. The test skips relevant library cases when the implementation does not support `graphicsPipelineLibraryIndependentInterpolationDecoration` ([source gate](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L896-L917)); the specification also defines the limit's effect on matches across the pre-rasterization and fragment boundary ([rule](../../../../vulkan-docs/src/chapters/interfaces.adoc#L168-L176)).

#### Component layout matching in the delegated family

**Possible failure symptoms:** The delegated family reports a result that differs from its expected color.

**Possible implementation causes:** A failure can involve location or component-slot assignment, width-specific packing, or interface matching after layout construction. The specification assigns component slots differently for 16-, 32-, and 64-bit values ([assignment rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#L206-L248)). This parent source only registers the family, so source-level investigation in the delegated implementation is needed to identify the failing flow or packing pattern.

#### Omitted output-variable handling

**Possible failure symptoms:** The `misc.skip_output_variable` image contains a pixel outside the expected `(0, 1, 1, 1)` byte thresholds, often indicating that `v2` did not arrive as the location-2 value.

**Possible implementation causes:** The implementation may compact declared interface variables by declaration order, instead of matching the fragment input at location 2 to the producer output at location 2. Vulkan permits a shader to write outputs that the subsequent stage does not declare or read ([interface rule](../../../../vulkan-docs/src/chapters/interfaces.adoc#L178-L181)); source-level investigation is needed to separate compiler interface lowering from later pipeline linking.

## Case Pruning

### Requirement-based pruning

- Unequal vector lengths require `VK_KHR_maintenance4`.
- Tessellation and geometry stage arrangements require `tessellationShader` and `geometryShader`, respectively.
- Pipeline-library cases involving `FLAT` or `NO_PERSPECTIVE` skip when `graphicsPipelineLibraryIndependentInterpolationDecoration` is unavailable.
- `shader_layout_component_matching` is excluded from Vulkan SC by its registration guard.

### Design-based pruning

- The vector matrix drops combinations where the output vector is shorter than the input vector because they do not exercise the intended permitted longer-output relationship.
- The source omits one tessellation/geometry stage arrangement because its comment identifies it as similar to another arrangement already covered ([stage list](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1263-L1273)).
- `COMPONENT0` decoration pairs use only `LOOSE_VARIABLE` and `MEMBER_OF_BLOCK`, matching the source's focused matrix boundary.

## Key Takeaways

- The family tests interface matching as a rendered, shader-observed property rather than relying on pipeline creation success alone.
- `vector_length` isolates the `maintenance4` type exception, while `decoration_mismatch` varies interface decorations across the same stage and declaration matrix.
- `skip_output_variable` proves that a skipped declaration does not renumber later `Location`-based inputs.
- Component-layout behavior belongs to the delegated family; this page records its registration boundary and the shared interface rules that give it context.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter enumerations and `TestParams` | [`vktPipelineInterfaceMatchingTests.cpp#L57-L133`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L57-L133) | Defines the generated case dimensions. |
| Generated input comparison | [`genInVerification()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L862-L894) | Defines integer and floating-point shader-side checks. |
| Feature and construction gates | [`InterfaceMatchingTestCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L896-L946) | Applies extension and stage requirements. |
| General result readback | [draw, copy, and selected-pixel check](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L354-L400) | Shows the regular host-visible pass condition. |
| Skipped-output case | [`MiscInterfaceMatchingTestCase`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1071-L1249) | Generates and validates `skip_output_variable`. |
| Registration | [`createInterfaceMatchingTests()`](../../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1254-L1357) | Registers the four direct branches. |
| Delegated component-layout implementation | [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1172-L1215`](../../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1172-L1215) | Owns the registered component-layout family. |
