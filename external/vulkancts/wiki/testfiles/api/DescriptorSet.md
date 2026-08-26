## Overview

**Core question:** does the implementation correctly handle `VkDescriptorSetLayout` lifetime, legally empty layouts, and `vkUpdateDescriptorSets` writes that span multiple bindings?

The `api.descriptor_set` test family is implemented in [vktApiDescriptorSetTests.cpp](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1) and registered under the `api` test category by [`createApiTests`](../../../modules/vulkan/api/vktApiTests.cpp#L120-L120). It exercises three descriptor-set behaviors through three intermediate nodes:

- deferred `VkDescriptorSetLayout` lifetime after `VkPipelineLayout` creation;
- creation of legally empty descriptor set layouts, including the push-descriptor variant;
- `vkUpdateDescriptorSets` writes that spill into the next binding when the destination binding runs out of array elements.

The page covers what each intermediate node verifies, how the host-side setup and result checking work, what failure of each node means, and which cases are pruned for Vulkan SC.

## Background Knowledge

- **Pipeline layouts bake descriptor set layout state at creation time.** `vkCreatePipelineLayout` consumes one or more `VkDescriptorSetLayout` handles and copies their content into the resulting `VkPipelineLayout`. After that call returns, the descriptor set layout objects are no longer referenced by the pipeline layout and may be destroyed. A driver must not require the layout to remain alive when a pipeline is later created against the same pipeline layout.
- **Empty descriptor set layouts are a legal edge case.** `VkDescriptorSetLayoutCreateInfo` allows `bindingCount = 0` and `pBindings = nullptr`. The resulting layout is a valid object that can be used to allocate descriptor sets, create pipeline layouts, or be the target of push-descriptor updates when `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` is set. The push-descriptor flag requires the `VK_KHR_push_descriptor` extension.
- **`vkUpdateDescriptorSets` writes can span multiple bindings.** When a `VkWriteDescriptorSet` targets `dstBinding` with `dstArrayElement` and `descriptorCount`, and the destination binding has fewer than `descriptorCount` array elements remaining starting from `dstArrayElement`, the surplus writes continue into the next binding as long as each subsequent binding has the same `descriptorType` and the descriptor type is compatible.

## Registration Hierarchy

```text
api.descriptor_set
├── descriptor_set_layout_lifetime
├── descriptor_set_layout
└── descriptor_set_layout_binding
```

The `descriptor_set` test family is built by [`createDescriptorSetTests`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L664-L672). The three direct intermediate nodes are registered by `createDescriptorSetLayoutLifetimeTests`, `createDescriptorSetLayoutTests`, and `createDescriptorSetLayoutBindingOrderingTests`. The six executable test case leaves under this family are listed in [`api.txt`](../../../mustpass/main/vk-default/api.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `descriptor_set_layout_lifetime`, `descriptor_set_layout`, `descriptor_set_layout_binding` | Selects the descriptor-set property under test: deferred lifetime, empty-layout creation, or binding-order spill. | [vktApiDescriptorSetTests.cpp#L666-L670](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L666-L670) |
| Lifetime pipeline type | `graphics`, `compute` | Selects which pipeline-creation entry point exercises the lifetime property. The two leaves share the same lifetime mechanism. | [vktApiDescriptorSetTests.cpp#L610-L615](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L610-L615) |
| Empty-layout flags | `0`, `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` | Selects whether the empty layout is a normal layout or a push-descriptor layout. | [vktApiDescriptorSetTests.cpp#L626-L632](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L626-L632) |
| Binding-order case | `update_subsequent_binding`, `layout_binding_order` | Splits the binding-order concept into a host-side functional check and a declarative Amber check. | [vktApiDescriptorSetTests.cpp#L642-L649](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L642-L649) |

## Behavior Parameters

The primary behavioral axis is the intermediate node directly below `descriptor_set`. Each value tests a different descriptor-set property.

### `descriptor_set_layout_lifetime` — deferred layout lifetime after pipeline-layout creation

Both test case leaves in this node share the helper [`createPipelineLayoutDestroyDescriptorSetLayout`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L50-L67). That helper creates a `VkDescriptorSetLayout`, uses it to build a `VkPipelineLayout`, and then releases the source layout through a `Unique<VkDescriptorSetLayout>` when the helper returns. The test then creates a pipeline against the surviving pipeline layout and submits a no-op draw or dispatch.

The `graphics` leaf creates a graphics pipeline with `rasterizerDiscardEnable = VK_TRUE` and a render pass with no attachments, then issues a 3-vertex draw. The `compute` leaf creates a compute pipeline, binds a descriptor set, and dispatches a 1×1×1 workgroup. Both shaders are no-ops; the tested property is that pipeline creation and submit succeed after the source descriptor set layout has been destroyed.

### `descriptor_set_layout` — legally empty descriptor set layout creation

This node has a single registered child, `empty_set`, which contains two test case leaves. Both call [`emptyDescriptorSetLayoutTest`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L308-L332) with a `VkDescriptorSetLayoutCreateInfo` whose `bindingCount = 0` and `pBindings = nullptr`.

The `normal` leaf passes flags = 0. The `push_descriptor` leaf passes `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` and first gates on `VK_KHR_push_descriptor` device support through `context.requireDeviceFunctionality`. The tested property is that `vkCreateDescriptorSetLayout` accepts both create-info variants on hardware that advertises the relevant extension.

### `descriptor_set_layout_binding` — binding-order spill in `vkUpdateDescriptorSets`

This node contains two test case leaves. The `update_subsequent_binding` leaf is the functional check. It builds a layout with three bindings: binding 0 holds two `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` descriptors, binding 1 holds one `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` descriptor, and binding 2 holds one `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` descriptor. It then issues a single `VkWriteDescriptorSet` with `dstBinding = 0`, `dstArrayElement = 0`, `descriptorCount = 3`. The first two writes fill binding 0; the third spills into binding 1 because the bindings have the same descriptor type. A second write puts one storage buffer descriptor into binding 2. A compute shader copies the source value of `5` from each of the three uniform buffer slots into a storage buffer; the test passes only when all three result slots equal `5`.

The `layout_binding_order` leaf is an Amber-driven case loaded from the data directory `api/descriptor_set/descriptor_set_layout_binding`. The C++ source registers it with the description string `"Test descriptor set layout binding order"`. The Amber script itself is not present in this repository's working tree; it is fetched by the CTS source-fetch step. The functional `update_subsequent_binding` leaf is the source-grounded description of the binding-order behavior tested by this node.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.api.descriptor_set.descriptor_set_layout_binding.update_subsequent_binding
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `descriptor_set_layout_binding` | Selects the descriptor-write binding-order tests, including the rule that a write continues into a compatible subsequent binding. |
| `update_subsequent_binding` | Selects the C++ functional case whose generated compute shader observes two descriptors at binding 0 and the spill target at binding 1. |
| Compute stage, one `1 × 1 × 1` workgroup | Runs one invocation, so each of the three shader reads maps directly to one host-checked output without invocation-dependent indexing. |

#### Purpose

This compute shader makes the cross-binding descriptor update observable: it reads both uniform-buffer descriptors at binding 0 and the subsequent uniform-buffer descriptor at binding 1, then writes the three values to separately checked result slots.

#### Structural Design

| Shader-visible resource | Descriptor location | Shader operation | Validation role |
|-------------------------|---------------------|------------------|-----------------|
| `uniformbufferarray[0]` | Set 0, binding 0, element 0 | Read `data` into `results.result0` | Confirms the first descriptor written at binding 0. |
| `uniformbufferarray[1]` | Set 0, binding 0, element 1 | Read `data` into `results.result1` | Confirms the second descriptor fills binding 0. |
| `uniformbuffer2` | Set 0, binding 1 | Read `data` into `results.result2` | Confirms the third descriptor spills into the subsequent binding. |
| `results` | Set 0, binding 2 | Store three 32-bit integers | Supplies the 12-byte host-visible result checked as `5, 5, 5`. |

#### Shader Code

```glsl
#version 310 es
/// One compute invocation reads the three uniform-buffer descriptors written by the host.
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Set 0, binding 0 is a two-element uniform-buffer descriptor array; both elements reference the 4-byte source buffer containing 5.
layout (set = 0, binding = 0) uniform UniformBuffer0 {
    int data;
} uniformbufferarray[2];
/// Set 0, binding 1 is the one-descriptor spill target of the three-element write that starts at binding 0.
layout (set = 0, binding = 1) uniform UniformBuffer2 {
    int data;
} uniformbuffer2;
/// Set 0, binding 2 is a 12-byte storage buffer whose three integers are checked by the host.
layout (set = 0, binding = 2) buffer StorageBuffer {
    int result0;
    int result1;
    int result2;
} results;

void main (void)
{
    /// Copy each descriptor-visible value into a distinct host-checked result slot.
    results.result0 = uniformbufferarray[0].data;
    results.result1 = uniformbufferarray[1].data;
    results.result2 = uniformbuffer2.data;
}
```

#### Additional Info

- The host supplies the same 4-byte uniform buffer containing `5` through all three `VkDescriptorBufferInfo` entries, so descriptor placement—not differing input data—is what determines whether all outputs become `5` ([source](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L350-L378)).
- A single write starts at binding 0 with `descriptorCount = 3`; binding 0 has only two elements, while the compatible binding 1 has one, making the third shader read the direct signal for the subsequent-binding update ([source](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L386-L407), [write](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L454-L465)).
- After dispatch, the host invalidates the result allocation and requires all three integers to equal `5` ([source](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L541-L555)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Binding-order case | `update_subsequent_binding` uses this generated compute shader and host readback. The sibling `layout_binding_order` case instead runs an Amber script, so it does not use this C++ shader builder. | [vktApiDescriptorSetTests.cpp#L637-L650](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L637-L650) |
| Descriptor bindings within the selected case | Binding 0 is a two-element uniform-buffer array, binding 1 is a single uniform buffer, and binding 2 is the storage result. These fixed declarations mirror the layout that permits the three-descriptor write to cross from binding 0 to binding 1. | [vktApiDescriptorSetTests.cpp#L386-L407](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L386-L407), [shader builder](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L578-L601) |

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
; Bound: 35
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource ESSL 310
               OpName %main "main"
               OpName %StorageBuffer "StorageBuffer"
               OpMemberName %StorageBuffer 0 "result0"
               OpMemberName %StorageBuffer 1 "result1"
               OpMemberName %StorageBuffer 2 "result2"
               OpName %results "results"
               OpName %UniformBuffer0 "UniformBuffer0"
               OpMemberName %UniformBuffer0 0 "data"
               OpName %uniformbufferarray "uniformbufferarray"
               OpName %UniformBuffer2 "UniformBuffer2"
               OpMemberName %UniformBuffer2 0 "data"
               OpName %uniformbuffer2 "uniformbuffer2"
               OpDecorate %StorageBuffer BufferBlock
               OpMemberDecorate %StorageBuffer 0 Offset 0
               OpMemberDecorate %StorageBuffer 1 Offset 4
               OpMemberDecorate %StorageBuffer 2 Offset 8
               OpDecorate %results Binding 2
               OpDecorate %results DescriptorSet 0
               OpDecorate %UniformBuffer0 Block
               OpMemberDecorate %UniformBuffer0 0 Offset 0
               OpDecorate %uniformbufferarray Binding 0
               OpDecorate %uniformbufferarray DescriptorSet 0
               OpDecorate %UniformBuffer2 Block
               OpMemberDecorate %UniformBuffer2 0 Offset 0
               OpDecorate %uniformbuffer2 Binding 1
               OpDecorate %uniformbuffer2 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%StorageBuffer = OpTypeStruct %int %int %int
%_ptr_Uniform_StorageBuffer = OpTypePointer Uniform %StorageBuffer
    %results = OpVariable %_ptr_Uniform_StorageBuffer Uniform
      %int_0 = OpConstant %int 0
%UniformBuffer0 = OpTypeStruct %int
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_arr_UniformBuffer0_uint_2 = OpTypeArray %UniformBuffer0 %uint_2
%_ptr_Uniform__arr_UniformBuffer0_uint_2 = OpTypePointer Uniform %_arr_UniformBuffer0_uint_2
%uniformbufferarray = OpVariable %_ptr_Uniform__arr_UniformBuffer0_uint_2 Uniform
%_ptr_Uniform_int = OpTypePointer Uniform %int
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
%UniformBuffer2 = OpTypeStruct %int
%_ptr_Uniform_UniformBuffer2 = OpTypePointer Uniform %UniformBuffer2
%uniformbuffer2 = OpVariable %_ptr_Uniform_UniformBuffer2 Uniform
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpAccessChain %_ptr_Uniform_int %uniformbufferarray %int_0 %int_0
         %19 = OpLoad %int %18
         %20 = OpAccessChain %_ptr_Uniform_int %results %int_0
               OpStore %20 %19
         %22 = OpAccessChain %_ptr_Uniform_int %uniformbufferarray %int_1 %int_0
         %23 = OpLoad %int %22
         %24 = OpAccessChain %_ptr_Uniform_int %results %int_1
               OpStore %24 %23
         %29 = OpAccessChain %_ptr_Uniform_int %uniformbuffer2 %int_0
         %30 = OpLoad %int %29
         %31 = OpAccessChain %_ptr_Uniform_int %results %int_2
               OpStore %31 %30
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- In the lifetime cases, the host builds a descriptor set layout, uses it to create a pipeline layout, releases the layout, then creates a graphics or compute pipeline and submits a command buffer that draws or dispatches. Pass is returned unconditionally after `submitCommandsAndWait` returns; Vulkan errors from `vkCreate*Pipelines` or `vkQueueSubmit` are converted into test failures by the CTS `VK_CHECK` helpers used by the create and submit wrappers, so a returned error surfaces as a test failure rather than as a silent pass.
- In the empty-layout cases, the host calls `vkCreateDescriptorSetLayout` with `bindingCount = 0` and the chosen flags. Pass is returned unconditionally after `createDescriptorSetLayout` returns; `VK_CHECK` inside the wrapper converts a non-`VK_SUCCESS` return into a test failure.
- For `update_subsequent_binding`, the host creates the descriptor set layout and pool, allocates a descriptor set, issues the two `vkUpdateDescriptorSets` calls, builds and dispatches a compute pipeline, then invalidates the result allocation and reads three `uint32_t` slots. Pass requires `resultPtr[0] == 5 && resultPtr[1] == 5 && resultPtr[2] == 5`; any other value produces `tcu::TestStatus::fail("Fail")`.
- For `layout_binding_order`, the host loads and runs the Amber script. Pass and fail are decided by the Amber harness based on the assertions in `layout_binding_order.amber`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `descriptor_set_layout_lifetime` | Driver or validation layers incorrectly require the `VkDescriptorSetLayout` to remain alive after `VkPipelineLayout` creation, or pipeline creation/execution fails because the layout was destroyed. |
| `descriptor_set_layout` | `vkCreateDescriptorSetLayout` rejects a legally empty `VkDescriptorSetLayoutCreateInfo`, or rejects the `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` flag on a device that advertises `VK_KHR_push_descriptor`. |
| `descriptor_set_layout_binding` | `vkUpdateDescriptorSets` does not spill writes into the next binding when the destination binding runs out of array elements, or the Amber-declared equivalent fails for the same reason. |

### Cause Analysis

#### `descriptor_set_layout_lifetime` failures

**Possible failure symptoms:** `vkCreateGraphicsPipelines` or `vkCreateComputePipelines` returns a non-`VK_SUCCESS` result, or `vkQueueSubmit` fails, or the validation layers report an error referencing the destroyed descriptor set layout. The test reports fail through the `VK_CHECK` path inside the CTS create and submit wrappers.

**Possible implementation causes:** the driver captures the `VkDescriptorSetLayout` handle rather than copying its content at `vkCreatePipelineLayout` time and then dereferences the destroyed handle during pipeline creation; the validation layers incorrectly flag the destroyed layout as a use-after-free; or the driver depends on a host-side mirror of the layout that was de-allocated when the layout was destroyed. Per Vulkan spec, the descriptor set layout state is baked into the pipeline layout at creation time and the source handle may be destroyed afterward, so any of these would be a conformance bug.

#### `descriptor_set_layout` failures

**Possible failure symptoms:** `vkCreateDescriptorSetLayout` returns a non-`VK_SUCCESS` result for a `VkDescriptorSetLayoutCreateInfo` with `bindingCount = 0`, or returns an error specifically for the `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` flag on a device that advertises `VK_KHR_push_descriptor`. The `VK_CHECK` inside `createDescriptorSetLayout` surfaces this as a test failure.

**Possible implementation causes:** the driver rejects the empty-binding edge case in its create-info validation, or the push-descriptor flag path is gated on the wrong extension query. For the `push_descriptor` case the test first calls `context.requireDeviceFunctionality("VK_KHR_push_descriptor")`, so a failure on a device that does not advertise the extension is a test skip rather than a test failure; an actual fail means the extension is advertised but the flag is rejected.

#### `descriptor_set_layout_binding` failures

**Possible failure symptoms:** for `update_subsequent_binding`, the host reads back result slots that do not all equal `5`. At least one of the three uniform buffer reads observed a value other than `5`, which means at least one of the three descriptors was not bound to the source buffer as expected. The test reports `tcu::TestStatus::fail("Fail")` after the comparison.

**Possible implementation causes:** `vkUpdateDescriptorSets` did not spill the third `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` write into binding 1 when binding 0 ran out of array elements, so binding 1's descriptor was left unbound or pointed at a stale resource; the binding-order spill rule was applied across incompatible descriptor types when it should not have been; or the descriptor write was silently truncated to the first binding. Source-level investigation of the driver's update-descriptor path is needed to confirm which of these applies. For the Amber-driven `layout_binding_order` case, the symptom and cause depend on the assertions in `layout_binding_order.amber`, which is not present in this repository's working tree; the C++ source's description string `"Test descriptor set layout binding order"` is the only on-tree documentation of its intent.

## Case Pruning

### Requirement-based pruning

- `descriptor_set_layout.empty_set.push_descriptor` is excluded from the Vulkan SC test set by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L628-L633) because `VK_KHR_push_descriptor` is not part of Vulkan SC.
- `descriptor_set_layout_binding.layout_binding_order` is excluded from the Vulkan SC test set by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L645-L650). Unlike the `push_descriptor` leaf, the source does not document the specific Vulkan SC incompatibility for this Amber case, and the Amber script is not in the working tree.
- The `push_descriptor` leaf additionally self-skips at runtime through `context.requireDeviceFunctionality("VK_KHR_push_descriptor")` if the device does not advertise the extension.

### Design-based pruning

- The lifetime node does not generate a separate leaf for each pipeline bind point; only `graphics` and `compute` are registered because they cover the two pipeline-creation entry points that the lifetime property exercises. Other bind points (ray tracing, mesh) are out of scope for this test family.
- The empty-set node does not generate leaves that allocate descriptor sets or create pipeline layouts from the empty layout. The node's scope is `vkCreateDescriptorSetLayout` acceptance only.
- The binding-order node exercises one specific spill pattern (a single write that spans two `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` bindings) and one storage-buffer write into a separate binding. Other spill patterns, such as writes that span three or more bindings or that mix descriptor types, are out of scope.

## Key Takeaways

- The `descriptor_set` test family covers three distinct descriptor-set properties, one per intermediate node: deferred layout lifetime after pipeline-layout creation, legally empty layout creation, and binding-order spill in `vkUpdateDescriptorSets`.
- The lifetime cases rely on `VK_CHECK` inside the CTS create and submit wrappers to convert Vulkan errors into test failures; they do not inspect a shader-observed value.
- The `update_subsequent_binding` case is the only leaf in this family that reads back a shader-written result. Its pass condition `resultPtr[0] == 5 && resultPtr[1] == 5 && resultPtr[2] == 5` directly verifies that the spill write reached binding 1 after filling binding 0.
- Two test case leaves (`push_descriptor` and `layout_binding_order`) are pruned for Vulkan SC because they depend on `VK_KHR_push_descriptor` or behavior that Vulkan SC does not include.
- See `## Failure Meaning` for the cause analysis behind each behavior parameter value's failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDescriptorSetTests` registration | [vktApiDescriptorSetTests.cpp#L664-L672](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L664-L672) | Builds the `descriptor_set` test family and adds the three intermediate nodes. |
| Parent registration in `createApiTests` | [vktApiTests.cpp#L120-L120](../../../modules/vulkan/api/vktApiTests.cpp#L120-L120) | Adds `createDescriptorSetTests` under the `api` test category. |
| `createPipelineLayoutDestroyDescriptorSetLayout` | [vktApiDescriptorSetTests.cpp#L50-L67](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L50-L67) | Shared lifetime helper: creates the pipeline layout, then releases the descriptor set layout. |
| `descriptorSetLayoutLifetimeGraphicsTest` | [vktApiDescriptorSetTests.cpp#L69-L226](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L69-L226) | Graphics lifetime path: creates a render pass, graphics pipeline, framebuffer, and submits a draw. |
| `descriptorSetLayoutLifetimeComputeTest` | [vktApiDescriptorSetTests.cpp#L228-L306](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L228-L306) | Compute lifetime path: builds a compute pipeline and dispatches a no-op shader. |
| `emptyDescriptorSetLayoutTest` | [vktApiDescriptorSetTests.cpp#L308-L332](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L308-L332) | Empty-layout creation entry; takes the create flags as a parameter. |
| `descriptorSetLayoutBindingOrderingTest` | [vktApiDescriptorSetTests.cpp#L334-L556](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L334-L556) | Functional binding-order test: issues the spill write and compares three result slots. |
| Inline GLSL shader sources | [vktApiDescriptorSetTests.cpp#L559-L601](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L559-L601) | Vertex, compute, and binding-order shaders used by the three shader-bearing leaves. |
| Empty-set registration | [vktApiDescriptorSetTests.cpp#L620-L635](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L620-L635) | Registers `normal` and `push_descriptor` under `empty_set`; gates `push_descriptor` on Vulkan SC. |
| Binding-order registration | [vktApiDescriptorSetTests.cpp#L637-L653](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L637-L653) | Registers `update_subsequent_binding` and the Amber `layout_binding_order` case. |
| Mustpass entries | [api.txt](../../../mustpass/main/vk-default/api.txt) | Lists the six registered test case leaves under `dEQP-VK.api.descriptor_set.*`. |
