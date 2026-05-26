# fragment_operations

## Overview

The [`fragment_operations`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L50-L53) category covers fragment-stage-adjacent graphics tests registered under the root group name passed into [`createTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L50-L53). The root registration file is [`vktFragmentOperationsTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L1), and its include section shows that the category dispatches to four sibling registration files: [`vktFragmentOperationsScissorTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L24-L30), [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L24-L30), [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L24-L30), and [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L24-L30).

Category facts below are drawn from the inspected source files under [`external/vulkancts/modules/vulkan/fragment_ops/`](../../modules/vulkan/fragment_ops/).

## Registration Entry Point

The category entry point is [`createTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L50-L53), which builds the root group through `createTestGroup()` and the local dispatcher [`addFragmentOperationsTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L38-L46). The direct children registered under the category are:

```text
fragment_operations
├── scissor
├── early_fragment
├── occlusion_query
└── transient_attachment_bit
```

Source: [`addFragmentOperationsTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L38-L46).

## File Inventory

| File | Role | Registered group(s) / notes |
|---|---|---|
| [`vktFragmentOperationsTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L1) | Root registration dispatcher | Root `fragment_operations` group only |
| [`vktFragmentOperationsScissorTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L1) | Registration and implementation | `scissor`, with nested `multi_viewport` child delegated to [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L25-L28) and [`vktFragmentOperationsScissorTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L573-L576) |
| [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1) | Registration and implementation | `early_fragment` |
| [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L1) | Registration and implementation | `occlusion_query` |
| [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L1) | Registration and implementation | `transient_attachment_bit` |
| [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L1) | Registration and implementation helper | Registers nested `multi_viewport` subgroup beneath `scissor`, not a root child |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktFragmentOperationsScissorTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L1) | [`vktFragmentOperationsScissorTests.md`](../testfiles/fragment_operations/vktFragmentOperationsScissorTests.md) |
| [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1) | [`vktFragmentOperationsEarlyFragmentTests.md`](../testfiles/fragment_operations/vktFragmentOperationsEarlyFragmentTests.md) |
| [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L1) | [`vktFragmentOperationsOcclusionQueryTests.md`](../testfiles/fragment_operations/vktFragmentOperationsOcclusionQueryTests.md) |
| [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L1) | [`vktFragmentOperationsTransientAttachmentTests.md`](../testfiles/fragment_operations/vktFragmentOperationsTransientAttachmentTests.md) |
| [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L1) | [`vktFragmentOperationsScissorMultiViewportTests.md`](../testfiles/fragment_operations/vktFragmentOperationsScissorMultiViewportTests.md) |

## Subgroup Structure and Major Themes

### `scissor` — fixed scissor clipping families

[`createScissorTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L581-L584) registers the displayed group name `scissor`. Inside that group, [`createTestsInGroup()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L512-L576) creates `points`, `lines`, `triangles`, and `multi_viewport`. The point, line, and triangle branches vary whether primitives are fully inside, partially inside, outside, or crossing the scissor rectangle, while `multi_viewport` is delegated to the companion file [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L573-L576).

### `multi_viewport` — repeated scissor grids over viewport counts

[`createScissorMultiViewportTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L442-L450) builds the `multi_viewport` subgroup and registers leaf cases `scissor_1` through `scissor_16` by looping from `1` to [`MIN_MAX_VIEWPORTS`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L61-L64). The constant is documented in code as the minimum number of viewports guaranteed when `multiViewport` is supported.

### `early_fragment` — depth, stencil, discard, sample-mask, and sample-count behavior

