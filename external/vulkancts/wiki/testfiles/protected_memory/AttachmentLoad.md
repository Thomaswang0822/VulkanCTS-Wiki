## Overview

**Core question:** Does a protected render-pass attachment load operation write the selected clear value into the attachment?

- This page covers `vktProtectedMemAttachmentLoadTests.cpp`, which implements `protected_memory.attachment.load_op`.
- The test creates one protected 128 x 128 `VK_FORMAT_R8G8B8A8_UNORM` color image and begins a render pass whose color attachment uses `VK_ATTACHMENT_LOAD_OP_CLEAR`.
- It records no draw. The attachment load operation must produce the image contents from the clear value supplied to `vkCmdBeginRenderPass`.
- Seven `static` test cases use fixed clear/reference data. Ten `random` test cases derive clear values and reference records from the command-line base seed.
- The test samples four positions after protected submission and compares them with the selected clear value.

## Background Knowledge

- A render-pass attachment load operation runs when a render pass begins. `VK_ATTACHMENT_LOAD_OP_CLEAR` initializes the attachment from the corresponding `VkClearValue` before subpass work uses it.
- Protected command buffers can access protected resources when submitted through a compatible protected queue path. This test keeps the color image, command pool, command buffer, and submission in the protected path.

## Registration Hierarchy

```text
protected_memory.attachment.load_op
├── static
└── random
```

