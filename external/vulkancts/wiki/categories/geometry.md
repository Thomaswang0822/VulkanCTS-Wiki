# geometry

## Overview

The [`geometry`](../../modules/vulkan/geometry/vktGeometryTests.cpp:36) category documents Vulkan geometry-shader tests registered by [`createTests()`](../../modules/vulkan/geometry/vktGeometryTests.cpp:56). In the inspected files, this category focuses on input primitive handling, emitted geometry shape/count, layered rendering, instanced geometry-shader invocations, varying propagation, explicit [`EmitVertex()`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:199) / [`EndPrimitive()`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:204) behavior, and selected built-in-variable behavior.

## Registration Entry Point

The category is rooted in [`createChildren()`](../../modules/vulkan/geometry/vktGeometryTests.cpp:41), which adds seven subgroups:

```text
geometry
├── input
├── basic
├── layered
├── instanced
├── varying
├── emit
└── builtin_variable
```

Source: [`vktGeometryTests.cpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp:41).

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktGeometryTests.cpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp:1) | Registration | Top-level geometry category registration |
| [`vktGeometryInputGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:1) | Implementation | Input primitive expansion and conversion coverage |
| [`vktGeometryBasicGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:1) | Implementation | Output-count, varying-output-count, and side-effect cases |
| [`vktGeometryLayeredRenderingTests.cpp`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1) | Implementation | Layered rendering, [`gl_Layer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:943), multi-layer content, and readback checks |
| [`vktGeometryInstancedRenderingTests.cpp`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp:1) | Implementation | Instanced draw + geometry-shader invocation combinations |
| [`vktGeometryVaryingGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:1) | Implementation | Vertex-to-geometry-to-fragment varying propagation cases |
| [`vktGeometryEmitGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:1) | Implementation | Emit/end primitive sequencing across output topologies |
| [`vktGeometryBuiltinVariableGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:1) | Implementation | Built-in variable cases such as point size and primitive IDs |
| [`vktGeometryTestsUtil.hpp`](../../modules/vulkan/geometry/vktGeometryTestsUtil.hpp:47) | Helper | Shared primitive mapping, image helpers, comparison helpers |
| [`vktGeometryTestsUtil.cpp`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:306) | Helper | GLSL topology mapping and fuzzy/file-image comparison helpers |
| [`vktGeometryBasicClass.hpp`](../../modules/vulkan/geometry/vktGeometryBasicClass.hpp:37) | Helper | Shared [`GeometryExpanderRenderTestInstance`](../../modules/vulkan/geometry/vktGeometryBasicClass.hpp:37) base |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktGeometryTests.cpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp:1) | [`vktGeometryTests.md`](../testfiles/geometry/vktGeometryTests.md) |
| [`vktGeometryInputGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:1) | [`vktGeometryInputGeometryShaderTests.md`](../testfiles/geometry/vktGeometryInputGeometryShaderTests.md) |
| [`vktGeometryBasicGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:1) | [`vktGeometryBasicGeometryShaderTests.md`](../testfiles/geometry/vktGeometryBasicGeometryShaderTests.md) |
| [`vktGeometryLayeredRenderingTests.cpp`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1) | [`vktGeometryLayeredRenderingTests.md`](../testfiles/geometry/vktGeometryLayeredRenderingTests.md) |
| [`vktGeometryInstancedRenderingTests.cpp`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp:1) | [`vktGeometryInstancedRenderingTests.md`](../testfiles/geometry/vktGeometryInstancedRenderingTests.md) |
| [`vktGeometryVaryingGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:1) | [`vktGeometryVaryingGeometryShaderTests.md`](../testfiles/geometry/vktGeometryVaryingGeometryShaderTests.md) |
| [`vktGeometryEmitGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:1) | [`vktGeometryEmitGeometryShaderTests.md`](../testfiles/geometry/vktGeometryEmitGeometryShaderTests.md) |
| [`vktGeometryBuiltinVariableGeometryShaderTests.cpp`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:1) | [`vktGeometryBuiltinVariableGeometryShaderTests.md`](../testfiles/geometry/vktGeometryBuiltinVariableGeometryShaderTests.md) |

## Subgroup Structure and Major Themes

### [`input`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:262)

The [`input`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:262) subgroup is further split into [`basic_primitive`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:263), [`triangle_strip_adjacency`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:264), and [`conversion`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:265).

Observed coverage includes:
- basic point/line/triangle input topologies and adjacency variants from [`inputPrimitives[]`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:267)
- triangle-strip-adjacency cases over vertex counts 0 through 12 from the loop in [`createInputGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:284)
- primitive conversion cases such as [`triangles_to_points`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:296) and [`points_to_triangles`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:300)

### [`basic`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:1002)

The [`basic`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:1002) subgroup combines three themes:
- fixed output-count patterns such as [`output_10`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:1005) and [`output_128`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:1006)
- varying output-count sources using attribute, uniform, or texture-controlled counts in [`VaryingOutputCountCase`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:550) and registrations at [`createBasicGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:1014)
- side-effect cases added with [`addFunctionCaseWithPrograms()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:1041), covering conditional and degenerate geometry-output paths

### [`layered`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:62)

