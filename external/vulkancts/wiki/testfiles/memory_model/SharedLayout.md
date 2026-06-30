## Overview

**Core question:** Can generated GLSL `shared` objects preserve shader-written values across write, barrier, read, and compare
steps for scalar, vector, matrix, array, nested-struct, 16-bit, and 8-bit layouts?

- This page covers the delegated `memory_model.shared` test family registered by
  [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp) and executed through
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp).
- The test family generates compute shaders that declare GLSL `shared` objects, write generated values into their fields, run
  workgroup-memory barriers, read the fields back, and report success through a single storage-buffer counter.
- The practical focus is shared-memory layout correctness: scalar, vector, matrix, array, array-of-array, nested-struct, 16-bit,
  and 8-bit fields must remain addressable and comparable after being written in `shared` memory.
- The host does not create buffers for the generated shared objects. The only host-visible result resource is the `passed`
  storage buffer used to summarize shader-side checks.

## Background Knowledge

- **GLSL `shared` memory.** A `shared` variable is workgroup shared memory: each compute workgroup has its own instance, and the
  memory is visible to invocations in that workgroup, not to all workgroups or the whole device.
- **Compute workgroup.** A compute workgroup is the execution scope that owns a `shared` variable; workgroup-local memory is
  separate from descriptor-backed buffer or image resources.
- **Composite shader data.** Structs, arrays, vectors, and matrices create nested member, index, and component paths that shader
  code can address individually.

## Registration Hierarchy

```text
memory_model.shared
├── scalar_types
├── vector_types
├── basic_types
├── basic_arrays
├── arrays_of_arrays
├── nested_structs
├── nested_structs_arrays
├── 16bit
└── 8bit
```

The first seven entries are base intermediate layout nodes. The `16bit` and `8bit` entries are intermediate nodes,
each repeating those same seven layout nodes with additional type candidates enabled
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L295-L327).

| Area | Layout nodes | Test cases per node | Total test cases | Meaning |
|------|--------------|---------------------|------------------|---------|
| base `memory_model.shared` | 7 | 10 | 70 | 32-bit and boolean scalar/vector/matrix/layout nodes. |
| `memory_model.shared.16bit` | 7 | 10 | 70 | Same layout shapes with 16-bit type candidates allowed. |
| `memory_model.shared.8bit` | 7 | 10 | 70 | Same layout shapes with 8-bit type candidates allowed. |
| Total | 21 | 10 | 210 | Deterministic randomized layout test cases across all intermediate nodes. |

## Intermediate Nodes

### scalar_types — Scalar shared-memory layouts

`scalar_types` generates cases whose checked members come from scalar type choices plus intentionally unused variables and
members. Its role is to establish the simplest shared-memory object shapes before vectors, matrices, arrays, or nested structs
are added [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L310-L314).

### vector_types — Vector field layouts

`vector_types` enables vector type candidates. These cases stress component addressing and vector storage in shared-memory
objects while keeping the overall object structure comparatively simple
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L310-L314).

### basic_types — Scalars, vectors, and matrices

`basic_types` enables the `FEATURE_VECTORS | FEATURE_MATRICES` set. It extends the scalar/vector coverage to matrix-shaped leaf
values, so the generated comparisons must handle matrix column/vector decomposition correctly
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L292-L314).

### basic_arrays — Arrays of basic types

`basic_arrays` adds array generation to the basic scalar/vector/matrix type set. The important change is that the flattening and
write/compare generation must step through array elements rather than only standalone fields
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L315-L316).

### arrays_of_arrays — Nested array layouts

`arrays_of_arrays` enables both arrays and arrays-of-arrays. These cases stress recursive indexing and flattening through nested
array levels [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L317-L320).

### nested_structs — Nested structure layouts

`nested_structs` enables generated struct types inside shared-memory objects. These cases test whether nested member paths remain
correct when the shader writes and compares individual leaves
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L321-L322).

### nested_structs_arrays — Structs combined with arrays

`nested_structs_arrays` combines basic types, structs, arrays, and arrays-of-arrays. It is the most structurally complex base
intermediate layout node because a check path may cross both struct-member and array-index boundaries
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L323-L326).

### 16bit — 16-bit intermediate variants of the seven layout nodes

`16bit` is an intermediate node that repeats the seven layout nodes with `FEATURE_16BIT_TYPES` enabled. The
same structural shapes are used, but type generation may choose `uint16`, `int16`, `float16`, and 16-bit vector forms
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L195-L218).

### 8bit — 8-bit intermediate variants of the seven layout nodes

`8bit` is an intermediate node that repeats the seven layout nodes with `FEATURE_8BIT_TYPES` enabled. These
cases add `uint8`, `int8`, and 8-bit vector candidates, then rely on promotion-aware generated comparisons
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L219-L233).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Layout shape node | `scalar_types`, `vector_types`, `basic_types`, `basic_arrays`, `arrays_of_arrays`, `nested_structs`, `nested_structs_arrays` | Controls whether generated shared-memory fields are simple leaves, vectors/matrices, arrays, nested arrays, structs, or combinations. | [registration loop](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L310-L326) |
| Type-width branch | base, `16bit`, `8bit` | Repeats the same seven layout nodes with base types only, 16-bit candidates, or 8-bit candidates. | [three-pass node loop](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L295-L327) |
| Test cases per layout node | `10`, named `0` through `9` | Provides deterministic random coverage within each layout node. | [createRandomCaseGroup()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L94-L105) |
| Base seeds | `0`, `25`, `50`, `50`, `950`, `100`, `150`, plus command-line base seed | Keeps random generation deterministic while giving each layout node a different starting seed range. | [case creation](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L94-L105), [registration loop](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L310-L326) |
| Shared object count | `1` to `3` | Controls how many top-level GLSL `shared` objects are declared in the generated shader. | [RandomSharedLayoutCase constructor](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L108-L123) |
| Members per shared object | `2` to `4` | Controls how many members each generated `S1` / `s1`-style object contains. | [generateSharedMemoryObject()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L134-L143) |
| Array length | `1` to `3` when arrays are enabled | Controls generated array sizes and therefore the number of leaf checks produced by flattening. | [array generation](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L185-L191) |
| Type depth | `3` for struct or arrays-of-arrays layout nodes, otherwise `1` | Determines whether the random generator may recurse into nested structs or nested arrays. | [generateSharedMemoryVar()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L145-L153) |
| Base type candidates | `float`, `int`, `uint`, `bool`, optional vectors and matrices | Provides the ordinary 32-bit/bool value space checked by the base layout nodes. | [base type selection](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L234-L268) |
| 16-bit candidates | `uint16`, `int16`, `float16`, optional 16-bit vectors | Adds narrow 16-bit fields that require feature gates and promoted comparison values. | [16-bit type selection](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L195-L218) |
| 8-bit candidates | `uint8`, `int8`, optional 8-bit vectors | Adds narrow 8-bit integer fields that require feature gates and promoted comparison values. | [8-bit type selection](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L219-L233) |

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.memory_model.shared.16bit.nested_structs_arrays.3
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `shared` | Selects the delegated shared-memory layout test family. |
| `16bit` | Enables `GL_EXT_shader_explicit_arithmetic_types` and allows 16-bit scalar/vector fields in generated structs. |
| `nested_structs_arrays` | Uses the most complex shared-layout generator branch: nested structs combined with arrays and arrays-of-arrays. |
| `3` | Selects deterministic case seed `150 + 3`, with value literals generated from the case name seed. |
| Compute stage | Emits one compute shader with `layout(local_size_x = 1) in;` and one host-visible `passed` counter buffer. |

#### Purpose

This shader tests whether a complex 16-bit-capable GLSL `shared` memory layout can preserve every generated leaf value after
shader-side writes, workgroup synchronization, and promoted comparisons. It is a concrete stress case for nested struct, array,
matrix, vector, and 16-bit field addressing.

#### Structural Design

| Phase | Shader behavior | What is being tested |
|-------|-----------------|----------------------|
| Interface setup | Declare the result buffer, generated helper structs, `S1` / `S2` / `S3`, and `shared S1 s1; shared S2 s2; shared S3 s3;`. | Whether generated composite shared-memory declarations are legal and addressable. |
| Write phase | Assign hard-coded generated values into every flattened leaf path. | Whether nested member and array paths can be written correctly. |
| Synchronization | Execute `barrier(); memoryBarrier();`. | Whether the shader follows the intended shared-memory write/read ordering pattern. |
| Compare phase | Compare each leaf with a generated expected literal, promoting 16-bit values where required. | Whether reads from shared memory return the exact values written earlier. |
| Result reduction | Increment `passed` once only if every comparison succeeds. | Converts many shader-side checks into one host-readable counter. |

#### Shader Code

Reconstructed GLSL for this path:

```glsl
#version 450
#extension GL_EXT_shader_explicit_arithmetic_types : enable
layout(local_size_x = 1) in;

/// Binding 0 is the only host-created resource: a 4-byte storage buffer containing `passed`.
/// The shader increments it once only when all generated shared-memory checks pass.
layout(std140, binding = 0) buffer block { highp uint passed; };
struct sA
{
	u16vec4 mA;
	u16vec2 mB[3][2];
};
struct sB
{
	highp vec2 mA;
	uint16_t mB;
};
struct sC
{
	sB mA;
};
struct sD
{
	f16vec3 mA;
	highp int mB;
	uint16_t mC;
};
struct sE
{
	mediump mat4 mA;
	bvec4 mB;
};
struct sF
{
	sD mA;
	sE mB;
	mediump int mC[2];
};
struct sG
{
	sC mA;
	sF mB;
};
struct sH
{
	f16vec2 mA;
};
struct sI
{
	sH mA;
};
struct sJ
{
	highp uvec3 mA;
};
struct sK
{
	bvec3 mA;
};
struct sL
{
	mediump mat4x3 mA;
	u16vec4 mB;
	f16vec3 mC;
};
struct sM
{
	sJ mA;
	sK mB;
	sL mC;
};
struct sN
{
	sI mA;
	sM mB;
};
struct sO
{
	f16vec2 mA[1];
};
struct sP
{
	i16vec3 mA[1];
	i16vec2 mB[2];
};
struct sQ
{
	sO mA;
	sP mB;
};
struct sR
{
	u16vec4 mA;
};
struct sS
{
	float16_t mA;
	bvec3 mB;
};
struct sT
{
	i16vec4 mA[1];
	sS mB;
};
struct sU
{
	sT mA;
};
struct sV
{
	i16vec2 mA;
	mediump uvec2 mB;
	int16_t mC;
};
struct sW
{
	sV mA;
	bvec4 mB[3];
};
struct sX
{
	mediump ivec3 mA;
	i16vec2 mB;
};
struct sY
{
	float16_t mA;
	mediump mat3x2 mB;
	uint16_t mC;
};
struct sZ
{
	sX mA;
	sY mB;
	f16vec2 mC[3];
};
struct sAA
{
	sW mA;
	lowp mat4x3 mB[2][1];
	sZ mC;
};
struct sAB
{
	float16_t mA;
	float16_t mB;
};
struct sAC
{
	mediump uint mA;
	mediump uint mB;
	f16vec4 mC;
};
struct sAD
{
	bool mA;
	sAB mB;
	sAC mC;
};
struct sAE
{
	sAD mA;
	i16vec4 mB[3][2];
};
struct sAF
{
	u16vec3 mA;
};
struct sAG
{
	lowp uvec3 mA;
};
struct sAH
{
	u16vec3 mA;
	i16vec3 mB;
};
struct sAI
{
	sAF mA;
	sAG mB;
	sAH mC;
};
struct sAJ
{
	bool mA;
	i16vec4 mB;
};
struct sAK
{
	sAJ mA;
};
struct sAL
{
	sAI mA;
	sAK mB;
};
struct S1 {
	sA a;
	sG b;
};
struct S2 {
	sN a;
	sQ b;
	sR c;
	sU d;
};
struct S3 {
	sAA a;
	sAE b;
	sAL c;
};

bool compare_float    (highp float a, highp float b)  { return abs(a - b) < 0.05; }
bool compare_vec2     (highp vec2 a, highp vec2 b)    { return compare_float(a.x, b.x)&&compare_float(a.y, b.y); }
bool compare_vec3     (highp vec3 a, highp vec3 b)    { return compare_float(a.x, b.x)&&compare_float(a.y, b.y)&&compare_float(a.z, b.z); }
bool compare_vec4     (highp vec4 a, highp vec4 b)    { return compare_float(a.x, b.x)&&compare_float(a.y, b.y)&&compare_float(a.z, b.z)&&compare_float(a.w, b.w); }
bool compare_mat3x2   (highp mat3x2 a, highp mat3x2 b){ return compare_vec2(a[0], b[0])&&compare_vec2(a[1], b[1])&&compare_vec2(a[2], b[2]); }
bool compare_mat4x3   (highp mat4x3 a, highp mat4x3 b){ return compare_vec3(a[0], b[0])&&compare_vec3(a[1], b[1])&&compare_vec3(a[2], b[2])&&compare_vec3(a[3], b[3]); }
bool compare_mat4     (highp mat4 a, highp mat4 b)    { return compare_vec4(a[0], b[0])&&compare_vec4(a[1], b[1])&&compare_vec4(a[2], b[2])&&compare_vec4(a[3], b[3]); }
bool compare_int      (highp int a, highp int b)      { return a == b; }
bool compare_ivec3    (highp ivec3 a, highp ivec3 b)  { return a == b; }
bool compare_uint     (highp uint a, highp uint b)    { return a == b; }
bool compare_uvec2    (highp uvec2 a, highp uvec2 b)  { return a == b; }
bool compare_uvec3    (highp uvec3 a, highp uvec3 b)  { return a == b; }
bool compare_bool     (bool a, bool b)                { return a == b; }
bool compare_bvec3    (bvec3 a, bvec3 b)              { return a == b; }
bool compare_bvec4    (bvec4 a, bvec4 b)              { return a == b; }
bool compare_uint16_t (highp uint a, highp uint b)    { return a == b; }
bool compare_u16vec2  (highp uvec2 a, highp uvec2 b)  { return a == b; }
bool compare_u16vec3  (highp uvec3 a, highp uvec3 b)  { return a == b; }
bool compare_u16vec4  (highp uvec4 a, highp uvec4 b)  { return a == b; }
bool compare_int16_t  (highp int a, highp int b)      { return a == b; }
bool compare_i16vec2  (highp ivec2 a, highp ivec2 b)  { return a == b; }
bool compare_i16vec3  (highp ivec3 a, highp ivec3 b)  { return a == b; }
bool compare_i16vec4  (highp ivec4 a, highp ivec4 b)  { return a == b; }
bool compare_float16_t(highp float a, highp float b)  { return abs(a - b) < 0.05; }
bool compare_f16vec2  (highp vec2 a, highp vec2 b)    { return compare_float(a.x, b.x)&&compare_float(a.y, b.y); }
bool compare_f16vec3  (highp vec3 a, highp vec3 b)    { return compare_float(a.x, b.x)&&compare_float(a.y, b.y)&&compare_float(a.z, b.z); }
bool compare_f16vec4  (highp vec4 a, highp vec4 b)    { return compare_float(a.x, b.x)&&compare_float(a.y, b.y)&&compare_float(a.z, b.z)&&compare_float(a.w, b.w); }

/// These three objects are shader-local workgroup shared-memory objects. The host does not create
/// descriptor-backed resources for them; their layout and leaf addressing are the tested data.
shared S1 s1;
shared S2 s2;
shared S3 s3;

void main (void) {
	/// Write phase: generated constants are embedded in shader source and assigned to every flattened leaf.
	s1.a.mA = u16vec4(1u, 9u, 8u, 5u);
	s1.a.mB[0][0] = u16vec2(3u, 6u);
	s1.a.mB[0][1] = u16vec2(8u, 6u);
	s1.a.mB[1][0] = u16vec2(2u, 7u);
	s1.a.mB[1][1] = u16vec2(6u, 0u);
	s1.a.mB[2][0] = u16vec2(7u, 2u);
	s1.a.mB[2][1] = u16vec2(5u, 6u);
	s1.b.mA.mA.mA = vec2(7.0, 3.0);
	s1.b.mA.mA.mB = uint16_t(2u);
	s1.b.mB.mA.mA = f16vec3(7.0, 4.0, -2.0);
	s1.b.mB.mA.mB = 9;
	s1.b.mB.mA.mC = uint16_t(2u);
	s1.b.mB.mB.mA = mat4(-5.0, 1.0, -6.0, 8.0, 5.0, 5.0, -3.0, 3.0, 1.0, -9.0, 7.0, -2.0, 2.0, 9.0, -3.0, 3.0);
	s1.b.mB.mB.mB = bvec4(true, false, false, true);
	s1.b.mB.mC[0] = -9;
	s1.b.mB.mC[1] = -7;
	s2.a.mA.mA.mA = f16vec2(-4.0, -4.0);
	s2.a.mB.mA.mA = uvec3(7u, 9u, 8u);
	s2.a.mB.mB.mA = bvec3(false, false, true);
	s2.a.mB.mC.mA = mat4x3(1.0, -3.0, -9.0, -6.0, 6.0, 5.0, -5.0, 2.0, 4.0, 9.0, 2.0, 5.0);
	s2.a.mB.mC.mB = u16vec4(5u, 4u, 8u, 0u);
	s2.a.mB.mC.mC = f16vec3(-8.0, -9.0, 5.0);
	s2.b.mA.mA[0] = f16vec2(1.0, -5.0);
	s2.b.mB.mA[0] = i16vec3(5, -3, 6);
	s2.b.mB.mB[0] = i16vec2(6, 2);
	s2.b.mB.mB[1] = i16vec2(4, 4);
	s2.c.mA = u16vec4(5u, 2u, 3u, 4u);
	s2.d.mA.mA[0] = i16vec4(-3, 4, -7, 1);
	s2.d.mA.mB.mA = float16_t(-5.0);
	s2.d.mA.mB.mB = bvec3(true, false, false);
	s3.a.mA.mA.mA = i16vec2(6, -3);
	s3.a.mA.mA.mB = uvec2(4u, 9u);
	s3.a.mA.mA.mC = int16_t(-9);
	s3.a.mA.mB[0] = bvec4(false, true, false, true);
	s3.a.mA.mB[1] = bvec4(true, false, false, false);
	s3.a.mA.mB[2] = bvec4(true, true, true, true);
	s3.a.mB[0][0] = mat4x3(6.0, -7.0, 7.0, -2.0, -7.0, 4.0, 1.0, -2.0, 4.0, -3.0, 6.0, 1.0);
	s3.a.mB[1][0] = mat4x3(-2.0, 5.0, 2.0, -8.0, -6.0, -5.0, 7.0, 5.0, -6.0, 5.0, -5.0, 3.0);
	s3.a.mC.mA.mA = ivec3(-8, 6, 5);
	s3.a.mC.mA.mB = i16vec2(-9, 7);
	s3.a.mC.mB.mA = float16_t(5.0);
	s3.a.mC.mB.mB = mat3x2(-8.0, 9.0, -8.0, -7.0, 9.0, -9.0);
	s3.a.mC.mB.mC = uint16_t(9u);
	s3.a.mC.mC[0] = f16vec2(8.0, -1.0);
	s3.a.mC.mC[1] = f16vec2(-1.0, 7.0);
	s3.a.mC.mC[2] = f16vec2(-7.0, 9.0);
	s3.b.mA.mA = false;
	s3.b.mA.mB.mA = float16_t(7.0);
	s3.b.mA.mB.mB = float16_t(7.0);
	s3.b.mA.mC.mA = 6u;
	s3.b.mA.mC.mB = 9u;
	s3.b.mA.mC.mC = f16vec4(-4.0, 0.0, 6.0, 4.0);
	s3.b.mB[0][0] = i16vec4(1, -6, -2, -8);
	s3.b.mB[0][1] = i16vec4(6, 6, 2, 9);
	s3.b.mB[1][0] = i16vec4(7, -8, -5, 8);
	s3.b.mB[1][1] = i16vec4(-3, -5, 7, -3);
	s3.b.mB[2][0] = i16vec4(-5, 7, -2, 1);
	s3.b.mB[2][1] = i16vec4(-9, 5, 9, 6);
	s3.c.mA.mA.mA = u16vec3(6u, 5u, 6u);
	s3.c.mA.mB.mA = uvec3(1u, 3u, 1u);
	s3.c.mA.mC.mA = u16vec3(2u, 9u, 8u);
	s3.c.mA.mC.mB = i16vec3(7, 7, 1);
	s3.c.mB.mA.mA = true;
	s3.c.mB.mA.mB = i16vec4(7, 1, 1, -3);

	/// Synchronization phase: keep the generated shared-memory write/read ordering pattern before validation.
	barrier();
	memoryBarrier();
	bool allOk = true;
	/// Compare phase: 16-bit leaves are promoted to 32-bit scalar/vector forms before comparison.
	allOk = compare_u16vec4(uvec4(1u, 9u, 8u, 5u), uvec4(s1.a.mA)) && allOk;
	allOk = compare_u16vec2(uvec2(3u, 6u), uvec2(s1.a.mB[0][0])) && allOk;
	allOk = compare_u16vec2(uvec2(8u, 6u), uvec2(s1.a.mB[0][1])) && allOk;
	allOk = compare_u16vec2(uvec2(2u, 7u), uvec2(s1.a.mB[1][0])) && allOk;
	allOk = compare_u16vec2(uvec2(6u, 0u), uvec2(s1.a.mB[1][1])) && allOk;
	allOk = compare_u16vec2(uvec2(7u, 2u), uvec2(s1.a.mB[2][0])) && allOk;
	allOk = compare_u16vec2(uvec2(5u, 6u), uvec2(s1.a.mB[2][1])) && allOk;
	allOk = compare_vec2(vec2(7.0, 3.0), s1.b.mA.mA.mA) && allOk;
	allOk = compare_uint16_t(uint(2u), uint(s1.b.mA.mA.mB)) && allOk;
	allOk = compare_f16vec3(vec3(7.0, 4.0, -2.0), vec3(s1.b.mB.mA.mA)) && allOk;
	allOk = compare_int(9, s1.b.mB.mA.mB) && allOk;
	allOk = compare_uint16_t(uint(2u), uint(s1.b.mB.mA.mC)) && allOk;
	allOk = compare_mat4(mat4(-5.0, 1.0, -6.0, 8.0, 5.0, 5.0, -3.0, 3.0, 1.0, -9.0, 7.0, -2.0, 2.0, 9.0, -3.0, 3.0), s1.b.mB.mB.mA) && allOk;
	allOk = compare_bvec4(bvec4(true, false, false, true), s1.b.mB.mB.mB) && allOk;
	allOk = compare_int(-9, s1.b.mB.mC[0]) && allOk;
	allOk = compare_int(-7, s1.b.mB.mC[1]) && allOk;
	allOk = compare_f16vec2(vec2(-4.0, -4.0), vec2(s2.a.mA.mA.mA)) && allOk;
	allOk = compare_uvec3(uvec3(7u, 9u, 8u), s2.a.mB.mA.mA) && allOk;
	allOk = compare_bvec3(bvec3(false, false, true), s2.a.mB.mB.mA) && allOk;
	allOk = compare_mat4x3(mat4x3(1.0, -3.0, -9.0, -6.0, 6.0, 5.0, -5.0, 2.0, 4.0, 9.0, 2.0, 5.0), s2.a.mB.mC.mA) && allOk;
	allOk = compare_u16vec4(uvec4(5u, 4u, 8u, 0u), uvec4(s2.a.mB.mC.mB)) && allOk;
	allOk = compare_f16vec3(vec3(-8.0, -9.0, 5.0), vec3(s2.a.mB.mC.mC)) && allOk;
	allOk = compare_f16vec2(vec2(1.0, -5.0), vec2(s2.b.mA.mA[0])) && allOk;
	allOk = compare_i16vec3(ivec3(5, -3, 6), ivec3(s2.b.mB.mA[0])) && allOk;
	allOk = compare_i16vec2(ivec2(6, 2), ivec2(s2.b.mB.mB[0])) && allOk;
	allOk = compare_i16vec2(ivec2(4, 4), ivec2(s2.b.mB.mB[1])) && allOk;
	allOk = compare_u16vec4(uvec4(5u, 2u, 3u, 4u), uvec4(s2.c.mA)) && allOk;
	allOk = compare_i16vec4(ivec4(-3, 4, -7, 1), ivec4(s2.d.mA.mA[0])) && allOk;
	allOk = compare_float16_t(float(-5.0), float(s2.d.mA.mB.mA)) && allOk;
	allOk = compare_bvec3(bvec3(true, false, false), s2.d.mA.mB.mB) && allOk;
	allOk = compare_i16vec2(ivec2(6, -3), ivec2(s3.a.mA.mA.mA)) && allOk;
	allOk = compare_uvec2(uvec2(4u, 9u), s3.a.mA.mA.mB) && allOk;
	allOk = compare_int16_t(int(-9), int(s3.a.mA.mA.mC)) && allOk;
	allOk = compare_bvec4(bvec4(false, true, false, true), s3.a.mA.mB[0]) && allOk;
	allOk = compare_bvec4(bvec4(true, false, false, false), s3.a.mA.mB[1]) && allOk;
	allOk = compare_bvec4(bvec4(true, true, true, true), s3.a.mA.mB[2]) && allOk;
	allOk = compare_mat4x3(mat4x3(6.0, -7.0, 7.0, -2.0, -7.0, 4.0, 1.0, -2.0, 4.0, -3.0, 6.0, 1.0), s3.a.mB[0][0]) && allOk;
	allOk = compare_mat4x3(mat4x3(-2.0, 5.0, 2.0, -8.0, -6.0, -5.0, 7.0, 5.0, -6.0, 5.0, -5.0, 3.0), s3.a.mB[1][0]) && allOk;
	allOk = compare_ivec3(ivec3(-8, 6, 5), s3.a.mC.mA.mA) && allOk;
	allOk = compare_i16vec2(ivec2(-9, 7), ivec2(s3.a.mC.mA.mB)) && allOk;
	allOk = compare_float16_t(float(5.0), float(s3.a.mC.mB.mA)) && allOk;
	allOk = compare_mat3x2(mat3x2(-8.0, 9.0, -8.0, -7.0, 9.0, -9.0), s3.a.mC.mB.mB) && allOk;
	allOk = compare_uint16_t(uint(9u), uint(s3.a.mC.mB.mC)) && allOk;
	allOk = compare_f16vec2(vec2(8.0, -1.0), vec2(s3.a.mC.mC[0])) && allOk;
	allOk = compare_f16vec2(vec2(-1.0, 7.0), vec2(s3.a.mC.mC[1])) && allOk;
	allOk = compare_f16vec2(vec2(-7.0, 9.0), vec2(s3.a.mC.mC[2])) && allOk;
	allOk = compare_bool(false, s3.b.mA.mA) && allOk;
	allOk = compare_float16_t(float(7.0), float(s3.b.mA.mB.mA)) && allOk;
	allOk = compare_float16_t(float(7.0), float(s3.b.mA.mB.mB)) && allOk;
	allOk = compare_uint(6u, s3.b.mA.mC.mA) && allOk;
	allOk = compare_uint(9u, s3.b.mA.mC.mB) && allOk;
	allOk = compare_f16vec4(vec4(-4.0, 0.0, 6.0, 4.0), vec4(s3.b.mA.mC.mC)) && allOk;
	allOk = compare_i16vec4(ivec4(1, -6, -2, -8), ivec4(s3.b.mB[0][0])) && allOk;
	allOk = compare_i16vec4(ivec4(6, 6, 2, 9), ivec4(s3.b.mB[0][1])) && allOk;
	allOk = compare_i16vec4(ivec4(7, -8, -5, 8), ivec4(s3.b.mB[1][0])) && allOk;
	allOk = compare_i16vec4(ivec4(-3, -5, 7, -3), ivec4(s3.b.mB[1][1])) && allOk;
	allOk = compare_i16vec4(ivec4(-5, 7, -2, 1), ivec4(s3.b.mB[2][0])) && allOk;
	allOk = compare_i16vec4(ivec4(-9, 5, 9, 6), ivec4(s3.b.mB[2][1])) && allOk;
	allOk = compare_u16vec3(uvec3(6u, 5u, 6u), uvec3(s3.c.mA.mA.mA)) && allOk;
	allOk = compare_uvec3(uvec3(1u, 3u, 1u), s3.c.mA.mB.mA) && allOk;
	allOk = compare_u16vec3(uvec3(2u, 9u, 8u), uvec3(s3.c.mA.mC.mA)) && allOk;
	allOk = compare_i16vec3(ivec3(7, 7, 1), ivec3(s3.c.mA.mC.mB)) && allOk;
	allOk = compare_bool(true, s3.c.mB.mA.mA) && allOk;
	allOk = compare_i16vec4(ivec4(7, 1, 1, -3), ivec4(s3.c.mB.mA.mB)) && allOk;
	/// Result reduction: the host expects exactly one increment after dispatching one workgroup with one invocation.
	if (allOk)
		passed++;

}
```

