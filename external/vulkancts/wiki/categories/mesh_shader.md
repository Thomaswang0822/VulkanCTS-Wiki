# mesh_shader

The `mesh_shader` category documents Vulkan CTS tests for `VK_NV_mesh_shader` and `VK_EXT_mesh_shader`. The root registration file creates `nv` and `ext` children in [vktMeshShaderTests.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L55-L84). The shared support helpers require the corresponding extension and requested task/mesh feature bits in [vktMeshShaderUtil.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L139).

## Registration Entry Point

| Item | Evidence |
|------|----------|
| Category root | [vktMeshShaderTests.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L55-L84) |
| NV support helper | [vktMeshShaderUtil.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L124) |
| EXT support helper | [vktMeshShaderUtil.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L139) |

## Registration Hierarchy

```text
mesh_shader
├── nv
└── ext
```

## Test Families

### nv — `VK_NV_mesh_shader` branch

The `nv` branch registers `smoke`, `api`, `synchronization`, `property`, `builtin`, `misc`, and `in_out` children from the root dispatcher [vktMeshShaderTests.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L63-L69). Its files cover basic rendering, draw APIs, synchronization, limits, built-ins, miscellaneous behavior, and interface variables.

### ext — `VK_EXT_mesh_shader` branch

The `ext` branch registers `smoke`, `api`, `synchronization`, `builtin`, `pipeline`, `misc`, `in_out`, `properties`, `conditional_rendering`, `provoking_vertex`, and `query` children [vktMeshShaderTests.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L71-L81). The inspected EXT files add pipeline-construction modes, shader objects, conditional rendering, provoking vertex, query matrices, multiview, secondary command buffers, and device-address-command variants.

## File Inventory

| Wiki page | Source role | Registered path roots |
|-----------|-------------|-----------------------|
| [vktMeshShaderTests](../testfiles/mesh_shader/vktMeshShaderTests.md) | Category dispatcher | `mesh_shader` |
| [vktMeshShaderSmokeTests](../testfiles/mesh_shader/vktMeshShaderSmokeTests.md) | NV smoke implementation | `mesh_shader.nv.smoke` |
| [vktMeshShaderApiTests](../testfiles/mesh_shader/vktMeshShaderApiTests.md) | NV draw API implementation | `mesh_shader.nv.api` |
| [vktMeshShaderSyncTests](../testfiles/mesh_shader/vktMeshShaderSyncTests.md) | NV synchronization implementation | `mesh_shader.nv.synchronization` |
| [vktMeshShaderPropertyTests](../testfiles/mesh_shader/vktMeshShaderPropertyTests.md) | NV property implementation | `mesh_shader.nv.property` |
| [vktMeshShaderBuiltinTests](../testfiles/mesh_shader/vktMeshShaderBuiltinTests.md) | NV built-in implementation | `mesh_shader.nv.builtin` |
| [vktMeshShaderMiscTests](../testfiles/mesh_shader/vktMeshShaderMiscTests.md) | NV misc and in/out implementation | `mesh_shader.nv.misc`, `mesh_shader.nv.in_out` |
| [vktMeshShaderSmokeTestsEXT](../testfiles/mesh_shader/vktMeshShaderSmokeTestsEXT.md) | EXT smoke implementation | `mesh_shader.ext.smoke` |
| [vktMeshShaderApiTestsEXT](../testfiles/mesh_shader/vktMeshShaderApiTestsEXT.md) | EXT draw API implementation | `mesh_shader.ext.api` |
| [vktMeshShaderSyncTestsEXT](../testfiles/mesh_shader/vktMeshShaderSyncTestsEXT.md) | EXT synchronization implementation | `mesh_shader.ext.synchronization` |
| [vktMeshShaderBuiltinTestsEXT](../testfiles/mesh_shader/vktMeshShaderBuiltinTestsEXT.md) | EXT built-in and pipeline implementation | `mesh_shader.ext.builtin`, `mesh_shader.ext.pipeline` |
| [vktMeshShaderMiscTestsEXT](../testfiles/mesh_shader/vktMeshShaderMiscTestsEXT.md) | EXT miscellaneous implementation | `mesh_shader.ext.misc` |
| [vktMeshShaderInOutTestsEXT](../testfiles/mesh_shader/vktMeshShaderInOutTestsEXT.md) | EXT interface variables | `mesh_shader.ext.in_out` |
| [vktMeshShaderPropertyTestsEXT](../testfiles/mesh_shader/vktMeshShaderPropertyTestsEXT.md) | EXT properties | `mesh_shader.ext.properties` |
| [vktMeshShaderConditionalRenderingTestsEXT](../testfiles/mesh_shader/vktMeshShaderConditionalRenderingTestsEXT.md) | EXT conditional rendering | `mesh_shader.ext.conditional_rendering` |
| [vktMeshShaderProvokingVertexTestsEXT](../testfiles/mesh_shader/vktMeshShaderProvokingVertexTestsEXT.md) | EXT provoking vertex | `mesh_shader.ext.provoking_vertex` |
| [vktMeshShaderQueryTestsEXT](../testfiles/mesh_shader/vktMeshShaderQueryTestsEXT.md) | EXT queries | `mesh_shader.ext.query` |

## Recurring Parameter Dimensions

| Theme | Observed dimensions | Evidence |
|-------|---------------------|----------|
| Draw APIs | direct/indirect/count draws, draw count, offsets/strides, count limits, task usage | [vktMeshShaderApiTests.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderApiTests.cpp#L662-L720), [vktMeshShaderApiTestsEXT.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L787-L855) |
| Synchronization | stage pair, resource, barrier, access pair | [vktMeshShaderSyncTests.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1334-L1386), [vktMeshShaderSyncTestsEXT.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1774-L1839) |
| Built-ins | explicit built-in cases and primitive shading-rate pairs | [vktMeshShaderBuiltinTests.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L2045-L2087), [vktMeshShaderBuiltinTestsEXT.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2564-L2617) |
| Interface variables | feature groups, owner, type, width, dimension, interpolation, permutations | [vktMeshShaderInOutTestsEXT.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1601-L1715) |
| Queries | query combination, geometry, reset/access, wait, draw call, result size, availability, blocks, task, ordering, multiview, command buffer | [vktMeshShaderQueryTestsEXT.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L1391-L1515) |

## Recurring Support Requirements

Common support starts with the NV or EXT mesh-shader helper [vktMeshShaderUtil.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L139). Additional inspected gates include `VK_KHR_draw_indirect_count`, `multiDrawIndirect`, `vertexPipelineStoresAndAtomics`, `VK_KHR_fragment_shading_rate`, `VK_EXT_conditional_rendering`, `VK_EXT_provoking_vertex`, `VK_EXT_host_query_reset`, and numeric shader features [vktMeshShaderApiTestsEXT.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderApiTestsEXT.cpp#L343-L358), [vktMeshShaderQueryTestsEXT.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L537-L553), [vktMeshShaderInOutTestsEXT.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L590-L605).

## Recurring Verification Methods

Rendering cases compare reference images or layers [vktMeshShaderSmokeTests.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L540-L542), synchronization cases verify expected values in buffers or rendered output [vktMeshShaderSyncTests.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1290-L1327), query cases check availability and numeric ranges [vktMeshShaderQueryTestsEXT.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderQueryTestsEXT.cpp#L766-L805), and property cases fail on invalid limits or shader-backed results [vktMeshShaderPropertyTestsEXT.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2419-L2421).

## Scope Notes

Helper-only mesh-shader utility files were not given Level-3 pages because they do not register tests.
