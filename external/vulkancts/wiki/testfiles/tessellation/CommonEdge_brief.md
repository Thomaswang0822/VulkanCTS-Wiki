# Understanding Brief: `tessellation.common_edge`

## One-Sentence Test Purpose

This test checks whether adjacent tessellated triangle or quad patches produce matching edge positions, including cases that require `precise` floating-point evaluation to prevent visible cracks.

## Background Knowledge

### Common-edge tessellation

A tessellator subdivides each patch independently. Two adjacent patches meet without a gap only when both sides generate the same subdivisions and the tessellation evaluation shader maps corresponding edge coordinates to identical clip-space positions. Vulkan requires the location of the two extra fractional-spacing segments to match for edges with identical tessellation level values ([tessellator spacing](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-tessellator-spacing)).

Why it matters here:

- The test gives a shared geometric edge the same endpoint-derived outer tessellation level from both patches.
- It covers equal, fractional-even, and fractional-odd spacing because each mode derives edge subdivisions differently.

### `precise` and `NoContraction`

The GLSL `precise` qualifier causes the compiler to preserve the relevant arithmetic operations through SPIR-V `NoContraction`. The Vulkan SPIR-V environment says `NoContraction` prevents rearrangement of decorated operations ([precision controls](../../../../vulkan-docs/src/appendices/spirvenv.adoc#spirvenv-op-prec)). This matters when adjacent patches name the same control points through different patch-local indices: equivalent expressions must still reach matching edge positions.

## One Concrete Example

Consider `dEQP-VK.tessellation.common_edge.quads_fractional_even_spacing_precise`.

The host builds a `4 x 4` grid of quad patches. It reverses the four indices for alternating `precise` patches, so one geometric corner can occupy a different patch-local index in neighboring patches ([index generation](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L308-L320)). The tessellation control shader marks `gl_TessLevelOuter` as `precise`, and the tessellation evaluation shader computes four bilinear terms before adding them into `pos` and marks `gl_Position` as `precise` ([shader generation](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L131-L222)).

The evaluation shader then counts the set bits in the floating-point representation of `pos`. Odd parity moves both x and y by `0.04`. A small mismatch between two nominally shared positions can therefore become a visible gap. This amplification is a test mechanism, not a tolerance or a reference calculation.

## End-to-End Test Flow

```text
[host] select triangles or quads, one spacing mode, and basic or precise behavior
[host] generate a 5 x 5 vertex grid, per-vertex tessellation parameters, and patch indices
[host] pack positions, tessellation parameters, and indices into one host-visible buffer
[host] create a 256 x 256 color attachment and a host-visible readback buffer
[host] build the four-stage tessellation graphics pipeline
[host] clear the attachment to black and issue one indexed patch draw
[device] derive each outer tessellation level from the two edge endpoints
[device] tessellate each patch and evaluate generated coordinates into clip-space positions
[device] amplify position-bit parity into a 0.04 diagonal position offset and shade the grid
[host] copy the image to the readback buffer and scan the central 70 percent rectangle
[host] fail on the first pixel whose red, green, and blue channels are all zero
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms()` emits ESSL 3.10 vertex, tessellation control, tessellation evaluation, and fragment shaders for every test case ([program generation](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L107-L241)). The primitive type controls the patch size and interpolation formula. The spacing mode controls the tessellation evaluation layout. The `precise` cases also require `GL_EXT_gpu_shader5` and qualify `gl_TessLevelOuter` and `gl_Position`.

No descriptor sets, push constants, specialization constants, or generated SPIR-V assembly strings participate in the test. The CTS shader toolchain compiles the generated GLSL.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Combined vertex/index buffer | yes | yes | read | no | Supplies grid positions, endpoint-derived tessellation parameters, and patch topology. |
| `256 x 256` `VK_FORMAT_R8G8B8A8_UNORM` color image | yes | yes | written | copied | Black clear pixels expose gaps between colored patches. |
| Host-visible color buffer | yes | yes, as transfer destination | written by copy | yes | Carries the rendered image to `verifyResult()`. |
| Tessellation stage inputs and outputs | generated interface | yes, through pipeline stages | read and written | no | Transport control-point positions and per-fragment colors; they are not descriptor resources. |

## What Is Checked

- `verifyResult()` scans x and y from 15 percent through 85 percent of the image dimensions, excluding the intended black border outside the grid.
- A pixel fails only when all RGB channels equal zero. Alpha does not participate in the check.
- The check stops at the first black pixel and reports its coordinate as evidence of a possible crack.
- The case passes when the central rectangle contains no black pixels ([verification](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L76-L105), [readback and result](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L443-L480)).

## Behavior Parameter Identification

> **Behavior parameter:** case type
>
> **Candidate values:** `basic`, `precise`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Adjacent patches generated different subdivisions or evaluated a shared edge inconsistently even though shared vertices use matching patch-local indices; rasterization, color-attachment, copyback, or image-readback behavior may also leave an unexpected black pixel. |
| `precise` | The implementation failed to preserve the `precise`/`NoContraction` arithmetic needed when neighboring patches use different patch-local control-point indices; the common tessellation or rendering/readback causes from `basic` also apply. |

## Important Variations and Special Cases

- `triangles` creates 32 three-control-point patches from the `4 x 4` cells. `quads` creates 16 four-control-point patches.
- `equal_spacing`, `fractional_odd_spacing`, and `fractional_even_spacing` change edge subdivision. They condition the common-edge behavior but do not change the host verifier.
- Basic cases arrange shared vertices at matching patch-local indices. Precise triangle cases rotate the second triangle's local indices; precise quad cases reverse alternating patches.
- The host fixes inner tessellation levels at `5.0`. Outer levels vary from `1.0` through `60.0` according to the average tessellation parameter of each edge's endpoints.
- The parity amplifier can reveal a position mismatch by turning it into a `0.04` offset. The source does not claim that this hash-like parity step detects every possible bit difference.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Case types and parameter storage | [`CaseType` and `CaseDefinition`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L60-L74) | Defines the primary behavior axis and the primitive/spacing dimensions. |
| Image pass/fail rule | [`verifyResult()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L76-L105) | Defines the central crop and exact black-pixel failure condition. |
| Generated shaders | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L107-L241) | Emits the edge levels, interpolation, `precise` qualifiers, parity amplifier, and colors. |
| Grid and patch indices | [`test()` data generation](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L257-L328) | Builds adjacent patches and changes local index ordering for precise cases. |
| Pipeline, draw, and readback | [`test()` runtime path](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L330-L480) | Shows resource setup, indexed draw, image copy, and verifier call. |
| Registration matrix | [`createCommonEdgeTests()`](../../../modules/vulkan/tessellation/vktTessellationCommonEdgeTests.cpp#L494-L518) | Generates all 12 leaves from primitive, case type, and spacing mode. |
| Spacing semantics | [`tessellation-tessellator-spacing`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-tessellator-spacing) | Specifies segment rounding and matching fractional segment placement. |
| `NoContraction` semantics | [`spirvenv-op-prec`](../../../../vulkan-docs/src/appendices/spirvenv.adoc#spirvenv-op-prec) | Grounds the precise arithmetic failure interpretation. |
| Mustpass coverage | [`tessellation.txt#L1-L12`](../../../mustpass/main/vk-default/tessellation.txt#L1-L12) | Confirms all 12 registered leaves in the default mustpass list. |

## Questions / Risk Points for User Audit

- Is `case type` the right primary behavioral axis, with primitive type and spacing mode treated as conditioning dimensions?
- Does the parity-offset explanation make clear that the test amplifies position differences rather than comparing positions directly?
- Does the page keep the `precise` claim bounded to arithmetic preservation supported by generated GLSL and SPIR-V `NoContraction` semantics?
- Is one precise quad tessellation evaluation shader enough for the representative walkthrough? It covers the most demanding interpolation and index-order case.

All semantic questions above are resolved by the inspected implementation, tessellation and SPIR-V environment chapters, generated shader output, and default mustpass entries. They remain review prompts rather than unresolved blockers.

## Conversion Notes for Final Wiki Rewrite

- Distill common-edge subdivision and `precise`/`NoContraction` into short prerequisite bullets.
- Use `dEQP-VK.tessellation.common_edge.quads_fractional_even_spacing_precise` for one shader-analyzer walkthrough of the tessellation evaluation stage.
- Keep vertex, tessellation-control, and fragment stage roles in the walkthrough's structural table and `Additional Info`; do not add walkthroughs for fixed stage plumbing.
- Carry `case type` with `basic` and `precise` into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table above directly into the final page and write `### Cause Analysis` from the source and spec evidence.
- Move source-navigation detail to the appendix and keep the runtime section focused on the grid draw, readback, and black-pixel check.
