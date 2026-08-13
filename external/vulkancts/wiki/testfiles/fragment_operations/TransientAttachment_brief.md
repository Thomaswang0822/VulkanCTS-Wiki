# Understanding Brief: fragment_operations.transient_attachment_bit / vktFragmentOperationsTransientAttachmentTests.cpp

This brief prepares the rewrite of the transient attachment Level-3 page. It is explanation-first and uses the source code as the primary authority.

## One-Sentence Test Purpose

This test checks whether a transient attachment backed by lazily allocated or device-local memory survives a load/store boundary between two render passes, so that a later fragment shader can read its cleared contents as an input attachment.

Core question: **if the first subpass clears a transient attachment and the next subpass reads it back through `subpassLoad`, does the implementation preserve the cleared value?**

## Background Knowledge

### Transient attachment bit and lazily allocated memory

`VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT` marks an image whose contents are only meaningful within a render pass instance. The Vulkan spec ties this usage bit to lazily allocated memory: a memory type with `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` may only be bound to a `VkImage` whose usage flags include `VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT`, and the implementation may back the image with zero committed memory until the attachment is actually rendered into. The spec note observes that transient framebuffer attachments that are not needed after a render pass may never be allocated at all on some implementations.

Why it matters here:

- The test deliberately pairs `VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT` with both lazy and device-local memory, so the two memory classes are exercised independently.
- A lazy-backed attachment is the spec-intended path for transient usage; a device-local attachment is the generic fallback that must still work because the usage flag and memory property are independent selections.

### Load and store ops across subpass boundaries

A render-pass attachment declares how its contents are treated at the start (`loadOp`) and end (`storeOp`) of a subpass. `VK_ATTACHMENT_LOAD_OP_CLEAR` fills the attachment with a clear value before the subpass runs. `VK_ATTACHMENT_LOAD_OP_LOAD` requires the attachment contents from a previous use to survive into this subpass. `VK_ATTACHMENT_STORE_OP_STORE` keeps the contents generated during the subpass.

Why it matters here:

- The test uses two separate render-pass instances. The first clears the transient attachment with `VK_ATTACHMENT_LOAD_OP_CLEAR` and stores with `VK_ATTACHMENT_STORE_OP_STORE`. The second loads with `VK_ATTACHMENT_LOAD_OP_LOAD`. The store-then-load handoff across two render passes is what the test actually exercises.
- Because transient attachments are intended to be discardable, a failure to preserve the cleared value across this handoff is the observable defect the test targets.

### Input attachment reads

An input attachment is a framebuffer attachment that the fragment shader of the same subpass can read through a `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT` descriptor. GLSL exposes it through `subpassLoad()` (floating point) or `usubpassInput` plus `subpassLoad()` (unsigned). The read returns the per-pixel attachment value at the fragment's location.

Why it matters here:

- The second render pass binds the transient attachment as an input attachment and the fragment shader reads it with `subpassLoad`. This is how the test observes what the implementation preserved from the clear in pass one.

## One Concrete Example

Consider `color_load_store_op_test_lazy_bit`. The transient color attachment is an `R8G8B8A8_UNORM` image with usage `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT | VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT`, backed by lazily allocated memory.

```
[host] create transient input image (lazy) + output color image (device-local) + result buffer (host-visible)
[device] render pass 1: clear transient attachment to RGBA (1.0, 1.0, 0.0, 1.0), store it
[device] pipeline barrier: color-attachment write -> input-attachment read
[device] render pass 2: fragment shader reads the attachment via subpassLoad(inputValue), writes fragColor = the loaded value
[device] copy output image to result buffer
[host] compare result against a reference filled with (1.0, 1.0, 0.0, 1.0)
```

The same shape applies to depth and stencil cases. Depth clears to 0.5; the shader maps the depth component to red. Stencil clears to 128; the shader reads it through `usubpassInput` and scales to 0.5 in the blue channel.

## End-to-End Test Flow

