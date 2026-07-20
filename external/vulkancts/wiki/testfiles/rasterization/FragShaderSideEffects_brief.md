# Understanding Brief: rasterization.frag_side_effects / vktRasterizationFragShaderSideEffectsTests.cpp

This brief prepares the rewrite of the `frag_side_effects` Level-3 Vulkan CTS page. The source file is the
primary authority; the old wiki page is a navigation aid only.

## One-Sentence Test Purpose

This test checks whether fragment-shader storage-buffer side effects remain observable when the fragment color
output is killed, demoted, terminated, sample-masked, rejected by stencil/depth/depth-bounds tests, or eliminated
by alpha-to-coverage, regardless of whether the color assignment appears before or after the side effect.

Core question: **does the implementation keep a fragment-shader storage-buffer write live even when every
subsequent pipeline stage suppresses or rejects the fragment's color output?**

## Background Knowledge

### Fragment-shader side effects versus color output visibility

A fragment shader may execute stores and atomics to storage buffers, storage images, or other non-color storage.
The Vulkan spec treats these side effects as observable independently of the per-fragment color output: whether
the final color survives `OpKill`, sample mask, stencil/depth/depth-bounds rejection, or alpha-to-coverage
does not change the fact that the shader executed and its side effects must be visible to the host after the
pipeline completes. The host observes those side effects through shader storage buffer reads after pipeline
execution.

Why it matters here:

- The tested SSBO write happens inside the fragment shader, at the per-pixel `outBuffer.val[bufferIndex] = 1`
  line, with one int32 slot per framebuffer pixel
  [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L256-L266).
- Color-output suppression mechanisms operate later in the pipeline or via control-flow exits; they must not
  retroactively remove earlier side effects.
- The host treats the SSBO check as the primary correctness signal: if any pixel's SSBO entry is not `1`, the
  case fails before the color attachment is even examined
  [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L622-L636).

### Helper invocation and `demote`

`VK_EXT_shader_demote_to_helper_invocation` introduces `OpDemoteToHelperInvocation` (GLSL `demote`). A demoted
invocation becomes a helper invocation: it continues executing shader instructions, but its outputs (color,
depth, etc.) are discarded by the rasterizer. This differs from `OpKill`/`discard`, which terminates the
invocation. The spec explicitly permits stores and atomics performed by demoted invocations to be visible to
subsequent pipeline work and to the host.

Why it matters here:

- The `demote` case writes the SSBO before the `demote` statement, then demotes
  [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L227-L229).
- A correct implementation must keep the earlier SSBO write visible and must not produce color output for the
  demoted pixel.

### `terminateInvocation` versus `OpKill`

`VK_KHR_shader_terminate_invocation` introduces `OpTerminateInvocation` (GLSL
`terminateInvocation`). Unlike `OpKill`, `terminateInvocation` ends the invocation immediately but is not
allowed to terminate the shader stage in a way that affects derivative computations or other invocations'
execution. For side-effect purposes, both `OpKill` and `OpTerminateInvocation` stop the invocation, so any
side effect performed before the terminating instruction must remain visible.

Why it matters here:

- The `terminate_invocation` case writes the SSBO before `terminateInvocation`
  [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L231-L233).
- The test asserts that the side effect survives even though the invocation terminates immediately after.

### Sample mask, stencil/depth rejection, alpha-to-coverage, and depth bounds

These pipeline-fixed-function stages can suppress a fragment's color output without terminating the shader:

- `gl_SampleMask` written to zero in the fragment shader removes per-sample coverage; with
  `VK_SAMPLE_COUNT_1_BIT`, this means no color output for that pixel
  [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L235-L239).
- Stencil test (`VK_COMPARE_OP_NEVER`) and depth test (`VK_COMPARE_OP_NEVER`) reject fragments before color
  blending/output [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L518-L523).
