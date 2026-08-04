## Overview

**Core question:** When CTS requests a specific SPIR-V version, do all modules compiled for that case carry exactly that version and still execute correctly?

`spirv_version` is a SPIR-V-assembly family beneath both instruction-test roots. It requests each version from `1.0` through `1.6` for a compute shader or for one selected graphics stage, examines every compiled module's version header, and then runs the ordinary compute or graphics validation path.

The implementation is [`vktSpvAsmSpirvVersionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp). The obsolete navigation page [`vktSpvAsmSpirvVersionTests.md`](vktSpvAsmSpirvVersionTests.md) remains unchanged.

## Background Knowledge

- **SPIR-V version request and header.** `SpirVAsmBuildOptions` receives the requested `SpirvVersion` while CTS compiles the authored assembly. `extractSpirvVersion()` then reads the version recorded in each resulting binary, so the test checks the build result rather than only whether the device supports some SPIR-V version.
- **Complete graphics pipelines.** A custom vertex, tessellation, geometry, or fragment stage needs companion stages to execute. The graphics helper therefore creates a vertex/fragment, tessellation, or geometry pipeline around the selected stage before its common verifier runs.
- **Storage-buffer declaration transition.** The compute source selects `Uniform` plus legacy `BufferBlock` through SPIR-V `1.3`, and `StorageBuffer` plus `Block` above `1.3`. This gives the same input/output program a declaration form suitable for the requested assembly version.

## Registration Hierarchy

[`createSpivVersionCheckTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L376-L403) is added to the compute instruction root and the graphics instruction root by [`vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21319-L21320) and [`#L21452-L21453`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21452-L21453), respectively. It is not inside a `CTS_USES_VULKANSC` exclusion.

```text
spirv_assembly.instruction.compute.spirv_version
├── 1_0_compute
├── 1_1_compute
├── 1_2_compute
├── 1_3_compute
├── 1_4_compute
├── 1_5_compute
└── 1_6_compute

spirv_assembly.instruction.graphics.spirv_version
├── 1_0_fragment
├── 1_0_geometry
├── 1_0_tesselation_control
├── 1_0_tesselation_evaluation
├── 1_0_vertex
├── 1_1_fragment
├── 1_1_geometry
├── 1_1_tesselation_control
├── 1_1_tesselation_evaluation
├── 1_1_vertex
├── 1_2_fragment
├── 1_2_geometry
├── 1_2_tesselation_control
├── 1_2_tesselation_evaluation
├── 1_2_vertex
├── 1_3_fragment
├── 1_3_geometry
├── 1_3_tesselation_control
├── 1_3_tesselation_evaluation
├── 1_3_vertex
├── 1_4_fragment
├── 1_4_geometry
├── 1_4_tesselation_control
├── 1_4_tesselation_evaluation
├── 1_4_vertex
├── 1_5_fragment
├── 1_5_geometry
├── 1_5_tesselation_control
├── 1_5_tesselation_evaluation
├── 1_5_vertex
├── 1_6_fragment
├── 1_6_geometry
├── 1_6_tesselation_control
├── 1_6_tesselation_evaluation
└── 1_6_vertex
```

### Matrix and mustpass reconciliation

The generator spans seven versions. For the compute call it accepts only `OPERATION_COMPUTE`, yielding `7 × 1 = 7` leaves. For the graphics call it accepts the five non-compute operations, yielding `7 × 5 = 35` leaves. Thus each profile carries 42 leaves.

| Root | Version values | Operation values | Leaves |
|------|----------------|------------------|-------:|
| `compute.spirv_version` | `1_0` through `1_6` | `compute` | 7 |
| `graphics.spirv_version` | `1_0` through `1_6` | `vertex`, `tesselation_evaluation`, `tesselation_control`, `geometry`, `fragment` | 35 |
| **Total** | | | **42** |

The standard [`vk-default/spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt) and Vulkan SC [`vksc-default/spirv-assembly.txt`](../../../mustpass/main/vksc-default/spirv-assembly.txt) each list the same 7 compute plus 35 graphics paths under their respective `dEQP-VK` and `dEQP-VKSC` prefixes. They are profile lists for the same generator, not distinct construction modes.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Requested SPIR-V version | `1_0`, `1_1`, `1_2`, `1_3`, `1_4`, `1_5`, `1_6` | Passed to `SpirVAsmBuildOptions` and compared to every compiled module header. | [`version loop`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L385-L398) |
| Operation | `compute`; `vertex`, `tesselation_evaluation`, `tesselation_control`, `geometry`, `fragment` | Selects compute execution or the graphics-stage builder and its complete pipeline context. | [`operation names and loop`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L378-L400) |
| Compute storage declaration | `Uniform`/`BufferBlock` through `1_3`; `StorageBuffer`/`Block` above `1_3` | Keeps the authored two-buffer compute program valid across the tested versions. | [`getComputeSourceCode()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L118-L154) |

## Behavior Parameters

### `1_0`: baseline requested version

CTS builds the selected operation with `SPIRV_VERSION_1_0` and requires every compiled binary to report `1.0`. Compute uses the legacy `Uniform`/`BufferBlock` declaration path.

### `1_1`: requested version `1.1`

The same selected operation and execution check are built with `SPIRV_VERSION_1_1`; the binary-header check must observe `1.1` for every compiled module. Compute remains on the legacy declaration path.

### `1_2`: requested version `1.2`

This value changes the requested build version while preserving the same operation matrix and follow-on oracle. Compute remains on the legacy declaration path.

### `1_3`: final legacy-buffer version

The request and binary-header expectation become `1.3`. It is the last tested version whose compute assembly uses `Uniform` and `BufferBlock`.

### `1_4`: first storage-buffer declaration version

The request and binary-header expectation become `1.4`. Compute switches to `StorageBuffer` and `Block`, and includes `%indata` and `%outdata` in the compute entry-point interface.

### `1_5`: requested version `1.5`

This case retains the newer compute declaration form and requires all produced modules to report `1.5`; operation selection and ordinary execution checking do not otherwise change.

### `1_6`: requested version `1.6`

This is the highest generated request. It retains the newer compute declaration form and requires all produced modules to report `1.6`.

The requested version is the primary behavior axis because it is the value supplied to compilation and directly checked in binary output. The operation is secondary: it chooses the execution context in which that versioned module is exercised.

## Shader Analysis

The shaders are CTS-authored SPIR-V assembly, not generated GLSL/HLSL. Compute source is constructed by [`getComputeSourceCode()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L118-L154); graphics source is created through the common stage builders selected by [`initGraphicsInstanceContext()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L69-L116). The graphics `testfun` extracts the first float from its `vec4` parameter, doubles it, subtracts the original, and returns the original first component. It supplies simple arithmetic to the common graphics harness; this family’s distinct assertion is the compiled-binary version.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

```text
dEQP-VK.spirv_assembly.instruction.compute.spirv_version.1_4_compute
```

| Parameter | Selected value | Consequence |
|-----------|----------------|-------------|
| Requested version | `1_4` | `SpirVAsmBuildOptions` requests SPIR-V 1.4, and the binary collection must report `1.4`. |
| Operation | `compute` | Uses the authored `OpFNegate` program and common compute verifier. |
| Storage declaration | `StorageBuffer` / `Block` | Uses the post-`1.3` buffer form at bindings 0 and 1. |
| Workgroups | `100 × 1 × 1` | One invocation processes each float. |

#### Purpose

This case demonstrates the first newer-declaration path. It checks that requesting SPIR-V `1.4` is reflected in the compiled module and that the module correctly negates each input float into the output buffer.

#### Structural Design

| Phase | Authored assembly behavior | Role in the check |
|-------|----------------------------|-------------------|
| Entry point | Declares `GLCompute`, `%id`, `%indata`, and `%outdata`; sets `LocalSize 1 1 1`. | Makes global invocation X select one buffer element. |
| Resources | Declares two `StorageBuffer` variables with `Block` and bindings 0/1. | Provides separate input and output runtime arrays. |
| Addressing | Loads `gl_GlobalInvocationID.x` and creates input/output access chains. | Maps each workgroup to one input and output element. |
| Arithmetic | Loads one float and emits `OpFNegate`. | Produces the expected negative value. |
| Store | Writes the result through `%outdata`. | Makes the common host verifier observe execution. |

#### Source Code

This is the exact `1_4` specialization of the compute assembly assembled by the source helpers. Audit-time semantic validation of this final fence uses `spirv-as --target-env spv1.4` → `spirv-val --target-env vulkan1.2` → `spirv-dis`; the source shown here does not establish a separate generation-time `spirv-as`/`spirv-val`/`spirv-dis` gate. Its disassembly is intentionally not duplicated for this `spirv_assembly` page.

<details>
<summary>Click to expand CTS-authored SPIR-V assembly</summary>

```llvm
OpCapability Shader
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %main "main" %id %indata %outdata
OpExecutionMode %main LocalSize 1 1 1
OpSource GLSL 430
OpName %main           "main"
OpName %id             "gl_GlobalInvocationID"
OpDecorate %id BuiltIn GlobalInvocationId
OpDecorate %buf Block
OpDecorate %indata DescriptorSet 0
OpDecorate %indata Binding 0
OpDecorate %outdata DescriptorSet 0
OpDecorate %outdata Binding 1
OpDecorate %f32arr ArrayStride 4
OpMemberDecorate %buf 0 Offset 0
%bool      = OpTypeBool
%void      = OpTypeVoid
%voidf     = OpTypeFunction %void
%u32       = OpTypeInt 32 0
%i32       = OpTypeInt 32 1
%f32       = OpTypeFloat 32
%uvec3     = OpTypeVector %u32 3
%fvec3     = OpTypeVector %f32 3
%uvec3ptr  = OpTypePointer Input %uvec3
%i32ptr    = OpTypePointer StorageBuffer %i32
%f32ptr    = OpTypePointer StorageBuffer %f32
%i32arr    = OpTypeRuntimeArray %i32
%f32arr    = OpTypeRuntimeArray %f32
%buf     = OpTypeStruct %f32arr
%bufptr  = OpTypePointer StorageBuffer %buf
%indata    = OpVariable %bufptr StorageBuffer
%outdata   = OpVariable %bufptr StorageBuffer
%id        = OpVariable %uvec3ptr Input
%zero      = OpConstant %i32 0
%main      = OpFunction %void None %voidf
%label     = OpLabel
%idval     = OpLoad %uvec3 %id
%x         = OpCompositeExtract %u32 %idval 0
             OpNop
%inloc     = OpAccessChain %f32ptr %indata %zero %x
%inval     = OpLoad %f32 %inloc
%neg       = OpFNegate %f32 %inval
%outloc    = OpAccessChain %f32ptr %outdata %zero %x
             OpStore %outloc %neg
             OpReturn
             OpFunctionEnd
```

</details>

#### Parameter Variation Summary

| Variation from the representative | Assembly or pipeline change | Version/execution check |
|-----------------------------------|-----------------------------|-------------------------|
| `1_0` through `1_3` compute | Uses `Uniform`/`BufferBlock`; omits the two buffers from the entry-point interface. | Each binary must report the selected lower version, then the same negation oracle runs. |
| `1_5` or `1_6` compute | Retains the `StorageBuffer`/`Block` form. | Each binary must report the selected newer version, then the same negation oracle runs. |
| `vertex` or `fragment` | Uses vertex-plus-fragment common graphics context. | Every module in that context must report the requested version before the default graphics verifier runs. |
| `tesselation_control` or `tesselation_evaluation` | Uses a complete tessellation pipeline. | Requires `tessellationShader`; binary-version check still covers every compiled module. |
| `geometry` | Uses vertex, geometry, and fragment context. | Requires `geometryShader`; binary-version check still covers every compiled module. |

## Runtime Execution and Result Checking

1. [`initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L290-L355) creates `SpirVAsmBuildOptions` from the used Vulkan version and the requested `SpirvVersion`, then adds the compute assembly or the selected graphics-stage assembly.
2. Compute specifications contain 100 pseudo-random positive floats in the input buffer, their negations as expected output, and `numWorkGroups = (100, 1, 1)` ([`getComputeShaderSpec()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L156-L180)).
3. Each instance first calls [`isSpirVersionsAsRequested()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L182-L198). It asserts a nonempty `BinaryCollection`, extracts every binary's version, and fails immediately if any differs from the requested version.
4. Only after a successful version comparison does compute delegate to `SpvAsmComputeShaderInstance::iterate()`; its common checker compares the output floats with the expected negatives using epsilon `0.001` ([`verifyOutputWithEpsilon()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L33-L61)).
5. Graphics then delegates to `runAndVerifyDefaultPipeline()`. This implementation does not define a separate graphics result oracle, so its graphics execution/result semantics remain those of the shared helper.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `1_0`, `1_1`, `1_2`, or `1_3` | Requested-version propagation or SPIR-V-header generation is wrong; the legacy compute buffer declaration path may also be implicated for compute. |
| `1_4`, `1_5`, or `1_6` | Requested-version propagation or SPIR-V-header generation is wrong; the newer compute storage-buffer/interface path may also be implicated for compute. |
| Any version only for `compute` | Compute assembly construction, binary collection contents, or the common compute execution path is wrong. |
| Any version only for one graphics operation | The selected graphics-stage builder, its pipeline composition, or the common graphics verifier is wrong. |
| Many versions and operations | Shared assembly compilation/build-option propagation or version extraction is wrong. |

