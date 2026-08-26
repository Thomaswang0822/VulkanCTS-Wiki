## Overview

**Core question:** Do push-descriptor commands make the selected resource available to graphics and compute work, including partial replacement through ordinary, template, and Commands2 commands?

- [`vktPipelinePushDescriptorTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1-L4933) implements the `push_descriptor` test family under applicable pipeline-construction roots.
- The family covers buffer, image, texel-buffer, sampler, and input-attachment descriptors across registered binding and command-count values.
- Graphics paths compare a rendered image with a software reference. Compute paths compare host-visible output data with expected values.
- Monolithic construction also tests incremental replacement, descriptor-update-template forms, Commands2 forms, and selected maintenance5 buffer-creation forms.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A descriptor set layout with `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT` does not allocate descriptor sets. `vkCmdPushDescriptorSet` supplies descriptors for it instead ([layout flag](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L358-L362)). The layout limit is `maxPushDescriptors`, and a pipeline layout may contain at most one push-descriptor layout ([layout constraints](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L145-L147), [pipeline-layout constraint](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1705-L1710)).
- A descriptor update template maps host-memory fields to descriptor updates. A push-descriptor template applies only to its specified bind point, pipeline layout, and set number ([template mapping](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4084-L4088), [push-template scope](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4183-L4186)).

## Registration Hierarchy

```text
pipeline.monolithic.push_descriptor
├── graphics
└── compute
```

`createPushDescriptorTests()` creates `graphics` for all construction types and adds `compute` only for monolithic construction ([factory](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4809-L4933)). The same factory supplies `pipeline_library`, `fast_linked_library`, and shader-object graphics inventories through its `pipelineType` parameter. The inspected split mustpass files contain 276 leaves: `monolithic` has 76, `pipeline_library` and `fast_linked_library` each have 36, and each shader-object list has 32.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | What it changes | Evidence |
|-----------|-------------------|-----------------|----------|
| Intermediate node | `graphics`, `compute` | Selects graphics rendering or compute dispatch. `compute` exists only for monolithic construction. | [factory](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4809-L4933) |
| Descriptor type | `uniform_buffer`, `storage_buffer`, `combined_image_sampler`, `sampler`, `sampled_image`, `storage_image`, `uniform_texel_buffer`, `storage_texel_buffer`, `input_attachment` | Selects the resource layout, shader declaration, and test implementation class. | [parameter matrix](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4769-L4806) |
| Binding | `0`, `1`, `3` | Selects the pushed binding and emitted shader binding. | [leaf-name construction](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4817-L4819) |
| Number of calls | `1`, `2`; `128` for the storage-buffer matrix | Changes the number of resource writes and associated draws or dispatches. | [parameter matrix](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4769-L4806) |
| Construction type | monolithic, pipeline library, fast linked library, shader object variants | Selects the pipeline construction path and controls pruning. | [support gate](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L88-L119) |
| Monolithic special leaves | `maintenance5_uniform_texel_buffer`, `maintenance5_storage_texel_buffer`, `maintenance5_uniform_buffer`; four `incremental_updates` leaves | The maintenance5 leaves create the selected buffers through `VkBufferUsageFlags2CreateInfoKHR`; the incremental leaves use ordinary, template, Commands2, and template-plus-Commands2 push commands. | [maintenance5 buffer path](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L448-L475), [special registration](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4898-L4927) |

Input attachments do not register under shader-object construction because they are unsupported with dynamic rendering ([pruning condition](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4884-L4894)).

## Behavior Parameters

The primary behavioral axis is the direct intermediate node. `graphics` tests descriptor visibility through raster output. `compute` tests it through storage-buffer output and adds four distinct incremental-update leaves in monolithic construction.

### `graphics` - descriptor reads through raster output

Graphics cases push the selected descriptor before each draw. Buffer cases use `PushDescriptorBufferGraphicsTest`; image and sampler cases use `PushDescriptorImageGraphicsTest`; texel buffers use `PushDescriptorTexelBufferGraphicsTest`; input attachments use `PushDescriptorInputAttachmentGraphicsTest`. The test draws quads whose expected colors identify the resource associated with each push command.

### `compute` - descriptor reads through storage output

Compute cases push both the selected input resource and an output storage buffer, dispatch, and compare every output item. The input descriptor can be a buffer, image, or texel buffer according to the registered leaf.

### `incremental_updates` - ordinary partial replacement

This monolithic compute leaf pushes two bindings for the first dispatch, replaces one binding for the second dispatch, then replaces the other for the third. Its two output buffers show whether commands preserve unaffected descriptor state and apply each replacement.

### `incremental_updates_template` - template partial replacement

This leaf uses `vkCmdPushDescriptorSetWithTemplate` for the same update sequence. It tests the template's mapping of host data to pushed descriptor writes.

### `incremental_updates_2` - Commands2 partial replacement

This leaf uses `vkCmdPushDescriptorSet2` for the same incremental sequence. It exercises the structure-based Commands2 command form.

### `incremental_updates_template_2` - template Commands2 partial replacement

This leaf uses `vkCmdPushDescriptorSetWithTemplate2` and checks the same two output relations as the other incremental cases.

## Shader Analysis

The following walkthrough uses `dEQP-VK.pipeline.monolithic.push_descriptor.compute.binding0_numcalls1_uniform_buffer`. It is representative because it exposes the direct dataflow from a pushed uniform buffer into a pushed output storage buffer. The broader descriptor matrix changes declarations and resource setup, while the central mechanism remains a resource read followed by an observable write.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.push_descriptor.compute.binding0_numcalls1_uniform_buffer
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | The test observes descriptor data through a storage-buffer result. |
| `binding0` | The input uniform buffer occupies set 0, binding 0. |
| `numcalls1` | One push operation supplies the input and output bindings before one dispatch. |
| `uniform_buffer` | The shader reads `inputData.color` from a uniform block. |

#### Purpose

The compute shader copies the `vec4` reached through the pushed uniform-buffer descriptor into the output storage-buffer descriptor. Host comparison makes an incorrect binding, descriptor payload, or result visibility observable.

#### Structural Design

| Phase | Shader action | Observable effect |
|-------|---------------|-------------------|
| Input | Read `inputData.color` from set 0, binding 0. | Selects the data reached by the pushed uniform-buffer descriptor. |
| Output | Store that value in `outData.color` at set 0, binding 1. | Makes the selected input available for host comparison. |

#### Shader Code

```glsl
#version 450
/// The pushed uniform-buffer descriptor supplies this read-only vec4.
layout(set = 0, binding = 0) uniform Block
{
    vec4 color;
} inputData;

/// The second pushed descriptor supplies the host-readable output buffer.
layout(set = 0, binding = 1) writeonly buffer Output
{
    vec4 color;
} outData;

void main()
{
    outData.color = inputData.color;
}
```

#### Additional Info

- `PushDescriptorBufferComputeTest::initPrograms()` changes the input declaration from `uniform` to `buffer` for storage-buffer leaves and derives both binding numbers from the case parameters ([generator](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1570-L1594)).
- The host pushes the input descriptor and output descriptor together, dispatches, adds a compute-to-host memory barrier, then compares the output allocation ([command recording and check](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1460-L1538)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Binding | Changes the input declaration's binding and the output binding remains one greater. | [compute generator](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1570-L1594) |
| Buffer descriptor type | Changes `uniform Block` to `buffer Block` for storage-buffer input. | [compute generator](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1570-L1594) |
| Calls | Does not change the copy statement. It changes how many input/output pairs are pushed and dispatched. | [recording loop](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1460-L1514) |
| Image and texel-buffer types | Use separate graphics and compute test classes with type-appropriate declarations and resource operations. | [factory dispatch](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4820-L4896) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 20
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %Output "Output"
               OpMemberName %Output 0 "color"
               OpName %outData "outData"
               OpName %Block "Block"
               OpMemberName %Block 0 "color"
               OpName %inputData "inputData"
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %outData NonReadable
               OpDecorate %outData Binding 1
               OpDecorate %outData DescriptorSet 0
               OpDecorate %Block Block
               OpMemberDecorate %Block 0 Offset 0
               OpDecorate %inputData Binding 0
               OpDecorate %inputData DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
     %Output = OpTypeStruct %v4float
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
    %outData = OpVariable %_ptr_Uniform_Output Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
      %Block = OpTypeStruct %v4float
%_ptr_Uniform_Block = OpTypePointer Uniform %Block
  %inputData = OpVariable %_ptr_Uniform_Block Uniform
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %17 = OpAccessChain %_ptr_Uniform_v4float %inputData %int_0
         %18 = OpLoad %v4float %17
         %19 = OpAccessChain %_ptr_Uniform_v4float %outData %int_0
               OpStore %19 %18
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `commonCheckSupported()` requires `VK_KHR_push_descriptor`, plus maintenance5 or maintenance6 when the parameters request them. Template-based incremental leaves also require `VK_KHR_descriptor_update_template` ([incremental support check](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1220-L1225)). It adds pipeline-library feature checks for library construction and shader-object plus dynamic-rendering checks for shader-object construction ([common support checks](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L88-L119)). The device setup enables the push-descriptor extension on pre-1.4 paths or `VkPhysicalDeviceVulkan14Features::pushDescriptor` on later API paths ([device setup](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L128-L180)).
- Each ordinary test builds a push-descriptor layout, creates the type-specific resources and pipeline, records `vkCmdPushDescriptorSet` writes, then submits and waits. The graphics buffer path pushes one buffer write before each quad draw ([recording](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L580-L625)).
- Graphics verification renders the same quads with `ReferenceRenderer`, reads the color attachment, and accepts only the configured threshold/position comparison ([verification](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L628-L663)). Compute verification invalidates host-visible memory and checks each expected `vec4` with `deMemCmp()` ([verification](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1516-L1538)).
- Incremental cases dispatch after the first complete update, after a one-binding replacement, and after a second replacement. A compute-to-compute barrier separates the second and third dispatch; there is no barrier between the first and second dispatch because they write different storage buffers. The checker compares the first output with the first uniform data and the second with the sum of both uniform data values. The third dispatch adds the second uniform value into the second dispatch's output, so the second relation also observes whether the barrier orders those shader accesses ([sequence and check](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1024-L1190)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `graphics` | Push-descriptor writes do not provide the selected buffer, image, texel-buffer, sampler, or input-attachment data to graphics work, or graphics result readback/comparison differs. |
| `compute` ordinary descriptor leaves | Push-descriptor writes do not provide the selected resource to compute work, or compute output visibility/readback differs. |
| `incremental_updates` | Replacing one pushed binding does not preserve or replace descriptor state as the three dispatches require. |
| `incremental_updates_template` | The descriptor update template maps host data to push descriptors incorrectly. |
| `incremental_updates_2` | `vkCmdPushDescriptorSet2` records an incorrect pushed descriptor update. |
| `incremental_updates_template_2` | `vkCmdPushDescriptorSetWithTemplate2` maps or records the template update incorrectly. |

### Cause Analysis

#### Graphics descriptor or result path

**Possible failure symptoms:** A color attachment differs from the software reference within the test's configured image-comparison tolerance.

**Possible implementation causes:** Source inspection shows that each draw receives a new pushed descriptor write before it executes. A failure can therefore involve descriptor binding state, the type-specific resource access path, raster output, or color-image readback. The final image does not isolate one of those stages; source-level investigation is needed to localize a particular mismatch.

#### Ordinary compute descriptor or visibility path

**Possible failure symptoms:** One output item differs byte-for-byte from its expected color.

**Possible implementation causes:** The selected input or output binding can be interpreted incorrectly, the compute write can be incorrect, or the compute-to-host visibility path can fail. The test records a `VK_ACCESS_SHADER_WRITE_BIT` to `VK_ACCESS_HOST_READ_BIT` barrier before host comparison, so the failure covers that command sequence as well as descriptor access ([barrier and check](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1499-L1538)).

#### Incremental descriptor-state replacement

**Possible failure symptoms:** The first output differs from the first uniform value, or the second output differs from the sum of the first and second uniform values.

**Possible implementation causes:** The first dispatch establishes both bindings. The second write replaces one binding, and the third replaces the other. A failure can indicate that a command incorrectly discards an unaffected pushed binding, applies a replacement to the wrong binding, or exposes a compute-write ordering defect. The two outputs identify the expected relations but do not uniquely locate the command that produced a mismatch.

#### Template mapping

**Possible failure symptoms:** The template incremental leaf fails its two output comparisons while the ordinary incremental form may not.

**Possible implementation causes:** The implementation may map the provided host-memory record to the wrong descriptor fields or apply the template to the wrong push-descriptor state. Vulkan limits a push-descriptor template to its specified bind point, layout, and set number ([template scope](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4183-L4186)); source-level investigation is needed to distinguish template interpretation from shared descriptor execution.

#### Commands2 recording

**Possible failure symptoms:** A Commands2 incremental leaf fails its final output comparisons.

**Possible implementation causes:** `VkPushDescriptorSetInfo` or `VkPushDescriptorSetWithTemplateInfo` can be processed differently from the legacy command route. The source selects these forms only for the `_2` leaves and otherwise retains the same dispatch and comparison design ([Commands2 branches](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1024-L1162)). A failure therefore points to the Commands2 update path or shared descriptor-state behavior; source-level investigation is needed for narrower localization.

## Case Pruning

### Requirement-based pruning

- Shader-object construction omits input-attachment leaves because input attachments are unsupported with dynamic rendering.

### Design-based pruning

- The factory adds `compute` only to the monolithic root, so non-monolithic construction types expose graphics leaves only.
- Graphics buffer leaves register only when `numCalls <= 2`; the `binding1_numcalls128_storage_buffer` matrix entry supplies compute coverage.
- Maintenance5 and incremental-update leaves are monolithic-only special cases.

## Key Takeaways

- Push descriptors replace descriptor-set allocation for a layout created with the push-descriptor layout flag.
- The `graphics` and ordinary `compute` paths test descriptor accessibility through different observable outputs.
- Incremental leaves test state replacement across three dispatches, with template and Commands2 forms covering distinct command interfaces.
- The split pipeline mustpass inventory contributes 276 `push_descriptor` leaves across monolithic, library, fast-linked-library, and shader-object construction paths.

## Source Reference Appendix

| Topic | Evidence |
|-------|----------|
| Registration and pruning | [createPushDescriptorTests](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L4769-L4933) |
| Support and device feature setup | [commonCheckSupported and createDeviceWithPushDescriptor](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L88-L180) |
| Buffer graphics push/draw/reference comparison | [PushDescriptorBufferGraphicsTestInstance](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L580-L663) |
| Buffer compute push/dispatch/readback comparison | [PushDescriptorBufferComputeTestInstance](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1460-L1538) |
| Incremental command forms and result check | [PushDescriptorIncrementalUpdatesComputeTestInstance](../../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1024-L1190) |
| Push-descriptor layout semantics | [descriptor set layouts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L122-L147) |
| Descriptor update template semantics | [descriptor update templates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4082-L4186) |
| Mustpass scope | `external/vulkancts/mustpass/main/vk-default/pipeline/` |
