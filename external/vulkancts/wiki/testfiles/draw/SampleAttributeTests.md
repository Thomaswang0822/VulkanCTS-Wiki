## Overview

**Core question:** Does a fragment shader use of `gl_SampleID`, `gl_SamplePosition`, or a `sample`-decorated input force implicit sample-rate shading when pipeline sample shading is disabled?

- The [`implicit_sample_shading`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L496-L517) test family contains three fragment-shader trigger variants.
- Each case renders one full-screen triangle into a 4 × 4, four-sample color attachment and increments a fragment-storage atomic counter.
- The pipeline sets `sampleShadingEnable = VK_FALSE` and `minSampleShading = 0.0`; the host verdict requires at least 64 counter increments, demonstrating one invocation per covered sample.
- The same implementation is registered under the render-pass path and the three non-nested dynamic-rendering paths; nested dynamic-rendering paths omit it because the draw dispatcher excludes this family for nested command buffers.

## Background Knowledge

- **Sample shading:** A multisample fragment can be shaded once per pixel or once for each covered sample. Vulkan permits implicit sample shading when a fragment shader statically uses `SampleID` or `SamplePosition`, and gives a `sample`-decorated input the corresponding sample-rate behavior. See [sample shading](https://registry.khronos.org/vulkan/specs/latest/html/chapters/primsrast.html#primsrast-sampleshading).
- **Fragment shader interface decorations:** `SampleID` identifies the sample for a sample-rate invocation, `SamplePosition` provides that sample's position, and the `sample` decoration selects sample interpolation for an input. These are shader interface semantics, not additional host-created resources. See [fragment shader inputs](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-fragmentinput).

## Registration Hierarchy

The dispatcher adds this family whenever `nestedSecondaryCmdBuffer` is false. The five rendering-path roots are created by [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198), while [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L101) supplies the nested-command-buffer boundary.

```text
draw.renderpass
└── implicit_sample_shading
```

```text
draw.dynamic_rendering.primary_cmd_buff
└── implicit_sample_shading
```

```text
draw.dynamic_rendering.partial_secondary_cmd_buff
└── implicit_sample_shading
```

```text
draw.dynamic_rendering.complete_secondary_cmd_buff
└── implicit_sample_shading
```

The family has three direct test case leaves:

```text
implicit_sample_shading
├── sample_decoration_dynamic_use
├── sample_id_static_use
└── sample_position_static_use
```

The checked-in mustpass lists confirm all three leaves under `draw.renderpass`, `draw.dynamic_rendering.primary_cmd_buff`, `draw.dynamic_rendering.partial_secondary_cmd_buff`, and `draw.dynamic_rendering.complete_secondary_cmd_buff` in `external/vulkancts/mustpass/main/vk-default/draw.txt` (12 entries total). The Vulkan SC list contains the three render-pass leaves in `external/vulkancts/mustpass/main/vksc-default/draw.txt` (3 entries total), matching the `#ifndef CTS_USES_VULKANSC` guard around dynamic-rendering test-tree creation and execution. Neither list contains the two nested dynamic-rendering roots, matching the dispatcher's `nestedSecondaryCmdBuffer` guard. The mustpass files select registered paths; feature and extension availability still determines whether an individual case is supported at runtime.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Trigger mechanism | `sample_decoration_dynamic_use`, `sample_id_static_use`, `sample_position_static_use` | Selects the fragment-shader construct that must cause implicit sample shading. | [`triggerCases`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L498-L509) |
| Sample count | `VK_SAMPLE_COUNT_4_BIT` | Provides four coverage samples per pixel for the invocation-count lower bound. | [`sampleCount`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L99-L102) |
| Render target | 4 × 4, `VK_FORMAT_R8G8B8A8_UNORM` | Covers 16 pixels; the color value is stored but is not the authoritative result. | [`imageFormat` and `imageExtent`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L206-L224) |
| Rendering path | `renderpass`; `dynamic_rendering.primary_cmd_buff`, `partial_secondary_cmd_buff`, `complete_secondary_cmd_buff` | Changes command recording and attachment setup without changing the shader trigger or expected count. | [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) |

## Behavior Parameters

The primary behavioral axis is the registered test case leaf, because each leaf changes the fragment-shader trigger while the host setup and counter check remain shared.

### `sample_decoration_dynamic_use`: dynamically used sample-qualified input

The vertex shader writes `verify` at location 0, and the fragment shader reads `layout (location = 0) sample in float verify`. It converts `ceil(verify)` to the increment value. The generated vertex values are between 0.75 and 1.0, so the increment is 1 while the `sample` decoration supplies the behavior under test. See [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L127-L168).

### `sample_id_static_use`: static use of `gl_SampleID`

The fragment shader contains the statement `gl_SampleID;` and increments the counter by 1. The value need not feed the color result: its static use is the trigger being tested.

### `sample_position_static_use`: static use of `gl_SamplePosition`

The fragment shader contains the statement `gl_SamplePosition;` and increments the counter by 1. As with `gl_SampleID`, the built-in's static use is the behavior under test rather than its numeric value.

## Shader Analysis

The generated vertex shader emits a full-screen triangle from three constant positions. Only the sample-decoration case adds the `verify` output. The fragment shader always writes a color and atomically adds to `buf.invocationCount`; the trigger variants add either a built-in reference or the `sample` input declaration. See [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L127-L168).

No separate shader-disassembler walkthrough is included: this page documents the generated GLSL trigger and the host-side invocation-count contract, and the exact shader strings are short and fully represented by the linked builder.

## Runtime Execution and Result Checking

- Support checking requires `fragmentStoresAndAtomics` for the storage-buffer atomic operation and `sampleRateShading` for all three trigger variants. Dynamic-rendering paths additionally require `VK_KHR_dynamic_rendering`. See [`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L113-L125).
- The instance creates a host-visible one-`uint32_t` storage buffer, clears it to zero, binds it at fragment descriptor binding 0, and creates a four-sample 4 × 4 color attachment. See [`iterate()` resource setup](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L182-L340).
- A graphics pipeline uses triangle-list rasterization and explicitly disables pipeline sample shading with `sampleShadingEnable = VK_FALSE`, `minSampleShading = 0.0`, and `rasterizationSamples = VK_SAMPLE_COUNT_4_BIT`. See [`multisampling`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L345-L365).
- The command buffer records either a render pass or dynamic rendering, binds the descriptor set and pipeline, and draws three vertices. Secondary-buffer cases differ only in where rendering and draw commands are recorded. A fragment-to-host buffer barrier, submission wait, and allocation invalidation precede the readback. See [`iterate()` command and readback flow](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L390-L482).
- The host compares the counter against `sampleCount * width * height = 4 * 4 * 4 = 64`. Values below 64 fail; values at or above 64 pass. See [`expectedCounter` and verdict](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L99-L102) and [`iterate()` result check](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L472-L491).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `sample_decoration_dynamic_use` | Failure to apply sample-qualified interpolation or implicit sample-rate execution; fragment input interface/lowering error; counter or synchronization problem. |
| `sample_id_static_use` | Failure to treat static `gl_SampleID` use as an implicit sample-shading trigger; fragment built-in handling; counter or synchronization problem. |
| `sample_position_static_use` | Failure to treat static `gl_SamplePosition` use as an implicit sample-shading trigger; fragment built-in handling; counter or synchronization problem. |
| Any value | Multisample attachment, pipeline sample state, draw coverage, atomic storage, barrier, or host readback can produce a low counter. |

### Cause Analysis

#### Trigger does not produce sample-rate invocations

**Possible failure symptoms:** The counter is below 64 for one trigger leaf, showing fewer than one counted invocation per sample for the 16-pixel target.

**Possible implementation causes:** The implementation may fail to recognize the relevant built-in or `sample` decoration as an implicit sample-shading trigger, or may lower the fragment interface/built-in incorrectly. The Vulkan sample-shading rules and the case-specific shader source establish the expected behavior; source-level investigation is needed to locate the responsible implementation component.

#### Multisample execution or coverage is incorrect

**Possible failure symptoms:** Multiple trigger leaves fail with a counter below 64, or the result varies with the rendering path despite identical shader behavior.

**Possible implementation causes:** The multisample attachment, rasterization sample state, draw coverage, render-pass/dynamic-rendering setup, or secondary-command-buffer execution may be incorrect. The source does not identify which implementation layer is responsible.

#### Atomic counter result is not visible to the host

**Possible failure symptoms:** Rendering completes but the host reads zero or a stale value, producing the explicit `Atomic counter value lower than expected` failure.

**Possible implementation causes:** The shader storage write, fragment-to-host memory dependency, mapped allocation visibility, or host invalidation/readback path may be incorrect. The test's barrier and allocation operations are visible in source; distinguishing an implementation fault from an environment issue requires further investigation.

## Case Pruning

### Requirement-based pruning

- A case is unsupported unless `fragmentStoresAndAtomics` and `sampleRateShading` are available. Dynamic-rendering variants additionally require `VK_KHR_dynamic_rendering` ([`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L113-L125)).

