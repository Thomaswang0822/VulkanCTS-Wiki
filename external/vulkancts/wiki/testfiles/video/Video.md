## Overview

**Core question:** How does `video` route its direct test families, including codec-specific synchronization coverage?

- `vktVideoTests.cpp` builds the `video` test category and attaches seven direct child groups: `capabilities`, `formats`, `profiles`, `decode`, `encode`, `synchronization`, and `synchronization2` ([`createTests`](../../../modules/vulkan/video/vktVideoTests.cpp#L40-L93)).
- The Vulkan CTS package registers the root name `video` with `video::createTests` ([`TestPackage::init`](../../../modules/vulkan/vktTestPackage.cpp#L1394-L1396)).
- The first five branches route to video-specific builders. The last two are adapters: they call the shared synchronization builders with one codec operation per child.
- The default mustpass file contains all seven branch prefixes. Its synchronization coverage contains 161 legacy paths and 112 `synchronization2` paths, with the same seven codec-operation names under each branch ([`video.txt`](../../../mustpass/main/vk-default/video.txt#L1-L25), [`video.txt`](../../../mustpass/main/vk-default/video.txt#L9029-L9301)).
- This page documents routing and page boundaries. It does not repeat the synchronization primitives, dependency rules, or operation mechanics documented by the shared synchronization pages.

## Background Knowledge

- **Video coding scope:** Vulkan video commands execute inside a video coding scope and require a queue family with compatible video coding capabilities ([Video Coding](../../../../vulkan-docs/src/chapters/videocoding.adoc#L8-L22)). This explains why the dispatcher keeps video capability and codec operation selection at the video category boundary.
- **Video profile:** A profile combines a codec operation with format-related fields such as chroma subsampling and luma and chroma bit depth. Vulkan uses it for capability queries and video resource and session creation ([`VkVideoProfileInfoKHR`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L320-L352)).
- **Synchronization delegation:** The legacy and `VK_KHR_synchronization2` APIs share synchronization concepts but use different source-side builders. The video adapter supplies the selected codec operation so shared synchronization cases can run in a video context. See the shared [`synchronization` category](../../categories/synchronization.md) for the dependency model and primitive-specific behavior.

## Registration Hierarchy

```text
video
├── capabilities
├── formats
├── profiles
├── decode
├── encode
├── synchronization (registration only)
└── synchronization2 (registration only)
```

The first five direct branches are implemented by their corresponding video source files. The two synchronization branches are registration-only entries on this page: they route to test construction in `synchronization/vktSynchronizationTests.cpp`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Direct video branch | `capabilities`, `formats`, `profiles`, `decode`, `encode` | Selects a video-owned builder with a distinct query, validation, decode, or encode scope. | [`vktVideoTests.cpp`](../../../modules/vulkan/video/vktVideoTests.cpp#L44-L49) |
| Synchronization API family | `synchronization`, `synchronization2` | Selects the legacy or `VK_KHR_synchronization2` shared synchronization builder. | [`vktVideoTests.cpp`](../../../modules/vulkan/video/vktVideoTests.cpp#L51-L90), [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L175-L194) |
| Codec operation in synchronization | `encode_h264`, `encode_h265`, `encode_av1`, `decode_h264`, `decode_h265`, `decode_av1`, `decode_vp9` | Supplies the video codec operation used by the delegated synchronization cases. | [`vktVideoTests.cpp`](../../../modules/vulkan/video/vktVideoTests.cpp#L54-L67) |

## Behavior Parameters

The primary behavioral axis for this page is the direct branch. Each value determines which builder receives the test context. The synchronization values are the page's delegated branch axis and add a second, codec-specialized selection.

### `capabilities` and `formats`: capability and format queries

The dispatcher calls `createVideoCapabilitiesTests`, which registers both the capability-query and format-query families. The same source file supplies both builders, and the page owns both direct branches ([`vktVideoCapabilitiesTests.cpp`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2297-L2323)).

### `profiles`: profile validation

The dispatcher calls `createVideoProfilesValidationTests`. Its codec list contains decode H.264, H.265, AV1, and VP9 plus encode H.264, H.265, and AV1, matching the codec-operation set used by the synchronization adapters ([`vktVideoProfilesValidationTests.cpp`](../../../modules/vulkan/video/vktVideoProfilesValidationTests.cpp#L1096-L1104)).

### `decode`: decode sessions

The dispatcher calls `createVideoDecodeTests`. The builder creates `h264`, `h265`, `av1`, and `vp9` intermediate nodes and distributes generated decode cases by codec ([`vktVideoDecodeTests.cpp`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1976-L2000)).

### `encode`: encode sessions

The dispatcher calls `createVideoEncodeTests`. The builder creates H.264 and H.265 codec branches and attaches the AV1 branch through `createVideoEncodeTestsAV1` ([`vktVideoEncodeTests.cpp`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3979-L4015)).

### `synchronization`: legacy synchronization with video operations

The dispatcher creates seven children below `video.synchronization`. Each child calls `createSynchronizationTests` with `SynchronizationType::LEGACY` selected inside the shared implementation and with one `VideoCodecOperationFlags` value. The names are exact: `encode_h264`, `encode_h265`, `encode_av1`, `decode_h264`, `decode_h265`, `decode_av1`, and `decode_vp9` ([`vktVideoTests.cpp`](../../../modules/vulkan/video/vktVideoTests.cpp#L51-L69)).

The shared builder uses the codec flag to construct the basic synchronization families, while it omits the non-video-only top-level families guarded by `videoCodecOperation == 0` ([`createBasicTests`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L53-L71), [`createTestsInternal`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L159)).

### `synchronization2`: synchronization2 with video operations

The dispatcher creates the same seven codec-named children below `video.synchronization2`, this time through `createSynchronization2Tests` ([`vktVideoTests.cpp`](../../../modules/vulkan/video/vktVideoTests.cpp#L72-L90)). The shared implementation selects `SynchronizationType::SYNCHRONIZATION2` before passing the codec operation into the common construction path ([`createSynchronization2Tests`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L186-L194)).

The adapter changes the synchronization API family and codec context. It does not define a second video synchronization algorithm on this page. Read the shared synchronization documentation for the primitive behavior and result checks.

## Shader Analysis

The dispatcher contains no shader source or shader-building logic. Its responsibility ends at attaching child test groups, so no representative shader walkthrough applies to this page.

## Runtime Execution and Result Checking

- The Vulkan CTS package creates the `video` root and passes the test context and root name to `video::createTests` ([`TestPackage::init`](../../../modules/vulkan/vktTestPackage.cpp#L1394-L1396)).
- `createTests` allocates a root group using the supplied name, adds the five video-owned builders, then creates the `synchronization` and `synchronization2` adapter groups ([`vktVideoTests.cpp`](../../../modules/vulkan/video/vktVideoTests.cpp#L40-L93)).
- The dispatcher performs no command recording, queue submission, codec bitstream processing, or result scan. Those actions belong to the selected child builder. For synchronization children, the shared synchronization implementation receives the codec operation and constructs the cases ([`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L159)).
- The default mustpass file exercises the registered leaves under `video.*`. The synchronization sections use `basic` cases and preserve the codec name in the path, such as `video.synchronization.decode_h264.basic...` and `video.synchronization2.encode_av1.basic...` ([`video.txt`](../../../mustpass/main/vk-default/video.txt#L9029-L9301)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `capabilities` | The capability-query registration or its video capability checks did not produce the expected case result. |
| `formats` | The format-query branch or its format support checks did not produce the expected case result. |
| `profiles` | The profile-validation branch or one of its codec/profile combinations did not produce the expected case result. |
| `decode` | The decode-session branch or a codec-specific decode case did not produce the expected case result. |
| `encode` | The encode-session branch or a codec-specific encode case did not produce the expected case result. |
| `synchronization` | The legacy synchronization adapter did not route the selected codec operation to the shared builder, or a delegated legacy synchronization case failed. |
| `synchronization2` | The synchronization2 adapter did not route the selected codec operation to the shared builder, or a delegated synchronization2 case failed. |

The mapping describes the dispatcher boundary. It does not assign a failure to a GPU, driver, compiler, or host without evidence from the selected child test's validation logic.

### Cause Analysis

#### Video root or direct-child registration

**Possible failure symptoms:** A requested `dEQP-VK.video.<branch>` path is missing, the test package cannot construct the `video` root, or a mustpass path resolves to the wrong direct child.

**Possible implementation causes:** The package registration may not bind `video` to `video::createTests`, or `createTests` may omit or rename one of its seven child groups. The source directly shows both registration sites and the child attachment order, so a failing path should be checked against [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1394-L1396) and [`vktVideoTests.cpp`](../../../modules/vulkan/video/vktVideoTests.cpp#L40-L93).

#### Codec-specialized synchronization delegation

**Possible failure symptoms:** A path such as `video.synchronization.decode_h264.basic...` or its `synchronization2` counterpart is absent, reaches a different codec operation, or fails inside a delegated basic synchronization case.

**Possible implementation causes:** The video dispatcher may pass the wrong codec flag or choose the wrong shared factory. The shared synchronization builder may then construct the wrong codec-specialized case set. The source distinguishes the legacy and synchronization2 factories and passes the codec flag into both ([`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L165-L194)). Further diagnosis belongs to the shared synchronization page and the delegated case implementation.

## Case Pruning

### Requirement-based pruning

The dispatcher applies no per-case feature, format, queue, or codec pruning. The selected child builder and, for synchronization branches, the shared synchronization implementation decide whether a case is supported. The source keeps the video codec operation in the delegated builder rather than filtering it at this root ([`vktVideoTests.cpp`](../../../modules/vulkan/video/vktVideoTests.cpp#L51-L90), [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L159)).

### Design-based pruning

The dispatcher deliberately exposes legacy synchronization and synchronization2 as separate direct branches while keeping codec selection as children of each branch. This preserves the registered distinction between API families and lets the shared implementation reuse its basic synchronization construction for each video codec operation.

## Key Takeaways

- `video` has seven direct branches. The first five are video-owned builders; `synchronization` and `synchronization2` are adapters into shared synchronization code.
- Both synchronization adapters register the same seven codec operation names: three encode operations and four decode operations.
- The legacy adapter calls `createSynchronizationTests`; the synchronization2 adapter calls `createSynchronization2Tests`. The codec flag is passed through to the shared implementation in both cases.
- The default mustpass paths retain both the API-family branch and the codec operation, which makes routing mistakes visible from the registered path alone.
- This page stops at the dispatcher boundary. Shared synchronization semantics and detailed case behavior belong to the synchronization documentation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Vulkan package root registration | [`TestPackage::init`](../../../modules/vulkan/vktTestPackage.cpp#L1394-L1396) | Binds the public `video` root to `video::createTests`. |
| Video root dispatcher | [`createTests`](../../../modules/vulkan/video/vktVideoTests.cpp#L40-L93) | Attaches all seven direct branches and passes codec operations to synchronization factories. |
| Shared synchronization construction | [`createTestsInternal`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L159) | Shows which shared families are built with a video codec operation. |
| Legacy and synchronization2 entry points | [`createSynchronizationTests` and `createSynchronization2Tests`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L165-L194) | Selects the synchronization type while preserving the codec argument. |
| Video-owned capability and format builders | [`createVideoCapabilitiesTests` and `createVideoFormatsTests`](../../../modules/vulkan/video/vktVideoCapabilitiesTests.cpp#L2297-L2323) | Confirms the `capabilities` and `formats` child builders. |
| Video-owned decode builder | [`createVideoDecodeTests`](../../../modules/vulkan/video/vktVideoDecodeTests.cpp#L1976-L2000) | Confirms codec intermediate nodes under `decode`. |
| Video-owned encode builder | [`createVideoEncodeTests`](../../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3979-L4000) | Confirms the encode branch and H.264/H.265 codec routing. |
| Default video mustpass | [`video.txt`](../../../mustpass/main/vk-default/video.txt#L9029-L9301) | Confirms the codec-specialized `synchronization` and `synchronization2` path sets. |
| Video coding scope | [`Video Coding`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L8-L22) | Supplies the external concept needed to understand video queue routing. |
| Video profiles | [`VkVideoProfileInfoKHR`](../../../../vulkan-docs/src/chapters/videocoding.adoc#L320-L352) | Defines the profile and codec-operation context used by video tests. |
