## Overview

**Core question:** Do Vulkan storage-image and storage-texel-buffer atomics update the addressed location and return values consistent with one legal serialization of competing compute invocations?

- [`vktImageAtomicOperationTests.cpp`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp) implements the `image.atomic_operations` test family and its generated case matrix.
- Each selected operation runs five compute invocations against each logical texel. For image resources, the test checks either the settled texel value or the old values returned by those atomics; storage texel-buffer cases use the corresponding buffer location.
- The family covers integer, feature-gated floating-point, 64-bit, and half-vector formats; image and buffer shapes; transfer and shader-based initialization/readback; and, outside Vulkan SC, sparse-resource variants.

## Background Knowledge

- **Atomic image access.** An image atomic addresses one texel through an image-texel pointer, reads and updates that location as one atomic operation, and returns the value from before its update. SPIR-V image atomics use `OpImageTexelPointer` to obtain the texel location before the atomic instruction accesses it.
- **Unspecified contention order.** Five invocations contend for each logical texel. The test cannot require one invocation order, so it checks a final value only where the operation's result is independent of that order, or accepts returned values that form some valid serial sequence.

## Registration Hierarchy

```text
image.atomic_operations
├── add
├── sub
├── inc
├── dec
├── min
├── max
├── and
├── or
├── xor
├── exchange
└── compare_exchange
```

[`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L89) registers `atomic_operations` under the `image` test category. [`createImageAtomicOperationTests()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2477-L2655) registers these eleven operation values and the leaves below each one.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Atomic operation | `add`, `sub`, `inc`, `dec`, `min`, `max`, `and`, `or`, `xor`, `exchange`, `compare_exchange` | Selects the atomic instruction and the reference rule. | [Operation enum and factory](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L306-L321) |
| Resource shape | `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array`, `buffer` | Changes coordinate dimensionality, layer handling, image-view type, and, for `buffer`, descriptor type. | [Image parameter array](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2481-L2499) |
| Format | `r32ui`, `r32i`, `r32f`, `r64ui`, `r64i`, plus non-Vulkan-SC `rg16f` and `rgba16f` | Selects integer, float, 64-bit, or half-vector operation and reference type. | [Format array](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2501-L2511) |
| Tiling | optimal; `linear` suffix | Changes format-feature support and excludes unsupported sparse or buffer combinations. | [Tiling array and factory pruning](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2513-L2516) |
| Initialization and readback | `notransfer`, `transfer` | `notransfer` uses generated fill/read compute shaders. `transfer` copies input data into the image and result data back to a buffer. | [Shared iteration path](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1515-L1663) |
| Shader read type | `normal_read`, plus non-Vulkan-SC `sparse_read` | Selects normal readback or a shader that also compares normal and sparse image loads. | [Read modes and support check](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L897-L950) |
| Backing type | `normal_img`, plus non-Vulkan-SC `sparse_img` | Selects ordinary allocation or sparse binding/residency setup for an image. | [Backing modes and sparse creation](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2530-L2538) |
| Result-checking leaf | `*_end_result`, `*_intermediate_values` | Selects final-state checking or validation of the five old values returned by the atomics. | [Leaf creation](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2626-L2636) |

The source dispatches `NUM_INVOCATIONS_PER_PIXEL`, fixed at five, times the logical x dimension. The shader folds `gx` back to the logical x coordinate with modulo arithmetic, which makes those five invocations target the same texel.

## Behavior Parameters

The primary behavioral axis is **atomic operation**. The type, compute-stage, resource, and result-checking dimensions select legal forms and observability for the selected operation.

### `add`: Addition

`add` adds a generated argument to each addressed value. It uses `imageAtomicAdd` in generated GLSL and checks the operation-specific initial value plus all five arguments.

### `sub`: Subtraction

`sub` subtracts the generated argument. It uses a specialized SPIR-V assembly shader with `OpAtomicISub`, then applies the five arguments to the initial value in the reference calculation.

### `inc`: Increment

`inc` increments by one for each contender. Its assembly shader uses `OpAtomicIIncrement`, which has no final argument operand.

### `dec`: Decrement

