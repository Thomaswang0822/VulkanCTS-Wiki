# Understanding Brief: `ubo`

## One-Sentence Test Purpose

This test family checks whether a Vulkan implementation reads uniform-block members from the offsets and strides required by the selected block layout, declaration shape, descriptor arrangement, and shader stage.

## Background Knowledge

### Uniform buffers and block layout

A `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` descriptor associates a buffer resource with a shader structure whose members can be loaded. Vulkan's standard-layout rules define how member alignment applies to that structure. With `scalarBlockLayout` enabled, members in the `Uniform` storage class use scalar alignment; otherwise, a `Uniform` block follows extended alignment unless `uniformBufferStandardLayout` permits base alignment.

Why it matters here:
- The test creates host reference bytes from the selected layout rules, then checks shader loads against those bytes.
- Arrays, nested structs, and matrices make member offsets and strides observable.

### Descriptor placement and stage visibility

A descriptor-set layout binding names a descriptor type, descriptor count, and stages that can access it. A uniform buffer may use `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER`; its descriptor offset must meet `minUniformBufferOffsetAlignment`.

Why it matters here:
- `per_block_buffer` assigns uniform data to separate buffers, while `single_buffer` packs block data into one buffer at aligned offsets.
- Graphics cases use vertex and fragment shaders; compute cases use a compute shader and a storage image for the result.

## One Concrete Example

For `dEQP-VK.ubo.single_basic_type.std140.float.compute`, the registration creates one `float` member in `Block`, declares the block for the compute shader, and selects `std140`. The case infrastructure calculates the member's reference offset, writes a deterministic value into host storage, uploads that storage through a uniform-buffer descriptor, then generates comparison code that multiplies a result by the member comparison. The compute shader writes that result to a storage image. The host passes the case only if every read-back pixel is white.

The page does not reproduce the generated GLSL or SPIR-V: source generators construct both from each exact registered case.

## End-to-End Test Flow

```text
[host] select a fixed layout shape or construct a deterministic random interface
[host] compute the reference layout and fill host storage with deterministic values
[host] generate the GLSL source for the selected graphics or compute path
[host] create uniform-buffer descriptors and upload either one buffer per block or aligned ranges in one buffer
[host] create the graphics or compute pipeline and submit the draw or dispatch
[device] load generated uniform-block members and compare them with generated reference values
[device] write comparison results to the graphics color target or compute storage image
[host] copy the image to host-visible memory and count non-white pixels
[host] pass only when the image is fully white
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`UniformBlockCase::delayedInit()` computes a reference layout, allocates reference storage, writes values with a fixed seed of `1`, and generates vertex/fragment or compute GLSL. The generator emits declarations from each interface, then recursively emits comparisons for basic members, arrays, structs, matrices, and block-instance arrays. `RandomUniformBlockCase` constructs its interface from a deterministic seed formed from the case number, its registered base seed, and the command-line base seed.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Reference UBO data | yes | yes, as `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` | read by shader | no | Contains values at source-calculated offsets and strides. |
| Per-block buffers or one shared buffer | yes | yes | read by shader | no | Exercises descriptor placement and, for the shared buffer, alignment between block ranges. |
| `colorImage` | yes | graphics attachment or compute storage image | written by shader path | yes | Carries one comparison result per rendered pixel or compute invocation. |
| `resultBuffer` | yes | transfer destination | no | yes | Holds the copied image for the all-white scan. |

## What Is Checked

- The generated shader reads the members that apply to its stage and compares them with the reference values that the host generated from the same case interface.
- A graphics pipeline places vertex and fragment comparison results in color channels. A compute pipeline stores its comparison result in `outImage`.
- `UniformBlockCaseInstance::iterate()` copies the result image to `resultBuffer`, counts pixels that differ from white, and fails when that count is nonzero.

## Behavior Parameter Identification

> **Behavior parameter:** `ubo` test family
>
> **Candidate values:** `2_level_array`, `2_level_struct_array`, `3_level_array`, `instance_array_basic_type`, `link_by_binding`, `multi_basic_types`, `multi_nested_struct`, `random`, `single_basic_array`, `single_basic_type`, `single_nested_struct`, `single_nested_struct_array`, `single_struct`, `single_struct_array`, `unsized_array`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2_level_array` | Nested-array layout, stride, or generated array-load comparison failure. |
| `2_level_struct_array` | Nested struct-array layout, buffer placement, or generated member-load comparison failure. |
| `3_level_array` | Three-level array layout, stride, or generated array-load comparison failure. |
| `instance_array_basic_type` | Uniform-block instance-array descriptor indexing, layout, or generated load failure. |
| `link_by_binding` | Descriptor binding linkage for same-named blocks across graphics stages or buffer-placement failure. |
| `multi_basic_types` | Multi-block descriptor placement, type-layout, stage-selection, or generated comparison failure. |
| `multi_nested_struct` | Multi-block nested-struct layout, descriptor placement, stage-selection, or generated comparison failure. |
| `random` | Deterministic generated interface layout, feature-specific declaration, descriptor indexing, or generated comparison failure. |
| `single_basic_array` | Array layout, stride, matrix-layout, or generated array-load comparison failure. |
| `single_basic_type` | Basic-member layout, stage-selection, or generated comparison failure. |
| `single_nested_struct` | Nested-struct layout, buffer placement, or generated member-load comparison failure. |
| `single_nested_struct_array` | Nested struct-array layout, buffer placement, or generated member-load comparison failure. |
| `single_struct` | Struct layout, buffer placement, or generated member-load comparison failure. |
| `single_struct_array` | Struct-array layout, buffer placement, or generated member-load comparison failure. |
| `unsized_array` | Uniform-buffer unsized-array layout, runtime size handling, or generated array-load comparison failure. |

