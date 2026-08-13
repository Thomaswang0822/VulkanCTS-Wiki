# Understanding Brief: fragment_operations.early_fragment

## One-Sentence Test Purpose

This test checks whether early fragment-test ordering preserves the expected depth, stencil, sample-mask, discard, and sample-count results when fragment shaders have observable side effects.

## Background Knowledge

### Early fragment tests and fragment-shader side effects

A fragment shader normally runs before the depth and stencil tests that determine whether its outputs reach the attachments. Declaring `layout(early_fragment_tests) in;` changes the ordering of depth and stencil testing relative to fragment shading. The source uses a coherent storage buffer and `atomicAdd()` as an observable side effect: the counter records fragment shader invocations even when a later operation discards the fragment, while attachment contents show which depth or stencil tests actually ran.

`EarlyAndLateFragmentTestsAMD` is a separate SPIR-V execution mode used by non-VulkanSC cases. The source emits it directly and gates it on `VK_AMD_shader_early_and_late_fragment_tests` and the `shaderEarlyAndLateFragmentTests` feature.

### Multisample coverage and sample counting

A multisampled fragment carries a coverage bit for each sample. Fragment operations can clear coverage bits, and the occlusion-query sample counter increments for surviving covered samples after the per-fragment tests. The source compares two query results: one from a shader without early fragment tests and one from a shader with early fragment tests. The latter shader either clears `gl_SampleMask[0]` or emits zero alpha with alpha-to-coverage, so the ordering of fragment shading, multisample coverage, sample-mask testing, and sample counting changes the observed count.

`VK_KHR_maintenance5` exposes properties that constrain or describe these ordering choices. The test only uses those properties in the `_maintenance5` sample-count cases; it does not treat an implementation's optional ordering as a universal failure.

## One Concrete Example

In a representative depth case, the host clears a 32x32 color image and a depth attachment to `0.5`, draws a rectangle, and binds a fragment shader that increments `sb_out.result` and writes yellow. With `early_fragment_tests`, the depth test can update the depth attachment before fragment shading. Without the declaration, the shader runs before the depth test. The host reads back the color image and the counter, then compares both with values derived from the selected depth/stencil mode and attachment use.

For a discard case, the fragment shader performs the atomic increment, writes `gl_FragDepth = 0.75f`, writes color, and executes `discard`. The source's verification checks that early tests still update depth or stencil, while the non-early path retains the cleared depth/stencil values when the fragment is discarded after shading.

For sample counting, the no-early shader writes `gl_SampleMask[0] = 0xAAAAAAAA`. The early shader declares `layout(early_fragment_tests) in;` and then writes `gl_SampleMask[0] = 0x0`, or writes zero alpha when alpha-to-coverage is selected. The source expects approximately half the total samples, allows zero for one permitted ordering, and allows a doubled early count when sample-mask testing occurs after counting. Maintenance5 properties turn the relevant optional outcomes into pass/fail checks for the maintenance5 variants.

## End-to-End Test Flow

