## Overview

**Core question:** Can a Vulkan implementation compile and execute a long physical-storage-buffer comparison shader without crashing?

- This page covers `ssbo.corner_case.long_shader_bitwise_and`, implemented in [`vktSSBOCornerCase.cpp`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L46-L60).
- The test generates one compute shader with 589 indexed comparisons against an unsized `ivec4` array reached through a buffer-reference pointer.
- The shader keeps a storage-buffer increment so the comparison chain remains observable to the compiler.
- The test passes when the dispatch completes without a crash. It does not compare a computed data result with a host reference.

## Background Knowledge

- A [buffer device address](https://docs.vulkan.org/spec/latest/chapters/resources.html#resources-buffer-device-addresses) lets shader code use a device address to reach storage-buffer memory. The address must be passed to the shader in a compatible interface, here a push constant containing a `BlockA` buffer-reference value.
- A compute dispatch runs the compute shader for its workgroup. This test uses one workgroup, so the stress comes from the generated shader expression sequence and buffer-reference accesses rather than from a large dispatch grid.

## Registration Hierarchy

```text
ssbo.corner_case
└── long_shader_bitwise_and
```

The `corner_case` test family is added to the `ssbo` test category by the parent [`createTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2235-L2255). [`createSSBOCornerCaseTests()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334) creates the family and its single test case leaf.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `long_shader_bitwise_and` | Selects the physical-storage-buffer stress implementation. | [`createSSBOCornerCaseTests()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334) |
| Comparison count | `589` | Controls the number of generated indexed comparisons and the size of the tested buffer. The source comment identifies 589 as the minimum value that caused the targeted crash. | [`CornerCase`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L46-L60) |
| Generated comparison constants | Deterministic values in `[-9, 9]` | Supplies the right-hand `ivec4` value for each comparison. A fixed random seed makes the generated shader reproducible. | [`useCornerCaseShader()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L62-L99) |

## Behavior Parameters

The test case leaf is the primary behavioral axis. It has one value.

### `long_shader_bitwise_and`: long buffer-reference comparison chain

The shader declares `BlockA` as a `std430` buffer-reference block with an unsized `ivec4 a[]` array. Its `main()` function initializes `allOk` to true, then ANDs the result of 589 calls to `compare_ivec4()`. Each call reads `blockA.a[i]` and compares it with a generated `ivec4` constant. If the aggregate result is true, the shader increments an auxiliary storage-buffer value. The test targets the compiler and execution path exercised by this unusually long chain of buffer-reference accesses.

## Shader Analysis

The test generates its compute shader in [`useCornerCaseShader()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L62-L99). The generated source uses `#version 310 es` and enables `GL_EXT_buffer_reference`. `BlockA` contains the unsized array, while `PC` carries the `BlockA` pointer through a push constant. The shader uses `compare_ivec4()` for each equality operation, combines the results with integer bitwise AND, and increments `ac_numIrrelevant` when all comparisons succeed. That increment gives the compiler an observable side effect and prevents it from removing the comparison sequence as unused work.

The test does not inspect the value of `ac_numIrrelevant` after execution. Its role is to preserve the generated workload, while the host-side result is whether the dispatch completes.

## Runtime Execution and Result Checking

- `CornerCase::createInstance()` checks buffer-device-address support and reports `NotSupportedError` when physical storage-buffer pointers are unavailable. [`createInstance()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L317-L322)
- The instance creates a 4-byte host-visible storage buffer for `ac_numIrrelevant`, clears it, and flushes the mapped memory. [`SSBOCornerCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L168-L217)
- It creates a second storage buffer with `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT`. Its size is `64 * 589` bytes, which accommodates the 589 `ivec4` elements read by the shader, and the host obtains its device address with `vkGetBufferDeviceAddress`. [`SSBOCornerCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L217-L241)
- The host builds a descriptor set with one storage-buffer binding for the auxiliary buffer and a pipeline layout with one compute-stage push-constant range large enough for `VkDeviceAddress`. [`SSBOCornerCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L188-L211), [`SSBOCornerCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L243-L283)
- The command buffer binds the compute pipeline, pushes the buffer address, binds the descriptor set, and dispatches `(1, 1, 1)`. The host submits that primary command buffer to the universal queue and waits for completion. [`SSBOCornerCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L285-L304)
- After the wait returns, the instance reports `pass("Test did not cause a crash")`. The test has no host-side comparison or expected-value check. [`SSBOCornerCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L300-L307)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `long_shader_bitwise_and` | The implementation failed while compiling, launching, or executing the generated physical-storage-buffer shader, or the submission did not complete normally. |

### Cause Analysis

#### Long physical-storage-buffer shader execution

**Possible failure symptoms:** The test process or device crashes during shader creation or the one-workgroup dispatch instead of reaching the pass result.

**Possible implementation causes:** The source establishes the stress conditions but does not identify a specific faulty component. The failure could arise in shader compilation, lowering of the repeated buffer-reference accesses and comparisons, pipeline creation, or device execution. Source-level investigation is needed to localize the cause.

## Case Pruning

### Requirement-based pruning

`CornerCase::createInstance()` skips the test with `NotSupportedError` unless the context supports buffer-device addresses. This excludes implementations that cannot provide the physical storage-buffer pointer feature required by the shader. [`createInstance()`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L317-L322)

### Design-based pruning

The test fixes the comparison count at 589 and registers one test case leaf. It does not generate a matrix of counts or expose the random constants as registered parameters. The fixed count preserves the regression workload identified by the source comment.

## Key Takeaways

- `long_shader_bitwise_and` is a crash-regression stress test, not a layout-result comparison.
- The workload combines a 589-element buffer-reference array with a generated chain of `ivec4` equality checks.
- The auxiliary storage-buffer increment keeps the generated comparison chain in the shader, but the test does not read that buffer back.
- A supported implementation reaches the pass result after the single compute dispatch completes without a crash.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `useCornerCaseShader()` | [`vktSSBOCornerCase.cpp#L62-L99`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L62-L99) | Generates the buffer-reference shader and its 589 comparisons. |
| `CornerCase::createInstance()` | [`vktSSBOCornerCase.cpp#L317-L322`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L317-L322) | Applies the buffer-device-address support gate. |
| `SSBOCornerCaseInstance::iterate()` setup | [`vktSSBOCornerCase.cpp#L168-L283`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L168-L283) | Creates buffers, descriptors, push constants, and the compute pipeline. |
| `SSBOCornerCaseInstance::iterate()` dispatch and result | [`vktSSBOCornerCase.cpp#L285-L307`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L285-L307) | Records, submits, waits for, and evaluates the dispatch. |
| `createSSBOCornerCaseTests()` | [`vktSSBOCornerCase.cpp#L330-L334`](../../../modules/vulkan/ssbo/vktSSBOCornerCase.cpp#L330-L334) | Registers `corner_case.long_shader_bitwise_and`. |
| Vulkan default mustpass | [`vk-default/ssbo.txt#L1`](../../../mustpass/main/vk-default/ssbo.txt#L1) | Confirms the Vulkan registration path. |
| Vulkan SC default mustpass | [`vksc-default/ssbo.txt#L1`](../../../mustpass/main/vksc-default/ssbo.txt#L1) | Confirms the Vulkan SC registration path. |