- Depth bounds test compares the framebuffer depth value against `[minDepthBounds, maxDepthBounds]`; the
  depth-bounds case uses mesh depth `0.75` against bounds `[0.25, 0.5]`, which fails the test
  [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L515, #L765-L768).
- Alpha-to-coverage converts fragment alpha to a temporary coverage mask; with alpha `0.0`, no samples are
  covered, so the pixel keeps the clear color
  [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L500-L512).

Why it matters here:

- All these mechanisms happen after the shader has had a chance to write the SSBO. The shader writes
  `outBuffer.val[bufferIndex] = 1` regardless of whether the per-fragment tests later pass.
- For all cases except `alpha_coverage_before`/`_after`, the expected color attachment value is the clear
  color `(0, 0, 0, 1)` [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L109-L112).
- The alpha-to-coverage cases additionally accept the draw color as a valid color attachment outcome, because
  the per-pixel coverage mask produced by alpha-to-coverage is implementation-dependent and the test accepts
  either the cleared or the drawn pixel value
  [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L641-L644).

## One Concrete Example

Representative test name from mustpass:

```text
dEQP-VK.rasterization.frag_side_effects.color_at_beginning.kill
```

Simplified behavior:

1. The host creates a 32x32 color attachment (`VK_FORMAT_R8G8B8A8_UNORM`), clears it to `(0, 0, 0, 1)`, and
   binds a 32x32 int32 storage buffer zeroed on the host.
2. The vertex shader draws a full-screen triangle strip with depth `0.0` (the default, since this case has no
   depth-bounds parameters).
3. For each covered pixel, the fragment shader:
   - computes `bufferIndex = fragCoord.y * 32 + fragCoord.x`;
   - assigns `outColor = vec4(0, 0, 1, 1)` (the draw color) when `colorAtEnd` is false (the `color_at_beginning`
     child);
   - writes `outBuffer.val[bufferIndex] = 1`;
   - executes `discard;`.
4. The host invalidates and reads the storage buffer; every entry must equal `1`.
5. The host copies the color attachment to a host-visible buffer; every pixel must equal the clear color
   `(0, 0, 0, 1)`.

Conceptual fragment shader reconstruction (matches
[vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L256-L266)):

```glsl
#version 450
layout(set=0, binding=0, std430) buffer OutputBuffer { int val[1024]; } outBuffer;
layout (location=0) out vec4 outColor;
void main() {
    const ivec2 fragCoord = ivec2(gl_FragCoord);
    const int bufferIndex = (fragCoord.y * 32) + fragCoord.x;
    outColor = vec4(0.0, 0.0, 1.0, 1.0);
    outBuffer.val[bufferIndex] = 1;
    discard;
}
```

Important simplifications:

- The real generator builds the color statement from `drawColor` and inserts it before or after the SSBO
  write depending on `colorAtEnd`.
- For alpha-coverage cases the `outColor.a` is written separately, the RGB is written via the
  `colorStatement`, and `alphaToCoverageEnable` is enabled in the multisample state.

## End-to-End Test Flow

```text
1. [host] register the case hierarchy
   1.1 create the `frag_side_effects` root group
   1.2 create the `color_at_beginning` and `color_at_end` color-order children
   1.3 for each color order, attach the 10 case-type leaves

2. [host] check feature support
   2.1 all cases require `fragmentStoresAndAtomics`
   2.2 `depth_bounds` requires `depthBounds`
   2.3 `demote` requires `VK_EXT_shader_demote_to_helper_invocation`
   2.4 `terminate_invocation` requires `VK_KHR_shader_terminate_invocation`

3. [host] generate shader program artifacts
   3.1 generate the vertex shader that places depth at the chosen mesh depth
   3.2 generate the fragment shader that writes the SSBO and, optionally, the color output
   3.3 for demote/terminate cases, emit the corresponding `#extension` directive
   3.4 for alpha-coverage cases, leave out the alpha component from the color statement

4. [host] create and bind resources
   4.1 create a 32x32 color image (R8G8B8A8_UNORM) with color-attachment and transfer-src usage
   4.2 for stencil_never/depth_never/depth_bounds cases, find a supported depth/stencil format and create a
       depth/stencil image
   4.3 create a host-visible color image buffer for readback
   4.4 create a vertex buffer containing a full-screen quad as a triangle list
   4.5 create a 1024-element int32 storage buffer, host-visible, zeroed
   4.6 build a descriptor set with the storage buffer bound at set 0, binding 0, fragment stage

5. [host] build pipeline state
   5.1 graphics pipeline with vertex and fragment stages
   5.2 multisample state with `VK_SAMPLE_COUNT_1_BIT`; `alphaToCoverageEnable` for alpha-coverage cases
   5.3 depth/stencil state:
       - depth test enabled and `VK_COMPARE_OP_ALWAYS` except for `depth_never` (`VK_COMPARE_OP_NEVER`)
       - stencil test enabled and `VK_COMPARE_OP_ALWAYS` except for `stencil_never` (`VK_COMPARE_OP_NEVER`)
       - depth-bounds test enabled for `depth_bounds` with bounds `[0.25, 0.5]`
   5.4 color-blend state with no blending and full color-write mask

6. [host] record and submit the command buffer
   6.1 begin render pass with clear color (color) and depth/stencil `(1.0, 0)`
   6.2 bind pipeline, descriptor set, vertex buffer
   6.3 draw the full-screen triangle list (6 vertices)
   6.4 end render pass
   6.5 insert a buffer memory barrier from `FRAGMENT_SHADER_BIT`/`SHADER_WRITE_BIT` to `HOST_BIT`/`HOST_READ_BIT`
       for the storage buffer
   6.6 insert an image memory barrier from `COLOR_ATTACHMENT_OUTPUT_BIT`/`COLOR_ATTACHMENT_WRITE_BIT` to
       `TRANSFER_BIT`/`TRANSFER_READ_BIT` for the color image
   6.7 copy the color image to the color image buffer
   6.8 insert a buffer memory barrier from `TRANSFER_BIT`/`TRANSFER_WRITE_BIT` to `HOST_BIT`/`HOST_READ_BIT`
       for the color image buffer

7. [device] fragment shader executes per covered pixel
   7.A for `kill`: write SSBO, write color (depending on order), `discard`
   7.B for `demote`: write SSBO, write color, `demote`
   7.C for `terminate_invocation`: write SSBO, write color, `terminateInvocation`
   7.D for `sample_mask_before`: set `gl_SampleMask[0] = 0`, write SSBO, write color
   7.E for `sample_mask_after`: write color, write SSBO, set `gl_SampleMask[0] = 0`
   7.F for `stencil_never`/`depth_never`/`depth_bounds`: write SSBO, write color; the per-fragment test then
       rejects the fragment before color output
   7.G for `alpha_coverage_before`: write RGB, set `outColor.a = 0`, write SSBO; alpha-to-coverage removes
       coverage
   7.H for `alpha_coverage_after`: write RGB, write SSBO, set `outColor.a = 0`; alpha-to-coverage removes
       coverage

8. [host] inspect results
   8.1 invalidate and read the storage buffer; every element must equal `1`
   8.2 invalidate and read the color image buffer; every pixel must match the expected color set
   8.3 if any pixel is unexpected, log a red/green error mask and the color buffer image
   8.4 pass only if both checks succeed
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | Generated/loaded where | Role |
|----------|------------------------|------|
| Vertex shader source | [FragSideEffectsTestCase::initPrograms()](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L197-L203) | Places a 2D position with the chosen mesh depth (`0.0` by default, `0.75` for depth bounds). |
| Fragment shader source | [FragSideEffectsTestCase::initPrograms()](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L205-L266) | Inserts the color statement before or after the SSBO write, plus the case-specific terminator/mask/test statement. |
| Graphics pipeline state | [FragSideEffectsInstance::iterate()](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L482-L567) | Configures multisample, depth/stencil, color-blend, and rasterization state per case type. |

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|------------------------------|---------------|-------------------------|--------------------|----------------|
| Color image (R8G8B8A8_UNORM, 32x32) | Yes | Yes (color attachment) | Written by color blend | Copied via `vkCmdCopyImageToBuffer` | The image whose pixel values are compared against the expected color set. |
| Depth/stencil image | Yes, for `depth_bounds`/`depth_never`/`stencil_never` cases | Yes (depth/stencil attachment) | Written by depth/stencil test | No | Provides the depth/stencil buffer the per-fragment tests operate on. |
| Color image readback buffer | Yes (host-visible) | Yes (transfer destination) | Transfer destination from the color image | Yes | Host-visible buffer the host invalidates and reads to inspect the color attachment. |
| Vertex buffer | Yes (host-visible) | Yes (vertex buffer) | Read by vertex shader | No | Contains the full-screen quad vertices (six `vec2` entries forming a triangle list). |
| Storage buffer (int32, 1024 entries) | Yes (host-visible, zeroed) | Yes (descriptor binding 0, fragment stage) | Written by fragment shader (`outBuffer.val[bufferIndex] = 1`) | Yes (invalidated and read by host) | The SSBO whose per-pixel `1` value is the primary correctness signal. |
| Descriptor set | Yes | Yes | Connects the storage buffer to binding 0 | No | Single `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` binding at set 0, binding 0. |

## What Is Checked

### Device-side checks

There are no explicit shader-side pass/fail writes; the shader simply writes `1` to the SSBO. The validation
is host-side.

### Host-side checks

| Check | Where | Pass condition |
|-------|-------|----------------|
| Storage buffer scan | [iterate()](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L622-L636) | Every one of the 1024 int32 entries equals `1`. Any mismatch returns `fail` immediately with the failing element index. |
| Color attachment scan | [iterate()](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L639-L676) | Every pixel matches one of the expected colors. For non-alpha-coverage cases, the expected set is `{clearColor}`. For `alpha_coverage_before`/`alpha_coverage_after`, the expected set is `{clearColor, drawColor}`. |
| Error mask logging | [iterate()](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L652-L674) | On color mismatch, the host writes a red/green error mask image and the color buffer image to the test log. |

There is no tolerance: any nonzero SSBO mismatch or any non-matching pixel fails the case.

## Behavior Parameter Identification

> **Behavior parameter:** `case_type` (the leaf directly under each color-order child)
>
> **Candidate values:** `kill`, `demote`, `terminate_invocation`, `sample_mask_before`, `sample_mask_after`,
> `stencil_never`, `depth_never`, `alpha_coverage_before`, `alpha_coverage_after`, `depth_bounds`

The secondary axis is `color_order` with values `color_at_beginning` and `color_at_end`. The primary axis
remains `case_type` because each case type exercises a materially different suppression mechanism for the
fragment color output.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `kill` | `OpKill`/`discard` retroactively removed the prior SSBO write, or the color attachment was unexpectedly updated despite the discard. |
| `demote` | The demoted helper invocation did not execute (or its stores were elided), or the demoted invocation unexpectedly produced color output. |
| `terminate_invocation` | `OpTerminateInvocation` was treated as if it suppressed prior side effects, or it was implemented by lowering that lost the SSBO store. |
| `sample_mask_before` | The shader exited early after `gl_SampleMask[0] = 0` and did not perform the SSBO write, or the sample-mask write did not suppress color output. |
| `sample_mask_after` | Setting `gl_SampleMask[0] = 0` after the SSBO write suppressed the SSBO write, or did not suppress color output. |
| `stencil_never` | The stencil-rejected fragment skipped shader execution entirely, or the stencil test let color output through. |
| `depth_never` | The depth-rejected fragment skipped shader execution entirely, or the depth test let color output through. |
| `alpha_coverage_before` | The alpha-to-coverage path removed the SSBO write, or the alpha-zero color output produced an unexpected pixel value. |
| `alpha_coverage_after` | Same as `alpha_coverage_before` but with the alpha assignment after the SSBO write. |
| `depth_bounds` | The depth-bounds-rejected fragment skipped shader execution, or the depth-bounds test let color output through. |

All cases also share a common failure surface: the storage-buffer-to-host barrier, the storage buffer
zeroing, or the host-side scan logic could be wrong independently of the case-specific mechanism.

## Important Variations and Special Cases

### `color_at_beginning` versus `color_at_end`

Both color-order children share the same set of 10 case-type leaves. The only difference is whether the
`outColor` assignment is emitted before or after the SSBO write in the generated fragment shader. This
explicitly varies whether the color assignment is placed at the start or the end of the shader so that
implementation optimizations that order or move the color write relative to the side effect cannot mask a
missing side effect [vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L692-L701).

### Alpha-coverage case color handling

For the `alpha_coverage_before` and `alpha_coverage_after` cases the `drawColor.w()` is forced to `0.0`
before shader generation. The generated shader leaves out the alpha component in the `colorStatement` and
emits a separate `outColor.a = float(0.0)` statement before or after the SSBO write. The host then accepts
either the clear color or the draw color as a valid color attachment outcome
[vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L207-L220, #L241-L245, #L641-L644).

### Depth/stencil format selection

When a depth/stencil attachment is needed (`depth_bounds`, `depth_never`, `stencil_never`), the host iterates
`{VK_FORMAT_D32_SFLOAT_S8_UINT, VK_FORMAT_D24_UNORM_S8_UINT}` and picks the first one whose
`VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` is supported
[vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L317-L353)].
The test fails with `TCU_FAIL` if neither format is supported.

### Depth bounds parameters

The `depth_bounds` case uses mesh depth `0.75` against bounds `[0.25, 0.5]`, which is intentionally outside
the bounds so the depth-bounds test rejects the fragment after shader execution
[vktRasterizationFragShaderSideEffectsTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L765-L768)].

