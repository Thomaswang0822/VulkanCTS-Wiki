# Understanding Brief: `robustness.oob_access`

## One-Sentence Test Purpose

This test checks whether texel-buffer and storage-image accesses outside their declared bounds follow the enabled robustness contract without exposing or modifying valid resource data.

## Background Knowledge

### Resource bounds and robust access

A Vulkan resource view defines the range visible to a shader. For texel buffers, that view may cover only part of a larger allocation; for images, the extent defines valid coordinates. Robustness features constrain accesses outside those bounds.

Why it matters here:
- An out-of-view texel index can still fall inside the backing allocation, exposing an implementation that checks the wrong bounds.
- A checked robust read must return zero, while a checked robust write must not change valid resource contents.

## One Concrete Example

Consider a `robust_on` `rba2` storage-texel-buffer read. The host creates a bounded view over initialized nonzero backing data, initializes the output to `0xFF`, and pushes an index one texel beyond the view. The compute shader reads that index into the output. The host then requires every output byte to be zero ([buffer execution and verification](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L341-L540)).

## End-to-End Test Flow

```text
[host] select robustness mode, resource kind, access distance, direction, format, and size
[host] check required features and format support
[host] initialize the target resource and any read-result buffer
[host] generate the compute shader and bind descriptors plus the invalid index/coordinate
[host] dispatch one compute workgroup
[device] perform the selected out-of-bounds read or write
[host] synchronize and read back the result or modified resource when the case has a defined check
[host] compare robust reads with zero or robust writes with the original data; otherwise require successful execution
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test generates a small compute shader specialized for texel-buffer or storage-image access, read or write direction, and 32-bit or 64-bit unsigned format. A push constant carries the invalid texel index or image coordinate ([buffer program generation](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L236-L305), [image program generation](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L630-L695)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Texel-buffer backing buffer and bounded view | yes | yes | read or written | yes for checked writes | Separates view bounds from allocation bounds. |
| Storage image | yes | yes | read or written | yes for checked writes | Exercises coordinate bounds and robust image access. |
| Read-result buffer | yes | yes | written by device | yes | Carries the value returned by an out-of-bounds read. |
| Push constants | yes | yes | read by device | no | Supply the selected invalid index or coordinate. |

## What Is Checked

- `rba2` texel-buffer reads: all returned bytes are zero.
- `rba2` texel-buffer writes: backing data is unchanged.
- Robust storage-image reads: all returned bytes are zero.
- Robust storage-image writes: copied-back image data is unchanged.
- Other inspected texel-buffer paths and `robust_off` storage-image paths: execution completes successfully without an asserted returned value ([buffer checks](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L517-L540), [image checks](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L922-L948)).

## Behavior Parameter Identification

> **Behavior parameter:** direct robustness-mode component
>
> **Candidate values:** `robust_on`, `robust_off`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `robust_on` | The enabled robustness path returned nonzero data for a checked out-of-bounds read, modified valid resource contents during a checked out-of-bounds write, or failed to execute the supported case. |
| `robust_off` | The unprotected storage-image case failed to execute successfully; the test does not diagnose a particular returned value. |

## Important Variations and Special Cases

- `off_by_one` accesses the first invalid element or coordinate; `off` selects a farther invalid location.
- Texel buffers appear only under `robust_on`; uniform texel-buffer writes are omitted.
- Texel-buffer cases distinguish `rba` from `rba2`, but explicit zero/unchanged comparison is performed only for `rba2` in the inspected source.
- Storage images use `16x16`, `64x64`, and `128x128` extents. Texel-buffer backing sizes are `256`, `1024`, and `4096` bytes.
- `VK_FORMAT_R64_UINT` adds 64-bit shader and atomic capability requirements.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and generated matrix | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L965-L1058) | Defines the exact modes, resources, directions, formats, and sizes. |
| Texel-buffer support and shader | [`OOBBufferTestCase`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L162-L305) | Defines feature gates and generated buffer-access programs. |
| Texel-buffer runtime check | [`OOBBufferTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L341-L540) | Shows initialization, dispatch, and robust2 validation. |
| Storage-image support and shader | [`OOBImageTestCase`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L578-L695) | Defines image feature gates and generated programs. |
| Storage-image runtime check | [`OOBImageTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L755-L948) | Shows initialization, dispatch, copyback, and mode-dependent checks. |
| Mustpass paths | [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13755-L13874) | Confirms registered `oob_access` coverage. |

## Questions / Risk Points for User Audit

- Is the distinction between view bounds and backing-allocation bounds clear enough?
- Is it clear that `robust_off` checks successful execution rather than a particular returned value?
- Is the source-limited distinction between `rba` and explicitly checked `rba2` stated conservatively enough?

## Conversion Notes for Final Wiki Rewrite

- Keep the view-bounds concept as page-local Background Knowledge.
- Use `robust_on` and `robust_off` as the final page's behavior-parameter values.
- Copy the Failure Cause Mapping table directly into the final page.
- Keep shader discussion compact because generated shader control flow is simple; emphasize host initialization, dispatch, copyback, and checking.
