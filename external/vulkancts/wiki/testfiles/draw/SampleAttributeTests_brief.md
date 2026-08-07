# Understanding Brief: `draw.renderpass.implicit_sample_shading`

## One-Sentence Test Purpose

This test checks whether a fragment shader construct that requires implicit sample shading produces at least one fragment invocation for every covered sample while pipeline sample shading is disabled.

## Background Knowledge

### Implicit sample shading

A multisampled attachment contains several coverage samples for each pixel. Pixel-rate shading can share one fragment invocation across covered samples, whereas sample-rate shading runs the fragment shader separately for each covered sample.

The pipeline can request sample shading explicitly, but Vulkan also defines implicit triggers. Static use of `gl_SampleID` or `gl_SamplePosition` requires sample shading at a rate of 1.0. A dynamically used fragment input decorated with `sample` also requires sample-rate behavior. See [sample shading](https://registry.khronos.org/vulkan/specs/latest/html/chapters/primsrast.html#primsrast-sampleshading).

Why it matters here:
- The test deliberately sets explicit pipeline sample shading off, leaving the shader construct as the only intended trigger.
- Counting shader invocations distinguishes a sample-rate result from a pixel-rate result without relying on a color-image comparison.

### The counter is the observable result

The fragment shader has access to a storage buffer containing one `uint` and calls `atomicAdd` once per invocation. An atomic addition prevents concurrent fragment invocations from overwriting one another.

Why it matters here:
- A 4 × 4 target with four samples per pixel has a lower bound of `4 * 4 * 4 = 64` counted invocations when every sample is shaded.
- The color attachment exists to perform the multisample draw; the host verdict comes from the storage buffer after synchronization and readback.

## One Concrete Example

Consider the `sample_id_static_use` test case leaf. Its generated fragment shader has this essential form (simplified from [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L151-L166)):

```glsl
layout (std430, binding = 0) buffer Output {
    uint invocationCount;
} buf;

void main() {
    gl_SampleID;                 /// static use is the trigger under test
    atomicAdd(buf.invocationCount, 1);
}
```

The source does not use the numeric value of `gl_SampleID`. It checks whether merely statically using the built-in causes the implementation to run this code at least once for every sample. In the actual case, a full-screen triangle covers 16 pixels of a four-sample attachment, so a conforming result is at least 64.

The `sample_decoration_dynamic_use` case uses a different trigger: the vertex shader writes `verify`, and the fragment shader declares `layout (location = 0) sample in float verify`. Its increment is `uint(ceil(verify))`; generated values lie from 0.75 through 1.0, so each invocation still adds 1. The value is dynamically consumed, ensuring that the sample-qualified interface is live.

## End-to-End Test Flow

```text
[host] select one registered trigger: sample decoration, gl_SampleID, or gl_SamplePosition
[host] check fragmentStoresAndAtomics and sampleRateShading; require VK_KHR_dynamic_rendering for dynamic-rendering paths
[host] generate vertex and fragment GLSL specialized for that trigger
[host] allocate and clear a host-visible one-uint storage buffer
[host] create a 4 × 4 four-sample color attachment and bind the storage buffer at fragment binding 0
[host] create a pipeline with sampleShadingEnable = VK_FALSE and minSampleShading = 0.0
[host] record one full-screen triangle draw through a render pass or dynamic rendering
[device] execute fragment shader invocations; each invocation atomically increments the storage-buffer counter
[host] add a fragment-write-to-host-read buffer barrier, submit, wait, invalidate mapped memory, and read the counter
[host] pass when the counter is at least 64; otherwise fail with the observed lower value
```

The dynamic-rendering primary, partial-secondary, and complete-secondary paths alter command-buffer recording only. They retain the same shaders, attachment sample count, counter, and pass condition.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L127-L168) generates GLSL 4.50 vertex and fragment shaders for the chosen `Trigger`.
- The vertex shader constructs a full-screen triangle from constant positions. For `sample_decoration_dynamic_use`, it also exports `verify` at location 0.
- The fragment shader always declares the storage buffer and atomically increments its counter. It conditionally emits `gl_SampleID;`, `gl_SamplePosition;`, or a `sample`-decorated `verify` input.
- Pipeline multisample state is generated with four rasterization samples but with `sampleShadingEnable = VK_FALSE` and `minSampleShading = 0.0` ([`multisampling`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L345-L365)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| One-`uint32_t` host-visible storage buffer | Yes | Yes, fragment binding 0 | Written atomically | Yes | Authoritative invocation-count result. |
| 4 × 4 `VK_FORMAT_R8G8B8A8_UNORM` four-sample color attachment | Yes | Yes | Written by fragment color output | No | Supplies the multisampled rasterization target. |
| `verify` shader interface value | Generated in shader, not a host-created buffer | Passed through stage interface | Written by vertex shader and read by fragment shader only for the sample-decoration leaf | No | Keeps the sample-qualified input dynamically used. |

## What Is Checked

- The expected lower bound is declared as `sampleCount * width * height`, where `sampleCount` is `VK_SAMPLE_COUNT_4_BIT` and width/height are both 4 ([`constants`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L99-L102)).
- After the draw and host visibility steps, the test copies the mapped storage-buffer value to `result`.
- `result < expectedCounter` fails with `Atomic counter value lower than expected: <result>`; every value at least 64 passes ([`result check`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L472-L491)).
- The test proves the required lower bound, not an exact count. It therefore does not infer an error from additional permitted fragment invocations.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf (fragment-shader implicit-sample-shading trigger)
>
> **Candidate values:** `sample_decoration_dynamic_use`, `sample_id_static_use`, `sample_position_static_use`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `sample_decoration_dynamic_use` | Failure to apply sample-qualified interpolation or implicit sample-rate execution; fragment input interface/lowering error; counter or synchronization problem. |
| `sample_id_static_use` | Failure to treat static `gl_SampleID` use as an implicit sample-shading trigger; fragment built-in handling; counter or synchronization problem. |
| `sample_position_static_use` | Failure to treat static `gl_SamplePosition` use as an implicit sample-shading trigger; fragment built-in handling; counter or synchronization problem. |
| Any value | Multisample attachment, pipeline sample state, draw coverage, atomic storage, barrier, or host readback can produce a low counter. |

## Important Variations and Special Cases

- The three trigger leaves share the fixed sample count and counter validation. The shader declaration/use is the intended behavioral difference.
- `sample_decoration_dynamic_use` differs from the two built-in leaves by using a live interface input. The generated `verify` values make `ceil(verify)` equal 1, keeping its counter contribution comparable with the built-in leaves.
- Render-pass and three non-nested dynamic-rendering paths register this family. Nested dynamic-rendering paths do not: [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L101) skips the family whenever `nestedSecondaryCmdBuffer` is true. This is a dispatcher scope decision, not an unsupported-feature result.
- All cases require `fragmentStoresAndAtomics` and `sampleRateShading`; dynamic rendering also requires `VK_KHR_dynamic_rendering` ([`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L113-L125)).

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Trigger variants | [`Trigger` and `TestParameters`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L59-L72) | Defines the selected shader behavior. |
| Feature checks | [`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L113-L125) | Establishes required features and dynamic-rendering gate. |
| Generated shaders | [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L127-L168) | Shows exact trigger constructs and counter increment. |
| Resource and pipeline setup | [`iterate()` setup](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L182-L365) | Creates the counter/attachment and disables explicit pipeline sample shading. |
| Command execution and verdict | [`iterate()` execution](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L390-L491) | Records draw variants, synchronizes readback, and checks the lower bound. |
| Family registration | [`createSampleAttributeTests()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L496-L519) | Registers exact test case leaves. |
| Draw-path dispatcher | [`createChildren()` and `createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L198) | Establishes rendering-path coverage and nested omission. |
| Vulkan semantics | [Sample shading](https://registry.khronos.org/vulkan/specs/latest/html/chapters/primsrast.html#primsrast-sampleshading) | Defines the implicit-trigger behavior. |

## Questions / Risk Points for User Audit

- Is the distinction between explicit pipeline sample shading and shader-triggered implicit sample shading clear?
- Does the counter lower-bound check make clear why the result is `>= 64` rather than equality?
- Are the live `sample` interface path and the static built-in paths described distinctly enough?
- Is the nested dynamic-rendering omission clearly represented as registration scope rather than a semantic limitation?

## Conversion Notes for Final Wiki Rewrite

- Retain the two concise prerequisite bullets on sample shading and sample-related fragment inputs.
- Use the three registered leaves as the final page's behavior parameter values.
- Copy the failure-cause mapping table unchanged into the final page; write detailed cause analysis separately.
- Keep the full-screen triangle, fixed 4 × 4 × 4 lower bound, and disabled pipeline sample-shading state in runtime/result checking rather than Background Knowledge.
