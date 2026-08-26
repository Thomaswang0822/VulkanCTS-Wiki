## Overview

**Core question:** Do `coherent`, `volatile`, and `restrict` resource declarations produce correct storage-image and texel-buffer access in their registered CTS cases?

- This page covers the implementation and registration in [`vktImageQualifiersTests.cpp`](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L191-L769) for the `image.qualifiers` test family.
- `coherent` and `volatile` use one generated compute-shader pattern: every invocation writes a coordinate-derived value, synchronizes within the workgroup, reads four peer locations, and stores their sum.
- `restrict` is registered here but implemented by the load/store test generator. Its cases use `restrict`-qualified readonly and writeonly image declarations.
- The page explains the registered matrix, a representative coherent shader, host execution, result checking, and what each family failure can indicate.

## Background Knowledge

For the shared concepts of images and views, layouts and synchronization, and subresources and copies, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- A shader memory qualifier decorates a resource declaration. It does not itself synchronize workgroup execution. The Vulkan shader rules say that `Coherent` accesses make available writes to the same buffer, buffer view, or image view visible, while explicit dependencies still order writes to different locations.
- `memoryBarrier()` orders an invocation's memory operations. `barrier()` is a control barrier that synchronizes execution within a workgroup; neither operation is implied by a memory qualifier.
- `volatile` requires accesses not to reuse an earlier load result, but does not prescribe a particular optimizer or cache implementation.
- `restrict` expresses an aliasing promise for the qualified declaration.

## Registration Hierarchy

```text
image.qualifiers
├── coherent
├── volatile
└── restrict
```

The factory owns all three test families. `coherent` and `volatile` expand by image type and format; `restrict` contributes one case per image type while delegating its implementation to the load/store generator.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `coherent`, `volatile`, `restrict` | Selects the declaration semantic; `restrict` also selects the delegated implementation. | [factory](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L726-L766) |
| Image type | `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array`, `buffer` | Chooses the storage image or storage texel-buffer declaration and coordinate shape. | [image matrix](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L711-L718) |
| Format for `coherent` / `volatile` | `r32f`, `r32ui`, `r32i` | Chooses float, unsigned-integer, or signed-integer image access and comparison type. | [format matrix](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L720-L760) |
| Image size | `64×1×1`, `64×1×8`, `64×64×1`, `64×64×8`, and `64×64×2` as appropriate to the image type | Defines the dispatch grid and layer or slice coverage. | [image matrix](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L711-L718) |
| Local workgroup size | Base `8×8×2`, clamped to the selected grid | Defines the workgroup-local wrapping used by the four peer reads. | [size helper](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L64-L88) |
| Read offsets | X `{1, 4, 7, 10}`, Y `{2, 5, 8, 11}`, Z `{3, 6, 9, 12}` | Select four peer coordinates within the same workgroup. | [offsets](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L64-L70) |

`cube_array` cases require the core image-cube-array feature in the locally generated `coherent` and `volatile` path.

## Behavior Parameters

The primary behavioral axis is the test family.

### coherent: Coherent declaration with synchronized peer reads

The generated shader declares `u_image` with `coherent`, writes one value per invocation, and reads peer-written values after `memoryBarrier()` plus `barrier()`. The reference image recomputes the same four-value sum on the CPU.

The qualifier applies to the declaration; the two barrier phases remain part of the mechanism that makes the workgroup exchange meaningful.

### volatile: Volatile declaration with the same workgroup computation

The generated shader uses the same resource, coordinate, barrier, read-offset, and comparison design as `coherent`, but declares `u_image` as `volatile`.

A volatile failure is therefore interpreted through the same observed image mismatch, while the tested declaration semantic differs from the coherent case.

### restrict: Delegated restrict-qualified load/store cases

The source passes each image type to `createImageQualifierRestrictCase`, which constructs a `LoadStoreTest` with `FLAG_RESTRICT_IMAGES` and explicit image-format declarations.

