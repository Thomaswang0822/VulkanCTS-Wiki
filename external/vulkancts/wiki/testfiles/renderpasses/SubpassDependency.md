## Overview

**Core question:** When subpass dependencies order work between subpasses, between a subpass and the outside of a render pass, or within a single subpass, does the implementation honor the resulting execution and memory ordering so that downstream reads see the right data?

- This page covers the `subpass_dependencies` test family group in [`vktRenderPassSubpassDependencyTests.cpp`](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp). The group is created by [`createRenderPassSubpassDependencyTests()`](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4596-L4599) and attached under `suballocation` for each rendering variant.
- It registers six test families that each exercise a different subpass dependency shape: external dependencies between render passes, implicit dependencies added by the implementation, late fragment test ordering with depth/stencil input attachments, a self-dependency from the geometry stage to indirect draw, a single attachment read and written on disjoint channels, and a single attachment used for both input and output.
- The core idea across all six families is to set up a data flow whose correctness depends on a specific subpass dependency, render it, read the result back, and compare it against a host-computed reference.
- Four families (`external_subpass`, `implicit_dependencies`, `late_fragment_tests`, `self_dependency`) are render-pass-only and are not registered for dynamic rendering. The remaining two (`separate_channels`, `single_attachment`) also run under dynamic rendering with local read.

## Background Knowledge

