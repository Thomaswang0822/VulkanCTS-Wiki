## Overview

**Core question:** Can externally backed images preserve their contents through sampling and transfer readback?

- This page covers `memory.opaque_and_dma`, implemented by [`vktMemoryOpaqueAndDmaImageTests.cpp`](../../../modules/vulkan/memory/vktMemoryOpaqueAndDmaImageTests.cpp).
- Four cases combine two formats with sampling and transfer consumers.

## Background Knowledge

Opaque external-memory handles represent platform-specific memory objects; DMA-BUF handles represent Linux dma-buf allocations. Both require compatible external-memory image creation and memory-property support. Unsupported combinations are skipped.

## Registration Hierarchy

```text
memory.opaque_and_dma
├── b8g8r8a8_unorm_sample
├── b8g8r8a8_unorm_transfer
├── r8g8b8a8_unorm_sample
└── r8g8b8a8_unorm_transfer
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format | `r8g8b8a8_unorm` / `b8g8r8a8_unorm` | Selects the external image format. | Source registration. |
| Consumer | `sample` / `transfer` | Selects fragment sampling or transfer readback. | Source registration. |

## Behavior Parameters

The sample consumer uses a fragment shader; the transfer consumer copies the image to a host-readable buffer and invalidates it before comparison.

## Shader Analysis

Only `sample` leaves use shaders. Transfer leaves use no shader.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.memory.opaque_and_dma.r8g8b8a8_unorm_sample
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `r8g8b8a8_unorm` | Selects the RGBA8 UNORM image format. |
| `sample` | Selects fragment-shader sampling. |

#### Purpose

The shader samples the externally backed image and writes the value for host comparison.

#### Structural Design

1. Transition the image for shader reads.
2. Sample it in a fragment invocation.
3. Write the value to the color attachment.
4. Compare the rendered result with the reference.

#### Shader Code

```glsl
#version 460
layout (location=0) out vec4 outColor;
layout (set=0, binding=0) uniform sampler2D img;
void main(void)
{
    const vec2 extent = vec2(64.0);
    const vec2 coords = gl_FragCoord.xy / extent;
    outColor = texture(img, coords);
}
```

#### Additional Info

- The source uses `gl_FragCoord.xy / extent`, where `extent` is generated from the selected image extent.
- The shader observes image contents; it does not implement external-memory synchronization.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Format | `r8g8b8a8_unorm` is the representative value; `b8g8r8a8_unorm` changes the image format. | [registration](../../../modules/vulkan/memory/vktMemoryOpaqueAndDmaImageTests.cpp#L669-L676) |
| Consumer | `sample` uses this shader; `transfer` uses host readback without shaders. | [registration](../../../modules/vulkan/memory/vktMemoryOpaqueAndDmaImageTests.cpp#L671-L676) |

#### SPIR-V

- Source: `vktMemoryOpaqueAndDmaImageTests.cpp`, `initPrograms()`
- Stage: Fragment
- Status: Validated with `glslangValidator -V` and `spirv-dis`
- Target SPIRV version: 1.0

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 24
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
```

</details>

## Runtime Execution and Result Checking

The test creates or imports the external image memory required by the selected path, initializes a reference image, and compares the observed pixels against that reference. Support checks skip unavailable external-memory, format, usage, or feature combinations.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter fails | Possible cause |
|----------------------------------|----------------|
| `sample` | External image setup, layout transition, descriptor access, shader sampling, synchronization, or output mismatch |
| `transfer` | External image setup, layout transition, copy, host visibility, invalidation, or readback mismatch |

### Cause Analysis

#### External-memory setup

**Possible failure symptoms:** The case is unsupported or fails before comparison.

**Possible implementation causes:** Incorrect handling of the required external handle, format, usage, or memory properties.

#### Content visibility

**Possible failure symptoms:** Rendered or copied pixels differ from the reference.

**Possible implementation causes:** Incorrect binding, layout, synchronization, shader access, or host invalidation.

## Case Pruning

### Requirement-based pruning

Support checks skip combinations lacking the required external-memory handle, format, usage, or feature support.

### Design-based pruning

The matrix uses two representative formats and two observation paths rather than every possible combination.

## Key Takeaways

- Four leaves cover two formats and two observation paths.
- Sampling validates shader visibility; transfer validates host readback.
- A mismatch does not by itself identify which external-memory or visibility stage failed.

## Source Reference Appendix

- [Test implementation](../../../modules/vulkan/memory/vktMemoryOpaqueAndDmaImageTests.cpp)
- [Memory test registration](../../../modules/vulkan/memory/vktMemoryTests.cpp)
- [Default MUSTPASS entries](../../../mustpass/main/vk-default/memory.txt)
