# Understanding Brief: `spirv_assembly.instruction.{compute,graphics}.image_sampler`

## One-Sentence Test Purpose

This test checks whether the implementation correctly executes SPIR-V image and sampler read instructions: `OpImageRead`, `OpImageFetch`, `OpImageSampleExplicitLod`, `OpImageSampleDrefImplicitLod`, and `OpImageSampleDrefExplicitLod`: across the descriptor encodings Vulkan allows (storage image, sampled image, combined image sampler, and the separate-variable / separate-descriptor variants), under both compute and graphics pipelines.

## Background Knowledge

### SPIR-V assembly authored in C++ string templates

Like every inline group in the `spirv_assembly` category, this test family builds shader modules from SPIR-V assembly text concatenated from C++ string fragments at test construction time ([`vktSpvAsmImageSamplerTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp)). There is no GLSL or HLSL frontend in the loop. A single compute builder ([`addComputeImageSamplerTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L788-L1028)) and a single graphics builder ([`addGraphicsImageSamplerTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1183-L1334)) concatenate the same set of helper strings (`getImageSamplerTypeStr`, `getImageReadOpStr`, `getFunctionDstVariableStr`, `getFunctionSrcVariableStr`, `getFunctionDstParamStr`, `getFunctionSrcParamStr`, `getFunctionParamTypeStr`, `getSamplerDecoration`, `getInterfaceList`) into a complete SPIR-V module whose only per-case variation is which read instruction is emitted and how the image/sampler variables are routed to a per-invocation `read_func`.

Why it matters here:
- The validator is the SPIR-V image/sampler instruction semantics itself, not a GLSL-to-SPIR-V translation the reader has to reverse-engineer.
- The shader text is the source of truth; small per-case differences live in which helper strings are concatenated, not in a separate shader per case.

### Image/sampler descriptor encodings exercised

The matrix iterates five `DescriptorType` values ([`getDescriptorName`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L216-L239)):

- `storage_image`: `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE`, no sampler, `OpTypeImage ... 2` (sampled=2, storage image).
- `sampled_image`: `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE` plus a separate `VK_DESCRIPTOR_TYPE_SAMPLER` at the next binding; the shader declares separate `%Image` and `%Sampler` variables and combines them with `OpSampledImage`.
- `combined_image_sampler`: one `VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER`; the shader declares one `%SampledImage` variable.
- `combined_image_sampler_separate_variables`: one combined descriptor at the Vulkan level, but the shader declares separate `%Image` and `%Sampler` variables that both read from the same binding, then combines them with `OpSampledImage`.
- `combined_image_sampler_separate_descriptors`: two combined descriptors at distinct bindings; the shader reads an image from binding 0 and a sampler from binding 1 (or vice versa for sampler decoration), then combines them.

Why it matters here:
- The matrix is intentionally constructed to drive every legal form of `OpTypeImage` / `OpTypeSampledImage` / `OpSampledImage` / `OpImage` / `OpLoad %Sampler` routing the SPIR-V spec permits for these five read instructions.
- A failure that localizes to one `DescriptorType` points at descriptor-encoding or variable-routing handling rather than at the read instruction itself.

### ReadOp and the Dref variant

`ReadOp` ([`getReadOpName`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L191-L214)) selects the SPIR-V instruction under test:

- `imageread`: `OpImageRead` against a storage image (`VK_FORMAT_R32G32B32A32_SFLOAT`).
- `imagefetch`: `OpImageFetch` against a sampled image (`VK_FORMAT_R32G32B32A32_SFLOAT`).
- `imagesample`: `OpImageSampleExplicitLod` with `Lod %c_f32_0` against a sampled image.
- `imagesample_dref_implicit_lod`: `OpImageSampleDrefImplicitLod` against a depth-comparison image (`VK_FORMAT_D32_SFLOAT`) with `Bias %c_f32_0` and a `%c_f32_0_5` reference value.
- `imagesample_dref_explicit_lod`: `OpImageSampleDrefExplicitLod` against the same depth image with `Lod %c_f32_0` and the same reference value.

The Dref variants are graphics-only and fragment-only (see `## Important Variations and Special Cases`). The compute builder iterates `READOP_IMAGEREAD..READOP_IMAGESAMPLE` only; the graphics builder iterates the full `READOP_LAST` range.

### TestType and the `optypeimage_mismatch` special case

`TestType` ([`getTestTypeName`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L166-L189)) selects how the image and sampler variables are routed to `read_func`:

- `all_local_variables`: `%InputData` (and `%SamplerData` when applicable) are loaded directly inside `read_func`.
- `pass_image_to_function`: the image is loaded in `main`/`test_code` and passed to `read_func` as a parameter.
- `pass_sampler_to_function`: the sampler is loaded in `main`/`test_code` and passed as a parameter.
- `pass_image_and_sampler_to_function`: both image and sampler are passed as parameters.
- `optypeimage_mismatch`: the `OpTypeImage` format declared in SPIR-V deliberately disagrees with the actual `VkFormat` of the bound image view (see `optypeimageFormatMismatchSpirvData`). The host replaces `verifyIO` with `nopVerifyFunction` so the test only checks execution stability, not output values.

Why it matters here:
- The `optypeimage_mismatch` subtree is the only branch where a mismatch between device output and host expected does **not** constitute failure; a crash or pipeline-creation failure is the failure signal.
- The pass-to-function variants exercise the SPIR-V function-parameter passing for opaque image and sampler types, which has historically been a fragile surface.

### `SpvAsmComputeShaderCase` and graphics shader utilities

The compute builder wraps each case in `SpvAsmComputeShaderCase`, which binds host-supplied input/output buffers as storage descriptors, dispatches `numWorkGroups` invocations, and compares the output buffer against an expected buffer. The graphics builder routes the same SPIR-V through `createTestForStage` for vertex, tessellation control, tessellation evaluation, geometry, and fragment stages, with `vertexPipelineStoresAndAtomics` or `fragmentStoresAndAtomics` requested depending on the stage.

Why it matters here:
- Default compute verification is byte equality between device-written output and host-supplied expected buffer; the `imageread`/`imagefetch`/`imagesample` cases expect the shader to copy input image data to the output buffer verbatim.
- The Dref cases replace byte equality with `verifyDepthCompareResult`, which checks `VK_COMPARE_OP_LESS` semantics: `D = 1.0 if D < Dref, otherwise D = 0.0`.
- The `optypeimage_mismatch` cases replace byte equality with `nopVerifyFunction`, which always returns `true`.

## One Concrete Example

The `compute.imageread.storage_image.all_local_variables.depth_property.non_depth` case is the smallest representative of the compute pattern. The shader declares a 2D storage image (`%Image = OpTypeImage %f32 2D 0 0 0 2 Rgba32f`) at descriptor set 0 binding 0, an output SSBO at binding 1, and a `read_func` that takes a `%u32` index, computes a `(row, col)` coordinate into `%coord = OpCompositeConstruct %v2u32 %row %col`, loads the storage image, and stores the result to `OutputData[0][ndx]`. The host fills the input image with 64 random `vec4` values, expects the output buffer to equal that input byte-for-byte, and dispatches `64×1×1` invocations.

```text
; excerpt of read_func (full module under #### Source Code in the page)
       %func_img = OpLoad %Image %InputData
           %color = OpImageRead %v4f32 %func_img %coord
                 %36 = OpAccessChain %_ptr_Uniform_v4type %OutputData %c_u32_0 %func_ndx
                       OpStore %36 %color
```

This case is representative because `OpImageRead` against a storage image is the simplest read path (no sampler, no `OpSampledImage`), so the walkthrough exposes the shared shell without distraction. Other readOp values add `%SamplerData` declarations and `OpSampledImage`/`OpImage` recombination but keep the same preamble, dispatch shape, and verification flow.

## End-to-End Test Flow

```text
[host] choose readOp, descriptorType, testType, depthProperty (and shaderStage for graphics)
[host] build SPIR-V assembly text by concatenating per-case helper strings
[host] compile assembly to a shader module at program-build time
[host] create input image(s) and sampler(s) from host-supplied vec4 data (depth uses 1 component)
[host] create output SSBO sized to numDataPoints (64) and zero it
[host] bind descriptor set 0: image at binding 0, sampler at binding 1 (when applicable), output at binding N
[host] compute dispatch numWorkGroups (64×1×1) or graphics draw
[device] each invocation reads coord (row, col) from its index, runs the per-case read op, writes output[id]
[host] invalidate output memory, read back bytes
[host] compare output to expected: byte equality (default), verifyDepthCompareResult (Dref), or nopVerifyFunction (mismatch)
[host] return pass/fail
```

For graphics cases the host additionally creates a render target and pairs the test shader with fixed-function vertex/fragment (or geometry/tessellation) stages through `createTestForStage`; verification is per-SSBO-element rather than per-pixel.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline SPIR-V assembly text concatenated from C++ string helpers (the only program artifact for this family).
- The compute SPIR-V 1.6 path (`_nontemporal` postfix) appends `Nontemporal` to the image read operand and switches the output encoding from `Uniform`+`BufferBlock` to `StorageBuffer`+`Block` with an explicit `OpEntryPoint` interface list ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L873-L889)).
- The graphics SPIR-V body is split into `pre_main`, `decoration`, and `testfun` fragments assembled by [`generateGraphicsImageSamplerSource`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1030-L1152) and merged with the standard graphics shader utility template.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input image (`%InputData`, `UniformConstant`) | yes (filled with 64 random `vec4`, or 16 for depth) | yes (descriptor set 0, binding 0) | read by shader | no | Carries the texel data the read op consumes |
| Second input image (`%InputData2`, separate-descriptors only) | yes (filled with `1.0 - inputData`) | yes (descriptor set 0, binding 1) | read by shader | no | Carries alternate image data so the shader can pull image and sampler from different bindings |
| Sampler (`%SamplerData`, `UniformConstant`) | yes (sampler object) | yes (descriptor set 0, binding 1 for `sampled_image`; binding 0 for `combined_image_sampler_separate_variables`) | read by shader | no | Provides sampler state for `imagefetch`/`imagesample`/Dref |
| Output SSBO (`%OutputData`, `Uniform`/`StorageBuffer`) | yes (zeroed) | yes (descriptor set 0, last binding) | written by shader | yes | Carries the per-invocation read result; compared against expected buffer |
| `gl_GlobalInvocationID` (`%id`, Input) for compute | n/a (built-in) | n/a | read by shader | no | Per-invocation index into the SSBO |
| Graphics vertex/index/color attachments | yes (graphics utilities) | yes | read/written by pipeline | yes (per-pixel or per-attachment) | The graphics path requires a render target even though the test signal lives in the output SSBO |

