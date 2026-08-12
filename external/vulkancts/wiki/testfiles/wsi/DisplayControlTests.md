## Overview

**Core question:** Do the four `VK_EXT_display_control` cases exercise their registered direct-display operations, and what does each reachable check establish?

- `vktWsiDisplayControlTests.cpp` implements four test case leaves under `wsi.display_control`.
- The cases do not take a platform window-system parameter. The counter case creates a direct display surface before its ownership gate. The power and display-event cases query the display count before the same gate, but never reach the call that retrieves `VkDisplayKHR` handles on current platforms. The device-event case registers an event on the logical device without enumerating displays.
- The source intends `display_power_control` to check a fixed power-state sequence, and the two event cases to check registration return values before destroying the fences without waiting. On every platform implementation currently in the repository, however, `hasDisplay()` is true for at least one WSI type. The shared ownership gate therefore reports `NotSupported` before the counter, power, or display-event operation; only `register_device_event` bypasses that gate.
- If the ownership gate were passed, `swapchain_counter` would enable `VK_SURFACE_COUNTER_VBLANK_EXT` and present 20 FIFO frames. Its counter query would still be unreachable: the iteration boundary finishes after frame index 19, so `render()` never enters its `m_frameNdx >= m_frameCount` query branch.

## Background Knowledge