That generator emits `restrict` on the readonly and writeonly image declarations. This family tests the delegated read/write path, not the local workgroup-sum algorithm used above.

## Shader Analysis

The representative path is `dEQP-VK.image.qualifiers.coherent.2d.r32ui`. It exercises the locally generated shader with an integer image format, so its final output can be checked exactly.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.qualifiers.coherent.2d.r32ui
```

| Parameter choice | Meaning in this representative case |
|---|---|
| Registered path: `image.qualifiers.coherent.2d.r32ui` | Selects the local coherent shader and unsigned 2D storage image. |
| Image extent: `64×64×1` | Leaves the base local size at `8×8×1` after clamping to the grid. |
| Image declaration: `layout(r32ui, binding=0) coherent uniform uimage2D` | Binds one coherent unsigned storage image. |
| Read offsets: `(1,2)`, `(4,5)`, `(7,8)`, `(10,11)` modulo the local size | Produces four same-workgroup peer reads. |

#### Purpose

This compute shader checks a `coherent` `uimage2D` declaration while moving data between invocations in the same 8×8 workgroup. Each invocation writes `gx ^ gy`, reads four wrapped peer coordinates after a memory and control barrier, then stores their sum.

#### Structural Design

| Phase | Per-invocation action | Required relationship |
|-------|-----------------------|-----------------------|
| Initial store | Store `gx ^ gy` at `(gx, gy)` | Each invocation owns one initial value. |
| Synchronize | Run `memoryBarrier()` and `barrier()` | Separates all initial writes from peer reads in the workgroup. |
| Gather | Load four wrapped peer coordinates and accumulate `.x` | Matches the CPU reference computation. |
| Final store | Run the second barrier pair and store the sum at the invocation's coordinate | Separates peer reads from final overwrites. |

#### Shader Code

```glsl
#version 440

layout(local_size_x = 8, local_size_y = 8, local_size_z = 1) in;
layout(r32ui, binding = 0) coherent uniform uimage2D u_image;

