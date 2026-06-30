## Overview

The `geometry` test category collects tests that check Vulkan geometry-shader input handling, output emission, layered rendering,
instanced geometry execution, varying transport, and selected built-in-variable behavior.

All families share the same broad idea: a graphics pipeline inserts a geometry shader between vertex processing and rasterization,
then turns geometry-stage behavior into an observable image or side effect. The category is therefore useful for understanding both
shader-stage interface correctness and host-visible validation of geometry-shader output.

## Category Structure

```text
geometry
├── input
├── basic
├── layered
├── instanced
├── varying
├── emit
└── builtin_variable
```

The direct test families are registered by
[createChildren()](../../modules/vulkan/geometry/vktGeometryTests.cpp#L41-L52). The registration-only dispatcher page
[vktGeometryTests.md](../testfiles/geometry/vktGeometryTests.md) is preserved as obsolete source-navigation material; readers should
use the rewritten family pages below for behavior-oriented explanations.

## How the Families Fit Together

The category is organized by which part of geometry-shader behavior is being stressed:

- `input`, `basic`, and `emit` focus on geometry construction: what primitive shape the shader receives, how many vertices it emits,
  and how `EmitVertex()` / `EndPrimitive()` form output primitives.
- `varying` and `builtin_variable` focus on shader interfaces: user-defined varyings and built-in variables must cross the vertex,
  geometry, and fragment stages with the expected values.
- `layered` and `instanced` focus on geometry-shader execution context: emitted primitives can target image layers through
  `gl_Layer`, and geometry invocations can multiply with draw instancing.
- Most families validate behavior by rendering deterministic output and comparing pixels with a reference image. Some cases add
  side-effect checks, storage-image feedback, copyback paths, or layered attachment inspection when pixels alone are not enough.

Together, these families cover whether an implementation can receive geometry correctly, expand or suppress it correctly, route it
to the right destination, and preserve the shader-visible values that make the result meaningful.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `geometry.input` | [InputGeometryShaderTests.md](../testfiles/geometry/InputGeometryShaderTests.md) | Input primitive topology, adjacency handling, `gl_in` shape, and input-to-output primitive conversion. |
| `geometry.basic` | [BasicGeometryShaderTests.md](../testfiles/geometry/BasicGeometryShaderTests.md) | Fixed and runtime-varying output counts, geometry-shader instancing in output-count tests, zero-output paths, maximum-output paths, and SSBO side effects. |
| `geometry.layered` | [LayeredRenderingTests.md](../testfiles/geometry/LayeredRenderingTests.md) | `gl_Layer` routing into 1D-array, 2D-array, cube, cube-array, and 3D layered targets, including readback and secondary-command-buffer variants. |
| `geometry.instanced` | [InstancedRenderingTests.md](../testfiles/geometry/InstancedRenderingTests.md) | How draw-instance count and geometry-shader invocation count multiply to produce the expected set of rectangles. |
| `geometry.varying` | [VaryingGeometryShaderTests.md](../testfiles/geometry/VaryingGeometryShaderTests.md) | User-defined varying propagation from vertex to geometry to fragment stages when the stages produce different numbers of outputs. |
| `geometry.emit` | [EmitGeometryShaderTests.md](../testfiles/geometry/EmitGeometryShaderTests.md) | `EmitVertex()` and `EndPrimitive()` sequencing for point, line-strip, and triangle-strip geometry output. |
| `geometry.builtin_variable` | [BuiltinVariableGeometryShaderTests.md](../testfiles/geometry/BuiltinVariableGeometryShaderTests.md) | `gl_PointSize`, `gl_PrimitiveIDIn`, geometry-written `gl_PrimitiveID`, primitive restart behavior, and the HLSL `SV_POSITION` geometry path. |

## Category Notes

- Every executable family in this category depends on geometry-shader support. Individual pages describe additional feature gates
  only when they affect that family directly.
