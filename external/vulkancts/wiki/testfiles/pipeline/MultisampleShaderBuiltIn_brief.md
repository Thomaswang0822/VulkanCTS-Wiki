# Understanding Brief: MultisampleShaderBuiltIn

## One-Sentence Test Purpose

This test checks whether fragment shaders observe and write multisample built-ins correctly, including sample identity, sample locations, coverage masks, and per-sample image results.

## Background Knowledge

A multisampled image stores a separate value for each sample in a pixel. A fragment shader can identify the current sample with `gl_SampleID`, obtain its location with `gl_SamplePosition`, read coverage through `gl_SampleMaskIn`, and contribute coverage through `gl_SampleMaskOut`. The Vulkan specification describes these built-ins in [SampleId](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-sampleid) and [SampleMask](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-samplemask). Sample positions and sample coverage affect which per-sample values survive rasterization and resolve operations.

The host can also provide a pipeline sample mask through `VkPipelineMultisampleStateCreateInfo::pSampleMask`. A shader output sample mask is combined with generated coverage, while an input sample mask exposes the coverage that reaches the invocation. See [Sample Mask](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-samplemask) and [Sample Mask Accesses](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-shader-samplemask).

## One Concrete Example

In `sample_id`, the fragment shader writes `float(gl_SampleID) / 255` to the red channel. The test fetches the multisampled image without resolving it and checks sample N at every pixel against N. This makes a wrong sample index visible even when all samples cover the same primitive.

## End-to-End Test Flow

