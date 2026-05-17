# vktImageAtomicOperationTests.cpp

## Overview

Tests that verify the correctness of Vulkan image atomic operations executed from compute shaders. The file covers atomic operations on various image types and formats, including both regular and sparse image backing, with verification of both end results and intermediate return values.

## Role of File

This is an implementation-heavy file that provides test implementations and registration for image atomic operation tests. It registers tests under `image.atomic_operations`.

## Source Code

- Implementation: [vktImageAtomicOperationTests.cpp](../../../modules/vulkan/image/vktImageAtomicOperationTests.cpp)
- Header: [vktImageAtomicOperationTests.hpp](../../../modules/vulkan/image/vktImageAtomicOperationTests.hpp)
- SPIR-V Shaders: [vktImageAtomicSpirvShaders.hpp](../../../modules/vulkan/image/vktImageAtomicSpirvShaders.hpp)

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

Evidence:
- `atomic_operations` group created by [`createImageAtomicOperationTests()`](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2477-L2479)
- Each operation subgroup created via loop at [lines 2540-2652](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2540-L2652)

## Test Families

### add �?Atomic addition operation

Tests the `imageAtomicAdd` function. Supports floating-point formats via `VK_EXT_shader_atomic_float`.

### sub �?Atomic subtraction operation

Tests the `OpAtomicISub` SPIR-V instruction. Requires SPIR-V assembly shaders from `vktImageAtomicSpirvShaders.cpp`.

### inc �?Atomic increment operation

Tests the `OpAtomicIIncrement` SPIR-V instruction. Requires SPIR-V assembly shaders.

### dec �?Atomic decrement operation

Tests the `OpAtomicIDecrement` SPIR-V instruction. Requires SPIR-V assembly shaders.

### min �?Atomic minimum operation

Tests the `imageAtomicMin` function. Supports floating-point via `VK_EXT_shader_atomic_float2` for f32 MIN/MAX.

### max �?Atomic maximum operation

Tests the `imageAtomicMax` function. Supports floating-point via `VK_EXT_shader_atomic_float2` for f32 MIN/MAX.

### and �?Atomic bitwise AND operation

Tests the `imageAtomicAnd` function.

### or �?Atomic bitwise OR operation

Tests the `imageAtomicOr` function.

### xor �?Atomic bitwise XOR operation

Tests the `imageAtomicXor` function.

### exchange �?Atomic exchange operation

Tests the `imageAtomicExchange` function. Verifies that the final value matches one of the atomic arguments.

### compare_exchange �?Atomic compare-exchange operation

Tests the `imageAtomicCompSwap` function. Verifies correct conditional update behavior.

### Nested test structure under each operation

Each operation subgroup contains nested groups (from outermost to innermost):
- Image type: `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array`, `buffer`
- Transfer mode: `notransfer`, `transfer`
- Read type: `normal_read`, `sparse_read` (non-VulkanSC only)
- Backing type: `normal_img`, `sparse_img` (non-VulkanSC only)
- Format combinations with tiling suffixes: `_linear` for linear tiling

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Image Types | IMAGE_TYPE_1D, 1D_ARRAY, 2D, 2D_ARRAY, 3D, CUBE, CUBE_ARRAY, BUFFER | [lines 2492-2499](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2492-L2499) |
| Integer Formats | R32_UINT, R32_SINT, R64_UINT, R64_SINT | [lines 2501-2506](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2501-L2506) |
| Float Formats | R32_SFLOAT, RG16_SFLOAT (Vulkan 1.2+), RGBA16_SFLOAT (Vulkan 1.2+) | [lines 2507-2509](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2507-L2509) |
| Tiling | VK_IMAGE_TILING_OPTIMAL, VK_IMAGE_TILING_LINEAR | [lines 2513-2516](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2513-L2516) |
| Image Sizes | 64x1x1 (1D/buffer), 64x1x8 (1D array), 64x64x1 (2D/cube), 64x64x8 (2D array), 48x48x8 (3D), 64x64x2 (cube array) | [lines 2492-2499](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2492-L2499) |
| Shader Read Type | NORMAL, SPARSE | [lines 2522-2527](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2522-L2527) |
| Backing Type | NORMAL, SPARSE | [lines 2533-2538](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2533-L2538) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_FORMAT_FEATURE_STORAGE_IMAGE_ATOMIC_BIT | Format must support atomic storage | [lines 1023-1028](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1023-L1028) |
| VK_EXT_shader_atomic_float | For float32 atomic operations | [lines 1075-1079](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1075-L1079) |
| VK_EXT_shader_atomic_float2 | For float32 MIN/MAX atomic operations | [lines 1089-1095](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1089-L1095) |
| VK_EXT_shader_image_atomic_int64 | For 64-bit integer atomic operations | [lines 1112-1126](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1112-L1126) |
| VK_NV_shader_atomic_float16_vector | For f16vec2/f16vec4 atomic operations | [lines 1058-1070](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1058-L1070) |
| DEVICE_CORE_FEATURE_SPARSE_BINDING | For sparse images | [line 1036](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1036) |
| DEVICE_CORE_FEATURE_IMAGE_CUBE_ARRAY | For cube array images | [line 1031](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1031) |
| DEVICE_CORE_FEATURE_SHADER_RESOURCE_RESIDENCY | For sparse shader reads | [line 1139](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L1139) |

## Verification Methods

### End Result Verification

`BinaryAtomicEndResultCase` verifies the final value after all atomic operations complete. Uses `isValueCorrect()` at [line 2089](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2089) to compute expected result by applying all atomic arguments to the initial value.

### Intermediate Values Verification

`BinaryAtomicIntermValuesCase` verifies that intermediate return values form a valid sequence. Uses `verifyRecursive()` at [line 2442](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2442) to validate that each return value matches a valid intermediate state in the atomic operation sequence.

### Data Types Verified

- 32-bit signed/unsigned integers
- 64-bit signed/unsigned integers
- 32-bit floating point
- 16-bit floating point vectors (f16vec2, f16vec4)

## Test Principles Observed

- **Order-independent operations**: ADD, SUB, INC, DEC, MIN, MAX, AND, OR, XOR verify final results regardless of invocation order
- **Order-dependent operations**: EXCHANGE and COMPARE_EXCHANGE verify that results match one of the input arguments
- **Sparse image support**: Tests verify sparse atomic operations when `sparseImageFloat32Atomics` or `sparseImageInt64Atomics` features are supported
- **Transfer vs non-transfer**: Tests both using transfer operations and shader-based initialization for image data
- **Multiple invocations per pixel**: Uses `NUM_INVOCATIONS_PER_PIXEL = 5` at [line 303](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L303) to exercise concurrent atomic access
- **Floating-point limitations**: Only ADD, MIN, MAX, and EXCHANGE operations are supported for floating-point formats

## Notes / Uncertainties

- Sparse read tests (`ShaderReadType::SPARSE`) are only available for 2D, 3D, 2D_ARRAY, CUBE, and CUBE_ARRAY image types; 1D, 1D_ARRAY, and BUFFER are excluded at [lines 2621-2623](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2621-L2623)
- Sparse images are only supported with VK_IMAGE_TILING_OPTIMAL (linear tiling excluded at [lines 2595-2598](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L2595-L2598))
- f16vec2 and f16vec4 formats require `VK_NV_shader_atomic_float16_vector` extension (non-VulkanSC only)
- The `Half` and `F16Vec2`/`F16Vec4` wrapper classes at [lines 51-270](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/image/vktImageAtomicOperationTests.cpp#L51-L270) provide half-float arithmetic for reference computation
