# vktAmberDepthTests.cpp

## Overview

[`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L1-L169) is the registered source file for the
Vulkan CTS `depth` category. The category is an Amber-backed root registered from the Vulkan test package as
`dEQP-VK.depth` via [`addRootChild("depth", ...)`](../../../modules/vulkan/vktTestPackage.cpp#L1393-L1395), and the
Amber depth factory returns a test group using the name supplied by that root registration
([`createAmberDepthGroup()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L163-L166)).

The file registers eight Amber script test cases. Each test uses a `D32_SFLOAT` depth attachment, a `60 x 60`
framebuffer, depth testing and depth writes, and Amber `EXPECT` commands to define pass/fail criteria in the script
files under [`data/vulkan/amber/depth/`](../../../data/vulkan/amber/depth/).

## Role

Registration and implementation wrapper for Amber depth-range and depth-clamp tests. The C++ file defines a specialized
[`DepthTestCase`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L45-L94) that extends the shared Amber test case
infrastructure, maps `TestInfo` entries to `.amber` files, records required features/extensions, and creates the
registered group.

## Source Code

- Primary source: [`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L1-L169)
- Header: [`vktAmberDepthTests.hpp`](../../../modules/vulkan/amber/vktAmberDepthTests.hpp#L1-L40)
- Root package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L108-L110),
  [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1393-L1395)
- Shared Amber execution support: [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L193-L286),
  [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432),
  [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615)
- Amber data files: [`depth/`](../../../data/vulkan/amber/depth/)

## Registration Hierarchy

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

The direct children are the eight entries in the `tests` vector
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L126-L149)). They are registered by
iterating that vector and adding one child per `.amber` filename
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L151-L156)).

## Test Families

### fs_clamp — Fragment-depth clamping

`fs_clamp` uses `depthClampZeroOne`, `depthClamp`, and `fragmentStoresAndAtomics` requirements in the C++ test table
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L127-L129)). Its Amber script enables
`DEPTH TEST`, `WRITE`, and `CLAMP`, sets viewport depth range `0.1..0.9`, writes the fragment depth observed through
`gl_FragCoord.z` into a storage buffer, and expects the depth attachment to contain `0.9` while the fragment-stage value
is `1.7` ([`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L15-L75)).

### out_of_range — Out-of-range fragment depth without unrestricted range

