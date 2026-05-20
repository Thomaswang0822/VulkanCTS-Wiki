# vktSpvAsmImageSamplerTests

## Overview

Tests for SPIR-V Assembly image and sampler operations, including OpImageRead, OpImageFetch, OpImageSampleExplicitLod, OpImageSampleDrefImplicitLod, and OpImageSampleDrefExplicitLod. Tests various descriptor types (storage image, sampled image, combined image sampler, separate variables, separate descriptors) and test types (local variables, passing image/sampler to functions, OpTypeImage format mismatch).

## Role

Implementation file

## Source

- [vktSpvAsmImageSamplerTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.image_sampler
├── imageread
├── imagefetch
└── imagesample

spirv_assembly.instruction.graphics.image_sampler
├── imageread
├── imagefetch
├── imagesample
├── imagesample_dref_implicit_lod
└── imagesample_dref_explicit_lod
```

## Test Families

### imageread — OpImageRead tests

Tests OpImageRead with storage image descriptors. Only valid with `DESCRIPTOR_TYPE_STORAGE_IMAGE`. Tests all test types (local variables, pass image/sampler to function, optypeimage_mismatch) with depth property variations.

Observed in `addComputeImageSamplerTest()` at vktSpvAsmImageSamplerTests.cpp#L812 and `addGraphicsImageSamplerTest()` at vktSpvAsmImageSamplerTests.cpp#L1204.

### imagefetch — OpImageFetch tests

Tests OpImageFetch with sampled image, combined image sampler, and separate variable/descriptor configurations. Not valid with storage image descriptors.

Observed in compute loop at vktSpvAsmImageSamplerTests.cpp#L812 and graphics loop at vktSpvAsmImageSamplerTests.cpp#L1204.

### imagesample — OpImageSampleExplicitLod tests

Tests OpImageSampleExplicitLod with sampled image and combined image sampler configurations. Uses Lod operand with value 0.0.

Observed in compute loop at vktSpvAsmImageSamplerTests.cpp#L812 and graphics loop at vktSpvAsmImageSamplerTests.cpp#L1204.

### imagesample_dref_implicit_lod — OpImageSampleDrefImplicitLod tests (graphics only)

Tests depth comparison sampling with implicit LOD. Only present in graphics pipeline (fragment shader). Uses Bias operand.

Observed in `addGraphicsImageSamplerTest()` at vktSpvAsmImageSamplerTests.cpp#L1204.

### imagesample_dref_explicit_lod — OpImageSampleDrefExplicitLod tests (graphics only)

Tests depth comparison sampling with explicit LOD. Only present in graphics pipeline (fragment shader). Uses Lod operand.

Observed in `addGraphicsImageSamplerTest()` at vktSpvAsmImageSamplerTests.cpp#L1204.

Each read operation group contains descriptor type sub-groups, which contain test type sub-groups, which contain depth_property sub-groups.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| ReadOp | `imageread`, `imagefetch`, `imagesample`, `imagesample_dref_implicit_lod`, `imagesample_dref_explicit_lod` | Image read operation |
| DescriptorType | `storage_image`, `sampled_image`, `combined_image_sampler`, `combined_image_sampler_separate_variables`, `combined_image_sampler_separate_descriptors` | Descriptor type configuration |
| TestType | `all_local_variables`, `pass_image_to_function`, `pass_sampler_to_function`, `pass_image_and_sampler_to_function`, `optypeimage_mismatch` | How image/sampler variables are used |
| DepthProperty | `non_depth`, `depth`, `unknown` | Depth property of OpTypeImage |
| FormatDataForShaders | 12 format variants | Format mismatch data for `optypeimage_mismatch` tests (rgba8, rgba8snorm, rgba8ui, rgba8i, rgba16ui, rgba16i, rgba16f, r32ui, r32i, rgba32ui, rgba32i, rgba32f) |
| SpirvVersion | SPIR-V 1.0, SPIR-V 1.6 (nontemporal) | SPIR-V version with optional Nontemporal image operand |
| ShaderStage | vert, tessc, tesse, geom, frag (graphics only) | Graphics shader stage |

Not all combinations are valid; `isValidTestCase()` at vktSpvAsmImageSamplerTests.cpp#L90-L163 filters invalid combinations.

## Support Requirements

- **vertexPipelineStoresAndAtomics** — required for vertex, tessellation, and geometry stages in graphics tests — vktSpvAsmImageSamplerTests.cpp#L1292
- **fragmentStoresAndAtomics** — required for fragment stage in graphics tests — vktSpvAsmImageSamplerTests.cpp#L1313
- **tessellationShader** — implicitly required for tessellation control/evaluation stages
- **geometryShader** — implicitly required for geometry stage
- SPIR-V 1.6 requires `OpEntryPoint` interface declaration and `Block`/`StorageBuffer` decorations — vktSpvAsmImageSamplerTests.cpp#L884-L889

## Verification Methods

- **Default IO verification**: For standard tests, output buffer is compared against expected input data (the shader passes input image data to the output buffer) — vktSpvAsmImageSamplerTests.cpp#L869
- **nopVerifyFunction**: For `optypeimage_mismatch` tests, results are ignored (only checking for crashes) — vktSpvAsmImageSamplerTests.cpp#L782-L786
- **verifyDepthCompareResult**: For depth comparison (Dref) tests, verifies VK_COMPARE_OP_LESS semantics: D=1.0 if D<Dref, otherwise D=0.0 — vktSpvAsmImageSamplerTests.cpp#L1154-L1181

## Notes

- Compute tests only iterate through `READOP_IMAGEREAD` to `READOP_IMAGESAMPLE` (inclusive), while graphics tests iterate through all `READOP_LAST` values — vktSpvAsmImageSamplerTests.cpp#L812 vs #L1204
- Dref read operations are only present in fragment/compute shaders (not vertex/tessellation/geometry) — vktSpvAsmImageSamplerTests.cpp#L1289-L1291
- The `optypeimage_mismatch` tests use a deliberately mismatched format in OpTypeImage to verify the implementation handles format mismatches gracefully
