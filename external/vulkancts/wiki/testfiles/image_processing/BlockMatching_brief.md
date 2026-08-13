# Understanding Brief: image_processing block_matching

## One-Sentence Test Purpose

This test checks whether `textureBlockMatchSADQCOM` and `textureBlockMatchSSDQCOM` produce the expected block error for graphics and compute execution across image, sampler, descriptor, and pipeline variants.

## Background Knowledge

### Block matching and error metrics

A block-matching operation compares a rectangular target region with a rectangular reference region and returns a per-component error metric. Sum of absolute differences (SAD) accumulates absolute channel differences; sum of squared differences (SSD) accumulates their squares. A zero metric means the compared values match for the selected operation and region.

Why it matters here:
- The generated shader calls one of the two QCOM block-matching built-ins, selected by the registered `sad` or `ssd` test family.
- The host constructs the same comparison from the input buffers and uses it as the expected metric.

### Vulkan image views and sampler state

A shader samples an image through an image view and sampler. The view can change component interpretation through a swizzle, while the sampler controls address handling and reduction behavior. Image tiling and layout are properties of the image resources and affect whether the requested usage is supported and how the test binds them.

Why it matters here:
- Graphics-only parameter groups deliberately vary address modes, reduction modes, tiling, layouts, and component swizzles.
- The target and reference images can have different dimensions or coordinates, so a block can reach outside the target image and exercise the selected address rule.

## One Concrete Example

Consider a basic `sad` case for `VK_FORMAT_R8G8B8A8_UNORM` with a `32x32` block at `(0,0)` in two `64x64` images. The host fills the reference image and either copies its block into the target image (`same`) or fills the target block independently (`diff`). The generated shader calls `textureBlockMatchSADQCOM` with the two sampled textures, their samplers, the two coordinates, and the block size. It writes the metric to a storage buffer and colors the output green for a zero metric or red otherwise. The host computes the expected metric from the same input buffers and compares both the metric and output image.

This example is conceptual shorthand for the generated cases; the exact image format, coordinates, and match mode come from the registered path.

## End-to-End Test Flow

[host] Select operation, format, execution path, and one generated parameter set.

[host] Check `VK_QCOM_image_processing`, `textureBlockMatch`, block-match format features, image-format usage, output-image capabilities, and any path-specific pipeline or descriptor requirements.

[host] Allocate host-visible buffers, fill the target and reference regions, create 2D images and views, create samplers, and upload the buffers into the images.

[host] Generate GLSL 4.50 source with `GL_QCOM_image_processing`, compile it to SPIR-V 1.4, and create the graphics or compute pipeline.

[host] Push target coordinate, reference coordinate, and block size; submit a draw or dispatch; copy the output image and error buffer back to host-visible memory.

[device] Execute the QCOM block-matching built-in in the selected shader stage and write the metric to the storage buffer. The graphics path writes a color attachment; the compute path writes a storage image.

[host] Build a CPU reference result from the input buffers and compare the metric against a block-size- and format-derived tolerance. Compare the result image with an exact zero image threshold.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Graphics cases generate a vertex shader and fragment shader. Normally the fragment shader performs block matching; the `shader_stages.vertex` cases put the block-matching code in the vertex shader while the fragment shader passes through its input color.
- Compute cases generate one compute shader with `local_size_x/y/z = 1`. Each invocation reads the global invocation ID, performs block matching, and stores the red/green result in an output image.
- Both paths compile the generated GLSL with `VK_QCOM_image_processing` enabled and explicit `SPIRV_VERSION_1_4` shader build options.

### Bound resources and memory objects

- Binding 0: target block-match image.
- Binding 1: reference block-match image, or the target view again for compute `self` cases.
- Bindings 2 and 3: target and reference samplers.
- Binding 4: storage buffer containing the returned `vec4` error metric.
- Binding 5 in compute cases: storage output image.
- Push constants carry `targetCoord`, `referenceCoord`, and `blockSize`.

## What Is Checked

- The CPU reference uses the selected SAD or SSD operation, target/reference coordinates, block size, target component mapping, target address mode, and reference reduction mode.
- The GPU metric must be within `calculateErrorThreshold()`, which scales floating-point and format quantization allowances with the number of block elements.
- The GPU result image must match the CPU result image with an exact `(0,0,0,0)` image threshold.
- A graphics or compute case passes only when both checks pass.

## Behavior Parameter Identification

The primary behavioral axis is the registered test family and its execution/variation groups:

- `sad` and `ssd` select the operation and therefore the CPU metric calculation and generated built-in.
- `basic` varies format, same/different input data, random reference data, and optional constant difference.
- Graphics-only monolithic groups vary one resource or stage property at a time: `block_sizes`, `address_modes`, `reduction_modes`, `tiling`, `swizzles`, `layouts`, `shader_stages`, and `descriptors`.
- Compute `self` compares two regions of one image rather than two separate image resources.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `sad` | SAD built-in execution, input data setup, or SAD reference calculation mismatch. |
| `ssd` | SSD built-in execution, input data setup, or SSD reference calculation mismatch. |
| `basic` | Baseline image/descriptor setup, shader execution, output transfer, or metric/image comparison failure. |
| `block_sizes` | Block coordinate/extent handling or boundary-sensitive block matching failure. |
| `address_modes` | Address-mode handling for out-of-range coordinates or blocks. |
| `reduction_modes` | Target/reference sampler reduction-mode interaction. |
| `tiling` | Block matching with linear/optimal image tiling combinations. |
| `swizzles` | Reference-image component mapping or metric interpretation. |
| `layouts` | Image layout handling for the target/reference sampling path. |
| `shader_stages` | Block matching in a non-fragment graphics shader stage. |
| `descriptors` | Update-after-bind descriptor update or consumption. |
| `self` | Matching two non-overlapping regions of a single image and its single-image descriptor path. |

### Cause Analysis

#### Operation or input-data mismatch

**Possible failure symptoms:** The returned error metric differs from the CPU reference by more than the calculated threshold, or a case intended to match produces a non-matching result image.

**Possible implementation causes:** The relevant QCOM built-in may be executed incorrectly, or the image contents, coordinates, format conversion, or operation selection may not agree between the device path and the host reference. The test does not isolate those causes further.

#### Resource-state or variant-handling mismatch

**Possible failure symptoms:** A failure is confined to a tiling, layout, swizzle, address-mode, reduction-mode, shader-stage, descriptor, or block-size group while the baseline path passes.

**Possible implementation causes:** The implementation may mishandle the selected image/sampler/view state or the variant's pipeline/descriptor setup. Source-level investigation is needed to distinguish API-state handling from the image-processing operation itself.

#### Output or copyback mismatch

**Possible failure symptoms:** The metric is acceptable but the result image comparison fails, or host-visible result data does not match the expected output.

**Possible implementation causes:** The output image write, image-to-buffer transfer, layout transition, or host visibility path may be incorrect. The test reports the comparison failure but does not localize the responsible stage.

## Important Variations and Special Cases

- Extended graphics groups are registered only for monolithic pipelines. `fast_lib` and `shader_objects` retain the `basic` group; compute retains `basic` plus `self`.
- `same` cases copy the reference block into the target block. `diff` cases fill the target block independently. `_random` changes generated reference colors; `_constdiff` adds a constant difference to copied source colors and is excluded for `same` cases.
- The compute `self` path uses target coordinates `(0,0)` and reference coordinates `(32,32)` in one `64x64` image. Overlapping self-test regions are intentionally not generated by the implementation.

## Source Mapping

- Registration and operation/group generation: `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1881-L2268`.
- Shared support checks: `external/vulkancts/modules/vulkan/image_processing/vktImageProcessingBase.cpp#L92-L168` and `vktImageProcessingBlockMatchingTests.cpp#L141-L272`.
- Generated graphics shaders: `vktImageProcessingBlockMatchingTests.cpp#L275-L369`.
- Generated compute shader: `vktImageProcessingBlockMatchingTests.cpp#L1195-L1218`.
- Runtime setup and checks: `vktImageProcessingBlockMatchingTests.cpp#L460-L773`, `#L960-L1129`, `#L1306-L1449`, and `#L1512-L1642`.
- Operation names and supported formats: `vktImageProcessingTestsUtil.cpp#L250-L255` and `#L408-L435`.

## Questions / Risk Points for User Audit

- The generated GLSL calls the extension built-ins through `getImageProcGLSLStr()`. A representative shader walkthrough should be generated only after selecting an exact mustpass case and completing the shader-analyzer/shader-disassembler round trip.
- The block-matching source contains support branches for weighted sampling and box filtering, but the current registration table adds only `sad` and `ssd`; this brief treats the registered scope as authoritative.

## Conversion Notes for Final Wiki Rewrite

- Keep exact registration identifiers and preserve the distinction between test families, intermediate nodes, and test case leaves.
- The final page should explain the generated shader and host/device data flow without copying this brief's scaffolding wholesale.
- If a shader walkthrough is included, its complete generated `#### SPIR-V` subsection must remain the final subsection of the walkthrough.