#### Additional Info

- The host dispatches this generated compute shader as one workgroup with one local invocation, so `barrier()` and
  `memoryBarrier()` preserve the generated shared-memory access pattern but are not primarily testing multi-invocation communication
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L282-L285),
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L464-L468).
- Expected values are hard-coded into the generated shader source as assignment and comparison literals; the host does not upload a
  separate expected-value buffer for the shared-memory fields
  [generateValue()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L90-L139),
  [generateSharedMemoryWrites()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L197-L269).
- The `16bit` branch is not only a naming prefix: it enables 16-bit type generation and requires the narrow-type support path before
  this shader can run
  [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L195-L218),
  [SharedLayoutCase::checkSupport()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L347-L358).

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Type-width branch | Base cases omit `GL_EXT_shader_explicit_arithmetic_types`; 8-bit cases use `GL_EXT_shader_explicit_arithmetic_types_int8`; this 16-bit case emits 16-bit scalar and vector declarations plus promoted comparisons. | [extension emission](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L277-L280), [16-bit type selection](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L195-L218) |
| Layout shape node | Less complex nodes remove parts of this structure: scalar/vector/basic nodes avoid nested struct-array paths, while `nested_structs_arrays` allows both recursive structs and array indexing. | [feature sets](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L310-L326), [recursive type generation](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L162-L191) |
| Case number | The exact member graph and literals change with the deterministic random seed; case `3` is one concrete generated layout, not a hand-written sample. | [case seed construction](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L94-L105), [value generation](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L90-L139) |
| Shared object count | This case generated three top-level shared objects; other cases may generate one, two, or three, changing declaration and write/compare volume. | [shared object loop](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L115-L123), [shared declarations](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L309-L310) |
| Compare helper set | The helper functions are generated only for the basic types and dependencies present in the selected case. | [helper collection](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L178-L195), [helper emission](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L304-L307) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 10
; Bound: 1408
; Schema: 0
               OpCapability Shader
               OpCapability Float16
               OpCapability Int16
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types"
               OpName %main "main"
               OpName %compare_float_f1_f1_ "compare_float(f1;f1;"
               OpName %a "a"
               OpName %b "b"
               OpName %compare_vec2_vf2_vf2_ "compare_vec2(vf2;vf2;"
               OpName %a_0 "a"
               OpName %b_0 "b"
               OpName %compare_vec3_vf3_vf3_ "compare_vec3(vf3;vf3;"
               OpName %a_1 "a"
               OpName %b_1 "b"
               OpName %compare_vec4_vf4_vf4_ "compare_vec4(vf4;vf4;"
               OpName %a_2 "a"
               OpName %b_2 "b"
               OpName %compare_mat3x2_mf32_mf32_ "compare_mat3x2(mf32;mf32;"
               OpName %a_3 "a"
               OpName %b_3 "b"
               OpName %compare_mat4x3_mf43_mf43_ "compare_mat4x3(mf43;mf43;"
               OpName %a_4 "a"
               OpName %b_4 "b"
               OpName %compare_mat4_mf44_mf44_ "compare_mat4(mf44;mf44;"
               OpName %a_5 "a"
               OpName %b_5 "b"
               OpName %compare_int_i1_i1_ "compare_int(i1;i1;"
               OpName %a_6 "a"
               OpName %b_6 "b"
               OpName %compare_ivec3_vi3_vi3_ "compare_ivec3(vi3;vi3;"
               OpName %a_7 "a"
               OpName %b_7 "b"
               OpName %compare_uint_u1_u1_ "compare_uint(u1;u1;"
               OpName %a_8 "a"
               OpName %b_8 "b"
               OpName %compare_uvec2_vu2_vu2_ "compare_uvec2(vu2;vu2;"
               OpName %a_9 "a"
               OpName %b_9 "b"
               OpName %compare_uvec3_vu3_vu3_ "compare_uvec3(vu3;vu3;"
               OpName %a_10 "a"
               OpName %b_10 "b"
               OpName %compare_bool_b1_b1_ "compare_bool(b1;b1;"
               OpName %a_11 "a"
               OpName %b_11 "b"
               OpName %compare_bvec3_vb3_vb3_ "compare_bvec3(vb3;vb3;"
               OpName %a_12 "a"
               OpName %b_12 "b"
               OpName %compare_bvec4_vb4_vb4_ "compare_bvec4(vb4;vb4;"
               OpName %a_13 "a"
               OpName %b_13 "b"
               OpName %compare_uint16_t_u1_u1_ "compare_uint16_t(u1;u1;"
               OpName %a_14 "a"
               OpName %b_14 "b"
               OpName %compare_u16vec2_vu2_vu2_ "compare_u16vec2(vu2;vu2;"
               OpName %a_15 "a"
               OpName %b_15 "b"
               OpName %compare_u16vec3_vu3_vu3_ "compare_u16vec3(vu3;vu3;"
               OpName %a_16 "a"
               OpName %b_16 "b"
               OpName %compare_u16vec4_vu4_vu4_ "compare_u16vec4(vu4;vu4;"
               OpName %a_17 "a"
               OpName %b_17 "b"
               OpName %compare_int16_t_i1_i1_ "compare_int16_t(i1;i1;"
               OpName %a_18 "a"
               OpName %b_18 "b"
               OpName %compare_i16vec2_vi2_vi2_ "compare_i16vec2(vi2;vi2;"
               OpName %a_19 "a"
               OpName %b_19 "b"
               OpName %compare_i16vec3_vi3_vi3_ "compare_i16vec3(vi3;vi3;"
               OpName %a_20 "a"
               OpName %b_20 "b"
               OpName %compare_i16vec4_vi4_vi4_ "compare_i16vec4(vi4;vi4;"
               OpName %a_21 "a"
               OpName %b_21 "b"
               OpName %compare_float16_t_f1_f1_ "compare_float16_t(f1;f1;"
               OpName %a_22 "a"
               OpName %b_22 "b"
               OpName %compare_f16vec2_vf2_vf2_ "compare_f16vec2(vf2;vf2;"
               OpName %a_23 "a"
               OpName %b_23 "b"
               OpName %compare_f16vec3_vf3_vf3_ "compare_f16vec3(vf3;vf3;"
               OpName %a_24 "a"
               OpName %b_24 "b"
               OpName %compare_f16vec4_vf4_vf4_ "compare_f16vec4(vf4;vf4;"
               OpName %a_25 "a"
               OpName %b_25 "b"
               OpName %param "param"
               OpName %param_0 "param"
               OpName %param_1 "param"
               OpName %param_2 "param"
               OpName %param_3 "param"
               OpName %param_4 "param"
               OpName %param_5 "param"
               OpName %param_6 "param"
               OpName %param_7 "param"
               OpName %param_8 "param"
               OpName %param_9 "param"
               OpName %param_10 "param"
               OpName %param_11 "param"
               OpName %param_12 "param"
               OpName %param_13 "param"
               OpName %param_14 "param"
               OpName %param_15 "param"
               OpName %param_16 "param"
               OpName %param_17 "param"
               OpName %param_18 "param"
               OpName %param_19 "param"
               OpName %param_20 "param"
               OpName %param_21 "param"
               OpName %param_22 "param"
               OpName %param_23 "param"
               OpName %param_24 "param"
               OpName %param_25 "param"
               OpName %param_26 "param"
               OpName %param_27 "param"
               OpName %param_28 "param"
               OpName %param_29 "param"
               OpName %param_30 "param"
               OpName %param_31 "param"
               OpName %param_32 "param"
               OpName %param_33 "param"
               OpName %param_34 "param"
               OpName %param_35 "param"
               OpName %param_36 "param"
               OpName %param_37 "param"
               OpName %param_38 "param"
               OpName %param_39 "param"
               OpName %param_40 "param"
               OpName %param_41 "param"
               OpName %param_42 "param"
               OpName %param_43 "param"
               OpName %param_44 "param"
               OpName %param_45 "param"
               OpName %param_46 "param"
               OpName %param_47 "param"
               OpName %param_48 "param"
               OpName %param_49 "param"
               OpName %param_50 "param"
               OpName %param_51 "param"
               OpName %param_52 "param"
               OpName %param_53 "param"
               OpName %param_54 "param"
               OpName %param_55 "param"
               OpName %param_56 "param"
               OpName %sA "sA"
               OpMemberName %sA 0 "mA"
               OpMemberName %sA 1 "mB"
               OpName %sB "sB"
               OpMemberName %sB 0 "mA"
               OpMemberName %sB 1 "mB"
               OpName %sC "sC"
               OpMemberName %sC 0 "mA"
               OpName %sD "sD"
               OpMemberName %sD 0 "mA"
               OpMemberName %sD 1 "mB"
               OpMemberName %sD 2 "mC"
               OpName %sE "sE"
               OpMemberName %sE 0 "mA"
               OpMemberName %sE 1 "mB"
               OpName %sF "sF"
               OpMemberName %sF 0 "mA"
               OpMemberName %sF 1 "mB"
               OpMemberName %sF 2 "mC"
               OpName %sG "sG"
               OpMemberName %sG 0 "mA"
               OpMemberName %sG 1 "mB"
               OpName %S1 "S1"
               OpMemberName %S1 0 "a"
               OpMemberName %S1 1 "b"
               OpName %s1 "s1"
               OpName %sH "sH"
               OpMemberName %sH 0 "mA"
               OpName %sI "sI"
               OpMemberName %sI 0 "mA"
               OpName %sJ "sJ"
               OpMemberName %sJ 0 "mA"
               OpName %sK "sK"
               OpMemberName %sK 0 "mA"
               OpName %sL "sL"
               OpMemberName %sL 0 "mA"
               OpMemberName %sL 1 "mB"
               OpMemberName %sL 2 "mC"
               OpName %sM "sM"
               OpMemberName %sM 0 "mA"
               OpMemberName %sM 1 "mB"
               OpMemberName %sM 2 "mC"
               OpName %sN "sN"
               OpMemberName %sN 0 "mA"
               OpMemberName %sN 1 "mB"
               OpName %sO "sO"
               OpMemberName %sO 0 "mA"
               OpName %sP "sP"
               OpMemberName %sP 0 "mA"
               OpMemberName %sP 1 "mB"
               OpName %sQ "sQ"
               OpMemberName %sQ 0 "mA"
               OpMemberName %sQ 1 "mB"
               OpName %sR "sR"
               OpMemberName %sR 0 "mA"
               OpName %sS "sS"
               OpMemberName %sS 0 "mA"
               OpMemberName %sS 1 "mB"
               OpName %sT "sT"
               OpMemberName %sT 0 "mA"
               OpMemberName %sT 1 "mB"
               OpName %sU "sU"
               OpMemberName %sU 0 "mA"
               OpName %S2 "S2"
               OpMemberName %S2 0 "a"
               OpMemberName %S2 1 "b"
               OpMemberName %S2 2 "c"
               OpMemberName %S2 3 "d"
               OpName %s2 "s2"
               OpName %sV "sV"
               OpMemberName %sV 0 "mA"
               OpMemberName %sV 1 "mB"
               OpMemberName %sV 2 "mC"
               OpName %sW "sW"
               OpMemberName %sW 0 "mA"
               OpMemberName %sW 1 "mB"
               OpName %sX "sX"
               OpMemberName %sX 0 "mA"
               OpMemberName %sX 1 "mB"
               OpName %sY "sY"
               OpMemberName %sY 0 "mA"
               OpMemberName %sY 1 "mB"
               OpMemberName %sY 2 "mC"
               OpName %sZ "sZ"
               OpMemberName %sZ 0 "mA"
               OpMemberName %sZ 1 "mB"
               OpMemberName %sZ 2 "mC"
               OpName %sAA "sAA"
               OpMemberName %sAA 0 "mA"
               OpMemberName %sAA 1 "mB"
               OpMemberName %sAA 2 "mC"
               OpName %sAB "sAB"
               OpMemberName %sAB 0 "mA"
               OpMemberName %sAB 1 "mB"
               OpName %sAC "sAC"
               OpMemberName %sAC 0 "mA"
               OpMemberName %sAC 1 "mB"
               OpMemberName %sAC 2 "mC"
               OpName %sAD "sAD"
               OpMemberName %sAD 0 "mA"
               OpMemberName %sAD 1 "mB"
               OpMemberName %sAD 2 "mC"
               OpName %sAE "sAE"
               OpMemberName %sAE 0 "mA"
               OpMemberName %sAE 1 "mB"
               OpName %sAF "sAF"
               OpMemberName %sAF 0 "mA"
               OpName %sAG "sAG"
               OpMemberName %sAG 0 "mA"
               OpName %sAH "sAH"
               OpMemberName %sAH 0 "mA"
               OpMemberName %sAH 1 "mB"
               OpName %sAI "sAI"
               OpMemberName %sAI 0 "mA"
               OpMemberName %sAI 1 "mB"
               OpMemberName %sAI 2 "mC"
               OpName %sAJ "sAJ"
               OpMemberName %sAJ 0 "mA"
               OpMemberName %sAJ 1 "mB"
               OpName %sAK "sAK"
               OpMemberName %sAK 0 "mA"
               OpName %sAL "sAL"
               OpMemberName %sAL 0 "mA"
               OpMemberName %sAL 1 "mB"
               OpName %S3 "S3"
               OpMemberName %S3 0 "a"
               OpMemberName %S3 1 "b"
               OpMemberName %S3 2 "c"
               OpName %s3 "s3"
               OpName %allOk "allOk"
               OpName %param_57 "param"
               OpName %param_58 "param"
               OpName %param_59 "param"
               OpName %param_60 "param"
               OpName %param_61 "param"
               OpName %param_62 "param"
               OpName %param_63 "param"
               OpName %param_64 "param"
               OpName %param_65 "param"
               OpName %param_66 "param"
               OpName %param_67 "param"
               OpName %param_68 "param"
               OpName %param_69 "param"
               OpName %param_70 "param"
               OpName %param_71 "param"
               OpName %param_72 "param"
               OpName %param_73 "param"
               OpName %param_74 "param"
               OpName %param_75 "param"
               OpName %param_76 "param"
               OpName %param_77 "param"
               OpName %param_78 "param"
               OpName %param_79 "param"
               OpName %param_80 "param"
               OpName %param_81 "param"
               OpName %param_82 "param"
               OpName %param_83 "param"
               OpName %param_84 "param"
               OpName %param_85 "param"
               OpName %param_86 "param"
               OpName %param_87 "param"
               OpName %param_88 "param"
               OpName %param_89 "param"
               OpName %param_90 "param"
               OpName %param_91 "param"
               OpName %param_92 "param"
               OpName %param_93 "param"
               OpName %param_94 "param"
               OpName %param_95 "param"
               OpName %param_96 "param"
               OpName %param_97 "param"
               OpName %param_98 "param"
               OpName %param_99 "param"
               OpName %param_100 "param"
               OpName %param_101 "param"
               OpName %param_102 "param"
               OpName %param_103 "param"
               OpName %param_104 "param"
               OpName %param_105 "param"
               OpName %param_106 "param"
               OpName %param_107 "param"
               OpName %param_108 "param"
               OpName %param_109 "param"
               OpName %param_110 "param"
               OpName %param_111 "param"
               OpName %param_112 "param"
               OpName %param_113 "param"
               OpName %param_114 "param"
               OpName %param_115 "param"
               OpName %param_116 "param"
               OpName %param_117 "param"
               OpName %param_118 "param"
               OpName %param_119 "param"
               OpName %param_120 "param"
               OpName %param_121 "param"
               OpName %param_122 "param"
               OpName %param_123 "param"
               OpName %param_124 "param"
               OpName %param_125 "param"
               OpName %param_126 "param"
               OpName %param_127 "param"
               OpName %param_128 "param"
               OpName %param_129 "param"
               OpName %param_130 "param"
               OpName %param_131 "param"
               OpName %param_132 "param"
               OpName %param_133 "param"
               OpName %param_134 "param"
               OpName %param_135 "param"
               OpName %param_136 "param"
               OpName %param_137 "param"
               OpName %param_138 "param"
               OpName %param_139 "param"
               OpName %param_140 "param"
               OpName %param_141 "param"
               OpName %param_142 "param"
               OpName %param_143 "param"
               OpName %param_144 "param"
               OpName %param_145 "param"
               OpName %param_146 "param"
               OpName %param_147 "param"
               OpName %param_148 "param"
               OpName %param_149 "param"
               OpName %param_150 "param"
               OpName %param_151 "param"
               OpName %param_152 "param"
               OpName %param_153 "param"
               OpName %param_154 "param"
               OpName %param_155 "param"
               OpName %param_156 "param"
               OpName %param_157 "param"
               OpName %param_158 "param"
               OpName %param_159 "param"
               OpName %param_160 "param"
               OpName %param_161 "param"
               OpName %param_162 "param"
               OpName %param_163 "param"
               OpName %param_164 "param"
               OpName %param_165 "param"
               OpName %param_166 "param"
               OpName %param_167 "param"
               OpName %param_168 "param"
               OpName %param_169 "param"
               OpName %param_170 "param"
               OpName %param_171 "param"
               OpName %param_172 "param"
               OpName %param_173 "param"
               OpName %param_174 "param"
               OpName %param_175 "param"
               OpName %param_176 "param"
               OpName %param_177 "param"
               OpName %param_178 "param"
               OpName %param_179 "param"
               OpName %param_180 "param"
               OpName %param_181 "param"
               OpName %param_182 "param"
               OpName %param_183 "param"
               OpName %param_184 "param"
               OpName %block "block"
               OpMemberName %block 0 "passed"
               OpName %_ ""
               OpMemberDecorate %sE 0 RelaxedPrecision
               OpMemberDecorate %sF 2 RelaxedPrecision
               OpMemberDecorate %sL 0 RelaxedPrecision
               OpMemberDecorate %sV 1 RelaxedPrecision
               OpMemberDecorate %sX 0 RelaxedPrecision
               OpMemberDecorate %sY 1 RelaxedPrecision
               OpMemberDecorate %sAA 1 RelaxedPrecision
               OpMemberDecorate %sAC 0 RelaxedPrecision
               OpMemberDecorate %sAC 1 RelaxedPrecision
               OpMemberDecorate %sAG 0 RelaxedPrecision
               OpDecorate %970 RelaxedPrecision
               OpDecorate %984 RelaxedPrecision
               OpDecorate %991 RelaxedPrecision
               OpDecorate %1022 RelaxedPrecision
               OpDecorate %1127 RelaxedPrecision
               OpDecorate %1163 RelaxedPrecision
               OpDecorate %1170 RelaxedPrecision
               OpDecorate %1177 RelaxedPrecision
               OpDecorate %1202 RelaxedPrecision
               OpDecorate %1268 RelaxedPrecision
               OpDecorate %1275 RelaxedPrecision
               OpDecorate %1359 RelaxedPrecision
               OpMemberDecorate %block 0 Offset 0
               OpDecorate %block BufferBlock
               OpDecorate %_ DescriptorSet 0
               OpDecorate %_ Binding 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
       %bool = OpTypeBool
          %9 = OpTypeFunction %bool %_ptr_Function_float %_ptr_Function_float
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
         %16 = OpTypeFunction %bool %_ptr_Function_v2float %_ptr_Function_v2float
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
         %23 = OpTypeFunction %bool %_ptr_Function_v3float %_ptr_Function_v3float
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %30 = OpTypeFunction %bool %_ptr_Function_v4float %_ptr_Function_v4float
%mat3v2float = OpTypeMatrix %v2float 3
%_ptr_Function_mat3v2float = OpTypePointer Function %mat3v2float
         %37 = OpTypeFunction %bool %_ptr_Function_mat3v2float %_ptr_Function_mat3v2float
