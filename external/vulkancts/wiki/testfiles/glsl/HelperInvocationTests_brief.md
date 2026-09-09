## Purpose

This brief supports `HelperInvocationTests.md`, the singular `glsl.helper_invocation` fragment-render family. It explains the helper-lane load oracle and the five shader-generation contexts without conflating them with the plural shader-executor family.

## Behavior Axis

The primary axis is the registered leaf: straight-line, quad-uniform branch, quad-uniform loop, explicit-gradient sample, and function-boundary round trip. All leaves share the same 16×16 texture, 32-element local array, quad comparison, and host result oracle.

## What Failure Means

### Failure Cause Mapping

| Result | Interpretation |
|---|---|
| Failed comparison bit | The loaded value differed from the source texel. |
| No shaded fragments | The draw produced no checked results. |
| No helper bit | The run did not exercise a helper invocation. |
| Pass | Every checked loaded value matched and at least one helper lane participated. |

## Source Mapping

- Registration: `vktShaderRenderHelperInvocationTests.cpp`, `createHelperInvocationTests`.
- Shader generation: `HelperInvocationLoadCase::initPrograms`.
- Support: `HelperInvocationLoadCase::checkSupport`.
- Host oracle: `HelperInvocationLoadInstance::verifyResult`.
- Mustpass: `vk-default/glsl.txt` and `vksc-default/glsl.txt`, five singular paths each.

## Resolved Risks

The representative GLSL was compiled with `glslangValidator -V --target-env spirv1.3`, validated with `spirv-val --target-env spv1.3`, and disassembled with `spirv-dis`. The generated artifact is included in the page.
