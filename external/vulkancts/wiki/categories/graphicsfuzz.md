# GraphicsFuzz Tests

## Overview

The Vulkan CTS `graphicsfuzz` category is an Amber-backed root for a large GraphicsFuzz shader corpus. It is registered
directly from the Vulkan test package as `dEQP-VK.graphicsfuzz` through
[`addRootChild("graphicsfuzz", ...)`](../../modules/vulkan/vktTestPackage.cpp#L1380-L1382), using the Amber GraphicsFuzz
factory declared in [`vktAmberGraphicsFuzzTests.hpp`](../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.hpp#L31-L37) and
implemented in [`vktAmberGraphicsFuzzTests.cpp`](../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L37-L49).

The category has one registered source file documented at Level 3:
[`vktAmberGraphicsFuzzTests.md`](../testfiles/graphicsfuzz/vktAmberGraphicsFuzzTests.md). The C++ wrapper populates the root
from [`data/vulkan/amber/graphicsfuzz/index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757), whose 757 entries
map `.amber` scripts to registered test names and descriptions, with optional per-case requirements parsed by the shared
Amber index reader ([`vktAmberTestCaseUtil.cpp`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L189)).

## Registration Entry Point

- Root category registration: [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1380-L1382)
- Amber GraphicsFuzz header included by the package: [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L106-L108)
- Category factory: [`createGraphicsFuzzTests()`](../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L46-L49)
- Index-file population call: [`createAmberTests()`](../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L37-L42)
- Shared parser loop: [`createAmberTestsFromIndexFile()`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L175-L189)

## Subgroup Structure

```text
graphicsfuzz
├── 757 direct Amber test cases from index.txt
└── no nested registered subgroups observed in the C++ wrapper
```

The user-facing Level-3 hierarchy fully expands the 757 direct children and is verified against mustpass coverage in
[`vktAmberGraphicsFuzzTests.md`](../testfiles/graphicsfuzz/vktAmberGraphicsFuzzTests.md#registration-hierarchy). Mustpass
lists 757 paths under `dEQP-VK.graphicsfuzz` ([`graphicsfuzz.txt`](../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757)).

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktAmberGraphicsFuzzTests.cpp`](../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L1-L52) | Registered source file | Creates the `graphicsfuzz` group and delegates case creation to `index.txt`. |
| [`vktAmberGraphicsFuzzTests.hpp`](../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.hpp#L1-L41) | Header | Declares the Amber GraphicsFuzz factory used by the Vulkan test package. |
| [`vktAmberTestCaseUtil.cpp`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L100-L189) | Shared Amber index parser | Reads filename, registered name, description, and optional requirements from `index.txt`, then adds test cases. |
| [`vktAmberTestCase.cpp`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L193-L286) | Shared Amber support | Checks registered requirements before execution. |
| [`vktAmberTestCase.cpp`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L615) | Shared Amber execution | Parses scripts, prepares shader binaries, executes Amber recipes, and returns pass/fail. |
| [`data/vulkan/amber/graphicsfuzz/`](../../data/vulkan/amber/graphicsfuzz/) | Test data | Contains `index.txt` and the `.amber` scripts referenced by the index. |
| [`graphicsfuzz.txt`](../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757) | Mustpass coverage | Lists the 757 registered `dEQP-VK.graphicsfuzz.*` paths. |

## Cross-File Test Themes

- **Index-driven Amber corpus**: the C++ file has no inline table of case names; the shared parser reads the data-side index
  and adds one `AmberTestCase` per entry ([`vktAmberGraphicsFuzzTests.cpp`](../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L37-L42),
  [`vktAmberTestCaseUtil.cpp`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L189)).
- **GraphicsFuzz shader reproducers**: representative scripts identify themselves as tests for bugs found by GraphicsFuzz and
  describe control-flow or reference-vs-variant behavior in comments
  ([`control-flow-switch.amber`](../../data/vulkan/amber/graphicsfuzz/control-flow-switch.amber#L17-L23),
  [`spv-double-branch-to-same-block.amber`](../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L19-L24)).
- **Coverage-oriented `cov-*` family**: 580 parsed index entries have names beginning with `cov-`, with descriptions citing
  compiler or optimizer paths such as LLVM, NIR, APFloat, instruction-combine, DAG, and value-tracking
  ([`index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L21-L40),
  [`index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L350-L390)).
- **Reference-vs-variant comparisons in sampled `spv-*`/`stable-*` scripts**: representative scripts render reference and
  variant pipelines and compare framebuffers with `EQ_HISTOGRAM_EMD_BUFFER`
  ([`spv-double-branch-to-same-block.amber`](../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L23-L30),
  [`spv-double-branch-to-same-block.amber`](../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L1231-L1231),
  [`stable-mergesort-reversed-for-loop.amber`](../../data/vulkan/amber/graphicsfuzz/stable-mergesort-reversed-for-loop.amber#L1555-L1555)).

## Recurring Parameter Dimensions

| Dimension | Observed values | Evidence |
|---|---|---|
| Registered children | 757 direct tests under `graphicsfuzz` | [`index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757), [`graphicsfuzz.txt`](../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757) |
| Case metadata | Filename, registered name, description, and optional requirement strings | [`vktAmberTestCaseUtil.cpp`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L126), [`vktAmberTestCaseUtil.cpp`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L149-L163) |
| Optional requirements observed | `VK_KHR_shader_terminate_invocation` on 72 entries; `VK_KHR_shader_float_controls` and `FloatControlsProperties.shaderSignedZeroInfNanPreserveFloat32` on 8 entries | Examples in [`index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L2-L4), [`index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L30-L40), [`index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L748-L754) |
| Common script verification styles in inspected samples | Direct red framebuffer expectations and reference-vs-variant histogram EMD comparisons | [`access-new-vector-inside-if-condition.amber`](../../data/vulkan/amber/graphicsfuzz/access-new-vector-inside-if-condition.amber#L110-L110), [`stable-mergesort-reversed-for-loop.amber`](../../data/vulkan/amber/graphicsfuzz/stable-mergesort-reversed-for-loop.amber#L1555-L1555) |

## Support / Feature Requirements

There is no category-wide support check in [`vktAmberGraphicsFuzzTests.cpp`](../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L37-L49). Support requirements are per-case strings read from the index and attached to the `AmberTestCase`
([`vktAmberTestCaseUtil.cpp`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L155-L163)). The shared Amber support code
then checks required device/instance extensions, features, and properties before execution
([`AmberTestCase::checkSupport()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286)).

## Verification Methods

The C++ file delegates test execution to the shared Amber runner. The runner parses the Amber source from the CTS archive
([`AmberTestCase::parse()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432)), compiles or maps shaders as needed,
executes the recipe through Amber's Vulkan engine, and returns pass/fail from the Amber execution result
([`AmberTestInstance::iterate()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615)).

At the script level, inspected pass/fail criteria use Amber `EXPECT` commands. Representative scripts directly compare a
framebuffer to red ([`access-new-vector-inside-if-condition.amber`](../../data/vulkan/amber/graphicsfuzz/access-new-vector-inside-if-condition.amber#L110-L110),
[`control-flow-switch.amber`](../../data/vulkan/amber/graphicsfuzz/control-flow-switch.amber#L242-L242)), while sampled
comparison scripts compare reference and variant framebuffers with `EQ_HISTOGRAM_EMD_BUFFER`
([`spv-double-branch-to-same-block.amber`](../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L1231-L1231)).

## Level-3 Pages

- [`vktAmberGraphicsFuzzTests.md`](../testfiles/graphicsfuzz/vktAmberGraphicsFuzzTests.md) — Amber GraphicsFuzz root
  wrapper and the 757 registered index-driven Amber test cases.

## Scope Notes

- No dedicated `external/vulkancts/modules/vulkan/graphicsfuzz/` source directory was found during source discovery; the
  category is implemented through the shared Amber module and registered directly as a root category.
- Existing wiki pages were not used as factual evidence for this category; claims above are derived from inspected source,
  Amber data, and mustpass coverage.
