# vktShaderLibrary.cpp

## Overview

Shared infrastructure implementing the `ShaderLibraryGroup` class and the `createShaderLibraryGroup()` factory function for Vulkan CTS. This file is not a single test group; rather, it provides the mechanism that parses declarative `.test` files and generates `ShaderCase` test cases from them. The groups it creates under `glsl` depend on which `.test` file is loaded at registration time.

## Role

Shared infrastructure. Implements the `ShaderLibraryGroup` class (a `tcu::TestCaseGroup` subclass that lazily initializes its children by parsing a `.test` file via `glu::sl::parseFile`) and the `ShaderCase`/`ShaderCaseInstance` classes that execute the parsed shader test specifications. The `createShaderLibraryGroup()` factory is called from [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1229-L1251) for each ES310 and 440 `.test` file.

## Source Code

[vktShaderLibrary.cpp](../../../modules/vulkan/vktShaderLibrary.cpp#L1-L1831)

## Registration Hierarchy

### glsl (ShaderLibrary ES310 portion)

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
└── swizzles
```

### glsl.440 (ShaderLibrary 440 portion)

```text
glsl.440
└── linkage
```

## Test Families

- **ES310 groups** (9 groups): `arrays`, `conditionals`, `constant_expressions`, `constants`, `conversions`, `functions`, `linkage`, `scoping`, `swizzles`. Each group is created by loading the corresponding `.test` file from `vulkan/glsl/es310/`. The `.test` files define groups and test cases declaratively.
- **440 group** (1 sub-group): `linkage` under the `440` intermediate group, loaded from `vulkan/glsl/440/linkage.test`.

Each `.test` file can define multiple sub-groups and test cases. The `both` keyword in a `.test` file generates two test cases with `_vertex` and `_fragment` suffixes. The `vertex` or `fragment` keywords produce a single test case.

## Parameter Dimensions

| Dimension | Description | Source |
|-----------|-------------|--------|
| GLSL version | ES310 or 440 | Determined by which `.test` file is loaded |
| Shader stage | vertex, fragment, or both | `both`/`vertex`/`fragment` keywords in `.test` files |
| Value blocks | Input, output, and uniform value sets | `values` blocks in `.test` files |
| Precision qualifiers | mediump, highp | Specified per-value in `.test` files |

## Support/Feature Requirements

Feature requirements are defined per-case in `.test` files via `require` directives. The parser in `framework/opengl/gluShaderLibrary.cpp` processes these and attaches them to the `ShaderCaseSpecification`. The Vulkan `ShaderCase::initPrograms` injects extension requirements into shader sources via `injectExtensionRequirements`.

## Verification Methods

ShaderCase-based rendering comparison. The `ShaderCaseInstance` class renders a 64x64 quad using the specified shader and compares the result against a reference:

- **OUTPUT_RESULT mode**: The fragment shader performs the comparison internally (using `isOk()` functions with a 0.05 tolerance for float types) and writes white (all 255) on pass. The host then checks that all pixels are white.
- **OUTPUT_COLOR mode**: The shader writes output values to color attachments. The host reads back the rendered image and compares each pixel against the expected reference values from the `.test` file's values block.

Sub-cases are iterated automatically when multiple value sets are defined in the `.test` file.

## Notes

- The `.test` files are located at `external/vulkancts/data/vulkan/glsl/es310/` and `external/vulkancts/data/vulkan/glsl/440/`.
- The `.test` file parser is in [gluShaderLibrary.cpp](../../../../../framework/opengl/gluShaderLibrary.cpp).
- The `ShaderLibraryGroup::init()` method lazily parses the `.test` file on first access, using `glu::sl::parseFile()` with a `ShaderCaseFactory` that creates Vulkan-specific `ShaderCase` objects.
- The `ShaderCase` class supports three case types: `CASETYPE_VERTEX_ONLY` (vertex shader under test with generated fragment shader), `CASETYPE_FRAGMENT_ONLY` (fragment shader under test with generated vertex shader), and `CASETYPE_COMPLETE` (full pipeline with specialization parameters).
- For `CASETYPE_COMPLETE`, shader sources are specialized using `StringTemplate` with stage-specific parameters (declarations, setup, output) and extension injection.
- The 440 group is registered as an intermediate `tcu::TestCaseGroup("440")` containing the linkage sub-group, while ES310 groups are registered directly under `glslTests`.
- Registration occurs in [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1219-L1251) within `createGlslTests()`.
