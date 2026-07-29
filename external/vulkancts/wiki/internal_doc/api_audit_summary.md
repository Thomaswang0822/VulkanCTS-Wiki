# api Audit Summary

This summary records confirmed defects corrected in place, unresolved findings, and pages with no confirmed issues for the `api` category audit. Understanding Briefs (`*_brief.md`) are excluded from audit scope. All 52 rewritten Level-3 pages and the Level-2 `api.md` page have been audited.

## Recurring Defect Patterns

### Off-by-one source line citations

- **Mistake:** Multiple pages cited source line numbers one line above or below the actual code of interest (a parent-dispatcher `addChild` call, an `imageInfo` struct field, or an `#ifndef CTS_USES_VULKANSC` block). A reader following the GitHub `#L` fragment landed on an adjacent line, often an unrelated registration call or preprocessor directive.
- **Correction:** Adjusted each `#L`/`#L-L` fragment to point at the actual line(s) of the cited code and re-verified against the current source.
- **Pages:** `FeatureInfo.md` (`vktApiTests.cpp#L96` -> `#L95`), `Maintenance6Check.md` (`vktApiMaintenance6Check.cpp` Parameter Dimensions evidence links `#L96`/`#L97`/`#L98` -> `#L95`/`#L96`/`#L97`), `Buffer.md` (`vktApiTests.cpp#L101` -> `#L102`), `CopiesAndBlittingDynamicStateMetaOps.md` (`vktApiCopiesAndBlittingTests.cpp#L286` -> `#L285`), `FrameBoundary.md` (`vktApiTests.cpp#L127-L136` -> `#L128-L137`, `#L131` -> `#L132`).

## Pages With Only Recurring Findings

- `Maintenance6Check.md` - only the off-by-one source-line pattern above.
- `Buffer.md` - only the off-by-one source-line pattern above.

## Pages With No Confirmed Issues

- `DriverProperties.md`
- `ToolingInfo.md`
- `ExtensionDuplicates.md`
- `Maintenance7.md`
- `FormatPropertiesExtendedKHR.md`
- `MemoryRequirementInvariance.md`
- `CopyImageToBuffer.md`
- `DebugUtils.md`

## `VersionCheck.md`

### version leaf logging claim overstated

- **Mistake:** The `### version` subsection stated the leaf "logs all four" values it reads (framework maximum, available instance, device, used API). Source at `vktApiVersionCheck.cpp#L79-L95` reads all four but logs only three at lines 93-95 (availableInstanceVersion, deviceVersion, usedApiVersion); the framework maximum (`maxVulkanVersion`, line 79) is never logged.
- **Correction:** Changed "logs all four" to "logs the available instance, device, and used API versions" so the Behavior Parameters sentence matches source behavior and the page's own `### Cause Analysis`.

## `DriverProperties.md`

No confirmed issues. Registration pass; links pass.

## `FeatureInfo.md`

### Subgroup feature-flag failure coverage overstated

- **Mistake:** The Failure Cause Mapping row for `subgroup_features` and the Cause Analysis symptoms both claimed the test checks the bidirectional relationship ("`shaderSubgroupPartitioned` feature reported without the corresponding `VK_SUBGROUP_FEATURE_PARTITIONED_BIT_EXT` operation bit, or vice versa"). Source `validateSubgroupFeatures` at `vktApiFeatureInfo.cpp#L8603-L8619` contains only one guard: `if (subgroupPartitionedFeatures.shaderSubgroupPartitioned && (vk11Properties.subgroupSupportedOperations & VK_SUBGROUP_FEATURE_PARTITIONED_BIT_EXT) == 0) TCU_FAIL(...)`. The reverse direction is never checked.
- **Correction:** Removed "or vice versa" from both the Failure Cause Mapping row and the Cause Analysis symptoms so the page reflects the single-direction check the test actually performs.

### Parent registration line anchor off by one

- **Mistake:** The Overview and Source Reference Appendix cited `vktApiTests.cpp#L96` for the call that attaches the `info` family to the `api` category. In the current source, `apiTests->addChild(api::createFeatureInfoTests(testCtx));` is at line 95; line 96 is `#ifndef CTS_USES_VULKANSC`.
- **Correction:** Changed both citations from `#L96` to `#L95` so the GitHub fragment points at the actual `addChild` call.

## `DeviceDrmProperties.md`

### 0xaa fill pattern mischaracterized as covering extension fields

- **Mistake:** The Parameter Dimensions table stated the 0xaa pattern pre-fills `VkPhysicalDeviceProperties2` "so uninitialized extension fields are detectable during debugging." Source shows the opposite allocation: `deMemset(&deviceDrmProperties, 0, ...)` zero-initializes the DRM extension struct (`vktApiDeviceDrmPropertiesTests.cpp#L88`), while `deMemset(&deviceProperties2, memsetPattern, ...)` 0xaa-fills only the parent struct (`vktApiDeviceDrmPropertiesTests.cpp#L92`). The parent's main data member is the standard `VkPhysicalDeviceProperties properties` field, not an extension field, so "extension fields" misidentifies what the 0xaa pattern validates and risks a wrong mental model that the DRM extension struct is 0xaa-filled.
- **Correction:** Dropped "extension" from "uninitialized extension fields" and added a brief clarifying sentence that the DRM extension struct is zero-initialized separately, matching the source allocation at L88 and L92.

## `DeviceInitialization.md`

### enumerateDevicesAllocLeakTest OOM handling inverted

- **Mistake:** Page stated that `VK_ERROR_OUT_OF_HOST_MEMORY` from `vkEnumeratePhysicalDevices` produces a quality warning rather than a hard failure (Behavior Parameters section) and that the quality warning fires when `vkEnumeratePhysicalDevices` throws `VK_ERROR_OUT_OF_HOST_MEMORY` before leak accounting can occur (Failure Meaning section). Source shows the opposite: the catch block in `enumerateDevicesAllocLeakTest()` at `vktApiDeviceInitializationTests.cpp#L597-L602` returns a quality warning only when `e.getError() != VK_ERROR_OUT_OF_HOST_MEMORY` (i.e., for `VK_ERROR_OUT_OF_DEVICE_MEMORY` or other OOM), and falls through to the allocation-balance check when the error IS `VK_ERROR_OUT_OF_HOST_MEMORY`. `vkDefs.cpp#L37-L40` confirms `OutOfMemoryError` wraps both `VK_ERROR_OUT_OF_HOST_MEMORY` and `VK_ERROR_OUT_OF_DEVICE_MEMORY`.
- **Correction:** Edited both passages to state that an out-of-memory error other than `VK_ERROR_OUT_OF_HOST_MEMORY` (such as `VK_ERROR_OUT_OF_DEVICE_MEMORY`) produces the quality warning and skips leak accounting, while `VK_ERROR_OUT_OF_HOST_MEMORY` falls through to the balance check.

## `ToolingInfo.md`

No confirmed issues. Registration pass; links pass.

## `ExtensionDuplicates.md`

No confirmed issues. Registration pass; links pass.

## `GetDeviceProcAddr.md`

### Case Pruning list-composition claim omitted non-WSI physical-device-level extension entry points

- **Mistake:** The Design-based pruning bullet stated the auto-generated list includes "only device-level extension entry points and WSI entry points that are not device-level commands." The `vk.xml`-derived list in `vkGetDeviceProcAddr.inl` actually contains 657 vendor-suffixed extension entry points at three command levels: device-level (e.g., `vkCmdDispatchGraphAMDX`), physical-device-level non-WSI (e.g., `vkGetPhysicalDeviceMultisamplePropertiesEXT` at L425, `vkGetPhysicalDeviceFeatures2KHR` at L738), and instance-level WSI (e.g., `vkCreateXcbSurfaceKHR`). The "only ... and WSI" wording excluded the entire non-WSI physical-device-level extension category, contradicting the page's own Background Knowledge, which already lists "physical-device-level commands" as a class that must resolve to `NULL`.
- **Correction:** Replaced the bullet to read "The list includes only extension entry points at device-level, physical-device-level, and instance-level (including WSI)." The follow-on sentence about absent core commands is unchanged because it remains accurate.

## `Maintenance3Check.md`

### `support_count_*` behavior parameter description overstated verification scope

