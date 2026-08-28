## Overview

**Core question:** Do out-of-bounds buffer references in an unexecuted shader branch remain harmless?

- This page covers the `robustness.non_robust_buffer_access` test family registered by [`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L58).
- Its two Amber compute test cases alternate between branches whose executed accesses are valid while the other branch contains overflow or underflow references.
- Each case passes only when the executed branch produces the complete expected interleaving without effects from the unexecuted references.

## Background Knowledge

For the shared model of bounded resource access and shader/host responsibilities, see [Robustness Background Knowledge](../../categories/robustness.md#background-knowledge).

- **Dynamic control flow:** Only the selected side of an `if` statement executes for an invocation. Buffer expressions in the unselected side must not behave as if they had been evaluated.
- **Non-robust buffer access:** These cases do not ask Vulkan to define the value of an executed out-of-bounds access. They keep invalid-looking expressions in unselected branches and check that only the selected branch contributes memory accesses and side effects.

## Registration Hierarchy

```text
robustness.non_robust_buffer_access
├── unexecuted_oob_overflow
└── unexecuted_oob_underflow
```

The two test case leaves are registered from the `nonRobustBufferAccessTests` vector and are present in the default mustpass list ([`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L54), [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13753-L13754)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `unexecuted_oob_overflow`, `unexecuted_oob_underflow` | Selects whether the unexecuted alternate path uses indices beyond the upper bound or below zero. | [`nonRobustBufferAccessTests`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L41-L46) |
| Execution backend | Amber file matching the test case leaf | Supplies the compute shader, buffers, dispatch, and equality check. | [`createAmberTestCase()`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L49-L54) |
| Workgroup configuration | `local_size_x = 4`; `RUN pipeline 4 1 1` | Runs 16 invocations, each producing part of the 1024-element output. | [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L39-L43), [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L103-L105) |
| Buffers | two 512-element inputs, one 8-element control buffer, one 1024-element output | Provides the valid source data, runtime branch choices, and complete result. | [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L79-L93) |

## Behavior Parameters

The primary behavioral axis is the test case leaf because it chooses which kind of invalid index appears only on the unexecuted path.

### `unexecuted_oob_overflow` — upper-bound references

