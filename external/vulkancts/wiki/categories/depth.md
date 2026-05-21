# Depth Tests

## Overview

The Vulkan CTS `depth` category is a compact Amber-backed root for depth clamp, depth-range, and depth-bias behavior.
It is registered directly from the Vulkan test package as `dEQP-VK.depth` through
[`addRootChild("depth", ...)`](../../modules/vulkan/vktTestPackage.cpp#L1393-L1395), using the Amber factory declared in
[`vktAmberDepthTests.hpp`](../../modules/vulkan/amber/vktAmberDepthTests.hpp#L35-L35) and implemented in
[`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L163-L166).

The category has one registered source file documented at Level 3:
[`vktAmberDepthTests.md`](../testfiles/depth/vktAmberDepthTests.md). The C++ file registers eight direct Amber test
cases from a local `tests` vector, each mapped to a `.amber` script under
[`data/vulkan/amber/depth/`](../../data/vulkan/amber/depth/)
([`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L126-L156)).

## Registration Entry Point

- Root category registration: [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1393-L1395)
- Amber depth header included by the package: [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L108-L110)
- Category factory: [`createAmberDepthGroup()`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L163-L166)
- Per-case registration loop: [`createTests()`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L124-L157)

## Subgroup Structure

```text
depth
├── fs_clamp
├── out_of_range
├── ez_fs_clamp
├── bias_fs_clamp
├── bias_outside_range
├── bias_outside_range_fs_clamp
├── out_of_range_unrestricted
└── bias_outside_range_fs_clamp_unrestricted
```

The displayed names come from the `TestInfo::name` values in the C++ registration table
([`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L96-L101),
[`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L126-L149)). Mustpass coverage lists the
same eight paths under `dEQP-VK.depth`
([`depth.txt`](../../mustpass/main/vk-default/depth.txt#L1-L8)).

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L1-L169) | Registered source file | Defines the specialized Amber depth test case, the eight-test table, the registration loop, and `createAmberDepthGroup()`. |
| [`vktAmberDepthTests.hpp`](../../modules/vulkan/amber/vktAmberDepthTests.hpp#L1-L40) | Header | Declares the Amber depth factory used by the Vulkan test package. |
| [`vktAmberTestCase.cpp`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L193-L286) | Shared Amber support | Parses requirements, checks support, compiles shaders, and executes Amber recipes for this category. |
| [`data/vulkan/amber/depth/`](../../data/vulkan/amber/depth/) | Test data | Contains the eight `.amber` scripts named by the C++ registration table. |

## Cross-File Test Themes

- **Depth clamp zero-one support**: every registered case requires `DepthClampZeroOneFeatures.depthClampZeroOne` in the
  C++ table ([`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L127-L148)).
- **Fragment-depth clamping and early fragment tests**: `fs_clamp` and `ez_fs_clamp` both check clamped output, with
  `ez_fs_clamp` adding `layout(early_fragment_tests) in;` in the script
  ([`fs_clamp.amber`](../../data/vulkan/amber/depth/fs_clamp.amber#L50-L75),
  [`ez_fs_clamp.amber`](../../data/vulkan/amber/depth/ez_fs_clamp.amber#L29-L77)).
- **Depth bias outside viewport range**: the `bias_*` cases use Amber `BIAS` settings and compare expected depth and
  fragment-stage depth values where storage output is present
  ([`bias_fs_clamp.amber`](../../data/vulkan/amber/depth/bias_fs_clamp.amber#L50-L76),
  [`bias_outside_range.amber`](../../data/vulkan/amber/depth/bias_outside_range.amber#L49-L74),
  [`bias_outside_range_fs_clamp.amber`](../../data/vulkan/amber/depth/bias_outside_range_fs_clamp.amber#L49-L74)).
- **Unrestricted depth-range reruns**: two cases are explicitly rerun with `VK_EXT_depth_range_unrestricted` because the
  source comments identify them as producing different results under that extension
  ([`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L144-L148)).

## Recurring Parameter Dimensions

| Dimension | Observed values | Evidence |
|---|---|---|
| Test count | 8 direct children | [`tests` vector](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L126-L149) |
| Depth format | `D32_SFLOAT` in the eight depth Amber scripts | Representative script declarations in [`fs_clamp.amber`](../../data/vulkan/amber/depth/fs_clamp.amber#L43-L44), [`out_of_range.amber`](../../data/vulkan/amber/depth/out_of_range.amber#L37-L38), and [`bias_outside_range_fs_clamp_unrestricted.amber`](../../data/vulkan/amber/depth/bias_outside_range_fs_clamp_unrestricted.amber#L43-L44) |
| Framebuffer size | `60 x 60` | Representative declarations in [`fs_clamp.amber`](../../data/vulkan/amber/depth/fs_clamp.amber#L57-L63) and [`out_of_range.amber`](../../data/vulkan/amber/depth/out_of_range.amber#L51-L57) |
| Viewport depth range | Mostly `0.1..0.9`; `bias_outside_range` uses `0.1..0.5` | [`fs_clamp.amber`](../../data/vulkan/amber/depth/fs_clamp.amber#L57-L57), [`bias_outside_range.amber`](../../data/vulkan/amber/depth/bias_outside_range.amber#L56-L56) |
| Required features/extensions | `DepthClampZeroOneFeatures.depthClampZeroOne`, conditionally `Features.depthClamp`, `Features.fragmentStoresAndAtomics`, and `VK_EXT_depth_range_unrestricted` | [`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L127-L149) |

## Support Requirements

The wrapper records feature and extension requirements from the `TestInfo` table and adds
`VK_EXT_depth_range_unrestricted` only for entries marked `unrestricted`
([`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L103-L121)). Non-unrestricted cases use a
custom device path intended to keep `VK_EXT_depth_range_unrestricted` disabled; that path's capability setup also requests
either `VK_KHR_depth_clamp_zero_one` or `VK_EXT_depth_clamp_zero_one` plus `depthClampZeroOne`,
`fragmentStoresAndAtomics`, and `depthClamp` features
([`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L79-L88),
[`vktAmberDepthTests.cpp`](../../modules/vulkan/amber/vktAmberDepthTests.cpp#L113-L114)).

The shared Amber support code checks registered requirements before execution and throws `NotSupportedError` for missing
requirements ([`AmberTestCase::checkSupport()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286)).

## Verification Methods

The C++ file delegates test execution to the shared Amber runner. The runner parses the Amber source from the CTS
archive ([`AmberTestCase::parse()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432)), compiles the shaders
listed by the recipe ([`AmberTestCase::initPrograms()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L435-L543)),
and executes the recipe through Amber's Vulkan engine
([`AmberTestInstance::iterate()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615)).

The script-level pass/fail criteria are the Amber `EXPECT` commands. In this category they compare the rendered color
buffer to green and compare depth-related values such as `depth0` and `fs_depth` against exact or tolerance-based
expected floats
([`fs_clamp.amber`](../../data/vulkan/amber/depth/fs_clamp.amber#L73-L75),
[`out_of_range.amber`](../../data/vulkan/amber/depth/out_of_range.amber#L65-L66),
[`bias_outside_range_fs_clamp_unrestricted.amber`](../../data/vulkan/amber/depth/bias_outside_range_fs_clamp_unrestricted.amber#L73-L75)).

## Level-3 Pages

- [`vktAmberDepthTests.md`](../testfiles/depth/vktAmberDepthTests.md) — Amber depth root implementation and the eight
  registered depth test cases.

## Scope Notes

- No dedicated `external/vulkancts/modules/vulkan/depth/` source directory was found during source discovery; the
  category is implemented through the shared Amber module and registered directly as a root category.
- The inspected API test plan section describes the test plan as a high-level Vulkan API testing outline and does not
  provide category-specific text for this Amber `depth` root
  ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L8-L13)).