- **Mistake:** The page stated "Each case verifies that `maxVariableDescriptorCount` is consistent across zero, one, and maximum descriptor counts, and that the reported maximum is usable. Inline uniform block cases check that the count is a multiple of 4 and within `maxInlineUniformBlockSize`." This is only true for `useVariableSize=true` cases (88 of 176). For `useVariableSize=false` cases, `testCountLayoutSupport()` at `vktApiMaintenance3Check.cpp#L801-L805` only checks `maxVariableDescriptorCount == 0u`; the IUB multiple-of-4 and `maxInlineUniformBlockSize` checks live inside the `useVariableSize=true` else branch at L808-L820.
- **Correction:** Replaced "Each case verifies ..." with two scoped sentences: cases with `useVariableSize=true` verify zero/one/maximum consistency and usability, with inline uniform block cases additionally checking the multiple-of-4 and `maxInlineUniformBlockSize` constraints; cases with `useVariableSize=false` verify that `maxVariableDescriptorCount` is zero.

## `Maintenance7.md`

No confirmed issues. Registration pass; links pass.

## `FormatPropertiesExtendedKHR.md`

No confirmed issues. Registration pass; links pass.

## `PhysicalDeviceFormatPropertiesMaint5.md`

### Registration Hierarchy prose overstated leaf count for `flags` node

- **Mistake:** Prose claimed "The two intermediate nodes (`format`, `flags`) each contain the same set of six test case leaves when both `HAS_FORMAT_PARAM` and `HAS_FLAGS_PARAM` apply". This is false for the `flags` node: only 4 of the 6 `FuncIDs` carry `HAS_FLAGS_PARAM` (DeviceImageFormatProps*, DeviceSparseImageFormatProps*), so `gFlags` receives 4 leaves, not 6. `DeviceFormatProps` and `DeviceFormatPropsSecond` carry only `HAS_FORMAT_PARAM` (`vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L47-L48`). The registration loop at `vktApiPhysicalDeviceFormatPropertiesMaint5Tests.cpp#L353-L356` adds a leaf to `gFormat` when `HAS_FORMAT_PARAM` is set and to `gFlags` only when `HAS_FLAGS_PARAM` is set. The table immediately below the prose already listed 6 leaves for `format` and 4 for `flags`, so the prose contradicted its own table.
- **Correction:** Rephrased to "The two intermediate nodes (`format`, `flags`) share the test case leaves whose `FuncIDs` carry both `HAS_FORMAT_PARAM` and `HAS_FLAGS_PARAM`; leaves with only `HAS_FORMAT_PARAM` appear only in the `format` node."

## `GetMemoryCommitment.md`

### Commitment query target mischaracterized as bound memory in Overview and Key Takeaways

- **Mistake:** The Core question framed the `memory_commitment` leaf as testing commitment "when the memory is bound to a transient image," and the Key Takeaways called it the "bound-memory path." Both imply the queried `VkDeviceMemory` is the image-bound allocation. In fact, `isDeviceMemoryCommitmentOk()` (`vktApiGetMemoryCommitment.cpp#L447-L477`) allocates a FRESH `pixelDataSize`-byte `VkDeviceMemory` per lazy memory type (L461-L466) and queries commitment on that fresh, unbound allocation (L471), checking it against the bound image's `memoryRequirements.size` (L472). The bound image's own memory (`imageAlloc`, L162-L164) is never queried. This created a wrong mental model that conflicted with the page's own Behavior Parameters section, which correctly describes the fresh allocation.
- **Correction:** Core question rephrased to "both when checked against a bound transient image's memory requirements and when checked against the size of each unbound allocation." Key Takeaways bullet rephrased to "checks commitment of a fresh lazy allocation against a bound transient image's `memoryRequirements.size`" vs. "checks commitment against each unbound allocation's own size."

## `Granularity.md`

### checkSupport pruning condition misstated as "every" instead of "any one"

- **Mistake:** Runtime section said checkSupport "throws NotSupportedError if every attachment format lacks both `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` and `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT`", implying all formats must fail. The source loops per-attachment and throws on the first format that lacks both bits (`vktApiGranularityTests.cpp#L445-L450`), so the case is skipped if ANY one attachment format is unsupported.
- **Correction:** Reworded to "iterates every attachment and throws NotSupportedError if any one attachment format lacks both" to match the per-attachment early-exit loop.

### Format sweep coverage claim cited non-covered "16-bit depth/stencil packed formats" that are actually inside the sweep

- **Mistake:** Case Pruning section stated the sweep "does not cover extension formats such as ASTC HDR, PVRTC, or the 16-bit depth/stencil packed formats, which sit above that enum value". `VK_FORMAT_D16_UNORM_S8_UINT = 128` and `VK_FORMAT_D24_UNORM_S8_UINT = 129` are both within the sweep range 1..130 (`VK_FORMAT_D32_SFLOAT_S8_UINT`), so they ARE covered. The formats actually above 130 are compressed texture formats (BC1 starts at 131), not depth/stencil packed formats.
- **Correction:** Replaced "or the 16-bit depth/stencil packed formats" with "standard compressed texture formats (BC, ETC2, EAC, ASTC LDR) starting at enum value 131" to name the correct uncovered category.

## `ImageCompressionControl.md`

### `compressionControlPlaneCount` dimension misstated for non-YCbCr formats under `explicit`

- **Mistake:** The Parameter Dimensions table listed `compressionControlPlaneCount` as "`numPlanes` for multi-planar YCbCr formats when `explicit`; `0` otherwise", implying the value is 0 for non-YCbCr formats under `explicit`. Source `vktApiImageCompressionControlTests.cpp#L453-L454` computes `numPlanes = isYCbCrFormat(format) ? getPlaneCount(format) : 1` and assigns `compressionControlPlaneCount = is_fixed_rate_ex ? numPlanes : 0`, so for non-YCbCr + `explicit` the value is `1`, not `0`. This also contradicted the page's own `### explicit` subsection which states the count is "the number of YCbCr planes (or `1` for non-YCbCr)".
- **Correction:** Updated the table cell to "`numPlanes` (YCbCr plane count, or `1` for non-YCbCr) when `explicit`; `0` otherwise", making the Parameter Dimensions table consistent with both the source and the page's `### explicit` Behavior Parameters subsection.

## `BufferMarker.md`

### `memory_dep` barrier insertion condition overstated

- **Mistake:** The page stated in three places that `VkBufferMemoryBarrier` is inserted "only when slot ownership changes" (Behavior Parameters `memory_dep` subsection, Failure Meaning > Cause Analysis > Marker/non-marker write ordering defect, Key Takeaways). This is false: the source condition at `vktApiBufferMarkerTests.cpp#L886-L908` is `(oldOwner != newOwner && oldOwner != NOBODY) || (oldOwner == NON_MARKER && newOwner == NON_MARKER)`, so barriers are also inserted when consecutive non-marker writers target the same slot. The condition is asymmetric: consecutive MARKER writes do NOT trigger a barrier, but consecutive NON_MARKER writes do.
- **Correction:** Edited the three locations to state that barriers are inserted when slot ownership changes OR when consecutive non-marker writers target the same slot, and added the explicit note that consecutive MARKER writes do not trigger a barrier in the Behavior Parameters subsection. Added a source link to the actual condition at `vktApiBufferMarkerTests.cpp#L886-L908`.

## `BufferViewCreate.md`

### Format sweep range in Overview inconsistent with source and other sections

- **Mistake:** Overview stated the family sweeps "from `VK_FORMAT_UNDEFINED + 1` through `VK_CORE_FORMAT_LAST`", but the source loop is `for (uint32_t format = vk::VK_FORMAT_UNDEFINED + 1; format < VK_CORE_FORMAT_LAST; format++)` (`vktApiBufferViewCreateTests.cpp#L415`), so the actual range tested is `VK_FORMAT_UNDEFINED + 1` through `VK_CORE_FORMAT_LAST - 1`. `VK_CORE_FORMAT_LAST` itself is a sentinel defined as `VK_FORMAT_ASTC_12x12_SRGB_BLOCK + 1` (`vkDefs.hpp#L177`), not a real Vulkan format. The same page's `## Parameter Dimensions and Observed Values` and `## Case Pruning` already state the correct "through `VK_CORE_FORMAT_LAST - 1`" range, so the Overview was a cross-section inconsistency that also implied the sentinel value itself is a tested format.
- **Correction:** Changed Overview bullet to "from `VK_FORMAT_UNDEFINED + 1` through `VK_CORE_FORMAT_LAST - 1`" so the Overview, Parameter Dimensions, and Case Pruning sections agree and match the source loop bound.

