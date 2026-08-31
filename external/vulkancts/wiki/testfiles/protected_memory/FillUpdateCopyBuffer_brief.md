# Understanding Brief: protected fill, update, and copy buffer tests

## One-Sentence Test Purpose

This test checks whether protected command buffers can fill, update, and copy protected buffer data and leave values that the protected validation path can read correctly.

## Background Knowledge

### Protected buffers and protected command execution

Protected memory restricts how commands and resources can interact. A protected command buffer submitted to a protected queue can access protected buffers, while an ordinary host readback is not the validation method used here.

Why it matters here:
- The destination and source buffers use protected memory, and the command pool is protected.
- A compute validator reads the protected destination and signals a mismatch through protected GPU work.

### Transfer commands and visibility

`vkCmdFillBuffer`, `vkCmdUpdateBuffer`, and `vkCmdCopyBuffer` are transfer operations. Fill repeats one 32-bit pattern, update embeds host-provided bytes in the recorded command, and copy transfers bytes from a source buffer. A transfer-to-shader barrier makes the destination writes available to the validator.

The source also contains `VK_KHR_device_address_commands` paths for `vkCmdFillMemoryKHR`, `vkCmdUpdateMemoryKHR`, and `vkCmdCopyMemoryKHR`. Those commands identify protected memory ranges by device address and use `VK_ADDRESS_COMMAND_PROTECTED_BIT_KHR`.

## One Concrete Example

For `protected_memory.buffer.copy.integer_buffer.primary.static.test_1`, the host selects the signed integer value `3` and four texel positions. The protected command buffer fills the protected source buffer with the 32-bit representation of `3`, makes that transfer write available to a later transfer read, and copies all 256 bytes to the protected destination. The validator then reads four `ivec4` texels from the destination. Every component at each selected position must equal `3` within the validator's comparison rule.

The transfer is the tested operation. The compute shader belongs to the checking infrastructure and does not implement the copy.

## End-to-End Test Flow

```text
[host] select operation, data type, command-buffer type, input set, and test case leaf
[host] require protected context support and create protected source and destination buffers
[host] allocate protected primary and secondary command buffers
[host] record fill, update, or source-fill-plus-copy commands in the selected command buffer
[device] execute the fixed-function transfer operation on protected memory
[device] apply the transfer-to-shader visibility dependency for the destination
[host] execute the secondary command buffer from the primary when the secondary path is selected
[host] submit the protected primary command buffer and wait for its fence
[host] configure reference data and protected validator resources
[device] run the protected compute validator against four destination texels
[host] report pass when validation completes; report failure when validation returns false
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `ResetSSBO` is a one-invocation compute program that sets the protected helper buffer's `zero` field to zero.
- `BufferValidator` is specialized for `vec4`, `ivec4`, or `uvec4` and reads the protected destination as a uniform texel buffer.
- Static cases carry six fixed values and four fixed sample positions. Random cases generate ten values and four positions per case from the command-line base seed.
- The update operation builds a 64-element `uint32_t` array in host memory and embeds it in `vkCmdUpdateBuffer` or the device-address update command.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Protected destination buffer | yes | yes | written by transfer command, read by validator | no | Holds the result under test. |
| Protected source buffer | yes | yes | written and read for `copy`; unused by the tested operation for `fill` and `update` | no | Supplies the copy source. |
| Host-visible reference uniform buffer | yes | yes | read by validator | host writes only | Supplies four positions and expected vectors. |
| Protected helper storage buffer | yes | yes | reset and written by validator | no | Converts a comparison mismatch into a validation timeout. |
| Uniform texel buffer view | yes | yes | read by validator | no | Interprets the destination as float, signed integer, or unsigned integer vectors. |

## What Is Checked

- The validator samples four positions in the 256-byte destination through a uniform texel buffer view.
- Float cases compare `vec4` values with an absolute per-component threshold of `0.1`. Signed and unsigned integer specializations use the same comparison expression with integer vector types, which requires exact equality in practice.
- On mismatch, the validator enters an error loop whose increment reads the protected helper's zero field. The validation queue submission then times out after one second and returns `false`.
- `iterate()` passes only when `validateBuffer()` returns `true`.
- The check samples four selected texels; it does not independently compare every destination word.

## Behavior Parameter Identification

> **Behavior parameter:** operation test family
>
> **Candidate values:** `fill`, `update`, `copy`

The data type, command-buffer type, static/random input set, and test case leaf broaden coverage without changing which buffer operation is under test.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fill` | The selected protected fill command, transfer-to-shader visibility, command-buffer execution form, or destination validation failed. |
| `update` | The selected protected inline update command, transfer-to-shader visibility, command-buffer execution form, or destination validation failed. |
| `copy` | Protected source initialization, the transfer-write-to-transfer-read dependency, the selected protected copy command, destination visibility, command-buffer execution form, or destination validation failed. |