```
[host] construct TransientAttachmentTestInstance with TestMode, memory-property flags, and render size 32x32
[host] bind transient input image with the requested memory requirement (lazy or local)
[host] bind a second R8G8B8A8_UNORM output image (device-local) and a host-visible result buffer
[host] build two render passes: pass one clears only the transient attachment; pass two binds the transient attachment as an input attachment plus the output image as a color attachment
[host] build a graphics pipeline for pass two with the input-attachment descriptor set
[device] begin pass one, clear transient attachment to the mode-specific clear value, end pass one
[device] pipeline memory barrier: attachment write (color or depth/stencil) -> input-attachment read, at the fragment-shader stage
[device] begin pass two, draw a full-screen triangle pair, fragment shader reads the transient attachment via subpassLoad and writes a color derived from it
[device] copy the output image into the result buffer with a layout transition
[host] invalidate and read back the result buffer
[host] build a reference image cleared to the expected decoded output color
[host] compare rendered output to the reference with tcu::floatThresholdCompare() using a Vec4(0.02) threshold
[host] pass if the comparison matches, fail otherwise
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The vertex shader is a fixed pass-through that copies `position` to `gl_Position`.

The fragment shader is generated in `TransientAttachmentTest::initPrograms` and differs by `TestMode`:

- Declaration uses `subpassInput` for color and depth, `usubpassInput` for stencil, at `input_attachment_index = 0, binding = 0`.
- Color mode: `fragColor = subpassLoad(inputValue)`.
- Depth mode: `fragColor = vec4(subpassLoad(inputValue).r, 0.0, 0.0, 1.0)`.
- Stencil mode: `fragColor = vec4(0.0, 0.0, float(subpassLoad(inputValue).r) / 256.0, 1.0)`.

Two render passes are constructed in the test instance rather than authored as assets: `renderPassOne` clears only the transient attachment; `renderPassTwo` declares the transient attachment as an input attachment and the output image as a color attachment.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Transient input image | yes, with transient + attachment + input-attachment usage | yes, lazy or device-local memory | yes, cleared in pass one, read as input attachment in pass two | no | the object under test |
| Input attachment descriptor set | yes, `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT` | yes | yes, read by fragment shader | no | the read channel that observes preserved contents |
| Output color image | yes, `R8G8B8A8_UNORM`, device-local | yes | yes, written by fragment shader in pass two | no, copied to buffer | the observable result |
| Result buffer | yes, host-visible | yes | yes, transfer destination | yes | host-side comparison input |
| Vertex buffer | yes, six vertices forming two triangles | yes | yes, vertex fetch | no | full-screen coverage so every pixel is sampled |

## What Is Checked

- The check is host-side. After the device writes the output image and copies it to the result buffer, the test builds a reference image cleared to the expected decoded output color and compares with `tcu::floatThresholdCompare()` using a per-component threshold of `0.02`.
- The expected decoded output color is derived from the clear value the way the fragment shader decodes it: color `(1.0, 1.0, 0.0, 1.0)`, depth `(0.5, 0.0, 0.0, 1.0)`, stencil `(0.0, 0.0, 0.5, 1.0)`.
- The comparison covers the whole 32x32 render area. Every case is judged independently.

## Behavior Parameter Identification

There are two registered behavioral axes in this test family.

> **Behavior parameter 1:** `attachment mode` (the TestMode axis)
>
> **Candidate values:** `color`, `depth`, `stencil`

> **Behavior parameter 2:** `memory-property mode` (the backing-memory axis)
>
> **Candidate values:** `lazy` (`VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT`), `local` (`VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT`)

If either identification is wrong, the failure analysis below needs to be redone.

## What Failure Means

### Failure Cause Mapping

Attachment mode axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `color` | Color-attachment clear/store/load path does not preserve the cleared value for input-attachment readback. |
| `depth` | Depth-aspect clear/store/load path or depth input-attachment read does not preserve the cleared 0.5 depth value. |
| `stencil` | Stencil-aspect clear/store/load path or unsigned stencil input-attachment read does not preserve the cleared 128 value. |

Memory-property mode axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `lazy` | Lazily allocated memory does not commit or preserve the transient attachment contents across the clear/load handoff. |
| `local` | Device-local transient attachment does not preserve contents across the clear/load handoff; not specific to lazy memory. |

Shared cause: if all six cases fail, the common infrastructure (input-attachment descriptor binding, the pipeline barrier between pass one and pass two, or the two-pass clear/load design itself) is the more likely cause than any single axis value.

## Important Variations and Special Cases

- The six registered leaves are the full product of the two axes: three attachment modes crossed with two memory-property modes. No case is generated programmatically beyond this fixed table.
- Stencil format is not fixed. The test instance selects the first supported stencil-capable format among `VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, and `VK_FORMAT_D32_SFLOAT_S8_UINT`. Color is always `VK_FORMAT_R8G8B8A8_UNORM`; depth is always `VK_FORMAT_D16_UNORM`.
- The pipeline barrier between pass one and pass two uses attachment-write to input-attachment-read access masks. For depth and stencil cases the source stage is both early and late fragment tests; for color it is the color-attachment-output stage.
- The output image layout transition and copy to the host-visible result buffer use `copyImageToBuffer` with the output image's final layout handled internally.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration table (six cases) | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L607-L623) | the full registered leaf set |
| TestMode enum | [`vktFragmentOperationsTransientAttachmentTests.cpp`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L56-L62) | the attachment-mode axis |
| checkSupport | [`TransientAttachmentTest::checkSupport()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L299-L329) | memory-type and format support gates |
| initPrograms (shader generation) | [`TransientAttachmentTest::initPrograms()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L252-L296) | per-mode fragment shader |
| iterate (runtime flow) | [`TransientAttachmentTestInstance::iterate()`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L372-L592) | clear, barrier, input-attachment draw, copyback |
| Memory-property selection | [`TransientAttachmentTestInstance`](../../../modules/vulkan/fragment_ops/vktFragmentOperationsTransientAttachmentTests.cpp#L366-L367) | lazy versus local memory requirement |

## Questions / Risk Points for User Audit

- Is the core test purpose clear: preserve a cleared transient attachment value across a clear/store/load handoff and read it back as an input attachment?
- Is the two-axis behavior parameter split correct, or should the single test case leaf be treated as the primary axis?
- Are the clear values and shader decode mapping stated correctly for all three modes?
- Is the failure cause analysis appropriately bounded, without preconceived driver-versus-hardware assumptions?

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge into a compact Level-3 bullet list covering transient attachment usage, lazy memory, and load/store across subpasses. Keep the ordinary-use framing of transient attachments.
- Use the two-axis Behavior Parameters structure (attachment mode and memory-property mode) directly in the final page.
- Copy the two Failure Cause Mapping tables into the final page's Failure Meaning section.
- The shader is simple enough that a single representative walkthrough (color mode) suffices, with the depth and stencil decode differences noted in Parameter Variation Summary.
- Move the source mapping table to the Source Reference Appendix.
- Keep the registration hierarchy tree with the six direct leaves exactly as registered.