For the shared concept direct-display objects, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- `VK_EXT_display_control` can create a fence that a display or device event will signal. The first-pixel-out event occurs when the first pixel of the next refresh cycle leaves the display engine. The hotplug event occurs when a display is plugged into or unplugged from the device ([event fences](../../../../vulkan-docs/src/chapters/synchronization.adoc#L2882-L2988)).
- A swapchain enables surface counters through `VkSwapchainCounterCreateInfoEXT`. The presentation engine activates them when it processes the first presentation command ([surface counters](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6434-L6489)).

## Registration Hierarchy

```text
wsi.display_control
├── swapchain_counter
├── display_power_control
├── register_display_event
└── register_device_event
```

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `swapchain_counter`, `display_power_control`, `register_display_event`, `register_device_event` | Selects the source path, including whether the ownership gate blocks its intended operation. | [`createDisplayControlTests`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L988-L994) |
| Display set | All handles returned by `vkGetPhysicalDeviceDisplayPropertiesKHR` | If their ownership gate were passed, the power and display-event cases would repeat for each available display. | [`getDisplays`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L853-L887) |
| Display ownership | No platform WSI type may report display access | Gates the counter, power, and display-event cases. Every repository platform implementation reports at least one available type, so these three cases currently stop as `NotSupported`; the device-event case does not run this check. | [`createTestDevice`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L96-L143), [`getDisplays`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L868-L875), [Linux](../../../../../framework/platform/lnx/tcuLnxVulkanPlatform.cpp#L509-L539), [Android](../../../../../framework/platform/android/tcuAndroidPlatform.cpp#L412-L417), [macOS](../../../../../framework/platform/osx/tcuOSXVulkanPlatform.cpp#L150-L159), [Windows](../../../../../framework/platform/win32/tcuWin32VulkanPlatform.cpp#L318-L324) |
| Power sequence | `ON`, `SUSPEND`, `OFF`, `ON`; 1000 ms after each request | Defines the intended three-state exercise and restoration to `ON`, after the currently blocking ownership gate. | [`testDisplayPowerControl`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L889-L930) |
| Display event type | `VK_DISPLAY_EVENT_TYPE_FIRST_PIXEL_OUT_EXT` | Defines one intended fence request per display after the currently blocking ownership gate. | [`testDisplayEvent`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L932-L962) |
| Device event type | `VK_DEVICE_EVENT_TYPE_DISPLAY_HOTPLUG_EXT` | Requests one fence for a display plug or unplug event. | [`testDeviceEvent`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L964-L984) |
| Counter path frame count | `20` | Would set the number of acquire, submit, and present iterations after the currently blocking ownership gate. | [`SwapchainCounterTestInstance`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L604-L637), [`iterate`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L762-L803) |
| Counter path present mode | `VK_PRESENT_MODE_FIFO_KHR` | Fixes presentation behavior for the swapchain case. | [`SwapchainCounterTestInstance`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L624-L630) |
| Enabled surface counter | `VK_SURFACE_COUNTER_VBLANK_EXT` | Adds the vblank counter to swapchain creation. The current loop does not reach the query. | [`createSwapchainCounterConfig`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L464-L469), [`render`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L748-L759) |
| Out-of-date recovery limit | `10` recoveries | Bounds swapchain recreation after acquire or present reports `VK_ERROR_OUT_OF_DATE_KHR`. | [`iterate`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L762-L803) |

## Behavior Parameters

The registered test case leaf is the primary behavioral axis. Each value selects a different extension operation or presentation path.

### `swapchain_counter`: direct presentation with an enabled counter

The constructor selects a direct display surface, then `createTestDevice()` applies the shared ownership gate. All current repository platforms make that gate report `NotSupported`, so the case does not reach swapchain creation or presentation. If a platform passed the gate, the source would enable `VK_SURFACE_COUNTER_VBLANK_EXT` on a FIFO swapchain and present 20 rendered frames; even then, `render()` would not query the counter because it sees indices 0 through 19 but requires `m_frameNdx >= 20`.

### `display_power_control`: display power requests

After obtaining the display count, the shared ownership gate runs before the display list and power loop. All current repository platforms therefore report `NotSupported`. If the gate were passed, the case would call `vkDisplayPowerControlEXT` with `VK_DISPLAY_POWER_STATE_ON_EXT`, `VK_DISPLAY_POWER_STATE_SUSPEND_EXT`, `VK_DISPLAY_POWER_STATE_OFF_EXT`, and `VK_DISPLAY_POWER_STATE_ON_EXT` for each display, require `VK_SUCCESS`, and sleep for 1000 ms after each call.

### `register_display_event`: first-pixel-out fence registration

This case uses the same display enumeration and ownership gate as the power case, so current repository platforms report `NotSupported` before event registration. If the gate were passed, it would call `vkRegisterDisplayEventEXT` with `VK_DISPLAY_EVENT_TYPE_FIRST_PIXEL_OUT_EXT` once per display, require `VK_SUCCESS`, and destroy all returned fences without waiting for the event.

### `register_device_event`: hotplug fence registration

The case calls `vkRegisterDeviceEventEXT` with `VK_DEVICE_EVENT_TYPE_DISPLAY_HOTPLUG_EXT`. It requires `VK_SUCCESS` and destroys the returned fence without waiting for a hotplug event.

## Shader Analysis

Only `swapchain_counter` defines shaders. If its ownership gate were passed, they would draw a fixed orange quad to produce presentable work; current repository platforms stop before pipeline creation. Shader output is not checked. The other three cases have no shader path.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.wsi.display_control.swapchain_counter
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `swapchain_counter` | Selects the only case that builds a graphics pipeline and presents frames. |
| `quad-vert` | Generates six clip-space positions from `gl_VertexIndex` for a triangle-list quad. |
| `VK_PRESENT_MODE_FIFO_KHR` and `VK_SURFACE_COUNTER_VBLANK_EXT` | Configure host-side presentation and swapchain creation without changing the shader source. |

#### Purpose

If execution reached the draw, the vertex shader would cover the render area with two triangles. It supplies rendering work for presentation but does not produce a value that the host validates.

#### Structural Design

| Phase | Operation | Result |
|---|---|---|
| Vertex selection | Divide offsets of `gl_VertexIndex` by 3, then take the remainder modulo 2 | Selects the x and y clip-space signs for each vertex. |
| Position output | Construct `vec4(x, y, 0.0, 1.0)` | Writes one corner position to `gl_Position`. |
| Fixed fragment stage | Write `vec4(1.0, 0.5, 0.0, 1.0)` | Colors the rendered quad orange. |

#### Shader Code

```glsl
#version 450
out gl_PerVertex {
    vec4 gl_Position;
};
highp float;
/// The built-in vertex index selects one of the six vertices in the triangle-list quad.
void main (void) {
    /// Each group of three vertices forms one triangle. The modulo selects its x sign.
    gl_Position = vec4(((gl_VertexIndex + 2) / 3) % 2 == 0 ? -1.0 : 1.0,
                       /// The offset changes the grouping used for the y sign.
                       ((gl_VertexIndex + 1) / 3) % 2 == 0 ? -1.0 : 1.0, 0.0, 1.0);
}
```

#### Additional Info

- [`initPrograms`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L822-L840) generates `quad-vert` and the fixed `quad-frag` stage. The fragment stage does not vary and is not part of the test's observation.
- [`createPipeline`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L428-L452) binds both modules. [`createCommandBuffer`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L288-L330) records a six-vertex draw.
- The source passes no explicit `vk::ShaderBuildOptions`, so the CTS uses the SPIR-V 1.0 baseline target ([baseline target](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Test case leaf | Only `swapchain_counter` builds the quad shaders. The three function cases have no shader stage. | [`SwapchainCounterTestCase::initPrograms`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L806-L840), [`createDisplayControlTests`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L988-L994) |
| Counter and present-mode values | `VK_SURFACE_COUNTER_VBLANK_EXT` and `VK_PRESENT_MODE_FIFO_KHR` affect host setup, while the generated GLSL remains fixed. | [`SwapchainCounterTestInstance`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L604-L637) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 37
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %gl_VertexIndex
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
       %bool = OpTypeBool
   %float_n1 = OpConstant %float -1
    %float_1 = OpConstant %float 1
      %int_1 = OpConstant %int 1
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpLoad %int %gl_VertexIndex
         %17 = OpIAdd %int %15 %int_2
         %19 = OpSDiv %int %17 %int_3
         %20 = OpSMod %int %19 %int_2
         %22 = OpIEqual %bool %20 %int_0
         %25 = OpSelect %float %22 %float_n1 %float_1
         %26 = OpLoad %int %gl_VertexIndex
         %28 = OpIAdd %int %26 %int_1
         %29 = OpSDiv %int %28 %int_3
         %30 = OpSMod %int %29 %int_2
         %31 = OpIEqual %bool %30 %int_0
         %32 = OpSelect %float %31 %float_n1 %float_1
         %34 = OpCompositeConstruct %v4float %25 %32 %float_0 %float_1
         %36 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %36 %34
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The counter case creates a custom instance with `VK_KHR_surface`, `VK_KHR_display`, and `VK_EXT_display_surface_counter`; selects a display, supporting plane, first display mode, surface, and present-capable queue; and then calls `createTestDevice()`. The ownership loop reports `NotSupported` because every current platform returns true for at least one WSI type, so execution stops there.
- If that gate were passed, the custom device would enable `VK_KHR_swapchain` and `VK_EXT_display_control`, create a FIFO swapchain with `VK_SURFACE_COUNTER_VBLANK_EXT`, and run acquire, draw, submit, and present iterations. The loop would still finish after calling `render()` at indices 0 through 19, before the guarded counter query could run.
- The power and display-event cases obtain a nonzero display count but hit the same ownership gate before the second enumeration call fills the display list. Their power requests and display-event registration checks are therefore unreachable on current repository platforms.
- The device-event case bypasses display enumeration and the ownership gate. It registers and destroys one fence without waiting, so a pass covers the registration return value and cleanup path, not hotplug delivery.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `swapchain_counter` | Current repository platforms report `NotSupported` at the ownership gate. If a platform passed that gate, swapchain setup, acquire, submission, or presentation could fail, or the case could exceed 10 `VK_ERROR_OUT_OF_DATE_KHR` results; the counter branch would remain unreachable. |
| `display_power_control` | Current repository platforms report `NotSupported` at the ownership gate. If a platform passed it, a power-transition request could return non-success. |
| `register_display_event` | Current repository platforms report `NotSupported` at the ownership gate. If a platform passed it, first-pixel-out event registration could return non-success. |
| `register_device_event` | A non-success result while registering the display-hotplug event fence. |

### Cause Analysis

#### Counter-path ownership gate or presentation failure

**Possible failure symptoms:** On current repository platforms, the case stops as `NotSupported` before device and swapchain creation. If a platform passed the ownership gate, `swapchain_counter` could return a Vulkan error during display/surface selection, swapchain resource creation, image acquisition, queue submission, or presentation, or report `Received too many VK_ERROR_OUT_OF_DATE_KHR errors.` after the bounded recovery path is exhausted.

**Possible implementation causes:** The current source gate conflicts with every platform's `hasDisplay()` behavior and prevents the intended operation; this is a CTS source defect, not an implementation failure. If a platform passed the gate, the selected device could lack a present-capable queue or fail a required display, surface, swapchain, synchronization, or presentation operation. Repeated out-of-date results could prevent completion. Even a pass on that hypothetical path could not establish counter correctness because the later frame-index defect prevents the query.

#### Power-path ownership gate or result failure

**Possible failure symptoms:** Current repository platforms stop as `NotSupported` before the power loop. On a platform that passed the ownership gate, `vkDisplayPowerControlEXT` could return a result other than `VK_SUCCESS` for one request in the `ON`, `SUSPEND`, `OFF`, `ON` sequence.

**Possible implementation causes:** The current source gate conflicts with every platform's `hasDisplay()` behavior and prevents the intended operation; this is a CTS source defect, not an implementation failure. If a platform passed the gate, the implementation could reject the requested state change; the CTS message would identify the failing `VkDisplayPowerStateEXT`.

#### Display-event ownership gate or registration failure

**Possible failure symptoms:** Current repository platforms stop as `NotSupported` before registration. On a platform that passed the ownership gate, `vkRegisterDisplayEventEXT` could return a non-success result for one display and report `vkRegisterDisplayEventEXT returned invalid result`.

**Possible implementation causes:** The current source gate conflicts with every platform's `hasDisplay()` behavior and prevents the intended operation; this is a CTS source defect, not an implementation failure. If a platform passed the gate, the implementation could fail to register `VK_DISPLAY_EVENT_TYPE_FIRST_PIXEL_OUT_EXT` or return its fence for that `VkDisplayKHR`. The case would still provide no evidence about later signaling because it never waits.

#### Device-event registration failure

**Possible failure symptoms:** `vkRegisterDeviceEventEXT` returns a non-success result, and the case reports `vkRegisterDeviceEventEXT returned invalid result`.

**Possible implementation causes:** The implementation fails to register `VK_DEVICE_EVENT_TYPE_DISPLAY_HOTPLUG_EXT` or return its fence. The case does not trigger or wait for hotplug, so later event signaling remains outside its result.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_display_control`.
- `swapchain_counter` also requires `VK_KHR_display`, `VK_KHR_surface`, `VK_EXT_display_surface_counter`, `VK_KHR_swapchain`, a display-plane intersection, a present-capable queue, FIFO presentation, and `VK_SURFACE_COUNTER_VBLANK_EXT` support.
- The shared ownership test design-prunes the counter, power, and display-event cases on every platform implementation currently in the repository because each reports at least one available WSI display type. The power and display-event cases also require at least one `VkDisplayKHR`; neither selects a display plane.
- The device-event case does not enumerate displays, inspect display ownership, or select a display plane.

### Design-based pruning

- The test family has four fixed leaves and no registered dimensions below them.
- If its ownership gate were passable, `swapchain_counter` would fix the frame count at 20, use FIFO presentation, and enable only the vblank counter; its later frame-index control flow would still omit the intended counter observation.
- `display_power_control` uses one four-step sequence rather than generating other state orders.
- The event cases select one event type each and omit fence waits or synthetic event triggers.

## Key Takeaways

- The registered test case leaf selects four separate direct-display behaviors.
- Current platform `hasDisplay()` implementations make the shared ownership gate report `NotSupported`, so the counter, power, and display-event operations are unreachable as the source stands.
- `register_device_event` remains reachable because it bypasses that gate; it validates registration and cleanup, not event delivery or fence signaling.
- Even if a platform passed the ownership gate, `swapchain_counter` would complete 20 presentations but its final index check would prevent the counter query and range validation from running.
- The fixed quad shaders would create presentable work on that hypothetical reachable path. Their output is not a checked result.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `createDisplayControlTests` | [`vktWsiDisplayControlTests.cpp#L988-L994`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L988-L994) | Registers the four test case leaves. |
| `createWsiTests` | [`vktWsiTests.cpp#L76-L90`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L90) | Attaches `display_control` under the `wsi` test category. |
| `createInstance` and `createTestDevice` | [`vktWsiDisplayControlTests.cpp#L70-L143`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L70-L143) | Defines counter-path extensions and display-ownership checks. |
| Platform `hasDisplay()` implementations | [Linux](../../../../../framework/platform/lnx/tcuLnxVulkanPlatform.cpp#L509-L539), [Android](../../../../../framework/platform/android/tcuAndroidPlatform.cpp#L412-L417), [macOS](../../../../../framework/platform/osx/tcuOSXVulkanPlatform.cpp#L150-L159), [Windows](../../../../../framework/platform/win32/tcuWin32VulkanPlatform.cpp#L318-L324) | Shows why at least one ownership-loop iteration succeeds on every current Vulkan platform. |
| `getDisplayAndDisplayPlane` and `createSurface` | [`vktWsiDisplayControlTests.cpp#L146-L245`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L146-L245) | Selects a compatible plane and creates the direct display surface. |
| `createSwapchainCounterConfig` and `createSwapchainConfig` | [`vktWsiDisplayControlTests.cpp#L464-L540`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L464-L540) | Enables the vblank counter and builds the fixed FIFO swapchain configuration. |
| `render` and `iterate` | [`vktWsiDisplayControlTests.cpp#L698-L803`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L698-L803) | Shows presentation, recovery, the guarded counter query, and termination before that query. |
| `initPrograms` | [`vktWsiDisplayControlTests.cpp#L822-L840`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L822-L840) | Generates the fixed quad shaders. |
| `getDisplays` | [`vktWsiDisplayControlTests.cpp#L853-L887`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L853-L887) | Enumerates displays for the function cases. |
| Power and event functions | [`vktWsiDisplayControlTests.cpp#L889-L984`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L889-L984) | Implements the command result checks and fence cleanup. |
| Default mustpass paths | [`wsi.txt#L11515-L11518`](../../../mustpass/main/vk-default/wsi.txt#L11515-L11518) | Lists all four registered paths. |
| Display control specification | [`wsi.adoc#L2181-L2234`](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L2181-L2234) | Defines display power control and power-state values. |
| Surface counter specification | [`wsi.adoc#L6434-L6491`](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6434-L6491) | Defines counter enablement, activation, and query behavior. |
| Event fence specification | [`synchronization.adoc#L2882-L2989`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L2882-L2989) | Defines device and display event fences. |
