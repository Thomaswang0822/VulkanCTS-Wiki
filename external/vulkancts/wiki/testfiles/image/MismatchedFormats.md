## Overview

**Core question:** Does the CTS complete a generated storage-image read, write, or sparse read when a `VkImage`/view format is paired with the shader image-format declaration selected by the test factory?

- [`vktImageMismatchedFormatsTests.cpp`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp) implements `image.mismatched_formats`, which [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100) adds to the `image` category.
- For every admitted pair, the image and its `VK_IMAGE_VIEW_TYPE_2D` view use the selected `VkFormat`; the generated GLSL layout qualifier comes from the selected `SpirvFormats` label. The factory does **not** require the two labels to be different, despite the family name.
- The factory admits only non-compressed Vulkan formats that `matching()` describes with equal used-channel count, pixel size, and `tcu::TextureChannelClass`. This is the test's source-level filter, not a restatement of the Vulkan SPIR-V/Vulkan-format compatibility table.
- The three generated operation groups have no data oracle: after successful submission and wait, `iterate()` returns `Passed` without uploading source texels, copying the image back, or examining shader results.

## Background Knowledge

For the shared concept image/view/format interpretation, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Formatted storage images.** The GLSL layout qualifier used here produces a non-`Unknown` SPIR-V `OpTypeImage` image format. Vulkan defines which SPIR-V image formats are compatible with which `VkFormat` values in its [SPIR-V/Vulkan image-format compatibility table](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L4369-L4381); it separately defines the sampled-type and signedness requirements for each SPIR-V image format in [Image Format and Type Matching](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L4274-L4344). The CTS factory's three-field filter is its own matrix-generation rule and does not encode that table.
- **Image operations.** The generated `imageLoad`, `sparseImageLoadARB`, and `imageStore` calls lower to SPIR-V image-read, sparse-read, and image-write operations. Vulkan describes `OpImageRead`/`OpImageSparseRead` and `OpImageWrite` as image accesses in the [image-access sections](../../../../vulkan-docs/src/chapters/images.adoc#L194-L245). The generator always supplies a four-component GLSL vector type, as required for read results by the [SPIR-V validity rule](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L749-L752).
- **Sparse reads.** A sparse image may have unbound regions. `sparseImageLoadARB` provides both a loaded vector and an integer residency result; this test declares both locals but uses neither. The sparse group therefore tests setup and completion, not a residency-code or texel-value expectation.

## Registration Hierarchy

```text
image.mismatched_formats
├── image_read
├── image_write
└── sparse_image_read  (not built for Vulkan SC)
```

[`createImageMismatchedFormatsTests()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L478-L524) creates the root and direct children, and adds one leaf for each admitted format pair to every applicable child. The checked-in inventories currently contain:

| Build inventory | `image_read` | `image_write` | `sparse_image_read` | Total |
|---|---:|---:|---:|---:|
| [`vk-default`](../../../mustpass/main/vk-default/image/mismatched-formats.txt) | 102 | 102 | 102 | 306 |
| [`vksc-default`](../../../mustpass/main/vksc-default/image/mismatched-formats.txt) | 102 | 102 | not registered | 204 |

## Parameter Dimensions and Observed Values

| Dimension | Registered values / construction | Meaning in this test | Evidence |
|---|---|---|---|
| Operation group | `image_read`, `image_write`, and, outside Vulkan SC, `sparse_image_read` | Selects the generated image instruction and sparse resource path. | [Factory](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L478-L524) |
| Vulkan image format | Every enum value from `VK_FORMAT_R4G4_UNORM_PACK8` up to (but excluding) `VK_CORE_FORMAT_LAST`, except compressed formats and formats rejected by `matching()` | Becomes the image-create and image-view `VkFormat`. | [Factory loop](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L489-L513), [image view](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L432-L436) |
| Shader image-format label | 39 `SpirvFormats` entries across floating-, fixed-, signed-integer-, and unsigned-integer channel classes | Determines the GLSL layout-format spelling, image type, vector type, and write value. | [`SpirvFormats` and helpers](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L90-L177) |
| Pair admission | Equal used-channel count, bytes per pixel, and `TextureChannelClass` | Limits the generated leaves. `mapVkFormat()` failures are caught and rejected. | [`matching()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L179-L194) |
| Leaf name | `<vk_format_without_VK_FORMAT_>_with_<SpirvFormats key>`, lower-cased | Identifies the selected pair; it does not itself prove that the two representations differ. | [Name construction](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L499-L511) |
| Resource and dispatch | One 8 x 8 x 1, one-mip, one-layer, single-sample, optimal-tiled 2D image; dispatch `8, 8, 1` | Keeps shape fixed while each one-invocation workgroup addresses a global `(x, y)` coordinate. | [Image create info](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L203-L229), [dispatch](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L444-L458) |

`ChannelClassToImageType()` selects `image2D` for non-integers, `iimage2D` for signed integers, and `uimage2D` for unsigned integers; the corresponding vector types are `vec4`, `ivec4`, and `uvec4`.

## Behavior Parameters

The direct operation group is the behavioral axis. Vulkan-format and shader-format choices select leaves within the shared matrix.

### `image_read`: ordinary storage-image read

The shader declares the formatted storage image and assigns `imageLoad(inputImage, ivec2(gl_GlobalInvocationID.xy))` to a local typed vector. The result is unused. The image transitions from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_GENERAL` and receives no initialization, upload, readback, or comparison; this is a completion-only path, not a texel-value test.

### `image_write`: ordinary storage-image write

Each invocation calls `imageStore` at its global 2D coordinate. The selected channel class determines the generated value:

| Channel class | Generated value |
|---|---|
| Non-integer | `vec4(0.25, 0.5, 0.0, 1.0)` |
| Signed integer | `ivec4(-1, 2, -1000, 2000)` |
| Unsigned integer | `uvec4(1, 10, 100, 1000)` |

The image contents are not copied back or compared.

### `sparse_image_read`: sparse storage-image read

Outside Vulkan SC, the image has `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`. The shader requires `GL_ARB_sparse_texture2`, calls `sparseImageLoadARB`, and leaves its result vector and residency integer unused. The host allocates/binds sparse memory and makes the compute submission wait on the sparse-bind semaphore; it still does not observe a texel or residency result.

## Shader Analysis

[`MismatchedFormatTest::initPrograms()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L294-L352) emits one compute shader per leaf. This walkthrough uses the exact registered write case below.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.mismatched_formats.image_write.r8g8b8a8_unorm_with_rgba8
```

| Parameter choice | Meaning in this representative case |
|---|---|
| Operation: `image_write` | The compute shader writes a constant value to a storage image. |
| Image format: `r8g8b8a8_unorm` | The Vulkan image stores four normalized 8-bit channels. |
| Shader format qualifier: `rgba8` | The generated GLSL declares the storage image with `rgba8`. |
| Dispatch | One invocation addresses one texel through `gl_GlobalInvocationID.xy`. |

#### Purpose

The compute shader verifies that the selected Vulkan image format accepts the generated `rgba8` storage-image declaration and write operation.

#### Structural Design

| Phase | Shader action |
|---|---|
| Coordinate | Convert `gl_GlobalInvocationID.xy` to the signed image coordinate. |
| Value | Construct the constant color `(0.25, 0.5, 0.0, 1.0)`. |
| Write | Store that value to binding 0 with `imageStore`. |

#### Shader Code

```glsl
#version 460
layout (rgba8, set = 0, binding = 0) uniform writeonly image2D inputImage;
void main (void)
{
    imageStore(inputImage, ivec2(gl_GlobalInvocationID.xy), vec4(0.25, 0.5, 0.0, 1.0));
}
```

#### Additional Info

- The selected leaf exercises the write template; read and sparse-read siblings use the matching image-format pair through different generated operations.
- The generated source is registered by [`MismatchedFormatTest::initPrograms()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L294-L352).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Operation family | `image_read` loads from the storage image; `sparse_image_read` adds sparse residency handling; `image_write` performs `imageStore`. | [shader generation](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L294-L352) |
| Vulkan image format | Changes the tested resource format and the compatible generated image declaration. | [format mapping](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L77-L143) |
| GLSL image qualifier | Changes the layout qualifier and sampled scalar/vector type selected for the shader declaration. | [format mapping](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L77-L143) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 27
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %4 "main" %14
               OpExecutionMode %4 LocalSize 1 1 1
               OpSource GLSL 460
               OpName %4 "main"
               OpName %9 "inputImage"
               OpName %14 "gl_GlobalInvocationID"
               OpDecorate %9 Binding 0
               OpDecorate %9 DescriptorSet 0
               OpDecorate %14 BuiltIn GlobalInvocationId
          %2 = OpTypeVoid
          %3 = OpTypeFunction %2
          %6 = OpTypeFloat 32
          %7 = OpTypeImage %6 2D 0 0 0 2 Rgba8
          %8 = OpTypePointer UniformConstant %7
          %9 = OpVariable %8 UniformConstant
         %11 = OpTypeInt 32 0
         %12 = OpTypeVector %11 3
         %13 = OpTypePointer Input %12
         %14 = OpVariable %13 Input
         %15 = OpTypeVector %11 2
         %18 = OpTypeInt 32 1
         %19 = OpTypeVector %18 2
         %21 = OpTypeVector %6 4
         %22 = OpConstant %6 0.25
         %23 = OpConstant %6 0.5
         %24 = OpConstant %6 0
         %25 = OpConstant %6 1
         %26 = OpConstantComposite %21 %22 %23 %24 %25
          %4 = OpFunction %2 None %3
          %5 = OpLabel
         %10 = OpLoad %7 %9
         %16 = OpLoad %12 %14
         %17 = OpVectorShuffle %15 %16 %16 0 1
         %20 = OpBitcast %19 %17
               OpImageWrite %10 %20 %26
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. The case creates the fixed image with `STORAGE`, `TRANSFER_SRC`, and `TRANSFER_DST` usage. Ordinary cases allocate/bind image memory; sparse cases call `allocateAndBindSparseImage()` and obtain a semaphore.
2. It creates a storage-image descriptor-set layout, descriptor pool/set, pipeline layout, shader module, and compute pipeline. Binding 0 receives the same-`VkFormat` 2D image view in `VK_IMAGE_LAYOUT_GENERAL`.
3. A command buffer transitions the image from `UNDEFINED` to `GENERAL`, binds pipeline and descriptor set, and dispatches `8 x 8 x 1` workgroups. Sparse submission waits on the bind semaphore; ordinary submission has no such wait.
4. After `submitCommandsAndWait()`, the instance unconditionally returns `tcu::TestStatus::pass("Passed")`.

