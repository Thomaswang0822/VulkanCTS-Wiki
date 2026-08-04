## Overview

**Core question:** does an implementation that advertises `VK_KHR_shader_untyped_pointers` correctly declare, access, load, store, copy, atomically update, type-pun, and pass through pointers whose pointee type is not encoded in the pointer itself?

The `untyped_pointers` test family in [`vktSpvAsmUntypedPointersTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp) registers SPIR-V assembly compute cases for `SPV_KHR_untyped_pointers` / `VK_KHR_shader_untyped_pointers`. Its `vulkan_memory_model` and `glsl_memory_model` roots select `OpMemoryModel Logical Vulkan` (SPIR-V 1.3) and `OpMemoryModel Logical GLSL450` (SPIR-V 1.0) for their common families; physical-storage cases replace that logical model with the corresponding `PhysicalStorageBuffer64` model, and `cooperative_matrix` exists only in the Vulkan root ([registration root](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12702-L12711)).

- The family centrally exercises `OpTypeUntypedPointerKHR`, `OpUntypedVariableKHR`, `OpUntypedAccessChainKHR`, and `OpUntypedArrayLengthKHR`; `SPV_KHR_untyped_pointers` also defines related untyped access-chain instructions.
- Seven interaction subgroups cover the basic load/store/copy/atomic/array-length/descriptor-array surface plus type punning, variable pointers, physical storage buffers, workgroup explicit layout, cooperative matrices, and block arrays.
- Every case is hand-authored SPIR-V assembly built from C++ `tcu::StringTemplate`s; there is no GLSL or HLSL source.

## Background Knowledge

- **`SPV_KHR_untyped_pointers` and its access instructions.** `OpTypeUntypedPointerKHR <StorageClass>` declares a pointer type that carries only a storage class, not a pointee type. `OpUntypedAccessChainKHR` supplies the type used to interpret addressing; `OpLoad` supplies its result type and `OpStore` supplies the stored object's type. `OpUntypedVariableKHR` declares a variable whose type is an untyped pointer, and `OpUntypedArrayLengthKHR` queries a runtime array length through such a pointer. The extension limits untyped pointers to storage classes with explicit layout, so interpretations have a consistent layout.
- **Memory model split.** This family creates `Logical Vulkan` cases with `VulkanMemoryModel`, `SPV_KHR_vulkan_memory_model`, and SPIR-V 1.3, and `Logical GLSL450` cases at SPIR-V 1.0. These are the two logical-model branches selected by its helper, not a claim that they are the only logical memory models generally; physical-storage cases deliberately replace either with `PhysicalStorageBuffer64 <Vulkan|GLSL450>`.
- **Type punning through untyped pointers.** Because an untyped pointer carries no pointee type, the same pointer can be loaded as one type and stored as a different type as long as the two types share the same byte size. This is the property most unique to untyped pointers; typed `OpTypePointer` makes punning illegal at the SPIR-V type level. The `type_punning` and `memory_interpretation` subgroups exercise this directly.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.untyped_pointers
├── vulkan_memory_model
└── glsl_memory_model
```

Both subtrees are implemented in the same source file. The `vulkan_memory_model` subtree registers `basic_usecase`, `type_punning`, `variable_pointers`, `physical_storage`, `workgroup_memory_explicit_layout`, `cooperative_matrix`, and `block_array`. The `glsl_memory_model` subtree registers the same set except `cooperative_matrix` ([Vulkan registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12679-L12689), [GLSL registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12691-L12700)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Memory model | `VULKAN`, `GLSL` | Top-level split. Selects `OpMemoryModel Logical Vulkan` (SPIR-V 1.3) or `Logical GLSL450` (SPIR-V 1.0). The `cooperative_matrix` subgroup is registered only under `VULKAN`. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L133-L139), [adjuster](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1406-L1437) |
| Subgroup | `basic_usecase`, `type_punning`, `variable_pointers`, `physical_storage`, `workgroup_memory_explicit_layout`, `cooperative_matrix`, `block_array` | Primary behavioral axis. Each subgroup targets a distinct untyped-pointer property or interaction. | [Vulkan groups](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12679-L12689) |
| Data type | `uint8`, `int8`, `uint16`, `int16`, `float16`, `uint32`, `int32`, `float32`, `uint64`, `int64`, `float64` | Scalar pointee type used by load/store/atomic/pun cases. Drives `OpCapability Int8/Int16/Int64/Float16/Float64` and the matching Vulkan feature bits. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L59-L74), [cases](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L304-L315) |
| Composite data type | `vec2/vec3/vec4` of each scalar | Vector pointee forms used by type-punning and copy paths. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L76-L113) |
| Container type | `STORAGE_BUFFER`, `UNIFORM`, `PUSH_CONSTANT`, `WORKGROUP` | Storage class the untyped pointer lives in. `UNIFORM` widens array stride to 16; `PUSH_CONSTANT` shrinks workgroup count to 4; `WORKGROUP` is exercised through the explicit-layout subtree. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L123-L131), [load containers](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L336-L340) |
| Operation type | `NORMAL`, `ATOMIC` | Whether the load/store uses `OpLoad`/`OpStore` or `OpAtomicLoad`/`OpAtomicStore`. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L115-L121) |
| Copy operation | `COPY_OBJECT`, `COPY_MEMORY`, `COPY_MEMORY_SIZED` | `OpCopyObject` of the loaded value, `OpCopyMemory` between untyped and typed pointers, or `OpCopyMemorySized` by byte count. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L141-L148) |
| Base test case | `LOAD`, `STORE`, `COPY_FROM`, `COPY_TO`, `ARRAY_LENGTH`, `DESCRIPTOR_ARRAY` | Core operations under `basic_usecase`. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L150-L160) |
| Atomic test case | `OP_ATOMIC_LOAD`…`OP_ATOMIC_XOR`, plus compare-exchange/exchange/increment/decrement/add/sub/min/max/and/or/xor | Atomic operation routed through an untyped pointer. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L182-L199) |
| Pointer test case | bitcast, select, phi, ptr_access_chain, function_call, ptr_equal, ptr_not_equal, ptr_diff, function_variable, private_variable, multiple_access_chains, workgroup_memory | Pointer-value operations on untyped pointers, split across `variable_pointers` and `physical_storage`. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L201-L222) |
| Memory interpretation | large stride, non-zero offset, mixed offsets, multiple access chains, `SHORT2_NO_STORAGE_CAP`, `CHAR4_NO_STORAGE_CAP`, `CHAR2_16BIT_STORAGE_CAP`, untyped-from-typed | Reinterpretation shapes and 8/16-bit storage capability probes. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L224-L237) |
| Block array test case | basic, reinterpret×4 (normal/untyped × access_chain/ptr_access_chain), select×4 | Array-of-block operations with normal vs untyped access chains. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L239-L252) |
| Workgroup test case | `ALIASED`, `NOT_ALIASED` | Workgroup explicit-layout aliasing with untyped workgroup pointers. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L254-L260) |
| Cooperative matrix | `BASIC_LOAD`, `BASIC_STORE`, `TYPE_PUNNING_LOAD`, `TYPE_PUNNING_STORE`, `MIXED_LOAD`, `MIXED_STORE` | Cooperative matrix load/store through untyped pointers. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L262-L272) |
| Matrix layout and role | `ROW_MAJOR`, `COL_MAJOR`; `A`, `B`, `ACCUMULATOR` | Cooperative matrix layout and operand role. | [enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L274-L289) |

