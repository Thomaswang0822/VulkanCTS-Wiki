# Understanding Brief: `compute.pipeline.workgroup_memory_explicit_layout`

## One-Sentence Test Purpose

This test checks whether the implementation correctly handles `VK_KHR_workgroup_memory_explicit_layout`-enabled compute
shaders when multiple `Workgroup` storage-class blocks share memory, when `Workgroup` blocks use explicit
`OpMemberDecorate Offset` layout, when a `Workgroup` block is declared with the SPIR-V `Aliased` decoration, when
`OpCopyMemory` moves data between workgroup blocks or between workgroup and storage blocks, and when the interaction with
`VK_KHR_zero_initialize_workgroup_memory` is required by the device.

## Background Knowledge

### Workgroup memory aliasing in SPIR-V

In standard Vulkan compute shaders, two `shared` blocks must not overlap unless the implementation explicitly opts into
sharing memory. The extension adds the SPIR-V capability `WorkgroupMemoryExplicitLayoutKHR` and the `SPV_KHR_workgroup_memory_explicit_layout`
extension so a shader can declare:

- `shared` blocks with the same base address via the `Aliased` decoration on the `OpVariable`,
- `shared` blocks whose `Block` members use `OpMemberDecorate Offset` to specify the byte offset of each member, allowing
  members of different blocks to intentionally overlap.

The C++ tests use the GLSL entry points `GL_EXT_shared_memory_block` (which enables the SPIR-V block syntax) and
`GL_EXT_shader_explicit_arithmetic_types` (which provides the explicit 8-bit, 16-bit, 64-bit types used by some alias
pairs), and `GL_EXT_scalar_block_layout` for the `layout(scalar)` cases.

Why it matters here: without the explicit layout guarantee, the implementation is free to lay out `shared` blocks using any
ordering it wants and would not be required to honor a write to one block being visible as a different-typed read through a
second overlapping block. `alias` and `padding` exist to verify that honoring *is* required and to nail down exactly how the
implementation does it.

### `WorkgroupMemoryExplicitLayoutKHR` feature bits

The Vulkan feature struct `VkPhysicalDeviceWorkgroupMemoryExplicitLayoutFeaturesKHR` exposes:

- `workgroupMemoryExplicitLayout` — the core feature, allowing `Aliased` decorations and `OpMemberDecorate Offset` inside
  `Workgroup` blocks,
- `workgroupMemoryExplicitLayoutScalarBlockLayout` — adds support for the `layout(scalar)` qualifier and the
  `ScalarBlockLayout` SPIR-V decoration in `Workgroup` blocks,
- `workgroupMemoryExplicitLayout8BitAccess` — adds 8-bit `Workgroup` access,
- `workgroupMemoryExplicitLayout16BitAccess` — adds 16-bit `Workgroup` access.

The C++ test gates each case on the smallest subset of these bits that the case actually exercises
([`checkSupportWithParams`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L77-L141)).

### `OpCopyMemory` and `OpControlBarrier` ordering in workgroup memory

`OpCopyMemory` is a raw byte copy in SPIR-V. In `Workgroup` storage class it copies between workgroup blocks; in
`StorageBuffer` storage class it copies between storage buffers. The extension's `OpCopyMemory` Amber cases deliberately
mix two patterns:

- whole-variable copy (when both source and destination have the same `Block` type and the same offsets), and
- `OpAccessChain`-extracted member copy (when the source and destination differ in their `OpMemberDecorate Offset`
  patterns but share the inner array type).

A `barrier()` or `OpControlBarrier` is required between writes and reads from different invocations, because the Amber
scripts deliberately split the work between two push-constant-selected invocations.

### `VK_KHR_zero_initialize_workgroup_memory` interaction

The companion `VK_KHR_zero_initialize_workgroup_memory` extension (or its Vulkan 1.4 core form
`shaderWorkgroupMemoryZeroInitialize`) requires that every `Workgroup` storage-class variable start at zero. The
`zero_ext` Amber cases rely on this: one variable carries a `null` initializer, an aliased variable does not, and the test
expects the aliased variable to read zero as well because of the combined guarantee. The case `block_with_offset` mixes
this with an `OpMemberDecorate Offset` that shifts the aliased region so only part of the output must be zero.

### Pipeline construction type as a gate

The category dispatcher mounts the family under three roots
([`vktComputeTests.cpp#L68-L85`](../../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85)):