## `BufferViewAccess.md`

### Memory-test failure message misquoted as `fail("BufferView test")`

- **Mistake:** The page claimed the memory-test case returns `tcu::TestStatus::fail("BufferView test")`. The literal string "BufferView test" is actually the pass-status argument at `vktApiBufferViewAccessTests.cpp#L623`, not the fail argument. The actual fail call at L617-L620 is `tcu::TestStatus::fail(errorMessage.str())` where the constructed string is "BufferView test failed. expected: <expected> actual: <actual>". The inline code therefore conflicted with the page's own prose ("with a message of the form `BufferView test failed. expected: <expected> actual: <actual>`") and with the parallel all-formats description, which correctly quotes the literal `fail("Invalid result values")`.
- **Correction:** Replaced the inline code with `tcu::TestStatus::fail("BufferView test failed. expected: <expected> actual: <actual>")` and removed the now-redundant "with a message of the form ..." clause, so the inline code matches the actual fail argument and is consistent with the all-formats failure description.

## `BufferMemoryRequirements.md`

### VUID-None-01888 enforcement mechanism misstated as "empty combination dropped"

- **Mistake:** Page claimed that when `protected` is mixed with a sparse bit, "the sparse bits removed, and the resulting empty combination is dropped from the matrix." Source at `vktApiBufferMemoryRequirementsTests.cpp#L211-L226` only erases sparse bits (residency/aliased/binding) when `protected` is present; `protected` itself is never erased, so the result is always `{protected}`, never empty. The `bits.empty() ? flags.erase(i) : std::next(i)` check at L225 is defensive and never triggers in this context. Actual deduplication happens in the duplicate-removal step at L241-L245, which collapses the multiple `{protected}` entries into the standalone one.
- **Correction:** Edited the bullet to state that the sparse bits are removed leaving only the `protected` bit, and the subsequent duplicate-removal step collapses these into the standalone `{protected}` entry; added L241-L245 as evidence alongside L211-L226.

## `MemoryRequirementInvariance.md`

No confirmed issues. Registration pass; links pass.

## `FillBuffer.md`

### `fill_buffer_vk_whole_size_device_address` command identity

- **Mistake:** Page claimed this leaf "Uses `vkCmdFillMemoryKHR` with `size = VK_WHOLE_SIZE`" (Behavior Parameters subsection heading and body), and the Failure Cause Mapping row listed "`vkCmdFillMemoryKHR` with `VK_WHOLE_SIZE` address-range sizing" as a possible cause. The Parameter Dimensions "Device-address commands" row also described the flag as a blanket switch from `vkCmdFillBuffer`/`vkCmdUpdateBuffer` to `vkCmdFillMemoryKHR`/`vkCmdUpdateMemoryKHR`. Source line `vktApiFillBufferTests.cpp#L347` shows `FillWholeBufferTestInstance::iterate()` always calls `vk.cmdFillBuffer` with the buffer handle; there is no `vk.cmdFillMemoryKHR` call in that instance. The `useDeviceAddressCommands` flag for this leaf only changes buffer creation (usage flag + `MemoryRequirement::DeviceAddress`), forces `synchronization2`, and switches the post-write barrier to a `VkMemoryRangeBarrierKHR` keyed on the buffer's device address (lines 323-343).
- **Correction:** Behavior Parameters subsection heading and body now state the fill command stays as `vkCmdFillBuffer` and the device-address path is exercised only through the `VkMemoryRangeBarrierKHR` post-write barrier, with a citation to line 348. Failure Cause Mapping row now names "`vkCmdFillBuffer` `VK_WHOLE_SIZE` alignment on the device-address buffer path". Parameter Dimensions "Device-address commands" row now distinguishes the non-WHOLE_SIZE switch (to `vkCmdFillMemoryKHR`/`vkCmdUpdateMemoryKHR`) from the WHOLE_SIZE leaf where the fill command stays as `vkCmdFillBuffer` and only the barrier switches.

### Initial destination pattern for explicit-size leaves

- **Mistake:** Parameter Dimensions table row "Initial destination pattern" listed `data[b] = (uint8_t)(b % 255)` for explicit-size leaves and cited `vktApiFillBufferTests.cpp#L820-L822`. Source lines 820-822 fill `params.testData` (the fill word / update source data), not the destination buffer. The actual destination pre-fill for explicit-size leaves is the pixel pattern `(x, y, z, 255)` produced by `generateBuffer()` (lines 587-597) and uploaded via `uploadBuffer()` (lines 534, 692). This contradicted the page's own `### Initial pattern` section, which correctly described the pixel pattern.
- **Correction:** Table row now lists "Pixel pattern `(x, y, z, 255)` viewed as `VK_FORMAT_R8G8B8A8_UINT` for explicit-size leaves; `0xff` memset for `VK_WHOLE_SIZE` leaves" with evidence citations to `vktApiFillBufferTests.cpp#L587-L597` (generateBuffer) and `vktApiFillBufferTests.cpp#L286` (0xff memset), aligning the table with the `### Initial pattern` section.

## `NullHandle.md`

### Behavioral group count mismatch

- **Mistake:** Page stated "The 24 leaves cluster into three behavioral groups" but provided only two subsections (Single-object destroy or free with 22 leaves + Multi-handle array free with 2 leaves = 24). Source has exactly two construction patterns: the generic `test<Object>()` template (`vktApiNullHandleTests.cpp#L194-L213`, 22 leaves) and two specializations `test<VkCommandBuffer>()`/`test<VkDescriptorSet>()` for array-free entry points (`vktApiNullHandleTests.cpp#L216`, `#L274`, 2 leaves).
- **Correction:** Changed "three behavioral groups" to "two behavioral groups".

### SC-specific gate heading mislabels destroy_event gate

- **Mistake:** Cause Analysis subsection was titled "SC-specific feature gates (destroy_event, free_descriptor_sets)", but `checkEventSupport()` for `destroy_event` is active only on non-VulkanSC builds (`#ifndef CTS_USES_VULKANSC` at `vktApiNullHandleTests.cpp#L323`) and gates `VK_KHR_portability_subset` events, not an SC feature. Only `checkSupportFreeDescriptorSets()` is SC-specific (`#ifdef CTS_USES_VULKANSC` at `vktApiNullHandleTests.cpp#L265`).
- **Correction:** Renamed heading to "Support gate skips (destroy_event, free_descriptor_sets)" since the subsection covers one non-VulkanSC portability gate and one VulkanSC property gate, and the body text already explains both correctly as skip outcomes rather than failures.

## `ObjectManagement.md`

### Barrier sync frequency misstated as "every fifth iteration"

- **Mistake:** Wiki stated multithreaded workers sync "with a barrier sync every fifth iteration" (Behavior Parameters and Runtime Execution sections). The natural reading implies barriers at iterations 5, 10, 15, ... (i.e. ~20 barriers per 100-iteration loop). Source computes `itersBetweenSyncs = numIters / 5` and triggers `barrier()` when `iterNdx % itersBetweenSyncs == 0`, so for `numIters=100` barriers fire at 0, 20, 40, 60, 80, exactly 5 barriers per loop.
- **Correction:** Replaced "every fifth iteration" with "five times per loop (every `numIters/5` iterations)" in both occurrences; kept the Vulkan SC "every iteration" note in the Runtime Execution occurrence.

### `alloc_callback_fail` retry-loop termination misstated

- **Mistake:** Wiki stated `finalLimit` is "default 10000, or `--deqp-test-iteration-count` if set" and that the loop terminates "when `maxTries` is reached". Source shows `maxTries = cmdLineIterCount != 0 ? cmdLineIterCount : getOomIterLimit<Object>()` (40 default, 20 for Device/DeviceGroup) and `finalLimit = std::max(maxTries, 10000u)`, so a small `--deqp-test-iteration-count` leaves `finalLimit` at 10000, not the cmdLine value. The loop does not terminate at `maxTries`; when `numPassingAllocs >= maxTries` it sets `numPassingAllocs = finalLimit` and makes one final attempt before terminating.
- **Correction:** Rewrote the sentence to state `maxTries` is `--deqp-test-iteration-count` if set else 40 (or 20 for Device/DeviceGroup); `finalLimit` is `max(maxTries, 10000)`; the loop terminates on success or at `finalLimit`, with one final attempt at `finalLimit` after `maxTries` is reached.

