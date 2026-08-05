## Overview

**Core question:** Do the non-VulkanSC Amber GLSL scripts execute their stated arithmetic, robustness, and struct-assignment checks and report the intended Amber expectations?

- [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L1-L106) registers three Amber-backed test families under the `glsl` test category: `combined_operations`, `crash_test`, and `logical_copy`.
- The package adds these families only when Vulkan SC is not in use. Each registered test case loads an Amber script from `vulkan/amber/<family>/<case>.amber` through [`createAmberTestCase()`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L200-L216).
- The scripts contain the shaders, pipeline declarations, resources, commands, and `EXPECT` checks. This page explains the three distinct behaviors, their feature requirements, and how Amber converts script results into CTS results.

## Background Knowledge

- An Amber script is a declarative test recipe. It can define shaders and resources, assemble a graphics or compute pipeline, issue work, and compare a framebuffer or buffer value with an expected result.
- A storage buffer object (SSBO) lets a shader write values that Amber can inspect after execution. A known value written after an operation can act as a completion sentinel without asserting the operation's unspecified numeric result.
- An unspecified shader result is not a portable value to compare. A robustness test can instead check that execution reaches a known point and does not interrupt or terminate Vulkan.

## Registration Hierarchy

```text
glsl
├── combined_operations (non-VulkanSC only)
├── crash_test (non-VulkanSC only)
└── logical_copy (non-VulkanSC only)
```

