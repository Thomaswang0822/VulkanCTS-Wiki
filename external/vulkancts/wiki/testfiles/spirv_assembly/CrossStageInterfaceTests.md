## Overview

**Core question:** Does an implementation transport SPIR-V stage-interface values and apply `Flat`, `NoPerspective`, and `RelaxedPrecision` semantics correctly across the graphics stages it supports?

- This page covers the implementation-bearing `cross_stage` test family in the `spirv_assembly` test category. It is registered below `spirv_assembly.instruction.graphics` and has two intermediate nodes: `basic_type` and `interface_blocks`.
- Six executable test case leaves select a qualifier and an interface representation. Each leaf can also iterate its source-selected decoration placements and every graphics-stage chain enabled by the device.
- The source authors the shader modules directly as SPIR-V 1.3 assembly C++ strings. It renders four colored vertices into a 51x51 `VK_FORMAT_R8G8B8A8_UNORM` attachment, reads it back, and compares pixels with qualifier-specific references.
- The representative assembly walkthrough uses `basic_type.flat` with the first internal option, `DECORATION_IN_VERTEX`. It shows the output-side `Flat` decorations that are central to this test; the fragment stage consumes the matching location-based inputs and checks the redundant representations.

## Background Knowledge

- **Stage interfaces.** An `Output` variable, block, or structure member matches an `Input` in the subsequent shader stage when their decorations and types meet Vulkan's interface rules. Interpolation decorations are excepted from the ordinary equivalent-decoration requirement; an input/output `RelaxedPrecision` difference is also excepted ([Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L119-L190)).
- **Fragment interpolation.** An undecorated fragment input is perspective-correct. `NoPerspective` requests linear interpolation, while `Flat` uses the provoking vertex value instead ([Interpolation Decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2879-L2915)). The test's red/green vertices make these choices visible in the attachment.
- **Interface blocks.** A block is an `OpTypeStruct` interface object. Every corresponding member must match, so a block allows the test to exercise member-based transport in addition to individual scalar and vector variables ([Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L122-L165)).

## Registration Hierarchy

```text
spirv_assembly.instruction.graphics.cross_stage
├── basic_type
└── interface_blocks
```

