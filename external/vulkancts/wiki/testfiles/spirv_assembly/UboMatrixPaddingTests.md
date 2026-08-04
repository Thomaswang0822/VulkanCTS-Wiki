## Overview

**Core question:** Does a SPIR-V shader read a padded, column-major `mat2x2` array from a uniform buffer at the offsets specified by `ArrayStride 32` and `MatrixStride 16`?

- [`vktSpvAsmUboMatrixPaddingTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L46-L293) implements the `ubo_padding` families under both `spirv_assembly.instruction.compute` and `spirv_assembly.instruction.graphics`.
- Every leaf reads 128 `mat2x2` values from one UBO and writes the four meaningful matrix scalars into a `vec4` output buffer. The compute runner byte-compares that readback with the CPU-generated values; graphics also samples rendered corner colors and uses its default resource-comparison rules.
- The host stores each matrix as two padded `vec4` slots: `(x, y, 0, 0)` followed by `(z, w, 0, 0)`. The zero lanes are deliberately not part of the expected matrix result.
- The six leaves vary only execution pipeline and graphics shader stage. The matrix type, buffer layout, data count, and CPU oracle are fixed.

## Background Knowledge

### Matrix shape versus matrix memory layout

The SPIR-V type is `OpTypeMatrix %v2float 2`, which is a `mat2x2`: two `vec2` columns, four useful 32-bit floating-point values total. Its type alone does not specify where the columns occur in a buffer. The UBO decorations do that:

| Decoration | Value | Consequence for one `mat2x2` |
|------------|-------|------------------------------|
| `ColMajor` | member layout | The first matrix index selects a column. |
| `MatrixStride` | 16 bytes | Column 0 starts at byte 0 and column 1 at byte 16. Each `vec2` uses 8 bytes, leaving 8 bytes of padding after it. |
| `ArrayStride` | 32 bytes | Matrix `i + 1` starts 32 bytes after matrix `i`: two 16-byte column slots. |

For matrix `i`, its four shader reads therefore resolve to these byte offsets from the beginning of the UBO member:

```text
matrix i, column 0, component 0 -> i * 32 +  0  -> x
matrix i, column 0, component 1 -> i * 32 +  4  -> y
matrix i, column 1, component 0 -> i * 32 + 16  -> z
matrix i, column 1, component 1 -> i * 32 + 20  -> w
```

Offsets `i * 32 + 8`, `+12`, `+24`, and `+28` are the padding lanes represented by the host-side zero values. The shader never intentionally reads them.

### Bound resources

| Resource | Descriptor | SPIR-V declaration | Host payload | Device access |
|----------|------------|--------------------|--------------|---------------|
| Input UBO | set 0, binding 0 | `Uniform`, `Block` | 256 `Vec4` values: two padded slots for each of 128 matrices | Reads matrix elements. |
| Output buffer | set 0, binding 1 | `Uniform`, `BufferBlock` in the authored assembly | 128 expected `Vec4` values | Writes `(x, y, z, w)` for each matrix; CTS reads it back for comparison. |

The compute path creates the input resource as `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER`; the graphics path does the same explicitly before creating its stage cases. The graphics output resource is constructed as `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER`.

### Compute and graphics forms

The compute shader has `LocalSize 1 1 1`, dispatches 128 workgroups in the x dimension, obtains `idx` from `GlobalInvocationId.x`, and handles one matrix per invocation.

The graphics function uses a signed function-local loop counter. Each execution of the selected custom graphics stage iterates from 0 through 127 and performs the same four loads and stores for each index, then returns its input parameter. The output-buffer writes are the layout-specific observation; the default graphics runner also checks rendered corner colors produced by the surrounding graphics pipeline.

## Registration Hierarchy

The factories create an `ubo_padding` group, and the instruction-suite parent attaches the compute and graphics factories separately ([parent attachment](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21399), [graphics parent attachment](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21498)). The default Vulkan and Vulkan SC mustpass inventories contain these same six leaves.

```text
spirv_assembly.instruction.compute.ubo_padding
└── mat2x2

spirv_assembly.instruction.graphics.ubo_padding
├── mat2x2_vert
├── mat2x2_tessc
├── mat2x2_tesse
├── mat2x2_geom
└── mat2x2_frag
```

The source registers these leaves in [`addComputeUboMatrixPaddingTest()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L46-L146) and [`addGraphicsUboMatrixPaddingTest()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L149-L273). The group factories are [`createUboMatrixPaddingComputeGroup()` and `createUboMatrixPaddingGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L278-L293).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Source evidence |
|-----------|-------------------|----------------------|-----------------|
| Execution pipeline | `compute`, `graphics` | Chooses the standalone compute module or shared graphics fragments. | [Group factories](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L278-L293) |
| Graphics stage | `_vert`, `_tessc`, `_tesse`, `_geom`, `_frag` | Places the graphics test function in vertex, tessellation-control, tessellation-evaluation, geometry, or fragment stage. | [Stage creation](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L254-L273) |
| Matrix type | `mat2x2` | Fixed two-column, two-row floating-point matrix. No other shape is registered. | [Compute type declarations](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L96-L101) |
| Matrix layout | `ColMajor`, `MatrixStride 16`, `ArrayStride 32` | Fixed padded UBO layout under test. | [Compute decorations](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L67-L73), [graphics decorations](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L191-L202) |
| Element count | 128 | Fixed number of matrix/output pairs. | [Compute setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L49-L50), [graphics setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L151-L153) |