- `compute.pipeline.workgroup_memory_explicit_layout` (the default `PIPELINE` construction),
- `compute.shader_object_spirv.workgroup_memory_explicit_layout` (`SHADER_OBJECT_SPIRV`),
- `compute.shader_object_binary.workgroup_memory_explicit_layout` (`SHADER_OBJECT_BINARY`).

The factory then drops the Amber-based children `copy_memory` and `zero_ext` whenever the construction type is a
shader-object variant because Amber cannot drive compute pipelines as shader objects
([`createWorkgroupMemoryExplicitLayoutTests`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1312-L1321)).

Why it matters here: when a reader sees `compute.shader_object_spirv.workgroup_memory_explicit_layout.copy_memory`, they
should expect a missing test rather than a `NotSupportedError` — the case is silently not registered.

## One Concrete Example

A representative case is `compute.pipeline.workgroup_memory_explicit_layout.alias.i32_to_u32_default`:

```text
[host] select GLSL #version 450 + extensions GL_EXT_shared_memory_block, GL_EXT_shader_explicit_arithmetic_types
[host] declare two aliased shared blocks with the default layout qualifier
       shared A { int32_t v; } a;
       shared B { uint32_t v; } b;
[host] declare a storage buffer Result { uint result; }
[host] write -2 to a.v and read through b.v via the inverse bit pattern 0xFFFFFFFE
[host] compile with ShaderBuildOptions(VK_SPIRV_VERSION_1_4, FLAG_ALLOW_WORKGROUP_SCALAR_OFFSETS = false)
[host] call checkSupportWithParams: int32-to-uint32 needs no extra feature (no scalar, no 8/16/64, no float)
[host] build ComputePipelineWrapper pipeline with pipeline-construction type
[host] record cmdBuffer with one vk.cmdDispatch(1,1,1) over a host-visible 1-uint result buffer pre-filled with 0xFF
[device] write a.v = -2 then read b.v == 0xFFFFFFFE and write gl_LocalInvocationIndex into result
[host] invalidate alloc and check result == 0
```

The `alias` reverse-aliased variants (`u32_to_i32_default`) use the opposite write/read pair to confirm that the same
memory region interpreted as either signed or unsigned yields the expected pattern both ways.

## End-to-End Test Flow

```text
[host] choose or generate test parameters (layout, function shape, synchronization, layout qualifier, type pair)
[host] build GLSL with the case-specific shared-block pair and storage-buffer result binding
[host] compile to SPIR-V targeting VK_SPIRV_VERSION_1_4 with optional FLAG_ALLOW_WORKGROUP_SCALAR_OFFSETS
[host] call checkSupportWithParams: throw NotSupportedError if any needed feature is missing
[host] create a host-visible result buffer of size workgroupSize * sizeof(uint32_t), pre-fill with 0xFF
[host] create one storage-buffer descriptor and bind it to a compute pipeline built from the SPIR-V
[host] submit vk.cmdDispatch and submitCommandsAndWait
[host] invalidateAlloc and read back result
[host] decide pass/fail: every entry must equal its expected value, otherwise emit "compute failed"
```

For the Amber `copy_memory` and `zero_ext` cases, the host side is replaced by the Amber driver:

