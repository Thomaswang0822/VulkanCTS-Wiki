# Understanding Brief: image.atomic_operations

## One-Sentence Test Purpose

This test family checks whether compute shaders perform atomic read-modify-write operations on storage-image texels and storage texel-buffer elements, including the values returned by the atomic instructions, across supported operations, numeric types, initialization paths, and sparse-resource variants.

## Background Knowledge

### Atomic operations return the value that was present before the update

An atomic operation identifies one storage location, reads its current value, applies one update without allowing another atomic update to interleave inside that operation, writes the new value, and returns the old value to its invocation. For image atomics, SPIR-V uses `OpImageTexelPointer` to obtain a pointer to the selected texel before an atomic instruction accesses it.

Why it matters here:

- Five compute invocations address each logical texel, so the final value and the five returned values expose different parts of the contract.
- The implementation may choose the order in which those competing invocations take effect. The test accepts any sequence that can result from applying each submitted argument once.

### Storage images, storage texel buffers, and sparse residency

A storage image exposes a formatted image view to a shader. A storage texel buffer exposes formatted buffer elements through a storage texel-buffer view. Both can supply the one atomic location selected by the generated coordinate. A sparse image adds an explicit residency binding path; a sparse read additionally asks the shader to compare a normal image load with `sparseImageLoadARB`.

Why it matters here:

- The `buffer` shape uses a storage texel-buffer descriptor instead of an image descriptor.
- Sparse backing and sparse shader reads add feature checks and resource setup without changing the atomic-operation rule.

## One Concrete Example

`dEQP-VK.image.atomic_operations.add.1d.notransfer.normal_read.normal_img.r32ui_end_result` starts every `r32ui` element at 18. The compute dispatch has five invocations for each of the 64 logical texels. Invocation `gx` atomically adds `gx * gx` at image coordinate `gx % 64`, so the five invocations that map to texel `x` contribute the arguments for `x`, `x + 64`, `x + 128`, `x + 192`, and `x + 256`. The host reads back each element and recomputes 18 plus those five arguments. The order does not affect addition's final value.

## End-to-End Test Flow