## `DescriptorSet.md`

### Unsupported Vulkan SC pruning reason for `layout_binding_order` Amber case

- **Mistake:** Page stated `layout_binding_order` is excluded from Vulkan SC "for the same reason" as `push_descriptor`, implying the cause is `VK_KHR_push_descriptor` not being in Vulkan SC, and asserted the Amber case "targets a behavior that depends on extension support that is not in Vulkan SC". The source documents the reason only for `push_descriptor` (`vktApiDescriptorSetTests.cpp#L629` comment: "Removed from Vulkan SC test set: VK_KHR_push_descriptor extension removed from Vulkan SC"); the `#ifndef CTS_USES_VULKANSC` block at L645-L650 that gates `layout_binding_order` has no explanatory comment, and the Amber script is not in the working tree so its extension dependencies cannot be confirmed. The Amber case is registered with description "Test descriptor set layout binding order", which is unrelated to push descriptors.
- **Correction:** Replaced the speculative "for the same reason" rationale with a factual statement that the source does not document the specific Vulkan SC incompatibility for this Amber case and that the Amber script is not in the working tree.

## `DescriptorPool.md`

### Out-of-pool-memory exhaustion pattern count understated

- **Mistake:** The Parameter Dimensions table listed only 4 patterns (`set-count`, `binding-count`, `array-size`, `array-size-across-bindings`) and the Failure Meaning Cause Analysis parenthetical listed only 3 line ranges (L192-L199, L208-L215, L216-L231), omitting the second FailureCase row entirely. The source defines 5 FailureCase rows (`vktApiDescriptorPoolTests.cpp#L189-L232`), and the page's own Source Appendix correctly enumerates 5 patterns, so the table and Cause Analysis were internally inconsistent with both source and appendix.
- **Correction:** Updated the Parameter Dimensions table to list all 5 patterns using the Source Appendix names (`set-count`, `descriptors-by-set-count`, `descriptors-by-binding-count`, `descriptors-by-array-size`, `descriptors-by-array-size-across-bindings`). Updated the Cause Analysis parenthetical to reference all 5 line ranges: L192-L199 (set-count), L200-L207 (descriptors-by-set-count), L208-L215 (binding-count), L216-L223 (array-size), L224-L231 (array-size-across-bindings).

## `CommandBuffers.md`

### Indirect dispatch alignment memOffset binds the indirect buffer, not the storage buffer

- **Mistake:** Page stated in three places that the storage buffer is bound at `memOffset` within an allocation. Source shows `bindBufferMemory(ctx.device, *indirectBuffer, ibMemory->getMemory(), memOffset)` binds the indirect buffer at `memOffset`; the storage buffer is a separate `BufferWithMemory` that manages its own memory.
- **Correction:** Changed "storage buffer" to "indirect buffer" in the Parameter Dimensions row for "Indirect dispatch memory offset", in the prose paragraph after the table, and in the `#### Indirect dispatch alignment mismatch` Cause Analysis.

### Large buffer command count dimension does not drive `execute_large_primary`

- **Mistake:** Parameter Dimensions row "Large buffer command count" listed `execute_large_primary` alongside `record_many_*` and `record_large_secondary` with value `10000` (`1000` on Vulkan SC) and stated "Each iteration records a set/reset event pair." `execute_large_primary` uses a different constant (`LARGE_BUFFER_SIZE` = 10000 non-SC / 100 on SC, not 1000) and records only `cmdSetEvent` calls (no reset), so the SC value and the set/reset-pair description do not apply to it.
- **Correction:** Removed `execute_large_primary` from the row's "Meaning" column; the row now covers only `record_many_*` and `record_large_secondary`, which share the `minNumCommands` constant (10000 / 1000 on SC) and the set/reset-pair recording pattern. `execute_large_primary` remains covered by the design-based pruning statement "`10000` large-buffer events becomes `100`".

### Set/reset event pair count in design-based pruning

- **Mistake:** Design-based pruning stated "`10000` set/reset event pairs becomes `1000`". The `10000` value is `minNumCommands` (total commands), and the loop runs `minNumCommands / 2` iterations, each recording one set + one reset pair. The actual pair counts are 5000 (non-SC) and 500 (SC).
- **Correction:** Changed to "`5000` set/reset event pairs becomes `500`".

### Simultaneous-use expected dispatch count

- **Mistake:** Cause Analysis `#### Counter mismatch on simultaneous-use dispatches` stated the expected atomic counter value is "1, 2, or 4 depending on the leaf". Source shows all four simultaneous-use leaves expect a count of 2: `simultaneousUseSecondaryBufferOnePrimaryBufferTest` (L1920), `simultaneousUseSecondaryBufferTwoPrimaryBuffersTest` (L2708), `simultaneousUseNestedSecondaryBufferTest` (L2199), `simultaneousUseNestedSecondaryBufferTwiceTest` (L2356).
- **Correction:** Changed to "(2 for every leaf)".

## `Pipeline.md`

### `pipeline_layout.lifetime` graphics/compute leaves falsely described as submitting a command buffer

- **Mistake:** The page claimed the basic `graphics` and `compute` leaves destroy `pipelineLayoutB` "before command buffer recording" (Behavior Parameters), "submit the command buffer" and pass "if execution completes without error" (Runtime), and could fail with "a non-`VK_SUCCESS` return from `vkQueueSubmit` or `vkQueueWaitIdle`" (Failure Meaning symptoms), with the implementation-cause paragraph repeating "after pipeline creation but before command buffer recording". This is false: `pipelineLayoutLifetimeTest()` at `vktApiPipelineTests.cpp#L848-L1169` calls `vk.beginCommandBuffer` (L876), `vk.cmdBindPipeline` (L1134), `vk.destroyPipelineLayout` (L1137), then `vk.cmdBindDescriptorSets` (L1139-L1142), and returns `pass` at L1168 without ever calling `endCommandBuffer`, `queueSubmit`, `queueWaitIdle`, or `submitCommandsAndWait`. A grep for those symbols confirms they appear only in `drawTriangleTest`, `framebufferCompatibleRenderPassTest`, `destroyEarlyTest`, and `pipelineInvalidPointersUnusedStructsTest`, not in `pipelineLayoutLifetimeTest`.
- **Correction:** Behavior Parameters now states the layout is destroyed "during command buffer recording, after binding the pipeline and before binding descriptor sets with replacement layouts". Runtime now states the host "begins command buffer recording and binds the pipeline, destroys `pipelineLayoutB`, then binds descriptor sets", with "The command buffer is not submitted; the test always passes if recording completes without error". Failure Meaning symptoms now state "a validation error or crash during command buffer recording (the command buffer is recorded but not submitted in these leaves)". The implementation-cause paragraph now lists the destruction point as "during command buffer recording, after binding the pipeline and before binding descriptor sets with replacement layouts (`graphics`, `compute`)".

## `ExternalMemory.md`

### Portability subset events pruning mis-scoped to copy-transference handle types

- **Mistake:** Page stated `transference_*` cases call `checkEvent()` "on copy-transference handle types". Source shows `transference_*` registration passes `checkEvent` directly as the support function for ALL handle types (`vktApiExternalMemoryTests.cpp#L5340` semaphores, `#L4598` fences), with no transference-type guard. The same direct `checkEvent` gating also applies to `signal_export_import_wait_*` (`#L5334`, `#L4589`) and `export_import_signal_wait_*` (`#L5382`, `#L4639`). The copy-transference conditional instead belongs to the `checkSupport`-gated cases (`#L4541-L4546`), which call `checkEvent` only when `getHandelTypeTransferences(...) == TRANSFERENCE_COPY`.
- **Correction:** Replaced the bullet to list the three case families that call `checkEvent` directly (`transference_*`, `signal_export_import_wait_*`, `export_import_signal_wait_*`) as pruned on all handle types, and noted that the `checkSupport`-gated cases (`import_twice_*`, `reimport_*`, `import_multiple_times_*`, `signal_import_*`, FD-only family) inherit the same check only on copy-transference handle types.

### AHB external format resolve depth/stencil failure cause misstated

