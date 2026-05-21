# cooperative_vector

The `cooperative_vector` category covers Vulkan CTS tests for cooperative-vector shader operations, EXT long-vector variants, cooperative-vector matrix multiplication/training operations, and cooperative-vector matrix conversion utilities. The Vulkan test package registers the root as `cooperative_vector` [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1397-L1399). The category dispatcher delegates six non-VulkanSC child groups to two implementation files [vktCooperativeVectorTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L41-L50), and the build inventory lists those registering implementation sources plus a helper utility file [CMakeLists.txt](../../modules/vulkan/cooperative_vector/CMakeLists.txt#L7-L23).

## Registration Entry Point

| Item | Evidence |
|------|----------|
| Package root | [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1397-L1399) |
| Category dispatcher | [vktCooperativeVectorTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L37-L58) |
| Dispatcher declaration | [vktCooperativeVectorTests.hpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.hpp#L30-L35) |
| Build inventory | [CMakeLists.txt](../../modules/vulkan/cooperative_vector/CMakeLists.txt#L7-L23) |

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

### basic — Cooperative-vector language and arithmetic operations

The `basic` group is registered through `createCooperativeVectorBasicTests(testCtx, false)` [vktCooperativeVectorTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L44-L44), which constructs the group name `basic` [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3909-L3912). It covers cooperative-vector construction, conversion, arithmetic, elementary functions, bit operations, and shifts across data types, storage classes, vector sizes, and shader stages [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3920-L4005). See [vktCooperativeVectorBasicTests](../testfiles/cooperative_vector/vktCooperativeVectorBasicTests.md).

### longvec — EXT long-vector variant of the basic matrix

The `longvec` group is registered through `createCooperativeVectorBasicTests(testCtx, true)` [vktCooperativeVectorTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L45-L45), which constructs the group name `longvec` [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3909-L3912). It reuses the basic operation matrix but enables `GL_EXT_long_vector` instead of `GL_NV_cooperative_vector` in shader generation [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L579-L586). See [vktCooperativeVectorBasicTests](../testfiles/cooperative_vector/vktCooperativeVectorBasicTests.md).

### matmul — Cooperative-vector matrix multiply and matrix-add networks

The `matmul` group is registered through `createCooperativeVectorMatrixMulTests(testCtx)` [vktCooperativeVectorTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L46-L46), which constructs the group name `matmul` [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4185-L4189). It covers matrix multiply, matrix multiply-add, transpose variants, chained matrix networks, training-bias cases, activations, layouts, nonuniform offsets, control-flow divergence, and 64-bit indexing [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4197-L4317), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4624-L4666). See [vktCooperativeVectorBasicTests](../testfiles/cooperative_vector/vktCooperativeVectorBasicTests.md).

### training — Cooperative-vector reduce-sum and outer-product accumulation

The `training` group is registered through `createCooperativeVectorTrainingTests(testCtx)` [vktCooperativeVectorTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L47-L47), which constructs the group name `training` [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4671-L4674). It covers `reducesum` and `outerproduct`, training-optimal layout, result-address modes, control-flow divergence, and 64-bit indexing variants [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4682-L4760), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4855-L4901). See [vktCooperativeVectorBasicTests](../testfiles/cooperative_vector/vktCooperativeVectorBasicTests.md).

### layoutconvert — Cooperative-vector matrix layout conversion

The `layoutconvert` group is registered through `createCooperativeVectorMatrixLayoutTests(testCtx)` [vktCooperativeVectorTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L48-L48), which constructs the group name `layoutconvert` [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L424-L428). It converts matrices through selected layout chains on the host or device and checks readable row/column-major values [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L165-L168), [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L341-L411). See [vktCooperativeVectorMatrixTests](../testfiles/cooperative_vector/vktCooperativeVectorMatrixTests.md).

### typeconvert — Cooperative-vector matrix component-type conversion

The `typeconvert` group is registered through `createCooperativeVectorMatrixTypeConversionTests(testCtx)` [vktCooperativeVectorTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L49-L49), which constructs the group name `typeconvert` [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L844-L848). It converts row-major source matrices to inferencing-optimal layout and back to a readable FP16/FP32 row-major destination, then compares each result with a CPU-quantized reference [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L606-L609), [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L819-L839). See [vktCooperativeVectorMatrixTests](../testfiles/cooperative_vector/vktCooperativeVectorMatrixTests.md).

## File Inventory

| Wiki page | Source role | Registered path roots |
|-----------|-------------|-----------------------|
| [vktCooperativeVectorTests](../testfiles/cooperative_vector/vktCooperativeVectorTests.md) | Category dispatcher | `cooperative_vector` |
| [vktCooperativeVectorBasicTests](../testfiles/cooperative_vector/vktCooperativeVectorBasicTests.md) | Basic, long-vector, matrix-multiply, and training implementation | `cooperative_vector.basic`, `cooperative_vector.longvec`, `cooperative_vector.matmul`, `cooperative_vector.training` |
| [vktCooperativeVectorMatrixTests](../testfiles/cooperative_vector/vktCooperativeVectorMatrixTests.md) | Matrix layout and component-type conversion implementation | `cooperative_vector.layoutconvert`, `cooperative_vector.typeconvert` |

## Recurring Parameter Dimensions

| Theme | Observed dimensions | Evidence |
|-------|---------------------|----------|
| Shader stage coverage | Compute, ray tracing stages, vertex, fragment, geometry, tessellation control/evaluation, task, and mesh stage names appear in the operation/matrix/training stage tables | [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3990-L4005), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4319-L4336) |
| Component and matrix types | Float16, float32, uint8, uint32, sint8, sint32, FP8 E4M3/E5M2, and packed 8-bit forms appear in the inspected case tables | [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3952-L3971), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4207-L4257), [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L429-L436) |
| Storage and addressing | SSBO, workgroup memory, variable-pointer forms, physical-storage-buffer addressing, nonuniform offsets, result-address modes, and 64-bit indexing variants are generated in selected families | [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3982-L3988), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4301-L4317), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4751-L4755), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4624-L4666) |
| Matrix layouts | Row-major, column-major, inferencing-optimal, and training-optimal layouts recur in matrix multiply, training, and conversion families | [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4294-L4299), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4728-L4730), [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L438-L443) |
| Host/device conversion | Matrix conversion pages test both host and device conversion paths | [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L445-L448), [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L866-L869) |
| Source-side pruning | The registration loops contain explicit filters for unsupported or excessive combinations; observed documentation should not treat table cartesian products as fully registered without those filters | [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4029-L4130), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4379-L4565), [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L465-L475) |