## What Is Checked

- **Default (compute and graphics non-Dref, non-mismatch):** exact byte equality between the device-written output SSBO and the host-supplied input image data. The shader is expected to copy `input[id]` to `output[id]` byte-for-byte.
- **`verifyDepthCompareResult` (Dref cases):** for each element, `D = 1.0 if D < Dref, otherwise D = 0.0` where `Dref = 0.5`. The host checks `(input < 0.5 && result == 0.0) || (input >= 0.5 && result == 1.0)` and fails on any element that violates `VK_COMPARE_OP_LESS` semantics ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1154-L1181)).
- **`nopVerifyFunction` (`optypeimage_mismatch`):** always returns `true`. The test passes if the shader compiles, the pipeline is created, and the dispatch/draw completes without crashing; the output buffer is ignored.
- **`isValidTestCase` filtering:** combinations that the SPIR-V/Vulkan spec disallow are not registered. Specifically, `imageread` is only valid with `storage_image`; `imagefetch`/`imagesample`/Dref are not valid with `storage_image`; `pass_image_to_function`/`pass_sampler_to_function`/`pass_image_and_sampler_to_function` are not valid with `combined_image_sampler`; `optypeimage_mismatch` is not valid with Dref ops ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L90-L163)).

## Behavior Parameter Identification

