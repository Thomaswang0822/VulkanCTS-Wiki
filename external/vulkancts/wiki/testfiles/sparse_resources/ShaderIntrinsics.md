## Overview

**Core question:** Do sparse image instructions return the expected texel and residency status when mip levels alternate between resident and nonresident memory?

- `vktSparseResourcesShaderIntrinsics.cpp` registers `sparse_resources.shader_intrinsics` and creates cases for five sparse image operations across supported image types, formats, sizes, and operands.
- The implementation is split between sampled-image graphics cases, storage-image compute cases, and the shared sparse-image setup and result checking.
- This page explains the generated case matrix, the storage compute path, the residency check, and the failure signals. The old source-style page remains available as a navigation aid.

## Background Knowledge

- Sparse image residency allows image memory to be bound per mip level. A test can therefore make one mip resident and another nonresident without changing the image object.
- Sparse image instructions return an operation result together with a residency code. `OpImageSparseTexelsResident` interprets that code; the returned texel and the residency result are separate values that this test checks independently.
- Sampled operations run in a graphics pipeline. Fetch and read operations run in a compute pipeline, and the queue and descriptor type change with that split.

## Registration Hierarchy

```text
sparse_resources.shader_intrinsics
├── 2d_sparse_fetch
├── 2d_array_sparse_fetch
├── 3d_sparse_fetch
├── 2d_sparse_read
├── 2d_array_sparse_read
├── cube_sparse_read
├── cube_array_sparse_read
├── 3d_sparse_read
├── 2d_sparse_sample_explicit_lod
├── 2d_array_sparse_sample_explicit_lod
├── 2d_sparse_sample_implicit_lod
├── 2d_array_sparse_sample_implicit_lod
├── 2d_sparse_gather
└── 2d_array_sparse_gather
```

The registration file creates these test families and delegates their case objects to the sampled and storage implementations.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Sparse operation | `*_sparse_fetch`, `*_sparse_read`, `*_sparse_sample_explicit_lod`, `*_sparse_sample_implicit_lod`, `*_sparse_gather` | Selects the sparse image instruction and its sampled or storage execution path. | [`createSparseResourcesShaderIntrinsicsTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L73-L84) |
| Image type | 2D, 2D array, cube, cube array, 3D | Changes image declaration, coordinate shape, layer count, and registration pruning. | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L55-L71) |
| Image size | Four sizes per image type, including `11_37_1` for 2D | Changes mip count, invocation grid, sparse blocks, and output extent. | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L55-L71) |
| Format | Formats returned by `getTestFormats` | Changes image component type, format qualifier, planes, and feature checks. | [`getTestFormats` and registration](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L55-L71) |
| Operand | empty, `Nontemporal` | The second operand variant is generated for the last listed size when that size passes format-alignment and image-type pruning, and requires Vulkan 1.3 or later. | [`operand` generation](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L110-L151) |

## Behavior Parameters

The primary behavioral axis is the sparse operation and image-type family. Format, size, and operand vary the same mechanism rather than replacing it.

### `*_sparse_fetch` and `*_sparse_read` — storage-image operations

`OpImageSparseFetch` uses an explicit mip level and a sampled-image descriptor. `OpImageSparseRead` uses a storage-image descriptor and the operation's optional operand. Both run in compute, write the returned texel to an output image, and record the residency result in a separate image.

### `*_sparse_sample_*` — sampled operations

Explicit-LOD and implicit-LOD sampling use the graphics sampled-image path. The fragment shader receives coordinates from the vertex stage, performs the selected sparse sample, and writes texel and residency results to color attachments.

### `*_sparse_gather` — gathered sampled values

The gather path performs four sparse gathers and combines their texel and residency information for output. It uses the sampled graphics path and is registered only for 2D and 2D-array images.

## Shader Analysis

The selected representative case is a storage-image compute case because its generated program exposes the complete sparse-operation result and the residency branch in one entry point. The owning builder is [`SparseShaderIntrinsicsCaseStorage::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L50-L415), which emits SPIR-V assembly directly through `programCollection.spirvAsmSources`, not GLSL or HLSL. The corresponding construction entry point is [`createSparseResourcesShaderIntrinsicsTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L51-L160).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.sparse_resources.shader_intrinsics.2d_sparse_read.r32ui.11_37_1
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `2d_sparse_read` | Selects `SparseCaseOpImageSparseRead` and the compute storage-image path. |
| `r32ui` | Selects one unsigned 32-bit component per plane, `%type_uint`/`%type_uvec4`, and the `R32ui` image format operand. |
| `11_37_1` | Selects the smallest 2D extent, which also has a `_nontemporal` sibling. |

#### Purpose

The generated compute program applies `OpImageSparseRead` at the invocation coordinate, stores the returned component vector, and records whether the sparse result reports resident texels.

#### Structural Design

| Phase | Generated operation |
|---|---|
| Bounds | Compare each component of `gl_GlobalInvocationID` with specialization-constant grid dimensions. |
| Sparse operation | Load the sparse storage image and issue `OpImageSparseRead`. |
| Texel result | Extract the operation's texel member and write it to the texel output image. |
| Residency result | Extract the residency code, call `OpImageSparseTexelsResident`, and write the resident or nonresident marker. |

#### Shader Code

The source generator emits SPIR-V directly. The central generated sequence is [`sparseImageOpString`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L451-L463), followed by the result extraction and output writes in [`SparseShaderIntrinsicsCaseStorage::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L327-L399). Because this test directly supplies SPIR-V assembly through `programCollection.spirvAsmSources`, the `#### SPIR-V` subsection below is the primary shader artifact; no hand-translated GLSL or HLSL block is expected.