[`createEarlyFragmentTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2755-L2895) registers `early_fragment` and directly adds several families of named cases:

- base early-fragment versus no-early-fragment depth and stencil tests, including `_no_attachment` variants at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2766-L2797)
- discard-focused depth and stencil cases at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2800-L2821)
- sample-mask cases over sample counts 2, 4, 8, and 16 at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2823-L2849)
- sample-count cases over the same sample counts, with optional early-and-late, `maintenance5`, and alpha-to-coverage variants at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2852-L2890)

### `occlusion_query` — precise versus conservative counts under fragment-operation modifiers

[`createOcclusionQueryTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L706-L767) registers `occlusion_query`. It defines a table of scissor, depth-clear, depth-write, stencil-clear, stencil-write, and combined `test_all` variants at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L710-L753), then instantiates both `conservative...` and `precise...` forms for every case at [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L755-L763).

### `transient_attachment_bit` — transient attachment load/store verification

[`createTransientAttachmentTests()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L601-L627) registers `transient_attachment_bit`. It creates six named cases spanning color, depth, and stencil test modes crossed with lazily allocated versus device-local memory properties at [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L607-L623).

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Primitive class | `points`, `lines`, and `triangles` in [`vktFragmentOperationsScissorTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L512-L570) |
| Scissor coverage relation | `inside`, `partially_inside`, `outside`, and `crossing` in [`vktFragmentOperationsScissorTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorTests.cpp#L516-L565) |
| Viewport count | `scissor_1` through `scissor_16` in [`vktFragmentOperationsScissorMultiViewportTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L442-L450) |
| Early-fragment mode | no early tests, early tests, and non-VulkanSC early-and-late tests in [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2766-L2788) |
| Attachment/test target | depth versus stencil in the early-fragment base and discard families at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2768-L2777) and [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2807-L2815) |
| Sample count | 2, 4, 8, and 16 in early-fragment sample-mask and sample-count families at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2839-L2848) and [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2854-L2889) |
| Occlusion-query modifiers | scissor, depth clear, depth write, stencil clear, stencil write, and combined `test_all` in [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L716-L753) |
| Query precision mode | `conservative` and `precise` prefixes in [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L755-L763) |
| Attachment mode | color, depth, and stencil in [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L56-L62) and [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L613-L618) |
| Memory-property mode | `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` versus `VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT` in [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L613-L618) |

## Recurring Support Requirements

Observed gates include `fragmentStoresAndAtomics`, `VK_AMD_shader_early_and_late_fragment_tests`, `VK_KHR_depth_stencil_resolve`, `VK_KHR_maintenance5`, precise occlusion-query support, and availability of compatible transient-attachment memory types and formats. Representative checks appear in [`EarlyFragmentTest::checkSupport()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L629-L638), [`EarlyFragmentSampleMaskTest::checkSupport()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1911-L1916), [`EarlyFragmentSampleCountTest::checkSupport()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L2713-L2749), [`OcclusionQueryTest::checkSupport()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L675-L701), and [`TransientAttachmentTest::checkSupport()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L299-L329).

## Recurring Verification Methods

Observed verification approaches include:

- image comparison with [`tcu::floatThresholdCompare()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsScissorMultiViewportTests.cpp#L430-L433), [`tcu::floatThresholdCompare()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L589-L591), and [`tcu::floatThresholdCompare()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L583-L584)
- query-result verification through [`vk.getQueryPoolResults()`](../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L557-L558) followed by exact-versus-nonzero checks in [`vktFragmentOperationsOcclusionQueryTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsOcclusionQueryTests.cpp#L572-L573)
- atomic side-effect counting in shaders through `atomicAdd(sb_out.result, 1u)` in the early-fragment shaders at [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L263-L266) and [`vktFragmentOperationsEarlyFragmentTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsEarlyFragmentTests.cpp#L1061-L1063)

## Notes / Uncertainties

- [`vktFragmentOperationsTests.cpp`](../../modules/vulkan/fragment_ops/vktFragmentOperationsTests.cpp#L38-L46) is a dispatcher only and does not warrant a separate Level-3 page under the requested scope because it does not itself register a distinct user-facing subgroup below `fragment_operations`.
- The inspected evidence confirms displayed group names and high-level parameter axes, but the documentation intentionally avoids enumerating every generated leaf case under `early_fragment` because the file constructs many names programmatically across sample-count loops.
