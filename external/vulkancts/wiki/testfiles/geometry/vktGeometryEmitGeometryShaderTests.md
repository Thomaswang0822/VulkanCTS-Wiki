# vktGeometryEmitGeometryShaderTests.cpp

## Overview

[`vktGeometryEmitGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L1) implements the [`emit`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L228) subgroup. It focuses on how geometry shaders behave when [`EmitVertex()`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L199) and [`EndPrimitive()`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L204) are invoked in different counts and sequences for point, line-strip, and triangle-strip outputs.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryEmitGeometryShaderTests.cpp`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L1)
- Shared base instance: [`GeometryExpanderRenderTestInstance`](../../../modules/vulkan/geometry/vktGeometryBasicClass.hpp#L37)
- Shared topology mapping helper: [`outputTypeToGLString()`](../../../modules/vulkan/geometry/vktGeometryTestsUtil.cpp#L331)

## Registration Path

This file contributes the subgroup returned by [`createEmitGeometryShaderTests()`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L226), which is attached under geometry by [`createChildren()`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L50).

## Test Hierarchy

The file registers one flat subgroup:

```text
emit
├── points_emit_0_end_0
├── points_emit_0_end_1
├── points_emit_1_end_1
├── points_emit_0_end_2
├── points_emit_1_end_2
├── line_strip_emit_0_end_0
├── line_strip_emit_0_end_1
├── line_strip_emit_1_end_1
├── line_strip_emit_2_end_1
├── line_strip_emit_0_end_2
├── line_strip_emit_1_end_2
├── line_strip_emit_2_end_2
├── line_strip_emit_2_end_2_emit_2_end_0
├── triangle_strip_emit_0_end_0
├── triangle_strip_emit_0_end_1
├── triangle_strip_emit_1_end_1
├── triangle_strip_emit_2_end_1
├── triangle_strip_emit_3_end_1
├── triangle_strip_emit_0_end_2
├── triangle_strip_emit_1_end_2
├── triangle_strip_emit_2_end_2
├── triangle_strip_emit_3_end_2
└── triangle_strip_emit_3_end_2_emit_3_end_0
```

Names are synthesized from [`EmitTestSpec`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L71) values in [`createEmitGeometryShaderTests()`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L232) and the name-building logic at [`emitTests[ndx].name = ...`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L261).

## Test Families

### 1. Point output emit/end sequences

Point-output cases use [`VK_PRIMITIVE_TOPOLOGY_POINT_LIST`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L233) and vary how many vertices are emitted before zero, one, or two [`EndPrimitive()`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L204) calls.

### 2. Line-strip output emit/end sequences

Line-output cases use [`VK_PRIMITIVE_TOPOLOGY_LINE_STRIP`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L238) and include both single-segment and two-segment sequences such as [`line_strip_emit_2_end_2_emit_2_end_0`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L245).

### 3. Triangle-strip output emit/end sequences

Triangle-output cases use [`VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L246) and extend the emit-count range to 3 vertices per segment, including two-segment cases such as [`triangle_strip_emit_3_end_2_emit_3_end_0`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L255).

### 4. Two-segment sequences

Some cases intentionally split output into A/B segments through [`emitCountA`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L74), [`endCountA`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L75), [`emitCountB`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L76), and [`endCountB`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L77). These are encoded by the second name suffix added when [`emitCountB`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L267) is nonzero.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Output topology | [`VK_PRIMITIVE_TOPOLOGY_POINT_LIST`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L233), [`VK_PRIMITIVE_TOPOLOGY_LINE_STRIP`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L238), [`VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L246) |
| Segment A emit count | 0..3 depending on topology in [`emitTests[]`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L232) |
| Segment A end count | 0..2 in [`emitTests[]`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L232) |
| Segment B emit count | 0, 2, or 3 in the two-segment cases at [`emitTests[]`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L245) and [`emitTests[]`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L255) |
| Segment B end count | 0 in the observed two-segment cases at [`emitTests[]`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L245) and [`emitTests[]`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L255) |
| Optional point-size path | Additional geometry program when topology is point list at [`geometry_pointsize`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L149) |

## Support / Feature Requirements

Support checking is explicit in [`EmitTest::checkSupport()`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L126), which requires [`DEVICE_CORE_FEATURE_GEOMETRY_SHADER`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L128).

## Verification Methods

This file does not define a file-local CPU-side verifier in the inspected range. It relies on the shared geometry render-test path through [`GeometryEmitTestInstance`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L82), which derives from [`GeometryExpanderRenderTestInstance`](../../../modules/vulkan/geometry/vktGeometryBasicClass.hpp#L37).

Within the inspected code, observability is driven by the generated geometry shader in [`shaderGeometry()`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L171), which:
- places output vertices at fixed positions [`position0`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L185) through [`position5`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L190)
- preserves primitive ID with [`gl_PrimitiveID = gl_PrimitiveIDIn`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L197)
- forwards color through [`v_frag_FragColor = v_geom_FragColor[0]`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L198)

Given the shared render-test dependency, this document limits itself to the evidence visible in the file rather than asserting a more specific comparison helper.

## Test Principles Observed

- **Emit/end sequencing is data-driven**: cases are represented as [`EmitTestSpec`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L71) data rather than separate hand-written tests
- **Topology-sensitive coverage**: output topology changes how far emit counts are explored, with triangle-strip reaching higher counts than point and line output
- **Single-segment and two-segment behavior**: the file checks both isolated and split primitive streams
- **Name generation mirrors semantics**: case names directly encode emit/end counts, making the registration tree descriptive of the tested sequence

## Notes / Uncertainties

- Verification is delegated to the shared geometry render-test path, but the exact base-class comparison implementation was not part of the inspected snippet set.
- The file contains a [`desc`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L79) field and builds descriptions at [`emitTests[ndx].desc = ...`](../../../modules/vulkan/geometry/vktGeometryEmitGeometryShaderTests.cpp#L263), but those descriptions are not otherwise consumed in the inspected range.
