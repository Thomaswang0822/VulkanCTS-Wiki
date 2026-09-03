## Overview

The `video` test category collects tests that check Vulkan video capability reporting, profile consistency, decode and encode behavior, and synchronization of video operations.

## Background Knowledge

- A Vulkan video profile identifies a codec operation together with the picture format characteristics that qualify it, including chroma subsampling and component bit depths. The same profile description is used when querying support and when creating video resources or sessions.
- Video decode and encode commands operate in a video coding scope and use session state, bitstream data, pictures, and reference-picture resources. This shared model is why capability, profile, session, and output-result tests belong to one category.
- Video operations are submitted through queue families that expose the required video-coding capability. Synchronization tests then check dependencies around those operations rather than re-testing codec correctness.

## Category Structure

```text
video
├── capabilities
├── formats
├── profiles
├── decode
├── encode
├── synchronization
└── synchronization2
```

The video dispatcher `vktVideoTests.cpp` is registration-only: it attaches the seven direct families but implements no test cases itself. The five Level-3 pages below cover the five video-owned families — `capabilities` and `formats` share one page, and `encode` is split into an H.264/H.265 page and an AV1 page. The `synchronization` and `synchronization2` branches do not have a dedicated Level-3 page yet.

## How the Families Fit Together

The families test different layers of the same video API contract:

- **When** the question is whether a device advertises a usable combination of queue, codec, profile, usage, and image format, read the capability and profile-validation pages.
- **When** the question is whether compressed input becomes the expected pictures, read the decode page; **when** the question is whether generated pictures become an acceptable bitstream, read the encode pages.
- **Which fields** are queried, cross-checked, or pruned differs from **which bytes** are produced and compared during decode and encode execution.
- The synchronization branches are a special ownership case: their implementation code is the shared synchronization category's builders in `synchronization/vktSynchronizationTests.cpp`, but the video dispatcher registers them under `video.synchronization` and `video.synchronization2`, one child per codec operation. Their 273 mustpass cases therefore belong to the `video` category by registration path, not to the synchronization categories. The detailed dependency rules remain in the synchronization documentation boundary; dedicated Level-3 pages for these video-registered branches are planned.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `capabilities` and `formats` | [Capabilities](../testfiles/video/Capabilities.md) | Queue and codec capability queries, video-format support queries, cross-query checks, and pruning. |
| `profiles` | [ProfilesValidation](../testfiles/video/ProfilesValidation.md) | Codec profile combinations and consistency checks across capability, format, image, and session APIs. |
| `decode` → H.264, H.265, AV1, and VP9 | [Decode](../testfiles/video/Decode.md) | Clip-driven decode execution, DPB and layout variants, status handling, and decoded-frame checking. |
| `encode` → H.264 and H.265 | [Encode](../testfiles/video/Encode.md) | H.264/H.265 encode definitions, resource-layout variants, support gates, and output-quality validation. |
| `encode` → AV1 | [EncodeAV1](../testfiles/video/EncodeAV1.md) | AV1's generated encode matrix, feature-specific variants, pruning, and quality checks. |

## Category Notes

The default `video` mustpass file contains 9,301 leaves across the seven direct families. The exact registered identifiers and current coverage are maintained by the source and mustpass links in the Level-3 pages; this gateway keeps the category-level relationships and navigation concise.
