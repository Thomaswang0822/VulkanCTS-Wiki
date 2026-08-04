## Overview

**Core question:** Do graphics pipelines preserve the required behavior when uncommon interface, descriptor, layout, rendering, and color-write conditions change?

- [`vktPipelineMiscTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L1) implements the `pipeline.misc` test family. It groups compact tests that do not belong to a more specific pipeline family.
- The family combines three monolithic Amber test cases with direct C++ cases for `PrimitiveId`, shader interfaces, descriptor binding, compatible layouts, dynamic rendering, and masked color output.
- Different leaves observe pixels, storage-buffer data, or successful command completion. A failure does not always identify one pipeline stage, so this page separates the mechanisms and their oracle limits.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A `VkPipelineLayout` fixes the descriptor-set-layout sequence used when pipelines and descriptor sets are bound. Commands choose the destination set index, so applications can bind sets out of numerical order and can leave unused set indices unbound. The accessed descriptor interface still determines which bindings must be valid.
- The [`PrimitiveId` contract](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-primitiveid) gives a fragment shader the geometry shader's primitive index when that stage exists, or the value that would have reached it if no geometry shader is present. Tessellation and geometry capability rules constrain legal use.
- A per-attachment `colorWriteMask` controls which color components reach a color attachment. It does not remove fragment shader execution or its storage-buffer side effects, which lets a test use a storage buffer as the oracle while suppressing color writes.
- Dynamic rendering supplies attachment information at command recording. A graphics pipeline created for dynamic rendering can have no color attachment or, with the relevant feature, an attachment unused by that pipeline.

## Registration Hierarchy

```text
pipeline.monolithic.misc
├── position_to_ssbo
├── primitive_id_from_tess
├── layer_read_from_frag
├── implicit_primitive_id
├── implicit_primitive_id_with_tessellation
├── array_of_structs_interface
├── descriptor_bind_test_backwards
├── descriptor_bind_test_holes
├── descriptor_bind_test_backwards_holes
├── identically_defined_layout
├── no_rendering
├── no_rendering_unused_attachment
└── color_write_mask_none
```

This tree is the canonical monolithic registration in [`createMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2543-L2622). The monolithic mustpass file contains these 13 leaves in [`pipeline/monolithic/monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt#L190995-L191007).

Other construction paths register only supported parts of the family. Fast linked library adds `compatible_render_pass`, `interpolate_at_sample_no_sample_shading`, and `frag_lib_varying_samples_2`, `_4`, `_8`, and `_16`; its mustpass scope has 15 `misc` leaves. The four shader-object mustpass files each retain seven common leaves: `array_of_structs_interface`, `color_write_mask_none`, the three `descriptor_bind_test_*` leaves, and the two `implicit_primitive_id*` leaves.

## Parameter Dimensions and Observed Values

| Dimension | Observed values | Meaning in this test | Evidence |
|-----------|-----------------|----------------------|----------|
| Pipeline construction type | monolithic, pipeline-library variants, shader-object variants | Selects the registration subset and the `GraphicsPipelineWrapper` construction path. | [`createMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2543-L2622) |
| Built-in interface path | `implicit_primitive_id`, `implicit_primitive_id_with_tessellation`, Amber `primitive_id_from_tess`, Amber `layer_read_from_frag` | Changes the producing stages or the built-in value read by a later stage. | [primitive-ID shaders](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L201-L275) |
| Descriptor binding configuration | `descriptor_bind_test_backwards`, `descriptor_bind_test_holes`, `descriptor_bind_test_backwards_holes` | Reverses update/bind order, omits sets 1 and 2, or does both. | [`BindingTestConfig`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L786-L797) |
| Layout identity | normal same-object layout use; `identically_defined_layout` | The latter creates independently allocated descriptor-set layouts with the same binding definition but different immutable sampler objects for pipeline creation and descriptor binding. | [layout construction and bind](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2112-L2189) |
| Dynamic-rendering attachment form | `no_rendering`, `no_rendering_unused_attachment` | Sets `colorAttachmentCount` to zero or one. | [dynamic-rendering setup](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L1942-L1972) |
| Result oracle | color image, host-visible storage buffer, successful submission | Selects image comparison, exact buffer values, or completion-only validation. | [direct result checks](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L407-L435) |

## Behavior Parameters

The primary behavioral axis is the behavioral group of test case leaves. The following groups share a source file but change the contract or the observable result.

### `amber_builtin_and_storage_cases`: monolithic Amber coverage

`position_to_ssbo`, `primitive_id_from_tess`, and `layer_read_from_frag` load Amber scripts only under monolithic construction. Their feature lists respectively require vertex-pipeline stores and atomics, tessellation plus geometry shader support, and geometry shader support. Their detailed program and result definitions reside in the named `.amber` artifacts, not in generated C++ GLSL.

