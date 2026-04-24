# [vktApiFragmentShaderOutputTests.cpp](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L1)

## Overview

Tests fragment shader output interactions with render pass color attachments. Validates three scenarios: shader output locations without corresponding attachments, attachments without corresponding shader output locations, and mismatched signedness between shader output types and attachment formats.

## Role of File

Implementation-heavy. Contains test instance logic, shader generation, and registration in a single source file (~775 lines). The public entry point [createFragmentShaderOutputTests()](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L698) assembles the full test tree.

## Source Code

- Source: [vktApiFragmentShaderOutputTests.cpp](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L1)
- Header: [vktApiFragmentShaderOutputTests.hpp](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.hpp#L1)
- Parent registration: `api` test group, child `fragment_shader_output` (non-VKSC only)

## Registration Path

```
api
 +-- fragment_shader_output
      +-- location_no_attachment
      +-- attachment_no_location
      +-- different_signedness
```

## Test Hierarchy

```
fragment_shader_output
 +-- location_no_attachment
 |    +-- <format_permutation_name>   -- e.g. unorm2unorm_snorm2snorm_uint2uint_sint2sint
 +-- attachment_no_location
 |    +-- <format_permutation_name>   -- e.g. unorm2unorm_snorm2snorm_uint2uint_sint2sint
 +-- different_signedness
      +-- <format_pair_name>          -- e.g. unorm2sint_snorm2uint
```

## Test Families

### Location No Attachment Family

Tests the case where a fragment shader writes to an output location that has no corresponding entry in `pColorAttachments`. The shader writes to `location = N` (where N equals the attachment count), while the render pass has fewer color attachments. The test verifies that the unattached location's image remains unchanged (at clear color) while all other attachments receive the shader output correctly. Defined by [LocationNoAttachment](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L61) enum value. Uses permutations of 4 formats (R8_UNORM, R8_SNORM, R8_UINT, R8_SINT) as both shader and render formats.

### Attachment No Location Family

Tests the case where `pColorAttachments` contains an entry for which the fragment shader has no corresponding output location. The shader skips output at the middle location index while the render pass has an attachment for it. The test verifies that the skipped attachment's image remains unchanged (at clear color) while all other attachments receive the shader output correctly. Defined by [AttachmentNoLocation](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L65) enum value. Uses permutations of 4 formats.

### Different Signedness Family

Tests the case where fragment shader output types have different signedness than the attachment format (e.g., UNORM shader output with SINT attachment, or UINT shader output with SNORM attachment). Only pairs where the signedness differs (one signed, one unsigned) are generated. Defined by [DifferentSignedness](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L69) enum value. All attachments are expected to render with the shader's output value reinterpreted according to the render format.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Test Case | LocationNoAttachment, AttachmentNoLocation, DifferentSignedness |
| Shader Format | R8_UNORM, R8_SNORM, R8_UINT, R8_SINT |
| Render Format | R8_UNORM, R8_SNORM, R8_UINT, R8_SINT |
| Format Pairing (LocationNoAttachment/AttachmentNoLocation) | All permutations of 4 formats (shader format = render format) |
| Format Pairing (DifferentSignedness) | Only cross-signedness pairs (UNORM/SNORM with SINT/UINT and vice versa) |

## Support / Feature Requirements

- Render format must support `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` and `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` ([checkSupport()](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L245))
- For LocationNoAttachment: attachment count + 1 must not exceed `maxColorAttachments` ([checkSupport()](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L253))
- For other cases: attachment count must not exceed `maxColorAttachments` ([checkSupport()](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L264))

## Verification Methods

- [verifyResults()](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L465): Reads back attachment pixel data and checks:
  - For LocationNoAttachment/AttachmentNoLocation: the mismatched attachment's buffer must be unchanged (clear color), all others must be rendered correctly
  - For DifferentSignedness: all attachments must be rendered with the expected value (shader output reinterpreted per render format)
  - Integer formats use exact match; float formats use tolerance of 0.001
  - [isBufferUnchanged()](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L475): checks buffer matches clear color
  - [isBufferRendered()](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L502): checks buffer matches expected shader output value

## Test Principles Observed

- Shader generation dynamically creates fragment shaders with the correct output types and locations based on test configuration ([initPrograms()](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L291))
- Clear colors are distinct per attachment to enable verification of which attachments were written ([makeClearColors()](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L431))
- Test uses 64x64 pixel images with a fullscreen triangle draw

## Notes / Uncertainties

- The DifferentSignedness tests may produce undefined behavior per the Vulkan spec when shader output and attachment format signedness mismatch; the test appears to validate that the implementation handles this gracefully rather than crashing
- The format permutation naming uses a shorthand like `unorm2unorm` meaning shader=R8_UNORM, render=R8_UNORM ([makeTitle()](../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L669))
- Only R8-width formats are tested; wider formats or multi-channel format combinations are not covered