%mat4v3float = OpTypeMatrix %v3float 4
%_ptr_Function_mat4v3float = OpTypePointer Function %mat4v3float
         %44 = OpTypeFunction %bool %_ptr_Function_mat4v3float %_ptr_Function_mat4v3float
%mat4v4float = OpTypeMatrix %v4float 4
%_ptr_Function_mat4v4float = OpTypePointer Function %mat4v4float
         %51 = OpTypeFunction %bool %_ptr_Function_mat4v4float %_ptr_Function_mat4v4float
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
         %58 = OpTypeFunction %bool %_ptr_Function_int %_ptr_Function_int
      %v3int = OpTypeVector %int 3
%_ptr_Function_v3int = OpTypePointer Function %v3int
         %65 = OpTypeFunction %bool %_ptr_Function_v3int %_ptr_Function_v3int
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
         %72 = OpTypeFunction %bool %_ptr_Function_uint %_ptr_Function_uint
     %v2uint = OpTypeVector %uint 2
%_ptr_Function_v2uint = OpTypePointer Function %v2uint
         %79 = OpTypeFunction %bool %_ptr_Function_v2uint %_ptr_Function_v2uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Function_v3uint = OpTypePointer Function %v3uint
         %86 = OpTypeFunction %bool %_ptr_Function_v3uint %_ptr_Function_v3uint
%_ptr_Function_bool = OpTypePointer Function %bool
         %92 = OpTypeFunction %bool %_ptr_Function_bool %_ptr_Function_bool
     %v3bool = OpTypeVector %bool 3
%_ptr_Function_v3bool = OpTypePointer Function %v3bool
         %99 = OpTypeFunction %bool %_ptr_Function_v3bool %_ptr_Function_v3bool
     %v4bool = OpTypeVector %bool 4
%_ptr_Function_v4bool = OpTypePointer Function %v4bool
        %106 = OpTypeFunction %bool %_ptr_Function_v4bool %_ptr_Function_v4bool
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
        %125 = OpTypeFunction %bool %_ptr_Function_v4uint %_ptr_Function_v4uint
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
        %136 = OpTypeFunction %bool %_ptr_Function_v2int %_ptr_Function_v2int
      %v4int = OpTypeVector %int 4
%_ptr_Function_v4int = OpTypePointer Function %v4int
        %147 = OpTypeFunction %bool %_ptr_Function_v4int %_ptr_Function_v4int
%float_0_0500000007 = OpConstant %float 0.0500000007
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
     %uint_3 = OpConstant %uint 3
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
     %v2bool = OpTypeVector %bool 2
     %ushort = OpTypeInt 16 0
   %v4ushort = OpTypeVector %ushort 4
   %v2ushort = OpTypeVector %ushort 2
%_arr_v2ushort_uint_2 = OpTypeArray %v2ushort %uint_2
%_arr__arr_v2ushort_uint_2_uint_3 = OpTypeArray %_arr_v2ushort_uint_2 %uint_3
         %sA = OpTypeStruct %v4ushort %_arr__arr_v2ushort_uint_2_uint_3
         %sB = OpTypeStruct %v2float %ushort
         %sC = OpTypeStruct %sB
       %half = OpTypeFloat 16
     %v3half = OpTypeVector %half 3
         %sD = OpTypeStruct %v3half %int %ushort
         %sE = OpTypeStruct %mat4v4float %v4bool
%_arr_int_uint_2 = OpTypeArray %int %uint_2
         %sF = OpTypeStruct %sD %sE %_arr_int_uint_2
         %sG = OpTypeStruct %sC %sF
         %S1 = OpTypeStruct %sA %sG
%_ptr_Workgroup_S1 = OpTypePointer Workgroup %S1
         %s1 = OpVariable %_ptr_Workgroup_S1 Workgroup
   %ushort_1 = OpConstant %ushort 1
   %ushort_9 = OpConstant %ushort 9
   %ushort_8 = OpConstant %ushort 8
   %ushort_5 = OpConstant %ushort 5
        %586 = OpConstantComposite %v4ushort %ushort_1 %ushort_9 %ushort_8 %ushort_5
%_ptr_Workgroup_v4ushort = OpTypePointer Workgroup %v4ushort
   %ushort_3 = OpConstant %ushort 3
   %ushort_6 = OpConstant %ushort 6
        %591 = OpConstantComposite %v2ushort %ushort_3 %ushort_6
%_ptr_Workgroup_v2ushort = OpTypePointer Workgroup %v2ushort
        %594 = OpConstantComposite %v2ushort %ushort_8 %ushort_6
   %ushort_2 = OpConstant %ushort 2
   %ushort_7 = OpConstant %ushort 7
        %598 = OpConstantComposite %v2ushort %ushort_2 %ushort_7
   %ushort_0 = OpConstant %ushort 0
        %601 = OpConstantComposite %v2ushort %ushort_6 %ushort_0
        %603 = OpConstantComposite %v2ushort %ushort_7 %ushort_2
        %605 = OpConstantComposite %v2ushort %ushort_5 %ushort_6
    %float_7 = OpConstant %float 7
    %float_3 = OpConstant %float 3
        %609 = OpConstantComposite %v2float %float_7 %float_3
%_ptr_Workgroup_v2float = OpTypePointer Workgroup %v2float
%_ptr_Workgroup_ushort = OpTypePointer Workgroup %ushort
%half_0x1_cp_2 = OpConstant %half 0x1.cp+2
%half_0x1p_2 = OpConstant %half 0x1p+2
%half_n0x1p_1 = OpConstant %half -0x1p+1
        %617 = OpConstantComposite %v3half %half_0x1_cp_2 %half_0x1p_2 %half_n0x1p_1
%_ptr_Workgroup_v3half = OpTypePointer Workgroup %v3half
      %int_9 = OpConstant %int 9
%_ptr_Workgroup_int = OpTypePointer Workgroup %int
   %float_n5 = OpConstant %float -5
    %float_1 = OpConstant %float 1
   %float_n6 = OpConstant %float -6
    %float_8 = OpConstant %float 8
        %628 = OpConstantComposite %v4float %float_n5 %float_1 %float_n6 %float_8
    %float_5 = OpConstant %float 5
   %float_n3 = OpConstant %float -3
        %631 = OpConstantComposite %v4float %float_5 %float_5 %float_n3 %float_3
   %float_n9 = OpConstant %float -9
   %float_n2 = OpConstant %float -2
        %634 = OpConstantComposite %v4float %float_1 %float_n9 %float_7 %float_n2
    %float_2 = OpConstant %float 2
    %float_9 = OpConstant %float 9
        %637 = OpConstantComposite %v4float %float_2 %float_9 %float_n3 %float_3
        %638 = OpConstantComposite %mat4v4float %628 %631 %634 %637
%_ptr_Workgroup_mat4v4float = OpTypePointer Workgroup %mat4v4float
       %true = OpConstantTrue %bool
      %false = OpConstantFalse %bool
        %643 = OpConstantComposite %v4bool %true %false %false %true
%_ptr_Workgroup_v4bool = OpTypePointer Workgroup %v4bool
     %int_n9 = OpConstant %int -9
     %int_n7 = OpConstant %int -7
     %v2half = OpTypeVector %half 2
         %sH = OpTypeStruct %v2half
         %sI = OpTypeStruct %sH
         %sJ = OpTypeStruct %v3uint
         %sK = OpTypeStruct %v3bool
         %sL = OpTypeStruct %mat4v3float %v4ushort %v3half
         %sM = OpTypeStruct %sJ %sK %sL
         %sN = OpTypeStruct %sI %sM
%_arr_v2half_uint_1 = OpTypeArray %v2half %uint_1
         %sO = OpTypeStruct %_arr_v2half_uint_1
      %short = OpTypeInt 16 1
    %v3short = OpTypeVector %short 3
%_arr_v3short_uint_1 = OpTypeArray %v3short %uint_1
    %v2short = OpTypeVector %short 2
%_arr_v2short_uint_2 = OpTypeArray %v2short %uint_2
         %sP = OpTypeStruct %_arr_v3short_uint_1 %_arr_v2short_uint_2
         %sQ = OpTypeStruct %sO %sP
         %sR = OpTypeStruct %v4ushort
    %v4short = OpTypeVector %short 4
%_arr_v4short_uint_1 = OpTypeArray %v4short %uint_1
         %sS = OpTypeStruct %half %v3bool
         %sT = OpTypeStruct %_arr_v4short_uint_1 %sS
         %sU = OpTypeStruct %sT
         %S2 = OpTypeStruct %sN %sQ %sR %sU
%_ptr_Workgroup_S2 = OpTypePointer Workgroup %S2
         %s2 = OpVariable %_ptr_Workgroup_S2 Workgroup
%half_n0x1p_2 = OpConstant %half -0x1p+2
        %677 = OpConstantComposite %v2half %half_n0x1p_2 %half_n0x1p_2
%_ptr_Workgroup_v2half = OpTypePointer Workgroup %v2half
     %uint_7 = OpConstant %uint 7
     %uint_9 = OpConstant %uint 9
     %uint_8 = OpConstant %uint 8
        %683 = OpConstantComposite %v3uint %uint_7 %uint_9 %uint_8
%_ptr_Workgroup_v3uint = OpTypePointer Workgroup %v3uint
        %686 = OpConstantComposite %v3bool %false %false %true
%_ptr_Workgroup_v3bool = OpTypePointer Workgroup %v3bool
        %689 = OpConstantComposite %v3float %float_1 %float_n3 %float_n9
    %float_6 = OpConstant %float 6
        %691 = OpConstantComposite %v3float %float_n6 %float_6 %float_5
    %float_4 = OpConstant %float 4
        %693 = OpConstantComposite %v3float %float_n5 %float_2 %float_4
        %694 = OpConstantComposite %v3float %float_9 %float_2 %float_5
        %695 = OpConstantComposite %mat4v3float %689 %691 %693 %694
%_ptr_Workgroup_mat4v3float = OpTypePointer Workgroup %mat4v3float
   %ushort_4 = OpConstant %ushort 4
        %699 = OpConstantComposite %v4ushort %ushort_5 %ushort_4 %ushort_8 %ushort_0
