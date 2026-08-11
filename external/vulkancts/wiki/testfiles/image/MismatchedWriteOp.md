## Overview

**Core question:** Does a Vulkan implementation accept and correctly execute `OpImageWrite` when the instruction's value operand has a permitted width that differs from the formatted storage image's used-channel count, or when the generated case selects a different same-channel-class source-format label?

- [`vktImageMismatchedWriteOpTests.cpp`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp) implements the `image.mismatched_write_op` test family under the `image` test category.
- `mismatched_vector_sizes` writes scalar through five-component values to a formatted 2D storage image. The generator admits a source width only when it is at least the target format's used-channel count, then compares the target's used components after readback.
- `mismatched_signedness_and_type` registers source/target format-name pairs within one texture channel class. Its generated module writes a four-component value using the target-derived sampled type, and its comparison callback returns `true`. This family tests successful setup and execution, not a numeric conversion result.
- Both direct test families share generated SPIR-V assembly, a storage image, a storage-buffer input, image upload/download helpers, and a one-invocation-per-texel compute dispatch.

## Background Knowledge

- **Formatted image writes.** A Vulkan image texel has up to four components. An image write encodes the supplied value in the target format, and components absent from that format are discarded. A wider `OpImageWrite` operand can therefore be valid for a narrower target format, while the target's used components remain the observable result.
- **Compute addressing and storage buffers.** This module uses `LocalSize 1 1 1`. Each global invocation maps `GlobalInvocationId.xy` to one 2D texel and computes a linear buffer index. The storage buffer supplies four scalar components that the module uses to construct the image-write operand.

## Registration Hierarchy

```text
image.mismatched_write_op
├── mismatched_vector_sizes
└── mismatched_signedness_and_type
```

[`createImageWriteOpTests()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1065-L1127) creates the test family and both direct children. The default Vulkan mustpass inventory lists leaves below each child.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct test family | `mismatched_vector_sizes`, `mismatched_signedness_and_type` | Chooses the primary property: operand width with a data oracle, or generated source-format pairing with completion-only validation. | [`createImageWriteOpTests()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1082-L1124) |
| Target image format | 41 entries: floating, normalized, signed-integer, unsigned-integer, and `R64` integer formats | Selects the image's `VkFormat`, SPIR-V image format, sampled type, used-channel count, and comparison type. | [`allFormats[]`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L459-L502) |
| Source operand width | `1`, `2`, `3`, `4`, `5`; maximum `4` in Vulkan SC | Selects scalar, `vec2`, `vec3`, `vec4`, or `vec5` construction for `mismatched_vector_sizes`. A case exists only when the width is at least the target's used-channel count. | [Width loop](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1106-L1119) |
| Source SPIR-V-format label | Formats in the target's `TextureChannelClass`, excluding pairs containing a 64-bit integer format | Forms `mismatched_signedness_and_type` leaf names and determines their per-case height. The generated shader reads its actual image type from the target format. | [Class grouping and factory loop](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L504-L514), [registration](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1087-L1104) |
| Image extent | Vector-size: `12 * sourceWidth` by `8 * (6 - sourceWidth + 1)`; source-format-pair: `12` by `8 * (pair index + 1)` | Sizes the dispatch and the source/result resources. | [Parameter construction](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1099-L1118) |
| Buffer channel type | `float`, `sint`, `uint`, `double`, `slong`, `ulong` with RGBA order | Chooses the source-buffer scalar type from the target format's channel class and 64-bit status. | [`makeChannelType()` and `makeBufferFormat()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L539-L559) |

The vector-size leaf suffixes use `_from_scalar`, `_from_vec2`, `_from_vec3`, `_from_vec4`, and, outside Vulkan SC, `_from_vec5`. For example, the default inventory contains `image.mismatched_write_op.mismatched_vector_sizes.rg32f_from_vec4`.

## Behavior Parameters

The primary behavioral axis is the direct **test family**. Target format, source width, and source-format label select the generated leaves within these two mechanisms.

### `mismatched_vector_sizes` - Write an operand with a selected vector width

The source builds an `OpImageWrite` value from one, two, three, four, or five buffer-loaded scalars. The constructor asserts, and the factory enforces, that the source width is at least the target format's used-channel count. After dispatch and image download, the comparator checks every target-format component against the source buffer.

A scalar target can therefore receive any admitted width, while a two-channel target begins at `vec2` and a four-channel target begins at `vec4`. The test does not request a value operand narrower than the target's used-channel count.

### `mismatched_signedness_and_type` - Run a generated same-channel-class format-pair case

The factory enumerates each target format against formats from the same `TextureChannelClass` and records the counterpart in `Params::spirvFormat` for naming and size generation. The common assembly generator obtains `SAMPLED_TYPE` and `SPIRV_IMAGE_FORMAT` from `vkFormat`, the target format. This direct family always constructs `%v4${SAMPLED_TYPE}` and calls `OpImageWrite` with that value.