- **Mistake:** Page's `#### AHB format-property or external-format-resolve query failure` cause analysis claimed the driver "advertises an external format resolve path for a depth/stencil format, which the spec disallows." The `AhbExternalFormatResolveApiInstance::iterate()` failure path returns `fail("Depth/stencil must be supported through Vulkan Format mapping")` only when `format != VK_FORMAT_UNDEFINED` (i.e., the driver DID map the AHB format to a Vulkan format) but that mapped format lacks `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT`/`VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT`, AND the AHB format is depth or stencil (`vktApiExternalMemoryTests.cpp#L5234-L5246`). The failure is therefore the opposite of an external-format-resolve advertisement: the driver mapped the depth/stencil AHB format to a Vulkan format that lacks the attachment features the spec requires for depth/stencil support through Vulkan Format mapping.
- **Correction:** Replaced the third cause clause with "the driver maps a depth/stencil AHB format to a Vulkan format that lacks the attachment features the spec requires for depth/stencil support through Vulkan Format mapping."

## `CopyBufferToBuffer.md`

### Offset sibling range stated as 0 to `kMaxOffset` (8) instead of 0 to `kMaxOffset-1` (7)

- **Mistake:** The Registration Hierarchy stated the `buffer_to_buffer_with_offset` sibling covers "`srcOffset`/`dstOffset` combinations from 0 to `kMaxOffset = 8`", which reads as offsets 0..8 (9 values, 81 combinations). The source loop is `srcOffset < BufferOffsetParams::kMaxOffset` with `kMaxOffset = 8u` (`vktApiCopyBufferToBufferTests.cpp#L626-L627`), so offsets are 0..7 (8 values, 64 combinations). The Key Takeaways already said "from 0 to 7", creating an internal inconsistency.
- **Correction:** Changed "from 0 to `kMaxOffset = 8`" to "from 0 to `kMaxOffset - 1 = 7`" so the stated range matches the `< kMaxOffset` loop and the "0_0 through 7_7" leaf names already in the same sentence.

### 4-byte-aligned offsets 12 and 16 classified as unaligned

- **Mistake:** The Parameter Dimensions table listed "unaligned (1, 3, 6, 9, 11, 12, 16)" with the meaning "Unaligned offsets test that the driver handles non-4-byte boundaries", and Behavior Parameters described `unaligned_regions` as having "unaligned offsets (srcOffset: 3, 6, 9, 12; dstOffset: 1, 6, 11, 16)". But 12 = 4x3 and 16 = 4x4 are 4-byte aligned, so classifying them as unaligned/non-4-byte-boundary is false.
- **Correction:** Removed 12 and 16 from the unaligned value list in Parameter Dimensions, leaving "unaligned (1, 3, 6, 9, 11)". Changed "with unaligned offsets" to "with offsets including non-4-byte-aligned values" in the `unaligned_regions` Behavior Parameters description.

## `CopyImageToBuffer.md`

No confirmed issues. Registration pass; links pass.

## `CopyBufferToImage.md`

### `buffer_offset_relaxed` queue-family coverage misstated in Failure Meaning

- **Mistake:** The Cause Analysis stated "The `buffer_offset_relaxed` leaf may fail on a non-universal queue while passing on the universal queue," and the Failure Cause Mapping said "especially relaxed alignment on a non-universal queue." Both are false: `buffer_offset_relaxed` is registered only when `queueSelection == QueueSelectionOptions::Universal` (`vktApiCopyBufferToImageTests.cpp#L796`), so it cannot fail on a non-universal queue. The Background Knowledge section already states this correctly, making the Failure Meaning section internally inconsistent.
- **Correction:** Failure Cause Mapping row now reads "including relaxed alignment on the universal queue (where `buffer_offset_relaxed` is registered)." Cause Analysis now reads "The `buffer_offset` leaf may fail on a non-universal queue while passing on the universal queue; `buffer_offset_relaxed` is registered only for the universal queue, so its failure specifically indicates relaxed-alignment rejection."

## `CopyDepthStencilToBuffer.md`

### `useSparseBinding` registered values overstated

- **Mistake:** The Parameter Dimensions table listed `useSparseBinding` with "Registered values: `false`, `true`", implying sparse-binding leaves exist for this family. No dispatcher call site (`vktApiCopiesAndBlittingTests.cpp` lines 134, 150, 163) passes `useSparseBinding=true` to `addCopyDepthStencilToBufferTests`, and the registration function (`vktApiCopyDepthStencilToBufferTests.cpp` lines 671-678) never propagates `testGroupParams->useSparseBinding` into `TestParams`, which defaults to false (`vktApiCopiesAndBlittingUtil.hpp` line 320). No mustpass entries exist under `copy_and_blit.sparse` for `depthstencil_to_buffer`. The page's own text contradicted the column: "this family does not register sparse leaves directly under `core`."
- **Correction:** Changed "Registered values" from `false`, `true` to `false` only, and rewrote the "Meaning in this test" cell to state that the constructor has a sparse code path but every registered leaf runs with `useSparseBinding=false` because the flag is neither propagated by the registration function nor set true by any dispatcher.

## `CopyMemoryIndirect.md`

### `count_0` check misdescribed as a no-op destination-write verification

- **Mistake:** The page stated that for `count_0` the test "verifies the device did not write to the destination by checking that the first destination byte does not equal the first source byte" (Runtime Execution, Pass condition, Key Takeaways) and that the message `No copies but first char in source data is '\0', which should not happen` is logged "when the first destination byte equals the first source byte" (Cause Analysis), plus listed "the device wrote data when `copyCount == 0`, violating the no-op contract" as a possible implementation cause. The source code shows otherwise: `std::vector<char> copiedData(copySize, 0)` is zero-initialized, the per-copy loop at line 2051 does not execute when `copyCount == 0`, and the check at line 2081 is `if (copiedData[0] == m_copyData[0])` which evaluates to `0 == m_copyData[0]`. The check fires when the source data's first byte is `'\0'` (matching the log message at line 2085), not on any destination-buffer comparison; the destination buffer is never directly checked.
- **Correction:** Edited four locations (Runtime Execution `count_0` bullet, Pass condition line, Key Takeaways `count_0` bullet, and Cause Analysis symptom description) to describe the check accurately as a source-data sanity check, and removed the "device wrote data when `copyCount == 0`" entry from the Cause Analysis possible implementation causes list since the test does not detect that condition.

## `CopiesAndBlittingDynamicStateMetaOps.md`

### Dynamic rasterization samples failure-cause wording

- **Mistake:** Cause Analysis for "Multisampled image sample corruption" listed "the implementation applied `vkCmdSetRasterizationSamplesEXT` with a different sample count on the second draw" as a spec-level cause. The test only records `vkCmdSetRasterizationSamplesEXT` when `!drawCount` (`vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L602-L605`); it is never called on the second draw, and the implementation honors persisted dynamic state rather than "applying" the command. The wording implied the command is re-issued on the second draw.
- **Correction:** Replaced with "the implementation did not honor the dynamic rasterization samples state set on the first draw during the second draw, using a different sample count", matching the actual persistence-based design.

### Parent registration source link off by one line

- **Mistake:** Both the Registration Hierarchy prose and the Source Reference Appendix linked parent registration to `vktApiCopiesAndBlittingTests.cpp#L286`. Line 286 is `createCopyMemoryIndirectTests`; the actual `copiesAndBlittingTests->addChild(createDynamicStateMetaOperationsTests(testCtx))` call is on line 285.
- **Correction:** Updated both `#L286` references to `#L285`.

## `DSColorBitCopy.md`

### Mip-level extent wording inverted conventional mip behavior

- **Mistake:** The page said "per-mip extents are computed by left-shifting the base extent by the mip level", whose natural reading is "extent at mip level N = baseExtent << N". That inverts conventional mip behavior (extent at mip N is `baseExtent >> N`) and does not match the code at `vktApiDSColorBitCopyTests.cpp#L607-L612`, which sets the image level-0 extent to `(baseExtent << selectedMipLevel)` so that the selected mip level has extent equal to the 16x16 base extent.
- **Correction:** Replaced "per-mip extents are computed by left-shifting the base extent by the mip level" with "image level-0 extents are computed by left-shifting the base extent by the selected mip level, so the selected mip level has the base extent".

### Mismatch logging described as first-only when all mismatches are logged

- **Mistake:** The page said "The first mismatch logs `Unexpected value at (x, y): expected 0x... but found 0x...` and the case returns `fail`", implying only the first mismatch is logged and that the case returns fail at that point. The scan loop at `vktApiDSColorBitCopyTests.cpp#L850-L864` logs every mismatch (setting `ok=false` but continuing) and only returns fail at L866-L867 after the full 16x16 scan completes.
- **Correction:** Replaced "The first mismatch logs ... and the case returns `fail`." with "Each mismatch logs `Unexpected value at (x, y): expected 0x... but found 0x...`; after scanning all pixels, the case returns `fail` if any mismatch was found."

