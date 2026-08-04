# Understanding Brief: pipeline stencil tests

## One-Sentence Test Purpose

This test checks whether Vulkan applies configured stencil comparisons, operations, masks, and references correctly across supported stencil formats, attachment arrangements, and selected pipeline-construction paths.

## Background Knowledge

### Stencil comparison and update

For each covered sample, Vulkan masks the stencil attachment value and the selected face reference, compares them with `VkCompareOp`, and can remove coverage when the comparison fails. The selected operation is `failOp` after a failed stencil comparison, `depthFailOp` after a passed stencil comparison and failed depth comparison, or `passOp` after both comparisons pass. A write mask limits the resulting stencil update.

Why it matters here:
- The main matrix changes exactly these operations and comparisons.
- The test changes front and back references and masks for each of four draws.

### Front and back state

Vulkan uses front state for front-facing polygons and back state for back-facing polygons. This suite provides an independently constructed front state and a seeded permutation of back states, so a result must match both state selections rather than a shared configuration.

## One Concrete Example

Consider `dEQP-VK.pipeline.monolithic.stencil.format.d16_unorm_s8_uint.states.fail_keep.pass_replace.dfail_invert.comp_equal.any`.

The case creates a color attachment and a `VK_FORMAT_D16_UNORM_S8_UINT` depth/stencil attachment, clears them, and draws four overlapping quads. Its front stencil state uses `KEEP` for a stencil failure, `REPLACE` after both tests pass, `INVERT` after a depth failure, and `EQUAL` for the stencil comparison. Each quad receives its own front/back reference and read/write masks through dynamic stencil commands. The implementation also selects a deterministic, different back-face state from its `StencilOpStateUniqueRandomIterator` for that exact front-state position. After the draw, the host reads the color and stencil images and compares both with `ReferenceRenderer` output configured with the same state.

## End-to-End Test Flow

```text
[host] register format, stencil-state, layout, and attachment variants
[host] select a stencil format and build front and back VkStencilOpState values
[host] create and clear the color attachment when requested and the stencil image
[host] record four draws, setting each draw's front/back masks and references
[device] select front or back stencil state, compare masked values, run depth testing, and apply the selected stencil operation
[host] wait for completion, read attachments, and render the matching software reference
[host] compare color when present and stencil in all main-matrix cases
[host] report pass only when the observed images match the reference
```

`no_stencil_att` uses a separate flow. It enables the stencil test despite providing no stencil attachment, draws a full-screen triangle, reads back color and depth, and reads stencil too when the backing depth format has that aspect. The expected color is blue, depth is `0.75`, and an available stencil aspect remains at its clear value `255`.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `StencilTest::initPrograms()` generates a pass-through vertex shader. With a color attachment it also generates a fragment shader that writes the interpolated color. These shaders make the fixed-function stencil result observable; they do not calculate stencil values.
- `createStencilTests()` generates the main matrix. The front state follows nested loops; the back state comes from a `StencilOpStateUniqueRandomIterator` seeded with `123`.
- `NoStencilAttachmentCase::initPrograms()` generates a vertex shader that places a full-screen triangle at pushed depth `0.75` and a fragment shader that writes blue.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color image | yes, except in `nocolor` | yes | written by fragment output | yes when present | Exposes coverage and color output for the main family. |
| Stencil or depth/stencil image | yes | yes | cleared, read, and written by fragment operations | yes | Holds the state that the main family compares with the software reference. |
| Vertex buffer | yes | yes | read by vertex fetch | no | Supplies the overlapping quads in the main family. |
| `no_stencil_att` depth image | yes | yes | depth attachment access | yes | Lets the special family prove that the draw still passes depth testing without a stencil attachment. |
| Readback buffers | yes | yes | transfer destination | yes | Carry `no_stencil_att` attachment results to host comparisons. |

## What Is Checked

- Main `format` and `nocolor` cases render the same quads in `ReferenceRenderer`. The host compares the stencil image in every case and compares the color image when a color attachment exists. Both comparisons use an integer threshold of `(2, 2, 2, 2)` and position deviation `(1, 1, 0)`.
- `no_stencil_att` requires an exact blue color result, depth `0.75` within `0.000025`, and, when available, an unchanged stencil value of `255`.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `format`, `nocolor`, `no_stencil_att`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `format` | Incorrect front/back stencil comparison, operation selection, masked update, layout handling, or color-and-stencil attachment interaction. |
| `nocolor` | Incorrect stencil behavior when no color attachment is present, including attachment setup or fixed-function execution that depends on color output. |
| `no_stencil_att` | Stencil test changes coverage or attachment contents despite the absence of a stencil attachment, or static/dynamic enabling diverges from the required behavior. |

## Important Variations and Special Cases

- The main family covers `VK_FORMAT_S8_UINT`, `VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, and `VK_FORMAT_D32_SFLOAT_S8_UINT`. Combined depth/stencil formats add a separate-depth/stencil-layout variant.
- The `general` layout case covers only the first three values in each operation and comparison loop. The `any` layout case covers the full matrix.
- `no_stencil_att` registers only for monolithic, fast-linked-library, and shader-object-unlinked-SPIR-V construction types. Render-pass coverage is omitted for shader objects, and Vulkan SC omits dynamic rendering.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Main matrix and special-family registration | [`createStencilTests()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1469-L1664) | Defines registered identifiers, formats, operation loops, and construction-type restrictions. |
| Main shader generation and support checks | [`StencilTest::initPrograms()` and `checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L265-L328) | Shows the simple shader role and requirements. |
| Main draw and reference comparison | [`StencilTestInstance::iterate()` and `verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L755-L880) | Defines the draw sequence and image-based oracle. |
| Missing-attachment execution and checks | [`NoStencilAttachmentInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1036-L1427) | Defines the no-stencil setup, expected values, and readback checks. |
| Vulkan stencil semantics | [`Stencil Test`](../../../../vulkan-docs/src/chapters/fragops.adoc#L1508-L1590) | Defines comparison, operation selection, masks, face selection, and the no-stencil-attachment rule. |

## Questions / Risk Points for User Audit

- The source and specification agree that no stencil attachment leaves coverage unmodified when stencil testing is enabled.
- The brief uses the test family as the behavioral axis because each family changes the property under test; operation, format, layout, and construction dimensions remain supporting matrix dimensions.
- The generated GLSL does not implement the tested stencil logic. A shader walkthrough and SPIR-V disassembly would describe boilerplate output transport rather than the fixed-function property, so the final page records no representative shader walkthrough.

## Conversion Notes for Final Wiki Rewrite

Keep a compact stencil-semantics prerequisite, the family-level failure table, and the explanation that shaders provide observability rather than stencil logic. Move detailed resource flow and values into runtime checking and parameter sections. Preserve the failure-cause mapping table verbatim.