The shader starts alternate-path indices high enough to create overflow or overlap references as the loop alternates branches. Runtime control data selects the valid path for each operation, so the unselected references must not disturb the expected interleaving ([`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L26-L35), [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L45-L76)).

### `unexecuted_oob_underflow` — negative references

The alternate-path input and output indices begin at `-128`. Branch control again keeps those references unexecuted while the selected accesses copy the valid inputs into their expected positions ([`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L26-L35), [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L45-L76)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.robustness.non_robust_buffer_access.unexecuted_oob_underflow
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `unexecuted_oob_underflow` | Places indices beginning at `-128` in the alternate branch while runtime control selects valid accesses. |
| `local_size_x = 4` | Runs four invocations per workgroup. |
| `RUN pipeline 4 1 1` | Launches 16 invocations for the complete output. |

#### Purpose

The compute shader copies two valid 512-element input arrays into alternating positions of a 1024-element output while negative indices remain confined to the branch not selected at runtime.

#### Structural Design

| Shader element | Role in this case |
|----------------|-------------------|
| `data_in0`, `data_in1` | Supply the valid values that form the interleaved result. |
| `data_in2` | Supplies runtime-dependent branch choices. |
| `data_out` | Receives the values checked against `expected`. |
| Alternate indices beginning at `-128` | Exercise underflow expressions only on the unselected side. |

#### Shader Code

The following is the complete GLSL shader embedded in the authoritative Amber case, not a simplified reconstruction ([shader body](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L36-L76)).

```glsl
#version 430

layout(local_size_x = 4, local_size_y = 1, local_size_z = 1) in;
layout(set = 0, binding = 0) readonly buffer In0 { int data_in0[512]; };
layout(set = 0, binding = 1) readonly buffer In1 { int data_in1[512]; };
layout(set = 0, binding = 2) readonly buffer In2 { int data_in2[8]; };
layout(set = 0, binding = 3) writeonly buffer Out0 { int data_out0[1024]; };

void main()
{
	uint base_index_in = 128 * gl_WorkGroupID.x;
	uint base_index_out = 256 * gl_WorkGroupID.x;
	int index_in0 = 0;
	int index_in1 = -128;
	int index_out0 = 0;
	int index_out1 = -128;
	int condition_index = 0;
	for(int i = 0; i < 256; ++i)
	{
		if (data_in2[condition_index] == 0)
		{
			data_out0[base_index_out + index_out0] = data_in0[base_index_in + index_in0];
			++index_out0;
			++index_in1;
		}
		else
		{
			data_out0[base_index_out + index_out1] = data_in1[base_index_in + index_in1];
			++index_out1;
			++index_in1;
		}
		condition_index += data_in2[condition_index + 1];
		int temp0 = index_in0;
		index_in0 = index_in1;
		index_in1 = temp0;
		int temp1 = index_out0;
		index_out0 = index_out1;
		index_out1 = temp1;
	}
}
```

The loop swaps the valid and negative index variables after every iteration. The runtime `data_in2` sequence selects the branch that uses valid addresses; the invalid expressions stay on the unselected branch.

#### Additional Info

- The runtime branch-control buffer prevents the selection pattern from becoming a compile-time constant.
- This walkthrough uses the CTS-authored Amber GLSL directly; the C++ registration code does not generate shader variants.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Test case leaf | `unexecuted_oob_overflow` starts alternate input and output indices above the valid range and decrements them; the branch, swap, dispatch, and equality-check structure remains the same. | [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L36-L76) |

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
; Bound: 119
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_WorkGroupID
               OpExecutionMode %main LocalSize 4 1 1
               OpSource GLSL 430
               OpName %main "main"
               OpName %base_index_in "base_index_in"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %base_index_out "base_index_out"
               OpName %index_in0 "index_in0"
               OpName %index_in1 "index_in1"
               OpName %index_out0 "index_out0"
               OpName %index_out1 "index_out1"
               OpName %condition_index "condition_index"
               OpName %i "i"
               OpName %In2 "In2"
               OpMemberName %In2 0 "data_in2"
               OpName %_ ""
               OpName %Out0 "Out0"
               OpMemberName %Out0 0 "data_out0"
               OpName %__0 ""
               OpName %In0 "In0"
               OpMemberName %In0 0 "data_in0"
               OpName %__1 ""
               OpName %In1 "In1"
               OpMemberName %In1 0 "data_in1"
               OpName %__2 ""
               OpName %temp0 "temp0"
               OpName %temp1 "temp1"
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %_arr_int_uint_8 ArrayStride 4
               OpDecorate %In2 BufferBlock
               OpMemberDecorate %In2 0 NonWritable
               OpMemberDecorate %In2 0 Offset 0
               OpDecorate %_ NonWritable
               OpDecorate %_ Binding 2
               OpDecorate %_ DescriptorSet 0
               OpDecorate %_arr_int_uint_1024 ArrayStride 4
               OpDecorate %Out0 BufferBlock
               OpMemberDecorate %Out0 0 NonReadable
               OpMemberDecorate %Out0 0 Offset 0
               OpDecorate %__0 NonReadable
               OpDecorate %__0 Binding 3
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %_arr_int_uint_512 ArrayStride 4
               OpDecorate %In0 BufferBlock
               OpMemberDecorate %In0 0 NonWritable
               OpMemberDecorate %In0 0 Offset 0
               OpDecorate %__1 NonWritable
               OpDecorate %__1 Binding 0
               OpDecorate %__1 DescriptorSet 0
               OpDecorate %_arr_int_uint_512_0 ArrayStride 4
               OpDecorate %In1 BufferBlock
               OpMemberDecorate %In1 0 NonWritable
               OpMemberDecorate %In1 0 Offset 0
               OpDecorate %__2 NonWritable
               OpDecorate %__2 Binding 1
               OpDecorate %__2 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
   %uint_128 = OpConstant %uint 128
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
   %uint_256 = OpConstant %uint 256
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
   %int_n128 = OpConstant %int -128
    %int_256 = OpConstant %int 256
       %bool = OpTypeBool
     %uint_8 = OpConstant %uint 8
%_arr_int_uint_8 = OpTypeArray %int %uint_8
        %In2 = OpTypeStruct %_arr_int_uint_8
%_ptr_Uniform_In2 = OpTypePointer Uniform %In2
          %_ = OpVariable %_ptr_Uniform_In2 Uniform
%_ptr_Uniform_int = OpTypePointer Uniform %int
  %uint_1024 = OpConstant %uint 1024
%_arr_int_uint_1024 = OpTypeArray %int %uint_1024
       %Out0 = OpTypeStruct %_arr_int_uint_1024
%_ptr_Uniform_Out0 = OpTypePointer Uniform %Out0
        %__0 = OpVariable %_ptr_Uniform_Out0 Uniform
   %uint_512 = OpConstant %uint 512
%_arr_int_uint_512 = OpTypeArray %int %uint_512
        %In0 = OpTypeStruct %_arr_int_uint_512
%_ptr_Uniform_In0 = OpTypePointer Uniform %In0
        %__1 = OpVariable %_ptr_Uniform_In0 Uniform
      %int_1 = OpConstant %int 1
%_arr_int_uint_512_0 = OpTypeArray %int %uint_512
        %In1 = OpTypeStruct %_arr_int_uint_512_0
%_ptr_Uniform_In1 = OpTypePointer Uniform %In1
        %__2 = OpVariable %_ptr_Uniform_In1 Uniform
     %uint_4 = OpConstant %uint 4
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_4 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%base_index_in = OpVariable %_ptr_Function_uint Function
%base_index_out = OpVariable %_ptr_Function_uint Function
  %index_in0 = OpVariable %_ptr_Function_int Function
  %index_in1 = OpVariable %_ptr_Function_int Function
 %index_out0 = OpVariable %_ptr_Function_int Function
 %index_out1 = OpVariable %_ptr_Function_int Function
%condition_index = OpVariable %_ptr_Function_int Function
          %i = OpVariable %_ptr_Function_int Function
      %temp0 = OpVariable %_ptr_Function_int Function
      %temp1 = OpVariable %_ptr_Function_int Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %16 = OpLoad %uint %15
         %17 = OpIMul %uint %uint_128 %16
               OpStore %base_index_in %17
         %20 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %21 = OpLoad %uint %20
         %22 = OpIMul %uint %uint_256 %21
               OpStore %base_index_out %22
               OpStore %index_in0 %int_0
               OpStore %index_in1 %int_n128
               OpStore %index_out0 %int_0
               OpStore %index_out1 %int_n128
               OpStore %condition_index %int_0
               OpStore %i %int_0
               OpBranch %33
         %33 = OpLabel
               OpLoopMerge %35 %36 None
               OpBranch %37
         %37 = OpLabel
         %38 = OpLoad %int %i
         %41 = OpSLessThan %bool %38 %int_256
               OpBranchConditional %41 %34 %35
         %34 = OpLabel
         %47 = OpLoad %int %condition_index
         %49 = OpAccessChain %_ptr_Uniform_int %_ %int_0 %47
         %50 = OpLoad %int %49
         %51 = OpIEqual %bool %50 %int_0
               OpSelectionMerge %53 None
               OpBranchConditional %51 %52 %80
         %52 = OpLabel
         %59 = OpLoad %uint %base_index_out
         %60 = OpLoad %int %index_out0
         %61 = OpBitcast %uint %60
         %62 = OpIAdd %uint %59 %61
         %68 = OpLoad %uint %base_index_in
         %69 = OpLoad %int %index_in0
         %70 = OpBitcast %uint %69
         %71 = OpIAdd %uint %68 %70
         %72 = OpAccessChain %_ptr_Uniform_int %__1 %int_0 %71
         %73 = OpLoad %int %72
         %74 = OpAccessChain %_ptr_Uniform_int %__0 %int_0 %62
               OpStore %74 %73
         %75 = OpLoad %int %index_out0
         %77 = OpIAdd %int %75 %int_1
               OpStore %index_out0 %77
         %78 = OpLoad %int %index_in1
         %79 = OpIAdd %int %78 %int_1
               OpStore %index_in1 %79
               OpBranch %53
         %80 = OpLabel
         %81 = OpLoad %uint %base_index_out
         %82 = OpLoad %int %index_out1
         %83 = OpBitcast %uint %82
         %84 = OpIAdd %uint %81 %83
         %89 = OpLoad %uint %base_index_in
         %90 = OpLoad %int %index_in1
         %91 = OpBitcast %uint %90
         %92 = OpIAdd %uint %89 %91
         %93 = OpAccessChain %_ptr_Uniform_int %__2 %int_0 %92
         %94 = OpLoad %int %93
         %95 = OpAccessChain %_ptr_Uniform_int %__0 %int_0 %84
               OpStore %95 %94
         %96 = OpLoad %int %index_out1
         %97 = OpIAdd %int %96 %int_1
               OpStore %index_out1 %97
         %98 = OpLoad %int %index_in1
         %99 = OpIAdd %int %98 %int_1
               OpStore %index_in1 %99
               OpBranch %53
         %53 = OpLabel
        %100 = OpLoad %int %condition_index
        %101 = OpIAdd %int %100 %int_1
        %102 = OpAccessChain %_ptr_Uniform_int %_ %int_0 %101
        %103 = OpLoad %int %102
        %104 = OpLoad %int %condition_index
        %105 = OpIAdd %int %104 %103
               OpStore %condition_index %105
        %107 = OpLoad %int %index_in0
               OpStore %temp0 %107
        %108 = OpLoad %int %index_in1
               OpStore %index_in0 %108
        %109 = OpLoad %int %temp0
               OpStore %index_in1 %109
        %111 = OpLoad %int %index_out0
               OpStore %temp1 %111
        %112 = OpLoad %int %index_out1
               OpStore %index_out0 %112
        %113 = OpLoad %int %temp1
               OpStore %index_out1 %113
               OpBranch %36
         %36 = OpLabel
        %114 = OpLoad %int %i
        %115 = OpIAdd %int %114 %int_1
               OpStore %i %115
               OpBranch %33
         %35 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Amber creates two 512-element `int32` input buffers, an eight-element branch-control buffer, a 1024-element output buffer, and an explicit expected buffer.
- It binds the four device-visible buffers to one compute pipeline and dispatches `4 1 1` workgroups.
- The shader uses the control values `0, 2, 1, 2, 0, 2, 1, -6` while advancing `condition_index`; this preserves runtime-dependent branch selection.
- After dispatch, Amber checks the entire result with `EXPECT data_out EQ_BUFFER expected` ([`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L79-L105), [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L79-L105)).
- The expected buffer is the increasing 1024-value sequence formed by interleaving the two initialized inputs.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `unexecuted_oob_overflow` | Upper-bound references from an unselected branch affected valid reads, writes, or control flow. |
| `unexecuted_oob_underflow` | Negative references from an unselected branch affected valid reads, writes, or control flow. |

### Cause Analysis

#### Unselected branch affects valid execution

**Possible failure symptoms:** `data_out` differs from the explicit 1024-element expected buffer at one or more positions, even though the selected branch's accesses are valid.

**Possible implementation causes:** Shader compilation or execution may incorrectly retain memory effects from buffer operations in the unselected branch. A mismatch can also indicate incorrect lowering of the branch/index expressions or valid storage-buffer operations; source-level investigation is needed to distinguish these mechanisms. Internal speculative work is not itself observable and is not a failure unless it changes execution or memory results.

## Case Pruning

### Requirement-based pruning

- The C++ registration loop is excluded when `CTS_USES_VULKANSC` is defined, so these Amber test case leaves are not registered for Vulkan SC ([`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L48-L55)).
- The registration file adds no explicit extension or optional-feature gate beyond the operations required by the Amber compute programs.

### Design-based pruning

- The matrix contains only the two boundary directions needed by the design: overflow and underflow.
- Executed out-of-bounds accesses are intentionally excluded. Their values or side effects are not the property this family tries to define.

## Key Takeaways

- The test family isolates invalid buffer references in branches that runtime control does not select.
- `unexecuted_oob_overflow` and `unexecuted_oob_underflow` exercise opposite index boundaries with the same full-buffer equality verdict.
- A failure means the valid executed path did not remain independent of the unexecuted path; see `## Failure Meaning` for possible causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test registration and Amber mapping | [`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L58) | Defines the test family and maps both test case leaves to Amber files. |
| Factory declaration | [`vktNonRobustBufferAccessTests.hpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.hpp#L31-L37) | Declares the registration entry point. |
| Category registration | [`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L84-L90) | Places the test family under `robustness`. |
| Overflow Amber case | [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L1-L105) | Defines the upper-bound shader path, resources, dispatch, and expected result. |
| Underflow Amber case | [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L1-L105) | Defines the negative-index shader path, resources, dispatch, and expected result. |
| Default mustpass entries | [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13753-L13754) | Confirms both registered test case paths. |