### Mustpass coverage

The `vk-default` mustpass file lists all 20 cases (10 case types x 2 color orders) under
`rasterization.frag_side_effects`
[ vk-default/rasterization.txt](../../../mustpass/main/vk-default/rasterization.txt#L8562-L8581)].
The `vksc-default` mustpass file lists the same 20 cases with the `dEQP-VKSC.` prefix
[vksc-default/rasterization.txt](../../../mustpass/main/vksc-default/rasterization.txt#L449-L468)].

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Case-type enumeration | [vktRasterizationFragShaderSideEffectsTests.cpp#L58-L70](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L58-L70) | Defines the 10 case types and their identifiers. |
| Test parameters and depth-bounds struct | [vktRasterizationFragShaderSideEffectsTests.cpp#L81-L107](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L81-L107) | Carries `caseType`, `clearColor`, `drawColor`, `colorAtEnd`, and optional depth-bounds parameters. |
| Feature support check | [FragSideEffectsTestCase::checkSupport()](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L162-L182) | Applies `fragmentStoresAndAtomics`, `depthBounds`, `VK_EXT_shader_demote_to_helper_invocation`, and `VK_KHR_shader_terminate_invocation` gates. |
| Vertex shader generation | [initPrograms() vertex shader](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L197-L203) | Emits the vertex shader that places depth at the chosen mesh depth. |
| Fragment shader generation | [initPrograms() fragment shader](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L205-L266) | Builds the per-case fragment shader with the color statement ordering and case-specific terminator/mask/test statement. |
| Pipeline state setup | [iterate() pipeline state](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L482-L567) | Configures multisample, depth/stencil, color-blend, and rasterization state per case type. |
| Render pass and draw | [iterate() render pass](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L575-L620) | Records the full-screen triangle-list draw with the configured clear values. |
| SSBO check | [iterate() SSBO scan](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L622-L636) | The primary pass condition: every SSBO entry must equal `1`. |
| Color attachment check | [iterate() color scan](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L639-L676) | The secondary pass condition: every pixel must match an expected color. Logs an error mask on failure. |
| Test family registration | [createFragSideEffectsTests()](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.cpp#L684-L777) | Creates the root, color-order children, and case-type leaves. |
| Mustpass evidence (vk-default) | [vk-default/rasterization.txt#L8562-L8581](../../../mustpass/main/vk-default/rasterization.txt#L8562-L8581) | Lists all 20 cases under `rasterization.frag_side_effects`. |
| Mustpass evidence (vksc-default) | [vksc-default/rasterization.txt#L449-L468](../../../mustpass/main/vksc-default/rasterization.txt#L449-L468) | Lists the same 20 cases with the `dEQP-VKSC.` prefix. |
| Factory declaration | [vktRasterizationFragShaderSideEffectsTests.hpp#L35](../../../modules/vulkan/rasterization/vktRasterizationFragShaderSideEffectsTests.hpp#L35) | Declares `createFragSideEffectsTests`. |

## Questions / Risk Points for User Audit

- [x] Is the core test purpose clear? The test asserts that fragment-shader side effects (SSBO writes) survive
  every color-output suppression mechanism in the Vulkan pipeline.
- [x] Is the host/device timeline understandable? The host generates the shader, builds the pipeline, submits a
  single draw, and inspects both the SSBO and the color attachment.
- [x] Are generated artifacts distinguished from real GPU resources? The shader source is generated; the
  storage buffer, color image, depth/stencil image, vertex buffer, descriptor set, and pipeline are real
  Vulkan resources.
- [x] Are important buffers, images, descriptors included? Yes: color image, depth/stencil image, color image
  readback buffer, vertex buffer, storage buffer, descriptor set.
- [x] Is the shader or device-side behavior explained at the right depth? The shader writes the SSBO and
  optionally the color, then exits or applies the case-specific suppression mechanism.
- [x] Are special variants explained only as much as needed? The alpha-coverage case has an additional
  expected color and a separate alpha assignment; the depth-bounds case has its own depth/bounds values; the
  demote and terminate cases require their own extensions.
- [x] Which parts should become final wiki content? The end-to-end flow, the resource table, the behavior
  parameter identification, and the failure cause mapping carry over directly. The background knowledge distills
  into a compact prerequisite list.
- [ ] Verify mustpass line anchors before publishing a final wiki page, because generated mustpass files may
  shift across CTS versions. (Risk: low. The anchors above match the current repo state.)

## Conversion Notes for Final Wiki Rewrite

- Keep the one-sentence purpose as the final page's short problem statement.
- Distill the background into a compact prerequisite list: fragment-shader side effects versus color output
  visibility; helper-invocation and `demote`; `terminateInvocation` versus `OpKill`; sample mask, stencil/depth
  rejection, alpha-to-coverage, and depth bounds.
- Select `color_at_beginning.kill` as the default walkthrough; add `color_at_beginning.demote` and
  `color_at_beginning.alpha_coverage_before` as materially different walkthroughs (extension directive +
  demote statement; alpha-coverage setup with separate alpha assignment).
- Preserve the resource table in a more formal final-wiki style because it directly addresses generated-artifact
  versus real Vulkan-resource confusion.
- Move detailed pruning rules and feature gates into the Case Pruning section.
- Do not copy the beginner-focused prose verbatim into the final page; convert it to the Level-3 wiki style.
- The `### Failure Cause Mapping` table from `## What Failure Means` should be copied directly into the final
  page's `## Failure Meaning` -> `### Failure Cause Mapping`. The `### Cause Analysis` subsection is written
  fresh during the final rewrite.
