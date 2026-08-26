# Understanding Brief: `texture.multisample`

## One-Sentence Test Purpose

These tests exercise per-sample storage-image accesses in compute shaders: one family applies atomic integer operations to every sample, while the other attempts writes with sample operands outside the image's valid sample range and checks whether valid samples retain their assigned colors.

## Background Knowledge

### Multisample image coordinates

Vulkan models an image texel coordinate as `(x,y,z,layer,sample,level)`. For a multisample image, the sample operand is therefore part of the addressed location rather than a filter or resolve parameter. Image coordinate validation compares that sample coordinate with the image's sample count.

Why it matters here:
- the `atomic` family addresses samples 0 through 3 of a four-sample storage image;
- the `invalid_sample_index` family deliberately supplies sample operands outside `[0,numSamples)`.

### Storage-image atomics and robust image access

SPIR-V image atomic instructions obtain a texel pointer through `OpImageTexelPointer`, then perform atomic read-modify-write operations on that location. Vulkan defines predictable out-of-bounds storage-image writes only when robust image access applies: such writes must not modify memory. The inspected tests request `shaderStorageImageMultisample`, but they do not request or enable `robustImageAccess` or `robustImageAccess2`. The common CTS device setup disables those robustness features by default.

This distinction exposes a specification risk in `invalid_sample_index`: its Amber comments say that invalid writes should be discarded, but the registered requirements do not establish the robust-image condition that provides that guarantee.

## One Concrete Example

The registered case `dEQP-VK.texture.multisample.atomic.storage_image_r32ui` binds a four-sample `R32_UINT` storage image and a single-sample `R8G8B8A8_UNORM` result image. Each 16 by 16 workgroup pairs invocation `(x,y)` with `(15-x,15-y)`.

For every sample `s`, one invocation initializes its texel to `s + id`. The pair then contributes two additions, two OR masks, and two XOR masks before the invocation clears bit `s`. The script expects:

```text
((s + 2*id + partnerId) | 0xcc000000) & ~(1u << s)
```

A matching texel writes green to the result image; a mismatch writes red. Amber requires the full 64 by 64 result image to be green.

The R64 scripts follow the same operation sequence, but their comparison expression uses `0x0a00000000000000`. The operations produce the 64-bit analogue `0xcc00000000000000`: the OR phase contributes the top-byte `0xc0`, and the two XOR masks combine to `0x0c` in the next byte. This source-side oracle mismatch means a conforming atomic result does not match the current R64 expected expression.

## End-to-End Test Flow