The layered tests are organized around the [`TestType`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:62) enum, which includes:
- default-layer and single-layer targeting
- all-layer drawing
- different per-layer content
- fragment-stage [`gl_Layer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1191) verification
- one invocation per layer and multiple layers per invocation
- layered readback cases
- secondary command buffer cases

### [`instanced`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp:423)

The instanced subgroup is generated from Cartesian combinations of draw-instance counts [`{1, 2, 4, 8}`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp:427) and geometry-shader invocation counts [`{1, 2, 8, 32, 64, 127}`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp:433).

### [`varying`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:273)

The varying subgroup uses [`VaryingTestSpec`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:70) combinations to vary what the vertex shader writes and what the geometry shader forwards, with five concrete cases registered in [`varyingTests[]`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:279).

### [`emit`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:226)

The emit subgroup builds a matrix of [`EmitTestSpec`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:71) cases over output topology plus emit/end counts for one or two primitive segments. Names are synthesized in [`createEmitGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:260).

### [`builtin_variable`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:430)

The built-in-variable subgroup is split into [`in_block`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:431) and [`outside_block`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:432), covering:
- [`point_size`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:435)
- [`primitive_id_in`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:437)
- [`primitive_id_in_restarted`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:439)
- [`primitive_id`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:441)
- [`position`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:443)

## Recurring Parameter Dimensions

The inspected geometry files repeatedly vary the following dimensions:

| Dimension | Observed examples |
|---|---|
| Input primitive topology | [`VK_PRIMITIVE_TOPOLOGY_POINT_LIST`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:268), [`VK_PRIMITIVE_TOPOLOGY_LINE_LIST_WITH_ADJACENCY`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:274), [`VK_PRIMITIVE_TOPOLOGY_TRIANGLE_FAN`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:273) |
| Output primitive topology | point, line-strip, triangle-strip mappings in [`outputTypeToGLString()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:331) and emit tests in [`EmitTestSpec`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:71) |
| Output vertex counts | fixed counts such as 10/128 and dual patterns in [`createBasicGeometryShaderTests()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:1005) |
| Output-count source | [`READ_ATTRIBUTE`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:64), [`READ_UNIFORM`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:67), [`READ_TEXTURE`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:68) |
| Shader instancing mode | [`MODE_WITHOUT_INSTANCING`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:74) and [`MODE_WITH_INSTANCING`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:75) |
| Layered image shape | [`VkImageViewType`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:77), size, and layer count in [`ImageParams`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:75) |
| Layered test behavior | [`TestType`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:62) |
| Draw instances / GS invocations | [`TestParams`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp:58) |
| Vertex vs geometry varying outputs | [`VertexOutputs`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:57) and [`GeometryOutputs`](../../modules/vulkan/geometry/vktGeometryVaryingGeometryShaderTests.cpp:63) |
| Emit/end sequencing | [`emitCountA`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:74), [`endCountA`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:75), [`emitCountB`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:76), [`endCountB`](../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp:77) |
| Built-in variable selection | [`VariableTest`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:64) and restart/indexed toggle via [`indicesTest`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:77) |

## Recurring Support Requirements

A recurring support gate across the geometry category is [`DEVICE_CORE_FEATURE_GEOMETRY_SHADER`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:136), required in input, basic, varying, emit, built-in, and instanced-related support checks.

Additional observed support gates include:
- portability-subset rejection for unsupported triangle fans in [`GeometryExpanderRenderTest::checkSupport()`](../../modules/vulkan/geometry/vktGeometryInputGeometryShaderTests.cpp:139)
- point-size support for the built-in point-size case via [`DEVICE_CORE_FEATURE_SHADER_TESSELLATION_AND_GEOMETRY_POINT_SIZE`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:199)
- vertex-pipeline atomics for side-effect tests in [`sideEffectSupportCheck()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:797)
- geometry-shader invocation-limit checks in [`checkSupport()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp:409)

## Recurring Verification Methods

Observed verification approaches differ by file:

- file-image comparison through [`compareWithFileImage()`](../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp:412), which combines fuzzy comparison with position-deviation comparison
- fuzzy image comparison in instanced rendering via [`tcu::fuzzyCompare()`](../../modules/vulkan/geometry/vktGeometryInstancedRenderingTests.cpp:401)
- explicit per-layer content validation in layered rendering via [`verifyLayerContent()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:687), [`verifyImageSingleColoredRow()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:451), [`verifyImageMultipleBars()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:524), and [`verifyEmptyImage()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:660)
- thresholded reference-image comparison in side-effect tests via [`tcu::floatThresholdCompare()`](../../modules/vulkan/geometry/vktGeometryBasicGeometryShaderTests.cpp:991)
- color coding of built-in-variable expectations inside shaders, for example fragment use of [`gl_PrimitiveID`](../../modules/vulkan/geometry/vktGeometryBuiltinVariableGeometryShaderTests.cpp:403)

## Relationship to the Test Plan

[`apitests.adoc`](../../../doc/testspecs/VK/apitests.adoc:15) describes the Vulkan CTS framework model in terms of [`TestCase`](../../../doc/testspecs/VK/apitests.adoc:30) and [`TestInstance`](../../../doc/testspecs/VK/apitests.adoc:43), but it does not appear to provide geometry-category-specific coverage details in the inspected range. For geometry documentation, the source files under [`modules/vulkan/geometry/`](../../modules/vulkan/geometry/vktGeometryTests.cpp:24) are the primary evidence.

## Notes / Uncertainties

- The geometry category currently contains eight wiki-tracked source files, but only seven subgroups under the top-level registration tree because [`vktGeometryTests.cpp`](../../modules/vulkan/geometry/vktGeometryTests.cpp:1) is a registration file rather than a subgroup implementation file.
- This category summary is based on the inspected geometry sources and helpers listed above; it intentionally does not reuse claims from the older geometry wiki pages.
