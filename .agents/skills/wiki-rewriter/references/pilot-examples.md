# Pilot Examples

Use these accepted pilot artifacts as style and structure references when uncertain. Do not copy their content into unrelated pages.

## Memory Model Pilot

- `external/vulkancts/wiki/testfiles/memory_model/vktMemoryModelMessagePassing.md`: accepted Level-3 example for a shader-heavy page with multiple test families, parameter dimensions, representative shader walkthroughs, runtime checking, pruning, takeaways, and source appendix.
- `external/vulkancts/wiki/testfiles/memory_model/MessagePassing_brief.md`: accepted Understanding Brief example for a concept-heavy shader page.
- `external/vulkancts/wiki/testfiles/memory_model/vktMemoryModelSharedLayout.md`: accepted Level-3 example for resource/layout-heavy shared memory behavior.
- `external/vulkancts/wiki/testfiles/memory_model/SharedLayout_brief.md`: accepted Understanding Brief example for generated layout/resource concepts.
- `external/vulkancts/wiki/testfiles/memory_model/vktMemoryModelPadding.md`: accepted simpler Level-3 example.

## Representative Patterns

Use an actor/step table when two shader actors perform paired behavior.

Use a compact top-down flow when the test is best understood as ordered phases.

Use resource tables when host-created resources, shader-local objects, descriptors, images, buffers, or readback targets are central to the mental model.

Use parameter tables only when dimensions affect behavior, resource layout, execution mode, validation, or pruning.

Keep source appendices last and focused on audit evidence.
