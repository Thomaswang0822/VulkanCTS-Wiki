# Understanding Brief: ycbcr image queries

## One-Sentence Test Purpose

This test checks whether shader image-query operations report the configured extent and mip-level count for sampled uncompressed and YCbCr images, including disjoint multi-planar images.

## Background Knowledge

### Image queries describe the image view without reading texels

`OpImageQuerySizeLod` returns the accessible dimensions for a selected mip level. `OpImageQueryLevels` returns the `levelCount` of the image view. Neither operation reads image texels. The Vulkan specification describes both operations in [SPIR-V image queries](../../../../vulkan-docs/src/chapters/images.adoc#images-spirv-queries).

Why it matters here:
- The test can use images without uploading meaningful pixel data. It checks image metadata exposed to the shader.
- Each `TestImage` has one mip level, so `textureQueryLevels(u_image)` must return `1`.

### A YCbCr image can be one image with multiple planes

YCbCr formats may contain multiple planes. The test creates a regular or `VK_IMAGE_CREATE_DISJOINT_BIT` image, allocates and binds its memory, and exposes it through a sampled image view with a sampler YCbCr conversion. The query still concerns the image view's logical dimensions, not the number of planes.

Why it matters here:
- Disjoint cases exercise the same query through the alternate image-memory arrangement.
- Plane divisors determine the dimensions selected for `size_lod` cases, so the constructed extent remains compatible with the format's plane layout.

## One Concrete Example

Consider the registered compute case `dEQP-VK.ycbcr.query.size_lod.compute.r8g8b8a8_unorm`. The generator creates a 2D, one-mip-level `VK_FORMAT_R8G8B8A8_UNORM` image and binds its view to `u_image`. The generated operation is conceptually:

```glsl
// Conceptual reconstruction of the generated operation.
result = textureSize(u_image, lod);
```

The executor supplies `lod = 0`, runs one compute invocation, and returns the `ivec2` result to the host. The host compares it with the `UVec2` extent used to create the image.

## End-to-End Test Flow

```text
[host] choose query type, shader stage, format, image flags, and image size
[host] create the image with one mip level and sampled-image usage
[host] allocate and bind image memory, then create the image view
[host] create a sampler and, for YCbCr formats, a sampler YCbCr conversion
[host] generate the shader containing textureSize or textureQueryLevels
[host] bind the image view and sampler in the combined image sampler descriptor
[host] submit the executor work
[device] run the selected shader stage and evaluate the image query
[device] write the query result to the executor's output buffer
[host] read the output and compare it with the expected extent or 1 mip level
[host] return pass only when every constructed image has the expected result
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`getShaderSpec()` selects GLSL 4.50, declares an integer `lod` input and an output named `result`, and emits one of two expressions. `generateSources()` passes that specification to the shader executor. The compute executor wraps the operation in a local-size-one shader and uses storage buffers for executor input and output.

| Artifact | Produced by | Why it matters |
|---|---|---|
| `textureSize(u_image, lod)` | `getShaderSpec()` for `QUERY_TYPE_IMAGE_SIZE_LOD` | Produces the queried 2D extent. |
| `textureQueryLevels(u_image)` | `getShaderSpec()` for `QUERY_TYPE_IMAGE_LEVELS` | Produces the image-view mip-level count. |
| GLSL 4.50 compute source | `initImageQueryPrograms()` and `vktShaderExecutor.cpp` | Supplies the operation to the selected executor-supported stage. |

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Test image | yes | yes, through its view | queried for metadata | no | Carries the extent and one mip level under test. |
| Image memory allocations | yes | yes | not read for texels by the query | no | Bind the regular or disjoint image. |
| Image view | yes | yes, in the combined sampler descriptor | used by the sampled image | no | Defines the image view queried by the shader. |
| Combined image sampler descriptor | yes | yes | read as `u_image` | no | Connects binding `0`, set `1` to the shader. |
| Executor input buffer | yes | yes | reads `lod` | no | Supplies the mip level for `textureSize`. |
| Executor output buffer | yes | yes | writes `result` | yes | Carries the query result to the host. |

The sampler YCbCr conversion is a sampler/view configuration object, not a pixel-data resource. The query does not validate YCbCr color conversion.

## What Is Checked

- `size_lod` creates six extents based on the format's maximum plane divisor: that divisor, twice the divisor in one dimension, twice in the other, and three larger products.
- The executor passes `lod = 0` for each image. The host compares the returned `ivec2` with the exact extent supplied to `TestImage`.
- `levels` creates one `16x18` image with one mip level and requires the returned integer to equal `1`.
- Any mismatch marks the aggregate result as failed. The test returns pass only when all images in the selected case pass.

## Behavior Parameter Identification

> **Behavior parameter:** query type (`ycbcr.query` test family)
>
> **Candidate values:** `size_lod`, `levels`

The query type changes the shader operation and the host-side expected result. Format, disjointness, shader stage, and image size vary the setup around that operation.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `size_lod` | The implementation reports incorrect image-view dimensions for the selected mip level, or the image/view setup does not preserve the configured extent. |
| `levels` | The implementation reports an incorrect image-view `levelCount`, or the image/view setup does not preserve the one-level configuration. |

## Important Variations and Special Cases

- The `VK_FORMAT_R8G8B8A8_UNORM` reference cases exercise the same query path without YCbCr conversion. They provide a non-planar comparison case.
- YCbCr formats are added from the YCbCr format range and the 444 EXT range. Multi-planar formats also receive `_disjoint` cases.
- The generator creates a shader group for every executor-supported shader stage. The selected stage is a registration dimension, not a change to the query expression.
- YCbCr cases require shared image support, midpoint chroma-sample support, and shader-stage support. Reference-format cases skip the YCbCr-specific checks.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| `getShaderSpec()` | [vktYCbCrImageQueryTests.cpp#L102-L142](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L102-L142) | Selects the query expression, types, descriptor declaration, and GLSL version. |
| Image creation and view setup | [vktYCbCrImageQueryTests.cpp#L145-L248](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L145-L248) | Shows one mip level, sampled usage, memory binding, view creation, and layout transition. |
| Query execution and checks | [vktYCbCrImageQueryTests.cpp#L330-L492](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L330-L492) | Creates cases, executes the shader, and compares results. |
| Support checks | [vktYCbCrImageQueryTests.cpp#L495-L515](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L495-L515) | Defines YCbCr and shader-stage feature requirements. |
| Case generation | [vktYCbCrImageQueryTests.cpp#L517-L599](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L517-L599) | Defines formats, disjoint variants, shader stages, and registered families. |
| Executor compute wrapper | [vktShaderExecutor.cpp#L3061-L3122](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3061-L3122) | Wraps the generated operation and binds executor I/O. |
| Executor buffer I/O | [vktShaderExecutor.cpp#L2034-L2130](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L2034-L2130) | Defines input/output storage buffers and result transport. |
| Vulkan query semantics | [images.adoc#images-spirv-queries](../../../../vulkan-docs/src/chapters/images.adoc#images-spirv-queries) | Defines what `OpImageQuerySizeLod` and `OpImageQueryLevels` return. |

## Questions / Risk Points for User Audit

- Does the distinction between image metadata queries and texel sampling remain clear?
- Is `query` the right primary behavioral axis, with `size_lod` and `levels` as its values?
- Should the final page list the complete registered format matrix, or is the source-backed range description sufficient?
- Is the compute walkthrough representative enough for the page's stage dimension?

## Conversion Notes for Final Wiki Rewrite

- Keep `query` as the primary behavioral axis and explain `size_lod` and `levels` separately.
- Distill the image-query and multi-plane explanations into a short `Background Knowledge` section.
- Use the compute `size_lod` case as the one representative shader walkthrough. The expression is shared across shader stages, while the executor wrapper changes by stage.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write `### Cause Analysis` separately from the test's checks.
- Keep the full source ranges in the appendix and leave registration paths to the hierarchy and parameter sections.