## Important Variations and Special Cases

- Each operation contains `float_buffer`, `integer_buffer`, and `unsigned_buffer` intermediate nodes. They select the texel-buffer format, generated validator type, value domain, and reference data.
- `primary` records the operation directly in the protected primary command buffer. `secondary` records it and the barriers in a protected secondary command buffer, then executes that buffer from the primary.
- Every type and command-buffer combination contains six `static` and ten `random` leaves. The float, primary, static branch also registers `test_device_address` under each operation.
- The implementation contains device-address command paths and conditionally requires `VK_KHR_device_address_commands`. In the inspected source, however, the three `test_device_address` registrations do not pass `true` for `useDeviceAddressCommands`; the default remains `false`. Those registered leaves therefore select the ordinary buffer-command path in this revision. This source discrepancy must remain visible until the registration is corrected or the intended behavior is otherwise confirmed.
- Under Vulkan SC, secondary cases require `secondaryCommandBufferNullOrImagelessFramebuffer` because the secondary command buffer uses null render-pass and framebuffer inheritance. The device-address commands are excluded from the Vulkan SC build path.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test case setup and support checks | [`FillUpdateCopyBufferTestCase`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L76-L123) | Stores operation parameters, initializes validator programs, and applies support checks. |
| Protected buffers and command-buffer selection | [`FillUpdateCopyBufferTestInstance::iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L141-L199) | Creates protected resources and selects primary or secondary recording. |
| Fixed-function operation commands | [`operation switch`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L200-L296) | Records buffer-object and device-address fill, update, and copy paths. |
| Visibility, submission, and pass/fail | [`final barrier and validation`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L298-L335) | Makes the destination shader-readable and calls the validator. |
| Float matrix and device-address registrations | [`createFillUpdateCopyBufferFloatTests`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L338-L435) | Defines float static/random cases and the `test_device_address` leaves. |
| Signed integer matrix | [`createFillUpdateCopyBufferIntegerTests`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L438-L527) | Defines signed static/random cases and command-buffer branches. |
| Unsigned integer matrix | [`createFillUpdateCopyBufferUnsignedTests`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L530-L611) | Defines unsigned static/random cases and command-buffer branches. |
| Operation registration | [`createFillBufferTests`, `createUpdateBufferTests`, and `createCopyBufferTests`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L616-L648) | Registers the three operation test families and their type children. |
| Protected context requirements | [`checkProtectedContextSupport`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127) | Checks Vulkan 1.1, protected memory, and protected queue support. |
| Validator programs | [`initBufferValidatorPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemBufferValidator.cpp#L86-L194) | Generates the reset and typed validation compute programs. |
| Validator resources and result | [`BufferValidator::validateBuffer`](../../../modules/vulkan/protected_memory/vktProtectedMemBufferValidator.hpp#L181-L324) | Creates descriptors and protected helper resources, dispatches validation, and interprets timeout. |
| Buffer fill and update semantics | [`clears.adoc`](../../../../vulkan-docs/src/chapters/clears.adoc#L542-L764) | Defines the device-address and buffer-object fill and update commands. |
| Buffer and memory-range copy semantics | [`copies.adoc`](../../../../vulkan-docs/src/chapters/copies.adoc#L22-L170) | Defines device-address memory-range copy and buffer-object copy commands. |

## Questions / Risk Points for User Audit

- Is the operation test family the right primary behavioral axis, with type, command-buffer form, and input set treated as secondary dimensions?
- Is the fixed-function operation clearly separated from the compute validation infrastructure?
- Should the registered `test_device_address` leaves continue to be documented as a source discrepancy until they pass `true` for `useDeviceAddressCommands`?
- Is the four-texel validation scope stated narrowly enough to avoid implying complete word-by-word readback?

## Conversion Notes for Final Wiki Rewrite

- Distill protected execution and transfer visibility into short prerequisite bullets.
- Use three independent registration trees, one for each operation, with their direct type children.
- Carry the operation-family behavior axis and the `### Failure Cause Mapping` table into the final page unchanged.
- Keep `## Shader Analysis` concise. Fill, update, copy, and their device-address forms are fixed-function commands; the validator shaders are checking infrastructure, so no representative shader walkthrough belongs on this page.
- Explain the source discrepancy in the parameter, runtime, pruning, and risk-sensitive failure text without claiming that this revision executes the device-address path.
- Keep the command sequence, barriers, validation timeout, and four sampled positions in the runtime section. Move source navigation to the appendix.
