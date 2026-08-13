## Overview

**Core question:** Do Vulkan implementations preserve the required relationship between early fragment tests, fragment-shader side effects, depth/stencil updates, sample coverage, and occlusion-query sample counts?

- This page covers the implementation and registration in [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L199-L348), registered as `fragment_operations.early_fragment`.
- The test family compares depth and stencil behavior with and without `layout(early_fragment_tests) in;`, exercises shader `discard` and `gl_SampleMask` writes, and checks sample counting at 2, 4, 8, and 16 samples.
- Non-VulkanSC builds add `EarlyAndLateFragmentTestsAMD` cases and selected `VK_KHR_maintenance5` cases. The direct registrations and their build notes are listed below.
- The page explains the generated shader side effects, host/device flow, support gates, image checks, and the source's explicit sample-count acceptance rules.

## Background Knowledge

For the shared concept of per-fragment testing and sample coverage, see [Background Knowledge](../../categories/fragment_operations.md#background-knowledge) of the `fragment_operations` page.

- **Early fragment tests:** A fragment shader that declares `layout(early_fragment_tests) in;` requests early depth and stencil testing. This page uses the declaration to compare when depth/stencil tests occur relative to shader-side behavior.
- **Shader side effects:** The base, discard, and sample-mask fragment shaders increment a coherent storage-buffer counter with `atomicAdd()`. This gives the host an observable count of shader activity alongside the color and depth/stencil images; the sample-count shaders instead expose their ordering through multisample coverage and occlusion queries.

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
├── discard_no_early_fragment_tests_depth
├── discard_no_early_fragment_tests_stencil
├── discard_early_fragment_tests_depth
├── discard_early_fragment_tests_stencil
├── discard_early_and_late_fragment_tests_depth (non-VulkanSC only)
├── discard_early_and_late_fragment_tests_stencil (non-VulkanSC only)
├── samplemask_no_early_fragment_tests_depth_samples_2
├── samplemask_no_early_fragment_tests_depth_samples_4
├── samplemask_no_early_fragment_tests_depth_samples_8
├── samplemask_no_early_fragment_tests_depth_samples_16
├── samplemask_early_fragment_tests_depth_samples_2
├── samplemask_early_fragment_tests_depth_samples_4
├── samplemask_early_fragment_tests_depth_samples_8
├── samplemask_early_fragment_tests_depth_samples_16
├── samplemask_early_and_late_fragment_tests_depth_samples_2 (non-VulkanSC only)
├── samplemask_early_and_late_fragment_tests_depth_replacing_mode_samples_2 (non-VulkanSC only)
├── samplemask_early_and_late_fragment_tests_depth_samples_4 (non-VulkanSC only)
├── samplemask_early_and_late_fragment_tests_depth_replacing_mode_samples_4 (non-VulkanSC only)
├── samplemask_early_and_late_fragment_tests_depth_samples_8 (non-VulkanSC only)
├── samplemask_early_and_late_fragment_tests_depth_replacing_mode_samples_8 (non-VulkanSC only)
├── samplemask_early_and_late_fragment_tests_depth_samples_16 (non-VulkanSC only)
├── samplemask_early_and_late_fragment_tests_depth_replacing_mode_samples_16 (non-VulkanSC only)
├── sample_count_early_fragment_tests_depth_samples_2
├── sample_count_early_fragment_tests_depth_samples_4
├── sample_count_early_fragment_tests_depth_samples_8
├── sample_count_early_fragment_tests_depth_samples_16
├── sample_count_early_fragment_tests_depth_samples_2_maintenance5 (non-VulkanSC only)
├── sample_count_early_fragment_tests_depth_alpha_to_coverage_samples_2_maintenance5 (non-VulkanSC only)
├── sample_count_early_fragment_tests_depth_samples_4_maintenance5 (non-VulkanSC only)
├── sample_count_early_fragment_tests_depth_alpha_to_coverage_samples_4_maintenance5 (non-VulkanSC only)
├── sample_count_early_fragment_tests_depth_samples_8_maintenance5 (non-VulkanSC only)
├── sample_count_early_fragment_tests_depth_alpha_to_coverage_samples_8_maintenance5 (non-VulkanSC only)
├── sample_count_early_fragment_tests_depth_samples_16_maintenance5 (non-VulkanSC only)
├── sample_count_early_fragment_tests_depth_alpha_to_coverage_samples_16_maintenance5 (non-VulkanSC only)
├── sample_count_early_and_late_fragment_tests_depth_samples_2 (non-VulkanSC only)
├── sample_count_early_and_late_fragment_tests_depth_samples_2_maintenance5 (non-VulkanSC only)
├── sample_count_early_and_late_fragment_tests_depth_samples_4 (non-VulkanSC only)
├── sample_count_early_and_late_fragment_tests_depth_samples_4_maintenance5 (non-VulkanSC only)
├── sample_count_early_and_late_fragment_tests_depth_samples_8 (non-VulkanSC only)
├── sample_count_early_and_late_fragment_tests_depth_samples_8_maintenance5 (non-VulkanSC only)
├── sample_count_early_and_late_fragment_tests_depth_samples_16 (non-VulkanSC only)
└── sample_count_early_and_late_fragment_tests_depth_samples_16_maintenance5 (non-VulkanSC only)
```

[`createEarlyFragmentTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2755-L2895) registers these direct children. The `samples_2`, `samples_4`, `samples_8`, and `samples_16` suffixes are generated from the sample-count array in the same function.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | Base early-fragment, `discard`, `samplemask`, `sample_count` | Selects which ordering property and observable result the case checks | [`createEarlyFragmentTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2755-L2895) |
| Attachment mode | `depth`, `stencil`; base family also has `_no_attachment` | Chooses the tested depth or stencil state, and whether the base render pass binds that test attachment | [`Flags`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L199-L206), [`EarlyFragmentTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L340-L405) |
| Fragment-test mode | `no_early_fragment_tests`, `early_fragment_tests`, and non-VulkanSC `early_and_late_fragment_tests` | Changes when depth/stencil and relevant fragment operations are performed | [`EarlyFragmentTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L227-L318) |
| Sample count | `samples_2`, `samples_4`, `samples_8`, `samples_16` | Selects the multisample image configuration and expected query scale | [`createEarlyFragmentTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2839-L2856) |
| Shader operation | Atomic increment; `discard`; `gl_SampleMask[0] = 0x0`; zero alpha for alpha-to-coverage | Provides the side effect or coverage change whose ordering is observed | [`EarlyFragmentDiscardTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1045-L1067), [`EarlyFragmentSampleMaskTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1824-L1847), [`EarlyFragmentSampleCountTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2572-L2666) |
| Sample-count modifiers | `earlyAndLate`, `alphaToCoverage`, `useMaintenance5` | Selects the AMD execution mode, alpha-to-coverage shader, or maintenance5-specific acceptance logic | [`SampleCountTestParams`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1941-L1947), [`createEarlyFragmentTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2858-L2891) |

