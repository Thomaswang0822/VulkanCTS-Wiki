# vktImageProcessingTests.cpp

## Overview

This is the **registration file** for the `image_processing` test category. It defines the top-level `createTests()` entry point and the `createChildren()` function that assembles the full test hierarchy by delegating to sub-group creation functions from the implementation files.

The file does not contain any test logic itself. It serves purely as a structural hub, wiring together the `graphics`, `api`, and `compute` sub-groups and their children.

**Source:** [vktImageProcessingTests.cpp](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp)

## Registration Hierarchy

```text
image_processing
├── graphics
├── api
└── compute
```

## Registration Details

### `createTests()` (line 83)

The public entry point exported via [vktImageProcessingTests.hpp](../../../modules/vulkan/image_processing/vktImageProcessingTests.hpp#L34). It uses `createTestGroup()` to create the root `image_processing` group with `createChildren` as the group initializer.

### `createChildren()` (line 43)

Populates the root group with three children:

| Child Group | Line | Creation Function | Source File |
|---|---|---|---|
| `graphics` | [L48](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L48) | Inline loop over pipeline construction types | This file |
| `api` | [L70](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L70) | `createImageProcessingApiTests()` | [vktImageProcessingApiTests.cpp](../../../modules/vulkan/image_processing/vktImageProcessingApiTests.cpp#L137) |
| `compute` | [L75](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L75) | `createImageProcessingBlockMatchingComputeTests()` | [vktImageProcessingBlockMatchingTests.cpp](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2265) |

### `graphics` Sub-group Construction (line 48-67)

The `graphics` group is built inline. It iterates over three `PipelineConstructionType` values and creates a sub-group for each:

| Sub-group Name | PipelineConstructionType | Line |
|---|---|---|
| `monolithic` | `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` | [L54](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L54) |
| `fast_lib` | `PIPELINE_CONSTRUCTION_TYPE_FAST_LINKED_LIBRARY` | [L55](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L55) |
| `shader_objects` | `PIPELINE_CONSTRUCTION_TYPE_SHADER_OBJECT_UNLINKED_SPIRV` | [L56](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L56) |

Each pipeline construction sub-group receives a single child: `block_matching`, created by `createImageProcessingBlockMatchingGraphicsTests()` at [L62](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L62).

### `compute` Sub-group Construction (line 75-78)

The `compute` group receives a single child: `block_matching`, created by `createImageProcessingBlockMatchingComputeTests()` at [L76](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L76).

## Test Families

This file registers no test families directly. All test families are contributed by the implementation files:

- **api** family: registered by [vktImageProcessingApiTests.cpp](./vktImageProcessingApiTests.md)
- **block_matching** family: registered by [vktImageProcessingBlockMatchingTests.cpp](./vktImageProcessingBlockMatchingTests.md)

## Dependencies

| Include | Role |
|---|---|
| `vktImageProcessingTests.hpp` | Declares `createTests()` |
| `vktImageProcessingApiTests.hpp` | Declares `createImageProcessingApiTests()` |
| `vktImageProcessingBlockMatchingTests.hpp` | Declares `createImageProcessingBlockMatchingGraphicsTests()` and `createImageProcessingBlockMatchingComputeTests()` |
| `vktTestGroupUtil.hpp` | Provides `createTestGroup()` helper |
| `vkPipelineConstructionUtil.hpp` | Defines `PipelineConstructionType` enum values |
