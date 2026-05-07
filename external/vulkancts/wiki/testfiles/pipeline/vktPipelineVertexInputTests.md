# vktPipelineVertexInputTests.cpp

## Overview

[`vktPipelineVertexInputTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1) implements the [`vertex_input`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3096) topic group of the pipeline category. It verifies vertex attribute fetching across a wide range of formats, binding mappings, attribute layouts, and shader types, including stress tests with many attributes, component mismatch cases, stride changes, unused bindings, and unbound inputs. Also delegates to nested subgroups for sRGB vertex formats and legacy vertex attributes.

## Role

Implementation file. Also dispatches to [`vktPipelineVertexInputSRGBTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L1) and [`vktPipelineLegacyAttrTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L1) for nested subgroups.

## Source Code

- Primary source: [`vktPipelineVertexInputTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1)
- Header: [`vktPipelineVertexInputTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.hpp#L1)
- Nested subgroup: [`vktPipelineVertexInputSRGBTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L1)
- Nested subgroup: [`vktPipelineLegacyAttrTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L1)

## Registration Path

This file contributes the subgroup returned by [`createVertexInputTests()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3096), which is attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L1).

**Variant coverage**: All variants. Some sub-groups are excluded for shader object variants.

## Test Hierarchy

```text
vertex_input
├── single_attribute
│   ├── int
│   │   ├── <format>_<rate_vertex>
│   │   └── <format>_<rate_vertex>_missing_components
│   ├── ivec2 / ivec3 / ivec4
│   ├── uint / uvec2 / uvec3 / uvec4
│   ├── float / vec2 / vec3 / vec4
│   ├── float16_t / f16vec2 / f16vec3 / f16vec4
│   ├── mat2 / mat3 / mat4
│   └── double / dvec2 / dvec3 / dvec4 / dmat2 / dmat3 / dmat4
├── multiple_attributes                   (excluded for shaderObject)
│   ├── binding_one_to_one
│   │   └── attributes
│   │       └── <glsl_type>
│   ├── binding_one_to_many
│   │   ├── attributes
│   │   └── attributes_sequential
│   ├── layout_skip
│   │   ├── binding_one_to_one / binding_one_to_many
│   └── out_of_order
│       ├── binding_one_to_one / binding_one_to_many
├── max_attributes                        (excluded for shaderObject)
│   ├── 16_attributes / 32_attributes / 64_attributes / 128_attributes
│   └── query_max_attributes
├── component_mismatch
│   ├── r64g64_to_double
│   ├── r64g64b64_to_double / r64g64b64_to_dvec2
│   └── r64g64b64a64_to_double / r64g64b64a64_to_dvec2 / r64g64b64a64_to_dvec3
├── misc
│   ├── stride_change_vert_frag
│   ├── stride_change_vert_tess_frag
│   ├── stride_change_vert_geom_frag
│   ├── stride_change_vert_tess_geom_frag
│   ├── unused_binding                    (monolithic, fast_linked_library, shader_object_unlinked_spirv)
│   ├── unused_binding_dynamic
│   ├── unbound_input                     (same + VK_KHR_maintenance9, non-VulkanSC)
│   ├── unbound_input_dynamic
│   ├── unbound_input_integer
│   └── unbound_input_dynamic_integer
├── legacy_vertex_attributes              (monolithic, fast_linked_library only)
│   └── (delegated to vktPipelineLegacyAttrTests.cpp)
└── srgb_vertex_formats                   (delegated to vktPipelineVertexInputSRGBTests.cpp)
```

Source: [`createVertexInputTests()`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3096).

## Test Families

### 1. single_attribute

Tests each GLSL vertex type with all compatible VkFormats, using both VERTEX and INSTANCE input rates. Also tests "missing components" (conversion to RGBA) for formats with fewer than 4 components.

### 2. multiple_attributes

Tests combinations of 3 different GLSL types as multiple vertex attributes, with various binding mappings (1:1, 1:many), attribute layouts (interleaved, sequential), layout skip, and layout order (in-order, out-of-order). Excluded for shader object variants.

### 3. max_attributes

Stress-tests with 16, 32, 64, 128, and device-max attributes using random GLSL types and compatible formats, with 1:1 and 1:many binding mappings and interleaved/sequential layouts. Excluded for shader object variants.

### 4. component_mismatch

Tests 64-bit float formats where the format has more components than the shader expects (e.g., R64G64B64_SFLOAT consumed as `double`), verifying correct "Conversion to RGBA" behavior.

### 5. misc / stride_change

Verifies that changing vertex buffer stride between pipeline binds (with/without tessellation/geometry shaders) works correctly without rebinding vertex buffers.

### 6. misc / unused_binding