## Behavior Parameters

The primary behavioral axis is the **subgroup**, the intermediate node below `<memory_model>`. Each subgroup targets a distinct untyped-pointer property or interaction. The memory model (`VULKAN` vs `GLSL`) is a secondary axis that changes `OpMemoryModel` and the SPIR-V target version but reuses the same pointer operations, except that `cooperative_matrix` is registered only under `VULKAN`.

### `basic_usecase` — core untyped pointer operations

The entry surface for untyped pointers: `load`, `store`, `copy` (`COPY_OBJECT` / `COPY_MEMORY` / `COPY_MEMORY_SIZED`), `array_length` (`OpUntypedArrayLengthKHR`), `atomics` (`OpAtomicLoad`/`OpAtomicStore`/`OpAtomic*`), and `descriptor_array` (untyped variable as an array of blocks). The ordinary load/store/copy forms route values between untyped and typed resource accesses; the other forms use their operation-specific resources and expected values. The container-type dimension (`STORAGE_BUFFER`, `UNIFORM`, `PUSH_CONSTANT`) varies the storage class the untyped pointer lives in.

### `type_punning` — same-byte-size reinterpretation

Exercises loading one type from an untyped pointer whose backing memory was written as a different same-byte-size type. The shape axis splits into `*_SAME_SIZE_TYPES` (e.g. `uint32` ↔ `float32`), `*_SCALAR_VECTOR`, and `*_VECTOR_SCALAR`. The `reinterpret` subtree further splits into `struct_as_type`, `multiple_access_chains`, and `memory_interpretation` (read/write) with offset and stride variations.

### `variable_pointers` — untyped pointer value flow

Verifies that an untyped pointer value can flow through `OpSelect`, `OpPhi`, `OpFunctionCall`, `OpPtrAccessChain`, `OpPtrEqual`, `OpPtrNotEqual`, and `OpPtrDiff`, and that `function_variable`, `private_variable`, and `workgroup_memory` forms compile and run correctly. Adds `VK_KHR_variable_pointers` plus `OpCapability VariablePointersStorageBuffer` / `VariablePointers`.

### `physical_storage` — untyped physical storage buffer pointers