> **Behavior parameter:** `ReadOp` (the test family leaf path component below `image_sampler`, registered as `imageread`, `imagefetch`, `imagesample`, `imagesample_dref_implicit_lod`, `imagesample_dref_explicit_lod`)
>
> **Candidate values:** `imageread`, `imagefetch`, `imagesample`, `imagesample_dref_implicit_lod`, `imagesample_dref_explicit_lod`

The page's `## Behavior Parameters` subsections explain each readOp at the level of which SPIR-V instruction is exercised, which descriptor encodings are valid for it, and which verification rule applies. The compute/graphics split and the `DescriptorType` × `TestType` × `DepthProperty` matrix are presented in `## Parameter Dimensions and Observed Values` rather than as separate behavioral axes because they are configuration dimensions that modulate the same readOp behavior rather than distinct properties.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `imageread` (compute or graphics) | `OpImageRead` against a storage image returns wrong texel data; storage-image descriptor binding or `OpTypeImage` (sampled=2) mishandled; `coord` computation wrong; host input image fill or expected buffer wrong; byte-equality mismatch on a single element |
| `imagefetch` (compute or graphics) | `OpImageFetch` against a sampled image returns wrong texel data; `OpImage` extraction from a combined image sampler wrong; separate-variable or separate-descriptor sampler routing wrong; `pass_sampler_to_function` / `pass_image_to_function` function-parameter passing wrong |
| `imagesample` (compute or graphics) | `OpImageSampleExplicitLod` with `Lod 0.0` returns wrong texel data; `OpSampledImage` recombination wrong; sampler state wrong; `coordf`/`normalcoordf` coordinate normalization wrong; SPIR-V 1.6 `Nontemporal` operand mishandled (compute `_nontemporal` variant) |
| `imagesample_dref_implicit_lod` (graphics, fragment only) | `OpImageSampleDrefImplicitLod` returns wrong depth-comparison result; depth image (`VK_FORMAT_D32_SFLOAT`) layout or `OpTypeImage ... Depth=1` declaration wrong; `Bias 0.0` or `Dref 0.5` operand mishandled; `verifyDepthCompareResult` host check wrong; non-fragment stage registered for Dref (would be a CTS bug, not a driver bug) |
| `imagesample_dref_explicit_lod` (graphics, fragment only) | `OpImageSampleDrefExplicitLod` returns wrong depth-comparison result; `Lod 0.0` operand mishandled; otherwise same class as the implicit-LOD variant |

