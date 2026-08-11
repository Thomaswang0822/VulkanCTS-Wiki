## Overview

**Core question:** When `VK_KHR_workgroup_memory_explicit_layout` is enabled, does the implementation honor `Aliased`
workgroup-memory blocks, explicit `Offset` decorations on `Workgroup` block members, and `OpCopyMemory` between
workgroup and storage objects, and does it keep doing so when `VK_KHR_zero_initialize_workgroup_memory`
is also required?

- [vktComputeWorkgroupMemoryExplicitLayoutTests.cpp](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1289-L1324)
  implements the `workgroup_memory_explicit_layout` test family under
  `dEQP-VK.compute.pipeline.workgroup_memory_explicit_layout`.
- The page also files the registered `alias`, `zero`, `padding`, `size`, `copy_memory`, and `zero_ext` test families
  under the same root.
- The four C++-implemented families each stress a different aspect of the explicit-layout contract: aliasing
  between typed workgroup blocks, manual zeroing of one block then reading another, layout-aware padding inside a
  block, and the device's `maxComputeSharedMemorySize` limit. The two Amber families reuse the contract to test
  `OpCopyMemory` and the interaction with `VK_KHR_zero_initialize_workgroup_memory`.
- Each C++ family compiles a per-case GLSL compute shader with a one-uint storage-buffer result and dispatches once.
  The host pre-fills the result buffer with `0xff`; `alias` writes the expected invocation index only on success, while
  `zero`, `padding`, and `size` always write a zero-on-success mismatch count. The Amber families check the result
  buffer with Amber `EXPECT` commands.

## Background Knowledge

- **Workgroup memory aliasing in SPIR-V.** The extension adds the SPIR-V capability `WorkgroupMemoryExplicitLayoutKHR`
  and the `SPV_KHR_workgroup_memory_explicit_layout` extension. With these, a compute shader may decorate an
  `OpVariable` in the `Workgroup` storage class with `Aliased`, allowing two `shared` blocks to share the same base
  address. Members of a `Workgroup` block may also carry an `OpMemberDecorate Offset` decoration so the implementation
  honors an explicit byte layout rather than computing one itself
  ([AliasTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L424-L505),
  [PaddingTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1018-L1067)).
- **Feature bits `workgroupMemoryExplicitLayout*`.** The Vulkan feature struct
  `VkPhysicalDeviceWorkgroupMemoryExplicitLayoutFeaturesKHR` exposes the core feature
  `workgroupMemoryExplicitLayout`, plus `workgroupMemoryExplicitLayoutScalarBlockLayout`,
  `workgroupMemoryExplicitLayout8BitAccess`, and `workgroupMemoryExplicitLayout16BitAccess`. Each C++ test gates itself
  on the smallest subset of these bits the case requires
  ([checkSupportWithParams](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L77-L141)).
- **`OpCopyMemory` semantics in `Workgroup`.** The Amber scripts use `OpCopyMemory` to copy identically typed objects
  between `Workgroup` and `StorageBuffer`. They deliberately split a same-type whole-block copy from an array copy
  driven through `OpAccessChain`: the latter is needed because the containing block types have different member
  offsets and therefore cannot be copied directly as one identically typed object
  ([copy_memory_basic.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_basic.amber),
  [copy_memory_two_invocations.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_two_invocations.amber)).
- **Zero-initialize interaction.** The `zero_ext` Amber cases rely on `VK_KHR_zero_initialize_workgroup_memory` (or its
  Vulkan 1.4 core form `shaderWorkgroupMemoryZeroInitialize`) to zero a `Workgroup` variable carrying an
  `OpConstantNull` initializer. `other_block` verifies that an uninitialized aliased sibling observes those zeros.
  In `block_with_offset`, the initialized variable's member starts at byte offset 64, so only bytes 64 through 127 of
  the uninitialized aliased variable are required to read zero
  ([zero_ext_block.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block.amber),
  [zero_ext_other_block.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_other_block.amber),
  [zero_ext_block_with_offset.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block_with_offset.amber)).

## Registration Hierarchy

```text
compute.pipeline.workgroup_memory_explicit_layout
├── alias
├── zero
├── padding
├── size
├── copy_memory (pipeline only)
└── zero_ext (pipeline only)
```