The primary behavior parameter is execution context: compute processes one element per invocation, while graphics places the same read/write operation in each of five graphics stages. The layout is intentionally constant, so a failing stage distinguishes the affected pipeline/compiler path rather than a different matrix layout variant.

## Behavior Parameters

### `mat2x2`: compute one matrix per invocation

The compute case reads `GlobalInvocationId.x` as `idx`. Four `OpAccessChain` operations select `dataInput[0][idx][column][component]`; each loaded scalar is stored in output vector element `idx` at component 0, 1, 2, or 3. With 128 `x` workgroups and local size 1, every matrix element is independently processed once.

### `mat2x2_<stage>`: graphics loop in a selected stage

The five graphics leaves share `pre_main`, decoration, and `testfun` fragments. The `testfun` loop begins with `i = 0`, continues while `i < 128`, performs the four scalar copies, increments `i`, and returns only after all output elements are written. `createTestForStage` selects the graphics stage and adds its suffix to the test name.

The matrix-index order is the same as compute:

```text
input[i][column 0][row 0] -> output[i].x
input[i][column 0][row 1] -> output[i].y
input[i][column 1][row 0] -> output[i].z
input[i][column 1][row 1] -> output[i].w
```

## Shader Analysis

The test authors the SPIR-V assembly directly in C++ rather than generating GLSL or HLSL. The representative case below is the compute `mat2x2` leaf. It includes the complete layout declaration and its four layout-sensitive loads; the source contains no distinct shader behavior for another matrix shape.