Verifies that unused vertex input bindings do not affect rendering. Tests both static and dynamic (`VK_EXT_vertex_input_dynamic_state`) vertex input. Limited to monolithic, fast_linked_library, and shader_object_unlinked_spirv.

### 7. misc / unbound_input

Verifies that unbound vertex inputs (using `VK_KHR_maintenance9`) produce correct default values. Tests float and integer inputs, static and dynamic vertex input. Non-VulkanSC only.

### 8. legacy_vertex_attributes

Delegated to [`vktPipelineLegacyAttrTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L1). Tests legacy vertex attribute behavior. Monolithic and fast_linked_library only.

### 9. srgb_vertex_formats

Delegated to [`vktPipelineVertexInputSRGBTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L1). Verifies sRGB vertex format linearization.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| GlslType | [Enum](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L122) (26 values) | INT, IVEC2-4, UINT, UVEC2-4, FLOAT, VEC2-4, F16, F16VEC2-4, MAT2-4, DOUBLE, DVEC2-4, DMAT2-4 |
| VkFormat (single attribute) | [Array](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1842) | ~80 vertex formats |
| VkVertexInputRate | Enum | VERTEX, INSTANCE |
| BindingMapping | [Enum](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L168) | ONE_TO_ONE, ONE_TO_MANY |
| AttributeLayout | [Enum](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L174) | INTERLEAVED, SEQUENTIAL |
| LayoutSkip | [Enum](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L181) | ENABLED, DISABLED |
| LayoutOrder | [Enum](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L186) | IN_ORDER, OUT_OF_ORDER |
| Attribute count (max_attributes) | [Array](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2137) | {16, 32, 64, 128, 0} (0 = query device max) |
| Component mismatch cases | [Struct array](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2204) | 6 specific format-to-type mappings |
| useTessellation | Loop | `false`, `true` |
| useGeometry | Loop | `false`, `true` |
| dynamicInputs | Loop | `false`, `true` (UnusedBinding, UnboundInput) |
| integerInput | Loop | `false`, `true` (UnboundInput) |

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| `maxVertexInputAttributes` limit | `VertexInputTest::checkSupport` | [495](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L495) |
| `shaderFloat16` + `storageInputOutput16` (for float16 types) | `VertexInputTest::checkSupport` | [501](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L501) |
| `shaderFloat64` (for double formats) | `isSupportedVertexFormat` | [73](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L73) |
| `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT` | `isSupportedVertexFormat` | [80](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L80) |
| `DEVICE_CORE_FEATURE_TESSELLATION_SHADER` | `StrideChangeCase::checkSupport` | [2401](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2401) |
| `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` | `StrideChangeCase::checkSupport` | [2404](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2404) |
| `VK_EXT_vertex_input_dynamic_state` (when dynamicInputs=true) | `UnusedBinding::checkSupport` | [2582](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2582) |
| `VK_KHR_maintenance9` | `UnboundInput::checkSupport` | [2836](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2836) |

## Verification Methods

### single_attribute, multiple_attributes, max_attributes, component_mismatch

**Integer threshold position deviation comparison** (`tcu::intThresholdPositionDeviationCompare`) with UVec4(2,2,2,2) threshold and IVec3(1,1,0) position deviation. Creates a reference image with left half red / right half blue (based on vertex attribute values), reads back the color attachment, and compares. [Line 1776](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1776).

### stride_change

**Float threshold comparison** (`tcu::floatThresholdCompare`) with threshold Vec4(0.0). Fills reference with expected blue color and compares against GPU result. [Line 2556](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2556).

### unused_binding

**Float threshold comparison** (`tcu::floatThresholdCompare`) with threshold Vec4(0.0). Sets per-pixel reference colors for 4 quadrants and compares. [Line 2809](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L2809).

### unbound_input

**Float threshold comparison** (`tcu::floatThresholdCompare`). Verifies that unbound inputs produce the expected default/zero values. [Line 3044](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L3044).

## Test Principles Observed

- **Format-type matrix coverage**: Every supported combination of GLSL type and VkFormat is tested
- **Binding mapping variety**: 1:1 and 1:many binding mappings exercise different vertex buffer layouts
- **Attribute count scaling**: Stress tests scale from 16 to device-max attributes
- **Stride change without rebind**: Verifies that stride changes take effect without rebinding vertex buffers
- **Unused and unbound input robustness**: Verifies that missing or unused vertex inputs do not cause incorrect rendering

## Notes / Uncertainties

- `multiple_attributes` and `max_attributes` are excluded for shader object variants
- `legacy_vertex_attributes` is limited to monolithic and fast_linked_library
- `unused_binding` and `unbound_input` are limited to monolithic, fast_linked_library, and shader_object_unlinked_spirv
- `unbound_input` is excluded for VulkanSC