```text
[host] load the .amber file and compile the SPIRV-ASM compute shader
[host] create the storage buffers and (for zero_ext) the push-constant block
[host] dispatch the workgroup selected by the test
[device] execute OpCopyMemory / OpControlBarrier / zero-init observation in the shader
[host] EXPECT result_buffer EQ_BUFFER expected_buffer or EXPECT per-slot zero entries
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL shader source for every `alias`, `zero`, `padding`, and `size` case, built from the case definition
  ([`AliasTest::initPrograms`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L424-L505),
  [`ZeroTest::initPrograms`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L783-L833),
  [`PaddingTest::initPrograms`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1018-L1067),
  [`SizeTest::initPrograms`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1165-L1209)).
- SPIR-V-ASM compute shaders under `data/vulkan/amber/compute/workgroup_memory_explicit_layout/` for the `copy_memory`
  and `zero_ext` cases.
- A `ComputePipelineWrapper` constructed with one of the three pipeline-construction types via the standard
  `vk::ComputePipelineConstructionType` machinery.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|------------------------------|---------------|-------------------------|--------------------|----------------|
| `Result { uint result; }` storage buffer | yes | yes (binding 0) | yes (one uint write) | yes | Single 32-bit pass/fail signal per invocation. |
| `shared A { … v; }` workgroup block | no | n/a (workgroup storage) | yes | no | Producer side of the aliasing/populating/padding/size exercise. |
| `shared B { … v; }` workgroup block | no | n/a (workgroup storage) | yes | no | Consumer side; same base address as `A` under `Aliased`. |
| Amber-side storage buffers (e.g. `input_buffer_0`, `input_buffer_1`, `output_buffer`) | yes (Amber) | yes | yes | yes (Amber EQ_BUFFER) | Source and sink of `OpCopyMemory` calls. |
| Amber-side push-constant `const_buf` | yes (Amber) | yes | n/a (read by shader) | no | Selects which invocation performs the copy in `zero_ext` and `two_invocations`. |

## What Is Checked

The C++ tests scan a one-entry result buffer that the shader writes with `gl_LocalInvocationIndex` (or `i`) and compare
it to the expected value
([`runCompute`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L207-L218)). A
mismatch returns `tcu::TestStatus::fail("compute failed")` and logs `failure at index <i>: expected <expected>, got <got>`.
The Amber tests rely on `EXPECT result_buffer EQ_BUFFER expected_buffer` or `EXPECT output_buffer IDX <off> EQ 0`.

## Behavior Parameter Identification

> **Behavior parameter:** `test family` under `compute.pipeline.workgroup_memory_explicit_layout`
>
> **Candidate values:** `alias`, `zero`, `padding`, `size`, `copy_memory`, `zero_ext`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `alias` | The implementation did not honor `Aliased` shared blocks, did not honor `OpMemberDecorate Offset` in `Workgroup` blocks, or used an incorrect byte order for the aliased reinterpretation of one of the type pairs. |
| `zero` | The implementation did not let one workgroup invocation fully populate `A` and the other fully observe `B`, or did not accept the zero-initialized `shared` block when the shader declares no initializer. |
| `padding` | The implementation did not honor a non-default `layout(offset = N)` member offset inside a `Workgroup` block, leaving the wrong word of the 32-word backing array populated. |
| `size` | The implementation silently rejected a workgroup-memory size larger than `maxComputeSharedMemorySize`, did not actually allocate that much workgroup memory, or returned `NotSupportedError` even though the device reported a sufficient limit. |
| `copy_memory` | `OpCopyMemory` between two `Workgroup` blocks (or between `Workgroup` and `StorageBuffer`) did not produce the expected bytes, or `OpAccessChain` did not produce the expected base pointer for the partial-block copy. |
| `zero_ext` | `VK_KHR_zero_initialize_workgroup_memory` did not zero-initialize a `Workgroup` variable that aliases (partially) with another `Workgroup` variable whose initializer is the SPIR-V `OpConstantNull` form. |

## Important Variations and Special Cases

- The `alias` family generates a cross product over layout qualifier (`default`, `std140`, `std430`, `scalar`), function
  shape (none, read, write, read+write), and synchronization (none, `barrier`), but only for case types whose
  `LayoutFlags` mask matches the current layout
  ([`AddAliasTests`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L641-L670)).
- The `padding` family has two flavors: 32-bit `uint` slots whose offsets are always multiples of 4 bytes, and 8-bit
  `uint8_t` slots whose offsets can be any byte (those cases require `layout(scalar)` and the
  `workgroupMemoryExplicitLayoutScalarBlockLayout` feature)
  ([`AddPaddingTests`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1069-L1108)).
- The `zero` family rejects `float16_t` element types in `useType()` because the `zero` path only covers integral and
  floating types that compare cleanly to zero
  ([`ZeroTest::checkSupport`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L738-L750)).
- The `copy_memory.variable_pointers` Amber case additionally requires `VariablePointerFeatures.variablePointers` and
  `VK_EXT_descriptor_indexing`
  ([`AddCopyMemoryTests`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1266-L1268)).
- The `size` family rejects sizes larger than `maxComputeSharedMemorySize` at `checkSupport` time, so a `NotSupportedError`
  is the expected signal rather than a `compute failed`
  ([`SizeTest::checkSupport`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1153-L1159)).
- The `copy_memory` and `zero_ext` families are only registered under `pipeline` (not under `shader_object_*`); the
  factory guards on `isComputePipelineConstructionTypeShaderObject`
  ([`createWorkgroupMemoryExplicitLayoutTests`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1312-L1321)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|--------------|----------------|
| Feature gating helper | [`checkSupportWithParams`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L77-L141) | Centralizes `workgroupMemoryExplicitLayout*`, `shaderInt8/16/64`, `shaderFloat16`, and `shaderFloat64` checks. |
| `alias` shader generation | [`AliasTest::initPrograms`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L424-L505) | Builds the per-case two-block shader with the matching `layout(...)` qualifier. |
| `alias` case data | [`AddAliasTests`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L536-L671) | Lists every type pair, layout mask, and requirement mask. |
| `zero` shader generation | [`ZeroTest::initPrograms`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L783-L833) | Manually populates `A` with non-zero then zero, then expects `B` to read zero. |
| `padding` shader generation | [`PaddingTest::initPrograms`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1018-L1067) | Compares 32 backing words against a per-case expected array. |
| `size` shader generation | [`SizeTest::initPrograms`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1165-L1209) | Eight workgroup-memory blocks each hold `size/4` words, written in a striped pattern. |
| Shared `runCompute` | [`runCompute`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L143-L219) | Records the per-case shader, dispatches once, scans the result buffer. |
| Amber wrapper | [`CreateAmberTestCase`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1231-L1254) | Adds `VK_KHR_workgroup_memory_explicit_layout`, `VK_KHR_spirv_1_4`, optional `VK_KHR_zero_initialize_workgroup_memory`, and optional `VK_EXT_shader_object` requirements. |
| Family factory | [`createWorkgroupMemoryExplicitLayoutTests`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1289-L1324) | Mounts `alias`, `zero`, `padding`, `size`, and conditionally `copy_memory` and `zero_ext`. |
| Category dispatcher | [`vktComputeTests.cpp#L48-L64`](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L64), [`vktComputeTests.cpp#L68-L85`](../../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85) | Mounts the factory under `pipeline`, `shader_object_spirv`, and `shader_object_binary`. |
| Amber scripts | [`copy_memory_basic.amber`](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_basic.amber), [`copy_memory_two_invocations.amber`](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_two_invocations.amber), [`copy_memory_variable_pointers.amber`](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/copy_memory_variable_pointers.amber), [`zero_ext_block.amber`](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block.amber), [`zero_ext_other_block.amber`](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_other_block.amber), [`zero_ext_block_with_offset.amber`](../../../data/vulkan/amber/compute/workgroup_memory_explicit_layout/zero_ext_block_with_offset.amber) | Provide the `copy_memory` and `zero_ext` Amber scripts. |

