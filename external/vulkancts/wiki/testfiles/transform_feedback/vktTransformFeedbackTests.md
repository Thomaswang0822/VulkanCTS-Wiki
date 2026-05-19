# vktTransformFeedbackTests.cpp

## Overview

[`vktTransformFeedbackTests.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L1) is the top-level dispatcher for the [`transform_feedback`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L36-L55) category. It registers three graphics-pipeline-library variants of simple transform-feedback tests plus fuzz-layout, primitives-generated-query, and primitive-restart subgroups.

## Role

Registration / dispatcher file.

## Source Code

- Primary source: [`vktTransformFeedbackTests.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L1)

## Registration Hierarchy

```text
transform_feedback
├── fuzz
├── primitive_restart
├── primitives_generated_query
├── simple
├── simple_fast_gpl
└── simple_optimized_gpl
```

## Test Families

### simple — Simple transform feedback under multiple pipeline construction modes

[`createTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L40-L49) registers [`simple`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7264-L7276), [`simple_fast_gpl`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7267-L7274), and [`simple_optimized_gpl`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7267-L7274) through different `PipelineConstructionType` values.

### fuzz — Interface-block layout fuzz tests

[`createTransformFeedbackFuzzLayoutTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L744-L747) returns the `fuzz` group.

### primitives_generated_query — Query behavior with transform feedback

[`createPrimitivesGeneratedQueryTests()`](../../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L3062-L3065) registers the primitives-generated-query subtree.

### primitive_restart — Primitive restart with transform feedback

[`createTransformFeedbackPrimitiveRestartTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L426-L440) registers dynamic/static primitive restart and topology variants.

## Parameter Dimensions

The dispatcher varies only pipeline construction mode for the simple tests using [`constructionTypes[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L42-L46); other parameter matrices are delegated to implementation files.

## Support / Feature Requirements

No support checks are implemented in this dispatcher; support is delegated to implementation test cases such as [`TransformFeedbackTestCase::checkSupport()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L4597-L4724).

## Verification Methods

No result validation is implemented in this dispatcher; child implementations verify transform-feedback buffers, query counters, images, or primitive-restart output.

## Test Principles Observed
- The root file separates category registration from test implementation.
- The same simple-test generator is reused under multiple pipeline-construction group names.

## Notes / Uncertainties

- This page documents source-observed registration and verification behavior. The hierarchy tree lists the complete direct children registered by the root dispatcher; implementation pages summarize large generated leaf matrices in prose and parameter tables.
