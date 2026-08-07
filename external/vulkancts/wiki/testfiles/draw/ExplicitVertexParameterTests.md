## Overview

**Core question:** Does `VK_AMD_shader_explicit_vertex_parameter` let a fragment shader reconstruct the same interpolated value as Vulkan's standard interpolation path?

- The [`explicit_vertex_parameter`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L764-L768) test family generates smooth and noperspective cases, with no auxiliary qualifier or with `sample`/`centroid`. Render-pass and primary-command-buffer paths generate sample counts 1 through 64; secondary-command-buffer paths are pruned to 1, 2, and 4.
- The vertex shader exports one value through `__explicitInterpAMD` and a second copy through the selected ordinary interpolation qualifier. The fragment shader fetches the first copy at each primitive vertex with `interpolateAtVertexAMD`, combines those values with the matching `gl_BaryCoord*AMD` coordinates, and compares the result with the ordinary input.
- The host reads the per-fragment expected/computed pairs from a storage buffer. The family is registered below the draw category's render-pass path and, when supported, each dynamic-rendering command-buffer path.

## Background Knowledge

- **Shader-stage interfaces:** Vertex outputs and fragment inputs form a user-defined interface matched by location and compatible decorations. This test deliberately carries two separately located values so one uses explicit vertex interpolation while the other supplies the comparison value. See [Shader Input and Output Interfaces](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-iointerfaces).
- **Barycentric interpolation:** A fragment's value over a triangle can be reconstructed from the three vertex values and barycentric coordinates. Smooth coordinates account for perspective; noperspective coordinates do not. `sample` and `centroid` select different sampling locations for the ordinary interpolated input and its corresponding AMD barycentric built-in.
- **Multisampling:** `gl_SampleID` distinguishes the storage-buffer result slot for each sample. The family requires the core `sampleRateShading` feature for every case, including sample-count-1 and non-`sample` branches; the pipeline itself leaves `sampleShadingEnable` false, while the fragment shader's use of `gl_SampleID` makes sample identity observable.

## Registration Hierarchy

The dispatcher adds this test family to the render-pass path and to the three non-nested dynamic-rendering paths. Nested secondary-command-buffer variants intentionally omit this family because the dispatcher stops after the `basic` family for nested variants.

```text
draw.renderpass
└── explicit_vertex_parameter
```

```text
draw.dynamic_rendering.primary_cmd_buff
└── explicit_vertex_parameter
```

```text
draw.dynamic_rendering.partial_secondary_cmd_buff
└── explicit_vertex_parameter
```

```text
draw.dynamic_rendering.complete_secondary_cmd_buff
└── explicit_vertex_parameter
```

Within each applicable `explicit_vertex_parameter` test family, the direct behavior branches are:

```text
explicit_vertex_parameter
├── smooth_samples_<count>
├── noperspective_samples_<count>
├── smooth_sample_samples_<count>
├── noperspective_sample_samples_<count>
├── smooth_centroid_samples_<count>
└── noperspective_centroid_samples_<count>
```

