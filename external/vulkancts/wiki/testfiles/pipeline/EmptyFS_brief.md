# Understanding Brief: EmptyFS

## One-Sentence Test Purpose

This test family checks whether graphics pipelines can omit the Fragment Shader or use a Fragment Shader with no outputs while retaining the expected depth-side effects.

## Background Knowledge

### Fragment Shader absence and no-output Fragment Shaders

A graphics pipeline can execute fragment operations without a Fragment Shader. The basic leaves compare depth data after drawing so they can observe the pre-rasterization and depth-test path without using color output. The empty-Fragment-Shader leaves create a `frag` module whose `main` has no outputs; no-Fragment-Shader leaves create no `frag` module.

### Depth samples and occlusion queries

Depth attachment writes can provide the oracle when a test has no useful color output. An occlusion query records passing samples, while the `masked_samples` leaf uses a compute program to fetch each sample from a multisampled depth image and write a result to an SSBO.

## One Concrete Example

For `dEQP-VK.pipeline.monolithic.empty_fs.masked_samples`, CTS creates an 8 x 8 depth/stencil image with four samples and a graphics pipeline with no Fragment Shader. Its sample mask is `0x5`, so samples 0 and 2 receive depth writes. After a depth-write to compute-read barrier, a compute shader fetches samples 0 through 3 at every pixel, stores `(sample0 + sample2) - (sample1 + sample3)` in an SSBO, and CTS requires each float to be within `[1.99, 2.01]`.

## End-to-End Test Flow

```text
[host] select a pipeline construction type and `empty_fs` test case leaf
[host] create depth attachment, render pass, pipeline resources, and generated shader modules
[host] create no Fragment Shader or create the no-output `frag` module for basic leaves
[host] record the graphics draw, with depth testing and writing enabled
[device] execute pre-rasterization and depth/sample operations without a color oracle
[host] copy depth, read the SSBO, and/or retrieve the occlusion query result
[host] compare the leaf-specific result and return pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Basic leaves generate `vert`; `tess_*` leaves also generate `tesc` and `tese`.
- `_empty_fs` leaves generate `frag`, with interpolated inputs and an empty `main`; `_no_fs` leaves omit it.
- `primitive_discard` generates a vertex program that assigns `gl_CullDistance`.
- `masked_samples` generates a vertex program and `comp`. The compute program reads the four depth samples and writes their selected-minus-unselected difference to an SSBO.
- The registration labels `geom_no_fs` and `geom_empty_fs` do not currently cause `geom` generation. [`createEmptyFSTests()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L804-L821) assigns `VK_SHADER_STAGE_VERTEX_BIT` to `geom`, while `lastIsGeometry()` accepts only `VK_SHADER_STAGE_GEOMETRY_BIT`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Basic depth image and transfer buffer | yes | yes | graphics writes depth; copy reads image | yes | The basic-leaf oracle is the 2 x 2 depth image. |
| Basic color image | yes | yes | render pass attaches and clears it | no | It supports the render-pass setup but is not validated. |
| Selective depth/stencil image | yes | yes | graphics writes depth; `comp` reads it for `masked_samples` | yes for `primitive_discard` | Stores the selective depth effects. |
| Vertex and index buffers | yes | yes | graphics draw reads them | no | Define the basic triangles or four quadrant triangles. |
| Query pool | yes | yes | graphics updates the occlusion count | yes | Checks surviving samples. |
| SSBO and descriptor set | yes, `masked_samples` only | yes | `comp` writes one float per pixel | yes | Carries the per-sample-depth check to the host. |

## What Is Checked

- Basic leaves compare copied 2 x 2 depth data with the reference depths `0`, `1/4`, `2/4`, and `3/4`, using `dsThresholdCompare` and threshold `0.000025`.
- `primitive_discard` requires the first and third depth-buffer quadrant centers to be near zero, the other two to remain near one, and a precise occlusion count of `32` when precise queries are supported.
- `masked_samples` requires every SSBO value to be within `[1.99, 2.01]` and a precise occlusion count of `128` when precise queries are supported.
- Without precise-query support, each selective-update leaf requires a nonzero query result instead of the exact count.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `vert_no_fs`, `vert_empty_fs`, `tess_no_fs`, `tess_empty_fs`, `geom_no_fs`, `geom_empty_fs`, `primitive_discard`, `masked_samples`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `vert_no_fs`, `vert_empty_fs` | Pipeline construction without a color-producing Fragment Shader, vertex-path depth writes, depth copyback, or depth comparison is incorrect. |
| `tess_no_fs`, `tess_empty_fs` | Tessellation-stage setup or execution, the absent/empty Fragment Shader path, depth writes, or readback is incorrect. |
| `geom_no_fs`, `geom_empty_fs` | The registered `geom` parameters currently select the vertex path; failure can involve that registration/selection, the absent/empty Fragment Shader path, depth writes, or readback. |
| `primitive_discard` | `gl_CullDistance` primitive selection, surviving depth coverage, occlusion-query accounting, or depth readback is incorrect. |
| `masked_samples` | The sample mask, multisampled depth writes, compute sample reads, SSBO result, or occlusion-query accounting is incorrect. |

## Important Variations and Special Cases

- The six basic leaves pair the labels `vert`, `tess`, and `geom` with `_no_fs` or `_empty_fs`; source behavior shows that the current `geom` parameter is a vertex-stage parameter.
- `tess_*` needs tessellation-related core features. `primitive_discard` needs `shaderCullDistance`.
- `primitive_discard` uses one sample and host depth copyback. `masked_samples` uses four samples, mask `0x5`, a compute readback program, and an SSBO.
- Vulkan default mustpass has 56 `empty_fs` entries: eight leaves under each of seven pipeline-construction roots. Vulkan SC mustpass has eight monolithic entries.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Basic pipeline and depth oracle | [`EmptyFSInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L101-L248) | Creates the basic resources, draws, copies depth, and compares it. |
| Selective-update execution | [`EmptyFSSelectiveDSUpdateInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L266-L577) | Creates the selective resources, barriers, query, and pass conditions. |
| Support requirements | [`EmptyFSCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L606-L622) | Gates tessellation, geometry, cull distance, and construction type. |
| Program generation | [`EmptyFSCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L624-L795) | Defines `frag`, `gl_CullDistance`, and `comp`. |
| Leaf registration | [`createEmptyFSTests()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L800-L829) | Defines the eight leaf names and their parameters. |
| Vulkan fragment operations | [fragment operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops) | Defines the relevant depth and sample-mask operation context. |
| Vulkan occlusion query | [occlusion query](../../../../vulkan-docs/src/chapters/queries.adoc#queries-occlusion) | Defines the sample-count observation used by selective leaves. |
| Vulkan default monolithic mustpass | [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt#L33409-L33416) | Shows the eight monolithic leaves. |

## Questions / Risk Points for User Audit

- Is the distinction between no Fragment Shader and a no-output Fragment Shader clear?
- Is the source-level `geom` registration mismatch clear enough to avoid claiming geometry-stage execution?
- Does the separate oracle for each leaf make the failure mapping understandable?

## Conversion Notes for Final Wiki Rewrite

- Keep the test case leaf as the behavior parameter.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Retain the `masked_samples` compute program as the representative shader walkthrough because it directly produces the SSBO oracle.
- Keep the `geom` registration mismatch in the final behavior and failure analysis.