There is no image upload, transfer copyback, shader-side reporting, or host comparison. A pass establishes that this implementation's selected support path, shader/pipeline/resource setup, submission, and wait completed; it does not establish a numerical read result, stored texel value, format conversion result, or sparse residency result.

## Failure Meaning

### Failure Cause Mapping

| Failing group | What the test can establish | What it cannot establish |
|---|---|---|
| `image_read` | A supported configuration did not complete one of shader compilation/module creation, pipeline or descriptor setup, image transition, submission/wait, or read execution steps. | A returned texel was wrong; the loaded vector is unused and the source image is not initialized. |
| `image_write` | A supported configuration did not complete one of the same setup/execution steps, including the typed write dispatch. | A stored texel was wrong; the image is never copied back or compared. |
| `sparse_image_read` | Required sparse support was unavailable, or a supported sparse configuration did not complete sparse binding/synchronization, shader setup, or dispatch. | The residency code or loaded texel was wrong; neither is consumed. |

### Cause Analysis

#### Setup, submission, or execution completion

**Possible failure symptoms:** A supported leaf does not reach the unconditional `Passed` verdict after submission and wait; a sparse leaf may instead fail its required support or sparse-resource path.

**Possible implementation causes:** The failure can occur in shader compilation or module creation, pipeline or descriptor setup, image transition, submission/wait, or the selected read/write execution; sparse leaves also include sparse binding and semaphore synchronization. The CTS log and implementation investigation are needed to identify the exact stage because the source-level verdict contract provides only completion evidence.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` in the selected Vulkan format's optimal-tiling features.
- `sparse_image_read` additionally requires the core sparse-binding feature, `sparseResidencyBuffer`, `shaderResourceResidency`, and `checkSparseImageFormatSupport()` for the exact create information.
- Vulkan SC does not compile/register the sparse group.

### Design-based pruning

- Compressed `VkFormat` values are skipped before pairing.
- A pair is added only if the source's `matching()` predicate succeeds. It catches the `tcu::InternalError` that `mapVkFormat()` can throw, so unmappable formats add no leaves.
- The matrix deliberately fixes the resource to one 8 x 8 2D mip/layer and varies format declarations and operation kind rather than dimensions, samples, or a result oracle.

## Key Takeaways

- `image.mismatched_formats` generates a source-filtered matrix of Vulkan-image and shader-image-format pairs; it includes both label-matched and label-different examples.
- Its format predicate is equal channel count, pixel size, and channel class. Consult the Vulkan compatibility table, rather than this predicate, for normative SPIR-V/Vulkan format compatibility.
- All three operation groups are completion-only tests. The sparse group adds sparse support, binding, and semaphore handling, but no residency or data oracle.

## Source Reference Appendix

| Subject | Link |
|---|---|
| Format metadata, type helpers, and pair filter | [`FormatInfo`, `SpirvFormats`, helpers, and `matching()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L69-L194) |
| Fixed image configuration | [`fillImageCreateInfo()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L203-L229) |
| Support checks and generated GLSL | [`checkSupport()` and `initPrograms()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L256-L352) |
| Resource setup, submission, and unconditional verdict | [`MismatchedFormatTestInstance::iterate()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L378-L469) |
| Registration | [`createImageMismatchedFormatsTests()`](../../../modules/vulkan/image/vktImageMismatchedFormatsTests.cpp#L478-L524) |
| Parent dispatcher | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100) |
| Mustpass inventories | [`vk-default`](../../../mustpass/main/vk-default/image/mismatched-formats.txt) and [`vksc-default`](../../../mustpass/main/vksc-default/image/mismatched-formats.txt) |
| Normative image-format background | [Vulkan image-format/type matching](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L4274-L4344) and [SPIR-V/Vulkan format compatibility](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L4369-L4381) |
