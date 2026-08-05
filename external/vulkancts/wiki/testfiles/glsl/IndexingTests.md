## Overview

`vktShaderRenderIndexingTests.cpp` implements the `glsl.indexing` shader-render test family. It generates GLSL ES 3.10 vertex/fragment shader pairs that exercise indexing of arrays, vector components, and matrix columns. Each generated shader is checked against a matching software evaluator by the shared shader-render harness. The family is registered directly below `glsl` by [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1263), and `createIndexingTests()` returns the `indexing` group at [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1357-L1360).

The page covers the five direct children, their generated case dimensions, shader data flow, host-side uniforms, result comparison, and the deliberate omissions in the registration loops.

## Background Knowledge

The tests compare several equivalent GLSL ways to select an element:

- **Static indexing:** a literal index such as `arr[0]`.
- **Dynamic indexing:** an index loaded from an integer uniform.
- **Static loop indexing:** a loop whose bound is a literal `4`.
- **Dynamic loop indexing:** a loop whose bound is an integer uniform.
- **Const write:** a local-array write using literal constructors; this mode is generated only for temporary-array writes.

A varying-array case writes an array in the vertex shader and reads it in the fragment shader. The other families can place the operation in either shader stage; the other stage passes the result through a varying. These are shader-render tests, so correctness is judged from rendered colors rather than by inspecting generated SPIR-V.

## Registration Hierarchy

```text
glsl.indexing
├── varying_array
├── uniform_array
├── tmp_array
├── vector_subscript
└── matrix_subscript
```

`ShaderIndexingTests::init()` creates these five children and adds generated leaves to each at [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1192-L1353). The factory is added without the `CTS_USES_VULKANSC` guard used by neighboring demote and bfloat16 families at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1261).

## Parameter Dimensions and Observed Values

| Dimension | Values and effect |
|---|---|
| Array element types | `float`, `vec2`, `vec3`, `vec4`, from `s_floatAndVecTypes` at [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1194-L1197). |
| Array access names | `static`, `dynamic`, `static_loop`, `dynamic_loop`, `const`, from `getIndexAccessTypeName()` at [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L45-L65). `const` is the final enum value so most loops can stop before it. |
| Shader stages | `vertex` and `fragment`, from `s_shaderTypes` at [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1192-L1195). |
| Vector types | `vec2`, `vec3`, `vec4`, crossed with six vector access modes: `direct`, `component`, `static_subscript`, `dynamic_subscript`, `static_loop_subscript`, `dynamic_loop_subscript`, at [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L67-L90). |
| Matrix types | `mat2`, `mat2x3`, `mat2x4`, `mat3x2`, `mat3`, `mat3x4`, `mat4x2`, `mat4x3`, `mat4`, at [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1321-L1323). |
| Dynamic-index uniforms | `ui_zero` through `ui_four`, bound at descriptor bindings 0 through 4 by [`IndexingTestUniformSetup::setup()`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L203-L210). |

Generated leaf naming is consistent with the registration code:

```text
<type>_<write_access>_write_<read_access>_read_<shader_stage>
```

