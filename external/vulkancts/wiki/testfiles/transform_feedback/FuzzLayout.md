## Overview

**Core question:** Does transform feedback preserve generated interface-block values at the layout computed for each case?

- `vktTransformFeedbackFuzzLayoutTests.cpp` registers the `transform_feedback.fuzz` test family and builds deterministic and seeded-random interface-block cases.
- The cases cover basic types, arrays, structures, nested aggregates, interface-block instance arrays, multiple blocks, multiple capture buffers, and vertex or geometry execution.
- Each case computes a reference layout and values, captures one drawn point, and compares the host-visible transform-feedback bytes with that reference.
- This page explains the layout axes, generated shader path, runtime capture, failure diagnostics, and pruning rules. The old navigation page remains preserved as `vktTransformFeedbackFuzzLayoutTests.md`.

## Background Knowledge

- **Transform-feedback packing:** The last pre-rasterization shader stage can write outputs decorated with `XfbBuffer`, `Offset`, and `XfbStride` into bound transform-feedback buffers. Arrays and structures expand in declaration order, vectors write their components in order, and matrices write column vectors. See [Transform Feedback](../../../../../external/vulkan-docs/src/chapters/vertexpostproc.adoc#vertexpostproc-transform-feedback).
- **Interface-block aggregates:** A GLSL output interface block can contain basic values, arrays, and named structures. An instance array creates repeated block instances. The test must keep the shader declaration, the host reference layout, and the transform-feedback buffer regions consistent.

## Registration Hierarchy

```text
transform_feedback.fuzz
├── 2_level_array
├── 2_level_struct_array
├── 3_level_array
├── instance_array_basic_type
├── multi_basic_types
├── multi_nested_struct
├── random_geometry
├── random_vertex
├── single_basic_array
├── single_basic_type
├── single_nested_struct
├── single_nested_struct_array
├── single_struct
├── single_struct_array
└── various_buffers
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Deterministic family | `2_level_array`, `3_level_array`, `2_level_struct_array`, `single_basic_type`, `single_basic_array`, `single_struct`, `single_struct_array`, `single_nested_struct`, `single_nested_struct_array`, `instance_array_basic_type`, `multi_basic_types`, `multi_nested_struct`, `various_buffers` | Selects a fixed aggregate shape or buffer arrangement | [`InterfaceBlockTests::init()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L397-L672) |
| Basic type | `float`, `vec2`...`vec4`, `int`, `ivec2`...`ivec4`, `uint`, `uvec2`...`uvec4`, float matrices, double and double matrices | Changes scalar width, vector component count, or matrix column layout | [`basicTypes[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L374-L384) |
| Precision | `lowp`, `mediump`, `highp` for types that support precision modifiers | Changes the generated GLSL precision qualifier | [`precisionFlags[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L386-L394) |
| Stage | `vertex`, `geometry` | Selects the stage that writes the interface block | [`createBlockBasicTypeCases()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L67-L77) |
| Aggregate shape | Array lengths `2` or `3` in deterministic families; nested structure combinations; instance arrays of `2` or `3` | Changes recursive layout traversal and repeated storage | [`Block2LevelStructArrayCase`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L311-L334) |
| Capture buffers | `000`, `010`, `100`, `110` | Routes three blocks to transform-feedback buffers 0 or 1 | [`xfbBufferNumbers[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L632-L671) |
| Random feature set | `scalar_types`, `vector_types`, `basic_types`, `basic_arrays`, `basic_instance_arrays`, `nested_structs`, `nested_structs_arrays`, `nested_structs_instance_arrays`, `nested_structs_arrays_instance_arrays`, `all_instance_array`, `all_unordered_and_instance_array`, `all_missing`, `all_unordered_and_missing` | Enables selected generated type and layout features | [`random` group construction](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L674-L738) |
| Random case count | `50` for the first nine random groups; `100` for the four `all_*` groups | Bounds the generated set for each vertex or geometry feature set | [`numCases` and `createRandomCaseGroup()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L685-L737) |

## Behavior Parameters

The primary behavioral axis is the registered test family. It selects which interface-layout rule the case stresses; type, stage, and generated seed are subordinate dimensions.

### 2_level_array: Two nested array levels

The case captures a basic type through two arrays of length two. It checks recursive array expansion and the resulting element strides in both vertex and geometry stages.

### 3_level_array: Three nested array levels

The case adds a third length-two array around the basic type. It stresses repeated array indexing and the accumulated transform-feedback size.

### 2_level_struct_array: Arrays of structures

The case contains a two-level array of a structure with a `u` member, a matrix member, and a vector member. The `std` variant has no block instance array; `instance_array` repeats the block twice.

### single_basic_type: One basic interface value

The case uses the complete basic-type list. Types with precision support appear below `lowp`, `mediump`, and `highp`; other types appear directly under the family. This is the smallest layout path and the representative shader below uses its `lowp.float.vertex` case.

### single_basic_array: Array of three basic values

The case captures three elements of each basic type. The host expects one interface entry with an array stride and validates every element.

### single_struct: One structure

The structure contains an unused `int vec3`, an array of two `float vec3` values, and a `float mat3`. The unused first member remains in the declaration but the test excludes it from expected-value generation and comparison.

### single_struct_array: Structure array with surrounding members

The block contains a `uint`, an array of two structures, and a `float vec4`. The `instance_array` variant repeats the block twice.

### single_nested_struct: Structure containing another structure

The case combines structures, a matrix array, unused members, and a block-level `uint` and `vec2`. It checks recursive member traversal while preserving alignment at aggregate boundaries.

### single_nested_struct_array: Nested structures and arrays

The case combines a two-element float array inside `S` with a two-element array of `T`, where `T` contains a matrix and an array of `S`. It also tests optional block instance arrays.

### instance_array_basic_type: Repeated basic-type blocks

Each basic type is placed in a block instance array of size three. The layout code maps each instance to successive transform-feedback buffer bindings and records the per-instance stride.

### multi_basic_types: Two blocks of basic values

`BlockA` and `BlockB` contain different scalar, vector, and matrix members. Both blocks use the same transform-feedback layout flags, with standard and two-instance variants in both stages.

### multi_nested_struct: Two blocks with nested structures

Two blocks use independently defined nested structures. The case checks that layout traversal and capture offsets remain correct across block boundaries and instance repetitions.

### various_buffers: Multiple blocks routed to buffer numbers

Three blocks use the `000`, `010`, `100`, and `110` buffer assignments. The cases include standard and two-instance variants, exercising buffer routing while the host binds one Vulkan buffer over multiple logical ranges.

### random_vertex: Seeded generated vertex layouts

Each case generates one to three blocks, one to three members per block, optional instance arrays, and feature-controlled types, arrays, or structures. The vertex shader writes the generated active members.

### random_geometry: Seeded generated geometry layouts

The layout generation matches `random_vertex`, but a pass-through vertex shader feeds a point-list geometry shader. The geometry shader writes the generated block values and emits one point.

## Shader Analysis

The generated shader is part of the tested behavior: its interface declarations carry the layout metadata that the host model predicts. One walkthrough covers the smallest deterministic vertex path; geometry cases use the same assignment generator with a different stage wrapper.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.transform_feedback.fuzz.single_basic_type.lowp.float.vertex
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `single_basic_type` | Selects one basic output value instead of an aggregate |
| `lowp.float.vertex` | Emits a low-precision float from the vertex stage |
| `xfb_buffer = 0`, `xfb_offset = 0`, `xfb_stride = 4` | Places the four-byte captured value at the beginning of buffer 0 |

#### Purpose

The shader writes one generated float through an output interface block. Transform feedback must capture that value at the host-computed offset.

#### Structural Design

| Phase | Generated shader operation | Captured consequence |
|-------|-----------------------------|----------------------|
| Declaration | Define `Block` as an output interface block with one `float var` | The block carries location and transform-feedback layout metadata |
| Assignment | Set `block.var` to the generated reference value | The captured component has a known expected value |
| Capture | Draw one point while transform feedback is active | Buffer 0 receives one four-byte value |

#### Shader Code

```glsl
#version 450

layout(location = 0, xfb_buffer = 0, xfb_offset = 0, xfb_stride = 4) out Block
{
    lowp float var;
};

void main (void)
{
    var = 31.0f;
}
```

#### Additional Info

- The `31.0f` literal is the value produced by the fixed `generateValues(..., 1)` reference path for this representative scalar case; the registration name selects the type and stage, not the value.
- The source generator emits a GLSL 4.50 vertex program and adds the `vert` collection entry in `InterfaceBlockCase::initPrograms()`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Basic type | Changes the declared type and generated constructor or component values; matrices are assigned in column-major source order | [`generateValueSrc()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1237-L1305) |
| Aggregate shape | Adds array brackets, structure declarations, and recursive member assignments | [`generateDeclaration()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1002-L1100) |
| Stage | Geometry cases use a pass-through vertex shader plus `layout(points) in` and `layout(points, max_vertices = 1) out`, then emit one point | [`generateTestShader()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1562-L1618) |
| Random feature set | Enables vectors, matrices, doubles, arrays, structures, instance arrays, missing or unassigned members, and out-of-order offsets | [`FeatureBits`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackRandomLayoutCase.hpp#L40-L54) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: vert
- Target SPIRV version: spirv1.0

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 15
; Schema: 0
               OpCapability Shader
               OpCapability TransformFeedback
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_
               OpExecutionMode %main Xfb
               OpSource GLSL 450
               OpName %main "main"
               OpName %Block "Block"
               OpMemberName %Block 0 "var"
               OpName %_ ""
               OpDecorate %Block Block
               OpMemberDecorate %Block 0 RelaxedPrecision
               OpMemberDecorate %Block 0 Offset 0
               OpDecorate %_ Location 0
               OpDecorate %_ XfbBuffer 0
               OpDecorate %_ XfbStride 4
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
      %Block = OpTypeStruct %float
%_ptr_Output_Block = OpTypePointer Output %Block
          %_ = OpVariable %_ptr_Output_Block Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
   %float_31 = OpConstant %float 31
%_ptr_Output_float = OpTypePointer Output %float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %14 = OpAccessChain %_ptr_Output_float %_ %int_0
               OpStore %14 %float_31
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `delayedInit()` computes the reference interface layout, allocates one contiguous host-side byte array, and derives per-binding offsets and sizes. It generates values with seed `1`, then generates the vertex or geometry shader source.
- `iterate()` creates shader modules, a no-attachment render pass and framebuffer, a point-list graphics pipeline, a resettable command pool, and a primary command buffer. The render extent is `256 x 256`.
- The test creates one host-visible buffer with `TRANSFER_SRC` and `TRANSFORM_FEEDBACK_BUFFER` usage. It binds the same buffer handle for each logical transform-feedback binding, using the computed offsets and sizes.
- The command buffer begins transform feedback, draws one vertex, ends transform feedback, and inserts a barrier from `TRANSFORM_FEEDBACK` writes to host reads. The host waits for submission, invalidates the mapped range, and scans the captured bytes.
- The checker compares integers exactly. It compares floats and doubles with an absolute tolerance of `0.05`. It ignores bytes belonging only to missing or unassigned fields and fails on the first active mismatch.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2_level_array` | Incorrect nested-array declaration, offset, array stride, or captured component order |
| `3_level_array` | Incorrect three-level array expansion, alignment, or matrix/array packing |
| `2_level_struct_array` | Incorrect structure-array or interface-block instance-array layout |
| `single_basic_type` | Incorrect scalar/vector/matrix type, precision declaration, or basic transform-feedback packing |
| `single_basic_array` | Incorrect array element offsets, stride, or capture order |
| `single_struct` | Incorrect structure-member traversal, alignment, or inactive-member handling |
| `single_struct_array` | Incorrect structure-array packing or block instance handling |
| `single_nested_struct` | Incorrect nested-structure traversal or alignment |
| `single_nested_struct_array` | Incorrect combined nested-structure and array layout |
| `instance_array_basic_type` | Incorrect interface-block instance-array expansion or per-instance transform-feedback buffer placement |
| `multi_basic_types` | Incorrect layout when multiple output blocks share a capture configuration |
| `multi_nested_struct` | Incorrect layout across multiple blocks containing nested structures |
| `various_buffers` | Incorrect `xfb_buffer` routing or per-buffer stride/offset handling |
| `random_vertex` | Incorrect handling of a generated vertex-stage layout combination |
| `random_geometry` | Incorrect handling of a generated geometry-stage layout combination |

### Cause Analysis

#### Layout declaration or packing mismatch

**Possible failure symptoms:** The checker reports a mismatch at an interface name and byte offset, with expected and retrieved scalar values differing. Array, matrix, or structure indices identify the affected aggregate position.

**Possible implementation causes:** The shader compiler or driver may interpret an `xfb_offset`, `xfb_stride`, aggregate alignment, matrix column stride, or `XfbBuffer` assignment differently from the source-defined reference model. The Vulkan specification requires component alignment and describes tight aggregate packing, so the failure identifies a disagreement in the declaration-to-buffer mapping.

#### Missing or unassigned member handling

**Possible failure symptoms:** A case with holes or inactive members fails only when an active member is compared, or the diagnostic shows unexpected bytes in a region the test considers active.

**Possible implementation causes:** The generated shader may omit a `FIELD_MISSING` member or leave a `FIELD_UNASSIGNED` member unwritten as intended, while the host mask may disagree with the emitted declaration or assignment set. The Vulkan specification leaves components of assigned outputs that the shader did not write undefined and leaves unrelated reserved storage unmodified; source-level investigation is needed for a more specific cause.

#### Stage execution or capture failure

**Possible failure symptoms:** All active values from a vertex or geometry case mismatch, or the result remains at the zeroed buffer contents.

**Possible implementation causes:** The relevant pre-rasterization stage may fail to execute the generated assignments, the geometry path may fail to emit its point, or transform feedback may not capture the declared outputs while active. The test's command sequence binds the buffers, begins capture, draws one point, ends capture, and synchronizes transform-feedback writes before host inspection.

#### Host reference or readback mismatch

**Possible failure symptoms:** The mismatch is consistent across active fields or appears after a successful draw, with offsets and expected bytes matching the test's logged layout.

**Possible implementation causes:** The host-side layout/value model, mapped-memory visibility, or readback interpretation may differ from the device result. The source uses a transform-feedback-to-host pipeline barrier and invalidates mapped memory before checking; a more specific implementation cause requires source-level investigation.

## Case Pruning

### Requirement-based pruning

- The test instance skips a case when `transformFeedback` is unavailable.
- It skips cases requiring more transform-feedback bindings than `maxTransformFeedbackBuffers` or more data than `maxTransformFeedbackBufferDataSize`.
- Vertex cases require `maxVertexOutputComponents` for the generated interface plus seven built-in components.
- Geometry cases require `geometryShader` and `maxGeometryOutputComponents` for the same component requirement.
- Layouts containing double-precision values require the core `shaderFloat64` feature.

These checks classify a case as unsupported on the current device; they do not indicate a failed layout result.

### Design-based pruning

- Deterministic families fix aggregate sizes to small values such as `2` or `3` so they isolate layout rules rather than create a large matrix.
- The random generator limits blocks to `1..3`, block and structure members to `1..3`, structure depth to `2`, array length to `1..4`, and instance-array length to `0..3`.
- Random member generation permits at most `numBlockMembers - 1` missing or unassigned members, retaining an active member for validation.
- The random feature groups deliberately separate scalar, vector, basic, array, structure, instance-array, missing-member, and out-of-order-offset coverage. Disabled features are excluded from each group's generator rather than pruned after execution.
- `FEATURE_ARRAYS_OF_ARRAYS` and `FEATURE_NESTED_STRUCTS` exist in the feature vocabulary, but the registered groups select the feature combinations shown above; the source does not register a separate nested-array-of-array group.

## Key Takeaways

- The test compares device-captured bytes with a host model built from the same aggregate hierarchy, offsets, strides, and active-member rules used to generate the shader.
- The deterministic families isolate specific layout shapes; `random_vertex` and `random_geometry` broaden the combinations while keeping seeds reproducible.
- A failure names the first active interface mismatch and records the layout and buffer ranges, which helps distinguish packing from stage, capture, and readback symptoms.
- Geometry cases change the execution wrapper, not the core layout walker: the generated interface assignments remain the behavior under test.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test-family registration | [`InterfaceBlockTests::init()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L372-L738) | Registers all deterministic and random groups |
| Deterministic case classes | [`BlockBasicTypeCase` and related classes](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L41-L334) | Define fixed interface-block shapes and sizes |
| Layout computation | [`computeXfbLayout()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L554-L912) | Computes alignment, offsets, strides, locations, and active entries |
| GLSL declarations | [`generateDeclaration()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1002-L1234) | Emits structures, blocks, qualifiers, and instance arrays |
| GLSL assignments | [`generateAssignment()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1237-L1559) | Emits active values and skips missing or unassigned fields |
| Program collection | [`InterfaceBlockCase::initPrograms()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L2020-L2028) | Registers generated vertex and optional geometry sources |
| Case preparation | [`InterfaceBlockCase::delayedInit()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L2036-L2112) | Builds reference storage, values, and shader source |
| Capture and synchronization | [`InterfaceBlockCaseInstance::iterate()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1788-L1860) | Runs the draw and makes capture data host-visible |
| Value validation | [`validateValue()` and `validateValues()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1863-L1999) | Compares values and formats diagnostics |
| Random generator | [`RandomInterfaceBlockCase`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackRandomLayoutCase.cpp#L56-L260) | Defines feature-controlled generation and bounds |
| Random feature vocabulary | [`FeatureBits`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackRandomLayoutCase.hpp#L40-L82) | Names the enabled layout features and generator limits |
| Transform-feedback specification | [Transform Feedback](../../../../../external/vulkan-docs/src/chapters/vertexpostproc.adoc#vertexpostproc-transform-feedback) | Defines capture, packing, stride, offsets, and buffer constraints |
| Shader-stage specification | [Shaders](../../../../../external/vulkan-docs/src/chapters/shaders.adoc#shaders) | Defines the generated vertex and geometry execution context |
| Legacy navigation page | [`vktTransformFeedbackFuzzLayoutTests.md`](vktTransformFeedbackFuzzLayoutTests.md) | Preserves the original source-navigation material |
