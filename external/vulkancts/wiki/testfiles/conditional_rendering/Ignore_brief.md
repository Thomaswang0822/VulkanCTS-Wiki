# Understanding Brief: `conditional_rendering.conditional_ignore`

## One-Sentence Test Purpose

This family checks that commands outside Vulkan's conditional-rendering affected-command list retain their normal behavior inside an active conditional block.

## Background Knowledge

### Affected and unaffected commands

Conditional rendering does not suppress every command recorded between begin and end. Vulkan defines an affected-command set; the ignore family targets commands outside that set and verifies their ordinary effects.

### Observable resource state

The test observes images, depth/stencil attachments, buffers, queries, timestamps, and other command-specific outputs. These resources turn command execution into a result that can be compared or inspected.

### Conditional command-buffer state

The condition may be established in primary or secondary command buffers and may be inherited by nested execution paths. The location of the state is a test dimension, while the unaffected-command rule remains the same.

## One Concrete Example

A clear-color case initializes an attachment, records the clear inside an active conditional-rendering block, submits the command buffer, and checks that the clear took effect even when the condition value would suppress an affected command.

## End-to-End Test Flow

```text
[host] choose an ignored command and condition variant
[host] create and initialize the command's observable resource
[host] record the command inside the selected conditional scope
[device] execute the ignored command normally
[host] synchronize, read back, and compare the command-specific result
```

## Generated Test Artifacts and Bound Resources

The family binds the resources required by each command class: attachments for clears and blits, buffers for copies, fills, and updates, query objects for query operations, and command-specific resources for ray tracing where registered. Shader stages appear only in paths that use a draw or dispatch as an observation mechanism.

## What Is Checked

Each case compares the observed result with the ordinary result expected for the selected command. A command that is unaffected by conditional rendering must not lose its effect merely because a conditional block surrounds it.

## Behavior Parameter Identification

> **Behavior parameter:** ignored command area
>
> **Candidate values:** binding, transfer, clear, query, synchronization, update, and other registered unaffected commands

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| ignored command area | Conditional suppression was applied to a command that should execute, or the command's result was not made visible to the host. |
| command-buffer variant | Conditional state was incorrectly propagated at a primary, secondary, inherited, or nested boundary. |
| result resource | The command or its synchronization and readback path produced an unexpected resource state. |

## Important Variations and Special Cases

- Inverted and non-inverted condition values provide the same unaffected-command expectation through different predicate states.
- Host-visible and device-local condition buffers exercise different storage and staging paths.
- Command-specific extensions and features gate specialized groups; unsupported groups are skipped.
- The family deliberately contrasts affected-command tests with commands that must ignore conditional rendering.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Registration and command areas | [vktConditionalIgnoreTests.cpp](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L1450-L1535) | Defines the direct ignored-command groups. |
| Runtime and results | [vktConditionalIgnoreTests.cpp](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L400-L1015) | Records commands and checks command-specific output. |
| Shared condition matrix | [vktConditionalRenderingTestUtil.hpp](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L144) | Defines condition and command-buffer variants. |
| Conditional semantics | [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2086-L2167) | Defines which commands are affected. |
| Mustpass coverage | [conditional-rendering.txt](../../../mustpass/main/vk-default/conditional-rendering.txt) | Lists executable ignore-family paths. |

## Questions / Risk Points for User Audit

- Are all command areas described as unaffected only where the current specification and source support that claim?
- Are resource-visibility failures kept distinct from incorrect conditional suppression?
- Are specialized ray-tracing and synchronization branches accurately scoped to registered variants?

## Conversion Notes for Final Wiki Rewrite

- Keep the tree to direct registered command areas; describe generated condition variants in tables and prose.
- Use one representative no-shader clear case because it makes the unaffected-command rule easiest to see.
- Keep command-specific result types and support requirements in the runtime and pruning sections.
