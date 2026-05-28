# vktRenderPassSubpassDependencyTests

## Source

- [vktRenderPassSubpassDependencyTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.subpass_dependencies
├── external_subpass
├── implicit_dependencies
├── late_fragment_tests
├── self_dependency
├── separate_channels
└── single_attachment
```

Evidence:
- `subpass_dependencies` group created at [`createRenderPassSubpassDependencyTests()`](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4587)
- Direct children added from [vktRenderPassSubpassDependencyTests.cpp#L4207](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4207) through [vktRenderPassSubpassDependencyTests.cpp#L4580](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4580)

Note: `external_subpass`, `implicit_dependencies`, `late_fragment_tests`, and `self_dependency` are excluded for `RENDERING_TYPE_DYNAMIC_RENDERING`. The representative root uses `renderpass1`; the same topic group also appears under `renderpass2` and `dynamic_rendering` (with exclusions).

## Role

Implementation file

The historical Vulkan API test plan includes dependencies among multipass data-flow dimensions ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L302-L308)); current source and mustpass remain authoritative for exact behavior.

## Test Families

### external_subpass — External subpass dependency tests

Tests external subpass dependencies between render passes. Each test creates multiple render passes with explicit dependencies from `VK_SUBPASS_EXTERNAL` to subpass 0 and back.

- **Pattern**: `external_subpass/render_size_<W>_<H>/render_passes_<N>`
- **Sync2 variant**: `render_passes_<N>_sync_2` (RENDERPASS2 only)
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4207-L4305](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4207-L4305)
- Excluded for `RENDERING_TYPE_DYNAMIC_RENDERING`

### implicit_dependencies — Implicit subpass dependency tests

Tests that implementations correctly add implicit subpass dependencies. The first render pass omits all explicit dependencies; subsequent passes define only the external-to-first-subpass dependency.

- **Pattern**: `implicit_dependencies/render_passes_<N>`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4307-L4375](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4307-L4375)
- Excluded for `RENDERING_TYPE_DYNAMIC_RENDERING`

### late_fragment_tests — Late fragment tests with depth/stencil attachments

Tests late fragment operations using depth/stencil attachments in multi-pass rendering. Subpasses wait for late fragment operations before reading previous subpass contents.

- **Pattern**: `late_fragment_tests/render_size_<W>_<H>/subpass_count_<N>/<format>`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4377-L4496](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4377-L4496)
- Excluded for `RENDERING_TYPE_DYNAMIC_RENDERING`

### self_dependency — Subpass self-dependency tests

Tests subpass self-dependency using geometry shader output to indirect draw.

- **Pattern**: `self_dependency/render_size_<W>_<H>/geometry_to_indirectdraw`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4498-L4525](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4498-L4525)
- Requires `DEVICE_CORE_FEATURE_GEOMETRY_SHADER`
- Excluded for `RENDERING_TYPE_DYNAMIC_RENDERING`

### separate_channels — Separate channel read/write tests

Tests using a single attachment with reads and writes on separate channels. This should work without a subpass self-dependency.

- **Pattern**: `separate_channels/<formatName>`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4527-L4552](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4527-L4552)
- 4 format variants: r8g8b8a8_unorm, r16g16b16a16_sfloat, d24_unorm_s8_uint, d32_sfloat_s8_uint

### single_attachment — Single attachment input/output tests

Tests using a single attachment for both input and output.

- **Pattern**: `single_attachment/<formatName>`
- **Definition**: [vktRenderPassSubpassDependencyTests.cpp#L4554-L4580](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L4554-L4580)
- 5 format variants: r8g8b8a8_unorm, b8g8r8a8_unorm, r16g16b16a16_sfloat, r5g6b5_unorm_pack16, a1r5g5b5_unorm_pack16

## Parameter Dimensions

| Parameter | Values | Source |
|-----------|--------|--------|
| External subpass renderPassCounts | {2, 3, 5} | - |
| External subpass renderSizes | {(64,64), (128,128), (512,512)} | - |
| External subpass syncType | LEGACY, SYNCHRONIZATION2 | - |
| Implicit renderPassCounts | {2, 3, 5} | - |
| Late fragment renderSizes | {(32,32), (64,64), (128,128)} | - |
| Late fragment subpassCounts | {2, 3, 5} | - |
| Late fragment formats | D24_UNORM_S8_UINT, D32_SFLOAT_S8_UINT | - |
| Self dependency renderSizes | {(64,64), (128,128), (512,512)} | - |
| Separate channels formats | 4 formats | - |
| Single attachment formats | 5 formats | - |

Note: external, implicit, late fragment, and self dependency tests are excluded for DYNAMIC_RENDERING.

## Support / Feature Requirements

Defined at [vktRenderPassSubpassDependencyTests.cpp#L3924-L3975](../../../modules/vulkan/renderpass/vktRenderPassSubpassDependencyTests.cpp#L3924-L3975):

- VK_KHR_synchronization2 for SYNCHRONIZATION2
- VK_KHR_create_renderpass2 for RENDERPASS2
- VK_KHR_dynamic_rendering_local_read for DYNAMIC_RENDERING
- DEVICE_CORE_FEATURE_GEOMETRY_SHADER for self dependency

## Verification Methods

- **ExternalDependency**: tcu::floatThresholdCompare with 4.0 * min_presentable_difference
- **SubpassDependency**: verifyDepth() with subpassCount * min_representable_difference; verifyStencil() exact
- **SelfDependency**: software renderer reference + tcu::floatThresholdCompare threshold 0.01f
- **SeparateChannels**: format-dependent thresholds
- **SingleAttachment**: tcu::floatThresholdCompare threshold 0.05f against (0.3, 0.6, 0.0, 1.0)
