# Fragment Shader Interlock

This page summarizes the Vulkan CTS `fragment_shader_interlock` category, which verifies `VK_EXT_fragment_shader_interlock` behavior through a generated `basic` test matrix.

## Registration Entry Point

The category is registered through [`FragmentShaderInterlock::createTests()`](../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockTests.cpp#L51-L54). Its root dispatcher adds exactly one child, `basic`, via [`createChildren()`](../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockTests.cpp#L37-L42).

## Subgroup Structure

```text
fragment_shader_interlock
└── basic
```

## File Inventory

| File | Role | Wiki page |
|---|---|---|
| [`vktFragmentShaderInterlockTests.cpp`](../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockTests.cpp#L1) | Root registration file | [`vktFragmentShaderInterlockTests.cpp`](../testfiles/fragment_shader_interlock/vktFragmentShaderInterlockTests.md) |
| [`vktFragmentShaderInterlockBasic.cpp`](../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L1) | Registered implementation file for `basic` | [`vktFragmentShaderInterlockBasic.cpp`](../testfiles/fragment_shader_interlock/vktFragmentShaderInterlockBasic.md) |
| [`vktFragmentShaderInterlockBasic.hpp`](../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.hpp#L32-L35) | Declares the `basic` factory | Header only |
| [`CMakeLists.txt`](../../modules/vulkan/fragment_shader_interlock/CMakeLists.txt#L1) | Build inventory | Build metadata |

## Cross-File Test Themes

The dispatcher exposes the `basic` branch, while [`vktFragmentShaderInterlockBasic.cpp`](../testfiles/fragment_shader_interlock/vktFragmentShaderInterlockBasic.md) generates the full case matrix. The implementation writes shaders using `GL_ARB_fragment_shader_interlock`, emits the selected pixel/sample/shading-rate interlock layout qualifier, and performs image or SSBO read/modify/write operations inside an invocation interlock region at [`vktFragmentShaderInterlockBasic.cpp`](../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L218-L327).

## Cross-File Parameter Dimensions

The generated matrix varies discard behavior, resource type, interlock mode, sample count, sample-shading state, and dimensions. The registration loops and value tables are in [`createBasicTests()`](../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L787-L862). The mustpass list confirms the category path shape with entries such as `fragment_shader_interlock.basic.discard.image.pixel_ordered...` at [`fragment-shader-interlock.txt`](../../mustpass/main/vk-default/fragment-shader-interlock.txt#L1-L24).

## Cross-File Support Requirements and Feature Gates

Per-case support checks require `VK_EXT_fragment_shader_interlock`; then they require the selected pixel, sample, or shading-rate interlock feature bits. Shading-rate interlock checks are guarded out for Vulkan SC and additionally require fragment-shading-rate support for fragment shader interlock at [`vktFragmentShaderInterlockBasic.cpp`](../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L154-L185).

## Cross-File Verification Methods

The implementation copies the tested image or SSBO data into a host-visible buffer and compares every copied word against the expected interlock bitmask, with zero expected for discarded odd entries at [`vktFragmentShaderInterlockBasic.cpp`](../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L735-L772).

## Level-3 Pages

- [`vktFragmentShaderInterlockTests.cpp`](../testfiles/fragment_shader_interlock/vktFragmentShaderInterlockTests.md)
- [`vktFragmentShaderInterlockBasic.cpp`](../testfiles/fragment_shader_interlock/vktFragmentShaderInterlockBasic.md)

## Notes / Scope

No direct test-plan match was used for this category; the claims above are based on inspected source and mustpass evidence.
