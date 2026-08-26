## Overview

**Core question:** When `VK_KHR_zero_initialize_workgroup_memory` is enabled, does every workgroup-memory variable start at zero
before any user code runs, regardless of its scalar, vector, matrix, or composite type, the workgroup dimensions, the workgroup
size, or whether the same pipeline is dispatched repeatedly?

- [vktComputeZeroInitializeWorkgroupMemoryTests.cpp](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1382-L1424)
  implements the `zero_initialize_workgroup_memory` test family under `dEQP-VK.compute.pipeline.zero_initialize_workgroup_memory`.
- The page also files the registered `max_workgroup_memory`, `types`, `composites`, `max_workgroups`, `specialize_workgroup`,
  `repeat_pipeline`, and `shared_memory_blocks` test families under the same root.
- Variants are parameter dimensions rather than distinct mechanisms: the family modulates **what shape of workgroup memory is
  declared**, **how the workgroup is sized**, **how the pipeline is reused**, and **how the test is driven (GLSL versus Amber)**.
- The C++ families use several result-recording strategies: `max_workgroup_memory` and `max_workgroups` atomically count zero
  observations, while `types`, `composites`, `specialize_workgroup`, and `repeat_pipeline` write observed values or Boolean
  mismatch indicators directly. The host compares every result entry with the family-specific expected value.

## Background Knowledge

- **Workgroup memory.** Variables declared with GLSL `shared` (or `Workgroup` in SPIR-V) are storage shared by every invocation in
  a workgroup; their lifetime is the workgroup dispatch. Ordinary GLSL `shared` variables are not initialized by the language, so
  their contents at shader start depend on the implementation.
- **Workgroup memory zero-initialization.** `VK_KHR_zero_initialize_workgroup_memory` (promoted to Vulkan 1.3 as the
  `shaderZeroInitializeWorkgroupMemory` feature) requires that **every** `Workgroup` storage-class variable with an initializer is
  initialized to zero before any user code in the shader executes. The rule covers scalars, vectors, matrices, arrays, and
  nested composite members.
- **`GL_EXT_null_initializer` and the `= {}` form.** The Vulkan GLSL translator reads `= {}` together with
  `GL_EXT_null_initializer` as a Vulkan-only spelling that maps to a SPIR-V `OpVariable` with an `OpConstantNull` initializer,
  which is the only spelling that drives the zero-initialization guarantee in the generated SPIR-V.
- **Result buffer as a fail/passed counter.** An `atomicAdd` of `1` for a zero-observed slot and `0` for a non-zero slot lets a
  test pack many independent invocations into the same buffer and let the host check the result with a single linear scan.
- **Specialization constants for workgroup size.** Using `layout(local_size_x_id = N, ...)` and `layout(constant_id = N) const`
  lets the host choose the workgroup size at pipeline-creation time without recompiling the shader, which makes the same
  compiled SPIR-V exercise every workgroup-size variant the test requests.

## Registration Hierarchy

```text
compute.pipeline.zero_initialize_workgroup_memory
├── max_workgroup_memory
├── types
├── composites
├── max_workgroups
├── specialize_workgroup
├── repeat_pipeline
└── shared_memory_blocks (pipeline only, non-VulkanSC only)
```

The `shared_memory_blocks` child is omitted under shader-object construction types because Amber cannot drive compute pipelines
as shader objects ([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1413-L1420](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1413-L1420)).

## Parameter Dimensions and Observed Values

The page is a generated-matrix page. The dimensions below keep the registered values but add why each dimension matters for
this test.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Workgroup count | `1`, `2`, `4`, `16`, `64`, `128` | `max_workgroup_memory` runs the same shader multiple workgroups at a time to exercise workgroup memory at scale. | [AddMaxWorkgroupMemoryTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L268-L278) |
| Workgroup dimension | `x`, `y`, `z` | `max_workgroups` stresses the per-axis `maxComputeWorkGroupSize` limit together with `maxComputeWorkGroupInvocations`; the active dimension is fixed to 65535 workgroups. | [AddMaxWorkgroupsTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L995-L1001) |
| Workgroup size | `x: 1..8`, `y: 1..8`, `z: 1..8` (512 combinations) | `specialize_workgroup` feeds the workgroup size through `local_size_x_id`/…`z_id` and the matching specialization constants; sizes that exceed `maxComputeWorkGroupInvocations` are pruned. | [AddSpecializeWorkgroupTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1092-L1107), [limit check](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1057-L1061) |
| Type family | `bool`, `bvec2..4`, `uint32_t`, `uvec2..4`, `int32_t`, `ivec2..4`, `uint8_t`/`int8_t`, `u8vec2..4`/`i8vec2..4`, `uint16_t`/`int16_t`, `u16vec2..4`/`i16vec2..4`, `uint64_t`/`int64_t`, `u64vec2..4`/`i64vec2..4`, `float32_t`, `f32vec2..4`, `f32mat2x2..4x4`, `float16_t`, `f16vec2..4`, `f16mat2x2..4x4`, `float64_t`, `f64vec2..4`, `f64mat2x2..4x4` | Each `types` case declares the named scalar/vector/matrix variable with `shared … = {}` and a randomized 1..16 variable count; the loop in `main()` compares each element to zero with the matching conversion. | [type list](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L446-L474), [support gates](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L329-L389) |
| Composite feature flags | `0x0`, `0x1`, `0x2`, `0x4`, `0x8`, `0x10`, `0x1f` (encoded in `CompositeCaseDef::index`) | The `composites` definitions differ by which explicit-type feature they need; per-case support throws `NotSupportedError` when the corresponding feature is absent. | [composite features](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L552-L568) |
| Composite shape | 11 hand-written `CompositeCaseDef` entries using `uint[…]= {}`, multi-dim arrays, structs, nested struct arrays, and a 5-level struct array | Each entry is a single generated test case; the bit-flag index selects which explicit-type features must be present. | [composite cases](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L602-L866) |
| Intended repeat parameters | Names encode repeat count `2`, `4`, `8`, or `16`, `xSize ∈ {4, 16, 32, 64}`, and writer row `odd ∈ {0, 1}` | The registration call currently passes `odd` into the constructor's `repeat` parameter and `repeat` into its `odd` parameter. Consequently even-named cases execute zero submissions and odd-named cases one submission; no invocation writes because runtime `m_odd` is 2, 4, 8, or 16. | [constructor](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1112-L1117), [registration](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1335-L1358) |
| Amber workgroup shapes | `workgroup_size_128`, `workgroup_size_8x8x2`, `workgroup_size_8x2x8`, `workgroup_size_2x8x8`, `workgroup_size_8x4x4`, `workgroup_size_4x8x4`, `workgroup_size_4x4x8` | `shared_memory_blocks` runs an Amber synchronization pattern for each workgroup layout. Invocation 0 overwrites the scalar before the barrier, so these scripts check propagation of `1`, not the initial zero value. | [AddSharedMemoryTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1360-L1377) |

