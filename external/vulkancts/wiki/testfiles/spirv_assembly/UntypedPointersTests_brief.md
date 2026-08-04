# Understanding Brief: spirv_assembly.instruction.compute.untyped_pointers

## One-Sentence Test Purpose

This test checks whether an implementation that advertises `VK_KHR_shader_untyped_pointers` can correctly declare, access, load, store, copy, atomically update, type-pun, and pass through untyped pointer variables across storage buffers, uniform buffers, push constants, workgroup memory, physical storage buffers, descriptor arrays, and cooperative matrices, using hand-authored SPIR-V assembly built from `OpTypeUntypedPointerKHR` / `OpUntypedVariableKHR` / `OpUntypedAccessChainKHR` / `OpUntypedArrayLengthKHR` instead of typed `OpTypePointer` variables.

## Background Knowledge

### `SPV_KHR_untyped_pointers` and `VK_KHR_shader_untyped_pointers`

`SPV_KHR_untyped_pointers` introduces a pointer type whose pointee type is not encoded in the pointer's type — `OpTypeUntypedPointerKHR <StorageClass>` takes only a storage class. The pointee type is supplied at the access/load/store site rather than at the pointer declaration. Vulkan exposes this through the `VK_KHR_shader_untyped_pointers` extension and the `shaderUntypedPointers` feature bit, which the CTS spec demands via `OpCapability UntypedPointersKHR` plus `OpExtension "SPV_KHR_untyped_pointers"` ([extension setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1637-L1645)).

Why it matters here:
- The whole test family is built around three new instructions that only make sense with the untyped-pointer capability: `OpUntypedVariableKHR` (variable whose type is an untyped pointer), `OpUntypedAccessChainKHR` (access chain returning an untyped pointer), and `OpUntypedArrayLengthKHR` (runtime array length queried through an untyped pointer).
- Because the pointee type is no longer in the pointer, the load/store instruction itself carries the result type. A correct implementation must honor that type at the memory access, independent of any decoration or pointer-type encoding.

### Memory model split: Vulkan vs GLSL450

SPIR-V `OpMemoryModel` selects the memory semantics available to atomics and barriers. `Logical Vulkan` (with `OpCapability VulkanMemoryModel` and `SPV_KHR_vulkan_memory_model`) is the newer model tied to SPIR-V 1.3+; `Logical GLSL450` is the original model. The untyped-pointer extension itself does not depend on the memory model, so the test registers two parallel subtrees — `vulkan_memory_model` and `glsl_memory_model` — that exercise the same pointer operations under each model ([Vulkan registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12679-L12689), [GLSL registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12691-L12700)).

Why it matters here:
- `adjustSpecForMemoryModel()` flips `OpMemoryModel Logical Vulkan` vs `OpMemoryModel Logical GLSL450` and bumps `spirvVersion` to `SPIRV_VERSION_1_3` only for the Vulkan path ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1406-L1437)).
- The cooperative-matrix interaction subtree is registered only under `vulkan_memory_model`. Cooperative matrices require SPIR-V 1.6 and `VK_KHR_cooperative_matrix`, and the interaction cases override `spirvVersion` to `SPIRV_VERSION_1_6` regardless of the memory-model default ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12296-L12302)).

### Type punning through untyped pointers

Because an untyped pointer carries no pointee type, the same pointer can be loaded as one type and stored as a different type as long as the two types share the same byte size. This is the "type punning" the test family exercises: load `%uint32` from an untyped pointer whose backing memory was written as `%float32`, or load a scalar where a vector was stored. The same mechanism backs the `memory_interpretation` subgroups that reinterpret memory through access chains with non-zero offsets, large strides, or mixed offsets.

Why it matters here:
- Type punning is the property most unique to untyped pointers — typed `OpTypePointer` makes punning illegal at the SPIR-V type level. Failure here points specifically at how the implementation lowers the load/store result type to the actual memory transaction.
- The `MEMORY_INTERPRETATION_TEST_CASE` enum includes cases (`SHORT2_NO_STORAGE_CAP`, `CHAR4_NO_STORAGE_CAP`, `CHAR2_16BIT_STORAGE_CAP`) that probe whether the implementation requires 8/16-bit storage capabilities when 8/16-bit punning happens purely through an untyped pointer ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1647-L1682)).

### Variable pointers, physical storage buffers, and cooperative matrices as pointer-value interactions

Untyped pointers must also interoperate with the rest of the pointer machinery in SPIR-V:

- `VK_KHR_variable_pointers` lets a pointer value flow through `OpSelect`, `OpPhi`, `OpFunctionCall`, `OpPtrAccessChain`, `OpPtrEqual`, `OpPtrNotEqual`, and `OpPtrDiff`. The `variable_pointers` subtree verifies these operations on untyped pointer values.
- `VK_KHR_physical_storage_buffer` (buffer device address) introduces `PhysicalStorageBuffer` storage class. The `physical_storage` subtree verifies `OpBitcast` between an untyped physical pointer and an integer address, plus select/phi/access-chain/function-call on physical untyped pointers. This subtree overrides `OpMemoryModel` to `PhysicalStorageBuffer64 <Vulkan|GLSL450>` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1818-L1846)).
- `VK_KHR_cooperative_matrix` loads and stores cooperative matrices through untyped pointers (`OpCooperativeMatrixLoadKHR` / `OpCooperativeMatrixStoreKHR` taking an untyped pointer). The `cooperative_matrix` subtree runs `basic_usecase`, `type_punning`, and `mixed` subgroups that combine untyped pointer access with cooperative matrix operations.

## One Concrete Example

Representative compute case: `dEQP-VK.spirv_assembly.instruction.compute.untyped_pointers.vulkan_memory_model.basic_usecase.load.storage.uint32`.

