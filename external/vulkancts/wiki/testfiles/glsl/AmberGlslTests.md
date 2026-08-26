## Overview

**Core question:** Do the non-VulkanSC Amber GLSL scripts execute their stated arithmetic, robustness, and struct-assignment checks and report the intended Amber expectations?

- [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L1-L106) registers three Amber-backed test families under the `glsl` test category: `combined_operations`, `crash_test`, and `logical_copy`.
- The package adds these families only when Vulkan SC is not in use. Each registered test case loads an Amber script from `vulkan/amber/<family>/<case>.amber` through [`createAmberTestCase()`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L200-L216).
- The scripts contain the shaders, pipeline declarations, resources, commands, and `EXPECT` checks. This page explains the three distinct behaviors, their feature requirements, and how Amber converts script results into CTS results.

## Background Knowledge

- An Amber script is a declarative test recipe. It can define shaders and resources, assemble a graphics or compute pipeline, issue work, and compare a framebuffer or buffer value with an expected result.
- A storage buffer object (SSBO) lets a shader write values that Amber can inspect after execution. A known value written after an operation can act as a completion sentinel without asserting the operation's unspecified numeric result.
- An unspecified shader result is not a portable value to compare. A robustness test can instead check that execution reaches a known point and does not interrupt or terminate Vulkan.

## Registration Hierarchy

```text
glsl
├── combined_operations (non-VulkanSC only)
├── crash_test (non-VulkanSC only)
└── logical_copy (non-VulkanSC only)
```

