# GLSL

## Overview

The `glsl` category is registered as the root child `glsl` by [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1353) and, for Vulkan SC package construction, by the same root-child call in [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1421). Unlike categories with a dedicated `modules/vulkan/{category}/` directory, its category tree is assembled by [`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1215-L1288) from ShaderLibrary `.test` files, ShaderRenderCase-based render tests, ShaderExecutor-based execution tests, and non-VulkanSC Amber/scripted GLSL tests.

## Registration Architecture

[`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1215-L1288) is the category aggregator. It first registers nine ES 3.10 ShaderLibrary groups from `vulkan/glsl/es310/*.test` paths at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1219-L1233), then creates the intermediate `440` group and attaches the GLSL 4.40 `linkage` ShaderLibrary file at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1235-L1251). It then attaches ShaderRenderCase groups at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1253-L1272), ShaderExecutor groups at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1274-L1279), and non-VulkanSC Amber / extension-oriented groups at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1281-L1287).

The directory layout follows that aggregation rather than a single `glsl` implementation directory:

| Source area | Registration evidence | Registered group families |
|---|---|---|
| ShaderLibrary infrastructure | ES 3.10 and 4.40 `.test` paths are passed to [`createShaderLibraryGroup()`](../../modules/vulkan/vktTestPackage.cpp#L1229-L1249), whose implementation constructs a [`ShaderLibraryGroup`](../../modules/vulkan/vktShaderLibrary.cpp#L1789-L1829) | `arrays`, `conditionals`, `constant_expressions`, `constants`, `conversions`, `functions`, `linkage`, `scoping`, `swizzles`, and `440.linkage` |
| [`shaderrender/`](../../modules/vulkan/shaderrender/vktShaderRender.cpp#L1) | [`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1253-L1272) adds `sr::create*Tests()` factories | `derivate`, `discard`, `demote`, `indexing`, `invariance`, `limits`, `loops`, `matrix`, `operator`, `precise`, `return`, `struct`, `switch`, `texture_functions`, `texture_gather`, `builtin_var` |
| [`shaderexecutor/`](../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L1) | [`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1274-L1279) adds ShaderExecutor factories, and non-VulkanSC `bfloat16` / `shader_expect_assume` at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1256-L1259) and [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1281-L1287) | `builtin`, `opaque_type_indexing`, `atomic_operations`, `shader_clock`, `helper_invocations`, `bfloat16`, `shader_expect_assume` |
| [`amber/`](../../modules/vulkan/amber/vktAmberGlslTests.cpp#L1) | Non-VulkanSC Amber factories are attached at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1281-L1285) | `combined_operations`, `crash_test`, `logical_copy` |

This means a test appears under `dEQP-VK.glsl.*` because its factory is attached by [`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1215-L1288), not because the implementation file lives in a category-specific directory.

## Registration Entry Point

The category entry point is [`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1215-L1288), wrapped by the overload at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1338-L1341) and attached to the Vulkan root package at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1353). The direct children registered under `glsl` are:

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
├── 440
│   └── linkage
├── derivate
├── discard
├── demote (non-VulkanSC only)
├── indexing
├── invariance
├── limits
├── loops
├── matrix
├── operator
├── precise
├── return
├── struct
├── switch
├── texture_functions
├── texture_gather
├── builtin_var
├── builtin
├── opaque_type_indexing
├── atomic_operations
├── shader_clock
├── helper_invocations
├── bfloat16 (non-VulkanSC only)
├── combined_operations (non-VulkanSC only)
├── crash_test (non-VulkanSC only)
├── logical_copy (non-VulkanSC only)
└── shader_expect_assume (non-VulkanSC only)
```

## File Inventory

### ShaderLibrary Infrastructure

| File or data source | Role | Level-3 doc |
|---|---|---|
| [`vktShaderLibrary.cpp`](../../modules/vulkan/vktShaderLibrary.cpp#L1) | Implements `ShaderLibraryGroup`, shader-case generation, and ShaderLibrary execution for `.test` files | [`vktShaderLibrary.md`](../testfiles/glsl/vktShaderLibrary.md) |
| [`vktShaderLibrary.hpp`](../../modules/vulkan/vktShaderLibrary.hpp#L1) | Declares the ShaderLibrary interfaces used by [`createShaderLibraryGroup()`](../../modules/vulkan/vktShaderLibrary.cpp#L1825-L1829) | — |
| `data/vulkan/glsl/es310/*.test` | Declarative ES 3.10 ShaderLibrary inputs registered from [`s_es310Tests`](../../modules/vulkan/vktTestPackage.cpp#L1219-L1233) | Covered by [`vktShaderLibrary.md`](../testfiles/glsl/vktShaderLibrary.md) |
| `data/vulkan/glsl/440/linkage.test` | Declarative GLSL 4.40 ShaderLibrary input registered under `glsl.440` at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1235-L1251) | Covered by [`vktShaderLibrary.md`](../testfiles/glsl/vktShaderLibrary.md) |

### ShaderRender Files

| Source file | Registered group(s) / evidence | Level-3 doc |
|---|---|---|
| [`vktShaderRenderDerivateTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2183-L2184) | `derivate` | [`vktShaderRenderDerivateTests.md`](../testfiles/glsl/vktShaderRenderDerivateTests.md) |
| [`vktShaderRenderDiscardTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderDiscardTests.cpp#L441-L447) | `discard`, `demote` | [`vktShaderRenderDiscardTests.md`](../testfiles/glsl/vktShaderRenderDiscardTests.md) |
| [`vktShaderRenderIndexingTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1357-L1358) | `indexing` | [`vktShaderRenderIndexingTests.md`](../testfiles/glsl/vktShaderRenderIndexingTests.md) |
| [`vktShaderRenderInvarianceTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1123-L1133) | `invariance`, `precise` | [`vktShaderRenderInvarianceTests.md`](../testfiles/glsl/vktShaderRenderInvarianceTests.md) |
| [`vktShaderRenderLimitTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L241-L242) | `limits` | [`vktShaderRenderLimitTests.md`](../testfiles/glsl/vktShaderRenderLimitTests.md) |
| [`vktShaderRenderLoopTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1618-L1619) | `loops` | [`vktShaderRenderLoopTests.md`](../testfiles/glsl/vktShaderRenderLoopTests.md) |
| [`vktShaderRenderMatrixTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2556-L2557) | `matrix` | [`vktShaderRenderMatrixTests.md`](../testfiles/glsl/vktShaderRenderMatrixTests.md) |
| [`vktShaderRenderOperatorTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L2988-L2989) | `operator` | [`vktShaderRenderOperatorTests.md`](../testfiles/glsl/vktShaderRenderOperatorTests.md) |
| [`vktShaderRenderReturnTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L523-L524) | `return` | [`vktShaderRenderReturnTests.md`](../testfiles/glsl/vktShaderRenderReturnTests.md) |
| [`vktShaderRenderStructTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L2117-L2118) | `struct` | [`vktShaderRenderStructTests.md`](../testfiles/glsl/vktShaderRenderStructTests.md) |
| [`vktShaderRenderSwitchTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L502-L503) | `switch` | [`vktShaderRenderSwitchTests.md`](../testfiles/glsl/vktShaderRenderSwitchTests.md) |
| [`vktShaderRenderTextureFunctionTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L8302-L8303) | `texture_functions` | [`vktShaderRenderTextureFunctionTests.md`](../testfiles/glsl/vktShaderRenderTextureFunctionTests.md) |
| [`vktShaderRenderTextureGatherTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3139-L3140) | `texture_gather` | [`vktShaderRenderTextureGatherTests.md`](../testfiles/glsl/vktShaderRenderTextureGatherTests.md) |
| [`vktShaderRenderBuiltinVarTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2499-L2500) | `builtin_var` | [`vktShaderRenderBuiltinVarTests.md`](../testfiles/glsl/vktShaderRenderBuiltinVarTests.md) |

### ShaderExecutor Files

| Source file | Registered group / evidence | Level-3 doc |
|---|---|---|
| [`vktShaderBuiltinTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderBuiltinTests.cpp#L41-L42) | `builtin` | [`vktShaderBuiltinTests.md`](../testfiles/glsl/vktShaderBuiltinTests.md) |
| [`vktOpaqueTypeIndexingTests.cpp`](../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2045-L2046) | `opaque_type_indexing` | [`vktOpaqueTypeIndexingTests.md`](../testfiles/glsl/vktOpaqueTypeIndexingTests.md) |
| [`vktAtomicOperationTests.cpp`](../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1589-L1590) | `atomic_operations` | [`vktAtomicOperationTests.md`](../testfiles/glsl/vktAtomicOperationTests.md) |
| [`vktShaderClockTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L255-L256) | `shader_clock` | [`vktShaderClockTests.md`](../testfiles/glsl/vktShaderClockTests.md) |
| [`vktShaderHelperInvocationsTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L634-L635) | `helper_invocations` | [`vktShaderHelperInvocationsTests.md`](../testfiles/glsl/vktShaderHelperInvocationsTests.md) |
| [`vktShaderBFloat16Tests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L204-L205) | `bfloat16` | [`vktShaderBFloat16Tests.md`](../testfiles/glsl/vktShaderBFloat16Tests.md) |
| [`vktShaderExpectAssumeTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1516-L1517) | `shader_expect_assume` | [`vktShaderExpectAssumeTests.md`](../testfiles/glsl/vktShaderExpectAssumeTests.md) |

### Amber Files

| Source file | Registered group(s) / evidence | Level-3 doc |
|---|---|---|
| [`vktAmberGlslTests.cpp`](../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L101) | `combined_operations`, `crash_test`, `logical_copy` | [`vktAmberGlslTests.md`](../testfiles/glsl/vktAmberGlslTests.md) |

## Subgroup Structure and Major Themes

### ShaderLibrary groups — declarative `.test` suites

The ES 3.10 ShaderLibrary groups are enumerated in `s_es310Tests` and expanded into `createShaderLibraryGroup(testCtx, name, "vulkan/glsl/es310/" + name + ".test")` calls at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1219-L1233). The `440` subgroup is explicitly constructed as `new tcu::TestCaseGroup(testCtx, "440")` and receives `vulkan/glsl/440/linkage.test` at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1235-L1251). The shared implementation parses and runs those declarative suites through [`ShaderLibraryGroup`](../../modules/vulkan/vktShaderLibrary.cpp#L1789-L1829) and [`ShaderCaseInstance::iterate()`](../../modules/vulkan/vktShaderLibrary.cpp#L1607-L1764).

### ShaderRender groups — rendered image / evaluator suites

The ShaderRender branch is attached by the contiguous `sr::create*Tests()` calls in [`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1253-L1272). These files use the shared [`ShaderRenderCase`](../../modules/vulkan/shaderrender/vktShaderRender.cpp#L583-L592) / [`ShaderRenderCaseInstance`](../../modules/vulkan/shaderrender/vktShaderRender.cpp#L658-L688) harness: cases render a quad grid, compute a vertex or fragment reference image, and compare result against reference in [`ShaderRenderCaseInstance::iterate()`](../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805). Specific files add specialized evaluators or comparisons, such as derivative interval behavior in [`vktShaderRenderDerivateTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L857-L876), matrix evaluation in [`MatrixShaderEvaluator::evaluate()`](../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1649-L1683), operator evaluation in [`OperatorShaderEvaluator`](../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L663-L854), texture lookup evaluation in [`TexLookupEvaluator`](../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1409-L1428), and texture-gather verification in [`TextureGatherInstance::verify()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1564-L1634).

### ShaderExecutor groups — shader execution and buffer readback suites

The ShaderExecutor branch is attached by [`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1274-L1279) plus the non-VulkanSC `bfloat16` and `shader_expect_assume` additions at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1256-L1259) and [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1281-L1287). This family uses shader execution plus host-side result validation: for example, atomic tests invalidate and compare output buffers in [`vktAtomicOperationTests.cpp`](../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L999-L1001) and validate legal atomic outcomes at [`vktAtomicOperationTests.cpp`](../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L626-L840); shader-clock tests read output values and call [`validateOutput()`](../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L113-L122); helper-invocation tests read back input/final buffers at [`vktShaderHelperInvocationsTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L375-L382); and shader-expect/assume tests validate output data after invalidation at [`vktShaderExpectAssumeTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L120-L127).

### Amber groups — scripted GLSL checks

The non-VulkanSC Amber GLSL groups are registered only inside the guarded block in [`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1281-L1287). [`vktAmberGlslTests.cpp`](../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L101) creates `combined_operations`, `crash_test`, and `logical_copy` groups by adding Amber test cases from `.amber` scripts. The common Amber test case parses scripts into an Amber recipe at [`AmberTestCase::initPrograms()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L415-L531), checks Amber requirements before execution at [`vktAmberTestCase.cpp`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L547-L573), and executes the recipe with Vulkan engine options at [`vktAmberTestCase.cpp`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L583-L608).

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| ShaderLibrary source level | ES 3.10 groups come from `vulkan/glsl/es310/*.test` at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1219-L1233); GLSL 4.40 coverage is the nested `440.linkage` group at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1235-L1251) |
| Shader stage | ShaderRender and ShaderExecutor files generate vertex/fragment/compute and other stage variants per file; the shared ShaderExecutor stage support helper dispatches graphics, tessellation, geometry, compute, task, and mesh checks in [`checkSupportShader()`](../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L4285-L4349) |
| Precision and data type | ShaderRender operator and matrix tests use evaluator-driven data specs, with operator cases binding `ShaderDataSpec` to [`OperatorShaderEvaluator`](../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L852-L854) and matrix cases binding input types to [`MatrixShaderEvaluator`](../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1955-L1957) |
| Control-flow shape | Loop cases are generated by [`createLoopTests()`](../../modules/vulkan/shaderrender/vktShaderRenderLoopTests.cpp#L1618-L1619), return cases by [`createReturnTests()`](../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L523-L524), and switch cases by [`createSwitchTests()`](../../modules/vulkan/shaderrender/vktShaderRenderSwitchTests.cpp#L502-L503) |
| Texture operation | Texture-function cases are created by [`createTextureFunctionTests()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L8302-L8303), while texture-gather cases are created by [`createTextureGatherTests()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L3139-L3140) and use texture-specific support and verifier paths |
| Extension-oriented scalar/vector types | Atomic operation support branches select int64, float atomic, float16-vector, and reference-memory paths in [`AtomicOperationCase::checkSupport()`](../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1058-L1295); BFloat16 tests register through [`createBFloat16Tests()`](../../modules/vulkan/shaderexecutor/vktShaderBFloat16Tests.cpp#L204-L205) and delegate constant/conversion/combo verification to BFloat16-specific files |

## Recurring Support Requirements

Observed support gates are distributed across the implementation files rather than centralized in the Level-2 page. ShaderRender texture-function cases check extension and feature conditions in [`ShaderTextureFunctionCase::checkSupport()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L2047-L2053), [`TextureQueryCase::checkSupport()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4008-L4027), and [`SparseShaderTextureFunctionCase::checkSupport()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L4931-L4940). Texture-gather cases check image-gather and offset requirements in [`TextureGather2DCase::checkSupport()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2275-L2291), [`TextureGather2DArrayCase::checkSupport()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2501-L2517), and [`TextureGatherCubeCase::checkSupport()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L2735-L2749).

ShaderExecutor support checks include `VK_KHR_shader_clock` in [`vktShaderClockTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L152-L155), `VK_KHR_buffer_device_address` for helper-invocation address loads in [`vktShaderHelperInvocationsTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L525-L528), atomic extension and feature branches in [`vktAtomicOperationTests.cpp`](../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1058-L1295), `VK_KHR_storage_buffer_storage_class` for selected opaque-indexing paths in [`vktOpaqueTypeIndexingTests.cpp`](../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1218-L1221), and `VK_KHR_shader_expect_assume` plus 16-bit / 8-bit storage requirements in [`vktShaderExpectAssumeTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L1108-L1140). Amber crash tests encode tessellation and geometry feature requirements in their parameter table at [`vktAmberGlslTests.cpp`](../../modules/vulkan/amber/vktAmberGlslTests.cpp#L54-L76), and AmberTestCase maps such feature strings to `VkPhysicalDeviceFeatures` in [`isRequirementSupported()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L102-L109).

## Recurring Verification Methods

| Method | Evidence and scope |
|---|---|
| ShaderRender rendered-image comparison | [`ShaderRenderCaseInstance::iterate()`](../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) renders, computes a reference, and calls `compareImages`; [`compareImages()`](../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2729) delegates to `tcu::pixelThresholdCompare` unless exact matching is requested |
| Specialized ShaderRender evaluators | Matrix and operator pages use source-backed evaluator functions, with representative implementations in [`MatrixShaderEvaluator::evaluate()`](../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1649-L1683) and [`OperatorShaderEvaluator`](../../modules/vulkan/shaderrender/vktShaderRenderOperatorTests.cpp#L663-L854) |
| Texture sampling / gather verification | Texture-function tests evaluate lookup expectations through [`TexLookupEvaluator`](../../modules/vulkan/shaderrender/vktShaderRenderTextureFunctionTests.cpp#L1409-L1428); texture-gather tests build expected pixel offsets in [`makePixelOffsetsFunctor()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L889-L909) and verify sampled results in [`TextureGatherInstance::verify()`](../../modules/vulkan/shaderrender/vktShaderRenderTextureGatherTests.cpp#L1564-L1634) |
| Pixel-threshold image comparison | Limit and built-in-variable render tests use `pixelThresholdCompare()` at [`vktShaderRenderLimitTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L88-L90) and [`vktShaderRenderBuiltinVarTests.cpp`](../../modules/vulkan/shaderrender/vktShaderRenderBuiltinVarTests.cpp#L2374-L2376) |
| ShaderExecutor buffer/result validation | Atomic tests invalidate output memory and compare legal outcomes at [`vktAtomicOperationTests.cpp`](../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L999-L1001) and [`vktAtomicOperationTests.cpp`](../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L626-L840); clock and expect/assume tests call file-local validators at [`vktShaderClockTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L113-L122) and [`vktShaderExpectAssumeTests.cpp`](../../modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp#L120-L127) |
| ShaderLibrary value/reference execution | [`ShaderCaseInstance::iterate()`](../../modules/vulkan/vktShaderLibrary.cpp#L1607-L1764) drives ShaderLibrary cases generated from `.test` specifications; helper code declares reference and user uniform blocks at [`vktShaderLibrary.cpp`](../../modules/vulkan/vktShaderLibrary.cpp#L127-L137) |
| Amber script execution | [`AmberTestCase::initPrograms()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L415-L531) parses shaders from Amber recipes, and [`AmberTestCase::iterate()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L547-L608) checks requirements and executes the recipe |

## Level-3 Documents

| Group(s) | Wiki document |
|---|---|
| ShaderLibrary ES 3.10 and `440.linkage` groups | [`vktShaderLibrary.md`](../testfiles/glsl/vktShaderLibrary.md) |
| `derivate` | [`vktShaderRenderDerivateTests.md`](../testfiles/glsl/vktShaderRenderDerivateTests.md) |
| `discard`, `demote` | [`vktShaderRenderDiscardTests.md`](../testfiles/glsl/vktShaderRenderDiscardTests.md) |
| `indexing` | [`vktShaderRenderIndexingTests.md`](../testfiles/glsl/vktShaderRenderIndexingTests.md) |
| `invariance`, `precise` | [`vktShaderRenderInvarianceTests.md`](../testfiles/glsl/vktShaderRenderInvarianceTests.md) |
| `limits` | [`vktShaderRenderLimitTests.md`](../testfiles/glsl/vktShaderRenderLimitTests.md) |
| `loops` | [`vktShaderRenderLoopTests.md`](../testfiles/glsl/vktShaderRenderLoopTests.md) |
| `matrix` | [`vktShaderRenderMatrixTests.md`](../testfiles/glsl/vktShaderRenderMatrixTests.md) |
| `operator` | [`vktShaderRenderOperatorTests.md`](../testfiles/glsl/vktShaderRenderOperatorTests.md) |
| `return` | [`vktShaderRenderReturnTests.md`](../testfiles/glsl/vktShaderRenderReturnTests.md) |
| `struct` | [`vktShaderRenderStructTests.md`](../testfiles/glsl/vktShaderRenderStructTests.md) |
| `switch` | [`vktShaderRenderSwitchTests.md`](../testfiles/glsl/vktShaderRenderSwitchTests.md) |
| `texture_functions` | [`vktShaderRenderTextureFunctionTests.md`](../testfiles/glsl/vktShaderRenderTextureFunctionTests.md) |
| `texture_gather` | [`vktShaderRenderTextureGatherTests.md`](../testfiles/glsl/vktShaderRenderTextureGatherTests.md) |
| `builtin_var` | [`vktShaderRenderBuiltinVarTests.md`](../testfiles/glsl/vktShaderRenderBuiltinVarTests.md) |
| `builtin` | [`vktShaderBuiltinTests.md`](../testfiles/glsl/vktShaderBuiltinTests.md) |
| `opaque_type_indexing` | [`vktOpaqueTypeIndexingTests.md`](../testfiles/glsl/vktOpaqueTypeIndexingTests.md) |
| `atomic_operations` | [`vktAtomicOperationTests.md`](../testfiles/glsl/vktAtomicOperationTests.md) |
| `shader_clock` | [`vktShaderClockTests.md`](../testfiles/glsl/vktShaderClockTests.md) |
| `helper_invocations` | [`vktShaderHelperInvocationsTests.md`](../testfiles/glsl/vktShaderHelperInvocationsTests.md) |
| `bfloat16` | [`vktShaderBFloat16Tests.md`](../testfiles/glsl/vktShaderBFloat16Tests.md) |
| `shader_expect_assume` | [`vktShaderExpectAssumeTests.md`](../testfiles/glsl/vktShaderExpectAssumeTests.md) |
| `combined_operations`, `crash_test`, `logical_copy` | [`vktAmberGlslTests.md`](../testfiles/glsl/vktAmberGlslTests.md) |

## Notes and Scope

- No dedicated `modules/vulkan/glsl/` directory was observed in the registration path; the authoritative category membership is the set of children attached by [`createGlslTests()`](../../modules/vulkan/vktTestPackage.cpp#L1215-L1288).
- Non-VulkanSC-only branches are controlled by `#ifndef CTS_USES_VULKANSC` around `demote`, `bfloat16`, Amber GLSL groups, and `shader_expect_assume` at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1256-L1259) and [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1281-L1287).
- Detailed generated case matrices, exact child lists below each Level-3 root, and file-local edge cases are documented in the linked Level-3 pages rather than duplicated here.
