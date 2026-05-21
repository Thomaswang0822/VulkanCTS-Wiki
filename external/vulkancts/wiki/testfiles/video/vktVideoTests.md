# vktVideoTests

## Overview

`vktVideoTests.cpp` is the dispatcher for the Vulkan CTS `video` category. The package registers the public root as `video` and delegates to `video::createTests` ([vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1394-L1396)). The dispatcher creates the root from the supplied name, adds capabilities, formats, profiles, decode, encode, synchronization, and synchronization2 children, and forwards synchronization children to shared synchronization builders with explicit video codec operations ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L40-L93)).

## Role of File

| Aspect | Evidence-backed description |
|---|---|
| Registration role | Creates the category root and attaches every direct child observed under `video` ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L40-L93)). |
| Dispatcher includes | Includes the capabilities, profiles, decode, encode, and synchronization headers used by the child factories ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L24-L29)). |
| Mustpass evidence | The default mustpass file contains paths for all seven direct children ([video.txt](../../../mustpass/main/vk-default/video.txt#L1-L25)). |

## Registration Hierarchy

```text
video
├── capabilities
├── decode
├── encode
├── formats
├── profiles
├── synchronization
└── synchronization2
```

## Test Families

- `capabilities` and `formats` are both registered by `vktVideoCapabilitiesTests.cpp` via separate factory functions ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L44-L46), [vktVideoCapabilitiesTests.cpp](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2297-L2317)).
- `profiles` is registered by `vktVideoProfilesValidationTests.cpp` and separates decode and encode validation branches ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L46-L46), [vktVideoProfilesValidationTests.cpp](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1096-L1324)).
- `decode` registers H.264, H.265, AV1, and VP9 decode test groups ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L48-L48), [vktVideoDecodeTests.cpp](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1976-L2033)).
- `encode` registers H.264, H.265, and AV1 encode test groups ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L49-L49), [vktVideoEncodeTests.cpp](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3979-L4015)).
- `synchronization` and `synchronization2` are direct children created in this dispatcher with seven codec-specific child names each; implementation details come from shared synchronization code, not from a separate `video/` source file ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L51-L90)).

## Parameter Dimensions and Observed Values

| Dimension | Observed values or source |
|---|---|
| Direct category children | `capabilities`, `formats`, `profiles`, `decode`, `encode`, `synchronization`, and `synchronization2` ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L44-L90)). |
| Synchronization codec branches | `encode_h264`, `encode_h265`, `encode_av1`, `decode_h264`, `decode_h265`, `decode_av1`, and `decode_vp9` for both synchronization APIs ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L54-L88)). |

## Support and Feature Requirements

This file itself does not perform support checks; support is delegated to the registered child test cases. The synchronization branches pass codec operation flags into shared synchronization builders ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L54-L88)).

## Verification Methods

This dispatcher does not verify Vulkan behavior directly. It provides registration coverage; verification occurs in the child implementation files and shared synchronization implementation.

## Test Principles

- Keep category assembly explicit: each top-level video family is registered from a direct `addChild` call rather than discovered dynamically ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L44-L90)).
- Reuse synchronization coverage by parameterizing shared synchronization builders with video codec operations ([vktVideoTests.cpp](../../../modules/vulkan/video/vktVideoTests.cpp#L54-L88)).

## Notes / Uncertainties

- `doc/testspecs/VK/apitests.adoc` was inspected as required; text search found no video-specific section, so category-specific claims in this page are based on inspected `external/vulkancts/` source and `mustpass/main/vk-default/video.txt` evidence.
- No Level-3 page is created for shared synchronization source under this category because the requested source discovery scope was `modules/vulkan/video/`; the video-specific registration names are documented here.
