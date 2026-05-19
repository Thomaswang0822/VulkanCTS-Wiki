# vktTessellationLimitsTests.cpp

## Overview

[`vktTessellationLimitsTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L1) registers [`limits`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L117-L141), a state-query style subgroup for required tessellation device limits.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTessellationLimitsTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L1)

## Registration Hierarchy

This file contributes the [`tessellation.limits`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L1) registration path.

```text
tessellation.limits
├── max_tessellation_control_per_patch_output_components
├── max_tessellation_control_per_vertex_input_components
├── max_tessellation_control_per_vertex_output_components
├── max_tessellation_control_total_output_components
├── max_tessellation_evaluation_input_components
├── max_tessellation_evaluation_output_components
├── max_tessellation_generation_level
└── max_tessellation_patch_size
```

## Test Families

### max_tessellation_control_per_patch_output_components — Max Tessellation Control Per Patch Output Components

The case is one of the visible limit entries in [`cases[]`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L141), comparing a queried device limit against the Vulkan-required minimum encoded in the table.

### max_tessellation_control_per_vertex_input_components — Max Tessellation Control Per Vertex Input Components

The case is one of the visible limit entries in [`cases[]`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L141), comparing a queried device limit against the Vulkan-required minimum encoded in the table.

### max_tessellation_control_per_vertex_output_components — Max Tessellation Control Per Vertex Output Components

The case is one of the visible limit entries in [`cases[]`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L141), comparing a queried device limit against the Vulkan-required minimum encoded in the table.

### max_tessellation_control_total_output_components — Max Tessellation Control Total Output Components

The case is one of the visible limit entries in [`cases[]`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L141), comparing a queried device limit against the Vulkan-required minimum encoded in the table.

### max_tessellation_evaluation_input_components — Max Tessellation Evaluation Input Components

The case is one of the visible limit entries in [`cases[]`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L141), comparing a queried device limit against the Vulkan-required minimum encoded in the table.

### max_tessellation_evaluation_output_components — Max Tessellation Evaluation Output Components

The case is one of the visible limit entries in [`cases[]`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L141), comparing a queried device limit against the Vulkan-required minimum encoded in the table.

### max_tessellation_generation_level — Max Tessellation Generation Level

The case is one of the visible limit entries in [`cases[]`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L141), comparing a queried device limit against the Vulkan-required minimum encoded in the table.

### max_tessellation_patch_size — Max Tessellation Patch Size

The case is one of the visible limit entries in [`cases[]`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L141), comparing a queried device limit against the Vulkan-required minimum encoded in the table.

## Parameter Dimensions

The parameter dimension is the [`LIMIT_*`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L141) selector paired with a required minimum value such as 64 or 32 in the registration table.

## Support / Feature Requirements

The test checks [`features.tessellationShader`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L79-L80) before querying limit values.

## Verification Methods

Verification is a device-limit comparison performed by the limit test function registered through [`addFunctionCase()`](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L141).

## Test Principles Observed
- The subgroup documents required minimum capabilities rather than drawing output.

## Notes / Uncertainties

- The page summarizes behavior observed in the inspected tessellation source files and does not infer additional generated cases beyond visible loops, arrays, or mustpass-confirmed paths.