### `implicit_primitive_id*`: fragment primitive index with and without tessellation

The generated vertex shader creates two side-by-side primitives. The fragment shader selects red for an even `gl_PrimitiveID` and green for an odd one. The tessellation variant inserts tessellation control and evaluation stages and changes topology to `VK_PRIMITIVE_TOPOLOGY_PATCH_LIST`; both variants require geometry shader support, and the tessellation variant also requires `tessellationShader`.

### `array_of_structs_interface`: stage-interface transport

This leaf creates a pipeline whose stages communicate through an array-of-structs interface. It renders a 4 x 4 image and compares the result against `vec4(0.30, 0.90, 0.60, 1.0)` with a `0.02` RGB threshold.

### `descriptor_bind_test_*`: reverse and sparse descriptor-set binding

The three leaves create four uniform-buffer descriptor sets. Their configuration reverses the update and bind sequence, skips set indices 1 and 2, or combines both conditions. The draw binds only required sets and must yield a uniform green image.

### `pipeline_library_misc_cases`: library-specific compatibility and sample behavior

Library construction registers `compatible_render_pass`; fast linked library also registers the `interpolate_at_sample_no_sample_shading` experiment and four varying-sample leaves. The interpolation test executes the same shader path through monolithic and fast-linked construction, stores per-invocation values in buffers, and compares the observed data after sorting because invocation order is unspecified. The varying-sample leaves use dynamic rendering and standard sample locations to check interpolation results for 2, 4, 8, or 16 samples.

### `identically_defined_layout`: use a compatible pipeline layout at bind time

This monolithic leaf creates two separate combined-image-sampler descriptor-set layouts with the same binding definition but different immutable sampler objects. It creates the graphics pipeline with the first pipeline layout, allocates and binds a descriptor set with the second, samples a byte-pattern image, and requires a byte-for-byte match in the rendered output. This exercises [pipeline-layout compatibility for set 0](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-compatibility). The source requires `VK_KHR_maintenance4` and `VK_KHR_maintenance5`.

### `no_rendering*`: dynamic rendering with no active or an unused attachment

These leaves create a dynamic-rendering graphics pipeline, draw, submit, and wait. `no_rendering` records `colorAttachmentCount = 0`; `no_rendering_unused_attachment` records one color attachment but requires the `dynamicRenderingUnusedAttachments` feature. They validate successful construction and execution, not image contents.

### `color_write_mask_none`: fragment storage effect with color output disabled

The leaf sets `colorWriteMask` to `0x0`, binds only descriptor sets 0 and 2, and draws a triangle. The fragment shader writes `uvec3(2, 3, 4)` through a buffer-reference payload. After submission, the host invalidates the payload allocation and checks those three values. This leaf requires `VK_KHR_buffer_device_address`, `VK_EXT_scalar_block_layout`, and fragment stores and atomics.

## Shader Analysis

The family has several generated GLSL programs and three Amber artifacts, but no single shader represents its behavior. The direct C++ leaves use shaders as compact instruments for a distinct host or pipeline-state contract.

- The [`implicit_primitive_id` fragment program](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L265-L275) maps `gl_PrimitiveID % 2` to red or green. Its image oracle makes a primitive-ID propagation error visible, but it cannot alone identify whether rasterization, stage linkage, or image readback caused the mismatch.
- The [`descriptor_bind_test_*` programs](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L853-L901) consume the uniform-buffer set interface while the host changes set-binding order and occupancy. The relevant behavior is descriptor-state selection, not shader algorithm complexity.
- The [`color_write_mask_none` fragment program](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2512-L2531) writes the exact payload while also assigning `color`. Because pipeline state masks every color component, the buffer is the only intended oracle.

A SPIR-V disassembly walkthrough is not included: this source generates several unrelated shaders at runtime, and the family tests pipeline contracts rather than a fixed embedded SPIR-V artifact.

## Runtime Execution and Result Checking

