## Overview

**Core question:** Does a fragment helper invocation preserve a sampled value through a local store and later load?

- This page documents the singular `glsl.helper_invocation` family implemented in `vktShaderRenderHelperInvocationTests.cpp`.
- Each case samples a 16×16 floating-point texture, stores the sample in a 32-element local array, loads it back, and compares quad-neighbour values.
- The five registered variants place that round trip in straight-line code, a quad-uniform divergent branch, a quad-uniform loop, an explicit-gradient sample, or a function call.
- This is separate from the plural `glsl.helper_invocations` shader-executor family.

## Background Knowledge

- A fragment helper invocation exists to support derivative-dependent fragment operations. Vulkan specifies that helper invocations remain active for instructions needed by execution paths that are not exclusive to helpers, while their stores and atomics must not affect memory. See [Vulkan shaders](https://github.com/KhronosGroup/Vulkan-Docs/blob/main/chapters/shaders.adoc#L3738-L3760).
- Subgroup quad operations broadcast a value from one of four quad lanes. The test uses these broadcasts to compare each lane's loaded value with the texture value addressed by the broadcast coordinate.
- `gl_HelperInvocation` reports whether an invocation is a helper. The test records the broadcast bit separately from the value comparison, so it can reject a run that never exercised a helper lane.

## Registration Hierarchy

```text
glsl.helper_invocation
├── load_after_store
├── load_after_store_divergent
├── load_after_store_loop
├── load_after_store_derivative
└── load_after_store_function
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `load_after_store`, `load_after_store_divergent`, `load_after_store_loop`, `load_after_store_derivative`, `load_after_store_function` | Selects where the sample/store/load sequence executes. | [createHelperInvocationTests](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L554-L562) |
| Render and texture extent | `16 × 16` | Gives one result slot per rendered pixel and a matching source texel. | [render dimensions](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L69-L73), [image setup](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L183-L205) |
| Local array length | `32` | Makes the indexed round trip observable and avoids a trivial one-element local. | [array constants](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L69-L73), [generated block](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L92-L116) |
| Fragment shader target | SPIR-V 1.3 | Fixes the generated shader compilation target. | [shader build options](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L527-L548) |

## Behavior Parameters

The test-case leaf is the primary behavioral axis.

### `load_after_store` — straight-line round trip

The fragment shader samples with `texture`, writes the value at a coordinate-derived index in `scratch[32]`, finds that index with a second loop, and assigns the loaded value to `loaded`.

### `load_after_store_divergent` — neighbouring quad branch

The shader selects one of two identical round-trip blocks from `(gl_FragCoord.xy / 2)`. The branch stays uniform within a quad while different quads choose different paths.

### `load_after_store_loop` — quad-uniform data-dependent loop

The trip count is `1 + (quadId.x & 3)`, so all lanes in a quad enter the same number of iterations while neighbouring quads differ.

### `load_after_store_derivative` — explicit-gradient sample

The sample uses `textureGrad(u_tex, uv, dFdx(uv), dFdy(uv))`, exercising the derivative-dependent operation explicitly before the local store/load round trip.

### `load_after_store_function` — function boundary

The round trip executes inside `roundTrip(vec2 uv)` and returns its local `loaded` value to `main`.

## Shader Analysis

The walkthrough below reconstructs the registered `load_after_store` fragment case. The other leaves change only the sample context described above; the verification tail and host-side oracle remain shared.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.helper_invocation.load_after_store
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `load_after_store` | Straight-line sample, local-array store, and indexed load. |
| `16 × 16` render and texture extent | One result slot per rendered pixel and matching source texel. |
| `32 vec4` local scratch array | Keeps the indexed round trip observable. |

#### Purpose

The shader asks whether a helper lane can continue through the sampling and local-array load path, while neighbouring lanes verify the loaded value.

#### Structural Design

| Phase | Shader operation | Purpose |
|---|---|---|
| Input | `gl_FragCoord` to `uv` | Selects the source texel. |
| Round trip | Sample, store, load | Tests the value path. |
| Quad check | Four broadcasts | Compares neighbouring lanes. |
| Report | Result bits | Exposes pass and helper coverage. |

#### Shader Code

```glsl
#version 450
#extension GL_KHR_shader_subgroup_basic : require
#extension GL_KHR_shader_subgroup_quad : require
layout(location = 0) out vec4 o_color;
layout(set = 0, binding = 0) uniform sampler2D u_tex;
layout(set = 0, binding = 1) buffer ResultBlock { uint results[]; };
void main (void)
{
    const vec2 fbSize = vec2(16.0, 16.0);
    vec2 uv = gl_FragCoord.xy / fbSize;
    vec4 sampled = texture(u_tex, uv);
    vec4 scratch[32];
    for (int i = 0; i < 32; ++i) scratch[i] = vec4(float(i) - 13.0);
    uint sx = uint(gl_FragCoord.x); uint sy = uint(gl_FragCoord.y);
    int storeIdx = int((sx * 7u + sy * 13u + 1u) % 32u);
    scratch[storeIdx] = sampled;
    int loadIdx = 0;
    for (int i = 0; i < 32; ++i) if (i == storeIdx) loadIdx = i;
    vec4 loaded = scratch[loadIdx];
    bool ok = true; uint helperBits = 0u;
    // The generated source expands this same check for lanes 0, 1, 2, and 3.
    for (uint lane = 0u; lane < 4u; ++lane) {
        vec4 laneLoaded = subgroupQuadBroadcast(loaded, lane);
        vec4 laneCoord = subgroupQuadBroadcast(gl_FragCoord, lane);
        helperBits |= subgroupQuadBroadcast(uint(gl_HelperInvocation), lane);
        ivec2 lanePix = clamp(ivec2(laneCoord.xy), ivec2(0), ivec2(15));
        vec4 expected = texelFetch(u_tex, lanePix, 0);
        if (any(greaterThan(abs(laneLoaded - expected), vec4(0.01)))) ok = false;
    }
    uint idx = uint(gl_FragCoord.y) * 16u + uint(gl_FragCoord.x);
    if (idx < 256u) results[idx] = (ok ? 1u : 0u) | (helperBits != 0u ? 2u : 0u);
    o_color = ok ? vec4(0.0,1.0,0.0,1.0) : vec4(1.0,0.0,0.0,1.0);
}
```

#### Additional Info

- The source generator expands the four lane checks at compile time; the loop in the walkthrough represents that repeated generated structure.
- The fragment shader requires subgroup basic and quad extensions, while support checking requires fragment-stage quad operations and subgroup size at least four. See [support gate](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L448-L455).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| `load_after_store_divergent` | Quad-uniform branch selects one of two round-trip blocks. | [divergent branch](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L502-L510) |
| `load_after_store_loop` | Quad-uniform data-dependent loop surrounds the block. | [loop variant](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L512-L520) |
| `load_after_store_derivative` | Uses `textureGrad` with `dFdx` and `dFdy`. | [derivative variant](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L495-L500) |
| `load_after_store_function` | Moves the round trip into `roundTrip`. | [function variant](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L474-L485) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: frag
- Target SPIRV version: spirv1.3

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 264
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformQuad
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %gl_HelperInvocation %o_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpSourceExtension "GL_KHR_shader_subgroup_quad"
               OpName %main "main"
               OpName %uv "uv"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %sampled "sampled"
               OpName %u_tex "u_tex"
               OpName %i "i"
               OpName %scratch "scratch"
               OpName %sx "sx"
               OpName %sy "sy"
               OpName %storeIdx "storeIdx"
               OpName %loadIdx "loadIdx"
               OpName %i_0 "i"
               OpName %loaded "loaded"
               OpName %ok "ok"
               OpName %helperBits "helperBits"
               OpName %laneLoaded "laneLoaded"
               OpName %laneCoord "laneCoord"
               OpName %gl_HelperInvocation "gl_HelperInvocation"
               OpName %lanePix "lanePix"
               OpName %expected "expected"
               OpName %px "px"
               OpName %py "py"
               OpName %idx "idx"
               OpName %ResultBlock "ResultBlock"
               OpMemberName %ResultBlock 0 "results"
               OpName %_ ""
               OpName %o_color "o_color"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %u_tex Binding 0
               OpDecorate %u_tex DescriptorSet 0
               OpDecorate %gl_HelperInvocation BuiltIn HelperInvocation
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %ResultBlock Block
               OpMemberDecorate %ResultBlock 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %o_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
   %float_16 = OpConstant %float 16
         %16 = OpConstantComposite %v2float %float_16 %float_16
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %20 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %21 = OpTypeSampledImage %20
%_ptr_UniformConstant_21 = OpTypePointer UniformConstant %21
      %u_tex = OpVariable %_ptr_UniformConstant_21 UniformConstant
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
     %int_32 = OpConstant %int 32
       %bool = OpTypeBool
       %uint = OpTypeInt 32 0
    %uint_32 = OpConstant %uint 32
%_arr_v4float_uint_32 = OpTypeArray %v4float %uint_32
%_ptr_Function__arr_v4float_uint_32 = OpTypePointer Function %_arr_v4float_uint_32
   %float_13 = OpConstant %float 13
      %int_1 = OpConstant %int 1
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
     %uint_7 = OpConstant %uint 7
    %uint_13 = OpConstant %uint 13
%_ptr_Function_bool = OpTypePointer Function %bool
       %true = OpConstantTrue %bool
     %uint_3 = OpConstant %uint 3
%_ptr_Input_bool = OpTypePointer Input %bool
%gl_HelperInvocation = OpVariable %_ptr_Input_bool Input
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
        %126 = OpConstantComposite %v2int %int_0 %int_0
     %int_15 = OpConstant %int 15
        %128 = OpConstantComposite %v2int %int_15 %int_15
%float_0_00999999978 = OpConstant %float 0.00999999978
        %140 = OpConstantComposite %v4float %float_0_00999999978 %float_0_00999999978 %float_0_00999999978 %float_0_00999999978
     %v4bool = OpTypeVector %bool 4
      %false = OpConstantFalse %bool
     %uint_2 = OpConstant %uint 2
    %uint_16 = OpConstant %uint 16
   %uint_256 = OpConstant %uint 256
%_runtimearr_uint = OpTypeRuntimeArray %uint
%ResultBlock = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_ResultBlock = OpTypePointer StorageBuffer %ResultBlock
          %_ = OpVariable %_ptr_StorageBuffer_ResultBlock StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
        %260 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
        %261 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %uv = OpVariable %_ptr_Function_v2float Function
    %sampled = OpVariable %_ptr_Function_v4float Function
          %i = OpVariable %_ptr_Function_int Function
    %scratch = OpVariable %_ptr_Function__arr_v4float_uint_32 Function
         %sx = OpVariable %_ptr_Function_uint Function
         %sy = OpVariable %_ptr_Function_uint Function
   %storeIdx = OpVariable %_ptr_Function_int Function
    %loadIdx = OpVariable %_ptr_Function_int Function
        %i_0 = OpVariable %_ptr_Function_int Function
     %loaded = OpVariable %_ptr_Function_v4float Function
         %ok = OpVariable %_ptr_Function_bool Function
 %helperBits = OpVariable %_ptr_Function_uint Function
 %laneLoaded = OpVariable %_ptr_Function_v4float Function
  %laneCoord = OpVariable %_ptr_Function_v4float Function
    %lanePix = OpVariable %_ptr_Function_v2int Function
   %expected = OpVariable %_ptr_Function_v4float Function
         %px = OpVariable %_ptr_Function_uint Function
         %py = OpVariable %_ptr_Function_uint Function
        %idx = OpVariable %_ptr_Function_uint Function
         %13 = OpLoad %v4float %gl_FragCoord
         %14 = OpVectorShuffle %v2float %13 %13 0 1
         %17 = OpFDiv %v2float %14 %16
               OpStore %uv %17
         %24 = OpLoad %21 %u_tex
         %25 = OpLoad %v2float %uv
         %26 = OpImageSampleImplicitLod %v4float %24 %25
               OpStore %sampled %26
               OpStore %i %int_0
               OpBranch %31
         %31 = OpLabel
               OpLoopMerge %33 %34 None
               OpBranch %35
         %35 = OpLabel
         %36 = OpLoad %int %i
         %39 = OpSLessThan %bool %36 %int_32
               OpBranchConditional %39 %32 %33
         %32 = OpLabel
         %45 = OpLoad %int %i
         %46 = OpLoad %int %i
         %47 = OpConvertSToF %float %46
         %49 = OpFSub %float %47 %float_13
         %50 = OpCompositeConstruct %v4float %49 %49 %49 %49
         %51 = OpAccessChain %_ptr_Function_v4float %scratch %45
               OpStore %51 %50
               OpBranch %34
         %34 = OpLabel
         %52 = OpLoad %int %i
         %54 = OpIAdd %int %52 %int_1
               OpStore %i %54
               OpBranch %31
         %33 = OpLabel
         %59 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %60 = OpLoad %float %59
         %61 = OpConvertFToU %uint %60
               OpStore %sx %61
         %64 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %65 = OpLoad %float %64
         %66 = OpConvertFToU %uint %65
               OpStore %sy %66
         %68 = OpLoad %uint %sx
         %70 = OpIMul %uint %68 %uint_7
         %71 = OpLoad %uint %sy
         %73 = OpIMul %uint %71 %uint_13
         %74 = OpIAdd %uint %70 %73
         %75 = OpIAdd %uint %74 %uint_1
         %76 = OpUMod %uint %75 %uint_32
         %77 = OpBitcast %int %76
               OpStore %storeIdx %77
         %78 = OpLoad %int %storeIdx
         %79 = OpLoad %v4float %sampled
         %80 = OpAccessChain %_ptr_Function_v4float %scratch %78
               OpStore %80 %79
               OpStore %loadIdx %int_0
               OpStore %i_0 %int_0
               OpBranch %83
         %83 = OpLabel
               OpLoopMerge %85 %86 None
               OpBranch %87
         %87 = OpLabel
         %88 = OpLoad %int %i_0
         %89 = OpSLessThan %bool %88 %int_32
               OpBranchConditional %89 %84 %85
         %84 = OpLabel
         %90 = OpLoad %int %i_0
         %91 = OpLoad %int %storeIdx
         %92 = OpIEqual %bool %90 %91
               OpSelectionMerge %94 None
               OpBranchConditional %92 %93 %94
         %93 = OpLabel
         %95 = OpLoad %int %i_0
               OpStore %loadIdx %95
               OpBranch %94
         %94 = OpLabel
               OpBranch %86
         %86 = OpLabel
         %96 = OpLoad %int %i_0
         %97 = OpIAdd %int %96 %int_1
               OpStore %i_0 %97
               OpBranch %83
         %85 = OpLabel
         %99 = OpLoad %int %loadIdx
        %100 = OpAccessChain %_ptr_Function_v4float %scratch %99
        %101 = OpLoad %v4float %100
               OpStore %loaded %101
               OpStore %ok %true
               OpStore %helperBits %uint_0
        %107 = OpLoad %v4float %loaded
        %109 = OpGroupNonUniformQuadBroadcast %v4float %uint_3 %107 %uint_0
               OpStore %laneLoaded %109
        %111 = OpLoad %v4float %gl_FragCoord
        %112 = OpGroupNonUniformQuadBroadcast %v4float %uint_3 %111 %uint_0
               OpStore %laneCoord %112
        %115 = OpLoad %bool %gl_HelperInvocation
        %116 = OpSelect %uint %115 %uint_1 %uint_0
        %117 = OpGroupNonUniformQuadBroadcast %uint %uint_3 %116 %uint_0
        %118 = OpLoad %uint %helperBits
        %119 = OpBitwiseOr %uint %118 %117
               OpStore %helperBits %119
        %123 = OpLoad %v4float %laneCoord
        %124 = OpVectorShuffle %v2float %123 %123 0 1
        %125 = OpConvertFToS %v2int %124
        %129 = OpExtInst %v2int %1 SClamp %125 %126 %128
               OpStore %lanePix %129
        %131 = OpLoad %21 %u_tex
        %132 = OpLoad %v2int %lanePix
        %133 = OpImage %20 %131
        %134 = OpImageFetch %v4float %133 %132 Lod %int_0
               OpStore %expected %134
        %135 = OpLoad %v4float %laneLoaded
        %136 = OpLoad %v4float %expected
        %137 = OpFSub %v4float %135 %136
        %138 = OpExtInst %v4float %1 FAbs %137
        %142 = OpFOrdGreaterThan %v4bool %138 %140
        %143 = OpAny %bool %142
               OpSelectionMerge %145 None
               OpBranchConditional %143 %144 %145
        %144 = OpLabel
               OpStore %ok %false
               OpBranch %145
        %145 = OpLabel
        %147 = OpLoad %v4float %loaded
        %148 = OpGroupNonUniformQuadBroadcast %v4float %uint_3 %147 %uint_1
               OpStore %laneLoaded %148
        %149 = OpLoad %v4float %gl_FragCoord
        %150 = OpGroupNonUniformQuadBroadcast %v4float %uint_3 %149 %uint_1
               OpStore %laneCoord %150
        %151 = OpLoad %bool %gl_HelperInvocation
        %152 = OpSelect %uint %151 %uint_1 %uint_0
        %153 = OpGroupNonUniformQuadBroadcast %uint %uint_3 %152 %uint_1
        %154 = OpLoad %uint %helperBits
        %155 = OpBitwiseOr %uint %154 %153
               OpStore %helperBits %155
        %156 = OpLoad %v4float %laneCoord
        %157 = OpVectorShuffle %v2float %156 %156 0 1
        %158 = OpConvertFToS %v2int %157
        %159 = OpExtInst %v2int %1 SClamp %158 %126 %128
               OpStore %lanePix %159
        %160 = OpLoad %21 %u_tex
        %161 = OpLoad %v2int %lanePix
        %162 = OpImage %20 %160
        %163 = OpImageFetch %v4float %162 %161 Lod %int_0
               OpStore %expected %163
        %164 = OpLoad %v4float %laneLoaded
        %165 = OpLoad %v4float %expected
        %166 = OpFSub %v4float %164 %165
        %167 = OpExtInst %v4float %1 FAbs %166
        %168 = OpFOrdGreaterThan %v4bool %167 %140
        %169 = OpAny %bool %168
               OpSelectionMerge %171 None
               OpBranchConditional %169 %170 %171
        %170 = OpLabel
               OpStore %ok %false
               OpBranch %171
        %171 = OpLabel
        %172 = OpLoad %v4float %loaded
        %174 = OpGroupNonUniformQuadBroadcast %v4float %uint_3 %172 %uint_2
               OpStore %laneLoaded %174
        %175 = OpLoad %v4float %gl_FragCoord
        %176 = OpGroupNonUniformQuadBroadcast %v4float %uint_3 %175 %uint_2
               OpStore %laneCoord %176
        %177 = OpLoad %bool %gl_HelperInvocation
        %178 = OpSelect %uint %177 %uint_1 %uint_0
        %179 = OpGroupNonUniformQuadBroadcast %uint %uint_3 %178 %uint_2
        %180 = OpLoad %uint %helperBits
        %181 = OpBitwiseOr %uint %180 %179
               OpStore %helperBits %181
        %182 = OpLoad %v4float %laneCoord
        %183 = OpVectorShuffle %v2float %182 %182 0 1
        %184 = OpConvertFToS %v2int %183
        %185 = OpExtInst %v2int %1 SClamp %184 %126 %128
               OpStore %lanePix %185
        %186 = OpLoad %21 %u_tex
        %187 = OpLoad %v2int %lanePix
        %188 = OpImage %20 %186
        %189 = OpImageFetch %v4float %188 %187 Lod %int_0
               OpStore %expected %189
        %190 = OpLoad %v4float %laneLoaded
        %191 = OpLoad %v4float %expected
        %192 = OpFSub %v4float %190 %191
        %193 = OpExtInst %v4float %1 FAbs %192
        %194 = OpFOrdGreaterThan %v4bool %193 %140
        %195 = OpAny %bool %194
               OpSelectionMerge %197 None
               OpBranchConditional %195 %196 %197
        %196 = OpLabel
               OpStore %ok %false
               OpBranch %197
        %197 = OpLabel
        %198 = OpLoad %v4float %loaded
        %199 = OpGroupNonUniformQuadBroadcast %v4float %uint_3 %198 %uint_3
               OpStore %laneLoaded %199
        %200 = OpLoad %v4float %gl_FragCoord
        %201 = OpGroupNonUniformQuadBroadcast %v4float %uint_3 %200 %uint_3
               OpStore %laneCoord %201
        %202 = OpLoad %bool %gl_HelperInvocation
        %203 = OpSelect %uint %202 %uint_1 %uint_0
        %204 = OpGroupNonUniformQuadBroadcast %uint %uint_3 %203 %uint_3
        %205 = OpLoad %uint %helperBits
        %206 = OpBitwiseOr %uint %205 %204
               OpStore %helperBits %206
        %207 = OpLoad %v4float %laneCoord
        %208 = OpVectorShuffle %v2float %207 %207 0 1
        %209 = OpConvertFToS %v2int %208
        %210 = OpExtInst %v2int %1 SClamp %209 %126 %128
               OpStore %lanePix %210
        %211 = OpLoad %21 %u_tex
        %212 = OpLoad %v2int %lanePix
        %213 = OpImage %20 %211
        %214 = OpImageFetch %v4float %213 %212 Lod %int_0
               OpStore %expected %214
        %215 = OpLoad %v4float %laneLoaded
        %216 = OpLoad %v4float %expected
        %217 = OpFSub %v4float %215 %216
        %218 = OpExtInst %v4float %1 FAbs %217
        %219 = OpFOrdGreaterThan %v4bool %218 %140
        %220 = OpAny %bool %219
               OpSelectionMerge %222 None
               OpBranchConditional %220 %221 %222
        %221 = OpLabel
               OpStore %ok %false
               OpBranch %222
        %222 = OpLabel
        %224 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
        %225 = OpLoad %float %224
        %226 = OpConvertFToU %uint %225
               OpStore %px %226
        %228 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
        %229 = OpLoad %float %228
        %230 = OpConvertFToU %uint %229
               OpStore %py %230
        %232 = OpLoad %uint %py
        %234 = OpIMul %uint %232 %uint_16
        %235 = OpLoad %uint %px
        %236 = OpIAdd %uint %234 %235
               OpStore %idx %236
        %237 = OpLoad %uint %idx
        %239 = OpULessThan %bool %237 %uint_256
               OpSelectionMerge %241 None
               OpBranchConditional %239 %240 %241
        %240 = OpLabel
        %246 = OpLoad %uint %idx
        %247 = OpLoad %bool %ok
        %248 = OpSelect %uint %247 %uint_1 %uint_0
        %249 = OpLoad %uint %helperBits
        %250 = OpINotEqual %bool %249 %uint_0
        %251 = OpSelect %uint %250 %uint_2 %uint_0
        %252 = OpBitwiseOr %uint %248 %251
        %254 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0 %246
               OpStore %254 %252
               OpBranch %241
        %241 = OpLabel
        %257 = OpLoad %bool %ok
        %262 = OpCompositeConstruct %v4bool %257 %257 %257 %257
        %263 = OpSelect %v4float %262 %260 %261
               OpStore %o_color %263
               OpReturn
               OpFunctionEnd

```

</details>

## Runtime Execution and Result Checking

- The host creates a 16×16 `R32G32B32A32_SFLOAT` sampled image and fills each texel with `(x, y, 0.5x - 0.25y, 1.0)`.
- A host-visible result buffer contains one `uint32_t` sentinel per pixel. The fragment shader writes bit 0 for a successful quad comparison and bit 1 when a quad observed a helper invocation.
- The draw covers the render target with one triangle. A fragment-to-host buffer barrier makes shader writes visible before readback.
- The host ignores untouched sentinel entries, rejects any failed comparison, rejects a run with no shaded fragments, and rejects a run with no helper observations. Otherwise it returns `Pass`. See [execution and oracle](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L364-L422).

## Failure Meaning

### Failure Cause Mapping

| Observed result | Meaning | Likely area to inspect |
|---|---|---|
| A result has bit 0 clear | A quad-broadcast loaded value differed from the source texel by more than `0.01`. | Fragment helper-invocation execution, subgroup quad operations, texture sampling, or local-array load handling. |
| No shaded fragments | The draw produced no fragment results. | Render pass, pipeline, viewport/scissor, or command submission setup. |
| No helper observations | The implementation did not generate a helper lane for this draw, so the intended helper-load property was not exercised. | Fragment coverage, derivative/helper-invocation generation, or implementation scheduling. |
| All checked results pass | The observed helper lanes preserved the sampled value through the tested load path. | The five variants share this oracle; a pass does not distinguish which internal implementation strategy was used. |

### Cause Analysis

#### Interpreting the result bits

**Possible failure symptoms:** A comparison bit can clear, or the helper-coverage bit can remain clear.

**Possible implementation causes:** Fragment helper execution, subgroup quad operations, texture sampling, or local-array load handling can differ from the test assumption.

The test separates value correctness from coverage. Bit 0 checks the quad-neighbour value, while bit 1 proves that at least one helper invocation participated in the quad broadcasts. A failure in either condition has a different interpretation from an untouched result slot.

## Case Pruning

### Requirement-based pruning

The case is skipped when fragment-stage quad subgroup operations are unavailable or when the subgroup size is below four. The test needs four lanes to address a subgroup quad.

### Design-based pruning

The five leaves are not interchangeable: the branch, loop, derivative, and function cases exercise distinct shader-generation contexts around the same load oracle. The test does not claim coverage for other shader stages or for plural `glsl.helper_invocations` cases.

## Key Takeaways

- The singular family targets helper-invocation continuity through a local array load after a sampled value is stored.
- Quad broadcasts let the fragment shader compare each lane against a coordinate-associated `texelFetch` value.
- The host requires both a correct value comparison and evidence that a helper invocation occurred.
- Support gates are fragment quad operations and subgroup size at least four.

## Source Reference Appendix

- [Registration and variants](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L425-L561)
- [Texture initialization and render resources](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L183-L357)
- [Command submission and result verification](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderHelperInvocationTests.cpp#L364-L422)
- [Mustpass VK paths](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/mustpass/main/vk-default/glsl.txt#L8448-L8452)
- [Mustpass Vulkan SC paths](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/mustpass/main/vksc-default/glsl.txt#L7057-L7061)