```text
[host] select atomic operation, image type, transfer mode, read mode, backing type, format, tiling, and result-check leaf
[host] check image or texel-buffer format support plus the features required by the selected type and resource form
[host] allocate the result resource and host-visible input and output buffers; allocate a second result resource for intermediate-value leaves
[host] initialize each logical texel with the operation-specific initial value through a transfer copy or a generated fill shader
[device] dispatch five compute invocations for every logical texel; each invocation atomically accesses the same logical texel as four peers
[device] for intermediate-value leaves, write each returned old value to a separate position in the extended intermediate-results resource
[host] synchronize shader writes for transfer or shader readback, copy observed data into host-visible memory, and wait for completion
[host] compare final values or search for a valid ordering of the five returned values; pass only when every checked texel succeeds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `BinaryAtomicEndResultCase::initPrograms()` generates the ordinary GLSL compute shader for `add`, `min`, `max`, bitwise operations, `exchange`, and `compare_exchange`. It derives the image type, coordinate type, format qualifier, argument expression, and compare value from the selected case.
- `BinaryAtomicIntermValuesCase::initPrograms()` generates the corresponding GLSL shader with a second write-only storage resource for returned values.
- `sub`, `inc`, and `dec` use the SPIR-V assembly template selected by `getSpirvAtomicOpShader()`, specialized with `OpAtomicISub`, `OpAtomicIIncrement`, or `OpAtomicIDecrement`.
- When `notransfer` is selected, `AddFillReadShader()` generates separate compute shaders that initialize the result resource and read it into a buffer after the atomic dispatch.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result storage image or storage texel-buffer view | yes | yes | atomically read and written | yes | Holds the initial value and the final atomic state. |
| Intermediate-results image or storage texel-buffer view | intermediate-value leaves only | yes | written by the atomic shader | yes | Stores one returned old value per contending invocation. |
| Host-visible input buffer | yes | transfer source or storage buffer for fill | read by initialization work | no | Supplies operation-specific initial texel values. |
| Host-visible output buffer | yes | transfer destination or storage buffer for readback | written by copy or read shader | yes | Makes the observed result available to the verifier. |
| Sparse image binding and wait semaphore | sparse backing only | yes | image is atomically accessed after binding | indirectly | Makes sparse-resident storage available before the compute submission. |

## What Is Checked

- `*_end_result` leaves inspect each final texel. For `add`, `sub`, `inc`, `dec`, `min`, `max`, `and`, `or`, and `xor`, the host applies the five generated arguments to the operation-specific initial value and requires an exact match.
- For `exchange` and `compare_exchange` end-result leaves, the host requires the final texel to equal one of the five generated atomic arguments. The compare-exchange shader uses 18 as the 32-bit comparison value and 820338753304 for 64-bit values.
- `*_intermediate_values` leaves record the old value returned by each of the five atomics. `verifyRecursive()` accepts the data only if it can assign each recorded value to a unique argument in an order where that value equals the state before that argument updates the location.
- Half-vector intermediate leaves run the same sequence check per component. The test represents `rg16f` and `rgba16f` values with the local `F16Vec2` and `F16Vec4` reference types.

## Behavior Parameter Identification

> **Behavior parameter:** atomic operation
>
> **Candidate values:** `add`, `sub`, `inc`, `dec`, `min`, `max`, `and`, `or`, `xor`, `exchange`, `compare_exchange`

The atomic-operation test family uses operation as its primary behavioral axis. Type, stage, resource, and result-checking choices select the legal implementation path and the observed aspect of the same operation.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `add` | Atomic addition, generated addend addressing, or final/intermediate result capture and validation. |
| `sub` | `OpAtomicISub` execution or its specialized SPIR-V assembly, result capture, or validation. |
| `inc` | `OpAtomicIIncrement` execution or its specialized SPIR-V assembly, result capture, or validation. |
| `dec` | `OpAtomicIDecrement` execution or its specialized SPIR-V assembly, result capture, or validation. |
| `min` | Atomic minimum semantics for the selected signed, unsigned, or floating-point type, or result validation. |
| `max` | Atomic maximum semantics for the selected signed, unsigned, or floating-point type, or result validation. |
| `and` | Atomic bitwise AND semantics, generated operand values, or result validation. |
| `or` | Atomic bitwise OR semantics, generated operand values, or result validation. |
| `xor` | Atomic bitwise XOR semantics, generated operand values, or result validation. |
| `exchange` | Atomic exchange return/final-state semantics or acceptance of one of the submitted arguments. |
| `compare_exchange` | Conditional compare-and-swap semantics, comparison-value typing, or acceptance of a submitted replacement value. |

## Important Variations and Special Cases

- **Atomic operation variation.** `add`, `sub`, `inc`, `dec`, `min`, `max`, `and`, `or`, and `xor` use order-independent final-result checks. `exchange` and `compare_exchange` accept a final value from the submitted arguments because the winning invocation can vary. `sub`, `inc`, and `dec` need SPIR-V assembly because the generated GLSL path has no matching function selected by `getAtomicOperationShaderFuncName()`.
- **Type variation.** The registration matrix includes `r32ui`, `r32i`, `r32f`, `r64ui`, and `r64i`; non-Vulkan-SC builds also include `rg16f` and `rgba16f`. Float cases retain only `add`, `exchange`, and, outside Vulkan SC, `min` and `max`. `r32f` requires `VK_EXT_shader_atomic_float`; `min` and `max` on it also require `VK_EXT_shader_atomic_float2`. The 64-bit formats require `VK_EXT_shader_image_atomic_int64`; the half-vector formats require `VK_NV_shader_atomic_float16_vector` outside Vulkan SC.
- **Stage variation.** All atomics run in compute shaders with `local_size_x = local_size_y = local_size_z = 1`. The source dispatches five times the logical x dimension, so five global invocations contend for each logical texel. `notransfer` also uses compute shaders for initialization and readback; `transfer` uses buffer-image copies around the atomic compute dispatch.
- **Resource variation.** Cases cover `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array`, and `buffer`, with optimal or linear tiling where registered. `buffer` uses storage texel-buffer descriptors. Non-Vulkan-SC builds add `normal_img` and `sparse_img` backing plus `normal_read` and `sparse_read`; sparse reads exclude 1D, 1D-array, and buffer shapes, and sparse backing excludes linear tiling and shapes that do not map to 2D or 3D Vulkan images.
- **Result-checking variation.** Every legal matrix combination has `*_end_result` and `*_intermediate_values` leaves. The first checks the settled location; the second checks the old values returned by the atomic calls and therefore detects a broken return-value sequence even if a commutative operation reaches the correct final value.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Image atomic semantics | [`images.adoc#L248-L263`](../../../../vulkan-docs/src/chapters/images.adoc#L248-L263) | Defines image-texel pointers as the route from image coordinates to atomic-accessible locations. |
| Operation enum, operation naming, and argument generation | [`vktImageAtomicOperationTests.cpp#L301-L650`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L301-L650) | Defines the operations, five-invocation constant, initial values, and per-invocation operands. |
| Generated GLSL and specialized SPIR-V selection | [`BinaryAtomicEndResultCase::initPrograms()` and `BinaryAtomicIntermValuesCase::initPrograms()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1194-L1418) | Builds the shaders and selects the SPIR-V templates. |
| Resource creation, initialization, dispatch, and host synchronization | [`BinaryAtomicInstanceBase::iterate()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1498-L1663) | Implements the shared host/device execution path. |
| End-result and returned-value checks | [`verifyResult()`, `isValueCorrect()`, and `verifyRecursive()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1935-L2099) | Defines the final-state and valid-sequence contracts. |
| Matrix registration and pruning | [`createImageAtomicOperationTests()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2477-L2655) | Defines registered operations, shapes, formats, resource modes, and result-check leaves. |

## Questions / Risk Points for User Audit

- Does the distinction between the final-state check and the returned-value sequence check make clear why both leaves are needed?
- Does the representative `add` path make the five-way contention and modulo addressing clear without implying a fixed invocation order?
- Are the feature-gated floating-point, 64-bit, half-vector, and sparse cases described at the right level for the final page?

## Conversion Notes for Final Wiki Rewrite

- Use atomic operation as the final page's primary behavior axis and copy the failure-cause table unchanged.
- Retain short background bullets on returned old values and image-texel locations, then put all concrete setup in the runtime and shader sections.
- Use the representative `add.1d.notransfer.normal_read.normal_img.r32ui_end_result` compute shader because it exposes shared coordinate folding and five-way contention without an extension-specific SPIR-V template.
- Put type, compute-stage, resource, and result-checking variation in the final parameter table and use the special-cases section for their pruning rules.