```text
[host] select depth or stencil mode, early-test mode, attachment mode, sample count, and optional sample-count modifiers
[host] check required features, extensions, image-format sample counts, and precise occlusion-query support where applicable
[host] create color and depth/stencil images, buffers, descriptors, render passes, framebuffers, pipelines, and query pools
[host] generate GLSL or the direct SPIR-V needed by the selected early-and-late case
[host] clear attachments and submit the draw; sample-count cases run no-early and early pipelines under two occlusion queries
[device] execute the fragment shader, including atomic increments, discard, sample-mask writes, or alpha-to-coverage behavior
[device] update color and depth/stencil attachments and occlusion-query counters according to the implementation's ordering
[host] copy images and buffers back, invalidate allocations, compare images and depth/stencil values, and inspect the atomic counter or query results
[host] return pass, fail, or quality warning according to the source's explicit checks
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The base and discard/sample-mask families generate GLSL vertex and fragment shaders. The base fragment shader optionally includes `layout(early_fragment_tests) in;`; the shader then increments a storage-buffer counter and writes color. The discard and sample-mask shaders add their respective side effects.
- Early-and-late variants use inline SPIR-V assembly with the `SPV_AMD_shader_early_and_late_fragment_tests` extension and `OpExecutionMode ... EarlyAndLateFragmentTestsAMD`.
- Sample-count variants generate separate no-early and early fragment programs. The early program declares `EarlyFragmentTests`; its source clears `gl_SampleMask[0]` or uses zero alpha for alpha-to-coverage.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color image and view | yes | yes | color attachment write | yes, through a transfer buffer | Image output and reference comparison |
| Depth/stencil image and view | yes when the selected case uses an attachment | yes | depth/stencil attachment write | yes, through a transfer buffer in the base, discard, and sample-mask paths | Shows whether early depth/stencil tests update the attachment |
| Coherent storage buffer `sb_out` | yes | yes, at fragment binding 0 | fragment shader atomic write | yes | Counts shader invocations as an observable side effect |
| Vertex buffer | yes | yes | vertex fetch | no | Supplies the rectangle geometry |
| Occlusion query pool | yes for sample-count tests | yes, around draw calls | sample-count write | yes, with `vkGetQueryPoolResults` | Reports samples surviving the per-fragment tests |

`gl_SampleMask` and fragment outputs are shader interface variables, not host-created buffers. The sample-count path also uses multisampled color and depth images plus resolve images.

## What Is Checked

- Base cases compare the rendered color image with a generated reference using `tcu::floatThresholdCompare`, then compare the atomic counter with an exact or tolerance-bounded expected range. Depth and stencil values are checked per pixel against the values implied by the selected mode and early-test setting.
- Discard and sample-mask cases compare color and depth/stencil readback and inspect the atomic counter. The source comments and checks specifically target depth/stencil writes when the shader discards or clears its sample mask.
- Sample-count cases first require both query results to be in the expected range. The reference is `(32 * 32 / 4) * sampleCount`, with a 5% tolerance. The source then accepts the early result in the same range, accepts zero as a quality-warning path unless a maintenance5 property makes it a failure, or accepts a doubled result when sample-mask testing occurs after counting, again applying the maintenance5 property when selected.

## Behavior Parameter Identification

> **Behavior parameter:** registered test family and its mode/value suffix
>
> **Candidate values:** base depth/stencil cases, discard depth/stencil cases, sample-mask depth cases at 2/4/8/16 samples, and sample-count depth cases at 2/4/8/16 samples with early-and-late, maintenance5, or alpha-to-coverage modifiers

The family is the primary behavioral axis because each family changes the operation whose ordering is being checked. Within the parameterized families, depth versus stencil, early mode, attachment use, sample count, and the sample-count modifiers change the concrete behavior or its acceptance rule.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Base depth/stencil or no-attachment case | Incorrect ordering or execution of early depth/stencil tests; incorrect fragment-shader side-effect or attachment handling |
| Discard depth/stencil case | Discard applied at the wrong point relative to depth/stencil testing, or incorrect depth/stencil update after fragment shading |
| Sample-mask case | Incorrect ordering or application of shader sample-mask writes relative to depth/stencil testing and fragment shading |
| Sample-count case | Incorrect sample-count ordering relative to fragment shading, multisample coverage, sample-mask testing, or alpha-to-coverage; unsupported maintenance5 or AMD mode handling |

## Important Variations and Special Cases

- Depth and stencil use different attachment formats and per-pixel expected values. The base family also has `_no_attachment` variants, which omit the test depth/stencil attachment while retaining the color path.
- `early_and_late_fragment_tests_*` and the corresponding discard, sample-mask, and sample-count cases are excluded from VulkanSC builds by `#ifndef CTS_USES_VULKANSC`.
- Sample-mask cases use 2, 4, 8, and 16 samples. They require `VK_KHR_depth_stencil_resolve` and validate that writing `gl_SampleMask[0] = 0x0` does not change the tested depth behavior.
- Sample-count cases use `SampleCountTestParams { sampleCount, earlyAndLate, alphaToCoverage, useMaintenance5 }`. The maintenance5 cases require `VK_KHR_maintenance5`; alpha-to-coverage appears only in the early-fragment maintenance5 registrations.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test-group registration | [`createEarlyFragmentTests()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2755-L2895) | Defines the direct children and parameterized names |
| Base shader and instance flags | [`EarlyFragmentTest`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L199-L348) | Defines depth/stencil, attachment, early, and early-and-late modes |
| Base execution and checks | [`EarlyFragmentTestInstance::iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L352-L621) | Creates resources, draws, compares images, and checks the atomic counter |
| Support gates | [`checkSupport()` implementations](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L629-L640) and [`EarlyFragmentSampleCountTest::checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2713-L2750) | Shows required features, extensions, formats, and query support |
| Discard checks | [`EarlyFragmentDiscardTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L642-L970) | Shows discard shader behavior and depth/stencil expectations |
| Sample-mask checks | [`EarlyFragmentSampleMaskTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1127-L1778) | Shows multisample setup, image comparisons, and counter checks |
| Sample-count query checks | [`EarlyFragmentSampleCountTestInstance::iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2136-L2522) | Shows query setup, image comparison, accepted ranges, and warning paths |
| Vulkan fragment-operation ordering | [`fragops.adoc`](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops) | Defines coverage, sample-mask, early-fragment, maintenance5, and sample-count semantics |
| Mustpass coverage | [`fragment-operations.txt`](../../../mustpass/main/vk-default/fragment-operations.txt) | Lists the enabled vk-default test paths |

## Questions / Risk Points for User Audit

- Is the distinction between an early depth/stencil test and the shader's later storage-buffer atomic side effect clear?
- Should the final page include a full generated SPIR-V walkthrough, or is the concise source-linked description sufficient for this multi-family page?
- Does the explanation of zero and doubled sample-count results preserve the source's quality-warning versus pass/fail behavior?
- Are the VulkanSC exclusions and maintenance5-only registrations visible without implying that all early-and-late cases exist in VulkanSC?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page's `## Background Knowledge` limited to early depth/stencil ordering, shader side effects, and multisample sample counting.
- Use the registered test family as the primary behavior axis, with compact tables for depth/stencil, sample count, early-and-late mode, attachment use, alpha-to-coverage, and maintenance5.
- Explain the three source-backed result classes for sample-count cases: expected range, zero with a quality warning or maintenance5-specific pass/fail, and doubled count with the analogous sample-mask ordering rule.
- Preserve the source's exact identifiers and direct-child notes in the parseable registration tree.
- Keep shader details tied to the generated programs and do not invent a reconstructed shader or SPIR-V listing beyond the source evidence inspected here.