%half_n0x1p_3 = OpConstant %half -0x1p+3
%half_n0x1_2p_3 = OpConstant %half -0x1.2p+3
%half_0x1_4p_2 = OpConstant %half 0x1.4p+2
        %704 = OpConstantComposite %v3half %half_n0x1p_3 %half_n0x1_2p_3 %half_0x1_4p_2
%half_0x1p_0 = OpConstant %half 0x1p+0
%half_n0x1_4p_2 = OpConstant %half -0x1.4p+2
        %708 = OpConstantComposite %v2half %half_0x1p_0 %half_n0x1_4p_2
    %short_5 = OpConstant %short 5
   %short_n3 = OpConstant %short -3
    %short_6 = OpConstant %short 6
        %713 = OpConstantComposite %v3short %short_5 %short_n3 %short_6
%_ptr_Workgroup_v3short = OpTypePointer Workgroup %v3short
    %short_2 = OpConstant %short 2
        %717 = OpConstantComposite %v2short %short_6 %short_2
%_ptr_Workgroup_v2short = OpTypePointer Workgroup %v2short
    %short_4 = OpConstant %short 4
        %721 = OpConstantComposite %v2short %short_4 %short_4
        %723 = OpConstantComposite %v4ushort %ushort_5 %ushort_2 %ushort_3 %ushort_4
   %short_n7 = OpConstant %short -7
    %short_1 = OpConstant %short 1
        %727 = OpConstantComposite %v4short %short_n3 %short_4 %short_n7 %short_1
%_ptr_Workgroup_v4short = OpTypePointer Workgroup %v4short
%_ptr_Workgroup_half = OpTypePointer Workgroup %half
        %732 = OpConstantComposite %v3bool %true %false %false
         %sV = OpTypeStruct %v2short %v2uint %short
%_arr_v4bool_uint_3 = OpTypeArray %v4bool %uint_3
         %sW = OpTypeStruct %sV %_arr_v4bool_uint_3
%_arr_mat4v3float_uint_1 = OpTypeArray %mat4v3float %uint_1
%_arr__arr_mat4v3float_uint_1_uint_2 = OpTypeArray %_arr_mat4v3float_uint_1 %uint_2
         %sX = OpTypeStruct %v3int %v2short
         %sY = OpTypeStruct %half %mat3v2float %ushort
%_arr_v2half_uint_3 = OpTypeArray %v2half %uint_3
         %sZ = OpTypeStruct %sX %sY %_arr_v2half_uint_3
        %sAA = OpTypeStruct %sW %_arr__arr_mat4v3float_uint_1_uint_2 %sZ
        %sAB = OpTypeStruct %half %half
     %v4half = OpTypeVector %half 4
        %sAC = OpTypeStruct %uint %uint %v4half
        %sAD = OpTypeStruct %bool %sAB %sAC
%_arr_v4short_uint_2 = OpTypeArray %v4short %uint_2
%_arr__arr_v4short_uint_2_uint_3 = OpTypeArray %_arr_v4short_uint_2 %uint_3
        %sAE = OpTypeStruct %sAD %_arr__arr_v4short_uint_2_uint_3
   %v3ushort = OpTypeVector %ushort 3
        %sAF = OpTypeStruct %v3ushort
        %sAG = OpTypeStruct %v3uint
        %sAH = OpTypeStruct %v3ushort %v3short
        %sAI = OpTypeStruct %sAF %sAG %sAH
        %sAJ = OpTypeStruct %bool %v4short
        %sAK = OpTypeStruct %sAJ
        %sAL = OpTypeStruct %sAI %sAK
         %S3 = OpTypeStruct %sAA %sAE %sAL
%_ptr_Workgroup_S3 = OpTypePointer Workgroup %S3
         %s3 = OpVariable %_ptr_Workgroup_S3 Workgroup
        %762 = OpConstantComposite %v2short %short_6 %short_n3
     %uint_4 = OpConstant %uint 4
        %765 = OpConstantComposite %v2uint %uint_4 %uint_9
%_ptr_Workgroup_v2uint = OpTypePointer Workgroup %v2uint
   %short_n9 = OpConstant %short -9
%_ptr_Workgroup_short = OpTypePointer Workgroup %short
        %771 = OpConstantComposite %v4bool %false %true %false %true
        %773 = OpConstantComposite %v4bool %true %false %false %false
        %775 = OpConstantComposite %v4bool %true %true %true %true
   %float_n7 = OpConstant %float -7
        %778 = OpConstantComposite %v3float %float_6 %float_n7 %float_7
        %779 = OpConstantComposite %v3float %float_n2 %float_n7 %float_4
        %780 = OpConstantComposite %v3float %float_1 %float_n2 %float_4
        %781 = OpConstantComposite %v3float %float_n3 %float_6 %float_1
        %782 = OpConstantComposite %mat4v3float %778 %779 %780 %781
        %784 = OpConstantComposite %v3float %float_n2 %float_5 %float_2
   %float_n8 = OpConstant %float -8
        %786 = OpConstantComposite %v3float %float_n8 %float_n6 %float_n5
        %787 = OpConstantComposite %v3float %float_7 %float_5 %float_n6
        %788 = OpConstantComposite %v3float %float_5 %float_n5 %float_3
        %789 = OpConstantComposite %mat4v3float %784 %786 %787 %788
     %int_n8 = OpConstant %int -8
      %int_6 = OpConstant %int 6
      %int_5 = OpConstant %int 5
        %794 = OpConstantComposite %v3int %int_n8 %int_6 %int_5
%_ptr_Workgroup_v3int = OpTypePointer Workgroup %v3int
    %short_7 = OpConstant %short 7
        %798 = OpConstantComposite %v2short %short_n9 %short_7
        %801 = OpConstantComposite %v2float %float_n8 %float_9
        %802 = OpConstantComposite %v2float %float_n8 %float_n7
        %803 = OpConstantComposite %v2float %float_9 %float_n9
        %804 = OpConstantComposite %mat3v2float %801 %802 %803
%_ptr_Workgroup_mat3v2float = OpTypePointer Workgroup %mat3v2float
%half_0x1p_3 = OpConstant %half 0x1p+3
%half_n0x1p_0 = OpConstant %half -0x1p+0
        %810 = OpConstantComposite %v2half %half_0x1p_3 %half_n0x1p_0
        %812 = OpConstantComposite %v2half %half_n0x1p_0 %half_0x1_cp_2
%half_n0x1_cp_2 = OpConstant %half -0x1.cp+2
%half_0x1_2p_3 = OpConstant %half 0x1.2p+3
        %816 = OpConstantComposite %v2half %half_n0x1_cp_2 %half_0x1_2p_3
%_ptr_Workgroup_bool = OpTypePointer Workgroup %bool
     %uint_6 = OpConstant %uint 6
%_ptr_Workgroup_uint = OpTypePointer Workgroup %uint
%half_0x0p_0 = OpConstant %half 0x0p+0
%half_0x1_8p_2 = OpConstant %half 0x1.8p+2
        %828 = OpConstantComposite %v4half %half_n0x1p_2 %half_0x0p_0 %half_0x1_8p_2 %half_0x1p_2
%_ptr_Workgroup_v4half = OpTypePointer Workgroup %v4half
   %short_n6 = OpConstant %short -6
   %short_n2 = OpConstant %short -2
   %short_n8 = OpConstant %short -8
        %834 = OpConstantComposite %v4short %short_1 %short_n6 %short_n2 %short_n8
    %short_9 = OpConstant %short 9
        %837 = OpConstantComposite %v4short %short_6 %short_6 %short_2 %short_9
   %short_n5 = OpConstant %short -5
    %short_8 = OpConstant %short 8
        %841 = OpConstantComposite %v4short %short_7 %short_n8 %short_n5 %short_8
        %843 = OpConstantComposite %v4short %short_n3 %short_n5 %short_7 %short_n3
        %845 = OpConstantComposite %v4short %short_n5 %short_7 %short_n2 %short_1
        %847 = OpConstantComposite %v4short %short_n9 %short_5 %short_9 %short_6
        %849 = OpConstantComposite %v3ushort %ushort_6 %ushort_5 %ushort_6
%_ptr_Workgroup_v3ushort = OpTypePointer Workgroup %v3ushort
        %852 = OpConstantComposite %v3uint %uint_1 %uint_3 %uint_1
        %854 = OpConstantComposite %v3ushort %ushort_2 %ushort_9 %ushort_8
        %856 = OpConstantComposite %v3short %short_7 %short_7 %short_1
        %859 = OpConstantComposite %v4short %short_7 %short_1 %short_1 %short_n3
   %uint_264 = OpConstant %uint 264
  %uint_3400 = OpConstant %uint 3400
     %uint_5 = OpConstant %uint 5
        %865 = OpConstantComposite %v4uint %uint_1 %uint_9 %uint_8 %uint_5
        %874 = OpConstantComposite %v2uint %uint_3 %uint_6
        %883 = OpConstantComposite %v2uint %uint_8 %uint_6
        %892 = OpConstantComposite %v2uint %uint_2 %uint_7
        %901 = OpConstantComposite %v2uint %uint_6 %uint_0
        %910 = OpConstantComposite %v2uint %uint_7 %uint_2
        %919 = OpConstantComposite %v2uint %uint_5 %uint_6
        %943 = OpConstantComposite %v3float %float_7 %float_4 %float_n2
   %float_n4 = OpConstant %float -4
        %996 = OpConstantComposite %v2float %float_n4 %float_n4
       %1026 = OpConstantComposite %v4uint %uint_5 %uint_4 %uint_8 %uint_0
       %1035 = OpConstantComposite %v3float %float_n8 %float_n9 %float_5
       %1044 = OpConstantComposite %v2float %float_1 %float_n5
     %int_n3 = OpConstant %int -3
       %1054 = OpConstantComposite %v3int %int_5 %int_n3 %int_6
       %1063 = OpConstantComposite %v2int %int_6 %int_2
      %int_4 = OpConstant %int 4
       %1073 = OpConstantComposite %v2int %int_4 %int_4
       %1082 = OpConstantComposite %v4uint %uint_5 %uint_2 %uint_3 %uint_4
       %1091 = OpConstantComposite %v4int %int_n3 %int_4 %int_n7 %int_1
       %1115 = OpConstantComposite %v2int %int_6 %int_n3
      %int_7 = OpConstant %int 7
       %1182 = OpConstantComposite %v2int %int_n9 %int_7
   %float_n1 = OpConstant %float -1
       %1215 = OpConstantComposite %v2float %float_8 %float_n1
       %1224 = OpConstantComposite %v2float %float_n1 %float_7
       %1233 = OpConstantComposite %v2float %float_n7 %float_9
    %float_0 = OpConstant %float 0
       %1280 = OpConstantComposite %v4float %float_n4 %float_0 %float_6 %float_4
     %int_n6 = OpConstant %int -6
     %int_n2 = OpConstant %int -2
       %1291 = OpConstantComposite %v4int %int_1 %int_n6 %int_n2 %int_n8
       %1300 = OpConstantComposite %v4int %int_6 %int_6 %int_2 %int_9
     %int_n5 = OpConstant %int -5
      %int_8 = OpConstant %int 8
       %1311 = OpConstantComposite %v4int %int_7 %int_n8 %int_n5 %int_8
       %1320 = OpConstantComposite %v4int %int_n3 %int_n5 %int_7 %int_n3
       %1329 = OpConstantComposite %v4int %int_n5 %int_7 %int_n2 %int_1
       %1338 = OpConstantComposite %v4int %int_n9 %int_5 %int_9 %int_6
       %1347 = OpConstantComposite %v3uint %uint_6 %uint_5 %uint_6
       %1363 = OpConstantComposite %v3uint %uint_2 %uint_9 %uint_8
       %1372 = OpConstantComposite %v3int %int_7 %int_7 %int_1
       %1388 = OpConstantComposite %v4int %int_7 %int_1 %int_1 %int_n3
      %block = OpTypeStruct %uint
