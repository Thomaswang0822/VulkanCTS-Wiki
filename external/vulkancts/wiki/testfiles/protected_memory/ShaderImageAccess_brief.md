# Understanding Brief: Shader image access in protected memory

## One-Sentence Test Purpose

This test checks whether fragment and compute pipelines can sample, fetch, load, store, and atomically modify protected images while preserving the expected image contents and pipeline access restrictions.

## Background Knowledge

### Protected memory and protected queue operations

Protected device memory is visible to the device but not to the host. Vulkan therefore couples protected resources with protected command buffers, protected-capable queues, and protected submissions. Shader reads from protected memory are valid in the fragment and compute stages used here; the test never maps the protected image on the CPU.

Why it matters here:

- The test uploads reference data through a transfer into a protected image, executes the selected shader operation in a protected submission, and validates the result with another protected compute submission.
- `VK_EXT_pipeline_protected_access` can restrict a pipeline to protected command buffers or to unprotected command buffers. A pipeline without either restriction remains usable in both contexts when the feature is enabled.

### Sampled-image access versus storage-image access

A combined image sampler supports filtered `texture` access and integer-coordinate `texelFetch`. A storage image supports `imageLoad`, `imageStore`, and format-limited atomic operations in `GENERAL` layout. The shader declaration, descriptor type, image layout, and result image all change with the selected access type.

Why it matters here:

- `sampling` uses normalized coordinates and nearest filtering; `texelfetch` addresses texels directly.
- `imageload` copies source texels into an observable result. `imagestore` adds a destination storage image in the fragment path.
- `imageatomics` updates the source image in place, so the host computes the same operation for every texel before validation.

## One Concrete Example

For `dEQP-VK.protected_memory.image.access.compute.default.none.imageatomics.add.r32i`, the generator emits this faithful compute shader shape:

```glsl
#version 450
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(set = 0, binding = 0, r32i) coherent uniform highp iimage2D u_resultImage;

void main() {
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);
    imageAtomicAdd(u_resultImage, ivec2(gx, gy), int(gx*gx + gy*gy));
}
```

The host dispatches `128 × 128 × 1` workgroups, each with one invocation. Invocation `(x,y)` atomically adds `x*x + y*y` to that texel's initial signed integer value. The test computes the same result on its CPU-side texture, then asks the protected image validator to compare four deterministic sample locations.

## End-to-End Test Flow

```text
[host] choose shader stage, pipeline-access mode, pipeline flags, image operation, format, and atomic operation if needed
[host] generate the selected fragment or compute GLSL plus the protected image-validation shaders
[host] create a deterministic 128 × 128 reference texture in unprotected host-visible storage
[host] upload it to an unprotected image, then copy it into the protected source image
[host] create protected source/result images, views, sampler, descriptors, pipeline, and protected command buffer as required by the case
[host] submit a protected draw or a 128 × 128 compute dispatch; maintenance5 no-protected-access uses the paired unprotected mode
[device] perform texture, texel-fetch, image-load/store, or image-atomic access
[host] compute the atomic reference image when the operation modifies texels in place
[host] choose the shader-produced image: color attachment, storage destination, or atomically modified source
[host] generate four deterministic reference coordinates and values
[device] run the protected image validator and sample those four coordinates with a 0.1 threshold
[host] treat validator timeout as failure; otherwise pass the case
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | Generated or loaded where | Role |
|----------|---------------------------|------|
| Fragment vertex shader | `ImageAccessTestCase::initPrograms()` | Passes quad position and texture coordinates to the fragment shader. |
| Fragment access shader | `ImageAccessTestCase::initPrograms()` | Performs the selected image operation and writes a color attachment or storage image. |
| Compute access shader | `ImageAccessTestCase::initPrograms()` | Maps one invocation to one texel and writes or atomically updates the result image. |
| `ResetSSBO` and `ImageValidator` compute shaders | `ImageValidator::initPrograms()` | Reset the protected helper buffer, sample four expected points, and force a timeout on mismatch. |
| Graphics or compute pipeline | Runtime path selected by shader stage | Carries the ordinary or protected-access pipeline flags. Maintenance5 cases supply those flags through `VkPipelineCreateFlags2CreateInfoKHR`. |

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Source image | yes | yes, binding 0 or 1 | shader reads it; atomics update it in place | no | Contains the protected test data. |
| Destination storage image | yes, when needed | yes, binding 0 or 1 | compute/store cases write it | no | Makes shader reads or stores observable. |
| Combined image sampler | yes for `sampling` and `texelfetch` | yes | shader reads source image | no | Selects normalized sampling or integer texel fetch. |
| Fragment color image | yes in fragment cases | yes, framebuffer attachment | fragment output writes it | no | Holds results for fragment reads and sampling; storage/atomic cases choose another result image when appropriate. |
| Protected validator helper SSBO | yes | yes, validator binding 1 | reset shader writes zero; validator enters an intentional nonterminating loop on mismatch | no | Converts a protected-image mismatch into a submission timeout without exposing protected values to the host. |
| Reference uniform buffer | yes, unprotected and host-visible | yes, validator binding 2 | validator reads four coordinates and values | initialized by host | Supplies comparison data that is independent of protected image contents. |
| Protected/unprotected command pool and submission | yes | yes | executes selected pipeline | no | Matches the case's protection mode and pipeline access restriction. |

## What Is Checked

| Access type | Shader-produced image selected for validation | Expected content |
|-------------|-----------------------------------------------|------------------|
| `sampling` | compute destination or fragment color attachment | Nearest-sampled source texture. |
| `texelfetch` | compute destination or fragment color attachment | Source texels fetched at integer coordinates. |
| `imageload` | compute destination or fragment color attachment | Source storage-image values. |
| `imagestore` | fragment destination storage image | Values loaded from the source and stored to the destination. |
| `imageatomics` | atomically modified source image | Initial red-channel value combined with `x*x + y*y` using the selected operation. |

The image validator samples four deterministic coordinates and accepts per-component absolute error up to `0.1`. It signals mismatch by entering a loop whose increment remains zero; a one-second validation submission timeout makes `validateImage()` return false. The case otherwise passes after a successful validator submission.

## Behavior Parameter Identification

> **Behavior parameter:** `access type` (behavioral group below the pipeline-flag dimensions)
>
> **Candidate values:** `sampling`, `texelfetch`, `imageload`, `imagestore`, `imageatomics`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sampling` | Protected sampled-image access, normalized-coordinate sampling, descriptor/layout handling, or result validation produced unexpected values. |
| `texelfetch` | Protected sampled-image texel fetch, integer coordinate handling, descriptor/layout handling, or result validation produced unexpected values. |
| `imageload` | Protected storage-image reads, storage-image format/descriptor handling, result writes, or validation produced unexpected values. |
| `imagestore` | The fragment path failed to copy values between protected storage images, or the destination image was not made available for validation. |
| `imageatomics` | A protected storage-image atomic operation, coherent image access, format-specific signedness, or CPU reference calculation disagreed with the validated image. |

