## Overview

[`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L20-L28) implements the `glsl.shader_expect_assume` group for `VK_KHR_shader_expect_assume`. It generates GLSL using the `SPV_KHR_expect_assume` intrinsics, runs each case through a vertex, fragment, or compute pipeline, and checks a two-word result for each of 32 elements. The public factory is [`createShaderExpectAssumeTests()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1516-L1519).

The group is added to the GLSL package only in non-Vulkan-SC builds ([registration](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287)). This page describes source-defined coverage and behavior; it does not claim that the cases were run on the current host.

## Source Code

- Implementation, generator, execution, and factory: [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L20-L28)
- Public declaration: [`vktShaderExpectAssumeTests.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.hpp#L23-L35)
- GLSL-package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1287)

## Registration Hierarchy

```text
glsl.shader_expect_assume
├── vertex
├── fragment
└── compute
```

The factory creates the three stage groups and their two direct operation groups in [`addShaderExpectAssumeTests()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1416-L1511). Each stage has 43 `expect` leaves and 4 `assume` leaves, for 47 leaves per stage. The leaf names are generated from the parameter table and receive `_vec2`–`_vec4` and/or `_wrong_expected` suffixes where applicable ([parameter loop](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1424-L1503)).

## Test Families

### `expect`

The `expect` cases exercise `expectKHR` with an operand and expected value. The generated shader initializes `control` to the wrong value, invokes the intrinsic, and selects the expected or wrong value according to the intrinsic result ([compute](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1190-L1203), [vertex](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1265-L1279), [fragment](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1371-L1384)). Normal cases validate the expected branch; `_wrong_expected` cases deliberately validate the alternate branch.

The scalar base cases are:

- `constant`
- `specializationconstant`
- `pushconstant`
- `storagebuffer_bool`
- `storagebuffer_int8`
- `storagebuffer_int16`
- `storagebuffer_int32`
- `storagebuffer_int64`

These entries are defined in the source table ([`testParams[]`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1424-L1436)). Storage-buffer expect cases additionally generate vector widths 2, 3, and 4, and all five storage-buffer expect types additionally generate wrong-expectation variants. The registration filter intentionally excludes vectors and wrong-expectation variants for non-storage-buffer or non-`expect` entries ([filter and suffixes](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1488)).

### `assume`

The `assume` cases exercise `assumeTrueKHR` and report the selected operand or its comparison result. Their scalar base entries are `constant`, `specializationconstant`, `pushconstant`, and `storagebuffer`; all use boolean data ([source table](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1437-L1442)). The shader templates emit the intrinsic before writing the verification value ([compute](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1190-L1215), [vertex](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1265-L1292), [fragment](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1371-L1395)).

### Stage execution

- `vertex` places the operation in the vertex shader, passes a flat `uint` to a simple fragment shader, and renders six vertices ([shader generation](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1231-L1321), [draw path](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L820-L865)).
- `fragment` uses a pass-through vertex shader and places the operation in the fragment shader; the fragment writes its x coordinate and verification value ([shader generation](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1324-L1409)).
- `compute` emits a one-workgroup shader with `local_size_x = 32`, writes directly to a storage buffer, and dispatches once ([shader generation](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1153-L1229), [dispatch](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L720-L750)).

All three templates enable `GL_EXT_spirv_intrinsics` and declare the `SPV_KHR_expect_assume` instructions ([compute declarations](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1157-L1164), [vertex declarations](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1235-L1241), [fragment declarations](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1341-L1347)).

## Parameter Dimensions

| Dimension | Source-defined values and restrictions |
|---|---|
| Stage | `vertex`, `fragment`, and `compute` ([stage array](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1418-L1455)). |
| Operation | `expect` and `assume`; each stage receives both direct child groups ([group creation](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1457-L1461)). |
| Data class | Constant, specialization constant, push constant, or storage buffer ([enum and parameter table](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L67-L73), [table](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1424-L1442)). |
| Data type | `bool` for all non-integer entries; storage-buffer `expect` also uses `int8`, `int16`, `int32`, and `int64` ([types](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L75-L82)). |
| Channel count | The loop considers 1–4, but counts above 1 are retained only for storage-buffer `expect`; those leaves receive `_vec2`, `_vec3`, or `_vec4` ([selection](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1482)). |
| Expectation state | `wrongExpected` is false and true. The true state is retained only for storage-buffer `expect` and receives `_wrong_expected` ([selection](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1488)). |
| Operand source | Constant, specialization constant, push constant, or stage-indexed storage-buffer element. Storage-buffer indexing uses `gl_GlobalInvocationID.x`, `gl_VertexIndex`, or `uint(gl_FragCoord.x)` ([operand setup](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L996-L1077)). |

## Support / Feature Requirements

| Requirement | Scope and behavior |
|---|---|
| `VK_KHR_shader_expect_assume` | Required by every case in [`checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1108-L1111). |
| 64-bit integer support | `shaderInt64` is required for `int64` cases ([check](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1117-L1121)). |
| 16-bit integer/storage support | `VK_KHR_16bit_storage`, `shaderInt16`, `storageBuffer16BitAccess`, and `uniformAndStorageBuffer16BitAccess` are required for `int16` cases ([check](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1122-L1135)). |
| 8-bit integer/storage support | `VK_KHR_shader_float16_int8`, `VK_KHR_8bit_storage`, `shaderInt8`, `storageBuffer8BitAccess`, and `uniformAndStorageBuffer8BitAccess` are required for `int8` cases ([check](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1136-L1149)). |
| Vulkan SC | The entire group is excluded at package registration by `#ifndef CTS_USES_VULKANSC` ([registration guard](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287)). |

A missing capability produces a not-supported result through the support checks; it is distinct from a shader, pipeline, or result-comparison failure.

## Verification Methods

`iterate()` dispatches compute cases or renders graphics cases, invalidates the output allocation, and calls the common validator ([iteration](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L106-L123)). The validator checks every element for the pair `(index, 1)` and returns `Result comparison failed` on the first mismatch ([validator](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L126-L137)).

- Compute writes `gl_GlobalInvocationID.x` and the verification result to `uvec2 outputBuffer[]` ([output writes](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1204-L1228)).
- Vertex writes the verification value to a flat output; the fragment stage adds `gl_FragCoord.x`, producing the same pair after rendering ([vertex output](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1281-L1305), [graphics fragment](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1311-L1321)).
- Fragment writes `int(gl_FragCoord.x)` and the verification value directly to its `uvec2` color output ([fragment output](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1385-L1409)).
- Graphics renders a `32 × 1` area to `VK_FORMAT_R32G32_UINT` and copies the image to the output buffer ([constants](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L57-L60), [render/copy](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L752-L870)).

A passing result establishes agreement among generated GLSL, intrinsic compilation/execution, the selected pipeline/resource path, synchronization, and the host oracle. It does not isolate one layer; conversely, a failed comparison does not by itself identify whether the intrinsic, generated shader, pipeline, or data transfer caused the mismatch.

## Test Principles

- Coverage is stage-first, with the same parameter-generation rules applied independently to vertex, fragment, and compute cases.
- The generator deliberately avoids a full Cartesian product: vector and wrong-expectation variants are limited to storage-buffer `expect` cases, while `assume` remains boolean and scalar.
- Constants, specialization constants, and push constants test operand sourcing separately from storage-buffer indexing; storage-buffer integer cases add scalar and vector data-layout coverage.
- The common `(index, 1)` oracle makes the stage paths comparable while preserving their different shader and transfer mechanisms.