void main(void)
{
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);

    imageStore(u_image, ivec2(gx, gy), uvec4(gx ^ gy));

    memoryBarrier();
    barrier();

    uint sum = uint(0);
    int groupBaseX = gx / 8 * 8;
    int groupBaseY = gy / 8 * 8;
    int xOffsets[] = int[] (1, 4, 7, 10);
    int yOffsets[] = int[] (2, 5, 8, 11);
    for (int i = 0; i < 4; i++)
    {
        int readX = groupBaseX + (gx + xOffsets[i]) % 8;
        int readY = groupBaseY + (gy + yOffsets[i]) % 8;
        sum += imageLoad(u_image, ivec2(readX, readY)).x;
    }

    memoryBarrier();
    barrier();

    imageStore(u_image, ivec2(gx, gy), uvec4(sum));
}
```

#### Additional Info

- The source obtains the GLSL version declaration from `GLSL_VERSION_440` and adds the shader without explicit build options, so the walkthrough uses the CTS source-collection baseline target, SPIR-V 1.0.
- The reconstructed local size is `8×8×1`: the source clamps the `8×8×2` base to the selected 2D image grid.
- The compiled output contains `OpDecorate %u_image Coherent`, which audits that the representative qualifier survived compilation.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Qualifier | `volatile` changes only the qualifier word in this generated declaration; the workgroup computation and reference algorithm remain the same. | [shader generators](../../../modules/vulkan/image/vktImageQualifiersTests.cpp) |
| Image format | `r32f` and `r32i` change the image and scalar types generated around the same coordinate and synchronization logic. | [shader generators](../../../modules/vulkan/image/vktImageQualifiersTests.cpp) |
| Image type | Other image types use `int`, `ivec2`, or `ivec3` coordinates as selected by `getCoordStr`; arrays, 3D images, cubes, and cube arrays also change the grid or layer shape. | [shader generators](../../../modules/vulkan/image/vktImageQualifiersTests.cpp) |
| Restrict family | `restrict` does not reuse this shader generator. It delegates to the load/store builder. | [shader generators](../../../modules/vulkan/image/vktImageQualifiersTests.cpp) |

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
; Bound: 111
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 8 8 1
               OpSource GLSL 440
               OpName %main "main"
               OpName %gx "gx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %gy "gy"
               OpName %u_image "u_image"
               OpName %sum "sum"
               OpName %groupBaseX "groupBaseX"
               OpName %groupBaseY "groupBaseY"
               OpName %xOffsets "xOffsets"
               OpName %yOffsets "yOffsets"
               OpName %i "i"
               OpName %readX "readX"
               OpName %readY "readY"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %u_image Coherent
               OpDecorate %u_image Binding 0
               OpDecorate %u_image DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
         %23 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_23 = OpTypePointer UniformConstant %23
    %u_image = OpVariable %_ptr_UniformConstant_23 UniformConstant
      %v2int = OpTypeVector %int 2
     %v4uint = OpTypeVector %uint 4
  %uint_3400 = OpConstant %uint 3400
     %uint_2 = OpConstant %uint 2
   %uint_264 = OpConstant %uint 264
%_ptr_Function_uint = OpTypePointer Function %uint
      %int_8 = OpConstant %int 8
     %uint_4 = OpConstant %uint 4
%_arr_int_uint_4 = OpTypeArray %int %uint_4
%_ptr_Function__arr_int_uint_4 = OpTypePointer Function %_arr_int_uint_4
      %int_1 = OpConstant %int 1
      %int_4 = OpConstant %int 4
      %int_7 = OpConstant %int 7
     %int_10 = OpConstant %int 10
         %59 = OpConstantComposite %_arr_int_uint_4 %int_1 %int_4 %int_7 %int_10
      %int_2 = OpConstant %int 2
      %int_5 = OpConstant %int 5
     %int_11 = OpConstant %int 11
         %64 = OpConstantComposite %_arr_int_uint_4 %int_2 %int_5 %int_8 %int_11
      %int_0 = OpConstant %int 0
       %bool = OpTypeBool
     %uint_8 = OpConstant %uint 8
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_8 %uint_8 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %gx = OpVariable %_ptr_Function_int Function
         %gy = OpVariable %_ptr_Function_int Function
        %sum = OpVariable %_ptr_Function_uint Function
 %groupBaseX = OpVariable %_ptr_Function_int Function
 %groupBaseY = OpVariable %_ptr_Function_int Function
   %xOffsets = OpVariable %_ptr_Function__arr_int_uint_4 Function
   %yOffsets = OpVariable %_ptr_Function__arr_int_uint_4 Function
          %i = OpVariable %_ptr_Function_int Function
      %readX = OpVariable %_ptr_Function_int Function
      %readY = OpVariable %_ptr_Function_int Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %16 = OpLoad %uint %15
         %17 = OpBitcast %int %16
               OpStore %gx %17
         %20 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %21 = OpLoad %uint %20
         %22 = OpBitcast %int %21
               OpStore %gy %22
         %26 = OpLoad %23 %u_image
         %27 = OpLoad %int %gx
         %28 = OpLoad %int %gy
         %30 = OpCompositeConstruct %v2int %27 %28
         %31 = OpLoad %int %gx
         %32 = OpLoad %int %gy
         %33 = OpBitwiseXor %int %31 %32
         %34 = OpBitcast %uint %33
         %36 = OpCompositeConstruct %v4uint %34 %34 %34 %34
               OpImageWrite %26 %30 %36
               OpMemoryBarrier %uint_1 %uint_3400
               OpControlBarrier %uint_2 %uint_2 %uint_264
               OpStore %sum %uint_0
         %43 = OpLoad %int %gx
         %45 = OpSDiv %int %43 %int_8
         %46 = OpIMul %int %45 %int_8
               OpStore %groupBaseX %46
         %48 = OpLoad %int %gy
         %49 = OpSDiv %int %48 %int_8
         %50 = OpIMul %int %49 %int_8
               OpStore %groupBaseY %50
               OpStore %xOffsets %59
               OpStore %yOffsets %64
               OpStore %i %int_0
               OpBranch %67
         %67 = OpLabel
               OpLoopMerge %69 %70 None
               OpBranch %71
         %71 = OpLabel
         %72 = OpLoad %int %i
         %74 = OpSLessThan %bool %72 %int_4
               OpBranchConditional %74 %68 %69
         %68 = OpLabel
         %76 = OpLoad %int %groupBaseX
         %77 = OpLoad %int %gx
         %78 = OpLoad %int %i
         %79 = OpAccessChain %_ptr_Function_int %xOffsets %78
         %80 = OpLoad %int %79
         %81 = OpIAdd %int %77 %80
         %82 = OpSMod %int %81 %int_8
         %83 = OpIAdd %int %76 %82
               OpStore %readX %83
         %85 = OpLoad %int %groupBaseY
         %86 = OpLoad %int %gy
         %87 = OpLoad %int %i
         %88 = OpAccessChain %_ptr_Function_int %yOffsets %87
         %89 = OpLoad %int %88
         %90 = OpIAdd %int %86 %89
         %91 = OpSMod %int %90 %int_8
         %92 = OpIAdd %int %85 %91
               OpStore %readY %92
         %93 = OpLoad %23 %u_image
         %94 = OpLoad %int %readX
         %95 = OpLoad %int %readY
         %96 = OpCompositeConstruct %v2int %94 %95
         %97 = OpImageRead %v4uint %93 %96
         %98 = OpCompositeExtract %uint %97 0
         %99 = OpLoad %uint %sum
        %100 = OpIAdd %uint %99 %98
               OpStore %sum %100
               OpBranch %70
         %70 = OpLabel
        %101 = OpLoad %int %i
        %102 = OpIAdd %int %101 %int_1
               OpStore %i %102
               OpBranch %67
         %69 = OpLabel
               OpMemoryBarrier %uint_1 %uint_3400
               OpControlBarrier %uint_2 %uint_2 %uint_264
        %103 = OpLoad %23 %u_image
        %104 = OpLoad %int %gx
        %105 = OpLoad %int %gy
        %106 = OpCompositeConstruct %v2int %104 %105
        %107 = OpLoad %uint %sum
        %108 = OpCompositeConstruct %v4uint %107 %107 %107 %107
               OpImageWrite %103 %106 %108
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The local implementation creates either a storage image plus image view or a storage texel buffer plus buffer view, then binds it at descriptor binding `0`.
- For image cases, it transitions the image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_GENERAL` before dispatch. After dispatch, it transitions the image to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, copies it to a host-visible buffer, and makes the copied range available to the host.
- The test creates a compute pipeline from the generated shader, dispatches the grid derived from the image extent and clamped local size, waits for completion, invalidates the readback allocation, and constructs a pixel-buffer view of the result.
- The CPU reference first assigns `x ^ y ^ z` to every element, then computes the same four wrapped offsets within each local workgroup. The local test compares that reference with every output layer, slice, or cube face.
- Integer outputs use exact comparison. Floating-point outputs use a `0.01` threshold. Any mismatching layer makes `comparePixelBuffers` return false and the case reports `Image comparison failed`.
- The delegated restrict cases use `LoadStoreTest` resource setup and verification rather than this local reference-image path.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `coherent` | Incorrect handling of the `coherent` declaration together with the shader barriers used for the workgroup read-after-write exchange. |
| `volatile` | Incorrect handling of the `volatile` declaration or of the same synchronized image-access sequence used by the generated case. |
| `restrict` | Incorrect lowering or execution of `restrict`-qualified read/write image declarations in the delegated load/store path. |

