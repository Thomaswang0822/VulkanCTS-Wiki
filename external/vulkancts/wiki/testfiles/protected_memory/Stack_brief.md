# Understanding Brief: protected memory stack storage

## One-Sentence Test Purpose

This test checks whether a protected compute shader can copy protected image data into function-local stack storage and read the same values through a global array for stack sizes from 32 to 512 bytes.

## Background Knowledge

### Protected memory and protected execution

Protected device memory may be accessed by device operations but must not be visible to the host. Protected images and protected command buffers keep the image data and queue work inside the protected path; the host can inspect only a separate validation result obtained through the CTS image-validation machinery. The Vulkan specification permits access to protected memory in the compute shader stage and the transfer stage when the protected-memory rules are satisfied ([protected memory](../../../../vulkan-docs/src/chapters/memory.adoc#L5566-L5654)).

Why it matters here:
- The compute dispatch reads a protected source image and writes a protected destination image.
- The host supplies the source image through an unprotected staging image, then validates the destination through protected-context helpers rather than mapping protected memory.

### Shader function-local arrays

A global GLSL array and an array declared inside a function can both hold shader values, but a compiler may place the function-local array in stack-like storage. This test copies the global array into a function-local array, reads one selected element from each array, and compares the two values. The comparison is repeated after rebuilding the global data with a shifted image coordinate.

Why it matters here:
- `p(idx)` exercises the function-local array path; `u(idx)` reads the global `protectedData` array.
- The test treats a mismatch between the two reads as a failed stack-storage check, not as a direct inspection of an implementation's physical stack.

## One Concrete Example

For `dEQP-VK.protected_memory.stack.stacksize_32`, the host derives an 8 by 4 invocation grid because the alternating dimension growth reaches an area of 32. Each invocation checks one linear index, `checked_ndx = gy * 8 + gx`. The shader loads 32 pixels into `protectedData`, copies those values into a local `vec4 localData[32]` inside `p()`, and compares `p(checked_ndx)` with `u(checked_ndx)`. A zero-valued output pixel means both repetitions matched; a one-valued pixel records a mismatch.

The example is the actual 32-byte registration case at the test-family level. The array length is the registered `stackMemSize`; the source image stores one `vec4` per array element, so the implementation uses the parameter as an element count even though the source comments describe each invocation as checking a byte element.

## End-to-End Test Flow

```text
[host] choose one of the registered stack sizes and derive imageWidth/imageHeight until their product reaches that size
[host] create an unprotected source image and fill it with deterministic unique colors from deInt32Hash(stackSize)
[host] create protected source and destination images with transfer, sampled, and storage usage
[host] upload the source data to the unprotected image and copy it into the protected source image
[host] clear the protected destination image, create two storage-image descriptors, and build the compute pipeline
[host] submit a protected command buffer that dispatches one workgroup
[device] load source pixels into global protectedData, copy them through p() into localData, and compare p() with u()
[device] repeat the load/compare sequence with the index shift used by the two outer iterations
[device] write vec4(0.0f) for a matching invocation or vec4(1.0f) for a mismatch into the protected destination image
[host] wait for the fence and sample four deterministic coordinates from the destination through ImageValidator
[host] repeat command-buffer creation and protected submission up to eight times until validation fails or all repetitions pass
[host] return pass only when every image validation succeeds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`StackTestCase::initPrograms` generates one compute GLSL source string. It fixes `#version 450`, chooses the local workgroup dimensions from `Params`, substitutes the selected stack size into both array declarations and the loop bound, and registers the result as the `comp` program. The CTS shader build uses the normal compute-source path; no explicit alternate SPIR-V target is set in this source file, so the default source-collection target is used.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Unprotected upload image | yes | yes | transfer source only | no | Holds deterministic source pixels before the protected copy. |
| Protected source image | yes | yes at set 0, binding 1 | compute read | no | Supplies the values copied into `protectedData`. |
| Protected destination image | yes | yes at set 0, binding 0 | compute write | sampled by validation | Stores the per-invocation match/mismatch signal. |
| `protectedData` | no, shader-local global array | no descriptor | compute read/write | no | Receives source pixels and is read by `u(idx)`. |
| `localData` | no, function-local shader array | no descriptor | compute write/read | no | Provides the stack-storage path exercised by `p(idx)`. |
| Image views and storage-image descriptors | yes | yes | address the two images | no | Binding 0 selects the destination and binding 1 selects the source. |

## What Is Checked

- `calculateRef()` sets the expected validation texture to zero for every destination texel.
- The shader stores one-valued output only when one of the two `vec4` comparisons differs during the two repetitions.
- `validateResult()` samples four pseudo-random normalized coordinates generated from `deInt32Hash(stackSize)` and asks `ImageValidator` to compare the protected destination against the zero reference in `VK_IMAGE_LAYOUT_GENERAL`.
- The test repeats the protected submit and validation sequence up to eight times. It returns `Pass` only if all checked samples match zero; otherwise it returns `Result validation failed`.

## Behavior Parameter Identification

> **Behavior parameter:** registered stack-size test family leaf
>
> **Candidate values:** `stacksize_32`, `stacksize_64`, `stacksize_128`, `stacksize_256`, `stacksize_512`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `stacksize_32` | Protected source-image access, function-local array storage for 32 elements, global/local value comparison, protected destination write, or image validation does not produce the expected zero image. |
| `stacksize_64` | Protected source-image access, function-local array storage for 64 elements, global/local value comparison, protected destination write, or image validation does not produce the expected zero image. |
| `stacksize_128` | Protected source-image access, function-local array storage for 128 elements, global/local value comparison, protected destination write, or image validation does not produce the expected zero image. |
| `stacksize_256` | Protected source-image access, function-local array storage for 256 elements, global/local value comparison, protected destination write, or image validation does not produce the expected zero image. |
| `stacksize_512` | Protected source-image access, function-local array storage for 512 elements, global/local value comparison, protected destination write, or image validation does not produce the expected zero image. |

## Important Variations and Special Cases

- The registered sizes are exact: 32, 64, 128, 256, and 512. The `Params` constructor alternates doubling width and height until the image area reaches the selected size, giving 8x4, 8x8, 16x8, 16x16, and 32x16 respectively.
- Each selected size changes the compute local size, image extent, global and function-local array lengths, image-load loop bound, and linear-index calculation. It is the primary behavior axis rather than a cosmetic label.
- The source image is initialized through an unprotected upload image, but the shader-visible source and destination images are protected. The test therefore checks protected execution without asking the host to read protected memory.
- `maxComputeWorkGroupInvocations` must cover the derived image area. A device that cannot support the selected local invocation count skips the case during `checkSupport()`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter derivation and deterministic seed | [`Params` and `getSeedValue`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L59-L86) | Defines stack sizes, image dimensions, and source-image seed. |
| Support gate and case creation | [`StackTestCase::checkSupport` and `createStackTests`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L104-L130) | Checks protected context support, invocation limits, and registers the five leaves. |
| Generated compute shader | [`StackTestCase::initPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L137-L213) | Emits the exact arrays, image bindings, comparison, and result write. |
| Protected image setup and descriptor bindings | [`StackTestInstance::iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L237-L334) | Creates images, stages source data, and binds destination/source at bindings 0 and 1. |
| Submission and repeated validation | [`StackTestInstance::iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L336-L372) | Dispatches protected work and repeats validation up to eight times. |
| Reference and image validation | [`calculateRef` and `validateResult`](../../../modules/vulkan/protected_memory/vktProtectedMemStackTests.cpp#L375-L405) | Defines the zero reference and sampled pass/fail check. |
| Protected-memory semantics | [`Protected Memory`](../../../../vulkan-docs/src/chapters/memory.adoc#L5566-L5654) | Defines protected memory visibility and permitted compute/transfer access. |

## Questions / Risk Points for User Audit

- The source comments call each invocation's item a byte, while the generated arrays contain `vec4` elements and the source image has one `vec4` per element. Should the final page describe the tested unit as an array element, with the source wording retained only as a quoted implementation comment?
- Does the final walkthrough need a second case, or is `stacksize_32` sufficient because the other registered sizes change dimensions and array bounds without changing shader control flow?
- Is the distinction between protected shader resources and the unprotected upload image clear enough for the final page?
- Should the final page call the local array “stack-like storage” rather than asserting a physical stack allocation, since the source tests behavior without inspecting implementation placement?

## Conversion Notes for Final Wiki Rewrite

- Use `stacksize_32` as the single representative walkthrough. It exposes the smallest complete generated shader and the same control-flow shape used by the larger leaves.
- Distill Background Knowledge to protected-memory visibility and the distinction between global and function-local shader arrays. Keep the byte-versus-element wording precise and avoid claiming a physical allocation mechanism.
- Carry the behavior-axis conclusion and copy this failure mapping table into `Stack.md` unchanged.
- Write fresh Cause Analysis around observable image mismatches and source-grounded candidate mechanisms; do not infer a bug location from the test name.
- Keep the protected/unprotected image distinction in Runtime Execution and the shader declaration comments. Move helper and source-file details into the final appendix.
- Read the generated shader through the shader-analyzer/disassembler workflow before finalizing the walkthrough and preserve the complete generated SPIR-V artifact.
