# Understanding Brief: spirv_assembly instruction graphics cross_stage

## One-Sentence Test Purpose

This test checks whether graphics pipeline stages pass matching SPIR-V interface values correctly when `Flat`, `NoPerspective`, or `RelaxedPrecision` decorations appear at selected producer or consumer interfaces.

## Background Knowledge

### Stage interfaces and matching

A pre-rasterization shader stage writes `Output` variables, and the next stage reads corresponding `Input` variables. Vulkan requires every non-built-in input to have an interface match in the preceding stage. Matching includes compatible types, locations, and structure members; interpolation decorations and the input/output `RelaxedPrecision` difference are exceptions to the otherwise-equivalent-decoration rule ([interface matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L119-L190)).

Why it matters here:
- The test transports the same color through vertex, optional tessellation and geometry stages, then a fragment shader compares redundant representations of it.
- `basic_type` uses separate scalar and vector variables; `interface_blocks` transports a `vec4` and `mat2` inside a block.

### Interpolation decorations

A fragment input without an interpolation decoration uses perspective-correct interpolation. `NoPerspective` selects linear interpolation, while `Flat` selects the provoking vertex's value ([interpolation decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#L2879-L2915)). `RelaxedPrecision` permits lower precision but does not change interface matching merely because it appears on one side of an input/output match ([interface matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L126-L135)).

Why it matters here:
- The red-to-green vertices make interpolation visible in the rendered color.
- Decoration placement is deliberate. The test observes valid producer placement, matching vertex-fragment placement, and the different behavior when an interpolation decoration exists only on the fragment input while intermediate stages are present.

## One Concrete Example

For `spirv_assembly.instruction.graphics.cross_stage.basic_type.flat`, the selected first internal option puts `Flat` on the vertex outputs. The authored SPIR-V assigns locations 0 through 4 to a full color plus scalar, `vec2`, `vec3`, and `vec4` views of that color. The fragment shader checks that each view agrees with the matching components of `color_in`; it turns failed component checks white. The host expects the flat, provoking-vertex color for this option.

## End-to-End Test Flow

```text
[host] choose a qualifier leaf and its internal decoration-placement options
[host] create four red/green vertex records, a 51x51 RGBA color attachment, and reference images
[host] assemble CTS-authored SPIR-V text into shader binaries and create each supported graphics pipeline
[host] clear the attachment, bind the vertex buffer and pipeline, and draw four vertices
[device] pass interface data through vertex and optional tessellation/geometry stages
[device] compare redundant interface values in the fragment shader and write the color result
[host] copy the image to host-visible memory and compare with a 0.05 threshold
[host] require either a matching expected image or, for the intentional negative paths, a non-match
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `CrossStageBasicTestsCase::initPrograms` and `CrossStageInterfaceTestsCase::initPrograms` build CTS-authored SPIR-V 1.3 assembly strings, then add stage variants to `spirvAsmSources` ([basic-type builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L686-L1785), [interface-block builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L1808-L2713)).
- The selected pipeline is VF, VTF, VGF, or VTGF, limited by the device's tessellation and geometry feature bits ([stage selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L253-L275)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | vertex binding 0 | read by vertex shader | no | Supplies four positions and red/green colors. |
| Color attachment | yes | framebuffer attachment | written by fragment output | yes | Provides the observable image. |
| `VkShaderModule` objects | yes | graphics pipeline stages | execute during draw | no | Hold the authored assembly variants. |
| Readback buffer | yes | transfer destination | written by image copy | yes | Carries the attachment pixels to `floatThresholdCompare`. |

## What Is Checked

- `checkImage` copies the attachment to a host-visible buffer, invalidates it, and compares all pixels with the chosen reference image using a per-component threshold of `0.05` ([readback and comparison](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L546-L595)).
- `flat` compares either the interpolation reference for decoration on the vertex output or the solid red reference for the VF placement variants. `no_perspective` distinguishes the perspective and linear interpolation references. `relaxedprecision` uses the interpolation reference for its only all-stages option ([reference selection and oracle](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L277-L295), [expected-pass/expected-fail branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L354-L387)).
- For `flat` and `no_perspective` decoration on the fragment input with VTF, VGF, or VTGF, the test intentionally requires `checkImage(referenceImage1)` to fail. This is a negative oracle, not an expected CTS case failure.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf, because each leaf selects one interface representation plus one decoration semantics.
>
> **Candidate values:** `basic_type.flat`, `basic_type.no_perspective`, `basic_type.relaxedprecision`, `interface_blocks.flat`, `interface_blocks.no_perspective`, `interface_blocks.relaxedprecision`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic_type.flat` | `Flat` decoration placement or provoking-vertex interpolation for separately declared scalar/vector interface variables is wrong; the fragment consistency checks or image comparison may also be wrong. |
| `basic_type.no_perspective` | `NoPerspective` placement or linear interpolation for separately declared scalar/vector interface variables is wrong; the perspective-versus-linear reference selection may also be wrong. |
| `basic_type.relaxedprecision` | `RelaxedPrecision` propagation or permitted precision behavior across the basic-variable interface is wrong; the looser shader epsilon or image comparison may also be wrong. |
| `interface_blocks.flat` | `Flat` decoration handling, block/member interface matching, or block-member transport through the selected stages is wrong. |
| `interface_blocks.no_perspective` | `NoPerspective` handling, block/member interface matching, or linear block-member interpolation is wrong. |
| `interface_blocks.relaxedprecision` | `RelaxedPrecision` handling for block variables or members, block transport, or the relaxed comparison tolerance is wrong. |

