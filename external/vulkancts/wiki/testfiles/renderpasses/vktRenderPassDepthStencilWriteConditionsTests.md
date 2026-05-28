# vktRenderPassDepthStencilWriteConditionsTests

## Source

[vktRenderPassDepthStencilWriteConditionsTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilWriteConditionsTests.cpp)

## Registration Hierarchy

```text
renderpasses.renderpass1.depth_stencil_write_conditions
```

Available under `renderpass1` only (non-SC). Registered at [L589](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilWriteConditionsTests.cpp#L589).

## Test Families

### depth_stencil_write_conditions — Depth/stencil write conditions for helper invocations

Tests that depth/stencil writes from helper invocations (discarded, demoted, or terminated fragments) do or do not affect the buffer. 54 test cases generated from a parameter matrix:

- **BufferType**: DEPTH (4 formats), STENCIL (2 formats)
- **DiscardType**: KILL (OpKill), DEMOTE (OpDemoteToHelperInvocation), TERMINATE (OpTerminateInvocation)
- **MutationMode**: WRITE, INITIALIZE, INITIALIZE_WRITE

Test names follow the pattern: `{buffer}_{'kill'|'terminate'|'demote'}_{'write'|'initialize'|'write_initialize'}_{format_postfix}`

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| BufferType | DEPTH, STENCIL |
| DiscardType | KILL (OpKill), DEMOTE (OpDemoteToHelperInvocation), TERMINATE (OpTerminateInvocation) |
| MutationMode | WRITE, INITIALIZE, INITIALIZE_WRITE |
| Depth formats | D32_SFLOAT_S8_UINT, D24_UNORM_S8_UINT, X8_D24_UNORM_PACK32, D32_SFLOAT |
| Stencil formats | D32_SFLOAT_S8_UINT, D24_UNORM_S8_UINT |

## Support / Feature Requirements

| Requirement | Condition |
|-------------|-----------|
| VK_EXT_shader_demote_to_helper_invocation | When DiscardType is DEMOTE ([L554](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilWriteConditionsTests.cpp#L554)) |
| VK_KHR_shader_terminate_invocation | When DiscardType is TERMINATE ([L556](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilWriteConditionsTests.cpp#L556)) |
| VK_EXT_shader_stencil_export | When BufferType is STENCIL ([L558](../../../modules/vulkan/renderpass/vktRenderPassDepthStencilWriteConditionsTests.cpp#L558)) |
| Format support | Via getPhysicalDeviceImageFormatProperties |

## Verification

| Aspect | Method |
|--------|--------|
| Depth/stencil buffer | Reads back after rendering and verifies writes from killed/terminated fragments do not affect the buffer |
| Demoted fragments | Helper invocations should not write depth/stencil per spec |
| Killed fragments | OpKill fragments must not produce depth/stencil writes |
| Terminated fragments | OpTerminateInvocation fragments must not produce depth/stencil writes |
