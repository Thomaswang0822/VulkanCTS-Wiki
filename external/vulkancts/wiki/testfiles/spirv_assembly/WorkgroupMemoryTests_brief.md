# Understanding Brief: spirv_assembly.instruction.compute.workgroup_memory / vktSpvAsmWorkgroupMemoryTests.cpp

This brief prepares a Level-3 rewrite of the workgroup-memory SPIR-V assembly page. It is explanation-first and treats the
CTS source as the primary authority.

## One-Sentence Test Purpose

This test checks whether a compute shader can copy an input buffer into SPIR-V `Workgroup` storage, synchronize the
workgroup, and write the array element at the reversed local index back to an output buffer for 11 scalar data types.

Core question: **does the implementation preserve writes to `OpTypePointer Workgroup` storage across an
`OpMemoryBarrier`/`OpControlBarrier` pair so that every invocation in a 128-thread workgroup observes its partner's
write?**

## Background Knowledge

### SPIR-V `Workgroup` storage class and `sharedData`

SPIR-V exposes the `Workgroup` storage class for per-workgroup memory shared by all invocations in a compute workgroup.
A variable declared with `OpTypePointer Workgroup` lives in this storage: each workgroup owns a separate instance, and
the variable is not backed by a host-created buffer or descriptor.

Why it matters here:

- The shader template declares `%sharedData = OpVariable %_ptr_Workgroup__arr_uint_128 Workgroup`
  [shader template](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L214-L217), a 128-element array
  sized to match the workgroup.
- The test does not allocate a Vulkan buffer for `sharedData`. The only host-visible resources are the input and output
  storage buffers bound at descriptor set 0, bindings 0 and 1.

### `OpMemoryBarrier` and `OpControlBarrier`

SPIR-V provides two workgroup-scoped synchronization instructions:

- `OpMemoryBarrier <scope> <semantics>` orders memory accesses without an execution barrier.
- `OpControlBarrier <execution-scope> <memory-scope> <semantics>` orders both execution and memory accesses within the
  given execution scope.

The shader template emits both back-to-back right after the input-to-shared copy and before the shared-to-output read
[shader template](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L251-L252):

```text
OpMemoryBarrier %uint_1 %uint_264
OpControlBarrier %uint_2 %uint_2 %uint_264
```

Why it matters here:

- The paired barriers make the partner write visible. Without them, invocation `idx` could read `sharedData[127-idx]`
  before invocation `127-idx` had stored its element, observing uninitialized workgroup memory.
- The constant operands encode the chosen scopes and semantics. `%uint_1 = 1` is the SPIR-V `Device` scope; `%uint_2 = 2` is the SPIR-V `Workgroup` scope. `%uint_264 = 264 = 0x108` combines the `WorkgroupMemory` memory-class bit (`0x100`) with `AcquireRelease` ordering (`0x8`).

### Index pairing inside a 128-thread workgroup

The compute shader runs with `OpExecutionMode %main LocalSize 16 4 2`, so one workgroup has exactly 128 invocations
matching the 128-element array size. Each invocation flattens its `gl_LocalInvocationID` into a scalar `idx`:

```text
idx = gl_LocalInvocationID.z * 64 + gl_LocalInvocationID.y * 16 + gl_LocalInvocationID.x
```

The reversal pairs invocation `idx` with invocation `127 - idx`, so each output element comes from a different
invocation's write to `sharedData`.

Why it matters here:

- A correct result requires every pair to exchange data through workgroup memory. If any pair fails the exchange, the
  host-side output check detects it as a wrong element.
- The test dispatches only one workgroup (`spec.numWorkGroups = IVec3(1, 1, 1)`), so there is no cross-workgroup
  synchronization involved.

## One Concrete Example

### `float64` representative case

Representative test name from mustpass:

```text
dEQP-VK.spirv_assembly.instruction.compute.workgroup_memory.float64
```

Concrete behavior for this case:

1. The host allocates an `inputData` vector of 128 `double` values produced by `getFloat64s(rnd, numElements)`.
2. The host computes the expected `outputData` as the reversed input array
   [float64 case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L275-L291).
3. The shader specialization substitutes `%f64 = OpTypeFloat 64`, `sizeBytes = 8`, and the `OpCapability Float64` line
   into the shared `shaderSource` template.
4. Each of the 128 invocations reads `inputData[idx]`, stores it into `sharedData[idx]`, runs the paired barriers, then
   reads `sharedData[127-idx]` and writes it to `outputData[idx]`.
5. The host runs `checkResultsFloat64` over the readback buffer, comparing each `uint64` slot against the expected
   `uint64` slot. If both bit patterns are NaN, they are treated as equal
   [checkResultsFloat64](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L115-L139).

Conceptual SPIR-V assembly (annotated, abbreviating boilerplate):

