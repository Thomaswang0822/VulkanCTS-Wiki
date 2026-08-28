# Understanding Brief: Uniform descriptor indexing

## One-Sentence Test Purpose

This test checks whether fragment shaders can access descriptor arrays with an index that is uniform within each subgroup for nine descriptor families, while the selected descriptor varies between subgroups of the draw.

## Background Knowledge

### Dynamically uniform descriptor selection

A fragment shader invocation can compute a different candidate descriptor index from its fragment coordinates. The shader then uses `subgroupBroadcastFirst()` to select the first invocation's index and peels that selected index from the subgroup before accessing the descriptor array. The access is therefore uniform within the subgroup even though different subgroups can select different descriptors. Vulkan's descriptor-indexing features define which descriptor-array classes may be indexed by non-uniform integer expressions, while `runtimeDescriptorArray` enables runtime-sized descriptor arrays ([descriptor-indexing features](../../../../vulkan-docs/src/chapters/features.adoc#L2004-L2077), [runtime descriptor arrays](../../../../vulkan-docs/src/chapters/features.adoc#L2141-L2145)).

Why it matters here:
- The test exercises descriptor-array selection without adding `nonuniformEXT(i)` to the access. The subgroup operation is the central behavior being checked.
- The descriptor type changes the shader declaration and access operation, but the fragment-coordinate-generated selection and subgroup peeling remain shared.
- The first subgroup index is not a single global device choice. It is a subgroup-scoped value, so the output can contain several descriptor colors across the 32 by 32 draw.

### Descriptor resources and fragment subgroups

A descriptor is a shader-visible reference to a buffer, buffer view, image view, sampler, or input attachment. The descriptor array element must still be valid for the descriptor type and shader stage. A subgroup is the implementation-defined set of fragment invocations in which subgroup operations such as `subgroupBroadcastFirst` are defined; this page does not treat a subgroup as a test hierarchy term ([subgroup scope](../../../../vulkan-docs/src/chapters/shaders.adoc#L3239-L3269)).

Why it matters here:
- The host creates and fills resources with descriptor-specific APIs, then writes one descriptor array binding at set 0, binding 0.
- Input attachments are render-pass attachments, not ordinary sampled images. They are loaded through `subpassInput` and require input-attachment render-pass wiring.
- Sampler and sampled-image cases add one auxiliary descriptor of the other type so the shader can construct a sampled image; this auxiliary descriptor is not the tested array.

## One Concrete Example

Consider `dEQP-VK.subgroups.uniform_descriptor_indexing.storage_buffer`. The host creates four host-visible storage buffers. Each buffer contains a repeated float color, with descriptor `i` initialized to `clearColors[1 + i % 4]`. The fragment shader computes a pseudo-random `materialIndex` in `[0, 3]`, broadcasts the first invocation's index to `i`, and reads `data[i].c` only for invocations whose own candidate equals the broadcast value. The fragment writes that float to the R8 color attachment. Different subgroups can therefore expose different descriptor colors, while every descriptor access within a subgroup uses one index.

## End-to-End Test Flow

```text
[host] select one descriptor family from the caseList and load its descriptor count, resource counts, and minimum group count
[host] require subgroup and descriptor-indexing support in the ordered checkSupport() gates
[host] create the 32 by 32 R8 color attachment and descriptor-family-specific buffers, buffer views, images, samplers, or input attachments
[host] fill descriptor resources with clearColors 1 through descriptorCount and update set 0, binding 0 as a descriptor array
[host] add the auxiliary sampled-image or sampler descriptor required by the sampler and sampled_image families
[host] generate the vertex and specialized fragment GLSL programs and request SPIR-V 1.3
[host] record image clears, buffer visibility barriers, one triangle draw, color-image copyback, and submit the command buffer
[device] compute a fragment-coordinate-derived candidate descriptor index
[device] broadcast the first candidate index in each subgroup and access the selected descriptor when the index matches
[device] write the selected resource value to the fragment color output
[host] count byte values in the copied 32 by 32 output image and decide pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms()` specializes one fragment template using the selected descriptor family's declaration, descriptor count, access expression, extra declarations, and layout qualifier ([`UniformDescriptorIndexingTestCase::initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L686-L774)).
- Every fragment variant enables `GL_KHR_shader_subgroup_ballot` and `GL_EXT_nonuniform_qualifier`, declares `layout(location = 0) out highp float fragColor`, computes the same cosine-based `noize`, and uses `subgroupBroadcastFirst` before the descriptor access.
- `ShaderBuildOptions` explicitly requests SPIR-V 1.3, so the generated fragment artifact is not inferred from the runtime Vulkan version.
- The vertex shader is a fixed full-frame triangle producer. The descriptor family changes only the fragment specialization and host resource path.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Descriptor array at set 0, binding 0 | yes | yes | read | no | The tested array whose element is selected by subgroup-uniform `i`. |
| Storage buffers | yes, four buffers | yes | fragment read | no | Each buffer stores one repeated float color for `storage_buffer`. |
| Uniform buffer | yes, one buffer with aligned ranges | yes | fragment read | no | Twelve descriptor elements point at aligned float ranges in one backing buffer. |
| Storage or uniform texel buffer views | yes, one backing buffer plus 16 views | yes | fragment read | no | `imageLoad` or `texelFetch` reads the selected R8 texel-buffer view. |
| Sampled images and samplers | yes | yes | fragment sample | no | The sampled-image, sampler, and combined-image-sampler families use descriptor-specific image and sampler arrangements. |
| Storage images | yes, four 3 by 3 images | yes | fragment read | no | `imageLoad` reads the selected `r8` storage image. |
| Input attachments | yes, four 32 by 32 images and render-pass attachments | yes | fragment read | no | `subpassLoad` reads the selected input attachment in the active subpass. |
| Color attachment and copyback buffer | yes, 32 by 32 R8 image with host-visible backing buffer | yes | fragment write, transfer read | yes | Carries the per-fragment descriptor colors to the host-side result map. |

## What Is Checked

- The host copies the 32 by 32 R8 output image and counts the distinct byte values in `resultMap`.
- A result passes only when no fragment retains background value `0`, the number of distinct groups is at least the family-specific `minGroupsCount`, and it is no greater than `descriptorCount` ([`iterate()` result check](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L353-L378)).
- A failure with background pixels reports the number of pixels whose value is zero. Otherwise it reports the observed number of groups and the expected lower and upper bounds.
- The source notes that the minimum group thresholds were chosen from implementation results because the number of returned groups depends on image size and shader noise. The check is therefore a bounded observable-color check, not a requirement that every descriptor appear.

## Behavior Parameter Identification

> **Behavior parameter:** descriptor family
>
> **Candidate values:** `storage_buffer`, `storage_texel_buffer`, `uniform_texel_buffer`, `storage_image`, `sampler`, `sampled_image`, `combined_image_sampler`, `uniform_buffer`, `input_attachment`

The descriptor family is the primary behavioral axis because each value changes the descriptor type, GLSL declaration, access expression, host resource creation, descriptor count, and minimum accepted color-group count. The nine values are registered in this exact order by `caseList`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `storage_buffer` | Storage-buffer descriptor-array indexing or buffer-backed value propagation produced an invalid or insufficient set of output color groups. |
| `storage_texel_buffer` | Storage-texel-buffer view indexing, R8 texel loading, or descriptor-specific resource setup produced an invalid or insufficient set of output color groups. |
| `uniform_texel_buffer` | Uniform-texel-buffer view indexing, texel loading, or descriptor-specific resource setup produced an invalid or insufficient set of output color groups. |
| `storage_image` | Storage-image descriptor-array indexing, image layout, or `imageLoad` behavior produced an invalid or insufficient set of output color groups. |
| `sampler` | Sampler-array indexing or construction of the sampled image from the selected sampler and auxiliary texture produced an invalid or insufficient set of output color groups. |
| `sampled_image` | Sampled-image-array indexing or construction of the sampled image from the selected image and auxiliary sampler produced an invalid or insufficient set of output color groups. |
| `combined_image_sampler` | Combined-image-sampler descriptor-array indexing or sampling of the selected image and sampler pair produced an invalid or insufficient set of output color groups. |
| `uniform_buffer` | Uniform-buffer descriptor-array indexing, aligned range setup, or buffer-backed value propagation produced an invalid or insufficient set of output color groups. |
| `input_attachment` | Input-attachment descriptor-array indexing, render-pass attachment wiring, or `subpassLoad` behavior produced an invalid or insufficient set of output color groups. |

## Important Variations and Special Cases

- The exact `caseList` order is `storage_buffer`, `storage_texel_buffer`, `uniform_texel_buffer`, `storage_image`, `sampler`, `sampled_image`, `combined_image_sampler`, `uniform_buffer`, and `input_attachment` ([`caseList`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L786-L829)).
- Buffer families use four storage buffers, one uniform buffer with twelve aligned descriptor ranges, or one texel-buffer allocation with sixteen views. The uniform-buffer case uses `minUniformBufferOffsetAlignment`; texel-buffer views use the device's texel-buffer alignment features when available.
- Image families use 3 by 3 R8 images except input attachments, which use 32 by 32 images to match the framebuffer. Storage images use `VK_IMAGE_LAYOUT_GENERAL`; other descriptor-image paths use `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`.
- The sampler family has one auxiliary sampled image and four samplers. The sampled-image family has one auxiliary sampler and sixteen sampled images. Combined image samplers carry image and sampler together in each descriptor element.
- Only the tested descriptor array uses binding 0. The sampler and sampled-image families add the complementary descriptor at binding 4 or binding 16 to complete `sampler2D` construction.
- The entire branch is absent from VulkanSC builds because both the include and the registration call are inside `#ifndef CTS_USES_VULKANSC`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registered descriptor families | [`caseList`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L786-L829) | Defines all nine direct children and their exact order. |
| Shader specialization | [`UniformDescriptorIndexingTestCase::initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L686-L774) | Defines the template and all nine declaration/access specializations. |
| Support gates | [`UniformDescriptorIndexingTestCase::checkSupport()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L625-L684) | Defines the ordered common and descriptor-specific feature requirements. |
| Descriptor-family configuration | [`iterate()` configurationMap](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L103-L139) | Defines descriptor counts, resource counts, and minimum accepted group counts. |
| Resource construction and updates | [`iterate()` setup](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L141-L270) | Creates family-specific resources and writes the descriptor set. |
| Buffer and image helpers | [`setupImages()` and buffer helpers](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L438-L581) | Defines image sizes, buffer contents, alignment, and buffer-view ranges. |
| Command execution | [`iterate()` draw and copy](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L284-L351) | Defines barriers, render-pass draw, copyback, and queue completion. |
| Host-side result | [`iterate()` result classification](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L353-L378) | Counts colors and emits pass/fail status. |
| Category dispatcher | [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L81) | Establishes the non-VulkanSC registration boundary. |
| Mustpass coverage | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L47808-L47816) | Confirms the nine executable family paths in the default mustpass list. |
| Descriptor-indexing feature semantics | [Descriptor-indexing features](../../../../vulkan-docs/src/chapters/features.adoc#L2004-L2077) | Defines the descriptor-array non-uniform-indexing feature meanings. |
| Runtime descriptor arrays | [Runtime descriptor arrays](../../../../vulkan-docs/src/chapters/features.adoc#L2141-L2145) | Defines the runtime-array prerequisite. |
| Subgroup scope | [Subgroup operations](../../../../vulkan-docs/src/chapters/shaders.adoc#L3239-L3269) | Defines the scope in which subgroup broadcast is meaningful. |
| Input attachments | [Render-pass subpasses](../../../../vulkan-docs/src/chapters/renderpass.adoc#L2219-L2263) | Defines input-attachment use and same-location reads. |

## Questions / Risk Points for User Audit

- Is `descriptor family` the clearest primary behavioral axis, given that it controls both shader access semantics and host resource setup?
- Does the storage-buffer example make clear that the broadcast makes the access uniform within each subgroup, while the candidate index varies across the draw?
- Are sampler and sampled-image auxiliary descriptors clearly separated from the tested descriptor arrays?
- Are the minimum group thresholds correctly presented as source-selected lower bounds rather than a requirement to observe every descriptor?
- Is the non-VulkanSC boundary visible without implying that the implementation file itself has no registration role?

No unresolved source ambiguity changes the selected representative case, the nine-family mapping, or the ordered support-gate interpretation.

## Conversion Notes for Final Wiki Rewrite

- Keep the concise definition of subgroup-uniform descriptor selection in `Background Knowledge`; move the concrete storage-buffer example into the shader walkthrough.
- Use the nine `caseList` children as the primary behavior-parameter subsections and preserve their exact order.
- Carry the descriptor-family configuration table and the resource-specific behavior into `Parameter Dimensions and Observed Values`, `Behavior Parameters`, and runtime prose rather than copying this brief wholesale.
- Preserve the ordered support gates exactly: subgroup size greater than one, fragment subgroup support, `runtimeDescriptorArray`, then the descriptor-specific non-uniform-indexing feature.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write `### Cause Analysis` fresh during the Level-3 rewrite.
- Use `dEQP-VK.subgroups.uniform_descriptor_indexing.storage_buffer` for the one representative fragment walkthrough and preserve the exact SPIR-V 1.3 artifact generated from that specialization.
- Keep the legacy navigation page untouched and limit the rewrite to `UniformDescriptorIndexing_brief.md` and `UniformDescriptorIndexing.md`.