The `copy_memory` and `zero_ext` children are not registered under the `shader_object_spirv` and `shader_object_binary`
roots because Amber cannot drive compute pipelines as shader objects; the factory guards on
`isComputePipelineConstructionTypeShaderObject`
([createWorkgroupMemoryExplicitLayoutTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1312-L1321),
[vktComputeTests.cpp#L48-L64](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L64),
[vktComputeTests.cpp#L68-L85](../../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85)).

## Parameter Dimensions and Observed Values

The page is a generated-matrix page. The dimensions below keep the registered values and add why each dimension matters
for this test.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Layout features | `workgroupMemoryExplicitLayout` (always), `workgroupMemoryExplicitLayoutScalarBlockLayout`, `workgroupMemoryExplicitLayout8BitAccess`, `workgroupMemoryExplicitLayout16BitAccess` | Cases gate on the smallest subset of these bits that the type pair or layout qualifier needs. | [checkSupportWithParams](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L77-L141) |
| Numeric types | 8-, 16-, 32-, and 64-bit integer and floating-point scalar/vector types (family-dependent) | Case data and `useType()` select the matching support checks, so an 8-bit case and a 64-bit floating-point case gate on different features. | [CheckSupportParams::useType](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L66-L74), [AddAliasTests case data](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L562-L634), [ZeroTest::checkSupport](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L738-L750) |
| Block layout qualifier | `default`, `std140`, `std430`, `scalar` | `alias` and `padding` cross-test the qualifier. The `scalar` qualifier requires `workgroupMemoryExplicitLayoutScalarBlockLayout` and the `GL_EXT_scalar_block_layout` extension plus `FLAG_ALLOW_WORKGROUP_SCALAR_OFFSETS` at compile time. | [AliasTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L424-L505), [PaddingTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1018-L1067) |
| Function shape | `none`, `read`, `write`, `read_write` | `alias` cross-tests helper-function access. `read` calls a read helper, `write` calls a write helper, and `read_write` calls the read helper but performs the write inline (its emitted write helper is unused). | [AliasTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L461-L497) |
| Synchronization | `none`, `barrier` | `alias` optionally inserts `barrier()` between the write and read. Because every alias shader has local size `1 × 1 × 1`, this is a single-invocation barrier variant, not cross-invocation communication. | [AliasTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L452-L486) |
| Workgroup-memory size | `8`, `64`, `4096`, `16384`, `32768`, `49152`, `65536` bytes | `size` compares each declared block with `maxComputeSharedMemorySize` and skips larger sizes with `NotSupportedError`. | [AddSizeTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1211-L1229), [SizeTest::checkSupport](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1153-L1159) |
| Pipeline construction type | `pipeline`, `shader_object_spirv`, `shader_object_binary` | The category dispatcher mounts the family under all three roots; the factory drops `copy_memory` and `zero_ext` under the shader-object roots. | [vktComputeTests.cpp#L48-L85](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85), [createWorkgroupMemoryExplicitLayoutTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1312-L1321) |

## Behavior Parameters

The primary behavioral axis is the **test family** under `compute.pipeline.workgroup_memory_explicit_layout`. Each
family picks a different shape of workgroup memory and a different mechanism to stress while sharing the same
explicit-layout contract.

### alias: Two typed workgroup blocks share the same memory

`alias` declares two `shared` blocks whose members carry `Aliased` and `OpMemberDecorate Offset` decorations, writes a
distinguishing pattern to block `A`, and checks that block `B` reads the same bytes reinterpreted as a different type
or layout. The case data list enumerates the type pair, the qualifier mask, and the feature requirements; the helper
loops then expand every combination of layout qualifier, function shape, and synchronization that the case data
allows
([AddAliasTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L536-L671)).
The simplest case is `vec4_array_to_vec2_array_default`, which uses standard `vec4`/`vec2` types and the default
layout qualifier.

### zero: One block is manually zeroed, the other is read

`zero` declares a large `shared A` of one element type and a `shared B` containing four struct elements, populates `A`
with non-zero and then zero values, and checks that all four elements of `B` read zero. The case matrix iterates
element types (`uint`, `uvec4`, `uint8_t`, `uvec4_8bit`, `uint16_t`), field types (`uint`, `uvec3`, `uint8_t`,
`uint16_t`, `float`, `fvec4`, `float16_t`, `double`, `dvec4`, `bool`), and an `elements` value from `1` to `4`.
The generated shader does not use `CaseDef::elements`: it always declares and checks `arr[4]`, so this value currently
changes only the test-case name and creates four behaviorally duplicate variants
([AddZeroTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L877-L915)).

### padding: `OpMemberDecorate Offset` controls which word of a backing array is populated

`padding` declares a backing `shared A { uint32_t words[32]; }` and a `shared B` block whose members carry explicit
`layout(offset = N)` qualifiers. The shader writes two values to `B` and computes how many of the 32 backing words
differ from their expected value; zero mismatches passes. One flavor uses 32-bit `uint` slots (offsets always multiples of 4); the other uses 8-bit
`uint8_t` slots (offsets can be any byte), which requires `layout(scalar)` and
`workgroupMemoryExplicitLayoutScalarBlockLayout`
([AddPaddingTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1069-L1108)).

### size: Eight workgroup blocks of a fixed byte size

`size` declares eight aliased `shared B_i { uint32_t words[size/4]; }` views, has invocation `0` fill `b0` with
`0xFFFF`, then has each of the eight invocations write its stripe through the correspondingly numbered view. After a
barrier, invocation `0` checks the combined pattern through `b0`. The `size` parameter is the aliased region's size in
bytes; the test supports `8`,
`64`, `4096`, `16384`, `32768`, `49152`, and `65536`, and skips larger ones with `NotSupportedError`
([AddSizeTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1211-L1229)).

### copy_memory: Amber `OpCopyMemory` between workgroup and storage blocks

`copy_memory` loads three Amber scripts. `basic` declares three aliased workgroup blocks and copies two storage
buffers into the first half of workgroup memory through `OpCopyMemory` (whole-variable when types match, `OpAccessChain`
otherwise), then copies the whole aliased block to an output buffer. `two_invocations` selects the copying invocations
through push constants and inserts an `OpControlBarrier`. `variable_pointers` exercises a similar copy with variable
pointers and `VK_EXT_descriptor_indexing`
([copy_memory_basic.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_basic.amber),
[copy_memory_two_invocations.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_two_invocations.amber),
[copy_memory_variable_pointers.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_variable_pointers.amber),
[AddCopyMemoryTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1256-L1269)).

### zero_ext: Zero-init interaction between two aliased workgroup blocks

`zero_ext` loads three Amber scripts. `block` declares one initialized workgroup block and copies it to output.
`other_block` adds an uninitialized aliased sibling and copies that sibling to verify it observes the initialized
block's zeros. `block_with_offset` instead puts `OpMemberDecorate Offset 64` on the initialized block and copies the
uninitialized, offset-zero sibling, so only output bytes 64 through 127 are expected to be zero
([zero_ext_block.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block.amber),
[zero_ext_other_block.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_other_block.amber),
[zero_ext_block_with_offset.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block_with_offset.amber),
[AddZeroInitializeExtensionTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1271-L1285)).

## Shader Analysis

Each test family emits its own compute shader. The page uses one walkthrough for `alias.vec4_array_to_vec2_array_default`
because that shader carries the highest signal of the aliasing contract: two blocks with different `vec4`/`vec2` types
share the same 48 bytes of workgroup memory and the test verifies a byte-exact cross-type reinterpretation. The
remaining families are summarized under `Parameter Variation Summary` because they only change the parameter dimension.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
compute.pipeline.workgroup_memory_explicit_layout.alias.vec4_array_to_vec2_array_default
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `alias` | Selects the cross-type workgroup-block family; produces two `shared` blocks with the `Aliased` decoration. |
| `vec4_array_to_vec2_array_default` | The simplest cross-type pair: standard `vec4[3]` writer and `vec2[6]` reader, default layout qualifier, no function-shape helpers, no `barrier()`. |
| `_default` layout | The block layout qualifier is left blank; the `GL_EXT_scalar_block_layout` extension is **not** enabled. |
| `FunctionNone` / `SynchronizationNone` | The shader writes the pattern directly into `a.v` and reads it directly through `b.v`; no `read()` / `write()` helper functions are emitted and no `barrier()` is inserted. |
| `Requirements = 0` | No `useType()` flag flips; the case gates on nothing beyond `workgroupMemoryExplicitLayout` and `VK_KHR_spirv_1_4`. |

#### Purpose

This shader verifies that two `Aliased` `Workgroup` blocks whose `Block` members carry `OpMemberDecorate Offset 0` and
whose array strides match (16 vs. 8) actually share the same base address, so a write through the `vec4[3]` view is
read back byte-exactly through the `vec2[6]` view.

#### Structural Design

| Step | Invocation action | Memory affected | What is checked |
|------|-------------------|-----------------|-----------------|
| 1 | Build the `vec4[3]` pattern as a constant composite array. | none | Establishes the source pattern `(1,1,2,2)(3,3,4,4)(5,5,6,6)`. |
| 2 | `OpAccessChain` into `a.v`, then `OpCopyLogical` followed by `OpStore` the constant composite. | `shared A { vec4 v[3]; }` (offset 0, stride 16) | Writes 48 bytes to the aliased region. |
| 3 | `OpAccessChain` into `b.v` and load the `vec2[6]` array. | `shared B { vec2 v[6]; }` (offset 0, stride 8) | Reads 48 bytes from the same aliased region. |
| 4 | Compare each of the six `vec2` elements against `(1,1)(2,2)(3,3)(4,4)(5,5)(6,6)`; if all match, store `index` into `Result`. | `Result { uint result; }` (binding 0) | A non-zero entry would imply the read pattern does not equal the write pattern. |
| 5 | The host scans `Result` and expects `index` (here `0`). | n/a | The pre-fill of `0xff` makes any failure visible. |

#### Shader Code

Reconstructed GLSL for this path:

```glsl
#version 450
#extension GL_EXT_shared_memory_block : enable
#extension GL_EXT_shader_explicit_arithmetic_types : enable

/// Both blocks must end up at the same base address; the extension's
/// Aliased decoration on the OpVariable tells the implementation it may reuse memory.
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Writer block: 3 vec4s = 48 bytes (ArrayStride 16).
shared A { vec4 v[3]; } a;
/// Reader block: 6 vec2s = 48 bytes (ArrayStride 8); same 48 bytes, reinterpreted.
shared B { vec2 v[6]; } b;
/// Single-slot pass/fail counter; host pre-fills with 0xff so any non-write is observable.
layout(set = 0, binding = 0) buffer Result { uint result; };

void main() {
  /// FunctionNone path: write the pattern directly into a.v, no helper call.
  int index = int(gl_LocalInvocationIndex);
  a.v = vec4[3] (vec4(1, 1, 2, 2), vec4(3, 3, 4, 4), vec4(5, 5, 6, 6));

  /// SynchronizationNone path: no barrier(); read back through b.v and check against
  /// the per-element vec2 pattern. If the entire array matches, record index in Result.
  if (b.v == vec2[6] (vec2(1), vec2(2), vec2(3), vec2(4), vec2(5), vec2(6)))
    result = index;
}
```

#### Additional Info

- The build flag `FLAG_ALLOW_WORKGROUP_SCALAR_OFFSETS` is **not** set for this case because the qualifier is the
  default one; only `LayoutScalar` flips that flag and adds `GL_EXT_scalar_block_layout`
  ([AliasTest::initPrograms build flags](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L499-L504)).
- The `vec4_array_to_vec2_array_*` case family is allowed under every qualifier (`DEFAULT | STD430 | SCALAR` plus
  `STD140` for some variants), so the `LayoutDefault` test is the cleanest representative of the cross-type
  reinterpretation rule; the same block pair under `layout(std430)` exercises the same memory, while under
  `layout(std140)` a different offset pattern is expected
  ([alias case data lines 613-628](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L613-L628)).
- The same GLSL pattern is reused across `func_*` and `barrier()` modifiers. `FunctionRead` calls `read()`,
  `FunctionWrite` calls `write()`, and `FunctionReadWrite` calls `read()` but leaves the write inline (despite also
  emitting an unused `write()` helper). `SynchronizationBarrier` emits `barrier();`
  ([AliasTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L461-L497),
  [AddAliasTests loop](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L641-L670)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Block layout qualifier | `_std140`, `_std430`, and `_scalar` variants change the generated `layout(...)` qualifier before each `shared` block; `_scalar` also enables `GL_EXT_scalar_block_layout` and sets `FLAG_ALLOW_WORKGROUP_SCALAR_OFFSETS`. | [AliasTest::initPrograms layout switch](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L426-L451), [build flag switch](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L499-L504) |
| Function shape | `_func_read` / `_func_write` / `_func_read_write` add a `void read(int)` or `void write(int)` helper that the main function calls instead of the inline assignment; the helpers either write to `a.v` or compare `b.v` to the expected value. | [AliasTest::initPrograms function helpers](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L461-L475) |
| Synchronization | `_barrier` inserts `barrier();` between the write to `a.v` and the read from `b.v`. | [AliasTest::initPrograms barrier line](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L485-L486) |
| Type pair | The same `(write, read)` pair is emitted for many type combinations: `i8/u8`, `i16/u16`, `i32/u32`, `i64/u64`, `f16/u16`, `f32/u32`, `f64/u64`, plus their `vec4_array`/`u8_array`/`u16_array`/`u32_array` byte-reinterpretation variants; each combination flips one or more `useType()` flags and may add `GL_EXT_scalar_block_layout`. | [AddAliasTests case data](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L562-L634) |
| Workgroup-memory size | `size` keeps the same `for (i = 0; i < size; i++)` pattern but varies `size` and the `words` array size; `padding` keeps the same 32-word backing array but varies the `layout(offset = N)` member offsets. | [SizeTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1165-L1209), [PaddingTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1018-L1067) |
| Zero-init interaction | `zero_ext` Amber scripts drop into raw SPIR-V and rely on `OpConstantNull` plus an uninitialized aliased sibling; `block_with_offset` adds an `OpMemberDecorate Offset 64` so only the offset-shifted half of the output must be zero. | [zero_ext_block_with_offset.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block_with_offset.amber) |
| Pipeline construction type | The shader is identical across `pipeline`, `shader_object_spirv`, and `shader_object_binary`; only `copy_memory` and `zero_ext` differ because Amber cannot drive compute pipelines as shader objects. | [createWorkgroupMemoryExplicitLayoutTests guard](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1312-L1321) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 96
; Schema: 0
               OpCapability Shader
               OpCapability WorkgroupMemoryExplicitLayoutKHR
               OpExtension "SPV_KHR_workgroup_memory_explicit_layout"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationIndex %a %b %_
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types"
               OpSourceExtension "GL_EXT_shared_memory_block"
               OpName %main "main"
               OpName %index "index"
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpName %A "A"
               OpMemberName %A 0 "v"
               OpName %a "a"
               OpName %B "B"
               OpMemberName %B 0 "v"
               OpName %b "b"
               OpName %Result "Result"
               OpMemberName %Result 0 "result"
               OpName %_ ""
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %_arr_v4float_uint_3 ArrayStride 16
               OpDecorate %A Block
               OpMemberDecorate %A 0 Offset 0
               OpDecorate %a Aliased
               OpDecorate %_arr_v2float_uint_6 ArrayStride 8
               OpDecorate %B Block
               OpMemberDecorate %B 0 Offset 0
               OpDecorate %b Aliased
               OpDecorate %Result Block
               OpMemberDecorate %Result 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
       %uint = OpTypeInt 32 0
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
     %uint_3 = OpConstant %uint 3
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
          %A = OpTypeStruct %_arr_v4float_uint_3
%_ptr_Workgroup_A = OpTypePointer Workgroup %A
          %a = OpVariable %_ptr_Workgroup_A Workgroup
      %int_0 = OpConstant %int 0
%_arr_v4float_uint_3_0 = OpTypeArray %v4float %uint_3
    %float_1 = OpConstant %float 1
    %float_2 = OpConstant %float 2
         %25 = OpConstantComposite %v4float %float_1 %float_1 %float_2 %float_2
    %float_3 = OpConstant %float 3
    %float_4 = OpConstant %float 4
         %28 = OpConstantComposite %v4float %float_3 %float_3 %float_4 %float_4
    %float_5 = OpConstant %float 5
    %float_6 = OpConstant %float 6
         %31 = OpConstantComposite %v4float %float_5 %float_5 %float_6 %float_6
         %32 = OpConstantComposite %_arr_v4float_uint_3_0 %25 %28 %31
%_ptr_Workgroup__arr_v4float_uint_3 = OpTypePointer Workgroup %_arr_v4float_uint_3
    %v2float = OpTypeVector %float 2
     %uint_6 = OpConstant %uint 6
%_arr_v2float_uint_6 = OpTypeArray %v2float %uint_6
          %B = OpTypeStruct %_arr_v2float_uint_6
%_ptr_Workgroup_B = OpTypePointer Workgroup %B
          %b = OpVariable %_ptr_Workgroup_B Workgroup
%_ptr_Workgroup__arr_v2float_uint_6 = OpTypePointer Workgroup %_arr_v2float_uint_6
%_arr_v2float_uint_6_0 = OpTypeArray %v2float %uint_6
         %46 = OpConstantComposite %v2float %float_1 %float_1
         %47 = OpConstantComposite %v2float %float_2 %float_2
         %48 = OpConstantComposite %v2float %float_3 %float_3
         %49 = OpConstantComposite %v2float %float_4 %float_4
         %50 = OpConstantComposite %v2float %float_5 %float_5
         %51 = OpConstantComposite %v2float %float_6 %float_6
         %52 = OpConstantComposite %_arr_v2float_uint_6_0 %46 %47 %48 %49 %50 %51
       %bool = OpTypeBool
     %v2bool = OpTypeVector %bool 2
     %Result = OpTypeStruct %uint
%_ptr_StorageBuffer_Result = OpTypePointer StorageBuffer %Result
          %_ = OpVariable %_ptr_StorageBuffer_Result StorageBuffer
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %index = OpVariable %_ptr_Function_int Function
         %12 = OpLoad %uint %gl_LocalInvocationIndex
         %13 = OpBitcast %int %12
               OpStore %index %13
         %34 = OpAccessChain %_ptr_Workgroup__arr_v4float_uint_3 %a %int_0
         %35 = OpCopyLogical %_arr_v4float_uint_3 %32
               OpStore %34 %35
         %43 = OpAccessChain %_ptr_Workgroup__arr_v2float_uint_6 %b %int_0
         %44 = OpLoad %_arr_v2float_uint_6 %43
         %54 = OpCompositeExtract %v2float %44 0
         %55 = OpCompositeExtract %v2float %52 0
         %57 = OpFOrdEqual %v2bool %54 %55
         %58 = OpAll %bool %57
         %59 = OpCompositeExtract %v2float %44 1
         %60 = OpCompositeExtract %v2float %52 1
         %61 = OpFOrdEqual %v2bool %59 %60
         %62 = OpAll %bool %61
         %63 = OpLogicalAnd %bool %58 %62
         %64 = OpCompositeExtract %v2float %44 2
         %65 = OpCompositeExtract %v2float %52 2
         %66 = OpFOrdEqual %v2bool %64 %65
         %67 = OpAll %bool %66
         %68 = OpLogicalAnd %bool %63 %67
         %69 = OpCompositeExtract %v2float %44 3
         %70 = OpCompositeExtract %v2float %52 3
         %71 = OpFOrdEqual %v2bool %69 %70
         %72 = OpAll %bool %71
         %73 = OpLogicalAnd %bool %68 %72
         %74 = OpCompositeExtract %v2float %44 4
         %75 = OpCompositeExtract %v2float %52 4
         %76 = OpFOrdEqual %v2bool %74 %75
         %77 = OpAll %bool %76
         %78 = OpLogicalAnd %bool %73 %77
         %79 = OpCompositeExtract %v2float %44 5
         %80 = OpCompositeExtract %v2float %52 5
         %81 = OpFOrdEqual %v2bool %79 %80
         %82 = OpAll %bool %81
         %83 = OpLogicalAnd %bool %78 %82
               OpSelectionMerge %85 None
               OpBranchConditional %83 %84 %85
         %84 = OpLabel
         %89 = OpLoad %int %index
         %90 = OpBitcast %uint %89
         %92 = OpAccessChain %_ptr_StorageBuffer_uint %_ %int_0
               OpStore %92 %90
               OpBranch %85
         %85 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Shared support gate.** `checkSupportWithParams` is the central helper. It requires `VK_KHR_workgroup_memory_explicit_layout`,
  `VK_KHR_spirv_1_4`, and the construction-type-dependent shader-object requirements; then conditionally requires the
  relevant `workgroupMemoryExplicitLayout*` feature bits and the matching `shaderInt8/16/64`, `shaderFloat16`, or
  `shaderFloat64` based on the case data
  ([checkSupportWithParams](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L77-L141)).
- **Per-family support derivation.** Each `*Test::checkSupport` initializes a `CheckSupportParams` from its case data:
  `AliasTest` reads the `Requirements` flags and the layout mask, `ZeroTest` calls `useType()` for the element type and
  the two field types, `PaddingTest` calls `useType()` for every declared type and sets `needsScalar` whenever any
  offset is not a multiple of 4 bytes
  ([AliasTest::checkSupport](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L408-L422),
  [ZeroTest::checkSupport](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L738-L750),
  [PaddingTest::checkSupport](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1004-L1016)).
- **`SizeTest` device limit check.** `SizeTest::checkSupport` requires `VK_KHR_workgroup_memory_explicit_layout`,
  `VK_KHR_spirv_1_4`, and the construction-type shader-object requirements; if `maxComputeSharedMemorySize < m_size`,
  the test throws `NotSupportedError` rather than dispatching
  ([SizeTest::checkSupport](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1153-L1163)).
- **Shared `runCompute`.** All four C++ families route through the same `runCompute` helper: it allocates a
  host-visible storage buffer of `sizeof(uint32_t) * workgroupSize`, pre-fills it with `0xff`, builds a
  `ComputePipelineWrapper` with the requested construction type, records a one-dispatch command buffer, submits and
  waits, invalidates the allocation, and scans the result buffer for the expected value
  ([runCompute](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L143-L219)).
- **Pass/fail rule.** A mismatch in `runCompute` emits a `failure at index <i>: expected <expected>, got <got>` log
  message and returns `tcu::TestStatus::fail("compute failed")`
  ([runCompute result scan](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L207-L218)).
- **Amber wrapper.** `CreateAmberTestCase` builds an `AmberTestCase` against the
  `data/vulkan/amber/compute/workgroup_memory_explicit_layout/` directory and adds the extension requirements; for the
  `zero_ext` family it also requires `VK_KHR_zero_initialize_workgroup_memory`. The helper has a shader-object branch
  that would use a `shader_object_<name>.amber` filename and add `VK_EXT_shader_object`, but the enclosing factory does
  not call these Amber registration functions for shader-object construction types
  ([CreateAmberTestCase](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1231-L1254)).
- **Amber pass/fail rule.** The `copy_memory` scripts compare the output buffer against an `EQ_BUFFER` reference
  buffer with the expected pattern; the `zero_ext` scripts use `EXPECT output_buffer EQ_BUFFER expected_buffer` for the
  zero pattern or `EXPECT output_buffer IDX <off> EQ 0` for the offset-shifted `block_with_offset` variant
  ([copy_memory_basic.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_basic.amber),
  [zero_ext_block.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block.amber),
  [zero_ext_block_with_offset.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block_with_offset.amber)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `alias` | The implementation did not honor the `Aliased` decoration on `OpVariable`, did not honor the `OpMemberDecorate Offset` decorations inside the `Workgroup` blocks, or used a byte order that does not match the expected cross-type reinterpretation. |
| `zero` | The implementation did not let the single invocation fully populate `A` and observe the aliased bytes through `B`, or the shader compiler changed the storage class or explicit layout of `A` or `B`. |
| `padding` | The implementation did not honor a non-default `layout(offset = N)` member offset inside a `Workgroup` block, leaving the wrong word of the 32-word backing array populated. |
| `size` | The implementation silently rejected an aliased workgroup-memory region at or below `maxComputeSharedMemorySize`, failed to alias the eight block views, or returned `NotSupportedError` for a size that the device's limits should have allowed. |
| `copy_memory` | The implementation produced a different byte sequence for `OpCopyMemory` between `Workgroup` and `StorageBuffer`, or the `OpAccessChain`-driven array copy did not populate the expected offset-shifted half. |
| `zero_ext` | The implementation did not zero the explicitly initialized `Workgroup` variable or did not expose its zeroed bytes through an aliased sibling, including the offset-shifted overlap. |

### Cause Analysis

#### Aliased workgroup blocks did not share the same base address

**Possible failure symptoms:** `alias.vec4_array_to_vec2_array_default` (and similar cross-type cases) report
`failure at index 0: expected 0, got 0xffffffff`; the result buffer entry stays at the host pre-fill value because
the shader's `b.v == …` check never succeeds.

**Possible implementation causes:** The implementation must honor `OpDecorate %a Aliased` and `OpDecorate %b Aliased`,
which together with the SPIR-V `WorkgroupMemoryExplicitLayoutKHR` capability require the variables to be allocated
from the same shared-memory allocation. A failure pinpoints either the SPIR-V module builder (the implementation
dropped the `Aliased` decoration through a front-end or back-end pass), the layout pass (the implementation did not
place `a` and `b` at the same offset in that allocation), or the comparison lowering (the `OpCopyLogical` + `OpStore` of the
composite array did not actually write the per-element pattern). Source-level investigation is needed to localize
the cause to the shader compiler, the workgroup-memory allocator, or the barrier-free store/load ordering inside a
single invocation.

#### Cross-type reinterpretation used the wrong byte order or layout

**Possible failure symptoms:** The shader compiles and runs but `b.v` does not match the expected pattern; the failure
log points to the read side, not the write side.

**Possible implementation causes:** The default `Block` layout (and `std140`/`std430`) computes the offset of every
block member from its own `OpMemberDecorate Offset` chain; the `vec2[6]` reader needs offsets `0, 8, 16, 24, 32, 40`,
which line up with the writer's `vec4[3]` offsets `0, 16, 32` only when the `vec4` slot is split into two `vec2`s.
A mismatch implies the implementation used the array-stride math from one block on the other, or it scaled the
`vec2` offsets to match the `vec4` strides. Source-level investigation is needed to determine whether the failure is
specific to one qualifier (`std140` vs `default`).

#### Required feature bit or numeric-width feature is missing

**Possible failure symptoms:** A case throws `NotSupportedError` with messages such as
`workgroupMemoryExplicitLayoutScalarBlockLayout not supported`, `shaderInt8 not supported`, or
`shaderFloat64 not supported` rather than reporting `compute failed`.

**Possible implementation causes:** `checkSupportWithParams` queries the device through
`VkPhysicalDeviceFeatures2` with a chained `VkPhysicalDeviceShaderFloat16Int8Features` and a chained
`VkPhysicalDeviceWorkgroupMemoryExplicitLayoutFeaturesKHR`. A `NotSupportedError` outcome is intended when the device
does not report the feature; a `compute failed` outcome for a case that should have been `NotSupportedError` points to
a failed feature query
([checkSupportWithParams](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L100-L140)).

#### Workgroup-memory size exceeded the device limit

**Possible failure symptoms:** `size.<bytes>` cases with a `bytes` value larger than
`maxComputeSharedMemorySize` log `NotSupportedError: Not enough shared memory supported.` instead of a
`compute failed` result.

**Possible implementation causes:** `SizeTest::checkSupport` reads
`context.getDeviceProperties().limits.maxComputeSharedMemorySize` and throws before the pipeline is built. A correct
`NotSupportedError` outcome is intended; a `compute failed` outcome for a size that should have been pruned implies the
host did not honor the device's limit
([SizeTest::checkSupport](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1153-L1163)).

#### Amber `OpCopyMemory` produced the wrong bytes

**Possible failure symptoms:** `copy_memory.basic`, `copy_memory.two_invocations`, or `copy_memory.variable_pointers`
fail with `EXPECT output_buffer EQ_BUFFER expected_buffer` mismatches.

**Possible implementation causes:** The Amber scripts rely on a partial-block copy through `OpAccessChain` when the
whole-block types do not match
([copy_memory_basic.amber partial copy](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_basic.amber#L88-L100));
a mismatch implies the implementation did not honor `OpAccessChain` on the `Workgroup` side, did not honor the
`Offset` decorations on the inner block members, or returned the source block's contents from an
uninitialized-but-aliased neighbor. `two_invocations` adds an `OpControlBarrier Workgroup Workgroup 0`; a mismatch
specifically at the boundary between the two push-constant-selected invocations could point to a barrier-handling
bug.

#### Amber `zero_ext` case left a non-zero residual in the aliased region

**Possible failure symptoms:** `zero_ext.block` and `zero_ext.other_block` fail with
`EXPECT output_buffer EQ_BUFFER expected_buffer` mismatches; `zero_ext.block_with_offset` fails with
`EXPECT output_buffer IDX <off> EQ 0` mismatches on the offset-shifted half.

**Possible implementation causes:** The implementation must combine `VK_KHR_workgroup_memory_explicit_layout` with
`VK_KHR_zero_initialize_workgroup_memory`. In `block_with_offset`, the SPIR-V `OpConstantNull` initializer is on
`offset_wg`, whose block member carries `Offset 64`; the shader copies the uninitialized offset-zero sibling `%wg`
([zero_ext_block_with_offset.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block_with_offset.amber)).
A failure in bytes 64 through 127 points to a missing zero initialization of `%offset_wg`, failure to honor its
`Offset 64`, or failure to expose the initialized overlapping bytes through `%wg`. There is no preceding workgroup
write or barrier in this script; only one selected invocation copies `%wg` to the output buffer.

## Case Pruning

### Requirement-based pruning

- Every C++ test family requires `VK_KHR_workgroup_memory_explicit_layout` and `VK_KHR_spirv_1_4`
  ([checkSupportWithParams](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L79-L80),
  [SizeTest::checkSupport](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1155-L1156)).
- `alias`, `zero`, and `padding` cases gate on `workgroupMemoryExplicitLayoutScalarBlockLayout`,
  `workgroupMemoryExplicitLayout8BitAccess`, `workgroupMemoryExplicitLayout16BitAccess`, `shaderInt8`, `shaderInt16`,
  `shaderInt64`, `shaderFloat16`, and `shaderFloat64` as required by the case data
  ([checkSupportWithParams](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L100-L140)).
- `size.<bytes>` cases with `bytes > maxComputeSharedMemorySize` are pruned with `NotSupportedError`
  ([SizeTest::checkSupport](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1158-L1159)).
- `copy_memory.variable_pointers` adds `VariablePointerFeatures.variablePointers` and `VK_EXT_descriptor_indexing`
  requirements
  ([AddCopyMemoryTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1266-L1268)).
- The `zero_ext` Amber cases require `VK_KHR_zero_initialize_workgroup_memory`
  ([CreateAmberTestCase zero-init flag](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1245-L1248)).
- `CreateAmberTestCase` contains support for shader-object-prefixed scripts and a `VK_EXT_shader_object` requirement,
  but this branch is unreachable for this family because registration omits both Amber groups for shader objects
  ([CreateAmberTestCase shader-object branch](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1249-L1252)).
- `copy_memory` and `zero_ext` are not registered under the `shader_object_spirv` and `shader_object_binary` roots at
  all, because Amber cannot drive compute pipelines as shader objects
  ([createWorkgroupMemoryExplicitLayoutTests guard](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1312-L1321)).

### Design-based pruning

- The C++ cases are gated behind `#ifndef CTS_USES_VULKANSC` at the dispatcher level, so the entire family is absent
  from a VulkanSC build
  ([vktComputeTests.cpp#L61-L63](../../../modules/vulkan/compute/vktComputeTests.cpp#L61-L63)).
- `AliasTest` only emits the layout qualifier if its bit is set in the case's `LayoutFlags` mask; the loop at
  `AddAliasTests` skips the inner block when `(c.layout & layout) == 0`
  ([AddAliasTests loop](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L659-L660)).
- The `alias` case data intentionally combines each type pair with both `_to_<b>` and `<b>_to_<a>` via the
  `CASE_WITH_REVERSE` macro, so every cross-type pair is exercised in both write-read orders
  ([AddAliasTests case data](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L562-L572)).
- `ZeroTest` deliberately restricts the element type to `uint`, `uvec4`, `uint8_t`, `uvec4_8bit`, and `uint16_t`, and
  the field types to a small subset that includes floating types; `float16_t` is rejected by `useType()` so the
  generator never sees it as an element type
  ([isTestedZeroElementType / isTestedFieldType](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L835-L875),
  [ZeroTest::checkSupport assertion](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L743)).
- `PaddingTest` uses two different element types (`uint` for aligned offsets, `uint8_t` for arbitrary offsets); the
  arbitrary-offset set is the one that flips `needsScalar` and requires the `ScalarBlockLayout` feature
  ([AddPaddingTests loops](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1069-L1108)).
- `size` deliberately lists fixed sizes rather than reading `maxComputeSharedMemorySize` dynamically because CTS does
  not allow dynamic shader generation from device properties
  ([AddSizeTests comment](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1218-L1220)).

## Key Takeaways

- The explicit-layout contract has two load-bearing pieces: the SPIR-V `Aliased` decoration on `OpVariable` lets two
  `Workgroup` blocks share memory, and the `OpMemberDecorate Offset` chain inside a `Workgroup` block pins the byte
  layout of every block member.
- The four C++ families each exercise a different aspect of the same contract (`alias` for cross-type reinterpretation,
  `zero` for manual zeroing observed through an aliased block, `padding` for explicit offset honoring, `size` for a large
  workgroup-memory allocation), and the two Amber families reuse the contract to test `OpCopyMemory` and the
  zero-initialize interaction.
- `alias.vec4_array_to_vec2_array_default` is the simplest representative because it uses standard `vec4`/`vec2` types
  and the default layout qualifier, so the only contract being exercised is the `Aliased` reinterpretation.
- The expected behavior of every C++ family is "the shader writes the expected pattern, the host scans for the
  expected value"; any mismatch logs `failure at index <i>: expected <expected>, got <got>`.
- The `copy_memory` and `zero_ext` Amber families only run under the default `pipeline` construction type because
  Amber cannot drive compute pipelines as shader objects.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test category factory declaration | [vktComputeWorkgroupMemoryExplicitLayoutTests.hpp#L38-L39](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.hpp#L38-L39) | Declares `createWorkgroupMemoryExplicitLayoutTests`. |
| Family factory | [createWorkgroupMemoryExplicitLayoutTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1289-L1324) | Mounts `alias`, `zero`, `padding`, `size`, and conditionally `copy_memory` and `zero_ext`. |
| Category dispatcher | [vktComputeTests.cpp#L48-L64](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L64), [vktComputeTests.cpp#L68-L85](../../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85) | Mounts the factory under `pipeline`, `shader_object_spirv`, and `shader_object_binary`. |
| Central support helper | [checkSupportWithParams](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L77-L141) | Centralizes `workgroupMemoryExplicitLayout*`, `shaderInt8/16/64`, `shaderFloat16`, and `shaderFloat64` checks. |
| Shared runtime helper | [runCompute](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L143-L219) | Records the result buffer, descriptor, command buffer, dispatch, and host scan; reused by every C++ family. |
| `alias` shader | [AliasTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L424-L505) | Generates the per-case two-block shader with the matching `layout(...)` qualifier. |
| `alias` registration | [AddAliasTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L536-L671) | Builds the cross-product of layout qualifier, function shape, and synchronization. |
| `zero` shader | [ZeroTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L783-L833) | Manually populates `A` with non-zero then zero values, then expects `B` to read zero. |
| `zero` registration | [AddZeroTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L877-L915) | Builds the element-type × field-type × element-count matrix. |
| `padding` shader | [PaddingTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1018-L1067) | Compares 32 backing words against a per-case expected array. |
| `padding` registration | [AddPaddingTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1069-L1108) | Builds the 32-bit-uint and 8-bit-uint offset-pair cases. |
| `size` shader | [SizeTest::initPrograms](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1165-L1209) | Generates the eight workgroup-memory blocks each holding `size/4` words, written in a striped pattern. |
| `size` registration | [AddSizeTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1211-L1229) | Builds the seven fixed-byte-size test cases. |
| Amber wrapper | [CreateAmberTestCase](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1231-L1254) | Loads the Amber script and adds `VK_KHR_workgroup_memory_explicit_layout`, `VK_KHR_spirv_1_4`, optional `VK_KHR_zero_initialize_workgroup_memory`, and optional `VK_EXT_shader_object` requirements. |
| `copy_memory` registration | [AddCopyMemoryTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1256-L1269) | Loads `copy_memory_basic.amber`, `copy_memory_two_invocations.amber`, and `copy_memory_variable_pointers.amber`. |
| `zero_ext` registration | [AddZeroInitializeExtensionTests](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1271-L1285) | Loads `zero_ext_block.amber`, `zero_ext_other_block.amber`, and `zero_ext_block_with_offset.amber`. |
| Vulkan SC and shader-object guards | [vktComputeTests.cpp#L61-L63](../../../modules/vulkan/compute/vktComputeTests.cpp#L61-L63), [createWorkgroupMemoryExplicitLayoutTests guard](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1312-L1321) | Hide the family under `CTS_USES_VULKANSC` and hide `copy_memory` and `zero_ext` under shader-object construction types. |
| Amber scripts | [copy_memory_basic.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_basic.amber), [copy_memory_two_invocations.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_two_invocations.amber), [copy_memory_variable_pointers.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_variable_pointers.amber), [zero_ext_block.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block.amber), [zero_ext_other_block.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_other_block.amber), [zero_ext_block_with_offset.amber](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block_with_offset.amber) | Provide the `copy_memory` and `zero_ext` Amber scripts. |