```text
; Capabilities, decorations, and type/constant declarations define:
;   %f64 = OpTypeFloat 64
;   %sharedData is a 128-element Workgroup array of %f64
;   %dataInput (binding 0) and %dataOutput (binding 1) are Uniform BufferBlock storage buffers
%main = OpFunction %void None %3
   %5 = OpLabel
  %idx = OpVariable %_ptr_Function_uint Function
        ; idx = z * 64 + y * 16 + x
        ...
        OpStore %idx %27
        ; read input, store into shared
  %42 = OpLoad %f64 %41
        OpStore %44 %42
        ; synchronize workgroup memory before partner read
        OpMemoryBarrier %uint_1 %uint_264
        OpControlBarrier %uint_2 %uint_2 %uint_264
        ; read partner's shared element and write to output
  %55 = OpLoad %f64 %54
        OpStore %56 %55
        OpReturn
        OpFunctionEnd
```

## End-to-End Test Flow

```text
[host] resolve data type and feature/extension requirements
[host] allocate inputData vector of 128 values for the selected type
[host] compute outputData as inputData reversed
[host] specialize the shared shaderSource template with dataType, dataTypeDecl, sizeBytes, capabilities, extensions
[host] create input storage buffer (binding 0) with inputData
[host] create output storage buffer (binding 1) with outputData
[host] dispatch one compute workgroup (16 x 4 x 2 = 128 invocations)
[device] each invocation reads inputData[idx] into sharedData[idx]
[device] OpMemoryBarrier + OpControlBarrier make workgroup writes visible
[device] each invocation reads sharedData[127-idx] and writes it to outputData[idx]
[host] copy outputData back, run the per-type verification callback
[host] decide pass/fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | Generated/loaded where | Role |
|----------|------------------------|------|
| SPIR-V assembly text | [StringTemplate shaderSource](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L176-L261) | Single shared template specialized per data type through `${dataType}`, `${dataTypeDecl}`, `${sizeBytes}`, `${capabilities:opt}`, `${extensions:opt}`. |
| Per-type specialization map | [float64 case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L263-L292) and following blocks | Substitutes data type, byte stride, capabilities, and extensions into the template. |
| Input/output buffer payloads | Per-case `inputData`/`outputData` vectors | Random per-seed input values plus reversed expected output. |

There is no GLSL or HLSL source. The shader text is authored directly as SPIR-V assembly in the C++ string template.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input storage buffer | Yes | Descriptor binding `0` | Read by compute shader | No | Provides the 128 random input values. Declared with `BufferBlock` decoration and `Uniform` storage class (legacy SPIR-V SSBO form). |
| Output storage buffer | Yes | Descriptor binding `1` | Written by compute shader | Yes | Receives the reversed-array result for host verification. Same `BufferBlock`/`Uniform` declaration form. |
| `sharedData` workgroup variable | No host object | No descriptor binding | Written and read inside the workgroup | No | The actual tested workgroup-memory object; not backed by a host resource. |
| Compute pipeline | Yes | Pipeline state | Executes one dispatch | No | Single compute dispatch with one workgroup. |

## What Is Checked

### Device-side observable behavior

The shader itself does not perform a pass/fail decision. It writes whatever it observes from `sharedData[127-idx]` to
`outputData[idx]`. If workgroup memory synchronization failed, that output slot would carry uninitialized or stale data.

### Host-side checks

The host reads back `outputData` and runs a per-type verification callback:

- For `float64`, `float32`, and `float16`, the custom callbacks compare the bit patterns element-by-element and treat
  two NaN bit patterns as equal
  [checkResultsFloat16](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L55-L79),
  [checkResultsFloat32](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L81-L105),
  [checkResultsFloat64](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L115-L139).
- For all integer types, no custom callback is registered (`spec.verifyIO` is left unset), so the default
  `SpvAsmComputeShaderCase` output verification compares raw bytes.

Pass condition: every element of `outputData` equals the reversed `inputData` element, with NaN-as-equal handling for
floating-point types. There is no tolerance and no partial-success rule.

## Behavior Parameter Identification

> **Behavior parameter:** data type, expressed as the registered test case leaf.
>
> **Candidate values:** `float64`, `float32`, `float16`, `int64`, `int32`, `int16`, `int8`, `uint64`, `uint32`,
> `uint16`, `uint8`.

The 11 leaves are siblings under `spirv_assembly.instruction.compute.workgroup_memory` with no intermediate nodes. Each
leaf changes the SPIR-V data type substituted into the shared template, the buffer stride, the buffer payload generator,
the required capabilities and extensions, and (for floating-point leaves) the verification callback.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `float64` | Workgroup-memory synchronization or float64 storage-buffer handling, with NaN-aware comparison accounting for NaN bit-pattern differences. |
| `float32` | Workgroup-memory synchronization for baseline 32-bit float storage. |
| `float16` | Workgroup-memory synchronization for 16-bit storage, including `SPV_KHR_16bit_storage` and `Float16` capability paths. |
| `int64` / `uint64` | Workgroup-memory synchronization for 64-bit integer storage, gated by `Int64` capability and `shaderInt64` feature. |
| `int32` / `uint32` | Baseline workgroup-memory synchronization for 32-bit integer storage, no extra features required. |
| `int16` / `uint16` | Workgroup-memory synchronization for 16-bit integer storage, including `SPV_KHR_16bit_storage` and `Int16` capability. |
| `int8` / `uint8` | Workgroup-memory synchronization for 8-bit integer storage, including `SPV_KHR_8bit_storage`, `UniformAndStorageBuffer8BitAccess`, and `Int8`. |

A common cause across every leaf is incorrect workgroup-memory barrier handling: the host observes wrong
outputData elements whenever the paired barriers do not make partner writes visible before partner reads.

## Important Variations and Special Cases

### Per-type feature and extension gates

The 11 leaves split into five feature/extension tiers:

- Baseline (no extra requirements): `float32`, `int32`, `uint32`.
- `shaderFloat64` + `Float64`: `float64`.
- `shaderInt64` + `Int64`: `int64`, `uint64`.
- `shaderInt16` + `Int16` + `VK_KHR_16bit_storage` + `storageBuffer16BitAccess`: `int16`, `uint16`.
- `shaderFloat16` + `Float16` + `VK_KHR_16bit_storage` + `VK_KHR_shader_float16_int8` + `storageBuffer16BitAccess`: `float16`.
- `shaderInt8` + `Int8` + `VK_KHR_8bit_storage` + `VK_KHR_shader_float16_int8` + `uniformAndStorageBuffer8BitAccess`: `int8`, `uint8`.

### NaN-aware verification for floating-point types

The three floating-point leaves use type-specific verification callbacks that reinterpret the buffer as integer bit
patterns and treat two NaN bit patterns as equal. The `float64` path uses a hand-rolled `isNanFloat64` helper because
the framework's `Float64` utility does not expose a `isNaN()` predicate directly
[isNanFloat64](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L107-L113).

### Unused `DataType` struct

The C++ file defines a `DataType` struct that is not consumed by the per-case registration logic
[DataType](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L48-L53). The case-specific
specialization maps are written inline. This is dead code rather than a test variation.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| NaN-aware verification callbacks | [checkResultsFloat16/32/64](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L55-L139) | Defines how floating-point results are compared bit-for-bit with NaN equality. |
| Workgroup size and element count | [numElements = 128](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L141-L156) | Pins the array length and dispatch shape used by every case. |
| Shared SPIR-V assembly template | [shaderSource](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L176-L261) | The single template specialized per data type. |
| Paired barriers | [OpMemoryBarrier + OpControlBarrier](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L251-L252) | The synchronization under test. |
| float64 specialization | [float64 case](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L263-L292) | Representative case used for the shader walkthrough. |
| Test family registration | [createWorkgroupMemoryComputeGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmWorkgroupMemoryTests.cpp#L618-L624) | Creates the `workgroup_memory` group and adds the 11 type leaves. |
| Parent attachment | [vktSpvAsmInstructionTests.cpp#L21415](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21415) | Attaches `workgroup_memory` under `spirv_assembly.instruction.compute`. |
| Mustpass entries | [spirv-assembly.txt#L19887-L19897](../../../mustpass/main/vk-default/spirv-assembly.txt#L19887-L19897) | Lists the 11 `dEQP-VK.spirv_assembly.instruction.compute.workgroup_memory.*` leaves. |

## Questions / Risk Points for User Audit

- [x] Is the data type leaf the correct primary behavioral axis? Yes — every leaf changes the SPIR-V data type, byte
  stride, feature/extension set, and (for floats) the verification callback, while the synchronization logic stays
  identical.
- [x] Is one representative walkthrough sufficient? Yes — the shader template is shared, and per-type variation only
  changes the substituted data type and capabilities. The `float64` walkthrough is selected because it exercises the
  NaN-aware verification path and the largest stride.
- [x] Should the final page document the exact bit decomposition of the `%uint_264` semantic constant? Yes. It records the concise, source-relevant form: `0x108` combines `WorkgroupMemory` with `AcquireRelease`, without treating the operand encoding as a separate test dimension.

## Conversion Notes for Final Wiki Rewrite

- Distill the background into a Level-3 prerequisite list: SPIR-V `Workgroup` storage class, the paired
  `OpMemoryBarrier`/`OpControlBarrier` synchronization, and the 128-thread workgroup pairing.
- Preserve the `float64` walkthrough as the single representative shader walkthrough. Per the TEMP-SPIRV-ASSEMBLY
  deviation, place the extracted SPIR-V assembly under `#### Source Code` (unfoldable) and omit the `#### SPIR-V`
  subsection. Run `spirv-as` → `spirv-val` → `spirv-dis` as a generation-time validation gate only; do not publish the
  disassembler output.
- Move the per-type feature/extension tier table into `## Behavior Parameters` as the value-by-value breakdown.
- Carry the `### Failure Cause Mapping` table directly into the final page's `### Failure Cause Mapping`.
- Keep the resource table compact: only the two descriptor-bound buffers and the `sharedData` workgroup variable are
  load-bearing.
