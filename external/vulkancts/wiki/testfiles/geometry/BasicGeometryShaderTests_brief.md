# Understanding Brief: geometry.basic

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation correctly handles geometry shaders that emit fixed, runtime-selected, zero,
large, instanced, or side-effect-only output patterns.

## Background Knowledge

### Geometry-shader output count is observable through raster output

A geometry shader declares `max_vertices`, but each invocation may emit fewer vertices with `EmitVertex()`. The fixed-output
and varying-output cases turn emitted vertex counts into visible triangle-strip arcs or rows in a 256x256 render target.

Why it matters here:
- output counts include zero, small values, and the maximum value `128`;
- the host validates the final rendered image against a reference image named after the test case leaf.

### Runtime count sources test more than the emit loop

The varying-output cases obtain the emitted count from vertex attributes, a uniform buffer, or a sampled texture. Instanced
variants use four geometry-shader invocations for one input point and index the selected count by `gl_InvocationID`.

Why it matters here:
- descriptor setup and shader indexing are part of the tested behavior for uniform and texture variants;
- wrong invocation indexing, resource binding, or sampled-channel handling changes the rendered reference pattern.

### Side effects are checked even when raster output should remain empty

The side-effect cases deliberately write `777u` to a storage buffer from the geometry shader while preventing a visible color
write. They prove that geometry-shader side effects are not discarded just because no fragment output should be produced.

Why it matters here:
- the pass condition combines an SSBO value check with a color-buffer invariance check;
- the cases require `vertexPipelineStoresAndAtomics` in addition to `geometryShader`.

## One Concrete Example

Representative path:

```text
dEQP-VK.geometry.basic.output_vary_by_texture_instancing
```

This case draws one point, but the geometry shader declares `layout(points, invocations=4) in`. The host creates a 4x1 RGBA8
texture with four texels. Each invocation samples one texel coordinate derived from `gl_InvocationID`; the active channel maps
to an emitted vertex count:

| Invocation | Sampled channel | Emitted vertex count | Color used in output |
|------------|-----------------|----------------------|----------------------|
| `0` | red | `6` | red |
| `1` | green | `0` | green, but no vertices emitted |
| `2` | blue | `128` | blue |
| `3` | alpha | `10` | yellow |

Each emitted pair of vertices forms one segment of a triangle strip arc around an invocation-specific base position. The final
image proves that texture sampling, invocation indexing, dynamic loop bounds, and geometry output all agree with the reference.

## End-to-End Test Flow

