## Overview

**Core question:** Does an implementation preserve the cleared contents of a transient attachment across a store/load handoff between two render passes, so a later fragment shader can read them back through an input attachment?

- Source file: [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L1).
- Registered test family: `fragment_operations.transient_attachment_bit`, a direct child of the [`fragment_operations`](../../categories/fragment_operations.md) test category.
- The file both registers and implements six test case leaves. Each leaf crosses one attachment mode (color, depth, or stencil) with one backing-memory mode (lazily allocated or device-local).
- The core test idea: clear a transient attachment in one render pass, store it, then load it back in a second render pass and read it through a fragment-shader input attachment. If the cleared value is preserved, the test passes.
- The page explains what is tested, how the two-axis matrix works, the shader read path, the host-side comparison, what a failure means, and where the six cases are registered.

## Background Knowledge

For the shared concept of transient attachment lifetime and load/store semantics, see [Background Knowledge](../../categories/fragment_operations.md#background-knowledge) of the `fragment_operations` page.

- **Transient attachment usage.** `VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT` permits an image to be backed by memory with `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` when used as a color, depth/stencil, or input attachment. A memory type with `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` may only be bound to a `VkImage` whose usage includes the transient bit, and the implementation may commit zero backing memory initially, growing the committed size as additional memory is needed. On some implementations, attachments that no render pass needs afterwards may never be allocated at all.
- **Load and store ops across render-pass instances.** A render-pass attachment declares how its contents are treated at the beginning and end of a render-pass instance. `VK_ATTACHMENT_LOAD_OP_CLEAR` fills the attachment with a clear value before the subpass runs. `VK_ATTACHMENT_LOAD_OP_LOAD` preserves the previous contents within the render area as the initial values. `VK_ATTACHMENT_STORE_OP_STORE` writes the contents generated during the render pass to memory. This test chains store then load across two separate render-pass instances, which is the boundary being exercised.
- **Input attachment reads.** An input attachment is a framebuffer attachment that the fragment shader of the same subpass can read through a `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT` descriptor. GLSL exposes it through `subpassLoad()` (floating point) or `usubpassInput` plus `subpassLoad()` (unsigned). The read returns the per-pixel attachment value at the fragment's location.

## Registration Hierarchy

```text
fragment_operations.transient_attachment_bit
├── color_load_store_op_test_lazy_bit
├── depth_load_store_op_test_lazy_bit
├── stencil_load_store_op_test_lazy_bit
├── color_load_store_op_test_local_bit
├── depth_load_store_op_test_local_bit
└── stencil_load_store_op_test_local_bit
```

Source: [`createTransientAttachmentTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L601-L627).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Attachment mode | `color`, `depth`, `stencil` | Selects which attachment aspect is cleared and read back, the transient attachment format, the aspect mask, and the fragment-shader decode of the read value. | [`TestMode`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L56-L62), [registration table](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L612-L618) |
| Memory-property mode | `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT`, `VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT` | Selects the backing memory of the transient attachment. Lazy is the spec-intended transient path; device-local is the generic fallback that must still work. | [registration table](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L612-L618) |
| Render size | `32 x 32` | Fixed render area for the clear, draw, and comparison. | [constructor arguments](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L622-L623) |
| Transient attachment format | `VK_FORMAT_R8G8B8A8_UNORM` (color), `VK_FORMAT_D16_UNORM` (depth), first supported of `VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT` (stencil) | The image format of the object under test, fixed per attachment mode. | [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L307-L312), [`TransientAttachmentTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L362-L365) |
| Image usage flags | color: `COLOR_ATTACHMENT \| TRANSIENT_ATTACHMENT \| INPUT_ATTACHMENT`; depth/stencil: `DEPTH_STENCIL_ATTACHMENT \| TRANSIENT_ATTACHMENT \| INPUT_ATTACHMENT` | The transient bit is always present, plus the attachment usage that lets the image serve as a render target, and the input-attachment usage that lets the second subpass read it. | [`TransientAttachmentTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L357-L361) |
| Output format | `VK_FORMAT_R8G8B8A8_UNORM` | Fixed format of the second, non-transient color attachment that receives the fragment shader output. | [`TransientAttachmentTestInstance::iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L380) |

## Behavior Parameters

This test family has two behavioral axes. The test case leaves are the full product of the two.

### Attachment mode

Each value selects a different attachment aspect, transient attachment format, and fragment-shader decode of the read value.

#### `color`: color attachment clear and readback

The transient attachment is an `R8G8B8A8_UNORM` color image with the color attachment, transient, and input attachment usage bits. The first render pass clears it to RGBA `(1.0, 1.0, 0.0, 1.0)` and stores it. The second render pass binds it as an input attachment and the fragment shader copies the loaded value directly to its output. The reference image is the clear color.

#### `depth`: depth aspect clear and readback

The transient attachment is a `VK_FORMAT_D16_UNORM` depth image with the depth-stencil attachment, transient, and input attachment usage bits. The first render pass clears the depth aspect to `0.5` and stores it. The fragment shader reads the depth value through `subpassLoad` and writes it into the red channel: `vec4(subpassLoad(inputValue).r, 0.0, 0.0, 1.0)`. The reference image is `(0.5, 0.0, 0.0, 1.0)`.

#### `stencil`: stencil aspect clear and readback

The transient attachment is a depth-stencil image with the first supported stencil-capable format, selected at support-check time. The first render pass clears the stencil aspect to `128` and stores it. Because stencil values are unsigned integers, the fragment shader declares the input attachment as `usubpassInput` and scales the read into the blue channel: `vec4(0.0, 0.0, float(subpassLoad(inputValue).r) / 256.0, 1.0)`. The reference image is `(0.0, 0.0, 0.5, 1.0)`.

### Memory-property mode

Each value selects a different backing memory for the transient attachment. This is the axis that distinguishes the `_lazy_bit` cases from the `_local_bit` cases.

#### `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT`: lazy backing

The transient attachment is bound with `MemoryRequirement::LazilyAllocated`. This is the spec-intended path for transient usage: the implementation may back the image with lazily committed memory and may avoid allocating it entirely when the contents are not needed after the render pass. The `_lazy_bit` cases exercise this path.

#### `VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT`: device-local backing

The transient attachment is bound with `MemoryRequirement::Local`. The transient usage bit and the memory-property selection are independent, so a device-local transient attachment is a legal configuration that must still preserve contents across the clear/load handoff. The `_local_bit` cases exercise this path and catch defects that are not specific to lazy memory.

## Shader Analysis

The shader path is the same for every case; only the input attachment declaration and the output decode change with the attachment mode. One walkthrough covers the structure, and the per-mode decode differences are summarized in the Parameter Variation Summary.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.fragment_operations.transient_attachment_bit.color_load_store_op_test_lazy_bit
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| attachment mode `color` | The transient attachment is a color image; the fragment shader copies the input attachment value directly to its output, so this is the simplest decode path. |
| memory-property `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` | The transient attachment is backed by lazily allocated memory, the spec-intended transient path. |

#### Purpose

Read the cleared transient attachment value back through a fragment-shader input attachment and copy it to the output color attachment, so the host can compare the output against the expected cleared value.

#### Structural Design

The fragment shader is a single read-and-write with no control flow.

| Phase | Operation |
|-------|-----------|
| Read | Load the input attachment texel at the fragment location through `subpassLoad`. |
| Write | Store the loaded value directly into the color output. |

#### Shader Code

##### Fragment Shader

```glsl
#version 450

/// Input attachment at binding 0: the transient attachment cleared in the first render pass and
/// preserved across a pipeline barrier into this subpass. subpassLoad reads the per-pixel value
/// back, which is what makes transient-attachment preservation observable.
layout(input_attachment_index = 0, binding = 0) uniform subpassInput inputValue;

layout(location = 0) out vec4 fragColor;

void main (void)
{
    fragColor = subpassLoad(inputValue);
}
```

##### Vertex Shader

```glsl
#version 450

layout(location = 0) in vec4 position;

out gl_PerVertex
{
    vec4 gl_Position;
};

void main (void)
{
    gl_Position = position;
}
```

#### Additional Info

- The vertex shader is a fixed pass-through and does not vary across the six cases. The test instance supplies six vertices forming two triangles that cover the full 32x32 render area.
- The fragment shader source is generated in [`TransientAttachmentTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L252-L296). Only the input attachment declaration type and the output expression change with the attachment mode.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Attachment mode `depth` | Declaration stays `subpassInput`; output becomes `vec4(subpassLoad(inputValue).r, 0.0, 0.0, 1.0)` to map the depth value into the red channel. | [`initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L289-L290) |
| Attachment mode `stencil` | Declaration becomes `usubpassInput`; output becomes `vec4(0.0, 0.0, float(subpassLoad(inputValue).r) / 256.0, 1.0)` to scale the unsigned stencil value into the blue channel. | [`initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L282-L283), [`initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L291-L292) |
| Memory-property mode | No shader-level variation. The memory-property axis changes only the backing memory of the transient attachment. | [`TransientAttachmentTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L366-L367) |

#### SPIR-V

##### Fragment Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 19
; Schema: 0
               OpCapability Shader
               OpCapability InputAttachment
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %fragColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %fragColor "fragColor"
               OpName %inputValue "inputValue"
               OpDecorate %fragColor Location 0
               OpDecorate %inputValue Binding 0
               OpDecorate %inputValue DescriptorSet 0
               OpDecorate %inputValue InputAttachmentIndex 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %fragColor = OpVariable %_ptr_Output_v4float Output
         %10 = OpTypeImage %float SubpassData 0 0 0 2 Unknown
%_ptr_UniformConstant_10 = OpTypePointer UniformConstant %10
 %inputValue = OpVariable %_ptr_UniformConstant_10 UniformConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
      %v2int = OpTypeVector %int 2
         %17 = OpConstantComposite %v2int %int_0 %int_0
       %main = OpFunction %void None %3
          %5 = OpLabel
         %13 = OpLoad %10 %inputValue
         %18 = OpImageRead %v4float %13 %17
               OpStore %fragColor %18
               OpReturn
               OpFunctionEnd
```

</details>

##### Vertex Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 18
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %position
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %position "position"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %position Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpLoad %v4float %position
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

The runtime flow in [`TransientAttachmentTestInstance::iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L372-L592) is:

- Create the transient input image with the mode-specific usage flags and bind it with the requested memory requirement (lazy or local). Create a second `R8G8B8A8_UNORM` output color image (device-local) and a host-visible result buffer.
- Build two render passes: [`renderPassOne`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L482-L484) clears only the transient attachment with `VK_ATTACHMENT_LOAD_OP_CLEAR` and `VK_ATTACHMENT_STORE_OP_STORE`; [`renderPassTwo`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L483-L484) declares the transient attachment as an input attachment and the output image as a color attachment, loading with `VK_ATTACHMENT_LOAD_OP_LOAD`.
- Record and submit a command buffer: begin pass one, end pass one (the clear happens on load), insert a [pipeline memory barrier](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L540-L551) from attachment write to `VK_ACCESS_INPUT_ATTACHMENT_READ_BIT` at the fragment-shader stage, begin pass two, bind the pipeline and the input-attachment descriptor set, draw six vertices, end pass two, copy the output image to the result buffer with a layout transition.
- On the host, invalidate the result buffer allocation, build a reference image cleared to the expected decoded output color, and compare with [`tcu::floatThresholdCompare()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L583-L584) using a per-component threshold of `Vec4(0.02)`.
- Pass if the comparison matches, fail otherwise. The comparison covers the whole 32x32 render area and each case is judged independently.

The expected decoded output color is the clear value transformed the way the fragment shader decodes it:

- color: `(1.0, 1.0, 0.0, 1.0)`
- depth: `(0.5, 0.0, 0.0, 1.0)`
- stencil: `(0.0, 0.0, 0.5f, 1.0)`

## Failure Meaning

### Failure Cause Mapping

Attachment mode axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `color` | Color-attachment clear/store/load path does not preserve the cleared value for input-attachment readback. |
| `depth` | Depth-aspect clear/store/load path or depth input-attachment read does not preserve the cleared 0.5 depth value. |
| `stencil` | Stencil-aspect clear/store/load path or unsigned stencil input-attachment read does not preserve the cleared 128 value. |

Memory-property mode axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` | Lazily allocated memory does not commit or preserve the transient attachment contents across the clear/load handoff. |
| `VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT` | Device-local transient attachment does not preserve contents across the clear/load handoff; not specific to lazy memory. |

If all six cases fail, the shared infrastructure (input-attachment descriptor binding, the pipeline barrier between pass one and pass two, or the two-pass clear/load design itself) is the more likely cause than any single axis value.

### Cause Analysis

#### Transient attachment contents not preserved across the clear/load handoff

**Possible failure symptoms:** the rendered output does not match the reference image built from the expected decoded clear value. The host-side `tcu::floatThresholdCompare()` reports a mismatch across the 32x32 render area and the case returns `TestStatus::fail("Rendered color image is not correct")`.

**Possible implementation causes:** the implementation dropped or corrupted the transient attachment contents between `VK_ATTACHMENT_STORE_OP_STORE` in pass one and `VK_ATTACHMENT_LOAD_OP_LOAD` in pass two. For lazy-backed cases this can mean the implementation never committed backing memory for the cleared attachment or discarded it after pass one. For device-local cases it points at the clear/store/load or layout-transition path for the transient usage bit. The Vulkan spec allows lazily allocated memory to commit zero memory initially and grow on demand, and marks transient attachment contents as only meaningful within a render pass instance; a failure here means the implementation did not preserve contents across the two-pass boundary the test deliberately constructs.

#### Input attachment read returns wrong per-pixel value

**Possible failure symptoms:** same image-comparison mismatch as above. The shader read a value that does not equal the cleared value at the fragment location.

**Possible implementation causes:** the input-attachment descriptor binding, the `subpassLoad` / `usubpassInput` read, or the aspect-mask selection did not return the preserved attachment value. For depth and stencil cases the source aspect is not the default color aspect, so an aspect-mask or input-attachment format mismatch is a candidate. Source-level investigation is needed to distinguish a descriptor or aspect issue from a preservation issue, since both produce the same observable comparison failure.

## Case Pruning

### Requirement-based pruning

[`TransientAttachmentTest::checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L299-L329) prunes a case before execution when the implementation cannot satisfy it:

- No memory type matches the requested property flag (`VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` or `VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT`); [`checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L299-L329) throws `NotSupportedError` after [`getMemoryTypeIndices()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L124-L134) returns no matches.
- The transient attachment format is not supported for the checked attachment-plus-transient image usage and optimal tiling, or the reported `sampleCounts` is zero; `checkSupport()` throws `NotSupportedError`.
- For stencil cases, if none of `VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, or `VK_FORMAT_D32_SFLOAT_S8_UINT` reports the depth-stencil attachment feature, [`getSupportedStencilFormat()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L102-L122) returns `VK_FORMAT_UNDEFINED` and the case is pruned.