- The common pattern creates shader modules, a graphics pipeline, attachments or buffers, records a draw, adds the relevant transfer or host-visibility barrier, submits to the universal queue, and waits. Each direct leaf supplies only the resources needed for its own oracle.
- Primitive-ID and descriptor-binding leaves use a small `R8G8B8A8_UNORM` attachment. They transition it from color-attachment output to transfer source, copy it to a host-visible buffer, invalidate that allocation, and compare pixels. The primitive leaf requires a left-red/right-green split; the descriptor leaf requires green throughout.
- The array-of-structs leaf follows the same image-readback shape with a thresholded expected color. The matching-layout leaf first uploads a byte pattern into a sampled image, transitions it for fragment reads, renders to a separate color image, copies that image back, and compares the bytes exactly.
- The library interpolation and varying-sample paths use storage buffers as their primary observation. The former sorts values before comparing because fragment invocation order is unspecified. The latter checks standard sample-location results for its selected count.
- No-rendering leaves build the graphics pipeline before command recording, then begin dynamic rendering with zero or one color attachment, bind the pipeline, draw, end rendering, and pass after `submitCommandsAndWait`. The source does not copy or inspect the created attachment, so these leaves localize a failure only to setup, recording, submission, or execution completion.
- The color-write-mask leaf disables attachment writes but gives the fragment shader a storage-buffer path. It invalidates the host-visible payload allocation and rejects any value other than 2, 3, 4 at its first three words.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `amber_builtin_and_storage_cases` | Amber program execution, required-stage built-in handling, or vertex-stage storage writes. |
| `implicit_primitive_id*` | `PrimitiveId` propagation to fragment execution, geometry/tessellation stage handling, or image readback. |
| `array_of_structs_interface` | Shader interface matching, varying transport, or color-output comparison. |
| `descriptor_bind_test_*` | Descriptor-set index handling, sparse/reverse bind state, or shader descriptor access. |
| `pipeline_library_misc_cases` | Pipeline-library linking, dynamic-rendering state, interpolation, or sample-location validation. |
| `identically_defined_layout` | Pipeline-layout compatibility for set 0, descriptor binding, immutable-sampler use, sampled-image access, or image comparison. |
| `no_rendering*` | Dynamic-rendering pipeline creation or execution with zero or unused color attachments. |
| `color_write_mask_none` | Color-write-mask application, fragment-stage execution, buffer device address access, or storage-buffer visibility. |

### Cause Analysis

#### Amber program execution, required-stage built-in handling, or vertex-stage storage writes

**Possible failure symptoms:** One of `position_to_ssbo`, `primitive_id_from_tess`, or `layer_read_from_frag` fails its Amber-defined check or skips because its required feature is unavailable.

**Possible implementation causes:** The failure can involve the Amber program path, the enabled feature path, a built-in stage contract, or the script's result mechanism. The registration code only supplies the script names and feature lists, so source-level investigation of the corresponding `.amber` artifact is needed for narrower localization.

#### `PrimitiveId` propagation to fragment execution, geometry/tessellation stage handling, or image readback

**Possible failure symptoms:** The expected vertical red/green split contains the wrong color or an unexpected pixel in either `implicit_primitive_id` leaf.

**Possible implementation causes:** The driver may propagate the wrong primitive index to fragment execution, mishandle the tessellation path, or fail in rasterization, attachment write, transfer, or host readback. The [PrimitiveId rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-primitiveid) define the fragment-stage value, but this image oracle cannot isolate the responsible stage.

#### Shader interface matching, varying transport, or color-output comparison

**Possible failure symptoms:** `array_of_structs_interface` differs from its expected color beyond the source threshold.

**Possible implementation causes:** A defect may occur while matching the array-of-structs stage interface, transporting the values, executing a shader, writing the color attachment, or copying it for comparison. The final image does not distinguish those paths without further shader or pipeline instrumentation.

#### Descriptor-set index handling, sparse/reverse bind state, or shader descriptor access

**Possible failure symptoms:** A `descriptor_bind_test_*` leaf yields any pixel other than green.

**Possible implementation causes:** The implementation may associate a descriptor set with the wrong set number after reverse binding, overwrite previously bound state, mishandle the deliberately unbound holes, or resolve a shader descriptor to the wrong resource. The image result also includes ordinary shader, rasterization, and readback paths, so a mismatch requires source-level tracing of the selected set indices.

#### Pipeline-library linking, dynamic-rendering state, interpolation, or sample-location validation

**Possible failure symptoms:** A library-only leaf reports a construction failure, too few invocations, an interpolation mismatch, or an unexpected standard sample position.

**Possible implementation causes:** A defect may lie in graphics-pipeline-library linking, use of incomplete state during library creation, dynamic-rendering attachment setup, fragment interpolation, atomic-buffer observation, or sample-location reporting. The library experiments compare several mechanisms at once, so their result cannot identify a single internal pipeline component.

#### Pipeline-layout compatibility, descriptor binding, immutable-sampler use, sampled-image access, or image comparison

**Possible failure symptoms:** `identically_defined_layout` returns output bytes different from the uploaded 4 x 4 source pattern.

