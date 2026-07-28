# Understanding Brief: `binding_model.push_constant_bank`

## One-Sentence Test Purpose

This test checks whether compute and graphics shaders read the value selected for each `VK_NV_push_constant_bank` bank when the host uses ordinary push constants, a shader `member_offset`, or descriptor-heap push data.

## Background Knowledge

### Bank selection and member placement

A push constant block belongs to the shader's `PushConstant` storage class. With `VK_NV_push_constant_bank`, `BankNV` selects a hardware bank and `MemberOffsetNV` adds an offset within that bank. The API and shader declarations must agree about the bank and byte range. The ordinary path also uses pipeline-layout push constant ranges, whose stage visibility and byte coverage define the interface consumed by a draw or dispatch ([push constant interface](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1045-L1095), [push constant ranges and updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L5160-L5208)).

Why it matters here:

- The generated shader declares eight bank-qualified blocks and copies one `uint` from each block to a result buffer.
- The member-offset cases add either 4 or 16 bytes to the shader-side bank address while the host records a matching nonzero command offset.

### Ordinary push constants and descriptor-heap push data

Ordinary `vkCmdPushConstants2` updates use a pipeline layout. A later draw or dispatch must use a layout compatible with the layout that established the push constant values. Descriptor-heap pipelines use `VK_PIPELINE_CREATE_2_DESCRIPTOR_HEAP_BIT_EXT` and descriptor mappings instead of descriptor-set layouts. They receive shader-visible `PushConstant` data through `vkCmdPushDataEXT`, because ordinary push constant commands are not compatible with descriptor heaps ([pipeline layout compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2021-L2055), [descriptor-heap push data](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L965-L1033), [descriptor-heap pipeline flag](../../../../vulkan-docs/src/chapters/pipelines.adoc#L495-L499)).

Why it matters here:

- `basic` binds a descriptor set for the result buffer, attempts to create a pipeline layout with one push constant range per active bank, and sends banked data with `vkCmdPushConstants2`.

The source range helper returns one `VkPushConstantRange` per active bank, with the same stage flags on every entry. The Vulkan pipeline-layout validity rule says that any two range entries must not include the same stage in `stageFlags`. `VkPushConstantRange` describes stage visibility and byte coverage, not a bank. Treat the repeated ranges as the source configuration under test, not as evidence that Vulkan provides one independently legal range per bank ([push constant range](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1841-L1891), [pipeline-layout validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1702-L1706), [range helper](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L174-L185)).
- `descriptor_heap` writes the result-buffer descriptor into a resource heap, maps shader set 0 binding 0 to heap offset 0, creates a pipeline with no pipeline layout, and sends each bank value with `vkCmdPushDataEXT`.

## One Concrete Example

The leaf `dEQP-VK.binding_model.push_constant_bank.basic.compute_member_offset_4` requests four active banks. Its generated compute shader includes blocks of this form:

```glsl
layout(push_constant, bank = 2, member_offset = 4) uniform PushConstantBank2 {
    uint data;
} bank2;

void main() {
    resultData.bank[2] = bank2.data;
}
```

The host creates four push constant range entries for the compute stage, each beginning at byte 0 and sized for the 4-byte offset plus one `uint`. For bank 2 it chains `VkPushConstantBankInfoNV{bank = 2}` to `VkPushConstantsInfo`, records a command offset of 4, and places the value 2 at the start of the supplied byte array. After one dispatch, the shader's bank-2 load should make `resultData.bank[2]` equal 2 ([range and upload helpers](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L174-L216), [member-offset compute execution](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1003-L1068)).

## End-to-End Test Flow

```text
1. Ordinary push-constant path
[host] choose compute or graphics, requested bank count, and optional member offset
[host] query the matching push-constant-bank limit and cap the active bank count at that limit and 8
[host] create a host-visible result buffer, initialize all eight words to 0xffffffff, and bind it through descriptor set 0 binding 0
[host] create one push constant range per active bank and create the compute or graphics pipeline with that layout
[host] bind the pipeline and descriptor set
[host] record one vkCmdPushConstants2 update per active bank with VkPushConstantBankInfoNV
[host] dispatch one workgroup or draw one point
[device] load every declared bank and write each value to the matching result-buffer word
[host] make shader writes available to host reads, submit, and wait
[host] invalidate the result allocation and compare the active prefix against 0, 1, ..., activeBankCount - 1

2. Descriptor-heap push-data path
[host] choose compute or graphics and a requested bank count
[host] query the matching push-data-bank limit and cap the active bank count at that limit and 8
[host] create a resource-heap buffer with one aligned result-buffer descriptor plus the implementation's reserved range
[host] create and initialize a device-addressable, host-visible result buffer
[host] encode the result-buffer descriptor at resource-heap offset 0 and flush both allocations
[host] create a descriptor-heap pipeline with a constant-offset mapping for set 0 binding 0 and no pipeline layout
[host] record host-write barriers, bind the pipeline and resource heap, and record one vkCmdPushDataEXT update per active bank
[host] dispatch one workgroup or draw one point
[device] resolve the storage buffer through the heap mapping, read each push-data bank through PushConstant storage, and write the observed values
[host] make shader writes available to host reads, submit, and wait
[host] invalidate the result allocation and compare the active prefix against the bank indices
```

The graphics flow begins dynamic rendering without attachments and uses rasterizer discard. The single vertex shader invocation performs the result-buffer stores before rasterization ([ordinary runtime paths](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L469-L593), [descriptor-heap runtime paths](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L598-L998)).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`PushConstantBankTestCase::initPrograms` emits GLSL 4.60 and requires `GL_NV_push_constant_bank`. The generator declares eight bank-qualified push constant blocks and an eight-word write-only result block. Compute cases add `layout(local_size_x = 1) in`; graphics cases add a `gl_Position` store. Member-offset cases add the selected `member_offset` to every bank declaration. The source collection uses its default CTS build options, whose baseline target is SPIR-V 1.0 ([shader generator](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1218-L1299), [baseline target](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Eight-word result buffer | yes | yes, as set 0 binding 0 or through resource-heap offset 0 | shader writes | yes | Carries the shader-observed value for each declared bank. |
| Ordinary descriptor set | yes | yes, only in `basic` | shader resolves the result buffer through it | no | Keeps result transport separate from the banked push constants. |
| Push constant ranges and pipeline layout | yes | used by ordinary pipeline creation and push updates | shader consumes the covered `PushConstant` interface | no | Defines the ordinary path's stage and byte coverage. |
| Resource heap | yes, only in `descriptor_heap` | yes, by device address | shader reads the encoded result-buffer descriptor | no | Replaces descriptor-set binding for the result buffer. |
| Push constants or push data | command state supplied by host | consumed by the draw or dispatch | shader reads | observed indirectly | Carries bank index `N` in bank `N`. |
| Reserved resource-heap range | yes, only in `descriptor_heap` | included in the bound heap range | reserved for implementation use | no | Satisfies the advertised `minResourceHeapReservedRange` requirement. |

The descriptor-heap code is implemented in this source file rather than delegated to `vktBindingDescriptorHeapTests.cpp`. It calls the descriptor-heap API directly to size the heap, encode the descriptor, attach the mapping, bind the heap, and push data.

## What Is Checked

- The host initializes every result word to `~0u`, so an unwritten active slot remains visibly wrong.
- After execution and an allocation invalidation, the host checks each active bank `N` for the exact value `N`.
- The active count is `min(requested count, matching device bank limit, 8)`. A leaf whose name requests more banks than the device exposes checks only the supported prefix.
- Any active mismatch logs the bank index, the member offset when nonzero, the expected value, and the observed value, then returns `Result mismatch` ([host validator](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L218-L238)).

## Behavior Parameter Identification

> **Behavior parameter:** transport and bank-layout behavior group
>
> **Candidate values:** `basic / zero-offset push constants`, `basic / member_offset push constants`, `descriptor_heap / push-data banks`

The shader stage and requested bank count change coverage inside each group. The three values above change the API transport or shader address calculation and therefore form the primary behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic / zero-offset push constants` | Bank selection, ordinary push-constant upload, stage visibility, or pipeline-layout compatibility is wrong. |
| `basic / member_offset push constants` | Bank selection or the combined API offset and shader `member_offset` address calculation is wrong. |
| `descriptor_heap / push-data banks` | Push-data bank selection, descriptor-heap pipeline mapping, heap binding/descriptor encoding, or heap memory visibility is wrong. |

A mismatch shared by all three groups can also come from generated shader lowering, result-buffer writes, shader-to-host synchronization, or host cache invalidation rather than the selected bank transport.

## Important Variations and Special Cases

- `basic` registers compute and graphics leaves for requested bank counts 1, 2, 4, and 8. It also registers compute and graphics member-offset leaves for offsets 4 and 16 with a requested count of 4.
- `descriptor_heap` registers compute and graphics leaves for requested bank counts 1, 4, and 8. These cases use offset 0 and the separate push-data limits.
- Compute and graphics select independent limits. Ordinary cases use `maxComputePushConstantBanks` or `maxGraphicsPushConstantBanks`; heap cases use `maxComputePushDataBanks` or `maxGraphicsPushDataBanks` ([bank limits](../../../../vulkan-docs/src/chapters/limits.adoc#L5384-L5424)).
- Graphics requires `vertexPipelineStoresAndAtomics` because the vertex shader writes the storage buffer. Heap cases add descriptor-heap, buffer-device-address, shader-untyped-pointer, and synchronization2 extension requirements ([support checks](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1144-L1205)).
- The default Vulkan mustpass file lists 18 leaves: 12 in `basic` and 6 in `descriptor_heap` ([mustpass range](../../../mustpass/main/vk-default/binding-model.txt#L60502-L60519)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test parameters and path classification | [`TestType` and `TestParams`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L56-L90) | Separates compute, graphics, heap, and member-offset behavior. |
| Ordinary resource, range, upload, and validation helpers | [helpers](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L118-L260) | Defines the result sentinel, descriptor set, ranges, banked updates, and exact host comparison. |
| Ordinary execution | [`runComputeTest` and `runGraphicsTest`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L469-L593) | Shows command order and shader-to-host completion. |
| Descriptor-heap execution | [`runComputeDescriptorHeapTest` and `runGraphicsDescriptorHeapTest`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L598-L998) | Defines heap sizing, descriptor encoding, mapping, barriers, binding, and push-data commands. |
| Member-offset execution | [member-offset paths](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1003-L1133) | Shows range size, command upload, and validation for offsets 4 and 16. |
| Support and custom device requirements | [support checks](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1144-L1205), [device creation](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L336-L443) | Connects each path to feature, extension, stage, and limit requirements. |
| Shader generation | [`initPrograms`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1218-L1299) | Produces the exact GLSL interface used by all leaves. |
| Registration | [population and family creation](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1301-L1399), [test-category entrypoint](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L70) | Confirms the two intermediate nodes and all generated leaf dimensions. |
| Mustpass evidence | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L60502-L60519) | Confirms the exact 18 executable paths in the default Vulkan list. |
| Push constants and compatibility | [push constant updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L5160-L5295), [pipeline layout compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2021-L2055) | Defines ordinary update state, byte ranges, and layout compatibility. |
| Descriptor heaps and push-data banks | [heap use](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L663-L724), [push data and bank selection](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L965-L1110) | Defines heap state, push-data transport, bank chaining, and per-stage bank bounds. |
| Shader bank interface and limits | [push constant interface](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1045-L1095), [bank decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2971-L2993), [bank limits](../../../../vulkan-docs/src/chapters/limits.adoc#L5384-L5424) | Defines shader placement and the four path-specific limits. |
| Synchronization model | [memory dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#L110-L180) | Explains why result and heap writes need explicit availability and visibility. |

## Questions / Risk Points for User Audit

- Is the distinction between ordinary push constants and descriptor-heap push data clear? Yes. Their layouts, commands, descriptor transport, and limits are described separately.
- Is `member_offset` tied to both shader placement and host upload? Yes. The concrete example and ordinary flow show both sides.
- Is the named bank count distinguished from the active bank count? Yes. Runtime clipping and active-prefix validation are explicit.
- Are generated shader declarations distinguished from host-created resources? Yes. Push constant blocks are command state in the shader interface, while the result and heap buffers are host-created resources.
- Is the descriptor-heap path delegated elsewhere? No. Source inspection confirms that this file implements it directly.
- No unresolved semantic risk remains after checking implementation, registration, mustpass, compiler output, and the push constant, descriptor heap, interface, pipeline, synchronization, and limits chapters.

## Conversion Notes for Final Wiki Rewrite

- Keep the three behavior groups as the primary axis and copy the Failure Cause Mapping table without changes.
- Turn `basic.compute_member_offset_4` into the single representative shader walkthrough. It includes bank selection and the only shader declaration branch not covered by the zero-offset form.
- Explain descriptor-heap setup in the runtime section rather than adding a nearly identical second shader. Its generated shader differs only by omitting `member_offset`; the host transport carries the meaningful distinction.
- Preserve the active-count clipping rule, exact 18-leaf mustpass count, heap reserved-range calculation, and active-prefix host validation.
- Keep source navigation in the appendix and retain narrow specification links beside normative claims.
