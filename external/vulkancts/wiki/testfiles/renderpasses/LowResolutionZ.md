## Overview

**Core question:** Does the implementation preserve correct depth behavior when render-pass depth attachments use low-resolution-Z optimization across render-pass boundaries and related depth operations?

- The `low_resolution_z` family is implemented in [vktRenderPassLowResolutionZTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp).
- It is shared across legacy render pass, render pass 2, and dynamic-rendering configurations selected by `SharedGroupParams`.
- The test compares rendered color output with the expected result after depth-direction, stencil, fragment-shader, blending, and boundary operations.

## Background Knowledge

A GPU may maintain reduced-resolution depth metadata to accelerate depth testing. Commands that alter depth state or write depth can require that metadata to be updated or invalidated. The test observes the resulting color image rather than implementation-internal metadata.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.low_resolution_z
├── direction_change
├── direction_preserve
├── blend
├── edge
├── stencil
├── fragment_shader
├── cross_renderpass
└── fuzz
```

The dispatcher instantiates the same implementation under the rendering/allocation roots permitted by `SharedGroupParams`. The fixed and fuzz groups are assembled by [createChildren](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp#L3020-L3070), and the family is created by [createRenderPassLowResolutionZTests](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp#L3068-L3072).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Depth operation | `direction_change`, `direction_preserve`, `blend`, `edge`, `stencil`, `fragment_shader`, `cross_renderpass` | Selects the depth or render-pass interaction under test. | [Test-group construction](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp#L3020-L3070) |
| Generated coverage | `fuzz` | Selects the seeded operation-combination group. | [Fuzz registration](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp#L3020-L3070) |

## Behavior Parameters

Fixed groups exercise depth-direction transitions, preservation, blending, edge behavior, stencil interaction, fragment-shader depth behavior, and cross-render-pass behavior. The source also adds a seeded fuzz group after the fixed groups.

## Shader Analysis

The `fragment_shader` behavior uses the test’s generated fragment-shader path; the other groups primarily exercise fixed-function depth, attachment, and render-pass behavior. The shader does not implement low-resolution-Z synchronization; it supplies one of the depth-writing or depth-testing operations whose result is checked by the host.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.renderpass.renderpass1.suballocation.low_resolution_z.fragment_shader
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `fragment_shader` | Selects the shader-assisted depth behavior. |
| `renderpass1.suballocation` | Selects the legacy render-pass and suballocation configuration. |

#### Purpose

The fragment shader provides the shader-side depth operation whose resulting color output is compared with the expected image.

#### Structural Design

1. The render pass binds the configured depth attachment.
2. The fragment stage performs the generated depth-related operation.
3. The test ends the render pass and compares the resulting color attachment.

#### Shader Code

The source-generated shader is configuration-dependent. The relevant generated fragment-stage shape is:

```glsl
// Generated depth/render-pass case; exact declarations depend on SharedGroupParams.
void main()
{
    // The test-specific fragment operation supplies the depth-related behavior.
}
```

#### Additional Info

- The shader does not directly update low-resolution-Z metadata.
- Other registered groups exercise fixed-function or boundary behavior without this shader-assisted path.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation group | `fragment_shader` is the representative group; other groups change the depth/render-pass operation. | [Test-group construction](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp#L3020-L3070) |
| Rendering configuration | `renderpass1.suballocation` is one permitted configuration; other `SharedGroupParams` roots reuse the family. | [Shared dispatcher registration](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8577-L8580) |

#### SPIR-V

No fixed hand-authored SPIR-V artifact is maintained for this configuration-dependent generated shader; the source builds the program through the CTS shader collection path.

- Source: `vktRenderPassLowResolutionZTests.cpp`, generated fragment program
- Stage: Fragment
- Status: Generated by CTS shader collection; no fixed artifact maintained
- Target SPIRV version: generated for the selected Vulkan test configuration

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generated from the source collection for the selected configuration.
```

</details>

## Runtime Execution and Result Checking

The test requires the features selected by each case, records the configured render sequence, and compares the resulting color attachment with the expected reference. The low-resolution-Z implementation detail is inferred from this observable depth-controlled result.

## Failure Meaning

### Failure Cause Mapping

| Failing behavior | Possible cause |
|------------------|----------------|
| Direction-change case | Incorrect depth-state transition or metadata invalidation. |
| Cross-render-pass case | Depth contents or metadata not preserved or invalidated across the boundary. |
| Stencil or fragment-shader case | Affected depth/stencil or shader-side depth path does not update depth state consistently. |
| Fuzz case | An interaction in the seeded generated combination is incorrect. |

### Cause Analysis

A color mismatch identifies an incorrect observable result, but does not alone distinguish depth metadata, synchronization, attachment transition, or shader causes. Reproduce the exact registered case and inspect the corresponding render sequence.

#### Depth metadata or boundary handling

**Possible failure symptoms:** A direction-change or cross-render-pass case produces a color mismatch while neighboring fixed groups pass.

**Possible implementation causes:** Depth contents or low-resolution metadata may not be updated or invalidated at the required state or render-pass boundary.

## Case Pruning

### Requirement-based pruning

- Leaves under `renderpass2` require `VK_KHR_create_renderpass2` and leaves under `dynamic_rendering` require `VK_KHR_dynamic_rendering`, checked against the rendering root the leaf was registered under ([rendering-root extension gates](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp#L1617-L1620)).
- Pipeline construction requirements are checked through `checkPipelineConstructionRequirements` for the `pipelineConstructionType` carried by the group parameters ([pipeline construction check](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp#L1625)).
- Steps that record into a secondary command buffer require `VK_KHR_maintenance7` ([secondary-command-buffer gate](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp#L1638-L1639)).
- Steps that blit or clear into the depth-stencil attachment need a depth-stencil format exposing the matching transfer/blit features; when neither `D24_UNORM_S8_UINT` nor `D32_SFLOAT_S8_UINT` qualifies, the case reports unsupported ([format-feature check](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp#L1641-L1655)).

### Design-based pruning

The fixed groups target named depth interactions; the seeded fuzz group expands combinations without registering every possible operation sequence as a separate hand-authored family.

## Key Takeaways

- The family checks observable depth-controlled rendering results.
- Its fixed groups cover depth direction, preservation, blending, edge, stencil, fragment-shader, and cross-render-pass behavior.
- The same implementation is shared across permitted rendering configurations.
- The fuzz group supplements, rather than replaces, the named behavioral cases.

## Source Reference Appendix

- [Test-group construction and registration](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp#L3015-L3072)
- [Low-resolution-Z test implementation](../../../modules/vulkan/renderpass/vktRenderPassLowResolutionZTests.cpp)
- [Shared dispatcher registration](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8577-L8580)
- [MUSTPASS entries](../../../mustpass/main/vk-default/renderpasses.txt)
