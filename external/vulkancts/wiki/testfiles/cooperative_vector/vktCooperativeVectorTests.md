# vktCooperativeVectorTests

This file is the `cooperative_vector` category dispatcher. The Vulkan test package registers the category root as `cooperative_vector` [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1397-L1399), and this dispatcher creates the category group with `createTestGroup` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L55-L58). In non-VulkanSC builds it delegates all visible child groups to the basic and matrix implementation files [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L41-L50).

## Source Files

| Role | Link |
|------|------|
| Category dispatcher | [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp) |
| Dispatcher declaration | [vktCooperativeVectorTests.hpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.hpp#L30-L35) |
| Basic, long-vector, matrix-multiply, and training groups | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3909-L4903) |
| Matrix layout and type-conversion groups | [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L424-L886) |
| Build inventory | [CMakeLists.txt](../../../modules/vulkan/cooperative_vector/CMakeLists.txt#L7-L23) |

## Registration Hierarchy

```text
cooperative_vector
├── basic
├── longvec
├── matmul
├── training
├── layoutconvert
└── typeconvert
```

## Test Families

### basic — Cooperative-vector arithmetic and construction operations

The dispatcher appends `createCooperativeVectorBasicTests(testCtx, false)` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L44-L44), and that factory constructs the registered group name `basic` when the `longVector` argument is false [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3909-L3912). The implementation page is [vktCooperativeVectorBasicTests](vktCooperativeVectorBasicTests.md).

### longvec — EXT long-vector variant of the basic operation matrix

The dispatcher appends `createCooperativeVectorBasicTests(testCtx, true)` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L45-L45), and the same factory constructs the registered group name `longvec` when `longVector` is true [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3909-L3912). The implementation page is [vktCooperativeVectorBasicTests](vktCooperativeVectorBasicTests.md).

### matmul — Cooperative-vector matrix multiply

The dispatcher appends `createCooperativeVectorMatrixMulTests(testCtx)` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L46-L46), and the factory constructs the registered group name `matmul` [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4185-L4189). The implementation page is [vktCooperativeVectorBasicTests](vktCooperativeVectorBasicTests.md).

### training — Cooperative-vector training operations

The dispatcher appends `createCooperativeVectorTrainingTests(testCtx)` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L47-L47), and the factory constructs the registered group name `training` [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4671-L4674). The implementation page is [vktCooperativeVectorBasicTests](vktCooperativeVectorBasicTests.md).

### layoutconvert — Matrix layout conversion

The dispatcher appends `createCooperativeVectorMatrixLayoutTests(testCtx)` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L48-L48), and the factory constructs the registered group name `layoutconvert` [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L424-L428). The implementation page is [vktCooperativeVectorMatrixTests](vktCooperativeVectorMatrixTests.md).

### typeconvert — Matrix component-type conversion

The dispatcher appends `createCooperativeVectorMatrixTypeConversionTests(testCtx)` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L49-L49), and the factory constructs the registered group name `typeconvert` [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L844-L848). The implementation page is [vktCooperativeVectorMatrixTests](vktCooperativeVectorMatrixTests.md).

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Source-level child groups | `basic`, `longvec`, `matmul`, `training`, `layoutconvert`, `typeconvert` | [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L44-L49), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3911-L3911), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4187-L4188), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4671-L4674), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L424-L428), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L844-L848) |
| VulkanSC condition | The dispatcher registers children only inside `#ifndef CTS_USES_VULKANSC` | [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L41-L50) |
| Build files | The cooperative-vector target compiles the dispatcher plus the two registering implementation files and the helper utility file | [CMakeLists.txt](../../../modules/vulkan/cooperative_vector/CMakeLists.txt#L7-L23) |

## Support Requirements

The dispatcher itself has no support checks beyond the VulkanSC compile-time guard; support checks are implemented in the delegated test-case classes [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L41-L50), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L310-L483), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L117-L158), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L551-L599).

## Verification Methods

The dispatcher does not execute tests directly. Verification is delegated to the implementation-specific instances: cooperative-vector operation tests compare shader outputs against CPU references [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2791-L3896), while matrix conversion tests validate converted memory contents after host or device conversion [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L341-L411), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L819-L839).

## Notes

The inspected API test plan provides general Vulkan CTS framework context but no cooperative-vector-specific test-family breakdown [apitests.adoc](../../../../../doc/testspecs/VK/apitests.adoc#L8-L13).