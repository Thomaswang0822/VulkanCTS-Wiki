# Understanding Brief: `none_stage` synchronization tests

## One-Sentence Test Purpose

This test checks whether image memory barriers using a `NONE` destination stage and access mask preserve image contents while changing between representative writable and readable layouts.

## Background Knowledge

### `NONE` scopes and image layout transitions

A synchronization barrier has source and destination execution/access scopes. `VK_PIPELINE_STAGE_2_NONE_KHR` and `VK_ACCESS_2_NONE_KHR` describe an empty destination scope; they do not name the later operation that will consume the image. The test therefore follows the `NONE` barrier with a second barrier that performs the layout transition and names the actual read stage/access.

Why it matters here:
- The first barrier tests the synchronization2 `NONE` semantics without making the read operation part of its destination scope.
- The second barrier makes the image legal and visible for transfer, shader, or input-attachment reading.

## One Concrete Example

Conceptually, a `general_to_shader_read` case does this:

```text
[host] fill a 32x32 reference gradient and arrange an image in `GENERAL`
[device] write or retain the gradient in the image
[device] issue a barrier whose destination is `VK_PIPELINE_STAGE_2_NONE_KHR` / `VK_ACCESS_2_NONE_KHR`
[device] issue a second barrier from `GENERAL` to `SHADER_READ_ONLY_OPTIMAL`
[device] sample the image into a color target
[host] copy the target back and compare it with the gradient
```

This is a conceptual outline, not a replacement for the registered case.

## End-to-End Test Flow

```text
[host] select synchronization type, access-mask mode, writable layout/aspect, and readable layout/aspect
[host] choose a compatible format and create the reference, transition, source, and result images/buffers
[host] generate a component gradient; build write/read graphics pipelines only when the selected layouts require them
[device] copy or render the gradient into the transition image
[device] submit the `NONE` barrier with the source stage/access selected for the write path
[device] submit the layout-transition barrier with `VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT_KHR` as source and the actual read stage/access as destination
[device] copy the image or render it through a sampler/input attachment into the result image
[host] wait for completion, invalidate the result allocation, and compare the result with the reference
[host] report pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- A host-generated component gradient supplies the expected image data.
- Vertex and fragment shaders are compiled when a color/depth/stencil attachment or shader-read path is selected. The fragment shader variant is selected by the tested aspect and read/write method (`frag-color`, `frag-color-to-depth`, `frag-color-to-stencil`, `frag-depth-or-stencil-to-color`, or `frag-stencil-to-color`).
- Render passes and framebuffers are built for attachment and input-attachment paths; transfer and `GENERAL` paths avoid unnecessary graphics pipelines.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Reference image | yes | yes | source for write pipeline or expected data | no | Provides the gradient and may be sampled by the write pipeline. |
| Transition image | yes | yes | written, transitioned, and read | indirectly | Carries the tested layout and synchronization state. |
| Source buffer | yes | yes | read by transfer | no | Supplies the initial gradient for copy-based writes. |
| Result image and destination buffer | yes | yes | render target, then copied | yes | Converts the image contents into the host-visible comparison. |

## What Is Checked

- Float formats are compared with a `0.01` threshold.
- Integer and unsigned-integer formats are compared component-wise; an error-mask image records mismatches.
- For combined depth/stencil formats, only the selected depth or stencil aspect is compared.
- Stencil cases skip the diagonal texels because the one-bit stencil draw does not produce the same diagonal gradient as the reference.

## Behavior Parameter Identification

> **Behavior parameter:** synchronization/access strategy
>
> **Candidate values:** synchronization2 with generic access flags (no prefix), synchronization2 with specific access flags (`old_access_`), legacy synchronization structures with `NONE` stage (`legacy_`)

The write/read layout pair and image aspect are matrix dimensions that change the operation path and validation format, but these three strategy values are the primary behavioral grouping in the registered names.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| synchronization2 with generic access flags (no prefix) | Incorrect handling of synchronization2 generic memory access masks, `NONE` destination scopes, layout transitions, or the selected image path. |
| synchronization2 with specific access flags (`old_access_`) | Incorrect handling of synchronization2-specific source/destination access types or their interaction with the `NONE` barrier and layout transition. |
| legacy synchronization structures with `NONE` stage (`legacy_`) | Incorrect legacy barrier handling for `VK_PIPELINE_STAGE_NONE_KHR`, or incorrect compatibility behavior in the sync2-only registration path. |

## Important Variations and Special Cases

- Ten writable and twelve readable layout/aspect descriptors generate compatible write-to-read combinations. Incompatible nonzero aspects are pruned.
- Color, depth, stencil, and combined depth/stencil cases select different formats and pipeline paths.
- `VK_IMAGE_LAYOUT_ATTACHMENT_OPTIMAL_KHR` and `VK_IMAGE_LAYOUT_READ_ONLY_OPTIMAL_KHR` exercise generalized layouts introduced with synchronization2.
- The `legacy_` cases use legacy synchronization structures but remain registered below `synchronization2.none_stage`; they are not a legacy `synchronization` test family.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Test instance setup and format/path selection | [`NoneStageTestInstance::NoneStageTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationNoneStageTests.cpp#L241-L398) | Maps layouts/aspects to formats, pipelines, and access masks. |
| Barrier sequence | [`NoneStageTestInstance::iterate`](../../../modules/vulkan/synchronization/vktSynchronizationNoneStageTests.cpp#L977-L1007) | Shows the `NONE` barrier followed by the layout-transition barrier. |
| Result checking | [`verifyResult`](../../../modules/vulkan/synchronization/vktSynchronizationNoneStageTests.cpp#L1088-L1128) | Defines comparison and stencil exceptions. |
| Registration generation | [`createNoneStageTests`](../../../modules/vulkan/synchronization/vktSynchronizationNoneStageTests.cpp#L1375-L1445) | Defines the three strategy prefixes and layout matrix. |
| Mustpass evidence | [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt#L32030-L32031) | Confirms the `synchronization2.none_stage` path is included. |

## Questions / Risk Points for User Audit

- Is the distinction between an empty destination scope and the following layout-transition barrier clear?
- Should the final page retain the conceptual `general_to_shader_read` example, or use a transfer-only case instead?
- Is the strategy grouping a useful primary behavior axis for failure analysis, given that each strategy also spans the full layout matrix?

## Conversion Notes for Final Wiki Rewrite

- Keep `Background Knowledge` to one concise explanation of empty scopes and the two-barrier sequence.
- Present the three synchronization/access strategies as behavior subsections, with layout/aspect combinations as parameter dimensions.
- Preserve the failure mapping table in the final page and write fresh cause analysis.
- Keep the full generated case inventory in the mustpass/source appendix rather than expanding hundreds of leaves in the hierarchy tree.