## Behavior Parameters

The primary behavioral axis is the registered test family. Its four groups use related render setups but observe different consequences of fragment-operation ordering.

### Base early-fragment cases — depth/stencil ordering and attachment use

The base cases select depth or stencil testing, enable or omit `layout(early_fragment_tests) in;`, and optionally omit the test attachment. The fragment shader increments `sb_out.result` and writes yellow. With an attachment and early tests, the source expects only the fragments passing the configured test to contribute to the counter and expects corresponding depth/stencil updates. Without early tests, shader execution precedes the depth/stencil test; `_no_attachment` cases isolate the color and counter path.

The non-VulkanSC `early_and_late_fragment_tests_*` cases use inline SPIR-V with `OpExecutionMode %4 EarlyAndLateFragmentTestsAMD`. The source does not generate a GLSL equivalent for that mode.

### Discard cases — depth/stencil writes around `discard`

The discard shader increments the coherent counter, writes `gl_FragDepth = 0.75f`, writes yellow, and executes `discard`. The registration comment defines the family purpose as checking that discard does not affect depth-test writes. With early tests, the depth/stencil attachment can be updated before the shader discards the fragment. With early tests disabled, the source expects the cleared depth/stencil values after the shader discards.

The non-VulkanSC early-and-late discard registrations use `FLAG_DONT_USE_EARLY_FRAGMENT_TESTS | FLAG_EARLY_AND_LATE_FRAGMENT_TESTS` in the registration table, and their inline SPIR-V carries the AMD execution mode.

### Sample-mask cases — clearing `gl_SampleMask`

The sample-mask shader increments the coherent counter, writes `gl_SampleMask[0] = 0x0`, writes yellow, and discards. The registration comment says the family checks that writing `gl_SampleMask` does not affect depth-test writes. Cases cover 2, 4, 8, and 16 samples. The source compares color output with a black reference, checks depth/stencil values, and checks the counter against the expected number of processed fragments.

