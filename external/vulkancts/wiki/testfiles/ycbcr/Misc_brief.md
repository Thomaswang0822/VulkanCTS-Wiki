# Understanding Brief: `ycbcr.misc.relaxed_precision`

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation can create and execute a fragment pipeline that applies `RelaxedPrecision` to sampling from a multi-planar image through a sampler YCbCr conversion.

## Background Knowledge

### `RelaxedPrecision` on image sampling

`RelaxedPrecision` permits reduced precision for decorated SPIR-V results and objects. Vulkan's standalone SPIR-V rules allow the decoration on an image-sampling instruction and on a variable that holds its result. The test places the decoration on both sampling paths, their sampled-image loads, the function-local value, and the fragment output.

Why it matters here:
- The fragment shader combines `RelaxedPrecision` with `OpImageSampleImplicitLod` and `OpImageSampleProjImplicitLod`.
- The implementation must accept and execute this decorated dataflow without rejecting or mishandling the pipeline.

### Sampler YCbCr conversion binding

A sampler YCbCr conversion interprets a multi-planar image through conversion parameters attached to both the sampler and image view. Vulkan fixes this conversion at pipeline creation through a combined image sampler that uses an immutable sampler.

Why it matters here:
- The sampled image uses `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM`.
- Descriptor set 0, binding 0 combines the converted image view with the immutable sampler used by the direct SPIR-V fragment shader.

## One Concrete Example

The only registered case is `dEQP-VK.ycbcr.misc.relaxed_precision`. Its fragment shader performs two samples from the same converted image:

```text
sample A = OpImageSampleImplicitLod(t, (0, 0))
sample B = OpImageSampleProjImplicitLod(t, (1, 1, 1))
fragment output = sample A * sample B
```

The source decorates both sample results and the multiplication result with `RelaxedPrecision`. It also decorates the sampled-image variable, sampled-image loads, function-local value, and output.

## End-to-End Test Flow

```text
[host] require VK_KHR_sampler_ycbcr_conversion
[host] register a generated vertex shader and CTS-authored fragment SPIR-V assembly
[host] create a 256x256 three-plane 4:2:0 image and an RGB-identity/full-range YCbCr conversion
[host] create the converted image view, immutable sampler, and combined-image-sampler descriptor
[host] create a 256x256 R8G8B8A8_UNORM color attachment and graphics pipeline
[host] transition the sampled image to SHADER_READ_ONLY_OPTIMAL
[host] begin a render pass, bind the descriptor and pipeline, and draw four triangle-strip vertices
[device] execute both relaxed-precision sample operations and multiply their results
[host] wait for queue completion
[host] pass if setup, pipeline creation, submission, and execution complete without an error
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms()` generates a vertex shader in GLSL 4.50. It derives a fullscreen triangle-strip position from `gl_VertexIndex`; its `texCoord` output is not consumed by the fragment entry-point interface.
- The same function supplies the fragment stage as CTS-authored SPIR-V assembly. This artifact contains the exact `RelaxedPrecision` decorations and image instructions under test.
- The ordinary source-collection baseline makes the direct assembly a SPIR-V 1.0 artifact.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Three-plane sampled image | yes | yes | read | no | Supplies the `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM` source for both fragment samples. |
| YCbCr conversion, sampler, and image view | yes | yes | used during sampling | no | Applies RGB identity, full range, cosited chroma locations, and nearest filtering. |
| Combined image sampler at set 0, binding 0 | yes | yes | read | no | Matches the fragment shader's sole `UniformConstant` variable. |
| `R8G8B8A8_UNORM` color attachment | yes | yes | written | no | Receives the multiplication result so the decorated fragment dataflow reaches an output. |

## What Is Checked

- The test has no pixel comparison, result copy, or host readback.
- It checks that the implementation accepts the direct SPIR-V fragment shader, creates the graphics pipeline, executes a draw that uses the converted multi-planar image, and completes the queue submission.
- `iterate()` returns `pass("Pass")` after `submitCommandsAndWait()` completes. A wrong but executable color value is outside this test's observable pass condition.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `relaxed_precision`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `relaxed_precision` | The implementation rejected or failed to execute the decorated SPIR-V sampling dataflow, the sampler YCbCr conversion setup, or the associated graphics pipeline and draw. |

## Important Variations and Special Cases

- The test family has one fixed case. It does not generate a parameter matrix.
- Both sampling forms appear in one fragment shader: ordinary implicit-LOD sampling at `(0,0)` and projective implicit-LOD sampling at homogeneous coordinate `(1,1,1)`.
- The image receives no uploaded texel data. This is acceptable because the test checks successful handling and execution, not a sampled color.
- The image barrier uses `VK_ACCESS_TRANSFER_WRITE_BIT` as the source access despite no preceding transfer command. Its essential role in this flow is the layout transition to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` before fragment sampling.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Resource, descriptor, and pipeline setup | [`RelaxedPrecisionTestInstance::iterate()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L60-L252) | Defines the fixed image, conversion, immutable sampler, descriptor, attachment, and pipeline. |
| Draw and pass condition | [Command recording and return](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L254-L275) | Shows the transition, four-vertex draw, queue wait, and unconditional pass after completion. |
| Feature requirement | [`RelaxedPrecisionTestCase::checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L294-L297) | Requires `VK_KHR_sampler_ycbcr_conversion`. |
| Shader artifacts | [`RelaxedPrecisionTestCase::initPrograms()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L299-L364) | Generates the vertex GLSL and direct fragment SPIR-V assembly. |
| Registration | [`createMiscTests()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L366-L373) | Registers the sole `relaxed_precision` leaf. |
| Mustpass entry | [`dEQP-VK.ycbcr.misc.relaxed_precision`](../../../mustpass/main/vk-default/ycbcr.txt#L59409) | Confirms the executable path in the default mustpass list. |
| Sampler YCbCr conversion rules | [Sampler YCbCr Conversion](../../../../vulkan-docs/src/chapters/samplers.adoc#L773-L801) | Grounds the immutable combined-image-sampler setup and conversion attachment. |
| SPIR-V image and precision rule | [Standalone SPIR-V image type rule](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L322-L329) | States that `RelaxedPrecision` can decorate a sampling instruction and the variable holding its result. |

## Questions / Risk Points for User Audit

- [x] The pass condition is execution-only; source inspection found no output comparison or readback.
- [x] The representative walkthrough should preserve the CTS-authored fragment assembly rather than reconstruct GLSL or HLSL.
- [x] The test purpose should remain limited to successful handling of decorated YCbCr sampling. It must not claim that the rendered color is checked.
- [x] The single test case leaf is the only defensible behavior parameter value.

## Conversion Notes for Final Wiki Rewrite

- Keep `RelaxedPrecision` and immutable sampler YCbCr conversion as the two prerequisites.
- Use `relaxed_precision` as the single behavior value and copy the Failure Cause Mapping table unchanged.
- Include one direct-SPIR-V fragment walkthrough. The vertex shader is fixed setup and does not participate in the tested property.
- Preserve the execution-only validation limitation in the runtime, failure, and takeaway sections.
- Move line-oriented evidence to the source appendix.
