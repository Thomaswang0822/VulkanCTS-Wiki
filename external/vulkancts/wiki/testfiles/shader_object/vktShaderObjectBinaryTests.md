# [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L1)

## Overview

[`vktShaderObjectBinaryTests.cpp`](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L1) implements the `shader_object/binary` branch. It covers shader binary queries, recreating shaders from binaries, incompatible or corrupted binary data, and device-feature bit variation when using shader binaries.

## Role of File

Implementation-heavy test file for the root-level `binary` branch.

## Source Code

- Primary source: [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L55)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [vktShaderObjectCreateUtil.hpp](../../../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1)
- [CMakeLists.txt](../../../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Path

```text
shader_object
+-- binary
    +-- query/{vert,tesc,tese,geom,frag,comp}/{unlinked,linked}/...
    +-- incompatible/{vert,tesc,tese,geom,frag,comp}/...
    +-- device_features/{vert,tesc,tese,geom,frag,comp}/{unlinked,linked}/0..31
```

Explicit registration path prefixes for verifier extraction:

```text
`shader_object.binary`
`shader_object.binary.query.vert.unlinked.same_shader`
`shader_object.binary.incompatible.frag.half_size`
`shader_object.binary.device_features.comp.unlinked.0`
```

Evidence: `createShaderObjectBinaryTests()` constructs `binary`, then adds `query`, `incompatible`, and `device_features` groups at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L838-L947).

## Test Hierarchy

```text
binary
+-- query
|   +-- stage
|       +-- unlinked
|       +-- linked (not for compute)
+-- incompatible
|   +-- stage
+-- device_features
    +-- stage
        +-- unlinked
        +-- linked (not for compute)
            +-- 0..31
```

## Test Families

### Binary query cases

`QueryType` includes `SAME_SHADER`, `NEW_SHADER`, `SHADER_FROM_BINARY`, `NEW_DEVICE`, `DEVICE_NO_EXTS_FEATURES`, and `ALL_FEATURE_COMBINATIONS` at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L47-L55). The registered `queryTypeTests[]` currently uses five of those values at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L860-L862).

### Incompatible binary cases

`IncompleteBinaryTestType` defines half-size, garbage, second-half garbage, create-from-half-size, and create-from-half-size-garbage modes at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L64-L71), registered under `incompatible` at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L889-L920).

### Device-feature binary cases

The `device_features` subgroup iterates each stage, linked/unlinked state except linked compute, and indices `0..31` at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L922-L941).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Shader stage | `vert`, `tesc`, `tese`, `geom`, `frag`, `comp` at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L842-L853) |
| Linked state | `false`, `true`; linked compute skipped at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L855-L871) and [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L926-L929) |
| Query type | registered query values at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L860-L882) |
| Incompatible binary type | five registered types at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L889-L908) |
| Device-feature index | `0..31` from loop at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L933-L936) |

## Support / Feature Requirements

- Binary query, incompatible, and device-feature cases require `VK_EXT_shader_object` at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L421-L429), [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L585-L593), and [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L796-L804).
- Tessellation and geometry stages require their corresponding core features in each of those support checks.

## Verification Methods

- Query tests create shaders using stage-specific `VkShaderCreateInfoEXT`; `getNextStage()` chooses next-stage flags based on tessellation and geometry feature support at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L73-L99).
- Incompatible tests are parameterized by binary corruption/truncation modes; detailed expected result handling is in `ShaderObjectIncompatibleBinaryInstance::iterate()` beginning at [vktShaderObjectBinaryTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L458).
- Device-feature tests vary feature bits through indices `0..31` during registration; exact feature-bit mapping is implemented in the instance body outside the compact registration excerpt.

## Test Principles Observed

- Compare binary behavior across shader stage, linked state, and device-feature combinations.
- Exclude linked compute cases explicitly during registration.
- Treat malformed binary data as its own family rather than mixing it with normal query/recreation paths.

## Notes / Uncertainties

- `ALL_FEATURE_COMBINATIONS` is present in the enum but was not observed in `queryTypeTests[]`; no registered case is claimed for it.
- More detailed verification wording should be added after inspecting complete `iterate()` implementations.
