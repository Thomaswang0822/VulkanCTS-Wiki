# Understanding Brief: Shader Object Tessellation Tests

## One-Sentence Test Purpose

This test checks whether independently created and bound tessellation shader objects apply their SPIR-V execution modes, including after a temporary stage rebind, and produce the expected rasterized pattern.

## Background Knowledge

### Tessellation execution modes

A patch passes through a tessellation control shader, the fixed-function tessellator, and a tessellation evaluation shader. The control shader writes inner and outer tessellation levels. The tessellator subdivides the patch according to those levels and the execution modes declared by the tessellation shaders. The evaluation shader converts each generated tessellation coordinate into a clip-space position.

Why it matters here:

- `Quads` or `Triangles` selects the parameter domain and generated primitive topology.
- `SpacingEqual` or `SpacingFractionalOdd` changes the edge subdivision pattern.
- `VertexOrderCcw`, `VertexOrderCw`, and `PointMode` change which primitives survive culling or how they rasterize.
- `OutputVertices` sets the tessellation control output patch size. The evaluation shader reads that size through `PatchVertices`.

The Vulkan tessellation rules require a shader-object pair to place the primitive type and triangle orientation in at least the tessellation evaluation shader, and to place `OutputVertices` in at least the tessellation control shader. Modes declared by both stages must agree ([tessellation execution modes](../../../../vulkan-docs/src/chapters/tessellation.adoc#L34-L109)).

### Independent shader-object binding

A shader object represents one stage and can be rebound without rebuilding a graphics pipeline. `vkCmdBindShadersEXT` changes only the listed stages. Shader-object draws also rely on dynamic state, including patch control-point count when a tessellation control shader is bound for patch-list drawing ([shader-object binding and state](../../../../vulkan-docs/src/chapters/shaders.adoc#L912-L1050)).

Why it matters here:

- The test binds vertex, tessellation control, tessellation evaluation, and fragment shader objects as one graphics chain.
- A `_rebind` case briefly replaces one tessellation stage with an intentionally different shader object and then restores the original before the draw.
- The rendered result must come from the restored binding, not the temporary one.

## One Concrete Example

Consider `dEQP-VK.shader_object.tessellation.glsl.spacing_fractional_odd_rebind`.

1. The selected tessellation control object declares `OutputVertices 4`, writes all inner and outer tessellation levels as `2.0`, and copies the four input control-point positions.
2. The selected tessellation evaluation object declares `Quads`, `SpacingFractionalOdd`, and `VertexOrderCcw`. It bilinearly interpolates the four control points.
3. The host first binds the selected control and evaluation objects. It then binds a temporary control object whose extra modes describe the opposite primitive, spacing, orientation, and point-mode choices, and immediately restores the selected control object.
4. A four-vertex patch is drawn in line polygon mode. The host expects the 17x17 `fractionalOdd` mask, offset by seven pixels in each axis, to contain white exactly where the generated lines rasterize.

The temporary object must not affect the draw. A stale temporary binding would select modes that disagree with the selected evaluation shader or change the tessellation pattern.

## End-to-End Test Flow

```text
[host] choose source-language placement, tessellation behavior, and rebind flag
[host] construct direct SPIR-V for vertex, control, evaluation, and fragment stages
[host] create one shader object per stage and optional temporary control/evaluation objects
[host] create a 32x32 color image and a host-visible image-copy buffer
[host] transition the image, bind the four graphics shader objects, and set dynamic state
[host] for a rebind case, bind the temporary tessellation object and then restore the selected object
[host] begin dynamic rendering and draw one patch of four or five vertices
[device] run vertex shading, tessellation control, fixed-function tessellation, tessellation evaluation, line/point rasterization, and fragment shading
[device] write white fragments over a black clear color
[host] barrier and copy the image to the host-visible buffer, then submit and wait
[host] compare a 17x17 region against the behavior-specific binary mask
[host] fail on the first pixel whose exact RGBA value differs; otherwise pass
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms()` builds SPIR-V assembly directly rather than generating GLSL or HLSL source. The source-language dimension controls where execution modes are placed:

- `glsl`: `OutputVertices` is on the control stage; primitive, spacing, orientation, and optional `PointMode` are on the evaluation stage.
- `hlsl`: the selected control stage also carries primitive, spacing, orientation, and optional `PointMode`; the selected evaluation stage carries the primitive mode. The mode placement models the different stage placement produced by the HLSL route while keeping the executable artifact as SPIR-V assembly.
- `_rebind`: adds temporary control and evaluation artifacts with opposite execution-mode choices. The runtime binds and restores the control stage for `glsl`, and the evaluation stage for `hlsl`.

The shaders use no descriptors, push constants, specialization constants, or stage user variables. All communication uses tessellation built-ins and `gl_Position`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Four or six `VkShaderEXT` objects | yes | yes | executed by device | no | Supply the selected stage chain and, for `_rebind`, the temporary control/evaluation alternatives. |
| 32x32 `R8G8B8A8_UNORM` image | yes | yes, as color attachment and copy source | fragment output writes it | indirectly | Holds the black-and-white tessellation pattern. |
| Host-visible color output buffer | yes | yes, as transfer destination | transfer writes it | yes | Carries the final image bytes to the CPU pixel check. |
| Tessellation levels and per-vertex patch data | no | shader-stage built-ins | control writes; tessellator/evaluation read | no | Control subdivision and control-point interpolation without descriptor resources. |

## What Is Checked

- The host checks the 17x17 window at image coordinates `(7..23, 7..23)`. `patch_vertices_5` shifts the checked y coordinate down by five pixels because the evaluation shader adds `0.3` to y when its input patch has more than four vertices.
- `spacing_fractional_odd`, `primitive_triangles`, and `point_mode` each have a dedicated expected mask. `orientation_cw` expects every checked pixel to stay black because back-face culling removes the clockwise output. All other cases use the `basic` mask.
- A set mask cell must equal `(1,1,1,1)` and an unset cell must equal `(0,0,0,1)`. The comparison has no tolerance.
- Every base and `_rebind` leaf uses the same check for its behavior. The rebind suffix changes only the binding sequence, so paired leaves must render the same mask.

## Behavior Parameter Identification

> **Behavior parameter:** `test case behavior before the optional _rebind suffix`
>
> **Candidate values:** `orientation_ccw`, `orientation_cw`, `spacing_equal`, `spacing_fractional_odd`, `patch_vertices_4`, `patch_vertices_5`, `primitive_quads`, `primitive_triangles`, `point_mode`

The source type and `_rebind` suffix are secondary dimensions. They change execution-mode placement and binding history while preserving the selected behavior's expected output.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `orientation_ccw` | Counter-clockwise tessellator winding, front-face interpretation, back-face culling, or execution-mode placement produced the wrong visible edges. |
| `orientation_cw` | Clockwise tessellated triangles were not culled as expected, or the orientation mode was ignored or read from the wrong shader object. |
| `spacing_equal` | Equal-spacing edge subdivision or its shader-object execution mode produced the wrong line pattern. |
| `spacing_fractional_odd` | Fractional-odd edge subdivision or its shader-object execution mode produced the wrong line pattern. |
| `patch_vertices_4` | Dynamic input patch size, four-vertex control output, or evaluation-stage `PatchVertices` handling produced the wrong base pattern. |
| `patch_vertices_5` | Five-control-point input/output handling or the `PatchVertices > 4` y-offset branch failed. |
| `primitive_quads` | Quad-domain tessellation or bilinear evaluation produced the wrong base pattern. |
| `primitive_triangles` | Triangle-domain tessellation, coordinate interpretation, or evaluation of the available control points produced the wrong triangular pattern. |
| `point_mode` | `PointMode` did not convert tessellator output to the expected sparse point pattern. |

Any `_rebind` failure also points to stage-binding persistence: the temporary control object in `glsl` or temporary evaluation object in `hlsl` may have remained active after the selected object was restored. A failure shared by both source types can also come from common drawing, rasterization, image synchronization, copyback, or exact pixel comparison paths.

## Important Variations and Special Cases

- The `glsl` and `hlsl` names describe execution-mode placement in the direct SPIR-V artifacts, not runtime compilation from source text. The shader bodies stay the same.
- The control shader always writes tessellation levels of `2.0`. This makes equal and fractional-odd spacing generate different observable masks at a small fixed patch size.
- `patch_vertices_4` and `patch_vertices_5` both set the dynamic input patch count to five and draw five vertices. Their control-stage `OutputVertices` modes differ: four for `patch_vertices_4`, five for `patch_vertices_5`. The evaluation shader shifts output only when the control output patch size exceeds four.
- The runtime uses `VK_POLYGON_MODE_LINE` to expose tessellated edges. `point_mode` overrides triangle or line generation with points.
- Rebind artifacts deliberately use opposite modes, but the test never draws while they are bound. Their purpose is to disturb the stage binding state before restoring the selected shader.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Runtime resources, binding, draw, and copyback | [ShaderObjectTessellationInstance::iterate](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L87-L258) | Creates shader objects and image resources, performs optional rebind, draws, and copies the result. |
| Expected masks and exact pixel check | [mask tables and validation loop](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L260-L384) | Defines the observable result for all nine behaviors. |
| Support requirements | [ShaderObjectTessellationCase::checkSupport](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L415-L420) | Requires `VK_EXT_shader_object` and tessellation shader support. |
| Execution-mode selection | [initPrograms mode branches](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L422-L485) | Chooses selected and temporary tessellation execution modes. |
| Control shader artifact | [control SPIR-V construction](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L558-L703) | Writes tessellation levels and copies control points. |
| Evaluation shader artifact | [evaluation SPIR-V construction](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L705-L878) | Interpolates patch positions and applies the five-vertex offset. |
| Artifact insertion | [program collection](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L909-L924) | Adds the direct SPIR-V stages and optional rebind artifacts. |
| Registration matrix | [createShaderObjectTessellationTests](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L929-L975) | Registers 36 leaves across source type, behavior, and rebind dimensions. |
| Mustpass paths | [tessellation.txt](../../../mustpass/main/vk-default/shader-object/tessellation.txt) | Lists all 36 executable default-mustpass paths. |
| Tessellator semantics | [tessellation.adoc](../../../../vulkan-docs/src/chapters/tessellation.adoc#L7-L109) | Defines stage flow and execution-mode ownership for shader objects. |
| Patch vertex built-in | [interfaces.adoc](../../../../vulkan-docs/src/chapters/interfaces.adoc#L4024-L4055) | Defines `PatchVertices` for control and evaluation stages. |

## Questions / Risk Points for User Audit

- Is it clear that `glsl` and `hlsl` select execution-mode placement in direct SPIR-V rather than a GLSL or HLSL source compiler path?
- Does the `patch_vertices_4` special case clearly distinguish the dynamic five-control-point input from the four-vertex control-stage output?
- Is the exact-mask validation sufficient to connect each visible failure to its tessellation mode?
- Does the rebind explanation make clear that no draw occurs with the temporary shader bound?

No unresolved semantic risk remains after checking the source, mustpass list, direct SPIR-V artifacts, and relevant Vulkan tessellation, shader-object, and built-in-variable rules.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.shader_object.tessellation.glsl.spacing_fractional_odd_rebind` for the representative walkthrough because it combines a distinctive spacing mask with the temporary control-stage rebind.
- Keep the direct-SPIR-V nature explicit. Show the control/evaluation algorithm as a compact mapping and preserve the authoritative evaluation assembly in the mandatory SPIR-V subsection.
- Distill tessellation mode ownership and independent per-stage binding into the final Background Knowledge bullets.
- Keep the three expected-mask classes and exact comparison details in Runtime Execution and Result Checking.
- Copy the Failure Cause Mapping table above into the final page without changes, followed by fresh cause analysis.
- Move implementation entry points and spec references to the final source appendix or focused inline evidence links.
