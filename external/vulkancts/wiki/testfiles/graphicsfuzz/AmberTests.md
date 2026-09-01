## Overview

**Core question:** Can Vulkan execute a broad corpus of GraphicsFuzz shader reproducers and produce each Amber recipe's expected result?

- [`vktAmberGraphicsFuzzTests.cpp`](../../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L37-L49) registers the `graphicsfuzz` test category from one data-side index rather than constructing its test cases in C++.
- Each index entry names an Amber file, the registered test case leaf, a description, and optional CTS requirements. The shared Amber test case parses and executes the referenced recipe.
- A programmatic comparison verified 757 unique index entries, 757 unique Amber filenames, and the same 757 unique `dEQP-VK.graphicsfuzz.*` names in the default mustpass list. The two files contain the same name set in different orders.
- The corpus contains direct expected-output tests, reference-versus-variant comparisons, and a small number of compute-buffer probes. Its shader programs are part of the tested behavior, while Amber supplies the pipeline, resource, execution, and result-checking instructions.

## Background Knowledge

- **Amber recipes.** AmberScript describes shaders, pipelines, bound resources, commands, and expectations in one test artifact. A recipe can contain GLSL or SPIR-V assembly and can check buffers or framebuffer regions [AmberScript shader declarations](../../../../amber/src/docs/amber_script.md#L115-L186) and [expectations](../../../../amber/src/docs/amber_script.md#L1119-L1171).
- **Differential shader testing.** A reference shader and a transformed variant should produce equivalent observable output when the transformation preserves semantics. Comparing the outputs can expose compiler or driver handling that changes the program's behavior.
- **Mirrored requirements.** CTS must decide support before Amber executes. Requirements recorded in `index.txt` therefore mirror extension or property declarations inside the corresponding recipe; a mismatch is a test-data error rather than an unsupported result discovered during execution.

## Registration Hierarchy

```text
graphicsfuzz
├── access-new-vector-inside-if-condition
├── barrier-in-loop-with-break
├── cov-access-array-dot
├── spv-double-branch-to-same-block
└── stable-mergesort-reversed-for-loop
```

The tree shows representative direct children because expanding all 757 leaves would hide the registration mechanism. [`createGraphicsFuzzTests()`](../../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L37-L49) creates the category, and [`AmberIndexFileParser::parse()`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L169) turns every tuple in [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757) into one direct `AmberTestCase` child. The verified full leaf set matches [`graphicsfuzz.txt`](../../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Corpus size | 757 unique test case leaves and 757 unique Amber filenames | Every indexed recipe becomes one direct child of `graphicsfuzz`. | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757), [`graphicsfuzz.txt`](../../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757) |
| Index tuple | filename, test name, description, then zero or more requirements | Separates the executable recipe path from its registered identifier and support gates. | [Index parser format and construction](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L169) |
| Name family | 580 `cov-*`, 32 `spv-*`, 23 `stable-*`, 122 other names | The names distinguish coverage-oriented reproducers, SPIR-V comparison cases, stable comparison cases, and other focused bug reproducers. These prefixes describe corpus organization, not separate registered test families. | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757) |
| CTS requirement profile | 677 entries with none; 72 with `VK_KHR_shader_terminate_invocation`; 8 with both `VK_KHR_shader_float_controls` and `FloatControlsProperties.shaderSignedZeroInfNanPreserveFloat32` | Requirements stay local to recipes that need termination semantics or 32-bit signed-zero, infinity, and NaN preservation. | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757), [`addRequirement()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L623-L631) |

The counts above come from parsing the current index and comparing its registered-name set with the current mustpass file. They do not estimate coverage from filename ranges.

## Behavior Parameters

The primary behavioral axis is the recipe's result oracle. It changes what Amber treats as evidence that the shader executed correctly. Most recipes use one of the following values; two indexed recipes contain both kinds of check.

### `fixed expected-result oracle`: check a known image or buffer value

These recipes encode a result that the shader must produce. Most draw a framebuffer and use `EQ_RGBA` or `EQ_RGB`; the compute recipes use buffer probes or scalar expectations. For example, `access-new-vector-inside-if-condition` must fill a 256 by 256 framebuffer with red after executing a dynamic vector access inside an `if` condition [recipe and expectation](../../../data/vulkan/amber/graphicsfuzz/access-new-vector-inside-if-condition.amber#L18-L42), [execution and check](../../../data/vulkan/amber/graphicsfuzz/access-new-vector-inside-if-condition.amber#L97-L110).

### `reference-versus-variant histogram oracle`: compare semantically equivalent outputs

These recipes run a reference pipeline and a transformed variant pipeline, then use `EQ_HISTOGRAM_EMD_BUFFER` with a recipe-defined tolerance. `spv-double-branch-to-same-block`, for example, states that both shaders should render the same image and compares their framebuffers with tolerance `0.005` [test intent](../../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L19-L27), [final expectation](../../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L1217-L1231). This oracle allows small positional differences in pixel distributions according to Amber's histogram Earth Mover's Distance comparison rather than requiring byte-for-byte equality [AmberScript comparator definition](../../../../amber/src/docs/amber_script.md#L1167-L1170).

## Shader Analysis

Shader code is central to this corpus. One walkthrough uses a compact direct-output reproducer because it exposes the full path from CTS-authored SPIR-V through an Amber draw to a concrete framebuffer expectation. The corpus has hundreds of distinct shaders, so this walkthrough explains the shared mechanism rather than representing every compiler path or oracle shape.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.graphicsfuzz.access-new-vector-inside-if-condition
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `access-new-vector-inside-if-condition` | Selects a GraphicsFuzz bug reproducer with dynamic vector extraction inside an `if` condition. |
| `fixed expected-result oracle` | Requires every pixel in the target framebuffer to be opaque red. |
| No optional index requirement | Runs without the termination or float-control gates used by other entries. |

#### Purpose

The fragment program checks that a dynamic access to a newly constructed vector inside a condition does not corrupt later control flow or the final color write.

#### Structural Design

| Shader step | Role in the selected case |
|-------------|---------------------------|
| Initialize `x` to zero | Fixes the dynamic vector index before clamping. |
| Clamp `x` to `[0,3]` and extract from `vec4(1.0)` | Produces `1.0`, so the comparison is true and the empty branch executes. |
| Merge control flow | Rejoins the true path at the selection merge. |
| Store `(1,0,0,1)` | Writes the red result checked by Amber. |

#### Shader Code

##### Fragment Shader

This stage uses CTS-authored direct SPIR-V assembly and does not use GLSL or HLSL source. The authoritative assembly appears under the matching stage heading in `#### SPIR-V`.

#### Additional Info

- The recipe includes the ESSL 3.10 source from which the assembly was derived, but Amber consumes the `SPIRV-ASM TARGET_ENV spv1.0` block.
- The vertex stage is Amber's fixed `PASSTHROUGH` shader. It supplies positions for `DRAW_RECT` and does not participate in the GraphicsFuzz reproducer.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Test case leaf | Other leaves replace the fragment or compute program with a different reproducer; comparison recipes may provide both reference and variant programs. | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757), [`spv-double-branch-to-same-block.amber`](../../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L19-L27) |
| Result oracle | Fixed-result recipes encode a known output, while differential recipes compare two output buffers. | [Direct expectation](../../../data/vulkan/amber/graphicsfuzz/access-new-vector-inside-if-condition.amber#L97-L110), [differential expectation](../../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L1217-L1231) |
| Optional requirement | Some shaders use termination instructions or floating-point preservation semantics and receive matching per-entry gates. | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757) |

#### SPIR-V

##### Fragment SPIR-V

- Status: generated and validated
- Source: CTS-authored direct SPIR-V from this walkthrough
- Stage: frag
- Target SPIRV version: spirv1.0

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 26
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %_GLF_color
               OpExecutionMode %main OriginUpperLeft
               OpSource ESSL 310
               OpName %main "main"
               OpName %x "x"
               OpName %_GLF_color "_GLF_color"
               OpDecorate %x RelaxedPrecision
               OpDecorate %5 RelaxedPrecision
               OpDecorate %6 RelaxedPrecision
               OpDecorate %_GLF_color Location 0
       %void = OpTypeVoid
          %8 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
    %float_1 = OpConstant %float 1
         %15 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
      %int_3 = OpConstant %int 3
       %bool = OpTypeBool
%_ptr_Output_v4float = OpTypePointer Output %v4float
 %_GLF_color = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
         %20 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
       %main = OpFunction %void None %8
         %21 = OpLabel
          %x = OpVariable %_ptr_Function_int Function
               OpStore %x %int_0
          %5 = OpLoad %int %x
          %6 = OpExtInst %int %1 SClamp %5 %int_0 %int_3
         %22 = OpVectorExtractDynamic %float %15 %6
         %23 = OpFOrdGreaterThanEqual %bool %22 %float_1
               OpSelectionMerge %24 None
               OpBranchConditional %23 %25 %24
         %25 = OpLabel
               OpBranch %24
         %24 = OpLabel
               OpStore %_GLF_color %20
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- During category construction, `createAmberTestsFromIndexFile()` reads `vulkan/amber/graphicsfuzz/index.txt`. For each tuple, it creates an `AmberTestCase` whose data path is `vulkan/amber/graphicsfuzz/<filename>`, adds every trailing requirement string, and attaches the case to `graphicsfuzz` [index parser](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L100-L169), [registration loop](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L175-L189).
- Before execution, `delayedInit()` loads the selected recipe from the CTS archive and calls Amber's parser. A missing or invalid recipe becomes an internal error [parse setup](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L193-L200), [`AmberTestCase::parse()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432).
- CTS compiles recipe shaders that Amber reports as GLSL or SPIR-V assembly and retains SPIR-V hexadecimal shaders as supplied. The compiled binaries are added to the shader map used by Amber [program initialization](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L435-L543), [shader-map construction](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L584-L605).
- `checkSupport()` tests the indexed extensions, features, and properties against the Vulkan device before the instance runs [support checks](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286). At execution time, Amber checks whether the recipe's own declarations are supported by the configured Vulkan device; a failed check raises an internal error [execution requirement check](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L571-L582). The separate `validateRequirements()` path compares the index requirements with the recipe declarations and reports a mismatch during capability-coherency validation [requirement validation](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L648-L707).
- Amber receives the existing Vulkan instance, physical device, device, universal queue, enabled features, and extensions through its engine configuration. It executes the complete recipe with `ExecuteWithShaderData()` [engine configuration](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L67-L80), [execution](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615).
- Amber evaluates each recipe's `EXPECT` command or legacy `probe` assertion. The CTS case passes only when Amber reports success; otherwise CTS logs Amber's error and returns `Fail` [result conversion](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L607-L615).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fixed expected-result oracle` | The shader compiled or executed incorrectly, a resource or pipeline command produced the wrong data, or Amber observed a value different from the recipe's fixed expectation. |
| `reference-versus-variant histogram oracle` | Semantically equivalent programs produced images whose histogram distance exceeded the recipe's tolerance. |

A parse, requirement, setup, or execution error can fail either oracle before a value comparison completes.

### Cause Analysis

#### Fixed expected-result mismatch

**Possible failure symptoms:** Amber reports a failed framebuffer, buffer, scalar, or probe comparison, or reports an earlier recipe execution error instead of the encoded result.

**Possible implementation causes:** Source inspection supports several paths to the symptom: incorrect shader compilation, incorrect pipeline or resource execution, or a Vulkan operation that does not produce the recipe's specified observable value. The failing recipe and Amber diagnostic are needed to separate these causes.

#### Reference-versus-variant divergence

**Possible failure symptoms:** `EQ_HISTOGRAM_EMD_BUFFER` reports that reference and variant framebuffer histograms differ by more than the stated tolerance.

**Possible implementation causes:** A semantics-preserving shader transformation may have been compiled or executed differently from its reference program. Pipeline or resource differences encoded by the recipe can also affect one output, so the two pipeline definitions and resulting images must be inspected before assigning the fault to shader compilation.

#### Recipe infrastructure or requirement failure

**Possible failure symptoms:** CTS reports an invalid Amber file, an unsupported indexed requirement, a CTS-versus-Amber requirement mismatch, or an `ExecuteWithShaderData()` error before the expected result is accepted.

**Possible implementation causes:** The index and recipe may disagree about required extensions or properties, the recipe may be malformed, shader assembly or compilation may fail, or Amber's Vulkan setup or command execution may return an error. These are distinct from an output mismatch and should be diagnosed from the logged Amber error.

## Case Pruning

### Requirement-based pruning

The category wrapper has no category-wide feature gate. The parser classifies each trailing index string as an extension, feature, or property. Unsupported indexed requirements produce `NotSupportedError` before execution [requirement classification](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L623-L631), [support checks](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286). In the current index, 72 cases require `VK_KHR_shader_terminate_invocation`; 8 different cases require both `VK_KHR_shader_float_controls` and `FloatControlsProperties.shaderSignedZeroInfNanPreserveFloat32`. Vulkan defines `shaderTerminateInvocation` as support for SPIR-V modules using `SPV_KHR_terminate_invocation` [feature definition](../../../../vulkan-docs/src/chapters/features.adoc#L5250-L5276), and defines the float-control property as preservation support for signed zero, NaNs, and infinities in 32-bit computations [property definition](../../../../vulkan-docs/src/chapters/limits.adoc#L1031-L1035).

### Design-based pruning

`index.txt` is the registration boundary. An Amber file in the data directory is not a CTS case unless the index names it. Source review found two `.amber` files in the directory that are absent from both the index and this mustpass list: `cov-reduce-load-array-replace-extract.amber` and `write-red-after-search.amber`. The inspected sources do not state whether those files are intentionally retained or stale, so the page does not count them as coverage.

## Key Takeaways

- The C++ wrapper registers no individual GraphicsFuzz case. The current index supplies all 757 direct test case leaves, recipe paths, descriptions, and per-case requirements.
- Amber owns recipe parsing, Vulkan command execution, and the final expectation checks; CTS owns registration, support gating, shader compilation or assembly, and conversion of Amber's result into the CTS status.
- Failures must be interpreted from the selected recipe's oracle and Amber diagnostic. A fixed-output mismatch, a reference-versus-variant divergence, and a recipe infrastructure error do not establish the same cause.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| GraphicsFuzz category factory | [`createGraphicsFuzzTests()`](../../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L37-L49) | Creates `graphicsfuzz` and selects its index file. |
| Index tuple parser and registration loop | [`AmberIndexFileParser`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L32-L189) | Maps every index tuple to one `AmberTestCase` and attaches requirements. |
| Amber parse and program setup | [`AmberTestCase::parse()` and `initPrograms()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L543) | Parses recipes and prepares their shader binaries. |
| Amber execution and CTS status | [`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615) | Supplies the Vulkan engine config, executes the recipe, logs errors, and returns pass or fail. |
| Requirement support and consistency | [`checkSupport()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286), [`validateRequirements()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L648-L707) | Checks indexed support gates and provides the index-versus-recipe consistency audit path. |
| Full registration data | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757) | Defines the registered recipes, names, descriptions, and optional requirements. |
| Default mustpass coverage | [`graphicsfuzz.txt`](../../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757) | Lists the 757 default conformance paths used for coverage comparison. |