## Questions / Risk Points for User Audit

- Is the `Aliased` decoration on `OpVariable` the only SPIR-V mechanism this test exercises for sharing workgroup memory?
- Are the `OpMemberDecorate Offset` decorations inside `Workgroup` blocks enough to prove the explicit-layout guarantee, or
  does the test also rely on `layout(scalar)` to force the layout rules the test wants?
- Is the distinction between `copy_memory` and `zero_ext` (both Amber, but one without and one with the
  `VK_KHR_zero_initialize_workgroup_memory` requirement) clearly drawn?
- Is the test design correctly explained: same memory region, two different GLSL types, byte-level reinterpretation?
- Which concrete example should become the representative walkthrough? The brief suggests
  `alias.i32_to_u32_default` because it covers the simplest cross-type reinterpretation without the `barrier()` /
  `func_*` modifiers.

## Conversion Notes for Final Wiki Rewrite

- The brief's `Background Knowledge` will be distilled into the Level-3 `Background Knowledge` section as four bullets
  covering: explicit layout capability, feature bits, `OpCopyMemory` semantics, and zero-initialize interaction. Detailed
  analogies and feature-by-feature explanations belong on this page only as concise bullets, not as teaching scaffolding.
- The `Behavior Parameter Identification` value `test family` will become the `## Behavior Parameters` section with one
  subsection per family. Each subsection will explain the property tested, the essential mechanism, and the variant
  shape.
- `### Failure Cause Mapping` will be copied directly into the final page. `### Cause Analysis` will be written fresh
  during the rewrite.
- The representative walkthrough will pick `alias.i32_to_u32_default` because the simplest cross-type aliasing case makes
  the aliasing concept concrete without the `barrier()` and `func_*` modifiers that would dominate a more complex case.
- Source details (e.g. exact `FLAG_ALLOW_WORKGROUP_SCALAR_OFFSETS` setup, exact `LayoutFlags` enumeration values, the
  helper macros) move to the `Source Reference Appendix` rather than the body.
- The `vulkan-docs` spec tree is not present in this checkout, so spec-anchored claims are flagged in the brief's
  `## Conversion Notes` and the final page notes that background-knowledge bullets are grounded in CTS source plus
  registration evidence; source-level investigation may be needed to confirm exact spec text.