The runtime follows the shared upload, dispatch, download sequence, but [`MismatchedSignednessAndTypeTestInstance::compare()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1055-L1061) ignores both pixel accesses and returns `true`. A passing result establishes successful execution of the generated configuration. It does not establish a checked signedness conversion, numeric type conversion, or post-write texel value.

## Shader Analysis

The source authors SPIR-V assembly directly through [`getProgramCodeAndVariables()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L600-L779), rather than generating GLSL or HLSL. The direct assembly generator is the authoritative shader representation, so this page does not present a reconstructed GLSL walkthrough or a duplicate compiler-produced SPIR-V disassembly.

### Representative shader walkthrough: `mismatched_vector_sizes.rg32f_from_vec4`

Representative path:

```text
image.mismatched_write_op.mismatched_vector_sizes.rg32f_from_vec4
```

#### Purpose

The representative leaf targets a two-channel 32-bit floating-point image and builds a four-component floating-point image-write operand. It tests that the generated `OpImageWrite` accepts and executes that operand form, then checks the two components the target format uses.

#### Structural Design

| Phase | Assembly behavior | Role in the test |
|-------|-------------------|------------------|
| Image declaration | Declares `%image_type = OpTypeImage %float 2D 0 0 0 2 Rg32f`. | Binds the two-channel target format to the storage image. |
| Invocation coordinate | Loads `%gid`, extracts x/y, bitcasts them to signed integers, and constructs `%id_xy`. | Selects one target texel per compute invocation. |
| Buffer access | Computes `y * imageWidth + x`, then loads `red`, `green`, `blue`, and `alpha` from the storage-buffer RGBA element. | Supplies data for the selected operand width. |
| Four-component write | Constructs `%rgba` from the four scalar loads and executes `OpImageWrite %img %id_xy %rgba`. | Exercises an operand wider than the target's two used channels. |

#### Source Code

```llvm
; Source-derived specialization emitted by MismatchedVectorSizesTest::initPrograms().
; The surrounding common template declares the entry point, descriptors, types,
; coordinate/index calculation, and %red/%green/%blue/%alpha loads.
%image_type = OpTypeImage %float 2D 0 0 0 2 Rg32f

; %id_xy is ivec2(GlobalInvocationId.xy).
; %red, %green, %blue, and %alpha come from buffer[index].rgba.
%rgba = OpCompositeConstruct %v4float %red %green %blue %alpha
        OpImageWrite %img %id_xy %rgba
```

#### Additional Info

