# vktShaderExpectAssumeTests.cpp

## Overview

[`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1) implements the GLSL `shader_expect_assume` group for `VK_KHR_shader_expect_assume`. The file comment identifies the target extension and SPIR-V operations, and the public factory returns a `shader_expect_assume` group through [`createShaderExpectAssumeTests()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1516-L1519).

The group is registered under the `glsl` category only for non-VulkanSC builds: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L116) includes the header, and [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287) adds `createShaderExpectAssumeTests()` inside `#ifndef CTS_USES_VULKANSC`.

## Role

Registration / dispatcher file and implementation-heavy test file. It defines the test parameters, per-case support checks, generated GLSL programs, compute and graphics execution paths, output validation, and the full registration matrix in one source file.

## Source Code

- Primary source: [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1)
- Header / factory declaration: [`vktShaderExpectAssumeTests.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.hpp#L23-L35)
- GLSL category registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1287)

## Registration Hierarchy

```text
glsl.shader_expect_assume
├── vertex
├── fragment
└── compute
```

## Test Families

### vertex — Graphics-pipeline vertex-shader execution

The `vertex` stage group is generated from the `VK_SHADER_STAGE_VERTEX_BIT` entry in the `stages[]` array and the stage-name mapping in [`addShaderExpectAssumeTests()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1416-L1455). Each stage group receives direct children named `expect` and `assume`, created before the parameter loop and attached to the stage group after cases are added at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1457-L1461) and [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1507-L1510).

Vertex cases compile the expect/assume operation into the vertex shader and pass a flat `uint value` to a simple fragment shader that writes `(gl_FragCoord.x, value)` into a `VK_FORMAT_R32G32_UINT` color attachment at [`addVertexTestShaders()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1231-L1321). The graphics path draws six vertices into a `kNumElements`-wide render area and copies the color image to the output buffer for host validation at [`render()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L752-L870).

### fragment — Graphics-pipeline fragment-shader execution

The `fragment` stage group is generated from `VK_SHADER_STAGE_FRAGMENT_BIT` by the same stage loop at [`addShaderExpectAssumeTests()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1418-L1455). It has the same direct `expect` and `assume` subgroups as the other stage groups, with cases dispatched into the correct subgroup according to `OpType` at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1492-L1502).

Fragment cases use a pass-through vertex shader and place the `SPV_KHR_expect_assume` intrinsic declarations plus the selected operation in the fragment shader at [`addFragmentTestShaders()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1324-L1409). The fragment shader writes `out_color.r = int(gl_FragCoord.x)` and `out_color.g` as the boolean verification value, which is later checked by the common host-side output comparison at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1385-L1404) and [`validateOutput()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L126-L137).

### compute — Compute-shader execution

The `compute` stage group is generated from `VK_SHADER_STAGE_COMPUTE_BIT` in the same stage array as the graphics stages at [`addShaderExpectAssumeTests()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1418-L1422). Compute execution is selected in [`iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L106-L123), which calls `dispatch()` for compute and `render()` for vertex or fragment cases.

Compute shaders declare the `SPV_KHR_expect_assume` intrinsics, use `local_size_x = ${TEST_ELEMENT_COUNT}`, and write `(gl_GlobalInvocationID.x, verification)` to the output storage buffer at [`addComputeTestShader()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1153-L1228). The dispatch path binds a compute pipeline and descriptor set, optionally pushes a true push-constant value, dispatches one workgroup, and inserts a shader-write-to-host-read barrier before host validation at [`dispatch()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L720-L750).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Operation subgroup | `expect` and `assume` are explicit child groups created for every stage at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1457-L1461). Cases are added to one of those groups by `OpType` at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1492-L1502). |
| Shader stage | `vertex`, `fragment`, and `compute` come from the three-entry `stages[]` array and stage-name mapping at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1418-L1455). |
| Base test names and data classes | The base `testParams[]` table includes `constant`, `specializationconstant`, `pushconstant`, storage-buffer bool/int8/int16/int32/int64 expect cases, and bool-only storage-buffer assume at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1424-L1442). |
| Data types | The source enum lists `Bool`, `Int8`, `Int16`, `Int32`, and `Int64` at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L75-L82), but the registration table uses integer types only for storage-buffer `expect` cases and uses bool for constants, specialization constants, push constants, and storage-buffer `assume` cases at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1424-L1442). |
| Vector width | The outer loop tries channel counts `1..4`, but channel counts above one are retained only for `OpType::Expect` with `DataClass::StorageBuffer`; those cases receive `_vec2`, `_vec3`, or `_vec4` suffixes at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1482). |
| Wrong expectation variants | The expectation-state loop generates `wrongExpected=false` and `wrongExpected=true`, but wrong-expected cases are retained only for storage-buffer `expect` cases and receive `_wrong_expected` at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1488). |
| Input variable source | Shader generation selects ordinary bool variables, specialization constants, push constants, or storage-buffer indexing based on `DataClass` at [`initPrograms()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L996-L1080). |
| Element count and formats | `kNumElements` is `32`, and graphics output uses `VK_FORMAT_R32G32_UINT` at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L57-L60). The output buffer stores two `uint32_t` words per element at [`generateStorageBuffers()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L518-L523). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| `VK_KHR_shader_expect_assume` | Every case calls `context.requireDeviceFunctionality("VK_KHR_shader_expect_assume")` in [`ShaderExpectAssumeCase::checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1108-L1111). |
| Non-VulkanSC registration | The GLSL category adds the group inside `#ifndef CTS_USES_VULKANSC` at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287). |
| 64-bit integer cases | `DataType::Int64` cases require `features.shaderInt64` at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1117-L1121). |
| 16-bit integer cases | `DataType::Int16` cases require `VK_KHR_16bit_storage`, `features.shaderInt16`, `storageBuffer16BitAccess`, and `uniformAndStorageBuffer16BitAccess` at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1122-L1135). |
| 8-bit integer cases | `DataType::Int8` cases require `VK_KHR_shader_float16_int8`, `VK_KHR_8bit_storage`, `shaderInt8`, `storageBuffer8BitAccess`, and `uniformAndStorageBuffer8BitAccess` at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1136-L1149). |
| Push constants and specialization constants | The file uses push constants or specialization info according to the data class: pipeline layouts include push-constant ranges for push-constant cases, and specialization info is attached for specialization-constant stages at [`generateGraphicsPipeline()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L274-L282) and [`generateComputePipeline()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L649-L665). |

