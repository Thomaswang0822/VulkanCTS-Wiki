## Overview

**Core question:** Does robust vertex input access preserve attributes whose checked fetches remain in range and return only permitted values when a draw fetches beyond a bound vertex buffer?

- This page covers the `robustness.vertex_access` test family implemented and registered by [vktRobustnessVertexAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L52-L1297).
- Each case binds vertex-rate and instance-rate data, then deliberately makes one kind of fetch cross or meet the end of a bound vertex buffer.
- The vertex shader copies three fetched attributes into a storage buffer. After accounting for Vulkan's same-binding allowance, the host checks fetches that remain in range against the populated data and classifies out-of-range results using the values allowed by robust vertex input semantics.
- The matrix covers 15 input formats, non-indexed and indexed draws, and six test case leaves. The default mustpass profile contains 90 paths [robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L96874-L96963).

## Background Knowledge

For the shared model of vertex input addressing and robustness contracts, see [Robustness Background Knowledge](../../categories/robustness.md#background-knowledge).

- **Vertex input addressing.** Each vertex input binding has a stride and an input rate. `VK_VERTEX_INPUT_RATE_VERTEX` selects data using the vertex index, while `VK_VERTEX_INPUT_RATE_INSTANCE` uses the instance index. Attribute descriptions select a binding, format, and byte offset [Vertex Input Description](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L324-L382).
- **Robust vertex input reads.** With `robustBufferAccess` enabled, Vulkan checks vertex input reads against the bound vertex buffer range. An out-of-range read can return a value from memory bound to that buffer, zero, or a permitted four-component `(0,0,0,x)` result. If one read is outside the checked range, other reads through the same binding in that shader invocation may also behave as out of range [Robust Buffer Access](../../../../vulkan-docs/src/chapters/shaders.adoc#L1925-L2030).
- **Input extraction.** A vertex format controls component count, scalar type, and conversion before the shader sees the value. The checker therefore handles integer, floating-point, 64-bit, and packed normalized data separately.

## Registration Hierarchy

```text
robustness.vertex_access
├── r32_uint
├── r32_sint
├── r32_sfloat
├── r32g32_uint
├── r32g32_sint
├── r32g32_sfloat
├── r32g32b32_uint
├── r32g32b32_sint
├── r32g32b32_sfloat
├── r32g32b32a32_uint
├── r32g32b32a32_sint
├── r32g32b32a32_sfloat
├── r64_uint
├── r64_sint
└── a2b10g10r10_unorm_pack32
```

Each format intermediate node contains `draw` and `draw_indexed`. Each of those nodes contains three executable leaves [registration](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1190-L1297), [mustpass](../../../mustpass/main/vk-default/robustness.txt#L96874-L96963).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Vertex input format | `r32_uint`, `r32_sint`, `r32_sfloat`, `r32g32_uint`, `r32g32_sint`, `r32g32_sfloat`, `r32g32b32_uint`, `r32g32b32_sint`, `r32g32b32_sfloat`, `r32g32b32a32_uint`, `r32g32b32a32_sint`, `r32g32b32a32_sfloat`, `r64_uint`, `r64_sint`, `a2b10g10r10_unorm_pack32` | Changes the shader input/output types, component count, buffer stride, and host comparison path. | [`vertexFormats`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1258-L1287) |
| Draw mode | `draw`, `draw_indexed` | Chooses sequential vertex indices or an explicit index buffer containing valid and large indices. | [`createDrawTests()` and `createDrawIndexedTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1190-L1256) |
| Non-indexed test case leaf | `vertex_out_of_bounds`, `vertex_incomplete`, `instance_out_of_bounds` | Chooses which bound vertex buffer range or record boundary the draw exceeds. | [`createDrawTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1202-L1224) |
| Indexed test case leaf | `last_index_out_of_bounds`, `indices_out_of_bounds`, `triangle_out_of_bounds` | Chooses where indices `100`, `101`, and `102` appear among valid indices. | [`s_indexConfigs`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L421-L435), [`createDrawIndexedTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1227-L1256) |
| Input rate | `VK_VERTEX_INPUT_RATE_VERTEX`, `VK_VERTEX_INPUT_RATE_INSTANCE` | Locations 0 and 1 share the vertex-rate binding. Location 2 uses the instance-rate binding. | [binding and attribute descriptions](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L541-L589) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. The same six leaves repeat for every registered format, split between the `draw` and `draw_indexed` intermediate nodes.

### `vertex_out_of_bounds` — sequential vertex fetches cross the buffer end

The host creates six complete vertex records but draws nine vertices. The first six vertex indices address populated data; the final three make locations 0 and 1 fetch beyond the vertex-rate buffer [non-indexed configurations](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1202-L1212).

### `vertex_incomplete` — the vertex-rate buffer ends inside a record

The vertex-rate buffer contains only one selected-format value, which is half of the two-attribute record consumed from binding 0, and the draw requests three vertices. Location 0's bytes fit, but location 1's do not; because both reads use binding 0, the checker permits both to behave as out of range [same-binding classification](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L920-L931), [robust vertex input rule](../../../../vulkan-docs/src/chapters/shaders.adoc#L1956-L1960).

### `instance_out_of_bounds` — later instances exceed instance-rate data

The vertex-rate buffer has enough data for the draw, but the instance-rate buffer holds one element while the command draws three instances. Location 2 is valid for the first instance and outside the checked range for later instances [non-indexed configurations](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1202-L1212).

### `last_index_out_of_bounds` — one final indexed fetch is outside the range

The index sequence is `0, 1, 2, 3, 4, 100`. It keeps the first five fetches in range and places one out-of-range fetch at the end [indexed patterns](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L421-L435).

### `indices_out_of_bounds` — valid and invalid indices alternate

The index sequence is `0, 100, 2, 101, 3, 102`. It interleaves several out-of-range fetches with valid fetches instead of placing them in one contiguous run [indexed patterns](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L421-L435).

### `triangle_out_of_bounds` — one primitive uses only invalid vertex indices

The index sequence is `100, 101, 102, 3, 4, 5`. The first triangle fetches all vertex-rate attributes out of range, while the second triangle remains in range [indexed patterns](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L421-L435).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.robustness.vertex_access.r32_uint.draw.vertex_out_of_bounds
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `r32_uint` | Uses one 32-bit unsigned component per attribute, which keeps the capture logic visible without vector, packed, or 64-bit syntax. |
| `draw` | Uses sequential vertex indices and no index buffer. |
| `vertex_out_of_bounds` | Provides six complete vertex records and launches nine vertices, so the last three invocations fetch locations 0 and 1 beyond binding 0. |
| One instance | Keeps location 2 in range and isolates the vertex-rate boundary. |

#### Purpose

The shader captures two vertex-rate attributes and one instance-rate attribute in an SSBO. The host uses those captured values to check that the valid records survive unchanged and the final out-of-range records contain permitted robust results.

#### Structural Design

| Shader input or output | Source | Role in this case |
|------------------------|--------|-------------------|
| `attr0`, `attr1` | binding 0, vertex rate | Two adjacent values in each record; records for vertex indices 6 through 8 are outside the six-record buffer. |
| `attr2` | binding 1, instance rate | One in-range value shared by the single instance. |
| `vertexNum` | binding 2, vertex rate | Selects a stable SSBO slot for each executed vertex. |
| `outData[27]` | set 0, binding 0 | Stores three observed values for each of nine vertices. |
| `gl_Position` | fixed shader value | Completes vertex processing; rendered pixels do not determine the verdict. |

#### Shader Code

```glsl
#version 310 es
precision highp float;

/// Locations 0 and 1 come from binding 0 at vertex rate. This case has six complete records,
/// while the draw launches nine vertices.
layout(location = 0) in uint attr0;
layout(location = 1) in uint attr1;

/// Location 2 comes from binding 1 at instance rate. Its only value stays in range in this case.
layout(location = 2) in uint attr2;

/// Binding 2 supplies a stable output slot for each executed vertex. It is bookkeeping input,
/// not a robust-access result.
layout(location = 3) in int vertexNum;

/// Set 0, binding 0 is a host-visible SSBO with three captured values for each of nine vertices.
layout(set = 0, binding = 0, std430) buffer outBuffer
{
    uint outData[27];
};

void main (void)
{
    /// Capture both vertex-rate attributes and the instance-rate attribute for host checking.
    outData[(gl_InstanceIndex * 27) + (vertexNum * 3 + 0)] = attr0;
    outData[(gl_InstanceIndex * 27) + (vertexNum * 3 + 1)] = attr1;
    outData[(gl_InstanceIndex * 27) + (vertexNum * 3 + 2)] = attr2;

    /// Rasterized position is irrelevant because the host judges the SSBO, not the color attachment.
    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
}
```

#### Additional Info

- The fragment shader writes constant white for every case. It does not carry the tested data, so the walkthrough omits it [fragment shader generation](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L357-L365).
- The generator computes the output array length from vertex count, instance count, component count, and three tested attributes [vertex shader generation](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L271-L353).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Vertex input format | Changes scalar or vector input declarations, output scalar type, component stores, extensions for 64-bit input, and output array length. | [format-dependent shader generation](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L271-L355) |
| Test case leaf | Changes the generated output array length through vertex and instance counts. The capture statements keep the same form. | [non-indexed case parameters](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1202-L1222) |
| Draw mode | Indexed cases use the same shader generator; host-side index data changes which vertex-rate records feed `attr0` and `attr1`. | [indexed construction](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L421-L488) |

#### SPIR-V

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
; Bound: 60
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %gl_InstanceIndex %vertexNum %attr0 %attr1 %attr2 %__0
               OpSource ESSL 310
               OpName %main "main"
               OpName %outBuffer "outBuffer"
               OpMemberName %outBuffer 0 "outData"
               OpName %_ ""
               OpName %gl_InstanceIndex "gl_InstanceIndex"
               OpName %vertexNum "vertexNum"
               OpName %attr0 "attr0"
               OpName %attr1 "attr1"
               OpName %attr2 "attr2"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %__0 ""
               OpDecorate %_arr_uint_uint_27 ArrayStride 4
               OpDecorate %outBuffer BufferBlock
               OpMemberDecorate %outBuffer 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_InstanceIndex BuiltIn InstanceIndex
               OpDecorate %vertexNum Location 3
               OpDecorate %attr0 Location 0
               OpDecorate %attr1 Location 1
               OpDecorate %attr2 Location 2
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
    %uint_27 = OpConstant %uint 27
%_arr_uint_uint_27 = OpTypeArray %uint %uint_27
  %outBuffer = OpTypeStruct %_arr_uint_uint_27
%_ptr_Uniform_outBuffer = OpTypePointer Uniform %outBuffer
          %_ = OpVariable %_ptr_Uniform_outBuffer Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_int = OpTypePointer Input %int
%gl_InstanceIndex = OpVariable %_ptr_Input_int Input
     %int_27 = OpConstant %int 27
  %vertexNum = OpVariable %_ptr_Input_int Input
      %int_3 = OpConstant %int 3
%_ptr_Input_uint = OpTypePointer Input %uint
      %attr0 = OpVariable %_ptr_Input_uint Input
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
      %int_1 = OpConstant %int 1
      %attr1 = OpVariable %_ptr_Input_uint Input
      %int_2 = OpConstant %int 2
      %attr2 = OpVariable %_ptr_Input_uint Input
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
        %__0 = OpVariable %_ptr_Output_gl_PerVertex Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %57 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_1
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpLoad %int %gl_InstanceIndex
         %18 = OpIMul %int %16 %int_27
         %20 = OpLoad %int %vertexNum
         %22 = OpIMul %int %20 %int_3
         %23 = OpIAdd %int %22 %int_0
         %24 = OpIAdd %int %18 %23
         %27 = OpLoad %uint %attr0
         %29 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %24
               OpStore %29 %27
         %30 = OpLoad %int %gl_InstanceIndex
         %31 = OpIMul %int %30 %int_27
         %32 = OpLoad %int %vertexNum
         %33 = OpIMul %int %32 %int_3
         %35 = OpIAdd %int %33 %int_1
         %36 = OpIAdd %int %31 %35
         %38 = OpLoad %uint %attr1
         %39 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %36
               OpStore %39 %38
         %40 = OpLoad %int %gl_InstanceIndex
         %41 = OpIMul %int %40 %int_27
         %42 = OpLoad %int %vertexNum
         %43 = OpIMul %int %42 %int_3
         %45 = OpIAdd %int %43 %int_2
         %46 = OpIAdd %int %41 %45
         %48 = OpLoad %uint %attr2
         %49 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %46
               OpStore %49 %48
         %59 = OpAccessChain %_ptr_Output_v4float %__0 %int_0
               OpStore %59 %57
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test creates a dedicated logical device with `robustBufferAccess` enabled, then creates host-visible vertex-rate, instance-rate, bookkeeping, optional index, and output buffers [device creation](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L378-L488), [buffer setup](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L596-L735).
- Binding 0 has two selected-format attributes at offsets `0` and one format element. Binding 1 has one instance-rate attribute. Binding 2 contains `R32_SINT` bookkeeping values that map executed vertices to output slots [vertex input setup](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L541-L589).
- The host binds the SSBO at set `0`, binding `0`, configures the graphics environment, and records either `vkCmdDraw` or `vkCmdDrawIndexed` with the case's vertex and instance counts [descriptor and draw setup](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L737-L799).
- Before submission, the host initializes the bookkeeping buffer. It submits the command buffer, waits for a fence, invalidates the output allocation, and calls `verifyResult()` [iteration](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L806-L858).
- `verifyResult()` maps each captured scalar to its source binding and index. Values that remain classified as in range after the same-binding allowance must match the populated input after format extraction. Out-of-range values must match a value available in the bound memory, zero, or the permitted four-component pattern [result verification](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L860-L1003).
- The color attachment makes the graphics draw valid, but the host reads only the SSBO for the verdict.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `vertex_out_of_bounds` | Incorrect robust handling when sequential non-indexed vertex fetches pass the end of the vertex-rate buffer. |
| `vertex_incomplete` | Incorrect bounds handling or input extraction when only part of a vertex record or attribute is available. |
| `instance_out_of_bounds` | Incorrect robust handling of instance-rate attributes when later instances exceed the instance buffer. |
| `last_index_out_of_bounds` | Incorrect robust indexed fetch behavior when the final submitted index selects a vertex outside the vertex-rate buffer. |
| `indices_out_of_bounds` | Incorrect robust indexed fetch behavior for several noncontiguous out-of-range indices mixed with valid indices. |
| `triangle_out_of_bounds` | Incorrect robust indexed fetch behavior when one complete primitive uses out-of-range vertex indices. |

All six values can also expose incorrect vertex format conversion, shader capture, or host classification for the selected format.

### Cause Analysis

#### Sequential and incomplete vertex-rate robust fetch handling

**Possible failure symptoms:** `vertex_out_of_bounds` produces an unexpected captured value for a valid or out-of-range sequential vertex, or `vertex_incomplete` mishandles a record split by the end of binding 0. `verifyResult()` reports the scalar as an unexpected in-range value or as outside the permitted robust result set.

**Possible implementation causes:** Bounds calculations can use the wrong binding range, stride, attribute offset, or format width. The implementation can also mishandle Vulkan's allowance for all reads through binding 0 in one invocation to behave as out of range when either adjacent attribute crosses the checked range [robust vertex input rule](../../../../vulkan-docs/src/chapters/shaders.adoc#L1936-L1960), [checker boundary logic](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L897-L932).

#### Instance-rate robust fetch handling

**Possible failure symptoms:** The first instance's `attr2` value does not match its input, or later instances return a value that the checker rejects as neither available input data, zero, nor the permitted vector pattern.

**Possible implementation causes:** Vertex input address generation can apply vertex-rate indexing to binding 1, use the wrong instance index, or check the fetch against the wrong range. The pipeline describes binding 1 with `VK_VERTEX_INPUT_RATE_INSTANCE`, and the checker derives its element index from the captured output's instance position [binding setup](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L556-L583), [instance-rate classification](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L897-L906).

#### Indexed vertex-rate robust fetch handling

**Possible failure symptoms:** A valid indexed fetch changes, an index of `100`, `101`, or `102` yields a rejected value, or results from the valid and invalid triangles map to the wrong output slots.

**Possible implementation causes:** Indexed draw processing can apply bounds checks to the submitted index position instead of the fetched vertex index, lose the explicit index during vertex input address calculation, or associate shader output with the wrong executed vertex. The host writes inverse bookkeeping values for the submitted indices and uses the original index sequence when classifying each fetch [indexed bookkeeping](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1169-L1185), [indexed patterns](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L421-L435).

#### Vertex format conversion, capture, or classification

**Possible failure symptoms:** Failures cluster by scalar type, component count, 64-bit format, or `a2b10g10r10_unorm_pack32`, including cases whose bounds pattern passes for other formats.

**Possible implementation causes:** Vertex input extraction or shader interface lowering can use the wrong signedness, width, vector component mapping, or packed normalized conversion. A failure can also come from the vertex-stage SSBO write path or host-side format-specific comparison rather than the fetch itself. The source uses separate checks for integer, float, 64-bit, and packed values [format checks](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1005-L1097).

## Case Pruning

### Requirement-based pruning

- On a device that exposes `VK_KHR_portability_subset`, the test requires `robustBufferAccess` [support check](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L255-L261).
- Every case requires `vertexPipelineStoresAndAtomics` because the vertex shader writes the output SSBO [storage support check](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L524-L528).
- `r64_uint` and `r64_sint` require `VK_EXT_shader_image_atomic_int64` and vertex-buffer support for the selected format [64-bit support checks](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L530-L539).
- Unsupported cases are skipped rather than reported as conformance failures.

### Design-based pruning

- The source registers the same six leaves for each of 15 formats. It does not generate a Cartesian product of arbitrary buffer lengths, draw counts, and index lists; those values are fixed per behavior leaf [case registration](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1190-L1287).
- Indexed cases use three six-index patterns. Other placements of out-of-range indices are outside this test family's registered design.

## Key Takeaways

- The test judges fetched vertex input data through a shader-written SSBO, not through rendered pixels or API errors.
- Locations 0 and 1 share one vertex-rate binding, while location 2 gives separate instance-rate coverage.
- Robustness does not require one fixed out-of-range value. The checker accepts the set permitted by the Vulkan robust vertex input rules while requiring fetches that remain classified as in range to preserve their expected values.
- Six behavior leaves separate sequential, incomplete-record, instance-rate, and indexed access patterns. The 15-format matrix repeats those access patterns across conversion and component layouts.
- See `## Failure Meaning` for how a failing leaf narrows the affected addressing, bounds, format, capture, or classification path.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test and instance types | [vktRobustnessVertexAccessTests.cpp#L52-L238](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L52-L238) | Defines the common test parameters, runtime resources, and draw-specific instances. |
| Shader generation | [`VertexAccessTest::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L263-L366) | Emits format-specific vertex inputs, SSBO capture stores, and the fixed fragment shader. |
| Indexed patterns | [`DrawIndexedAccessTest::s_indexConfigs`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L421-L435) | Defines the three indexed behavior leaves' index sequences. |
| Vertex input and resource setup | [`VertexAccessInstance`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L493-L800) | Creates bindings, buffers, descriptor state, and graphics draw configuration. |
| Submission and result checking | [`iterate()` and `verifyResult()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L806-L1003) | Submits the draw, reads the SSBO, and applies in-range and robust out-of-range checks. |
| Format-sensitive checks | [`isValueWithinVertexBufferOrZero()` and `isExpectedValueFromVertexBuffer()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1005-L1097) | Handles packed, integer, floating-point, and 64-bit values. |
| Non-indexed registration | [`createDrawTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1190-L1225) | Registers the three non-indexed test case leaves. |
| Indexed registration | [`createDrawIndexedTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1227-L1256) | Registers the three indexed test case leaves. |
| Format matrix and test family root | [`addVertexFormatTests()` and `createVertexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1258-L1297) | Registers 15 format intermediate nodes under `robustness.vertex_access`. |
| Robust vertex input semantics | [Vulkan specification: Robust Buffer Access](../../../../vulkan-docs/src/chapters/shaders.adoc#L1925-L2030) | Defines checked ranges, same-binding behavior, and permitted out-of-range values. |
| Vertex input state | [Vulkan specification: Vertex Input Description](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L257-L409) | Defines bindings, input rates, formats, and offsets. |
| Mustpass inventory | [robustness.txt#L96874-L96963](../../../mustpass/main/vk-default/robustness.txt#L96874-L96963) | Confirms 90 registered paths for the 15 by 2 by 3 matrix. |
