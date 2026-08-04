## Overview

**Core question:** Does a SPIR-V `OpVariable` initializer produce the specified value in `Private` and `Output` storage classes?

- This implementation file owns `spirv_assembly.instruction.compute.variable_init` and `spirv_assembly.instruction.graphics.variable_init`.
- The compute family exercises `Private` variables initialized from constants or from pointers to `Workgroup` variables.
- The graphics family exercises constant initialization in `Private` variables across five graphics stages and constant initialization in vertex `Output` variables observed by a fragment shader.
- The test authors SPIR-V assembly templates directly. The result oracle is a host-visible storage buffer filled with `1.0f` expectations.

## Background Knowledge

- SPIR-V `OpVariable` can declare a variable with an initializer whose type matches the declared pointer's pointee type. This page focuses on initialization semantics, rather than ordinary host-created descriptor resources. See the Vulkan shader-module requirement for SPIR-V input in [shaders.adoc](../../../../vulkan-docs/src/chapters/shaders.adoc#L1400-L1416).
- `Private` storage gives each shader invocation its own object. `Workgroup` storage is shared by the invocations in a compute workgroup. The `*_from_workgroup` cases initialize a private pointer, write the composite constant through it, and load the value back through that pointer. Vulkan describes Workgroup storage and its scope in [shaders.adoc](../../../../vulkan-docs/src/chapters/shaders.adoc#L3173-L3217).
- Shader-stage `Output` variables carry values through the graphics interface. The output cases initialize a vertex output and let the fragment shader read the corresponding input. The interface relationship is described in [interfaces.adoc](../../../../vulkan-docs/src/chapters/interfaces.adoc#L56-L108).

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.variable_init
└── private
```

The graphics implementation registers the same `variable_init` family below `spirv_assembly.instruction.graphics`, with the direct children `private` and `output`:

```text
spirv_assembly.instruction.graphics.variable_init
├── private
└── output
```

The source file implements both roots. Their factories are called by the instruction dispatcher in [`vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21399-L21402) and [`vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21498-L21501).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Initialized type | `float`, `vec4`, `matrix`, `floatarray`, `struct` | Selects the composite type used by `OpVariable` and the number of floats written to the result buffer. | [`testParams`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L53-L76) |
| Initialization source | `INITIALIZATION_SOURCE_CONSTANT`, `INITIALIZATION_SOURCE_GLOBAL` | Selects a direct typed constant or a `Private` pointer initialized with the address of a `Workgroup` variable. The shader writes the all-ones value to that Workgroup object only after loading the pointer. | [`InitializationSource`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L47-L59), [global-source assembly construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L184-L203) |
| Storage class | `Private`, `Output` | Chooses the SPIR-V storage class whose initializer behavior becomes observable. `Output` is used only by the graphics output family. | [compute assembly](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L152-L169), [output assembly](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L537-L552) |
| Execution path | compute; graphics `vert`, `tessc`, `tesse`, `geom`, `frag`; graphics output `vert` plus `frag` | Varies the shader stage and the interface path while preserving the initializer value. | [`addGraphicsVariableInitPrivateTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L247-L315), [`addGraphicsVariableInitOutputTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L615-L651) |
| Component count | 1, 4, 8, 8, 16 | Determines the output array stride and expected-buffer length: `float` 1, `vec4` 4, `matrix` 8, `floatarray` 8, `struct` 16. | [`testParams`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L67-L76), [compute sizing](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L127-L175) |

The current `vk-default/spirv-assembly.txt` and `vksc-default/spirv-assembly.txt` each contain 39 matching leaves:

- 9 compute-private leaves: five direct constant cases and four `*_from_workgroup` cases.
- 25 graphics-private leaves: five data types across `frag`, `geom`, `tessc`, `tesse`, and `vert`.
- 5 graphics-output leaves: the five direct constant data types.

The mustpass entries are listed in the [Vulkan default file](../../../mustpass/main/vk-default/spirv-assembly.txt#L19557-L19565) and [Vulkan SC default file](../../../mustpass/main/vksc-default/spirv-assembly.txt#L5677-L5685) for compute, and at [Vulkan default graphics entries](../../../mustpass/main/vk-default/spirv-assembly.txt#L39079-L39108) and [Vulkan SC graphics entries](../../../mustpass/main/vksc-default/spirv-assembly.txt#L20904-L20933).

## Behavior Parameters

The primary behavioral axis is the implementation's three behavior groups. They differ in storage class, initialization route, or shader-stage data flow.

### `compute.private`: compute `Private` initialization

The compute builder runs all nine `testParams` entries. Direct cases declare a typed `Private` variable with an all-ones constant and load it before storing the result. Workgroup-source cases declare a `Private` pointer variable, load the pointer, store the all-ones composite through it into the `Workgroup` object, and load the typed value through the pointer before the output store. The dispatch uses `numElements = 128 / numComponents` workgroups. See [`addComputeVariableInitPrivateTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L113-L227).

### `graphics.private`: graphics-stage `Private` initialization

This builder retains only the five constant-source entries. For each type, it creates a graphics case for `vert`, `tessc`, `tesse`, `geom`, and `frag`. The selected stage initializes a `Private` variable from its all-ones typed constant, writes the value to the storage buffer, and uses the standard graphics helper to run the case. The builder initially requests `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`; the helper clears the irrelevant requirement, retaining the vertex-pipeline feature for `vert`, `tessc`, `tesse`, and `geom`, and the fragment feature for `frag`. See [`addGraphicsVariableInitPrivateTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L231-L315) and [`defaultCheckSupport`](../../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L3196-L3221).

### `graphics.output`: vertex `Output` initialization

This family retains the same five constant-source types but uses a vertex-plus-fragment pipeline. The vertex module declares `outData` in `Output` storage with the typed all-ones initializer. It also forwards position and a color through ordinary interface variables. The fragment module loads the `Output`-backed input at location 2 and stores it into the descriptor-backed storage buffer. For `struct`, the interface carries a structure containing a matrix, a vector, and four scalar floats. See [`addShaderCodeOutput`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L329-L599) and [`addGraphicsVariableInitOutputTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L602-L653).

## Shader Analysis

This category constructs SPIR-V assembly directly in C++ string templates. The following walkthrough extracts one exact compute assembly case. The `spirv_assembly` category workflow publishes the CTS-authored assembly under `#### Source Code`; it does not reconstruct GLSL/HLSL or publish a duplicate `#### SPIR-V` disassembly subsection. The extracted module should still pass `spirv-as`, `spirv-val`, and `spirv-dis` validation before publication.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.variable_init.private.float
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute.private` | The compute implementation writes the initialized value to a storage buffer. |
| `float` | `%f1` has type `Private %f32`, and each output element occupies one 32-bit float. |
| `INITIALIZATION_SOURCE_CONSTANT` | The initializer is `%f32_1`, so the selected `Private` object receives the constant directly. |
| `numElements = 128` | The builder launches 128 one-invocation workgroups and writes one buffer element per invocation. |

#### Purpose

This module checks direct constant initialization of a `Private` scalar. Each invocation loads the initialized value and stores it at its own `GlobalInvocationId.x` result index.

#### Structural Design

| Phase | SPIR-V operation shape | Observable role |
|-------|------------------------|-----------------|
| Type and constant setup | `%f32`, `%f32_1`, `OpTypePointer Private %f32` | Defines a scalar and its all-ones initializer. |
| Variable declaration | `%f1 = OpVariable %dataPtr Private %f32_1` | Tests `OpVariable` initialization in `Private` storage. |
| Invocation index | Load `GlobalInvocationId.x` | Selects one of 128 result elements. |
| Result write | `OpLoad %f32 %f1`, then `OpAccessChain` and `OpStore` | Makes the initializer observable to the host. |

#### Source Code

<details>
<summary>Click to expand CTS-authored SPIR-V assembly for <code>compute.variable_init.private.float</code></summary>

```llvm
                         OpCapability Shader
                         OpExtension "SPV_KHR_storage_buffer_storage_class"
                    %1 = OpExtInstImport "GLSL.std.450"
                         OpMemoryModel Logical GLSL450
                         OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
                         OpExecutionMode %main LocalSize 1 1 1
                         OpSource GLSL 430
                         OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
OpDecorate %outputArray ArrayStride 4
                               OpMemberDecorate %Output 0 Offset 0
                               OpDecorate %Output Block
                               OpDecorate %dataOutput DescriptorSet 0
                               OpDecorate %dataOutput Binding 0
                               OpDecorate %floatArray ArrayStride 4
                               OpMemberDecorate %struct 0 Offset 0
                               OpMemberDecorate %struct 1 Offset 32
                               OpMemberDecorate %struct 2 Offset 48
                               OpMemberDecorate %struct 3 Offset 52
                               OpMemberDecorate %struct 4 Offset 56
                               OpMemberDecorate %struct 5 Offset 60
                 %void = OpTypeVoid
             %voidFunc = OpTypeFunction %void
                  %f32 = OpTypeFloat 32
                  %u32 = OpTypeInt 32 0
              %c_u32_0 = OpConstant %u32 0
                %v4f32 = OpTypeVector %f32 4
                      %f32_1 = OpConstant %f32 1
                    %v4f32_1 = OpConstantComposite %v4f32 %f32_1 %f32_1 %f32_1 %f32_1
                     %matrix = OpTypeMatrix %v4f32 2
                   %matrix_1 = OpConstantComposite %matrix %v4f32_1 %v4f32_1
                    %c_u32_8 = OpConstant %u32 8
                 %floatArray = OpTypeArray %f32 %c_u32_8
               %floatArray_1 = OpConstantComposite %floatArray %f32_1 %f32_1 %f32_1 %f32_1 %f32_1 %f32_1 %f32_1 %f32_1
                     %struct = OpTypeStruct %floatArray %v4f32 %f32 %f32 %f32 %f32
                   %struct_1 = OpConstantComposite %struct %floatArray_1 %v4f32_1 %f32_1 %f32_1 %f32_1 %f32_1
                %numElements = OpConstant %u32 128
                %outputArray = OpTypeArray %f32 %numElements
                     %Output = OpTypeStruct %outputArray
                %_ptr_Output = OpTypePointer StorageBuffer %Output
                      %sbPtr = OpTypePointer StorageBuffer %f32
                 %dataOutput = OpVariable %_ptr_Output StorageBuffer
              %dataPtr = OpTypePointer Private %f32
   %_ptr_Function_uint = OpTypePointer Function %u32
               %v3uint = OpTypeVector %u32 3
    %_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
      %_ptr_Input_uint = OpTypePointer Input %u32
                  %int = OpTypeInt 32 1
                %int_0 = OpConstant %int 0
             %f1 = OpVariable %dataPtr Private %f32_1
                 %main = OpFunction %void None %voidFunc
                %entry = OpLabel
        %invocationPtr = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %c_u32_0
           %invocation = OpLoad %u32 %invocationPtr
     %outputData = OpLoad %f32 %f1
            %outputPtr = OpAccessChain %sbPtr %dataOutput %int_0 %invocation
                         OpStore %outputPtr %outputData
                         OpReturn
                         OpFunctionEnd
```

</details>

#### Additional Info

- The template retains declarations for matrix, array, and structure constants even in the scalar specialization. They are part of the common source template; only `%f1` and the result type determine this leaf's executed value path.
- The output buffer is a storage-buffer object at descriptor set 0, binding 0. It is not the initialized `Private` variable.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Initialized type | Changes the `Private` pointer type, constant composite, result element type, array stride, and workgroup count. | [`testParams` and compute specialization](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L122-L176) |
| Initialization source | Replaces the direct typed initializer/load with a pointer load, Workgroup store, and indirect typed load. | [`INITIALIZATION_SOURCE_GLOBAL` branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L178-L203) |
| Workgroup layout variant | Adds `WorkgroupMemoryExplicitLayoutKHR`, entry-point interfaces, and SPIR-V 1.4 for the array and structure global-source cases. | [`WorkgroupMemoryExplicitLayoutKHR` branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L212-L221) |

## Runtime Execution and Result Checking

- The compute builder allocates a `Float32Buffer` containing 128 values of `1.0f`, specializes one assembly module, requests one workgroup per output element, and registers the case as a `SpvAsmComputeShaderCase`. The output array uses an element stride of `numComponents * 4` bytes. See [`addComputeVariableInitPrivateTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L113-L227).
- Direct compute cases load the `Private` object and write the value at the invocation index. Global-source cases perform the extra pointer and Workgroup operations before the same output write.
- Graphics-private cases configure one storage-buffer output containing 128 expected `1.0f` values and invoke `createTestsForAllStages()` for each constant-source type. The common graphics runner accepts exact values or up to one ULP of RTZ/RNE difference; for the vertex, tessellation, and geometry variants, its generic fallback also accepts a finite value equal to the expectation plus a non-negative integer. Thus the expected buffer is all ones, but those four stage variants do not enforce exact all-ones readback. See [`addGraphicsVariableInitPrivateTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L231-L315) and [graphics-resource comparison](../../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L4719-L4784).
- Graphics-output cases create a vertex-plus-fragment pipeline. The expected buffer length equals the selected type's component count, and `outputTest()` calls `runAndVerifyDefaultPipeline()`. See [`outputTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L319-L327) and [`addGraphicsVariableInitOutputTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L636-L651).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `compute.private` | Incorrect `Private` `OpVariable` initialization or load/store lowering; for `*_from_workgroup`, incorrect pointer initialization or Workgroup access. |
| `graphics.private` | Incorrect `Private` initializer handling in a generated vertex, fragment, geometry, tessellation-control, or tessellation-evaluation stage, or incorrect storage-buffer write behavior. |
| `graphics.output` | Incorrect `Output` initializer handling in the vertex stage, interface transfer to the fragment stage, or fragment storage-buffer write behavior. |

### Cause Analysis

#### Compute `Private` initialization and Workgroup-pointer access

**Possible failure symptoms:** One or more output-buffer elements differs from the expected all-ones value. A direct constant case tests the loaded `Private` value. A `*_from_workgroup` failure includes the pointer load, the Workgroup store, or the indirect typed load in the observed path.

**Possible implementation causes:** The source shows two distinct SPIR-V forms. A failing direct case points to handling of a typed `Private` initializer or its load/store path. A failing global-source case can additionally involve `VariablePointers`, the Workgroup object, or the pointer's pointee type. The test does not isolate which instruction failed, so source-level investigation is needed for a narrower diagnosis.

#### Graphics `Private` initialization

**Possible failure symptoms:** The graphics helper reports a storage-buffer result outside its accepted comparison for one or more generated shader stages. The expected buffer contains 128 `1.0f` values; the `frag` variant allows only the runner's one-ULP RTZ/RNE tolerance, while the `vert`, `tessc`, `tesse`, and `geom` variants additionally accept finite values equal to the expectation plus a non-negative integer.

**Possible implementation causes:** The selected stage uses a `Private` initialized constant, then writes that value through the common graphics path. A failure can reflect stage-specific lowering of `OpVariable`, the storage-buffer write, or shared graphics setup. The result alone does not distinguish those paths, so source-level investigation is needed.

#### Graphics `Output` initialization and interface transfer

**Possible failure symptoms:** `runAndVerifyDefaultPipeline()` reports a mismatch in the selected type's output buffer. The mismatch means the fragment stage did not store the expected all-ones value received from the vertex output path.

**Possible implementation causes:** The vertex `Output` initializer, the vertex-to-fragment interface matching, the fragment input load, or the fragment storage-buffer store could produce the mismatch. The test observes the final buffer and does not independently check each interface step.

## Case Pruning

### Requirement-based pruning

- Graphics-private skips every `INITIALIZATION_SOURCE_GLOBAL` entry. That builder only creates constant-source cases.
- Graphics-output makes the same constant-source-only selection. Workgroup-pointer initializers are not meaningful for this vertex-output interface path.
- All cases require `VK_KHR_storage_buffer_storage_class`, because the result buffer uses the SPIR-V `StorageBuffer` class.
- Compute global-source cases request `VK_KHR_variable_pointers` and the `variablePointers` feature. `floatarray_from_workgroup` and `struct_from_workgroup` additionally request `VK_KHR_workgroup_memory_explicit_layout` and SPIR-V 1.4.
- Graphics-private initially requests `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`; its support helper retains only the feature for the customized stage: vertex-pipeline stores for `vert`, `tessc`, `tesse`, and `geom`, or fragment stores for `frag`. Graphics-output requests `fragmentStoresAndAtomics`.

### Design-based pruning

The common parameter table contains nine entries, but the graphics builders intentionally retain only the five direct constant entries. The four Workgroup-source entries therefore appear only under compute. The five data types are tested in every generated graphics-private stage, while output initialization has one vertex-plus-fragment case per type.

## Key Takeaways

- The compute cases separate direct constant initialization from pointer-valued initialization that reaches a Workgroup variable. The global-source module writes the all-ones composite after loading that pointer; it does not initialize the Workgroup variable in its declaration.
- The graphics-private cases repeat direct `Private` initialization across five shader stages without changing the expected all-ones oracle.
- The graphics-output cases test a different storage class and observe the initialized vertex value after fragment-stage interface transport.
- The host-visible storage buffer validates the complete path but cannot localize a failure to one SPIR-V instruction or one pipeline stage without further investigation.
- The current mustpass inventory contains 39 leaves for each inspected Vulkan and Vulkan SC default file: 9 compute-private, 25 graphics-private, and 5 graphics-output.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter table and shared assembly templates | [`vktSpvAsmVariableInitTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L47-L111) | Defines the types, constants, storage-buffer layout, and Workgroup declarations. |
| Compute-private registration and generator | [`addComputeVariableInitPrivateTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L113-L229) | Builds direct and indirect initialization cases and registers nine compute leaves. |
| Graphics-private registration and generator | [`addGraphicsVariableInitPrivateTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L231-L317) | Registers five types across five graphics stages. |
| Graphics output shader construction | [`addShaderCodeOutput`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L329-L600) | Builds the type-specific vertex and fragment SPIR-V assembly. |
| Graphics output registration and expected result | [`addGraphicsVariableInitOutputTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L602-L654) | Registers the five output cases and their all-ones buffers. |
| Group factories | [`createVariableInitComputeGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L658-L674) | Defines the two `variable_init` roots. |
| Compute mustpass leaves | [`spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt#L19557-L19565) | Confirms the nine compute-private leaves. |
| Graphics mustpass leaves | [`spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt#L39079-L39108) | Confirms the 25 graphics-private and 5 graphics-output leaves. |
| SPIR-V storage classes and interfaces | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L2999-L3005), [`interfaces.adoc`](../../../../vulkan-docs/src/chapters/interfaces.adoc#L56-L108) | Grounds the storage-class and stage-interface concepts used by the tests. |
