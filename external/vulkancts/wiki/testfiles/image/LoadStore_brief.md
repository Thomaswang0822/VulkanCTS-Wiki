# Understanding Brief: storage-image load/store tests

## One-Sentence Test Purpose

This test area checks that Vulkan storage-image and texel-buffer operations preserve the expected texel data across formatted and formatless access, compatible view reinterpretation, selected SPIR-V operands, device-scope visibility, and AMD explicit-LOD operations.

## Background Knowledge

### Storage-image access and image views

A storage image is a descriptor-backed image view that a shader reads with `imageLoad` or writes with `imageStore`. The view format determines the storage interpretation exposed to the shader. A GLSL layout format qualifier gives the shader a specific SPIR-V image format. Formatless storage access omits that qualifier and needs the matching read-without-format or write-without-format capability.

Why it matters here:

- The same basic transfer is registered with both declaration styles.
- The reinterpretation cases bind a compatible view format to mutable image storage rather than converting texels.

### Visibility versus execution order

A pipeline barrier can order the stages that execute, but shader memory semantics determine whether a device-scope image write becomes available to a later shader and visible to its image load. The device-scope family deliberately uses both mechanisms: shader barriers for availability or visibility and a command-buffer barrier for execution order.

Why it matters here:

- `comp_comp` hands data from one compute shader to another.
- `comp_draw` hands data from a compute shader to a fragment shader through a color-attachment result.

## One Concrete Example

`image.load_store.with_format.2d.r8g8b8a8_unorm` uses a source and a destination 64 x 64 storage image. The host uploads an XOR-coordinate reference pattern to the source. Each compute invocation reads `(63 - x, y)` from the source and writes that value at `(x, y)` in the destination. The host copies the destination to a buffer, flips the reference horizontally, and compares the two images. The mirror makes a successful result depend on the read coordinate as well as the write coordinate.

## End-to-End Test Flow

```text
[host] select the registered root, resource shape, format, tiling, and declaration flags
[host] check the required format features, extension, API version, and device features
[host] create images or texel-buffer views, descriptors, a host-visible helper buffer, and generated shader artifacts
[host] upload a reference image when the selected root has a source resource
[device] dispatch imageStore or imageLoad/imageStore work, or execute the selected two-stage device-scope path
[host] apply shader-to-transfer and transfer-to-host synchronization, then copy the observed result to host-visible memory
[host] generate or transform the expected reference and perform format-aware comparison
[host] report pass only when the comparison succeeds
```

The extension-operand roots use generated SPIR-V assembly rather than generated GLSL. `load_store_lod` repeats upload, dispatch, copyback, and comparison for every mip level.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `StoreTest::initPrograms()` generates GLSL for plain stores. It chooses image type, coordinate dimensionality, typed value expression, optional layout format, and constant-value behavior.
- `LoadStoreTest::makePrograms()` generates the normal load/store GLSL. It emits the source and destination declarations and mirrors the x coordinate before the load.
- `ImageExtendOperandTest::initPrograms()` builds SPIR-V assembly containing `OpImageRead` and `OpImageWrite`, with `SignExtend`, `ZeroExtend`, or `Nontemporal` selected by the case.
- The device-scope factory emits a store-side compute shader plus a load-side compute or fragment shader. Those shaders use `memoryBarrier` with `MakeAvailable` or `MakeVisible`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Source image or source texel-buffer view | yes | yes | read by load/store paths | indirectly | Holds uploaded reference texels. |
| Destination image or destination texel-buffer view | yes | yes | written by store and load/store paths | yes | Holds the observed result. |
| Host-visible helper buffer | yes | transfer or texel-buffer use as needed | transfer source/destination | yes | Uploads references and receives copied output. |
| Per-layer uniform buffer for stores | yes | yes | read by store shader | no | Supplies the layer index used by generated store logic. |
| Device-scope color attachment | only for `comp_draw` | yes | written by fragment shader | yes | Converts the second image load into a graphics-stage result. |

## What Is Checked