Verifies `OpBitcast` between an untyped `PhysicalStorageBuffer` pointer and a 64-bit integer address, plus select/phi/access-chain/function-call on physical untyped pointers. `adjustSpecForPhysicalStorageBuffer` overrides `OpMemoryModel` to `PhysicalStorageBuffer64 <Vulkan|GLSL450>` and adds `VK_KHR_buffer_device_address` + `OpCapability PhysicalStorageBufferAddresses`.

### `workgroup_memory_explicit_layout` — workgroup untyped pointers with explicit layout

Exercises untyped pointers in the `Workgroup` storage class under `VK_KHR_workgroup_memory_explicit_layout`, with `ALIASED` and `NOT_ALIASED` variants. 8/16-bit element types add `WorkgroupMemoryExplicitLayout8BitAccessKHR` / `WorkgroupMemoryExplicitLayout16BitAccessKHR`.

### `cooperative_matrix` — cooperative matrix load/store through untyped pointers

Vulkan-memory-model-only. Exercises `OpCooperativeMatrixLoadKHR` / `OpCooperativeMatrixStoreKHR` with an untyped memory pointer in `basic_usecase`, `type_punning`, and `mixed` subgroups. It requires both `VK_KHR_shader_untyped_pointers` and `VK_KHR_cooperative_matrix`, checks both feature bits, and accepts a leaf only when the queried cooperative-matrix properties contain the selected component type in the selected A, B, or C role. It overrides the SPIR-V target to 1.6 regardless of the memory-model default.

### `block_array` — array-of-blocks with untyped pointers

Exercises untyped pointers indexing into arrays of blocks, with `basic`, `reinterpret` (normal vs untyped × access_chain vs ptr_access_chain), and `select` variants. Always adds `SPV_EXT_descriptor_indexing` + `StorageBufferArrayDynamicIndexing`; the `*_PTR_ACCESS_CHAIN` and `SELECT_*` variants additionally pull in `SPV_KHR_variable_pointers`.

## Shader Analysis

This page uses one representative walkthrough. The selected case is the smallest one that exercises the untyped-pointer instruction trio (`OpTypeUntypedPointerKHR`, `OpUntypedVariableKHR`, `OpUntypedAccessChainKHR`) under the Vulkan memory model at SPIR-V 1.3. Other subgroups reuse the same template structure with different `createShaderMain`/`createShaderVariables` branches; their differences are summarized in `#### Parameter Variation Summary`.

### Representative Shader Walkthrough 1

- **Representative path:** `spirv_assembly.instruction.compute.untyped_pointers.vulkan_memory_model.basic_usecase.load.storage.uint32`
- **Source file:** [`vktSpvAsmUntypedPointersTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp)
- **Builder function:** [`addLoadTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L6967-L7083), which specializes the four `tcu::StringTemplate`s from `createShaderHeader()`, `createShaderAnnotations(BaseTestCases::LOAD)`, `createShaderVariables(BaseTestCases::LOAD)`, and `createShaderMain(BaseTestCases::LOAD)`.

#### Purpose

Verify that an `OpLoad %uint32` through an `OpUntypedAccessChainKHR` result into an `OpUntypedVariableKHR`-declared storage buffer variable produces the same bytes the host wrote, and that the result round-trips into a typed `OpTypePointer StorageBuffer %uint32` output. The expected output buffer equals the random input buffer, so any mismatch isolates the untyped-pointer load path.

#### Parameter Values Chosen

| Parameter | Value | Source |
|-----------|-------|--------|
| Memory model | `VULKAN` → `OpMemoryModel Logical Vulkan`, SPIR-V 1.3 | [adjustSpecForMemoryModel](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1412-L1422) |
| Subgroup | `basic_usecase` → `load` | [addBasicUsecaseTestGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12604-L12612) |
| Container type | `STORAGE_BUFFER` → `StorageBuffer` storage class | [getStorageClass](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L936-L946) |
| Data type | `UINT32` → `OpTypeInt 32 0` | [getDeclaration](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L876-L893) |
| Operation | `NORMAL` → `OpLoad` with no extra args | [LOAD_OPERATION_CASES](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L342-L345) |
| Workgroup count | 64 (`Constants::numThreads`) | [addLoadTests](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L6989-L6991) |
| Array stride | 4 (`getSizeInBytes(UINT32)`) | [getResourceDecorations](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1176-L1202) |

#### Structural Design

The shader is a single `GLCompute` entry point with a `1 1 1` local size, dispatched across 64 work groups so each invocation handles one array element. The flow has three phases: resolve the invocation index, form the untyped input pointer and typed output pointer at that index, then load-and-store between them.

```mermaid
flowchart TD
    A["Entry: %main, LocalSize 1 1 1"] --> B["OpAccessChain %id → %id_loc"]
    B --> C["OpLoad %uint32 %id_loc → %x (invocation index)"]
    C --> D["OpUntypedAccessChainKHR → %input_data_var_loc<br/>(untyped ptr into input buffer at index x)"]
    C --> E["OpAccessChain → %output_data_var_loc<br/>(typed ptr into output buffer at index x)"]
    D --> F["OpLoad %uint32 %input_data_var_loc → %temp_data_var_loc<br/>(result type drives the load, not the pointer)"]
    F --> G["OpStore %output_data_var_loc %temp_data_var_loc"]
    G --> H["OpReturn"]
```

