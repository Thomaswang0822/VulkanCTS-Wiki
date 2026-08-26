# Chinese Page Synchronization Tracker

## Scope

Direct tree comparison:

```bash
git diff before_repair_reference..vkcts-wiki -- \
  external/vulkancts/wiki/testfiles/<category>/<Page>.md
```

The lead agent owns the exhaustive A/B/C classification below. For class A,
delta-sync workers use the command above to inspect and apply the concrete change;
they do not reclassify pages. Class B pages are deleted and cleanly republished
with `wiki-publisher`. Class C pages require no Chinese edit.

## Counts

- Changed English Level-3 pages: **299**
- Class A — localized delta sync: **255**
- Class B — full clean republish: **35**
- Class C — no Chinese edit: **9**
- Classified: **299 / 299**
- Class A completed: **10 / 255**; remaining: **245**
- Class B completed: **0 / 35**; remaining: **35**

## Class A — Localized Delta Sync

### `api` — 19 pages

- [ ] `external/vulkancts/wiki/testfiles/api/BufferMarker.md`
- [ ] `external/vulkancts/wiki/testfiles/api/BufferViewAccess.md`
- [ ] `external/vulkancts/wiki/testfiles/api/CommandBuffers.md`
- [ ] `external/vulkancts/wiki/testfiles/api/CopiesAndBlittingDynamicStateMetaOps.md`
- [ ] `external/vulkancts/wiki/testfiles/api/CopiesAndBlittingReinterpret.md`
- [ ] `external/vulkancts/wiki/testfiles/api/CopyBufferToBuffer.md`
- [ ] `external/vulkancts/wiki/testfiles/api/CopyDepthStencilMSAA.md`
- [ ] `external/vulkancts/wiki/testfiles/api/CopyImageToImage.md`
- [ ] `external/vulkancts/wiki/testfiles/api/CopyMemoryIndirect.md`
- [ ] `external/vulkancts/wiki/testfiles/api/DSColorBitCopy.md`
- [ ] `external/vulkancts/wiki/testfiles/api/DescriptorSet.md`
- [ ] `external/vulkancts/wiki/testfiles/api/DeviceAddressCommands.md`
- [ ] `external/vulkancts/wiki/testfiles/api/DeviceInitialization.md`
- [ ] `external/vulkancts/wiki/testfiles/api/ExtensionDuplicates.md`
- [ ] `external/vulkancts/wiki/testfiles/api/FragmentShaderOutput.md`
- [ ] `external/vulkancts/wiki/testfiles/api/Maintenance3Check.md`
- [ ] `external/vulkancts/wiki/testfiles/api/Resolve.md`
- [ ] `external/vulkancts/wiki/testfiles/api/Smoke.md`
- [ ] `external/vulkancts/wiki/testfiles/api/UseAfterCopy.md`

### `binding_model` — 1 pages

- [ ] `external/vulkancts/wiki/testfiles/binding_model/DescriptorUpdate.md`

### `compute` — 7 pages

- [x] `external/vulkancts/wiki/testfiles/compute/BasicComputeShader.md`
- [x] `external/vulkancts/wiki/testfiles/compute/CooperativeMatrix.md`
- [x] `external/vulkancts/wiki/testfiles/compute/CooperativeMatrixOpConstantNull.md`
- [x] `external/vulkancts/wiki/testfiles/compute/IndirectComputeDispatch.md`
- [x] `external/vulkancts/wiki/testfiles/compute/ShaderBuiltinVar.md`
- [x] `external/vulkancts/wiki/testfiles/compute/WorkgroupMemoryExplicitLayout.md`
- [x] `external/vulkancts/wiki/testfiles/compute/ZeroInitializeWorkgroupMemory.md`

### `draw` — 22 pages

- [ ] `external/vulkancts/wiki/testfiles/draw/AhbExternalFormatResolveTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/BasicDrawTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/ConcurrentTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/DepthBiasTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/DepthClampTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/DifferingInterpolationTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/DiscardRectanglesTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/ExplicitVertexParameterTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/IndexedTest.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/IndirectInstancedTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/InstancedTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/InvertedDepthRangesTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/MultisampleLinearInterpolationTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/OutputLocationTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/PointClampTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/SampleAttributeTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/ScissorTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/ShaderDrawParametersTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/ShaderInvocationTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/ShaderLayerTests.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/SimpleTest.md`
- [ ] `external/vulkancts/wiki/testfiles/draw/VertexAttribDivisorTests.md`

### `dynamic_state` — 7 pages