### Design-based pruning

- The fixed 4 × 4 target and four-sample attachment keep the atomic-counter proof small; the test does not expand a sample-count or framebuffer-size matrix.
- Nested dynamic-rendering paths intentionally omit the family because [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L101) does not add it when `nestedSecondaryCmdBuffer` is true. This is a registration boundary, not a claim that the trigger semantics are invalid there.

## Key Takeaways

- All three leaves test implicit sample shading, but each uses a distinct fragment-shader trigger.
- Pipeline sample shading remains disabled, so the counter is evidence of shader-triggered behavior rather than explicit `minSampleShading` configuration.
- The authoritative check is a host-visible atomic counter of at least 64 after a 4 × 4 draw with four samples per pixel.
- Render-pass and three non-nested dynamic-rendering paths share this family; nested paths preserve the dispatcher’s intentional omission.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test-family factory | [`createSampleAttributeTests()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L496-L519) | Registers the family and its three test case leaves. |
| Trigger enum and parameters | [`Trigger`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L59-L72) | Defines the behavioral variants. |
| Support gate | [`checkSupport()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L113-L125) | Defines feature and dynamic-rendering requirements. |
| Shader generation | [`initPrograms()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L127-L168) | Generates the three fragment-shader trigger forms. |
| Host execution and verdict | [`iterate()`](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L182-L491) | Creates resources, records rendering, reads the counter, and applies the 64 minimum. |
| Draw dispatcher | [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L101) | Establishes non-nested registration and nested-path omission. |
| Rendering-path roots | [`createTests()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L198) | Creates render-pass and dynamic-rendering hierarchy roots. |
| Vulkan sample-shading semantics | [Sample shading](https://registry.khronos.org/vulkan/specs/latest/html/chapters/primsrast.html#primsrast-sampleshading) | Defines implicit sample-shading triggers and rates. |
| Vulkan fragment interfaces | [Fragment shader interfaces](https://registry.khronos.org/vulkan/specs/latest/html/chapters/interfaces.html#interfaces-fragmentinput) | Defines sample-related input decorations and built-ins. |
| Understanding Brief | [SampleAttributeTests_brief.md](SampleAttributeTests_brief.md) | Learning-oriented analysis and source mapping. |
