# Fragment Shading Barycentric

This page summarizes the Vulkan CTS `fragment_shading_barycentric` category, which verifies `VK_KHR_fragment_shader_barycentric` behavior for per-vertex data and barycentric weights.

## Registration Entry Point

The category root is created by [`FragmentShadingBarycentric::createTests()`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2642-L3150). The function constructs the category group using the caller-provided name, builds monolithic `data` and `weights` roots, and registers `pipeline_library` and `fast_linked_library` variants at [`vktFragmentShadingBarycentricTests.cpp`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2645-L2659) and [`vktFragmentShadingBarycentricTests.cpp`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L3146-L3149).

## Subgroup Structure

```text
fragment_shading_barycentric
├── data
├── weights
├── pipeline_library
└── fast_linked_library
```

## File Inventory

| File | Role | Wiki page |
|---|---|---|
| [`vktFragmentShadingBarycentricTests.cpp`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1) | Root registration and implementation file | [`vktFragmentShadingBarycentricTests.cpp`](../testfiles/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.md) |
| [`vktFragmentShadingBarycentricTests.hpp`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.hpp#L32-L35) | Declares the category factory | Header only |
| [`CMakeLists.txt`](../../modules/vulkan/fragment_shading_barycentric/CMakeLists.txt#L1) | Build inventory | Build metadata |

## Cross-File Test Themes

This category is implemented in one source file. The `data` branch checks barycentric access to per-vertex values across topology, aggregate, data-type, interpolation, provoking-vertex, dynamic-indexing, and shader-stage combinations. The `weights` branch checks barycentric weight behavior with perspective modes, rotations, topology state, and MSAA interpolation variants. Registration evidence is in [`createTests()`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2642-L3150).

## Cross-File Parameter Dimensions

Key parameter dimensions include pipeline construction type, primitive topology, clip/no-clip, aggregate shape, data type, interpolation mode, mesh versus vertex shader path, MSAA subtype, rotation, and dynamic topology-in-pipeline mode. These are visible in the registration value arrays and loops at [`vktFragmentShadingBarycentricTests.cpp`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2646-L2738), [`vktFragmentShadingBarycentricTests.cpp`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2740-L2943), and [`vktFragmentShadingBarycentricTests.cpp`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L2946-L3143).

## Cross-File Support Requirements and Feature Gates

The common requirement is `VK_KHR_fragment_shader_barycentric` with the barycentric feature bit. Conditional requirements cover provoking-vertex-last behavior, dynamic topology state, mesh shader support, double-precision data, tessellation and geometry stages, and sample-rate shading at [`vktFragmentShadingBarycentricTests.cpp`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1494-L1567).

## Cross-File Verification Methods

Data tests render encoded values into an integer color image and verify the copied host-visible result buffer. Weight tests compare a tested rendering against a reference rendering using integer threshold comparison with threshold `(1,1,1,1)` at [`vktFragmentShadingBarycentricTests.cpp`](../../modules/vulkan/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.cpp#L1251-L1262).

## Level-3 Pages

- [`vktFragmentShadingBarycentricTests.cpp`](../testfiles/fragment_shading_barycentric/vktFragmentShadingBarycentricTests.md)

## Notes / Scope

No direct test-plan match was used. The category is not documented as Vulkan SC registered here because the inspected prior registration evidence did not include `fragment_shading_barycentric` in the Vulkan SC block.
