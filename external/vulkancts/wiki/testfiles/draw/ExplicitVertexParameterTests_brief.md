# Understanding Brief: Explicit Vertex Parameter Tests

## One-Sentence Test Purpose

This test checks whether `VK_AMD_shader_explicit_vertex_parameter` produces explicit per-vertex interpolation results that agree with ordinary smooth, noperspective, sample-qualified, and centroid-qualified interpolation.

## Background Knowledge

### Shader interpolation and stage interfaces

A vertex shader output becomes a fragment shader input through the graphics shader interface. Interpolation decorations determine how values vary across a primitive. `smooth` applies perspective correction, while `noperspective` interpolates in screen space. Auxiliary `sample` and `centroid` qualifiers select different fragment sampling locations.

### AMD explicit vertex parameters

The extension adds `__explicitInterpAMD` and `interpolateAtVertexAMD`. The explicit input is not read as the already-interpolated fragment value: the fragment shader requests the value at vertex indices 0, 1, and 2, then combines those values with the appropriate AMD barycentric coordinate built-in. This test uses that reconstructed value as an independent check against an ordinary interpolated input.

Why it matters here:
- The ordinary and explicit paths must use matching interpolation semantics.
- Perspective and non-perspective paths require different barycentric coordinate families.
- Sample and centroid variants matter only when multisampling provides distinct sample locations.

## One Concrete Example

For a representative `smooth_samples_2` case, the generated interface is conceptually:

```glsl
layout(location = 0) __explicitInterpAMD out float out_data_explicit;
layout(location = 1) smooth out float out_data_smooth;
```