### Cause Analysis

#### Requested version not reflected in compiled modules

**Possible failure symptoms:** the case fails with `Binary SPIR-V version is different from requested` before its compute output or graphics pipeline result is evaluated. A pattern confined to one requested value shows that at least one binary in that case does not report the value requested by its `SpirVAsmBuildOptions`.

**Possible implementation causes:** compilation may not propagate the requested build option into the module header, a stage builder may use different options, or `extractSpirvVersion()` may decode the binary header incorrectly. The test establishes a request/header mismatch but does not identify which compiler, CTS, or extraction component caused it.

#### Version-boundary compute declaration path

**Possible failure symptoms:** compute failures split at the `1_3`/`1_4` boundary: legacy-version leaves can pass while newer-version leaves fail, or the reverse. A binary-header mismatch remains distinct from a follow-on numerical mismatch because the former exits before the common compute verifier.

**Possible implementation causes:** the source changes `Uniform`/`BufferBlock` to `StorageBuffer`/`Block` above `1.3`, and adds the two buffer variables to the entry-point interface. A failure limited to one side can involve assembly construction, compilation, or the resource interpretation for that declaration form. The test does not on its own isolate the exact layer.

#### Operation-specific execution path

**Possible failure symptoms:** all binary versions match, but only compute, tessellation, geometry, or another selected graphics operation fails its ordinary execution check. Tessellation and geometry cases can instead be reported as not supported when their required feature is absent.