### Representative Shader Walkthrough: compute `mat2x2`

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.ubo_padding.mat2x2
```

#### Purpose

The module verifies that the UBO address calculation implicit in `OpAccessChain` applies the member's `ColMajor`, `MatrixStride 16`, and array `ArrayStride 32` decorations. The output stores omit the padding lanes, so an incorrect column stride, array stride, or matrix orientation changes one or more components of the compared `vec4`.

#### Structural Design

| Phase | Assembly behavior |
|-------|-------------------|
| Invocation index | Reads `%id`, the `GlobalInvocationId`, and takes component 0 as the matrix index. |
| Output type | Declares an array of 128 `v4float` values in a legacy `Uniform`/`BufferBlock` output buffer. |
| Input type | Declares an array of 128 `mat2v2float` values in a `Uniform`/`Block` UBO. |
| Layout | Decorates the matrix array with `ArrayStride 32` and its enclosing member with `ColMajor` and `MatrixStride 16`. |
| Copy | Loads column 0 components 0/1 and column 1 components 0/1, then stores them at output vector components 0–3. |

#### Source Code

<details>
<summary>Click to expand CTS-authored SPIR-V assembly for the representative compute case</summary>

```llvm
OpCapability Shader
%1 = OpExtInstImport "GLSL.std.450"
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %main "main" %id
OpExecutionMode %main LocalSize 1 1 1
OpSource GLSL 430
OpDecorate %id BuiltIn GlobalInvocationId
OpDecorate %_arr_v4 ArrayStride 16
OpMemberDecorate %Output 0 Offset 0
OpDecorate %Output BufferBlock
OpDecorate %dataOutput DescriptorSet 0
OpDecorate %dataOutput Binding 1
OpDecorate %_arr_mat2v2 ArrayStride 32
OpMemberDecorate %Input 0 ColMajor
OpMemberDecorate %Input 0 Offset 0
OpMemberDecorate %Input 0 MatrixStride 16
OpDecorate %Input Block
OpDecorate %dataInput DescriptorSet 0
OpDecorate %dataInput Binding 0
%void = OpTypeVoid
%3 = OpTypeFunction %void
%u32 = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %u32
%v3uint = OpTypeVector %u32 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%id = OpVariable %_ptr_Input_v3uint Input
%i32 = OpTypeInt 32 1
%int_0 = OpConstant %i32 0
%int_1 = OpConstant %i32 1
%uint_0 = OpConstant %u32 0
%uint_1 = OpConstant %u32 1
%uint_2 = OpConstant %u32 2
%uint_3 = OpConstant %u32 3
%_ptr_Input_uint = OpTypePointer Input %u32
%f32 = OpTypeFloat 32
%v4float = OpTypeVector %f32 4
%uint_128 = OpConstant %u32 128
%_arr_v4 = OpTypeArray %v4float %uint_128
%Output = OpTypeStruct %_arr_v4
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
%dataOutput = OpVariable %_ptr_Uniform_Output Uniform
%v2float = OpTypeVector %f32 2
%mat2v2float = OpTypeMatrix %v2float 2
%_arr_mat2v2 = OpTypeArray %mat2v2float %uint_128
%Input = OpTypeStruct %_arr_mat2v2
%_ptr_Uniform_Input = OpTypePointer Uniform %Input
%dataInput = OpVariable %_ptr_Uniform_Input Uniform
%_ptr_Uniform_float = OpTypePointer Uniform %f32
%main = OpFunction %void None %3
%5 = OpLabel
%i = OpVariable %_ptr_Function_uint Function
%14 = OpAccessChain %_ptr_Input_uint %id %uint_0
%15 = OpLoad %u32 %14
OpStore %i %15
%idx = OpLoad %u32 %i
%34 = OpAccessChain %_ptr_Uniform_float %dataInput %int_0 %idx %int_0 %uint_0
%35 = OpLoad %f32 %34
%36 = OpAccessChain %_ptr_Uniform_float %dataOutput %int_0 %idx %uint_0
OpStore %36 %35
%40 = OpAccessChain %_ptr_Uniform_float %dataInput %int_0 %idx %int_0 %uint_1
%41 = OpLoad %f32 %40
%42 = OpAccessChain %_ptr_Uniform_float %dataOutput %int_0 %idx %uint_1
OpStore %42 %41
%46 = OpAccessChain %_ptr_Uniform_float %dataInput %int_0 %idx %int_1 %uint_0
%47 = OpLoad %f32 %46
%49 = OpAccessChain %_ptr_Uniform_float %dataOutput %int_0 %idx %uint_2
OpStore %49 %47
%52 = OpAccessChain %_ptr_Uniform_float %dataInput %int_0 %idx %int_1 %uint_1
%53 = OpLoad %f32 %52
%55 = OpAccessChain %_ptr_Uniform_float %dataOutput %int_0 %idx %uint_3
OpStore %55 %53
OpReturn
OpFunctionEnd
```

</details>

#### Additional Info

- This is the direct assembly string assembled by [`addComputeUboMatrixPaddingTest()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L54-L127). The legacy `Uniform` plus `BufferBlock` declarations are intentional source content.
- The source's graphics fragments reproduce the same `mat2x2` UBO type and decorations, with a loop surrounding the four accesses ([fragments](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L178-L250)).
- The representative module is a SPIR-V 1.0-style layout. Assembling or validating the displayed code should use a target environment compatible with `BufferBlock`; such a tool run checks the documentation extraction, not device conformance execution.

