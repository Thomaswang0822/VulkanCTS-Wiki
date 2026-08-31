## Overview

**Core question:** Do protected buffer fill, update, and copy commands produce the expected destination data in both command-buffer forms?

- This page covers `vktProtectedMemFillUpdateCopyBufferTests.cpp`, which implements the `protected_memory.buffer.fill`, `protected_memory.buffer.update`, and `protected_memory.buffer.copy` test families.
- Each operation runs on protected buffers through either a primary command buffer or a secondary command buffer executed by the primary.
- Float, signed integer, and unsigned integer branches combine six fixed values with ten base-seed-dependent random values. A protected compute validator checks four destination texels after the transfer work.
- The implementation also contains `VK_KHR_device_address_commands` paths for fill, update, and copy. The registered `test_device_address` leaves do not enable those paths in the inspected source, so this page records that discrepancy instead of claiming coverage the current constructor calls do not select.
- The copy setup creates its source buffer without `VK_BUFFER_USAGE_TRANSFER_SRC_BIT`, which both `vkCmdCopyBuffer` and the implemented device-address copy path require. This is an unresolved CTS source defect rather than valid copy-command coverage.

## Background Knowledge

- A protected command buffer must access resources with a compatible protection state. These tests allocate protected buffers, use a protected command pool, and submit work to a protected queue.
- Buffer fill, update, and copy commands perform transfer work. A buffer memory barrier must make their writes available to the compute validator. The copy path also needs a dependency between the source fill and the source read by the copy.
- `VK_KHR_device_address_commands` provides memory-range commands that address memory through device addresses. Protected ranges use `VK_ADDRESS_COMMAND_PROTECTED_BIT_KHR`.

## Registration Hierarchy

```text
protected_memory.buffer.fill
├── float_buffer
├── integer_buffer
└── unsigned_buffer

protected_memory.buffer.update
├── float_buffer
├── integer_buffer
└── unsigned_buffer

protected_memory.buffer.copy
├── float_buffer
├── integer_buffer
└── unsigned_buffer
```

