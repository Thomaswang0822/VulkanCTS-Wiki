# vktSpvAsmUntypedPointersTests

## Overview

SPIR-V assembly tests for the `SPV_KHR_untyped_pointers` / `VK_KHR_shader_untyped_pointers` feature area. The file registers Vulkan and GLSL memory-model variants and generates groups for load/store/copy, type punning, atomics, descriptor arrays, memory reinterpretation, variable pointers, physical storage buffers, workgroup memory explicit layout, cooperative matrices, and block arrays ([extension setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1637-L1645), [group registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12604-L12710)).

## Role

Implementation file

## Source

- [vktSpvAsmUntypedPointersTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12702)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.untyped_pointers
├── vulkan_memory_model
└── glsl_memory_model
```

## Test Families

### vulkan_memory_model — Untyped pointers with Vulkan memory model

Tests untyped pointer operations using the Vulkan memory model; the Vulkan variant registers seven subgroups: `basic_usecase`, `type_punning`, `variable_pointers`, `physical_storage`, `workgroup_memory_explicit_layout`, `cooperative_matrix`, and `block_array` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12679-L12689)).

- **basic_usecase**: Core untyped pointer operations including `load`, `store`, `copy`, `array_length`, `atomics`, and `descriptor_array` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12604-L12612)).
- **type_punning**: Type-punning operations including `load`, `store`, `copy`, and `reinterpret`; reinterpret expands into `struct_as_type`, `multiple_access_chains`, and `memory_interpretation` ([type-punning](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12627-L12633), [reinterpret](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12620-L12625)).
- **variable_pointers**: Interactions with variable pointers: `op_select`, `op_ptr_equal`, `op_ptr_not_equal`, `op_ptr_diff`, `op_phi`, `op_function_call`, `op_ptr_access_chain`, `function_variable`, `private_variable`, `multiple_access_chains`, and `workgroup_memory` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12644-L12657)).
- **physical_storage**: Interactions with physical storage buffers: `op_bitcast`, `op_select`, `op_phi`, `op_function_call`, and `op_ptr_access_chain` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12635-L12642)).
- **workgroup_memory_explicit_layout**: Workgroup memory explicit-layout interactions with `aliased` and `not_aliased` variants ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12659-L12665)).
- **cooperative_matrix**: Cooperative matrix interactions with `basic_usecase`, `type_punning`, and `mixed` subgroups ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12667-L12672)).
- **block_array**: Block array operation subgroup ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12674-L12677)).

### glsl_memory_model — Untyped pointers with GLSL memory model

Uses the GLSL memory model and registers `basic_usecase`, `type_punning`, `variable_pointers`, `physical_storage`, `workgroup_memory_explicit_layout`, and `block_array`; unlike the Vulkan memory model variant, this inspected registration does not add a `cooperative_matrix` subgroup ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12691-L12700)).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Memory model | `VULKAN`, `GLSL` | Top-level generated memory-model groups ([enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L133-L139), [registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12702-L12710)) |
| Data type | `UINT8`, `INT8`, `UINT16`, `INT16`, `FLOAT16`, `UINT32`, `INT32`, `FLOAT32`, `UINT64`, `INT64`, `FLOAT64` | Base scalar data types in the inspected enum and base case array ([enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L59-L74), [case array](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L304-L315)) |
| Composite data type | `VEC2` through `VEC4` forms of scalar types | Composite data-type enum drives vector forms for type-punning paths ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L76-L113)) |
| Operation type | `NORMAL`, `ATOMIC` | Operation-type enum used by generated operation families ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L115-L121)) |
| Container type | `STORAGE_BUFFER`, `UNIFORM`, `PUSH_CONSTANT`, `WORKGROUP` | Untyped pointer storage locations ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L123-L131)) |
| Copy operation | `COPY_OBJECT`, `COPY_MEMORY`, `COPY_MEMORY_SIZED` | Copy mechanisms generated by copy tests ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L141-L148)) |
| Base test case | `LOAD`, `STORE`, `COPY_FROM`, `COPY_TO`, `ARRAY_LENGTH`, `DESCRIPTOR_ARRAY` | Core base operations ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L150-L160)) |
| Type-punning test case | load/store/copy same-size and scalar-vector variants, custom struct, multiple access chains, memory interpretation | Type-punning enum and registered subgroup structure ([enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L162-L180), [groups](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12620-L12633)) |
| Atomic test case | `OP_ATOMIC_LOAD` through `OP_ATOMIC_XOR`, plus compare-exchange/exchange/increment/decrement/add/sub/min/max/and/or | Atomic operation enum and subgroup registration ([enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L182-L199), [groups](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12569-L12584)) |
| Pointer test case | Physical-storage and variable-pointer operations such as bitcast, select, phi, access-chain, function-call, equality, inequality, diff, and workgroup memory | Pointer-operation enum and registered interaction groups ([enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L201-L222), [groups](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12635-L12657)) |
| Memory interpretation | large array stride, non-zero offset, mixed offsets, and related read/write interpretations | Memory-interpretation enum and read/write subgroup registration ([enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L224-L237), [groups](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12614-L12618)) |
| Block array test case | Basic and reinterpret/select block-array variants | Block-array enum and subgroup registration ([enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L239-L252), [group](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12674-L12677)) |
| Workgroup test case | `ALIASED`, `NOT_ALIASED` | Workgroup explicit-layout cases ([enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L254-L260), [groups](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12659-L12665)) |
| Cooperative matrix | `BASIC_LOAD`, `BASIC_STORE`, `TYPE_PUNNING_LOAD`, `TYPE_PUNNING_STORE`, `MIXED_LOAD`, `MIXED_STORE` | Cooperative matrix enum and group registration ([enum](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L262-L272), [groups](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12667-L12672)) |
| Matrix layout and role | `ROW_MAJOR`, `COL_MAJOR`; `A`, `B`, `ACCUMULATOR` | Matrix layout/type enums and arrays used by cooperative-matrix generation ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L274-L289), [arrays](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L363-L370)) |

## Support Requirements

- The untyped-pointer setup emits `OpExtension "SPV_KHR_untyped_pointers"`, `OpCapability UntypedPointersKHR`, requests `shaderUntypedPointers`, and adds `VK_KHR_shader_untyped_pointers` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1637-L1645)).
- Data-type helpers add storage/int/float feature requirements according to the generated scalar type; atomic float min/max cases also add `VK_EXT_shader_atomic_float2` where required ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1600-L1627)).
- Variable-pointer tests call `adjustSpecForVariablePointers()` before generating variable-pointer assembly ([example](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L6860-L6865)).
- Physical-storage interaction tests call `adjustSpecForPhysicalStorageBuffer()` and set `usesPhysStorageBuffer` in generated cases ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L11713-L11750)).
- Cooperative matrix interaction cases require both `VK_KHR_shader_untyped_pointers` and `VK_KHR_cooperative_matrix`, check the corresponding feature structs, and verify matrix support for the requested parameters ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12224-L12253)).
- The entire registered `untyped_pointers` group is documented as non-VulkanSC through the registration hierarchy; the source file is compiled/registered under the non-VulkanSC instruction compute path in the surrounding category registration.

## Verification Methods

- Output resources are compared through `SpvAsmComputeShaderCase` expected-output resources; generated cases commonly push the same initialized resource as input and expected output for in-place transformations ([example](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L6879-L6894)).
- Type-punning tests generate assembly from type-punning templates and same-size or scalar/vector data-type combinations, then compare the reinterpreted result through expected resources ([example setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L7161-L7195)).
- Atomic tests construct expected atomic resources from operation descriptors and register compute shader cases against those outputs ([example](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L9150-L9189)).
- Pointer interaction tests generate shader assembly for selected pointer operations, run one workgroup, and compare the resulting resource contents against the expected resource ([physical-storage example](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L11690-L11752)).

## Notes

- The file is very large and defines its major parameter enums near the top of the source ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L59-L289)).
- The Vulkan memory model variant includes `cooperative_matrix`; the GLSL memory model variant does not in the inspected registration ([Vulkan](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12679-L12689), [GLSL](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12691-L12700)).