#### Parameter Variation Summary

| Parameter dimension | Variation from the representative assembly | Evidence |
|---------------------|--------------------------------------------|----------|
| Execution pipeline | Graphics replaces the standalone compute entry-point body with generated graphics fragments and a 128-iteration function loop. | [Graphics test function](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L204-L250) |
| Shader stage | The graphics utility inserts the shared function into vertex, tessellation-control, tessellation-evaluation, geometry, or fragment stage. | [Stage registrations](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L254-L273) |
| Matrix layout and count | No registered variation: all six leaves retain `mat2x2`, 128 elements, `ColMajor`, `MatrixStride 16`, and `ArrayStride 32`. | [Compute setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L49-L146), [graphics setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L151-L252) |

The displayed module is CTS-authored SPIR-V assembly extracted from the source template, not reconstructed GLSL or HLSL. Audit-time semantic validation used `spirv-as`, `spirv-val`, and `spirv-dis`; the disassembly is intentionally not published as a duplicate `#### SPIR-V` subsection.

## Runtime Execution and Result Checking

1. The host seeds a `de::Random` generator from the group name and creates 128 random `Vec4` values.
2. For each expected vector `v = (x, y, z, w)`, it appends `(x, y, 0, 0)` and `(z, w, 0, 0)` to the input UBO data. It keeps the original `v` in `outputData` as the expected output.
3. The compute case dispatches 128 x-direction workgroups. In a graphics case, each execution of the selected custom stage runs the function that loops over all 128 indices.
4. The shader copies only the four non-padding UBO values into one output `vec4` per index.
5. `SpvAsmComputeShaderCase` byte-compares the complete output-buffer readback with the expected `outputData`. The graphics utility first checks rendered corner colors and then compares the output resource: the fragment path accepts exact values or up to one ULP, while the vertex, tessellation, and geometry fallback may also accept an expected finite float plus a non-negative integer to accommodate tests whose shaders execute repeatedly.

The test has no shader-side boolean verdict and does not compare the input padding lanes. Its layout-specific observation is the output buffer constructed from the four matrix-component loads; graphics has the additional, generic rendered-image probes.

## Failure Meaning

### Failure Cause Mapping

| Failing behavior parameter | What the failing output establishes | Plausible implementation area |
|----------------------------|--------------------------------------|-------------------------------|
| `mat2x2` compute | The runner reached readback and found at least one byte different from the expected output resource. | Compute shader/module/pipeline setup, decorated UBO address calculation, matrix component indexing, output-buffer store, or host/device synchronization/readback. |
| `mat2x2_vert`, `mat2x2_tessc`, `mat2x2_tesse`, or `mat2x2_geom` | A graphics module/pipeline step, rendered corner probe, or default resource comparison failed. For a resource mismatch, the non-fragment fallback is not strict equality: it can accept a finite expected float plus a non-negative integer. | The selected graphics-stage or surrounding pipeline path; only a qualifying resource mismatch is evidence consistent with UBO layout handling or storage-buffer writes. |
| `mat2x2_frag` | A graphics module/pipeline step, rendered corner probe, or fragment resource comparison failed. The latter allows exact output or at most one ULP. | The fragment-stage or surrounding pipeline path; only a qualifying resource mismatch is evidence consistent with UBO layout handling or storage-buffer writes under the fragment-store feature path. |

