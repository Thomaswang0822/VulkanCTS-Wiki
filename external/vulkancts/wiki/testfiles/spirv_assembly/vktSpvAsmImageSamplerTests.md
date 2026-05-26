# vktSpvAsmImageSamplerTests

## Overview

Tests for SPIR-V Assembly image and sampler operations, including `OpImageRead`, `OpImageFetch`, `OpImageSampleExplicitLod`, `OpImageSampleDrefImplicitLod`, and `OpImageSampleDrefExplicitLod`. Compute registration covers read/fetch/sample operations while graphics registration covers all read operations, including Dref variants ([addComputeImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L788-L824), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1183-L1219)). Descriptor and test-type combinations are filtered by [isValidTestCase()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L90-L163).

## Role

Implementation file

## Source

- [vktSpvAsmImageSamplerTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1337)

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

Tests `OpImageRead` with storage image descriptors. The validity filter permits `READOP_IMAGEREAD` only with `DESCRIPTOR_TYPE_STORAGE_IMAGE` ([isValidTestCase()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L120-L126)).

Observed in the compute read-operation loop and graphics read-operation loop ([addComputeImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L812-L824), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1204-L1219)).

### imagefetch — OpImageFetch tests

Tests `OpImageFetch` with sampled image, combined image sampler, and separate variable/descriptor configurations. The validity filter excludes storage-image descriptors for `READOP_IMAGEFETCH` ([isValidTestCase()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L128-L134)).

Observed in the compute and graphics read-operation loops ([addComputeImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L812-L824), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1204-L1219)).

### imagesample — OpImageSampleExplicitLod tests

Tests `OpImageSampleExplicitLod` with sampled image and combined-image sampler configurations. The validity filter groups `READOP_IMAGESAMPLE` with sampled/combined descriptor forms ([isValidTestCase()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L136-L144)).

Observed in the compute and graphics read-operation loops ([addComputeImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L812-L824), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1204-L1219)).

### imagesample_dref_implicit_lod — OpImageSampleDrefImplicitLod tests (graphics only)

Tests depth-comparison sampling with implicit LOD. The graphics loop registers Dref read operations, and non-fragment stages are skipped for Dref operations so only fragment-stage cases are emitted ([addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1204-L1219), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1289-L1316)).

Observed in [`addGraphicsImageSamplerTest()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1204-L1219).

### imagesample_dref_explicit_lod — OpImageSampleDrefExplicitLod tests (graphics only)

Tests depth-comparison sampling with explicit LOD. The graphics loop registers Dref read operations, and non-fragment stages are skipped for Dref operations so only fragment-stage cases are emitted ([addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1204-L1219), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1289-L1316)).

Observed in [`addGraphicsImageSamplerTest()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1204-L1219).

Each read operation group contains descriptor type sub-groups, which contain test type sub-groups, which contain depth_property sub-groups.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| ReadOp | `imageread`, `imagefetch`, `imagesample`, `imagesample_dref_implicit_lod`, `imagesample_dref_explicit_lod` | Image read operation |
| DescriptorType | `storage_image`, `sampled_image`, `combined_image_sampler`, `combined_image_sampler_separate_variables`, `combined_image_sampler_separate_descriptors` | Descriptor type configuration |
| TestType | `all_local_variables`, `pass_image_to_function`, `pass_sampler_to_function`, `pass_image_and_sampler_to_function`, `optypeimage_mismatch` | How image/sampler variables are used |
| DepthProperty | `non_depth`, `depth`, `unknown` | Depth property of OpTypeImage |
| FormatDataForShaders | 12 format variants | Format mismatch data for `optypeimage_mismatch` tests ([optypeimageFormatMismatchSpirvData](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L610-L625)) |
| SpirvVersion | SPIR-V 1.0, SPIR-V 1.6 (`_nontemporal`) | SPIR-V versions iterated by compute cases ([addComputeImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L802-L810)) |
| ShaderStage | vert, tessc, tesse, geom, frag (graphics only) | Graphics shader stage |

Not all combinations are valid; [`isValidTestCase()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L90-L163) filters invalid combinations.

## Support Requirements

- **`vertexPipelineStoresAndAtomics`** — requested for vertex, tessellation, and geometry stages in non-Dref graphics tests ([addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1289-L1296))
- **`fragmentStoresAndAtomics`** — requested for fragment-stage graphics tests ([addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1312-L1316))
- **Tessellation shader stages** are included through `createTestForStage()` calls for tessellation control/evaluation in non-Dref graphics tests ([addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1298-L1305))
- **Geometry shader stage** is included through a `createTestForStage()` call for non-Dref graphics tests ([addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1307-L1309))
- SPIR-V 1.6 path uses an `OpEntryPoint` interface list and switches output decoration/storage class to `Block`/`StorageBuffer` ([addComputeImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L873-L889))

## Verification Methods

- **Default IO verification**: standard tests expect the shader to pass input image data to the output buffer ([addComputeImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L868-L869), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1261-L1263))
- **`nopVerifyFunction`**: for `optypeimage_mismatch` tests, results are ignored so the test only checks execution stability ([nopVerifyFunction()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L781-L786), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1267-L1273))
- **`verifyDepthCompareResult`**: for depth-comparison (Dref) tests, verifies the source-commented `VK_COMPARE_OP_LESS` semantics ([verifyDepthCompareResult()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1154-L1181))

## Notes

- Compute tests only iterate through `READOP_IMAGEREAD` to `READOP_IMAGESAMPLE` inclusive, while graphics tests iterate through all `READOP_LAST` values ([addComputeImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L812-L814), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1204-L1206))
- For graphics Dref read-operation groups, the source skips vertex, tessellation, and geometry stages and emits only fragment-stage cases; the compute registration does not include Dref read-operation groups ([addComputeImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L812-L814), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1289-L1316))
- The `optypeimage_mismatch` tests use alternate format data and `nopVerifyFunction`; the documented purpose is execution stability rather than output-value checking ([addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1221-L1237), [addGraphicsImageSamplerTest()](../../../modules/vulkan/spirv_assembly/vktSpvAsmImageSamplerTests.cpp#L1267-L1273))