%_ptr_Uniform_block = OpTypePointer Uniform %block
          %_ = OpVariable %_ptr_Uniform_block Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %allOk = OpVariable %_ptr_Function_bool Function
   %param_57 = OpVariable %_ptr_Function_v4uint Function
   %param_58 = OpVariable %_ptr_Function_v4uint Function
   %param_59 = OpVariable %_ptr_Function_v2uint Function
   %param_60 = OpVariable %_ptr_Function_v2uint Function
   %param_61 = OpVariable %_ptr_Function_v2uint Function
   %param_62 = OpVariable %_ptr_Function_v2uint Function
   %param_63 = OpVariable %_ptr_Function_v2uint Function
   %param_64 = OpVariable %_ptr_Function_v2uint Function
   %param_65 = OpVariable %_ptr_Function_v2uint Function
   %param_66 = OpVariable %_ptr_Function_v2uint Function
   %param_67 = OpVariable %_ptr_Function_v2uint Function
   %param_68 = OpVariable %_ptr_Function_v2uint Function
   %param_69 = OpVariable %_ptr_Function_v2uint Function
   %param_70 = OpVariable %_ptr_Function_v2uint Function
   %param_71 = OpVariable %_ptr_Function_v2float Function
   %param_72 = OpVariable %_ptr_Function_v2float Function
   %param_73 = OpVariable %_ptr_Function_uint Function
   %param_74 = OpVariable %_ptr_Function_uint Function
   %param_75 = OpVariable %_ptr_Function_v3float Function
   %param_76 = OpVariable %_ptr_Function_v3float Function
   %param_77 = OpVariable %_ptr_Function_int Function
   %param_78 = OpVariable %_ptr_Function_int Function
   %param_79 = OpVariable %_ptr_Function_uint Function
   %param_80 = OpVariable %_ptr_Function_uint Function
   %param_81 = OpVariable %_ptr_Function_mat4v4float Function
   %param_82 = OpVariable %_ptr_Function_mat4v4float Function
   %param_83 = OpVariable %_ptr_Function_v4bool Function
   %param_84 = OpVariable %_ptr_Function_v4bool Function
   %param_85 = OpVariable %_ptr_Function_int Function
   %param_86 = OpVariable %_ptr_Function_int Function
   %param_87 = OpVariable %_ptr_Function_int Function
   %param_88 = OpVariable %_ptr_Function_int Function
   %param_89 = OpVariable %_ptr_Function_v2float Function
   %param_90 = OpVariable %_ptr_Function_v2float Function
   %param_91 = OpVariable %_ptr_Function_v3uint Function
   %param_92 = OpVariable %_ptr_Function_v3uint Function
   %param_93 = OpVariable %_ptr_Function_v3bool Function
   %param_94 = OpVariable %_ptr_Function_v3bool Function
   %param_95 = OpVariable %_ptr_Function_mat4v3float Function
   %param_96 = OpVariable %_ptr_Function_mat4v3float Function
   %param_97 = OpVariable %_ptr_Function_v4uint Function
   %param_98 = OpVariable %_ptr_Function_v4uint Function
   %param_99 = OpVariable %_ptr_Function_v3float Function
  %param_100 = OpVariable %_ptr_Function_v3float Function
  %param_101 = OpVariable %_ptr_Function_v2float Function
  %param_102 = OpVariable %_ptr_Function_v2float Function
  %param_103 = OpVariable %_ptr_Function_v3int Function
  %param_104 = OpVariable %_ptr_Function_v3int Function
  %param_105 = OpVariable %_ptr_Function_v2int Function
  %param_106 = OpVariable %_ptr_Function_v2int Function
  %param_107 = OpVariable %_ptr_Function_v2int Function
  %param_108 = OpVariable %_ptr_Function_v2int Function
  %param_109 = OpVariable %_ptr_Function_v4uint Function
  %param_110 = OpVariable %_ptr_Function_v4uint Function
  %param_111 = OpVariable %_ptr_Function_v4int Function
  %param_112 = OpVariable %_ptr_Function_v4int Function
  %param_113 = OpVariable %_ptr_Function_float Function
  %param_114 = OpVariable %_ptr_Function_float Function
  %param_115 = OpVariable %_ptr_Function_v3bool Function
  %param_116 = OpVariable %_ptr_Function_v3bool Function
  %param_117 = OpVariable %_ptr_Function_v2int Function
  %param_118 = OpVariable %_ptr_Function_v2int Function
  %param_119 = OpVariable %_ptr_Function_v2uint Function
  %param_120 = OpVariable %_ptr_Function_v2uint Function
  %param_121 = OpVariable %_ptr_Function_int Function
  %param_122 = OpVariable %_ptr_Function_int Function
  %param_123 = OpVariable %_ptr_Function_v4bool Function
  %param_124 = OpVariable %_ptr_Function_v4bool Function
  %param_125 = OpVariable %_ptr_Function_v4bool Function
  %param_126 = OpVariable %_ptr_Function_v4bool Function
  %param_127 = OpVariable %_ptr_Function_v4bool Function
  %param_128 = OpVariable %_ptr_Function_v4bool Function
  %param_129 = OpVariable %_ptr_Function_mat4v3float Function
  %param_130 = OpVariable %_ptr_Function_mat4v3float Function
  %param_131 = OpVariable %_ptr_Function_mat4v3float Function
  %param_132 = OpVariable %_ptr_Function_mat4v3float Function
  %param_133 = OpVariable %_ptr_Function_v3int Function
  %param_134 = OpVariable %_ptr_Function_v3int Function
  %param_135 = OpVariable %_ptr_Function_v2int Function
  %param_136 = OpVariable %_ptr_Function_v2int Function
  %param_137 = OpVariable %_ptr_Function_float Function
  %param_138 = OpVariable %_ptr_Function_float Function
  %param_139 = OpVariable %_ptr_Function_mat3v2float Function
  %param_140 = OpVariable %_ptr_Function_mat3v2float Function
  %param_141 = OpVariable %_ptr_Function_uint Function
  %param_142 = OpVariable %_ptr_Function_uint Function
  %param_143 = OpVariable %_ptr_Function_v2float Function
  %param_144 = OpVariable %_ptr_Function_v2float Function
  %param_145 = OpVariable %_ptr_Function_v2float Function
  %param_146 = OpVariable %_ptr_Function_v2float Function
  %param_147 = OpVariable %_ptr_Function_v2float Function
  %param_148 = OpVariable %_ptr_Function_v2float Function
  %param_149 = OpVariable %_ptr_Function_bool Function
  %param_150 = OpVariable %_ptr_Function_bool Function
  %param_151 = OpVariable %_ptr_Function_float Function
  %param_152 = OpVariable %_ptr_Function_float Function
  %param_153 = OpVariable %_ptr_Function_float Function
  %param_154 = OpVariable %_ptr_Function_float Function
  %param_155 = OpVariable %_ptr_Function_uint Function
  %param_156 = OpVariable %_ptr_Function_uint Function
  %param_157 = OpVariable %_ptr_Function_uint Function
  %param_158 = OpVariable %_ptr_Function_uint Function
  %param_159 = OpVariable %_ptr_Function_v4float Function
  %param_160 = OpVariable %_ptr_Function_v4float Function
  %param_161 = OpVariable %_ptr_Function_v4int Function
  %param_162 = OpVariable %_ptr_Function_v4int Function
  %param_163 = OpVariable %_ptr_Function_v4int Function
  %param_164 = OpVariable %_ptr_Function_v4int Function
  %param_165 = OpVariable %_ptr_Function_v4int Function
  %param_166 = OpVariable %_ptr_Function_v4int Function
  %param_167 = OpVariable %_ptr_Function_v4int Function
  %param_168 = OpVariable %_ptr_Function_v4int Function
  %param_169 = OpVariable %_ptr_Function_v4int Function
  %param_170 = OpVariable %_ptr_Function_v4int Function
  %param_171 = OpVariable %_ptr_Function_v4int Function
  %param_172 = OpVariable %_ptr_Function_v4int Function
  %param_173 = OpVariable %_ptr_Function_v3uint Function
  %param_174 = OpVariable %_ptr_Function_v3uint Function
  %param_175 = OpVariable %_ptr_Function_v3uint Function
  %param_176 = OpVariable %_ptr_Function_v3uint Function
  %param_177 = OpVariable %_ptr_Function_v3uint Function
  %param_178 = OpVariable %_ptr_Function_v3uint Function
  %param_179 = OpVariable %_ptr_Function_v3int Function
  %param_180 = OpVariable %_ptr_Function_v3int Function
  %param_181 = OpVariable %_ptr_Function_bool Function
  %param_182 = OpVariable %_ptr_Function_bool Function
  %param_183 = OpVariable %_ptr_Function_v4int Function
  %param_184 = OpVariable %_ptr_Function_v4int Function
        %588 = OpAccessChain %_ptr_Workgroup_v4ushort %s1 %int_0 %int_0
               OpStore %588 %586
        %593 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_0 %int_0
               OpStore %593 %591
        %595 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_0 %int_1
               OpStore %595 %594
        %599 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_1 %int_0
               OpStore %599 %598
        %602 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_1 %int_1
               OpStore %602 %601
        %604 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_2 %int_0
               OpStore %604 %603
        %606 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_2 %int_1
               OpStore %606 %605
        %611 = OpAccessChain %_ptr_Workgroup_v2float %s1 %int_1 %int_0 %int_0 %int_0
               OpStore %611 %609
        %613 = OpAccessChain %_ptr_Workgroup_ushort %s1 %int_1 %int_0 %int_0 %int_1
               OpStore %613 %ushort_2
        %619 = OpAccessChain %_ptr_Workgroup_v3half %s1 %int_1 %int_1 %int_0 %int_0
               OpStore %619 %617
        %622 = OpAccessChain %_ptr_Workgroup_int %s1 %int_1 %int_1 %int_0 %int_1
               OpStore %622 %int_9
        %623 = OpAccessChain %_ptr_Workgroup_ushort %s1 %int_1 %int_1 %int_0 %int_2
               OpStore %623 %ushort_2
        %640 = OpAccessChain %_ptr_Workgroup_mat4v4float %s1 %int_1 %int_1 %int_1 %int_0
               OpStore %640 %638
        %645 = OpAccessChain %_ptr_Workgroup_v4bool %s1 %int_1 %int_1 %int_1 %int_1
               OpStore %645 %643
        %647 = OpAccessChain %_ptr_Workgroup_int %s1 %int_1 %int_1 %int_2 %int_0
               OpStore %647 %int_n9
        %649 = OpAccessChain %_ptr_Workgroup_int %s1 %int_1 %int_1 %int_2 %int_1
               OpStore %649 %int_n7
        %679 = OpAccessChain %_ptr_Workgroup_v2half %s2 %int_0 %int_0 %int_0 %int_0
               OpStore %679 %677
        %685 = OpAccessChain %_ptr_Workgroup_v3uint %s2 %int_0 %int_1 %int_0 %int_0
               OpStore %685 %683
        %688 = OpAccessChain %_ptr_Workgroup_v3bool %s2 %int_0 %int_1 %int_1 %int_0
               OpStore %688 %686
        %697 = OpAccessChain %_ptr_Workgroup_mat4v3float %s2 %int_0 %int_1 %int_2 %int_0
               OpStore %697 %695
        %700 = OpAccessChain %_ptr_Workgroup_v4ushort %s2 %int_0 %int_1 %int_2 %int_1
               OpStore %700 %699
        %705 = OpAccessChain %_ptr_Workgroup_v3half %s2 %int_0 %int_1 %int_2 %int_2
               OpStore %705 %704
        %709 = OpAccessChain %_ptr_Workgroup_v2half %s2 %int_1 %int_0 %int_0 %int_0
               OpStore %709 %708
        %715 = OpAccessChain %_ptr_Workgroup_v3short %s2 %int_1 %int_1 %int_0 %int_0
               OpStore %715 %713
        %719 = OpAccessChain %_ptr_Workgroup_v2short %s2 %int_1 %int_1 %int_1 %int_0
               OpStore %719 %717
        %722 = OpAccessChain %_ptr_Workgroup_v2short %s2 %int_1 %int_1 %int_1 %int_1
               OpStore %722 %721
        %724 = OpAccessChain %_ptr_Workgroup_v4ushort %s2 %int_2 %int_0
               OpStore %724 %723
        %729 = OpAccessChain %_ptr_Workgroup_v4short %s2 %int_3 %int_0 %int_0 %int_0
               OpStore %729 %727
        %731 = OpAccessChain %_ptr_Workgroup_half %s2 %int_3 %int_0 %int_1 %int_0
               OpStore %731 %half_n0x1_4p_2
        %733 = OpAccessChain %_ptr_Workgroup_v3bool %s2 %int_3 %int_0 %int_1 %int_1
               OpStore %733 %732
        %763 = OpAccessChain %_ptr_Workgroup_v2short %s3 %int_0 %int_0 %int_0 %int_0
               OpStore %763 %762
        %767 = OpAccessChain %_ptr_Workgroup_v2uint %s3 %int_0 %int_0 %int_0 %int_1
               OpStore %767 %765
        %770 = OpAccessChain %_ptr_Workgroup_short %s3 %int_0 %int_0 %int_0 %int_2
               OpStore %770 %short_n9
        %772 = OpAccessChain %_ptr_Workgroup_v4bool %s3 %int_0 %int_0 %int_1 %int_0
               OpStore %772 %771
        %774 = OpAccessChain %_ptr_Workgroup_v4bool %s3 %int_0 %int_0 %int_1 %int_1
               OpStore %774 %773
        %776 = OpAccessChain %_ptr_Workgroup_v4bool %s3 %int_0 %int_0 %int_1 %int_2
               OpStore %776 %775
        %783 = OpAccessChain %_ptr_Workgroup_mat4v3float %s3 %int_0 %int_1 %int_0 %int_0
               OpStore %783 %782
        %790 = OpAccessChain %_ptr_Workgroup_mat4v3float %s3 %int_0 %int_1 %int_1 %int_0
               OpStore %790 %789
        %796 = OpAccessChain %_ptr_Workgroup_v3int %s3 %int_0 %int_2 %int_0 %int_0
               OpStore %796 %794
        %799 = OpAccessChain %_ptr_Workgroup_v2short %s3 %int_0 %int_2 %int_0 %int_1
               OpStore %799 %798
        %800 = OpAccessChain %_ptr_Workgroup_half %s3 %int_0 %int_2 %int_1 %int_0
               OpStore %800 %half_0x1_4p_2
        %806 = OpAccessChain %_ptr_Workgroup_mat3v2float %s3 %int_0 %int_2 %int_1 %int_1
               OpStore %806 %804
        %807 = OpAccessChain %_ptr_Workgroup_ushort %s3 %int_0 %int_2 %int_1 %int_2
               OpStore %807 %ushort_9
        %811 = OpAccessChain %_ptr_Workgroup_v2half %s3 %int_0 %int_2 %int_2 %int_0
               OpStore %811 %810
        %813 = OpAccessChain %_ptr_Workgroup_v2half %s3 %int_0 %int_2 %int_2 %int_1
               OpStore %813 %812
        %817 = OpAccessChain %_ptr_Workgroup_v2half %s3 %int_0 %int_2 %int_2 %int_2
               OpStore %817 %816
        %819 = OpAccessChain %_ptr_Workgroup_bool %s3 %int_1 %int_0 %int_0
               OpStore %819 %false
        %820 = OpAccessChain %_ptr_Workgroup_half %s3 %int_1 %int_0 %int_1 %int_0
               OpStore %820 %half_0x1_cp_2
        %821 = OpAccessChain %_ptr_Workgroup_half %s3 %int_1 %int_0 %int_1 %int_1
               OpStore %821 %half_0x1_cp_2
        %824 = OpAccessChain %_ptr_Workgroup_uint %s3 %int_1 %int_0 %int_2 %int_0
               OpStore %824 %uint_6
        %825 = OpAccessChain %_ptr_Workgroup_uint %s3 %int_1 %int_0 %int_2 %int_1
               OpStore %825 %uint_9
        %830 = OpAccessChain %_ptr_Workgroup_v4half %s3 %int_1 %int_0 %int_2 %int_2
               OpStore %830 %828
        %835 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_0 %int_0
               OpStore %835 %834
        %838 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_0 %int_1
               OpStore %838 %837
        %842 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_1 %int_0
               OpStore %842 %841
        %844 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_1 %int_1
               OpStore %844 %843
        %846 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_2 %int_0
               OpStore %846 %845
        %848 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_2 %int_1
               OpStore %848 %847
        %851 = OpAccessChain %_ptr_Workgroup_v3ushort %s3 %int_2 %int_0 %int_0 %int_0
               OpStore %851 %849
        %853 = OpAccessChain %_ptr_Workgroup_v3uint %s3 %int_2 %int_0 %int_1 %int_0
               OpStore %853 %852
        %855 = OpAccessChain %_ptr_Workgroup_v3ushort %s3 %int_2 %int_0 %int_2 %int_0
               OpStore %855 %854
        %857 = OpAccessChain %_ptr_Workgroup_v3short %s3 %int_2 %int_0 %int_2 %int_1
               OpStore %857 %856
        %858 = OpAccessChain %_ptr_Workgroup_bool %s3 %int_2 %int_1 %int_0 %int_0
               OpStore %858 %true
        %860 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_2 %int_1 %int_0 %int_1
               OpStore %860 %859
               OpControlBarrier %uint_2 %uint_2 %uint_264
               OpMemoryBarrier %uint_1 %uint_3400
               OpStore %allOk %true
        %866 = OpAccessChain %_ptr_Workgroup_v4ushort %s1 %int_0 %int_0
        %867 = OpLoad %v4ushort %866
        %868 = OpUConvert %v4uint %867
               OpStore %param_57 %865
               OpStore %param_58 %868
        %871 = OpFunctionCall %bool %compare_u16vec4_vu4_vu4_ %param_57 %param_58
        %872 = OpLoad %bool %allOk
        %873 = OpLogicalAnd %bool %871 %872
               OpStore %allOk %873
        %875 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_0 %int_0
        %876 = OpLoad %v2ushort %875
        %877 = OpUConvert %v2uint %876
               OpStore %param_59 %874
               OpStore %param_60 %877
        %880 = OpFunctionCall %bool %compare_u16vec2_vu2_vu2_ %param_59 %param_60
        %881 = OpLoad %bool %allOk
        %882 = OpLogicalAnd %bool %880 %881
               OpStore %allOk %882
        %884 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_0 %int_1
        %885 = OpLoad %v2ushort %884
        %886 = OpUConvert %v2uint %885
               OpStore %param_61 %883
               OpStore %param_62 %886
        %889 = OpFunctionCall %bool %compare_u16vec2_vu2_vu2_ %param_61 %param_62
        %890 = OpLoad %bool %allOk
        %891 = OpLogicalAnd %bool %889 %890
               OpStore %allOk %891
        %893 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_1 %int_0
        %894 = OpLoad %v2ushort %893
        %895 = OpUConvert %v2uint %894
               OpStore %param_63 %892
               OpStore %param_64 %895
        %898 = OpFunctionCall %bool %compare_u16vec2_vu2_vu2_ %param_63 %param_64
        %899 = OpLoad %bool %allOk
        %900 = OpLogicalAnd %bool %898 %899
               OpStore %allOk %900
        %902 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_1 %int_1
        %903 = OpLoad %v2ushort %902
        %904 = OpUConvert %v2uint %903
               OpStore %param_65 %901
               OpStore %param_66 %904
        %907 = OpFunctionCall %bool %compare_u16vec2_vu2_vu2_ %param_65 %param_66
        %908 = OpLoad %bool %allOk
        %909 = OpLogicalAnd %bool %907 %908
               OpStore %allOk %909
        %911 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_2 %int_0
        %912 = OpLoad %v2ushort %911
        %913 = OpUConvert %v2uint %912
               OpStore %param_67 %910
               OpStore %param_68 %913
        %916 = OpFunctionCall %bool %compare_u16vec2_vu2_vu2_ %param_67 %param_68
        %917 = OpLoad %bool %allOk
        %918 = OpLogicalAnd %bool %916 %917
               OpStore %allOk %918
        %920 = OpAccessChain %_ptr_Workgroup_v2ushort %s1 %int_0 %int_1 %int_2 %int_1
        %921 = OpLoad %v2ushort %920
        %922 = OpUConvert %v2uint %921
               OpStore %param_69 %919
               OpStore %param_70 %922
        %925 = OpFunctionCall %bool %compare_u16vec2_vu2_vu2_ %param_69 %param_70
        %926 = OpLoad %bool %allOk
        %927 = OpLogicalAnd %bool %925 %926
               OpStore %allOk %927
               OpStore %param_71 %609
        %930 = OpAccessChain %_ptr_Workgroup_v2float %s1 %int_1 %int_0 %int_0 %int_0
        %931 = OpLoad %v2float %930
               OpStore %param_72 %931
        %932 = OpFunctionCall %bool %compare_vec2_vf2_vf2_ %param_71 %param_72
        %933 = OpLoad %bool %allOk
        %934 = OpLogicalAnd %bool %932 %933
               OpStore %allOk %934
        %935 = OpAccessChain %_ptr_Workgroup_ushort %s1 %int_1 %int_0 %int_0 %int_1
        %936 = OpLoad %ushort %935
        %937 = OpUConvert %uint %936
               OpStore %param_73 %uint_2
               OpStore %param_74 %937
        %940 = OpFunctionCall %bool %compare_uint16_t_u1_u1_ %param_73 %param_74
        %941 = OpLoad %bool %allOk
        %942 = OpLogicalAnd %bool %940 %941
               OpStore %allOk %942
        %944 = OpAccessChain %_ptr_Workgroup_v3half %s1 %int_1 %int_1 %int_0 %int_0
        %945 = OpLoad %v3half %944
        %946 = OpFConvert %v3float %945
               OpStore %param_75 %943
               OpStore %param_76 %946
        %949 = OpFunctionCall %bool %compare_f16vec3_vf3_vf3_ %param_75 %param_76
        %950 = OpLoad %bool %allOk
        %951 = OpLogicalAnd %bool %949 %950
               OpStore %allOk %951
               OpStore %param_77 %int_9
        %954 = OpAccessChain %_ptr_Workgroup_int %s1 %int_1 %int_1 %int_0 %int_1
        %955 = OpLoad %int %954
               OpStore %param_78 %955
        %956 = OpFunctionCall %bool %compare_int_i1_i1_ %param_77 %param_78
        %957 = OpLoad %bool %allOk
        %958 = OpLogicalAnd %bool %956 %957
               OpStore %allOk %958
        %959 = OpAccessChain %_ptr_Workgroup_ushort %s1 %int_1 %int_1 %int_0 %int_2
        %960 = OpLoad %ushort %959
        %961 = OpUConvert %uint %960
               OpStore %param_79 %uint_2
               OpStore %param_80 %961
        %964 = OpFunctionCall %bool %compare_uint16_t_u1_u1_ %param_79 %param_80
        %965 = OpLoad %bool %allOk
        %966 = OpLogicalAnd %bool %964 %965
               OpStore %allOk %966
               OpStore %param_81 %638
        %969 = OpAccessChain %_ptr_Workgroup_mat4v4float %s1 %int_1 %int_1 %int_1 %int_0
        %970 = OpLoad %mat4v4float %969
               OpStore %param_82 %970
        %971 = OpFunctionCall %bool %compare_mat4_mf44_mf44_ %param_81 %param_82
        %972 = OpLoad %bool %allOk
        %973 = OpLogicalAnd %bool %971 %972
               OpStore %allOk %973
               OpStore %param_83 %643
        %976 = OpAccessChain %_ptr_Workgroup_v4bool %s1 %int_1 %int_1 %int_1 %int_1
        %977 = OpLoad %v4bool %976
               OpStore %param_84 %977
        %978 = OpFunctionCall %bool %compare_bvec4_vb4_vb4_ %param_83 %param_84
        %979 = OpLoad %bool %allOk
        %980 = OpLogicalAnd %bool %978 %979
               OpStore %allOk %980
               OpStore %param_85 %int_n9
        %983 = OpAccessChain %_ptr_Workgroup_int %s1 %int_1 %int_1 %int_2 %int_0
        %984 = OpLoad %int %983
               OpStore %param_86 %984
        %985 = OpFunctionCall %bool %compare_int_i1_i1_ %param_85 %param_86
        %986 = OpLoad %bool %allOk
        %987 = OpLogicalAnd %bool %985 %986
               OpStore %allOk %987
               OpStore %param_87 %int_n7
        %990 = OpAccessChain %_ptr_Workgroup_int %s1 %int_1 %int_1 %int_2 %int_1
        %991 = OpLoad %int %990
               OpStore %param_88 %991
        %992 = OpFunctionCall %bool %compare_int_i1_i1_ %param_87 %param_88
        %993 = OpLoad %bool %allOk
        %994 = OpLogicalAnd %bool %992 %993
               OpStore %allOk %994
        %997 = OpAccessChain %_ptr_Workgroup_v2half %s2 %int_0 %int_0 %int_0 %int_0
        %998 = OpLoad %v2half %997
        %999 = OpFConvert %v2float %998
               OpStore %param_89 %996
               OpStore %param_90 %999
       %1002 = OpFunctionCall %bool %compare_f16vec2_vf2_vf2_ %param_89 %param_90
       %1003 = OpLoad %bool %allOk
       %1004 = OpLogicalAnd %bool %1002 %1003
               OpStore %allOk %1004
               OpStore %param_91 %683
       %1007 = OpAccessChain %_ptr_Workgroup_v3uint %s2 %int_0 %int_1 %int_0 %int_0
       %1008 = OpLoad %v3uint %1007
               OpStore %param_92 %1008
       %1009 = OpFunctionCall %bool %compare_uvec3_vu3_vu3_ %param_91 %param_92
       %1010 = OpLoad %bool %allOk
       %1011 = OpLogicalAnd %bool %1009 %1010
               OpStore %allOk %1011
               OpStore %param_93 %686
       %1014 = OpAccessChain %_ptr_Workgroup_v3bool %s2 %int_0 %int_1 %int_1 %int_0
       %1015 = OpLoad %v3bool %1014
               OpStore %param_94 %1015
       %1016 = OpFunctionCall %bool %compare_bvec3_vb3_vb3_ %param_93 %param_94
       %1017 = OpLoad %bool %allOk
       %1018 = OpLogicalAnd %bool %1016 %1017
               OpStore %allOk %1018
               OpStore %param_95 %695
       %1021 = OpAccessChain %_ptr_Workgroup_mat4v3float %s2 %int_0 %int_1 %int_2 %int_0
       %1022 = OpLoad %mat4v3float %1021
               OpStore %param_96 %1022
       %1023 = OpFunctionCall %bool %compare_mat4x3_mf43_mf43_ %param_95 %param_96
       %1024 = OpLoad %bool %allOk
       %1025 = OpLogicalAnd %bool %1023 %1024
               OpStore %allOk %1025
       %1027 = OpAccessChain %_ptr_Workgroup_v4ushort %s2 %int_0 %int_1 %int_2 %int_1
       %1028 = OpLoad %v4ushort %1027
       %1029 = OpUConvert %v4uint %1028
               OpStore %param_97 %1026
               OpStore %param_98 %1029
       %1032 = OpFunctionCall %bool %compare_u16vec4_vu4_vu4_ %param_97 %param_98
       %1033 = OpLoad %bool %allOk
       %1034 = OpLogicalAnd %bool %1032 %1033
               OpStore %allOk %1034
       %1036 = OpAccessChain %_ptr_Workgroup_v3half %s2 %int_0 %int_1 %int_2 %int_2
       %1037 = OpLoad %v3half %1036
       %1038 = OpFConvert %v3float %1037
               OpStore %param_99 %1035
               OpStore %param_100 %1038
       %1041 = OpFunctionCall %bool %compare_f16vec3_vf3_vf3_ %param_99 %param_100
       %1042 = OpLoad %bool %allOk
       %1043 = OpLogicalAnd %bool %1041 %1042
               OpStore %allOk %1043
       %1045 = OpAccessChain %_ptr_Workgroup_v2half %s2 %int_1 %int_0 %int_0 %int_0
       %1046 = OpLoad %v2half %1045
       %1047 = OpFConvert %v2float %1046
               OpStore %param_101 %1044
               OpStore %param_102 %1047
       %1050 = OpFunctionCall %bool %compare_f16vec2_vf2_vf2_ %param_101 %param_102
       %1051 = OpLoad %bool %allOk
       %1052 = OpLogicalAnd %bool %1050 %1051
               OpStore %allOk %1052
       %1055 = OpAccessChain %_ptr_Workgroup_v3short %s2 %int_1 %int_1 %int_0 %int_0
       %1056 = OpLoad %v3short %1055
       %1057 = OpSConvert %v3int %1056
               OpStore %param_103 %1054
               OpStore %param_104 %1057
       %1060 = OpFunctionCall %bool %compare_i16vec3_vi3_vi3_ %param_103 %param_104
       %1061 = OpLoad %bool %allOk
       %1062 = OpLogicalAnd %bool %1060 %1061
               OpStore %allOk %1062
       %1064 = OpAccessChain %_ptr_Workgroup_v2short %s2 %int_1 %int_1 %int_1 %int_0
       %1065 = OpLoad %v2short %1064
       %1066 = OpSConvert %v2int %1065
               OpStore %param_105 %1063
               OpStore %param_106 %1066
       %1069 = OpFunctionCall %bool %compare_i16vec2_vi2_vi2_ %param_105 %param_106
       %1070 = OpLoad %bool %allOk
       %1071 = OpLogicalAnd %bool %1069 %1070
               OpStore %allOk %1071
       %1074 = OpAccessChain %_ptr_Workgroup_v2short %s2 %int_1 %int_1 %int_1 %int_1
       %1075 = OpLoad %v2short %1074
       %1076 = OpSConvert %v2int %1075
               OpStore %param_107 %1073
               OpStore %param_108 %1076
       %1079 = OpFunctionCall %bool %compare_i16vec2_vi2_vi2_ %param_107 %param_108
       %1080 = OpLoad %bool %allOk
       %1081 = OpLogicalAnd %bool %1079 %1080
               OpStore %allOk %1081
       %1083 = OpAccessChain %_ptr_Workgroup_v4ushort %s2 %int_2 %int_0
       %1084 = OpLoad %v4ushort %1083
       %1085 = OpUConvert %v4uint %1084
               OpStore %param_109 %1082
               OpStore %param_110 %1085
       %1088 = OpFunctionCall %bool %compare_u16vec4_vu4_vu4_ %param_109 %param_110
       %1089 = OpLoad %bool %allOk
       %1090 = OpLogicalAnd %bool %1088 %1089
               OpStore %allOk %1090
       %1092 = OpAccessChain %_ptr_Workgroup_v4short %s2 %int_3 %int_0 %int_0 %int_0
       %1093 = OpLoad %v4short %1092
       %1094 = OpSConvert %v4int %1093
               OpStore %param_111 %1091
               OpStore %param_112 %1094
       %1097 = OpFunctionCall %bool %compare_i16vec4_vi4_vi4_ %param_111 %param_112
       %1098 = OpLoad %bool %allOk
       %1099 = OpLogicalAnd %bool %1097 %1098
               OpStore %allOk %1099
       %1100 = OpAccessChain %_ptr_Workgroup_half %s2 %int_3 %int_0 %int_1 %int_0
       %1101 = OpLoad %half %1100
       %1102 = OpFConvert %float %1101
               OpStore %param_113 %float_n5
               OpStore %param_114 %1102
       %1105 = OpFunctionCall %bool %compare_float16_t_f1_f1_ %param_113 %param_114
       %1106 = OpLoad %bool %allOk
       %1107 = OpLogicalAnd %bool %1105 %1106
               OpStore %allOk %1107
               OpStore %param_115 %732
       %1110 = OpAccessChain %_ptr_Workgroup_v3bool %s2 %int_3 %int_0 %int_1 %int_1
       %1111 = OpLoad %v3bool %1110
               OpStore %param_116 %1111
       %1112 = OpFunctionCall %bool %compare_bvec3_vb3_vb3_ %param_115 %param_116
       %1113 = OpLoad %bool %allOk
       %1114 = OpLogicalAnd %bool %1112 %1113
               OpStore %allOk %1114
       %1116 = OpAccessChain %_ptr_Workgroup_v2short %s3 %int_0 %int_0 %int_0 %int_0
       %1117 = OpLoad %v2short %1116
       %1118 = OpSConvert %v2int %1117
               OpStore %param_117 %1115
               OpStore %param_118 %1118
       %1121 = OpFunctionCall %bool %compare_i16vec2_vi2_vi2_ %param_117 %param_118
       %1122 = OpLoad %bool %allOk
       %1123 = OpLogicalAnd %bool %1121 %1122
               OpStore %allOk %1123
               OpStore %param_119 %765
       %1126 = OpAccessChain %_ptr_Workgroup_v2uint %s3 %int_0 %int_0 %int_0 %int_1
       %1127 = OpLoad %v2uint %1126
               OpStore %param_120 %1127
       %1128 = OpFunctionCall %bool %compare_uvec2_vu2_vu2_ %param_119 %param_120
       %1129 = OpLoad %bool %allOk
       %1130 = OpLogicalAnd %bool %1128 %1129
               OpStore %allOk %1130
       %1131 = OpAccessChain %_ptr_Workgroup_short %s3 %int_0 %int_0 %int_0 %int_2
       %1132 = OpLoad %short %1131
       %1133 = OpSConvert %int %1132
               OpStore %param_121 %int_n9
               OpStore %param_122 %1133
       %1136 = OpFunctionCall %bool %compare_int16_t_i1_i1_ %param_121 %param_122
       %1137 = OpLoad %bool %allOk
       %1138 = OpLogicalAnd %bool %1136 %1137
               OpStore %allOk %1138
               OpStore %param_123 %771
       %1141 = OpAccessChain %_ptr_Workgroup_v4bool %s3 %int_0 %int_0 %int_1 %int_0
       %1142 = OpLoad %v4bool %1141
               OpStore %param_124 %1142
       %1143 = OpFunctionCall %bool %compare_bvec4_vb4_vb4_ %param_123 %param_124
       %1144 = OpLoad %bool %allOk
       %1145 = OpLogicalAnd %bool %1143 %1144
               OpStore %allOk %1145
               OpStore %param_125 %773
       %1148 = OpAccessChain %_ptr_Workgroup_v4bool %s3 %int_0 %int_0 %int_1 %int_1
       %1149 = OpLoad %v4bool %1148
               OpStore %param_126 %1149
       %1150 = OpFunctionCall %bool %compare_bvec4_vb4_vb4_ %param_125 %param_126
       %1151 = OpLoad %bool %allOk
       %1152 = OpLogicalAnd %bool %1150 %1151
               OpStore %allOk %1152
               OpStore %param_127 %775
       %1155 = OpAccessChain %_ptr_Workgroup_v4bool %s3 %int_0 %int_0 %int_1 %int_2
       %1156 = OpLoad %v4bool %1155
               OpStore %param_128 %1156
       %1157 = OpFunctionCall %bool %compare_bvec4_vb4_vb4_ %param_127 %param_128
       %1158 = OpLoad %bool %allOk
       %1159 = OpLogicalAnd %bool %1157 %1158
               OpStore %allOk %1159
               OpStore %param_129 %782
       %1162 = OpAccessChain %_ptr_Workgroup_mat4v3float %s3 %int_0 %int_1 %int_0 %int_0
       %1163 = OpLoad %mat4v3float %1162
               OpStore %param_130 %1163
       %1164 = OpFunctionCall %bool %compare_mat4x3_mf43_mf43_ %param_129 %param_130
       %1165 = OpLoad %bool %allOk
       %1166 = OpLogicalAnd %bool %1164 %1165
               OpStore %allOk %1166
               OpStore %param_131 %789
       %1169 = OpAccessChain %_ptr_Workgroup_mat4v3float %s3 %int_0 %int_1 %int_1 %int_0
       %1170 = OpLoad %mat4v3float %1169
               OpStore %param_132 %1170
       %1171 = OpFunctionCall %bool %compare_mat4x3_mf43_mf43_ %param_131 %param_132
       %1172 = OpLoad %bool %allOk
       %1173 = OpLogicalAnd %bool %1171 %1172
               OpStore %allOk %1173
               OpStore %param_133 %794
       %1176 = OpAccessChain %_ptr_Workgroup_v3int %s3 %int_0 %int_2 %int_0 %int_0
       %1177 = OpLoad %v3int %1176
               OpStore %param_134 %1177
       %1178 = OpFunctionCall %bool %compare_ivec3_vi3_vi3_ %param_133 %param_134
       %1179 = OpLoad %bool %allOk
       %1180 = OpLogicalAnd %bool %1178 %1179
               OpStore %allOk %1180
       %1183 = OpAccessChain %_ptr_Workgroup_v2short %s3 %int_0 %int_2 %int_0 %int_1
       %1184 = OpLoad %v2short %1183
       %1185 = OpSConvert %v2int %1184
               OpStore %param_135 %1182
               OpStore %param_136 %1185
       %1188 = OpFunctionCall %bool %compare_i16vec2_vi2_vi2_ %param_135 %param_136
       %1189 = OpLoad %bool %allOk
       %1190 = OpLogicalAnd %bool %1188 %1189
               OpStore %allOk %1190
       %1191 = OpAccessChain %_ptr_Workgroup_half %s3 %int_0 %int_2 %int_1 %int_0
       %1192 = OpLoad %half %1191
       %1193 = OpFConvert %float %1192
               OpStore %param_137 %float_5
               OpStore %param_138 %1193
       %1196 = OpFunctionCall %bool %compare_float16_t_f1_f1_ %param_137 %param_138
       %1197 = OpLoad %bool %allOk
       %1198 = OpLogicalAnd %bool %1196 %1197
               OpStore %allOk %1198
               OpStore %param_139 %804
       %1201 = OpAccessChain %_ptr_Workgroup_mat3v2float %s3 %int_0 %int_2 %int_1 %int_1
       %1202 = OpLoad %mat3v2float %1201
               OpStore %param_140 %1202
       %1203 = OpFunctionCall %bool %compare_mat3x2_mf32_mf32_ %param_139 %param_140
       %1204 = OpLoad %bool %allOk
       %1205 = OpLogicalAnd %bool %1203 %1204
               OpStore %allOk %1205
       %1206 = OpAccessChain %_ptr_Workgroup_ushort %s3 %int_0 %int_2 %int_1 %int_2
       %1207 = OpLoad %ushort %1206
       %1208 = OpUConvert %uint %1207
               OpStore %param_141 %uint_9
               OpStore %param_142 %1208
       %1211 = OpFunctionCall %bool %compare_uint16_t_u1_u1_ %param_141 %param_142
       %1212 = OpLoad %bool %allOk
       %1213 = OpLogicalAnd %bool %1211 %1212
               OpStore %allOk %1213
       %1216 = OpAccessChain %_ptr_Workgroup_v2half %s3 %int_0 %int_2 %int_2 %int_0
       %1217 = OpLoad %v2half %1216
       %1218 = OpFConvert %v2float %1217
               OpStore %param_143 %1215
               OpStore %param_144 %1218
       %1221 = OpFunctionCall %bool %compare_f16vec2_vf2_vf2_ %param_143 %param_144
       %1222 = OpLoad %bool %allOk
       %1223 = OpLogicalAnd %bool %1221 %1222
               OpStore %allOk %1223
       %1225 = OpAccessChain %_ptr_Workgroup_v2half %s3 %int_0 %int_2 %int_2 %int_1
       %1226 = OpLoad %v2half %1225
       %1227 = OpFConvert %v2float %1226
               OpStore %param_145 %1224
               OpStore %param_146 %1227
       %1230 = OpFunctionCall %bool %compare_f16vec2_vf2_vf2_ %param_145 %param_146
       %1231 = OpLoad %bool %allOk
       %1232 = OpLogicalAnd %bool %1230 %1231
               OpStore %allOk %1232
       %1234 = OpAccessChain %_ptr_Workgroup_v2half %s3 %int_0 %int_2 %int_2 %int_2
       %1235 = OpLoad %v2half %1234
       %1236 = OpFConvert %v2float %1235
               OpStore %param_147 %1233
               OpStore %param_148 %1236
       %1239 = OpFunctionCall %bool %compare_f16vec2_vf2_vf2_ %param_147 %param_148
       %1240 = OpLoad %bool %allOk
       %1241 = OpLogicalAnd %bool %1239 %1240
               OpStore %allOk %1241
               OpStore %param_149 %false
       %1244 = OpAccessChain %_ptr_Workgroup_bool %s3 %int_1 %int_0 %int_0
       %1245 = OpLoad %bool %1244
               OpStore %param_150 %1245
       %1246 = OpFunctionCall %bool %compare_bool_b1_b1_ %param_149 %param_150
       %1247 = OpLoad %bool %allOk
       %1248 = OpLogicalAnd %bool %1246 %1247
               OpStore %allOk %1248
       %1249 = OpAccessChain %_ptr_Workgroup_half %s3 %int_1 %int_0 %int_1 %int_0
       %1250 = OpLoad %half %1249
       %1251 = OpFConvert %float %1250
               OpStore %param_151 %float_7
               OpStore %param_152 %1251
       %1254 = OpFunctionCall %bool %compare_float16_t_f1_f1_ %param_151 %param_152
       %1255 = OpLoad %bool %allOk
       %1256 = OpLogicalAnd %bool %1254 %1255
               OpStore %allOk %1256
       %1257 = OpAccessChain %_ptr_Workgroup_half %s3 %int_1 %int_0 %int_1 %int_1
       %1258 = OpLoad %half %1257
       %1259 = OpFConvert %float %1258
               OpStore %param_153 %float_7
               OpStore %param_154 %1259
       %1262 = OpFunctionCall %bool %compare_float16_t_f1_f1_ %param_153 %param_154
       %1263 = OpLoad %bool %allOk
       %1264 = OpLogicalAnd %bool %1262 %1263
               OpStore %allOk %1264
               OpStore %param_155 %uint_6
       %1267 = OpAccessChain %_ptr_Workgroup_uint %s3 %int_1 %int_0 %int_2 %int_0
       %1268 = OpLoad %uint %1267
               OpStore %param_156 %1268
       %1269 = OpFunctionCall %bool %compare_uint_u1_u1_ %param_155 %param_156
       %1270 = OpLoad %bool %allOk
       %1271 = OpLogicalAnd %bool %1269 %1270
               OpStore %allOk %1271
               OpStore %param_157 %uint_9
       %1274 = OpAccessChain %_ptr_Workgroup_uint %s3 %int_1 %int_0 %int_2 %int_1
       %1275 = OpLoad %uint %1274
               OpStore %param_158 %1275
       %1276 = OpFunctionCall %bool %compare_uint_u1_u1_ %param_157 %param_158
       %1277 = OpLoad %bool %allOk
       %1278 = OpLogicalAnd %bool %1276 %1277
               OpStore %allOk %1278
       %1281 = OpAccessChain %_ptr_Workgroup_v4half %s3 %int_1 %int_0 %int_2 %int_2
       %1282 = OpLoad %v4half %1281
       %1283 = OpFConvert %v4float %1282
               OpStore %param_159 %1280
               OpStore %param_160 %1283
       %1286 = OpFunctionCall %bool %compare_f16vec4_vf4_vf4_ %param_159 %param_160
       %1287 = OpLoad %bool %allOk
       %1288 = OpLogicalAnd %bool %1286 %1287
               OpStore %allOk %1288
       %1292 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_0 %int_0
       %1293 = OpLoad %v4short %1292
       %1294 = OpSConvert %v4int %1293
               OpStore %param_161 %1291
               OpStore %param_162 %1294
       %1297 = OpFunctionCall %bool %compare_i16vec4_vi4_vi4_ %param_161 %param_162
       %1298 = OpLoad %bool %allOk
       %1299 = OpLogicalAnd %bool %1297 %1298
               OpStore %allOk %1299
       %1301 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_0 %int_1
       %1302 = OpLoad %v4short %1301
       %1303 = OpSConvert %v4int %1302
               OpStore %param_163 %1300
               OpStore %param_164 %1303
       %1306 = OpFunctionCall %bool %compare_i16vec4_vi4_vi4_ %param_163 %param_164
       %1307 = OpLoad %bool %allOk
       %1308 = OpLogicalAnd %bool %1306 %1307
               OpStore %allOk %1308
       %1312 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_1 %int_0
       %1313 = OpLoad %v4short %1312
       %1314 = OpSConvert %v4int %1313
               OpStore %param_165 %1311
               OpStore %param_166 %1314
       %1317 = OpFunctionCall %bool %compare_i16vec4_vi4_vi4_ %param_165 %param_166
       %1318 = OpLoad %bool %allOk
       %1319 = OpLogicalAnd %bool %1317 %1318
               OpStore %allOk %1319
       %1321 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_1 %int_1
       %1322 = OpLoad %v4short %1321
       %1323 = OpSConvert %v4int %1322
               OpStore %param_167 %1320
               OpStore %param_168 %1323
       %1326 = OpFunctionCall %bool %compare_i16vec4_vi4_vi4_ %param_167 %param_168
       %1327 = OpLoad %bool %allOk
       %1328 = OpLogicalAnd %bool %1326 %1327
               OpStore %allOk %1328
       %1330 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_2 %int_0
       %1331 = OpLoad %v4short %1330
       %1332 = OpSConvert %v4int %1331
               OpStore %param_169 %1329
               OpStore %param_170 %1332
       %1335 = OpFunctionCall %bool %compare_i16vec4_vi4_vi4_ %param_169 %param_170
       %1336 = OpLoad %bool %allOk
       %1337 = OpLogicalAnd %bool %1335 %1336
               OpStore %allOk %1337
       %1339 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_1 %int_1 %int_2 %int_1
       %1340 = OpLoad %v4short %1339
       %1341 = OpSConvert %v4int %1340
               OpStore %param_171 %1338
               OpStore %param_172 %1341
       %1344 = OpFunctionCall %bool %compare_i16vec4_vi4_vi4_ %param_171 %param_172
       %1345 = OpLoad %bool %allOk
       %1346 = OpLogicalAnd %bool %1344 %1345
               OpStore %allOk %1346
       %1348 = OpAccessChain %_ptr_Workgroup_v3ushort %s3 %int_2 %int_0 %int_0 %int_0
       %1349 = OpLoad %v3ushort %1348
       %1350 = OpUConvert %v3uint %1349
               OpStore %param_173 %1347
               OpStore %param_174 %1350
       %1353 = OpFunctionCall %bool %compare_u16vec3_vu3_vu3_ %param_173 %param_174
       %1354 = OpLoad %bool %allOk
       %1355 = OpLogicalAnd %bool %1353 %1354
               OpStore %allOk %1355
               OpStore %param_175 %852
       %1358 = OpAccessChain %_ptr_Workgroup_v3uint %s3 %int_2 %int_0 %int_1 %int_0
       %1359 = OpLoad %v3uint %1358
               OpStore %param_176 %1359
       %1360 = OpFunctionCall %bool %compare_uvec3_vu3_vu3_ %param_175 %param_176
       %1361 = OpLoad %bool %allOk
       %1362 = OpLogicalAnd %bool %1360 %1361
               OpStore %allOk %1362
       %1364 = OpAccessChain %_ptr_Workgroup_v3ushort %s3 %int_2 %int_0 %int_2 %int_0
       %1365 = OpLoad %v3ushort %1364
       %1366 = OpUConvert %v3uint %1365
               OpStore %param_177 %1363
               OpStore %param_178 %1366
       %1369 = OpFunctionCall %bool %compare_u16vec3_vu3_vu3_ %param_177 %param_178
       %1370 = OpLoad %bool %allOk
       %1371 = OpLogicalAnd %bool %1369 %1370
               OpStore %allOk %1371
       %1373 = OpAccessChain %_ptr_Workgroup_v3short %s3 %int_2 %int_0 %int_2 %int_1
       %1374 = OpLoad %v3short %1373
       %1375 = OpSConvert %v3int %1374
               OpStore %param_179 %1372
               OpStore %param_180 %1375
       %1378 = OpFunctionCall %bool %compare_i16vec3_vi3_vi3_ %param_179 %param_180
       %1379 = OpLoad %bool %allOk
       %1380 = OpLogicalAnd %bool %1378 %1379
               OpStore %allOk %1380
               OpStore %param_181 %true
       %1383 = OpAccessChain %_ptr_Workgroup_bool %s3 %int_2 %int_1 %int_0 %int_0
       %1384 = OpLoad %bool %1383
               OpStore %param_182 %1384
       %1385 = OpFunctionCall %bool %compare_bool_b1_b1_ %param_181 %param_182
       %1386 = OpLoad %bool %allOk
       %1387 = OpLogicalAnd %bool %1385 %1386
               OpStore %allOk %1387
       %1389 = OpAccessChain %_ptr_Workgroup_v4short %s3 %int_2 %int_1 %int_0 %int_1
       %1390 = OpLoad %v4short %1389
       %1391 = OpSConvert %v4int %1390
               OpStore %param_183 %1388
               OpStore %param_184 %1391
       %1394 = OpFunctionCall %bool %compare_i16vec4_vi4_vi4_ %param_183 %param_184
       %1395 = OpLoad %bool %allOk
       %1396 = OpLogicalAnd %bool %1394 %1395
               OpStore %allOk %1396
       %1397 = OpLoad %bool %allOk
               OpSelectionMerge %1399 None
               OpBranchConditional %1397 %1398 %1399
       %1398 = OpLabel
       %1404 = OpAccessChain %_ptr_Uniform_uint %_ %int_0
       %1405 = OpLoad %uint %1404
       %1406 = OpIAdd %uint %1405 %int_1
               OpStore %1404 %1406
               OpBranch %1399
       %1399 = OpLabel
               OpReturn
               OpFunctionEnd
