# vktFragmentOperationsEarlyFragmentTests.cpp

## Overview

[`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1) implements the displayed `early_fragment` subgroup under [`fragment_operations`](../../categories/fragment_operations.md). The file registers depth- and stencil-oriented early-fragment coverage, discard variants, sample-mask variants, and sample-count variants, including non-VulkanSC early-and-late fragment execution mode cases and selected `maintenance5` combinations.

## Role

Registration and implementation file. It owns the user-visible `early_fragment` subgroup and contains the corresponding shader generation, support checks, render setup, query logic, and image verification.

## Source Code

- Primary source: [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1)
- Header: [`vktFragmentOperationsEarlyFragmentTests.hpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.hpp)

## Registration Hierarchy

```text
fragment_operations.early_fragment
├── no_early_fragment_tests_depth
├── no_early_fragment_tests_stencil
├── early_fragment_tests_depth
├── early_fragment_tests_stencil
├── no_early_fragment_tests_depth_no_attachment
├── no_early_fragment_tests_stencil_no_attachment
├── early_fragment_tests_depth_no_attachment
├── early_fragment_tests_stencil_no_attachment
├── early_and_late_fragment_tests_depth (non-VulkanSC only)
├── early_and_late_fragment_tests_stencil (non-VulkanSC only)
├── early_and_late_fragment_tests_depth_no_attachment (non-VulkanSC only)
├── early_and_late_fragment_tests_stencil_no_attachment (non-VulkanSC only)
├── discard_* cases
├── samplemask_* cases
└── sample_count_* cases
```

Source: [`createEarlyFragmentTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2755-L2895).

## Test Families

### Base early-fragment depth and stencil cases

The first registration block adds eight baseline names in [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2759-L2797):

- `no_early_fragment_tests_depth`
- `no_early_fragment_tests_stencil`
- `early_fragment_tests_depth`
- `early_fragment_tests_stencil`
- `no_early_fragment_tests_depth_no_attachment`
- `no_early_fragment_tests_stencil_no_attachment`
- `early_fragment_tests_depth_no_attachment`
- `early_fragment_tests_stencil_no_attachment`

For non-VulkanSC builds, the same block also adds four `early_and_late_fragment_tests_*` variants at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2780-L2797). The SPIR-V path for these cases explicitly emits `OpExecutionMode %4 EarlyAndLateFragmentTestsAMD` at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L281-L284).

### Discard cases

The second registration block adds discard-focused cases at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2800-L2821). The visible comment states the family intent as checking that discard does not affect depth test writes. The registered names cover depth and stencil targets, with additional early-and-late variants for non-VulkanSC builds.

### Sample-mask cases

The third block registers `samplemask_*` names over sample counts 2, 4, 8, and 16 at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2823-L2849). The fragment shader for this family writes `gl_SampleMask[0] = 0x0` after `atomicAdd()` at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1840-L1842). The visible comment states this family checks that writing to `gl_SampleMask` does not affect depth test writes.

### Sample-count cases

The fourth block registers `sample_count_*` names over sample counts 2, 4, 8, and 16 at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2852-L2890). The generated combinations vary:

- early-fragment versus early-and-late mode
- optional `maintenance5`
- optional alpha-to-coverage

These switches are carried in [`SampleCountTestParams`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1941-L1946) and then toggled during registration at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2860-L2889).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Test target | Depth and stencil flags in [`Flags`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L199-L206) and base case tables at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2766-L2788) |
| Early-fragment mode | No early tests, early tests, and non-VulkanSC early-and-late tests from the registration blocks at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2766-L2797) |
| Test attachment usage | Default attachment path versus `_no_attachment` variants at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2772-L2777) |
| Shader-side behavior | Base atomic counter increment, discard variants, sample-mask write variants, and sample-count logic seen in [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L263-L266), [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1061-L1063), and [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1840-L1842) |
| Sample count | 2, 4, 8, 16 from the registration arrays at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2839-L2848) and [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2854-L2856) |
| Optional sample-count modifiers | `earlyAndLate`, `alphaToCoverage`, `useMaintenance5` fields in [`SampleCountTestParams`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1941-L1946) |

## Support Requirements

[`EarlyFragmentTest::checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L629-L638) requires `fragmentStoresAndAtomics` for the base family, and additionally requires `VK_AMD_shader_early_and_late_fragment_tests` plus the corresponding feature bit when the early-and-late mode flag is used. [`EarlyFragmentSampleMaskTest::checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1911-L1916) adds a requirement for `VK_KHR_depth_stencil_resolve`. [`EarlyFragmentSampleCountTest::checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2713-L2749) inherits the base checks, re-requires the AMD early-and-late extension when needed, and requires `VK_KHR_maintenance5` when `useMaintenance5` is true.

## Verification Methods

The base and related image-producing families compare rendered output against a reference image with [`tcu::floatThresholdCompare()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L589-L591), [`tcu::floatThresholdCompare()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L900-L902), and [`tcu::floatThresholdCompare()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1686-L1688). The fragment shaders increment an SSBO counter with `atomicAdd(sb_out.result, 1u)` in the base path at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L263-L266) and in the discard-related shader path at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1061-L1063).

For the sample-count family, the code logs two query-derived sample counts and applies acceptance rules over expected ranges in [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2427-L2468). The visible comment for this family states that half the samples are killed at different pipeline points and the sample counting is then verified at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2852-L2853).

## Notes / Uncertainties

- This file is implementation-heavy and programmatically generates many direct children, so the parseable hierarchy above intentionally stops at one level while the family sections describe the generated name sets.
- The inspected evidence confirms registration, support checks, SPIR-V execution modes, and verification helpers, but this page avoids inferring semantics beyond what the file comments and code explicitly state.
