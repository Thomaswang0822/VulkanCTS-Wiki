# vktPipelineColorWriteEnableTests.cpp

## Overview

[`vktPipelineColorWriteEnableTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1) implements two topic groups of the pipeline category: [`color_write_enable`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1662) and [`color_write_enable_maxa`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1832). It verifies `VK_EXT_color_write_enable` dynamic state, which allows per-attachment color write enable to be set dynamically via `cmdSetColorWriteEnableEXT()`, including tests at `maxColorAttachments` limits.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineColorWriteEnableTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1)
- Header: [`vktPipelineColorWriteEnableTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.hpp#L1)

## Registration Path

This file contributes two subgroups:
- [`createColorWriteEnableTests()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1662) returns the `color_write_enable` group
- [`createColorWriteEnable2Tests()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1832) returns the `color_write_enable_maxa` group

Both are attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L1).

**Variant coverage**: All variants.

## Test Hierarchy

```text
color_write_enable
├── all_channels                          (BVec4(true,true,true,true))
│   ├── cmd_buffer_start
│   │   ├── enable_all / enable_first / enable_second / enable_last
│   │   ├── enable_first_and_second / enable_second_and_last
│   │   ├── disable_all / disable_first / disable_second / disable_last
│   │   ├── disable_first_and_second / disable_second_and_last
│   ├── before_draw / between_pipelines / after_pipelines
│   │   └── (same 12 tests)
│   ├── before_good_static / two_draws_dynamic / two_draws_static
│   │   └── (same 12 tests)
│   └── static
│       └── (same 12 tests, static-only)
├── red_channel / green_channel / blue_channel / alpha_channel
│   └── (same ordering subgroups as above)
└── no_channels
    └── (same ordering subgroups as above)

color_write_enable_maxa
├── cwe_before_bind                       (setColorWriteEnable before pipeline bind)
│   ├── attachments3_more0 through attachments3_more3
│   ├── attachments4_more0 through attachments4_more3
│   └── attachments5_more0 through attachments5_more3
└── cwe_after_bind                        (setColorWriteEnable after pipeline bind)
    └── (same attachment combinations)
```

Source: [`createColorWriteEnableTests()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1662), [`createColorWriteEnable2Tests()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1832).

## Test Families

### color_write_enable group

#### 1. Channel enable groups

Control which RGBA channels are enabled in the `colorWriteMask`. Six channel mask variants: all_channels, red_channel, green_channel, blue_channel, alpha_channel, no_channels. Tests that only enabled channels are written.

#### 2. Ordering groups

Control when the dynamic color write enable state is set relative to pipeline binding and draw calls:
- `cmd_buffer_start`: Set at command buffer start
- `before_draw`: Set before draw call
- `between_pipelines`: Set between pipeline binds (skipped for shader object)
- `after_pipelines`: Set after pipeline binds (skipped for shader object)
- `before_good_static`: Set before a good static pipeline
- `two_draws_dynamic`: Two draws with dynamic state
- `two_draws_static`: Two draws with static state
- `static`: Statically-set color write enable (no dynamic state)

#### 3. Enable/Disable tests

Control which of the 3 color attachments have writes dynamically enabled or disabled. 12 patterns: enable_all, enable_first, enable_second, enable_last, enable_first_and_second, enable_second_and_last, and corresponding disable_* variants.

### color_write_enable_maxa group

#### 4. cwe_before_bind / cwe_after_bind

When `cmdSetColorWriteEnableEXT()` is called relative to pipeline binding. Tests with varying attachment counts (3, 4, 5) and additional "more" attachments (0-3), exercising `maxColorAttachments` limits.

## Parameter Dimensions

### color_write_enable (TestConfig struct at [line 147](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L147))

| Parameter | Source | Values |
|---|---|---|
| channelMask | `tcu::BVec4` | 6 cases (all, red, green, blue, alpha, none) |
| sequenceOrdering | [SequenceOrdering enum](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L133) | 7 dynamic values + static |
| colorWriteEnableConfig | `StaticAndDynamicPair<Bool32Vec>` | 6 mask patterns x enable vs. disable |
| inverse | `bool` | `true`/`false` (enable vs. disable tests) |
| pipelineConstructionType | Factory parameter | PipelineConstructionType |

### color_write_enable_maxa (TestParams struct at [line 1101](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1101))

| Parameter | Source | Values |
|---|---|---|
| attachmentCount | Loop | {3, 4, 5} |
| attachmentMore | Loop | {0, 1, 2, 3} |
| setCweBeforePlBind | `bool` | `true`/`false` |
| colorWriteEnables | `bool` | `true` |
| pct | Factory parameter | PipelineConstructionType |

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| `VK_EXT_color_write_enable` | `checkSupport` | [283](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L283) |
| Color format support (`VK_FORMAT_R8G8B8A8_UNORM` with COLOR_ATTACHMENT_BIT + TRANSFER_SRC_BIT) | `checkSupport` | [286](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L286) |
| Depth/stencil format support | `checkSupport` | [293](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L293) |
| `attachmentCount + attachmentMore <= maxColorAttachments` (maxa group) | `checkSupport` | [1242](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1242) |
| Pipeline construction requirements (maxa group) | `checkSupport` | [1262](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1262) |

## Verification Methods

### color_write_enable group

**Per-pixel color comparison** with threshold `kColorThreshold(0.005f)` at [line 940](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L940). For each of the 3 color attachments, every pixel is compared against the expected color. An error mask image is generated for logging.

**Depth comparison** with tolerance `1.0e-07f` at [line 962](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L962). Verifies that depth is always written even when color writes are disabled.

### color_write_enable_maxa group

**Per-pixel color comparison** in `verifyAttachment()` at [line 1547](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1547). Expected value depends on whether the attachment's color write enable is set: if enabled, the source color (attenuated by blend factor) is expected; if disabled, the background (clear) color is expected.

## Test Principles Observed

- **Channel-level write control**: Tests each channel independently to verify that color write enable masks work per-channel
- **State ordering coverage**: Multiple ordering variants test when dynamic state is set relative to pipeline binding and draw calls
- **Depth-write independence**: Verifies that disabling color writes does not affect depth writes
- **maxColorAttachments limit testing**: The `maxa` group exercises the device's maximum attachment count

## Notes / Uncertainties

- For shader object construction type, `between_pipelines` and `after_pipelines` orderings are skipped ([line 1725](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1725)) because these orderings involve binding multiple pipelines, which is not applicable to shader objects
- The `static` subgroup tests pipelines with no dynamic color write enable state at all
