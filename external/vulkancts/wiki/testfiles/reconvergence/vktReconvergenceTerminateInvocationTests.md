# vktReconvergenceTerminateInvocationTests

This file implements the `reconvergence.terminate_invocation` branch. It is included by the main reconvergence source [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L24-L25), declared in its own header [vktReconvergenceTerminateInvocationTests.hpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.hpp#L30-L35), and registered into the category tree through `createTerminateInvocationTests(testCtx)` [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7943-L7947).

## Source Files

| Role | Link |
|------|------|
| Terminate-invocation implementation | [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp) |
| Factory declaration | [vktReconvergenceTerminateInvocationTests.hpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.hpp#L30-L35) |
| Parent category implementation | [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7943-L7947) |

## Registration Hierarchy

```text
reconvergence.terminate_invocation
├── bit_count
├── terminate_helpers
├── oob_read
└── quad_any
```

## Test Families

### bit_count — Terminated invocations removed from ballot counts

This child uses `SubCase::BIT_COUNT` and is registered as `bit_count` [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L653-L660). The shader records an all-invocation ballot, terminates invocations selected by subgroup invocation ID modulo the divisor, takes a second alive ballot, and marks success when the terminated and alive counts add up to the original count [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L276-L306).

### terminate_helpers — Terminating helper invocations

This child uses `SubCase::TERMINATE_HELPERS` and is registered as `terminate_helpers` [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L661-L664). Its shader terminates only helper invocations, then expects `subgroupAny(should_terminate)` to be false afterward and writes sampled color with the blue component set to 1 [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L308-L330).

### oob_read — Terminated invocation out-of-bounds read robustness

This child uses `SubCase::OOB_READ` and is registered as `oob_read` [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L665-L668). The shader terminates selected invocations and then chooses an out-of-bounds storage-buffer index only for the terminated invocations; the source comment records the expected no-crash behavior [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L332-L354).

### quad_any — Quad operations after termination

This child uses `SubCase::QUAD_ANY` and is registered as `quad_any` [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L669-L672). The shader terminates selected invocations and helpers, then uses `subgroupQuadAny(gl_HelperInvocation)`; the comment states this condition should remain false if `terminateInvocation` is implemented properly [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L356-L376).

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Subcases | `BIT_COUNT`, `TERMINATE_HELPERS`, `OOB_READ`, `QUAD_ANY` | [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L55-L61) |
| Divisor | `2` for `bit_count`, `oob_read`, and `quad_any`; `0` for `terminate_helpers` | [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L67-L77) |
| Helper-invocation built-in use | `terminate_helpers` and `quad_any` use `gl_HelperInvocation` | [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L84-L87) |
| Framebuffer extent | 32 by 32 pixels | [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L386-L390) |
| Format | `VK_FORMAT_R8G8B8A8_UNORM` | [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L390-L393) |

## Support / Feature Requirements

`bit_count` and `terminate_helpers` require `VK_KHR_shader_maximal_reconvergence` because `needsMaximalReconvergence()` returns true for those subcases [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L166-L169), [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L196-L200). The minimum API version is Vulkan 1.3 for subcases using `gl_HelperInvocation` and Vulkan 1.1 otherwise [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L201-L203). All cases require fragment-stage subgroup support, `VK_SUBGROUP_FEATURE_BASIC_BIT`, and `VK_KHR_shader_quad_control`; `bit_count` additionally requires ballot support, while `terminate_helpers` and `quad_any` require vote support [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L205-L226).

## Verification Methods

All subcases render a full-screen triangle into an R8G8B8A8 framebuffer, copy the image to a host-visible buffer, and dispatch to subcase-specific result checking [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L386-L571). The `bit_count` and `oob_read` checks build a reference image where terminated pixels remain at the clear color and non-terminated pixels match the sampled texture with blue set to 1; comparison uses `tcu::floatThresholdCompare` with a red-channel tolerance for sampling imprecision [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L574-L599). The `terminate_helpers` check expects every pixel to match the sampled texture with blue set to 1 [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L602-L623). The `quad_any` check expects terminated pixels to remain at the clear color and other pixels to be exact blue, using a zero threshold [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L626-L648).

## Notes

This file registers its own `terminate_invocation` group and therefore receives a Level-3 page under the analyzer rule for registered source files [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L653-L675).