All leaves share vertex-buffer setup, render pass, pipeline creation, readback, and threshold comparison. A shared failure cannot by itself isolate those mechanisms from stage-interface behavior.

## Important Variations and Special Cases

- The six registered leaves are present in both `vk-default/spirv-assembly.txt` and `vksc-default/spirv-assembly.txt`; source does not compile the family out for Vulkan SC.
- `flat` and `no_perspective` each carry three internal decoration options: vertex only, fragment only, and all shaders. `relaxedprecision` has one all-shaders option ([registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2717-L2746)). These are runtime iterations, not extra registered mustpass leaves.
- VF always runs. VTF requires `tessellationShader`; VGF requires `geometryShader`; VTGF requires both. Unsupported optional stage combinations are not created.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Runtime and expected-result logic | [CrossStageTestInstance::iterate](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L182-L390) | Stage selection, rendering, reference choice, and pass/fail branch. |
| Basic-type SPIR-V builder | [CrossStageBasicTestsCase::initPrograms](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L686-L1785) | Decorations and the basic-variable producer/consumer modules. |
| Interface-block SPIR-V builder | [CrossStageInterfaceTestsCase::initPrograms](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L1808-L2713) | Block declarations and optional-stage modules. |
| Image oracle | [checkImage](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L546-L595) | Copyback and threshold comparison. |
| Leaf registration | [createCrossStageInterfaceTests](../../../modules/vulkan/spirv_assembly/vktSpvAsmCrossStageInterfaceTests.cpp#L2717-L2746) | Exact registered leaf names and internal options. |
| Vulkan interface rules | [Interface Matching](../../../../vulkan-docs/src/chapters/interfaces.adoc#L119-L190) | Matching and `RelaxedPrecision` exception. |

## Questions / Risk Points for User Audit

- Does the distinction between registered leaves and their internal decoration-placement/stage iterations remain clear?
- Does the negative image oracle read as an intentional expected non-match rather than a test case that must fail?
- Does the failure mapping preserve the common setup and readback localization limit?

## Conversion Notes for Final Wiki Rewrite

- Keep the test case leaf as the behavior parameter and copy the failure table verbatim.
- Use the selected `basic_type.flat` vertex producer as the representative CTS-authored SPIR-V walkthrough. The page should describe the fragment checker and interface-block variation without reconstructing GLSL.
- Publish the selected source assembly once under `#### Source Code`; validate the extracted text with `spirv-as --target-env spv1.3`, `spirv-val --target-env spv1.3`, and `spirv-dis`, but do not publish a duplicate `#### SPIR-V` section.
