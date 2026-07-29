# Binding Model Audit Summary

## `ShaderAccess.md`

### Push descriptors bypass bind commands

- **Mistake:** The page described `bind` and `bind2` as selecting `vkCmdBindDescriptorSets` or `vkCmdBindDescriptorSets2` for every update method, although push variants bypass both commands.
- **Correction:** The page now distinguishes the registered bind-command branches from push-descriptor command recording in the overview, parameter table, runtime explanation, and failure localization. Evidence: `vktBindingShaderAccessTests.cpp#L1868-L1933`, `vktBindingShaderAccessTests.cpp#L9855-L9863`.

### Compute synchronization and comparison vary by resource

- **Mistake:** The page described every compute case as using a host-write-to-shader-read barrier and exact vector equality, although image resources use separate upload and transition paths and comparison tolerances vary by resource.
- **Correction:** The page now documents resource-specific synchronization and exact versus tolerant comparison rules. Evidence: `vktBindingShaderAccessTests.cpp#L2804-L3008`, `vktBindingShaderAccessTests.cpp#L5083-L5191`, `vktBindingShaderAccessTests.cpp#L7304-L7341`, `vktBindingShaderAccessTests.cpp#L9257-L9363`.

### Maintenance6 requirement covers every bind2 resource class

- **Mistake:** Requirement-based pruning restricted `VK_KHR_maintenance6` to `bind2` buffer cases, although buffer, image, and texel-buffer case classes all require it.
- **Correction:** The requirement now covers all `bind2` cases with evidence for each resource class. Evidence: `vktBindingShaderAccessTests.cpp#L3631-L3635`, `vktBindingShaderAccessTests.cpp#L7411-L7434`, `vktBindingShaderAccessTests.cpp#L9416-L9420`.

### Representative mustpass anchor

- **Mistake:** The appendix linked a mustpass line containing the compute case rather than the reconstructed vertex representative.
- **Correction:** The anchor now points to the exact representative path at `binding-model.txt#L65909`.

## `DescriptorSetRandom.md`

### Representative update-after-bind behavior overstated

- **Mistake:** The walkthrough claimed that internal seed `7512` generated no update-after-bind binding, although binding selection occurs during `iterate()` through a fresh 1-in-8 random draw and device-dependent per-type feature checks.
- **Correction:** The page now describes candidate selection and feature-dependent runtime behavior without asserting an unsupported fixed result. Evidence: `vktBindingDescriptorSetRandomTests.cpp#L1558-L1585`.

### Representative SPIR-V target was incorrect

- **Mistake:** The compute walkthrough used SPIR-V 1.4 even though the selected compute source inherits the collection's SPIR-V 1.0 baseline because it is inserted without the local build-options override.
- **Correction:** The complete representative shader artifact was regenerated for SPIR-V 1.0, validated, disassembled, and embedded byte-for-byte. The worker-recorded disassembly SHA-256 is `ef1ceee79d0dab0b01d46288fc7f9158a7f3c2e6c4275fd89625748e9fbf3673`. Evidence: `vktBindingDescriptorSetRandomTests.cpp#L1102-L1125`, `vkPrograms.cpp#L1048-L1052`, `vktTestPackage.cpp#L476-L483`.

### Variable descriptor counts were tied too narrowly to `runtimesize`

- **Mistake:** The explanation and failure analysis presented variable descriptor counts as part of `runtimesize`, although layout generation can select a variable-count last binding for every indexing mode.
- **Correction:** The page now separates runtime-sized shader declarations from the cross-mode variable-count allocation mechanism and documents corresponding symptoms and causes. Evidence: `vktBindingDescriptorSetRandomTests.cpp#L757-L787`, `vktBindingDescriptorSetRandomTests.cpp#L1648-L1664`.

## `DescriptorUpdate.md`

### Acceleration-structure handoff was not directly linked

- **Mistake:** The registration-only boundary named the separate acceleration-structure assignment without directly linking readers to its rewritten page.
- **Correction:** The page now links the registration-only branch to `DescriptorUpdateAS.md` in the overview, pruning text, and key takeaways. Evidence: `vktBindingDescriptorUpdateTests.cpp#L1907-L1918`, `vktBindingDescriptorUpdateASTests.cpp#L2566-L2662`.

### Samplerless support requirements were overbroad

- **Mistake:** The support description read as though every descriptor-type feature was required for every samplerless case.
- **Correction:** The page now states the shared transfer-destination and color-attachment requirements plus only the feature selected by the current descriptor type. Evidence: `vktBindingDescriptorUpdateTests.cpp#L288-L325`.

## `DescriptorCopy.md`

### `graphics_uab` inline-uniform support gate

- **Mistake:** The page generalized `graphics_uab` feature pruning to every descriptor type and omitted that the registered inline-uniform cases do not test `inlineUniformBlock` or `descriptorBindingInlineUniformBlockUpdateAfterBind` before applying `VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT`.
- **Correction:** The page now distinguishes the standard per-type update-after-bind gates from the inline-uniform branch and records the missing CTS support check as a coverage gap rather than an implementation requirement. Evidence: `vktBindingDescriptorCopyTests.cpp#L1707-L1723`, `vktBindingDescriptorCopyTests.cpp#L1909-L1941`, `descriptorsets.adoc#L697-L703`.

### Hierarchy terminology was one level too deep

- **Mistake:** The page called `compute`, `graphics`, `graphics_uab`, and `misc` separate test families even though they are intermediate nodes below the `descriptor_copy` test family.
- **Correction:** The overview, registration explanation, parameter table, behavior-axis text, failure localization, and appendix now use the canonical test-family and intermediate-node terminology. Evidence: `vktBindingModelTests.cpp#L52-L60`, `vktBindingDescriptorCopyTests.cpp#L3754-L3786`.

## `DescriptorInlineUniform.md`

### Copy failures do not isolate descriptor-copy handling

- **Mistake:** The three copy mappings named only copy handling, although `DescriptorOps::copyDescriptor` records prerequisite writes for both bindings and the shader compares every source member marked as written along with marked destination members.
- **Correction:** The cause analysis now states that a non-green copy leaf can result from the prerequisite source write even when the descriptor-copy step is correct. Evidence: `vktBindingDescriptorInlineUniformTests.cpp#L374-L385`, `vktBindingDescriptorInlineUniformTests.cpp#L743-L755`.

## `UnusedInvalidDescriptor.md`

### Write-family relationship was overstated as a comparison

- **Mistake:** The overview described `write.unused` and `write.invalid` as a comparison, although they are independently registered branches.
- **Correction:** The overview now describes the two independent checks. Evidence: `vktBindingUnusedInvalidDescriptorTests.cpp#L1283-L1329`.

### Copy resource state was described too vaguely

- **Mistake:** The `copy` behavior heading said the referenced resource became undefined, obscuring the concrete operation performed by the test.
- **Correction:** The heading now states that the copied descriptor's referenced resource is destroyed, matching the source's lifetime transition and the page's runtime explanation.

## Pages With No Confirmed Issues

- `DescriptorUpdateAS.md`
- `DynamicOffset.md`
- `DescriptorBuffer.md`
- `Mutable.md`
- `DescriptorCombination.md`
- `PushConstantBank.md`
- `BufferDeviceAddress.md`
- `DescriptorHeap.md`
- `Stages.md`
