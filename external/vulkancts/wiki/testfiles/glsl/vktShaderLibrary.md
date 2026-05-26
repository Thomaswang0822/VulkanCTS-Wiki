# vktShaderLibrary.cpp

## Overview

[`vktShaderLibrary.cpp`](../../../modules/vulkan/vktShaderLibrary.cpp#L1) is shared Vulkan-side infrastructure for declarative GLSL `.test` files. It does not define one standalone registered root of its own; instead, [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1215-L1251) calls [`createShaderLibraryGroup()`](../../../modules/vulkan/vktShaderLibrary.cpp#L1825-L1829) once for each registered shader-library data file and attaches the resulting groups under the existing `glsl` category.

The same `glsl` category also registers many non-library `ShaderRenderCase` and related groups after the shader-library block in [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1265). This page documents only the `ShaderLibraryGroup` users registered at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1219-L1251), plus the execution path in [`vktShaderLibrary.cpp`](../../../modules/vulkan/vktShaderLibrary.cpp#L1227-L1686).

## Role

Shared infrastructure and registered-use documentation. [`ShaderLibraryGroup`](../../../modules/vulkan/vktShaderLibrary.cpp#L1790-L1821) subclasses `tcu::TestCaseGroup`, stores a `.test` filename, and lazily parses that file in [`ShaderLibraryGroup::init()`](../../../modules/vulkan/vktShaderLibrary.cpp#L1799-L1817). Parsed declarative nodes are converted to Vulkan-specific groups and cases by [`ShaderCaseFactory`](../../../modules/vulkan/vktShaderLibrary.cpp#L1766-L1788), whose `createGroup()` returns `tcu::TestCaseGroup` children and whose `createCase()` returns [`ShaderCase`](../../../modules/vulkan/vktShaderLibrary.cpp#L1780-L1784).

## Source Code

- Primary Vulkan implementation: [`vktShaderLibrary.cpp`](../../../modules/vulkan/vktShaderLibrary.cpp#L1)
- Factory declaration: [`vktShaderLibrary.hpp`](../../../modules/vulkan/vktShaderLibrary.hpp#L33-L34)
- Registered users in the GLSL category: [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1215-L1251)
- Shared `.test` parser: [`gluShaderLibrary.cpp`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1756-L1762)
- ES310 data directory examples: [`arrays.test`](../../../data/vulkan/glsl/es310/arrays.test#L18-L42) and [`linkage.test`](../../../data/vulkan/glsl/es310/linkage.test#L3-L28)
- 440 data-file example: [`linkage.test`](../../../data/vulkan/glsl/440/linkage.test#L3-L46)

## Registration Hierarchy

```text
glsl
├── arrays
├── conditionals
├── constant_expressions
├── constants
├── conversions
├── functions
├── linkage
├── scoping
├── swizzles
└── 440 (contains shader-library child linkage)
```

The direct ES310 children are generated from `s_es310Tests[]` and registered by iterating that table in [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1219-L1233). The `440` intermediate group is constructed explicitly, populated from `s_440Tests[]`, and then attached under `glsl` at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1235-L1251). Within `440`, the inspected shader-library child is `linkage`, because `s_440Tests[]` contains only that name at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1235-L1249).

## Test Families

### arrays — ES310 array declarations, constructors, length, returns, and parameters

The registered `arrays` group is created from `vulkan/glsl/es310/arrays.test` by the ES310 registration loop in [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1229-L1233). The data file demonstrates nested declarative grouping, such as `group constructor`, followed by cases like `float3` and `float4` at [`arrays.test`](../../../data/vulkan/glsl/es310/arrays.test#L18-L66). A `both` shader block inside a case is parsed into two generated cases with `_vertex` and `_fragment` suffixes by [`ShaderParser::parseShaderCase()`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1570-L1610).

### conditionals, constant_expressions, constants, conversions, functions, scoping, and swizzles — ES310 language-feature libraries

These seven direct children are registered from their matching `vulkan/glsl/es310/<name>.test` files by the same `s_es310Tests[]` table and loop at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1220-L1233). Their detailed case hierarchy is declarative: [`ShaderParser::parseShaderGroup()`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1660-L1696) turns `group` blocks into nested `TestCaseGroup` nodes, [`ShaderParser::parseShaderCase()`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1450-L1658) turns `case` blocks into one or more `ShaderCase` nodes, and [`ShaderParser::parseImport()`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1698-L1716) can splice imported files relative to the current `.test` file.

### linkage — ES310 varying/linkage library

The ES310 `linkage` child is registered from `vulkan/glsl/es310/linkage.test` by the same ES310 table at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1220-L1233). The inspected data file begins with a `varying` group, a nested `rules` group, and cases such as `vertex_declare` and `both_declare` at [`linkage.test`](../../../data/vulkan/glsl/es310/linkage.test#L3-L52). These are complete vertex/fragment cases in parser terms because they provide explicit `vertex` and `fragment` shader blocks rather than a `both` block, and the parser creates a single `CASETYPE_COMPLETE` case when stage-specific sources are present and no pipeline-program list is used at [`gluShaderLibrary.cpp`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1612-L1632).

### 440 — Core GLSL linkage library under an intermediate group

The `440` direct child is not a `.test` file itself. It is an intermediate `tcu::TestCaseGroup(testCtx, "440")` created in [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1242-L1243). Its inspected shader-library child is `linkage`, registered from `vulkan/glsl/440/linkage.test` by iterating `s_440Tests[]` at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1235-L1249). The `440/linkage.test` file starts with `group varying`, `group component`, and nested component-qualifier cases such as `vert_in.vec2.as_float_float` at [`linkage.test`](../../../data/vulkan/glsl/440/linkage.test#L3-L46).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Registered data-file version roots | ES310 direct roots are the nine names in `s_es310Tests[]`; the 440 root is an explicit `440` group containing the `linkage` shader-library group at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1220-L1251). |
| Data-file paths | ES310 filenames are built as `vulkan/glsl/es310/` + name + `.test` at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1229-L1233); 440 filenames are built as `vulkan/glsl/440/` + name + `.test` at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1245-L1249). |
| Parsed hierarchy | `group` blocks become nested `TestCaseGroup` nodes and can contain nested groups, cases, or imports at [`ShaderParser::parseShaderGroup()`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1660-L1696). |
| Case-stage form | A `both` block generates separate `_vertex` and `_fragment` cases; explicit stage blocks generate a complete case when pipeline programs are absent at [`gluShaderLibrary.cpp`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1570-L1632). |
| Shader stages accepted by the parser | The case parser accepts `vertex`, `fragment`, `tessellation_control`, `tessellation_evaluation`, `geometry`, and `both` tokens as shader-source blocks at [`gluShaderLibrary.cpp`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1507-L1546). |
| Values and sub-cases | `values` blocks are parsed once per case at [`gluShaderLibrary.cpp`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1500-L1506); the Vulkan runner advances `m_subCaseNdx` until `getNumSubCases()` is exhausted at [`vktShaderLibrary.cpp`](../../../modules/vulkan/vktShaderLibrary.cpp#L1566-L1572) and [`vktShaderLibrary.cpp`](../../../modules/vulkan/vktShaderLibrary.cpp#L1683-L1686). |
| Output mode | Cases default to `OUTPUT_RESULT`; `output_color` switches to `OUTPUT_COLOR` and records a format token at [`gluShaderLibrary.cpp`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1461-L1464) and [`gluShaderLibrary.cpp`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1494-L1499). |
| Render extent | `ShaderCaseInstance` renders and reads back `64 x 64` images, from `RENDER_WIDTH` and `RENDER_HEIGHT` at [`vktShaderLibrary.cpp`](../../../modules/vulkan/vktShaderLibrary.cpp#L1236-L1240). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| Expected result restriction in Vulkan wrapper | [`ShaderCase::initPrograms()`](../../../modules/vulkan/vktShaderLibrary.cpp#L1707-L1715) asserts a valid specification and throws `InternalError` unless `m_spec.expectResult` is `EXPECT_PASS`; this wrapper is for executing passing shader-library cases, not documenting negative compile/link expectation behavior. |
| Parser-level `require extension` directives | [`ShaderParser::parseRequirement()`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1220-L1263) parses one or more extension alternatives and optional affected stage masks into `RequiredExtension` entries. |
| Parser-level capability/limit requirements | The same parser handles `require limit`, `full_glsl_es_100_support`, `only_glsl_es_100_support`, and `exactly_one_draw_buffer` requirements at [`gluShaderLibrary.cpp`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1264-L1303). |
| Extension injection into shader sources | Required extensions are converted into `#extension ... : require` statements in [`generateExtensionStatements()`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1840-L1849) and inserted by [`injectExtensionRequirements()`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1852-L1870). |
| Case-shape validation | Shared validation rejects invalid case shapes, including vertex-only cases with non-vertex shaders, fragment-only cases with non-fragment shaders, and complete cases without both vertex and fragment stages at [`gluShaderLibrary.cpp`](../../../../../framework/opengl/gluShaderLibrary.cpp#L210-L224). |

## Verification Methods

- [`ShaderCaseInstance`](../../../modules/vulkan/vktShaderLibrary.cpp#L1227-L1291) owns the render resources, input/reference/uniform buffers, output images, readback buffers, pipeline, descriptor set, command buffer, and current sub-case index used to execute parsed shader cases.
- Before each draw, the runner writes the selected sub-case's input, expected-output, and uniform values into host-visible memory with [`writeValuesToMem()`](../../../modules/vulkan/vktShaderLibrary.cpp#L1218-L1225) from [`ShaderCaseInstance::iterate()`](../../../modules/vulkan/vktShaderLibrary.cpp#L1607-L1620).
- The command buffer renders to one or more color attachments and copies each attachment to a host-visible buffer for checking at [`vktShaderLibrary.cpp`](../../../modules/vulkan/vktShaderLibrary.cpp#L1518-L1557).
- In default `OUTPUT_RESULT` mode, generated shader comparison code uses `isOk(value, reference, 0.05)` for floating-point outputs and exact `isOk(value, reference)` for non-float outputs at [`genCompareOp()`](../../../modules/vulkan/vktShaderLibrary.cpp#L206-L231). The host then requires every pixel in the readback image to be white `(255, 255, 255, 255)` via [`checkResultImage()`](../../../modules/vulkan/vktShaderLibrary.cpp#L1574-L1590) and the `OUTPUT_RESULT` branch of [`iterate()`](../../../modules/vulkan/vktShaderLibrary.cpp#L1624-L1643).
- In `OUTPUT_COLOR` mode, used by inspected 440 linkage cases such as [`linkage.test`](../../../data/vulkan/glsl/440/linkage.test#L7-L15), the host builds an integer reference vector from the expected output value for the current sub-case and requires every pixel in each output attachment to match it in [`checkResultImageWithReference()`](../../../modules/vulkan/vktShaderLibrary.cpp#L1592-L1606) and the `OUTPUT_COLOR` branch of [`iterate()`](../../../modules/vulkan/vktShaderLibrary.cpp#L1644-L1680).
- Multiple value sets are handled by returning `TestStatus::incomplete()` until the sub-case index reaches `getNumSubCases()`, then returning pass at [`vktShaderLibrary.cpp`](../../../modules/vulkan/vktShaderLibrary.cpp#L1683-L1686).

## Test Principles

- Registration is data-driven: the source names the `.test` files in [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1220-L1249), while the deeper hierarchy and case names come from parsed `group` and `case` blocks in the data files through [`parseFile()`](../../../../../framework/opengl/gluShaderLibrary.cpp#L1756-L1762).
- The Vulkan layer specializes declarative cases into executable shader programs. Vertex-only cases receive the parsed vertex shader plus a generated fragment shader, fragment-only cases receive a generated vertex shader plus the parsed fragment shader, and complete cases specialize all provided program sources at [`ShaderCase::initPrograms()`](../../../modules/vulkan/vktShaderLibrary.cpp#L1716-L1745).
- The page's registration tree intentionally lists only the direct shader-library users under `glsl`. It does not claim to cover later non-library `glsl` children registered after the shader-library block in [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1265).
- Correctness is image-readback based: parsed expected values feed either shader-side white/non-white decisions or host-side per-pixel color comparisons after a rendered 64x64 image is copied back to buffers at [`vktShaderLibrary.cpp`](../../../modules/vulkan/vktShaderLibrary.cpp#L1518-L1686).

## Notes / Uncertainties

- This is a shared infrastructure file with registered users, not a file that constructs a single `TestCaseGroup` root named after the source file. The inspected registration users are the ES310 table and the 440 `linkage` entry in [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1219-L1251).
- The detailed generated case lists are owned by the `.test` files and parser. This audit inspected representative ES310 and 440 data files, but the page avoids enumerating every generated descendant because that would duplicate the declarative data-file contents.
