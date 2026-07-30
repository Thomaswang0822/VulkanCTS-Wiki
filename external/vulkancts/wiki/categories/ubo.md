## Overview

The `ubo` test category collects tests that check whether Vulkan implementations correctly lay out, bind, and read uniform-buffer blocks.

## Background Knowledge

No common prerequisite concepts need category-level explanation for this test category.

## Category Structure

```text
ubo
├── 2_level_array
├── 2_level_struct_array
├── 3_level_array
├── instance_array_basic_type
├── link_by_binding
├── multi_basic_types
├── multi_nested_struct
├── random
├── single_basic_array
├── single_basic_type
├── single_nested_struct
├── single_nested_struct_array
├── single_struct
├── single_struct_array
└── unsized_array
```

[`UniformBlockTests::init()`](../../modules/vulkan/ubo/vktUniformBlockTests.cpp#L446-L1256) registers all 15 direct test families. One Level-3 page covers them because the same implementation and shared case infrastructure define their layouts, generated shaders, execution paths, and result checks. The direct-family roots agree with the `vk-default/ubo.txt` and `vksc-default/ubo.txt` mustpass lists.

## How the Families Fit Together

All families compare shader uniform loads against host-generated values packed according to a source-calculated reference layout.

- The fixed-shape families vary **which fields** appear in a block: one basic member, arrays, nested arrays, structs, struct arrays, nested structs, and a final unsized array.
- `instance_array_basic_type`, `multi_basic_types`, `multi_nested_struct`, and `link_by_binding` vary **which descriptors and stages** access block instances or multiple blocks.
- The fixed families isolate declared layouts and interfaces. `random` constructs deterministic interfaces from registered feature sets and seeds, combining types, nesting, layouts, buffer arrangements, and selected feature paths.
- `std140`, `std430`, `scalar`, matrix-major, shader-stage, buffer-placement, and component-load variants apply across multiple families; they change the declaration or access path rather than defining separate category-level mechanisms.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| All direct `ubo` test families: `2_level_array`, `2_level_struct_array`, `3_level_array`, `instance_array_basic_type`, `link_by_binding`, `multi_basic_types`, `multi_nested_struct`, `random`, `single_basic_array`, `single_basic_type`, `single_nested_struct`, `single_nested_struct_array`, `single_struct`, `single_struct_array`, and `unsized_array` | [UniformBlockTests.md](../testfiles/ubo/UniformBlockTests.md) | Registration hierarchy, layout and interface dimensions, generated shader behavior, runtime result checking, feature pruning, and the meaning of a failed comparison. |