### Cause Analysis

#### Coherent declaration or workgroup access ordering

**Possible failure symptoms:** one or more output pixels, layers, slices, or cube faces differ from the CPU's four-offset sum; integer cases require an exact match and floating-point cases exceed the allowed threshold.

**Possible implementation causes:** the Vulkan shader rules specify `Coherent` availability and visibility for accesses through the same buffer, buffer view, or image view, while the generated `memoryBarrier()` and `barrier()` establish the phase ordering the case relies on. A compiler or execution path that loses the coherent decoration, mishandles the barrier sequence, or performs image loads/stores inconsistently can produce the observed mismatch.

#### Volatile declaration or repeated image-access handling

**Possible failure symptoms:** the same reference comparison fails for a `volatile` case, despite the identical coordinate, synchronization, and reference algorithm used by the coherent family.

**Possible implementation causes:** the qualifier may be lowered incorrectly, or the image access and workgroup synchronization sequence may be handled incorrectly. This test observes only the final image result, so source-level investigation is needed to distinguish a declaration-semantic defect from a shared local access-path defect.

#### Restrict-qualified delegated load/store path

**Possible failure symptoms:** the delegated `LoadStoreTest` reports its image load/store result as incorrect for a selected image type.

**Possible implementation causes:** `createImageQualifierRestrictCase` enables `FLAG_RESTRICT_IMAGES`, and the load/store generator emits `restrict` on its image declarations. A failure can arise if that declaration is lowered or executed inconsistently with the test's readonly/writeonly resource use. The delegated verifier and generator require source-level inspection for a more specific diagnosis.