%compare_float_f1_f1_ = OpFunction %bool None %9
          %a = OpFunctionParameter %_ptr_Function_float
          %b = OpFunctionParameter %_ptr_Function_float
         %13 = OpLabel
        %168 = OpLoad %float %a
        %169 = OpLoad %float %b
        %170 = OpFSub %float %168 %169
        %171 = OpExtInst %float %1 FAbs %170
        %173 = OpFOrdLessThan %bool %171 %float_0_0500000007
               OpReturnValue %173
               OpFunctionEnd
%compare_vec2_vf2_vf2_ = OpFunction %bool None %16
        %a_0 = OpFunctionParameter %_ptr_Function_v2float
        %b_0 = OpFunctionParameter %_ptr_Function_v2float
         %20 = OpLabel
      %param = OpVariable %_ptr_Function_float Function
    %param_0 = OpVariable %_ptr_Function_float Function
    %param_1 = OpVariable %_ptr_Function_float Function
    %param_2 = OpVariable %_ptr_Function_float Function
        %178 = OpAccessChain %_ptr_Function_float %a_0 %uint_0
        %179 = OpLoad %float %178
               OpStore %param %179
        %181 = OpAccessChain %_ptr_Function_float %b_0 %uint_0
        %182 = OpLoad %float %181
               OpStore %param_0 %182
        %183 = OpFunctionCall %bool %compare_float_f1_f1_ %param %param_0
               OpSelectionMerge %185 None
               OpBranchConditional %183 %184 %185
        %184 = OpLabel
        %188 = OpAccessChain %_ptr_Function_float %a_0 %uint_1
        %189 = OpLoad %float %188
               OpStore %param_1 %189
        %191 = OpAccessChain %_ptr_Function_float %b_0 %uint_1
        %192 = OpLoad %float %191
               OpStore %param_2 %192
        %193 = OpFunctionCall %bool %compare_float_f1_f1_ %param_1 %param_2
               OpBranch %185
        %185 = OpLabel
        %194 = OpPhi %bool %183 %20 %193 %184
               OpReturnValue %194
               OpFunctionEnd