A cross-cutting cause shared by every readOp: the `optypeimage_mismatch` subtree of each readOp deliberately declares an `OpTypeImage` format that disagrees with the bound `VkFormat`. A failure there means the implementation crashed or refused pipeline creation; output bytes are ignored. This is the only branch where a value mismatch is not a failure.

### Cause Analysis

Detailed `### Cause Analysis` is written fresh during the Level-3 rewrite; the brief stops at the cause mapping above.

## Important Variations and Special Cases

- **Dref is graphics-only and fragment-only.** The graphics builder registers `imagesample_dref_implicit_lod` and `imagesample_dref_explicit_lod` test families but skips vertex, tessellation, and geometry stages for them; only `shader_frag` cases are emitted ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1289-L1316)). The compute builder does not register Dref families at all (its loop stops at `READOP_IMAGESAMPLE`).
- **SPIR-V 1.6 `_nontemporal` variant (compute only).** Each compute case is registered twice: once at SPIR-V 1.0 with the default `Uniform`+`BufferBlock` output encoding, and once at SPIR-V 1.6 with `StorageBuffer`+`Block`, an explicit `OpEntryPoint` interface list (returned by `getInterfaceList`), and a `Nontemporal` image operand appended to the read op ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L802-L810), [source](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L873-L889)). The `_nontemporal` variant only applies to `imageread`/`imagefetch`/`imagesample` since the compute loop stops at `READOP_IMAGESAMPLE`.
- **`optypeimage_mismatch` matrix.** The mismatch subtree iterates all 12 entries in `optypeimageFormatMismatchSpirvData`: each entry pairs a real `VkFormat` (e.g. `VK_FORMAT_R8G8B8A8_UNORM`) with a deliberately wrong SPIR-V `OpTypeImage` format (e.g. `Rgba16f`). The shader is registered once per format under `optypeimage_mismatch_<formatname>` (e.g. `optypeimage_mismatch_rgba8`). The mismatch subtree is not registered for Dref ops ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L153-L157)).
- **`combined_image_sampler_separate_descriptors` second image.** The host fills a second image with `1.0 - inputData` so that pulling the image from binding 0 versus binding 1 produces observably different output. This catches descriptor-indexing bugs that would otherwise be masked by identical data.
- **`DepthProperty` (`non_depth`, `depth`, `unknown`).** Drives the third argument to `OpTypeImage` (`0`, `1`, `2` respectively). For Dref ops, the SPIR-V format is forced to `R32f` regardless of `DepthProperty` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L667-L669)); for non-Dref ops the default is `Rgba32f`.
- **Feature requirements.** Non-Dref graphics cases for vertex/tessellation/geometry stages require `vertexPipelineStoresAndAtomics`; fragment cases require `fragmentStoresAndAtomics` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1289-L1316)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `addComputeImageSamplerTest`: compute builder | [`vktSpvAsmImageSamplerTests.cpp#L788-L1028`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L788-L1028) | Iterates `ReadOp` × `DescriptorType` × `TestType` × `FormatData` × `SpirvVersion` × `DepthProperty` and concatenates the SPIR-V module |
| `addGraphicsImageSamplerTest`: graphics builder | [`vktSpvAsmImageSamplerTests.cpp#L1183-L1334`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1183-L1334) | Iterates the full `ReadOp` range and dispatches to `createTestForStage` per stage |
| `isValidTestCase`: combination filter | [`vktSpvAsmImageSamplerTests.cpp#L90-L163`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L90-L163) | Encodes the SPIR-V/Vulkan rules for which `ReadOp` × `DescriptorType` × `TestType` combinations are legal |
| `getImageReadOpStr`: per-readOp SPIR-V body | [`vktSpvAsmImageSamplerTests.cpp#L628-L656`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L628-L656) | Returns the SPIR-V instruction string for each `ReadOp`, including the `Nontemporal` operand for SPIR-V 1.6 |
| `getImageSamplerTypeStr`: image/sampler type declarations | [`vktSpvAsmImageSamplerTests.cpp#L664-L730`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L664-L730) | Returns the `OpTypeImage`/`OpTypeSampler`/`OpTypeSampledImage`/`OpVariable` block per `DescriptorType` |
| `getFunctionDstVariableStr` / `getFunctionSrcVariableStr`: variable routing | [`vktSpvAsmImageSamplerTests.cpp#L301-L445`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L301-L445), [`vktSpvAsmImageSamplerTests.cpp#L448-L523`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L448-L523) | Per-`TestType` routing of image/sampler variables between `main`/`test_code` and `read_func` |
| `optypeimageFormatMismatchSpirvData`: mismatch matrix | [`vktSpvAsmImageSamplerTests.cpp#L610-L625`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L610-L625) | 12-entry table of real `VkFormat` ↔ wrong SPIR-V `OpTypeImage` format pairings |
| `verifyDepthCompareResult`: Dref verification | [`vktSpvAsmImageSamplerTests.cpp#L1154-L1181`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1154-L1181) | Implements the `VK_COMPARE_OP_LESS` host check for Dref cases |
| `nopVerifyFunction`: mismatch verification | [`vktSpvAsmImageSamplerTests.cpp#L781-L786`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L781-L786) | Always-true verifier for `optypeimage_mismatch` cases |
| `createImageSamplerComputeGroup` / `createImageSamplerGraphicsGroup`: registration roots | [`vktSpvAsmImageSamplerTests.cpp#L1337-L1354`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1337-L1354) | Top-level entrypoints called from the `spirv_assembly.instruction` aggregator |

