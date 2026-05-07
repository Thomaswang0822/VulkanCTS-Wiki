# vktPipelineShaderModuleIdentifierTests.cpp

## Overview

[`vktPipelineShaderModuleIdentifierTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp#L1) implements the [`shader_module_identifier`](../../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp#L3738) topic group. It verifies VK_EXT_shader_module_identifier functionality, testing pipeline creation using shader module identifiers instead of full shader code, including property queries, constant identifiers, and pipeline-from-id operations.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineShaderModuleIdentifierTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp#L1)
- Header: [`vktPipelineShaderModuleIdentifierTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.hpp#L1)

## Registration Path

[`createShaderModuleIdentifierTests()`](../../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp#L3738) returns the `shader_module_identifier` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Not shader-object, VK only.

## Test Hierarchy

```text
shader_module_identifier
├── properties
│   └── {test_case}
├── constant_identifiers
│   └── {pipeline_type}
│       └── {pipeline_count}
│           └── {use_sc}
│               └── {api_call}
│                   └── {different_device}
├── pipeline_from_id
│   └── {pipeline_type}
│       └── {pipeline_count}
│           └── {use_sc}
│               └── {pipeline_cache}
│                   └── {module_usage}
│                       └── {capturing}
├── hlsl_tessellation
│   └── {test_case}
└── misc
    └── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| Properties test | Verifies shader module identifier property queries |
| Constant identifiers test | Verifies pipeline creation with constant shader module identifiers |
| Pipeline from ID test | Verifies pipeline creation from shader module identifiers |
| HLSL tessellation test | Verifies shader module identifiers with HLSL tessellation shaders |
| Misc test | Verifies miscellaneous shader module identifier behaviors |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Pipeline type | Enum | Graphics, compute |
| Pipeline count | Array | Single, multiple |
| Use SC | Bool | With/without specialization constants |
| API call | Enum | Different API call patterns |
| Different device | Bool | Same/different device |
| Pipeline cache | Bool | With/without pipeline cache |
| Module usage | Enum | Different shader module usage patterns |
| Capturing | Enum | Different capturing modes |
| PipelineConstructionType | Parameter | Non-shader-object variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_shader_module_identifier` | Primary extension for all tests |
| `geometryShader` | Required for geometry shader identifier tests |
| `tessellationShader` | Required for tessellation shader identifier tests |
| `VK_KHR_acceleration_structure` | Required for ray tracing identifier tests |
| `VK_KHR_ray_tracing_pipeline` | Required for ray tracing identifier tests |
| `VK_EXT_mesh_shader` | Required for mesh shader identifier tests |
| `vertexPipelineStoresAndAtomics` | Required for some tests |
| `fragmentStoresAndAtomics` | Required for some tests |

## Verification Methods

- **Property query verification**: Verify `vkGetShaderModuleIdentifierEXT` returns valid identifiers
- **Pipeline creation verification**: Verify pipelines created from identifiers produce correct results
- **Identifier consistency**: Verify that the same shader code produces consistent identifiers
- **Cross-device verification**: Verify identifier behavior across different devices

## Notes

- Excluded from shader-object variants
- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
- Uses a custom `TestGroupWithClean` class for resource cleanup
