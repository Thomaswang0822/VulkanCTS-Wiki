# Understanding Brief: `memory.concurrent_access`

## One-Sentence Test Purpose

This test checks whether a host and a compute shader can access disjoint elements of one host-visible coherent storage buffer concurrently without corrupting untouched elements, and whether completed shader writes become visible to the host.

## Background Knowledge

### Disjoint concurrent accesses

A data race requires conflicting accesses to the same memory location. This test separates the locations by element parity: the shader accesses even elements while a host thread reads odd elements. The implementation must not let a device access alter neighboring host-read elements.

Why it matters here:
- The concurrent check concerns isolation between disjoint elements, not synchronized access to one element.
- The selected element width determines the tested granularity.

### Device-to-host visibility

A memory dependency makes writes available and visible to later accesses. The test records a compute-to-host memory barrier with shader read/write source access and host-read destination access. Host-coherent memory removes the need for an explicit invalidate after device writes have been made available to the host domain.

Why it matters here:
- Queue completion alone establishes completion; the recorded barrier supplies the device-write-to-host-read memory dependency.
- `VK_MEMORY_PROPERTY_HOST_COHERENT_BIT` controls cache-management requirements, not which buffer elements may be accessed concurrently.

## One Concrete Example

On a device without 8-bit or 16-bit storage-buffer access, the test views the first 500 bytes of its 501-byte allocation as 125 `uint32_t` elements. It initializes every byte to `0x5b`, so each element starts as `1532713819` (`0x5b5b5b5b`). Workgroup 0 checks element 0, workgroup 1 checks element 2, and so on. A second host thread reads elements 1, 3, 5, and so on while the dispatch may be running. After completion, even elements must equal `3402287818` (`0xcacacaca`), and odd elements must retain the initial value.

## End-to-End Test Flow

```text
[host] allocate a 501-byte host-visible coherent storage buffer
[host] choose the smallest supported storage-buffer integer width: 8, 16, or 32 bits
[host] initialize every byte to 0x5b and bind the buffer at descriptor binding 0
[host] record a compute dispatch followed by a compute-shader-to-host memory barrier
[host] lock the final-validation mutex and start a second host thread
[host/device] submit the command buffer while the second thread reads only odd elements
[device] each workgroup checks and conditionally replaces one even element with the 0xca byte pattern
[host] wait for queue completion, release the final-validation mutex, and join the second thread
[host] the second thread checks every element against its parity-dependent expected value
[host] report the first classified mismatch or pass
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms()` registers three inline GLSL compute shaders: `comp_1`, `comp_2`, and `comp_4`. They differ only in storage element type, required extension, and constants. Runtime feature queries select the shader for the smallest supported width. No explicit `vk::ShaderBuildOptions` are supplied, so compilation uses the source collection's baseline SPIR-V target.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 501-byte `BufferWithMemory` allocation | yes | yes, storage buffer at set 0 binding 0 | reads and conditionally writes even typed elements | yes, directly through the persistent mapping | Holds both the shader-accessed and host-read element sets. |
| Compute pipeline and `comp_1`/`comp_2`/`comp_4` module | yes | yes | executes on the device | no | Selects the access granularity supported by the device. |
| `VkMemoryBarrier` in the command buffer | yes | part of submitted commands | orders shader accesses before host reads | no | Makes completed shader writes available for host visibility. |
| `std::mutex` and `ResultInfo` | yes | no | no | host-only | Prevent final validation from starting before queue completion and preserve the first result classification. |

## What Is Checked

- During submission, each odd typed element read by the second thread must still equal the repeated `0x5b` initial pattern.
- After queue completion and the memory barrier, every even typed element must equal the repeated `0xca` shader pattern.
- After completion, every odd typed element must still equal the initial pattern.
- The first mismatch records its index, observed value, and one of three result types. The test passes only when no mismatch occurs.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `shader_and_host`

The single leaf is the behavioral axis because it selects the only implemented concurrent host/device mechanism. Integer width is runtime-selected capability coverage, not a registered behavior value.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shader_and_host` | Disjoint-access corruption during the dispatch, incorrect compute storage-buffer access, or failed device-to-host visibility after the barrier. |

## Important Variations and Special Cases

- The test prefers 8-bit storage-buffer elements when `uniformAndStorageBuffer8BitAccess` is supported, otherwise 16-bit elements when `uniformAndStorageBuffer16BitAccess` is supported, and otherwise 32-bit elements. This changes access granularity but not the parity-based mechanism.
- Integer division ignores the trailing byte(s): 501 elements at 8 bits, 250 at 16 bits, or 125 at 32 bits. The odd allocation size does not create an unaligned typed access.
- The dispatch count is the ceiling of half the typed element count. For every possible selected width, this maps exactly to the valid even indices.
- The test is registered for Vulkan and Vulkan SC. Its registration sits outside the `CTS_USES_VULKANSC` exclusion in the memory test category dispatcher.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Concurrent and final host checks | [`secondThreadFunction()`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L63-L104) | Defines odd-element concurrent reads and parity-based final validation. |
| Buffer, width selection, descriptors, dispatch, and barrier | [`testShaderAndHostAccess()`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L106-L247) | Defines the complete runtime and result classification. |
| Inline compute shaders | [`initPrograms()`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L250-L285) | Defines all three generated GLSL variants. |
| Test registration | [`createConcurrentAccessTests()`](../../../modules/vulkan/memory/vktMemoryConcurrentAccessTests.cpp#L289-L295) | Registers `concurrent_access.shader_and_host`. |
| Category registration | [`createTests()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L44-L74) | Places the test family under `memory`, including Vulkan SC. |
| Mustpass leaf | [`memory.txt`](../../../mustpass/main/vk-default/memory.txt#L580) | Confirms the executable path. |
| Availability and visibility | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L159-L160) | Defines what a memory dependency enforces. |
| Host coherent memory | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L1733-L1749) | Defines automatic host-domain availability and visibility. |

## Questions / Risk Points for User Audit

- The purpose, host/device timeline, resource roles, and three failure classes are resolved from source.
- The registered path is confirmed by source registration and the default mustpass list.
- The 32-bit shader is the representative walkthrough because it requires no optional storage extension and preserves the same mechanism as narrower variants.
- No unresolved semantic risk blocks the rewrite.

## Conversion Notes for Final Wiki Rewrite

- Keep disjoint concurrent accesses and device-to-host visibility as the two prerequisites.
- Turn the 32-bit concrete example into one representative shader walkthrough and cover 8-bit/16-bit differences in its variation table.
- Keep integer width in the parameter inventory, but carry `shader_and_host` as the primary behavioral axis.
- Copy the Failure Cause Mapping table unchanged.
- Move source navigation to the final appendix and keep the runtime timeline concise.
