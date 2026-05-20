# vktRobustnessOOBAccessTests

## Overview

This page documents the Vulkan CTS `robustness.oob_access` group implemented by [`vktRobustnessOOBAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L1-L1064). The group generates compute tests for out-of-bounds accesses to texel buffers and storage images, splitting cases into `robust_on` and `robust_off` roots. Robust-on cases check defined robustness behavior for reads and writes; robust-off cases are generated only for storage images in the inspected code.

## Role of file

[`vktRobustnessOOBAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L965-L1061) is an implementation and registration file for the `oob_access` Level-3 group. The category root adds the group directly with `createOOBAccessTests(testCtx)` ([`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L96-L97)), and the header declares the factory ([`vktRobustnessOOBAccessTests.hpp`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.hpp#L29-L35)).

## Source code link

- Source: [`vktRobustnessOOBAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L1-L1064)
- Header: [`vktRobustnessOOBAccessTests.hpp`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.hpp#L1-L39)

## Inspected related files

| File | Evidence used |
|------|---------------|
| [`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L96-L97) | Category root registration. |
| [`vktRobustnessOOBAccessTests.hpp`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.hpp#L29-L35) | Factory declaration. |
| [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13755-L13874) | Default mustpass entries for `oob_access`. |

## Registration Hierarchy

```text
robustness.oob_access
├── robust_on
└── robust_off
```

The root group is constructed as `oob_access`, and the direct children are generated from `isRobust` values as `robust_on` and `robust_off` ([`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L965-L1058)). The inspected default mustpass file lists both direct children and their generated leaves ([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13755-L13874)).

## Test Families

### `robust_on`

The `robust_on` group contains texel-buffer and storage-image cases. Texel-buffer cases are generated only for robust-on because the source explicitly skips texel-buffer tests when `isRobust` is false ([`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L982-L989)). For texel buffers, the generator combines access type, uniform/storage texel buffer type, read/write direction, `R32_UINT`/`R64_UINT` format, backing size, and robustness level `rba` or `rba2` ([`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L990-L1024)). Uniform texel buffer write cases are skipped because the source continues when `!isRead` and the texel buffer type is uniform ([`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L990-L994)).

### `robust_off`

The `robust_off` group contains storage-image cases only in the inspected source. For each access type, it combines read/write direction, `R32_UINT`/`R64_UINT` format, and image extents `16x16`, `64x64`, and `128x128` ([`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L1028-L1054)). Because `m_params.isRobust` is false for this branch, the verification code does not compare robust read-zero or write-unchanged results and instead passes after successful execution ([`OOBImageTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L922-L948)).

## Parameter dimensions and observed values

| Dimension | Observed values / ranges | Evidence |
|-----------|--------------------------|----------|
| Direct groups | `robust_on`, `robust_off` | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L973-L978) |
| Access types | `off_by_one`, `off` | [`OOBAccessType`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L54-L58), [`oobAccessName`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L969-L971) |
| Texel buffer types | `texel_buffer_uniform`, `texel_buffer_storage` | [`TexelBufferType`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L60-L64), [`texelBufferName`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L969-L970) |
| Robustness levels for texel-buffer cases | `rba`, `rba2` | [`RobustnessLevel`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L66-L71), robust-level loop in [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L999-L1002) |
| Formats | `VK_FORMAT_R32_UINT`, `VK_FORMAT_R64_UINT` | Format loops in [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L995-L996) and [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L1030-L1033) |
| Texel-buffer backing sizes | `256`, `1024`, `4096` bytes | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L997-L998) |
| Storage-image extents | `16x16`, `64x64`, `128x128` | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L1034-L1050) |
| Read/write directions | `read`, `write`; uniform texel buffers skip write cases | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L990-L994), [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L1030-L1051) |
| OOB index calculation | Texel buffer: one past view size or halfway farther into backing memory; image: extent or extent plus `64,64` | [`OOBBufferTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L341-L349), [`OOBImageTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L755-L761) |

## Support / feature requirements

- Robust texel-buffer cases require portability-subset `robustBufferAccess` when applicable; `rba2` cases require `VK_EXT_robustness2` and `robustBufferAccess2` ([`OOBBufferTestCase::checkSupport()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L162-L188)).
- Texel-buffer cases check format support for uniform or storage texel buffer features and reject cases exceeding `maxTexelBufferElements` ([`OOBBufferTestCase::checkSupport()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L190-L204)).
- Robust image cases require `VK_EXT_image_robustness`; device capabilities add `robustImageAccess` when robust image cases are used ([`OOBImageTestCase::checkSupport()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L578-L586), [`OOBImageTestCase::initDeviceCapabilities()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L614-L620)).
- Storage-image cases check `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` and `getPhysicalDeviceImageFormatProperties` for the selected format and usage ([`OOBImageTestCase::checkSupport()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L588-L605)).
- `R64` formats require `VK_EXT_shader_image_atomic_int64`, `shaderInt64`, `shaderBufferInt64Atomics`, and `shaderImageInt64Atomics` through common support checks and capability setup ([`commonCheckSupport()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L145-L160), [`OOBBufferTestCase::initDeviceCapabilities()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L228-L233), [`OOBImageTestCase::initDeviceCapabilities()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L622-L627)).

## Verification methods

- Texel-buffer tests initialize backing data with a nonzero byte pattern and initialize the read/write I/O buffer to `0xFF`, then dispatch a one-workgroup compute shader accessing the selected OOB texel ([`OOBBufferTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L341-L407), [`OOBBufferTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L437-L489)).
- For `rba2` texel-buffer reads, the test compares the output value against all zero bytes; for `rba2` writes, it compares the whole backing buffer against its original reference data ([`OOBBufferTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L517-L538)). Cases not using `rba2` pass after successful execution in the inspected code ([`OOBBufferTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L517-L540)).
- Storage-image tests initialize the image through a buffer copy, dispatch a one-workgroup compute shader with an OOB coordinate, and for writes copy the image back to a buffer before host comparison ([`OOBImageTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L784-L899), [`OOBImageTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L901-L924)).
- For robust image reads, the output value must be all zero bytes; for robust image writes, the copied-back image data must match the original reference data ([`OOBImageTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L926-L948)).

## Test principles

- Generate a compact matrix around read/write direction, resource type, format width, robustness feature level, and OOB distance rather than hard-coding each case ([`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L969-L1058)).
- Use compute shaders with push constants carrying the OOB index so each case changes only parameters and generated shader/resource setup ([`OOBBufferTestCase::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L236-L305), [`OOBImageTestCase::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L630-L695)).
- Distinguish defined robust outcomes from mere successful execution: robust2 texel buffers and robust images compare read-zero/write-unchanged results, while non-robust storage-image cases do not assert returned data ([`OOBBufferTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L517-L540), [`OOBImageTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L926-L948)).

## Notes / uncertainties

- The parseable hierarchy expands only one level below `oob_access`; the large generated leaf matrix is described in Test Families and parameter tables instead of the tree.
- The inspected default mustpass file lists `robust_off` entries before `robust_on`, while the source generation loop adds `robust_on` before `robust_off`; the tree follows source order ([`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L973-L1058), [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13755-L13874)).
- No additional helper implementation file was inspected for image/buffer copy utilities; claims about copy behavior are limited to calls visible in the assigned source.