- [ ] `external/vulkancts/wiki/testfiles/dynamic_state/Clear.md`
- [ ] `external/vulkancts/wiki/testfiles/dynamic_state/Compute.md`
- [ ] `external/vulkancts/wiki/testfiles/dynamic_state/Discard.md`
- [ ] `external/vulkancts/wiki/testfiles/dynamic_state/General.md`
- [ ] `external/vulkancts/wiki/testfiles/dynamic_state/Inheritance.md`
- [ ] `external/vulkancts/wiki/testfiles/dynamic_state/RS.md`
- [ ] `external/vulkancts/wiki/testfiles/dynamic_state/VP.md`

### `fragment_operations` — 4 pages

- [ ] `external/vulkancts/wiki/testfiles/fragment_operations/EarlyFragment.md`
- [ ] `external/vulkancts/wiki/testfiles/fragment_operations/OcclusionQuery.md`
- [ ] `external/vulkancts/wiki/testfiles/fragment_operations/ScissorMultiViewport.md`
- [ ] `external/vulkancts/wiki/testfiles/fragment_operations/TransientAttachment.md`

### `geometry` — 7 pages

- [ ] `external/vulkancts/wiki/testfiles/geometry/BasicGeometryShaderTests.md`
- [ ] `external/vulkancts/wiki/testfiles/geometry/BuiltinVariableGeometryShaderTests.md`
- [ ] `external/vulkancts/wiki/testfiles/geometry/EmitGeometryShaderTests.md`
- [ ] `external/vulkancts/wiki/testfiles/geometry/InputGeometryShaderTests.md`
- [ ] `external/vulkancts/wiki/testfiles/geometry/InstancedRenderingTests.md`
- [ ] `external/vulkancts/wiki/testfiles/geometry/LayeredRenderingTests.md`
- [ ] `external/vulkancts/wiki/testfiles/geometry/VaryingGeometryShaderTests.md`

### `glsl` — 4 pages

- [ ] `external/vulkancts/wiki/testfiles/glsl/AmberGlslTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/DerivateTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/LoopTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/ShaderLibrary.md`

### `image` — 10 pages

- [ ] `external/vulkancts/wiki/testfiles/image/2dArrayCompatible.md`
- [ ] `external/vulkancts/wiki/testfiles/image/DepthStencilSeparate.md`
- [ ] `external/vulkancts/wiki/testfiles/image/GeneralLayout.md`
- [ ] `external/vulkancts/wiki/testfiles/image/HostImageCopy.md`
- [ ] `external/vulkancts/wiki/testfiles/image/LoadStore.md`
- [ ] `external/vulkancts/wiki/testfiles/image/MismatchedFormats.md`
- [ ] `external/vulkancts/wiki/testfiles/image/MismatchedWriteOp.md`
- [ ] `external/vulkancts/wiki/testfiles/image/Mutable.md`
- [ ] `external/vulkancts/wiki/testfiles/image/Qualifiers.md`
- [ ] `external/vulkancts/wiki/testfiles/image/SampleDrawnCubeFace.md`

### `image_processing` — 1 pages

- [ ] `external/vulkancts/wiki/testfiles/image_processing/BlockMatching.md`

### `memory` — 2 pages

- [ ] `external/vulkancts/wiki/testfiles/memory/ExternalDmaHeap.md`
- [ ] `external/vulkancts/wiki/testfiles/memory/ExternalMemoryHost.md`

### `memory_model` — 3 pages

- [x] `external/vulkancts/wiki/testfiles/memory_model/MessagePassing.md`
- [x] `external/vulkancts/wiki/testfiles/memory_model/Padding.md`
- [x] `external/vulkancts/wiki/testfiles/memory_model/SharedLayout.md`

### `pipeline` — 40 pages

- [ ] `external/vulkancts/wiki/testfiles/pipeline/AttachmentFeedbackLoopLayout.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/BindPoint.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/BindVertexBuffers2.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/ColorWriteEnable.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/DescriptorLimits.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/DualBlend.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/DynamicControlPoints.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/DynamicOffset.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/DynamicVertexAttribute.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/ExecutableProperties.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/ExtendedDynamicStateMisc.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/FramebufferAttachment.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/Image.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/Image2DViewOf3D.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/ImageView.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/InputAttributeOffset.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/InterfaceMatching.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/LegacyAttr.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/MatchedAttachments.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/MaxVaryings.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/Misc.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/MultisampleImage.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/MultisampleInterpolation.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/MultisampleMixedAttachmentSamples.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/MultisampleResolveMaint10.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/MultisampleSampleLocationsExt.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/MultisampleShaderBuiltIn.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/MultisampleShaderFragmentMask.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/NoPosition.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/PushConstant.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/PushDescriptor.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/RenderToImage.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/RobustnessCache.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/Sampler.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/ShaderComponentDecoratedLayoutMatching.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/ShaderModuleIdentifier.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/SpecConstant.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/StencilExport.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/VertexInput.md`
- [ ] `external/vulkancts/wiki/testfiles/pipeline/VertexInputSRGB.md`