## Recurring Support Requirements

Cooperative-vector operation tests require Vulkan 1.1, either `cooperativeVector` or `longVector` depending on the path, maximum component-count support, and advertised cooperative-vector property combinations [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L310-L339), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L406-L483). Additional gates cover shader 64-bit indexing, ray tracing and acceleration-structure features, mesh/task shader features, variable pointers, buffer device address, shader float16, and training accumulation properties [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L341-L403). Matrix conversion tests require Vulkan 1.1, `cooperativeVector`, nonzero cooperative-vector property count, and component interpretations advertised by `VkCooperativeVectorPropertiesNV` [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L117-L158), [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L551-L599).

## Recurring Verification Methods

The operation, matrix-multiply, and training tests generate GLSL for the selected stage, execute compute/ray-tracing/graphics/mesh commands, then compare shader outputs against CPU-computed references [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L564-L586), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2367-L2789), [vktCooperativeVectorBasicTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2791-L3896). Matrix conversion tests convert memory through host or device paths and compare converted contents against source values or CPU-quantized references [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L341-L411), [vktCooperativeVectorMatrixTests.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L819-L839).

## Scope Notes

The inspected API test plan provides general Vulkan CTS framework context but no cooperative-vector-specific test-family breakdown [apitests.adoc](../../../../doc/testspecs/VK/apitests.adoc#L8-L13). The Level-3 scope contains the three source files that register tests in this category; `vktCooperativeVectorUtils.cpp` is documented as a helper because it provides data-type and conversion helpers but does not register tests [CMakeLists.txt](../../modules/vulkan/cooperative_vector/CMakeLists.txt#L12-L19), [vktCooperativeVectorUtils.cpp](../../modules/vulkan/cooperative_vector/vktCooperativeVectorUtils.cpp#L34-L101).