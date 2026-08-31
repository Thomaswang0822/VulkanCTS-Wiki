# Understanding Brief: Protected Attachment Load Operation

## One-Sentence Test Purpose

This test checks whether `VK_ATTACHMENT_LOAD_OP_CLEAR` initializes a protected color attachment to the render-pass clear value before the image is sampled for validation.

## Background Knowledge

### Render-pass attachment load operations

A render pass chooses a load operation for each attachment. `VK_ATTACHMENT_LOAD_OP_CLEAR` writes the clear value supplied when the render pass begins, before any subpass commands need the attachment contents. This test ends the render pass without drawing, so the attachment load operation produces the image being checked.

Why it matters here:
- The clear is fixed-function render-pass behavior rather than a draw or transfer command.
- The attachment starts in `VK_IMAGE_LAYOUT_UNDEFINED`, so the expected pixels come from the load operation alone.

### Protected image execution

Protected memory restricts access to protected resources. The test creates a protected image, records work in a protected command buffer, and submits it to a protected queue. The validator then samples the image through its protected checking path.

Why it matters here:
- The render-pass operation and the image must use compatible protection states.
- Validation checks the result without exposing the protected image through a direct host readback.

## One Concrete Example

The static test case `clear_1` begins a render pass on a protected 128 by 128 `VK_FORMAT_R8G8B8A8_UNORM` image with the clear value `(1, 0, 0, 1)`. No draw call follows. After the render pass ends, the test makes color-attachment writes available to compute-shader reads. The validator samples four coordinates and expects red at each one.

## End-to-End Test Flow

```text
[host] select one static or base-seed-dependent random clear value and four reference records
[host] require protected-memory support and a protected queue
[host] create a protected 128 x 128 VK_FORMAT_R8G8B8A8_UNORM image, image view, render pass, and framebuffer
[host] allocate a primary command buffer from a protected command pool
[host] transition the image from VK_IMAGE_LAYOUT_UNDEFINED to VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
[host] begin the render pass with the selected clear value
[device] execute VK_ATTACHMENT_LOAD_OP_CLEAR for the color attachment
[host] end the render pass without recording a draw
[host] transition the image to VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL and make color writes visible to compute reads
[host] submit the protected command buffer and wait for completion
[host] run ImageValidator with four coordinates and four expected values
[host] pass when validation completes with all sampled values within the comparison threshold
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The tested operation does not use a test-core shader. `AttachmentLoadTestCase::initPrograms()` asks `ImageValidator` to register its `ResetSSBO` and `ImageValidator` compute programs. These programs check the result after the render pass; they do not initialize the attachment.

The static input set contains seven fixed clear/reference records. The random input set contains ten cases generated from the command-line base seed. Each random case generates one clear value, four sample coordinates, and four expected values equal to that clear value.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Protected color image | yes | yes, as a color attachment and sampled image | cleared by the render-pass load operation and sampled by validation | no | Holds the fixed-function result under test. |
| Color image view and framebuffer | yes | yes | select the image subresource used by the render pass | no | Connect the protected image to the color attachment. |
| Host-visible validator references | yes | yes, as validator input | read by the validator compute shader | initialized by host | Carry four coordinates and four expected values. |
| Protected validator helper buffer | yes | yes, as storage | reset and used by validator programs | no direct host image readback | Supports protected result checking. |

## What Is Checked

- `ImageValidator::validateImage()` samples the final image at four supplied coordinates.
- Each sampled `vec4` must match its expected value within an absolute per-component threshold of `0.1`.
- Static cases expect their fixed clear value at all four coordinates. Random cases generate the clear value and matching expected values together.
- A validator mismatch prevents validation from completing. The test reports pass when `validateImage()` returns true.

## Behavior Parameter Identification

> **Behavior parameter:** input set
>
> **Candidate values:** `static`, `random`

Both values exercise the same attachment load operation. They differ in how the clear value and reference records are chosen. No other behavioral dimension is registered below `load_op`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `static` | Protected render-pass attachment initialization, image state transitions, fixed reference handling, or image validation failed for a known clear value. |
| `random` | Protected render-pass attachment initialization, image state transitions, seeded input/reference generation, or image validation failed for a generated clear value. |

Both values share the protected image, render-pass, submission, and validator path. A failure in either value can come from common infrastructure rather than the input-set construction.

## Important Variations and Special Cases

- `static` registers `clear_1` through `clear_7` with fixed RGBA values. The values include opaque primary colors, alpha variations, and a mixed fractional color.
- `random` registers `clear_1` through `clear_10`. A `de::Random` instance seeded from the command-line base seed creates each clear value and four sample coordinates.
- The image format, 128 by 128 extent, primary command-buffer form, attachment count, mip level, and array layer remain fixed.
- The render pass contains no draw. This keeps the observed image contents attributable to the attachment load operation.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test case support and validator setup | [`AttachmentLoadTestCase`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L71-L102) | Requires protected context support and initializes validator programs. |
| Protected attachment and command setup | [`AttachmentLoadTestInstance::iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L114-L138) | Creates the protected image, render-pass objects, and protected primary command buffer. |
| Layout transition and render-pass load operation | [`render-pass recording`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L140-L167) | Transitions the image, supplies the clear value, and ends the render pass without drawing. |
| Final barrier, submission, and result | [`submit and validate`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L168-L211) | Makes the image shader-readable, submits protected work, and calls `validateImage()`. |
| Static and random registration | [`createAttachmentLoadTests`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L216-L350) | Defines seven fixed cases, ten seeded random cases, and the registered hierarchy. |
| Protected support requirements | [`checkProtectedContextSupport`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127) | Checks the API, protected-memory feature, and protected queue. |
| Render-pass helper | [`createRenderPass`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L399-L405) | Routes creation through the common single-color render-pass helper. |
| Common render-pass construction | [`makeRenderPass`](../../../framework/vulkan/vkObjUtil.cpp#L614-L690) | Defines the attachment load operation and layouts used by the helper. |
| Validator shader and comparison | [`ImageValidator::initPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Defines the sampling check, threshold, and mismatch path. |
| Validator resources and dispatch | [`ImageValidator::validateImage`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Binds the protected image and reference data and executes validation. |

## Questions / Risk Points for User Audit

- Is `input set` the clearest name for the `static` and `random` behavioral axis?
- Is the distinction between fixed-function `VK_ATTACHMENT_LOAD_OP_CLEAR` and validator compute shaders explicit enough?
- Does the four-coordinate validation scope avoid implying a full host image readback?
- Is the protected-resource explanation limited to behavior established by the source and support checks?

The inspected source resolves the operation, hierarchy, input counts, image setup, synchronization, and validation path. No unresolved point changes the final page's behavior or failure claims.

## Conversion Notes for Final Wiki Rewrite

- Distill the background to attachment load semantics and protected execution compatibility.
- Carry `input set` with values `static` and `random` into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table into the final page unchanged.
- Keep `## Shader Analysis` concise. The render-pass load operation is fixed-function, while the compute programs belong to validation infrastructure.
- Put the image transitions, render-pass begin/end sequence, four-sample check, and threshold in runtime and failure sections.
- Keep source entry points in the appendix and preserve exact registered identifiers.