```text
1. atomic
[host] register one Amber case for each signed/unsigned 32-bit or 64-bit format
[host] check required features and four-sample storage-image creation support
[host] parse the Amber script and compile its compute shader for SPIR-V 1.0 by default
[host] create and bind the multisample integer image and RGBA8 result image
[host] dispatch 4 by 4 workgroups, each containing 16 by 16 invocations
[device] initialize four samples, synchronize, and perform add/OR, XOR, and AND phases
[device] compare all four samples and write green or red to the result image
[host] apply Amber's EXPECT command to all 64 by 64 result pixels

2. invalid_sample_index
[host] register one Amber case for each sample count 2, 4, 8, 16, 32, or 64
[host] check shaderStorageImageMultisample and sampled-image creation support for that count
[host] parse the Amber script and compile its compute shader for SPIR-V 1.0 by default
[host] create and bind a 16 by 16 multisample RGBA8 image and a result image
[host] dispatch one 16 by 16 workgroup
[device] issue imageStore for sample operands -256 through 255, assigning distinct colors only to valid samples
[device] read valid samples, compare them with their assigned colors, and write green or red
[host] apply Amber's EXPECT command to all 16 by 16 result pixels
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

Each test case loads one Amber script containing a GLSL 4.30 compute shader, image declarations, descriptor bindings, a dispatch command, and an `EXPECT` command. The common Amber executor uses SPIR-V 1.0 unless a script supplies another target environment; these scripts do not.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `texture` in `atomic` | yes | yes, set 0 binding 0 | read and written | no direct host comparison | Holds four independent integer samples per texel and receives the tested atomics. |
| `texture` in `invalid_sample_index` | yes | yes, set 0 binding 0 | read and written | no direct host comparison | Holds 2 to 64 RGBA8 samples per texel while the shader issues valid and invalid sample writes. |
| `result` | yes | yes, set 0 binding 1 | written | yes, through Amber `EXPECT` | Converts shader-side comparisons into a green pass image or red failure pixels. |
| Invocation IDs and local arrays | no | no | shader-local | no | Supply coordinates, partner IDs, and expected colors; they are not Vulkan resources. |

## What Is Checked

- `atomic` checks every sample of every texel against the expression encoded in its script, then requires every result pixel to equal RGBA `(0,255,0,255)`.
- `invalid_sample_index` reads only valid samples after issuing writes for sample operands from -256 through 255. It requires every valid sample to retain its assigned color and every result pixel to be green.
- The checks happen first in the compute shader and then in Amber. Amber does not inspect the multisample image directly.
- The R32 atomic oracle matches the scripted operations. The R64 oracle does not.
- The invalid-sample discard expectation lacks the robust-image feature requirement needed to derive that behavior from the inspected Vulkan specification.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `atomic`, `invalid_sample_index`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `atomic` | Incorrect per-sample storage-image addressing, atomic operation, or workgroup image-memory synchronization; for `storage_image_r64i` and `storage_image_r64ui`, the inspected expected-value mismatch is also a direct test-side cause. |
| `invalid_sample_index` | A valid sample changed or was read incorrectly after the mixed write loop; the test also relies on an out-of-bounds discard guarantee without enabling robust image access, so the result cannot be attributed to a conformance defect from the inspected requirements alone. |

## Important Variations and Special Cases

- `atomic` has signed and unsigned 32-bit cases plus signed and unsigned 64-bit cases. All use four samples and the same control flow. The 64-bit cases add `shaderInt64` and the 64-bit image extensions in GLSL.
- `invalid_sample_index` varies only the image sample count and its valid-color table. The scripts cover counts 2, 4, 8, 16, 32, and 64.
- The invalid-sample comments label the tested maximum as 256, but the loop condition `s < distortion` makes 255 the largest issued sample operand.
- The dispatcher excludes the whole `texture.multisample` test family from Vulkan SC. `createAtomicTests` also has its own Vulkan SC guard.
- C++ image requirements let the Amber case skip when the requested format, usage, extent, or sample count is unsupported.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and image requirements | [multisample registration](../../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L38-L156) | Defines both direct children, leaves, feature requirements, formats, sizes, and sample counts. |
| Parent dispatcher | [`createTextureTests`](../../../modules/vulkan/texture/vktTextureTests.cpp#L60-L66) | Registers `multisample` only outside Vulkan SC. |
| R32 atomic reference | [`storage_image_r32ui.amber`](../../../data/vulkan/amber/texture/multisample/atomic/storage_image_r32ui.amber) | Shows the complete atomic sequence and matching expected expression. |
| R64 oracle discrepancy | [`storage_image_r64ui.amber`](../../../data/vulkan/amber/texture/multisample/atomic/storage_image_r64ui.amber) | Shows the 64-bit operation masks and the inconsistent expected constant. |
| Invalid-sample reference | [`sample_count_4.amber`](../../../data/vulkan/amber/texture/multisample/invalidsampleindex/sample_count_4.amber) | Shows the issued sample range and valid-sample verification. |
| Amber compilation and support | [common Amber executor](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L193-L285) and [shader collection](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L436-L479) | Parses scripts, checks features and image support, and selects SPIR-V 1.0 by default. |
| Image coordinate rules | [Image Coordinate Validation](../../../../vulkan-docs/src/chapters/images.adoc#L42-L103) | Defines the sample index as an image coordinate and checks it against the sample count. |
| Image writes and atomics | [SPIR-V image writes and atomics](../../../../vulkan-docs/src/chapters/images.adoc#L236-L263) | Maps SPIR-V sample operands to image coordinates and describes image atomic pointers. |
| Out-of-bounds guarantee | [Robust Image Access](../../../../vulkan-docs/src/chapters/shaders.adoc#L2169-L2199) | States the condition under which out-of-bounds storage-image writes cannot modify memory. |

## Questions / Risk Points for User Audit

- The `invalid_sample_index` scripts require no robust-image feature even though their expected discard behavior depends on robust image access in the inspected specification. This remains a conformance-claim risk.
- Both R64 atomic scripts compare against `0x0a00000000000000`, which does not include the final OR/XOR result produced by their own operation sequence. This remains a test-oracle defect.
- The comments in all invalid-sample scripts say the tested maximum is 256, while the shaders stop at 255. The page uses the executed range.
