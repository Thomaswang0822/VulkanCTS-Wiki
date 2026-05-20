# Push Constant Bank Tests

Tests NV push-constant bank behavior both with ordinary push constants and descriptor-heap push data integration.

## Source

- [`vktBindingPushConstantBankTests.cpp`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp)

## Registration Hierarchy

```text
binding_model.push_constant_bank
├── basic
└── descriptor_heap
```

## Test Families

### basic — Basic push-constant bank tests without descriptor heap

Basic tests using `vkCmdPushConstants2` + `VkPushConstantBankInfoNV`. Generated cases vary compute/graphics use, bank count, and member offsets. Created at [`vktBindingPushConstantBankTests.cpp:1391`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1391); populated via [`populateBasicTests`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1392); added to the parent group at [`vktBindingPushConstantBankTests.cpp:1393`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1393).

### descriptor_heap — Push-constant bank tests with descriptor heap integration

Tests using `vkCmdPushDataEXT` + `VkPushConstantBankInfoNV` for descriptor-heap push-data paths. Created at [`vktBindingPushConstantBankTests.cpp:1396`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1396); populated via [`populateDescriptorHeapTests`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1397); added to the parent group at [`vktBindingPushConstantBankTests.cpp:1398`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1398).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingPushConstantBankTests.cpp:1388`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1388) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingPushConstantBankTests.cpp:1391`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1391) |
| Build availability | Root or nested registration determines whether the group is always present or guarded by `CTS_USES_VULKANSC` |

## Support / Feature Requirements

Support checks are implemented near [`vktBindingPushConstantBankTests.cpp:1145`](../../../modules/vulkan/binding_model/vktBindingPushConstantBankTests.cpp#L1145). Requirements vary by selected case and extension path; this page records only the recurring gates visible in the inspected file.

## Verification Methods

Cases validate shader-visible push-constant bank data after command recording and descriptor-heap related push-data paths.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