The fragment shader obtains three vertex values from `in_data_explicit`, reads `gl_BaryCoordSmoothAMD`, forms `(I, J, K)`, and calculates `I*data1 + J*data2 + K*data0`. It compares that result with `in_data_smooth`. The code above is a shortened faithful illustration; the exact generated templates are in [`initPrograms()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L257-L331).

## End-to-End Test Flow

```text
[host] choose interpolation, auxiliary qualifier, sample count, and rendering variant
[host] require VK_AMD_shader_explicit_vertex_parameter, sample-rate shading, and supported samples
[host] generate specialized vertex and fragment GLSL
[host] create images, vertex buffer, storage buffer, descriptors, and pipeline
[host] record render-pass or dynamic-rendering draw commands
[device] rasterize a four-vertex triangle strip and execute both interpolation paths
[device] write expected/computed pairs to the storage buffer and color pass/fail feedback
[host] wait for completion, invalidate the storage-buffer allocation, and inspect every pair
[host] pass only when every absolute difference is at most 0.0005
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms()` specializes a vertex and fragment GLSL template for `smooth` or `noperspective`, `none`/`sample`/`centroid`, and the selected sample count. Both shaders require `GL_AMD_shader_explicit_vertex_parameter`. The fragment template allocates `vec4 values[WIDTH * HEIGHT * samples]` in a write-only std140 storage block and uses `gl_SampleID` in its index.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Vertex buffer | yes | vertex input | read | no | Supplies four clip-space positions and scalar values. |
| Color image(s) | yes | color attachment | written | no | Receives shader green/red feedback; multisample cases also use a resolve image. |
| Storage buffer | yes | descriptor set binding 0 | fragment writes | yes | Stores expected and reconstructed values for the authoritative verdict. |
| Descriptor set/layout | yes | pipeline binding | selects storage buffer | no | Makes the result buffer visible to the fragment shader. |

The four vertices have clip-space positions with different `z`/`w` values and scalar data `1.0`, `0.0`, `0.5`, and `1.0`; they form a triangle strip over the 16×16 target. See [`PositionValueVertex` data](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L427-L449).

## What Is Checked

- The fragment shader writes `vec4(expected, res, 0u, 0u)` for each pixel/sample.
- The host checks `abs(ptr[valueNdx].x() - ptr[valueNdx].y()) <= 0.0005` for all `16 * 16 * samples` entries.
- The color output is green for shader differences below the same threshold and red otherwise, but the host storage-buffer scan determines pass/fail.
- Unsupported extension, feature, dynamic-rendering, or sample-count requirements produce `NotSupportedError` rather than a failed comparison.

## Behavior Parameter Identification

> **Behavior parameter:** interpolation branch (including auxiliary sampling mode)
>
> **Candidate values:** `smooth`, `noperspective`, `sample`, `centroid`

Sample count is an orthogonal coverage dimension. The source registers names combining both axes, for example `smooth_sample_samples_4` and `noperspective_centroid_samples_8`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `smooth` | Incorrect smooth AMD barycentric coordinates, explicit vertex fetch, perspective handling, or ordinary interface interpolation. |
| `noperspective` | Incorrect non-perspective AMD barycentric coordinates, explicit vertex fetch, or ordinary interface interpolation. |
| `sample` | Incorrect sample-qualified interpolation/barycentric behavior, sample identification, or sample-rate execution. |
| `centroid` | Incorrect centroid-qualified interpolation/barycentric behavior or mismatch between the two sampling paths. |
| Any sample count | Multisample attachment/resolve setup, per-sample indexing, pipeline sample state, or host readback can make otherwise-correct shader results fail. |

## Important Variations and Special Cases

- `sample` and `centroid` are omitted for sample count 1 because the source treats those qualifiers as ineffective there.
- For dynamic rendering with a secondary command buffer, the source keeps only sample counts 1, 2, and 4 to limit the matrix.
- The same family is available under render-pass and non-nested dynamic-rendering variants. Nested secondary-command-buffer variants intentionally register only `basic` in the dispatcher.
- Multisample dynamic rendering uses a multisample color attachment and average resolve into the single-sample color image; render-pass cases create the corresponding attachments and framebuffer.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Registration factory | [`createExplicitVertexParameterTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L764-L768) | Creates the exact `explicit_vertex_parameter` test family. |
| Matrix and pruning | [`createTests()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L727-L760) | Defines interpolation, auxiliary, sample-count, and secondary-buffer coverage. |
| Support requirements | [`checkSupport()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L244-L255) | Requires the extension, sample support, dynamic rendering where needed, and sample-rate shading. |
| Shader templates | [`initPrograms()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L257-L331) | Generates the explicit and ordinary interpolation paths. |
| Resources and draw | [`iterate()`](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L338-L607) | Creates images/buffers/pipeline and submits the selected rendering path. |
| Verdict | [`iterate()` readback](../../../modules/vulkan/draw/vktDrawExplicitVertexParameterTests.cpp#L609-L627) | Compares every expected/computed pair with tolerance 0.0005. |
| Variant registration | [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L120) | Shows non-nested coverage and nested-mode omission. |
| Mustpass evidence | [`vk-default/draw.txt`](../../../mustpass/main/vk-default/draw.txt#L439-L452) | Lists dynamic secondary variants and their reduced sample matrix. |
| Vulkan interface semantics | [Shader Input and Output Interfaces](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-iointerfaces) | Grounds the stage-interface explanation. |

## Questions / Risk Points for User Audit

- Is the distinction between the ordinary comparison input and the `__explicitInterpAMD` input clear?
- Should the final page include a full generated shader walkthrough, or is the concise source-grounded explanation sufficient?
- Are the sample-rate and centroid variations explained without implying that the host directly validates the color image?

## Conversion Notes for Final Wiki Rewrite

- Keep `Background Knowledge` to the three prerequisite concepts; move the concrete example into `Shader Analysis` or a short prose example.
- Preserve the exact behavior-parameter mapping table in the final page's `Failure Meaning` section.
- Keep the source appendix focused on the factory, matrix, shader generation, runtime verdict, dispatcher, and mustpass evidence.
- Do not copy this brief's review questions into the user-facing page.
