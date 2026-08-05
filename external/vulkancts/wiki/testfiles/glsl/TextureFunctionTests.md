## Overview

[`vktShaderRenderTextureFunctionTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1) implements `glsl.texture_functions`, the rendered GLSL suite for texture sampling, texel fetches, and texture queries. [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1272) attaches the factory to the GLSL package.

The file is both the registration point and the implementation. It builds lookup specifications and texture descriptions from case tables, generates vertex, fragment, or compute shaders, binds the requested texture, and compares shader output against CPU reference evaluation. Query tests use dedicated instances that validate returned dimensions, level counts, sample counts, or LOD values.

The default Vulkan mustpass contains 7,907 normalized leaves rooted at `dEQP-VK.glsl.texture_functions`; the Vulkan SC list contains 5,948 rooted at `dEQP-VKSC.glsl.texture_functions`. The difference comes from sparse variants that are excluded from Vulkan SC and from ordinary families for which sparse variants are available. Both lists contain the same 435 query leaves.

## Role

The suite checks the GLSL texture-function surface across sampler types, coordinate forms, mip selection, offsets, wrapping modes, shader stages, and sparse residency behavior. The test hierarchy follows function families. Offset families add wrap-mode subgroups and, where supported, `_pcoffset` branches that source the offset from a push constant.

## Source Code

- Primary source and factory: [`vktShaderRenderTextureFunctionTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4427-L8305)
- Public declarations: [`vktShaderRenderTextureFunctionTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.hpp#L1-L41)
- GLSL package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1272)
- Shared rendered-image harness: [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L658-L805)
- Vulkan mustpass coverage: [`vk-default/glsl.txt`](../../../mustpass/main/vk-default/glsl.txt)
- Vulkan SC mustpass coverage: [`vksc-default/glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt)

## Registration Hierarchy

```text
glsl.texture_functions
├── texture
├── textureclamp
├── textureoffset
├── textureoffset_pcoffset
├── textureoffsetclamp
├── textureoffsetclamp_pcoffset
├── textureproj
├── textureprojoffset
├── textureprojoffset_pcoffset
├── texturelod
├── texturelodoffset
├── texturelodoffset_pcoffset
├── textureprojlod
├── textureprojlodoffset
├── textureprojlodoffset_pcoffset
├── texturegrad
├── texturegradclamp
├── texturegradoffset
├── texturegradoffset_pcoffset
├── texturegradoffsetclamp
├── texturegradoffsetclamp_pcoffset
├── textureprojgrad
├── textureprojgradoffset
├── textureprojgradoffset_pcoffset
├── texelfetch
├── texelfetchoffset
├── texelfetchoffset_pcoffset
└── query
```

`createCaseGroup()` expands each table row into `_vertex`, `_fragment`, and `_compute` leaves according to its flags. It prefixes eligible ordinary leaves with `sparse_` when Vulkan SC is not being built ([expansion](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4948-L5007)). The tree omits generated wrap-mode and per-case levels.

## Test Families

### Sampling, projection, and explicit LOD

`texture` covers ordinary sampled lookups; `textureclamp` adds LOD clamping. `textureproj` covers projected lookup coordinate forms. `texturelod`, `textureprojlod`, and their offset forms provide explicit LOD. The case tables cover 2D, cube, 2D-array, 3D, 1D, 1D-array, and cube-array textures where a function signature permits them ([texture tables](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5059-L7012)).

The ordinary direct groups are created from their case tables, while offset branches are assembled in loops. Each offset family has `clamp_to_edge`, `clamp_to_border`, `repeat`, `mirrored_repeat`, and `mirrored` subgroups ([wrapping modes](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5009-L5022), [offset construction](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L6023-L6037)). `_pcoffset` variants substitute offset components from a push-constant block instead of embedding literals in the shader ([source generation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2072-L2090)).

### Explicit gradients and clamp variants

`texturegrad` and `textureprojgrad` supply explicit derivatives. `texturegradclamp` applies a LOD clamp; offset and offset-clamp variants combine these controls with the wrap-mode hierarchy. `GRAD_CASE_SPEC` and `GRADCLAMP_CASE_SPEC` store coordinate, derivative, offset, and clamp inputs in a `TextureLookupSpec` ([case-spec macros](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4436-L4476)).

The CPU evaluators calculate the lookup LOD from gradients, perform projection division for projected functions, and apply the configured minimum LOD for clamp cases ([gradient evaluators](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1180-L1260)).