### Cause Analysis

A component shift such as receiving a padding zero where `z` or `w` is expected is consistent with incorrect application of `MatrixStride 16`. Values taken from a neighboring matrix are consistent with incorrect `ArrayStride 32`. Swapped or reordered components can be consistent with column-major indexing or access-chain handling. The CTS source cannot, by itself, localize a particular failure to a compiler, driver, descriptor, synchronization, or memory-layout implementation component; graphics failures can also arise from generic pipeline setup or image probes.

## Case Pruning

### Requirement-based pruning

- The compute leaf does not set an extra `VulkanFeatures` request in this file.
- Before registering the vertex, tessellation-control, tessellation-evaluation, and geometry cases, the graphics builder sets `vertexPipelineStoresAndAtomics = true` and `fragmentStoresAndAtomics = false` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L254-L268)).
- Before registering the fragment case, it sets `vertexPipelineStoresAndAtomics = false` and `fragmentStoresAndAtomics = true` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L270-L273)).
- Tessellation and geometry cases additionally depend on the corresponding graphics stages being available to the graphics test utility.
- The builder supplies no extension list, specialization constants, push constants, or graphics interfaces.

### Design-based pruning

- Only `mat2x2` is tested. The test isolates padding around two-component columns rather than covering every matrix dimension or alternate row-major layouts.
- The count is fixed at 128. It is large enough to exercise repeated array-stride addressing but does not vary at runtime.
- The output stores only the four semantically meaningful matrix scalars. The host initializes padding lanes to zero to establish the intended physical representation, but the oracle does not require a shader to read or preserve them.
- One compute assembly is published because the graphics cases retain the same type, decorations, host data, and four-copy logic; they differ in execution wrapper and selected stage.

## Key Takeaways

- `mat2x2` occupies 32 bytes in this UBO, not the 16 bytes required by four contiguous floats: `MatrixStride 16` inserts 8 bytes after each two-float column.
- The test confirms the four access-chain paths produce `(x, y, z, w)` and do not treat the padding lanes as components or confuse adjacent matrices.
- Compute uses 128 one-element invocations; graphics uses a 128-iteration function in each of five selected stages.
- The stage leaves distinguish pipeline paths while preserving the same UBO layout and expected output data.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Compute builder | [`addComputeUboMatrixPaddingTest()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L46-L146) | Defines the complete compute assembly, 128-element data generation, resource binding, and `mat2x2` leaf. |
| Graphics builder | [`addGraphicsUboMatrixPaddingTest()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L149-L273) | Defines graphics fragments, resources, four-copy loop, feature selections, and five stage leaves. |
| Graphics utility runner | [`defaultCheckSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L3130-L3252), [`runAndVerifyDefaultPipeline()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L3260-L3280), and its result checks ([image](../../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L4600-L4717), [resources](../../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L4719-L4784)) | Establishes graphics-stage availability and feature gates, pipeline execution, corner-color probes, and the stage-dependent default resource comparator. |
| Group factories | [`createUboMatrixPaddingComputeGroup()` and `createUboMatrixPaddingGraphicsGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmUboMatrixPaddingTests.cpp#L278-L293) | Creates the two `ubo_padding` groups. |
| Parent registration | [`vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21399) and [graphics attachment](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21498) | Places the groups below the compute and graphics instruction paths. |
| Default Vulkan inventory | [`mustpass/main/vk-default/spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt#L16208) and [graphics leaves](../../../mustpass/main/vk-default/spirv-assembly.txt#L38934-L38938) | Lists the six `dEQP-VK` leaves. |
| Vulkan SC inventory | [`mustpass/main/vksc-default/spirv-assembly.txt`](../../../mustpass/main/vksc-default/spirv-assembly.txt#L5648) and [graphics leaves](../../../mustpass/main/vksc-default/spirv-assembly.txt#L20759-L20763) | Lists the six corresponding `dEQP-VKSC` leaves. |
