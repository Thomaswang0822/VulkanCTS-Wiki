# Discard Query Tests

Tests for occlusion-query behavior under fragment discard-related conditions in `query_pool`. This page documents the `discard` Level-3 group registered from [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:54) and implemented in [`vktQueryPoolDiscardTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp).

## Source

- [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)
- [`vktQueryPoolDiscardTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp)
- [`vktQueryPoolDiscardTests.hpp`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.hpp)

## Registration

| Item | Value |
|------|-------|
| Top-level parent | `query_pool` via [`createTests()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:59) |
| Level-3 group name | `discard` via [`createDiscardTests()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:533) |
| Child registration | [`queryPoolTests->addChild(createDiscardTests(testCtx))`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:54) |
| Group population | [`createDiscardTests()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:533) |
| Vulkan SC split | The top-level `discard` group exists in both Vulkan and Vulkan SC, but one discard subtype is compiled out in SC builds via [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:546) |

## Summary

The `discard` group validates precise and non-precise occlusion-query behavior when fragment visibility is reduced by shader `discard`, by zeroing the sample mask, or by alpha-to-coverage. It also checks the interaction of those mechanisms with early fragment tests and optional depth testing. All cases render a `32 x 32` image, verify the exact black/white stripe pattern produced by the fragment shader, and then compare the occlusion-query result against either an exact expected sample count or a weaker non-zero requirement depending on whether `VK_QUERY_CONTROL_PRECISE_BIT` is enabled.

## Test Hierarchy

```text
query_pool
└── discard
    ├── normal
    │   ├── no_depth
    │   │   ├── none
    │   │   │   ├── discard
    │   │   │   ├── sample_mask
    │   │   │   ├── alpha_to_coverage
    │   │   │   └── alpha_to_coverage_dynamic    (non-SC only)
    │   │   └── precise
    │   │       ├── discard
    │   │       ├── sample_mask
    │   │       ├── alpha_to_coverage
    │   │       └── alpha_to_coverage_dynamic    (non-SC only)
    │   └── with_depth
    │       ├── none
    │       │   ├── discard
    │       │   ├── sample_mask
    │       │   ├── alpha_to_coverage
    │       │   └── alpha_to_coverage_dynamic    (non-SC only)
    │       └── precise
    │           ├── discard
    │           ├── sample_mask
    │           ├── alpha_to_coverage
    │           └── alpha_to_coverage_dynamic    (non-SC only)
    └── early
        ├── no_depth
        │   ├── none
        │   │   ├── discard
        │   │   ├── sample_mask
        │   │   ├── alpha_to_coverage
        │   │   └── alpha_to_coverage_dynamic    (non-SC only)
        │   └── precise
        │       ├── discard
        │       ├── sample_mask
        │       ├── alpha_to_coverage
        │       └── alpha_to_coverage_dynamic    (non-SC only)
        └── with_depth
            ├── none
            │   ├── discard
            │   ├── sample_mask
            │   ├── alpha_to_coverage
            │   └── alpha_to_coverage_dynamic    (non-SC only)
            └── precise
                ├── discard
                ├── sample_mask
                ├── alpha_to_coverage
                └── alpha_to_coverage_dynamic    (non-SC only)
```

The nested hierarchy is built by the three boolean loops and the discard-type loop in [`createDiscardTests()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:551).

## Registered Families

### Early-fragment-test split

The first registration axis is `earlyFragmentTests`, producing the exact group names:

| Boolean | Group name | Meaning |
|---------|------------|---------|
| `false` | `normal` | Fragment shader runs without `layout(early_fragment_tests)` |
| `true` | `early` | Fragment shader includes `layout(early_fragment_tests) in;` in [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:511) |

The group naming is defined by [`earlyFragmentName`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:553).

### Depth-use split

Inside each early-fragment branch, the second axis is `useDepth`:

| Boolean | Group name | Meaning |
|---------|------------|---------|
| `false` | `no_depth` | Depth testing and writes are disabled in [`createPipeline()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:303) |
| `true` | `with_depth` | Depth testing and writes are enabled in [`createPipeline()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:303) |