The family is attached by [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L120), and its branches are created by [`createTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L727-L760).

The generated default mustpass lists confirm 38 render-pass cases and 38 primary-command-buffer cases. Each secondary-command-buffer path contains 14 cases because it retains only sample counts 1, 2, and 4. Vulkan SC has only the 38 render-pass cases. See the [`vk-default` draw list](../../../mustpass/main/vk-default/draw.txt) and [`vksc-default` draw list](../../../mustpass/main/vksc-default/draw.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Interpolation | `smooth`, `noperspective` | Selects both the ordinary comparison qualifier and the matching AMD barycentric coordinate family. | [`Interpolation`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L62-L66), [`getTestName()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L166-L177) |
| Auxiliary qualifier | none, `sample`, `centroid` | Changes the sampling rule for the ordinary input and selects `gl_BaryCoord*SampleAMD` or `gl_BaryCoord*CentroidAMD`. | [`AuxiliaryQualifier`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L68-L73), [`barycentricVariableString()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L115-L146) |
| Sample count | Render pass/primary: `1`, `2`, `4`, `8`, `16`, `32`, `64`; secondary: `1`, `2`, `4` | Controls multisample attachments and the number of result values per pixel. | [`samples[]` and secondary pruning](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L731-L748) |
| Rendering path | `renderpass`; dynamic rendering `primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff` | Reuses the same interpolation matrix with different rendering and command-buffer recording. | [`createTests()` dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) |
| Render target | 16 × 16 pixels, `VK_FORMAT_R8G8B8A8_UNORM` | Bounds the color target and storage-buffer indexing workload. | [`WIDTH`/`HEIGHT`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L75-L79), image creation [`#L356-L379`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L356-L379) |

## Behavior Parameters

The primary behavioral axis is the interpolation/auxiliary branch. Sample count is an orthogonal coverage dimension and is explained in the matrix above.

### `smooth`: perspective-correct reconstruction

The ordinary input uses `smooth`; the explicit path uses `gl_BaryCoordSmoothAMD`, `gl_BaryCoordSmoothSampleAMD`, or `gl_BaryCoordSmoothCentroidAMD`. The fragment shader's weighted sum must agree with standard perspective-correct interpolation.

### `noperspective`: screen-space reconstruction

The ordinary input uses `noperspective`; the explicit path uses the matching `gl_BaryCoordNoPersp*AMD` built-in. Agreement here checks that the explicit coordinates and vertex fetch follow the non-perspective interpolation rule.

### `sample` and `centroid`: auxiliary sampling

These branches apply the auxiliary qualifier to the ordinary input and use the corresponding AMD barycentric variable. They are only registered for sample counts at least 2, where the qualifier can distinguish sampling behavior.

## Shader Analysis

The generated shaders are the core of this family. [`initPrograms()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L257-L331) specializes the same templates for each matrix value:

- The vertex shader writes `out_data_explicit` with `__explicitInterpAMD` and writes `out_data_smooth` or `out_data_noperspective` at separate locations with the selected auxiliary qualifier.
- The fragment shader reads `in_data_explicit` and the ordinary comparison input. It calls `interpolateAtVertexAMD(in_data_explicit, 0/1/2)`, arranges the three fetched values as `data1`, `data2`, `data0`, and computes `bary_coord.x * data.x + bary_coord.y * data.y + bary_coord.z * data.z`.
- `gl_FragCoord` and `gl_SampleID` determine the result slot; the selected AMD barycentric built-in determines the reconstructed value. The shader stores `vec4(expected, res, 0u, 0u)` and emits green when the difference is strictly below `0.0005`, otherwise red. The color attachment is never read for the verdict; only the storage buffer is checked by the host.

The input vertices use four positions with differing clip-space `z` and `w` values and values `1.0`, `0.0`, `0.5`, and `1.0`, so the strip's two triangles exercise perspective-sensitive interpolation rather than a constant or degenerate value. See [`PositionValueVertex` initialization](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L427-L449).

## Runtime Execution and Result Checking

- Support checking requires `VK_AMD_shader_explicit_vertex_parameter`, a supported framebuffer color sample count, and the core `sampleRateShading` feature. Dynamic-rendering variants additionally require `VK_KHR_dynamic_rendering`; unsupported combinations are reported as unsupported. See [`checkSupport()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L244-L255).
- The instance creates a single-sample color image and, for multisample cases, a multisample color image plus resolve attachment. It also creates a host-visible vertex buffer and host-visible storage buffer, binds the latter at descriptor binding 0, and builds a graphics pipeline using `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`.
- The command path records either a render pass or dynamic rendering. Secondary-buffer variants record the draw in a secondary command buffer and execute it from a primary buffer; the complete variant contains the dynamic-rendering scope in the secondary buffer.
- A four-vertex triangle strip is drawn into the 16 × 16 target. After `submitCommandsAndWait`, the host invalidates the storage-buffer allocation and checks every `WIDTH * HEIGHT * samples` entry. Any `abs(expected - computed) > 0.0005` changes the result to fail. See [`iterate()` readback](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L606-L627).

### Verdict limitations visible in the source

- The SSBO is initialized to zero, and an untouched entry therefore contains `(expected, computed) = (0, 0)` and passes. The check detects disagreement in shader-written entries, but by itself does not prove that every intended pixel/sample invocation wrote an entry.
- The host uses `> 0.0005`, whereas the shader color uses `< 0.0005`; a difference exactly equal to the threshold passes host verification but produces red. Because the color attachment is not read back, the host rule is the effective pass/fail rule.
- A NaN in either stored component also does not satisfy the host's `> 0.0005` condition under ordinary floating-point comparison. Thus the readback predicate is specifically a finite-difference check, not a comprehensive validation of stored numeric values.
- The fragment block is declared with `WIDTH * HEIGHT * samples * samples` elements because the already sample-scaled `numValues` is multiplied by `samples` again during template substitution ([shader specialization](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L257-L327)). The backing buffer and all actual indices use only `WIDTH * HEIGHT * samples`; the extra declared range is not accessed by this shader.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `smooth` | Incorrect smooth AMD barycentric coordinates, explicit vertex fetch, perspective handling, or ordinary interface interpolation. |
| `noperspective` | Incorrect non-perspective AMD barycentric coordinates, explicit vertex fetch, or ordinary interface interpolation. |
| `sample` | Incorrect sample-qualified interpolation/barycentric behavior, sample identification, or sample-rate execution. |
| `centroid` | Incorrect centroid-qualified interpolation/barycentric behavior or mismatch between the two sampling paths. |
| Any sample count | Multisample attachment/resolve setup, per-sample indexing, pipeline sample state, or host readback can make otherwise-correct shader results fail. |

### Cause Analysis

#### Explicit and ordinary interpolation disagree

**Possible failure symptoms:** One or more storage-buffer entries have expected and computed values differing by more than `0.0005`; the corresponding shader color is red.

**Possible implementation causes:** The implementation may produce inconsistent interpolation decorations between the vertex and fragment stages, lower `interpolateAtVertexAMD` incorrectly, or calculate the selected smooth/non-perspective barycentric coordinates incorrectly. The source and Vulkan interface rules establish the compared paths, but a more specific fault location requires implementation investigation.

#### Sample or centroid behavior disagrees

**Possible failure symptoms:** Only `sample` or `centroid` branches, or only particular sample IDs, show mismatched expected/computed pairs.

**Possible implementation causes:** The implementation may use the wrong interpolation sampling location, mishandle the AMD `SampleAMD`/`CentroidAMD` coordinate variant, or fail to execute the sample-qualified input at sample rate. The test source supports these hypotheses; it does not identify which implementation component is responsible.

#### Multisample setup or result indexing fails

**Possible failure symptoms:** Failures correlate with sample counts greater than one, with wrong or missing entries in the storage buffer.

**Possible implementation causes:** The multisample attachment, resolve path, sample state, `gl_SampleID`-based index, command-buffer rendering arrangement, or host-visible buffer handling may be incorrect. Source-level investigation is needed to distinguish these causes.

## Case Pruning

### Requirement-based pruning

- `sample` and `centroid` cases are not registered for `VK_SAMPLE_COUNT_1_BIT`, because the source treats those qualifiers as ineffective for a single sample ([`createTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L744-L758)).
- A requested sample count is skipped as unsupported when it is absent from `framebufferColorSampleCounts` ([`checkSupport()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L244-L250)).
- Dynamic-rendering cases require `VK_KHR_dynamic_rendering`, and all cases require `VK_AMD_shader_explicit_vertex_parameter` and sample-rate shading.

### Design-based pruning

- Secondary-command-buffer dynamic-rendering variants keep only sample counts 1, 2, and 4 to control the generated test count ([`createTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L744-L748)).
- Nested secondary variants are omitted at category registration time because `vktDrawTests.cpp` intentionally registers only `basic` for nested modes. This is a dispatcher design boundary, not evidence that explicit vertex parameters are unsupported there.

## Key Takeaways

- The family compares two independent shader paths: ordinary interpolation and explicit per-vertex fetch plus AMD barycentric reconstruction.
- `smooth` and `noperspective` test different interpolation mathematics; `sample` and `centroid` add sampling-location variants.
- The effective verdict is a host-side `abs(expected - computed) > 0.0005` check over every allocated storage-buffer entry, with the untouched-entry and NaN limitations described above.
- Render-pass and non-nested dynamic-rendering command-buffer arrangements reuse the same behavioral matrix, while nested dynamic-rendering paths intentionally do not register this family.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test-family factory | [`createExplicitVertexParameterTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L764-L768) | Registers `explicit_vertex_parameter`. |
| Case generator | [`createTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L727-L760) | Defines interpolation, auxiliary, sample-count, and pruning matrix. |
| Support gate | [`DrawTestCase::checkSupport()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L244-L255) | Defines required extension, feature, sample-count, and dynamic-rendering support. |
| Shader generation | [`DrawTestCase::initPrograms()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L257-L331) | Generates the compared vertex/fragment shader paths. |
| Host execution and verdict | [`DrawTestInstance::iterate()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L338-L627) | Creates resources, records rendering, reads results, and applies tolerance. |
| Draw dispatcher | [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L120) | Establishes variant coverage and nested-mode omission. |
| Default mustpass coverage | [`vk-default/draw.txt`](../../../mustpass/main/vk-default/draw.txt) | Confirms 104 Vulkan cases: 38 render-pass, 38 primary, and 14 per secondary path. |
| Vulkan SC mustpass coverage | [`vksc-default/draw.txt`](../../../mustpass/main/vksc-default/draw.txt) | Confirms the 38 render-pass-only Vulkan SC cases. |
| AMD shader semantics | [`VK_AMD_shader_explicit_vertex_parameter`](https://registry.khronos.org/vulkan/specs/latest/html/appendices.html#VK_AMD_shader_explicit_vertex_parameter) | Connects Vulkan support to the AMD SPIR-V explicit-vertex-parameter extension. |
| Vulkan interface semantics | [Shader Input and Output Interfaces](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-iointerfaces) | Background for stage interface matching. |
| Understanding Brief | [ExplicitVertexParameterTests_brief.md](ExplicitVertexParameterTests_brief.md) | Learning-oriented analysis and source mapping. |