- [`MismatchedVectorSizesTest::initPrograms()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L797-L829) substitutes a single scalar write for width 1 and `v2`, `v3`, `v4`, or `v5` composite construction for the other widths.
- The common template declares storage image binding 0 and storage-buffer binding 1, emits `GlobalInvocationId` as the only built-in, and fixes `LocalSize 1 1 1` ([template](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L602-L718)).
- The source uses `SpirVAsmBuildOptions` with `SPIRV_VERSION_1_4` for both direct families ([program registration](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L826-L829), [second-family registration](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L841-L847)).

#### Parameter Variation Summary

| Parameter dimension | Assembly-level variation from this representative case | Evidence |
|---------------------|--------------------------------------------------------|----------|
| Source width | Replaces the `v4float` composite with a scalar write or `v2`, `v3`, or `v5` composite. Width 5 adds LongVector declarations and capability support. | [Write templates](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L797-L825), [long-vector setup](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L761-L769) |
| Target channel class | Replaces `%float` with `%sint`, `%uint`, `%slong`, or `%ulong` as selected by the target-derived buffer format. | [`getChannelStr()` and buffer format selection](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L516-L559), [template substitution](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L745-L776) |
| Target image format | Replaces the `Rg32f` image-format token and can change the target used-channel count that admits source widths. | [Format list](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L459-L502), [factory condition](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1111-L1119) |
| Direct test family | Always builds a four-component composite in `mismatched_signedness_and_type`; its format-pair field does not replace the target-derived image declaration in the common template. | [Second-family generator](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L831-L848), [parameter uses](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L745-L776) |

## Runtime Execution and Result Checking

- `StorageImage2D` creates a one-mip, one-layer, optimally tiled 2D image with storage, transfer-source, and transfer-destination usage. Its helper buffer holds the host-visible upload/download representation ([creation](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L256-L316), [transfer helpers](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L318-L387)).
- The instance creates a separate host-visible storage buffer using the target-derived RGBA buffer format. It binds the storage image at descriptor binding 0 and the storage buffer at binding 1.
- Before dispatch, `populate()` fills the storage buffer with channel-class-specific patterns and `clear()` initializes the image. The command buffer uploads the image, transitions it to `GENERAL`, dispatches `textureWidth` by `textureHeight` workgroups, then downloads the image through a transfer-source layout.
- The host flushes the initialized allocations before submission, waits for queue completion, invalidates the image and buffer allocations, and calls the selected family's comparator.
- `mismatched_vector_sizes` compares all texels through the target format's used-channel count. Signed and unsigned integers require exact equality; other channel classes use `0.0005f`. `mismatched_signedness_and_type` accepts the completed run because its comparator unconditionally returns `true`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `mismatched_vector_sizes` | SPIR-V operand-width acceptance or lowering, formatted storage-image write behavior for used components, format-specific conversion, or image transfer/readback comparison failure. |
| `mismatched_signedness_and_type` | SPIR-V image/value type acceptance or lowering, format-specific storage-image pipeline setup, descriptor or dispatch execution failure. |

### Cause Analysis

#### SPIR-V operand width, formatted write, format conversion, or readback comparison

**Possible failure symptoms:** A `mismatched_vector_sizes` case reports `Pixel comparison failed` after the host downloads the image. For any target texel, the comparator only considers components from index 0 through the target format's used-channel count minus one. Integer differences require no tolerance; floating and fixed-point differences beyond `0.0005f` fail the case.

**Possible implementation causes:** The generated module varies the value type passed to `OpImageWrite` while retaining the target image declaration. A failure can arise during module acceptance or lowering of the selected width, storage-image write execution, encoding into the target format, transfer-based download, or the source/result handling used by the comparator. The shared result does not isolate one of those stages without runtime diagnostics and source-level investigation.

#### SPIR-V image/value acceptance, pipeline setup, descriptor use, or dispatch execution

**Possible failure symptoms:** A supported `mismatched_signedness_and_type` case can fail before it reaches a successful completed run, such as during shader-module or pipeline creation, descriptor setup, command submission, or device execution. It cannot report a wrong texel value because its comparator ignores the downloaded pixels.

**Possible implementation causes:** This path combines the generated target-derived image/value declarations with a same-channel-class source-format-pair registration matrix. Incorrect acceptance or lowering of the module, selected storage-image configuration, descriptor binding, layout/transfer sequence, or compute dispatch can prevent completion. The source's unconditional `true` comparison prevents the test from identifying a numerical data error, and a specific failed stage requires runtime logs and source-level investigation.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_KHR_variable_pointers`, `VK_KHR_storage_buffer_storage_class`, optimal-tiling `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT`, and both transfer-source and transfer-destination support for the target format.
- A 64-bit integer target requires the `shaderInt64` feature and `VK_EXT_shader_image_atomic_int64`. The generated assembly adds `SPV_EXT_shader_image_int64`, `Int64ImageEXT`, and `Int64` declarations for that target.
- Outside Vulkan SC, width-5 vector leaves require `VkPhysicalDeviceShaderLongVectorFeaturesEXT::longVector`. Vulkan SC does not register width-5 leaves.

### Design-based pruning

- The source includes only its fixed 41-format list and only 2D, one-mip, one-layer images. It varies write operands and target formats rather than image dimensionality, samples, layers, or mip levels.
- `mismatched_vector_sizes` excludes widths smaller than the target format's used-channel count. It consequently avoids cases where the test would need to define an expected value for missing input components.
- `mismatched_signedness_and_type` pairs formats only inside the same `TextureChannelClass` and skips every pair containing a 64-bit integer format. This narrows the completion-only matrix to the generator's intended type groups.

## Key Takeaways

- `mismatched_vector_sizes` tests write operands that are at least as wide as the formatted target and compares only the target's used channels after copyback.
- The source uses direct SPIR-V assembly so it can control the exact `OpImageWrite` value type, including the non-GLSL-standard five-component vector path.
- `mismatched_signedness_and_type` shares the execution infrastructure but has no numeric oracle. Its `spirvFormat` parameter affects registration names and extent selection, while the common assembly builds the image declaration from the target `vkFormat`.
- A failure in the vector-size family provides a post-write pixel mismatch. A failure in the second family identifies a completion problem but cannot diagnose a stored texel value.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Format matrix and buffer-type helpers | [`allFormats[]`, `getChannelStr()`, and `makeBufferFormat()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L459-L559) | Defines generated target formats and target-derived scalar/vector representations. |
| Support checks and direct assembly template | [`MismatchedWriteOpTest::checkSupport()` and `getProgramCodeAndVariables()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L561-L779) | Defines feature gates, descriptors, image declaration, addressing, and conditional assembly declarations. |
| Write operand generators | [`MismatchedVectorSizesTest::initPrograms()` and `MismatchedSignednessAndTypeTest::initPrograms()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L792-L848) | Defines the two `OpImageWrite` value constructions. |
| Data generation and comparison | [`clear()`, `populate()`, and comparators](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L850-L1061) | Defines initialized patterns and the distinct verdict contracts. |
| Runtime setup and submission | [`MismatchedWriteOpTestInstance::iterate()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L961-L1023) | Creates descriptors/pipeline/resources, dispatches, downloads, and reports the comparison result. |
| Test registration | [`createImageWriteOpTests()`](../../../modules/vulkan/image/vktImageMismatchedWriteOpTests.cpp#L1065-L1127) | Registers direct test families and their generated leaves. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L99) | Places `mismatched_write_op` in the `image` test category. |
| Default Vulkan inventory | [`image/mismatched-write-op.txt`](../../../mustpass/main/vk-default/image/mismatched-write-op.txt) | Confirms executable default-Vulkan leaves for both direct families. |
| Vulkan image-write semantics | [`images.adoc`](../../../../vulkan-docs/src/chapters/images.adoc#L165-L192) | Defines formatted image writes and discarding of components absent from the target format. |