The C++ builder [`addLoadTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L6967-L7083) holds four `tcu::StringTemplate`s — `shaderHeader`, `shaderAnnotations`, `shaderVariables`, `shaderFunctions` — built once from `createShaderHeader()`, `createShaderAnnotations(BaseTestCases::LOAD)`, `createShaderVariables(BaseTestCases::LOAD)`, and `createShaderMain(BaseTestCases::LOAD)`. For the `storage` container and `uint32` data type the host fills the spec map with:

- `${baseType}` = `uint32`, `${baseDecl}` = `OpTypeInt   32 0`
- `${storageClass}` = `StorageBuffer` (from `getStorageClass(STORAGE_BUFFER)`)
- `${threadCount}` = `64` (`Constants::numThreads`)
- `${alignment}` = `4` (`getSizeInBytes(UINT32)`)
- `${loadOp}` = `OpLoad`, `${args}` = `""` (the `NORMAL` entry of `LOAD_OPERATION_CASES`)
- `${storageDecorations}` from `getResourceDecorations(STORAGE_BUFFER, UINT32, 64)` — `ArrayStride 4` plus descriptor set/binding 0/1.

The specialized SPIR-V declares an untyped input pointer `%input_data_untyped_var = OpUntypedVariableKHR %storage_buffer_untyped_ptr StorageBuffer %input_buffer` and a typed output pointer `%output_data_var = OpVariable %output_buffer_storage_buffer_ptr StorageBuffer`. Each of the 64 invocations reads `GlobalInvocationId.x`, computes `%input_data_var_loc = OpUntypedAccessChainKHR %storage_buffer_untyped_ptr %input_buffer %input_data_untyped_var %c_uint32_0 %x`, loads `%uint32` from that untyped location, and stores it into the typed output buffer at the same index. The expected output buffer equals the input buffer (in-place round trip), so a mismatch isolates the untyped-pointer load path.

## End-to-End Test Flow

```text
[host] pick memory model (VULKAN|GLSL), subgroup, container type, data type, and operation
[host] call adjustSpecForUntypedPointers + adjustSpecForMemoryModel + adjustSpecForDataTypes + adjustSpecForSmallContainerType (+ subgroup-specific adjusters) to assemble extensions/capabilities/feature bits
[host] specialize the four StringTemplates (header/annotations/variables/main) into one SPIR-V assembly string
[host] create a filled input buffer (random data, seed = deStringHash(testGroup name)); for PUSH_CONSTANT bind it as push constants, otherwise as descriptor set 0 binding 0
[host] create an expected output resource (commonly equal to the input for in-place round trips; atomics build it from the operation descriptor)
[host] dispatch numWorkGroups = (PUSH_CONSTANT ? pushConstArraySize=4 : numThreads=64) work groups of local size 1 1 1
[device] each invocation reads GlobalInvocationId.x, OpUntypedAccessChainKHR into the untyped input pointer, performs the load/store/copy/atomic/pun, and writes the typed output
[host] SpvAsmComputeShaderCase copies back the output SSBO
[host] compare output against the expected resource byte-for-byte (exact comparison through the SpvAsmComputeShaderCase expected-output mechanism)
[host] pass only if every element matches
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- **Specialized SPIR-V assembly text.** Every subgroup holds four `tcu::StringTemplate`s (header, annotations, variables, main) and specializes them through a `map<string,string>` of placeholders (`${baseType}`, `${baseDecl}`, `${storageClass}`, `${alignment}`, `${threadCount}`, `${loadOp}`, `${storeOp}`, `${copyOp}`, `${extensions}`, `${capabilities}`, `${memModelOp}`, `${sameSizeType}`, `${sameSizeDecl}`, `${matrixUse}`, `${matrixLayout}`, ...). The specialized text is registered with `dst.spirvAsmSources.add("comp")`. There is no GLSL or HLSL source anywhere in this file.
- **Per-case capability/extension blocks.** `adjustSpecForUntypedPointers`, `adjustSpecForMemoryModel`, `adjustSpecForDataTypes`, `adjustSpecForSmallContainerType`, `adjustSpecForAtomicOperations`, `adjustSpecForAtomicAddOperations`, `adjustSpecForAtomicMinMaxOperations`, `adjustSpecForMemoryInterpretation`, `adjustSpecForBlockArray`, `adjustSpecForVariablePointers`, `adjustSpecForPhysicalStorageBuffer`, `adjustSpecForWorkgroupMemoryExplicitLayout`, and `adjustSpecForCooperativeMatrix` each push `OpCapability`/`OpExtension` strings into a vector that is concatenated into the header's `${capabilities}` and `${extensions}` slots.
- **SPIR-V target version per subtree.** `SPIRV_VERSION_1_3` for `vulkan_memory_model` (set by `adjustSpecForMemoryModel`), `SPIRV_VERSION_1_0` implicit for `glsl_memory_model`, and `SPIRV_VERSION_1_6` for the cooperative-matrix interaction subtree (set explicitly in `CooperativeMatrixInteractionTestCase::initPrograms`).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input buffer (storage/uniform/push-constant form) | yes, `createFilledBuffer`/`createFilledResource` with `FillingTypes::RANDOM` seeded by `deStringHash(testGroup->getName())` | yes, descriptor set 0 binding 0 (or push constants for `PUSH_CONSTANT`) | read by `OpUntypedAccessChainKHR` + `OpLoad`/`OpAtomicLoad` | no | backs the untyped pointer the test exercises |
| Output buffer (storage buffer) | yes, `createFilledResource` with the same desc as input (commonly in-place round trip) | yes, descriptor set 0 binding 1 | written by `OpStore`/`OpAtomicStore`/`OpCopyMemory`/`OpCopyMemorySized` | yes | the host compares this byte-for-byte against the expected resource |
| Push constants (PUSH_CONSTANT container only) | yes, sized to `Constants::pushConstArraySize = 4` | yes, push-constant range | read via untyped pointer | no | exercises untyped pointers in the `PushConstant` storage class |
| Workgroup memory (WORKGROUP container / explicit-layout subtree) | declared as `%workgroup_untyped_var = OpUntypedVariableKHR ... Workgroup ...` | shader-local | read/written by the same workgroup | no | exercises untyped pointers in `Workgroup` storage, including aliased vs not-aliased explicit layout |
| Physical storage buffer (physical_storage subtree) | yes, buffer device address | yes, `PhysicalStorageBuffer` | read/written through `OpBitcast` between `OpTypeUntypedPointerKHR PhysicalStorageBuffer` and `OpTypeInt 64` | yes | exercises untyped pointers in the physical storage class, overriding `OpMemoryModel` to `PhysicalStorageBuffer64` |

## What Is Checked

- The output storage buffer is compared against an expected resource byte-for-byte through `SpvAsmComputeShaderCase`'s expected-output mechanism. There is no per-case tolerance; the comparison is exact.
- For in-place round-trip cases (load/store/copy), the expected output equals the random input, so any byte mismatch isolates the untyped-pointer path.
- For atomic cases, the expected resource is constructed by the host from the operation descriptor (initial value, operand, compare/exchange value) so the test checks both the new memory state and, where relevant, the value returned by the atomic.
- For type-punning cases, the expected output is the host-side reinterpretation of the input under the same byte-size mapping.
- Each generated case is registered as its own `SpvAsmComputeShaderCase` and checked independently.

## Behavior Parameter Identification

> **Behavior parameter:** `subgroup` (the intermediate node below `<memory_model>` — `basic_usecase`, `type_punning`, `variable_pointers`, `physical_storage`, `workgroup_memory_explicit_layout`, `cooperative_matrix`, `block_array`)
>
> **Candidate values:** `basic_usecase`, `type_punning`, `variable_pointers`, `physical_storage`, `workgroup_memory_explicit_layout`, `cooperative_matrix`, `block_array`

A secondary axis is `memory_model` (`VULKAN` vs `GLSL`); it changes `OpMemoryModel` and the SPIR-V target version but reuses the same pointer operations, except that `cooperative_matrix` is registered only under `VULKAN`.

## What Failure Means

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

## Important Variations and Special Cases

- **Container type axis (basic_usecase only).** `LOAD_CONTAINER_TYPE_CASES` covers `STORAGE_BUFFER`, `UNIFORM`, and `PUSH_CONSTANT` for the load family. `UNIFORM` widens the array stride to `Constants::uniformAlignment = 16` and binds the input as `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER`. `PUSH_CONSTANT` shrinks `numWorkgroup` to `Constants::pushConstArraySize = 4` and moves the input into push constants. The `WORKGROUP` container exists in the `ContainerTypes` enum but is exercised through the workgroup explicit-layout subtree rather than the basic load/store family.
- **Atomic data-type pruning.** `ATOMIC_DATA_TYPE_CASES` drops 8-bit and `INT16` types (8/16-bit atomic int ops are noted as unavailable on known devices) and `ATOMIC_INT_DATA_TYPE_CASES` further restricts integer-only atomics to 32/64-bit. Float atomics add `VK_EXT_shader_atomic_float` / `VK_EXT_shader_atomic_float2` plus the matching `OpCapability AtomicFloat*MinMaxEXT` only for the min/max cases.
- **Type-punning shape axis.** `TypePunningTestCases` splits into `*_SAME_SIZE_TYPES` (same byte size, different type), `*_SCALAR_VECTOR` (scalar ↔ vector of the same total size), and `*_VECTOR_SCALAR`. The `reinterpret` subtree further splits into `struct_as_type`, `multiple_access_chains`, and `memory_interpretation` (read/write).
- **Memory-interpretation capability probes.** `SHORT2_NO_STORAGE_CAP` / `CHAR4_NO_STORAGE_CAP` deliberately omit `StorageBuffer16BitAccess`/`StorageBuffer8BitAccess` to test whether the implementation requires those capabilities when 8/16-bit access happens only through an untyped pointer. `CHAR2_16BIT_STORAGE_CAP` does request them.
- **Cooperative-matrix subtree is Vulkan-memory-model-only.** `addGLSLMemoryModelTestGroup` does not register `cooperative_matrix`. The cooperative-matrix interaction cases override `spirvVersion` to `SPIRV_VERSION_1_6` and check both `shaderUntypedPointers` and `cooperativeMatrix` feature bits, plus per-matrix-type support via `checkMatrixSupport`.
- **Physical-storage overrides the memory model.** `adjustSpecForPhysicalStorageBuffer` rewrites `OpMemoryModel` to `PhysicalStorageBuffer64 Vulkan` or `PhysicalStorageBuffer64 GLSL450` and adds `VK_KHR_buffer_device_address` + `OpCapability PhysicalStorageBufferAddresses`.
- **Block-array subtree always adds descriptor indexing.** `adjustSpecForBlockArray` adds `SPV_EXT_descriptor_indexing` + `StorageBufferArrayDynamicIndexing`; the `REINTERPRET_*_PTR_ACCESS_CHAIN` and `SELECT_*` variants additionally pull in `SPV_KHR_variable_pointers`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Extension/capability setup | [vktSpvAsmUntypedPointersTests.cpp#L1637-L1645](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1637-L1645) | `adjustSpecForUntypedPointers` — emits `OpCapability UntypedPointersKHR`, `OpExtension "SPV_KHR_untyped_pointers"`, `VK_KHR_shader_untyped_pointers` |
| Memory model adjuster | [vktSpvAsmUntypedPointersTests.cpp#L1406-L1437](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1406-L1437) | `adjustSpecForMemoryModel` — flips `OpMemoryModel` and SPIR-V version |
| Parameter enums | [vktSpvAsmUntypedPointersTests.cpp#L59-L289](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L59-L289) | All `*_TEST_CASE` enums and matrix layout/type enums |
| Shader header builder | [vktSpvAsmUntypedPointersTests.cpp#L2513-L2527](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L2513-L2527) | `createShaderHeader` |
| LOAD annotations | [vktSpvAsmUntypedPointersTests.cpp#L2576-L2586](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L2576-L2586) | `createShaderAnnotations(BaseTestCases::LOAD)` |
| LOAD variables | [vktSpvAsmUntypedPointersTests.cpp#L3480-L3516](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L3480-L3516) | `createShaderVariables(BaseTestCases::LOAD)` — `OpTypeUntypedPointerKHR`, `OpUntypedVariableKHR` |
| LOAD main | [vktSpvAsmUntypedPointersTests.cpp#L5440-L5456](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L5440-L5456) | `createShaderMain(BaseTestCases::LOAD)` — `OpUntypedAccessChainKHR` + `OpLoad` |
| `addLoadTests` driver | [vktSpvAsmUntypedPointersTests.cpp#L6967-L7083](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L6967-L7083) | Specializes the four templates and binds input/output resources |
| Cooperative-matrix SPIR-V 1.6 override | [vktSpvAsmUntypedPointersTests.cpp#L12255-L12303](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12255-L12303) | `CooperativeMatrixInteractionTestCase::initPrograms` — sets `SPIRV_VERSION_1_6` |
| Cooperative-matrix support check | [vktSpvAsmUntypedPointersTests.cpp#L12224-L12253](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12224-L12253) | `checkSupport` — gates `shaderUntypedPointers` + `cooperativeMatrix` + matrix support |
| Physical-storage adjuster | [vktSpvAsmUntypedPointersTests.cpp#L1818-L1846](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L1818-L1846) | Overrides `OpMemoryModel` to `PhysicalStorageBuffer64` |
| Registration root | [vktSpvAsmUntypedPointersTests.cpp#L12702-L12711](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12702-L12711) | `createUntypedPointersTestGroup` — registers `vulkan_memory_model` and `glsl_memory_model` |
| Vulkan subtree registration | [vktSpvAsmUntypedPointersTests.cpp#L12679-L12689](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12679-L12689) | `addVulkanMemoryModelTestGroup` |
| GLSL subtree registration | [vktSpvAsmUntypedPointersTests.cpp#L12691-L12700](../../../modules/vulkan/spirv_assembly/vktSpvAsmUntypedPointersTests.cpp#L12691-L12700) | `addGLSLMemoryModelTestGroup` — no `cooperative_matrix` |
| Mustpass leaves | [spirv-assembly.txt#L16233-L16244](../../../mustpass/main/vk-default/spirv-assembly.txt#L16233-L16244) | Sample `glsl_memory_model.basic_usecase.array_length.*` leaves |

## Questions / Risk Points for User Audit

- Is the `subgroup`-as-primary-behavior-axis identification correct, or should `memory_model` be treated as the primary axis with `subgroup` as a secondary axis? My current identification treats `subgroup` as primary because it changes what is being tested, while `memory_model` only changes the surrounding semantics.
- The `vulkan-docs/src/chapters/` directory is not present in this checkout, so spec grounding for `VK_KHR_shader_untyped_pointers` is drawn from the SPIR-V extension and CTS source rather than the Vulkan spec chapters. Is an external spec read required before the page ships, or is the SPIR-V extension + CTS source sufficient?
- The representative walkthrough case picks `vulkan_memory_model.basic_usecase.load.storage.uint32` because it is the smallest case that exercises the three new untyped-pointer instructions (`OpTypeUntypedPointerKHR`, `OpUntypedVariableKHR`, `OpUntypedAccessChainKHR`) and runs at SPIR-V 1.3. A second walkthrough covering `type_punning` or `physical_storage` would expose a different mechanism. Should a second walkthrough be added?
- The `memory_interpretation` subtree has the `SHORT2_NO_STORAGE_CAP` / `CHAR4_NO_STORAGE_CAP` capability-probe cases whose pass/fail expectation is "succeeds even without the 8/16-bit storage capability because access is through an untyped pointer." Is this expectation correct, or do these cases expect a specific validation outcome?

## Conversion Notes for Final Wiki Rewrite

- The brief's `Background Knowledge` (untyped pointers, memory model split, type punning, pointer-value interactions) should be distilled into a compact Level-3 `## Background Knowledge` bullet list, keeping the untyped-pointer instruction trio, the memory-model split, and the type-punning property.
- The concrete `load.storage.uint32` example becomes the single `### Representative Shader Walkthrough 1` under `## Shader Analysis`. Per the `TEMP-SPIRV-ASSEMBLY` deviation, the assembly is placed under `#### Source Code` (unfoldable, `;`-annotated), and `#### SPIR-V` is omitted.
- The `### Failure Cause Mapping` table above is copied directly into the final page's `### Failure Cause Mapping`.
- The host/device flow becomes a compact `## Runtime Execution and Result Checking` list; the resource table is condensed to the input/output/push-constant/workgroup/physical picture.
- The container-type, atomic pruning, type-punning shape, and capability-probe variations move into `## Parameter Dimensions and Observed Values`, `## Behavior Parameters`, and `## Case Pruning` rather than `Important Variations`.
- Source mappings become the `## Source Reference Appendix` table.