The exceptions are `varying_array`, whose names are `<type>_<vertex_access>_write_<fragment_access>_read`, and `uniform_array`, whose names are `<type>_<read_access>_read_<shader_stage>` ([`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1209-L1214), [`#L1232-L1240`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1232-L1240)).

## Behavior Parameters

### `varying_array`: cross-stage array access

This child generates four element types × four vertex write modes × four fragment read modes. Both write and read loops stop before `INDEXACCESS_CONST` at [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1202-L1217). The vertex builder declares a four-element output array, writes values derived from `a_coords`, and passes it to the fragment shader. Static and dynamic writes use four explicit assignments; loop writes use either a literal `4` bound or `ui_four` ([`#L280-L335`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L280-L335)). The fragment shader sums the four selected elements and writes the result to `o_color` ([`#L337-L381`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L337-L381)).

### `uniform_array`: uniform-buffer array reads

This child generates four element types × four read modes × two shader stages. The builder chooses the vertex or fragment stream with `std::ostringstream &op = isVertexCase ? vtx : frag` ([`#L408-L415`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L408-L415)). It declares `u_arr[4]` in a uniform block at binding 5, reads its four elements using the selected access form, and sums them ([`#L434-L481`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L434-L481)). When the case is a vertex variant, the computed color is carried to the fragment shader; when it is a fragment variant, the fragment shader performs the read directly.

`IndexingTestUniformSetup` uploads four `Vec4` slots at binding 5. The slots contain the same coordinate-derived value scaled by `1.0`, `0.5`, `0.25`, and `0.125`, adapted to the selected scalar/vector type ([`#L211-L246`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L211-L246)).

### `tmp_array`: local temporary-array writes and reads

This child generates four element types × five write modes × four read modes × two shader stages. The write loop includes `const` (`INDEXACCESS_LAST`), while the read loop stops before it ([`#L1249-L1274`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1249-L1274)). The builder declares a local `arr[]`, writes it using explicit indices, uniform indices, or static/dynamic loops, then reads and reduces it in the selected stage ([`#L522-L650`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L522-L650)). Const writes use literal constructors and expand the local array to 40 elements so unused positions can be filled safely ([`#L582-L599`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L671-L678)). The evaluator uses uniform coordinates for const-write cases and coordinate values for the other write modes ([`#L695-L702`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L695-L702)).

### `vector_subscript`: vector component selection

This child crosses `vec2`, `vec3`, and `vec4` with all six write modes, all six read modes, and both shader stages ([`#L1282-L1314`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1282-L1314)). The direct mode uses a vector expression/swizzle; component mode names individual components; the remaining modes use literal, uniform, literal-loop, or uniform-loop subscripts. Dynamic-index uniforms are emitted only for components that exist for the selected vector length ([`#L733-L776`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L733-L776)). The read path reduces the vector to a scalar sum through `dot()`, component reads, subscripts, or loops ([`#L787-L888`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L787-L888)).

### `matrix_subscript`: matrix-column selection

This child crosses nine matrix shapes with four write modes, four read modes, and both shader stages ([`#L1317-L1351`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1317-L1351)). For each shape, `createMatrixSubscriptCase()` derives the column count, row count, column-vector type, and dynamic-loop uniform name ([`#L997-L1009`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L997-L1009)). It writes matrix columns by literal index, uniform index, literal-bounded loop, or uniform-bounded loop, then reads and sums columns using the corresponding read form ([`#L1053-L1130`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1053-L1130)). Matrix-shape-specific evaluators account for rectangular matrices as well as square ones ([`#L926-L995`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L926-L995)).

## Shader Analysis

All five builders emit `#version 310 es` sources. They use position and coordinate vertex inputs, explicit locations for stage interfaces, and `mediump` values for tested arrays/vectors/matrices. Uniform declarations are added conditionally: dynamic access needs bindings 0–3, dynamic-loop access needs binding 4, and uniform-array data uses binding 5. Representative declarations and source construction are visible in the array, vector, and matrix builders at [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L284-L350), [`#L745-L776`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L745-L776), and [`#L1011-L1042`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1011-L1042).

The generated computation follows one invariant: four values are written with weights `1.0`, `0.5`, `0.25`, and `0.125`, then all four are read and summed. The expected scale is therefore `1.875`. Array evaluators implement this as `1.875f * coords` or `1.875f * constCoords` depending on whether the case uses interpolated or constant coordinates ([`#L92-L154`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L92-L154)). Vector evaluators sum the selected weighted components ([`#L707-L731`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L707-L731)); matrix evaluators apply shape-dependent column reductions ([`#L926-L995`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L926-L995)).

## Runtime Execution and Result Checking

`ShaderIndexingCase` derives from `ShaderRenderCase`, installs the selected evaluator, generated vertex and fragment sources, and `IndexingTestUniformSetup` ([`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L249-L272)). The shared case registers the generated GLSL programs and creates `ShaderRenderCaseInstance` ([`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L632)).

At iteration time, the harness creates the quad grid, renders the generated shaders, computes a vertex- or fragment-stage software reference according to `m_isVertexCase`, and compares the two images with an error threshold of `0.2f` ([`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805)). The reference evaluator runs once per pixel after the evaluation context is reset for that pixel; the clear color is used only if an evaluator marks the pixel discarded ([`#L2692-L2718`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2718)). The default comparison is `tcu::fuzzyCompare()`; non-fuzzy mode uses `tcu::pixelThresholdCompare()` ([`#L2721-L2730`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).

## Failure Meaning

A failure is an image mismatch, so it indicates that a generated indexing form did not produce the same color as the evaluator. The case name identifies the likely axis:

- `static` versus `dynamic` failures point to literal versus uniform-driven index handling.
- `static_loop` or `dynamic_loop` failures point to indexing inside a loop or to the loop bound.
- `varying_array` failures can involve either the vertex write or fragment read side, because both are independently varied.
- `uniform_array` failures additionally implicate uniform-buffer array layout or binding 5.
- `vector_subscript` failures implicate component/swizzle selection or vector-length-specific dynamic indices.
- `matrix_subscript` failures implicate column selection, rectangular matrix shape, or stage placement.

The implementation does not define a file-local `checkSupport()` override. Support behavior therefore comes from the shared shader-render setup and shader compilation path; no indexing-specific feature or extension gate is present in the inspected source ([`ShaderIndexingCase`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L251-L272)).

## Case Pruning

The registration code intentionally omits combinations rather than generating every enum cross-product:

- `const` is omitted from varying-array, uniform-array, temporary-array reads, and matrix access loops because those loops stop at `INDEXACCESS_CONST`.
- `const` exists only as a temporary-array write mode.
- Vector `direct` and `component` are valid vector-specific modes, so they use `VectorAccessType` rather than the array access enum.
- Matrix cases use the four non-const array access modes and do not generate a const matrix access.
- Dynamic uniforms are declared only when the selected builder needs them, avoiding irrelevant descriptors in static cases.

These restrictions are visible in the `init()` loops and conditional shader declarations at [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1202-L1217), [`#L1227-L1242`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1227-L1242), [`#L1253-L1274`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1253-L1274), and [`#L1325-L1346`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1325-L1346).

## Key Takeaways

- `glsl.indexing` tests semantic equivalence of direct, uniform-driven, and loop-based indexing forms across arrays, vector components, and matrix columns.
- The direct hierarchy separates cross-stage varyings, uniform arrays, local arrays, vector subscripts, and matrix subscripts.
- The generated names expose the tested type, write/read access modes, and shader stage, making a mismatch diagnosable from its CTS path.
- Uniform setup supplies deterministic index selectors and weighted data; software evaluators independently reconstruct the expected color.
- Pass/fail is based on rendered-image comparison, not shader compilation success alone.

## Source Reference Appendix

- Registration and all generated combinations: [`ShaderIndexingTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1192-L1353)
- Access-mode enums and names: [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L45-L90)
- Uniform setup and case wrapper: [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L186-L272)
- Array shader builders: [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L280-L702)
- Vector builder and evaluator: [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L707-L921)
- Matrix builder and evaluator: [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L926-L1166)
- GLSL package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1263)
- Shared shader-render execution and comparison: [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L632), [`#L773-L805`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [`#L2692-L2730`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2730)