```text
[host] select an image size, sample count, and pipeline construction type
[host] check sample-rate shading, pipeline-construction, image-format, and image-limit support
[host] create a multisampled color image, a single-sample resolve image when needed, a render pass or compute target, and readback storage
[host] compile the generated vertex, fragment, and compute shader programs
[host] draw or dispatch work that reads or writes the multisample built-ins
[device] execute per-sample fragment invocations or compute image operations
[device] write per-sample values, a resolved color image, or a storage-image/readback-buffer result
[host] copy or fetch results, invalidate host-visible allocations, and compare them with the case-specific expectation
[host] report a failure when any sample, position, mask bit, or image value differs
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The common cases generate GLSL vertex and fragment shaders in the implementation file. The shaders encode sample IDs or positions into color channels, inspect `gl_SampleMaskIn`, or assign `gl_SampleMaskOut`. See [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L343-L376) and the sample-mask shader builders at [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L814-L1180).
- `image_write_sample` generates compute shaders that use `gl_SampleID` with multisample storage images. Its support check requires `shaderStorageImageMultisample` ([`WriteSampleTest::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1302-L1321)).
- `write_sample_mask` uses a fragment shader that writes `gl_SampleMask`, then a second subpass reads the per-sample result through an input attachment ([`WriteSampleMaskTestCase::initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1711-L1781)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Multisampled `VK_FORMAT_R8G8B8A8_UNORM` color image | yes | color attachment or storage image | yes | yes | Holds the per-sample built-in result. |
| Single-sample resolve image | yes | resolve attachment | yes | yes | Exposes resolved sample-position or sample-mask behavior. |
| Input attachment | yes | fragment descriptor/input attachment | read | no | Lets the second subpass inspect per-sample mask output. |
| Host-visible buffer | yes | transfer destination or storage buffer | written | yes | Supplies the host-side comparison data. |
| Vertex buffer | yes | vertex input | read | no | Covers the render target so the fragment tests run across the image. |

## What Is Checked

- `sample_id` checks that each fetched sample contains its own index.
- `sample_position.distribution` checks legal, unique positions and checks the average position against the implementation's uniformity threshold.
- `sample_position.correctness` checks that an interpolated screen-space value has the expected fractional part at `gl_SamplePosition`.
- `sample_mask.pattern`, `bit_count`, `bit_count_0_5`, and `correct_bit` compare input mask values with pipeline coverage and sample invocation state.
- `sample_mask.write` and `write_sample_mask` compare the output mask effect with expected per-sample coverage.
- `image_write_sample` checks that each compute invocation writes the expected sample in a multisample storage image.

## Behavior Parameter Identification

> **Behavior parameter:** test family and intermediate test case node
>
> **Candidate values:** `sample_id`, `sample_position`, `sample_mask`, `image_write_sample`, `write_sample_mask`; under `sample_position`: `distribution`, `correctness`; under `sample_mask`: `pattern`, `bit_count`, `bit_count_0_5`, `correct_bit`, `write`

These registered families select different built-in contracts and comparison paths. Image size, sample count, and pipeline construction type change the matrix around that contract. The registration code constructs the family and leaf hierarchy in [`createMultisampleShaderBuiltInTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2228-L2326).

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sample_id` | Incorrect sample invocation identity or per-sample fetch/index handling. |
| `sample_position` | Incorrect sample coordinates, interpolation at sample locations, or resolve/readback handling. |
| `sample_mask` | Incorrect input coverage mask, sample-count interpretation, shading-rate handling, or output-mask application. |
| `image_write_sample` | Incorrect storage-image sample addressing or multisample image write behavior. |
| `write_sample_mask` | Incorrect shader output mask combination, subpass input-attachment visibility, or per-sample readback. |

## Important Variations and Special Cases

- Common image-based families use 128x128 and 137x191 images. `sample_id` and `sample_position` use 2, 4, 8, 16, 32, and 64 samples. The sample-mask families use 2, 4, 8, 16, and 32 samples.
- `image_write_sample` runs only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` and uses 2, 4, 8, and 16 samples.
- `write_sample_mask` runs for the construction types registered by the pipeline category and uses 1, 2, 4, 8, and 16 samples.
- The common cases require `sampleRateShading`. The storage-image case additionally requires `shaderStorageImageMultisample`. The relevant cases check graphics pipeline library support through the shared multisample base.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Family and leaf registration | [`createMultisampleShaderBuiltInTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L2228-L2326) | Defines the hierarchy, dimensions, and monolithic-only branch. |
| Sample ID shaders and verification | [`MSCaseSampleID`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L296-L381) | Shows the per-sample ID encoding and exact comparison. |
| Sample position checks | [`MSInstanceSamplePosDistribution`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L384-L548) | Checks legal, unique, and approximately uniform positions. |
| Sample mask cases | [`MSCaseSampleMaskPattern` through `MSCaseSampleMaskWrite`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L799-L1181) | Defines input-mask and output-mask behavior. |
| Storage-image sample writes | [`WriteSampleTest`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1244-L1634) | Checks `gl_SampleID` in compute image writes. |
| Fragment mask writes and readback | [`WriteSampleMaskTestCase`](../../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1638-L2224) | Builds the two-subpass mask test and validates the buffer. |
| Pipeline category registration | [`createPipelineTests`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L130-L143) | Places this test family under supported pipeline construction roots. |
| Built-in semantics | [SampleId](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-sampleid), [SampleMask](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-samplemask) | Defines the shader-visible values and mask rules. |

## Questions / Risk Points for User Audit

- Is the distinction between resolved-image checks and per-sample fetch checks clear?
- Is the monolithic-only scope of `image_write_sample` clear?
- Should the final page include a detailed shader walkthrough for one common case, or is the source-linked summary sufficient for this generated shader matrix?

## Conversion Notes for Final Wiki Rewrite

- Use the five direct registered families as the page's hierarchy and behavior coverage.
- Copy the failure mapping table into the final page under `## Failure Meaning` and `### Failure Cause Mapping`.
- Explain `gl_SampleID`, `gl_SamplePosition`, and `gl_SampleMaskIn/Out` as distinct observable contracts.
- Keep the runtime section in temporal order and distinguish multisample fetch, resolve, storage-image, and input-attachment readback paths.