- **Subpass dependency.** A `VkSubpassDependency` defines an execution and memory dependency between two subpasses, between a subpass and `VK_SUBPASS_EXTERNAL`, or from a subpass back to itself. The source and destination stage masks pick which pipeline stages synchronize, and the source and destination access masks pick which memory accesses are ordered. For attachments the dependency also behaves like an image memory barrier whose layouts come from the subpass descriptions ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc)).
- **`VK_SUBPASS_EXTERNAL`.** Using `VK_SUBPASS_EXTERNAL` as the source subpass extends the synchronization scope to commands submitted before `vkCmdBeginRenderPass`. Using it as the destination subpass extends the scope to commands submitted after `vkCmdEndRenderPass`. This is how a dependency crosses the render pass boundary.
- **Self-dependency.** A dependency whose source and destination are the same subpass orders work inside that subpass. The `self_dependency` family uses this shape to order a geometry shader storage write before a later indirect draw command read ([self-dependency](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L1996-L2002)). The attachment-based families `separate_channels` and `single_attachment` use a self-dependency with `VK_DEPENDENCY_BY_REGION_BIT` to order a color write before a fragment shader input attachment read.
- **Late fragment tests.** Depth and stencil writes become visible to later subpasses through the `VK_PIPELINE_STAGE_LATE_FRAGMENT_TESTS_BIT` stage, which covers depth/stencil operations performed after the fragment shader. Depending on `LATE_FRAGMENT_TESTS` rather than `EARLY_FRAGMENT_TESTS` makes the test insensitive to whether the implementation runs depth/stencil early or late.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.subpass_dependencies
├── external_subpass
├── implicit_dependencies
├── late_fragment_tests
├── self_dependency
├── separate_channels
└── single_attachment
```

The tree shows the `renderpass1.suballocation.subpass_dependencies` representative scope. The same six families are registered under `renderpasses.renderpass2.suballocation.subpass_dependencies`, and `separate_channels` and `single_attachment` are also registered under each `renderpasses.dynamic_rendering.*.suballocation.subpass_dependencies` path. The four render-pass-only families (`external_subpass`, `implicit_dependencies`, `late_fragment_tests`, `self_dependency`) are guarded by `if (groupParams->renderingType != RENDERING_TYPE_DYNAMIC_RENDERING)` and are skipped for dynamic rendering. All six families are added inside [`initTests()`](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4205-L4593).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Render size | `{32,32}`, `{64,64}`, `{128,128}`, `{512,512}` | Changes the framebuffer area over which dependencies must hold. Late fragment tests use the three smaller sizes; external and self-dependency families use the three larger sizes. The implicit family uses a single fixed `{128,128}` size and varies only the render pass count. | [renderSizes arrays](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4224), [implicit fixed size](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4378), [late fragment sizes](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4392), [self-dependency sizes](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4513) |
| Render pass count | `2`, `3`, `5` | Number of chained render passes in the external and implicit families. More passes chain more external dependencies, which stresses cross-render-pass ordering. | [renderPassCounts](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4222), [implicit counts](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4322) |
| Subpass count | `2`, `3`, `5` | Number of subpasses inside one render pass for late fragment tests. Each subpass reads the previous subpass's depth through an input attachment. | [subpassCounts](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4394) |
| Depth/stencil format | `D24_UNORM_S8_UINT`, `D32_SFLOAT_S8_UINT` | Attachment format for late fragment tests and for the depth/stencil variant of separate channels. The specification requires implementations to support at least one of these for depth/stencil attachments. | [late fragment formats](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4398), [separate channels configs](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4547-L4550) |
| Color format | `R8G8B8A8_UNORM`, `B8G8R8A8_UNORM`, `R16G16B16A16_SFLOAT`, `R5G6B5_UNORM_PACK16`, `A1R5G5B5_UNORM_PACK16` | Attachment format for the single attachment family, chosen to cover UNORM, signed float, and packed formats. | [single attachment configs](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4574-L4578) |
| Synchronization type | `LEGACY`, `SYNCHRONIZATION2` | Selects legacy `VkSubpassDependency` versus `VkSubpassDependency2` / synchronization2 barriers. The synchronization2 variant is registered only for `renderpass2`. | [sync2 variant](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4303-L4310) |

## Behavior Parameters

The primary behavioral axis is the test family. Each family builds a different dependency shape and checks a different ordering property. The remaining dimensions above configure render size, pass count, subpass count, format, and synchronization type but do not change what is being tested.

### external_subpass: explicit dependencies across render passes

This family chains two to five render passes that each contain one subpass and explicit dependencies from `VK_SUBPASS_EXTERNAL` to subpass 0 and back. The first pass renders four colored quads. Each later pass blurs the previous pass's output, alternating horizontal and vertical blur, by sampling the previous pass's color attachment as a texture ([dependency construction](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4263-L4285)). Correct output requires the external dependencies to carry the previous pass's color writes into the next pass's texture reads.

### implicit_dependencies: implementation-added dependencies

This family uses the same blur chain as `external_subpass`, but the first render pass declares no dependencies at all and later passes declare only the `VK_SUBPASS_EXTERNAL` to subpass 0 dependency. The implementation must add the implicit dependencies that order subpass 0 to external, so that each pass reads the previous pass's stored output ([dependency construction](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4355-L4372)). The test verifies that these implicit dependencies produce the same blurred result as the explicit ones.

### late_fragment_tests: depth/stencil input attachment ordering

This family runs one render pass with two to five subpasses that share a chain of depth/stencil attachments. Subpass 0 renders 128 triangles at pseudorandom depths. Each later subpass reads the previous subpass's depth through an input attachment and writes `previousDepth - 0.02` to its own depth attachment ([fragment shader](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4037-L4044)). Each inter-subpass dependency uses `VK_PIPELINE_STAGE_LATE_FRAGMENT_TESTS_BIT` as the source stage and `VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT` as the source access, with `VK_DEPENDENCY_BY_REGION_BIT`, so the next subpass's input attachment read only observes the previous subpass's depth after late fragment tests complete ([dependency construction](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4469-L4478)).

### self_dependency: geometry stage to indirect draw

This family uses one subpass with a self-dependency from `VK_PIPELINE_STAGE_GEOMETRY_SHADER_BIT` to `VK_PIPELINE_STAGE_DRAW_INDIRECT_BIT`. The pipeline draws 128 points with a geometry shader that emits a small quad per point and writes a new `VkDrawIndirectCommand` into a storage buffer ([geometry shader](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4070-L4105)). The command buffer then issues two `vkCmdDrawIndirect` calls against that same buffer. The self-dependency orders the geometry shader's storage write before the second indirect draw's command read, so the second draw uses the geometry-written parameters ([dependency](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L1996-L2002), [command recording](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L2150-L2167)).

### separate_channels: disjoint channel read and write on one attachment

This family writes one color attachment from a single draw that also reads the same attachment as an input attachment, but the read channels (R, G) and the write channels (B, A) do not overlap because the pipeline color write mask is set to `VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT` ([color write mask](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L2618-L2628)). For color formats the render pass declares a self-dependency from `COLOR_ATTACHMENT_OUTPUT` to `FRAGMENT_SHADER` with `BY_REGION_BIT` ([self-dependency](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L2564-L2567)). For depth/stencil formats the family uses a depth/stencil attachment with depth test and stencil write instead, and declares no subpass dependency. The test confirms that the disjoint-channel case produces the expected `(initR, initG, initR + initG, 1.0)` color, or the expected depth and stencil values, without needing a hazard-preventing self-dependency on the same channels.

### single_attachment: one attachment used for input and output

This family uses one color attachment as both input attachment and color output inside a single-subpass render pass. The render pass declares a self-dependency from `COLOR_ATTACHMENT_OUTPUT` to `FRAGMENT_SHADER` with `VK_DEPENDENCY_BY_REGION_BIT` ([render pass 0 dependency](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3332-L3335)). A first draw writes a solid color `(0.1, 0.2, 0.0, 1.0)`, a pipeline barrier orders the write before the next read, and a second draw loads the attachment as an input attachment and adds `(0.1, 0.2, 0.0, 0.0)` ([draw sequence](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3722-L3763)). A second render pass then samples the result through a combined image sampler and adds the same offset again, producing a final `(0.3, 0.6, 0.0, 1.0)`.

## Shader Analysis

The shaders in this file are tools that produce the data flow each dependency must order. They are not the behavior under test. No representative shader walkthrough is included for that reason. The notable shader roles are:

- External and implicit families generate a fullscreen quad in the vertex shader, a four-color pattern in the first fragment shader, and alternating horizontal or vertical blur in later fragment shaders, all built as GLSL strings parameterized by image size and blur kernel ([ExternalPrograms](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3824-L3933)).
- Late fragment tests use a vertex shader that takes depth from vertex data in subpass 0 and a fullscreen-quad vertex shader in later subpasses, with a fragment shader that loads the previous depth from an input attachment and subtracts `0.02` ([SubpassPrograms](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3990-L4051)).
- Self-dependency uses a geometry shader that emits a quad and writes the indirect draw parameters into a storage buffer bound at binding 0 ([SubpassSelfDependencyBackwardsPrograms](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4054-L4114)).
- Separate channels and single attachment use short vertex and fragment shaders that read input attachments with `subpassLoad` or sample textures and write computed colors ([SeparateChannelsPrograms](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4116-L4149), [SingleAttachmentPrograms](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4151-L4193)).

## Runtime Execution and Result Checking

All families follow the same host-side shape: build resources, record the render pass or dynamic rendering instance, submit and wait, copy the result image to a host-visible buffer, invalidate the mapped range, and compare against a reference. The reference computation and threshold differ per family.

- **External and implicit families.** The host renders the same four-color pattern and applies the same alternating blur in software, then compares the final pass's output with `tcu::floatThresholdCompare` using a threshold of four times the minimum representable difference for the format. More chained passes accumulate more blur rounds, so a missing external dependency produces a visibly different blur result ([reference and threshold](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L933-L994)).
- **Late fragment tests.** The host runs a software reference renderer that draws the same triangles with depth test enabled, then subtracts `0.02` per additional subpass. Depth is compared with `verifyDepth` using a threshold of `subpassCount` times the minimum representable difference, and stencil is compared exactly with `verifyStencil` ([depth and stencil checks](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L1756-L1776)). The growing depth threshold accounts for precision loss from each subpass's `0.02` subtraction.
- **Self-dependency.** The host converts the random points into the same quads the geometry shader produces and runs a software reference renderer. The result is compared with `tcu::floatThresholdCompare` using a threshold of `0.01` ([self-dependency check](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L2224-L2233)). The clear color is green and the geometry-emitted quads are red, so a missing self-dependency leaves some points undrawn or drawn with stale parameters.
- **Separate channels.** For color formats the host builds the expected `(initR, initG, initR + initG, 1.0)` chessboard and compares with a `0.01` threshold. For depth/stencil formats it compares depth with a minimum-representable-difference threshold and stencil exactly ([separate channels checks](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L2810-L2877)).
- **Single attachment.** The host expects every pixel to equal `(0.3, 0.6, 0.0, 1.0)` and compares with a `0.05` threshold ([single attachment check](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3498-L3524)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `external_subpass` | An external dependency did not carry the previous render pass's color writes into the next pass's texture reads, or synchronization2 lowering changed the dependency. |
| `implicit_dependencies` | The implementation did not add the implicit subpass-to-external dependency needed to make each pass read the previous pass's stored output. |
| `late_fragment_tests` | An inter-subpass dependency did not wait for `LATE_FRAGMENT_TESTS`, so an input attachment read observed stale or in-flight depth/stencil writes. |
| `self_dependency` | The geometry shader's storage write was not ordered before the second indirect draw's command read, so the draw used stale parameters. |
| `separate_channels` | The implementation treated the disjoint-channel read and write as a hazard and serialized or dropped work, or the depth/stencil path mis-ordered depth and stencil access. |
| `single_attachment` | The self-dependency did not order the first color write before the input attachment read, so the second draw read stale attachment contents. |
| Any family (common cause) | Resource setup, descriptor binding, image layout transition, or copyback produced wrong data independent of dependency handling. |

### Cause Analysis

#### Missing or weakened cross-pass external dependency

**Possible failure symptoms:** The external or implicit family's final image differs from the host blur reference by more than the four-times-minimum threshold. The difference tends to look like one pass of blur is missing or applied against stale texture contents, because one render pass read an image that had not yet received the previous pass's store.

**Possible implementation causes:** The Vulkan specification makes `VK_SUBPASS_EXTERNAL` extend the synchronization scope to commands before `vkCmdBeginRenderPass` or after `vkCmdEndRenderPass` ([renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc)). A driver that does not insert the external dependency's memory barrier between the previous pass's `STORE_OP_STORE` and the next pass's texture read, or that lowers synchronization2 dependencies incorrectly, can produce this symptom. The implicit family has the same symptom when the implementation fails to add the implicit subpass-to-external dependency the specification requires.

#### Late fragment test ordering not honored

**Possible failure symptoms:** Depth readback differs from the reference by more than `subpassCount` times the minimum representable difference, or stencil readback differs at any pixel. The error pattern tracks where later subpasses read a depth value that an earlier subpass had not finished writing.

**Possible implementation causes:** The dependency from subpass `N-1` to subpass `N` names `VK_PIPELINE_STAGE_LATE_FRAGMENT_TESTS_BIT` as the source stage so that the input attachment read in subpass `N` only observes depth/stencil writes after late fragment tests complete. A driver that routes depth/stencil writes through `EARLY_FRAGMENT_TESTS` only, or that does not block the next subpass's input attachment read on late fragment tests, exposes the test to early or partial depth values. Source-level investigation is needed to distinguish a stage-mask handling bug from a tiling architecture that defers depth/stencil resolves.

#### Self-dependency storage write not visible to indirect draw

**Possible failure symptoms:** The self-dependency result image is missing some of the red quads that the geometry shader should have produced through the second indirect draw, or draws them at the wrong count, leaving green clear color where quads should appear.

**Possible implementation causes:** The self-dependency orders `VK_ACCESS_SHADER_WRITE_BIT` from the geometry shader before `VK_ACCESS_INDIRECT_COMMAND_READ_BIT` of the second `vkCmdDrawIndirect`. A driver that does not serialize the storage buffer write and the indirect command read inside one subpass lets the second draw reuse the initial `(64, 1, 0, 0)` parameters instead of the geometry-written `(64, 1, 64, 0)` parameters. Because the test draws 128 points but the indirect parameters advance `firstVertex` to 64, a missing ordering typically shows up as the second half of the points not rendering.

#### Single attachment self-dependency read/write hazard

**Possible failure symptoms:** The single attachment result deviates from `(0.3, 0.6, 0.0, 1.0)` by more than the `0.05` threshold. Pixels may match the solid color `(0.1, 0.2, 0.0, 1.0)`, indicating the input attachment read happened before the first write became visible, or may show partial blending.

**Possible implementation causes:** The render pass declares a self-dependency with `VK_DEPENDENCY_BY_REGION_BIT` from `COLOR_ATTACHMENT_OUTPUT` to `FRAGMENT_SHADER`, and the recorded pipeline barrier between the two draws expresses the same ordering for the dynamic rendering path. A driver that does not enforce framebuffer-space ordering inside a subpass, or that ignores the self-dependency because the source and destination subpass indices are equal, lets the second draw read undefined attachment contents. On some tilers the issue may instead come from how the attachment is split across tiles when `BY_REGION_BIT` is used.

## Case Pruning

### Requirement-based pruning

- `renderpass2` requires `VK_KHR_create_renderpass2` for every family, and the synchronization2 variant of `external_subpass` additionally requires `VK_KHR_synchronization2` ([external checkSupport](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3971-L3978)).
- The `self_dependency` family requires the `geometryShader` device feature ([self-dependency checkSupport](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3981-L3987)).
- Dynamic rendering requires `VK_KHR_dynamic_rendering_local_read`, and depth/stencil formats under dynamic rendering are skipped when `dynamicRenderingLocalReadDepthStencilAttachments` is not supported on Vulkan 1.4 and later ([SubpassTestConfig checkSupport](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3944-L3956)).
- The late fragment tests family checks that the selected depth/stencil format supports `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` and `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` before registering each case ([format check](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3958-L3967)).

### Design-based pruning

- The four render-pass-only families are not registered under `dynamic_rendering`. Dynamic rendering has no render pass object and no subpass dependency structure for cross-pass or self-dependency ordering in the shapes these families test, so they are guarded out at registration time ([guard](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4220), [guard](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4320), [guard](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4390), [guard](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4511)).
- The synchronization2 variant of `external_subpass` is registered only for `renderpass2`, because `VkSubpassDependency2` belongs to the render pass 2 API surface ([sync2 guard](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4303-L4310)).

## Key Takeaways

- Each of the six families targets one dependency shape: cross-pass external, implementation-added implicit, late fragment test ordering, geometry-to-indirect-draw self-dependency, disjoint-channel same-attachment access, and same-attachment input and output.
- `external_subpass` and `implicit_dependencies` use the same blur chain; the difference is whether the cross-pass ordering comes from explicit dependencies or from ones the implementation must add implicitly.
- `late_fragment_tests` depends on `VK_PIPELINE_STAGE_LATE_FRAGMENT_TESTS_BIT` so the result is correct whether the implementation runs depth/stencil early or late, and its depth threshold grows with subpass count to absorb accumulated precision loss.
- `self_dependency` is the only family that uses a non-framebuffer-space self-dependency, ordering a geometry shader storage write before an indirect command read inside one subpass.
- `separate_channels` shows that disjoint read and write channels on one attachment do not require a hazard-preventing dependency, and `single_attachment` shows the opposite case where a self-dependency is required for same-attachment input and output.
- See [Failure Meaning](#failure-meaning) for how each dependency shape maps to a distinct failure symptom.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family group factory | [`createRenderPassSubpassDependencyTests`](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4596-L4599) | Creates the `subpass_dependencies` group and dispatches to `initTests`. |
| Registration and matrix generation | [`initTests`](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4205-L4593) | Adds all six families and their render size, pass count, subpass count, and format children. |
| External dependency render pass construction | [external dependencies](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4263-L4285) | Builds the explicit external-to-subpass and subpass-to-external dependencies. |
| Implicit dependency render pass construction | [implicit dependencies](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4355-L4372) | Adds only the external-to-first-subpass dependency and relies on implicit subpass-to-external ordering. |
| Late fragment dependency construction | [late fragment dependencies](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4469-L4488) | Wires inter-subpass dependencies on `LATE_FRAGMENT_TESTS` with `BY_REGION_BIT`. |
| Self-dependency construction | [geometry-to-indirect self-dependency](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L1996-L2002) | Declares the geometry shader to indirect draw self-dependency. |
| Separate channels render pass | [separate channels dependency](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L2560-L2568) | Adds the color self-dependency for the color path and omits it for the depth/stencil path. |
| Single attachment render pass | [single attachment dependency](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3332-L3335) | Declares the self-dependency used for same-attachment input and output. |
| Depth and stencil verification | [`verifyDepth` and `verifyStencil`](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L98-L141) | Host-side comparators used by the late fragment and separate channels families. |
| Support checks | [`checkSupport`](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3936-L3987) | Requires render pass 2, synchronization2, dynamic rendering local read, geometry shader, and format support as applicable. |
| Attachment under `suballocation` | [`vktRenderPassTests.cpp#L8565`](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8565) | Attaches the `subpass_dependencies` group under `suballocation` for every rendering variant. |
| Vulkan spec: subpass dependencies | [renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc) | Defines `VkSubpassDependency`, `VK_SUBPASS_EXTERNAL`, and the synchronization scopes they create. |
