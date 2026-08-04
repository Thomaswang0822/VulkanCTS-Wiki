# Understanding Brief: `pipeline.push_descriptor`

## One-Sentence Test Purpose

This test checks whether an implementation can make descriptor data available through push-descriptor commands for graphics and compute work across descriptor classes, bindings, update counts, and supported pipeline-construction paths.

## Background Knowledge

### Push descriptor layouts

A layout created with `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT` cannot allocate descriptor sets. Commands push descriptor writes into the command buffer for that layout instead ([descriptor-set-layout flag](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L358-L362)). A pipeline layout may contain at most one such layout ([pipeline-layout rule](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1705-L1710)).

Why it matters here:
- The tests create a push-descriptor layout, issue `vkCmdPushDescriptorSet`, then draw or dispatch without allocating a descriptor set.
- The selected binding and descriptor type must agree with both the layout and the shader declaration.

### Descriptor update templates

A descriptor update template maps host-memory update data to descriptor writes ([template definition](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4084-L4088)). A template whose type is `VK_DESCRIPTOR_UPDATE_TEMPLATE_TYPE_PUSH_DESCRIPTORS` targets a particular pipeline bind point, layout, and set number ([push-template contract](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4183-L4186)).

Why it matters here:
- The incremental-update cases compare ordinary push commands with template-based and Commands2 forms.
- Replacing one binding must preserve the other binding until a later write replaces it.

## One Concrete Example

The representative leaf `dEQP-VK.pipeline.monolithic.push_descriptor.compute.binding0_numcalls1_uniform_buffer` creates a push-descriptor set layout with a uniform-buffer input at binding 0 and an output storage buffer at binding 1. The host pushes both writes, dispatches a compute shader, invalidates the readback allocation, and compares the output `vec4` with the input `vec4` ([layout setup](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1301-L1359), [push, dispatch, and check](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1460-L1538)).

## End-to-End Test Flow

```text
[host] select descriptor type, binding, call count, construction type, and optional maintenance path
[host] require push-descriptor support and create a device, layout, resources, and pipeline
[host] record one or more push-descriptor writes, followed by draws or dispatches
[device] read the pushed resource and write a color attachment or storage output
[host] wait, read the image or invalidate the output allocation, then compare with expected data
[host] report pass only when every checked result matches
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

Each test case supplies GLSL through `initPrograms()`. The buffer-compute path generates declarations that change from `uniform` to `buffer` for the selected input descriptor and writes `inputData.color` to `outData.color` ([generator](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1570-L1594)). Graphics, image, texel-buffer, and input-attachment paths use their own test classes and source generation.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Push-descriptor layout and pipeline layout | Yes | Yes | Used by commands | No | Establish the binding contract without allocating a descriptor set. |
| Input buffer, image, texel buffer, sampler, or input attachment | Yes | Yes | Read by the selected shader path | No | Supplies the descriptor payload under test. |
| Color attachment or output storage buffer | Yes | Yes | Written by graphics or compute work | Yes | Provides the observable result. |
| Descriptor update template, incremental leaves only | Yes | Yes | Interpreted by the push-template command | No | Tests the template route for the same descriptor state. |

## What Is Checked

- Graphics paths render reference-colored geometry, read the color attachment, and use `tcu::intThresholdPositionDeviationCompare()` with an RGBA threshold of `(2, 2, 2, 2)` and a position deviation of `(1, 1, 0)` ([image check](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L628-L663)).
- Ordinary compute paths invalidate the output allocation and compare each result item to its expected color with `deMemCmp()` ([buffer check](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1516-L1538)).
- Incremental compute paths check both output buffers: the first equals the first uniform value, while the second equals the sum of the first and second uniform values ([incremental check](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1164-L1190)).

## Behavior Parameter Identification

> **Behavior parameter:** test family / direct intermediate node
>
> **Candidate values:** `graphics`, `compute`; within monolithic `compute`, `incremental_updates`, `incremental_updates_template`, `incremental_updates_2`, `incremental_updates_template_2`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics` | Push-descriptor writes do not provide the selected buffer, image, texel-buffer, sampler, or input-attachment data to graphics work, or graphics result readback/comparison differs. |
| `compute` ordinary descriptor leaves | Push-descriptor writes do not provide the selected resource to compute work, or compute output visibility/readback differs. |
| `incremental_updates` | Replacing one pushed binding does not preserve or replace descriptor state as the three dispatches require. |
| `incremental_updates_template` | The descriptor update template maps host data to push descriptors incorrectly. |
| `incremental_updates_2` | `vkCmdPushDescriptorSet2` records an incorrect pushed descriptor update. |
| `incremental_updates_template_2` | `vkCmdPushDescriptorSetWithTemplate2` maps or records the template update incorrectly. |

## Important Variations and Special Cases

- The factory registers `graphics` for each construction type. It registers `compute` only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` ([registration](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4809-L4932)).
- Input attachments are excluded for shader-object construction because that path uses dynamic rendering ([source condition](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4884-L4894)).
- Monolithic adds `maintenance5_uniform_texel_buffer`, `maintenance5_storage_texel_buffer`, and `maintenance5_uniform_buffer`, plus four incremental compute leaves ([special leaves](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4898-L4927)).
- The inspected pipeline mustpass files contain 276 matching leaves: 76 monolithic, 36 each pipeline-library and fast-linked-library, and 32 in each of the four shader-object lists.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Support and device setup | [common support and device creation](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L88-L180) | Requires the extension or Vulkan 1.4 feature and construction-type dependencies. |
| Buffer graphics | [push, draw, and image check](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L580-L663) | Shows per-draw push writes and reference-image validation. |
| Incremental updates | [command sequence and checker](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1024-L1190) | Shows the three updates, commands2/template alternatives, barrier, and expected results. |
| Registration matrix | [createPushDescriptorTests](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4769-L4933) | Defines the leaf names, pruning, and special cases. |

## Questions / Risk Points for User Audit

- Does the separation between descriptor-class coverage and incremental-update semantics make the two mechanisms clear?
- Does the host/device timeline make the observable dataflow clear?
- Does the failure mapping distinguish the ordinary push path from template and Commands2 variants?

## Conversion Notes for Final Wiki Rewrite

- Use `graphics` and `compute` as the page's primary behavioral axis; make the four incremental leaves separate compute mechanisms.
- Retain the buffer-compute example as the single representative shader walkthrough.
- Copy the failure-cause table unchanged into the final page, then add source-grounded cause analysis there.
- Keep generated shader and resource detail proportional. The broad descriptor matrix belongs in parameter and runtime sections.