### `query_pool` — 5 pages

- [ ] `external/vulkancts/wiki/testfiles/query_pool/Concurrent.md`
- [ ] `external/vulkancts/wiki/testfiles/query_pool/FragInvocation.md`
- [ ] `external/vulkancts/wiki/testfiles/query_pool/Maintenance7.md`
- [ ] `external/vulkancts/wiki/testfiles/query_pool/Occlusion.md`
- [ ] `external/vulkancts/wiki/testfiles/query_pool/Statistics.md`

### `rasterization` — 5 pages

- [ ] `external/vulkancts/wiki/testfiles/rasterization/Core.md`
- [ ] `external/vulkancts/wiki/testfiles/rasterization/FragShaderSideEffects.md`
- [ ] `external/vulkancts/wiki/testfiles/rasterization/OrderAttachmentAccess.md`
- [ ] `external/vulkancts/wiki/testfiles/rasterization/ProvokingVertex.md`
- [ ] `external/vulkancts/wiki/testfiles/rasterization/ShaderTileImage.md`

### `ray_query` — 4 pages

- [ ] `external/vulkancts/wiki/testfiles/ray_query/BarycentricCoordinates.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_query/DirectionLength.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_query/NonUniformArgs.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_query/Stress.md`

### `ray_tracing_pipeline` — 27 pages

- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/AccelerationStructures.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/Amber.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/Barrier.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/BarycentricCoordinates.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/Build.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/BuildIndirect.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/BuildLarge.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/Builtin.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/CallableShaders.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/CaptureReplay.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/ComplexControlFlow.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/DataSpill.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/DirectionLength.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/InvocationReorderActivity.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/MemGuarantee.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/Misc.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/NonUniformArgs.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/NullAS.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/OpacityMicromap.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/PipelineFlags.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/PipelineLibrary.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/PositionFetch.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/ShaderBindingTable.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/ShaderExecutionReorder.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/TraceRays.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/TraversalControl.md`
- [ ] `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/Watertightness.md`

### `renderpasses` — 19 pages

- [ ] `external/vulkancts/wiki/testfiles/renderpasses/CustomResolve.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/DepthStencilResolve.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/DepthStencilWriteConditions.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/DynamicRenderingDepthStencilResolve.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/DynamicRenderingLocalRead.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/DynamicRenderingLocalReadMaint10.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/DynamicRenderingUnusedAttachments.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/FragmentDensityMap.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/LoadStoreOpNone.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/Multisample.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/MultisampleResolve.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/MultiviewPerView.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/NestedCommandBuffers.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/PerformanceCountersByRegion.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/RemainingArrayLayers.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/RenderPassTests.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/SampleRead.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/SubpassDependency.md`
- [ ] `external/vulkancts/wiki/testfiles/renderpasses/UnusedAttachmentSparseFilling.md`

### `sparse_resources` — 11 pages

- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/BufferTests.md`
- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/ImageMemoryAliasing.md`
- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/ImageRebind.md`
- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/ImageSparseBinding.md`
- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/ImageSparseResidency.md`
- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/MipmapSparseResidency.md`
- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/MultisampledImageSparseBinding.md`
- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/MultisampledImageSparseResidency.md`
- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/QueueBindSparseTests.md`
- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/ShaderIntrinsics.md`
- [ ] `external/vulkancts/wiki/testfiles/sparse_resources/TransferQueueTests.md`

### `spirv_assembly` — 40 pages

- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/16bitStorageTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/64bitCompareTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/8bitStorageTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/CompositeInsertTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/ComputeShaderDerivativesTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/ConditionalBranchTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/CrossStageInterfaceTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/EmptyStructTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/FloatControls2Tests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/FloatControlsExtensionlessTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/FloatControlsTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/FmaTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/FromHlslTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/ImageSamplerTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/IndexingTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/InstructionTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/IntegerDotProductTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/LdexpTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/Maint9VectorizationTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/MultipleShadersTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/NonSemanticInfoTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/PhysicalStorageBufferPointerTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/PointerParameterTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/PtrAccessChainTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/RawAccessChainTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/RelaxedWithForwardReferenceTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/SignedIntCompareTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/SignedOpTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/SpirvVersion1p4Tests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/SpirvVersionTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/TerminateInvocationTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/TrinaryMinMaxTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/TypeTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/UboMatrixPaddingTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/UntypedPointersTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/VariableInitTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/VariablePointersTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/VaryingNameTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/VectorShuffleTests.md`
- [ ] `external/vulkancts/wiki/testfiles/spirv_assembly/WorkgroupMemoryTests.md`

### `synchronization` — 4 pages

