# vktFragmentShaderInterlockTests.cpp

This page documents the root registration file for the Vulkan CTS `fragment_shader_interlock` category.

## Overview

[`vktFragmentShaderInterlockTests.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockTests.cpp#L1) is a dispatcher file. Its `createChildren()` implementation directly registers the `basic` subgroup through [`createBasicTests()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockTests.cpp#L37-L42), and [`createTests()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockTests.cpp#L51-L54) creates the category group using the caller-provided category name.

## Role of File

- Registration / dispatcher file.
- It includes the category header, the `basic` branch header, and test-group utility support at [`vktFragmentShaderInterlockTests.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockTests.cpp#L25-L27).
- It does not define per-case shader programs or verification logic; those are implemented in [`vktFragmentShaderInterlockBasic.cpp`](vktFragmentShaderInterlockBasic.md).

## Registration Hierarchy

```text
fragment_shader_interlock
└── basic
```

## Test Families

### basic — Basic fragment shader interlock cases

The only direct child is `basic`, registered by the dispatcher at [`vktFragmentShaderInterlockTests.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockTests.cpp#L37-L42). The detailed generated matrix is documented in [`vktFragmentShaderInterlockBasic.cpp`](vktFragmentShaderInterlockBasic.md).

## Parameter Dimensions

No parameters are created in this dispatcher file. Parameterized test cases are created by the `basic` implementation file.

## Support / Feature Requirements

This file performs no support checks. The per-case requirements are in [`FSITestCase::checkSupport()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L154-L186).

## Verification Methods

This file performs no runtime verification. Verification is implemented by the `basic` test instances.

## Test Principles

The root file keeps category registration separate from implementation so the root category exposes the single `basic` branch while the detailed matrix is built in the branch implementation.

## Notes / Uncertainties

The inspected file shows no conditional registration at the root level.