```text
1. Fixed-output and varying-output render cases
[host] register one leaf per output pattern or runtime count source
[host] generate vertex, geometry, and fragment GLSL for the selected leaf
[host] create the shared render target, vertex buffer, graphics pipeline, and optional descriptor set
[host] upload per-case vertex data, uniform data, or sampled texture data
[host] record one draw using point-list input topology
[device] vertex shader forwards position and either color/count metadata or resource index metadata
[device] geometry shader chooses an emit count and emits triangle-strip vertices, possibly across four invocations
[device] fragment shader writes the forwarded color to the color attachment
[host] copy the rendered image to a host-visible buffer
[host] compare the image with `vulkan/data/geometry/<test-name>.png`

2. Side-effect cases
[host] create a 1x1 color target, vertex buffer, and host-visible storage buffer initialized to zero
[host] bind the storage buffer to the geometry stage and draw one triangle
[device] geometry shader writes `ssbo.value = 777u`
[device] condition or degeneracy prevents visible color output
[host] read the storage buffer and color image
[host] require `ssbo.value == 777u` and require the color image to equal the clear color
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Fixed-output leaves generate a point-input geometry shader with `triangle_strip` output and a `max_vertices` value derived
  from the registered pattern.
- Varying-output leaves generate one of three geometry shaders: attribute-backed, uniform-backed, or texture-backed. Each has
  optional `invocations=4` syntax in instanced cases.
- Side-effect leaves generate GLSL 460 vertex, geometry, and fragment shaders. Their geometry shader contains the SSBO write
  and either a conditional emit path or a degenerate two-vertex triangle-strip path.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Shared render target for image cases | yes | as color attachment | written by fragment shader | yes | Main observable result for fixed and varying output counts. |
| Vertex buffer | yes | yes | read by vertex input | no | Carries positions and either colors, emitted counts, or primitive indices. |
| Uniform buffer | yes, uniform variants only | descriptor set binding `0` | read by geometry shader | no | Supplies the count vector `6, 0, 128, 10`. |
| Sampled texture and sampler | yes, texture variants only | descriptor set binding `0` | sampled by geometry shader | no | Encodes the same count vector through RGBA channels. |
| Side-effect SSBO | yes, side-effect cases only | descriptor set binding `0` | written by geometry shader | yes | Proves geometry-stage storage-buffer side effects are preserved. |
| Side-effect 1x1 color target | yes, side-effect cases only | as color attachment | should not be visibly written | yes | Confirms the side effect is not explained by ordinary raster output. |

## What Is Checked

| Case family | Check |
|-------------|-------|
| Fixed output count | Rendered row/strip pattern matches the reference image for the registered output-count pattern. |
| Varying output count | Rendered arcs match the reference image for counts sourced from attributes, uniforms, or texture channels. |
| Instanced varying output | The same count-source behavior is indexed by `gl_InvocationID` across four geometry invocations. |
| Side effect with condition | SSBO value becomes `777u`, while the color buffer remains at the clear color because the condition is zero. |
| Side effect with degenerate geometry | SSBO value becomes `777u`, while only two emitted vertices prevent a visible triangle. |

## What Failure Means

A failure suggests one of the following implementation problems:

- incorrect geometry-shader `EmitVertex()` loop execution or `max_vertices` handling;
- incorrect handling of zero-output invocations;
- wrong `gl_InvocationID` behavior for geometry-shader instancing;
- descriptor, uniform-buffer, sampled-texture, or channel-selection bugs in the geometry stage;
- missing or incorrectly optimized geometry-stage storage-buffer side effects;
- unexpected raster output from conditional or degenerate geometry paths;
- image comparison mismatch caused by incorrect geometry-shader output positions or fragment colors.

## Important Variations and Special Cases

- Fixed output leaves include single-count cases (`10`, `128`) and two-invocation patterns (`10/100`, `100/10`, `0/128`,
  `128/0`). The two-count patterns use `gl_PrimitiveIDIn` to choose the per-primitive count.
- Varying output leaves all use the canonical counts `6`, `0`, `128`, and `10`, but the source of those counts changes.
- Instanced varying-output leaves collapse the input draw to one point and use four geometry invocations instead of four input
  vertices.
- Side-effect leaves are not image-reference variants. They use a storage buffer and an exact color-buffer comparison to prove
  that side effects and raster output are evaluated independently.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test family registration | [createBasicGeometryShaderTests()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L1000-L1047) | Lists the exact `geometry.basic` test case leaves. |
| Fixed-output shader generator | [GeometryOutputCountTest::initPrograms()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L475-L542) | Generates the fixed-pattern geometry shader and fragment shader. |
| Varying-output resource setup | [VaryingOutputCountTestInstance](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L184-L391) | Creates uniform/texture descriptors and vertex data for varying count sources. |
| Varying-output shader generator | [VaryingOutputCountCase::initPrograms()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L577-L764) | Generates attribute, uniform, and texture geometry-shader variants. |
| Shared render execution | [GeometryExpanderRenderTestInstance::iterate()](../../../modules/vulkan/geometry/vktGeometryBasicClass.cpp#L71-L203) | Describes the common render, copyback, and image comparison path. |
| Side-effect shaders | [sideEffectInitPrograms()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L803-L866) | Generates SSBO-writing geometry shaders. |
| Side-effect validation | [sideEffectTest()](../../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp#L868-L996) | Checks the SSBO sentinel and unchanged color buffer. |

## Questions / Risk Points for User Audit

- The final page should explain that `geometry.basic` is one test family with several direct test case leaves, not separate
  intermediate nodes.
- The shader walkthrough should use one representative varying-output path and summarize fixed-output and side-effect shader
  differences instead of adding three full walkthroughs.
- The side-effect cases should not be described as normal image-reference tests.

## Conversion Notes for Final Wiki Rewrite

- Preserve the three behavioral groups: fixed output counts, runtime-varying output counts, and side-effect-only output.
- Use `output_vary_by_texture_instancing` as the representative shader walkthrough because it covers descriptors, texture
  sampling, `gl_InvocationID`, and the maximum `128` emit count.
- Keep the shared render path concise and link to `GeometryExpanderRenderTestInstance::iterate()` for evidence.
- Put the registration inventory and source mapping in concise tables; avoid copying this brief's learning scaffolding verbatim.