- `store` compares a generated coordinate pattern, or the representable middle value for `_constant` leaves, against copied output.
- Normal `load_store`, `format_reinterpret`, `device_scope_access`, and `load_store_lod` compare a horizontally flipped reference against output. The LOD path compares each mip level separately.
- `extend_operands_spirv1p4` and `nontemporal_operand` use an 8 x 8 integer reference and exact integer comparison. Relaxed-precision leaves mask the upper bits before comparing.
- The shared comparison helper uses exact integer thresholds, bounded fixed-point thresholds, or floating ULP thresholds according to the output format.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `store`, `load_store`, `format_reinterpret`, `extend_operands_spirv1p4`, `nontemporal_operand`, `device_scope_access`, `load_store_lod`

The seven direct roots change the instruction form or visibility rule under test. Formats, image types, tilings, layer binding, precision, and view offsets configure those behaviors.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `store` | Storage-image or storage-texel-buffer write, generated coordinate/value handling, or copyback/comparison failure. |
| `load_store` | Source read, destination write, formatless capability handling, descriptor setup, or mirrored-reference validation failure. |
| `format_reinterpret` | Mutable compatible-view creation, same-size format interpretation, or reinterpretation reference handling failure. |
| `extend_operands_spirv1p4` | SPIR-V 1.4 image operand lowering, signedness/width handling, relaxed-precision masking, or integer readback failure. |
| `nontemporal_operand` | SPIR-V 1.6 `Nontemporal` handling on `OpImageWrite`, integer image write, or readback failure. |
| `device_scope_access` | Device-scope availability/visibility semantics, cross-stage ordering, graphics output setup, or result copyback failure. |
| `load_store_lod` | AMD explicit-LOD instruction handling, mip-level addressing, per-level transfer, or per-level comparison failure. |

## Important Variations and Special Cases

- `with_format` declares the image format on both read and write image declarations. `without_format` leaves the read image unqualified but declares the write image. `without_any_format` leaves both unqualified. Normal `load_store` has all three groups; the AMD LOD family has the first two.
- The ordinary resource matrix includes 1D, 1D array, 2D, 2D array, 3D, cube, cube array, and buffer views. Buffer leaves can use an aligned nonzero view offset. Selected buffer load leaves use a uniform texel-buffer source, including a three-component special case that expands one fetched texel into three destination stores.
- Depth-only storage cases appear only in formatless groups, use optimal tiling, and apply only to 2D and 2D-array shapes. The disabled formatted branch avoids substituting an unrelated SPIR-V format declaration for a depth format.
- `nontemporal_operand` is not registered for Vulkan SC. It requires Vulkan 1.3 or later in non-Vulkan-SC builds.
- `comp_draw` excludes 3D textures and skips in compute-only execution because it needs a graphics pipeline and a color attachment.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Reference generation, comparison, compatibility, and copy helpers | [`vktImageLoadStoreTests.cpp#L250-L539`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L250-L539) | Defines the expected data and format-aware result checks. |
| Store support and generated GLSL | [`StoreTest`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L541-L861) | Implements plain `imageStore` behavior. |
| Normal load/store support and shader generator | [`LoadStoreTest`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1200-L1684) | Implements format declarations, the mirror operation, and device-scope shader variants. |
| Host image and buffer execution | [`LoadStoreTestInstance` and derived instances](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1726-L2422) | Sets up resources, dispatches, copies results, and validates output. |
| SPIR-V operand generator and integer result check | [`ImageExtendOperandTest`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L2671-L2990) | Implements extension operands and `Nontemporal`. |
| Seven registration factories | [`vktImageLoadStoreTests.cpp#L3408-L3975`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3408-L3975) | Defines the direct `image` roots and their generated case matrices. |

## Questions / Risk Points for User Audit

- Is the distinction between execution order and image-memory visibility clear in the device-scope explanation?
- Does the chosen mirrored 2D example give enough context for the ordinary load/store matrix?
- Should the final page retain the full generated SPIR-V walkthrough for a normal GLSL case, or is a shorter audited assembly block preferred by the wiki review process?

## Conversion Notes for Final Wiki Rewrite

- Use the seven direct test families as the final page's behavior parameter axis and copy the failure-cause table unchanged.
- Keep the final Background Knowledge section limited to formatted versus formatless access and device-scope availability/visibility.
- Use `image.load_store.with_format.2d.r8g8b8a8_unorm` as the representative shader walkthrough because its normal GLSL source exposes the mirrored read/write behavior without special extensions.
- Keep the complete parameter matrix in a compact table; move detailed helper and factory navigation to the source appendix.
