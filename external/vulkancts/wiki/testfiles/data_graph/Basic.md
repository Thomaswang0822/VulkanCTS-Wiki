## Overview

**Core question:** Does a TOSA-backed data graph pipeline accept the declared tensor graph, resource layout, and execution path, then produce the reference tensor results when submitted?

- This page covers the implementation-bearing `data_graph.basic` test family in `vktDataGraphBasicTests.cpp`. It registers `create_pipeline` and `submit_pipeline`, and obtains the graph implementation from the TOSA provider.
- `create_pipeline` checks creation of a data graph pipeline and its session. Its generated cases vary the shader input form and compiler-control chain in addition to the graph parameters.
- `submit_pipeline` creates and binds the graph, dispatches it with `cmdDispatchDataGraphARM`, waits for completion, and checks output tensors against TOSA reference computations.
- The generated suffixes cover resource cardinality, session memory, format strings, input/output/constant stride modes, binding order, tiling, and sparse constants. The full suffix axes are described in the parameter tables below rather than expanded as hierarchy nodes.

## Background Knowledge

- A data graph pipeline describes a graph over tensor resources. Inputs and outputs are tensor resources bound through descriptor sets; constants are pipeline resources supplied as host data. This distinction explains why the submit path creates descriptors only for tensor resources, while pipeline construction also adds constants.
- A tensor description carries a format, dimensions, tiling, and optional explicit strides. Packed and non-packed layouts can address the same logical elements with different memory spacing, so the host-side strided view must use the same description as the tensor object.
- A pipeline session is the session object passed to `cmdDispatchDataGraphARM`. The TOSA provider also uses session memory as a graph-selection dimension: the no-session-memory cases select one-layer graphs, while the session-memory cases select two-layer graphs.

## Registration Hierarchy

The page covers both implementation-bearing test families registered by `basicTestsGroup`:

```text
data_graph.basic
├── create_pipeline
└── submit_pipeline
```

