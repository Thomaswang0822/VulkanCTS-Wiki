# vktAmberGlslTests.cpp

## Overview

[`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L1-L106) registers the Amber-backed GLSL groups that are added under `glsl` when Vulkan SC is not in use. The GLSL package registration calls `createCombinedOperationsGroup()`, `createCrashTestGroup()`, and `createLogicalCopyGroup()` inside the non-VulkanSC block in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287). Each factory builds a `tcu::TestCaseGroup` and creates `AmberTestCase` children whose scripts are loaded from `data/vulkan/amber/<group>/<case>.amber` by the Amber helper in [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L200-L216).

## Role

Registration / dispatcher file for a small set of Amber scripts, with the per-test shader programs, pipelines, and expectations defined in the corresponding `.amber` data files.

## Source Code

- Primary source: [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L1-L106)
- Root package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287)
- Amber case construction helper: [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L200-L216)
- Amber execution and pass/fail wrapper: [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615)
- Inspected Amber script directories: [`combined_operations`](../../../data/vulkan/amber/combined_operations), [`crash_test`](../../../data/vulkan/amber/crash_test), and [`logical_copy`](../../../data/vulkan/amber/logical_copy)

## Registration Hierarchy

```text
glsl
├── combined_operations (non-VulkanSC only)
├── crash_test (non-VulkanSC only)
└── logical_copy (non-VulkanSC only)
```

The parseable tree lists the three `glsl` direct children registered by this source file. The child cases below those roots are described in `## Test Families`, where the C++ registration vectors and Amber scripts provide the case-level evidence.

## Test Families

### combined_operations — Bitwise and integer-expression Amber graphics cases

The `combined_operations` group name and its two direct child names come from the `combinedOperationsTests` vector in [`createCombinedOperationsGroup()`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L51). Each child is registered through `createAmberTestCase()` with the group name as the Amber data-directory name and `<case>.amber` as the script filename at [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L45-L50).

| Case | Script-backed behavior |
|---|---|
| `notxor` | Uses a passthrough vertex shader and a GLSL fragment shader that writes `~(op1 ^ op2)` from two `uint` push constants, then expects the full 16x16 `B8G8R8A8_UNORM` framebuffer to be white at [`notxor.amber`](../../../data/vulkan/amber/combined_operations/notxor.amber#L18-L50). |
| `negintdivand` | Draws a 250x250 rectangle, computes `ivec2(frag_color.xy * 256)`, branches on `((iv.y / 2) & 64)`, and checks two 30x30 framebuffer regions for cyan and red at [`negintdivand.amber`](../../../data/vulkan/amber/combined_operations/negintdivand.amber#L17-L52). |

### crash_test — Division-by-zero and related undefined-result robustness scripts

The `crash_test` group is generated from `crashTestParameters`, which registers six children and passes explicit CTS feature requirements only for tessellation-control, tessellation-evaluation, and geometry cases at [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L54-L78). The Amber scripts exercise explicit division, modulo, normalization, `smoothstep`, and two-argument `atan` forms that use zero-valued divisors or zero-length inputs; the fragment-script comment states the intended criterion as avoiding Vulkan interruption or termination for such unspecified results at [`divbyzero_frag.amber`](../../../data/vulkan/amber/crash_test/divbyzero_frag.amber#L17-L24).

| Case | Shader stage where the risky operations are performed | Completion / expectation evidence |
|---|---|---|
| `divbyzero_vert` | Vertex shader, limited to `gl_VertexIndex == 0`, writes `ssbo.data[1]` through `ssbo.data[19]` from the risky expressions and finally writes `ssbo.data[0] = 42` at [`divbyzero_vert.amber`](../../../data/vulkan/amber/crash_test/divbyzero_vert.amber#L17-L79). | The script draws a 32x32 rectangle and expects `ssbo_buffer` index 0 to equal 42 at [`divbyzero_vert.amber`](../../../data/vulkan/amber/crash_test/divbyzero_vert.amber#L91-L106). |
| `divbyzero_tesc` | Tessellation-control shader, limited to `gl_InvocationID == 0`, performs the same expression sequence and writes the sentinel at [`divbyzero_tesc.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tesc.amber#L21-L91). | The script declares `DEVICE_FEATURE tessellationShader`, draws a patch list, and expects `ssbo_buffer` index 0 to equal 42 at [`divbyzero_tesc.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tesc.amber#L17-L18) and [`divbyzero_tesc.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tesc.amber#L127-L146). |
| `divbyzero_tese` | Tessellation-evaluation shader, limited by a selected output position, performs the risky expression sequence and writes the sentinel at [`divbyzero_tese.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tese.amber#L42-L107). | The script declares `DEVICE_FEATURE tessellationShader`, draws a patch list, and expects `ssbo_buffer` index 0 to equal 42 at [`divbyzero_tese.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tese.amber#L17-L18) and [`divbyzero_tese.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tese.amber#L130-L149). |
| `divbyzero_geom` | Geometry shader performs the risky expression sequence once, writes the sentinel, then emits the input triangle at [`divbyzero_geom.amber`](../../../data/vulkan/amber/crash_test/divbyzero_geom.amber#L21-L95). | The script declares `DEVICE_FEATURE geometryShader`, draws a rectangle through the geometry pipeline, and expects `ssbo_buffer` index 0 to equal 42 at [`divbyzero_geom.amber`](../../../data/vulkan/amber/crash_test/divbyzero_geom.amber#L17-L18) and [`divbyzero_geom.amber`](../../../data/vulkan/amber/crash_test/divbyzero_geom.amber#L109-L126). |
| `divbyzero_frag` | Fragment shader sweeps expressions by `gl_FragCoord`, including the integer case `7 / (ifragcoord.y - 8)`, and writes a known red pixel at `(0, 0)` before the risky branch at [`divbyzero_frag.amber`](../../../data/vulkan/amber/crash_test/divbyzero_frag.amber#L25-L123). | The script draws a 32x32 rectangle and checks only the known 1x1 pixel at `(0, 0)` for red, so it verifies successful completion plus the sentinel pixel rather than exact values from the undefined-result expressions at [`divbyzero_frag.amber`](../../../data/vulkan/amber/crash_test/divbyzero_frag.amber#L126-L136). |
| `divbyzero_comp` | Compute shader performs the risky expression sequence once and writes the sentinel at [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L16-L72). | The script dispatches a 1x1x1 compute pipeline and expects `ssbo_buffer` index 0 to equal 42 at [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L75-L87). |

### logical_copy — Struct assignment cases in Amber graphics scripts

The `logical_copy` group is registered from two `TestParameters` entries, both without explicit CTS feature requirements, at [`createLogicalCopyGroup()`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L81-L102). Both Amber scripts declare the same `Bar` structure inside a `std430` storage buffer with `Bar b` starting at offset 16, bind that buffer as storage, and run a 32x32 graphics draw at [`initialized_struct.amber`](../../../data/vulkan/amber/logical_copy/initialized_struct.amber#L17-L61) and [`undefined_memory.amber`](../../../data/vulkan/amber/logical_copy/undefined_memory.amber#L17-L60).

`initialized_struct` assigns `Bar new_bar = {0, 0, {0, 0}}` to `b` and then expects four 32-bit words at byte offsets 16, 20, 24, and 28 to become zero at [`initialized_struct.amber`](../../../data/vulkan/amber/logical_copy/initialized_struct.amber#L32-L36) and [`initialized_struct.amber`](../../../data/vulkan/amber/logical_copy/initialized_struct.amber#L63-L66). `undefined_memory` declares `Bar new_bar;` without initialization and assigns it to `b`, but the inspected script has no `EXPECT` command after the draw, so its pass condition is successful Amber execution rather than a defined buffer-value comparison at [`undefined_memory.amber`](../../../data/vulkan/amber/logical_copy/undefined_memory.amber#L32-L35) and [`undefined_memory.amber`](../../../data/vulkan/amber/logical_copy/undefined_memory.amber#L47-L60).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Registered Amber groups | `combined_operations`, `crash_test`, and `logical_copy` are the group-name constants used by the three factories in [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L102). |
| Amber script path construction | `createAmberTestCase()` prefixes scripts with `vulkan/amber/`, appends the group/category, and then appends the filename supplied by the GLSL factory at [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L200-L216). |
| `combined_operations` cases | `notxor` and `negintdivand` are the only entries in `combinedOperationsTests` at [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L39-L43). |
| `crash_test` shader stages | Case names cover vertex, tessellation-control, tessellation-evaluation, geometry, fragment, and compute stages through `divbyzero_vert`, `divbyzero_tesc`, `divbyzero_tese`, `divbyzero_geom`, `divbyzero_frag`, and `divbyzero_comp` at [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L62-L70). |
| Risky arithmetic/function forms in `crash_test` | The SSBO-based stage scripts use integer division, floating division, scalar/vector `normalize`, integer and floating/vector `mod`, scalar/vector `smoothstep`, and scalar/vector `atan(y, x)` before writing sentinel value 42, as shown for vertex and compute at [`divbyzero_vert.amber`](../../../data/vulkan/amber/crash_test/divbyzero_vert.amber#L33-L78) and [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L27-L72). |
| Graphics draw sizes and compute dispatch | `notxor` draws 16x16, `negintdivand` draws 250x250, most crash graphics scripts draw 32x32 or a six-vertex patch list, logical-copy scripts draw 32x32, and the compute crash script dispatches 1x1x1 at [`notxor.amber`](../../../data/vulkan/amber/combined_operations/notxor.amber#L43-L50), [`negintdivand.amber`](../../../data/vulkan/amber/combined_operations/negintdivand.amber#L50-L52), [`divbyzero_tesc.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tesc.amber#L118-L146), and [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L79-L87). |
| `logical_copy` struct states | `initialized_struct` uses aggregate initialization of `Bar`, while `undefined_memory` assigns an uninitialized local `Bar`, at [`initialized_struct.amber`](../../../data/vulkan/amber/logical_copy/initialized_struct.amber#L32-L36) and [`undefined_memory.amber`](../../../data/vulkan/amber/logical_copy/undefined_memory.amber#L32-L35). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| Non-VulkanSC registration | The three Amber GLSL factories are added under `glsl` inside `#ifndef CTS_USES_VULKANSC` in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1281-L1287). |
| CTS feature requirement plumbing | Requirements passed to `createAmberTestCase()` are added to the `AmberTestCase` requirement set at [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L213-L216), and `AmberTestCase::checkSupport()` throws `NotSupportedError` for missing feature strings at [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L229-L248). |
| Tessellation crash cases | `divbyzero_tesc` and `divbyzero_tese` pass `Features.tessellationShader` in the C++ registration table and also declare `DEVICE_FEATURE tessellationShader` in their Amber scripts at [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L63-L67), [`divbyzero_tesc.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tesc.amber#L17-L18), and [`divbyzero_tese.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tese.amber#L17-L18). |
| Geometry crash case | `divbyzero_geom` passes `Features.geometryShader` in the C++ registration table and declares `DEVICE_FEATURE geometryShader` in the Amber script at [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L67-L68) and [`divbyzero_geom.amber`](../../../data/vulkan/amber/crash_test/divbyzero_geom.amber#L17-L18). |
| Amber requirement consistency | `validateRequirements()` parses the Amber recipe, normalizes Amber `DEVICE_FEATURE` names to `Features.<name>`, and requires the recipe requirements to match the CTS-side requirements at [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L648-L707). |
| Cases without explicit feature requirements | `combined_operations`, vertex/fragment/compute crash cases, and both `logical_copy` cases pass empty requirement vectors in their C++ tables; the inspected scripts for those cases do not declare `DEVICE_FEATURE` lines at [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L39-L50), [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L63-L70), and [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L90-L100). |
| Compute-only command-line mode | `AmberTestInstance::iterate()` rejects non-compute Amber shaders when the CTS command line uses compute-only mode, so graphics-script cases are not eligible in that mode while `divbyzero_comp` uses only a compute shader at [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L557-L569) and [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L16-L87). |

## Verification Methods

- The shared Amber runner executes the parsed recipe with `amber::ExecutionType::kExecute` and returns a CTS pass only when Amber execution succeeds; Amber failure text is logged and converted to `tcu::TestStatus::fail("Fail")` at [`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615).
- `combined_operations` cases use framebuffer `EXPECT` commands: `notxor` expects the whole 16x16 framebuffer to be `EQ_RGBA 255 255 255 255`, while `negintdivand` expects two 30x30 regions to match cyan and red at [`notxor.amber`](../../../data/vulkan/amber/combined_operations/notxor.amber#L48-L50) and [`negintdivand.amber`](../../../data/vulkan/amber/combined_operations/negintdivand.amber#L50-L52).
- SSBO-based crash cases (`divbyzero_vert`, `divbyzero_tesc`, `divbyzero_tese`, `divbyzero_geom`, and `divbyzero_comp`) use successful execution plus `EXPECT ssbo_buffer IDX 0 EQ 42` after the risky operations write a known sentinel at [`divbyzero_vert.amber`](../../../data/vulkan/amber/crash_test/divbyzero_vert.amber#L76-L106), [`divbyzero_tesc.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tesc.amber#L88-L146), [`divbyzero_tese.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tese.amber#L104-L149), [`divbyzero_geom.amber`](../../../data/vulkan/amber/crash_test/divbyzero_geom.amber#L81-L126), and [`divbyzero_comp.amber`](../../../data/vulkan/amber/crash_test/divbyzero_comp.amber#L70-L87).
- The fragment crash case is intentionally weaker than exact arithmetic validation: it writes a known red pixel before the expression sweep and checks only that pixel, matching the script comment that the test succeeds if division-by-zero expressions do not crash at [`divbyzero_frag.amber`](../../../data/vulkan/amber/crash_test/divbyzero_frag.amber#L17-L24) and [`divbyzero_frag.amber`](../../../data/vulkan/amber/crash_test/divbyzero_frag.amber#L32-L36).
- `initialized_struct` validates the storage-buffer bytes corresponding to the copied `Bar` members by expecting zero at offsets 16, 20, 24, and 28 after the draw at [`initialized_struct.amber`](../../../data/vulkan/amber/logical_copy/initialized_struct.amber#L48-L66).
- `undefined_memory` has no script-level `EXPECT`; the documented criterion is therefore only that the Amber draw completes without a recipe execution failure at [`undefined_memory.amber`](../../../data/vulkan/amber/logical_copy/undefined_memory.amber#L47-L60) and [`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L607-L615).

## Test Principles

- The source file keeps registration data small and delegates shader contents, pipelines, resources, draws, dispatches, and expectations to Amber scripts through `createAmberTestCase()` at [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L37-L102) and [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L200-L216).
- `crash_test` avoids asserting the numerical results of undefined or unspecified zero-divisor expressions; instead the inspected scripts use sentinel writes or a known framebuffer pixel to prove execution reached a known point after or around those expressions at [`divbyzero_vert.amber`](../../../data/vulkan/amber/crash_test/divbyzero_vert.amber#L33-L106) and [`divbyzero_frag.amber`](../../../data/vulkan/amber/crash_test/divbyzero_frag.amber#L17-L24).
- Feature-gated Amber scripts duplicate their requirements in both CTS-side registration and Amber `DEVICE_FEATURE` declarations, and the Amber test-case utility checks that the two requirement sets match before running the test at [`vktAmberGlslTests.cpp`](../../../modules/vulkan/amber/vktAmberGlslTests.cpp#L63-L76), [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L648-L707), and the feature declarations in [`divbyzero_tesc.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tesc.amber#L17-L18), [`divbyzero_tese.amber`](../../../data/vulkan/amber/crash_test/divbyzero_tese.amber#L17-L18), and [`divbyzero_geom.amber`](../../../data/vulkan/amber/crash_test/divbyzero_geom.amber#L17-L18).
- The logical-copy scripts distinguish a defined aggregate-copy case with explicit storage-buffer expectations from an uninitialized-local assignment case whose inspected script is execution-only, preventing a broader claim that both logical-copy cases compare copied struct contents at [`initialized_struct.amber`](../../../data/vulkan/amber/logical_copy/initialized_struct.amber#L32-L66) and [`undefined_memory.amber`](../../../data/vulkan/amber/logical_copy/undefined_memory.amber#L32-L60).

## Notes / Uncertainties

- This file registers three separate top-level GLSL children rather than one single group; the hierarchy section therefore preserves one parseable tree for each registered root under `glsl`.
- No source-backed claim is made that the values produced by division-by-zero, zero-length normalization, or the other risky expressions are deterministic; the inspected `crash_test` scripts verify completion/sentinel conditions instead.
- The inspected `undefined_memory` Amber script contains no `EXPECT` command, so this page does not characterize its result as a storage-buffer value comparison.
