# vktTransformFeedbackPrimitiveRestartTests.cpp

## Overview

[`vktTransformFeedbackPrimitiveRestartTests.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L1) registers [`primitive_restart`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L426-L440), verifying transform-feedback output when primitive restart and primitive topology may be dynamic.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTransformFeedbackPrimitiveRestartTests.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L1)

## Registration Hierarchy

```text
transform_feedback.primitive_restart
├── dynamic_primitive_restart_dynamic_primitive_topology
├── dynamic_primitive_restart_static_primitive_topology
├── static_primitive_restart_dynamic_primitive_topology
└── static_primitive_restart_static_primitive_topology
```

## Test Families

### dynamic_primitive_restart_* / static_primitive_restart_* — Primitive restart mode matrix

The subgroup is a 2x2 matrix over dynamic/static primitive restart and dynamic/static primitive topology, with names assembled in [`createTransformFeedbackPrimitiveRestartTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L432-L438).

## Parameter Dimensions

Parameters are `dynamicPrimitiveRestart` and `dynamicPrimitiveTopology` from [`PrimitiveRestartInstance::Params`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L432-L435).

## Support / Feature Requirements

[`PrimitiveRestartCase::checkSupport()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L90-L99) requires `VK_EXT_transform_feedback`, and conditionally requires `VK_EXT_extended_dynamic_state2` and `VK_EXT_extended_dynamic_state` for dynamic primitive restart/topology.

## Verification Methods

After drawing and ending transform feedback, the instance invalidates the counter and data buffers, checks the counter upper bound, copies captured positions, and compares them with expected results in [`iterate()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L336-L370).

## Test Principles Observed
- A compact 2x2 dynamic-state matrix isolates primitive restart from primitive topology dynamism.
- Degenerate-triangle behavior is handled by allowing a lower counter while still validating captured positions.

## Notes / Uncertainties

- This page documents source-observed registration and verification behavior. The hierarchy tree lists the complete direct children of the documented registered group.
