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
dEQP-VK.sparse_resources.shader_intrinsics.2d_sparse_read.<format>.11_37_1
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `2d_sparse_read` | Selects `SparseCaseOpImageSparseRead` and the compute storage-image path. |
| `<format>` | Keeps the format-dependent component and image declarations symbolic because the registration matrix supplies multiple formats. |
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

The source generator emits SPIR-V directly. The central generated sequence is [`sparseImageOpString`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L451-L463), followed by the result extraction and output writes in [`SparseShaderIntrinsicsCaseStorage::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesShaderIntrinsicsStorage.cpp#L327-L399). The source uses a format-dependent `OpTypeImage`, so this page does not substitute a hand-translated GLSL or HLSL reconstruction.

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

#### Source Code
116|
117|The following is the exact single-plane `R32_UINT` specialization emitted by `SparseShaderIntrinsicsCaseStorage::initPrograms`: `2d_sparse_read` selects `SparseCaseOpImageSparseRead`, the `11_37_1` extent selects a 2D coordinate, and the `R32_UINT` format supplies `%type_uint`, `%type_uvec4`, and `R32ui` image operands. The `sparseImageOpString` helper emits `OpImageSparseRead` without a mip-level operand because this case has no optional operand. The assembly was mechanically round-tripped through `spirv-as --target-env spv1.0`, `spirv-val --target-env spv1.0`, and `spirv-dis`; the matching `; Version: 1.0` header passed the validation gate.
118|
119|```llvm
OpCapability Shader
OpCapability ImageCubeArray
OpCapability SparseResidency
OpCapability StorageImageExtendedFormats
%ext_import = OpExtInstImport "GLSL.std.450"
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %func_main "main" %input_GlobalInvocationID
OpExecutionMode %func_main LocalSize 1 1 1
OpSource GLSL 440
OpName %func_main "main"
OpName %input_GlobalInvocationID "gl_GlobalInvocationID"
OpName %input_WorkGroupSize "gl_WorkGroupSize"
OpName %uniform_image_sparse_plane0 "u_imageSparse_plane0"
OpName %uniform_image_texels_plane0 "u_imageTexels_plane0"
OpName %uniform_image_residency_plane0 "u_imageResidency_plane0"
OpDecorate %input_GlobalInvocationID BuiltIn GlobalInvocationId
OpDecorate %input_WorkGroupSize BuiltIn WorkgroupSize
OpDecorate %constant_uint_grid_x SpecId 1
OpDecorate %constant_uint_grid_y SpecId 2
OpDecorate %constant_uint_grid_z SpecId 3
OpDecorate %constant_uint_work_group_size_x SpecId 4
OpDecorate %constant_uint_work_group_size_y SpecId 5
OpDecorate %constant_uint_work_group_size_z SpecId 6
OpDecorate %uniform_image_sparse_plane0 DescriptorSet 0
OpDecorate %uniform_image_sparse_plane0 Binding 0
OpDecorate %uniform_image_texels_plane0 DescriptorSet 0
OpDecorate %uniform_image_texels_plane0 Binding 1
OpDecorate %uniform_image_texels_plane0 NonReadable
OpDecorate %uniform_image_residency_plane0 DescriptorSet 0
OpDecorate %uniform_image_residency_plane0 Binding 2
OpDecorate %uniform_image_residency_plane0 NonReadable
%type_bool = OpTypeBool
%type_int = OpTypeInt 32 1
%type_uint = OpTypeInt 32 0
%type_float = OpTypeFloat 32
%type_ivec2 = OpTypeVector %type_int 2
%type_ivec3 = OpTypeVector %type_int 3
%type_ivec4 = OpTypeVector %type_int 4
%type_uvec3 = OpTypeVector %type_uint 3
%type_uvec4 = OpTypeVector %type_uint 4
%type_vec2 = OpTypeVector %type_float 2
%type_vec3 = OpTypeVector %type_float 3
%type_vec4 = OpTypeVector %type_float 4
%type_input_uint = OpTypePointer Input %type_uint
%type_input_uvec3 = OpTypePointer Input %type_uvec3
%type_function_int = OpTypePointer Function %type_int
%type_function_img_comp_vec4 = OpTypePointer Function %type_uvec4
%type_void = OpTypeVoid
%type_void_func = OpTypeFunction %type_void
%type_struct_int_img_comp_vec4_plane0 = OpTypeStruct %type_int %type_uvec4
%type_image_sparse_fmt98 = OpTypeImage %type_uint 2D 0 0 0 2 R32ui
%type_uniformconst_image_sparse_plane0 = OpTypePointer UniformConstant %type_image_sparse_fmt98
%type_uniformconst_image_residency_plane0 = OpTypePointer UniformConstant %type_image_sparse_fmt98
%uniform_image_sparse_plane0 = OpVariable %type_uniformconst_image_sparse_plane0 UniformConstant
%uniform_image_texels_plane0 = OpVariable %type_uniformconst_image_sparse_plane0 UniformConstant
%uniform_image_residency_plane0 = OpVariable %type_uniformconst_image_residency_plane0 UniformConstant
%input_GlobalInvocationID = OpVariable %type_input_uvec3 Input
%constant_uint_grid_x = OpSpecConstant %type_uint 1
%constant_uint_grid_y = OpSpecConstant %type_uint 1
%constant_uint_grid_z = OpSpecConstant %type_uint 1
%constant_uint_work_group_size_x = OpSpecConstant %type_uint 1
%constant_uint_work_group_size_y = OpSpecConstant %type_uint 1
%constant_uint_work_group_size_z = OpSpecConstant %type_uint 1
%input_WorkGroupSize = OpSpecConstantComposite %type_uvec3 %constant_uint_work_group_size_x %constant_uint_work_group_size_y %constant_uint_work_group_size_z
%constant_uint_0 = OpConstant %type_uint 0
%constant_uint_1 = OpConstant %type_uint 1
%constant_uint_2 = OpConstant %type_uint 2
%constant_int_0 = OpConstant %type_int 0
%constant_int_1 = OpConstant %type_int 1
%constant_int_2 = OpConstant %type_int 2
%constant_bool_true = OpConstantTrue %type_bool
%constant_uint_resident = OpConstant %type_uint 1
%constant_uvec4_resident = OpConstantComposite %type_uvec4 %constant_uint_resident %constant_uint_resident %constant_uint_resident %constant_uint_resident
%constant_uint_not_resident = OpConstant %type_uint 0
%constant_uvec4_not_resident = OpConstantComposite %type_uvec4 %constant_uint_not_resident %constant_uint_not_resident %constant_uint_not_resident %constant_uint_not_resident
%func_main = OpFunction %type_void None %type_void_func
%label_func_main = OpLabel
%access_GlobalInvocationID_x = OpAccessChain %type_input_uint %input_GlobalInvocationID %constant_uint_0
%local_uint_GlobalInvocationID_x = OpLoad %type_uint %access_GlobalInvocationID_x
%local_int_GlobalInvocationID_x = OpBitcast %type_int %local_uint_GlobalInvocationID_x
%access_GlobalInvocationID_y = OpAccessChain %type_input_uint %input_GlobalInvocationID %constant_uint_1
%local_uint_GlobalInvocationID_y = OpLoad %type_uint %access_GlobalInvocationID_y
%local_int_GlobalInvocationID_y = OpBitcast %type_int %local_uint_GlobalInvocationID_y
%access_GlobalInvocationID_z = OpAccessChain %type_input_uint %input_GlobalInvocationID %constant_uint_2
%local_uint_GlobalInvocationID_z = OpLoad %type_uint %access_GlobalInvocationID_z
%local_int_GlobalInvocationID_z = OpBitcast %type_int %local_uint_GlobalInvocationID_z
%local_ivec2_GlobalInvocationID_xy = OpCompositeConstruct %type_ivec2 %local_int_GlobalInvocationID_x %local_int_GlobalInvocationID_y
%local_ivec3_GlobalInvocationID_xyz = OpCompositeConstruct %type_ivec3 %local_int_GlobalInvocationID_x %local_int_GlobalInvocationID_y %local_int_GlobalInvocationID_z
%comparison_range_x = OpULessThan %type_bool %local_uint_GlobalInvocationID_x %constant_uint_grid_x
OpSelectionMerge %label_out_range_x None
OpBranchConditional %comparison_range_x %label_in_range_x %label_out_range_x
%label_in_range_x = OpLabel
%comparison_range_y = OpULessThan %type_bool %local_uint_GlobalInvocationID_y %constant_uint_grid_y
OpSelectionMerge %label_out_range_y None
OpBranchConditional %comparison_range_y %label_in_range_y %label_out_range_y
%label_in_range_y = OpLabel
%comparison_range_z = OpULessThan %type_bool %local_uint_GlobalInvocationID_z %constant_uint_grid_z
OpSelectionMerge %label_out_range_z None
OpBranchConditional %comparison_range_z %label_in_range_z %label_out_range_z
%label_in_range_z = OpLabel
%local_image_sparse_plane0 = OpLoad %type_image_sparse_fmt98 %uniform_image_sparse_plane0
%local_sparse_op_result_plane0 = OpImageSparseRead %type_struct_int_img_comp_vec4_plane0 %local_image_sparse_plane0 %local_ivec2_GlobalInvocationID_xy
%local_img_comp_vec4_plane0 = OpCompositeExtract %type_uvec4 %local_sparse_op_result_plane0 1
%local_residency_code_plane0 = OpCompositeExtract %type_int %local_sparse_op_result_plane0 0
%local_image_texels_plane0 = OpLoad %type_image_sparse_fmt98 %uniform_image_texels_plane0
OpImageWrite %local_image_texels_plane0 %local_ivec2_GlobalInvocationID_xy %local_img_comp_vec4_plane0
%local_image_residency_plane0 = OpLoad %type_image_sparse_fmt98 %uniform_image_residency_plane0
%local_texel_resident_plane0 = OpImageSparseTexelsResident %type_bool %local_residency_code_plane0
OpSelectionMerge %branch_texel_resident_plane0 None
OpBranchConditional %local_texel_resident_plane0 %label_texel_resident_plane0 %label_texel_not_resident_plane0
%label_texel_resident_plane0 = OpLabel
OpImageWrite %local_image_residency_plane0 %local_ivec2_GlobalInvocationID_xy %constant_uvec4_resident
OpBranch %branch_texel_resident_plane0
%label_texel_not_resident_plane0 = OpLabel
OpImageWrite %local_image_residency_plane0 %local_ivec2_GlobalInvocationID_xy %constant_uvec4_not_resident
OpBranch %branch_texel_resident_plane0
%branch_texel_resident_plane0 = OpLabel
OpBranch %label_out_range_z
%label_out_range_z = OpLabel
OpBranch %label_out_range_y
%label_out_range_y = OpLabel
OpBranch %label_out_range_x
%label_out_range_x = OpLabel
OpReturn
OpFunctionEnd

246|```
247|
248|## Runtime Execution and Result Checking

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

309|
