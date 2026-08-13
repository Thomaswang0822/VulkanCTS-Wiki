## Overview

The `tessellation` test category collects tests that check Vulkan tessellation limits, primitive generation, shader interfaces, and interactions with drawing and geometry processing.

## Background Knowledge

- **Tessellation pipeline.** A tessellation control shader runs once per output control point of a patch, writes per-vertex and per-patch data, and selects inner and outer tessellation levels. The fixed-function primitive generator subdivides the patch. A tessellation evaluation shader runs for generated coordinates and produces vertices for rasterization or a later geometry stage.
- **Primitive domains and spacing.** Triangle, quad, and isoline domains interpret tessellation coordinates and levels differently. Equal, fractional-even, and fractional-odd spacing select segment counts and placement. Winding, point mode, and domain origin further control generated primitives.
- **Patch interfaces and invocations.** Tessellation shaders exchange both per-control-point arrays and data shared by the whole patch. Control-shader invocations can communicate through outputs when barriers establish the required ordering. Geometry shaders can then amplify, route, or resize tessellated primitives.

## Category Structure

```text
tessellation
├── limits
├── tesscoord
├── winding
├── shader_input_output
├── misc_draw
├── common_edge
├── fractional_spacing
├── primitive_discard
├── invariance
├── user_defined_io
├── geometry_interaction
├── tess_io
└── matrix_multiplication
```

The registration-only category dispatcher also assembles four children below `geometry_interaction`: `passthrough`, `limits`, `scatter`, and `point_size`. They are documented in separate Level-3 pages.

## How the Families Fit Together

- **Capability and primitive-generation families** cover required limits, generated coordinates, spacing, winding, discard behavior, common edges, and invariance rules.
- **Shader-interface families** cover built-ins, user-defined per-vertex and per-patch data, maximum IO configurations, barriers, and control-shader matrix operations.
- **Draw and geometry-interaction families** put tessellation into complete graphics pipelines, including indirect or instanced draws and geometry-stage passthrough, amplification, layer routing, and point-size propagation.
- Each family selects an oracle suited to the contract: property bounds, exact or tolerant data comparison, primitive-set comparison, or framebuffer analysis.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `limits` | [Limits](../testfiles/tessellation/Limits.md) | Required tessellation feature and device-limit checks. |
| `tesscoord` | [Coordinates](../testfiles/tessellation/Coordinates.md) | Reference generation and comparison of tessellation-coordinate sets. |
| `winding` | [Winding](../testfiles/tessellation/Winding.md) | Winding, domain-origin, viewport-flip, and shader-language cases. |
| `shader_input_output` | [Shader Input and Output](../testfiles/tessellation/ShaderInputOutput.md) | Patch sizes, built-ins, stage interfaces, barriers, and cross-invocation values. |
| `misc_draw` | [Miscellaneous Draw](../testfiles/tessellation/MiscDraw.md) | Draw commands, instancing, state changes, no-patch behavior, and the barrier regression. |
| `common_edge` | [Common Edge](../testfiles/tessellation/CommonEdge.md) | Continuity along shared edges across primitive and spacing modes. |
| `fractional_spacing` | [Fractional Spacing](../testfiles/tessellation/FractionalSpacing.md) | Fractional-even and fractional-odd segment rules. |
| `primitive_discard` | [Primitive Discard](../testfiles/tessellation/PrimitiveDiscard.md) | Patch discard when relevant outer tessellation levels are non-positive. |
| `invariance` | [Invariance](../testfiles/tessellation/Invariance.md) | Primitive, edge, triangle-set, and coordinate invariance guarantees. |
| `user_defined_io` | [User-Defined IO](../testfiles/tessellation/UserDefinedIO.md) | Per-vertex, per-patch, array, and interface-block transport. |
| `geometry_interaction.passthrough` | [Geometry Passthrough](../testfiles/tessellation/GeometryPassthrough.md) | Identity behavior across tessellation and geometry stages. |
| `geometry_interaction.limits` | [Geometry Limits](../testfiles/tessellation/GeometryLimits.md) | Required-value tessellation and geometry amplification workloads. |
| `geometry_interaction.scatter` | [Geometry Scatter](../testfiles/tessellation/GeometryScatter.md) | Geometry instances, primitives, and layer routing. |
| `geometry_interaction.point_size` | [Geometry Point Size](../testfiles/tessellation/GeometryPointSize.md) | Point-size values written and transformed across shader stages. |
| `tess_io` | [Maximum IO](../testfiles/tessellation/MaxIO.md) | Maximum tessellation-stage interfaces and tessellation-level IO. |
| `matrix_multiplication` | [Matrix Multiplication](../testfiles/tessellation/MatrixMultiplication.md) | Tessellation-control matrix multiplication and framebuffer validation. |