Each intermediate node contains test case leaves named `clear_1` onward. `static` has seven leaves and `random` has ten.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Input set | `static`, `random` | Selects fixed clear/reference records or ten records generated from the command-line base seed. | [`createAttachmentLoadTests`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L216-L350) |
| Static test case leaf | `clear_1` through `clear_7` | Selects one fixed `VkClearValue` and four expected samples. | [`testData`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L218-L314) |
| Random test case leaf | `clear_1` through `clear_10` | Selects one generated clear value, four generated coordinates, and four expected values equal to the clear value. | [`random case construction`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L326-L345) |
| Color image | `VK_FORMAT_R8G8B8A8_UNORM`, 128 x 128 | Fixes the attachment representation and extent for all cases. | [`AttachmentLoadTestInstance::iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L114-L130) |
| Command-buffer form | primary | Records the render pass and image barriers in one protected primary command buffer. | [`command-buffer setup`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L133-L138) |

## Behavior Parameters

The primary behavioral axis is the input set. Both values run the same protected render-pass operation, but they choose the clear and reference data in different ways.

### static: fixed clear and reference data

`static` registers seven known RGBA clear values. Each case supplies the same selected value as the expected result at four coordinates, which makes a failure reproducible without reconstructing random input.

### random: seeded clear and reference data

`random` registers ten cases. A `de::Random` instance uses the command-line base seed to generate each clear value and four coordinates. The case expects the generated clear value at every generated coordinate, extending input coverage without changing the render-pass mechanism.

## Shader Analysis

The operation under test is the fixed-function `VK_ATTACHMENT_LOAD_OP_CLEAR` behavior at render-pass begin, so there is no test-core shader to walk through. `AttachmentLoadTestCase::initPrograms()` registers the `ResetSSBO` and `ImageValidator` compute programs for result checking. `ResetSSBO` resets the protected helper buffer; `ImageValidator` samples and compares the completed image. Neither shader performs the attachment load operation.

## Runtime Execution and Result Checking

- `AttachmentLoadTestCase::checkSupport()` calls `checkProtectedContextSupport()`, which requires the protected-memory execution path and a protected queue.
- The test creates one protected 2D image with color-attachment and sampled-image usage. It uses `VK_FORMAT_R8G8B8A8_UNORM`, one mip level, one array layer, and a 128 x 128 extent.
- An image view, one-color render pass, and framebuffer bind that image as the attachment. The test allocates a primary command buffer from a protected command pool.
- The first image barrier changes the image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`. Its destination access includes `VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT`.
- The test begins the render pass with the case's `VkClearValue` and ends it without recording a draw. The attachment load operation supplies the checked color without a draw or another render-pass write.
- The final barrier changes the image to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`. It makes color-attachment writes available to compute-shader reads.
- The test submits the protected primary command buffer and waits on a fence.
- `ImageValidator::validateImage()` receives four coordinates and four expected `tcu::Vec4` values. Its compute validator samples the protected image and compares each component with an absolute threshold of `0.1`.
- A comparison mismatch enters the validator's error path and prevents validation from completing. The test passes when `validateImage()` returns true.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `static` | Protected render-pass attachment initialization, image state transitions, fixed reference handling, or image validation failed for a known clear value. |
| `random` | Protected render-pass attachment initialization, image state transitions, seeded input/reference generation, or image validation failed for a generated clear value. |

Both values share the protected image, render-pass, submission, and validator path. A failure in either value can come from common infrastructure rather than the input-set construction.

### Cause Analysis

#### Protected attachment initialization

**Possible failure symptoms:** One or more validator samples differ from the selected clear value by more than `0.1`, so validation does not return success. A static failure identifies the exact clear value from the test case name and log; a random failure also depends on the recorded base seed.

**Possible implementation causes:** The render pass may fail to apply `VK_ATTACHMENT_LOAD_OP_CLEAR` to the protected color attachment, may use the wrong `VkClearValue`, or may store an incorrect `VK_FORMAT_R8G8B8A8_UNORM` result. The source records no draw that could replace the load result. A more specific cause requires inspection of the failing clear value and implementation path.

#### Protected image state and submission

**Possible failure symptoms:** The protected submission fails, or the validator cannot observe the color-attachment result after the final layout transition and access dependency.

**Possible implementation causes:** The protected command-buffer and image path may be incompatible, the transition into color-attachment layout may fail, or the final barrier may not make color writes available to compute reads. The test supplies a protected image, protected command pool, protected submission, and explicit barriers. The failing command and validation log are needed to distinguish these paths.

#### Image validation

**Possible failure symptoms:** Validation does not complete after sampling one or more of the four supplied coordinates. The test checks four samples; it does not compare every texel through a host image readback.

**Possible implementation causes:** The validator may receive incorrect reference data, sample the wrong image state, or compare an incorrect sampled value. Since the same validator path serves both input sets, matching failures in `static` and `random` can indicate shared validation or visibility behavior. Source-level investigation is needed to identify a more specific cause.

## Case Pruning

### Requirement-based pruning

- `checkProtectedContextSupport()` rejects configurations that do not provide the required protected-memory execution path and protected queue support.
- The test requires the protected image to support its fixed color-attachment and sampled-image uses with `VK_FORMAT_R8G8B8A8_UNORM`.

### Design-based pruning

- The test fixes the format, 128 x 128 extent, one color attachment, one mip level, one array layer, and primary command-buffer form. It does not generate format, size, attachment-count, or secondary-command-buffer variants.
- `static` contains seven hand-written cases. `random` contains ten base-seed-dependent cases. Both sets use the same render-pass and validation flow.
- Validation samples four supplied coordinates rather than comparing every image location. This bounds what each passing case establishes.

## Key Takeaways

- The image contents come from `VK_ATTACHMENT_LOAD_OP_CLEAR`; no draw or transfer command writes the checked attachment.
- `static` and `random` vary clear/reference input construction while preserving the same protected render-pass path.
- The image moves from undefined state to color-attachment use, then to shader-readable state for four-sample validation.
- Validator compute shaders check the result but do not implement the operation under test.
- A failure can involve attachment initialization, protected image state and submission, input/reference handling, or validation. The behavior value and failing sample help narrow the investigation without identifying a bug location in advance.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Support checks and validator program setup | [`AttachmentLoadTestCase`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L71-L102) | Requires protected support, creates the instance, and registers validator programs. |
| Protected image and command setup | [`AttachmentLoadTestInstance::iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L114-L138) | Creates the protected attachment, render-pass objects, and primary command buffer. |
| Initial transition and attachment load | [`render-pass recording`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L140-L167) | Transitions the image and begins the render pass with the selected clear value. |
| Final transition, protected submission, and result | [`submit and validate`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L168-L211) | Makes the image shader-readable, submits the command buffer, and returns the validator result. |
| Registered input matrix | [`createAttachmentLoadTests`](../../../modules/vulkan/protected_memory/vktProtectedMemAttachmentLoadTests.cpp#L216-L350) | Defines the seven static cases, ten random cases, and registered hierarchy. |
| Protected context requirements | [`checkProtectedContextSupport`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127) | Checks API support, protected memory, and protected queue availability. |
| Render-pass helper | [`createRenderPass`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L399-L405) | Creates the common single-color render pass used by the test. |
| Validator shader and threshold | [`ImageValidator::initPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L47-L115) | Defines the compute sampling comparison, `0.1` threshold, and error path. |
| Validator resources and submission | [`ImageValidator::validateImage`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L264) | Binds references and the sampled image, then executes protected validation. |