`out_of_range` requires `DepthClampZeroOneFeatures.depthClampZeroOne` in the C++ table
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L130-L130)). The Amber fragment shader
writes `gl_FragDepth = 2.0`, uses depth compare `equal`, and expects the rendered color to pass with depth value `1.0`
after a clear to `1.0` ([`out_of_range.amber`](../../../data/vulkan/amber/depth/out_of_range.amber#L15-L66)).

### ez_fs_clamp — Early fragment test variant of fragment-depth clamping

`ez_fs_clamp` has the same C++ requirements as `fs_clamp`
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L131-L133)). The Amber script differs by
using `layout(early_fragment_tests) in;` in the fragment shader while keeping depth clamp enabled and the same expected
`depth0 = 0.9` and `fs_depth = 1.7` checks
([`ez_fs_clamp.amber`](../../../data/vulkan/amber/depth/ez_fs_clamp.amber#L15-L77)).

### bias_fs_clamp — Depth bias plus clamping

`bias_fs_clamp` also requires `depthClampZeroOne`, `depthClamp`, and `fragmentStoresAndAtomics`
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L134-L136)). Its Amber pipeline enables
`BIAS constant 1.0 clamp 0.0 slope 0.0` and `CLAMP on`, then expects `depth0 = 0.9` and `fs_depth = 1.7`
([`bias_fs_clamp.amber`](../../../data/vulkan/amber/depth/bias_fs_clamp.amber#L15-L76)).

### bias_outside_range — Depth-bias value outside the viewport range

`bias_outside_range` requires `depthClampZeroOne` and `fragmentStoresAndAtomics`
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L137-L139)). Its Amber pipeline uses
viewport depth range `0.1..0.5` and a large constant bias of `2097152.0`, then expects both the depth attachment and the
fragment-stage recorded value to be `0.625`
([`bias_outside_range.amber`](../../../data/vulkan/amber/depth/bias_outside_range.amber#L15-L74)).

### bias_outside_range_fs_clamp — Larger depth-bias value outside range

`bias_outside_range_fs_clamp` requires `depthClampZeroOne` and `fragmentStoresAndAtomics`
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L140-L142)). Its Amber pipeline uses
constant bias `16777216.0`, keeps viewport depth range `0.1..0.9`, and expects `depth0 = 1.0` while recording
`fs_depth = 1.9` ([`bias_outside_range_fs_clamp.amber`](../../../data/vulkan/amber/depth/bias_outside_range_fs_clamp.amber#L15-L74)).

### out_of_range_unrestricted — Out-of-range fragment depth with unrestricted range

`out_of_range_unrestricted` is one of the reruns called out in the source comment for cases with different results when
`VK_EXT_depth_range_unrestricted` is enabled
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L144-L146)). The C++ wrapper adds the
extension requirement for `unrestricted` entries
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L118-L120)). Its Amber script also
declares `DEVICE_EXTENSION VK_EXT_depth_range_unrestricted`, writes `gl_FragDepth = 2.0`, uses compare op `not_equal`,
and expects `depth0 = 2.0`
([`out_of_range_unrestricted.amber`](../../../data/vulkan/amber/depth/out_of_range_unrestricted.amber#L15-L67)).

### bias_outside_range_fs_clamp_unrestricted — Depth-bias rerun with unrestricted range

`bias_outside_range_fs_clamp_unrestricted` is the second unrestricted rerun
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L146-L148)). The Amber script declares
`VK_EXT_depth_range_unrestricted`, applies constant bias `16777216.0`, and expects both the depth attachment and the
fragment-stage recorded value to be `1.9`
([`bias_outside_range_fs_clamp_unrestricted.amber`](../../../data/vulkan/amber/depth/bias_outside_range_fs_clamp_unrestricted.amber#L15-L75)).

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|---|---|---|
| Registered test names | `fs_clamp`, `out_of_range`, `ez_fs_clamp`, `bias_fs_clamp`, `bias_outside_range`, `bias_outside_range_fs_clamp`, `out_of_range_unrestricted`, `bias_outside_range_fs_clamp_unrestricted` | [`tests` vector](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L126-L149) |
| Unrestricted-range mode | `false` for six cases, `true` for two reruns | [`TestInfo::unrestricted`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L96-L101), [`tests` vector](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L126-L149) |
| Depth format | `D32_SFLOAT` in the inspected depth Amber scripts | Example buffers in [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L43-L44), [`out_of_range.amber`](../../../data/vulkan/amber/depth/out_of_range.amber#L37-L38), and [`bias_outside_range_fs_clamp_unrestricted.amber`](../../../data/vulkan/amber/depth/bias_outside_range_fs_clamp_unrestricted.amber#L43-L44) |
| Framebuffer size | `60 x 60` | Example pipeline declarations in [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L57-L63) and [`out_of_range.amber`](../../../data/vulkan/amber/depth/out_of_range.amber#L51-L57) |
| Viewport depth ranges | `0.1..0.9` in most scripts; `0.1..0.5` in `bias_outside_range` | [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L57-L57), [`bias_outside_range.amber`](../../../data/vulkan/amber/depth/bias_outside_range.amber#L56-L56) |
| Depth pipeline toggles | `TEST on`, `WRITE on`, optional `CLAMP on`, optional `BIAS` | [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L50-L55), [`bias_fs_clamp.amber`](../../../data/vulkan/amber/depth/bias_fs_clamp.amber#L50-L56), [`bias_outside_range.amber`](../../../data/vulkan/amber/depth/bias_outside_range.amber#L49-L54) |
| Expected outputs | Color equality, depth equality or tolerance checks, and storage-buffer depth checks where present | [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L73-L75), [`out_of_range.amber`](../../../data/vulkan/amber/depth/out_of_range.amber#L65-L66), [`bias_outside_range.amber`](../../../data/vulkan/amber/depth/bias_outside_range.amber#L72-L74) |

## Support / Feature Requirements

The C++ wrapper adds each `base_required_features` entry with
[`testCase->addRequirement(req)`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L115-L116), and adds
`VK_EXT_depth_range_unrestricted` for entries whose `unrestricted` flag is `true`
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L118-L120)). The wrapper also creates a
custom device for non-unrestricted cases so `VK_EXT_depth_range_unrestricted` is not enabled
([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L79-L88),
[`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L113-L114)).

| Requirement | Cases | Evidence |
|---|---|---|
| `DepthClampZeroOneFeatures.depthClampZeroOne` | All eight cases | Every `TestInfo` entry includes it in [`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L127-L148) |
| `Features.depthClamp` | `fs_clamp`, `ez_fs_clamp`, `bias_fs_clamp` | [`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L127-L136) |
| `Features.fragmentStoresAndAtomics` | All cases that record `gl_FragCoord.z` to `fs_depth`; not the two `out_of_range` cases | [`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L127-L148), storage-buffer writes in [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L31-L40) |
| `VK_EXT_depth_range_unrestricted` | `out_of_range_unrestricted`, `bias_outside_range_fs_clamp_unrestricted` | [`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L144-L148), [`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L118-L120) |
| `VK_KHR_depth_clamp_zero_one` or `VK_EXT_depth_clamp_zero_one` on the custom device | Non-unrestricted cases using the custom-device path | [`initDeviceCapabilities()`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L79-L88) |

The shared Amber support path checks registered requirements against device/instance extensions and features before
execution ([`AmberTestCase::checkSupport()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286)).

## Verification Methods

Verification is delegated to Amber script execution. During initialization, the shared Amber test case parses the script
from the CTS archive ([`AmberTestCase::parse()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432)); during
execution, the test builds an Amber Vulkan engine config, checks Amber-declared requirements, executes the recipe, and
returns pass or fail from `ExecuteWithShaderData()`
([`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615)).

Inside the depth scripts, pass/fail criteria are visible as `EXPECT` statements. The inspected cases compare the color
buffer to green (`EQ_RGBA 0 255 0 255`) and compare either the depth attachment alone or both the depth attachment and
`fs_depth` storage value to specific expected floats, sometimes with `TOLERANCE 1.0e-6`
([`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L73-L75),
[`out_of_range_unrestricted.amber`](../../../data/vulkan/amber/depth/out_of_range_unrestricted.amber#L66-L67),
[`bias_outside_range_fs_clamp_unrestricted.amber`](../../../data/vulkan/amber/depth/bias_outside_range_fs_clamp_unrestricted.amber#L73-L75)).

## Test Principles

- **Compare restricted and unrestricted depth-range behavior**: the source explicitly reruns selected cases when
  `VK_EXT_depth_range_unrestricted` is enabled because those cases have different expected results
  ([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L144-L148)).
- **Separate pipeline depth value from fragment-stage observed value**: scripts with `fragmentStoresAndAtomics` write
  `gl_FragCoord.z` to `fs_depth`, allowing Amber to check both attachment results and fragment-visible depth where the
  script defines both expectations ([`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L31-L40),
  [`fs_clamp.amber`](../../../data/vulkan/amber/depth/fs_clamp.amber#L73-L75)).
- **Use custom device capability control for non-unrestricted cases**: non-unrestricted cases use a custom device path
  so `VK_EXT_depth_range_unrestricted` is not enabled while still requiring depth-clamp-zero-one support
  ([`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L79-L88),
  [`vktAmberDepthTests.cpp`](../../../modules/vulkan/amber/vktAmberDepthTests.cpp#L113-L114)).

## Notes / Uncertainties

- No separate `external/vulkancts/modules/vulkan/depth/` directory exists in the inspected tree; this category is rooted
  from [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1393-L1395) and implemented by the Amber source
  file documented here.