## Behavior Parameters

The primary behavioral axis is the **test family** under `zero_initialize_workgroup_memory`. Each family picks a different
parameter dimension to stress while the same core mechanism (workgroup memory must read zero at shader start) is being tested.

### max_workgroup_memory — Largest possible workgroup memory is zero-initialized

`max_workgroup_memory` declares a `shared uvec4 wg_mem[num_elems]` whose size equals the device's `maxComputeSharedMemorySize`,
where `num_elems = maxComputeSharedMemorySize / 16` ([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L211-L241](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L211-L241)).
The host derives dimensions from the per-axis limits, using multiples of 13 for additional dimensions and a target capped at
247 invocations. Each invocation walks every `uvec4` slot but records only its own flat-index slot; invocation 0 also records
slots beyond the workgroup size. A recorded slot adds `1` when `wg_mem[i][j] == 0` and
`0` otherwise; slots beyond the local workgroup size are recorded by the invocation whose flat local index is zero. The host expects every entry
to equal the dispatched workgroup count `numWGX * numWGY * numWGZ`: each workgroup contributes one zero observation per slot.
The buffer is initialized to zero before dispatch so the atomic counts start at zero
([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L62-L162](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L62-L162)).

### types — Scalar/vector/matrix shape does not change the zero-init promise

`types` declares one to sixteen `shared <typeName> wg_mem<k> = {};` variables of a single scalar, vector, or matrix type and has
every invocation compare each element to zero. The mapping from `wg_mem` to a uint result buffer slot uses `numElements` for
scalars/vectors, `numRows` for matrices, and `numVariables` for the variable index. The test exports a result buffer where
`0` means the element was zero and `1` means it was not. The host then confirms every entry is `0`
([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L391-L474](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L391-L474)).

### composites — Nested arrays and structs stay zero-initialized

`composites` writes 11 hand-crafted `CompositeCaseDef` entries that combine `= {}` zero-initialization with one- and
two-dimensional arrays, structs, nested struct arrays, and a 5-level struct array. Each entry also encodes a feature bit mask
in `m_caseDef.index` that the support check maps to `shaderFloat16`, `shaderFloat64`, `shaderInt8`, `shaderInt16`, and
`shaderInt64`. The host runs each case with shape-specific spec values such as `{16}`, `{4, 8}`, `{2, 3, 4}`, `{6, 5, 4, 3, 2}`,
or none ([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L476-L873](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L476-L873)).

### max_workgroups — One axis pushed to the maximum dispatch count

`max_workgroups` declares a `shared uint wg_mem[2] = {};`. The invocation with local x ID zero atomically exchanges the two
slots before a `barrier()`. The active dispatch axis is forced to `65535` workgroups while the other two axes stay at `1`.
After the barrier, each invocation checks the slot selected by `gl_LocalInvocationID.x % 2` and atomically adds `1` or `0` to
its flat-local-index result entry
([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L875-L1001](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L875-L1001)).

### specialize_workgroup — Workgroup size picked at pipeline creation

`specialize_workgroup` declares a `shared uint wg_mem[WGX][WGY][WGZ] = {};` and threads the workgroup size through
`layout(local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2)` together with `layout(constant_id = 0..2) const`. The
host supplies `{WGX, WGY, WGZ}` as specialization data and discards sizes that exceed `maxComputeWorkGroupInvocations`. Each
invocation copies its own workgroup-memory slot into the matching result buffer entry
([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1003-L1107](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1003-L1107)).

### repeat_pipeline — Zero-initialization holds across repeated dispatches