#### Resource and Interface Facts

| Resource | Declaration | Role |
|----------|-------------|------|
| `%input_data_untyped_var` | `OpUntypedVariableKHR %storage_buffer_untyped_ptr StorageBuffer %input_buffer` | Input SSBO at descriptor set 0 binding 0. Backed by a host-filled random buffer; the untyped pointer is the tested access path. |
| `%output_data_var` | `OpVariable %output_buffer_storage_buffer_ptr StorageBuffer` | Output SSBO at descriptor set 0 binding 1. Read back by the host and compared against the expected (== input) buffer. |
| `%id` | `OpVariable %vec3_uint32_input_ptr Input` | `GlobalInvocationId`; provides the per-invocation index `x`. |
| `%storage_buffer_untyped_ptr` | `OpTypeUntypedPointerKHR StorageBuffer` | The untyped pointer type itself; no pointee type encoded. |
| `%storage_buffer_uint32_ptr` | `OpTypePointer StorageBuffer %uint32` | Typed pointer used for the output side, so the round trip exercises both untyped and typed access in one shader. |

#### Source Code

The SPIR-V assembly below is extracted from the C++ `tcu::StringTemplate` concatenation in [`addLoadTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L6967-L7083) (header from `createShaderHeader`, annotations from `createShaderAnnotations(BaseTestCases::LOAD)`, variables from `createShaderVariables(BaseTestCases::LOAD)`, main from `createShaderMain(BaseTestCases::LOAD)`). Wiki-authored section markers use `;` comment syntax. The assembly targets SPIR-V 1.3 (set by `adjustSpecForMemoryModel` for the `VULKAN` path). It was round-trip-validated with `spirv-as` → `spirv-val` → `spirv-dis` against `spv1.3`; the disassembler output is not published (category-scoped `TEMP-SPIRV-ASSEMBLY` deviation).

```llvm
; SPIR-V
; Version: 1.3
; Generator: Vulkan CTS vktSpvAsmUntypedPointersTests; 0
; Bound: 25
; Schema: 0
; --- header: createShaderHeader + adjustSpecForUntypedPointers + adjustSpecForMemoryModel(VULKAN) ---
OpCapability Shader
OpCapability UntypedPointersKHR
OpCapability VulkanMemoryModel
OpCapability VulkanMemoryModelDeviceScopeKHR
OpExtension "SPV_KHR_storage_buffer_storage_class"
OpExtension "SPV_KHR_untyped_pointers"
OpExtension "SPV_KHR_vulkan_memory_model"
OpMemoryModel Logical Vulkan
OpEntryPoint GLCompute %main "main" %id
OpExecutionMode %main LocalSize 1 1 1
; --- annotations: createShaderAnnotations(LOAD) + getResourceDecorations(STORAGE_BUFFER, UINT32, 64) ---
OpDecorate %id BuiltIn GlobalInvocationId
OpMemberDecorate %input_buffer 0 Offset 0
OpDecorate %input_buffer Block
OpMemberDecorate %output_buffer 0 Offset 0
OpDecorate %output_buffer Block
OpDecorate %array_uint32_64 ArrayStride 4
OpDecorate %input_data_untyped_var DescriptorSet 0
OpDecorate %input_data_untyped_var Binding 0
OpDecorate %output_data_var DescriptorSet 0
OpDecorate %output_data_var Binding 1
; --- types, constants, variables: createShaderVariables(LOAD) ---
%void = OpTypeVoid
%uint32 = OpTypeInt 32 0
%vec3_uint32 = OpTypeVector %uint32 3
%void_func = OpTypeFunction %void
%c_uint32_0 = OpConstant %uint32 0
%c_uint32_64 = OpConstant %uint32 64
%array_uint32_64 = OpTypeArray %uint32 %c_uint32_64
%input_buffer = OpTypeStruct %array_uint32_64
%output_buffer = OpTypeStruct %array_uint32_64
%uint32_input_ptr = OpTypePointer Input %uint32
%vec3_uint32_input_ptr = OpTypePointer Input %vec3_uint32
%storage_buffer_uint32_ptr = OpTypePointer StorageBuffer %uint32
%storage_buffer_untyped_ptr = OpTypeUntypedPointerKHR StorageBuffer
%output_buffer_storage_buffer_ptr = OpTypePointer StorageBuffer %output_buffer
%id = OpVariable %vec3_uint32_input_ptr Input
%input_data_untyped_var = OpUntypedVariableKHR %storage_buffer_untyped_ptr StorageBuffer %input_buffer
%output_data_var = OpVariable %output_buffer_storage_buffer_ptr StorageBuffer
; --- entry point: createShaderMain(LOAD) ---
%main = OpFunction %void None %void_func
%label_main = OpLabel
%id_loc = OpAccessChain %uint32_input_ptr %id %c_uint32_0
%x = OpLoad %uint32 %id_loc
%input_data_var_loc = OpUntypedAccessChainKHR %storage_buffer_untyped_ptr %input_buffer %input_data_untyped_var %c_uint32_0 %x
%output_data_var_loc = OpAccessChain %storage_buffer_uint32_ptr %output_data_var %c_uint32_0 %x
%temp_data_var_loc = OpLoad %uint32 %input_data_var_loc
OpStore %output_data_var_loc %temp_data_var_loc
OpReturn
OpFunctionEnd
```

#### Parameter Variation Summary

- **Container type** varies the `${storageClass}` placeholder and the resource decorations. `UNIFORM` widens `ArrayStride` to 16 and binds the input as `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER`; `PUSH_CONSTANT` shrinks the workgroup count to 4 and moves the input into the push-constant range. The shader body is otherwise identical.
- **Operation type** swaps `${loadOp}` between `OpLoad` and `OpAtomicLoad` (with `${args}` = `%c_uint32_1 %c_uint32_0`); the atomic path is registered under `basic_usecase.atomics` rather than `basic_usecase.load`.
- **Data type** swaps `${baseType}`/`${baseDecl}` and adds the matching `OpCapability Int8/Int16/Int64/Float16/Float64` plus `OpExtension "SPV_KHR_8bit_storage"`/`"SPV_KHR_16bit_storage"` and the corresponding storage capability (`StorageBuffer8BitAccess` etc.) for 8/16-bit types in storage/uniform/push-constant containers.
- **Memory model** swaps `OpMemoryModel` between `Logical Vulkan` (SPIR-V 1.3, with `VulkanMemoryModel` capability) and `Logical GLSL450` (SPIR-V 1.0); the rest of the shader is unchanged.
- **`STORE`/`COPY_FROM`/`COPY_TO`** mirror `LOAD`: the untyped pointer moves to the output side for `STORE`/`COPY_TO`, and `${copyOp}` inserts `OpCopyObject`/`OpCopyMemory`/`OpCopyMemorySized` for the copy cases.
- **`ARRAY_LENGTH`** replaces the load/store body with `OpUntypedArrayLengthKHR %uint32 %input_buffer %input_data_untyped_var 0` stored into a `uint32` output, querying the runtime array length through the untyped pointer.
- **`DESCRIPTOR_ARRAY`** wraps the input in an array-of-blocks and indexes it dynamically, exercising an untyped variable over a block array.

#### Additional Info

- The `physical_storage` subtree overrides `OpMemoryModel` to `PhysicalStorageBuffer64 <Vulkan|GLSL450>` and uses `OpTypeUntypedPointerKHR PhysicalStorageBuffer` plus `OpBitcast` between the untyped physical pointer and a 64-bit address. That override happens in `adjustSpecForPhysicalStorageBuffer`, not in the `LOAD` template shown here.
- The `cooperative_matrix` subtree overrides the SPIR-V target to 1.6 in `CooperativeMatrixInteractionTestCase::initPrograms` and uses `OpCooperativeMatrixLoadKHR`/`OpCooperativeMatrixStoreKHR` with the untyped pointer as the memory operand. It is registered only under `vulkan_memory_model`.

## Runtime Execution and Result Checking

- The ordinary generated families select their memory model, data type, container, and operation, then call their applicable `adjustSpecFor*` helpers to assemble `OpCapability`/`OpExtension`/feature requirements and `${memModelOp}`. They specialize the header, annotations, variables, and main `tcu::StringTemplate`s into SPIR-V assembly registered as `comp`.
- In the representative `basic_usecase.load` family, the input uses `FillingTypes::RANDOM` seeded by `deStringHash(testGroup->getName())`; `PUSH_CONSTANT` binds it as push constants, while the other variants bind descriptor set 0 binding 0 as storage or uniform. Its expected output is that input, and its dispatch is four work groups for push constants or 64 otherwise, with local size `1 1 1`.
- Other ordinary cases provide operation-specific resources and expected results; atomic cases, for example, construct expected resources from their operation descriptors (initial value, operands, and compare/exchange value).
- The ordinary generated cases use `SpvAsmComputeShaderCase`, which copies back the output SSBO and compares it byte-for-byte against the expected resource. The comparison is exact; there is no per-case tolerance.
- Cooperative-matrix leaves instead use `CooperativeMatrixInteractionTestCase`. Its custom instance allocates buffers sized for the queried matrix, but initializes and compares only `expectedBytes.size()` bytes, where `expectedBytes` is built from one scalar `m_params.dataType` resource. Thus its exact oracle observes only that leading scalar-sized output prefix, not every matrix element.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic_usecase` | Untyped pointer declaration/access-chain/load/store lowering; `OpUntypedArrayLengthKHR` runtime-array length; atomic opcode routing through untyped pointer; descriptor-array indexing of untyped variables |
| `type_punning` | Result-type-driven memory transaction width; same-byte-size type reinterpretation; access-chain offset/stride math; 8/16-bit storage capability gating when punning through untyped pointer |
| `variable_pointers` | Untyped pointer value flowing through `OpSelect`/`OpPhi`/`OpFunctionCall`/`OpPtrAccessChain`/`OpPtrEqual`/`OpPtrNotEqual`/`OpPtrDiff`; function/private variable pointer storage |
| `physical_storage` | `OpBitcast` between untyped physical pointer and 64-bit address; physical storage memory model; access-chain on physical untyped pointer |
| `workgroup_memory_explicit_layout` | Aliased vs not-aliased explicit layout with untyped workgroup pointer; 8/16-bit workgroup access capability |
| `cooperative_matrix` | `OpCooperativeMatrixLoadKHR`/`OpCooperativeMatrixStoreKHR` taking untyped pointer; cooperative matrix + Vulkan memory model + SPIR-V 1.6 interaction; matrix layout/role decoding |
| `block_array` | Untyped pointer to array-of-blocks; descriptor-array dynamic indexing; `OpPtrAccessChain` into block arrays; reinterpret/select across normal vs untyped access chains |
| (all subgroups, both memory models) | Memory-model-specific lowering (`Logical Vulkan` vs `Logical GLSL450`); missing `VK_KHR_shader_untyped_pointers` feature gate; wrong SPIR-V target version |

### Cause Analysis

#### Untyped pointer declaration and access-chain lowering

**Possible failure symptoms:** The output buffer mismatches the expected (input) buffer at the elements touched by `OpUntypedAccessChainKHR` + `OpLoad`/`OpStore`. For `ARRAY_LENGTH`, the output `uint32` does not equal the runtime array length. The mismatch is reproducible per case and does not depend on input data values, only on which element index is accessed.

**Possible implementation causes:** The SPIR-V frontend mishandles `OpUntypedVariableKHR` or `OpUntypedAccessChainKHR` and computes a wrong effective address, drops the trailing indices, or ignores the storage class encoded in `OpTypeUntypedPointerKHR`. For `OpUntypedArrayLengthKHR`, the lowering reads the wrong stride or bound. Source-level investigation is needed before attributing the failure to a specific backend stage.

#### Result-type-driven memory transaction width

**Possible failure symptoms:** Type-punning cases (`*_SAME_SIZE_TYPES`, `*_SCALAR_VECTOR`, `*_VECTOR_SCALAR`) produce bytes that match a different width than the load/store result type specifies. For example, loading `%uint32` from memory written as `%float32` returns a value whose low or high bits are zeroed or sign-extended incorrectly.

**Possible implementation causes:** The backend derives the memory transaction width from the pointer's pointee type instead of the `OpLoad`/`OpStore` result type, or it caches a pointee type on the untyped pointer that contradicts the result type at the access site. The `SHORT2_NO_STORAGE_CAP` / `CHAR4_NO_STORAGE_CAP` cases additionally check whether the implementation wrongly requires `StorageBuffer16BitAccess`/`StorageBuffer8BitAccess` when 8/16-bit access happens only through an untyped pointer; if those cases fail, the implementation is over-gating the capability.

#### Pointer-value flow through variable-pointer operations

**Possible failure symptoms:** `variable_pointers` cases fail when the untyped pointer passes through `OpSelect`/`OpPhi`/`OpFunctionCall`/`OpPtrAccessChain` or is compared with `OpPtrEqual`/`OpPtrNotEqual`/`OpPtrDiff`. The output is wrong only on the path that uses the flowed pointer, not on the direct-access path.

**Possible implementation causes:** The optimizer or code generator loses track of the untyped pointer's storage class when it is forwarded through a `phi` or `select`, or it refuses to materialize a `VariablePointers`-conformant pointer value because the untyped pointer type lacks a pointee type. Source-level investigation is needed to confirm whether the failure is in the SPIR-V frontend's variable-pointer legality check or in the backend's pointer representation.

#### Physical storage buffer address round-trip

**Possible failure symptoms:** `physical_storage` cases fail on `OpBitcast` between an untyped `PhysicalStorageBuffer` pointer and a 64-bit address, or on a subsequent load/store through the cast pointer. The output is wrong only for the physical-storage path; the same operations through a `StorageBuffer` untyped pointer succeed.

**Possible implementation causes:** The `OpMemoryModel PhysicalStorageBuffer64` form is not honored, the address computed by `OpBitcast` is truncated or zero-extended incorrectly, or the access-chain on a physical untyped pointer produces a wrong offset. Source-level investigation is needed to separate SPIR-V frontend handling from buffer-device-address backend lowering.

#### Cooperative matrix load/store through untyped pointers

**Possible failure symptoms:** `cooperative_matrix` cases fail specifically when `OpCooperativeMatrixLoadKHR`/`OpCooperativeMatrixStoreKHR` take an untyped pointer as the memory operand, or fail to compile/load at SPIR-V 1.6. The custom oracle can establish only that its leading scalar-sized output prefix differs from the expected scalar bytes; it does not establish that every matrix element is wrong. Non-cooperative untyped pointer cases in the same memory model may still pass.

**Possible implementation causes:** The cooperative-matrix lowering may not accept an untyped pointer as the memory operand, or the SPIR-V 1.6 target override may be absent. The support gate is narrower than a full cooperative-matrix property match: `checkMatrixSupport` tests only whether any property advertises the selected component type in the selected A, B, or C role. A skip therefore establishes neither complete shape/layout support nor an untyped-versus-typed support difference.

#### Memory-model and feature-gate mismatches

**Possible failure symptoms:** A case passes under one memory model but fails under the other, or the entire family is skipped because `shaderUntypedPointers` is reported as unsupported on a device that advertises `VK_KHR_shader_untyped_pointers`.

**Possible implementation causes:** The driver's `OpMemoryModel Logical Vulkan` path handles untyped pointers differently from its `Logical GLSL450` path, or the driver reports `VK_KHR_shader_untyped_pointers` in the extension list but leaves `shaderUntypedPointers = VK_FALSE` in the feature struct. Source-level investigation is needed to confirm whether the failure is a driver feature-query defect or a genuine shader-lowering difference.

## Case Pruning

### Requirement-based pruning

- `VK_KHR_shader_untyped_pointers` and `shaderUntypedPointers` are required for every case. `adjustSpecForUntypedPointers` emits `OpCapability UntypedPointersKHR` + `OpExtension "SPV_KHR_untyped_pointers"` and sets the feature bit ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1637-L1645)).
- The parent instruction registration adds `untyped_pointers` only inside `#ifndef CTS_USES_VULKANSC`; it is absent from the Vulkan SC build and has no `vksc-default` mustpass leaves ([registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21429-L21433)).
- 8/16-bit element types add `OpCapability Int8`/`Int16`/`Float16` plus `SPV_KHR_8bit_storage`/`SPV_KHR_16bit_storage` and the matching `StorageBuffer8BitAccess`/`StorageBuffer16BitAccess`/`UniformAndStorageBuffer8BitAccess`/`UniformAndStorageBuffer16BitAccess`/`StoragePushConstant8`/`StoragePushConstant16` capability per container type ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1713-L1815)).
- `vulkan_memory_model` adds `VulkanMemoryModel` + `SPV_KHR_vulkan_memory_model` and selects SPIR-V 1.3; `cooperative_matrix` requires `VK_KHR_cooperative_matrix` + `cooperativeMatrix`, tests `shaderUntypedPointers`, and gates only on the selected A/B/C component type appearing in the queried cooperative-matrix properties before overriding SPIR-V to 1.6 ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12224-L12303)).
- `variable_pointers` adds `VK_KHR_variable_pointers` + `VariablePointersStorageBuffer`/`VariablePointers`; `physical_storage` adds `VK_KHR_buffer_device_address` + `PhysicalStorageBufferAddresses`; `workgroup_memory_explicit_layout` adds `VK_KHR_workgroup_memory_explicit_layout`; `block_array` adds `SPV_EXT_descriptor_indexing` + `StorageBufferArrayDynamicIndexing` (and `SPV_KHR_variable_pointers` for the `*_PTR_ACCESS_CHAIN`/`SELECT_*` variants).
- Atomic float min/max cases add `VK_EXT_shader_atomic_float2` plus `OpCapability AtomicFloat16/32/64MinMaxEXT`; atomic int64 adds `VK_KHR_shader_atomic_int64` + `Int64Atomics`; atomic float add cases add `VK_EXT_shader_atomic_float` (+ `VK_EXT_shader_atomic_float2` for float16).