`createCrossStageInterfaceTests` registers three leaves under each intermediate node: `flat`, `no_perspective`, and `relaxedprecision` ([registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2717-L2746)). The main Vulkan and Vulkan SC mustpass lists each contain all six paths ([Vulkan entries](../../../mustpass/main/vk-default/spirv-assembly.txt#L23859-L23864), [Vulkan SC entries](../../../mustpass/main/vksc-default/spirv-assembly.txt#L9816-L9821)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Interface representation | `basic_type`, `interface_blocks` | Selects separately declared `float`/`vec2`/`vec3`/`vec4` values or a block containing `vec4 colorVec` and `mat2 colorMat`. | [Two program builders](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L686-L1785) and [interface-block builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L1808-L2713) |
| Qualifier leaf | `flat`, `no_perspective`, `relaxedprecision` | Selects decoration text, reference images, and the shader's relative comparison epsilon. | [Decoration branches](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L690-L787), [reference selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L277-L295) |
| Decoration placement | `DECORATION_IN_VERTEX`, `DECORATION_IN_FRAGMENT`, `DECORATION_IN_ALL_SHADERS` for `flat` and `no_perspective`; `DECORATION_IN_ALL_SHADERS` only for `relaxedprecision` | An internal runtime iteration chooses which SPIR-V input/output declarations receive the decoration. It does not create additional registered leaves. | [Leaf construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2724-L2740) |
| Stage chain | VF; VTF if `tessellationShader`; VGF if `geometryShader`; VTGF if both | Adds optional producer-consumer links while preserving the same vertex-to-fragment observable. | [Feature selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L182-L188), [stage-chain construction](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L253-L275) |
| Comparison epsilon | `0.0` for `flat`; `3e-7` for `no_perspective`; `2e-3` for `relaxedprecision` | The fragment shaders compare redundant representations of a color and write white on a mismatch. | [Basic-type epsilon selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L688-L787) |

## Behavior Parameters

The primary behavioral axis is the registered test case leaf. The intermediate node changes the interface representation and the leaf changes the SPIR-V decoration semantics; together they define the behavior under test.

### `basic_type.flat`: flat basic-variable transport

Separately declared `color`, scalar, and vector outputs use `Flat` decorations. The fragment shader receives the matching values at locations 0 through 4 and checks that every redundant representation agrees with `color_in`. The test uses an exact in-shader epsilon of `0.0`.

### `basic_type.no_perspective`: linear basic-variable interpolation

The same location and type layout uses `NoPerspective`. The red/green geometry distinguishes the linear reference from the perspective-correct reference. This leaf retains the separate scalar/vector checks and uses a `3e-7` relative epsilon.

### `basic_type.relaxedprecision`: basic-variable relaxed precision

The assembly applies `RelaxedPrecision` to the interface values in all relevant stages. The source uses only the all-shaders option and a `2e-3` relative epsilon, so a permitted lower-precision result does not look like an interface mismatch.

### `interface_blocks.flat`: flat block-member transport

A `Block` structure carries `colorVec` and `colorMat` at location 1, alongside the ordinary location-0 color. `Flat` decorations are attached to the relevant block members. The fragment shader compares the vector plus two selected matrix elements with the ordinary color components.

### `interface_blocks.no_perspective`: linear block-member interpolation

This leaf uses the same block shape with `NoPerspective`. It tests that location assignment, member matching, and linear interpolation survive the selected VF, VTF, VGF, or VTGF chain.

### `interface_blocks.relaxedprecision`: relaxed precision for block members

The block path applies `RelaxedPrecision` through its selected stages and compares with the larger `2e-3` epsilon. It isolates block/member transport from the basic-variable declarations without adding decoration-placement variants.

## Shader Analysis

The shaders are CTS-authored SPIR-V assembly, not generated GLSL or HLSL. The following exact representative source is extracted from `CrossStageBasicTestsCase::initPrograms` for `basic_type.flat`, option 0 (`DECORATION_IN_VERTEX`). The source appends the five displayed `Flat` decorations after the fixed location decorations. It was assembled and validated as SPIR-V 1.3; per the `spirv_assembly` category rule, the round-trip disassembly is a validation artifact and is not published a second time.

### Representative Shader Walkthrough 1: `basic_type.flat` vertex producer, `DECORATION_IN_VERTEX`

#### Purpose

The vertex module copies input position and color, then writes the color in five equivalent forms to locations 0 through 4. `Flat` appears on all five user outputs. The matching fragment module uses the same locations and detects disagreement between the forms.

#### Parameter Values Chosen

| Parameter | Selected value | Consequence |
|-----------|----------------|-------------|
| CTS path | `spirv_assembly.instruction.graphics.cross_stage.basic_type.flat` | Selects basic variables and `Flat`. |
| Internal decoration option | `DECORATION_IN_VERTEX` | Inserts `Flat` on vertex outputs, not on the fragment declarations. |
| Representative stage | Vertex | Shows the producer-side interface declarations and writes. |
| SPIR-V target | 1.3 | Matches the `; Version: 1.3` authored assembly header. |

#### Structural Design

| Interface location | Vertex output | Write performed by `main` | Fragment-side purpose |
|--------------------|---------------|---------------------------|-----------------------|
| 0 | `%color_out : vec4` | full input color | baseline color result |
| 1 | `%r_float_out : float` | input red | checked against red |
| 2 | `%rg_float_out : vec2` | input red/green | checked against red/green |
| 3 | `%rgb_float_out : vec3` | input red/green/blue | checked against red/green/blue |
| 4 | `%rgba_float_out : vec4` | full input color | checked against full color |

`%13` is the built-in vertex-output block. `%17` is the location-0 position input and `%color_in` is the location-1 color input supplied by the host vertex buffer. `%color_out` and the four derived outputs are `Output` variables. `OpAccessChain`, `OpLoad`, `OpCompositeConstruct`, and `OpStore` implement the copies; this producer has no descriptors or device memory resources.

#### Source Code

<details>
<summary>Click to expand CTS-authored SPIR-V assembly</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 2
; Bound: 60
; Schema: 0
OpCapability Shader
%1 = OpExtInstImport "GLSL.std.450"
OpMemoryModel Logical GLSL450
OpEntryPoint Vertex %4 "main" %13 %17 %color_out %color_in %r_float_out %rg_float_out %rgb_float_out %rgba_float_out
OpMemberDecorate %11 0 BuiltIn Position
OpMemberDecorate %11 1 BuiltIn PointSize
OpMemberDecorate %11 2 BuiltIn ClipDistance
OpMemberDecorate %11 3 BuiltIn CullDistance
OpDecorate %11 Block
OpDecorate %17 Location 0
OpDecorate %color_out Location 0
OpDecorate %color_in Location 1
OpDecorate %r_float_out Location 1
OpDecorate %rg_float_out Location 2
OpDecorate %rgb_float_out Location 3
OpDecorate %rgba_float_out Location 4
OpDecorate %color_out Flat
OpDecorate %r_float_out Flat
OpDecorate %rg_float_out Flat
OpDecorate %rgb_float_out Flat
OpDecorate %rgba_float_out Flat
%2 = OpTypeVoid
%3 = OpTypeFunction %2
%6 = OpTypeFloat 32
%7 = OpTypeVector %6 4
%8 = OpTypeInt 32 0
%9 = OpConstant %8 1
%10 = OpTypeArray %6 %9
%11 = OpTypeStruct %7 %6 %10 %10
%12 = OpTypePointer Output %11
%13 = OpVariable %12 Output
%14 = OpTypeInt 32 1
%15 = OpConstant %14 0
%16 = OpTypePointer Input %7
%17 = OpVariable %16 Input
%19 = OpTypePointer Output %7
%color_out = OpVariable %19 Output
%color_in = OpVariable %16 Input
%24 = OpTypePointer Output %6
%r_float_out = OpVariable %24 Output
%26 = OpConstant %8 0
%27 = OpTypePointer Input %6
%30 = OpTypeVector %6 2
%31 = OpTypePointer Output %30
%rg_float_out = OpVariable %31 Output
%38 = OpTypeVector %6 3
%39 = OpTypePointer Output %38
%rgb_float_out = OpVariable %39 Output
%45 = OpConstant %8 2
%rgba_float_out = OpVariable %19 Output
%56 = OpConstant %8 3
%4 = OpFunction %2 None %3
%5 = OpLabel
%18 = OpLoad %7 %17
%20 = OpAccessChain %19 %13 %15
OpStore %20 %18
%23 = OpLoad %7 %color_in
OpStore %color_out %23
%28 = OpAccessChain %27 %color_in %26
%29 = OpLoad %6 %28
OpStore %r_float_out %29
%33 = OpAccessChain %27 %color_in %26
%34 = OpLoad %6 %33
%35 = OpAccessChain %27 %color_in %9
%36 = OpLoad %6 %35
%37 = OpCompositeConstruct %30 %34 %36
OpStore %rg_float_out %37
%41 = OpAccessChain %27 %color_in %26
%42 = OpLoad %6 %41
%43 = OpAccessChain %27 %color_in %9
%44 = OpLoad %6 %43
%46 = OpAccessChain %27 %color_in %45
%47 = OpLoad %6 %46
%48 = OpCompositeConstruct %38 %42 %44 %47
OpStore %rgb_float_out %48
%50 = OpAccessChain %27 %color_in %26
%51 = OpLoad %6 %50
%52 = OpAccessChain %27 %color_in %9
%53 = OpLoad %6 %52
%54 = OpAccessChain %27 %color_in %45
%55 = OpLoad %6 %54
%57 = OpAccessChain %27 %color_in %56
%58 = OpLoad %6 %57
%59 = OpCompositeConstruct %7 %51 %53 %55 %58
OpStore %rgba_float_out %59
OpReturn
OpFunctionEnd
```

</details>

#### Additional Info

- The representative assembly deliberately preserves the source IDs and instruction order. The assembler's disassembly canonicalizes IDs and spacing, so it is not text-identical to the authored source even though the binary validates.
- The corresponding fragment assembly reads the same five locations, calculates relative error for each scalar/vector form, and writes `vec4(1.0)` or component-wise `1.0` on an inconsistency ([fragment builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L901-L1059)).
- `no_perspective` substitutes `NoPerspective` decoration strings; `relaxedprecision` substitutes `RelaxedPrecision` strings and changes the comparison epsilon. `interface_blocks` changes the location-1 variables to a `Block` struct and has a different fragment checker ([basic variants](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L690-L787), [block variants](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L1810-L2005)).

## Runtime Execution and Result Checking

- `CrossStageTestInstance` creates four vertex records, with the first two red and the last two green. For `no_perspective`, the first two positions use a non-unit `w` to make perspective-correct and linear interpolation distinguishable ([vertex data](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L392-L412)).
- It allocates a host-visible vertex buffer and a 51x51 RGBA color attachment, writes the vertex data, and creates a render pass, framebuffer, and graphics pipeline for each supported stage chain ([setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L182-L251), [pipeline creation](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L446-L544)).
- For every internal decoration option and supported chain, it clears the image, transitions it to a color attachment, binds the vertex buffer and pipeline, records `vkCmdDraw` with four vertices, submits, and waits ([draw loop](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L297-L340)).
- `checkImage` copies the attachment to a host-visible transfer-destination buffer, invalidates the allocation, and calls `tcu::floatThresholdCompare` with `tcu::Vec4(0.05f)` ([readback](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L546-L595)).
- `flat` uses the interpolation reference when only the vertex output receives the decoration and the solid-red reference for other VF placements. `no_perspective` swaps the perspective and linear references. For `flat` or `no_perspective` with a fragment-only decoration and an intermediate tessellation or geometry chain, the test requires a non-match against `referenceImage1`; that is the source's intentional negative oracle ([oracle branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L354-L387)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic_type.flat` | `Flat` decoration placement or provoking-vertex interpolation for separately declared scalar/vector interface variables is wrong; the fragment consistency checks or image comparison may also be wrong. |
| `basic_type.no_perspective` | `NoPerspective` placement or linear interpolation for separately declared scalar/vector interface variables is wrong; the perspective-versus-linear reference selection may also be wrong. |
| `basic_type.relaxedprecision` | `RelaxedPrecision` propagation or permitted precision behavior across the basic-variable interface is wrong; the looser shader epsilon or image comparison may also be wrong. |
| `interface_blocks.flat` | `Flat` decoration handling, block/member interface matching, or block-member transport through the selected stages is wrong. |
| `interface_blocks.no_perspective` | `NoPerspective` handling, block/member interface matching, or linear block-member interpolation is wrong. |
| `interface_blocks.relaxedprecision` | `RelaxedPrecision` handling for block variables or members, block transport, or the relaxed comparison tolerance is wrong. |

All leaves share vertex-buffer setup, render pass, pipeline creation, readback, and threshold comparison. A shared failure cannot by itself isolate those mechanisms from stage-interface behavior.

### Cause Analysis

#### Interpolation decoration or stage-interface transport

**Possible failure symptoms:** the copied attachment differs from its selected reference, or a deliberate fragment-only multi-stage negative path unexpectedly matches `referenceImage1`. The fragment checker can also turn component groups white before host readback when redundant values disagree.

**Possible implementation causes:** Vulkan defines `Flat` as provoking-vertex selection and `NoPerspective` as linear fragment interpolation. An affected implementation can mishandle those interpolation modes, associate a producer and consumer by the wrong location/type, or lose an interface value when tessellation or geometry relays it. The image result cannot distinguish these alternatives without inspecting the failing stage chain and decoration placement.

#### Block and member matching

**Possible failure symptoms:** an `interface_blocks` leaf fails while the matching `basic_type` leaf passes, often for a selected vector or matrix component rather than every color component.

**Possible implementation causes:** interface matching requires structure members to match. Investigate block layout or member-location handling, block/member decorations, and relay code for tessellation or geometry stages. The CTS source establishes the observable result but does not identify a particular compiler or hardware component.

#### Relaxed precision or comparison tolerance

**Possible failure symptoms:** a `relaxedprecision` leaf differs from the interpolation reference beyond its shader epsilon or exceeds the host `0.05` threshold while a comparable strict leaf passes.

**Possible implementation causes:** `RelaxedPrecision` allows the relevant lower-precision behavior, and this test raises the shader's relative epsilon to `2e-3`. A result outside both tolerances can come from incorrect precision propagation, arithmetic, interface transfer, or reference/oracle selection. Source-level investigation is required to localize it further.

#### Shared rendering and readback path

**Possible failure symptoms:** all six leaves, including their VF baselines, fail with a similar image discrepancy or without a qualifier-specific pattern.

**Possible implementation causes:** common setup includes vertex input, color-attachment rendering, image-to-buffer copy, mapped-memory invalidation, and `floatThresholdCompare`. The source does not isolate these shared operations from the interface property, so investigate that setup before attributing a common failure to a decoration implementation.

## Case Pruning

### Requirement-based pruning

VF always runs. VTF is added only when `tessellationShader` is enabled; VGF is added only when `geometryShader` is enabled; VTGF requires both ([stage selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L253-L275)). Unsupported optional chains are not run. The six registered leaves occur in both observed Vulkan and Vulkan SC mustpass files, and `createCrossStageInterfaceTests` has no `CTS_USES_VULKANSC` exclusion.

### Design-based pruning

`flat` and `no_perspective` exercise all three decoration-placement options because placement changes the observed behavior. `relaxedprecision` intentionally uses only `DECORATION_IN_ALL_SHADERS`. The source fixes color type, locations, image size, and four input vertices; it uses the basic-variable and interface-block forms instead of enumerating every possible interface type and block layout.

## Key Takeaways

- The six registered leaves divide the behavior by qualifier and interface representation. Decoration placement and stage chain are internal iterations, so mustpass has six leaves rather than a Cartesian product of those dimensions.
- The fragment shader contains a device-side redundancy check, but the CTS result is determined by full-image host comparison against qualifier-specific references.
- The fragment-only placement with an optional intermediate stage is intentionally tested as a negative image condition. A pass there means the expected non-match occurred.
- The representative assembly is the CTS source of truth. It passed the SPIR-V 1.3 assemble, validate, and disassemble gate; the published source is checked against that exact extraction.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Runtime loop | [CrossStageTestInstance::iterate](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L182-L390) | Feature-driven stage selection, drawing, reference selection, and final status. |
| Vertex data | [createVertexData](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L392-L412) | Red/green input geometry and the non-unit-`w` `no_perspective` setup. |
| Pipeline setup | [makeGraphicsPipeline](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L446-L544) | Vertex-input layout and selected shader modules. |
| Image oracle | [checkImage and reference fills](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L546-L650) | Readback buffer and image-reference construction. |
| Basic-variable program builder | [CrossStageBasicTestsCase::initPrograms](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L686-L1785) | Decoration strings and basic-type stage modules. |
| Interface-block program builder | [CrossStageInterfaceTestsCase::initPrograms](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L1808-L2713) | Block/member modules and optional-stage relays. |
| Test registration | [createCrossStageInterfaceTests](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2717-L2746) | Exact hierarchy and six leaves. |
| Vulkan contract | [Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L119-L190) and [Interpolation Decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2879-L2915) | Interface-match rules and fragment interpolation semantics. |
| Mustpass coverage | [Vulkan entries](../../../mustpass/main/vk-default/spirv-assembly.txt#L23859-L23864) and [Vulkan SC entries](../../../mustpass/main/vksc-default/spirv-assembly.txt#L9816-L9821) | Current six-leaf coverage in both lists. |
