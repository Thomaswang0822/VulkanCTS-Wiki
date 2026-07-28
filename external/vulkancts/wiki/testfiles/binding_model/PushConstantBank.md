## Overview

**Core question:** Does each compute or graphics invocation read the value uploaded to its selected push constant bank, including a nonzero member offset and descriptor-heap push data?

- The `push_constant_bank` test family implements two intermediate nodes. `basic` uses `vkCmdPushConstants2` with a pipeline layout; `descriptor_heap` uses `vkCmdPushDataEXT`, a descriptor mapping, and a bound resource heap.
- Every generated shader declares eight bank-qualified push constant blocks and copies their `uint` values to an eight-word result buffer. Each leaf activates a supported prefix of those banks.
- The primary behavior groups are zero-offset ordinary push constants, ordinary push constants with `member_offset`, and descriptor-heap push-data banks. Compute and graphics variants exercise separate bank limits and shader stages.
- Host validation requires result word `N` to equal bank index `N` for every active bank.

## Background Knowledge

For the shared concept of availability and visibility, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Push constant banks and member placement.** `BankNV` selects the hardware bank used by a `PushConstant` variable or block. `MemberOffsetNV` adds an offset within that bank. The API-provided byte range and shader decorations together determine placement ([push constant interface](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1045-L1095), [bank decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2971-L2993)).
- **Pipeline-layout compatibility.** Ordinary push constants are programmed against a pipeline layout. A draw or dispatch must use a layout compatible for push constants with the layout that established the values; identical push constant ranges define that compatibility ([pipeline layout compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2021-L2055), [push constant state](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L5160-L5208)).
- **Descriptor-heap push data.** A descriptor-heap pipeline uses descriptor mappings instead of descriptor-set layouts and may have a null pipeline layout. `vkCmdPushDataEXT` supplies its `PushConstant` storage because ordinary push constant commands are incompatible with descriptor heaps ([descriptor-heap pipeline flag](../../../../vulkan-docs/src/chapters/pipelines.adoc#L495-L499), [push data](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L965-L1033)).
- **Memory availability and visibility.** Command execution order alone does not make host writes visible to shaders or shader writes visible to the host. The heap path uses host-to-shader barriers for the encoded descriptor and result sentinel, and both paths establish shader-to-host visibility before readback ([memory dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#L110-L180)).

## Registration Hierarchy

```text
binding_model.push_constant_bank
├── basic
└── descriptor_heap
```

The `binding_model` dispatcher registers this test family only outside Vulkan SC builds ([test-category registration](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L70)). The default Vulkan mustpass file contains 18 leaves: 12 under `basic` and 6 under `descriptor_heap` ([mustpass range](../../../mustpass/main/vk-default/binding-model.txt#L60502-L60519)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `basic`, `descriptor_heap` | Selects ordinary pipeline-layout push constants or descriptor-heap push data. | [family creation](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1385-L1399) |
| Shader stage | `compute`, `graphics` | Uses a one-invocation compute dispatch or a one-vertex draw. Each stage has independent ordinary and push-data bank limits. | [test types](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L59-L90), [limits](../../../../vulkan-docs/src/chapters/limits.adoc#L5384-L5424) |
| Requested bank count in `basic` | `1`, `2`, `4`, `8` | Selects the requested active prefix for zero-offset ordinary cases. | [`populateBasicTests`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1301-L1327) |
| Requested bank count in `descriptor_heap` | `1`, `4`, `8` | Selects the requested active prefix for push-data cases. | [`populateDescriptorHeapTests`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1354-L1381) |
| `member_offset` in `basic` | `4`, `16` | Adds a shader-side bank offset and selects a matching nonzero host command offset. These leaves request four banks. | [member-offset registration](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1329-L1351), [member-offset execution](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1003-L1133) |
| Active bank count | `min(requested, matching device limit, 8)` | Prevents a leaf from addressing banks beyond its path-specific limit or the test's fixed eight-bank result array. | [ordinary clipping](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L469-L477), [heap clipping](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L598-L609) |

The implementation queries four different limits. Compute and graphics ordinary paths use `maxComputePushConstantBanks` and `maxGraphicsPushConstantBanks`; heap paths use `maxComputePushDataBanks` and `maxGraphicsPushDataBanks`. `VkPushConstantBankInfoNV::bank` must stay below the limit selected by the command and stage ([bank selection validity](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1035-L1107)).

## Behavior Parameters

The primary axis is the transport and bank-layout behavior group. Stage and bank count broaden the coverage within each group.

### `basic / zero-offset push constants`: bank selection through a pipeline layout

The host attempts to create one ordinary push constant range per active bank for either the compute or vertex stage. For bank `N`, it chains `VkPushConstantBankInfoNV{bank = N}` to `VkPushConstantsInfo`, supplies value `N`, and records `vkCmdPushConstants2`. The pipeline and descriptor set use the same layout, so the draw or dispatch uses the source's intended push constant and result-buffer interfaces ([range and upload helpers](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L140-L216), [ordinary paths](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L469-L593)).

The source range helper returns one `VkPushConstantRange` per active bank, with the same stage flags on every entry. The Vulkan pipeline-layout validity rule says that any two range entries must not include the same stage in `stageFlags`. `VkPushConstantRange` describes stage visibility and byte coverage, not a bank. Treat the repeated ranges as the source configuration under test, not as evidence that Vulkan provides one independently legal range per bank ([push constant range](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1841-L1891), [pipeline-layout validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1702-L1706), [range helper](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L174-L185)).

### `basic / member_offset push constants`: bank selection plus byte placement

The generated block adds `member_offset = 4` or `16`. Its declared `uint` retains member offset zero within the block, so `MemberOffsetNV` moves the block's bank address. The host expands each range to `memberOffset + sizeof(uint32_t)` and records the same nonzero command offset for every active bank ([shader branch](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1238-L1253), [member-offset paths](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1003-L1133)).

The upload helper passes `memberOffset + sizeof(uint32_t)` as the command's `size` and uses the same expression for the range size ([upload helper](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L188-L215)). This source behavior matters when investigating a member-offset-only failure because ordinary push constant validity requires the complete command byte interval to fit a matching layout range ([common push constant validity](../../../../vulkan-docs/src/chapters/commonvalidity/push_constants_common.adoc#L5-L26)).

### `descriptor_heap / push-data banks`: bank selection without a pipeline layout

The host encodes the result storage-buffer descriptor at byte offset zero in a resource heap. A `VkDescriptorSetAndBindingMappingEXT` maps shader set 0 binding 0 to that constant heap offset. The pipeline has `VK_PIPELINE_CREATE_2_DESCRIPTOR_HEAP_BIT_EXT` and no pipeline layout. After binding the heap, the host chains the selected bank to `VkPushDataInfoEXT` and records a 4-byte `vkCmdPushDataEXT` update at offset zero ([heap compute setup](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L598-L760), [heap graphics setup](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L782-L980)).

The resource heap includes one aligned descriptor-sized user range and a separately aligned reserved range of at least `minResourceHeapReservedRange`. The heap command is recorded before the draw or dispatch that consumes it, as required for subsequent shaders to use the bound address ([reserved ranges and heap state](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L663-L724), [`vkCmdBindResourceHeapEXT`](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L825-L860)).

## Shader Analysis

One walkthrough covers the generated shader's richest declaration branch. The descriptor-heap shader omits `member_offset`, but otherwise has the same eight bank-qualified blocks and result stores. Its distinct behavior comes from host-side push-data and heap commands, which the runtime section treats separately.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.push_constant_bank.basic.compute_member_offset_4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `basic` | Uses descriptor set 0 for the result buffer and `vkCmdPushConstants2` for bank data. |
| `compute` | Runs one local invocation and uses the compute ordinary-bank limit. |
| `member_offset_4` | Requests four active banks and adds four bytes to each shader block's bank address. |

#### Purpose

This shader exposes bank identity and member placement in one result array. Each load uses a different `BankNV` decoration, and every variable also carries `MemberOffsetNV 4`.

#### Structural Design

| Shader element | Role |
|----------------|------|
| `ResultData.bank[8]` | Receives one shader-observed word for every declared bank. |
| `PushConstantBank0` through `PushConstantBank7` | Declare eight independent bank-qualified `PushConstant` blocks. |
| `member_offset = 4` | Adds the nonzero placement dimension shared by the four active banks in this leaf. |
| `main` stores | Copy bank `N` to result slot `N`, making wrong bank routing visible to the host. |

#### Shader Code

```glsl
#version 460
#extension GL_NV_push_constant_bank : require

layout(local_size_x = 1) in;

/// Binding 0 is a write-only storage buffer. The shader stores one observed value per declared bank.
layout(std430, binding = 0) writeonly buffer ResultData {
    uint bank[8];
} resultData;

/// Each block selects a different push constant bank. member_offset = 4 adds four bytes to the member's bank address.
layout(push_constant, bank = 0, member_offset = 4) uniform PushConstantBank0 {
    uint data;
} bank0;

layout(push_constant, bank = 1, member_offset = 4) uniform PushConstantBank1 {
    uint data;
} bank1;

layout(push_constant, bank = 2, member_offset = 4) uniform PushConstantBank2 {
    uint data;
} bank2;

layout(push_constant, bank = 3, member_offset = 4) uniform PushConstantBank3 {
    uint data;
} bank3;

layout(push_constant, bank = 4, member_offset = 4) uniform PushConstantBank4 {
    uint data;
} bank4;

layout(push_constant, bank = 5, member_offset = 4) uniform PushConstantBank5 {
    uint data;
} bank5;

layout(push_constant, bank = 6, member_offset = 4) uniform PushConstantBank6 {
    uint data;
} bank6;

layout(push_constant, bank = 7, member_offset = 4) uniform PushConstantBank7 {
    uint data;
} bank7;

void main() {
    /// Copy every declared bank to a distinct result slot. The host checks only the active prefix for this case.
    resultData.bank[0] = bank0.data;
    resultData.bank[1] = bank1.data;
    resultData.bank[2] = bank2.data;
    resultData.bank[3] = bank3.data;
    resultData.bank[4] = bank4.data;
    resultData.bank[5] = bank5.data;
    resultData.bank[6] = bank6.data;
    resultData.bank[7] = bank7.data;
}
```

#### Additional Info

- `initPrograms` always emits all eight blocks and stores. The host checks only the active prefix, which is four banks for this leaf ([shader generator](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1218-L1299), [host validator](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L218-L238)).
- The default `SourceCollections` build options select the CTS baseline SPIR-V target, which is SPIR-V 1.0 ([baseline target](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `member_offset` | Zero-offset and descriptor-heap cases omit `member_offset`; the other offset leaf substitutes `16`. | [declaration generator](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1238-L1253) |
| Shader stage | Graphics omits the compute workgroup declaration and writes `gl_Position`; bank loads and result stores remain the same. | [stage generation](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1229-L1232), [graphics suffix](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1261-L1264) |
| Bank count | The generated shader stays at eight blocks. Runtime setup and host validation change the active prefix. | [fixed generator loop](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1238-L1259), [runtime clipping](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L469-L477) |
| Transport | The GLSL `PushConstant` interface remains bank-qualified. The host uses `vkCmdPushDataEXT` and a heap descriptor mapping in `descriptor_heap`. | [push-data bank semantics](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L990-L1066) |

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
; Bound: 74
; Schema: 0
               OpCapability Shader
               OpCapability PushConstantBanksNV
               OpExtension "SPV_NV_push_constant_bank"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 460
               OpSourceExtension "GL_NV_push_constant_bank"
               OpName %main "main"
               OpName %ResultData "ResultData"
               OpMemberName %ResultData 0 "bank"
               OpName %resultData "resultData"
               OpName %PushConstantBank0 "PushConstantBank0"
               OpMemberName %PushConstantBank0 0 "data"
               OpName %bank0 "bank0"
               OpName %PushConstantBank1 "PushConstantBank1"
               OpMemberName %PushConstantBank1 0 "data"
               OpName %bank1 "bank1"
               OpName %PushConstantBank2 "PushConstantBank2"
               OpMemberName %PushConstantBank2 0 "data"
               OpName %bank2 "bank2"
               OpName %PushConstantBank3 "PushConstantBank3"
               OpMemberName %PushConstantBank3 0 "data"
               OpName %bank3 "bank3"
               OpName %PushConstantBank4 "PushConstantBank4"
               OpMemberName %PushConstantBank4 0 "data"
               OpName %bank4 "bank4"
               OpName %PushConstantBank5 "PushConstantBank5"
               OpMemberName %PushConstantBank5 0 "data"
               OpName %bank5 "bank5"
               OpName %PushConstantBank6 "PushConstantBank6"
               OpMemberName %PushConstantBank6 0 "data"
               OpName %bank6 "bank6"
               OpName %PushConstantBank7 "PushConstantBank7"
               OpMemberName %PushConstantBank7 0 "data"
               OpName %bank7 "bank7"
               OpDecorate %_arr_uint_uint_8 ArrayStride 4
               OpDecorate %ResultData BufferBlock
               OpMemberDecorate %ResultData 0 NonReadable
               OpMemberDecorate %ResultData 0 Offset 0
               OpDecorate %resultData NonReadable
               OpDecorate %resultData Binding 0
               OpDecorate %resultData DescriptorSet 0
               OpDecorate %PushConstantBank0 Block
               OpDecorate %PushConstantBank0 BankNV 0
               OpMemberDecorate %PushConstantBank0 0 Offset 0
               OpDecorate %bank0 MemberOffsetNV 4
               OpDecorate %bank0 BankNV 0
               OpDecorate %PushConstantBank1 Block
               OpDecorate %PushConstantBank1 BankNV 1
               OpMemberDecorate %PushConstantBank1 0 Offset 0
               OpDecorate %bank1 MemberOffsetNV 4
               OpDecorate %bank1 BankNV 1
               OpDecorate %PushConstantBank2 Block
               OpDecorate %PushConstantBank2 BankNV 2
               OpMemberDecorate %PushConstantBank2 0 Offset 0
               OpDecorate %bank2 MemberOffsetNV 4
               OpDecorate %bank2 BankNV 2
               OpDecorate %PushConstantBank3 Block
               OpDecorate %PushConstantBank3 BankNV 3
               OpMemberDecorate %PushConstantBank3 0 Offset 0
               OpDecorate %bank3 MemberOffsetNV 4
               OpDecorate %bank3 BankNV 3
               OpDecorate %PushConstantBank4 Block
               OpDecorate %PushConstantBank4 BankNV 4
               OpMemberDecorate %PushConstantBank4 0 Offset 0
               OpDecorate %bank4 MemberOffsetNV 4
               OpDecorate %bank4 BankNV 4
               OpDecorate %PushConstantBank5 Block
               OpDecorate %PushConstantBank5 BankNV 5
               OpMemberDecorate %PushConstantBank5 0 Offset 0
               OpDecorate %bank5 MemberOffsetNV 4
               OpDecorate %bank5 BankNV 5
               OpDecorate %PushConstantBank6 Block
               OpDecorate %PushConstantBank6 BankNV 6
               OpMemberDecorate %PushConstantBank6 0 Offset 0
               OpDecorate %bank6 MemberOffsetNV 4
               OpDecorate %bank6 BankNV 6
               OpDecorate %PushConstantBank7 Block
               OpDecorate %PushConstantBank7 BankNV 7
               OpMemberDecorate %PushConstantBank7 0 Offset 0
               OpDecorate %bank7 MemberOffsetNV 4
               OpDecorate %bank7 BankNV 7
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %uint_8 = OpConstant %uint 8
%_arr_uint_uint_8 = OpTypeArray %uint %uint_8
 %ResultData = OpTypeStruct %_arr_uint_uint_8
%_ptr_Uniform_ResultData = OpTypePointer Uniform %ResultData
 %resultData = OpVariable %_ptr_Uniform_ResultData Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%PushConstantBank0 = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBank0 = OpTypePointer PushConstant %PushConstantBank0
      %bank0 = OpVariable %_ptr_PushConstant_PushConstantBank0 PushConstant
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
      %int_1 = OpConstant %int 1
%PushConstantBank1 = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBank1 = OpTypePointer PushConstant %PushConstantBank1
      %bank1 = OpVariable %_ptr_PushConstant_PushConstantBank1 PushConstant
      %int_2 = OpConstant %int 2
%PushConstantBank2 = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBank2 = OpTypePointer PushConstant %PushConstantBank2
      %bank2 = OpVariable %_ptr_PushConstant_PushConstantBank2 PushConstant
      %int_3 = OpConstant %int 3
%PushConstantBank3 = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBank3 = OpTypePointer PushConstant %PushConstantBank3
      %bank3 = OpVariable %_ptr_PushConstant_PushConstantBank3 PushConstant
      %int_4 = OpConstant %int 4
%PushConstantBank4 = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBank4 = OpTypePointer PushConstant %PushConstantBank4
      %bank4 = OpVariable %_ptr_PushConstant_PushConstantBank4 PushConstant
      %int_5 = OpConstant %int 5
%PushConstantBank5 = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBank5 = OpTypePointer PushConstant %PushConstantBank5
      %bank5 = OpVariable %_ptr_PushConstant_PushConstantBank5 PushConstant
      %int_6 = OpConstant %int 6
%PushConstantBank6 = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBank6 = OpTypePointer PushConstant %PushConstantBank6
      %bank6 = OpVariable %_ptr_PushConstant_PushConstantBank6 PushConstant
      %int_7 = OpConstant %int 7
%PushConstantBank7 = OpTypeStruct %uint
%_ptr_PushConstant_PushConstantBank7 = OpTypePointer PushConstant %PushConstantBank7
      %bank7 = OpVariable %_ptr_PushConstant_PushConstantBank7 PushConstant
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpAccessChain %_ptr_PushConstant_uint %bank0 %int_0
         %19 = OpLoad %uint %18
         %21 = OpAccessChain %_ptr_Uniform_uint %resultData %int_0 %int_0
               OpStore %21 %19
         %26 = OpAccessChain %_ptr_PushConstant_uint %bank1 %int_0
         %27 = OpLoad %uint %26
         %28 = OpAccessChain %_ptr_Uniform_uint %resultData %int_0 %int_1
               OpStore %28 %27
         %33 = OpAccessChain %_ptr_PushConstant_uint %bank2 %int_0
         %34 = OpLoad %uint %33
         %35 = OpAccessChain %_ptr_Uniform_uint %resultData %int_0 %int_2
               OpStore %35 %34
         %40 = OpAccessChain %_ptr_PushConstant_uint %bank3 %int_0
         %41 = OpLoad %uint %40
         %42 = OpAccessChain %_ptr_Uniform_uint %resultData %int_0 %int_3
               OpStore %42 %41
         %47 = OpAccessChain %_ptr_PushConstant_uint %bank4 %int_0
         %48 = OpLoad %uint %47
         %49 = OpAccessChain %_ptr_Uniform_uint %resultData %int_0 %int_4
               OpStore %49 %48
         %54 = OpAccessChain %_ptr_PushConstant_uint %bank5 %int_0
         %55 = OpLoad %uint %54
         %56 = OpAccessChain %_ptr_Uniform_uint %resultData %int_0 %int_5
               OpStore %56 %55
         %61 = OpAccessChain %_ptr_PushConstant_uint %bank6 %int_0
         %62 = OpLoad %uint %61
         %63 = OpAccessChain %_ptr_Uniform_uint %resultData %int_0 %int_6
               OpStore %63 %62
         %68 = OpAccessChain %_ptr_PushConstant_uint %bank7 %int_0
         %69 = OpLoad %uint %68
         %70 = OpAccessChain %_ptr_Uniform_uint %resultData %int_0 %int_7
               OpStore %70 %69
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Ordinary push-constant path

- The host creates a host-visible 32-byte storage buffer, fills all eight words with `~0u`, flushes it, and writes it to descriptor set 0 binding 0 ([ordinary resources](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L118-L171)).
- It builds the stage-specific push constant ranges and pipeline layout, then creates either a compute pipeline or a vertex-only graphics pipeline with rasterizer discard. Graphics begins dynamic rendering with no attachments ([ordinary compute](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L469-L509), [ordinary graphics](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L537-L563)).
- Command order is pipeline bind, descriptor-set bind, one banked push update per active bank, then one dispatch or one-point draw. The shader writes result word `N` from bank `N`.
- A shader-write-to-host-read barrier follows execution. The host submits, waits, invalidates the allocation, and checks the active prefix ([ordinary command order](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L511-L531), [graphics command order](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L565-L592)).

### Descriptor-heap push-data path

- The host calculates an aligned one-descriptor user range, aligns the reserved-range offset to `resourceHeapAlignment`, and appends `minResourceHeapReservedRange`. Both heap and result buffers use host-visible, device-addressable memory ([heap sizing and buffers](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L611-L672)).
- It writes a storage-buffer descriptor for the result address into heap offset zero, flushes the heap, and attaches a constant-offset descriptor mapping to the shader stage. The descriptor-heap pipeline needs no pipeline layout ([descriptor encoding and mapping](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L674-L716)).
- Before execution, synchronization2 barriers make host writes to the heap visible as resource-heap reads and make the result sentinel visible before shader writes. Command order is pipeline bind, resource-heap bind, one banked push-data update per active bank, then dispatch. Graphics performs the same state sequence inside dynamic rendering before a one-point draw ([compute command order](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L718-L776), [graphics command order](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L932-L997)).
- No non-heap descriptor or ordinary push-constant command follows the heap state. Such a command would invalidate descriptor-heap state ([heap-state invalidation](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L675-L710)).

### Shared host validation

`verifyResults` invalidates the result allocation and compares each active word with its bank index. The original `~0u` sentinel distinguishes an unwritten word from every expected index 0 through 7. A mismatch logs the bank, optional member offset, expected value, and observed value, then fails with `Result mismatch` ([host validator](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L218-L238)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic / zero-offset push constants` | Bank selection, ordinary push-constant upload, stage visibility, or pipeline-layout compatibility is wrong. |
| `basic / member_offset push constants` | Bank selection or the combined API offset and shader `member_offset` address calculation is wrong. |
| `descriptor_heap / push-data banks` | Push-data bank selection, descriptor-heap pipeline mapping, heap binding/descriptor encoding, or heap memory visibility is wrong. |

A mismatch shared by all three groups can also come from generated shader lowering, result-buffer writes, shader-to-host synchronization, or host cache invalidation rather than the selected bank transport.

### Cause Analysis

#### Ordinary zero-offset bank state

**Possible failure symptoms:** An active result slot remains `~0u`, contains another bank's index, or differs only between compute and graphics leaves. Failures may begin when the requested bank count exceeds one.

**Possible implementation causes:** The implementation may reject or mishandle the source's repeated same-stage range entries before push data reaches the shader, route `VkPushConstantBankInfoNV::bank` to the wrong hardware bank, apply an update to the wrong stage, mishandle the layout used by `vkCmdPushConstants2`, or lower `BankNV` incorrectly. The bank field selects the destination bank, and the command's stage and byte interval must agree with the pipeline layout ([bank chaining](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1035-L1096), [push constant interface](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1045-L1095), [pipeline-layout validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1702-L1706)). The first failing bank and stage narrow the source-level investigation.

#### Member-offset address calculation

**Possible failure symptoms:** Zero-offset leaves pass while `compute_member_offset_4`, `compute_member_offset_16`, or their graphics counterparts return a wrong value or leave the corresponding active slot unchanged.

**Possible implementation causes:** The shader compiler or implementation may ignore `MemberOffsetNV`, add it more than once, combine it with `BankNV` incorrectly, or read the wrong bytes from the bank. Investigation must also compare the recorded command interval against the created range because the upload helper uses `memberOffset + sizeof(uint32_t)` for both range size and command size while starting the command at `memberOffset` ([upload helper](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L188-L215), [push constant range validity](../../../../vulkan-docs/src/chapters/commonvalidity/push_constants_common.adoc#L5-L26)).

#### Descriptor-heap push-data and mapping state

**Possible failure symptoms:** Ordinary leaves pass while heap leaves return `~0u`, another bank's value, or a stage-specific mismatch. A complete sentinel array points toward a missing result write or inaccessible mapped descriptor.

**Possible implementation causes:** The implementation may route the wrong push-data bank, fail to expose `vkCmdPushDataEXT` through `PushConstant` storage, decode the heap descriptor incorrectly, apply the set/binding mapping to the wrong offset, or lose the bound heap state before execution. A visibility defect can also hide the host-written descriptor from the shader. The specification separates push-data bank limits from ordinary bank limits and makes heap bindings available only to later shader commands ([push-data banks](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L1035-L1107), [resource-heap binding](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L825-L860)).

#### Shared shader output or host readback path

**Possible failure symptoms:** All three behavior groups fail with the same slot pattern, including single-bank cases, or the observed words remain at the common sentinel.

**Possible implementation causes:** The generated shader may be compiled incorrectly, the storage-buffer descriptor may resolve to the wrong address, shader writes may not become visible to host reads, or the host allocation may not be invalidated correctly. The ordinary and heap paths use different descriptor transports but share the generated stores and final validator, so the cross-path pattern matters. Source-level investigation should start with the SPIR-V interface, result address, barriers, and invalidation rather than assuming a bank-routing defect.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `VK_KHR_maintenance5`, `VK_NV_push_constant_bank`, and the `pushConstantBank` feature. A zero matching bank limit produces `NotSupportedError` ([support checks](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1144-L1190), [feature definition](../../../../vulkan-docs/src/chapters/features.adoc#L9518-L9538)).
- Heap leaves also require `VK_EXT_descriptor_heap`, `VK_KHR_buffer_device_address`, `VK_KHR_shader_untyped_pointers`, and `VK_KHR_synchronization2`. The custom device enables descriptor heaps, buffer device address, and synchronization2 for those paths ([heap support](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1192-L1198), [device creation](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L384-L423)).
- Graphics leaves require `vertexPipelineStoresAndAtomics` for vertex-stage storage-buffer writes ([graphics support](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1200-L1204)).
- A requested count is clipped to the matching device limit and eight. The leaf still executes when at least one bank exists, but validation covers only that supported prefix.
- The enclosing `binding_model` registration excludes this test family from Vulkan SC builds ([registration guard](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L61-L71)).

### Design-based pruning

- The test fixes the generated interface and result array at eight banks. It samples requested counts rather than generating every count from 1 through 8.
- `basic` includes count 2 to probe the first multi-bank boundary. `descriptor_heap` keeps only 1, 4, and 8 because its distinct behavior is the transport and mapping path.
- Member-offset coverage uses four requested banks and two aligned nonzero offsets, 4 and 16. It does not cross-product offsets with all bank counts.
- Only compute and vertex stages appear. The graphics path uses a vertex-only pipeline with rasterizer discard so a framebuffer does not obscure push-constant and storage-write behavior.

## Key Takeaways

- `basic` and `descriptor_heap` exercise separate Vulkan command paths and separate device limits even though their generated shaders use the same bank-qualified `PushConstant` storage.
- Bank `N` carries value `N`, and result slot `N` makes bank swaps, missing updates, and stale state easy to locate.
- `member_offset` changes shader placement as well as host upload. Its source-level command interval deserves explicit inspection when only those leaves fail.
- Descriptor-heap leaves validate more than push data: they also depend on host-written descriptor encoding, constant-offset mapping, reserved-range sizing, heap binding, and host-to-shader visibility.
- Requested bank counts do not guarantee equal runtime coverage. The implementation checks only the prefix supported by the path-specific bank limit, capped at eight.
- See `## Failure Meaning` to distinguish bank transport failures from the shared result-write and readback path.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameter classification | [`TestType`, `TestParams`, and helpers](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L56-L95) | Defines stage, transport, requested count, and member offset. |
| Ordinary resources, upload, and validation | [shared helpers](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L118-L260) | Creates the result path, ranges, banked command payloads, and host comparison. |
| Ordinary runtime | [`runComputeTest` and `runGraphicsTest`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L469-L593) | Records pipeline, descriptor, push, execution, barrier, and readback order. |
| Descriptor-heap runtime | [`runComputeDescriptorHeapTest` and `runGraphicsDescriptorHeapTest`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L598-L998) | Implements heap sizing, descriptor encoding, mappings, push data, and synchronization directly in this file. |
| Member-offset runtime | [member-offset paths](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1003-L1133) | Connects shader placement with pipeline-layout ranges and command uploads. |
| Support and custom device setup | [support checks](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1144-L1205), [device creation](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L336-L443) | Defines features, extensions, queue stage, and limit gates. |
| Generated programs | [`initPrograms`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1218-L1299) | Emits the exact GLSL declarations and result stores. |
| Registration and mustpass | [population](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1301-L1399), [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L60502-L60519) | Confirms two intermediate nodes and 18 default Vulkan leaves. |
| Push constant specification | [pipeline layouts and commands](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1171-L1250), [updates and compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L5160-L5295) | Defines ordinary ranges, updates, state, and compatible consumption. |
| Shader interface specification | [push constant interface](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1045-L1095), [bank decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2971-L2993) | Defines `PushConstant`, `BankNV`, and `MemberOffsetNV`. |
| Descriptor heap specification | [heap state](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L663-L724), [push data and banks](../../../../vulkan-docs/src/chapters/descriptorheaps.adoc#L965-L1110) | Defines heap command state, push data, bank chaining, and bank bounds. |
| Limits and synchronization | [bank limits](../../../../vulkan-docs/src/chapters/limits.adoc#L5384-L5424), [memory dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#L110-L180) | Defines the four path-specific counts and visibility model. |
