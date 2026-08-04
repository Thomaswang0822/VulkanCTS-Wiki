# Understanding Brief: PhysicalStorageBufferPointerTests

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation can take a buffer device address produced on the host, hand it to a compute shader as a `PhysicalStorageBuffer` pointer (through a push constant or an SSBO field), and dereference it with `OpLoad`/`OpStore` to copy 64 int32 elements from a source buffer to a destination buffer.

## Background Knowledge

### Physical storage buffer pointers

The `PhysicalStorageBuffer` storage class holds pointers that reference device memory by 64-bit address rather than by a `VkBuffer`-backed variable. A shader forms such a pointer either by loading a pointer-typed value that the host wrote into a push constant or SSBO field, or by converting a 64-bit unsigned integer address with `OpConvertUToPtr`. Dereferences use the `Aligned` optional operand on `OpLoad`/`OpStore` to promise the access alignment. This is the SPIR-V analog of a raw device pointer in C, and it is the single mechanism this page exercises.

Why it matters here:

- The shader copies buffers that the host never binds as `StorageBuffer` variables; the host only publishes their device addresses. Correctness depends on the address round trip: host `vkGetBufferDeviceAddress` → push-constant/SSBO field → shader pointer → `OpLoad`/`OpStore`.
- The `PhysicalStorageBufferAddresses` capability, the `SPV_KHR_physical_storage_buffer` extension, and the `PhysicalStorageBuffer64` addressing model are all required to make this round trip legal.

### Buffer device addresses on the host

`VK_KHR_buffer_device_address` (core in Vulkan 1.2) exposes `vkGetBufferDeviceAddress`, which returns a 64-bit address for a buffer created with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT`. The host then writes that 64-bit value into a push constant or SSBO field that the shader interprets as a `PhysicalStorageBuffer` pointer. The CTS feature gate is `bufferDeviceAddress`.

### `OpConvertUToPtr` and `OpSelect` on pointers

`OpConvertUToPtr` turns a 64-bit unsigned integer into a `PhysicalStorageBuffer` pointer. `OpSelect` chooses between two pointer-typed operands based on a boolean condition. SPIR-V 1.4 permits `OpSelect` on pointer operands. The `addrs_in_ssbo` case uses both so the same buffer address can be reached either as a pointer-typed SSBO field or as a `uint64` field converted at use time.

## One Concrete Example

The `push_constants` case is the smallest faithful example. The host creates two int32 buffers of 64 elements, queries each one's device address, and packs the pair into a push constant struct `{uint64_t src; uint64_t dst; int32_t cnt; bool use_fun;}`. The shader loads `src` and `dst` as `PhysicalStorageBuffer` pointers to a runtime array of int32, then loops `cnt` times copying `src[i]` to `dst[i]` with `OpLoad`/`OpStore Aligned 4`. The host invalidates the destination buffer and compares it element-by-element against the source. The copy succeeds only if the device address survived the host→push-constant→shader round trip and the physical-storage-buffer dereference honored the `Aligned 4` access.

## End-to-End Test Flow

```text
[host] check support: VK_KHR_get_physical_device_properties2, bufferDeviceAddress (and shaderInt64 for addrs_in_ssbo)
[host] create src and dst int32[64] buffers with VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT (host-visible, coherent)
[host] src.iota(64); dst.zero(); flush both
[host] query src.getDeviceAddress() and dst.getDeviceAddress()
[host] for push_constants*: pack {src, dst, 64, use_fun} into a push constant
[host] for addrs_in_ssbo: build an SSBO struct {srcAsBuff, srcAsUint, dstAsBuff, dstAsUint} all equal to the two addresses; bind it as descriptor set 0
[host] build compute pipeline (no descriptor set for push_constants cases; one storage-buffer descriptor for addrs_in_ssbo)
[host] push constants (push_constants cases only), then dispatch: 1x1x1 for push_constants cases; 64x1x1 for addrs_in_ssbo
[device] load PhysicalStorageBuffer pointers from push constant or SSBO; dereference with OpLoad/OpStore Aligned 4
[host] submit, wait, invalidate dst
[host] pass iff std::equal(src.begin(), src.end(), dst.begin())
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- One SPIR-V assembly compute shader string template per `initPrograms` overload. The push-constant template is shared by `push_constants` and `push_constants_function`; the `use_fun` push-constant value selects the inline loop versus the `OpFunctionCall` path at runtime. The `addrs_in_ssbo` template is a separate, single-entry-point shader.
- Both shaders target SPIR-V 1.4 via `vk::SpirVAsmBuildOptions(..., vk::SPIRV_VERSION_1_4, true)`.
- No GLSL or HLSL source exists; the assembly is the source of truth.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `src` int32[64] buffer | yes, with shader-device-address usage | addressed by device address only (push_constants: via push constant; addrs_in_ssbo: via SSBO field) | read by shader through `PhysicalStorageBuffer` pointer | no (host compares it directly) | Source of the copy; its device address is the value under test |
| `dst` int32[64] buffer | yes, with shader-device-address usage | addressed by device address only | written by shader through `PhysicalStorageBuffer` pointer | yes, after invalidate | Destination of the copy; compared against `src` |
| Push constant `{src, dst, cnt, use_fun}` | yes | yes, via `cmdPushConstants` | read by shader | no | Carries the two device addresses for the push_constants cases |
| SSBO `{srcAsBuff, srcAsUint, dstAsBuff, dstAsUint}` | yes | yes, descriptor set 0 binding 0 | read by shader | no | Carries the two device addresses in both pointer-typed and uint-typed fields for the addrs_in_ssbo case |