The two early-and-late forms differ in whether the registration also sets `FLAG_DONT_USE_EARLY_FRAGMENT_TESTS`; the `replacing_mode` suffix is the source's name for that variant. These cases are non-VulkanSC only.

### Sample-count cases — occlusion-query ordering

Each sample-count case creates multisampled color and depth images, then runs two pipelines under precise occlusion queries: one without early fragment tests and one with early fragment tests. The no-early shader writes a mask that removes half the samples. The early shader clears `gl_SampleMask[0]`, or emits zero alpha when the alpha-to-coverage modifier is enabled. The source comment states that half the samples are killed at different pipeline points and that the resulting sample count is verified.

The expected reference is `(32 * 32 / 4) * sampleCount` with a 5% tolerance. Both query results pass when they fall in that range. If the early result is zero, the source returns a quality warning for the non-maintenance5 case, while a maintenance5 case checks `earlyFragmentMultisampleCoverageAfterSampleCounting`: `VK_TRUE` makes that result fail and `VK_FALSE` makes it pass. If the early result is twice the range, the source treats that as sample-mask testing after sample counting; the maintenance5 variant checks `earlyFragmentSampleMaskTestBeforeSampleCounting` in the analogous way. Other values fail and cause both rendered images to be logged.

## Shader Analysis

The source generates GLSL for the base, discard, sample-mask, and ordinary sample-count paths. It also embeds SPIR-V for `EarlyAndLateFragmentTestsAMD`. The important shader operations are shown in the Behavior Parameters section: the atomic increment, `discard`, `gl_SampleMask[0]` writes, and alpha-to-coverage input. No reconstructed shader or hand-written SPIR-V listing is included here; the source links are the authoritative artifacts.

## Runtime Execution and Result Checking

- The host creates a 32x32 `VK_FORMAT_R8G8B8A8_UNORM` color image and, when required, a depth or stencil attachment. It creates a host-visible vertex buffer and transfer buffers for image readback. The base, discard, and sample-mask paths also create a coherent storage-buffer descriptor for the atomic result; the sample-count path instead creates a two-entry precise occlusion-query pool.
- The command buffer transitions images, begins render passes, clears color and depth/stencil values, binds the generated pipelines, draws six vertices, and copies attachment contents to host-visible buffers before waiting for completion. The base, discard, and sample-mask paths bind the storage-buffer descriptor; sample-count paths run no-early and early pipelines under separate query entries.
- Base and discard paths invalidate the readback allocations and compare color with a generated reference using `tcu::floatThresholdCompare`. They then inspect depth/stencil values and the atomic counter. The base counter uses an exact or tolerance-bounded range derived from the selected early-test and attachment modes.
- Sample-mask paths use multisampled color and depth/stencil attachments and resolve images. They compare the resolved color image and depth/stencil readback, then check the atomic counter.
- Sample-count paths create two precise occlusion-query entries, draw once without early tests and once with early tests, copy both resolved color images, and wait for the query results before applying the explicit acceptance branches described above.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Base depth/stencil or no-attachment case | Incorrect ordering or execution of early depth/stencil tests; incorrect fragment-shader side-effect or attachment handling |
| Discard depth/stencil case | Discard applied at the wrong point relative to depth/stencil testing, or incorrect depth/stencil update after fragment shading |
| Sample-mask case | Incorrect ordering or application of shader sample-mask writes relative to depth/stencil testing and fragment shading |
| Sample-count case | Incorrect sample-count ordering relative to fragment shading, multisample coverage, sample-mask testing, or alpha-to-coverage; incorrect maintenance5 or AMD-mode behavior after support checks |

### Cause Analysis

#### Early depth/stencil ordering and attachment handling

**Possible failure symptoms:** The color comparison, depth/stencil per-pixel check, or atomic counter check fails. The source expects different attachment values and counter ranges for early versus non-early modes and for attachment versus `_no_attachment` cases.

**Possible implementation causes:** The implementation may execute depth/stencil testing at an order inconsistent with the shader's declared mode, update the wrong attachment state, or produce a different set of fragment-shader invocations. The source and fragment-operation specification establish the ordering under test; a more specific cause requires investigation of the failing path.

#### Discard ordering

