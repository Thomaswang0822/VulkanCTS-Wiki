# vktCooperativeVectorBasicTests

This file registers and implements four `cooperative_vector` child groups: `basic`, `longvec`, `matmul`, and `training`. The dispatcher calls these factories from the category root [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L44-L47). The file uses one shared `CooperativeVectorTestCase`/`CooperativeVectorTestInstance` implementation for shader generation, execution, and result comparison [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L264-L310), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1753-L1796).

## Source Files

| Role | Link |
|------|------|
| Registering implementation | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp) |
| Factory declarations | [vktCooperativeVectorBasicTests.hpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.hpp#L34-L37) |
| Category dispatcher | [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L44-L47) |
| Component and data helpers | [vktCooperativeVectorUtils.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorUtils.cpp#L34-L101) |

## Registration Hierarchy

```text
cooperative_vector
├── basic
├── longvec
├── matmul
└── training
```

## Test Families

### basic — Cooperative-vector language and arithmetic operations

The `basic` group is produced by `createCooperativeVectorBasicTests(testCtx, false)` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L44-L44). Its direct children are operation groups from the `ttCases` table: `length`, `constant`, `convert`, `composite`, `composite_rvalue`, `vector_extract`, arithmetic operations, elementary functions, bit operations, shifts, and `composite_array` [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3920-L3950). Under each operation, the code nests data-type pairs, storage classes, component counts, and shader stages [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3952-L4005), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4007-L4181).

### longvec — EXT long-vector language and arithmetic operations

The `longvec` group is produced by the same factory when `longVector` is true [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L45-L45), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3909-L3912). It reuses the same operation, data-type, storage-class, component-count, and stage generation loops as `basic`, but passes `useLongVector = true` into the case definition [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4146-L4172). Shader generation enables `GL_EXT_long_vector` for these cases instead of `GL_NV_cooperative_vector` [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L579-L586).

### matmul — Cooperative-vector matrix multiply and matrix-add operations

The `matmul` group is produced by `createCooperativeVectorMatrixMulTests` [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4185-L4189). Its direct operation children cover `matrixmul`, `matrixmuladd`, `matrixmuladdtranspose`, `matrixmul3`, `matrixmul2addmul2`, `matrixmul2add`, and `matrixmultrainingbias` [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4197-L4205). The nested matrix dimensions are named `NxK`, with examples from `1x1` through `128x128` in the inspected table [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4259-L4277). This group also adds a `64b_indexing` child with per-stage `muladd_...` cases [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4624-L4666).

### training — Cooperative-vector training operations

The `training` group is produced by `createCooperativeVectorTrainingTests` and registers the name `training` [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4671-L4674). Its direct operation children are `reducesum` and `outerproduct` [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4682-L4685). Reduce-sum uses component-count names such as `components1` through `components65`, while outer-product uses `NxK` matrix sizes [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4692-L4720). This group also adds a `64b_indexing` child with `reducesum_...` and `outerproduct_...` per-stage cases [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4855-L4901).

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Basic/longvec operations | `length`, `constant`, `convert`, `composite`, `composite_rvalue`, `vector_extract`, `add`, `sub`, `mul`, `div`, `negate`, `vectortimesscalar`, `exp`, `log`, `tanh`, `atan`, `min`, `max`, `clamp`, `step`, `fma`, `func`, `and`, `or`, `xor`, `not`, `shl`, `shr`, `composite_array` | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3920-L3950) |
| Basic/longvec data type pairs | Float16, uint8, uint32, sint8, sint32, and float32 input/output combinations listed in `dtCases` | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3952-L3971) |
| Basic/longvec component counts | `components1`, `components2`, `components3`, `components4`, `components5`, `components6`, `components7`, `components8`, `components9`, `components31`, `components65`, `components1024` | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3973-L3980) |
| Storage classes | `buffer`, `workgroup`, `buffer_varptr`, `workgroup_varptr`, `physical_buffer`; training omits `workgroup` and `workgroup_varptr` | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3982-L3988), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4722-L4726) |
| Shader stages | Compute, ray tracing stages, vertex, fragment, geometry, tessellation control/evaluation, task, and mesh stage names appear in the case tables | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3990-L4005), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4319-L4336) |
| Matrix multiply operations | `matrixmul`, `matrixmuladd`, `matrixmuladdtranspose`, `matrixmul3`, `matrixmul2addmul2`, `matrixmul2add`, `matrixmultrainingbias` | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4197-L4205) |
| Matrix layouts and activations | Row-major, column-major, inferencing-optimal, training-optimal layouts; activation cases include `no_activation`, `actmul`, `actmax`, `actnonuniform`, `actdivergent`, `actsigmoid`, leaky-ReLU forms, `acthardgelu`, and load variants | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4279-L4299) |
| Training result-address modes | `resultuniform`, `resultunique`, and `resultclustered` | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4751-L4755) |
| Combination filters | The registration loops skip unsupported or high-count combinations, including workgroup storage outside compute, selected non-compute component counts, FP8 non-optimal matrix layouts, selected activation/type combinations, and selected divergent-control-flow combinations | [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4029-L4130), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4379-L4565) |

## Support Requirements

The shared support check requires Vulkan 1.1 [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L310-L315). For cooperative-vector cases it requires the `cooperativeVector` feature, checks the requested component count against `maxCooperativeVectorComponents`, queries `VkCooperativeVectorPropertiesNV`, and validates the requested type combination against advertised properties [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L317-L327), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L406-L483). For long-vector cases it requires `longVector` and checks `maxVectorComponents` [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L329-L339). Additional gates cover shader 64-bit indexing, ray tracing and acceleration-structure support for ray tracing stages, mesh/task shader support, variable pointers, buffer device address, shader float16, and cooperative-vector training accumulation properties [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L341-L403).

## Verification Methods

The tests generate GLSL for the selected stage, enabling either `GL_NV_cooperative_vector` or `GL_EXT_long_vector` and using stage-specific source wrappers [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L564-L586), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1593-L1751). The execution path allocates input, matrix/bias, output, and address buffers; converts optimal matrix layouts with `vkConvertCooperativeVectorMatrixNV` or `cmdConvertCooperativeVectorMatrixNV`; dispatches compute, ray tracing, graphics, or mesh work; then invalidates the output allocation [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1796-L2343), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2367-L2789). Verification compares the GPU output against CPU references for floating-point scalar/vector operations, integer operations, matrix multiply networks, reduce-sum, and outer-product cases [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2791-L3132), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3133-L3441), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3444-L3877).

## Test Principles

The file stresses the same cooperative-vector operations across storage classes, vector sizes, component types, and shader stages while pruning combinations explicitly in source to control test count and avoid unsupported mixes [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4007-L4181), [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4338-L4622). Matrix tests exercise both arithmetic semantics and layout conversion paths by converting matrices before shader execution when optimal layouts are involved [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2248-L2343).

## Notes

The inspected API test plan provides general Vulkan CTS framework context but no cooperative-vector-specific test-family breakdown [apitests.adoc](../../../../../doc/testspecs/VK/apitests.adoc#L8-L13).