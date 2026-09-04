# Understanding Brief: tensor.dimension_query

## One-Sentence Test Purpose

This test checks whether shader-side `tensorSizeARM` queries return the dimensions used to create an ARM tensor across supported formats, ranks, and tilings.

## Background Knowledge

### Tensor rank and shape

A tensor's rank is its number of dimensions. Its shape gives the size of each dimension in index order: a rank-2 tensor with shape `{2, 1}` has dimension 0 of size 2 and dimension 1 of size 1. `tensorSizeARM` returns one of those sizes from the tensor descriptor; it does not read tensor element data.

Why it matters here:
- The generator emits one query for every dimension index from `0` through `rank - 1`.
- The host compares the returned sequence with the same `pDimensions` sequence used to create the tensor.

### Tensor query execution

The Vulkan tensor query operation is represented in SPIR-V by `OpTensorQuerySizeARM`. The operation queries the size of the tensor descriptor that a shader tensor operation would access. The query therefore tests descriptor metadata and rank/index agreement, while the tensor's element contents are irrelevant.

Why it matters here:
- The compute shader needs only a bound tensor view and a storage buffer for its results.
- A descriptor, rank, or dimension mismatch can affect the query before any tensor element access would occur.

## One Concrete Example

Consider the registered case `dEQP-VK.tensor.dimension_query.r32_uint_linear_shape_2_1`. The host creates a linear `VK_FORMAT_R32_UINT` tensor with rank 2 and dimensions `{2, 1}`. The generated compute shader has one invocation and writes:

```glsl
layout(set=0, binding=0) uniform tensorARM<uint, 2> tens;
layout(set=0, binding=1, std430) buffer _buff { uint data[]; };

void main()
{
    data[0] = tensorSizeARM(tens, 0);
    data[1] = tensorSizeARM(tens, 1);
}
```

The expected readback is `data[0] == 2` and `data[1] == 1`. The tensor format changes the tensor element type in the declaration, but it does not change which shape values the two queries must return.

## End-to-End Test Flow

```text
[host] select one format, one shape, and one tiling from the registered matrix
[host] create a tensor description with the selected rank, dimensions, format, tiling, and shader usage
[host] create tensor memory and a tensor view
[host] create a host-visible storage buffer with one uint32_t slot per dimension and clear it
[host] bind the tensor view at descriptor binding 0 and the output buffer at binding 1
[host] generate and compile the rank-specific compute shader
[host] create a compute pipeline and record one dispatch of 1 x 1 x 1
[device] execute one tensorSizeARM query for each dimension index and store the values in the output buffer
[host] apply a shader-write to host-read buffer barrier, submit, and wait for completion
[host] invalidate the output allocation and compare every slot with the original tensor dimension
[host] return pass when all slots match; otherwise report the first mismatching index and values
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms` calls `genShaderQueryDimensions(m_dimension.size(), m_format)` for each test case. The generator emits GLSL 4.50, requires `GL_ARM_tensors` and `GL_EXT_shader_explicit_arithmetic_types`, declares a rank-specialized `tensorARM<format, rank>`, and prints one `tensorSizeARM` assignment per dimension. The source collection compiles this as the `comp` compute program.

The representative rank-2 `VK_FORMAT_R32_UINT` source produces SPIR-V 1.0 with `OpTypeTensorARM %uint %uint_2` and one `OpTensorQuerySizeARM` instruction for each queried index. The full generated disassembly belongs in the final page's representative walkthrough.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkTensorARM` plus `VkTensorViewARM` | yes | yes, descriptor binding 0 | tensor descriptor queried; tensor elements are not read | no | Supplies the format, rank, dimensions, and tiling metadata under test. |
| Host-visible `VkBuffer` | yes | yes, storage-buffer binding 1 | compute shader writes one `uint` per dimension | yes | Carries query results back to the host. |
| Descriptor set | yes | yes | shader accesses both descriptors through set 0 | no | Connects the tensor view and result buffer to the generated declarations. |

The test does not initialize or inspect tensor element data. For linear tiling, the constructor computes tensor strides, but the query test uses those strides only as part of tensor creation.

## What Is Checked

- The output buffer has `m_dimensions.size()` `uint32_t` elements and starts cleared.
- After completion, the host invalidates the allocation and checks each `bufferMemory[element_idx]` against `m_dimensions[element_idx]`.
- A mismatch fails with the index, expected dimension, and buffer value. The test passes only when every dimension slot matches.
- The Vulkan specification describes `OpTensorQuerySizeARM` as querying the size of the tensor descriptor that a shader tensor operation would access; the test's expected values are the tensor description's `pDimensions` entries.