`basicTestsGroup` adds these two direct children in [vktDataGraphBasicTests.cpp#L423-L427](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L423-L427). The mustpass file contains the corresponding prefixes `dEQP-VK.data_graph.basic.create_pipeline` and `dEQP-VK.data_graph.basic.submit_pipeline` in [data-graph.txt#L1-L2](../../../mustpass/main/vk-default/data-graph.txt#L1-L2).

## Parameter Dimensions and Observed Values

The source generates a Cartesian product and keeps only `TestParams` values that pass `valid()` and have a supported TOSA format. These dimensions are therefore generated suffix axes, not additional registration hierarchy levels.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `create_pipeline`, `submit_pipeline` | Selects handle-creation checking or full dispatch and result checking. | [vktDataGraphBasicTests.cpp#L397-L427](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L397-L427) |
| Instruction set | `tosa` | Selects `DataGraphTestProviderTosa`, the only provider branch implemented here. | [vktDataGraphTestProvider.hpp#L44-L62](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.hpp#L44-L62) |
| Shader input for `create_pipeline` | `shaderBinary`, `shaderModule` | Supplies the generated SPIR-V through `VkShaderModuleCreateInfo` or `VkDataGraphPipelineShaderModuleCreateInfoARM`. | [vktDataGraphBasicTests.cpp#L195-L217](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L195-L217) |
| Compiler control for `create_pipeline` | `noCompCtrl`, `emptyCompCtrl` | Omits the compiler-control structure or chains one with `pVendorOptions` set to an empty string. | [vktDataGraphBasicTests.cpp#L219-L225](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L219-L225) |
| Input cardinality | `noIn`, `oneIn`, `manyIn` in the generator; observed basic mustpass cases use `oneIn` and `manyIn` | Chooses the number of graph inputs. The provider implements the one-input/one-output families and the many-input/many-output add/sub family. | [vktDataGraphTestUtil.hpp#L106-L111](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L106-L111), [vktDataGraphTosaUtil.hpp#L1206-L1240](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1206-L1240) |
| Output cardinality | `oneOut`, `manyOut` | Chooses the number of graph outputs. No-output combinations are removed by `valid()`. | [vktDataGraphTestUtil.cpp#L166-L170](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L166-L170) |
| Constant cardinality | `noConst`, `manyConst` in observed basic cases | Selects graphs without constants or convolution graphs with weights and bias constants. | [vktDataGraphTosaUtil.hpp#L1210-L1237](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1210-L1237) |
| Session memory | `noSession`, `session` | Selects one-layer or two-layer TOSA graph implementations for the supported cardinality combinations. | [vktDataGraphTosaUtil.hpp#L1243-L1275](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1243-L1275) |
| Format string | `i8`, `i32`, `fp16`, `fp32`, `i8i8i32`, `fp16fp16fp16`, `fp32fp32fp32` | Selects the Vulkan formats and host types used by the chosen TOSA graph. | [vktDataGraphTosaUtil.hpp#L235-L253](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L235-L253), [vktDataGraphTosaUtil.hpp#L881-L901](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L881-L901) |
| Input stride mode | `implicitIn`, `packedIn`, `notPackedIn` | Selects implicit strides, explicit packed strides, or explicit non-packed strides for input tensors. | [vktDataGraphTestUtil.cpp#L80-L96](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L80-L96), [vktDataGraphTosaUtil.hpp#L719-L724](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L719-L724) |
| Output stride mode | `implicitOut`, `packedOut`, `notPackedOut` | Selects the corresponding output tensor stride representation. | [vktDataGraphTestUtil.cpp#L92-L94](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L92-L94), [vktDataGraphTosaUtil.hpp#L726-L732](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L726-L732) |
| Constant stride mode | `implicitConst`, `packedConst` in observed cases | Constants may use implicit or packed stride representation. `notPackedConst` is removed by `valid()`. | [vktDataGraphTestUtil.cpp#L146-L155](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L146-L155) |
| Binding order | `orderedBindings`, `unorderedBindings` | Keeps the logical resources while changing their descriptor binding numbers. | [vktDataGraphTestUtil.cpp#L96-L114](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L96-L114), [vktDataGraphTosaUtil.hpp#L76-L82](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L76-L82) |
| Tensor tiling | `linearTiling`, `optimalTiling` | Selects the tiling in tensor descriptions for tensor inputs and outputs. Constants remain linear. | [vktDataGraphTestUtil.cpp#L98-L114](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L98-L114), [vktDataGraphTestProvider.cpp#L57-L65](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L57-L65) |
| Sparse constants | `sparseConstants` or no suffix | Requests sparsity hints for constant resources. The implemented convolution classes provide hints for weights and bias. | [vktDataGraphTestProvider.cpp#L108-L138](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L108-L138), [vktDataGraphTosaUtil.hpp#L734-L738](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L734-L738) |

The observed mustpass totals are 2,544 `create_pipeline` cases and 636 `submit_pipeline` cases. The create family adds the two shader input modes and two compiler-control modes to the same generated graph matrix. The submit family uses the graph parameters without those two create-only axes. The counts and prefixes come from [data-graph.txt#L1-L3180](../../../mustpass/main/vk-default/data-graph.txt#L1-L3180), where the basic section is followed by the other data graph families.

The TOSA provider maps supported graph shapes to these implementations:

| Resource and session selection | TOSA graph behavior | Format strings |
|--------------------------------|----------------------|----------------|
| `oneIn_oneOut_noConst_noSession` | One `MAX_POOL2D` operation. Input dimensions are `{1, 8, 16, 4}` and output dimensions are `{1, 4, 8, 4}`. | `i8`, `fp32`, `fp16` |
| `oneIn_oneOut_manyConst_noSession` | One `CONV2D` operation using weights and bias constants. | `i8i8i32`, `fp32fp32fp32`, `fp16fp16fp16` |
| `oneIn_oneOut_noConst_session` | Two `MAX_POOL2D` operations connected through a transient tensor. | `i8`, `fp32`, `fp16` |
| `oneIn_oneOut_manyConst_session` | Two `CONV2D` operations, with a `CAST` between transient formats when the input and output formats differ. | `i8i8i32`, `fp32fp32fp32`, `fp16fp16fp16` |
| `manyIn_manyOut_noConst_noSession` | One `ADD` output and one `SUB` output from two inputs. | `i32`, `fp32`, `fp16` |

These mappings are selected in [vktDataGraphTosaUtil.hpp#L1203-L1275](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1203-L1275). The registered case names preserve the lower-case TOSA token and encode the selected resource axes, for example `dEQP-VK.data_graph.basic.submit_pipeline.tosa_oneIn_oneOut_manyConst_noSession_fp16fp16fp16_implicitIn_implicitOut_implicitConst_orderedBindings_linearTiling`.

## Behavior Parameters

The primary behavioral axis is the registered test family. Its values change the host-side operation being checked.

### `create_pipeline` | Create the pipeline and session

The test obtains the TOSA `DataGraphTest`, creates tensor descriptions for all resources, and creates tensor memory and views for input and output resources. It builds a descriptor-set layout containing tensor bindings, then chains the graph resource descriptions and constant descriptions into `VkDataGraphPipelineCreateInfoARM`. The generated SPIR-V can enter through either the data graph shader-module structure or an ordinary shader-module create-info structure. The test creates the data graph pipeline and a session for that pipeline, and checks both handles with `check<VkPipeline>` and `check<VkDataGraphPipelineSessionARM>`. It returns `pass("test succeeded")` after those checks. See [vktDataGraphBasicTests.cpp#L122-L248](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L122-L248).

### `submit_pipeline` | Dispatch and check tensor outputs

The test creates and initializes every tensor resource. It uploads input data, clears output tensors, and initializes constant host data, including sparsity patterns when requested. It creates a tensor descriptor set, builds the pipeline with tensor and constant resource descriptions, creates a session, records pipeline and descriptor binding commands, dispatches with `cmdDispatchDataGraphARM`, waits for the queue, and verifies each output tensor. See [vktDataGraphBasicTests.cpp#L251-L392](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L251-L392).

The two family values share the same provider, graph generation, feature gates, and parameter pruning. Only `submit_pipeline` reaches device execution and output comparison.

## Shader Analysis

The TOSA provider does not use GLSL or HLSL. For each graph class, CTS constructs SPIR-V assembly text with `TosaSpirv`, assembles it with `spvtools::SpirvTools` using `SPV_ENV_UNIVERSAL_1_6`, validates the binary, and returns that binary to the data graph pipeline. The walkthrough below follows that direct-SPIR-V path for one exact `submit_pipeline` case. The module has a graph entry point rather than a GLSL/HLSL execution-stage shader, so the direct SPIR-V module is shown without inventing a source-language shader or a Vulkan stage label.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.data_graph.basic.submit_pipeline.tosa_manyIn_manyOut_noConst_noSession_fp16_implicitIn_implicitOut_implicitConst_orderedBindings_linearTiling
```

| Parameter choice | Meaning in this representative case |
|------------------|--------------------------------------|
| `submit_pipeline` | Executes the graph, submits it with `cmdDispatchDataGraphARM`, and verifies both output tensors. |
| `manyIn_manyOut_noConst_noSession` | Selects the two-input, two-output `ADD`/`SUB` graph with no constants and no session-memory layer. |
| `fp16`, `orderedBindings`, `linearTiling` | Uses four rank-4 FP16 tensors with dimensions `{1, 8, 16, 4}`, bindings `0..3` in resource order, and linear tensor tiling. |

#### Purpose

This module describes a two-input data graph whose first output is the TOSA `ADD` result and whose second output is the TOSA `SUB` result. It checks the graph operation and its tensor interface after the host submits the graph and compares both outputs with the corresponding reference calculations.

#### Structural Design

| Graph phase | Direct SPIR-V structure | Role |
|------------|-------------------------|------|
| Interface | `OpTypeTensorARM` and `OpTypeGraphARM` describe four FP16 tensors, two inputs, and two outputs. | Defines the graph's tensor signature and rank-4 shape. |
| Entry point | `OpGraphEntryPointARM` connects `main` to the graph object and its four resource variables. | Exposes the graph to the Vulkan data graph pipeline. |
| Inputs | Two `OpGraphInputARM` instructions select input indices `0` and `1`. | Supplies the two input tensors to the graph. |
| Operations | `OpExtInst` imports `TOSA.001000.1` and emits `ADD` and `SUB`. | Produces the two graph results. |
| Outputs | Two `OpGraphSetOutputARM` instructions map the results to output indices `0` and `1`. | Connects operation results to the output tensors checked by CTS. |

#### Shader Code

This representative case uses direct SPIR-V generated by the CTS `TosaSpirv` builder; it does not use GLSL or HLSL. The graph-specific implementation adds each resource, emits `ADD` and `SUB`, sets both outputs, calls `bake()`, obtains the assembled source with `source()`, and validates the resulting binary before returning it. The generator definitions are in [vktDataGraphTosaSpirv.cpp#L259-L420](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaSpirv.cpp#L259-L420) and [vktDataGraphTosaSpirv.cpp#L445-L507](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaSpirv.cpp#L445-L507); the exact `ADD`/`SUB` graph path and SPIR-V Tools validation are in [vktDataGraphTosaUtil.hpp#L121-L158](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L121-L158).

#### Additional Info

- The four resources use the exact source dimensions `{1, 8, 16, 4}` and FP16 format from `DataGraphTestTosaAddSub<VK_FORMAT_R16_SFLOAT>`; ordered bindings leave them at bindings `0`, `1`, `2`, and `3`. [vktDataGraphTosaUtil.hpp#L63-L82](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L63-L82)
- The generated module declares `GraphARM`, `TensorsARM`, `Float16`, `VulkanMemoryModel`, `SPV_ARM_graph`, `SPV_ARM_tensors`, and `SPV_KHR_vulkan_memory_model`, matching the data graph and tensor instructions emitted by the generator.
- The displayed artifact was generated by compiling this repository's `TosaSpirv` implementation with the selected resource setup, then assembled for `spv1.6`, validated with `spirv-val --target-env spv1.6`, and disassembled with `spirv-dis`. It is a generated artifact, not hand-authored assembly.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation graph | The no-constant many-input/many-output selection emits `ADD` and `SUB`; one-input selections emit `MAX_POOL2D` or `CONV2D`, and session-memory selections emit two graph operations. | [DataGraphTestProviderTosa::getDataGraphTest](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1243-L1275) |
| Tensor format and shape | Format selection changes the `OpTypeTensorARM` element type; resource-specific graph classes also change tensor dimensions and operation attributes. | [TosaSpirv::typeTensor](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaSpirv.cpp#L259-L288), [TOSA graph constructors](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L63-L116) |
| Resource binding | `shuffleBindings` changes `Binding` decorations and host descriptor writes without changing the logical graph operations. | [TosaSpirv::spirvGraphParam](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaSpirv.cpp#L311-L330), [DataGraphTestTosaAddSub binding setup](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L76-L82) |
| Session memory | The session variant selects a two-layer graph and therefore emits an additional operation and transient tensor type. | [DataGraphTestProviderTosa::getDataGraphTest](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1257-L1267) |

#### SPIR-V

- Status: generated and validated
- Source: CTS-generated direct SPIR-V from `DataGraphTestTosaAddSub<VK_FORMAT_R16_SFLOAT>::spirvBinary`
- Stage: data graph entry point `main`
- Target SPIRV version: spv1.6

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.6
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 23
; Schema: 0
               OpCapability GraphARM
               OpCapability TensorsARM
               OpCapability Int8
               OpCapability Int16
               OpCapability Int64
               OpCapability Float16
               OpCapability Shader
               OpCapability VulkanMemoryModel
               OpCapability Matrix
               OpExtension "SPV_ARM_graph"
               OpExtension "SPV_ARM_tensors"
               OpExtension "SPV_KHR_vulkan_memory_model"
          %1 = OpExtInstImport "TOSA.001000.1"
               OpMemoryModel Logical Vulkan
               OpName %main_arg_0 "main_arg_0"
               OpName %main_arg_1 "main_arg_1"
               OpName %main_res_0 "main_res_0"
               OpName %main_res_1 "main_res_1"
               OpDecorate %main_arg_0 Binding 0
               OpDecorate %main_arg_0 DescriptorSet 0
               OpDecorate %main_arg_1 Binding 1
               OpDecorate %main_arg_1 DescriptorSet 0
               OpDecorate %main_res_0 Binding 2
               OpDecorate %main_res_0 DescriptorSet 0
               OpDecorate %main_res_1 Binding 3
               OpDecorate %main_res_1 DescriptorSet 0
       %half = OpTypeFloat 16
       %uint = OpTypeInt 32 0
     %uint_4 = OpConstant %uint 4
     %uint_1 = OpConstant %uint 1
     %uint_8 = OpConstant %uint 8
    %uint_16 = OpConstant %uint 16
     %uint_0 = OpConstant %uint 0
%_arr_uint_uint_4 = OpTypeArray %uint %uint_4
         %14 = OpConstantComposite %_arr_uint_uint_4 %uint_1 %uint_8 %uint_16 %uint_4
         %15 = OpTypeTensorARM %half %uint_4 %14
%_ptr_UniformConstant_15 = OpTypePointer UniformConstant %15
 %main_arg_0 = OpVariable %_ptr_UniformConstant_15 UniformConstant
 %main_arg_1 = OpVariable %_ptr_UniformConstant_15 UniformConstant
 %main_res_0 = OpVariable %_ptr_UniformConstant_15 UniformConstant
 %main_res_1 = OpVariable %_ptr_UniformConstant_15 UniformConstant
         %17 = OpTypeGraphARM 2 %15 %15 %15 %15
               OpGraphEntryPointARM %18 "main" %main_arg_0 %main_arg_1 %main_res_0 %main_res_1
         %18 = OpGraphARM %17
         %19 = OpGraphInputARM %15 %uint_0
         %20 = OpGraphInputARM %15 %uint_1
         %21 = OpExtInst %15 %1 ADD %19 %20
         %22 = OpExtInst %15 %1 SUB %19 %20
               OpGraphSetOutputARM %21 %uint_0
               OpGraphSetOutputARM %22 %uint_1
               OpGraphEndARM
```

</details>

## Runtime Execution and Result Checking

- The provider constructs `ResourceInformation` entries for input, output, and constant resources. Inputs and outputs are tensor resources; constants are host data with an identifier and optional sparsity hints. [vktDataGraphTestUtil.hpp#L260-L295](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L260-L295)
- The submit path creates `VkTensorDescriptionARM` values from the selected tiling, format, dimensions, and strides, then allocates `TensorWithMemory` and a tensor view for every input and output. [vktDataGraphBasicTests.cpp#L263-L280](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L263-L280)
- `initData` uploads inputs and clears outputs. For convolution graphs it fills weights and bias host arrays and passes requested sparsity information to the fill helper. Constants do not receive tensor allocations in this path. [vktDataGraphBasicTests.cpp#L282-L289](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L375-L390), [vktDataGraphTosaUtil.hpp#L809-L843](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L809-L843)
- The descriptor set contains only `VK_DESCRIPTOR_TYPE_TENSOR_ARM` bindings. The update writes each tensor view at its selected binding, including the shuffled binding layouts. [vktDataGraphBasicTests.cpp#L292-L325](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L292-L325)
- The pipeline wrapper adds tensor descriptions with descriptor-set and binding indices, and adds constants with their descriptions, host pointers, identifiers, and sparsity hints. [vktDataGraphBasicTests.cpp#L327-L346](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L327-L346)
- The command buffer binds the data graph pipeline and tensor descriptor set, dispatches one `cmdDispatchDataGraphARM` operation with the created session, ends recording, submits to the universal queue, and waits for completion. [vktDataGraphBasicTests.cpp#L355-L374](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L355-L374)
- For each output resource, the provider downloads the tensor into a strided host view, computes the expected result with the matching TOSA reference implementation, and calls `verifyTensor`. The checks are `MAX_POOL2D`, two-layer max-pool, `CONV2D`, two-layer convolution with its cast, or `ADD` and `SUB`, depending on the selected provider family. [vktDataGraphTosaUtil.hpp#L204-L232](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L204-L232), [vktDataGraphTosaUtil.hpp#L405-L426](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L405-L426), [vktDataGraphTosaUtil.hpp#L853-L878](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L853-L878), [vktDataGraphTosaUtil.hpp#L1135-L1165](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1135-L1165)
- Floating-point tensors use an SNR threshold of 140 dB when the noise power is nonzero. Integer and other non-floating tensor types use exact element comparison and report the first differing index. [vktDataGraphTestUtil.hpp#L381-L425](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L381-L425)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `create_pipeline` | Pipeline or session creation rejected the generated graph, resource descriptions, shader input form, or compiler-control chain. |
| `submit_pipeline` | Dispatch did not produce the TOSA reference output for the selected resource layout, binding arrangement, tiling, stride, constant, or session-memory case. |

### Cause Analysis

#### Pipeline and session creation failures

**Possible failure symptoms:** The pipeline handle or session handle check fails, or pipeline creation reports an error before the test reaches submission.

**Possible implementation causes:** The source identifies the failing operation as data graph pipeline or session creation, but it does not attribute the error to a particular driver, compiler, or hardware mechanism. Investigate the generated graph resource descriptions, shader-module path, compiler-control chain, and implementation support for the selected feature combination.

#### Dispatch and tensor result failures

**Possible failure symptoms:** Queue submission fails, or an output tensor differs from the reference. Floating-point output can report SNR below 140 dB. Integer output can report the first index whose value differs from the reference.

**Possible implementation causes:** The source narrows the check to the dispatched graph output and its host-side reference calculation. Investigate tensor binding and descriptor updates, tensor dimensions, explicit strides, tiling, constant data and sparsity hints, graph execution, synchronization, or the TOSA operation implementation. The source does not establish which implementation component is responsible for a particular mismatch.

## Case Pruning

### Requirement-based pruning

- `TestParams::checkSupport()` requires `VK_ARM_data_graph` and `VK_ARM_tensors`. It queries `VkPhysicalDeviceDataGraphFeaturesARM` and `VkPhysicalDeviceTensorFeaturesARM` and requires `dataGraph`, `dataGraphShaderModule`, `tensors`, and `shaderTensorAccess`. [vktDataGraphTestUtil.hpp#L219-L251](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L219-L251)
- If any selected resource uses non-packed strides, support also requires `tensorNonPacked`. [vktDataGraphTestUtil.hpp#L253-L256](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L253-L256)
- The provider rejects a case when requested constants are absent, a `manyIn` or `manyOut` selection has fewer than two matching resources, tensor-resource tiling differs from the selected tiling, or a resource's packed-stride state differs from the selected mode. Sparse-constant requests also require sparsity hints whose dimensions and group sizes fit the tensor shapes. [vktDataGraphTestProvider.cpp#L37-L138](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L37-L138)

These skips mean the selected case is unsupported or invalid for the current implementation or generated resource set. They are not output mismatches.

### Design-based pruning

- `getTestParamsVariations()` removes optimal-tiling combinations with explicit strides because the source states that optimal tiling does not support them. [vktDataGraphTestUtil.cpp#L139-L145](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L139-L145)
- Constant strides cannot be `notPacked`; constants without a graph constant, inputs without graph inputs, and sparse constants without graph constants are removed. [vktDataGraphTestUtil.cpp#L146-L165](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L146-L165)
- Resource cardinality generation omits no-output graphs because every graph must have at least one output. The provider then exposes only the five TOSA graph/cardinality/session combinations listed above. [vktDataGraphTestUtil.hpp#L127-L132](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L127-L132), [vktDataGraphTosaUtil.hpp#L1206-L1240](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1206-L1240)

These exclusions define the intended generated matrix. They do not indicate a failed Vulkan operation.

## Key Takeaways

- `create_pipeline` isolates pipeline and session construction, including the two shader input forms and optional empty compiler-control chain.
- `submit_pipeline` exercises the complete path from TOSA-generated graph and tensor resources through descriptor binding, dispatch, queue completion, and output comparison.
- The provider uses session memory, resource cardinality, and format strings to select distinct TOSA graphs, including one- and two-layer max-pool, one- and two-layer convolution, and two-output add/sub.
- Strides, binding order, tiling, constants, and sparsity are part of the checked resource contract. The result checker reads the selected output layout rather than comparing an unrelated packed buffer.
- A failure identifies either creation/session setup or a dispatch/output mismatch. The source does not, by itself, identify the responsible implementation layer.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `basicTestsGroup` | [vktDataGraphBasicTests.cpp#L423-L427](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L423-L427) | Registers the two direct test families. |
| `createPipelineGroup` and `submitPipelineGroup` | [vktDataGraphBasicTests.cpp#L397-L421](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L397-L421) | Expands create-only and shared generated parameter axes. |
| `createPipelineTest` | [vktDataGraphBasicTests.cpp#L122-L248](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L122-L248) | Builds and checks a pipeline and session. |
| `submitPipelineTest` | [vktDataGraphBasicTests.cpp#L251-L392](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L251-L392) | Builds, dispatches, waits for, and verifies a graph. |
| `TestParams::valid` and `getTestParamsVariations` | [vktDataGraphTestUtil.cpp#L139-L219](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L139-L219) | Defines generated parameter pruning and format expansion. |
| `TestParams::checkSupport` | [vktDataGraphTestUtil.hpp#L219-L256](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L219-L256) | Defines the extension and feature gates. |
| `DataGraphTestProviderTosa` | [vktDataGraphTosaUtil.hpp#L1203-L1275](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1203-L1275) | Maps resource and session parameters to TOSA graph classes. |
| `DataGraphTestProvider::validate` | [vktDataGraphTestProvider.cpp#L37-L138](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L37-L138) | Checks provider/resource consistency before execution. |
| `DataGraphTest::verifyTensor` | [vktDataGraphTestUtil.hpp#L381-L425](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L381-L425) | Defines floating-point SNR and non-floating exact comparison. |
| `TosaSpirv` graph construction | [vktDataGraphTosaSpirv.cpp#L259-L420](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaSpirv.cpp#L259-L420) | Generates graph resource declarations and TOSA SPIR-V source. |
| TOSA graph implementations | [vktDataGraphTosaUtil.hpp#L46-L1275](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L46-L1275) | Defines resource shapes, generated operations, initialization, and reference checks. |
| Basic mustpass prefixes and generated cases | [data-graph.txt#L1-L3180](../../../mustpass/main/vk-default/data-graph.txt#L1-L3180) | Confirms the registered `create_pipeline` and `submit_pipeline` case families. |