`dec` decrements by one for each contender. Its assembly shader uses `OpAtomicIDecrement`, also without the final argument operand.

### `min`: Minimum

`min` retains the smallest submitted value or initial value. The generated arguments include positive and negative values for signed and floating-point formats, while unsigned arithmetic naturally interprets the corresponding values as large unsigned values.

### `max`: Maximum

`max` retains the largest submitted value or initial value. Float `max` requires the feature path for float min/max atomics.

### `and`: Bitwise AND

`and` combines the initial value and five generated integer arguments with bitwise AND. It is absent from the floating-point format branches.

### `or`: Bitwise OR

`or` combines the initial value and five generated integer arguments with bitwise OR. It shares the ordinary generated GLSL path with the other integer operations.

### `xor`: Bitwise XOR

`xor` combines the initial value and five generated integer arguments with bitwise XOR. The final check recomputes the same sequence from the source-generated arguments.

### `exchange`: Replacement

`exchange` replaces the texel with an invocation-specific argument. Since the final writer is not predetermined, the final-state check accepts any one of the five submitted arguments.

### `compare_exchange`: Conditional replacement

`compare_exchange` replaces a texel only when its old value equals the fixed comparison value: 18 for 32-bit paths and 820338753304 for 64-bit paths. Its final-state check accepts a submitted replacement value, because one contender can win the comparison before the value changes.

## Shader Analysis