## Questions / Risk Points for User Audit

- Is `ReadOp` the right primary behavioral axis, or should the page split compute vs. graphics as the primary axis and treat `ReadOp` as a secondary axis per pipeline variant?
- Is one representative walkthrough (`compute.imageread.storage_image.all_local_variables.depth_property.non_depth`) enough, or should a second walkthrough cover a Dref case to make the `verifyDepthCompareResult` story concrete?
- Should the `optypeimage_mismatch` matrix be enumerated as a separate behavioral group, or stay as a `TestType` dimension that modulates every readOp?
- Is the SPIR-V 1.6 `_nontemporal` variant worth a separate `#### Parameter Variation Summary` row, or is a single bullet enough?
- The compute builder dispatches `numWorkGroups = (64,1,1)` but the shader reads `gl_GlobalInvocationID.x` only. Is this worth calling out in the page, or is it implicit in the dispatch shape?

## Conversion Notes for Final Wiki Rewrite

- Carry `### Failure Cause Mapping` directly into the final page's `### Failure Cause Mapping`.
- Distill Background Knowledge into a short bullet list: SPIR-V-assembly-in-C++-templates, image/sampler descriptor encodings, ReadOp and Dref variant, `SpvAsmComputeShaderCase`/graphics shader utilities with the three verification rules (byte equality / `verifyDepthCompareResult` / `nopVerifyFunction`).
- Use `compute.imageread.storage_image.all_local_variables.depth_property.non_depth` as the single representative shader walkthrough. Extract the SPIR-V assembly from the C++ string-template concatenation in `addComputeImageSamplerTest` (SPIR-V 1.0 path) and place it under `#### Source Code` (unfoldable, no `#### SPIR-V` subsection per the spirv_assembly deviation).
- The `optypeimage_mismatch` and Dref variations are explained in `## Behavior Parameters` and `## Failure Meaning` prose, not as additional walkthroughs.
- The page must start with `## Overview` (no top-level `#` title); the output filename is `ImageSamplerTests.md`.
- Compute/graphics split goes in `## Registration Hierarchy` and `## Parameter Dimensions and Observed Values`, not in `## Behavior Parameters` (which is per-readOp).
- The Dref-fragment-only and SPIR-V-1.6-`_nontemporal`-compute-only pruning rules belong in `## Case Pruning`.