[`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287) adds all three test families inside its non-VulkanSC block. The factory functions in [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L102) register the test case leaves listed below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test family | `combined_operations`, `crash_test`, `logical_copy` | Selects one of three unrelated Amber-script behaviors: expression output, robustness against zero-divisor operations, or struct assignment. | [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L102) |
| `combined_operations` case | `notxor`, `negintdivand` | Selects a whole-frame unsigned bitwise result or selected regions produced by integer division and bitwise operations. | [`combinedOperationsTests`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L51) |
| `crash_test` stage | `vert`, `tesc`, `tese`, `geom`, `frag`, `comp` | Places the risky arithmetic in each supported programmable stage represented by the scripts. | [`crashTestParameters`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L54-L78) |
| `crash_test` operation form | integer and floating division, `normalize`, `mod`, `smoothstep`, `atan(y, x)` | Exercises explicit or implied zero-divisor behavior without comparing its unspecified result. | [`divbyzero_vert.amber`](../../../data/vulkan/amber/crash_test/divbyzero_vert.amber#L33-L78) and [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L27-L72) |
| `logical_copy` source state | initialized aggregate, uninitialized local | Distinguishes assignment of a defined `Bar` value from assignment of an uninitialized local `Bar`. | [`createLogicalCopyGroup()`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L81-L102) |
| Work submission | 16x16, 32x32, or 250x250 graphics draws; a patch-list draw; 1x1x1 compute dispatch | Matches each script's chosen stage and validation mechanism. | [`notxor.amber`](../../../data/vulkan/amber/combined_operations/notxor.amber#L43-L50), [`divbyzero_tesc.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tesc.amber#L118-L146), and [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L75-L87) |

## Behavior Parameters

The primary behavioral axis is the registered test family. Each family chooses a different property and pass condition.

### `combined_operations` - expression results in graphics shaders

`notxor` supplies two `uint` push constants to a fragment shader, which writes `~(op1 ^ op2)` and must produce a white 16x16 framebuffer. `negintdivand` derives integer coordinates from the fragment color, branches on `((iv.y / 2) & 64)`, and checks cyan and red 30x30 regions. These cases compare defined framebuffer output rather than merely completing execution. See [`notxor.amber`](../../../data/vulkan/amber/combined_operations/notxor.amber#L18-L50) and [`negintdivand.amber`](../../../data/vulkan/amber/combined_operations/negintdivand.amber#L17-L52).

### `crash_test` - zero-divisor robustness across shader stages

The six cases place equivalent risky expressions in vertex, tessellation-control, tessellation-evaluation, geometry, fragment, and compute shaders. The scripts exercise division, modulo, normalization, `smoothstep`, and two-argument `atan` with zero-valued divisors or zero-length inputs. The property under test is completion: the scripts do not treat the resulting values as deterministic.

The vertex, tessellation, geometry, and compute scripts write `42` to `ssbo.data[0]` after the expression sequence and expect that sentinel. The fragment script first writes a known red pixel at `(0, 0)` and checks only that pixel after sweeping the risky expressions over the rest of the draw. See [`divbyzero_frag.amber`](../../../data/vulkan/amber/crash_test/divbyzero_frag.amber#L17-L136).

### `logical_copy` - assignment to a `std430` struct in a storage buffer

Both graphics scripts declare `Bar` with two scalar members and a two-element array, place `Bar b` after a `uvec4` in a `std430` storage buffer, and assign a local `Bar` to `b`. `initialized_struct` assigns `{0, 0, {0, 0}}` and checks the four words at byte offsets 16, 20, 24, and 28. `undefined_memory` assigns an uninitialized local `Bar`; it has no `EXPECT`, so it tests successful recipe execution rather than a defined copied value. See [`initialized_struct.amber`](../../../data/vulkan/amber/logical_copy/initialized_struct.amber#L17-L66) and [`undefined_memory.amber`](../../../data/vulkan/amber/logical_copy/undefined_memory.amber#L17-L60).

## Shader Analysis

Amber scripts store their GLSL directly rather than generating it from a CTS builder function. The page therefore uses the script-level behavior as its shader evidence instead of a reconstructed generated-shader walkthrough.

- In `notxor`, the fragment shader receives two `uint` values through a push-constant block and writes the complement of their XOR to the color attachment. The selected constants make all channels of the expected `B8G8R8A8_UNORM` framebuffer white. [`notxor.amber`](../../../data/vulkan/amber/combined_operations/notxor.amber#L20-L50)
- In the SSBO-backed `crash_test` stages, the risky expressions precede `ssbo.data[0] = 42`. The sentinel makes the check independent of each unspecified result while showing that shader execution reached the final store. [`divbyzero_vert.amber`](../../../data/vulkan/amber/crash_test/divbyzero_vert.amber#L17-L106)
- In `initialized_struct`, the vertex shader writes the aggregate-initialized local struct through a `std430` storage-buffer declaration. The fragment shader only supplies a color output for the graphics pipeline and does not participate in the buffer check. [`initialized_struct.amber`](../../../data/vulkan/amber/logical_copy/initialized_struct.amber#L17-L59)

## Runtime Execution and Result Checking

- `createAmberTestCase()` constructs each script path by prefixing `vulkan/amber/`, then appending the registered family and script filename. It also transfers CTS-side requirement strings to the `AmberTestCase`. [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L200-L216)
- The test case parses the script, compiles GLSL recipes into the CTS program collection, and supplies the compiled shader binaries to Amber for execution. [`AmberTestCase::parse()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432) and [`AmberTestCase::initPrograms()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L435-L544)
- Amber runs the recipe with Vulkan execution. A successful Amber result becomes `tcu::TestStatus::pass("Pass")`; any Amber execution error is logged and becomes `tcu::TestStatus::fail("Fail")`. [`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615)
- `combined_operations` uses framebuffer `EXPECT` commands. The five SSBO-backed crash scripts use `EXPECT ssbo_buffer IDX 0 EQ 42`; the fragment crash script checks its known red pixel. `initialized_struct` checks four SSBO offsets. `undefined_memory` has no script-level comparison. [`undefined_memory.amber`](../../../data/vulkan/amber/logical_copy/undefined_memory.amber#L47-L60)
- Tessellation-control and tessellation-evaluation cases require `tessellationShader`; the geometry case requires `geometryShader`. Their C++ registration and Amber `DEVICE_FEATURE` declarations must match, and `validateRequirements()` rejects a mismatch. [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L63-L76) and [`AmberTestCase::validateRequirements()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L648-L707)
- In compute-only mode, `AmberTestInstance::iterate()` rejects a recipe containing a non-compute shader. The graphics-script cases are therefore unsupported in that mode, while `divbyzero_comp` uses only a compute shader. [`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L557-L569)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `combined_operations` | Incorrect GLSL integer or bitwise expression evaluation, push-constant delivery, graphics rendering, or framebuffer comparison. |
| `crash_test` | Vulkan interruption or termination during a zero-divisor or zero-length operation, failure to reach the sentinel store or known pixel, or a stage/pipeline execution failure. |
| `logical_copy` | Incorrect storage-buffer struct assignment or layout for `initialized_struct`, or failure to execute the uninitialized-local assignment recipe. |

### Cause Analysis

#### Expression result, resource delivery, or framebuffer checking

**Possible failure symptoms:** `notxor` fails its full-frame white comparison, or `negintdivand` fails one of its cyan or red region comparisons.

**Possible implementation causes:** The scripts depend on fragment shader arithmetic, push constants where used, color attachment writes, and Amber's framebuffer comparison. Source-level investigation is needed to isolate which component produced a mismatching pixel.

#### Robustness completion or stage execution

**Possible failure symptoms:** A sentinel-based crash case does not expose `42` at SSBO index 0, the fragment case does not preserve its red `(0, 0)` pixel, or Amber reports an execution failure.

**Possible implementation causes:** The script comments identify interruption or termination during zero-divisor calculations as the prohibited outcome. A failure can also arise before validation from the selected shader stage, pipeline, or feature setup. The source does not support treating the unspecified expression values themselves as an expected numeric result.

#### Struct copy or storage-buffer layout

**Possible failure symptoms:** `initialized_struct` retains a nonzero value at one of the four checked byte offsets, or `undefined_memory` reports recipe execution failure.

**Possible implementation causes:** The initialized case depends on the `std430` layout and the assignment of all members of `Bar` into the bound storage buffer. For the uninitialized case, the script has no value comparison, so source-level investigation is needed to distinguish a shader, pipeline, or Amber execution failure.

## Case Pruning

### Requirement-based pruning

- The entire Amber area is absent when Vulkan SC is in use because `createGlslTests()` registers it inside `#ifndef CTS_USES_VULKANSC`. [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287)
- `divbyzero_tesc` and `divbyzero_tese` require `tessellationShader`; `divbyzero_geom` requires `geometryShader`. Missing requirements make the corresponding case unsupported. [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L54-L78) and [`AmberTestCase::checkSupport()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L229-L248)
- Compute-only mode excludes every recipe with a graphics shader. This leaves `divbyzero_comp` eligible and excludes the graphics cases. [`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L557-L569)

### Design-based pruning

- `crash_test` deliberately validates completion rather than the numeric values of zero-divisor and zero-length operations because the scripts identify those values as unspecified.
- `undefined_memory` deliberately has no `EXPECT` command. It does not claim that copying an uninitialized `Bar` yields a portable storage-buffer value.

## Key Takeaways

- This source file is a compact registration layer. Amber scripts hold the behavior that matters: shader code, resources, pipeline commands, and pass conditions.
- `combined_operations` compares defined rendered output, whereas `crash_test` checks safe completion around operations with unspecified results.
- The `crash_test` cases cover vertex, tessellation-control, tessellation-evaluation, geometry, fragment, and compute stages, with feature gating where a stage requires it.
- `logical_copy` separates a checked aggregate assignment from an execution-only uninitialized-local assignment; only `initialized_struct` asserts copied storage-buffer contents.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Amber GLSL family factories | [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L106) | Registers the three test families, their case names, and CTS-side feature requirements. |
| GLSL package registration | [`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287) | Places the families below `glsl` only for non-VulkanSC builds. |
| Amber case construction | [`createAmberTestCase()`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L200-L216) | Builds the script path and transfers requirements. |
| Amber parsing, compilation, and execution | [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L615) | Parses recipes, builds GLSL programs, runs Amber, and maps its result to CTS pass or fail. |
| Combined-operation scripts | [`combined_operations`](../../../data/vulkan/amber/combined_operations) | Defines the two graphics expression cases and framebuffer checks. |
| Crash-test scripts | [`crash_test`](../../../data/vulkan/amber/crash_test) | Defines the stage-specific robustness cases, sentinels, and feature declarations. |
| Logical-copy scripts | [`logical_copy`](../../../data/vulkan/amber/logical_copy) | Defines the storage-buffer struct-assignment cases. |
