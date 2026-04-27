# [vktApiFragmentShaderOutputTests.cpp](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L1)

## Overview

Tests fragment shader output behavior when there is a mismatch between shader output locations and render pass color attachments. Covers three scenarios: a shader output location with no corresponding attachment, an attachment with no corresponding shader output, and shader/attachment format signedness mismatches.

## Role of File

Implementation-heavy. Contains shader generation, rendering pipeline setup, result verification, and test registration.

## Source Code

| File | Description |
|------|-------------|
| [vktApiFragmentShaderOutputTests.cpp](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L1) | Test implementation and registration |
| [vktApiFragmentShaderOutputTests.hpp](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.hpp#L1) | Declares `createFragmentShaderOutputTests` |
| [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L134) | Parent registration: `apiTests->addChild(createFragmentShaderOutputTests(testCtx))` |

## Registration Path

```
api
  +-- fragment_shader_output
       +-- location_no_attachment
       |    +-- <permutation test cases>
       +-- attachment_no_location
       |    +-- <permutation test cases>
       +-- different_signedness
            +-- <permutation test cases>
```

## Test Hierarchy

```
fragment_shader_output
  +-- location_no_attachment
  |    Fragment shader writes to a location beyond pColorAttachments count
  |    +-- <format permutation tests>
  |         e.g. unorm2unorm_snorm2snorm_uint2uint_sint2sint
  +-- attachment_no_location
  |    pColorAttachments has an entry with no matching shader output location
  |    +-- <format permutation tests>
  +-- different_signedness
       Shader output type differs from attachment format signedness
       +-- <format permutation tests>
            e.g. unorm2uint_uint2unorm_sint2sint_uint2uint
```

## Test Families

### fragment_shader_output

Group name verified at [vktApiFragmentShaderOutputTests.cpp:728](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L728): `new tcu::TestCaseGroup(testCtx, "fragment_shader_output", "Verify fragment shader output with multiple attachments")`.

Three test cases defined at [lines 711-715](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L711):

| Subgroup | ShaderOutputCases | Description |
|----------|-------------------|-------------|
| `location_no_attachment` | LocationNoAttachment | Shader writes to location N but pColorAttachments has fewer than N+1 entries |
| `attachment_no_location` | AttachmentNoLocation | pColorAttachments has entry at index N but shader does not output to location N |
| `different_signedness` | DifferentSignedness | Shader output type (UNORM/SNORM/UINT/SINT) differs from attachment format |

For `location_no_attachment` and `attachment_no_location`, test cases are generated from permutations of 4 R8 variants (UNORM, SNORM, UINT, SINT) at [lines 700-705](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L700). For `different_signedness`, test cases use pairs of format combinations where signedness differs ([lines 717-726](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L717)).

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Shader format | R8_UNORM, R8_SNORM, R8_UINT, R8_SINT | 4 formats at [line 701](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L701) |
| Render format | R8_UNORM, R8_SNORM, R8_UINT, R8_SINT | Same 4 formats |
| Test case | LocationNoAttachment, AttachmentNoLocation, DifferentSignedness | 3 cases |
| Render size | 64x64 | Hard-coded at [line 599](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L599) |

## Support / Feature Requirements

- `maxColorAttachments` must be sufficient for the number of attachments used ([lines 251-272](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L251))
- Each render format must support `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT | VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` ([lines 276-288](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L276))

## Verification Methods

- **LocationNoAttachment / AttachmentNoLocation**: The attachment at the mismatched index must remain at its clear color (unchanged), while all other attachments must contain the shader-written value. Verified by `isBufferUnchanged` and `isBufferRendered` at [lines 566-576](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L566).
- **DifferentSignedness**: All attachments must contain the rendered value. For UNORM/SNORM, expects 1.0f; for UINT, expects `unsignedIntColor` (123); for SINT, expects `signedIntColor` (111) ([lines 578-583](../../../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L578)).

## Test Principles Observed

- Mismatch validation: tests edge cases in the shader-to-attachment binding contract
- Format coverage: tests all signedness combinations for R8 variants
- Pixel-level verification: reads back attachment contents and compares against expected values

## Notes / Uncertainties

- The `different_signedness` tests do not use validation layers; they verify pixel output values rather than checking for validation errors
- The number of test cases in `different_signedness` can be large due to the combinatorial pairing of format combinations
- The test uses `std::next_permutation` to generate permutations for the non-signedness cases, which produces all unique orderings of the 4 formats