## Behavior Parameter Identification

> **Behavior parameter:** tensor shape and rank
>
> **Candidate values:** `shape_1`, `shape_2_1`, `shape_4_2_1`, `shape_8_4_2_1`, `shape_4_8_16_2_1`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shape_1` | Rank-1 tensor query or dimension-0 descriptor metadata handling. |
| `shape_2_1` | Rank-2 query indexing or shape propagation for dimensions 0 and 1. |
| `shape_4_2_1` | Rank-3 query indexing or shape propagation for dimensions 0 through 2. |
| `shape_8_4_2_1` | Rank-4 query indexing or shape propagation for dimensions 0 through 3. |
| `shape_4_8_16_2_1` | Rank-5 support, query indexing, or propagation of the final dimension. |

## Important Variations and Special Cases

- The five shapes cover ranks 1 through 5. The rank-1 case emits one query; the rank-5 case emits five.
- Every shape is combined with all eight integer formats returned by `getAllTestFormats`: `VK_FORMAT_R8_UINT`, `VK_FORMAT_R8_SINT`, `VK_FORMAT_R16_UINT`, `VK_FORMAT_R16_SINT`, `VK_FORMAT_R32_UINT`, `VK_FORMAT_R32_SINT`, `VK_FORMAT_R64_UINT`, and `VK_FORMAT_R64_SINT`.
- Each format and shape is registered for both `VK_TENSOR_TILING_LINEAR_ARM` and `VK_TENSOR_TILING_OPTIMAL_ARM`.
- The test requires compute-stage tensor access. It does not exercise vertex, fragment, or other shader stages.
- A case is skipped when `VK_ARM_tensors`, shader tensor access, compute-stage tensor access, the selected format/tiling tensor-shader feature, or the device's `maxTensorDimensionCount` requirement is unavailable.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and case matrix | [addDimensionQueriesTestCases](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L275-L289) | Defines the five shapes, all formats, and both tilings. |
| Registered family | [createDimensionQueryTests](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L293-L300) | Creates the `dimension_query` test family. |
| Shader generator | [genShaderQueryDimensions](../../../modules/vulkan/tensor/shaders/vktTensorQueryDimensionsShaders.cpp#L40-L65) | Emits the rank-specific `tensorSizeARM` shader. |
| Support checks | [TensorDimensionQueriesTestCase::checkSupport](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L238-L261) | Enforces extension, rank, feature, stage, and format/tiling gates. |
| Tensor and output setup | [TensorDimensionsQueriesTestInstance::iterate](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L92-L153) | Creates and binds the tensor view and result buffer. |
| Dispatch and synchronization | [TensorDimensionsQueriesTestInstance::iterate](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L155-L194) | Runs one compute dispatch and makes writes visible to the host. |
| Result comparison | [TensorDimensionsQueriesTestInstance::iterate](../../../modules/vulkan/tensor/vktTensorDimensionQuery.cpp#L196-L218) | Defines the per-dimension pass/fail check. |
| Format list and support helpers | [getAllTestFormats](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L48-L56), [support helpers](../../../modules/vulkan/tensor/vktTensorTestsUtil.cpp#L341-L412) | Supplies formats and implements format, feature, and stage queries. |
| Mustpass cases | [tensor.txt#L761-L840](../../../mustpass/main/vk-default/tensor.txt#L761-L840) | Confirms the 80 registered default mustpass cases. |
| Tensor query semantics | [tensorops.adoc#L231-L239](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#L231-L239) | Defines `OpTensorQuerySizeARM` as a descriptor-size query. |

## Questions / Risk Points for User Audit

- Does the rank/shape explanation make clear that the output sequence follows `pDimensions` order?
- Is the distinction between querying descriptor metadata and reading tensor elements clear?
- Is the compute-only stage restriction visible enough?
- Should the final page show a rank-1 walkthrough as well as the rank-2 representative?
- Do the failure rows distinguish rank behavior from the format and tiling dimensions that are crossed with every shape?

## Conversion Notes for Final Wiki Page

- Distill the rank/shape and descriptor-query concepts into short page-local Background Knowledge bullets.
- Use `dEQP-VK.tensor.dimension_query.r32_uint_linear_shape_2_1` as the exact representative path.
- Preserve the host/device flow, resource table, support gates, result comparison, and pruning sections in a more compact page form.
- Include the generated rank-2 GLSL and the complete validated SPIR-V disassembly in `## Shader Analysis`.
- Copy the `### Failure Cause Mapping` table above directly into the final page. Write `### Cause Analysis` fresh; do not copy it from this brief.