%compare_vec3_vf3_vf3_ = OpFunction %bool None %23
        %a_1 = OpFunctionParameter %_ptr_Function_v3float
        %b_1 = OpFunctionParameter %_ptr_Function_v3float
         %27 = OpLabel
    %param_3 = OpVariable %_ptr_Function_float Function
    %param_4 = OpVariable %_ptr_Function_float Function
    %param_5 = OpVariable %_ptr_Function_float Function
    %param_6 = OpVariable %_ptr_Function_float Function
    %param_7 = OpVariable %_ptr_Function_float Function
    %param_8 = OpVariable %_ptr_Function_float Function
        %198 = OpAccessChain %_ptr_Function_float %a_1 %uint_0
        %199 = OpLoad %float %198
               OpStore %param_3 %199
        %201 = OpAccessChain %_ptr_Function_float %b_1 %uint_0
        %202 = OpLoad %float %201
               OpStore %param_4 %202
        %203 = OpFunctionCall %bool %compare_float_f1_f1_ %param_3 %param_4
               OpSelectionMerge %205 None
               OpBranchConditional %203 %204 %205
        %204 = OpLabel
        %207 = OpAccessChain %_ptr_Function_float %a_1 %uint_1
        %208 = OpLoad %float %207
               OpStore %param_5 %208
        %210 = OpAccessChain %_ptr_Function_float %b_1 %uint_1
        %211 = OpLoad %float %210
               OpStore %param_6 %211
        %212 = OpFunctionCall %bool %compare_float_f1_f1_ %param_5 %param_6
               OpBranch %205
        %205 = OpLabel
        %213 = OpPhi %bool %203 %27 %212 %204
               OpSelectionMerge %215 None
               OpBranchConditional %213 %214 %215
        %214 = OpLabel
        %218 = OpAccessChain %_ptr_Function_float %a_1 %uint_2
        %219 = OpLoad %float %218
               OpStore %param_7 %219
        %221 = OpAccessChain %_ptr_Function_float %b_1 %uint_2
        %222 = OpLoad %float %221
               OpStore %param_8 %222
        %223 = OpFunctionCall %bool %compare_float_f1_f1_ %param_7 %param_8
               OpBranch %215
        %215 = OpLabel
        %224 = OpPhi %bool %213 %205 %223 %214
               OpReturnValue %224
               OpFunctionEnd
%compare_vec4_vf4_vf4_ = OpFunction %bool None %30
        %a_2 = OpFunctionParameter %_ptr_Function_v4float
        %b_2 = OpFunctionParameter %_ptr_Function_v4float
         %34 = OpLabel
    %param_9 = OpVariable %_ptr_Function_float Function
   %param_10 = OpVariable %_ptr_Function_float Function
   %param_11 = OpVariable %_ptr_Function_float Function
   %param_12 = OpVariable %_ptr_Function_float Function
   %param_13 = OpVariable %_ptr_Function_float Function
   %param_14 = OpVariable %_ptr_Function_float Function
   %param_15 = OpVariable %_ptr_Function_float Function
   %param_16 = OpVariable %_ptr_Function_float Function
        %228 = OpAccessChain %_ptr_Function_float %a_2 %uint_0
        %229 = OpLoad %float %228
               OpStore %param_9 %229
        %231 = OpAccessChain %_ptr_Function_float %b_2 %uint_0
        %232 = OpLoad %float %231
               OpStore %param_10 %232
        %233 = OpFunctionCall %bool %compare_float_f1_f1_ %param_9 %param_10
               OpSelectionMerge %235 None
               OpBranchConditional %233 %234 %235
        %234 = OpLabel
        %237 = OpAccessChain %_ptr_Function_float %a_2 %uint_1
        %238 = OpLoad %float %237
               OpStore %param_11 %238
        %240 = OpAccessChain %_ptr_Function_float %b_2 %uint_1
        %241 = OpLoad %float %240
               OpStore %param_12 %241
        %242 = OpFunctionCall %bool %compare_float_f1_f1_ %param_11 %param_12
               OpBranch %235
        %235 = OpLabel
        %243 = OpPhi %bool %233 %34 %242 %234
               OpSelectionMerge %245 None
               OpBranchConditional %243 %244 %245
        %244 = OpLabel
        %247 = OpAccessChain %_ptr_Function_float %a_2 %uint_2
        %248 = OpLoad %float %247
               OpStore %param_13 %248
        %250 = OpAccessChain %_ptr_Function_float %b_2 %uint_2
        %251 = OpLoad %float %250
               OpStore %param_14 %251
        %252 = OpFunctionCall %bool %compare_float_f1_f1_ %param_13 %param_14
               OpBranch %245
        %245 = OpLabel
        %253 = OpPhi %bool %243 %235 %252 %244
               OpSelectionMerge %255 None
               OpBranchConditional %253 %254 %255
        %254 = OpLabel
        %258 = OpAccessChain %_ptr_Function_float %a_2 %uint_3
        %259 = OpLoad %float %258
               OpStore %param_15 %259
        %261 = OpAccessChain %_ptr_Function_float %b_2 %uint_3
        %262 = OpLoad %float %261
               OpStore %param_16 %262
        %263 = OpFunctionCall %bool %compare_float_f1_f1_ %param_15 %param_16
               OpBranch %255
        %255 = OpLabel
        %264 = OpPhi %bool %253 %245 %263 %254
               OpReturnValue %264
               OpFunctionEnd
%compare_mat3x2_mf32_mf32_ = OpFunction %bool None %37
        %a_3 = OpFunctionParameter %_ptr_Function_mat3v2float
        %b_3 = OpFunctionParameter %_ptr_Function_mat3v2float
         %41 = OpLabel
   %param_17 = OpVariable %_ptr_Function_v2float Function
   %param_18 = OpVariable %_ptr_Function_v2float Function
   %param_19 = OpVariable %_ptr_Function_v2float Function
   %param_20 = OpVariable %_ptr_Function_v2float Function
   %param_21 = OpVariable %_ptr_Function_v2float Function
   %param_22 = OpVariable %_ptr_Function_v2float Function
        %269 = OpAccessChain %_ptr_Function_v2float %a_3 %int_0
        %270 = OpLoad %v2float %269
               OpStore %param_17 %270
        %272 = OpAccessChain %_ptr_Function_v2float %b_3 %int_0
        %273 = OpLoad %v2float %272
               OpStore %param_18 %273
        %274 = OpFunctionCall %bool %compare_vec2_vf2_vf2_ %param_17 %param_18
               OpSelectionMerge %276 None
               OpBranchConditional %274 %275 %276
        %275 = OpLabel
        %279 = OpAccessChain %_ptr_Function_v2float %a_3 %int_1
        %280 = OpLoad %v2float %279
               OpStore %param_19 %280
        %282 = OpAccessChain %_ptr_Function_v2float %b_3 %int_1
        %283 = OpLoad %v2float %282
               OpStore %param_20 %283
        %284 = OpFunctionCall %bool %compare_vec2_vf2_vf2_ %param_19 %param_20
               OpBranch %276
        %276 = OpLabel
        %285 = OpPhi %bool %274 %41 %284 %275
               OpSelectionMerge %287 None
               OpBranchConditional %285 %286 %287
        %286 = OpLabel
        %290 = OpAccessChain %_ptr_Function_v2float %a_3 %int_2
        %291 = OpLoad %v2float %290
               OpStore %param_21 %291
        %293 = OpAccessChain %_ptr_Function_v2float %b_3 %int_2
        %294 = OpLoad %v2float %293
               OpStore %param_22 %294
        %295 = OpFunctionCall %bool %compare_vec2_vf2_vf2_ %param_21 %param_22
               OpBranch %287
        %287 = OpLabel
        %296 = OpPhi %bool %285 %276 %295 %286
               OpReturnValue %296
               OpFunctionEnd
%compare_mat4x3_mf43_mf43_ = OpFunction %bool None %44
        %a_4 = OpFunctionParameter %_ptr_Function_mat4v3float
        %b_4 = OpFunctionParameter %_ptr_Function_mat4v3float
         %48 = OpLabel
   %param_23 = OpVariable %_ptr_Function_v3float Function
   %param_24 = OpVariable %_ptr_Function_v3float Function
   %param_25 = OpVariable %_ptr_Function_v3float Function
   %param_26 = OpVariable %_ptr_Function_v3float Function
   %param_27 = OpVariable %_ptr_Function_v3float Function
   %param_28 = OpVariable %_ptr_Function_v3float Function
   %param_29 = OpVariable %_ptr_Function_v3float Function
   %param_30 = OpVariable %_ptr_Function_v3float Function
        %300 = OpAccessChain %_ptr_Function_v3float %a_4 %int_0
        %301 = OpLoad %v3float %300
               OpStore %param_23 %301
        %303 = OpAccessChain %_ptr_Function_v3float %b_4 %int_0
        %304 = OpLoad %v3float %303
               OpStore %param_24 %304
        %305 = OpFunctionCall %bool %compare_vec3_vf3_vf3_ %param_23 %param_24
               OpSelectionMerge %307 None
               OpBranchConditional %305 %306 %307
        %306 = OpLabel
        %309 = OpAccessChain %_ptr_Function_v3float %a_4 %int_1
        %310 = OpLoad %v3float %309
               OpStore %param_25 %310
        %312 = OpAccessChain %_ptr_Function_v3float %b_4 %int_1
        %313 = OpLoad %v3float %312
               OpStore %param_26 %313
        %314 = OpFunctionCall %bool %compare_vec3_vf3_vf3_ %param_25 %param_26
               OpBranch %307
        %307 = OpLabel
        %315 = OpPhi %bool %305 %48 %314 %306
               OpSelectionMerge %317 None
               OpBranchConditional %315 %316 %317
        %316 = OpLabel
        %319 = OpAccessChain %_ptr_Function_v3float %a_4 %int_2
        %320 = OpLoad %v3float %319
               OpStore %param_27 %320
        %322 = OpAccessChain %_ptr_Function_v3float %b_4 %int_2
        %323 = OpLoad %v3float %322
               OpStore %param_28 %323
        %324 = OpFunctionCall %bool %compare_vec3_vf3_vf3_ %param_27 %param_28
               OpBranch %317
        %317 = OpLabel
        %325 = OpPhi %bool %315 %307 %324 %316
               OpSelectionMerge %327 None
               OpBranchConditional %325 %326 %327
        %326 = OpLabel
        %330 = OpAccessChain %_ptr_Function_v3float %a_4 %int_3
        %331 = OpLoad %v3float %330
               OpStore %param_29 %331
        %333 = OpAccessChain %_ptr_Function_v3float %b_4 %int_3
        %334 = OpLoad %v3float %333
               OpStore %param_30 %334
        %335 = OpFunctionCall %bool %compare_vec3_vf3_vf3_ %param_29 %param_30
               OpBranch %327
        %327 = OpLabel
        %336 = OpPhi %bool %325 %317 %335 %326
               OpReturnValue %336
               OpFunctionEnd
%compare_mat4_mf44_mf44_ = OpFunction %bool None %51
        %a_5 = OpFunctionParameter %_ptr_Function_mat4v4float
        %b_5 = OpFunctionParameter %_ptr_Function_mat4v4float
         %55 = OpLabel
   %param_31 = OpVariable %_ptr_Function_v4float Function
   %param_32 = OpVariable %_ptr_Function_v4float Function
   %param_33 = OpVariable %_ptr_Function_v4float Function
   %param_34 = OpVariable %_ptr_Function_v4float Function
   %param_35 = OpVariable %_ptr_Function_v4float Function
   %param_36 = OpVariable %_ptr_Function_v4float Function
   %param_37 = OpVariable %_ptr_Function_v4float Function
   %param_38 = OpVariable %_ptr_Function_v4float Function
        %340 = OpAccessChain %_ptr_Function_v4float %a_5 %int_0
        %341 = OpLoad %v4float %340
               OpStore %param_31 %341
        %343 = OpAccessChain %_ptr_Function_v4float %b_5 %int_0
        %344 = OpLoad %v4float %343
               OpStore %param_32 %344
        %345 = OpFunctionCall %bool %compare_vec4_vf4_vf4_ %param_31 %param_32
               OpSelectionMerge %347 None
               OpBranchConditional %345 %346 %347
        %346 = OpLabel
        %349 = OpAccessChain %_ptr_Function_v4float %a_5 %int_1
        %350 = OpLoad %v4float %349
               OpStore %param_33 %350
        %352 = OpAccessChain %_ptr_Function_v4float %b_5 %int_1
        %353 = OpLoad %v4float %352
               OpStore %param_34 %353
        %354 = OpFunctionCall %bool %compare_vec4_vf4_vf4_ %param_33 %param_34
               OpBranch %347
        %347 = OpLabel
        %355 = OpPhi %bool %345 %55 %354 %346
               OpSelectionMerge %357 None
               OpBranchConditional %355 %356 %357
        %356 = OpLabel
        %359 = OpAccessChain %_ptr_Function_v4float %a_5 %int_2
        %360 = OpLoad %v4float %359
               OpStore %param_35 %360
        %362 = OpAccessChain %_ptr_Function_v4float %b_5 %int_2
        %363 = OpLoad %v4float %362
               OpStore %param_36 %363
        %364 = OpFunctionCall %bool %compare_vec4_vf4_vf4_ %param_35 %param_36
               OpBranch %357
        %357 = OpLabel
        %365 = OpPhi %bool %355 %347 %364 %356
               OpSelectionMerge %367 None
               OpBranchConditional %365 %366 %367
        %366 = OpLabel
        %369 = OpAccessChain %_ptr_Function_v4float %a_5 %int_3
        %370 = OpLoad %v4float %369
               OpStore %param_37 %370
        %372 = OpAccessChain %_ptr_Function_v4float %b_5 %int_3
        %373 = OpLoad %v4float %372
               OpStore %param_38 %373
        %374 = OpFunctionCall %bool %compare_vec4_vf4_vf4_ %param_37 %param_38
               OpBranch %367
        %367 = OpLabel
        %375 = OpPhi %bool %365 %357 %374 %366
               OpReturnValue %375
               OpFunctionEnd
%compare_int_i1_i1_ = OpFunction %bool None %58
        %a_6 = OpFunctionParameter %_ptr_Function_int
        %b_6 = OpFunctionParameter %_ptr_Function_int
         %62 = OpLabel
        %378 = OpLoad %int %a_6
        %379 = OpLoad %int %b_6
        %380 = OpIEqual %bool %378 %379
               OpReturnValue %380
               OpFunctionEnd