## Verification Methods

- Test execution selects `dispatch()` for compute and `render()` for graphics, invalidates the host-visible output allocation, then calls `validateOutput()` at [`iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L106-L123).
- Host validation checks all `32` output elements. Each element must contain its element index in the first `uint32_t` and `1` in the second `uint32_t`; otherwise the case fails with `Result comparison failed` at [`validateOutput()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L126-L137).
- `expect` shaders initialize a `control` value to the wrong value, call `${TEST_OPERATOR}(${VARNAME}, ${EXPECTEDVALUE})`, and set the verification output according to whether `control` matches the expected value for normal cases or the wrong value for wrong-expectation cases at [`addComputeTestShader()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1194-L1223), [`addVertexTestShaders()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1270-L1300), and [`addFragmentTestShaders()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1375-L1404).
- `assume` shaders call `assumeTrueKHR` with the selected operand and write a boolean result derived from the operand value; for bool-only assume cases with no explicit expected-value parameter, the generated code writes `uint(${VARNAME})` at [`addComputeTestShader()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1190-L1209), [`addVertexTestShaders()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1266-L1285), and [`addFragmentTestShaders()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1371-L1389).
- Storage-buffer input data is initialized per element and per vector channel. Wrong-expectation variants deliberately offset the input values or set bool values to false at [`generateStorageBuffers()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L545-L580).
- Graphics cases render to a `VK_FORMAT_R32G32_UINT` image sized `32 x 1`, then copy that image to the same output buffer layout validated by the host at [`generateAttachments()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L210-L243) and [`render()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L858-L870).

## Test Principles

- The registration matrix is stage-first: `vertex`, `fragment`, and `compute` are the direct children of `glsl.shader_expect_assume`, and each direct child contains `expect` and `assume` subgroups populated by the shared parameter loop at [`addShaderExpectAssumeTests()`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1416-L1511).
- The source intentionally narrows non-scalar, wrong-expectation, and integer coverage to storage-buffer `expect` cases through the `channelCount > 1 || wrongExpected` filter and the `testParams[]` table at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1424-L1442) and [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1463-L1488).
- The same host-side oracle is used for compute, vertex, and fragment paths: shader-generated output must form `(index, 1)` pairs for every element, while stage-specific code only changes how those pairs are produced and transferred to the output buffer.
- The GLSL snippets expose the target SPIR-V intrinsics via `GL_EXT_spirv_intrinsics` and `spirv_instruction` declarations for `assumeTrueKHR` and `expectKHR` in the generated compute, vertex, and fragment shader sources at [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1157-L1164), [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1235-L1241), and [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1341-L1347).

## Notes / Uncertainties

- No separate helper file specific to `shader_expect_assume` was found in the inspected source; shared executor headers are included, but the registration and case implementation are local to [`vktShaderExpectAssumeTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L26-L28).
