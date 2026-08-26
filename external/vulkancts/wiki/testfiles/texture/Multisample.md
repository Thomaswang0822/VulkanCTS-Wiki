## Overview

**Core question:** Do multisample storage-image operations address the intended sample and preserve valid samples when a shader also issues out-of-range sample writes?

- `texture.multisample` is a Vulkan-only Amber family with two direct children: `atomic` and `invalid_sample_index`.
- The atomic cases apply integer atomics to each of four samples, then compare shader-read values with a scripted oracle.
- The invalid-index cases issue sample operands from -256 through 255 and check the values stored at valid sample indices.
- Two unresolved test defects remain in the source: the R64 atomic oracle does not match the operation sequence, and the invalid-index cases rely on robust image-write behavior without enabling robust image access.

## Background Knowledge

- A multisample image stores several values for each `(x,y)` texel. Storage-image instructions include a sample operand, so `(x,y,sample)` identifies the accessed value.
- [`Image Coordinate Validation`](../../../../vulkan-docs/src/chapters/images.adoc#L42-L103) treats the sample operand as an image coordinate and compares it with the image sample count.
- Robust image access is required for predictable results from out-of-bounds storage-image writes. Without it, [`Shader Out-of-Bounds Memory Access`](../../../../vulkan-docs/src/chapters/shaders.adoc#L1871-L1921) says applications must not execute out-of-bounds accesses.
- The default CTS device disables core and extension image robustness in [`DeviceFeatures`](../../../framework/vulkan/vkDeviceFeatures.cpp#L210-L234). These cases request `shaderStorageImageMultisample`, but not a robust image access feature.

## Registration Hierarchy

```text
texture.multisample
├── atomic (non-VulkanSC only)
└── invalid_sample_index (non-VulkanSC only)
```

The dispatcher omits `multisample` from Vulkan SC. The `atomic` function has an additional local Vulkan SC guard; `invalid_sample_index` relies on the dispatcher guard.

## Parameter Dimensions and Observed Values

| Dimension | Observed values | Effect |
|-----------|-----------------|--------|
| Test family | `atomic`, `invalid_sample_index` | Selects atomic read-modify-write testing or mixed valid/out-of-range sample writes. |
| Atomic format | `R32_SINT`, `R32_UINT`, `R64_SINT`, `R64_UINT` | Selects signedness and integer width. R64 also requires `shaderInt64`. |
| Atomic sample count | 4 | Every atomic case operates on samples 0 through 3. |
| Invalid-index sample count | 2, 4, 8, 16, 32, 64 | Sets the valid interval `[0,numSamples)` while the issued range stays -256 through 255. |
| Image extent | 64x64 for atomic; 16x16 for invalid-index | Matches the dispatch coverage and Amber result expectation. |
| Shader stage | compute | Both families use GLSL 4.30 compute shaders with 16x16 local size. |

## Behavior Parameters

The direct test family is the primary behavior parameter.

### `atomic`: per-sample image atomics

Four cases use a four-sample integer storage image. Each invocation initializes its own texel; its mirrored partner addresses that texel in the paired atomic sequence. The invocation's own add contributes `id`, the mirrored invocation contributes `partnerId`, and the initial value already contains `id`, yielding `s + 2*id + partnerId` before the bit masks. The R32 expression therefore matches the operations. Both R64 scripts instead use `0x0a00000000000000` in the expected expression, even though the OR operations set the top bits and the XOR masks produce `0xcc00000000000000`; this is an unresolved source-level oracle defect.

### `invalid_sample_index`: mixed valid and invalid sample writes

Six cases create an RGBA8 multisample image with 2 to 64 samples. One invocation per texel writes sample operands from -256 through 255. Valid indices receive a repeating color table; invalid indices receive white. The shader limits its reads to valid samples and emits green if they still equal the assigned colors.

The script comments say invalid writes should be discarded, but the registration requests `shaderStorageImageMultisample` and no robust image access feature. The default CTS device disables robust image access, so the test does not establish the specification condition that guarantees those writes cannot modify memory. This is an unresolved source-level conformance-claim defect.

## Shader Analysis

The first walkthrough follows the atomic instruction path; the second follows invalid sample writes. Both shader sources come from Amber, and the common Amber path compiles them as SPIR-V 1.0.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen


Representative path:

```text
dEQP-VK.texture.multisample.atomic.storage_image_r32ui
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `atomic` | Selects per-sample integer storage-image atomic operations. |
| `storage_image_r32ui` | Uses an `r32ui` four-sample image and 32-bit unsigned atomic values. |
| 4 samples | The shader initializes and checks samples 0 through 3. |
| 4x4 workgroups, 16x16 local invocations | Covers the 64x64 image with one invocation per texel. |

#### Purpose

This walkthrough isolates the shader behavior exercised by the selected representative case.

#### Structural Design


| Phase | Shader operation | Validation signal |
|-------|------------------|-------------------|
| Initialize | Store `sample + id` into each of four samples. | Gives every texel/sample a deterministic starting value. |
| Synchronize | Use image memory barriers and workgroup barriers. | Orders paired atomic operations and subsequent reads. |
| Mutate | Apply add, min/max, AND, OR, and XOR atomics at mirrored texels. | Exercises the multisample storage-image atomic path. |
| Verify | Compare all four samples with the expected expression. | Write green on success and red on mismatch. |

#### Shader Code

```glsl
#version 430

layout(local_size_x = 16, local_size_y = 16) in;
uniform layout(set=0, binding=0, r32ui) uimage2DMS texture;
uniform layout(set=0, binding=1, rgba8) image2D result;

void main()
{
    ivec2 loc = ivec2(gl_LocalInvocationID.xy);
    // Partner location is a mirror in local workgroup space.
    ivec2 partnerLoc = ivec2(15) - loc;
    uint id = loc.y * 16 + loc.x;
    uint partnerId = partnerLoc.y * 16 + partnerLoc.x;
    ivec2 workGroupOffset = ivec2(gl_WorkGroupID.xy) * ivec2(16);

    // Initialize texture with id + sample id
    for (int s = 0; s < 4; s++)
        imageStore(texture, loc + workGroupOffset, s, uvec4(s + id));

    memoryBarrierImage();
    barrier();

    for (int s = 0; s < 4; s++)
    {
        // Add id to both location and partner location.
        imageAtomicAdd(texture, loc + workGroupOffset, s, id);
        imageAtomicAdd(texture, partnerLoc + workGroupOffset, s, id);

        // Set MSB for location and the second MSB for partner.
        imageAtomicOr(texture, loc + workGroupOffset, s, 1u << 31);
        imageAtomicOr(texture, partnerLoc + workGroupOffset, s, 1u << 30);
    }

    memoryBarrierImage();
    barrier();

    for (int s = 0; s < 4; s++)
    {
        // XOR with two patterns in the second highest byte. Should set this
        // byte to 0xc. The order of XOR operations don't matter.
        imageAtomicXor(texture, loc + workGroupOffset, s, 0x0a000000);
        imageAtomicXor(texture, partnerLoc + workGroupOffset, s, 0x06000000);
    }

    memoryBarrierImage();
    barrier();

    for (int s = 0; s < 4; s++)
    {
        // Finally mask out one of LSBs based on sample
        imageAtomicAnd(texture, loc + workGroupOffset, s, ~(1u << s));
    }

    // Verification
    bool ok = true;

    for (int s = 0; s < 4; s++)
    {
        if (imageLoad(texture, loc + workGroupOffset, s).r != (((s + id * 2 + partnerId) | 0xcc000000) & ~(1u << s)))
            ok = false;
    }

    vec4 color = ok ? vec4(0, 1, 0, 1) : vec4(1, 0, 0, 1);
    imageStore(result, loc + workGroupOffset, color);
}
```

The shader pairs each local invocation with its mirror around `(15,15)`. Each phase targets an `OpImageTexelPointer` for one sample and applies atomics, with an image memory barrier and workgroup barrier between dependent phases. The final load compares all four samples before writing a green or red result pixel.

#### Additional Info


- The representative source is the Amber [`storage_image_r32ui.amber`](../../../data/vulkan/amber/texture/multisample/atomic/storage_image_r32ui.amber) compute shader.
- Four 16x16 workgroups cover the 64x64 image, and the shader validates all four samples before writing the result image.
- The R32 unsigned case uses the operation-consistent oracle; the separate R64 scripts have the source-level oracle defect documented earlier on this page.

#### Parameter Variation Summary


| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Integer format | Signed and unsigned 32-bit cases change image type and atomic operand type; 64-bit cases use 64-bit integer image atomics and require `shaderInt64`. | [case registration](../../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L38-L156) |
| Atomic script | Each registered format selects its corresponding Amber shader while retaining four samples and the paired atomic sequence. | [representative R32 script](../../../data/vulkan/amber/texture/multisample/atomic/storage_image_r32ui.amber) |

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
; Bound: 223
; Schema: 0
               OpCapability Shader
               OpCapability StorageImageMultisample
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationID %gl_WorkGroupID
               OpExecutionMode %main LocalSize 16 16 1
               OpSource GLSL 430
               OpName %main "main"
               OpName %loc "loc"
               OpName %gl_LocalInvocationID "gl_LocalInvocationID"
               OpName %partnerLoc "partnerLoc"
               OpName %id "id"
               OpName %partnerId "partnerId"
               OpName %workGroupOffset "workGroupOffset"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %s "s"
               OpName %texture "texture"
               OpName %s_0 "s"
               OpName %s_1 "s"
               OpName %s_2 "s"
               OpName %ok "ok"
               OpName %s_3 "s"
               OpName %color "color"
               OpName %result "result"
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %texture Binding 0
               OpDecorate %texture DescriptorSet 0
               OpDecorate %result Binding 1
               OpDecorate %result DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
     %int_15 = OpConstant %int 15
         %20 = OpConstantComposite %v2int %int_15 %int_15
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_1 = OpConstant %uint 1
%_ptr_Function_int = OpTypePointer Function %int
     %int_16 = OpConstant %int 16
     %uint_0 = OpConstant %uint 0
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
         %49 = OpConstantComposite %v2int %int_16 %int_16
      %int_0 = OpConstant %int 0
      %int_4 = OpConstant %int 4
       %bool = OpTypeBool
         %62 = OpTypeImage %uint 2D 0 0 1 2 R32ui
%_ptr_UniformConstant_62 = OpTypePointer UniformConstant %62
    %texture = OpVariable %_ptr_UniformConstant_62 UniformConstant
     %v4uint = OpTypeVector %uint 4
      %int_1 = OpConstant %int 1
  %uint_2056 = OpConstant %uint 2056
     %uint_2 = OpConstant %uint 2
   %uint_264 = OpConstant %uint 264
%_ptr_Image_uint = OpTypePointer Image %uint
%uint_2147483648 = OpConstant %uint 2147483648
%uint_1073741824 = OpConstant %uint 1073741824
%uint_167772160 = OpConstant %uint 167772160
%uint_100663296 = OpConstant %uint 100663296
%_ptr_Function_bool = OpTypePointer Function %bool
       %true = OpConstantTrue %bool
%uint_3422552064 = OpConstant %uint 3422552064
      %false = OpConstantFalse %bool
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
        %208 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
        %209 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
     %v4bool = OpTypeVector %bool 4
        %213 = OpTypeImage %float 2D 0 0 0 2 Rgba8
%_ptr_UniformConstant_213 = OpTypePointer UniformConstant %213
     %result = OpVariable %_ptr_UniformConstant_213 UniformConstant
    %uint_16 = OpConstant %uint 16
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_16 %uint_16 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
        %loc = OpVariable %_ptr_Function_v2int Function
 %partnerLoc = OpVariable %_ptr_Function_v2int Function
         %id = OpVariable %_ptr_Function_uint Function
  %partnerId = OpVariable %_ptr_Function_uint Function
%workGroupOffset = OpVariable %_ptr_Function_v2int Function
          %s = OpVariable %_ptr_Function_int Function
        %s_0 = OpVariable %_ptr_Function_int Function
        %s_1 = OpVariable %_ptr_Function_int Function
        %s_2 = OpVariable %_ptr_Function_int Function
         %ok = OpVariable %_ptr_Function_bool Function
        %s_3 = OpVariable %_ptr_Function_int Function
      %color = OpVariable %_ptr_Function_v4float Function
         %15 = OpLoad %v3uint %gl_LocalInvocationID
         %16 = OpVectorShuffle %v2uint %15 %15 0 1
         %17 = OpBitcast %v2int %16
               OpStore %loc %17
         %21 = OpLoad %v2int %loc
         %22 = OpISub %v2int %20 %21
               OpStore %partnerLoc %22
         %27 = OpAccessChain %_ptr_Function_int %loc %uint_1
         %28 = OpLoad %int %27
         %30 = OpIMul %int %28 %int_16
         %32 = OpAccessChain %_ptr_Function_int %loc %uint_0
         %33 = OpLoad %int %32
         %34 = OpIAdd %int %30 %33
         %35 = OpBitcast %uint %34
               OpStore %id %35
         %37 = OpAccessChain %_ptr_Function_int %partnerLoc %uint_1
         %38 = OpLoad %int %37
         %39 = OpIMul %int %38 %int_16
         %40 = OpAccessChain %_ptr_Function_int %partnerLoc %uint_0
         %41 = OpLoad %int %40
         %42 = OpIAdd %int %39 %41
         %43 = OpBitcast %uint %42
               OpStore %partnerId %43
         %46 = OpLoad %v3uint %gl_WorkGroupID
         %47 = OpVectorShuffle %v2uint %46 %46 0 1
         %48 = OpBitcast %v2int %47
         %50 = OpIMul %v2int %48 %49
               OpStore %workGroupOffset %50
               OpStore %s %int_0
               OpBranch %53
         %53 = OpLabel
               OpLoopMerge %55 %56 None
               OpBranch %57
         %57 = OpLabel
         %58 = OpLoad %int %s
         %61 = OpSLessThan %bool %58 %int_4
               OpBranchConditional %61 %54 %55
         %54 = OpLabel
         %65 = OpLoad %62 %texture
         %66 = OpLoad %v2int %loc
         %67 = OpLoad %v2int %workGroupOffset
         %68 = OpIAdd %v2int %66 %67
         %69 = OpLoad %int %s
         %70 = OpLoad %int %s
         %71 = OpBitcast %uint %70
         %72 = OpLoad %uint %id
         %73 = OpIAdd %uint %71 %72
         %75 = OpCompositeConstruct %v4uint %73 %73 %73 %73
               OpImageWrite %65 %68 %75 Sample %69
               OpBranch %56
         %56 = OpLabel
         %76 = OpLoad %int %s
         %78 = OpIAdd %int %76 %int_1
               OpStore %s %78
               OpBranch %53
         %55 = OpLabel
               OpMemoryBarrier %uint_1 %uint_2056
               OpControlBarrier %uint_2 %uint_2 %uint_264
               OpStore %s_0 %int_0
               OpBranch %83
         %83 = OpLabel
               OpLoopMerge %85 %86 None
               OpBranch %87
         %87 = OpLabel
         %88 = OpLoad %int %s_0
         %89 = OpSLessThan %bool %88 %int_4
               OpBranchConditional %89 %84 %85
         %84 = OpLabel
         %90 = OpLoad %v2int %loc
         %91 = OpLoad %v2int %workGroupOffset
         %92 = OpIAdd %v2int %90 %91
         %93 = OpLoad %int %s_0
         %94 = OpLoad %uint %id
         %96 = OpImageTexelPointer %_ptr_Image_uint %texture %92 %93
         %97 = OpAtomicIAdd %uint %96 %uint_1 %uint_0 %94
         %98 = OpLoad %v2int %partnerLoc
         %99 = OpLoad %v2int %workGroupOffset
        %100 = OpIAdd %v2int %98 %99
        %101 = OpLoad %int %s_0
        %102 = OpLoad %uint %id
        %103 = OpImageTexelPointer %_ptr_Image_uint %texture %100 %101
        %104 = OpAtomicIAdd %uint %103 %uint_1 %uint_0 %102
        %105 = OpLoad %v2int %loc
        %106 = OpLoad %v2int %workGroupOffset
        %107 = OpIAdd %v2int %105 %106
        %108 = OpLoad %int %s_0
        %110 = OpImageTexelPointer %_ptr_Image_uint %texture %107 %108
        %111 = OpAtomicOr %uint %110 %uint_1 %uint_0 %uint_2147483648
        %112 = OpLoad %v2int %partnerLoc
        %113 = OpLoad %v2int %workGroupOffset
        %114 = OpIAdd %v2int %112 %113
        %115 = OpLoad %int %s_0
        %117 = OpImageTexelPointer %_ptr_Image_uint %texture %114 %115
        %118 = OpAtomicOr %uint %117 %uint_1 %uint_0 %uint_1073741824
               OpBranch %86
         %86 = OpLabel
        %119 = OpLoad %int %s_0
        %120 = OpIAdd %int %119 %int_1
               OpStore %s_0 %120
               OpBranch %83
         %85 = OpLabel
               OpMemoryBarrier %uint_1 %uint_2056
               OpControlBarrier %uint_2 %uint_2 %uint_264
               OpStore %s_1 %int_0
               OpBranch %122
        %122 = OpLabel
               OpLoopMerge %124 %125 None
               OpBranch %126
        %126 = OpLabel
        %127 = OpLoad %int %s_1
        %128 = OpSLessThan %bool %127 %int_4
               OpBranchConditional %128 %123 %124
        %123 = OpLabel
        %129 = OpLoad %v2int %loc
        %130 = OpLoad %v2int %workGroupOffset
        %131 = OpIAdd %v2int %129 %130
        %132 = OpLoad %int %s_1
        %134 = OpImageTexelPointer %_ptr_Image_uint %texture %131 %132
        %135 = OpAtomicXor %uint %134 %uint_1 %uint_0 %uint_167772160
        %136 = OpLoad %v2int %partnerLoc
        %137 = OpLoad %v2int %workGroupOffset
        %138 = OpIAdd %v2int %136 %137
        %139 = OpLoad %int %s_1
        %141 = OpImageTexelPointer %_ptr_Image_uint %texture %138 %139
        %142 = OpAtomicXor %uint %141 %uint_1 %uint_0 %uint_100663296
               OpBranch %125
        %125 = OpLabel
        %143 = OpLoad %int %s_1
        %144 = OpIAdd %int %143 %int_1
               OpStore %s_1 %144
               OpBranch %122
        %124 = OpLabel
               OpMemoryBarrier %uint_1 %uint_2056
               OpControlBarrier %uint_2 %uint_2 %uint_264
               OpStore %s_2 %int_0
               OpBranch %146
        %146 = OpLabel
               OpLoopMerge %148 %149 None
               OpBranch %150
        %150 = OpLabel
        %151 = OpLoad %int %s_2
        %152 = OpSLessThan %bool %151 %int_4
               OpBranchConditional %152 %147 %148
        %147 = OpLabel
        %153 = OpLoad %v2int %loc
        %154 = OpLoad %v2int %workGroupOffset
        %155 = OpIAdd %v2int %153 %154
        %156 = OpLoad %int %s_2
        %157 = OpLoad %int %s_2
        %158 = OpShiftLeftLogical %uint %uint_1 %157
        %159 = OpNot %uint %158
        %160 = OpImageTexelPointer %_ptr_Image_uint %texture %155 %156
        %161 = OpAtomicAnd %uint %160 %uint_1 %uint_0 %159
               OpBranch %149
        %149 = OpLabel
        %162 = OpLoad %int %s_2
        %163 = OpIAdd %int %162 %int_1
               OpStore %s_2 %163
               OpBranch %146
        %148 = OpLabel
               OpStore %ok %true
               OpStore %s_3 %int_0
               OpBranch %168
        %168 = OpLabel
               OpLoopMerge %170 %171 None
               OpBranch %172
        %172 = OpLabel
        %173 = OpLoad %int %s_3
        %174 = OpSLessThan %bool %173 %int_4
               OpBranchConditional %174 %169 %170
        %169 = OpLabel
        %175 = OpLoad %62 %texture
        %176 = OpLoad %v2int %loc
        %177 = OpLoad %v2int %workGroupOffset
        %178 = OpIAdd %v2int %176 %177
        %179 = OpLoad %int %s_3
        %180 = OpImageRead %v4uint %175 %178 Sample %179
        %181 = OpCompositeExtract %uint %180 0
        %182 = OpLoad %int %s_3
        %183 = OpBitcast %uint %182
        %184 = OpLoad %uint %id
        %185 = OpIMul %uint %184 %uint_2
        %186 = OpIAdd %uint %183 %185
        %187 = OpLoad %uint %partnerId
        %188 = OpIAdd %uint %186 %187
        %190 = OpBitwiseOr %uint %188 %uint_3422552064
        %191 = OpLoad %int %s_3
        %192 = OpShiftLeftLogical %uint %uint_1 %191
        %193 = OpNot %uint %192
        %194 = OpBitwiseAnd %uint %190 %193
        %195 = OpINotEqual %bool %181 %194
               OpSelectionMerge %197 None
               OpBranchConditional %195 %196 %197
        %196 = OpLabel
               OpStore %ok %false
               OpBranch %197
        %197 = OpLabel
               OpBranch %171
        %171 = OpLabel
        %199 = OpLoad %int %s_3
        %200 = OpIAdd %int %199 %int_1
               OpStore %s_3 %200
               OpBranch %168
        %170 = OpLabel
        %205 = OpLoad %bool %ok
        %211 = OpCompositeConstruct %v4bool %205 %205 %205 %205
        %212 = OpSelect %v4float %211 %208 %209
               OpStore %color %212
        %216 = OpLoad %213 %result
        %217 = OpLoad %v2int %loc
        %218 = OpLoad %v2int %workGroupOffset
        %219 = OpIAdd %v2int %217 %218
        %220 = OpLoad %v4float %color
               OpImageWrite %216 %219 %220
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen


Representative path:

```text
dEQP-VK.texture.multisample.invalid_sample_index.sample_count_4
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `invalid_sample_index` | Selects mixed valid and out-of-range multisample image writes. |
| `sample_count_4` | Makes sample operands 0 through 3 valid. |
| `R8G8B8A8_UNORM` | Stores the repeating RGBA color table used for valid-sample verification. |
| Sample operands -256 through 255 | Exercises a fixed broad range while reads remain limited to valid samples. |

#### Purpose

This walkthrough isolates the shader behavior exercised by the selected representative case.

#### Structural Design


| Phase | Shader operation | Validation signal |
|-------|------------------|-------------------|
| Write sweep | Issue `imageStore` for sample operands from -256 through 255. | Valid samples receive indexed colors; invalid operands receive white. |
| Synchronize | Apply image and workgroup barriers. | Orders writes before valid-sample reads. |
| Verify | Read only samples 0 through 3 and compare with the expected colors. | Write green if every valid sample is preserved, otherwise red. |

#### Shader Code

```glsl
#version 430

layout(local_size_x = 16, local_size_y = 16) in;

uniform layout(set=0, binding=0, rgba8) image2DMS texture;
uniform layout(set=0, binding=1, rgba8) image2D result;


void main()
{
    int numSamples = 4;
    int distortion = 256;
    vec4 ndxColors[4];

    ndxColors[0] = vec4(1.0, 0.0, 0.0, 1.0);
    ndxColors[1] = vec4(0.0, 1.0, 0.0, 1.0);
    ndxColors[2] = vec4(0.0, 0.0, 1.0, 1.0);
    ndxColors[3] = vec4(0.0, 1.0, 1.0, 1.0);

    ivec2 uv = ivec2(gl_GlobalInvocationID.xy);

    // Initialize texture
    for (int s = -distortion; s < distortion; s++)
    {
        vec4 color = vec4(1);

        if (s >= 0 && s < numSamples) color = ndxColors[s % 4];

        imageStore(texture, uv, s, color);
    }

    memoryBarrierImage();
    barrier();

    // Verification
    bool imageOk = true;

    for (int s = 0; s < numSamples; s++)
    {
        vec4 color = vec4(1);

        if (s >= 0 && s < numSamples) color = ndxColors[s % 4];

        if (imageLoad(texture, uv, s) != color)
            imageOk = false;
    }

    vec4 resultColor = imageOk ? vec4(0, 1, 0, 1) : vec4(1, 0, 0, 1);
    imageStore(result, uv, resultColor);
}
```

The first loop emits `OpImageWrite` with the dynamic sample operand. The second loop limits its reads to samples 0 through 3 and compares them with the valid color table. The test therefore observes whether the valid samples match the color table. It still lacks the robustness guarantee required for the out-of-range writes.

#### Additional Info


- The representative source is [`sample_count_4.amber`](../../../data/vulkan/amber/texture/multisample/invalidsampleindex/sample_count_4.amber).
- The issued operand range remains -256 through 255 for every leaf; the registered sample count changes only the valid interval and loop bound.
- The robustness precondition caveat for invalid writes is documented earlier on this page and is not resolved by the shader-side valid-sample check.

#### Parameter Variation Summary


| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Sample count | Registered leaves use 2, 4, 8, 16, 32, or 64 samples, changing the valid interval and valid-sample verification loop. | [case registration](../../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L38-L156) |
| Issued sample operands | Every leaf retains the -256 through 255 write sweep; only the number of valid operands changes. | [representative sample-count-4 script](../../../data/vulkan/amber/texture/multisample/invalidsampleindex/sample_count_4.amber) |

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
; Bound: 133
; Schema: 0
               OpCapability Shader
               OpCapability StorageImageMultisample
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 16 16 1
               OpSource GLSL 430
               OpName %main "main"
               OpName %numSamples "numSamples"
               OpName %distortion "distortion"
               OpName %ndxColors "ndxColors"
               OpName %uv "uv"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %s "s"
               OpName %color "color"
               OpName %texture "texture"
               OpName %imageOk "imageOk"
               OpName %s_0 "s"
               OpName %color_0 "color"
               OpName %resultColor "resultColor"
               OpName %result "result"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %texture Binding 0
               OpDecorate %texture DescriptorSet 0
               OpDecorate %result Binding 1
               OpDecorate %result DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_4 = OpConstant %int 4
    %int_256 = OpConstant %int 256
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_4 = OpConstant %uint 4
%_arr_v4float_uint_4 = OpTypeArray %v4float %uint_4
%_ptr_Function__arr_v4float_uint_4 = OpTypePointer Function %_arr_v4float_uint_4
      %int_0 = OpConstant %int 0
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
         %22 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
%_ptr_Function_v4float = OpTypePointer Function %v4float
      %int_1 = OpConstant %int 1
         %26 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
      %int_2 = OpConstant %int 2
         %29 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
      %int_3 = OpConstant %int 3
         %32 = OpConstantComposite %v4float %float_0 %float_1 %float_1 %float_1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
       %bool = OpTypeBool
         %57 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
         %70 = OpTypeImage %float 2D 0 0 1 2 Rgba8
%_ptr_UniformConstant_70 = OpTypePointer UniformConstant %70
    %texture = OpVariable %_ptr_UniformConstant_70 UniformConstant
     %uint_1 = OpConstant %uint 1
  %uint_2056 = OpConstant %uint 2056
     %uint_2 = OpConstant %uint 2
   %uint_264 = OpConstant %uint 264
%_ptr_Function_bool = OpTypePointer Function %bool
       %true = OpConstantTrue %bool
     %v4bool = OpTypeVector %bool 4
      %false = OpConstantFalse %bool
        %125 = OpTypeImage %float 2D 0 0 0 2 Rgba8
%_ptr_UniformConstant_125 = OpTypePointer UniformConstant %125
     %result = OpVariable %_ptr_UniformConstant_125 UniformConstant
    %uint_16 = OpConstant %uint 16
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_16 %uint_16 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
 %numSamples = OpVariable %_ptr_Function_int Function
 %distortion = OpVariable %_ptr_Function_int Function
  %ndxColors = OpVariable %_ptr_Function__arr_v4float_uint_4 Function
         %uv = OpVariable %_ptr_Function_v2int Function
          %s = OpVariable %_ptr_Function_int Function
      %color = OpVariable %_ptr_Function_v4float Function
    %imageOk = OpVariable %_ptr_Function_bool Function
        %s_0 = OpVariable %_ptr_Function_int Function
    %color_0 = OpVariable %_ptr_Function_v4float Function
%resultColor = OpVariable %_ptr_Function_v4float Function
               OpStore %numSamples %int_4
               OpStore %distortion %int_256
         %24 = OpAccessChain %_ptr_Function_v4float %ndxColors %int_0
               OpStore %24 %22
         %27 = OpAccessChain %_ptr_Function_v4float %ndxColors %int_1
               OpStore %27 %26
         %30 = OpAccessChain %_ptr_Function_v4float %ndxColors %int_2
               OpStore %30 %29
         %33 = OpAccessChain %_ptr_Function_v4float %ndxColors %int_3
               OpStore %33 %32
         %41 = OpLoad %v3uint %gl_GlobalInvocationID
         %42 = OpVectorShuffle %v2uint %41 %41 0 1
         %43 = OpBitcast %v2int %42
               OpStore %uv %43
         %45 = OpLoad %int %distortion
         %46 = OpSNegate %int %45
               OpStore %s %46
               OpBranch %47
         %47 = OpLabel
               OpLoopMerge %49 %50 None
               OpBranch %51
         %51 = OpLabel
         %52 = OpLoad %int %s
         %53 = OpLoad %int %distortion
         %55 = OpSLessThan %bool %52 %53
               OpBranchConditional %55 %48 %49
         %48 = OpLabel
               OpStore %color %57
         %58 = OpLoad %int %s
         %59 = OpSGreaterThanEqual %bool %58 %int_0
         %60 = OpLoad %int %s
         %61 = OpLoad %int %numSamples
         %62 = OpSLessThan %bool %60 %61
         %63 = OpLogicalAnd %bool %59 %62
               OpSelectionMerge %65 None
               OpBranchConditional %63 %64 %65
         %64 = OpLabel
         %66 = OpLoad %int %s
         %67 = OpSMod %int %66 %int_4
         %68 = OpAccessChain %_ptr_Function_v4float %ndxColors %67
         %69 = OpLoad %v4float %68
               OpStore %color %69
               OpBranch %65
         %65 = OpLabel
         %73 = OpLoad %70 %texture
         %74 = OpLoad %v2int %uv
         %75 = OpLoad %int %s
         %76 = OpLoad %v4float %color
               OpImageWrite %73 %74 %76 Sample %75
               OpBranch %50
         %50 = OpLabel
         %77 = OpLoad %int %s
         %78 = OpIAdd %int %77 %int_1
               OpStore %s %78
               OpBranch %47
         %49 = OpLabel
               OpMemoryBarrier %uint_1 %uint_2056
               OpControlBarrier %uint_2 %uint_2 %uint_264
               OpStore %imageOk %true
               OpStore %s_0 %int_0
               OpBranch %87
         %87 = OpLabel
               OpLoopMerge %89 %90 None
               OpBranch %91
         %91 = OpLabel
         %92 = OpLoad %int %s_0
         %93 = OpLoad %int %numSamples
         %94 = OpSLessThan %bool %92 %93
               OpBranchConditional %94 %88 %89
         %88 = OpLabel
               OpStore %color_0 %57
         %96 = OpLoad %int %s_0
         %97 = OpSGreaterThanEqual %bool %96 %int_0
         %98 = OpLoad %int %s_0
         %99 = OpLoad %int %numSamples
        %100 = OpSLessThan %bool %98 %99
        %101 = OpLogicalAnd %bool %97 %100
               OpSelectionMerge %103 None
               OpBranchConditional %101 %102 %103
        %102 = OpLabel
        %104 = OpLoad %int %s_0
        %105 = OpSMod %int %104 %int_4
        %106 = OpAccessChain %_ptr_Function_v4float %ndxColors %105
        %107 = OpLoad %v4float %106
               OpStore %color_0 %107
               OpBranch %103
        %103 = OpLabel
        %108 = OpLoad %70 %texture
        %109 = OpLoad %v2int %uv
        %110 = OpLoad %int %s_0
        %111 = OpImageRead %v4float %108 %109 Sample %110
        %112 = OpLoad %v4float %color_0
        %114 = OpFUnordNotEqual %v4bool %111 %112
        %115 = OpAny %bool %114
               OpSelectionMerge %117 None
               OpBranchConditional %115 %116 %117
        %116 = OpLabel
               OpStore %imageOk %false
               OpBranch %117
        %117 = OpLabel
               OpBranch %90
         %90 = OpLabel
        %119 = OpLoad %int %s_0
        %120 = OpIAdd %int %119 %int_1
               OpStore %s_0 %120
               OpBranch %87
         %89 = OpLabel
        %122 = OpLoad %bool %imageOk
        %123 = OpCompositeConstruct %v4bool %122 %122 %122 %122
        %124 = OpSelect %v4float %123 %26 %22
               OpStore %resultColor %124
        %128 = OpLoad %125 %result
        %129 = OpLoad %v2int %uv
        %130 = OpLoad %v4float %resultColor
               OpImageWrite %128 %129 %130
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Atomic cases

1. Amber creates a 64x64 four-sample integer storage image and a single-sample RGBA8 result image.
2. A 4x4 dispatch covers 64x64 texels because each workgroup has 16x16 invocations.
3. Every invocation initializes four samples, then synchronized workgroup phases apply atomic add/OR, XOR, and AND operations.
4. The shader loads each sample and compares it with the script's expected expression.
5. The shader writes green on success and red on failure. Amber requires every result pixel to equal `(0,255,0,255)`.

### Invalid-index cases

1. Amber creates a 16x16 multisample RGBA8 image with the registered sample count and a 16x16 result image.
2. One 16x16 workgroup covers the full extent.
3. Each invocation writes sample operands from -256 through 255, assigning test colors only inside `[0,numSamples)`.
4. After image and workgroup barriers, the shader reads every valid sample and compares it with the expected color.
5. The shader writes green or red. Amber requires the full result image to be green.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `atomic` | Incorrect per-sample storage-image addressing, atomic operation, or workgroup image-memory synchronization; for `storage_image_r64i` and `storage_image_r64ui`, the inspected expected-value mismatch is also a direct test-side cause. |
| `invalid_sample_index` | A valid sample changed or was read incorrectly after the mixed write loop; the test also relies on an out-of-bounds discard guarantee without enabling robust image access, so the result cannot be attributed to a conformance defect from the inspected requirements alone. |

### Cause Analysis

#### Per-sample address selection

**Possible failure symptoms:** One or more sample comparisons fail while other samples at the same texel remain correct, producing red result pixels.

**Possible implementation causes:** The storage-image path may select the wrong multisample plane for `imageLoad`, `imageStore`, or `OpImageTexelPointer`. Investigation should compare the dynamic sample operand with the selected sample storage.

#### Atomic operation or synchronization behavior

**Possible failure symptoms:** R32 atomic cases show widespread red pixels or values that vary between runs, operation phases, or mirrored invocation pairs.

**Possible implementation causes:** Integer image atomics may produce an incorrect result, or image memory may not become visible after `memoryBarrierImage` plus `barrier`. The shader uses barriers between every dependent phase, so investigation should preserve that ordering.

#### R64 test oracle

**Possible failure symptoms:** R64 signed and unsigned cases fail consistently even when the observed value reflects the scripted OR and XOR operations.

**Possible implementation causes:** The R64 scripts contain a confirmed test-side cause: both compare against a constant with `0x0a` in the high byte instead of the `0xcc` pattern produced by their own operation sequence. Source repair is outside this documentation audit.

#### Invalid sample index without robustness

**Possible failure symptoms:** Valid sample colors change after out-of-range writes, or behavior varies across devices despite correct valid-index image operations.

**Possible implementation causes:** The tests issue out-of-bounds image accesses without enabling robust image access. Vulkan does not provide the expected discard guarantee under the documented setup, so the behavior cannot be localized to a conformant implementation defect from this test alone.

## Case Pruning

### Requirement-based pruning

- Registration creates only formats and sample counts listed in the two source arrays.
- Amber support checks can skip a case when its required feature or image creation requirements are unsupported.
- R64 cases require `shaderInt64` in addition to `shaderStorageImageMultisample`.
- The texture dispatcher omits the whole family from Vulkan SC.
- No runtime randomization or generated case expansion changes the ten default Vulkan leaves.

### Design-based pruning

The source uses fixed Amber leaves and does not add further runtime-generated case families.

## Key Takeaways

- The family contains ten Amber leaves: four atomic formats and six invalid-index sample counts.
- The shaders perform verification; Amber checks only the green/red result image.
- The R32 atomic path exercises per-sample image atomics and synchronization.
- The R64 oracle and the missing robustness requirement are unresolved source-level defects, not documentation uncertainties.

## Source Reference Appendix

| Topic | Source |
|-------|--------|
| Registration, requirements, and image parameters | [`vktTextureMultisampleTests.cpp`](../../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L38-L156) |
| Texture dispatcher and Vulkan SC exclusion | [`createTextureTests`](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L67) |
| Representative R32 atomic script | [`storage_image_r32ui.amber`](../../../data/vulkan/amber/texture/multisample/atomic/storage_image_r32ui.amber) |
| R64 oracle defect | [`storage_image_r64ui.amber`](../../../data/vulkan/amber/texture/multisample/atomic/storage_image_r64ui.amber#L33-L70) |
| Representative invalid-index script | [`sample_count_4.amber`](../../../data/vulkan/amber/texture/multisample/invalidsampleindex/sample_count_4.amber) |
| Default-device robustness state | [`DeviceFeatures`](../../../framework/vulkan/vkDeviceFeatures.cpp#L210-L234) |
| Amber execution and shader compilation | [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L410-L479) |
| Image coordinate validation | [`images.adoc`](../../../../vulkan-docs/src/chapters/images.adoc#L42-L103) |
| Image sample operands and atomics | [`images.adoc`](../../../../vulkan-docs/src/chapters/images.adoc#L225-L263) |
| Out-of-bounds access requirements | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L1871-L1921) |
| Default mustpass inventory | [`texture.txt`](../../../mustpass/main/vk-default/texture.txt#L10384-L10393) |