#### Additional Info

- The storage path creates three bindings per image plane: sparse input, texel output, and residency output. [`recordCommands`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L548-L572) packages those bindings per mip level.
- The shader uses specialization constants for grid and workgroup sizes. The host dispatches enough workgroups to cover the grid and the shader's bounds checks discard excess invocations.
- The `Nontemporal` case changes the generated SPIR-V target to SPIR-V 1.6 in the storage builder.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Sparse operation | Changes the emitted `OpImageSparse*` instruction and operand form. | [`operation printers`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L427-L464) |
| Image type | Changes `OpTypeImage` dimensionality and coordinate construction. | [`getOpTypeImageSparse`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsBase.cpp#L144-L246) |
| Format | Changes component types, image format operands, and plane declarations. | [`initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L50-L63) |
| Operand | Adds `Nontemporal` to the generated sparse instruction and selects SPIR-V 1.6. | [`initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L65-L72) |

#### SPIR-V

The following is the hand-reconstructed single-plane `R32_UINT` specialization emitted by `SparseShaderIntrinsicsCaseStorage::initPrograms`: `2d_sparse_read` selects `SparseCaseOpImageSparseRead`, the `11_37_1` extent selects a 2D coordinate, and the `R32_UINT` format supplies `%type_uint`, `%type_uvec4`, and `R32ui` image operands. The `sparseImageOpString` helper emits `OpImageSparseRead` without a mip-level operand because this case has no optional operand. The assembly was round-tripped through `spirv-as --target-env spv1.0`, `spirv-val --target-env spv1.0`, and `spirv-dis`; the matching `; Version: 1.0` header passed the validation gate.

- Status: generated and validated
- Source: reconstructed direct `SPIR-V` assembly from the CTS generator
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 78
; Schema: 0
               OpCapability Shader
               OpCapability ImageCubeArray
               OpCapability SparseResidency
               OpCapability StorageImageExtendedFormats
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 440
               OpName %main "main"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %gl_WorkGroupSize "gl_WorkGroupSize"
               OpName %u_imageSparse_plane0 "u_imageSparse_plane0"
               OpName %u_imageTexels_plane0 "u_imageTexels_plane0"
               OpName %u_imageResidency_plane0 "u_imageResidency_plane0"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %8 SpecId 1
               OpDecorate %9 SpecId 2
               OpDecorate %10 SpecId 3
               OpDecorate %11 SpecId 4
               OpDecorate %12 SpecId 5
               OpDecorate %13 SpecId 6
               OpDecorate %u_imageSparse_plane0 DescriptorSet 0
               OpDecorate %u_imageSparse_plane0 Binding 0
               OpDecorate %u_imageTexels_plane0 DescriptorSet 0
               OpDecorate %u_imageTexels_plane0 Binding 1
               OpDecorate %u_imageTexels_plane0 NonReadable
               OpDecorate %u_imageResidency_plane0 DescriptorSet 0
               OpDecorate %u_imageResidency_plane0 Binding 2
               OpDecorate %u_imageResidency_plane0 NonReadable
       %bool = OpTypeBool
        %int = OpTypeInt 32 1
       %uint = OpTypeInt 32 0
      %float = OpTypeFloat 32
      %v2int = OpTypeVector %int 2
      %v3int = OpTypeVector %int 3
      %v4int = OpTypeVector %int 4
     %v3uint = OpTypeVector %uint 3
     %v4uint = OpTypeVector %uint 4
    %v2float = OpTypeVector %float 2
    %v3float = OpTypeVector %float 3
    %v4float = OpTypeVector %float 4
%_ptr_Input_uint = OpTypePointer Input %uint
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%_ptr_Function_int = OpTypePointer Function %int
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
       %void = OpTypeVoid
         %31 = OpTypeFunction %void
 %_struct_32 = OpTypeStruct %int %v4uint
         %33 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_33 = OpTypePointer UniformConstant %33
%_ptr_UniformConstant_33_0 = OpTypePointer UniformConstant %33
%u_imageSparse_plane0 = OpVariable %_ptr_UniformConstant_33 UniformConstant
%u_imageTexels_plane0 = OpVariable %_ptr_UniformConstant_33 UniformConstant
%u_imageResidency_plane0 = OpVariable %_ptr_UniformConstant_33_0 UniformConstant
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
          %8 = OpSpecConstant %uint 1
          %9 = OpSpecConstant %uint 1
         %10 = OpSpecConstant %uint 1
         %11 = OpSpecConstant %uint 1
         %12 = OpSpecConstant %uint 1
         %13 = OpSpecConstant %uint 1
%gl_WorkGroupSize = OpSpecConstantComposite %v3uint %11 %12 %13
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
       %true = OpConstantTrue %bool
   %uint_1_0 = OpConstant %uint 1
         %44 = OpConstantComposite %v4uint %uint_1_0 %uint_1_0 %uint_1_0 %uint_1_0
   %uint_0_0 = OpConstant %uint 0
         %46 = OpConstantComposite %v4uint %uint_0_0 %uint_0_0 %uint_0_0 %uint_0_0
       %main = OpFunction %void None %31
         %47 = OpLabel
         %48 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %49 = OpLoad %uint %48
         %50 = OpBitcast %int %49
         %51 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %52 = OpLoad %uint %51
         %53 = OpBitcast %int %52
         %54 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %55 = OpLoad %uint %54
         %56 = OpBitcast %int %55
         %57 = OpCompositeConstruct %v2int %50 %53
         %58 = OpCompositeConstruct %v3int %50 %53 %56
         %59 = OpULessThan %bool %49 %8
               OpSelectionMerge %60 None
               OpBranchConditional %59 %61 %60
         %61 = OpLabel
         %62 = OpULessThan %bool %52 %9
               OpSelectionMerge %63 None
               OpBranchConditional %62 %64 %63
         %64 = OpLabel
         %65 = OpULessThan %bool %55 %10
               OpSelectionMerge %66 None
               OpBranchConditional %65 %67 %66
         %67 = OpLabel
         %68 = OpLoad %33 %u_imageSparse_plane0
         %69 = OpImageSparseRead %_struct_32 %68 %57
         %70 = OpCompositeExtract %v4uint %69 1
         %71 = OpCompositeExtract %int %69 0
         %72 = OpLoad %33 %u_imageTexels_plane0
               OpImageWrite %72 %57 %70
         %73 = OpLoad %33 %u_imageResidency_plane0
         %74 = OpImageSparseTexelsResident %bool %71
               OpSelectionMerge %75 None
               OpBranchConditional %74 %76 %77
         %76 = OpLabel
               OpImageWrite %73 %57 %44
               OpBranch %75
         %77 = OpLabel
               OpImageWrite %73 %57 %46
               OpBranch %75
         %75 = OpLabel
               OpBranch %66
         %66 = OpLabel
               OpBranch %63
         %63 = OpLabel
               OpBranch %60
         %60 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The shared instance creates a `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT | VK_IMAGE_CREATE_SPARSE_BINDING_BIT` image with transfer-destination usage plus sampled or storage usage. Cube cases add cube compatibility; multi-planar cases add the required mutable and extended-usage flags.
- The host obtains sparse image memory requirements, binds alternating mip levels, binds the mip tail as resident, and fills reference data with resident and nonresident markers.
- Storage cases create a compute queue and a sparse-binding queue. For each mip level, the host binds the descriptor set, supplies grid and workgroup specialization values, and dispatches enough workgroups to cover the mip extent.
- Barriers move the input image from transfer writes to shader reads and move output images from shader writes to transfer reads. The host copies texel and residency images back and compares them with the reference data.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any sparse intrinsic family | Sparse image binding or image-operation behavior returned wrong texels or residency information; shader generation or descriptor setup selected the wrong operation or resource type |
| `*_nontemporal` case | The implementation did not support or correctly process the `Nontemporal` operand and its SPIR-V 1.6 variant |

### Cause Analysis

#### Wrong sparse result or residency status

**Possible failure symptoms:** The texel output differs from initialized resident-mip data, or the residency image contains the wrong bound or unbound marker.

**Possible implementation causes:** The sparse image bind mapping, sparse instruction execution, image view or descriptor selection, shader lowering, or output synchronization may be involved. The test source does not identify one of these as the cause, so source-level investigation is needed for a particular failure.

#### Unsupported or incorrect `Nontemporal` handling

**Possible failure symptoms:** A `_nontemporal` case is rejected by support checks or produces a different texel or residency result from the equivalent ordinary case.

**Possible implementation causes:** The implementation may lack the required Vulkan 1.3 feature support or may mishandle the `Nontemporal` operand in the SPIR-V 1.6 instruction. The exact cause requires investigation of the failing operation and device support.

## Case Pruning

### Requirement-based pruning

- Every case requires shader resource residency, image-size support, sparse binding and residency support for the concrete image type and format, and the sampled or storage usage needed by its operation.
- R64 formats require `VK_EXT_shader_image_atomic_int64`, `shaderImageInt64Atomics`, and `sparseImageInt64Atomics`.
- `Nontemporal` variants require Vulkan 1.3 or later. Device limits also reject images exceeding sparse address space, framebuffer limits, or compute invocation limits.

### Design-based pruning

- Fetch excludes cube and cube-array images.
- Sampling and gather exclude cube, cube-array, and 3D images.
- Image sizes that do not satisfy a format's alignment requirement are skipped. The `Nontemporal` duplicate is created only for the last size in each image-type list.

## Key Takeaways

- The test checks two outputs from every sparse operation: the returned texel and the operation's residency report.
- Alternating mip-level binds make the residency result observable while the host reference data supplies an independent texel check.
- The registration matrix changes operation, image type, format, size, and operand, but the core contract remains the same.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Registration matrix | [`createSparseResourcesShaderIntrinsicsTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsics.cpp#L51-L160) | Registers all families and applies design pruning |
| Storage shader generation | [`SparseShaderIntrinsicsCaseStorage::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L50-L415) | Emits compute SPIR-V and specialization constants |
| Sampled shader generation | [`SparseShaderIntrinsicsCaseSampledBase::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsSampled.cpp#L135-L405) | Emits sampled graphics stages |
| Sparse image setup | [`SparseShaderIntrinsicsInstanceBase::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsBase.cpp#L574-L845) | Creates images and binds mip-level memory |
| Storage command recording | [`SparseShaderIntrinsicsInstanceStorage::recordCommands`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L531-L751) | Records barriers, descriptors, and dispatches |
| Result checking | [`SparseShaderIntrinsicsInstanceBase::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsBase.cpp#L986-L1238) | Compares texel and residency outputs |