[`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287) adds all three test families inside its non-VulkanSC block. The factory functions in [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L102) register the test case leaves listed below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test family | `combined_operations`, `crash_test`, `logical_copy` | Selects one of three unrelated Amber-script behaviors: expression output, robustness against zero-divisor operations, or struct assignment. | [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L102) |
| `combined_operations` case | `notxor`, `negintdivand` | Selects a whole-frame unsigned bitwise result or selected regions produced by integer division and bitwise operations. | [`combinedOperationsTests`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L51) |
| `crash_test` stage | `vert`, `tesc`, `tese`, `geom`, `frag`, `comp` | Places the risky arithmetic in each supported programmable stage represented by the scripts. | [`crashTestParameters`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L54-L78) |
| `crash_test` operation form | integer and floating division, `normalize`, `mod`, `smoothstep`, `atan(y, x)` | Exercises explicit or implied zero-divisor behavior without comparing its unspecified result. | [`divbyzero_vert.amber`](../../../data/vulkan/amber/crash_test/divbyzero_vert.amber#L33-L78) and [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L27-L72) |
| `logical_copy` source state | initialized aggregate, uninitialized local | Distinguishes assignment of a defined `Bar` value from assignment of an uninitialized local `Bar`. | [`createLogicalCopyGroup()`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L81-L102) |
| Work submission | 16x16, 32x32, or 250x250 graphics draws; a patch-list draw; 1x1x1 compute dispatch | Matches each script's chosen stage and validation mechanism. | [`notxor.amber`](../../../data/vulkan/amber/combined_operations/notxor.amber#L43-L50), [`divbyzero_tesc.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tesc.amber#L118-L146), and [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L75-L87) |

## Behavior Parameters

The primary behavioral axis is the registered test family. Each family chooses a different property and pass condition.

### `combined_operations` - expression results in graphics shaders

`notxor` supplies two `uint` push constants to a fragment shader, which writes `~(op1 ^ op2)` and must produce a white 16x16 framebuffer. `negintdivand` derives integer coordinates from the fragment color, branches on `((iv.y / 2) & 64)`, and checks cyan and red 30x30 regions. These cases compare defined framebuffer output rather than merely completing execution. See [`notxor.amber`](../../../data/vulkan/amber/combined_operations/notxor.amber#L18-L50) and [`negintdivand.amber`](../../../data/vulkan/amber/combined_operations/negintdivand.amber#L17-L52).

### `crash_test` - zero-divisor robustness across shader stages

The six cases place equivalent risky expressions in vertex, tessellation-control, tessellation-evaluation, geometry, fragment, and compute shaders. The scripts exercise division, modulo, normalization, `smoothstep`, and two-argument `atan` with zero-valued divisors or zero-length inputs. The property under test is completion: the scripts do not treat the resulting values as deterministic.

The vertex, tessellation, geometry, and compute scripts write `42` to `ssbo.data[0]` after the expression sequence and expect that sentinel. The fragment script first writes a known red pixel at `(0, 0)` and checks only that pixel after sweeping the risky expressions over the rest of the draw. See [`divbyzero_frag.amber`](../../../data/vulkan/amber/crash_test/divbyzero_frag.amber#L17-L136).

### `logical_copy` - assignment to a `std430` struct in a storage buffer

Both graphics scripts declare `Bar` with two scalar members and a two-element array, place `Bar b` after a `uvec4` in a `std430` storage buffer, and assign a local `Bar` to `b`. `initialized_struct` assigns `{0, 0, {0, 0}}` and checks the four words at byte offsets 16, 20, 24, and 28. `undefined_memory` assigns an uninitialized local `Bar`; it has no `EXPECT`, so it tests successful recipe execution rather than a defined copied value. See [`initialized_struct.amber`](../../../data/vulkan/amber/logical_copy/initialized_struct.amber#L17-L66) and [`undefined_memory.amber`](../../../data/vulkan/amber/logical_copy/undefined_memory.amber#L17-L60).

## Shader Analysis

Amber keeps the GLSL source in the `.amber` recipe. The representative case below is the compute variant of `crash_test`, whose shader is compiled by `AmberTestCase::initPrograms()` with the recipe's default `spv1.0` target (`SPIRV_VERSION_1_0`) and then executed by Amber. The source, registration, mustpass entry, and generated SPIR-V all describe the same case.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.crash_test.divbyzero_comp
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `crash_test` | Selects the family that exercises zero-divisor and zero-length calculations for completion, not for a portable numeric result. |
| `divbyzero_comp` | Selects the compute-stage recipe: one `local_size` 1 workgroup reads zero from an SSBO, performs the complete scalar/vector operation matrix, then writes the completion sentinel `42`. |
| Default Amber shader target | The recipe has no `TARGET_ENV`; `AmberTestCase::initPrograms()` therefore leaves `spirvVersion` at `SPIRV_VERSION_1_0`, which is the target used for the canonical disassembly below. |

#### Purpose

This shader checks that Vulkan execution survives integer and floating-point division, normalization, modulo, `smoothstep`, and two-argument `atan` when their divisor or input length is zero. The pass signal is the final `ssbo.data[0] = 42` store, not any value produced by the unspecified operations.

#### Structural Design

| Phase | Shader-visible operation | Observable role |
|---|---|---|
| Initialization | Load `ssbo.data[0]` and convert it from `int` to `float`. | The recipe initializes the SSBO element to zero, so `ival == 0` and `val == 0.0`. |
| Operation matrix | Write results of scalar and vector forms of division, `normalize`, `mod`, `smoothstep`, and `atan(7, value)` to `ssbo.data[1..19]`. | Exercises explicit and implied zero-division paths without comparing those result slots. |
| Completion | Store `42` to `ssbo.data[0]`. | Proves that execution reached the known-good store. |
| Host check | Dispatch `1 1 1`, then run `EXPECT ssbo_buffer IDX 0 EQ 42`. | Converts completion into the Amber/CTS pass condition. |

#### Shader Code

```glsl
#version 450
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

/// The SSBO is descriptor set 0, binding 0. Its first element is the zero
/// input; the remaining elements receive the operation results.
layout(binding = 0) buffer block0
{
    int data[20];
} ssbo;

void main()
{
  // Zero constants
  int ival = ssbo.data[0];
  float val = float(ival);

  /// Each assignment deliberately covers one scalar or vector form. The
  /// recipe does not compare these intermediate values because zero-divisor
  /// results are unspecified.
  // int div
  ssbo.data[1] = 7 / ival;
  // float div
  ssbo.data[2] = int(7.0 / val);
  // normalize float
  ssbo.data[3] = int(normalize(val));
  // normalize vec2
  ssbo.data[4] = int(normalize(vec2(val))[ival]);
  // normalize vec3
  ssbo.data[5] = int(normalize(vec3(val))[ival]);
  // normalize vec4
  ssbo.data[6] = int(normalize(vec4(val))[ival]);
  // integer mod
  ssbo.data[7] = 7 % ival;
  // float mod
  ssbo.data[8] = int(mod(7.0, val));
  // vec2 mod
  ssbo.data[9] = int(mod(vec2(7.0), vec2(val))[ival]);
  // vec3 mod
  ssbo.data[10] = int(mod(vec3(7.0), vec3(val))[ival]);
  // vec4 mod
  ssbo.data[11] = int(mod(vec4(7.0), vec4(val))[ival]);
  // float smoothstep
  ssbo.data[12] = int(smoothstep(val, val, 0.3));
  // vec2 smoothstep
  ssbo.data[13] = int(smoothstep(vec2(val), vec2(val), vec2(0.3))[ival]);
  // vec3 smoothstep
  ssbo.data[14] = int(smoothstep(vec3(val), vec3(val), vec3(0.3))[ival]);
  // vec4 smoothstep
  ssbo.data[15] = int(smoothstep(vec4(val), vec4(val), vec4(0.3))[ival]);
  // float atan2
  ssbo.data[16] = int(atan(7.0, val));
  // vec2 atan2
  ssbo.data[17] = int(atan(vec2(7.0), vec2(val))[ival]);
  // vec3 atan2
  ssbo.data[18] = int(atan(vec3(7.0), vec3(val))[ival]);
  // vec4 atan2
  ssbo.data[19] = int(atan(vec4(7.0), vec4(val))[ival]);

  // Known good value
  ssbo.data[0] = 42;
}
```

#### Additional Info

- The exact Amber recipe initializes all 20 `int32` elements to zero, binds `ssbo_buffer` as storage at descriptor set 0/binding 0, dispatches one workgroup, and checks only index 0. [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L16-L87)
- The C++ registration supplies no extra CTS-side feature requirement for `divbyzero_comp`; the mustpass list contains the exact leaf `dEQP-VK.glsl.crash_test.divbyzero_comp`. [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L62-L76) and [`glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L5244-L5249)
- `AmberTestCase::initPrograms()` wraps this source in `glu::ComputeSource` and uses the parsed target environment, defaulting to SPIR-V 1.0 when the Amber shader has no explicit target. [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L435-L475)

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `crash_test` stage | The same operation matrix is placed in vertex, tessellation-control, tessellation-evaluation, geometry, fragment, or compute shaders; the compute case uses `local_size = 1,1,1` and a single dispatch. | [`crash_test` recipes](../../../data/vulkan/amber/crash_test) |
| Operation form | `divbyzero_comp` includes scalar and vector forms of division, normalization, modulo, `smoothstep`, and `atan`; the fragment recipe instead sweeps zero divisors over `gl_FragCoord` and preserves a known red pixel. | [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L27-L72) and [`divbyzero_frag.amber`](../../../data/vulkan/amber/crash_test/divbyzero_frag.amber#L25-L136) |
| Shader target environment | No explicit `TARGET_ENV` in this recipe selects the C++ default SPIR-V 1.0 path; other Amber recipes can override the parsed target. | [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L442-L455) |

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
; Bound: 176
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %ival "ival"
               OpName %block0 "block0"
               OpMemberName %block0 0 "data"
               OpName %ssbo "ssbo"
               OpName %val "val"
               OpDecorate %_arr_int_uint_20 ArrayStride 4
               OpDecorate %block0 BufferBlock
               OpMemberDecorate %block0 0 Offset 0
               OpDecorate %ssbo Binding 0
               OpDecorate %ssbo DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
       %uint = OpTypeInt 32 0
    %uint_20 = OpConstant %uint 20
%_arr_int_uint_20 = OpTypeArray %int %uint_20
     %block0 = OpTypeStruct %_arr_int_uint_20
%_ptr_Uniform_block0 = OpTypePointer Uniform %block0
       %ssbo = OpVariable %_ptr_Uniform_block0 Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_int = OpTypePointer Uniform %int
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
      %int_1 = OpConstant %int 1
      %int_7 = OpConstant %int 7
      %int_2 = OpConstant %int 2
    %float_7 = OpConstant %float 7
      %int_3 = OpConstant %int 3
      %int_4 = OpConstant %int 4
    %v2float = OpTypeVector %float 2
      %int_5 = OpConstant %int 5
    %v3float = OpTypeVector %float 3
      %int_6 = OpConstant %int 6
    %v4float = OpTypeVector %float 4
      %int_8 = OpConstant %int 8
      %int_9 = OpConstant %int 9
         %76 = OpConstantComposite %v2float %float_7 %float_7
     %int_10 = OpConstant %int 10
         %85 = OpConstantComposite %v3float %float_7 %float_7 %float_7
     %int_11 = OpConstant %int 11
         %94 = OpConstantComposite %v4float %float_7 %float_7 %float_7 %float_7
     %int_12 = OpConstant %int 12
%float_0_300000012 = OpConstant %float 0.300000012
     %int_13 = OpConstant %int 13
        %114 = OpConstantComposite %v2float %float_0_300000012 %float_0_300000012
     %int_14 = OpConstant %int 14
        %125 = OpConstantComposite %v3float %float_0_300000012 %float_0_300000012 %float_0_300000012
     %int_15 = OpConstant %int 15
        %136 = OpConstantComposite %v4float %float_0_300000012 %float_0_300000012 %float_0_300000012 %float_0_300000012
     %int_16 = OpConstant %int 16
     %int_17 = OpConstant %int 17
     %int_18 = OpConstant %int 18
     %int_19 = OpConstant %int 19
     %int_42 = OpConstant %int 42
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
       %ival = OpVariable %_ptr_Function_int Function
        %val = OpVariable %_ptr_Function_float Function
         %17 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_0
         %18 = OpLoad %int %17
               OpStore %ival %18
         %22 = OpLoad %int %ival
         %23 = OpConvertSToF %float %22
               OpStore %val %23
         %26 = OpLoad %int %ival
         %27 = OpSDiv %int %int_7 %26
         %28 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_1
               OpStore %28 %27
         %31 = OpLoad %float %val
         %32 = OpFDiv %float %float_7 %31
         %33 = OpConvertFToS %int %32
         %34 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_2
               OpStore %34 %33
         %36 = OpLoad %float %val
         %37 = OpExtInst %float %1 Normalize %36
         %38 = OpConvertFToS %int %37
         %39 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_3
               OpStore %39 %38
         %41 = OpLoad %float %val
         %43 = OpCompositeConstruct %v2float %41 %41
         %44 = OpExtInst %v2float %1 Normalize %43
         %45 = OpLoad %int %ival
         %46 = OpVectorExtractDynamic %float %44 %45
         %47 = OpConvertFToS %int %46
         %48 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_4
               OpStore %48 %47
         %50 = OpLoad %float %val
         %52 = OpCompositeConstruct %v3float %50 %50 %50
         %53 = OpExtInst %v3float %1 Normalize %52
         %54 = OpLoad %int %ival
         %55 = OpVectorExtractDynamic %float %53 %54
         %56 = OpConvertFToS %int %55
         %57 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_5
               OpStore %57 %56
         %59 = OpLoad %float %val
         %61 = OpCompositeConstruct %v4float %59 %59 %59 %59
         %62 = OpExtInst %v4float %1 Normalize %61
         %63 = OpLoad %int %ival
         %64 = OpVectorExtractDynamic %float %62 %63
         %65 = OpConvertFToS %int %64
         %66 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_6
               OpStore %66 %65
         %67 = OpLoad %int %ival
         %68 = OpSMod %int %int_7 %67
         %69 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_7
               OpStore %69 %68
         %71 = OpLoad %float %val
         %72 = OpFMod %float %float_7 %71
         %73 = OpConvertFToS %int %72
         %74 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_8
               OpStore %74 %73
         %77 = OpLoad %float %val
         %78 = OpCompositeConstruct %v2float %77 %77
         %79 = OpFMod %v2float %76 %78
         %80 = OpLoad %int %ival
         %81 = OpVectorExtractDynamic %float %79 %80
         %82 = OpConvertFToS %int %81
         %83 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_9
               OpStore %83 %82
         %86 = OpLoad %float %val
         %87 = OpCompositeConstruct %v3float %86 %86 %86
         %88 = OpFMod %v3float %85 %87
         %89 = OpLoad %int %ival
         %90 = OpVectorExtractDynamic %float %88 %89
         %91 = OpConvertFToS %int %90
         %92 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_10
               OpStore %92 %91
         %95 = OpLoad %float %val
         %96 = OpCompositeConstruct %v4float %95 %95 %95 %95
         %97 = OpFMod %v4float %94 %96
         %98 = OpLoad %int %ival
         %99 = OpVectorExtractDynamic %float %97 %98
        %100 = OpConvertFToS %int %99
        %101 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_11
               OpStore %101 %100
        %103 = OpLoad %float %val
        %104 = OpLoad %float %val
        %106 = OpExtInst %float %1 SmoothStep %103 %104 %float_0_300000012
        %107 = OpConvertFToS %int %106
        %108 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_12
               OpStore %108 %107
        %110 = OpLoad %float %val
        %111 = OpCompositeConstruct %v2float %110 %110
        %112 = OpLoad %float %val
        %113 = OpCompositeConstruct %v2float %112 %112
        %115 = OpExtInst %v2float %1 SmoothStep %111 %113 %114
        %116 = OpLoad %int %ival
        %117 = OpVectorExtractDynamic %float %115 %116
        %118 = OpConvertFToS %int %117
        %119 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_13
               OpStore %119 %118
        %121 = OpLoad %float %val
        %122 = OpCompositeConstruct %v3float %121 %121 %121
        %123 = OpLoad %float %val
        %124 = OpCompositeConstruct %v3float %123 %123 %123
        %126 = OpExtInst %v3float %1 SmoothStep %122 %124 %125
        %127 = OpLoad %int %ival
        %128 = OpVectorExtractDynamic %float %126 %127
        %129 = OpConvertFToS %int %128
        %130 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_14
               OpStore %130 %129
        %132 = OpLoad %float %val
        %133 = OpCompositeConstruct %v4float %132 %132 %132 %132
        %134 = OpLoad %float %val
        %135 = OpCompositeConstruct %v4float %134 %134 %134 %134
        %137 = OpExtInst %v4float %1 SmoothStep %133 %135 %136
        %138 = OpLoad %int %ival
        %139 = OpVectorExtractDynamic %float %137 %138
        %140 = OpConvertFToS %int %139
        %141 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_15
               OpStore %141 %140
        %143 = OpLoad %float %val
        %144 = OpExtInst %float %1 Atan2 %float_7 %143
        %145 = OpConvertFToS %int %144
        %146 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_16
               OpStore %146 %145
        %148 = OpLoad %float %val
        %149 = OpCompositeConstruct %v2float %148 %148
        %150 = OpExtInst %v2float %1 Atan2 %76 %149
        %151 = OpLoad %int %ival
        %152 = OpVectorExtractDynamic %float %150 %151
        %153 = OpConvertFToS %int %152
        %154 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_17
               OpStore %154 %153
        %156 = OpLoad %float %val
        %157 = OpCompositeConstruct %v3float %156 %156 %156
        %158 = OpExtInst %v3float %1 Atan2 %85 %157
        %159 = OpLoad %int %ival
        %160 = OpVectorExtractDynamic %float %158 %159
        %161 = OpConvertFToS %int %160
        %162 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_18
               OpStore %162 %161
        %164 = OpLoad %float %val
        %165 = OpCompositeConstruct %v4float %164 %164 %164 %164
        %166 = OpExtInst %v4float %1 Atan2 %94 %165
        %167 = OpLoad %int %ival
        %168 = OpVectorExtractDynamic %float %166 %167
        %169 = OpConvertFToS %int %168
        %170 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_19
               OpStore %170 %169
        %172 = OpAccessChain %_ptr_Uniform_int %ssbo %int_0 %int_0
               OpStore %172 %int_42
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `createAmberTestCase()` constructs each script path by prefixing `vulkan/amber/`, then appending the registered family and script filename. It also transfers CTS-side requirement strings to the `AmberTestCase`. [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L200-L216)
- The test case parses the script, compiles GLSL recipes into the CTS program collection, and supplies the compiled shader binaries to Amber for execution. [`AmberTestCase::parse()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432) and [`AmberTestCase::initPrograms()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L435-L544)
- Amber runs the recipe with Vulkan execution. A successful Amber result becomes `tcu::TestStatus::pass("Pass")`; any Amber execution error is logged and becomes `tcu::TestStatus::fail("Fail")`. [`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615)
- `combined_operations` uses framebuffer `EXPECT` commands. The five SSBO-backed crash scripts use `EXPECT ssbo_buffer IDX 0 EQ 42`; the fragment crash script checks its known red pixel. `initialized_struct` checks four SSBO offsets. `undefined_memory` has no script-level comparison. [`undefined_memory.amber`](../../../data/vulkan/amber/logical_copy/undefined_memory.amber#L47-L60)
- Tessellation-control and tessellation-evaluation cases require `tessellationShader`; the geometry case requires `geometryShader`. Their C++ registration and Amber `DEVICE_FEATURE` declarations must match, and `validateRequirements()` rejects a mismatch. [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L63-L76) and [`AmberTestCase::validateRequirements()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L648-L707)
- In compute-only mode, `AmberTestInstance::iterate()` rejects a recipe containing a non-compute shader. The graphics-script cases are therefore unsupported in that mode, while `divbyzero_comp` uses only a compute shader. [`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L557-L569)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `combined_operations` | Incorrect GLSL integer or bitwise expression evaluation, push-constant delivery, graphics rendering, or framebuffer comparison. |
| `crash_test` | Vulkan interruption or termination during a zero-divisor or zero-length operation, failure to reach the sentinel store or known pixel, or a stage/pipeline execution failure. |
| `logical_copy` | Incorrect storage-buffer struct assignment or layout for `initialized_struct`, or failure to execute the uninitialized-local assignment recipe. |

### Cause Analysis

#### Expression result, resource delivery, or framebuffer checking

**Possible failure symptoms:** `notxor` fails its full-frame white comparison, or `negintdivand` fails one of its cyan or red region comparisons.

**Possible implementation causes:** The scripts depend on fragment shader arithmetic, push constants where used, color attachment writes, and Amber's framebuffer comparison. Source-level investigation is needed to isolate which component produced a mismatching pixel.

#### Robustness completion or stage execution

**Possible failure symptoms:** A sentinel-based crash case does not expose `42` at SSBO index 0, the fragment case does not preserve its red `(0, 0)` pixel, or Amber reports an execution failure.

**Possible implementation causes:** The script comments identify interruption or termination during zero-divisor calculations as the prohibited outcome. A failure can also arise before validation from the selected shader stage, pipeline, or feature setup. The source does not support treating the unspecified expression values themselves as an expected numeric result.

#### Struct copy or storage-buffer layout

**Possible failure symptoms:** `initialized_struct` retains a nonzero value at one of the four checked byte offsets, or `undefined_memory` reports recipe execution failure.

**Possible implementation causes:** The initialized case depends on the `std430` layout and the assignment of all members of `Bar` into the bound storage buffer. For the uninitialized case, the script has no value comparison, so source-level investigation is needed to distinguish a shader, pipeline, or Amber execution failure.

## Case Pruning

### Requirement-based pruning

- The entire Amber area is absent when Vulkan SC is in use because `createGlslTests()` registers it inside `#ifndef CTS_USES_VULKANSC`. [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287)
- `divbyzero_tesc` and `divbyzero_tese` require `tessellationShader`; `divbyzero_geom` requires `geometryShader`. Missing requirements make the corresponding case unsupported. [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L54-L78) and [`AmberTestCase::checkSupport()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L229-L248)
- Compute-only mode excludes every recipe with a graphics shader. This leaves `divbyzero_comp` eligible and excludes the graphics cases. [`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L557-L569)

### Design-based pruning

- `crash_test` deliberately validates completion rather than the numeric values of zero-divisor and zero-length operations because the scripts identify those values as unspecified.
- `undefined_memory` deliberately has no `EXPECT` command. It does not claim that copying an uninitialized `Bar` yields a portable storage-buffer value.

## Key Takeaways

- This source file is a compact registration layer. Amber scripts hold the behavior that matters: shader code, resources, pipeline commands, and pass conditions.
- `combined_operations` compares defined rendered output, whereas `crash_test` checks safe completion around operations with unspecified results.
- The `crash_test` cases cover vertex, tessellation-control, tessellation-evaluation, geometry, fragment, and compute stages, with feature gating where a stage requires it.
- `logical_copy` separates a checked aggregate assignment from an execution-only uninitialized-local assignment; only `initialized_struct` asserts copied storage-buffer contents.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Amber GLSL family factories | [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L106) | Registers the three test families, their case names, and CTS-side feature requirements. |
| GLSL package registration | [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287) | Places the families below `glsl` only for non-VulkanSC builds. |
| Amber case construction | [`createAmberTestCase()`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L200-L216) | Builds the script path and transfers requirements. |
| Amber parsing, compilation, and execution | [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L615) | Parses recipes, builds GLSL programs, runs Amber, and maps its result to CTS pass or fail. |
| Combined-operation scripts | [`combined_operations`](../../../data/vulkan/amber/combined_operations) | Defines the two graphics expression cases and framebuffer checks. |
| Crash-test scripts | [`crash_test`](../../../data/vulkan/amber/crash_test) | Defines the stage-specific robustness cases, sentinels, and feature declarations. |
| Logical-copy scripts | [`logical_copy`](../../../data/vulkan/amber/logical_copy) | Defines the storage-buffer struct-assignment cases. |