## Important Variations and Special Cases

- `std430` cases require `scalarBlockLayout` or `uniformBufferStandardLayout`; `scalar` cases require `scalarBlockLayout`.
- 16-bit and 8-bit element cases require `uniformAndStorageBuffer16BitAccess` and `uniformAndStorageBuffer8BitAccess`, respectively.
- `random.descriptor_indexing` requires `shaderUniformBufferArrayNonUniformIndexing` and `runtimeDescriptorArray`.
- `unsized_array` requires `shaderUniformBufferUnsizedArray` outside Vulkan SC builds.
- The random generator caps type depth, array length, members, block count, and descriptor availability. It reduces arrays whose calculated complexity reaches `70` or more.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Package and family registration | [`TestPackage::init()`](../../../modules/vulkan/vktTestPackage.cpp#L1345-L1356) and [`UniformBlockTests::init()`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L446-L1256) | Registers `ubo` and its direct test families. |
| Fixed case construction | [`vktUniformBlockTests.cpp`](../../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L85-L420) | Defines fixed interfaces, stage variants, buffer modes, and random-case creation. |
| Layout and generated comparisons | [`computeReferenceLayout()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L572-L767) and [`generateCompareSrc()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1612-L1733) | Derives reference bytes and shader checks. |
| Shader generation | [`generateVertexShader()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1755-L1803), [`generateFragmentShader()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1805-L1853), and [`generateComputeShader()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L1855-L1911) | Generates each case's GLSL source. |
| Runtime and result checking | [`UniformBlockCaseInstance::iterate()`](../../../modules/vulkan/ubo/vktUniformBlockCase.cpp#L2089-L2404) | Uploads data, submits the selected path, and scans read-back pixels. |
| Random interface generation | [`RandomUniformBlockCase`](../../../modules/vulkan/ubo/vktRandomUniformBlockCase.cpp#L55-L315) | Builds deterministic generated interfaces. |
| Vulkan descriptor semantics | [`descriptors.adoc`](../../../../vulkan-docs/src/chapters/descriptors.adoc#L391-L397) and [`descriptorsets.adoc`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L17-L27) | Defines uniform-buffer descriptors and descriptor-set layout bindings. |
| Vulkan layout semantics | [`interfaces.adoc`](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1815-L1960) | Defines matrix, scalar, base, extended, and standard-buffer layout rules. |
| Vulkan limits | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L166-L172) and [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L647-L653) | Defines per-stage uniform-buffer and descriptor-offset limits. |

## Questions / Risk Points for User Audit

- The brief identifies generated shader and resource-layout behavior as the reason for this brief. The final page summarizes generators rather than reproducing any generated shader or SPIR-V material.
- The fixed and random sources establish the test mechanism. Exact generated text still depends on the selected registered case and, for `random`, its seed.
- The final page should retain the failure mapping table unchanged and explain that non-white output proves at least one generated comparison failed, without assigning a defect to a specific implementation layer.

## Conversion Notes for Final Wiki Rewrite

- Keep the two background concepts as concise prerequisites.
- Use the direct `ubo` test families as the behavior parameter values.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Explain shader generation, declaration selection, and recursive comparison generation without inserting reconstructed GLSL or SPIR-V.
- Keep detailed source links in the appendix and link only the evidence needed in the main prose.