### Design-based pruning

The test does not generate a parameter matrix programmatically. The six registered leaves are the full, fixed product of the two behavioral axes, so there is no design-based pruning beyond the choice not to enumerate further combinations.

## Key Takeaways

- The test exercises preservation of a transient attachment's cleared value across a `STORE` then `LOAD` handoff between two render-pass instances, observed through a fragment-shader input attachment read.
- The two behavioral axes are independent: attachment mode (color, depth, stencil) and memory-property mode (lazy, device-local). A failure localized to one axis value points at that aspect or memory path; a failure across all six points at shared infrastructure.
- Lazy-backed cases test the spec-intended transient path; device-local cases are a legal fallback that must also preserve contents, and a failure there is not specific to lazy memory.
- See `## Failure Meaning` for the detailed cause analysis of the two observable failure mechanisms.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration table (six cases) | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L607-L623) | The full registered leaf set and the two-axis crossing. |
| `createTransientAttachmentTests()` | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L601-L627) | Builds the `transient_attachment_bit` group and adds the six children. |
| `TestMode` enum | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L56-L62) | The attachment-mode axis. |
| `TransientAttachmentTest::initPrograms()` | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L252-L296) | Per-mode fragment and vertex shader generation. |
| `TransientAttachmentTest::checkSupport()` | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L299-L329) | Memory-type and format support gates. |
| `TransientAttachmentTestInstance::iterate()` | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L372-L592) | Clear, barrier, input-attachment draw, copyback, and comparison. |
| `getSupportedStencilFormat()` | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L102-L122) | First-supported stencil format selection. |
| `getMemoryTypeIndices()` | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L124-L134) | Memory-type discovery for the requested property flags. |
| `makeRenderPass()` | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L180-L224) | Builds both render passes, including the input-attachment reference for pass two. |
| Mustpass coverage | [`fragment-operations.txt`](../../../mustpass/main/vk-default/fragment-operations.txt#L146-L151) | Lists all six vk-default leaves for this family. |
| Header | [`vktFragmentOperationsTransientAttachmentTests.hpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.hpp) | Declares the group factory. |