## Important Variations and Special Cases

- Shader stage: `fragment` renders a four-vertex triangle strip and exposes results through a color attachment or storage image. `compute` dispatches one invocation per texel. Compute `imagestore` is omitted because another protected-memory test already covers it.
- Pipeline access mode: `default` uses the protected-memory path without requesting `pipelineProtectedAccess`. `protected_access` requires `VK_EXT_pipeline_protected_access` and tests `none`, `protected_access_only`, and `no_protected_access` flags. Invalid default-plus-flag combinations are not registered.
- Protection mode: the `no_protected_access` pipeline flag changes `Params::protectionMode` to unprotected, so the corresponding command pool, resources, and submission match the pipeline restriction.
- Formats: ordinary accesses use `rgba8`, `r32i`, and `r32ui`. Image atomics use only `r32i` and `r32ui`.
- Atomic operations: `add`, `min`, `max`, `and`, `or`, `xor`, and `exchange` each have signed and unsigned cases.
- Maintenance5: two non-Vulkan-SC `misc` cases pass protected-only and no-protected-access flags through `VkPipelineCreateFlags2CreateInfoKHR` while creating a compute image-load pipeline.
- Vulkan SC: only `default.none` branches are present; pipeline-protected-access and `misc` maintenance5 cases are excluded at compile time.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameters and operation enums | [vktProtectedMemShaderImageAccessTests.cpp#L57-L130](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L57-L130) | Defines stage, access, atomic, pipeline, and protection choices. |
| GLSL generation | [ImageAccessTestCase::initPrograms()](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L347-L524) | Generates the exact fragment and compute shaders. |
| Compute resources and execution | [executeComputeTest()](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L574-L824) | Creates images/descriptors, creates the pipeline, dispatches, and chooses the result. |
| Fragment resources and execution | [executeFragmentTest()](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L826-L1208) | Creates render targets and descriptors, draws, synchronizes, and chooses the result. |
| Atomic reference and result selection | [calculateAtomicRef() and validateResult()](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1210-L1247) | Computes expected atomic output and launches image validation. |
| Registration matrix and pruning | [createShaderImageAccessTests()](../../../modules/vulkan/protected_memory/vktProtectedMemShaderImageAccessTests.cpp#L1251-L1404) | Registers stages, modes, flags, accesses, atomic operations, formats, and maintenance5 cases. |
| Protected image validator shader | [ImageValidator::initPrograms()](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Shows four-sample comparison and timeout-based mismatch signaling. |
| Protected image validator runtime | [ImageValidator::validateImage()](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Creates validation resources and turns timeout into failure. |
| Protected memory model | [memory.adoc#L5564-L5643](../../../../vulkan-docs/src/chapters/memory.adoc#L5564-L5643) | Defines protected resources, submissions, access rules, and pipeline restrictions. |
| Pipeline restriction semantics | [pipelines.adoc#L758-L763](../../../../vulkan-docs/src/chapters/pipelines.adoc#L758-L763) | Defines protected-only and no-protected-access pipeline binding restrictions. |
| Vulkan mustpass inventory | [protected-memory.txt#L407-L604](../../../mustpass/main/vk-default/protected-memory.txt#L407-L604) | Provides the 198 Vulkan test paths for this family. |

## Questions / Risk Points for User Audit

- [x] The access type is the primary behavioral axis because it changes shader instructions, descriptor type, image layout, resource topology, and expected result.
- [x] The compute signed atomic-add case is representative for the final shader walkthrough because it exercises protected read/write access, coherent storage-image atomics, per-texel coordinate mapping, and exact CPU reference calculation.
- [x] Fragment-stage differences can be explained in the parameter and runtime sections without a second full walkthrough; the same generator and validation contract cover them.
- [x] The validator does not copy protected pixels to the host. It reports a mismatch indirectly through a protected compute submission timeout.
- [x] Source and spec evidence resolve the pipeline flag semantics and the maintenance5 path; no semantic risk blocks the final page.

## Conversion Notes for Final Wiki Rewrite

- Distill protected memory, image access classes, and timeout-based validation into short prerequisite bullets.
- Use `access type` with the five values above as `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table unchanged.
- Insert one auto-mode walkthrough for `dEQP-VK.protected_memory.image.access.compute.default.none.imageatomics.add.r32i`, built from `ImageAccessTestCase::initPrograms()`.
- Keep the resource and runtime explanation focused on why protected image values never need host readback.
- Put the full registration matrix and source navigation in the parameter table and appendix rather than the opening narrative.