## `Smoke.md`

### Key Takeaways overstates `renderTriangleTest` sharing

- **Mistake:** The page stated "The four rendering cases share [`renderTriangleTest()`]" implying all four rendering cases (triangle, asm_triangle, asm_triangle_no_opname, unused_resolve_attachment) use that function. Source evidence shows only three do: `addFunctionCaseWithPrograms(... "triangle", createTriangleProgs, renderTriangleTest)` at L870, `... "asm_triangle", createTriangleAsmProgs, renderTriangleTest)` at L871, `... "asm_triangle_no_opname", createProgsNoOpName, renderTriangleTest)` at L872. The fourth leaf is registered at L873-L874 with `renderTriangleUnusedResolveAttachmentTest` (defined at L581-L860), a separate function with its own render pass, zero-offset bindings, and readback access. The Source Reference Appendix on the same page correctly lists the two functions separately, so the takeaway's "four ... share `renderTriangleTest()`" created an inconsistent and false mental model.
- **Correction:** Replaced "share [`renderTriangleTest()`](...) and a software-reference comparison through `rr::Renderer`" with "share a common pipeline structure and a software-reference comparison through `rr::Renderer`". This is accurate for all four cases: each builds vertex buffer + color image + render pass + pipeline + framebuffer + command buffer + draw + copyImageToBuffer + host readback, and each calls `renderReferenceTriangle()` (L307-L323) which uses `rr::Renderer`.

## `CopyImageToImage.md`

### Non-existent `array_to_array_partial` leaf listed under `array` subgroup

- **Mistake:** The `### array` subsection listed `array_to_array_partial` as a registered leaf between `array_to_array_layers` and `array_to_array_whole`. No such leaf is registered: `addImageToImageArrayTests()` in `vktApiCopyImageToImageTests.cpp` registers only `array_to_array_layers` (L3874), `array_to_array_whole` (L3926), `array_to_array_whole_remaining_layers` (L3981), `array_to_array_partial_remaining_layers` (L4035), and `array_to_array_whole_mipmap_*` (L4112). Mustpass confirms only those leaves exist under `image_to_image.array`.
- **Correction:** Removed `array_to_array_partial` from the leaf list in the `### array` subsection so the enumerated leaves match the source registration and mustpass.

## `CopyBufferToDepthStencil.md`

### Sparse-binding variants claimed but never registered for `buffer_to_depthstencil`

- **Mistake:** The page claimed `useSparseBinding` is `true` for a "dedicated-allocation `copy_commands2` sparse branch" of `buffer_to_depthstencil`, and listed sparse-binding failure symptoms/causes and sparse pruning requirements. No sparse `buffer_to_depthstencil` cases exist: `addSparseCopyTests` (`vktApiCopiesAndBlittingTests.cpp#L57-L72`) only registers `image_to_image`; mustpass has zero `copy_and_blit.sparse.buffer_to_depthstencil.*` entries. `TestParams::useSparseBinding` defaults to `false` (`vktApiCopiesAndBlittingUtil.hpp#L321`) and `addCopyBufferToDepthStencilTests` (`vktApiCopyBufferToDepthStencilTests.cpp#L835-L837`) never propagates `useSparseBinding` from `TestGroupParams` to `TestParams`. The constructor's sparse code (L226-L254) is inherited dead infrastructure for this family.
- **Correction:** Removed the `useSparseBinding` row from Parameter Dimensions; removed the "Sparse binding, when enabled..." sentence from Runtime Execution step 1; removed "(with the sparse semaphore when sparse binding is enabled)" from step 6; removed the "Sparse binding failure" bullet from shared infrastructure failure causes; removed the entire `#### Sparse binding failure` Cause Analysis subsection; removed the sparse-binding bullet from Requirement-based pruning; removed "or the sparse memory binding" from Key Takeaways; removed ", sparse image format properties" from the `checkSupport` appendix entry. Preserved the two Source Reference Appendix entries that accurately describe source code structure (class member `m_sparseAllocations` at L50; constructor sparse code at L226-L254).

## `CopyDepthStencilMSAA.md`

### Registration matrix mismatch between `core` and `copy_commands2`

- **Mistake:** The page claimed `core` and `copy_commands2` "share the same source implementation and parameter matrix; only the recorded command differs." It also described the family as registered under "two dispatcher intermediate nodes" (`core` and `copy_commands2`), omitting the `dedicated_allocation` parent. In reality, `core` uses `ALLOCATION_KIND_SUBALLOCATED` (emits `_bind_offset` leaves), while `copy_commands2` uses `ALLOCATION_KIND_DEDICATED` (no `_bind_offset` leaves). The actual matrix-match for `copy_commands2` is the `dedicated_allocation` parent (dedicated + NONE), which the page omitted entirely. The Key Takeaway about comparing `core` vs `copy_commands2` to isolate command divergence was therefore misleading because the two paths differ in allocation kind as well as the recorded command.
- **Correction:** Updated four locations to reflect the three-parent registration (`core`, `dedicated_allocation`, `copy_commands2`) with accurate allocation-kind and command mapping. The Registration Hierarchy paragraph now states that `dedicated_allocation` and `copy_commands2` share the same dedicated-allocation parameter matrix (no `_bind_offset` variants), while `core` differs in allocation kind and emits the additional `_bind_offset` leaves. The Key Takeaway now identifies `dedicated_allocation` vs `copy_commands2` as the correct pair for isolating `vkCmdCopyImage` vs `vkCmdCopyImage2` divergence.

## `Blitting.md`

### Blit leaf name encoding pattern is wrong

- **Mistake:** The page stated the leaf name encodes the tiling/layout pair as `<src_tiling><src_layout>_<dst_tiling><dst_layout>` with example `general_general_linear`. That pattern has four parts but the example has only three. The actual encoding in `getBlitImageTilingLayoutCaseName` (`vktApiBlittingTests.cpp#L2876-L2888`) returns just the layout name (`general`/`optimal` from `getImageLayoutCaseName`, `vktApiCopiesAndBlittingUtil.cpp#L477-L490`) for `VK_IMAGE_TILING_OPTIMAL` and just `linear` for `VK_IMAGE_TILING_LINEAR` (layout ignored). The filter suffix (`_nearest`/`_linear`/`_cubic`) is appended at `vktApiBlittingTests.cpp#L2950`, producing `<src>_<dst>_<filter>` (e.g. `general_general_linear` = OPTIMAL+GENERAL src, OPTIMAL+GENERAL dst, LINEAR filter).
- **Correction:** Replaced the four-part pattern with the accurate three-part form `<src>_<dst>_<filter>`, where each side is `general` or `optimal` (the layout name, for `VK_IMAGE_TILING_OPTIMAL`) or `linear` (for `VK_IMAGE_TILING_LINEAR`, ignoring the layout).

## `Resolve.md`

### Key Takeaways falsely claims the verification shader is the only shader

- **Mistake:** The Key Takeaways stated "The verification fragment shader is the only shader in this test", but `initPrograms` always adds `vert` and `frag` shaders (used by the source-image fill render pass) and conditionally adds the `verify` shader. The page's own `## Shader Analysis` section lists all three (`vktApiResolveTests.cpp#L1659-L1754`, with `vert`/`frag` at L1661-L1673 and `verify` at L1675-L1753), creating an internal contradiction and a wrong mental model that there is only one shader.
- **Correction:** Removed the "is the only shader in this test, and it" clause so the bullet now reads "The verification fragment shader is verification infrastructure rather than tested behavior. It runs with `VK_SAMPLE_COUNT_1_BIT` and iterates samples in software to avoid the `sampleRateShading` feature." The key point (verification shader is infrastructure, not tested behavior) is preserved.

## `CopyMultiplaneImageTransferQueue.md`

### LSB don't-care byte position misidentified as the high byte