**Possible failure symptoms:** A depth or stencil value remains at the clear value when the early case expects an update, or changes when the non-early case expects the clear value. The counter or color check may also fail.

**Possible implementation causes:** The implementation may apply `discard` before the early depth/stencil write, or may apply the depth/stencil test after a discard in a path where the source expects an earlier update. The source does not identify a particular hardware or driver component as the cause.

#### Shader sample-mask ordering

**Possible failure symptoms:** The sample-mask case reports unexpected depth/stencil values, color output, or atomic-counter values after the shader writes `gl_SampleMask[0] = 0x0`.

**Possible implementation causes:** The implementation may apply the shader sample-mask result at an unexpected point relative to early depth/stencil testing or fragment shading. The source's support and validation code does not isolate whether a failure originates in hardware, the driver, or shader compilation.

#### Sample-count ordering

**Possible failure symptoms:** A query result falls outside the expected range, or the early result is zero or doubled in a maintenance5 case whose reported property requires the opposite ordering. The source logs the no-early and early images when neither accepted range matches.

**Possible implementation causes:** The implementation may order fragment shading, multisample coverage, sample-mask testing, or alpha-to-coverage differently from the source's selected acceptance branch. For non-maintenance5 cases, the source explicitly permits some outcomes as quality warnings, so a warning is not the same result as a failed correctness check.

## Case Pruning

### Requirement-based pruning

- Early-and-late and maintenance5 registrations are compiled out for VulkanSC by `#ifndef CTS_USES_VULKANSC`.
- Base and sample-count cases require `fragmentStoresAndAtomics`; early-and-late cases additionally require `VK_AMD_shader_early_and_late_fragment_tests` and a true `shaderEarlyAndLateFragmentTests` feature bit.
- Sample-mask cases require `VK_KHR_depth_stencil_resolve` and query the selected color and depth/stencil format properties to verify support for the requested sample count.
- Sample-count cases require precise occlusion queries and supported multisampled color and depth formats. Their `_maintenance5` registrations require `VK_KHR_maintenance5`.

### Design-based pruning

- The registration loops generate only sample counts 2, 4, 8, and 16.
- Sample-mask cases target depth and use one set of early/early-and-late variants; they do not generate the full depth/stencil and attachment matrix used by the base family.
- Alpha-to-coverage is generated only for the early-fragment maintenance5 sample-count cases. The sample-count implementation always uses a depth test rather than adding a stencil family.

## Key Takeaways

- The base, discard, and sample-mask families use shader side effects plus attachment readback to expose the ordering of early depth/stencil tests.
- `EarlyAndLateFragmentTestsAMD` is an explicit SPIR-V mode and is available only in non-VulkanSC registrations after its extension and feature checks pass.
- Sample-count cases compare two precise occlusion-query results and accept only the ranges and quality-warning paths encoded in the source; the page does not generalize those branches beyond the tested cases.
- The maintenance5 variants use `earlyFragmentMultisampleCoverageAfterSampleCounting` and `earlyFragmentSampleMaskTestBeforeSampleCounting` to decide whether zero or doubled sample counts are allowed or failing.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createEarlyFragmentTests()` | [`registration`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2755-L2895) | Registers every direct child and generated sample-count variant |
| Base shader generation and checks | [`EarlyFragmentTest`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L208-L640) | Defines early-test modes, atomic side effects, image comparison, and counter validation |
| Discard implementation | [`EarlyFragmentDiscardTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L642-L1125) | Tests discard with depth/stencil writes |
| Sample-mask implementation | [`EarlyFragmentSampleMaskTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1127-L1916) | Tests `gl_SampleMask` across multisample counts |
| Sample-count implementation | [`EarlyFragmentSampleCountTestInstance::iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2136-L2522) | Runs the paired queries and applies acceptance rules |
| Sample-count shaders and support | [`EarlyFragmentSampleCountTest`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2524-L2750) | Defines sample-mask, alpha-to-coverage, AMD mode, and maintenance5 variants |
| Declaration | [`vktFragmentOperationsEarlyFragmentTests.hpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.hpp#L1-L41) | Declares `createEarlyFragmentTests()` |
| Vulkan fragment operation order | [`Fragment Operations`](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops) | Defines early-fragment, sample-mask, multisample coverage, maintenance5, and sample-count semantics |
| Mustpass list | [`fragment-operations.txt`](../../../mustpass/main/vk-default/fragment-operations.txt) | Records vk-default coverage for the registered paths |