## Case Pruning

### Requirement-based pruning

- The local `coherent` and `volatile` path calls `requireDeviceCoreFeature(DEVICE_CORE_FEATURE_IMAGE_CUBE_ARRAY)` for `cube_array` cases.
- The delegated restrict implementation uses the load/store test's support checks for the selected texture, format, and image usage.

### Design-based pruning

- The `coherent` and `volatile` families use the same three scalar formats for every registered image type, which gives the local reference algorithm comparable float, signed, and unsigned coverage.
- The `restrict` family intentionally has one case per image type. It delegates to a fixed `VK_FORMAT_R32G32B32A32_UINT` load/store configuration instead of duplicating the local three-format workgroup-sum matrix.

## Key Takeaways

- `coherent` and `volatile` share one generated workgroup computation, but they test distinct declaration qualifiers.
- The first barrier pair protects the peer-read phase; the second separates reads from final overwrites. The qualifier does not replace these barriers.
- `restrict` belongs to the same registered test family but uses a separate load/store generator and verification path.
- A local-family failure is an output-reference mismatch, not direct evidence of a specific cache or optimizer mechanism.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Qualifier factory and matrix | [createImageQualifiersTests](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L695-L769) | Registers the three families, image types, formats, and restrict delegation. |
| Local GLSL generator | [MemoryQualifierTestCase::initPrograms](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L241-L305) | Generates the qualifier declaration and the two-phase workgroup algorithm. |
| Runtime dispatch and outcome | [MemoryQualifierInstanceBase::iterate](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L352-L419) | Creates and dispatches the pipeline, reads back results, and reports pass or failure. |
| CPU reference | [generateReferenceImage](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L421-L463) | Reproduces the expected four-offset sums. |
| Image setup and copyback | [MemoryQualifierInstanceImage](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L491-L603) | Creates the storage image and executes layout, copy, and host-read barriers. |
| Restrict-case factory | [createImageQualifierRestrictCase](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3760-L3769) | Configures the delegated load/store test with `FLAG_RESTRICT_IMAGES`. |
| Restrict declaration generator | [LoadStoreTest::makePrograms](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1444-L1507) | Emits restrict-qualified readonly and writeonly image declarations. |
| Vulkan shader memory rules | [Shaders](../../../../vulkan-docs/src/chapters/shaders.adoc#L2291-L2340) | Documents `Coherent`, memory barriers, availability, and visibility. |
| Mustpass qualifier cases | [qualifiers.txt](../../../mustpass/main/vk-default/image/qualifiers.txt#L1-L56) | Lists the 56 registered default-profile cases. |