- [ ] `external/vulkancts/wiki/testfiles/synchronization/BasicSemaphore.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/ImplicitTests.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/NoneStageTests.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/OperationSingleQueue.md`

### `tessellation` — 4 pages

- [ ] `external/vulkancts/wiki/testfiles/tessellation/Coordinates.md`
- [ ] `external/vulkancts/wiki/testfiles/tessellation/GeometryPointSize.md`
- [ ] `external/vulkancts/wiki/testfiles/tessellation/GeometryScatter.md`
- [ ] `external/vulkancts/wiki/testfiles/tessellation/ShaderInputOutput.md`

### `texture` — 6 pages

- [ ] `external/vulkancts/wiki/testfiles/texture/CompressedFormat.md`
- [ ] `external/vulkancts/wiki/testfiles/texture/Conversion.md`
- [ ] `external/vulkancts/wiki/testfiles/texture/Multisample.md`
- [ ] `external/vulkancts/wiki/testfiles/texture/Shadow.md`
- [ ] `external/vulkancts/wiki/testfiles/texture/Swizzle.md`
- [ ] `external/vulkancts/wiki/testfiles/texture/TexelOffset.md`

### `ubo` — 1 pages

- [ ] `external/vulkancts/wiki/testfiles/ubo/UniformBlockTests.md`

### `wsi` — 2 pages

- [ ] `external/vulkancts/wiki/testfiles/wsi/AcquireDrmDisplayTests.md`
- [ ] `external/vulkancts/wiki/testfiles/wsi/ColorSpaceTests.md`

## Class B — Full Clean Republish

### `clipping` — 1 pages

- [ ] `external/vulkancts/wiki/testfiles/clipping/ClippingTests.md`

### `draw` — 1 pages

- [ ] `external/vulkancts/wiki/testfiles/draw/MultiExtTests.md`

### `glsl` — 19 pages

- [ ] `external/vulkancts/wiki/testfiles/glsl/AtomicOperationTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/BuiltinTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/BuiltinVarTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/DiscardTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/IndexingTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/InvarianceTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/LimitTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/MatrixTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/OpaqueTypeIndexingTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/OperatorTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/ReturnTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/ShaderBFloat16Tests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/ShaderClockTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/ShaderExpectAssumeTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/ShaderHelperInvocationsTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/StructTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/SwitchTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/TextureFunctionTests.md`
- [ ] `external/vulkancts/wiki/testfiles/glsl/TextureGatherTests.md`

### `pipeline` — 1 pages

- [ ] `external/vulkancts/wiki/testfiles/pipeline/MultisampledRenderToSingleSampled.md`

### `renderpasses` — 1 pages

- [ ] `external/vulkancts/wiki/testfiles/renderpasses/DynamicRenderingRandom.md`

### `ssbo` — 2 pages

- [ ] `external/vulkancts/wiki/testfiles/ssbo/SSBOCornerCase.md`
- [ ] `external/vulkancts/wiki/testfiles/ssbo/SSBOLayoutNestedUnsizedArraysTests.md`

### `synchronization` — 10 pages

- [ ] `external/vulkancts/wiki/testfiles/synchronization/CrossInstanceSharing.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/GlobalPriorityQueue.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/ImageLayoutTransition.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/InternallySynchronized.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/InternallySynchronizedObjects.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/OperationMultiQueue.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/SignalOrder.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/SmokeTests.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/TimelineSemaphore.md`
- [ ] `external/vulkancts/wiki/testfiles/synchronization/Win32KeyedMutex.md`

## Class C — No Chinese Edit

### `api` — 2 pages

- `external/vulkancts/wiki/testfiles/api/Blitting.md`
- `external/vulkancts/wiki/testfiles/api/CopyBufferToImage.md`

### `binding_model` — 1 pages

- `external/vulkancts/wiki/testfiles/binding_model/UnusedInvalidDescriptor.md`

### `draw` — 1 pages

- `external/vulkancts/wiki/testfiles/draw/NegativeViewportHeightTests.md`

### `fragment_operations` — 1 pages

- `external/vulkancts/wiki/testfiles/fragment_operations/Scissor.md`

### `pipeline` — 1 pages

- `external/vulkancts/wiki/testfiles/pipeline/LogicOp.md`

### `ray_tracing_pipeline` — 2 pages

- `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/LinearSweptSpheres.md`
- `external/vulkancts/wiki/testfiles/ray_tracing_pipeline/ProceduralGeometry.md`

### `wsi` — 1 pages

- `external/vulkancts/wiki/testfiles/wsi/SharedPresentableImageTests.md`

## Completion

- Update the checkboxes as class A pages are synchronized and class B pages are republished.
- Delete this temporary tracker only after every class A and B checkbox is complete and the published Chinese repository passes validation.
