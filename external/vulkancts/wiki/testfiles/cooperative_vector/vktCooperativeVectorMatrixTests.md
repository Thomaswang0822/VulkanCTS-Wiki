# vktCooperativeVectorMatrixTests

This file registers and implements the `layoutconvert` and `typeconvert` child groups under `cooperative_vector`. The category dispatcher appends both factories after the basic, long-vector, matrix-multiply, and training groups [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L44-L49). The file contains separate test-case classes for matrix layout conversion and matrix component-type conversion [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L66-L117), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L500-L551).

## Source Files

| Role | Link |
|------|------|
| Registering implementation | [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp) |
| Factory declarations | [vktCooperativeVectorMatrixTests.hpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.hpp#L34-L35) |
| Category dispatcher | [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L48-L49) |
| Component and data helpers | [vktCooperativeVectorUtils.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorUtils.cpp#L34-L220) |

## Registration Hierarchy

```text
cooperative_vector
├── layoutconvert
└── typeconvert
```

## Test Families

### layoutconvert — Matrix layout conversion chains

The dispatcher appends `createCooperativeVectorMatrixLayoutTests(testCtx)` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L48-L48), and the factory constructs the registered group name `layoutconvert` [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L424-L428). It nests host/device conversion mode, matrix component type, first destination layout, and second destination layout [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L429-L448), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L450-L493). FP8 layout-conversion combinations are filtered when either intermediate layout is row-major or column-major because the source comment states FP8 can only be written in optimal layout [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L465-L475).

### typeconvert — Matrix component-type conversion through optimal layout

The dispatcher appends `createCooperativeVectorMatrixTypeConversionTests(testCtx)` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L49-L49), and the factory constructs the registered group name `typeconvert` [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L844-L848). It nests host/device conversion mode and explicit source/destination component-type pairs such as `float32tofloat16`, `float32tofloate4m3`, `float16tofloate5m2`, and FP8-to-FP16/self conversions [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L849-L869), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L871-L885).

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Conversion execution mode | `device` and `host` for both layout and type conversion | [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L445-L448), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L866-L869) |
| Layout-conversion matrix types | `float32`, `float16`, `uint8`, `sint8`, `floate4m3`, `floate5m2` | [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L429-L436) |
| Layout-conversion layouts | `rowMajor`, `colMajor`, `inferencingOptimal`, `trainingOptimal` | [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L438-L443) |
| Layout-conversion matrix extents | The test iterates `numRows` and `numColumns` from 1 through 32 | [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L224-L227) |
| Type-conversion pairs | Float32/float16/FP8 conversion pairs listed in `dtCases` | [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L849-L864) |
| Type-conversion element count | 32-bit sources use `2 << 16` elements; 16-bit and 8-bit sources use `1 << (8 * srcElementSize)` elements | [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L619-L637) |

## Support / Feature Requirements

Both conversion families require Vulkan 1.1 and the `cooperativeVector` feature [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L117-L127), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L551-L561). Both query `VkCooperativeVectorPropertiesNV` and require a nonzero property count [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L129-L147), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L563-L580). Layout conversion accepts a case when the matrix interpretation is advertised, with a special allowance for `VK_COMPONENT_TYPE_FLOAT32_NV` [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L148-L158). Type conversion requires both source and destination matrix interpretations to be supported, again allowing float32 as a source-side special case [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L582-L599).

## Verification Methods

Layout-conversion tests allocate one buffer, initialize a row-major source matrix, then convert through two selected layouts and back to row-major using host calls or device commands [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L178-L207), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L224-L339). The verification reads row-major and column-major intermediate outputs when those layouts are present and compares each element against the original source value [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L341-L411).

Type-conversion tests construct a 1-by-N row-major source matrix covering deterministic bit patterns for 32-bit, 16-bit, or 8-bit source sizes [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L606-L637), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L697-L721). They convert row-major input to inferencing-optimal layout, then convert back to row-major with an FP16 or FP32 readable destination type [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L727-L809). Verification compares each output element with a CPU reference produced by quantizing the source to the requested destination component type, treating matching NaN values as acceptable [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L819-L839).

## Test Principles

The layout tests validate that repeated conversions preserve row/column-major readable matrix values across host and device execution paths [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L165-L168), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L297-L330). The type tests validate conversion semantics for all enumerated source values for 8-bit and 16-bit sources and a deterministic/randomized 32-bit source set [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L606-L609), [vktCooperativeVectorMatrixTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorMatrixTests.cpp#L697-L721).

## Notes

