# vktMemoryModelPadding.cpp

This document describes the delegated `memory_model.padding` tests implemented in
[vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp).

## Overview

The `padding` branch verifies that copying `std140` structures through a shader using the Vulkan memory model does not modify
host-visible padding bytes in the destination buffer. The source defines CPU-side structures with explicit padding byte arrays
that mirror shader-side structures without explicit padding fields.

## Role of File

- **Implementation-heavy registered subgroup file.** The file constructs the `padding` group and registers one direct child,
  `test` [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L360-L367).
- It is delegated from the category root in
  [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2410-L2413).

## Source Code

| Purpose | Link |
|---------|------|
| Padding host structures | [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L44-L75) |
| Padding-byte initialization and checks | [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L77-L133) |
| Shader generation | [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L177-L223) |
| Support checks | [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L225-L232) |
| Dispatch and verification | [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L234-L355) |
| Group registration | [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L360-L367) |

## Other Inspected Related Files

| File | Role |
|------|------|
| [vktMemoryModelPadding.hpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.hpp) | Declares `createPaddingTests`. |
| [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp) | Adds `padding` to the category root. |

## Registration Hierarchy

```text
memory_model.padding
└── test
```

## Test Families

### test — `std140` structure-copy padding preservation

The only registered child copies arrays of three structures from a uniform buffer into a storage buffer using `std140` layouts.
The shader declares structures `A`, `B`, and `C`, wraps them in `BufferStructure`, then copies `subA[idx]`, `subB[idx]`, and
`subC[idx]` from input to output for each global invocation
[vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L182-L220).

The CPU-side mirror structures expose 12-byte, 8-byte, and 4-byte padding regions so the test can initialize and validate those
bytes directly [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L44-L75).

## Parameter Dimensions and Observed Values

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Array length | `3` elements per substructure array | [kArrayLength](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L68-L75) |
| Structures | `Pad12`, `Pad8`, `Pad4`, mirrored by shader `A`, `B`, `C` | [host structures](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L44-L75), [shader structures](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L182-L202) |
| Input scalar values | `a = 1`, `b = 2`, `c = 3` | [constants](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L242-L247) |
| Padding bytes | input padding `0xFE`, output-initial padding `0x7F` | [constants](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L242-L258) |
| Work size | dispatch x dimension equals `kArrayLength` | [dispatch](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L340-L345) |

## Support / Feature Requirements

The test requires `VK_KHR_vulkan_memory_model` and the `vulkanMemoryModel` feature before execution
[vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L225-L232).

## Verification Methods

The test initializes input and output buffers on the host, flushes both allocations, dispatches the compute shader, invalidates
the output allocation, and calls `checkValues(kA, kB, kC, kOutputPaddingByte)`. Passing therefore requires the copied scalar
members to match `1`, `2`, and `3`, while the destination padding bytes must remain at the original output padding value
`0x7F` [vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L256-L270) and
[vktMemoryModelPadding.cpp](../../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L350-L355).

## Test Principles Observed

- Verify that shader structure assignment copies declared members without corrupting implicit padding bytes.
- Use host-visible explicit padding arrays as the oracle for bytes that are not shader-declared fields.
- Use `std140` alignment to make the tested padding sizes concrete and observable.

## Notes / Uncertainties

- The file registers only one test case. No additional parameterized padding variants were observed in the inspected source.