- **Mistake:** The `#### LSB don't-care tolerance failures` symptoms sentence parenthetically identified the masked even `byteNdx` as "(the high byte of the 16-bit container)". For `R10X6_UNORM_PACK16` (10 data bits in MSBs, 6 unused LSBs) and `R12X4_UNORM_PACK16` (12 data bits in MSBs, 4 unused LSBs), the unused LSBs live in the LOW byte, which is the even `byteNdx` under little-endian byte ordering. The test applies `0xC0`/`0xF0` masks only when `!(byteNdx & 0x01)` (`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L736-L739`), i.e. on the low byte containing the unused LSBs; the high byte carries full data bits and is compared with `0xFF`. The page's Background Knowledge bullet states this correctly ("the lower 6 bits ... of each even byte are implementation-defined"), but the Cause Analysis parenthetical gave the reader the opposite mental model.
- **Correction:** Replaced the parenthetical with "(the low byte of each 16-bit value, which holds the unused 6 or 4 LSBs)" so the byte position matches the actual data layout and the mask semantics.

### `minImageTransferGranularity` failure direction reversed

- **Mistake:** The `#### Transfer-queue-specific failures` causes sentence said the reported `minImageTransferGranularity` is "coarser than the implementation actually requires, causing `genCopies` to generate regions that violate the implementation's real granularity." This is self-contradictory: if the reported granularity is coarser (larger alignment) than required, regions aligned to it also satisfy the finer real requirement, so no violation occurs. The failure only happens when the reported granularity is FINER (smaller) than the real requirement, so `genCopies` (`vktApiCopyMultiplaneImageTransferQueueTests.cpp#L262-L269`) produces regions that violate the coarser real granularity. The page's own `## Key Takeaways` already states the correct direction ("a driver whose real granularity is coarser than reported will fail"), confirming the Cause Analysis wording was backwards.
- **Correction:** Changed "reported coarser than the implementation actually requires" to "reported finer than the implementation's real requirement", making the Cause Analysis consistent with the Key Takeaways and the alignment logic in `genCopies`.

## `CopiesAndBlittingReinterpret.md`

### Destination image usage flags overstated

- **Mistake:** The page claimed "The host creates source and destination `VkImage` objects with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_SAMPLED_BIT | VK_IMAGE_USAGE_STORAGE_BIT`." This is false for the destination: per `vktApiCopiesAndBlittingReinterpretTests.cpp#L118-L119`, the destination `VkImage` is created with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_STORAGE_BIT` only — no `VK_IMAGE_USAGE_SAMPLED_BIT`. Only the source image (lines `#L82-L83`) carries all four flags including `SAMPLED_BIT`, because only the source is sampled via `texelFetch` through the view-format `imageView` (line `#L643-L645`). Stating that both images are created with `SAMPLED_BIT` creates a wrong mental model of what each image is used for.
- **Correction:** Rewrote the bullet to state the source is created with all four usage flags and the destination with the three-flag set (no `SAMPLED_BIT`), with a brief parenthetical explaining why: only the source is sampled through the view.

## `UseAfterCopy.md`

### Depth-write misattributed as implementation failure cause

- **Mistake:** The `### Cause Analysis` for `#### Depth/stencil attachment failure` listed "the depth test compare op was not `VK_COMPARE_OP_LESS` or the depth write was disabled" as a possible implementation cause. The "depth write was disabled" claim is wrong: `depthWriteEnable` is intentionally hardcoded to `VK_FALSE` in the test pipeline at `vktApiUseAfterCopyTests.cpp#L1456` (alongside `depthTestEnable = isDS` at L1448 and `depthCompareOp = VK_COMPARE_OP_LESS` at L1457). The application — not the implementation — disables depth writes, and the implementation respecting `depthWriteEnable = VK_FALSE` is correct behavior, not a failure cause. The brief's actual phrasing was "depth written but not made available to early/late fragment tests," which the page already covers in the preceding barrier clause; "depth write was disabled" was a garbled addition that creates a wrong mental model.
- **Correction:** Replaced "the depth write was disabled" with the actual valid implementation-bug alternative ("the depth test was not enabled despite `depthTestEnable` being set") and added a clarifying parenthetical noting that `depthWriteEnable = VK_FALSE` is intentional test design (citing L1456), so an implementation that respects it is not at fault.

## `ImageClearing.md`

### Partial-clear uses two rects forming a cross, not a single inner-75% rect

- **Mistake:** The page described the partial-clear path as a single sub-rectangular `VkClearRect` covering the inner 75% of the attachment (from `imageExtent / 8` to `imageExtent * 7 / 8`), with `clearCoords` selecting only inside-rect texels. Source evidence at `vktApiImageClearingTests.cpp#L2041-L2066` shows two `VkClearRect`s forming a cross-like region: a horizontal band `y ∈ [height/8, 5*height/8]` across the full width, plus a vertical band `x ∈ [width/8, 5*width/8]` across the full height. `clearCoords = (width/8, height/8, 5*width/8, 5*height/8)` (the inner box), and `isInClearRange` (line 222 comment: `Check if a point lies in a cross-like area.`) uses it to identify the cross region, not a single rect.
- **Correction:** Rewrote the `partial_clear_color_attachment` and `partial_clear_depth_stencil_attachment` behavior-parameter subsections, the partial-clear runtime bullet, and the `#### Partial-clear rect and scissor interaction` cause analysis to describe two rects forming a cross, the actual `clearCoords` bounds, and the four-corner-quadrant outside-rect comparison.

### `_multiple_subresourcerange` is non-overlapping multi-range dispatch, not overwrite semantics

- **Mistake:** The page claimed the `_multiple_subresourcerange` variants clear "two overlapping subresource ranges" and exercise "overlapping-range overwrite semantics" with "the second clear overwrites the first in the overlapping range". Source at `vktApiImageClearingTests.cpp#L1628-L1676` (color) and `#L1859-L1909` (depth/stencil) shows a single clear call with non-overlapping ranges: one `VkImageSubresourceRange` per mip level for the color path, and one range per aspect (depth, stencil) for the depth/stencil path. There is no second clear call and no overwrite being tested.
- **Correction:** Rewrote the `clear_color_image` behavior-parameter `_multiple_subresourcerange` sentence, the multi-range runtime bullet, the `_multiple_subresourcerange` failure-cause-mapping row, the `#### Multi-range clear overwrite semantics` cause analysis (retitled to `#### Multi-range clear dispatch`), and the key-takeaways bullet to describe single-call multi-range dispatch with per-mip (color) or per-aspect (depth/stencil) non-overlapping ranges.

### `vkCmdClearDepthStencilImage` always uses `TRANSFER_DST_OPTIMAL`, not aspect-specific layouts

- **Mistake:** The page (both the BGK bullet and the `clear_depth_stencil_image` behavior-parameter subsection) claimed the image-clear path uses `VK_IMAGE_LAYOUT_DEPTH_ATTACHMENT_OPTIMAL` / `VK_IMAGE_LAYOUT_STENCIL_ATTACHMENT_OPTIMAL` for the `_DEPTH` / `_STENCIL` modes. Source at `vktApiImageClearingTests.cpp#L1911-L1975` shows `ClearDepthStencilImageTestInstance::iterate()` always transitions to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` (lines 1935, 1944, 1956, 1967) regardless of `separateDepthStencilLayoutMode`; only the aspect mask changes. The aspect-specific layouts are used only by the attachment-clear path (`ClearAttachmentTestInstance::iterate()` lines 2006-2015).
- **Correction:** Updated the BGK bullet and the `clear_depth_stencil_image` behavior-parameter subsection to state that the image-clear path always uses `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` with aspect-mask-only separation, while the attachment-clear path transitions into the aspect-specific layouts.

### Attachment-clear layout transition is done by an explicit pipeline barrier, not by the render-pass load op

- **Mistake:** The page's runtime bullet stated "For attachment clears, the render pass's load op performs the equivalent transition." Source at `vktApiImageClearingTests.cpp#L2071-L2088` shows an explicit `pipelineImageBarrier(UNDEFINED -> attachmentLayout)` before `beginRenderPass`. The render pass's `VK_ATTACHMENT_LOAD_OP_CLEAR` load op (configured at lines 935, 937) performs the pre-clear to `initValue` (passed as `clearValue` to `beginRenderPass` at line 2088), not a layout transition.
- **Correction:** Rewrote the runtime bullet to describe the explicit pipeline barrier for attachment clears and to correctly attribute the pre-clear (not layout transition) to the render-pass load op, with an added source link to the attachment-clear barrier.

## `FragmentShaderOutput.md`

### Registration scope misstated as "unconditional"