### Query-precision split

Inside each depth branch, the third axis is `precise`:

| Boolean | Group name | Query flags |
|---------|------------|-------------|
| `false` | `none` | No query control flags |
| `true` | `precise` | `VK_QUERY_CONTROL_PRECISE_BIT` |

The flag selection happens in [`QueryPoolDiscardTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:366).

### Discard-type split

Each precision group contains one leaf case per discard mechanism listed in [`discardTypes`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:538):

| Enum | Leaf name | Mechanism |
|------|-----------|-----------|
| `DiscardType::DISCARD` | `discard` | Fragment shader executes `discard;` on even `x` coordinates |
| `DiscardType::SAMPLE_MASK` | `sample_mask` | Fragment shader writes `gl_SampleMask[0] = 0;` on even `x` coordinates |
| `DiscardType::ALPHA_TO_COVERAGE` | `alpha_to_coverage` | Fragment shader writes alpha `0.0` on even `x` coordinates while alpha-to-coverage is enabled |
| `DiscardType::ALPHA_TO_COVERAGE_DYNAMIC` | `alpha_to_coverage_dynamic` | Same alpha-based behavior, but enable is set dynamically with [`cmdSetAlphaToCoverageEnableEXT()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:378) |

The dynamic alpha-to-coverage leaf is registered only in non-SC builds because it is enclosed by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:546).

## Parameter Dimensions

The file generates the Cartesian product of four axes:

| Dimension | Values | Registration source |
|-----------|--------|---------------------|
| Early-fragment mode | `normal`, `early` | [`earlyFragmentTest`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:551) |
| Depth mode | `no_depth`, `with_depth` | [`depth`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:556) |
| Query precision | `none`, `precise` | [`precise`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:560) |
| Discard mechanism | `discard`, `sample_mask`, `alpha_to_coverage`, plus `alpha_to_coverage_dynamic` in non-SC builds | [`discardTypes`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:538) |

This produces:

- `2 x 2 x 2 x 4 = 32` leaf cases in non-SC builds; and
- `2 x 2 x 2 x 3 = 24` leaf cases in Vulkan SC builds.

### Fixed rendering configuration

All generated cases share the same base rendering setup:

| Parameter | Value | Source |
|-----------|-------|--------|
| Query type | `VK_QUERY_TYPE_OCCLUSION` | [`VkQueryPoolCreateInfo`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:344) |
| Image size | `32 x 32` | [`m_imageSize`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:71) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` | [`m_colorFormat`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:72) |
| Depth format | `VK_FORMAT_D16_UNORM` | [`m_depthFormat`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:73) |
| Primitive topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` | [`makeGraphicsPipeline()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:325) |
| Draw call | [`vk.cmdDraw()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:381) with vertex count `4` |

## Support Requirements

Support checking is implemented in [`QueryPoolDiscardTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:477).

| Requirement | Needed for | Source |
|------------|------------|--------|
| `occlusionQueryPrecise` feature | All `*/precise/*` cases | [`QueryPoolDiscardTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:487) |
| `extendedDynamicState3AlphaToCoverageEnable` feature | `alpha_to_coverage_dynamic` cases | [`QueryPoolDiscardTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:482) |
| `earlyFragmentSampleMaskTestBeforeSampleCounting` maintenance5 property | All `early/*/*/*` cases | [`QueryPoolDiscardTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:489) |
| `earlyFragmentMultisampleCoverageAfterSampleCounting` maintenance5 property | `early/*/*/alpha_to_coverage` and `early/*/*/alpha_to_coverage_dynamic` cases | [`QueryPoolDiscardTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:493) |

### Vulkan SC behavior

Two Vulkan-SC-relevant behaviors are explicit in the source:

- `alpha_to_coverage_dynamic` is not compiled or registered in SC builds because both its registration and dynamic-state setup are inside `#ifndef CTS_USES_VULKANSC`; see [`vktQueryPoolDiscardTests.cpp:315`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:315) and [`vktQueryPoolDiscardTests.cpp:546`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:546).
- The rest of the hierarchy is shared across Vulkan and Vulkan SC, so exact path names for `normal`, `early`, `no_depth`, `with_depth`, `none`, `precise`, `discard`, `sample_mask`, and `alpha_to_coverage` remain unchanged.

## Verification Methods

### Query-result verification

The test reads one 32-bit occlusion result after submission with [`getQueryPoolResults()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:408). Expected behavior depends on the precision mode.

#### Precise-query cases

For `*/precise/*` cases, [`QueryPoolDiscardTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:411) computes an exact expected result:

| Condition | Effect on expected result |
|-----------|---------------------------|
| Base image area | Start from `32 x 32 = 1024` |
| `normal` branch | Divide by `2` because half the columns are discarded / masked / suppressed |
| `early` branch | Do not divide, because the maintenance5 property being tested means sample-mask evaluation happens before sample counting |
| Any alpha-to-coverage branch | Multiply by `4` because the render pass switches to `VK_SAMPLE_COUNT_4_BIT` in [`createRenderPass()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:148) |

Concretely, the exact expected values are:

| Branch shape | Expected count |
|--------------|----------------|
| `normal/*/precise/discard` or `sample_mask` | `512` |
| `early/*/precise/discard` or `sample_mask` | `1024` |
| `normal/*/precise/alpha_to_coverage*` | `2048` |
| `early/*/precise/alpha_to_coverage*` | `4096` |

Here `alpha_to_coverage*` means `alpha_to_coverage` and, in non-SC builds, `alpha_to_coverage_dynamic`.

#### Non-precise-query cases

For `*/none/*` cases, the verification rule is intentionally weaker: the returned occlusion result must be non-zero. This is enforced in [`QueryPoolDiscardTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:426).

### Rendered-image verification

The test also copies the color image to a host-visible buffer and checks every pixel. The expected pattern is defined in [`QueryPoolDiscardTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:439):

| Pixel `x` parity | Expected color |
|------------------|----------------|
| Even `x` | black `vec4(0.0)` |
| Odd `x` | white `vec4(1.0)` |

This per-pixel image check ensures that the fragment-control mechanism actually affected the intended half of the framebuffer rather than merely producing a matching query count by accident.

## Rendering and Shader Notes

### Shader behavior

[`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:499) generates a simple full-screen strip:

- the vertex shader derives clip-space positions from `gl_VertexIndex`, producing a quad from four vertices;
- the fragment shader always initializes `gl_SampleMask[0] = ~0` and writes white;
- on even `gl_FragCoord.x`, it either discards, zeroes the sample mask, or writes alpha `0.0` depending on the registered discard type.

### MSAA and alpha-to-coverage path

For alpha-to-coverage variants, [`TestParameters::isAlphaToCoverage()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:63) causes the render setup to change in multiple places:

- a 4x MSAA color image is allocated in [`createRenderPass()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:148);
- the depth image also uses 4x samples in [`createRenderPass()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:158);
- the render pass adds a multisampled color attachment plus resolve attachment in [`createRenderPass()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:193);
- the pipeline multisample state uses `VK_SAMPLE_COUNT_4_BIT` and enables alpha-to-coverage in [`createPipeline()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:281).

For the dynamic variant, alpha-to-coverage is additionally toggled through [`VK_DYNAMIC_STATE_ALPHA_TO_COVERAGE_ENABLE_EXT`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:316).

## Notes

- All cases are `TestCase`-based and use the same execution class, [`QueryPoolDiscardTestInstance`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:69), with behavior driven entirely by `TestParameters`.
- The exact subgroup name `none` is important: it denotes absence of query control flags, not failure or unsupported behavior.
- The page documents the precise registration harness from [`createDiscardTests()`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp:533) and does not create or modify any broader Level-2 query-pool category page.
- This page documents only the Level-3 file represented by [`vktQueryPoolDiscardTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp).