## What Is Checked

- The host compares the destination buffer against the source buffer element-by-element using `std::equal` with no tolerance. The case passes only when all 64 int32 elements match.
- For the push_constants cases, the single dispatched invocation must copy all 64 elements via its loop; a short or skipped copy produces a mismatched destination.
- For addrs_in_ssbo, each of the 64 invocations copies one element indexed by `GlobalInvocationID.x`. The `gid_x % 2` selector alternates between pointer-typed and uint-converted address representations, so a single mis-handled representation produces a stable pattern of wrong slots.

## Behavior Parameter Identification

> **Behavior parameter:** the test case leaf (`pass method`), which controls how the two buffer device addresses are communicated to the shader.
>
> **Candidate values:** `push_constants`, `push_constants_function`, `addrs_in_ssbo`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `push_constants` | Push-constant transport of 64-bit device addresses broken, or `PhysicalStorageBuffer` pointer formed from a push-constant field dereferenced incorrectly (`OpAccessChain` + `OpLoad Aligned 4`/`OpStore Aligned 4`). |
| `push_constants_function` | Same as `push_constants`, plus passing `PhysicalStorageBuffer` pointers as `OpFunctionParameter` values and dereferencing them inside the callee. |
| `addrs_in_ssbo` | `OpConvertUToPtr` on a 64-bit SSBO field mis-handled, `OpSelect` between pointer-typed and uint-converted pointers mis-handled, or `Int64` capability handling for the `uint64` address fields. |

All three cases share the same final host comparison; any destination element that differs from the corresponding source element fails the case.

## Important Variations and Special Cases

- The `push_constants` and `push_constants_function` cases share one shader. The `use_fun` push-constant field selects the inline copy loop (`use_fun == 0`) versus the `OpFunctionCall %cpbuffs` path (`use_fun != 0`). The function-call path additionally exercises `PhysicalStorageBuffer` pointers as function parameters, which is the only structural difference between the two registrations.
- The `addrs_in_ssbo` shader is single-entry, dispatched 64×1×1, and uses `gid_x % 2` to alternate address representations between invocations. The host fills the SSBO with the same device address twice (once as a pointer-typed field, once as a `uint64` field), so both representations must resolve to the same buffer.
- All three cases require SPIR-V 1.4 and the `PhysicalStorageBufferAddresses` capability plus the `SPV_KHR_physical_storage_buffer` extension. `addrs_in_ssbo` additionally requires the `Int64` capability and the `shaderInt64` feature because the SSBO stores the addresses as `uint64` fields.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `PassMethod` enum and `TestParams` | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L55-L66](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L55-L66) | Defines the three pass methods and the element count. |
| Push-constant shader template | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L400-L527](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L400-L527) | Shared SPIR-V assembly for `push_constants` and `push_constants_function`. |
| Push-constant host setup and comparison | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L533-L581](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L533-L581) | Builds buffers, queries device addresses, pushes constants, dispatches, compares. |
| SSBO shader template | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L588-L670](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L588-L670) | SPIR-V assembly for `addrs_in_ssbo` with `OpConvertUToPtr` and `OpSelect`. |
| SSBO host setup and comparison | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L682-L738](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L682-L738) | Builds the SSBO, binds it, dispatches 64×1×1, compares. |
| Support checks | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L350-L362](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L350-L362) | `bufferDeviceAddress`, `shaderInt64`, instance extension gates. |
| Registration factory | [vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L742-L763](../../../modules/vulkan/spirv_assembly/vktSpvAsmPhysicalStorageBufferPointerTests.cpp#L742-L763) | Registers the three test case leaves under `physical_storage_buffer`. |

## Questions / Risk Points for User Audit

- Is the core test purpose (host device address → shader physical-storage-buffer pointer → faithful copy) clearly stated?
- Is the shared-shader relationship between `push_constants` and `push_constants_function` clear, and is the `use_fun` runtime branch the only structural difference?
- Is the `addrs_in_ssbo` address-representation duality (pointer-typed field versus `uint64` field plus `OpConvertUToPtr`/`OpSelect`) explained at the right depth?
- Are the two representative walkthroughs (push-constants shader, addrs_in_ssbo shader) the right choice, or should `push_constants_function` get a third walkthrough?

## Conversion Notes for Final Wiki Rewrite

- The brief's Background Knowledge on physical-storage-buffer pointers, host device addresses, and `OpConvertUToPtr`/`OpSelect` distills into a short Level-3 `## Background Knowledge` bullet list. Keep only what the reader needs before the shader walkthroughs.
- The push-constants shader becomes Representative Shader Walkthrough 1; the addrs_in_ssbo shader becomes Representative Shader Walkthrough 2. Two walkthroughs are justified because the two shaders are structurally different (push-constant transport with a runtime loop/function-call branch versus SSBO transport with address-representation selection).
- The `### Failure Cause Mapping` table above is copied directly into the final page's `### Failure Cause Mapping`.
- `### Cause Analysis` is written fresh during the rewrite.
- The end-to-end flow and resource table condense into `## Runtime Execution and Result Checking`.
- The `vulkan-docs/src/chapters/` directory is absent in this checkout; Background Knowledge is grounded in the SPIR-V capability/extension semantics visible in the CTS source plus established Vulkan physical-storage-buffer semantics. This is consistent with the sibling `PointerParameterTests.md` rewrite.