- **Mistake:** The Overview claimed the family is "registered unconditionally," but the call to `createFragmentShaderOutputTests` at `vktApiTests.cpp#L134` sits inside `#ifndef CTS_USES_VULKANSC` (lines 128-137), so it is skipped on Vulkan SC builds. The vksc-default mustpass contains no `fragment_shader_output` entries, confirming the conditional registration.
- **Correction:** Replaced "registered unconditionally" with a precise statement that registration is for non-Vulkan SC builds only, naming the `#ifndef CTS_USES_VULKANSC` guard and the absent vksc-default mustpass entries.

### Float tolerance misattributed to `isBufferRendered` in `different_signedness`

- **Mistake:** The "Normalized value not written as expected" cause analysis said the rendered-value check uses `1.0f` "within the `0.001f` tolerance used by the float comparator." `isBufferRendered` at `vktApiFragmentShaderOutputTests.cpp#L525-L530` uses exact `pixels.getPixel(x, y).x() != 1.0f` equality for unorm/snorm render attachments. The `toleq(..., 0.001f)` tolerance at line 496 lives only in `isBufferUnchanged` for the clear-color check, not in the rendered-value check used by `different_signedness`.
- **Correction:** Replaced the parenthetical with a precise statement: the readback pixel must equal `1.0f` exactly (citing line 528), and the `0.001f` tolerance applies only to the clear-color check in `isBufferUnchanged`.

## `FrameBoundary.md`

### Off-by-one `vktApiTests.cpp` line citations

- **Mistake:** Three citations pointed one line above the actual source. The Overview cited `vktApiTests.cpp#L127-L136` for the `#ifndef CTS_USES_VULKANSC` block containing the `createFrameBoundaryTests` registration, but the block actually spans lines 128-137 (line 128 is the `#ifndef`, line 137 is `#endif`). The Registration Hierarchy prose and the Source Reference Appendix both cited `#L131` for the `addChild(createFrameBoundaryTests)` call, but that call is on line 132 (line 131 is `apiTests->addChild(createMaintenance6Tests(testCtx));`).
- **Correction:** Updated all three citations to `#L128-L137` (Overview) and `#L132` (Registration Hierarchy and Source Reference Appendix), matching the actual `#ifndef CTS_USES_VULKANSC` block and the `createFrameBoundaryTests` registration call.

### False "fixed across all leaves" image-attribute claim

- **Mistake:** The Case Pruning design-based pruning section stated "The image format (`VK_FORMAT_R8G8B8A8_UNORM`), image extent (`16x16`), and image usage flags are fixed across all leaves." This is false for the `wsi` path: `createSwapchain` uses `surfaceFormats[0].format` (line 367/379), an extent clamped to surface capabilities via `de::clamp(16u, ...)` (lines 369-371), and only `VK_IMAGE_USAGE_TRANSFER_DST_BIT` (line 383), whereas `core`/`sync2` use `VK_FORMAT_R8G8B8A8_UNORM`, a literal `16x16` extent, and `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT` (lines 215, 221, 227).
- **Correction:** Scoped the fixed-attribute claim to `core` and `sync2` with their actual usage flags, and added a brief clause noting the `wsi` path uses the swapchain's first surface format, a clamped extent, and only `VK_IMAGE_USAGE_TRANSFER_DST_BIT`, with a citation to `createSwapchain` lines 367-383.

## `DeviceAddressCommands.md`

### Overview parenthetical mislabels `vkCmdBindIndexBuffer2` as address-form

- **Mistake:** The Overview said the three binding-cluster leaves exercise "the address-form vertex/index binding commands (`vkCmdBindVertexBuffers3KHR`, `vkCmdBindIndexBuffer3KHR`, and `vkCmdBindIndexBuffer2`)". `vkCmdBindIndexBuffer2` is a `VkBuffer`-form command, not address-form: it is called as `vk.cmdBindIndexBuffer2(cmdBuffer, indexBuffer, sizeof(uint32_t), indexDataSize, VK_INDEX_TYPE_UINT32)` at `vktApiDeviceAddressCommandsTests.cpp#L681`. Only the `3KHR` variants take `VkDeviceAddress` ranges.
- **Correction:** Dropped `vkCmdBindIndexBuffer2` from the parenthetical so it lists only the two address-form commands (`vkCmdBindVertexBuffers3KHR` and `vkCmdBindIndexBuffer3KHR`).

### Sparse-buffer copy Runtime bullet conflates the two copy leaves

- **Mistake:** The "Sparse-buffer copy leaves" bullet stated "The dense side is filled with `253`; the sparse bound chunk is populated from a host-visible staging buffer via `vkCmdCopyBuffer`." Source at `vktApiDeviceAddressCommandsTests.cpp#L166-L172` fills the source side with `253` and the destination side with `0`; the `vkCmdCopyBuffer` from staging to the sparse buffer at `#L204-L211` runs only when `useSparseSrc` is true (i.e., only for `copy_from_memory_with_unbound_ranges`). For `copy_to_memory_with_unbound_ranges` the dense destination is filled with `0` (not `253`), and the sparse chunk is populated by `vkCmdCopyMemoryKHR`, not by `vkCmdCopyBuffer`.
- **Correction:** Rewrote the bullet to state that the source side is filled with `253` and the destination side initialized to `0`, and to scope the staging-buffer `vkCmdCopyBuffer` upload to `copy_from_memory_with_unbound_ranges` while noting that `copy_to_memory_with_unbound_ranges` populates the sparse destination directly via `vkCmdCopyMemoryKHR`.

### `use_all_vertex_index_binds` index-buffer offsets misstated as all non-zero

- **Mistake:** The subsection said "Index buffers use distinct non-zero offsets". The first draw binds the index buffer at offset `0` (`vktApiDeviceAddressCommandsTests.cpp#L669`); only the second (`sizeof(uint32_t)` at `#L681`) and third (`2 * sizeof(uint32_t)` at `#L692`) use non-zero offsets.
- **Correction:** Replaced "distinct non-zero offsets" with "distinct offsets (zero for the first draw, non-zero for the others)".

## `PerformanceCountersByRegion.md`

### Non-existent struct fields listed in Design-based pruning

- **Mistake:** Page claimed "the test does not validate the `data`, `name`, or `description` fields." But `VkPerformanceCounterARM` only has `sType`, `pNext`, `counterID` (no `data` field), and `VkPerformanceCounterDescriptionARM` only has `sType`, `pNext`, `flags`, `name` (no `description` field), per `external/vulkancts/framework/vulkan/generated/vulkan/vkStructTypes.inl#L5012-L5025`. The page conflated the ARM variants with the KHR variants (`VkPerformanceCounterDescriptionKHR` does have `description`, at lines 5027-5035).
- **Correction:** Replaced with the accurate statement that the only non-`sType`/`pNext` field the test does not validate is `name` on `VkPerformanceCounterDescriptionARM`.

### Overstated count requirement for undersized buffer

- **Mistake:** Page stated "For the undersized case, the implementation must report `count = 1` when asked for one slot." But the test only fails when `count > 1` (`vktApiPerformanceCountersByRegionTests.cpp#L220-L223`), so `count = 0` also passes. The claim was stricter than what the test enforces.
- **Correction:** Changed to "the implementation must report `count` no greater than `1` when asked for one slot (the test fails only when `count > 1`)".

## `DebugUtils.md`

No confirmed issues. Registration pass; links pass.

## `api.md` (Level-2)

No confirmed issues. The page accurately represents the 38 direct children registered by `createApiTests()`; the 52 rewritten Level-3 pages are correctly explained (14 from `copy_and_blit` delegated files, 2 from `buffer_view`); the 15 Vulkan SC exclusions match the `#ifndef CTS_USES_VULKANSC` guards in source; the mandatory `## Background Knowledge` section uses the canonical no-common-concepts sentence; navigation tables route each family to the correct rewritten Level-3 page; family relationships are explained at category level without duplicating Level-3 mechanisms, matrices, or shader walkthroughs; source line citations are correct. Links pass.

## Category Validation

- **Registration validator** (`verify_registration_paths.py api`): 1 failure, caused by obsolete original `vktApiMaintenance3Check.md` (navigation-style page with a malformed Registration Hierarchy tree). The rewritten `Maintenance3Check.md` passes. Obsolete originals are out of audit scope and must be preserved per harness policy.
- **Link validator** (`validate_wiki_links.py`): Level-2 `api.md` and all audited Level-3 pages pass.