`repeat_pipeline` declares a `shared uint wg_mem[WGX][2] = {};`; its shader is designed to let the y-row selected by `m_odd`
write from a host source buffer, synchronize, and then have both rows copy shared memory to the result buffer. The runtime is
designed to submit the same command buffer `m_repeat` times and refill the result buffer with `0xff` between submissions.
However, registration calls the constructor as `(x, odd, repeat)` although its parameters are `(xSize, repeat, odd)`. Therefore
the registered even cases submit zero times, odd cases submit once, and `m_odd` is always 2, 4, 8, or 16, so the write branch
never executes. As implemented, this family does not exercise repeated dispatches or the intended alternating source pattern
([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1109-L1358](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1109-L1358)).

### shared_memory_blocks — Amber-covered workgroup shapes

`shared_memory_blocks` adds non-VulkanSC, non-shader-object Amber cases that pick a different workgroup shape per case file.
Each Amber script writes `1` from `gl_LocalInvocationIndex == 0`, executes `barrier()`, then writes the observed `wg_mem` value
into a result buffer. The expected buffer is `1` and the result buffer is initialized to `99`. Because the shared scalar is
overwritten before it is observed, these scripts validate visibility of the write after the barrier, not zero-initialization ([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1360-L1377](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1360-L1377);
[Amber workgroup_size_128.amber](../../../data/vulkan/amber/compute/zero_initialize_workgroup_memory/workgroup_size_128.amber)).

## Shader Analysis

Each test family emits its own compute shader. The page uses one walkthrough for the `max_workgroup_memory` family because that
shader carries the highest signal of the zero-initialization contract: it forces a `shared` array of `maxComputeSharedMemorySize`
bytes and asks every invocation to confirm every slot is zero. The remaining families are summarized under
`Parameter Variation Summary` because they only change the parameter dimension.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.compute.pipeline.zero_initialize_workgroup_memory.max_workgroup_memory.1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `max_workgroup_memory` | Selects the largest-workgroup-memory branch that declares `shared uvec4 wg_mem[num_elems]` with `num_elems = maxComputeSharedMemorySize / 16`. |
| `.1` | `numWGX = 1`, `numWGY = 1`, `numWGZ = 1`; the host also supplies the workgroup size (`WGX`, `WGY`, `WGZ`) and `numElems` as specialization constants. |
| `numWGX * numWGY * numWGZ` expected value | When `increment = 1` the host expects every result buffer entry to equal this product: each dispatched workgroup contributes exactly one observation for each slot (its matching invocation, or invocation 0 for slots beyond the workgroup size). |
| `GL_EXT_null_initializer` + `= {}` | Drives the generated SPIR-V to declare `wg_mem` with an `OpConstantNull` initializer, which is the only spelling that produces the zero-initialization guarantee. |
| `local_size_x_id = 0, …` | The host supplies the workgroup size through specialization constants rather than baking it into the shader source. |

#### Purpose

This shader verifies that a `shared` array whose declared size equals the device's `maxComputeSharedMemorySize` is fully
zero-initialized at shader start, then atomically records any non-zero slot into the host-visible result buffer.

#### Structural Design

| Step | Invocation A | Running index in result buffer | What is checked |
|------|--------------|---------------------------------|-----------------|
| 1 | Compute `idx_z`, `idx_y`, `idx_x`, and the flat `idx` from `gl_LocalInvocationID` and the workgroup size. | n/a | Establishes the per-invocation slot identity used as the result buffer index. |
| 2 | For each `uvec4 wg_mem[i]`, walk `j = 0..3` and read `wg_val = wg_mem[i][j]`. | n/a | Reads every workgroup-memory slot the family declared. |
| 3 | If `idx == shared_idx`, atomically add `1` to `a.a[idx]` when `wg_val == 0`, otherwise add `0`. | Slot owned by this invocation | Confirms zero for the slots the invocation owns. |
| 4 | If `idx == 0` and `shared_idx >= wg_size`, atomically add `1` to `a.a[shared_idx]` when `wg_val == 0`, otherwise add `0`. | Unowned slots, only the lane 0 invocation | Confirms zero for the slots no real invocation owns. |
| 5 | The host scans the result buffer and expects every entry to equal `numWGX * numWGY * numWGZ` (the workgroup count). | All slots | A single mismatching entry fails the test. |

#### Shader Code

Reconstructed GLSL for this path:

```glsl
#version 450
#extension GL_EXT_null_initializer : enable
/// Workgroup size is supplied at pipeline-creation time through specialization constants 0..2.
layout(local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2) in;
/// Storage buffer that receives one atomic counter per workgroup-memory slot. The host initializes it to zero.
layout(set = 0, binding = 0) buffer A { uint a[]; } a;
/// `num_elems` is the number of `uvec4` slots that fill the device's maxComputeSharedMemorySize; the host
/// overrides it via SpecId 3 (= 16384 / 16 by default).
layout(constant_id = 3) const uint num_elems = 16384 / 16;
/// `num_wgs` is reserved by the source but not referenced by the shader body.
layout(constant_id = 4) const uint num_wgs = 0;
/// `= {}` together with GL_EXT_null_initializer is the only spelling that drives the zero-initialization
/// contract for the workgroup-memory variable in the generated SPIR-V.
shared uvec4 wg_mem[num_elems] = {};
void main() {
  /// Flatten the local invocation ID into a single index so result buffer slots line up with workgroup-memory slots.
  uint idx_z = gl_LocalInvocationID.z * gl_WorkGroupSize.x * gl_WorkGroupSize.y;
  uint idx_y = gl_LocalInvocationID.y * gl_WorkGroupSize.x;
  uint idx_x = gl_LocalInvocationID.x;
  uint idx = idx_x + idx_y + idx_z;
  uint wg_size = gl_WorkGroupSize.x * gl_WorkGroupSize.y * gl_WorkGroupSize.z;
  for (uint i = 0; i < num_elems; ++i) {
    for (uint j = 0; j < 4; ++j) {
      uint shared_idx = 4*i + j;
      uint wg_val = wg_mem[i][j];
      /// The invocation that owns the slot writes 1 (zero seen) or 0 (non-zero seen) into its result buffer slot.
      if (idx == shared_idx) {
        atomicAdd(a.a[idx], wg_val == 0 ? 1 : 0);
      /// Lane 0 records the remaining slots so the host can verify zero even for unobserved workgroup-memory slots.
      } else if (idx == 0 && shared_idx >= wg_size) {
        atomicAdd(a.a[shared_idx], wg_val == 0 ? 1 : 0);
      }
    }
  }
}
```

#### Additional Info

- The host reads `properties.limits.maxComputeSharedMemorySize` and `properties.limits.maxComputeWorkGroupInvocations` to pick
  the workgroup dimensions and the `num_elems` specialization value
  ([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L243-L266](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L243-L266)).
  The shader shown here uses the source's default `num_elems = 16384 / 16`; the real run uses the device's value. The host initializes the result buffer to zero and dispatches the case's requested number of workgroups; the per-slot check
  (`0` for a non-zero value, `1` for zero) combined with `atomicAdd` guarantees that any non-zero workgroup-memory slot leaves the result
  buffer entry strictly below the expected workgroup count
  ([vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L82-L158](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L82-L158)).