### Design-based pruning

- `ATOMIC_DATA_TYPE_CASES` drops `UINT8`/`INT8`/`UINT16`/`INT16` from atomic cases (8/16-bit atomic int ops are noted as unavailable on known devices) and keeps `FLOAT16`, `UINT32`/`INT32`/`FLOAT32`, `UINT64`/`INT64`/`FLOAT64` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L310-L313)).
- `ATOMIC_INT_DATA_TYPE_CASES` further restricts integer-only atomics (min/max/and/or/xor) to 32/64-bit types.
- The `WORKGROUP` container is not exercised by the basic load/store family; it is covered by the `workgroup_memory_explicit_layout` subtree.
- `cooperative_matrix` is registered only under `vulkan_memory_model`; its program builder uses SPIR-V 1.6.

## Key Takeaways

- The page covers one test family, `untyped_pointers`, with Vulkan and GLSL logical-memory-model roots. Physical-storage leaves replace the logical model with `PhysicalStorageBuffer64`, and `cooperative_matrix` is Vulkan-root-only.
- The tested property is that the load/store result type, not the pointer's type, drives the memory transaction, because `OpTypeUntypedPointerKHR` carries no pointee type. Type punning is the most direct probe of this property.
- Every case is hand-authored SPIR-V assembly built from four `tcu::StringTemplate`s; the untyped-pointer instruction trio (`OpTypeUntypedPointerKHR`, `OpUntypedVariableKHR`, `OpUntypedAccessChainKHR`) plus `OpUntypedArrayLengthKHR` is the surface under test.
- Ordinary generated cases use exact byte comparisons through `SpvAsmComputeShaderCase`; in-place round-trip cases make a mismatch evidence about that exercised path. The cooperative-matrix custom oracle is exact only over its leading scalar-sized expected byte range, so it does not validate a full matrix result.
- Failure analysis is per-subgroup; see `## Failure Meaning` for the cause mapping. Memory-model and feature-gate mismatches are the only cross-subgroup causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createUntypedPointersTestGroup` | [vktSpvAsmUntypedPointersTests.cpp#L12702-L12711](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12702-L12711) | Registration root: creates `vulkan_memory_model` and `glsl_memory_model` |
| `addVulkanMemoryModelTestGroup` | [vktSpvAsmUntypedPointersTests.cpp#L12679-L12689](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12679-L12689) | Registers the seven Vulkan subgroups including `cooperative_matrix` |
| `addGLSLMemoryModelTestGroup` | [vktSpvAsmUntypedPointersTests.cpp#L12691-L12700](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12691-L12700) | Registers the six GLSL subgroups (no `cooperative_matrix`) |
| `addBasicUsecaseTestGroup` | [vktSpvAsmUntypedPointersTests.cpp#L12604-L12612](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12604-L12612) | Routes `load`/`store`/`copy`/`array_length`/`atomics`/`descriptor_array` |
| `addLoadTests` | [vktSpvAsmUntypedPointersTests.cpp#L6967-L7083](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L6967-L7083) | Driver for the representative walkthrough case |
| `createShaderHeader` | [vktSpvAsmUntypedPointersTests.cpp#L2513-L2527](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L2513-L2527) | Header template (capabilities/extensions/memory model/entry point) |
| `createShaderAnnotations(LOAD)` | [vktSpvAsmUntypedPointersTests.cpp#L2576-L2586](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L2576-L2586) | Decorations for the LOAD case |
| `createShaderVariables(LOAD)` | [vktSpvAsmUntypedPointersTests.cpp#L3480-L3516](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L3480-L3516) | Types/constants/variables: defines `OpTypeUntypedPointerKHR` and `OpUntypedVariableKHR` |
| `createShaderMain(LOAD)` | [vktSpvAsmUntypedPointersTests.cpp#L5440-L5456](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L5440-L5456) | Entry point body: `OpUntypedAccessChainKHR` + `OpLoad` + `OpStore` |
| `adjustSpecForUntypedPointers` | [vktSpvAsmUntypedPointersTests.cpp#L1637-L1645](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1637-L1645) | Emits `OpCapability UntypedPointersKHR` + extension + feature bit |
| `adjustSpecForMemoryModel` | [vktSpvAsmUntypedPointersTests.cpp#L1406-L1437](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1406-L1437) | Flips `OpMemoryModel` and SPIR-V version |
| `adjustSpecForSmallContainerType` | [vktSpvAsmUntypedPointersTests.cpp#L1713-L1815](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1713-L1815) | 8/16-bit storage capabilities per container |
| `adjustSpecForPhysicalStorageBuffer` | [vktSpvAsmUntypedPointersTests.cpp#L1818-L1846](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1818-L1846) | Overrides `OpMemoryModel` to `PhysicalStorageBuffer64` |
| `adjustSpecForCooperativeMatrix` | [vktSpvAsmUntypedPointersTests.cpp#L1894-L1901](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1894-L1901) | Adds `VK_KHR_cooperative_matrix` + `CooperativeMatrixKHR` |
| `CooperativeMatrixInteractionTestCase::initPrograms` | [vktSpvAsmUntypedPointersTests.cpp#L12255-L12303](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12255-L12303) | Overrides SPIR-V target to 1.6 |
| `CooperativeMatrixInteractionTestCase::checkSupport` | [vktSpvAsmUntypedPointersTests.cpp#L12224-L12253](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12224-L12253) | Gates `shaderUntypedPointers` + `cooperativeMatrix` + matrix support |
| Parameter enums | [vktSpvAsmUntypedPointersTests.cpp#L59-L289](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L59-L289) | All `*_TEST_CASE` enums and matrix layout/type enums |
| Mustpass leaves | [spirv-assembly.txt#L16233-L19552](../../../mustpass/main/vk-default/spirv-assembly.txt#L16233-L19552) | 3,320 `vk-default` leaves: 1,408 GLSL-root and 1,912 Vulkan-root leaves |
