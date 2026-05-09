# [vktApiFragmentShaderOutputTests.cpp](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L1)

## Overview

Tests fragment shader output behavior when there is a mismatch between shader output locations and render pass color attachments. Covers three scenarios: a shader output location with no corresponding attachment, an attachment with no corresponding shader output, and shader/attachment format signedness mismatches.

## Role of File

Implementation-heavy. Contains shader generation, rendering pipeline setup, result verification, and test registration.

## Source Code

| File | Description |
|------|-------------|
| [vktApiFragmentShaderOutputTests.cpp](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L1) | Test implementation and registration |
| [vktApiFragmentShaderOutputTests.hpp](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.hpp#L1) | Declares `createFragmentShaderOutputTests` |
| [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L134) | Parent registration: `apiTests->addChild(createFragmentShaderOutputTests(testCtx))` |

## Registration Hierarchy

```text
api.fragment_shader_output
├── location_no_attachment
├── attachment_no_location
└── different_signedness
```

The confirmed Level-3 root is `fragment_shader_output`, which [createApiTests()](../../../modules/vulkan/api/vktApiTests.cpp#L134) adds directly under `api`. [createFragmentShaderOutputTests()](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L698-L760) creates that root group and registers exactly three direct child subgroups: `location_no_attachment`, `attachment_no_location`, and `different_signedness`.

## Test Families

### location_no_attachment — Shader output location without a matching attachment

[createFragmentShaderOutputTests()](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L711-L715) registers `location_no_attachment` as one of the three direct child groups under `fragment_shader_output`. In this family, the shader writes to location `N` while `pColorAttachments` provides fewer than `N + 1` attachments, matching the case description captured in the local `cases[]` table and the observed verification flow.

For this branch, [createFragmentShaderOutputTests()](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L753-L760) uses [`std::next_permutation()`](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L755) over the four `R8` format variants declared at [vktApiFragmentShaderOutputTests.cpp#L700-L705](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L700-L705) to generate leaf cases with different shader/attachment format orderings.

### attachment_no_location — Attachment without a matching shader output location

[createFragmentShaderOutputTests()](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L711-L715) registers `attachment_no_location` as the second direct child group. This family exercises the inverse mismatch: `pColorAttachments` contains an entry at index `N`, but the fragment shader does not write to location `N`.

Its leaf cases are generated through the same permutation loop used for `location_no_attachment`, again reordering the four `R8` format variants from [vktApiFragmentShaderOutputTests.cpp#L700-L705](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L700-L705) via [vktApiFragmentShaderOutputTests.cpp#L753-L760](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L753-L760).

### different_signedness — Shader and attachment formats with different signedness

[createFragmentShaderOutputTests()](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L711-L715) registers `different_signedness` as the third direct child group. This branch focuses on shader output type and attachment format pairs whose integer-vs-normalized signedness classification differs.

Before subgroup registration, [createFragmentShaderOutputTests()](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L717-L726) builds `signednessFormats` from the same four base formats by selecting shader/render pairs whose boolean signedness markers differ through an XOR test. The `different_signedness` branch then combines two distinct entries from that filtered list in the nested loops at [vktApiFragmentShaderOutputTests.cpp#L735-L749](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L735-L749), skipping duplicate shader-format and render-format reuse before creating each leaf test.

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Registration root | `api.fragment_shader_output` | Confirmed by [createApiTests()](../../../modules/vulkan/api/vktApiTests.cpp#L134) and [createFragmentShaderOutputTests()](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L728-L732) |
| Direct child subgroup names | `location_no_attachment`, `attachment_no_location`, `different_signedness` | Registered from the `cases[]` table at [vktApiFragmentShaderOutputTests.cpp#L711-L715](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L711-L715) and instantiated at [vktApiFragmentShaderOutputTests.cpp#L730-L732](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L730-L732) |
| Shader format | `R8_UNORM`, `R8_SNORM`, `R8_UINT`, `R8_SINT` | Four formats declared at [vktApiFragmentShaderOutputTests.cpp#L700-L705](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L700-L705) |
| Render format | `R8_UNORM`, `R8_SNORM`, `R8_UINT`, `R8_SINT` | Same four formats are reused for render targets |
| Test case family | `LocationNoAttachment`, `AttachmentNoLocation`, `DifferentSignedness` | Encoded in the local `cases[]` table at [vktApiFragmentShaderOutputTests.cpp#L706-L715](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L706-L715) |
| Render size | `64x64` | Hard-coded at [vktApiFragmentShaderOutputTests.cpp#L599](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L599) |

## Support / Feature Requirements

- `maxColorAttachments` must be sufficient for the number of attachments used ([vktApiFragmentShaderOutputTests.cpp#L251-L272](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L251-L272)).
- Each render format must support `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT | VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` ([vktApiFragmentShaderOutputTests.cpp#L276-L288](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L276-L288)).

## Verification Methods

- **LocationNoAttachment / AttachmentNoLocation**: The attachment at the mismatched index must remain at its clear color (unchanged), while all other attachments must contain the shader-written value. Verified by `isBufferUnchanged` and `isBufferRendered` at [vktApiFragmentShaderOutputTests.cpp#L566-L576](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L566-L576).
- **DifferentSignedness**: All attachments must contain the rendered value. For `UNORM`/`SNORM`, expects `1.0f`; for `UINT`, expects `unsignedIntColor` (`123`); for `SINT`, expects `signedIntColor` (`111`) ([vktApiFragmentShaderOutputTests.cpp#L578-L583](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L578-L583)).

## Test Principles Observed

- Mismatch validation: tests edge cases in the shader-to-attachment binding contract.
- Format coverage: tests `R8` signedness combinations and ordering-driven attachment layouts.
- Pixel-level verification: reads back attachment contents and compares against expected values.

## Notes / Uncertainties

- The `different_signedness` tests do not use validation layers; they verify pixel output values rather than checking for validation errors.
- The `different_signedness` branch can generate many leaf cases because it combines two distinct signedness-mismatched format pairs from the filtered `signednessFormats` set.
- The non-signedness branches use [`std::next_permutation()`](../../../modules/vulkan/api/vktApiFragmentShaderOutputTests.cpp#L755) over the four base formats, so the exact leaf count depends on the generated unique orderings accepted by that loop.
