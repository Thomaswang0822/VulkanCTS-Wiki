## Overview

**Core question:** Do YCbCr multi-planar images behave correctly when their compatible planes are used as color attachments?

- This page covers `ycbcr.render_attachment`, implemented in `vktYCbCrRenderAttachmentTests.cpp`.
- The family covers two-plane and three-plane 420, 422, and 444 formats in joint and disjoint memory modes.
- Each case selects a plane-compatible image view and checks the rendered plane contents.

## Background Knowledge

For shared multi-planar image, plane-view, and disjoint-memory concepts, see [Background Knowledge](../../categories/ycbcr.md#background-knowledge) of the `ycbcr` page.

- A plane-compatible view exposes one plane of a multi-planar image using its compatible single-plane format.
- Joint images use one allocation; disjoint images bind each plane separately while retaining one logical image.
- A color-attachment view must use an aspect and format compatible with the selected plane.

## Registration Hierarchy

```text
ycbcr.render_attachment
├── g8_b8_r8_3plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── g8_b8r8_2plane_420_unorm
└── g8_b8r8_2plane_422_unorm
```

Each format expands to joint/disjoint binding variants and one leaf per applicable plane.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Format | `g8_b8_r8_3plane_420_unorm`, `g8_b8_r8_3plane_422_unorm`, `g8_b8_r8_3plane_444_unorm`, `g8_b8r8_2plane_420_unorm`, `g8_b8r8_2plane_422_unorm` | Selects plane count and chroma subsampling. | [`vktYCbCrRenderAttachmentTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrRenderAttachmentTests.cpp) |
| Binding mode | `joint`, `disjoint` | Selects shared or per-plane memory binding. | [`createRenderAttachmentTests`](../../../modules/vulkan/ycbcr/vktYCbCrRenderAttachmentTests.cpp) |
| Plane | `plane0`, `plane1`, `plane2` | Selects the compatible attachment format and aspect. | [`RenderAttachmentTestInstance`](../../../modules/vulkan/ycbcr/vktYCbCrRenderAttachmentTests.cpp) |

## Behavior Parameters

The primary behavioral axis is the selected plane, with binding mode determining whether the image uses joint or disjoint memory.

### Plane attachment

The test creates a multi-planar image, creates a compatible plane view, renders to that view, and verifies the selected plane. Three-plane formats expose three plane leaves; two-plane formats expose two.

### Joint and disjoint binding

Joint cases bind one allocation for the image. Disjoint cases obtain and bind plane-specific memory requirements. Both modes use the same render and readback contract.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.ycbcr.render_attachment.r8g8b8a8_unorm.plane0.joint
```

| Parameter choice | Meaning in this representative case |
|---|---|
| Plane | `plane0` |
| Binding | `joint` |

#### Purpose

The shader writes a deterministic color to the selected plane-compatible attachment so the host can compare the result.

#### Structural Design

- Vertex stage draws a fullscreen triangle.
- Fragment stage writes the test color.
- Host code creates the multi-planar image and plane view.

#### Shader Code

```glsl
#version 450
layout(location = 0) out vec4 outColor;
void main(void) { outColor = vec4(1.0); }
```

#### Additional Info

- The shader does not select the plane; the image view and attachment aspect do.
- Joint and disjoint cases share the shader and differ in memory binding.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Plane | `plane0`, `plane1`, `plane2` | Host selects the compatible plane view. [`createRenderAttachmentTests`](../../../modules/vulkan/ycbcr/vktYCbCrRenderAttachmentTests.cpp#L415-L478) |
| Binding mode | `joint`, `disjoint` | Host selects image allocation strategy. [`RenderAttachmentTestInstance`](../../../modules/vulkan/ycbcr/vktYCbCrRenderAttachmentTests.cpp#L90-L150) |

#### SPIR-V

- Status: reconstructed from the source shader setup
- Source: `vktYCbCrRenderAttachmentTests.cpp`
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End
; Fragment shader writes the deterministic attachment color.
```

</details>

## Runtime Execution and Result Checking

The test creates the image and view, builds a render pass and framebuffer, records and submits a draw, and reads back the selected plane. Support checks prune unsupported format, usage, and plane combinations.

## Failure Meaning

### Failure Cause Mapping

| Failing behavior | Possible cause |
|---|---|
| Image or view creation fails | Incorrect plane-compatible format or unsupported usage. |
| Disjoint case fails | Incorrect per-plane memory requirement or binding handling. |
| Plane comparison fails | Incorrect aspect selection, layout transition, or color write. |

### Cause Analysis

#### Plane-compatible render attachment

**Possible failure symptoms:** Image creation, plane binding, rendering, or selected-plane comparison fails.

**Possible implementation causes:** The implementation may mishandle multi-planar attachment compatibility, plane aspects, disjoint bindings, or layout transitions. The exact lower-level cause requires implementation investigation.

## Case Pruning

### Requirement-based pruning

Cases are skipped when the format, compatible plane view, color-attachment usage, or required Vulkan SC support is unavailable. Such skips are capability filtering, not conformance failures.

### Design-based pruning

The matrix keeps distinct plane and binding combinations; unsupported duplicate combinations are not executed.

## Key Takeaways

- `render_attachment` adds render-target coverage for YCbCr plane-compatible views.
- The matrix varies plane count, subsampling, joint/disjoint binding, and plane aspect.
- The Vulkan SC mustpass contains 26 leaves for this family.

## Source Reference Appendix

- [`vktYCbCrRenderAttachmentTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrRenderAttachmentTests.cpp)
- [`ycbcr.txt`](../../../mustpass/main/vksc-default/ycbcr.txt)
