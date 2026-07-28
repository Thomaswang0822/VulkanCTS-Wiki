## Overview

**Core question:** When a fragment shader's output locations and a render pass's color attachments do not match one-to-one, does the implementation leave the unmatched attachment at its clear value and write the shader outputs to the matched attachments as expected?

- [vktApiFragmentShaderOutputTests.cpp](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp) implements the `fragment_shader_output` test family under the `api` test category. The same file holds the test logic, format-matrix generation, support checks, and registration.
- The family registers three intermediate nodes: `location_no_attachment`, `attachment_no_location`, and `different_signedness`. The first two exercise shader/attachment location mismatches in opposite directions. The third exercises render passes whose two color attachments use shader/render format pairs drawn from a same-integer-class matrix.
- The core test idea is pixel-level verification: the test renders a triangle into multiple `R8` color attachments, copies each attachment back to a host-visible buffer, and compares per-pixel values against an expected value derived from the case type.
- The page covers the registered path matrix, the per-intermediate-node behavior, runtime setup, the pass/fail rule, and what a failure points to. It does not analyze shaders because the fragment shader is generated test infrastructure whose only role is to write a known value to each output location.
- The family is registered unconditionally; `createApiTests()` attaches it to the `api` test category at [vktApiTests.cpp#L134](../../../modules/vulkan/api/vktApiTests.cpp#L134).

## Background Knowledge

- **Render pass color attachments.** A render pass declares a list of color attachments through `pColorAttachments` of `VkSubpassDescription`. Each entry references an attachment index in the render pass's `pAttachments` array. The framebuffer must provide a compatible image view for each declared attachment.
- **Fragment shader output locations.** A fragment shader declares its color outputs with `layout(location = N) out <type> colorN`. Vulkan binds shader output locations to color attachment indices one-to-one by default: location `N` writes to `pColorAttachments[N]`. If a shader output has no corresponding color attachment, or a color attachment has no corresponding shader output, the unmatched side is not an error; the unmatched shader output is discarded and the unmatched attachment is left at its `loadOp` result.
- **`R8` format classes used by this test.** The four formats used here split into two classes. `VK_FORMAT_R8_UNORM` and `VK_FORMAT_R8_SNORM` are normalized floating-point formats. `VK_FORMAT_R8_UINT` and `VK_FORMAT_R8_SINT` are integer formats. The host-side checker treats integer formats as bit-pattern-preserving and normalized formats as float-compared against `1.0f`.

## Registration Hierarchy

```text
api.fragment_shader_output
├── location_no_attachment
├── attachment_no_location
└── different_signedness
```

`createFragmentShaderOutputTests` creates the `fragment_shader_output` test family and is attached to the `api` test category by [vktApiTests.cpp#L134](../../../modules/vulkan/api/vktApiTests.cpp#L134). The three intermediate nodes are registered from the local `cases[]` table at [vktApiFragmentShaderOutputTests.cpp#L706-L715](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L706-L715); the same loop also drives the per-node leaf generation at [vktApiFragmentShaderOutputTests.cpp#L730-L768](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L730-L768).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `location_no_attachment`, `attachment_no_location`, `different_signedness` | Selects which shader/attachment interface property is exercised: shader output without attachment, attachment without shader output, or two-attachment combinations from the same-class format matrix. | [cases[] table](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L706-L715) |
| Shader format | `VK_FORMAT_R8_UNORM`, `VK_FORMAT_R8_SNORM`, `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT` | The format declared in the shader's `layout(location = N) out <type>` declaration. Selects the output vector type (`vec4`, `ivec4`, or `uvec4`) and the value written. | [formatsWithNames](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L700-L705), [initPrograms type/value lambdas](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L295-L322) |
| Render format | `VK_FORMAT_R8_UNORM`, `VK_FORMAT_R8_SNORM`, `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT` | The format of the color attachment image and image view. The host-side checker reads back pixels according to this format. | [formatsWithNames](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L700-L705) |
| Render size | `64x64` | Hard-coded render area. Every leaf uses the same fixed size. | [iterate](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L599-L600) |
| Attachment count | 4 for `location_no_attachment` and `attachment_no_location`; 2 for `different_signedness` | Number of color attachments bound to the render pass. The mismatched-location branches use 4 attachments so the magic location index `attachments/2 = 2` is the unmatched slot; the signedness branch uses 2 attachments so each combination has one same-class pair per attachment. | [iterate](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L613), [different_signedness registration loop](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L735-L749) |

The full leaf matrix is enumerated in the mustpass file under `dEQP-VK.api.fragment_shader_output.*` (86 leaves total: 23 for `location_no_attachment`, 23 for `attachment_no_location`, 40 for `different_signedness`).

## Behavior Parameters

The primary behavioral axis is the intermediate node. Each value changes both the shader generation and the host-side verification rule.

### `location_no_attachment`: Shader output location with no matching attachment

The shader writes to a location that is beyond the `pColorAttachments` array. For an attachment count of 4, the test picks `magicLoc = attachments/2 = 2` and reroutes the shader output that would normally target location 2 to `location = attachments` (location 4) instead. Locations 0, 1, and 3 keep their original declarations. The render pass still declares only attachments 0 through 3, so the shader output at location 4 has no corresponding attachment and is discarded; attachment 2 receives no shader write and stays at its clear value.

The leaf matrix is generated by walking every permutation of the four `R8` formats through [`std::next_permutation`](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L755) over `formatsWithNames`. Each permutation assigns one format to each of the four attachments, with the shader format equal to the render format for every attachment. The `while` loop body only runs after the first `next_permutation` call returns true, so the initial sorted permutation is skipped and 23 leaves result.

Verification requires the magic-location attachment to be unchanged from its clear color and every other attachment to contain the shader-written value. The check is performed by `isBufferUnchanged` and `isBufferRendered` at [vktApiFragmentShaderOutputTests.cpp#L566-L576](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L566-L576).

### `attachment_no_location`: Attachment with no matching shader output location

The shader skips writing to `magicLoc`, while the render pass still declares an attachment at that index. The shader has outputs at locations 0, 1, and 3, but no output at location 2. Attachment 2 receives no shader write and must remain at its clear color.

The leaf matrix is generated by the same permutation loop as `location_no_attachment` and produces 23 leaves with the same set of format orderings. The only difference from `location_no_attachment` is the shader generation branch: the skipped location emits no `layout(location = ...) out` declaration and no write statement, instead of rerouting the declaration to a higher location. See [initPrograms](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L326-L354).

Verification uses the same `isBufferUnchanged`/`isBufferRendered` rule as `location_no_attachment`.

### `different_signedness`: Two-attachment combinations from a same-class format matrix

Each leaf has exactly two color attachments. The (shaderFormat, renderFormat) pair for each attachment is drawn from `signednessFormats`, a list built at [vktApiFragmentShaderOutputTests.cpp#L717-L726](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L717-L726) by keeping only pairs whose two formats share the same integer/non-integer class: both `R8_UINT`/`R8_SINT` (integer) or both `R8_UNORM`/`R8_SNORM` (non-integer). The registration loop at [vktApiFragmentShaderOutputTests.cpp#L735-L749](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L735-L749) combines two such pairs into a single test. The two pairs must differ in both shader format and render format, so no two attachments repeat the same shader format or the same render format.

The resulting 40 leaves cover a mix of within-class mismatches and cross-class pairings: each attachment may have shader/render types that differ within the same class (for example `sint` shader to `uint` render, or `unorm` shader to `snorm` render), and the two attachments may sit in the same class (for example `sint2sint` + `uint2uint`) or in different classes (for example `sint2sint` + `snorm2snorm`).

Verification requires every attachment to be rendered with the shader-written value. The check is performed by `isBufferRendered` at [vktApiFragmentShaderOutputTests.cpp#L578-L583](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L578-L583). The expected value follows bit-pattern preservation for integer attachments: a `sint` shader output (`111`) read back from a `uint` attachment must equal `111`, and a `uint` shader output (`123`) read back from a `sint` attachment must equal `123`. For `unorm`/`snorm` attachments, the expected value is `1.0f`.

## Shader Analysis

The shaders generated by [initPrograms](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L291-L368) are test infrastructure used to verify the fragment output interface, not the behavior under test. The fragment shader writes a single known constant to each output location; the choice of constant depends only on the shader format (normalized formats write `(1.0, 1.0, 1.0, 1.0)`, `R8_UINT` writes `(123, 123, 123, 123)`, `R8_SINT` writes `(111, 111, 111, 111)`). The vertex shader is a fixed pass-through that emits a full-screen triangle pair. No representative shader walkthrough is provided because the shader logic does not encode the tested behavior; the tested behavior is the host-side interface contract between shader output locations and render pass attachments.

## Runtime Execution and Result Checking

[iterate](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L591-L666) runs the same host-side sequence for every leaf:

- Creates a vertex shader module and a fragment shader module from the program collection built by `initPrograms`.
- Allocates a host-visible vertex buffer holding two triangles that cover the 64x64 render area and copies the vertex data into it.
- For each attachment: creates a color image with `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT`, a host-visible transfer destination buffer sized to one pixel per format element, and an image view.
- Builds a render pass with `VK_ATTACHMENT_LOAD_OP_CLEAR` and `VK_ATTACHMENT_STORE_OP_STORE` for every attachment, with `finalLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` so the next step can copy directly.
- Builds a framebuffer, an empty pipeline layout, and a graphics pipeline whose `VkPipelineColorBlendStateCreateInfo::attachmentCount` matches the attachment count, with `colorWriteMask` set to all RGBA bits.
- Begins a command buffer, binds the pipeline and vertex buffer, begins the render pass with per-attachment clear colors produced by [makeClearColors](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L431-L459), draws the triangle pair, ends the render pass, inserts a `VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT` → `VK_PIPELINE_STAGE_TRANSFER_BIT` memory barrier, and copies each attachment image to its paired buffer.
- Submits the command buffer and waits.
- Calls [verifyResults](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L465-L589) which scans every pixel of every attachment buffer through `tcu::ConstPixelBufferAccess` and returns the pass/fail verdict.

Clear colors are constructed so that each attachment has a distinct, recoverable value: [makeClearColors](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L431-L459) walks the render formats and assigns decrementing per-component values for `unorm` (floats starting at `0.25`), `uint` (unsigned starting at `64`), and `sint`/`snorm` (signed starting at `32`). The exact clear values feed the `isBufferUnchanged` check, not a fixed expected-value table.

The pass/fail condition depends on the intermediate node:

- `location_no_attachment` and `attachment_no_location`: the magic-location attachment (`attachments/2`) must match its clear color exactly, and every other attachment must match its shader-written expected value.
- `different_signedness`: every attachment must match its shader-written expected value.

A leaf returns `tcu::TestStatus::pass` if `verifyResults` returns true, otherwise `tcu::TestStatus::fail` with the message `"One or more attachments rendered incorrectly"`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `location_no_attachment` | Unmatched shader output not discarded; unmatched attachment overwritten; wrong attachment index written by the shader-to-attachment binding. |
| `attachment_no_location` | Unmatched attachment overwritten despite no shader output; shader output locations shifted or compacted. |
| `different_signedness` | Integer bit-pattern not preserved across `sint`/`uint` shader/attachment pairs; normalized value not written as expected for `unorm`/`snorm` pairs; wrong attachment written due to cross-attachment format confusion. |
| All branches (shared) | Attachment clear value not applied; copy-back image layout or barrier mishandled; pixel readback interpretation mismatch. |

### Cause Analysis

#### Unmatched shader output not discarded

**Possible failure symptoms:** In a `location_no_attachment` leaf, the magic-location attachment contains the shader-written value (for example `123`, `111`, or `1.0f`) instead of its clear color. `isBufferUnchanged` returns false for that attachment.

**Possible implementation causes:** The implementation routes the shader output at `location = attachments` (location 4) to attachment 2 instead of discarding it, or compacts shader output locations so the high location aliases an existing attachment. Vulkan specifies that shader outputs without a matching color attachment are discarded; routing them to a different attachment would be an implementation defect. Source-level investigation is needed to confirm whether the failure is in shader output location assignment or in pipeline/attachment binding.

#### Unmatched attachment overwritten

**Possible failure symptoms:** In an `attachment_no_location` leaf, the magic-location attachment contains the shader-written value for a neighboring attachment instead of its clear color, or contains any value other than the clear color. `isBufferUnchanged` returns false.

**Possible implementation causes:** The implementation writes to attachment 2 even though no shader output targets location 2, or it shifts shader output locations so that an output for location 3 (or 1) lands on attachment 2. Vulkan specifies that an attachment with no matching shader output retains its `loadOp` result. Confirmation requires source-level investigation into how the driver maps shader output locations to attachment indices.

#### Wrong attachment index written by the shader-to-attachment binding

**Possible failure symptoms:** In a `location_no_attachment` or `attachment_no_location` leaf, the magic-location attachment is unchanged but one of the other attachments (for example attachment 3) contains an unexpected value: either the value meant for a different location, or the clear color.

**Possible implementation causes:** The pipeline's color blend state or the driver's location-to-attachment mapping is offset or scrambled, so the shader output for location `N` is written to attachment `M` with `N != M`. The pipeline is created with `attachmentCount` matching the render pass at [createGraphicsPipeline](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L174-L194), so a miscount on the implementation side would surface here. Source-level investigation is needed to localize the offset.

#### Integer bit-pattern not preserved across same-class pairs

**Possible failure symptoms:** In a `different_signedness` leaf with a `sint` shader and `uint` render format (or the reverse), the readback value differs from the shader-written constant. For example, a `sint` shader output of `111` read back from a `uint` attachment is not `111`.

**Possible implementation causes:** The implementation converts the integer shader output instead of writing the raw bits, or it sign-extends/truncates in a way that changes the value. Vulkan specifies that integer shader outputs are written bit-for-bit to integer attachments of the same class. Source-level investigation is needed to determine whether the issue is in shader output conversion, attachment write, or pixel readback.

#### Normalized value not written as expected

**Possible failure symptoms:** In a `different_signedness` leaf with a `unorm` or `snorm` render attachment, the readback pixel is not `1.0f` (within the `0.001f` tolerance used by the float comparator).

**Possible implementation causes:** The implementation writes a different normalized value, applies unexpected clamping, or stores the value in a way that does not round-trip through `R8_UNORM`/`R8_SNORM`. Source-level investigation is needed to determine whether the issue is in shader output conversion or in attachment storage.

#### Cross-attachment format confusion

**Possible failure symptoms:** In a `different_signedness` leaf, one attachment contains the value expected for the other attachment, suggesting the two attachments' formats or shader outputs were swapped.

**Possible implementation causes:** The pipeline's color blend attachment state or the render pass's `pColorAttachments` array maps the two attachments to the wrong shader output locations. The pipeline is built with `attachmentCount = 2` and one `VkPipelineColorBlendAttachmentState` per attachment at [createGraphicsPipeline](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L181-L188); a misalignment in the driver's handling of that array could swap the bindings. Source-level investigation is needed to confirm.

#### Shared infrastructure failures (all branches)

**Possible failure symptoms:** Across all three intermediate nodes, attachments do not match their expected values in patterns that do not track the per-node rules above. Clear colors may not appear where expected; shader-written values may not appear where expected.

**Possible implementation causes:** The render pass `loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR` is not honored, the `VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT` → `VK_PIPELINE_STAGE_TRANSFER_BIT` barrier at [iterate](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L652-L653) does not correctly synchronize the color attachment writes before the image-to-buffer copy, or the host-side `tcu::ConstPixelBufferAccess` interpretation of the readback buffer does not match the render format. These causes affect every leaf and would surface across all three intermediate nodes.

## Case Pruning

### Requirement-based pruning

- `maxColorAttachments` must be at least `attachments + 1` for `location_no_attachment` (because the shader output reroutes to location `attachments`, which is one beyond the highest attachment index) and at least `attachments` for the other two intermediate nodes. Checked at [checkSupport](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L251-L272); leaves that exceed the limit raise `NotSupportedError` and are skipped on the current device.
- Every render format must support `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT | VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` in `optimalTilingFeatures`. Checked at [checkSupport](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L276-L288); leaves with an unsupported format raise `NotSupportedError`. In practice the four `R8` formats are widely supported, so this check rarely prunes on desktop implementations.

### Design-based pruning

- The `location_no_attachment` and `attachment_no_location` branches walk only the permutations returned by `std::next_permutation` starting from the sorted `formatsWithNames` vector. The initial sorted permutation is not emitted as a leaf because the `while` loop body only runs after the first `next_permutation` call returns true. The result is 23 leaves out of the 24 possible permutations of four distinct formats. See [vktApiFragmentShaderOutputTests.cpp#L753-L766](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L753-L766).
- The `different_signedness` branch restricts each attachment's (shaderFormat, renderFormat) pair to same-class combinations through `signednessFormats`. Cross-class pairs (for example `sint` shader to `unorm` render) are intentionally excluded from the matrix; this is a design choice, not a hardware requirement. See [vktApiFragmentShaderOutputTests.cpp#L717-L726](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L717-L726).
- The `different_signedness` registration loop skips any pair of `signednessFormats` entries that share a shader format or a render format, so no leaf repeats the same shader format or the same render format across its two attachments. See [vktApiFragmentShaderOutputTests.cpp#L738-L740](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L738-L740).
- The shader format and render format are always identical for the `location_no_attachment` and `attachment_no_location` branches; the permutation varies only the assignment of formats to attachment slots. See [vktApiFragmentShaderOutputTests.cpp#L760-L763](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L760-L763).

## Key Takeaways

- The `fragment_shader_output` test family verifies the shader-to-attachment binding contract for color outputs: an unmatched shader output must be discarded, and an unmatched attachment must retain its clear value.
- `location_no_attachment` and `attachment_no_location` are mirror images. The first reroutes a shader output to a high location with no attachment; the second omits a shader output for an existing attachment. Both expect the magic-location attachment to remain at its clear color.
- `different_signedness` restricts each attachment's shader/render format pair to a same-integer-class combination, then combines two such pairs into one render pass. The expected value follows bit-pattern preservation for integer pairs and `1.0f` for normalized pairs.
- All verification is host-side pixel scanning of readback buffers. There is no validation-layer pass/fail path; the test reports `pass` or `fail` based on per-pixel value comparison against the clear color or the shader-written constant.
- See `## Failure Meaning` for the cause analysis of mismatches in each branch.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parent registration in `createApiTests` | [vktApiTests.cpp#L134](../../../modules/vulkan/api/vktApiTests.cpp#L134) | Attaches `fragment_shader_output` to the `api` test category. |
| Family factory `createFragmentShaderOutputTests` | [vktApiFragmentShaderOutputTests.cpp#L698-L772](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L698-L772) | Builds the root group, the format matrix, the signedness-class filter, and the per-node leaf registration loops. |
| `formatsWithNames` declaration | [vktApiFragmentShaderOutputTests.cpp#L700-L705](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L700-L705) | The four `R8` formats and their integer/non-integer classification flag. |
| `cases[]` table | [vktApiFragmentShaderOutputTests.cpp#L706-L715](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L706-L715) | Maps each intermediate node name to its `ShaderOutputCases` enum and `signedness` flag. |
| `signednessFormats` build | [vktApiFragmentShaderOutputTests.cpp#L717-L726](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L717-L726) | Same-class (shader/render) pair filter used by the `different_signedness` branch. |
| `different_signedness` registration loop | [vktApiFragmentShaderOutputTests.cpp#L735-L749](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L735-L749) | Combines two same-class pairs into one two-attachment leaf, skipping shared shader or render formats. |
| Permutation registration loop | [vktApiFragmentShaderOutputTests.cpp#L753-L766](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L753-L766) | Generates the 23 leaves for each of `location_no_attachment` and `attachment_no_location`. |
| Shader generation `initPrograms` | [vktApiFragmentShaderOutputTests.cpp#L291-L368](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L291-L368) | Builds the fragment shader, including the `magicLoc` reroute (`LocationNoAttachment`) and the `magicLoc` skip (`AttachmentNoLocation`). |
| `magicLoc` computation | [vktApiFragmentShaderOutputTests.cpp#L324](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L324) | `attachments / 2` selects the unmatched location index. |
| Render pass creation `createColorRenderPass` | [vktApiFragmentShaderOutputTests.cpp#L116-L172](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L116-L172) | Builds the multi-attachment render pass with `loadOp = CLEAR`, `storeOp = STORE`, and `finalLayout = TRANSFER_SRC_OPTIMAL`. |
| Pipeline creation `createGraphicsPipeline` | [vktApiFragmentShaderOutputTests.cpp#L174-L194](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L174-L194) | Builds the graphics pipeline with one `VkPipelineColorBlendAttachmentState` per attachment. |
| Support checks `checkSupport` | [vktApiFragmentShaderOutputTests.cpp#L245-L289](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L245-L289) | Enforces `maxColorAttachments` and per-format `COLOR_ATTACHMENT_BIT | TRANSFER_SRC_BIT` support. |
| `makeClearColors` | [vktApiFragmentShaderOutputTests.cpp#L431-L459](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L431-L459) | Builds per-attachment clear colors used by `isBufferUnchanged`. |
| `verifyResults` | [vktApiFragmentShaderOutputTests.cpp#L465-L589](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L465-L589) | Host-side pixel scan; dispatches to `isBufferUnchanged`/`isBufferRendered` per intermediate node. |
| `isBufferUnchanged` and `isBufferRendered` | [vktApiFragmentShaderOutputTests.cpp#L475-L533](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L475-L533) | Per-attachment expected-value comparisons for clear-color and shader-written cases. |
| `iterate` | [vktApiFragmentShaderOutputTests.cpp#L591-L666](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L591-L666) | End-to-end host sequence: setup, draw, copy-back, verify, pass/fail return. |
| `TestConfig` and `ShaderOutputCases` | [vktApiFragmentShaderOutputTests.cpp#L57-L84](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L57-L84) | Configuration struct and enum that carry the per-leaf case type and format list. |
| Mustpass source | [mustpass/main/vk-default/api.txt](../../../mustpass/main/vk-default/api.txt) | Authoritative list of registered `dEQP-VK.api.fragment_shader_output.*` leaves. |
| Test header | [vktApiFragmentShaderOutputTests.hpp](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.hpp) | Declares `createFragmentShaderOutputTests`. |