### Integer texel fetches

`texelfetch` uses integer coordinates and an explicit mip level. `texelfetchoffset` and `texelfetchoffset_pcoffset` add literal or push-constant offsets beneath the same five wrap-mode group names, although fetch evaluation uses integer coordinates rather than filtered normalized sampling ([registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L7974-L8024), [shader input handling](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2081-L2088)).

### Texture queries

The `query` group holds `texturesize`, multisample `texturesizems`, `texturesamples`, `texturequerylevels`, and `texturequerylod` ([registration](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L8027-L8296)). Size, sample-count, and level queries generate vertex, fragment, and compute cases where supported by the source loops. Multisample-size queries are vertex/fragment only, and `texturequerylod` is fragment only ([query loops](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L8077-L8293)).

## Coverage Reconciliation

| Profile | Leaves | Notes |
|---|---:|---|
| Vulkan default | 7,907 | Includes eligible `sparse_` texture-function leaves |
| Vulkan SC default | 5,948 | Excludes sparse paths and has fewer ordinary leaves in sparse-capable families |
| Query subtree, both profiles | 435 | No sparse expansion |

The source names 28 direct children below `texture_functions`, including `query`. The mustpass lists contain generated stage, wrapping, case-table, and sparse descendants rather than only those direct children.

## Parameter Dimensions

| Dimension | Coverage |
|---|---|
| Function form | Ordinary, projected, explicit-LOD, explicit-gradient, LOD-clamp, texel-fetch, and query forms ([function enum](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L57-L102)) |
| Texture type | 2D, cube, 2D array, 3D, 1D, 1D array, and cube array where applicable ([texture specifications](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5059-L5312)) |
| Format and sampler | Normalized, float, signed/unsigned integer, and depth-comparison textures; nearest, linear, mipmapped, shadow, and fetch sampler configurations ([samplers](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5023-L5057)) |
| Texture layout | Single-level and mipmapped textures; offset tests use small textures to exercise offsets outside image extents ([specifications](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L5061-L5312)) |
| Offset source | Literal shader offsets and `_pcoffset` push-constant offsets |
| Wrap mode | `clamp_to_edge`, `clamp_to_border`, `repeat`, `mirrored_repeat`, and `mirrored` |
| Shader stage | Vertex, fragment, and compute, subject to case flags and support constraints ([case expansion](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4962-L5003)) |

## Support / Feature Requirements

| Requirement | Scope |
|---|---|
| `imageCubeArray` | Cube-array cases reject devices without the feature ([check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1431-L1439)) |
| `VK_KHR_portability_subset` / `mutableComparisonSamplers` | Comparison-sampler cases skip when portability subset lacks mutable comparison samplers ([helper](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1442-L1458)) |
| `VK_KHR_maintenance8` | Required for push-constant-offset lookup variants ([ordinary check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2047-L2053)) |
| `VK_KHR_compute_shader_derivatives` and `computeDerivativeGroupQuads` | Required by compute cases that use implicit derivatives, not explicit LOD or gradients ([check](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2054-L2065)) |
| Sparse textures | Sparse cases compile only outside Vulkan SC; sparse clamp cases also require `shaderResourceMinLod` ([sparse instance](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4478-L4505)) |

Push-constant-offset cases do not generate compute leaves because the source excludes `pcOffset` cases from the compute expansion ([condition](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4990-L5002)).

## Verification

For lookup families, `TexLookupEvaluator` invokes the table-selected CPU evaluator ([evaluator](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1409-L1428)). The shared ShaderRender instance renders the shader, computes the matching vertex or fragment reference image, and compares the images with fuzzy or pixel-threshold comparison ([iteration](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [comparison](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).

Sparse shaders call `sparse*ARB` functions, check `sparseTexelsResidentARB`, and write a distinct fallback color for nonresident results ([sparse shader generation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4774-L4868)).

`TextureQueryCase` selects a query-specific instance for size, multisample size, LOD, level-count, and sample-count functions ([instance selection](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L3988-L4005)). Those instances render query results and compare their integer or floating components with expected values; `TextureSizeInstance`, for example, derives dimensions by texture type and validates only legal LODs ([size validation](../../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2920-L3035)).

## Notes

- The documented hierarchy records canonical direct children. Source tables and loops create deeper case, stage, wrap-mode, and sparse descendants.
- Sparse coverage is intentionally absent from Vulkan SC builds because the sparse classes and their registration are under `#ifndef CTS_USES_VULKANSC`.