**Possible implementation causes:** The implementation may fail to treat the independently created pipeline layouts as compatible for set 0, mishandle the immutable sampler from the bound descriptor set's layout, sample the image incorrectly, or fail in the copyback path. The [pipeline-layout compatibility rules](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-compatibility) require identically defined descriptor-set layouts through the accessed set index. This leaf's final byte comparison does not isolate which stage failed.

#### Dynamic-rendering pipeline creation or execution with zero or unused color attachments

**Possible failure symptoms:** `no_rendering` or `no_rendering_unused_attachment` fails pipeline creation, command recording, queue submission, or completion.

**Possible implementation causes:** The driver may mishandle a pipeline with no attachment state, command execution under an empty rendering attachment list, or the unused-attachment feature path. These leaves deliberately lack an image oracle; successful completion establishes only that the sequence completed without a reported failure.

#### Color-write-mask application, fragment-stage execution, buffer device address access, or storage-buffer visibility

**Possible failure symptoms:** `color_write_mask_none` reads values other than 2, 3, and 4 from the payload buffer.

**Possible implementation causes:** A defect may incorrectly suppress fragment execution with a zero color-write mask, fail to consume the bound descriptor or buffer device address, mishandle scalar block layout, or leave shader writes unavailable to the host. The buffer oracle proves the intended storage effect, but it does not separately test the attachment's suppressed color output.

## Case Pruning

### Requirement-based pruning

The primitive-ID tessellation form requires `tessellationShader`; both generated primitive-ID forms require `geometryShader`. The Amber leaves specify their own feature lists. `no_rendering*` requires `VK_KHR_dynamic_rendering`, and its unused-attachment form also requires `dynamicRenderingUnusedAttachments`. `identically_defined_layout` requires `VK_KHR_maintenance4` and `VK_KHR_maintenance5`. The masked-color leaf requires buffer device address, scalar block layout, and fragment stores and atomics. Library interpolation and varying-sample leaves impose dynamic-rendering, storage-write, sample-count, and standard-sample-location requirements.

### Design-based pruning

The three Amber leaves and `identically_defined_layout` are monolithic-only. Library-specific leaves are registered only for library construction. The no-rendering leaves are excluded from shader-object construction, and the C++ no-rendering and library-only blocks are excluded in Vulkan SC. The common direct leaves remain across construction types where `checkPipelineConstructionRequirements()` permits them.

## Key Takeaways

- `pipeline.misc` is a source-file grouping, not one uniform execution model. Each test case leaf selects a small but distinct pipeline contract.
- Pixel comparisons cover primitive-ID, descriptor, interface, and matching-layout paths. `color_write_mask_none` instead observes a fragment storage write, while `no_rendering*` observes successful completion only.
- Reverse descriptor binds and descriptor-set holes are intentional state configurations. The observed green image confirms only that the shader received the required descriptor data.
- A matching-layout failure, a primitive-ID mismatch, or a dynamic-rendering completion failure each needs source-level follow-up because their final oracle spans multiple pipeline stages.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Family registration | [`createMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2543-L2622) | Defines the canonical leaves and construction-dependent additions. |
| Amber registration | [`addMonolithicAmberTests()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L92-L131) | Names the monolithic Amber cases and their feature requirements. |
| Primitive-ID path | [`ImplicitPrimitiveIDPassthroughCase`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L133-L435) | Generates stages, renders the two primitives, and checks the split image. |
| Descriptor-binding path | [`PipelineLayoutBindingTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L903-L1115) | Implements reverse and sparse descriptor-set binding and green-image validation. |
| Library interpolation path | [`PipelineLibraryInterpolateAtSampleTestInstance`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L439-L783) | Builds monolithic and fast-linked pipelines and evaluates buffer observations. |
| Interface and varying-sample paths | [`arrayOfStructsInterfaceTest()` and `varyingSamplesFragTest()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L1266-L1838) | Define color-interface and sample-location result checks. |
| Dynamic-rendering path | [`PipelineNoRenderingTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L1860-L2014) | Creates the attachment-free and unused-attachment submissions. |
| Pipeline-layout compatibility path | [`IdenticallyDefinedLayoutTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2051-L2263) | Uses independently created, compatible pipeline layouts across pipeline creation and descriptor binding. |
| Masked-color path | [`PipelineColorWriteMaskNoneTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2282-L2539) | Disables color writes and validates the storage-buffer payload. |
| `PrimitiveId` specification | [`interfaces.adoc`](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-primitiveid) | Defines primitive-index values and fragment-stage constraints. |
| Pipeline-layout compatibility specification | [`descriptorsets.adoc`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-compatibility) | Defines compatibility for set N and the use of previously bound descriptor sets by a compatible pipeline layout. |
