# vktRenderPassSparseRenderTargetTests

## Source

[vktRenderPassSparseRenderTargetTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp)

## Registration

Added to `suballocation` subgroup (monolithic pipeline, non-SC).

Registered group name: `"sparserendertarget"` ([L870](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L870))

## Test Families

```
sparserendertarget
+-- SparseRenderTargetTestInstance
    Tests render pass with sparse-resident color images.
    Each supported format becomes an individual test case.
```

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| Formats | 44 color formats ([L797-L848](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L797-L848)) |
| Test naming | Each format becomes a test case named by lowercasing the format enum |

## Support Requirements

| Requirement | Condition |
|-------------|-----------|
| sparseResidencyImage2D feature | Always ([L776](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L776)) |
| VK_KHR_create_renderpass2 | For renderpass2 ([L769](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L769)) |
| VK_KHR_dynamic_rendering | For dynamic rendering ([L772](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L772)) |
| VK_KHR_maintenance5 | For VK_FORMAT_A8_UNORM_KHR ([L765](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L765)) |
| Sparse image format properties | Must be non-empty |

## Verification

| Aspect | Method |
|--------|--------|
| Color | tcu::floatThresholdCompare against reference ([L643](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L643)) |
| Results | Collected via tcu::ResultCollector |