%compare_ivec3_vi3_vi3_ = OpFunction %bool None %65
        %a_7 = OpFunctionParameter %_ptr_Function_v3int
        %b_7 = OpFunctionParameter %_ptr_Function_v3int
         %69 = OpLabel
        %383 = OpLoad %v3int %a_7
        %384 = OpLoad %v3int %b_7
        %385 = OpIEqual %v3bool %383 %384
        %386 = OpAll %bool %385
               OpReturnValue %386
               OpFunctionEnd
%compare_uint_u1_u1_ = OpFunction %bool None %72
        %a_8 = OpFunctionParameter %_ptr_Function_uint
        %b_8 = OpFunctionParameter %_ptr_Function_uint
         %76 = OpLabel
        %389 = OpLoad %uint %a_8
        %390 = OpLoad %uint %b_8
        %391 = OpIEqual %bool %389 %390
               OpReturnValue %391
               OpFunctionEnd
%compare_uvec2_vu2_vu2_ = OpFunction %bool None %79
        %a_9 = OpFunctionParameter %_ptr_Function_v2uint
        %b_9 = OpFunctionParameter %_ptr_Function_v2uint
         %83 = OpLabel
        %394 = OpLoad %v2uint %a_9
        %395 = OpLoad %v2uint %b_9
        %397 = OpIEqual %v2bool %394 %395
        %398 = OpAll %bool %397
               OpReturnValue %398
               OpFunctionEnd
%compare_uvec3_vu3_vu3_ = OpFunction %bool None %86
       %a_10 = OpFunctionParameter %_ptr_Function_v3uint
       %b_10 = OpFunctionParameter %_ptr_Function_v3uint
         %90 = OpLabel
        %401 = OpLoad %v3uint %a_10
        %402 = OpLoad %v3uint %b_10
        %403 = OpIEqual %v3bool %401 %402
        %404 = OpAll %bool %403
               OpReturnValue %404
               OpFunctionEnd
%compare_bool_b1_b1_ = OpFunction %bool None %92
       %a_11 = OpFunctionParameter %_ptr_Function_bool
       %b_11 = OpFunctionParameter %_ptr_Function_bool
         %96 = OpLabel
        %407 = OpLoad %bool %a_11
        %408 = OpLoad %bool %b_11
        %409 = OpLogicalEqual %bool %407 %408
               OpReturnValue %409
               OpFunctionEnd
%compare_bvec3_vb3_vb3_ = OpFunction %bool None %99
       %a_12 = OpFunctionParameter %_ptr_Function_v3bool
       %b_12 = OpFunctionParameter %_ptr_Function_v3bool
        %103 = OpLabel
        %412 = OpLoad %v3bool %a_12
        %413 = OpLoad %v3bool %b_12
        %414 = OpLogicalEqual %v3bool %412 %413
        %415 = OpAll %bool %414
               OpReturnValue %415
               OpFunctionEnd
%compare_bvec4_vb4_vb4_ = OpFunction %bool None %106
       %a_13 = OpFunctionParameter %_ptr_Function_v4bool
       %b_13 = OpFunctionParameter %_ptr_Function_v4bool
        %110 = OpLabel
        %418 = OpLoad %v4bool %a_13
        %419 = OpLoad %v4bool %b_13
        %420 = OpLogicalEqual %v4bool %418 %419
        %421 = OpAll %bool %420
               OpReturnValue %421
               OpFunctionEnd
%compare_uint16_t_u1_u1_ = OpFunction %bool None %72
       %a_14 = OpFunctionParameter %_ptr_Function_uint
       %b_14 = OpFunctionParameter %_ptr_Function_uint
        %114 = OpLabel
        %424 = OpLoad %uint %a_14
        %425 = OpLoad %uint %b_14
        %426 = OpIEqual %bool %424 %425
               OpReturnValue %426
               OpFunctionEnd
%compare_u16vec2_vu2_vu2_ = OpFunction %bool None %79
       %a_15 = OpFunctionParameter %_ptr_Function_v2uint
       %b_15 = OpFunctionParameter %_ptr_Function_v2uint
        %118 = OpLabel
        %429 = OpLoad %v2uint %a_15
        %430 = OpLoad %v2uint %b_15
        %431 = OpIEqual %v2bool %429 %430
        %432 = OpAll %bool %431
               OpReturnValue %432
               OpFunctionEnd
%compare_u16vec3_vu3_vu3_ = OpFunction %bool None %86
       %a_16 = OpFunctionParameter %_ptr_Function_v3uint
       %b_16 = OpFunctionParameter %_ptr_Function_v3uint
        %122 = OpLabel
        %435 = OpLoad %v3uint %a_16
        %436 = OpLoad %v3uint %b_16
        %437 = OpIEqual %v3bool %435 %436
        %438 = OpAll %bool %437
               OpReturnValue %438
               OpFunctionEnd
%compare_u16vec4_vu4_vu4_ = OpFunction %bool None %125
       %a_17 = OpFunctionParameter %_ptr_Function_v4uint
       %b_17 = OpFunctionParameter %_ptr_Function_v4uint
        %129 = OpLabel
        %441 = OpLoad %v4uint %a_17
        %442 = OpLoad %v4uint %b_17
        %443 = OpIEqual %v4bool %441 %442
        %444 = OpAll %bool %443
               OpReturnValue %444
               OpFunctionEnd
%compare_int16_t_i1_i1_ = OpFunction %bool None %58
       %a_18 = OpFunctionParameter %_ptr_Function_int
       %b_18 = OpFunctionParameter %_ptr_Function_int
        %133 = OpLabel
        %447 = OpLoad %int %a_18
        %448 = OpLoad %int %b_18
        %449 = OpIEqual %bool %447 %448
               OpReturnValue %449
               OpFunctionEnd
%compare_i16vec2_vi2_vi2_ = OpFunction %bool None %136
       %a_19 = OpFunctionParameter %_ptr_Function_v2int
       %b_19 = OpFunctionParameter %_ptr_Function_v2int
        %140 = OpLabel
        %452 = OpLoad %v2int %a_19
        %453 = OpLoad %v2int %b_19
        %454 = OpIEqual %v2bool %452 %453
        %455 = OpAll %bool %454
               OpReturnValue %455
               OpFunctionEnd
%compare_i16vec3_vi3_vi3_ = OpFunction %bool None %65
       %a_20 = OpFunctionParameter %_ptr_Function_v3int
       %b_20 = OpFunctionParameter %_ptr_Function_v3int
        %144 = OpLabel
        %458 = OpLoad %v3int %a_20
        %459 = OpLoad %v3int %b_20
        %460 = OpIEqual %v3bool %458 %459
        %461 = OpAll %bool %460
               OpReturnValue %461
               OpFunctionEnd
%compare_i16vec4_vi4_vi4_ = OpFunction %bool None %147
       %a_21 = OpFunctionParameter %_ptr_Function_v4int
       %b_21 = OpFunctionParameter %_ptr_Function_v4int
        %151 = OpLabel
        %464 = OpLoad %v4int %a_21
        %465 = OpLoad %v4int %b_21
        %466 = OpIEqual %v4bool %464 %465
        %467 = OpAll %bool %466
               OpReturnValue %467
               OpFunctionEnd
%compare_float16_t_f1_f1_ = OpFunction %bool None %9
       %a_22 = OpFunctionParameter %_ptr_Function_float
       %b_22 = OpFunctionParameter %_ptr_Function_float
        %155 = OpLabel
        %470 = OpLoad %float %a_22
        %471 = OpLoad %float %b_22
        %472 = OpFSub %float %470 %471
        %473 = OpExtInst %float %1 FAbs %472
        %474 = OpFOrdLessThan %bool %473 %float_0_0500000007
               OpReturnValue %474
               OpFunctionEnd
%compare_f16vec2_vf2_vf2_ = OpFunction %bool None %16
       %a_23 = OpFunctionParameter %_ptr_Function_v2float
       %b_23 = OpFunctionParameter %_ptr_Function_v2float
        %159 = OpLabel
   %param_39 = OpVariable %_ptr_Function_float Function
   %param_40 = OpVariable %_ptr_Function_float Function
   %param_41 = OpVariable %_ptr_Function_float Function
   %param_42 = OpVariable %_ptr_Function_float Function
        %478 = OpAccessChain %_ptr_Function_float %a_23 %uint_0
        %479 = OpLoad %float %478
               OpStore %param_39 %479
        %481 = OpAccessChain %_ptr_Function_float %b_23 %uint_0
        %482 = OpLoad %float %481
               OpStore %param_40 %482
        %483 = OpFunctionCall %bool %compare_float_f1_f1_ %param_39 %param_40
               OpSelectionMerge %485 None
               OpBranchConditional %483 %484 %485
        %484 = OpLabel
        %487 = OpAccessChain %_ptr_Function_float %a_23 %uint_1
        %488 = OpLoad %float %487
               OpStore %param_41 %488
        %490 = OpAccessChain %_ptr_Function_float %b_23 %uint_1
        %491 = OpLoad %float %490
               OpStore %param_42 %491
        %492 = OpFunctionCall %bool %compare_float_f1_f1_ %param_41 %param_42
               OpBranch %485
        %485 = OpLabel
        %493 = OpPhi %bool %483 %159 %492 %484
               OpReturnValue %493
               OpFunctionEnd
%compare_f16vec3_vf3_vf3_ = OpFunction %bool None %23
       %a_24 = OpFunctionParameter %_ptr_Function_v3float
       %b_24 = OpFunctionParameter %_ptr_Function_v3float
        %163 = OpLabel
   %param_43 = OpVariable %_ptr_Function_float Function
   %param_44 = OpVariable %_ptr_Function_float Function
   %param_45 = OpVariable %_ptr_Function_float Function
   %param_46 = OpVariable %_ptr_Function_float Function
   %param_47 = OpVariable %_ptr_Function_float Function
   %param_48 = OpVariable %_ptr_Function_float Function
        %497 = OpAccessChain %_ptr_Function_float %a_24 %uint_0
        %498 = OpLoad %float %497
               OpStore %param_43 %498
        %500 = OpAccessChain %_ptr_Function_float %b_24 %uint_0
        %501 = OpLoad %float %500
               OpStore %param_44 %501
        %502 = OpFunctionCall %bool %compare_float_f1_f1_ %param_43 %param_44
               OpSelectionMerge %504 None
               OpBranchConditional %502 %503 %504
        %503 = OpLabel
        %506 = OpAccessChain %_ptr_Function_float %a_24 %uint_1
        %507 = OpLoad %float %506
               OpStore %param_45 %507
        %509 = OpAccessChain %_ptr_Function_float %b_24 %uint_1
        %510 = OpLoad %float %509
               OpStore %param_46 %510
        %511 = OpFunctionCall %bool %compare_float_f1_f1_ %param_45 %param_46
               OpBranch %504
        %504 = OpLabel
        %512 = OpPhi %bool %502 %163 %511 %503
               OpSelectionMerge %514 None
               OpBranchConditional %512 %513 %514
        %513 = OpLabel
        %516 = OpAccessChain %_ptr_Function_float %a_24 %uint_2
        %517 = OpLoad %float %516
               OpStore %param_47 %517
        %519 = OpAccessChain %_ptr_Function_float %b_24 %uint_2
        %520 = OpLoad %float %519
               OpStore %param_48 %520
        %521 = OpFunctionCall %bool %compare_float_f1_f1_ %param_47 %param_48
               OpBranch %514
        %514 = OpLabel
        %522 = OpPhi %bool %512 %504 %521 %513
               OpReturnValue %522
               OpFunctionEnd
%compare_f16vec4_vf4_vf4_ = OpFunction %bool None %30
       %a_25 = OpFunctionParameter %_ptr_Function_v4float
       %b_25 = OpFunctionParameter %_ptr_Function_v4float
        %167 = OpLabel
   %param_49 = OpVariable %_ptr_Function_float Function
   %param_50 = OpVariable %_ptr_Function_float Function
   %param_51 = OpVariable %_ptr_Function_float Function
   %param_52 = OpVariable %_ptr_Function_float Function
   %param_53 = OpVariable %_ptr_Function_float Function
   %param_54 = OpVariable %_ptr_Function_float Function
   %param_55 = OpVariable %_ptr_Function_float Function
   %param_56 = OpVariable %_ptr_Function_float Function
        %526 = OpAccessChain %_ptr_Function_float %a_25 %uint_0
        %527 = OpLoad %float %526
               OpStore %param_49 %527
        %529 = OpAccessChain %_ptr_Function_float %b_25 %uint_0
        %530 = OpLoad %float %529
               OpStore %param_50 %530
        %531 = OpFunctionCall %bool %compare_float_f1_f1_ %param_49 %param_50
               OpSelectionMerge %533 None
               OpBranchConditional %531 %532 %533
        %532 = OpLabel
        %535 = OpAccessChain %_ptr_Function_float %a_25 %uint_1
        %536 = OpLoad %float %535
               OpStore %param_51 %536
        %538 = OpAccessChain %_ptr_Function_float %b_25 %uint_1
        %539 = OpLoad %float %538
               OpStore %param_52 %539
        %540 = OpFunctionCall %bool %compare_float_f1_f1_ %param_51 %param_52
               OpBranch %533
        %533 = OpLabel
        %541 = OpPhi %bool %531 %167 %540 %532
               OpSelectionMerge %543 None
               OpBranchConditional %541 %542 %543
        %542 = OpLabel
        %545 = OpAccessChain %_ptr_Function_float %a_25 %uint_2
        %546 = OpLoad %float %545
               OpStore %param_53 %546
        %548 = OpAccessChain %_ptr_Function_float %b_25 %uint_2
        %549 = OpLoad %float %548
               OpStore %param_54 %549
        %550 = OpFunctionCall %bool %compare_float_f1_f1_ %param_53 %param_54
               OpBranch %543
        %543 = OpLabel
        %551 = OpPhi %bool %541 %533 %550 %542
               OpSelectionMerge %553 None
               OpBranchConditional %551 %552 %553
        %552 = OpLabel
        %555 = OpAccessChain %_ptr_Function_float %a_25 %uint_3
        %556 = OpLoad %float %555
               OpStore %param_55 %556
        %558 = OpAccessChain %_ptr_Function_float %b_25 %uint_3
        %559 = OpLoad %float %558
               OpStore %param_56 %559
        %560 = OpFunctionCall %bool %compare_float_f1_f1_ %param_55 %param_56
               OpBranch %553
        %553 = OpLabel
        %561 = OpPhi %bool %551 %543 %560 %552
               OpReturnValue %561
               OpFunctionEnd
```

</details>
## Runtime Execution and Result Checking

- Before shader execution, delayed initialization flattens every generated shared-object member and generates expected values for
  each reference entry [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L502-L519).
- The host creates a 4-byte storage buffer with `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT`, allocates host-visible memory, binds it, and
  clears it to zero [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L367-L388).
- That buffer is bound as descriptor binding `0`; no descriptor is created for the generated GLSL `shared` objects
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L389-L417).
- The host creates a compute pipeline from the generated shader module, binds the pipeline and descriptor set, and dispatches one
  workgroup with `vkCmdDispatch(1, 1, 1)`
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L419-L468).
- The device increments `passed` only if every generated field comparison succeeds
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L327-L340).
- After execution, the host invalidates the allocation, reads the counter, and requires `passed == 1`. Any other value is logged as
  an incorrect counter value and fails the case
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L470-L488).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| GLSL `shared` objects | No host-side resource | No descriptor | Written and read in the compute shader | No | Actual tested shared-memory layout. |
| `passed` storage buffer | Yes | Descriptor binding `0` | Incremented if all checks pass | Yes | Only host-visible result channel. |
| Generated compute pipeline | Yes | Pipeline state | Executes generated code | No | Contains struct declarations, writes, barriers, and comparisons. |
| Images, samplers, attachments, expected-value buffers | No | No | No | No | Not part of this test design. |

## Case Pruning

### Requirement-based pruning

- Base shared-layout cases do not add an explicit Vulkan memory-model feature gate in the inspected support function
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L347-L358).
- If either 16-bit or 8-bit types are enabled, the device must support `VK_KHR_shader_float16_int8`
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L347-L351).
- `16bit` cases additionally require the Vulkan 1.2 `shaderFloat16` feature
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L353-L355).
- `8bit` cases additionally require the Vulkan 1.2 `shaderInt8` feature
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L353-L357).

### Design-based pruning

- The generator uses layout-node feature flags to decide which shapes are meaningful for each layout node: arrays are disabled outside array
  nodes, arrays-of-arrays are disabled outside the corresponding nodes, and struct recursion is enabled only for struct
  nodes [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L145-L153).
- Array length is zero when arrays are not enabled and at most three when arrays are enabled, keeping random layouts bounded while
  still producing indexable shared-memory paths
  [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L108-L113).
- The dispatch shape is intentionally fixed to one local invocation and one workgroup. This makes the test a shared-memory layout
  and access test rather than a multi-invocation communication test
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L282-L285),
  [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L464-L468).

## Key Takeaways

- `memory_model.shared` tests GLSL workgroup shared-memory layout and access correctness, not descriptor-backed buffer or image
  resources.
- The host generates shader source containing shared-object declarations, expected-value assignments, barriers, and comparisons;
  the host does not upload expected values into a shared-memory resource.
- Complex structures are flattened into leaf checks so nested structs, arrays, matrices, and vectors can be validated field by
  field.
- `16bit` and `8bit` are real intermediate nodes that repeat the first seven layout nodes with additional
  narrow-type candidates and feature requirements.
- Failures can indicate wrong shared-memory layout/addressing, incorrect compiler lowering for shared-memory objects, incorrect
  narrow-type promotion/comparison behavior, or broken shader-side write/read synchronization around the generated barrier pattern.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `shared` test family attachment | [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2410-L2413) | Adds the delegated `shared` test family under the `memory_model` test category. |
| Shared-layout hierarchy creation | [createSharedMemoryLayoutTests()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L287-L330) | Builds the base, `16bit`, and `8bit` intermediate node hierarchy. |
| Random test case creation | [createRandomCaseGroup()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L94-L105) | Creates 10 deterministic random test cases per layout node and applies the command-line base seed. |
| Random case constructor | [RandomSharedLayoutCase::RandomSharedLayoutCase()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L108-L124) | Enables narrow-type flags, chooses the number of shared objects, and starts case initialization. |
| Shared object generation | [generateSharedMemoryObject()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L134-L160) | Creates `S1` / `s1`-style shared-object structs and members. |
| Random recursive type generation | [generateType()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L162-L285) | Chooses basic, vector, matrix, array, and nested struct field types. |
| Layout flattening | [computeReferenceLayout()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L55-L88) | Converts generated layouts into reference entries for leaf checks. |
| Expected value generation | [generateValue()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L90-L139) | Produces the small constants embedded into generated shader code. |
| Assignment and comparison emission | [generateSharedMemoryWrites()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L197-L269) | Emits both shared-memory writes and comparison statements. |
| Compute shader assembly | [generateComputeShader()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L271-L345) | Builds the full generated GLSL compute shader. |
| Support checks | [SharedLayoutCase::checkSupport()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L347-L358) | Gates 16-bit and 8-bit cases on extension and feature support. |
| Runtime execution | [SharedLayoutCaseInstance::iterate()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L360-L489) | Creates the result buffer, dispatches the shader, and checks `passed == 1`. |
| Deferred shader setup | [SharedLayoutCase::delayedInit()](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L502-L519) | Flattens layouts, generates values, and stores the generated compute shader source. |
| Compare helper utilities | [vktTypeComparisonUtil.cpp](../../../modules/vulkan/util/vktTypeComparisonUtil.cpp#L34-L248) | Supplies comparison helper text and promotion rules for narrow types. |