**Possible implementation causes:** compute uses its common buffer-output harness, while graphics uses operation-specific common builders and `runAndVerifyDefaultPipeline()`. A stage-specific pattern can therefore involve the selected stage builder, complete pipeline composition, or shared verifier. More evidence is required to distinguish those possibilities.

#### Shared build-option or extraction path

**Possible failure symptoms:** many requested versions and both compute and graphics operations fail the same header comparison, potentially before any execution oracle runs.

**Possible implementation causes:** common build-option propagation, binary collection population, or version extraction is shared across the family. The broad pattern is useful localization evidence, but it is not proof of a particular driver or host defect.

## Case Pruning

### Requirement-based pruning

- [`checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L274-L288) rejects a requested version above `getMaxSpirvVersionForAsm(context.getUsedApiVersion())` as not supported.
- `tesselation_control` and `tesselation_evaluation` require `tessellationShader`; `geometry` requires `geometryShader`. The relevant leaves are not supported if the feature is unavailable.

### Design-based pruning

The compute registration intentionally excludes the five graphics operations, while the graphics registration intentionally excludes `compute`. This produces one 7-leaf compute matrix and one 35-leaf graphics matrix rather than redundant cross-root registrations. The source’s registered spelling is `tesselation_*`, and that identifier is preserved in the leaf names.

## Key Takeaways

- The family checks an exact compiled-binary property: every binary in a case must report the requested SPIR-V version, not merely a version the device accepts.
- The seven-version matrix runs once as compute and once for each of five graphics operations, accounting for 42 mustpass leaves in both observed profile lists.
- Version `1.4` is the compute declaration boundary: versions above `1.3` use `StorageBuffer`/`Block` and expose both buffers in the entry-point interface.
- A header mismatch fails before ordinary shader execution; a later failure instead belongs to the shared compute or graphics validation path.
- See `## Failure Meaning` for the request/header, declaration-boundary, operation-specific, and shared-path diagnostic map.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Root registrations | [`vktSpvAsmInstructionTests.cpp#L21319-L21320`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21319-L21320), [`#L21452-L21453`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21452-L21453) | Adds the family beneath compute and graphics instruction roots. |
| Graphics context | [`initGraphicsInstanceContext()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L69-L116) | Selects a complete graphics stage set and supplies the custom arithmetic fragment. |
| Compute assembly | [`getComputeSourceCode()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L118-L154) | Defines the authored compute module and version-boundary declaration choice. |
| Compute data / expected output | [`getComputeShaderSpec()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L156-L180) | Creates 100 positive floats and their negative expected outputs. |
| Version assertion | [`isSpirVersionsAsRequested()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L182-L198) | Extracts and compares every compiled module version. |
| Runtime instances | [`SpvAsmGraphicsSpirvVersionsInstance::iterate()` and `SpvAsmComputeSpirvVersionsInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L217-L253) | Shows version-check ordering and common verifier delegation. |
| Support and program setup | [`checkSupport()` and `initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L274-L355) | Defines support gates and attaches requested-version build options. |
| Leaf generator | [`createSpivVersionCheckTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L376-L403) | Defines exact version/operation names and registration products. |
| Compute verifier | [`verifyOutputWithEpsilon()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L33-L61) | Defines the shared float result comparison. |
