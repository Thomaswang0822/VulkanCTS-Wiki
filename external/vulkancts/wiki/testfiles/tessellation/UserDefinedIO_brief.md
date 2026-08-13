# Understanding Brief: `tessellation.user_defined_io`

## One-Sentence Test Purpose

This test checks whether user-defined values written by a tessellation control shader arrive unchanged at the tessellation evaluation shader across per-patch, per-vertex, array, structure, and interface-block declaration forms.

## Background Knowledge

### Tessellation control-to-evaluation interfaces

A tessellation control shader consumes an input patch and produces an output patch. Each control-shader invocation owns one output control point and may also produce data shared by the patch. A tessellation evaluation shader later receives the output patch and runs for tessellator-generated coordinates. The stage roles and output-patch model are defined in [Tessellation Control Shaders](../../../../vulkan-docs/src/chapters/shaders.adoc#L2576-L2586) and [Tessellation Evaluation Shaders](../../../../vulkan-docs/src/chapters/shaders.adoc#L2668-L2681).

Why it matters here:

- A per-vertex output is an array at the receiving tessellation stage, with one element for each output control point.
- A per-patch output has one value for the patch and uses the GLSL `patch` qualifier.
- The producer and consumer must agree on locations, type structure, array shape, and per-patch status. Vulkan requires user-defined input and output interface variables to use `Location` and defines matching in terms of equivalent decorations and types in [User-Defined Variable Interface and Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L104-L180).

### Basic subobjects and diagnostic indexing

The generator recursively visits scalar/vector leaves inside variables, arrays, structures, and interface blocks. In this implementation, each visited scalar or vector is one "basic subobject." The control shader assigns a deterministic sequence beginning at `1.3`, advancing by `0.4` per basic subobject; vector components add `0.8` offsets. The evaluation shader regenerates the same sequence and records the first basic-subobject index whose value differs. [`glslTraverseBasicTypes()` and its assign/check visitors](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L120-L195) implement this traversal.

Why it matters here:

- Nested declarations are checked leaf by leaf instead of only through a rendered color.
- The returned index maps a failure to an exact variable, array element, block member, or nested structure member.

## One Concrete Example

Consider:

```text
dEQP-VK.tessellation.user_defined_io.per_vertex.vertex_io_array_size_spec_min.triangles
```

The tessellation control shader declares per-vertex outputs similar to the following reconstructed fragment:

```glsl
struct S {
    highp int x;
    highp vec4 y;
};

layout(location = 2) out S in_te_s[];
layout(location = 4) out highp float in_te_f[];
layout(location = 0) in highp float in_tc_attr[32];
```

The matching evaluation inputs use arrays with an explicit capacity of 32:

```glsl
layout(location = 2) in S in_te_s[32];
layout(location = 4) in highp float in_te_f[32];
```

Only five elements carry output-patch values because the control shader declares `layout(vertices = 5) out`. Each control invocation writes its `gl_InvocationID` element. The evaluation shader checks all five produced elements, not all 32 declared slots. The source selects 32 because that is the minimum required `maxTessellationPatchSize`; the limit and its minimum are documented in [Tessellation Limits](../../../../vulkan-docs/src/chapters/limits.adoc#L430-L458) and the limits table at [`maxTessellationPatchSize`](../../../../vulkan-docs/src/chapters/limits.adoc#L6622-L6632).

This example is reconstructed from the declaration and traversal branches in [`UserDefinedIOTest::UserDefinedIOTest()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L478-L665). It shows that explicit capacity changes the declaration form without changing the five values that the test expects the output patch to contain.

## End-to-End Test Flow

```text
[host] select one IO form, one array-size spelling, and one primitive type
[host] generate matching vertex, tessellation-control, tessellation-evaluation, and fragment shaders
[host] fill a ten-float vertex buffer with inner/outer tessellation levels and image placement values
[host] allocate a host-visible SSBO for an invocation count and one diagnostic index per possible evaluation invocation
[host] create a black 256 x 256 color target and a host-visible image readback buffer
[host] build a four-stage patch pipeline with ten input control points
[host] draw one patch
[device] run five tessellation-control invocations and assign deterministic values to every generated user-defined output leaf
[device] tessellate the patch using the fixed equal-spacing levels
[device] compare every user-defined evaluation input leaf with the expected deterministic sequence
[device] color correct evaluations green and incorrect evaluations red, then atomically append each diagnostic index to the SSBO
[host] wait, copy and invalidate the result allocations, and compare the rendered image with the primitive-specific PNG
[host] require at least the reference number of unique evaluation vertices
[host] require every returned diagnostic index to equal the number of checked inputs
[host] pass only when the invocation, diagnostic, and image checks all succeed
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

[`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L668-L770) generates four GLSL ES 3.10 stages:

- The vertex shader forwards each scalar attribute.
- The tessellation control shader emits five output vertices, writes deterministic user-defined values, copies tessellation levels, and supplies patch-wide image placement.
- The tessellation evaluation shader checks all generated user-defined inputs, emits green or red, and writes one diagnostic index to an SSBO per invocation.
- The fragment shader forwards the selected color.
- Runtime verification loads one of three reference PNGs selected by primitive type.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Ten-float vertex buffer | yes | yes | vertex/TCS read | no | Supplies positive tessellation levels plus scale and offset values. |
| Diagnostic SSBO at set 0, binding 0 | yes | yes | atomic and indexed writes in tessellation evaluation | yes | Records invocation count and first failed basic-subobject index for each evaluation invocation. |
| `VK_FORMAT_R8G8B8A8_UNORM` color image | yes | yes, as color attachment | fragment write | indirectly | Shows the expected tessellated primitive in green; a shader mismatch changes fragments to red. |
| Host-visible color buffer | yes | transfer destination | transfer write | yes | Receives the rendered image for fuzzy comparison. |
| User-defined TCS outputs and TES inputs | no | shader-stage interface | TCS writes, TES reads | no | Carry the values under test; they are interface variables rather than descriptor-backed resources. |
| Primitive reference PNG | loaded by host | no | no | host reads | Supplies the expected 256 by 256 image for isolines, quads, or triangles. |

## What Is Checked

- [`referenceVertexCount()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L803-L810) supplies both the maximum result-buffer capacity and a minimum unique-vertex count. The observed evaluation invocation count must be at least the unique count.
- Every diagnostic value must lie in `[0, numTEInputs]`. A value below `numTEInputs` identifies the first mismatching basic subobject; a value above it is invalid. [`iterate()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L969-L1015) performs this scan and resolves an index back to a declaration path.
- [`tcu::fuzzyCompare()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L950-L967) compares the rendered image against the primitive-specific PNG with threshold `0.02`.
- The final result passes only if no invocation-count or diagnostic check returned early and the image comparison succeeds.

## Behavior Parameter Identification

> **Behavior parameter:** `IO form`
>
> **Candidate values:** `per_patch`, `per_patch_array`, `per_patch_block`, `per_patch_block_array`, `per_vertex`, `per_vertex_block`

IO form is the primary behavioral axis because it changes whether data belongs to a whole patch or to individual control points, whether the top-level object is singular or arrayed, and whether members travel as standalone variables or through an interface block. Array-size spelling and primitive type broaden declaration and tessellator coverage without changing that central transport contract.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `per_patch` | Incorrect matching or transport of singular `patch`-qualified structure/scalar variables. |
| `per_patch_array` | Incorrect matching, indexing, or transport of a `patch`-qualified standalone array. |
| `per_patch_block` | Incorrect matching or member layout/transport for a singular `patch`-qualified interface block. |
| `per_patch_block_array` | Incorrect matching, element indexing, or member transport for an array of `patch`-qualified interface blocks. |
| `per_vertex` | Incorrect invocation-to-element writes or transport of standalone per-vertex structure/scalar arrays. |
| `per_vertex_block` | Incorrect invocation-to-element writes, matching, or nested member transport for a per-vertex interface-block array. |

All six values also depend on the shared shader generator, tessellation execution, SSBO diagnostics, rasterization, synchronization, copyback, and image comparison paths.

## Important Variations and Special Cases

- The registration matrix contains 54 test cases: six IO forms, three array-size spellings, and three primitive types. [`createUserDefinedIOTests()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1031-L1087) generates the matrix, which appears in [`vk-default/tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L1002-L1055).
- `vertex_io_array_size_implicit` leaves the relevant per-vertex input arrays unsized. `vertex_io_array_size_shader_builtin` spells their capacity as `gl_MaxPatchVertices`. `vertex_io_array_size_spec_min` spells it as `32`. The dimension always changes the tessellation-control input declaration and also changes the evaluation declaration for per-vertex IO forms.
- Primitive type changes the evaluation shader's `layout(... ) in`, the number of generated vertices, and the reference image. It does not change the user-defined declaration form or comparison sequence.
- Standalone structures do not contain array members because the generator records that such an output declaration is illegal. Block forms add a two-float array member to the nested structure. The `per_patch_array` form omits the standalone structure variable because an array of structures is disallowed in that form. [`UserDefinedIOTest::UserDefinedIOTest()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L514-L563) encodes these choices.
- `per_patch_block_array` uses a smaller block without the direct `blockS` member so the generated declaration stays within limited per-patch output storage. It still contains nested arrays through `blockFa` and `blockSa`.
- The port did not include negative compile tests because its shader-library path cannot represent expected shader-compilation failures. The source records this scope boundary next to registration at [`createUserDefinedIOTests()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1027-L1031).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Constants, IO forms, array-size forms | [`Constants`, `IOType`, `VertexIOArraySize`, and `CaseDefinition`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L60-L97) | Defines the fixed sizes and all generated dimensions. |
| Recursive object traversal | [`TopLevelObject`, `glslTraverseBasicTypes()`, and visitors](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L102-L243) | Defines deterministic assignment and comparison by basic subobject. |
| Standalone variables and blocks | [`Variable` and `IOBlock`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L245-L452) | Generates declarations, traversal code, counts, and diagnostic names. |
| Case-specific interface generation | [`UserDefinedIOTest::UserDefinedIOTest()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L478-L665) | Selects qualifiers, arrays, blocks, locations, and expected values. |
| Shader generation | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L668-L770) | Produces the four GLSL stages and device-side validation. |
| Runtime and checks | [`UserDefinedIOTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L792-L1018) | Creates resources, draws, reads back, and decides pass/fail. |
| Registration matrix | [`createUserDefinedIOTests()`](../../../modules/vulkan/tessellation/vktTessellationUserDefinedIO.cpp#L1027-L1087) | Generates all 54 test paths and records unported negative-test scope. |
| Interface semantics | [User-Defined Variable Interface and Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L104-L180) | Grounds location, decoration, and type matching. |
| Tessellation stage semantics | [Tessellation Control and Evaluation Shaders](../../../../vulkan-docs/src/chapters/shaders.adoc#L2576-L2681) | Grounds output patches, per-patch data, invocation roles, and evaluation execution. |
| Mustpass inventory | [`vk-default/tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L1002-L1055) | Confirms the complete registered Vulkan path matrix. |

## Questions / Risk Points for User Audit

- Is `IO form` the clearest primary behavioral axis, given that it changes ownership and declaration structure while the other dimensions extend coverage?
- Is the distinction between declared per-vertex array capacity and the five produced output-patch elements explicit enough?
- Does the diagnostic explanation make clear that the SSBO stores one first-failure index per evaluation invocation?
- Are the intentional structure/array exclusions described as design boundaries rather than runtime pruning?
- Is image comparison presented as a second observable result rather than the only user-defined IO check?

No unresolved source, specification, or mustpass risk changes the test purpose, representative shader choice, or validation claims.

## Conversion Notes for Final Wiki Rewrite

- Distill stage-interface matching and basic-subobject indexing into short Background Knowledge bullets.
- Use `per_vertex.vertex_io_array_size_spec_min.triangles` for one representative walkthrough. It exposes per-invocation element writes, explicit array capacity, nested structure transport, and device-side diagnostics without the larger block traversal.
- Carry `IO form` and all six exact registered values into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table above unchanged into the final page, then add source/spec-grounded cause analysis.
- Keep the 54-case matrix compact: the parseable registration tree should list the six direct IO-form children, while later tables describe array-size and primitive dimensions.
- Preserve the resource and validation facts as concise runtime prose. Keep source navigation in the appendix.