[`BinaryAtomicEndResultCase::initPrograms()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1194-L1275) generates ordinary GLSL for this representative case. It selects SPIR-V assembly only for `sub`, `inc`, and `dec`. The walkthrough uses `add` because it shows the shared coordinate folding, generated argument, and compute-stage atomic path directly.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.atomic_operations.add.1d.notransfer.normal_read.normal_img.r32ui_end_result
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `add` | Calls `imageAtomicAdd` and permits an order-independent final-value check. |
| `1d` | Uses a 64-element storage image and scalar integer coordinates. |
| `notransfer` | Uses generated compute shaders to fill the image and read its result. |
| `normal_read.normal_img` | Uses ordinary image backing and ordinary image readback. |
| `r32ui_end_result` | Uses `uimage1D` with `r32ui` storage and checks only the final texel values. |

#### Purpose

The shader creates five atomic additions to every logical texel. `gx % 64` directs invocations 0 through 63, 64 through 127, and the next three 64-invocation ranges to the same 64 image elements. The host verifies the resulting sum at each element.

#### Structural Design

| Shader element | Action | Tested property |
|----------------|--------|-----------------|
| Global invocation ID | Converts each unsigned component to `int`. | Derives the generated coordinate and argument. |
| Folded coordinate | Uses `gx % 64`. | Creates five-way contention for each logical 1D texel. |
| Generated argument | Computes `gx*gx + gy*gy + gz*gz` and converts it to `uint`. | Gives each contender an observable, distinct addend. |
| Atomic call | Executes `imageAtomicAdd` on binding 0. | Atomically updates the selected `r32ui` storage-image texel. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_shader_atomic_float : enable
#extension GL_EXT_shader_atomic_float2 : enable
#extension GL_KHR_memory_scope_semantics : enable
#extension GL_EXT_shader_explicit_arithmetic_types_float16 : enable
#extension GL_NV_shader_atomic_fp16_vector : enable

/// The selected image type is a one-dimensional unsigned integer storage image.
precision highp uimage1D;

/// One invocation per workgroup makes the global ID the generated dispatch coordinate.
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 exposes the initialized result image for coherent atomic access.
layout (r32ui, binding=0) coherent uniform uimage1D u_resultImage;

void main (void)
{
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);
    int gz = int(gl_GlobalInvocationID.z);
    /// Five x ranges fold onto the same 64 logical texels; each call contributes its coordinate-derived addend.
    imageAtomicAdd(u_resultImage, gx % 64, uint(gx*gx + gy*gy + gz*gz));
}
```

#### Additional Info

- The CTS generator emits the same extension block for the ordinary GLSL path. This selected unsigned-integer `add` case does not depend on the float or float16 extensions it enables.
- The selected case receives SPIR-V 1.0 through the default `SourceCollections` shader-build path. The fill and readback shaders explicitly use SPIR-V 1.3, but they are not the atomic shader analyzed here.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Operation | Changes the atomic function and argument shape; `compare_exchange` adds a typed comparison value. `sub`, `inc`, and `dec` replace GLSL with specialized SPIR-V assembly. | [Operation mapping and generator branch](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L475-L498) |
| Image shape | Changes coordinate scalar/vector form and storage image type. `buffer` uses a storage texel-buffer descriptor rather than an image descriptor. | [Coordinate and type selection](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L335-L354) |
| Format | Changes image format qualifier, scalar/vector type, extension declarations, and selected atomic-operation legality. | [Support checks](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L987-L1141) |
| Result-checking leaf | `intermediate_values` adds binding 1 and stores the old value returned by the atomic call at the unfurled invocation coordinate. | [Intermediate shader generator](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1356-L1417) |
| Initialization/readback mode | `notransfer` produces fill/read compute shaders. `transfer` initializes and reads back with buffer-image copies. | [Program and execution branches](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1204-L1207) |

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
; Bound: 50
; Schema: 0
               OpCapability Shader
               OpCapability Image1D
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_shader_atomic_float"
               OpSourceExtension "GL_EXT_shader_atomic_float2"
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types_float16"
               OpSourceExtension "GL_KHR_memory_scope_semantics"
               OpSourceExtension "GL_NV_shader_atomic_fp16_vector"
               OpName %main "main"
               OpName %gx "gx"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %gy "gy"
               OpName %gz "gz"
               OpName %u_resultImage "u_resultImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %u_resultImage Coherent
               OpDecorate %u_resultImage Binding 0
               OpDecorate %u_resultImage DescriptorSet 0
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
     %uint_2 = OpConstant %uint 2
         %28 = OpTypeImage %uint 1D 0 0 0 2 R32ui
%_ptr_UniformConstant_28 = OpTypePointer UniformConstant %28
%u_resultImage = OpVariable %_ptr_UniformConstant_28 UniformConstant
     %int_64 = OpConstant %int 64
%_ptr_Image_uint = OpTypePointer Image %uint
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %gx = OpVariable %_ptr_Function_int Function
         %gy = OpVariable %_ptr_Function_int Function
         %gz = OpVariable %_ptr_Function_int Function
         %15 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %16 = OpLoad %uint %15
         %17 = OpBitcast %int %16
               OpStore %gx %17
         %20 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %21 = OpLoad %uint %20
         %22 = OpBitcast %int %21
               OpStore %gy %22
         %25 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %26 = OpLoad %uint %25
         %27 = OpBitcast %int %26
               OpStore %gz %27
         %31 = OpLoad %int %gx
         %33 = OpSMod %int %31 %int_64
         %34 = OpLoad %int %gx
         %35 = OpLoad %int %gx
         %36 = OpIMul %int %34 %35
         %37 = OpLoad %int %gy
         %38 = OpLoad %int %gy
         %39 = OpIMul %int %37 %38
         %40 = OpIAdd %int %36 %39
         %41 = OpLoad %int %gz
         %42 = OpLoad %int %gz
         %43 = OpIMul %int %41 %42
         %44 = OpIAdd %int %40 %43
         %45 = OpBitcast %uint %44
         %47 = OpImageTexelPointer %_ptr_Image_uint %u_resultImage %33 %uint_0
         %48 = OpAtomicIAdd %uint %47 %uint_1 %uint_0 %45
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host allocates a host-visible input buffer, initializes every logical element with the operation-specific initial value, allocates an output buffer, and creates either image resources or a storage texel-buffer view. For non-buffer resources, it creates the result image with `VK_IMAGE_USAGE_STORAGE_BIT`; transfer leaves also include transfer source and destination usage.
- `notransfer` leaves dispatch a generated fill shader to write the initialized input-buffer values into the result image. `transfer` leaves copy the buffer into an image in `VK_IMAGE_LAYOUT_GENERAL`. Buffer leaves use the initialized input buffer directly as the storage texel-buffer backing.
- The atomic compute pipeline dispatches `5 * gridSize.x()` by `gridSize.y()` by `gridSize.z()` workgroups. For intermediate-value leaves, the atomic shader writes each returned old value into a second resource sized for the extended invocation grid.
- After the atomic dispatch, transfer leaves transition the result image to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` and copy it to the output buffer. Shader-readback leaves use a compute read shader after a shader-write-to-shader-read barrier. A final buffer barrier makes output visible to the host before allocation invalidation and verification.
- End-result verification recomputes the expected result per logical texel. Intermediate verification gathers five old values and five arguments, then recursively searches assignments that could form one legal serial ordering of those atomics.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `add` | Atomic addition, generated addend addressing, or final/intermediate result capture and validation. |
| `sub` | `OpAtomicISub` execution or its specialized SPIR-V assembly, result capture, or validation. |
| `inc` | `OpAtomicIIncrement` execution or its specialized SPIR-V assembly, result capture, or validation. |
| `dec` | `OpAtomicIDecrement` execution or its specialized SPIR-V assembly, result capture, or validation. |
| `min` | Atomic minimum semantics for the selected signed, unsigned, or floating-point type, or result validation. |
| `max` | Atomic maximum semantics for the selected signed, unsigned, or floating-point type, or result validation. |
| `and` | Atomic bitwise AND semantics, generated operand values, or result validation. |
| `or` | Atomic bitwise OR semantics, generated operand values, or result validation. |
| `xor` | Atomic bitwise XOR semantics, generated operand values, or result validation. |
| `exchange` | Atomic exchange return/final-state semantics or acceptance of one of the submitted arguments. |
| `compare_exchange` | Conditional compare-and-swap semantics, comparison-value typing, or acceptance of a submitted replacement value. |

### Cause Analysis

#### Arithmetic and bitwise atomic execution

**Possible failure symptoms:** `add`, `sub`, `inc`, `dec`, `min`, `max`, `and`, `or`, or `xor` reports a comparison failure when a final texel differs from the reference or when five returned values cannot form a valid sequence.

**Possible implementation causes:** The selected operation can fail in typed image atomic execution, coordinate-to-texel addressing, generated operand evaluation, or write/readback synchronization. `sub`, `inc`, and `dec` also exercise the specialized SPIR-V instructions rather than the ordinary generated GLSL path. A source-level investigation should compare the failing format, resource shape, and result-check leaf with a passing nearby case to separate those paths.

#### Exchange and compare-and-swap ordering

**Possible failure symptoms:** `exchange` or `compare_exchange` reports a final texel that matches none of the five generated arguments, or an intermediate-values leaf cannot arrange the returned values into a valid sequence.

**Possible implementation causes:** The final writer for `exchange` depends on the legal execution order. `compare_exchange` also depends on correct comparison against the operation's fixed initial value and typed comparison constant. Incorrect old-value returns, conditional replacement, image-atomic serialization, or result capture can produce this symptom.

#### Feature-gated type or resource path

**Possible failure symptoms:** Failures cluster in `r32f` min/max, 64-bit integer, half-vector, sparse-backing, sparse-read, linear-tiling, or buffer leaves while ordinary `r32ui` image leaves pass.

**Possible implementation causes:** The support checks select extension features and format capabilities before execution. A failure after the case runs can arise from the selected typed image atomic capability, the format-specific image or texel-buffer descriptor path, sparse binding/residency behavior, or the same copy/readback path used to observe the result. The CTS code itself raises `NotSupportedError` when required advertised features are absent, so an executed failing case has passed those preconditions.

#### Final-state or returned-value validation path

**Possible failure symptoms:** An `*_end_result` leaf fails while an equivalent `*_intermediate_values` leaf passes, or the reverse, for the same operation and resource configuration.

**Possible implementation causes:** End-result leaves use an exact reference for the order-independent operations and membership in the submitted arguments for `exchange` and `compare_exchange`. Intermediate leaves instead validate an ordering witness with `verifyRecursive()`. A discrepancy can point to the different output resource, copyback path, return-value write, or host verification rule; source-level investigation should determine whether the observed values or the selected validation condition first diverged.

## Case Pruning

### Requirement-based pruning

- All image cases require the selected format and tiling to support storage-image access and storage-image atomics. Buffer cases require both storage texel-buffer and atomic storage texel-buffer format features. Linear cases explicitly require linear-tiling storage-image and atomic support.
- `r32f` cases require `VK_EXT_shader_atomic_float` and `shaderImageFloat32Atomics`; float `add` also requires `shaderImageFloat32AtomicAdd`. Float `min` and `max` require `VK_EXT_shader_atomic_float2` and `shaderImageFloat32AtomicMinMax` outside Vulkan SC.
- `r64ui` and `r64i` require `VK_EXT_shader_image_atomic_int64` and `shaderImageInt64Atomics`. Non-Vulkan-SC half-vector formats require `VK_NV_shader_atomic_float16_vector` and `shaderFloat16VectorAtomics`.
- Sparse backing requires sparse binding, the matching 2D or 3D sparse-residency feature, and sparse image format support. Sparse float and 64-bit integer operations also require their sparse atomic feature bits. Sparse reads require shader resource residency. Cube arrays require the cube-array image feature.
- Transfer leaves require transfer-source and transfer-destination format features.

### Design-based pruning

- The factory does not register linear-tiled integer buffer leaves. Those cases would require the SPIR-V program path for the relevant atomics, but the source excludes the combination.
- Sparse backing is limited to resource shapes that map to 2D or 3D Vulkan images, and excludes linear tiling. Sparse shader reads exclude 1D, 1D-array, and buffer shapes. `sparse_read` also excludes `transfer`, because transfer readback would make it duplicate the normal-read result path.
- Floating-point formats retain `add` and `exchange`; non-Vulkan-SC builds also retain `min` and `max`. Integer-only operations remain absent because the generated reference operations do not define meaningful float bitwise behavior.
- Each legal matrix combination produces both final-state and returned-value leaves. This intentional duplication observes two distinct atomic contracts rather than adding redundant cases.

## Key Takeaways

- The family uses five invocations per logical texel to turn atomic serialization into an observable property without requiring a particular schedule.
- Final-state leaves cover the settled storage location. Intermediate-value leaves cover the old values returned by the atomic instructions and accept any complete legal serial sequence.
- `sub`, `inc`, and `dec` test SPIR-V atomic instructions through specialized assembly, while the other operations use generated GLSL.
- Feature gates and pruning keep floating-point, 64-bit, half-vector, sparse, linear, and texel-buffer cases within the capabilities that the selected operation and resource form require.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L89) | Places `atomic_operations` in the `image` test category. |
| Image atomic semantics | [`images.adoc#L248-L263`](../../../../vulkan-docs/src/chapters/images.adoc#L248-L263) | Defines image-texel pointers as the location used by SPIR-V atomics. |
| Operation and reference helpers | [`vktImageAtomicOperationTests.cpp#L301-L808`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L301-L808) | Defines operations, initial values, generated arguments, order classification, and reference arithmetic. |
| Support checks | [`commonCheckSupport()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L987-L1141) | Checks format, extension, feature, sparse, and transfer requirements. |
| Generated atomic shaders | [`BinaryAtomicEndResultCase::initPrograms()` and `BinaryAtomicIntermValuesCase::initPrograms()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1194-L1418) | Generates GLSL and selects specialized SPIR-V assembly. |
| Shared execution path | [`BinaryAtomicInstanceBase::iterate()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1498-L1663) | Allocates resources, initializes, dispatches, synchronizes, reads back, and reports pass/fail. |
| Validation | [`BinaryAtomicEndResultInstance::verifyResult()` and `BinaryAtomicIntermValuesInstance::verifyRecursive()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1935-L2099) | Implements final-value and returned-value sequence checks. |
| Case matrix factory | [`createImageAtomicOperationTests()`](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2477-L2655) | Registers the operation, type, resource, and result-checking matrix. |
| SPIR-V template interface | [`vktImageAtomicSpirvShaders.hpp`](../../../modules/vulkan/image/vktImageAtomicSpirvShaders.hpp#L35-L57) | Defines selection of specialized templates for the SPIR-V-only operations. |
