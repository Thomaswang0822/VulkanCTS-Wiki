# Understanding Brief: `image.mismatched_write_op`

## One-Sentence Test Purpose

This test checks whether Vulkan accepts and, for vector-size cases, correctly executes `OpImageWrite` when its value operand has a permitted vector width or type representation that differs from the storage image's formatted texel shape.

## Background Knowledge

### `OpImageWrite` value operands and formatted texels

`OpImageWrite` writes a value to one storage-image texel. Vulkan image formats contain from one to four color components; during an image write, components absent from the image format are discarded. This makes an operand wider than the target format meaningful: the test can require the target's used components to survive without asserting anything about extra supplied components.

Why it matters here:

- `mismatched_vector_sizes` emits scalar, two-, three-, four-, or five-component operands only when the operand width is at least the target format's used-channel count.
- The result comparator checks exactly the target format's used components, so it does not turn discarded extra components into an oracle.

### Compute invocations and the storage-buffer source

The generated compute module has local size `1 1 1`. Each global invocation converts `GlobalInvocationId.xy` to a 2D integer image coordinate, computes `y * imageWidth + x`, loads four scalar components from a storage buffer, constructs the selected `OpImageWrite` value, and writes one texel. The storage buffer is therefore source data for the write, not the test result.

Why it matters here:

- The host populates the buffer and clears the image before dispatch, then copies the image back into its helper buffer for comparison.
- The signedness-and-type family uses the same execution shape but has no numeric comparison; successful generation, pipeline creation, dispatch, and completion form its observable result.

## One Concrete Example

For a conceptual `image.mismatched_write_op.mismatched_vector_sizes.rg32f_from_vec4` case, the host creates a two-channel floating-point storage image and a four-component floating-point storage buffer. One invocation loads `red`, `green`, `blue`, and `alpha` from the buffer and emits this source-derived write sequence:

```text
%rgba = OpCompositeConstruct %v4float %red %green %blue %alpha
        OpImageWrite %img %id_xy %rgba
```

The image format has two used channels. The source generator permits the four-component operand because `4 >= 2`; after copyback, the test compares the image's two used components with the corresponding buffer components using a `0.0005f` floating-point tolerance. It does not require an observable destination for `blue` or `alpha`.

## End-to-End Test Flow

```text
[host] register a target format and either a source vector width or a same-channel-class source SPIR-V format
[host] check image-format support, required extensions, and conditional 64-bit or long-vector support
[host] generate a SPIR-V assembly compute module with a selected OpImageWrite value operand
[host] create a 2D storage image, a storage buffer, descriptors, and a compute pipeline
[host] populate the buffer, clear the image, upload the image contents, and transition it to GENERAL
[device] each 1x1x1 compute invocation loads four buffer components and writes one image texel
[host] transition and copy the image to its helper buffer, wait for completion, invalidate host-visible allocations
[host] compare used channels for mismatched_vector_sizes, or accept completion for mismatched_signedness_and_type
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

[`getProgramCodeAndVariables()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L600-L779) builds a SPIR-V assembly template. It selects the storage-image sampled type, declared SPIR-V image format, storage-buffer array stride, image dimensions, and optional Int64 or LongVector declarations. [`MismatchedVectorSizesTest::initPrograms()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L792-L829) inserts one of five `OpImageWrite` operand constructions. [`MismatchedSignednessAndTypeTest::initPrograms()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L831-L848) always constructs a four-component operand but varies the declared source `spirvFormat` through registration.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 2D storage image and image view | yes | yes, descriptor binding 0 | written by `OpImageWrite` | yes, through its helper buffer | Holds the observed formatted image result. |
| Storage buffer | yes | yes, descriptor binding 1 | read by the compute shader | source buffer is host-populated; image helper buffer is inspected | Supplies the four scalar source components. |
| Image helper buffer | yes, inside `StorageImage2D` | transfer source/destination | used for image upload and download | yes | Initializes and retrieves the image contents. |
| Generated SPIR-V compute module | yes | used to create the compute pipeline | executes on dispatch | no | Fixes the image declaration and value operand being tested. |

## What Is Checked

- `mismatched_vector_sizes` compares every texel's target-format components after copyback. Signed and unsigned integer values must match exactly. Floating and fixed-point values use `0.0005f` tolerance.
- The comparator uses the target format's used-channel count, not the source operand width.
- `mismatched_signedness_and_type` reaches the same dispatch and copyback sequence, but its `compare()` callback returns `true`; it checks successful execution rather than a numeric conversion or reinterpretation result.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `mismatched_vector_sizes`, `mismatched_signedness_and_type`

The two direct test families change the primary property under test. Format, source width, and source SPIR-V format select cases within those family behaviors.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `mismatched_vector_sizes` | SPIR-V operand-width acceptance or lowering, formatted storage-image write behavior for used components, format-specific conversion, or image transfer/readback comparison failure. |
| `mismatched_signedness_and_type` | SPIR-V image/value type acceptance or lowering, format-specific storage-image pipeline setup, descriptor or dispatch execution failure. |

## Important Variations and Special Cases

- The vector-size matrix uses widths 1 through 5 in Vulkan builds and 1 through 4 in Vulkan SC builds. Width 5 requires `longVector` where that feature is available.
- Both direct families draw targets from the source's 41-format list. The signedness-and-type registration groups source and target formats by the same `TextureChannelClass` and excludes a pair if either format is a 64-bit integer format.
- 64-bit integer target formats require `shaderInt64`, `VK_EXT_shader_image_atomic_int64`, `SPV_EXT_shader_image_int64`, and 64-bit buffer channels. This extends the resource/type representation; it does not change the comparison model.
- The source names the second family `mismatched_signedness_and_type`, but its factory pairs formats within one channel class and its shader sampled type comes from the target format's buffer representation. The test therefore establishes execution acceptance for that generated declaration pairing, not a checked cross-class numeric conversion.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Format matrix and channel-class helpers | [`allFormats[]` and format helpers](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L459-L559) | Defines the available targets and source-format grouping. |
| Support gates and assembly template | [`checkSupport()` and `getProgramCodeAndVariables()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L561-L779) | Defines legal-device gates and generated module declarations. |
| Two write-operand generators | [`initPrograms()` implementations](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L792-L848) | Shows each `OpImageWrite` value construction. |
| Runtime setup and verdict | [`MismatchedWriteOpTestInstance::iterate()` and comparators](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L961-L1061) | Establishes upload, dispatch, download, and the two validation contracts. |
| Registration factory | [`createImageWriteOpTests()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1065-L1127) | Defines the direct test families and case-generation loops. |
| Image-write semantics | [`images.adoc`](../../../../vulkan-docs/src/chapters/images.adoc#L165-L192) | States formatted image-write encoding and treatment of components absent from the image format. |

## Questions / Risk Points for User Audit

- Does the distinction between a wider operand and a target format with fewer used channels make the vector-size oracle clear?
- Does the page make clear that the second family's `compare()` callback does not validate numeric data?
- Is the direct-SPIR-V generator explained at enough depth without presenting reconstructed GLSL that the source does not generate?

## Conversion Notes for Final Wiki Rewrite

- Keep only the short prerequisites on formatted image writes and one-invocation-per-texel compute addressing.
- Retain the `rg32f_from_vec4`-style operand example as an explanatory source-derived sequence, not as a reconstructed GLSL walkthrough.
- Use the two direct test families as the final behavioral axis and copy the failure-cause table unchanged.
- State the direct-SPIR-V exception explicitly in `## Shader Analysis`; do not claim that `mismatched_signedness_and_type` checks a numeric conversion.