- The Amber scripts instead overwrite the scalar with 1 before the barrier and compare every output with a reference value of
  1. Their pre-filled 99 detects missing output writes, but the scripts do not observe the scalar's initial value
  ([workgroup_size_128.amber](../../../data/vulkan/amber/compute/zero_initialize_workgroup_memory/workgroup_size_128.amber)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Workgroup dimensions (`local_size_x_id, …`) | The same `local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2` declaration form is used for `max_workgroup_memory`, `max_workgroups`, and `specialize_workgroup`; the host overrides the specialization constants per case. | [MaxWorkgroupMemoryTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L211-L241), [MaxWorkgroupsTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L929-L965), [SpecializeWorkgroupTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1064-L1084) |
| Type family | `types` swaps the single `shared uvec4 wg_mem[…]` for `shared <typeName> wg_mem<k> = {};` variables and converts each element to zero before the result buffer write. | [TypeTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L391-L434) |
| Composite shape | `composites` substitutes the per-case `typeDefinition` (one- or two-dim arrays, structs, nested struct arrays, 5-level struct array) and reads via the per-case `assignment` block; spec constants drive array sizes when needed. | [CompositeTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L570-L592), [CompositeCaseDef entries](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L602-L866) |
| Repeat count | The shader and runtime support one writing y-row and `m_repeat` submissions, but the swapped registration arguments reduce the actual cases to zero or one submission with no writing row. | [RepeatedPipelineTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1161-L1185), [registration](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1335-L1358) |
| Workgroup size | `specialize_workgroup` keeps the same `local_size_x_id` form but reads `wg_mem` directly into the result buffer without an "unowned slot" branch. | [SpecializeWorkgroupTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1064-L1084) |
| Driver | `shared_memory_blocks` is a separate Amber script per workgroup shape; the script is auto-loaded by the `AddSharedMemoryTests` helper. | [AddSharedMemoryTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1360-L1377), [workgroup_size_8x8x2.amber](../../../data/vulkan/amber/compute/zero_initialize_workgroup_memory/workgroup_size_8x8x2.amber) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.3`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 122
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_null_initializer"
               OpName %main "main"
               OpName %idx_z "idx_z"
               OpName %gl_LocalInvocationID "gl_LocalInvocationID"
               OpName %idx_y "idx_y"
               OpName %idx_x "idx_x"
               OpName %idx "idx"
               OpName %wg_size "wg_size"
               OpName %i "i"
               OpName %num_elems "num_elems"
               OpName %j "j"
               OpName %shared_idx "shared_idx"
               OpName %wg_val "wg_val"
               OpName %wg_mem "wg_mem"
               OpName %A "A"
               OpMemberName %A 0 "a"
               OpName %a "a"
               OpName %num_wgs "num_wgs"
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %16 SpecId 0
               OpDecorate %17 SpecId 1
               OpDecorate %18 SpecId 2
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %num_elems SpecId 3
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %A Block
               OpMemberDecorate %A 0 Offset 0
               OpDecorate %a Binding 0
               OpDecorate %a DescriptorSet 0
               OpDecorate %num_wgs SpecId 4
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%_ptr_Input_uint = OpTypePointer Input %uint
         %16 = OpSpecConstant %uint 1
         %17 = OpSpecConstant %uint 1
         %18 = OpSpecConstant %uint 1
%gl_WorkGroupSize = OpSpecConstantComposite %v3uint %16 %17 %18
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
         %41 = OpSpecConstantOp %uint CompositeExtract %gl_WorkGroupSize 0
         %42 = OpSpecConstantOp %uint CompositeExtract %gl_WorkGroupSize 1
         %43 = OpSpecConstantOp %uint IMul %41 %42
         %44 = OpSpecConstantOp %uint CompositeExtract %gl_WorkGroupSize 2
         %45 = OpSpecConstantOp %uint IMul %43 %44
  %num_elems = OpSpecConstant %uint 1024
       %bool = OpTypeBool
     %uint_4 = OpConstant %uint 4
     %v4uint = OpTypeVector %uint 4
%_arr_v4uint_num_elems = OpTypeArray %v4uint %num_elems
         %73 = OpConstantNull %_arr_v4uint_num_elems
%_ptr_Workgroup__arr_v4uint_num_elems = OpTypePointer Workgroup %_arr_v4uint_num_elems
     %wg_mem = OpVariable %_ptr_Workgroup__arr_v4uint_num_elems Workgroup %73
%_ptr_Workgroup_uint = OpTypePointer Workgroup %uint
%_runtimearr_uint = OpTypeRuntimeArray %uint
          %A = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_A = OpTypePointer StorageBuffer %A
          %a = OpVariable %_ptr_StorageBuffer_A StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
      %int_1 = OpConstant %int 1
    %num_wgs = OpSpecConstant %uint 1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %idx_z = OpVariable %_ptr_Function_uint Function
      %idx_y = OpVariable %_ptr_Function_uint Function
      %idx_x = OpVariable %_ptr_Function_uint Function
        %idx = OpVariable %_ptr_Function_uint Function
    %wg_size = OpVariable %_ptr_Function_uint Function
          %i = OpVariable %_ptr_Function_uint Function
          %j = OpVariable %_ptr_Function_uint Function
 %shared_idx = OpVariable %_ptr_Function_uint Function
     %wg_val = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_2
         %15 = OpLoad %uint %14
         %21 = OpCompositeExtract %uint %gl_WorkGroupSize 0
         %22 = OpIMul %uint %15 %21
         %24 = OpCompositeExtract %uint %gl_WorkGroupSize 1
         %25 = OpIMul %uint %22 %24
               OpStore %idx_z %25
         %27 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_1
         %28 = OpLoad %uint %27
         %29 = OpCompositeExtract %uint %gl_WorkGroupSize 0
         %30 = OpIMul %uint %28 %29
               OpStore %idx_y %30
         %32 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %33 = OpLoad %uint %32
               OpStore %idx_x %33
         %35 = OpLoad %uint %idx_x
         %36 = OpLoad %uint %idx_y
         %37 = OpIAdd %uint %35 %36
         %38 = OpLoad %uint %idx_z
         %39 = OpIAdd %uint %37 %38
               OpStore %idx %39
               OpStore %wg_size %45
               OpStore %i %uint_0
               OpBranch %47
         %47 = OpLabel
               OpLoopMerge %49 %50 None
               OpBranch %51
         %51 = OpLabel
         %52 = OpLoad %uint %i
         %55 = OpULessThan %bool %52 %num_elems
               OpBranchConditional %55 %48 %49
         %48 = OpLabel
               OpStore %j %uint_0
               OpBranch %57
         %57 = OpLabel
               OpLoopMerge %59 %60 None
               OpBranch %61
         %61 = OpLabel
         %62 = OpLoad %uint %j
         %64 = OpULessThan %bool %62 %uint_4
               OpBranchConditional %64 %58 %59
         %58 = OpLabel
         %66 = OpLoad %uint %i
         %67 = OpIMul %uint %uint_4 %66
         %68 = OpLoad %uint %j
         %69 = OpIAdd %uint %67 %68
               OpStore %shared_idx %69
         %76 = OpLoad %uint %i
         %77 = OpLoad %uint %j
         %79 = OpAccessChain %_ptr_Workgroup_uint %wg_mem %76 %77
         %80 = OpLoad %uint %79
               OpStore %wg_val %80
         %81 = OpLoad %uint %idx
         %82 = OpLoad %uint %shared_idx
         %83 = OpIEqual %bool %81 %82
               OpSelectionMerge %85 None
               OpBranchConditional %83 %84 %101
         %84 = OpLabel
         %92 = OpLoad %uint %idx
         %94 = OpAccessChain %_ptr_StorageBuffer_uint %a %int_0 %92
         %95 = OpLoad %uint %wg_val
         %96 = OpIEqual %bool %95 %uint_0
         %98 = OpSelect %int %96 %int_1 %int_0
         %99 = OpBitcast %uint %98
        %100 = OpAtomicIAdd %uint %94 %uint_1 %uint_0 %99
               OpBranch %85
        %101 = OpLabel
        %102 = OpLoad %uint %idx
        %103 = OpIEqual %bool %102 %uint_0
        %104 = OpLoad %uint %shared_idx
        %105 = OpLoad %uint %wg_size
        %106 = OpUGreaterThanEqual %bool %104 %105
        %107 = OpLogicalAnd %bool %103 %106
               OpSelectionMerge %109 None
               OpBranchConditional %107 %108 %109
        %108 = OpLabel
        %110 = OpLoad %uint %shared_idx
        %111 = OpAccessChain %_ptr_StorageBuffer_uint %a %int_0 %110
        %112 = OpLoad %uint %wg_val
        %113 = OpIEqual %bool %112 %uint_0
        %114 = OpSelect %int %113 %int_1 %int_0
        %115 = OpBitcast %uint %114
        %116 = OpAtomicIAdd %uint %111 %uint_1 %uint_0 %115
               OpBranch %109
        %109 = OpLabel
               OpBranch %85
         %85 = OpLabel
               OpBranch %60
         %60 = OpLabel
        %117 = OpLoad %uint %j
        %118 = OpIAdd %uint %117 %int_1
               OpStore %j %118
               OpBranch %57
         %59 = OpLabel
               OpBranch %50
         %50 = OpLabel
        %119 = OpLoad %uint %i
        %120 = OpIAdd %uint %119 %int_1
               OpStore %i %120
               OpBranch %47
         %49 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Shared support gate.** Every test family's `checkSupport` calls `context.requireDeviceFunctionality("VK_KHR_zero_initialize_workgroup_memory")`
  and forwards the construction type to `checkShaderObjectRequirements`
  ([MaxWorkgroupMemoryTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L204-L209),
  [TypeTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L329-L333),
  [CompositeTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L535-L539),
  [MaxWorkgroupsTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L922-L927),
  [SpecializeWorkgroupTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1051-L1062),
  [RepeatedPipelineTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1154-L1159)).
- **Per-type feature gating.** `TypeTest` and `CompositeTest` additionally query `VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2`
  with a `VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SHADER_FLOAT16_INT8_FEATURES` chain and reject unsupported cases via
  `TCU_THROW(NotSupportedError, …)` for `shaderFloat16`, `shaderFloat64`, `shaderInt8`, `shaderInt16`, or `shaderInt64`
  ([TypeTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L329-L389),
  [CompositeTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L535-L568)).
- **Specialization data plumbing.** `runCompute` builds a `VkSpecializationMapEntry` array sized to the `specValues` vector and
  threads the entries through `ComputePipelineWrapper::setSpecializationInfo` before pipeline build
  ([runCompute](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L62-L162)).
- **Resource pre-fill and dispatch.** The shared `runCompute` helper initializes the result buffer to zero for atomic-counting
  families (`increment != 0`) and to `0xff` for direct-write families. It builds one storage-buffer binding and dispatches
  `numWGX`, `numWGY`, and `numWGZ` workgroups. `repeat_pipeline` instead uses two storage-buffer bindings and fills its output buffer with `0xff`; its
  command buffer is recorded once, and the host dispatches `numWGX * numWGY * numWGZ` workgroups before a
  `SHADER_WRITE → HOST_READ` memory barrier and a submit-and-wait
  ([runCompute](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L62-L162),
  [RepeatedPipelineInstance::iterate](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1187-L1333)).
- **Repeat pipeline.** The record-then-submit loop can run the same `cmdBuffer` `m_repeat` times and refill the result buffer
  between submits, but the swapped constructor arguments mean registered cases perform zero or one submission, never two or more
  ([RepeatedPipelineInstance::iterate](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1187-L1333)).
- **Pass/fail rule.** Every entry of the result buffer is expected to equal `numWGX * numWGY * numWGZ` (or zero for the
  inverse-checking variants); any mismatch fails with a `failure at index <i>: expected <expected>, got <got>` message
  ([runCompute result scan](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L150-L161),
  [RepeatedPipelineInstance::iterate result scan](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1314-L1323)).
- **Amber cases.** The `shared_memory_blocks` Amber scripts compare the result buffer against a fixed reference buffer
  (`EXPECT result_buffer EQ_BUFFER reference_buffer`); the result buffer's `FILL 99` makes missing or incorrect shader writes
  visible ([workgroup_size_128.amber](../../../data/vulkan/amber/compute/zero_initialize_workgroup_memory/workgroup_size_128.amber)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `max_workgroup_memory` | The implementation failed to zero-initialize at least one slot of the largest-possible `shared` array, or the shader compiler lowered the `= {}` initializer so SPIR-V no longer carries a `Workgroup` initializer for the largest declared array. |
| `types` | A scalar/vector/matrix workgroup-memory variable of the named type was not zero at shader start, or the explicit-type extension required by the type (such as `shaderFloat16`/`shaderFloat64`/`shaderInt8`/`shaderInt16`/`shaderInt64`) was misreported. |
| `composites` | A nested-array, struct, or 5-level struct array workgroup-memory variable failed to start at zero, including under the explicit-type feature combinations selected by the case's bit-flag index. |
| `max_workgroups` | The zero-initialization guarantee did not hold when a single dispatch axis was pushed to 65535 workgroups, or the `shared uint[2]` exchange was reordered against the barrier. |
| `specialize_workgroup` | The workgroup memory was not zero-initialized for the size chosen at pipeline-creation time, or the host-supplied `local_size_x_id`/`local_size_y_id`/`local_size_z_id` specialization constants did not produce the expected workgroup size. |
| `repeat_pipeline` | With the current argument-order defect, only odd-named cases execute, once, and they test that all shared values read zero; even-named cases execute no shader work and cannot report a result mismatch. |
| `shared_memory_blocks` | An Amber case for a non-trivial workgroup shape failed propagation of invocation 0's value `1` through the workgroup barrier, or failed to write/bind the output buffer; it does not directly diagnose initial zero-initialization. |

### Cause Analysis

#### Shared memory was not zero-initialized at shader start

**Possible failure symptoms:** The single-workgroup cases fail with a `failure at index <i>` message that reports a non-zero
slot for `max_workgroup_memory`, the type-and-composite cases leave non-zero entries in the result buffer, or the `repeat_pipeline`
case fails on a later iteration even though the first iteration passes.

**Possible implementation causes:** The driver or shader compiler must preserve the `OpConstantNull` initializer from the generated
SPIR-V through to the dispatched workgroup memory; a failure could indicate that the shader object / pipeline layout stripped
the initializer, or that the implementation does not respect `VK_KHR_zero_initialize_workgroup_memory` for the specific type
family or composite shape used by the case. Source-level investigation is needed to localize the cause to the compiler, the
pipeline-state handling, or the workgroup memory allocator.

#### Host over-counted because the workgroup size exceeded `maxComputeWorkGroupInvocations`

**Possible failure symptoms:** Only `specialize_workgroup` cases with `x * y * z > maxComputeWorkGroupInvocations` would
nominally fail there; the source's size check turns those into `NotSupportedError` instead, so the symptom is a `NotSupportedError`
log rather than a `compute failed` message.

**Possible implementation causes:** Source inspection shows that the threshold check is at
[SpecializeWorkgroupTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1057-L1061).
The host reads `VkPhysicalDeviceProperties.limits.maxComputeWorkGroupInvocations`; the failure mode is a host bookkeeping error
rather than a device-side bug.

#### Required explicit-type feature is missing

**Possible failure symptoms:** `TypeTest` and `CompositeTest` throw `NotSupportedError` with messages such as `shaderFloat16 not
supported` or `shaderInt64 not supported` rather than reporting a `compute failed` result.

**Possible implementation causes:** The support check reads `VkPhysicalDeviceShaderFloat16Int8Features` from
`VkPhysicalDeviceFeatures2` and rejects unsupported cases
([TypeTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L329-L389),
[CompositeTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L535-L568)). A
correct `NotSupportedError` outcome is intended; a `compute failed` outcome for a case that should have been `NotSupportedError`
points to a failed feature query.

#### Result buffer or descriptor wiring failed

**Possible failure symptoms:** Direct-write families leave entries at the `0xffffffff` host fill, atomic-counting families leave
entries at zero, or output is otherwise unchanged regardless of the shader's reads.

**Possible implementation causes:** Host inspection shows that the result buffer is created with `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT`
and `VK_BUFFER_USAGE_TRANSFER_DST_BIT` and flushed once before `vk.cmdDispatch`
([runCompute](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L62-L162)). A failure pinpoints
either a barrier configuration, a missing barrier, or a descriptor-write problem; source-level investigation is needed to
distinguish those.

#### Amber case driver mismatch

**Possible failure symptoms:** `shared_memory_blocks` Amber cases fail with `EXPECT result_buffer EQ_BUFFER reference_buffer`
mismatches.

**Possible implementation causes:** The Amber scripts pre-fill the result buffer with `99` and the reference buffer with `1`
([workgroup_size_128.amber](../../../data/vulkan/amber/compute/zero_initialize_workgroup_memory/workgroup_size_128.amber)).
A failure points to failed visibility of the writer's `wg_mem = 1` after `barrier()`, or to a buffer-binding or pipeline-build
problem in the Amber driver surface. It cannot indicate a non-zero initial value because the initial value is never read.

## Case Pruning

### Requirement-based pruning

- Every test family requires `VK_KHR_zero_initialize_workgroup_memory` ([checkSupport entries](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L204-L208)).
- `types` cases whose `typeName` references `float16_t`, `float64_t`, `int8_t`, `int16_t`, or `int64_t` (and the corresponding
  vector/matrix names) require the matching explicit-type feature
  ([TypeTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L329-L389)).
- `composites` cases whose `m_caseDef.index` sets any of the bits `0x1`/`0x2`/`0x4`/`0x8`/`0x10` require the matching explicit-type
  feature ([CompositeTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L552-L568)).
- `specialize_workgroup` cases are pruned when `x * y * z > maxComputeWorkGroupInvocations`
  ([SpecializeWorkgroupTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1057-L1061)).
- The `shared_memory_blocks` family is fully pruned when the build is `CTS_USES_VULKANSC` or the construction type is a
  shader-object mode, because Amber cannot drive compute pipelines as shader objects
  ([AddSharedMemoryTests guard](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1359-L1378),
  [group registration guard](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1413-L1420)).

### Design-based pruning

- The generated `TypeCaseDef` list uses the shader translator's canonical explicit-type names (e.g. `f32mat4x3`, `i64vec2`) and
  intentionally does not include GLSL built-in matrix types such as `mat4`; the test exercises the explicit-type extension
  surface end-to-end ([type list](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L446-L466)).
- `max_workgroup_memory` picks the workgroup size as `(limits.maxComputeWorkGroupSize[d] / 13) * 13` so the total stays an
  exact multiple of 13 and below `maxComputeWorkGroupInvocations`. This is a test-design choice rather than a device requirement
  ([MaxWorkgroupMemoryInstance::iterate](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L243-L266)).
- `repeat_pipeline` fixes the workgroup size to `local_size_x_id = WGX`, `local_size_y = 2`, `local_size_z = 1`; the shader is
  designed for a read/write contrast between the y-rows, but the registration argument swap prevents that branch from running
  ([RepeatedPipelineTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1161-L1185)).
- The page intentionally leaves the `max_workgroup_memory` shader's `num_wgs` spec constant reserved but unused, so the host
  side keeps the constant in the specialization map without changing the expected comparison
  ([MaxWorkgroupMemoryTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L211-L241)).

## Key Takeaways

- The C++ families are intended to test the same property: initialized `Workgroup` storage-class variables must start at zero.
  The current `repeat_pipeline` registration prevents its repeat dimension from being exercised, and the Amber cases overwrite
  shared memory before observing it.
- The `= {}` spelling together with `GL_EXT_null_initializer` is the load-bearing piece of GLSL that bridges the Vulkan
  extension to the SPIR-V `OpConstantNull` initializer.
- Result encoding varies by family: atomic-counting cases accumulate zero observations, while the other C++ cases directly
  store values or mismatch flags. All C++ paths finish with a linear comparison against their family-specific expectation.
- `max_workgroups` tests the contract at the maximum per-axis dispatch count. `repeat_pipeline` was designed to test repeated
  runs, but its current registration argument order prevents it from dispatching more than once.
- The Amber scripts under `shared_memory_blocks` are the only test family that does not run through the C++ runtime helper;
  they use fixed workgroup shapes but overwrite shared memory before reading it, so they do not verify its initial value.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test category factory declaration | [vktComputeZeroInitializeWorkgroupMemoryTests.hpp#L38-L39](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.hpp#L38-L39) | Declares `createZeroInitializeWorkgroupMemoryTests`. |
| Top-level group factory | [createZeroInitializeWorkgroupMemoryTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1382-L1424) | Registers the seven test families under the `zero_initialize_workgroup_memory` group. |
| Category dispatcher | [vktComputeTests.cpp#L48-L64](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L64), [vktComputeTests.cpp#L68-L85](../../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85) | Mounts `zero_initialize_workgroup_memory` under the `pipeline`, `shader_object_spirv`, and `shader_object_binary` construction types. |
| Shared runtime helper | [runCompute](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L62-L162) | Records the result buffer, descriptor, command buffer, memory barrier, and host scan; reused by `max_workgroup_memory`, `types`, `composites`, `max_workgroups`, and `specialize_workgroup`. |
| `max_workgroup_memory` shader | [MaxWorkgroupMemoryTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L211-L241), [MaxWorkgroupMemoryInstance::iterate](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L243-L266) | Generates the largest-possible workgroup-memory shader and the per-call workgroup-size specialization. |
| `max_workgroup_memory` registration | [AddMaxWorkgroupMemoryTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L268-L278) | Builds the per-workgroup-count test cases. |
| `types` shader | [TypeTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L391-L434) | Generates the per-type scalar/vector/matrix shader. |
| `types` registration | [AddTypeTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L442-L474) | Builds the type-name test cases. |
| `composites` shader | [CompositeTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L570-L592) | Generates the per-composite shader from the per-case `typeDefinition` and `assignment`. |
| `composites` feature bits | [CompositeTest::checkSupport](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L552-L568) | Encodes the explicit-type feature requirements as a bit mask. |
| `composites` registration | [AddCompositeTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L600-L873) | Builds the 11 hand-written composite test cases. |
| `max_workgroups` shader | [MaxWorkgroupsTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L929-L965) | Generates the per-axis maximum-workgroup shader. |
| `max_workgroups` registration | [AddMaxWorkgroupsTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L995-L1001) | Builds the `x`/`y`/`z` test cases. |
| `specialize_workgroup` shader | [SpecializeWorkgroupTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1064-L1084) | Generates the specialization-constant workgroup-size shader. |
| `specialize_workgroup` registration | [AddSpecializeWorkgroupTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1092-L1107) | Builds the 8×8×8 = 512 size test cases. |
| `repeat_pipeline` shader | [RepeatedPipelineTest::initPrograms](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1161-L1185) | Generates the repeated-pipeline shader. |
| `repeat_pipeline` runtime | [RepeatedPipelineInstance::iterate](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1187-L1333) | Records the pipeline once and has a loop capable of submitting it `m_repeat` times. |
| `repeat_pipeline` registration | [AddRepeatedPipelineTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1335-L1358) | Builds the named `xSize × odd × repeat` cases, but passes `odd` and `repeat` to the constructor in the wrong order. |
| `shared_memory_blocks` registration | [AddSharedMemoryTests](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1360-L1377) | Loads the seven Amber scripts under `data/vulkan/amber/compute/zero_initialize_workgroup_memory/`. |
| Vulkan SC and shader-object guards | [preprocessor guard](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1359-L1378), [group registration guard](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1413-L1420) | Hide `shared_memory_blocks` under `CTS_USES_VULKANSC` and shader-object construction types. |
| Amber tests | [workgroup_size_128.amber](../../../data/vulkan/amber/compute/zero_initialize_workgroup_memory/workgroup_size_128.amber), [workgroup_size_8x8x2.amber](../../../data/vulkan/amber/compute/zero_initialize_workgroup_memory/workgroup_size_8x8x2.amber) | Provide the seven workgroup-shape Amber scripts. |