Each type intermediate node contains `primary` and `secondary`, followed by `static` and `random`. The static branches contain `test_1` through `test_6`; the random branches contain `test_1` through `test_10`. Each operation also registers `test_device_address` under `float_buffer.primary.static`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Operation test family | `fill`, `update`, `copy` | Selects the protected fixed-function buffer operation and is the primary behavioral axis. | [`operation registration`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L616-L648) |
| Destination interpretation | `float_buffer`, `integer_buffer`, `unsigned_buffer` | Selects the uniform texel-buffer format, generated validator vector type, and value domain. | [`type registration`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L430-L435), [`signed type registration`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L522-L527), and [`unsigned type registration`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L606-L611) |
| Command-buffer type | `primary`, `secondary` | Selects direct primary recording or secondary recording followed by `vkCmdExecuteCommands`. | [`command-buffer setup`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L174-L199) and [`secondary execution`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L316-L320) |
| Input set | `static`, `random` | Selects six fixed values and positions or ten cases generated from the command-line base seed. | [`float matrix`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L338-L425), [`signed matrix`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L438-L517), and [`unsigned matrix`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L530-L601) |
| Static test case leaf | `test_1` through `test_6` | Selects one fixed fill or update bit pattern and four sample positions. | [`static float cases`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L341-L381) |
| Random test case leaf | `test_1` through `test_10` | Selects one generated value and four generated positions. | [`random float cases`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L392-L419) |
| Device-address leaf | `test_device_address` under each `float_buffer.primary.static` branch | Intended to select the `VK_KHR_device_address_commands` form. The current registration omits the constructor argument that would set `useDeviceAddressCommands` to `true`, so these leaves take the ordinary buffer-command path in the inspected revision. | [`device-address registration`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L384-L390) and [`constructor default`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L80-L89) |
| Buffer size | 256 bytes | Holds 64 32-bit words, or 16 four-component texels, and fixes the full range used by each operation. | [`buffer size calculation`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L46-L49) and [`iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L141-L164) |

The Vulkan mustpass list contains 291 leaves for these families: 97 each for `fill`, `update`, and `copy`. The float branches contribute one extra primary static leaf per operation for `test_device_address`.

## Behavior Parameters

The primary behavioral axis is the operation test family. Type, command-buffer form, and input set vary representation and execution coverage around that operation.

### fill: repeat one 32-bit pattern

The ordinary path calls `vkCmdFillBuffer` on the complete protected destination. The command repeats the selected 32-bit bit pattern throughout the buffer. The device-address implementation path uses `vkCmdFillMemoryKHR` with the destination address range and `VK_ADDRESS_COMMAND_PROTECTED_BIT_KHR`, although the inspected registrations do not enable that path.

### update: embed source bytes in the command

The host builds 64 copies of the selected 32-bit value and records `vkCmdUpdateBuffer` to update the complete protected destination. The device-address implementation path records `vkCmdUpdateMemoryKHR` for the same byte count and protected address flag, but the current `test_device_address` constructor calls leave that path disabled.

### copy: initialize a source and copy it to the destination

The test first fills the protected source with the selected value. It inserts a transfer-write-to-transfer-read buffer barrier, then copies all 256 bytes to the protected destination with `vkCmdCopyBuffer`. However, the source buffer lacks the required `VK_BUFFER_USAGE_TRANSFER_SRC_BIT`, so the recorded copy is not a valid use of that command. The device-address implementation path pairs `vkCmdFillMemoryKHR` with `vkCmdCopyMemoryKHR` over protected source and destination address ranges and has the same missing transfer-source usage; the current registrations also do not select it.

## Shader Analysis

The tested fill, update, copy, and device-address memory commands are fixed-function transfer operations, so there is no test-core shader to walk through. `ResetSSBO` and `BufferValidator` are compute programs used after the transfer to check protected destination data. They do not implement any tested buffer operation.

## Runtime Execution and Result Checking

- `checkSupport()` calls `checkProtectedContextSupport()`, which requires Vulkan 1.1, the protected-memory feature, and a protected queue. A case with `useDeviceAddressCommands == true` would also require `VK_KHR_device_address_commands`.
- Under Vulkan SC, a secondary case requires `secondaryCommandBufferNullOrImagelessFramebuffer` because the secondary command buffer uses a `VkCommandBufferInheritanceInfo` with null render-pass and framebuffer handles.
- The test creates 256-byte protected source and destination buffers. Both receive uniform-texel-buffer and transfer-destination usage; a selected device-address path would also add shader-device-address usage and a device-address memory requirement. The copy source never receives `VK_BUFFER_USAGE_TRANSFER_SRC_BIT`, despite the source-usage requirement for both `vkCmdCopyBuffer` and `VkDeviceMemoryCopyKHR` address ranges.
- It allocates protected primary and secondary command buffers and records into the one selected by the `primary` or `secondary` intermediate node.
- `fill` writes the selected 32-bit pattern to the destination. `update` creates a 64-word host array containing that pattern and records it as inline update data. `copy` fills the source, inserts a source barrier from transfer write to transfer read, and copies the complete source range to the destination.
- A final buffer barrier makes destination transfer writes available to compute-shader reads. The secondary path records this barrier in the secondary command buffer, ends that buffer, and executes it from the primary.
- The test submits the protected primary command buffer and waits on a fence. It then calls `BufferValidator::validateBuffer()` for the protected destination.
- The validator writes four positions and four reference vectors into a host-visible uniform buffer. It exposes the protected destination through a typed uniform texel-buffer view and uses a protected helper storage buffer.
- `ResetSSBO` sets the helper's `zero` field to zero. `BufferValidator` fetches four destination texels and compares them with the references. Float vectors use an absolute per-component threshold of `0.1`; the signed and unsigned integer forms require equal values under the same expression.
- A mismatch enters a loop whose increment is the helper's zero value, so the validation submission times out after one second and returns `false`. A completed validation submission returns `true`; `iterate()` then reports pass.
- The validator checks four selected texels. The result does not establish an independent comparison of every word in the 256-byte buffer.
- Although each operation registers `float_buffer.primary.static.test_device_address`, those constructor calls use the default `useDeviceAddressCommands == false`. In this source revision they run `vkCmdFillBuffer`, `vkCmdUpdateBuffer`, or the ordinary source-fill and `vkCmdCopyBuffer` sequence rather than the device-address commands.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fill` | The selected protected fill command, transfer-to-shader visibility, command-buffer execution form, or destination validation failed. |
| `update` | The selected protected inline update command, transfer-to-shader visibility, command-buffer execution form, or destination validation failed. |
| `copy` | The source-buffer usage setup, protected source initialization, the transfer-write-to-transfer-read dependency, the selected protected copy command, destination visibility, command-buffer execution form, or destination validation failed. |

### Cause Analysis

#### Protected fill or update execution

**Possible failure symptoms:** One of the four sampled destination texels differs from the selected value, or the validator submission times out after detecting that mismatch. A command submission error can also prevent the test from reaching a successful result.

**Possible implementation causes:** The protected command may fail to write the requested range, may use the wrong 32-bit pattern or inline update bytes, or may fail to make the transfer write visible to the validator. Vulkan defines both commands as transfer operations and requires compatible protected resource access. The test supplies a complete protected destination and a transfer-to-compute dependency; diagnosis beyond those possibilities requires the failing case and Vulkan error information.

#### Protected source initialization and copy execution

**Possible failure symptoms:** A `copy` case produces a wrong value at one of the four sampled destination texels, times out during validation, or returns a Vulkan command or submission error.

**Possible implementation causes:** The CTS source creates the copy source without `VK_BUFFER_USAGE_TRANSFER_SRC_BIT`, violating the source-buffer usage requirement for `vkCmdCopyBuffer`; the implemented `VkDeviceMemoryCopyKHR` path has the same requirement for the buffer from which its source address was queried. Beyond this test-setup defect, the source fill may write incorrect data, the barrier may fail to make that write available to the copy, the copy may not preserve all requested bytes, or the destination barrier may fail to make copied data available to the validator. The test copies the complete 256-byte range with zero source and destination offsets. A specific implementation cause requires investigation only after the source usage defect is corrected.

#### Command-buffer recording and execution form

**Possible failure symptoms:** A failure limited to `secondary` cases appears when the protected operation and barriers are recorded in a secondary command buffer and executed from the primary. A corresponding `primary` case records the same operation directly.

**Possible implementation causes:** A secondary-only failure may involve secondary command-buffer recording, null render-pass and framebuffer inheritance, protected secondary execution, or `vkCmdExecuteCommands`. A failure shared with primary cases points toward common operation, synchronization, resource, or validator behavior. The source does not identify one component as the cause without case-specific evidence.

#### Destination validation

**Possible failure symptoms:** The protected validator submission times out after a mismatch at a sampled texel, or another queue error prevents validation from returning success.

**Possible implementation causes:** The typed buffer view, reference uniform, descriptor bindings, transfer-to-shader dependency, reset program, comparison program, or protected validation submission may be wrong. Since the validator checks four positions rather than all buffer words, a passing result is limited to those observations.

#### Registered device-address leaf does not select the device-address path

**Possible failure symptoms:** The three `test_device_address` leaves pass or fail exactly like their ordinary float primary static counterparts and do not exercise `vkCmdFillMemoryKHR`, `vkCmdUpdateMemoryKHR`, or `vkCmdCopyMemoryKHR`.

**Possible implementation causes:** The registration constructs each leaf without the final `useDeviceAddressCommands` argument, whose default is `false`. This is a CTS source discrepancy rather than a device conformance failure. The source or intended registration must be corrected or confirmed before these leaves can support a device-address command coverage claim.

## Case Pruning

### Requirement-based pruning

- All cases require Vulkan 1.1, protected-memory support, and a protected queue through `checkProtectedContextSupport()`.
- Under Vulkan SC, secondary cases are skipped when `secondaryCommandBufferNullOrImagelessFramebuffer` is `VK_FALSE`.
- A case that enables the device-address implementation path requires `VK_KHR_device_address_commands`. The inspected `test_device_address` registrations do not enable the flag, so they do not trigger this support check.
- The test fixes offsets and sizes to valid full-buffer ranges rather than generating invalid or partially bound transfer cases.

### Design-based pruning

- Each operation uses one 256-byte range. The matrix does not vary offsets, partial sizes, overlapping copies, queue families, or multiple regions.
- The type branches cover float, signed integer, and unsigned integer texel interpretations. They do not generate narrower component widths or other texel-buffer formats.
- Each type and command-buffer branch uses six static and ten random cases. Random positions remain within the 16 available four-component texels.
- Device-address leaves exist only in the float, primary, static branch. No signed, unsigned, secondary, or random device-address leaves are registered.
- The validator samples four positions instead of checking every destination word. This is the selected validation design.

## Key Takeaways

- `fill`, `update`, and `copy` are the behavioral values because each selects a different fixed-function transfer mechanism on protected buffers.
- The copy path adds protected source initialization and a transfer dependency before the destination write, but its source buffer lacks the required transfer-source usage flag. Copy conformance results remain unresolved until that CTS setup defect is corrected.
- Primary and secondary recording, three destination interpretations, and fixed or random values broaden each operation's coverage.
- A protected compute validator checks four typed destination texels after a transfer-to-shader barrier; its shaders are checking infrastructure.
- The source implements device-address command variants, but the registered `test_device_address` leaves leave their selection flag false. Coverage of those commands remains an unresolved source discrepancy.
- Failure interpretation should follow the mapping above rather than assume a driver, hardware, host, or validator fault before the failing stage is isolated.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test case parameters and support | [`FillUpdateCopyBufferTestCase`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L76-L123) | Stores the operation, command-buffer form, validator, and device-address selection flag. |
| Protected buffers and command buffers | [`FillUpdateCopyBufferTestInstance::iterate`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L141-L199) | Creates protected resources and selects primary or secondary recording. |
| Fill, update, and copy commands | [`operation switch`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L200-L296) | Contains the ordinary buffer commands and device-address command variants. |
| Destination visibility and result | [`submit and validate`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L298-L335) | Records the transfer-to-compute barrier, submits protected work, and calls the validator. |
| Float static and random matrix | [`createFillUpdateCopyBufferFloatTests`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L338-L435) | Defines float values, sample positions, and the registered device-address leaves. |
| Signed static and random matrix | [`createFillUpdateCopyBufferIntegerTests`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L438-L527) | Defines signed integer values, positions, and command-buffer branches. |
| Unsigned static and random matrix | [`createFillUpdateCopyBufferUnsignedTests`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L530-L611) | Defines unsigned integer values, positions, and command-buffer branches. |
| Operation test families | [`operation registration`](../../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L616-L648) | Registers `fill`, `update`, and `copy` with the three direct type children. |
| Category placement | [`protected buffer registration`](../../../modules/vulkan/protected_memory/vktProtectedMemTests.cpp#L74-L80) | Places the three operation families under `protected_memory.buffer`. |
| Protected context support | [`checkProtectedContextSupport`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127) | Checks API version, protected memory, and protected queue availability. |
| Validation shader generation | [`initBufferValidatorPrograms`](../../../modules/vulkan/protected_memory/vktProtectedMemBufferValidator.cpp#L86-L194) | Generates typed texel-buffer validation and helper reset programs. |
| Validation resources and timeout | [`BufferValidator::validateBuffer`](../../../modules/vulkan/protected_memory/vktProtectedMemBufferValidator.hpp#L181-L324) | Configures references and descriptors, dispatches protected validation, and interprets timeout. |
| Fill and update command semantics | [`clears.adoc`](../../../../vulkan-docs/src/chapters/clears.adoc#L542-L764) | Defines device-address and buffer-object forms of fill and update. |
| Copy command semantics | [`copies.adoc`](../../../../vulkan-docs/src/chapters/copies.adoc#L22-L170) | Defines protected memory-range copy and buffer-object copy operations. |
