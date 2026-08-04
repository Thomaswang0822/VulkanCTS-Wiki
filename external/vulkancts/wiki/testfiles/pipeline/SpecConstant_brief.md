# Understanding Brief: pipeline specialization constants

## One-Sentence Test Purpose

This test family checks whether Vulkan pipeline creation supplies the intended specialization-constant values to graphics and compute shaders, including values that change declarations, expressions, composites, built-ins, and compute local size.

## Background Knowledge

### Pipeline-time constant substitution

A SPIR-V specialization constant receives its value when Vulkan creates a pipeline. `VkSpecializationInfo` maps SPIR-V constant IDs to byte ranges in application data. An entry whose ID the shader does not use has no effect. Each mapped ID must be unique, and an entry size must match the declared constant's size ([Vulkan specialization constants](../../../../vulkan-docs/src/chapters/pipelines.adoc#L9505-L9599)).

Why it matters here:
- The source generates declarations with `constant_id` values and either leaves them at their shader defaults or supplies bytes through `VkSpecializationMapEntry`.
- The tested shader writes the selected value or a result derived from it to a storage buffer, so the host can compare bytes without inferring the value from rendered color.

### Stage-local use and local size

A graphics pipeline needs supporting stages, but only the selected graphics stage declares and consumes the specialization constants. Compute adds `local_size_x_id`, `local_size_y_id`, and `local_size_z_id`, which let pipeline creation choose `gl_WorkGroupSize` ([specialization-constant overview](../../../../vulkan-docs/src/chapters/pipelines.adoc#L9505-L9518)).

## One Concrete Example

The compute `local_size.xyz` test declares three local-size IDs and specializes them to 3, 5, and 7. The shader records `gl_WorkGroupSize` and an atomic count in an SSBO. One dispatch must therefore produce `(3, 5, 7)` and `105`. This case checks both map-entry substitution and the effect of those constants on workgroup execution ([case definition](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1692-L1704)).

## End-to-End Test Flow

```text
[host] select a stage and a CaseDefinition with declarations, optional replacement bytes, SSBO layout, and expected offsets
[host] generate GLSL and compile its stage programs
[host] build VkSpecializationInfo from map entries and data when a case supplies entries
[host] allocate and bind a host-visible SSBO
[host] create the graphics or compute pipeline and attach specialization information to its relevant stage
[device] draw one triangle or dispatch one workgroup; the selected shader writes observed values to the SSBO
[host] synchronize shader writes for host reads, invalidate the allocation, and compare each expected byte range
[host] report failure when any expected offset differs
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`generateSpecConstantCode` replaces `${ID}` in each source declaration. `initPrograms` inserts the resulting declarations, the output-buffer declaration, and case-specific code only in the selected stage. The source creates GLSL for vertex, fragment, tessellation-control, tessellation-evaluation, geometry, or compute and uses SPIR-V 1.3 build options ([generation](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L330-L352), [stage generation](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L355-L513)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Output SSBO | yes | yes, set 0 binding 0 | selected shader writes | yes | Carries raw observed values for byte-for-byte checking. |
| Specialization data and map entries | yes | supplied at pipeline creation | consumed while specialization occurs | no | Selects replacement values and offsets. |
| Graphics color attachment and vertex buffer | yes, graphics only | yes | rasterization uses them | no | Runs the selected graphics stage; validation still uses the SSBO. |

## What Is Checked

`verifyValues` compares each expected `OffsetValue` directly against the host-visible output allocation. The normal families cover default versus supplied scalar values, packed and generic-stride data, built-in replacement, expression and array-size use, and vector, matrix, array, and structure composites. Compute also covers local size, an unaligned hand-authored SPIR-V case, and a same-ID case ([byte verifier](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L217-L238), [registration](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2932-L2994)).

## Behavior Parameter Identification

> **Behavior parameter:** test mechanism
>
> **Candidate values:** `default_value`, `basic`, `builtin`, `expression`, `composite`, `local_size`, `unaligned_spec_constant`, `same_id`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `default_value` | Pipeline creation incorrectly replaces a declaration that has no supplied value, or the selected stage does not preserve its default. |
| `basic` | Map-entry ID, byte offset, byte size, or packed-data handling supplies the wrong scalar value. |
| `builtin` | Built-in specialization constant handling fails for the default or replacement path. |
| `expression` | A specialized value is wrong when consumed by a constant expression, array declaration, or array operation. |
| `composite` | Composite member layout, element mapping, or reconstructed composite value is wrong. |
| `local_size` | The local-size IDs do not specialize `gl_WorkGroupSize` or workgroup execution as expected. |
| `unaligned_spec_constant` | The implementation mishandles the unaligned byte range used by the hand-authored SPIR-V case. |
| `same_id` | The same constant ID does not produce the expected value in each declared use. |

## Important Variations and Special Cases

The five non-monolithic split mustpass lists each contain 1,170 graphics leaves, 234 for each of `vertex`, `fragment`, `tess_control`, `tess_eval`, and `geometry`. The monolithic list contains those 1,170 graphics leaves plus 243 compute leaves, for 1,413 total. Compute-only `local_size`, `unaligned_spec_constant`, and `same_id` therefore do not appear in the five split non-monolithic lists.

Feature flags gate tessellation, geometry, 64-bit integer and floating point, 16-bit integer and floating point, and 8-bit integer cases. The support check also requests the appropriate storage and atomic features for graphics-stage SSBO writes ([support checks](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L832-L860)).

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Specialization-data builder | [`Specialization`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L254-L301) | Creates map entries and chooses packed versus generic-stride offsets. |
| Shader generation | [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L355-L513) | Inserts declarations and output writes into the selected stage. |
| Compute execution | [`ComputeTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L552-L630) | Builds, dispatches, synchronizes, and reads back the compute pipeline. |
| Graphics execution | [`GraphicsTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L665-L830) | Builds, draws, synchronizes, and reads back the graphics pipeline. |
| Family registration | [`createSpecConstantTests`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2932-L2994) | Defines graphics, monolithic compute, and their test mechanisms. |

## Questions / Risk Points for User Audit

- Is the distinction between default declarations and API-supplied replacement data clear?
- Does the SSBO-based result check make the graphics and compute paths understandable?
- Does the failure map separate malformed map-data behavior from use-site behavior?

## Conversion Notes for Final Wiki Rewrite

The final page should retain the mechanism-based behavior axis and copy the failure-cause mapping table unchanged. It should compact the prerequisite explanation, describe generated shaders without a representative shader walkthrough, and keep the local-size `xyz` case as a short execution example rather than embedding generated SPIR-V.
