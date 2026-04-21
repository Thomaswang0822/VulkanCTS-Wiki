# Vulkan CTS Framework and Mechanism

## Overview

This document provides a comprehensive understanding of how Vulkan CTS is organized, how tests are registered, executed, and verified.

## 1. Vulkan CTS Organization Structure

### 1.1 Directory Hierarchy

```
VK-GL-CTS/
├── external/
│   └── vulkancts/
│       ├── modules/
│       │   └── vulkan/              # Vulkan-specific tests
│       │       ├── api/              # Core Vulkan API tests
│       │       ├── pipeline/         # Pipeline creation and management
│       │       ├── draw/             # Drawing operations
│       │       ├── compute/          # Compute shader tests
│       │       ├── memory/           # Memory management
│       │       ├── image/            # Image operations
│       │       ├── synchronization/  # Sync primitives (fences, semaphores)
│       │       ├── shader_object/    # Shader object tests
│       │       ├── ray_tracing/      # Ray tracing tests
│       │       ├── mesh_shader/      # Mesh shader tests
│       │       ├── video/            # Video encode/decode tests
│       │       └── ... (many more)
│       ├── framework/
│       │   └── vulkan/              # Vulkan framework utilities
│       └── mustpass/
│           └── main/
│               ├── vk-default.txt    # Mustpass list for Vulkan
│               └── vksc-default.txt  # Mustpass list for Vulkan SC
├── framework/                        # dEQP test framework
│   ├── common/                       # Common utilities
│   ├── opengl/                       # OpenGL framework (not Vulkan)
│   └── platform/                     # Platform abstraction
└── external/                         # External dependencies
    ├── spirv-tools/                  # SPIR-V validation and tools
    ├── glslang/                      # GLSL/HLSL compilation
    ├── vulkan-docs/                  # Vulkan specification
    └── amber/                        # Amber test format
```

### 1.2 Test Categories

Vulkan tests are organized into the following top-level categories registered by [`TestPackage::init()`](../modules/vulkan/vktTestPackage.cpp:1346):

1. **info** - Device and driver information tests
2. **api** - Core Vulkan API functionality
3. **memory** - Memory allocation and binding
4. **pipeline** - Pipeline creation and management
5. **binding_model** - Descriptor set binding
6. **spirv_assembly** - SPIR-V assembly tests
7. **glsl** - GLSL shader tests
8. **renderpasses** - Render pass functionality
9. **ubo** - Uniform buffer objects
10. **dynamic_state** - Dynamic state changes
11. **ssbo** - Shader storage buffer objects
12. **query_pool** - Query pool operations
13. **draw** - Drawing operations
14. **compute** - Compute shader tests
15. **image** - Image creation and operations
16. **image_processing** - Image processing operations
17. **wsi** - Window System Integration
18. **synchronization** - Synchronization primitives
19. **synchronization2** - Synchronization2 API tests
20. **sparse_resources** - Sparse memory resources
21. **tessellation** - Tessellation shader tests
22. **rasterization** - Rasterization tests
23. **clipping** - Clipping tests
24. **fragment_operations** - Fragment operation tests
25. **texture** - Texture sampling tests
26. **geometry** - Geometry shader tests
27. **robustness** - Robustness and out-of-bounds access
28. **multiview** - Multi-view rendering
29. **subgroups** - Subgroup operations
30. **ycbcr** - YCbCr image format
31. **protected_memory** - Protected memory tests
32. **device_group** - Multi-device rendering
33. **memory_model** - Memory model operations
34. **conditional_rendering** - Conditional rendering
35. **graphicsfuzz** - GraphicsFuzz/Amber-based tests
36. **imageless_framebuffer** - Imageless framebuffer tests
37. **transform_feedback** - Transform feedback
38. **descriptor_indexing** - Descriptor indexing
39. **fragment_shader_interlock** - Fragment shader interlock
40. **drm_format_modifiers** - DRM format modifiers
41. **ray_tracing_pipeline** - Ray tracing pipeline
42. **ray_query** - Ray query operations
43. **fragment_shading_rate** - Fragment shading rate
44. **reconvergence** - Reconvergence tests
45. **mesh_shader** - Mesh shader tests
46. **fragment_shading_barycentric** - Barycentric coordinates
47. **depth** - Amber depth tests
48. **video** - Video encode/decode
49. **shader_object** - Shader object API
50. **dgc** - Device generated commands
51. **cooperative_vector** - Cooperative vector
52. **tensor** - Tensor operations
53. **data_graph** - Data graph operations

## 2. Test Registration Mechanism

### 2.1 Registration Pattern

Tests are registered using a hierarchical pattern. The main test package registers top-level test categories in [vktTestPackage.cpp:1346-1401](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/vktTestPackage.cpp#L1346):

```cpp
void TestPackage::init(void)
{
    addRootChild("api", m_caseListFilter, api::createTests);
    addRootChild("memory", m_caseListFilter, memory::createTests);
    addRootChild("pipeline", m_caseListFilter, pipeline::createTests);
    // ... more categories
}
```

### 2.2 Test Group Creation Pattern

Each test category has a creation function that builds its children. For example, from [vktApiTests.cpp:86-142](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/api/vktApiTests.cpp#L86):

```cpp
void createApiTests(tcu::TestCaseGroup *apiTests)
{
    tcu::TestContext &testCtx = apiTests->getTestContext();

    apiTests->addChild(createVersionSanityCheckTests(testCtx));
    apiTests->addChild(createDebugUtilsTests(testCtx));
    apiTests->addChild(createDriverPropertiesTests(testCtx));
    apiTests->addChild(createSmokeTests(testCtx));
    apiTests->addChild(createDeviceInitializationTests(testCtx));
    apiTests->addChild(createBufferTests(testCtx));
    // ... more child tests
}

tcu::TestCaseGroup *createTests(tcu::TestContext &testCtx, const std::string &name)
{
    return createTestGroup(testCtx, name, createApiTests);
}
```

### 2.3 Test Hierarchy Example

```
dEQP-VK/
├── api/
│   ├── version_sanity_check/
│   ├── debug_utils/
│   ├── driver_properties/
│   ├── device_initialization/
│   ├── buffer/
│   │   ├── create.destroy
│   │   ├── get_memory_requirements
│   │   └── ... (many more)
│   ├── command_buffers/
│   ├── copies_and_blitting/
│   ├── descriptor_set/
│   ├── pipeline/
│   └── ... (many more)
├── memory/
├── pipeline/
└── ... (more categories)
```

### 2.4 Test Case Naming Convention

Test names follow the pattern: `dEQP-VK.<category>.<subcategory>.<test_name>`

Example: `dEQP-VK.api.buffer.create.destroy`

## 3. Test Execution Flow

### 3.1 Execution Pipeline

Vulkan CTS execution builds on the generic dEQP node lifecycle and adds Vulkan-specific hooks in [`vkt::TestCase`](../modules/vulkan/vktTestCase.hpp:277).

At the framework level, test nodes provide [`init()`](../../../framework/common/tcuTestCase.hpp:152), [`deinit()`](../../../framework/common/tcuTestCase.hpp:153), and [`iterate()`](../../../framework/common/tcuTestCase.hpp:154). Vulkan test cases typically implement the following extension points:

1. [`checkSupport()`](../modules/vulkan/vktTestCase.hpp:280)
   - Validate required features, extensions, limits, or queue capabilities
   - Commonly throws `NotSupportedError` when prerequisites are missing

2. [`delayedInit()`](../modules/vulkan/vktTestCase.hpp:277)
   - Optional Vulkan-specific initialization before program setup
   - Used when tests need additional non-const setup after support checks

3. [`initPrograms()`](../modules/vulkan/vktTestCase.hpp:278)
   - Register shader programs or source collections needed by the test

4. [`createInstance()`](../modules/vulkan/vktTestCase.hpp:279)
   - Create a [`vkt::TestInstance`](../modules/vulkan/vktTestCase.hpp:289) that executes the runtime logic
   - The default implementation throws unless overridden in the test case implementation, as shown in [`TestCase::createInstance()`](../modules/vulkan/vktTestCase.cpp:1932)

5. [`TestInstance::iterate()`](../modules/vulkan/vktTestCase.hpp:299)
   - Execute the actual Vulkan operations
   - Perform verification and return [`tcu::TestStatus`](../../../framework/common/tcuTestCase.hpp:253)

Verification is therefore usually part of test logic inside [`iterate()`](../modules/vulkan/vktTestCase.hpp:299), not a separate universal framework callback.

### 3.2 Test Instance Pattern

Each Vulkan test usually derives from [`vkt::TestCase`](../modules/vulkan/vktTestCase.hpp:277) and provides a matching [`vkt::TestInstance`](../modules/vulkan/vktTestCase.hpp:289):

```cpp
class MyTestCase : public vkt::TestCase
{
public:
    MyTestCase(tcu::TestContext &testCtx, const std::string &name)
        : TestCase(testCtx, name) {}

    void checkSupport(Context &ctx) const override;
    void initPrograms(vk::SourceCollections &programCollection) const override;
    TestInstance *createInstance(Context &ctx) const override;
};

class MyTestInstance : public TestInstance
{
public:
    MyTestInstance(Context &ctx)
        : TestInstance(ctx) {}

    tcu::TestStatus iterate(void) override;
};

tcu::TestStatus MyTestInstance::iterate(void)
{
    VkBuffer         buffer = VK_NULL_HANDLE;
    const VkResult   result = vkCreateBuffer(device, &createInfo, nullptr, &buffer);

    if (result != VK_SUCCESS)
        return tcu::TestStatus::fail("Failed to create buffer");

    VkMemoryRequirements requirements;
    vkGetBufferMemoryRequirements(device, buffer, &requirements);

    if (requirements.size == 0u)
        return tcu::TestStatus::fail("Invalid memory requirements");

    return tcu::TestStatus::pass("Buffer created successfully");
}
```


## 4. Test Verification Methods

### 4.1 Return Value Verification

Most Vulkan functions return `VkResult`. Tests verify these:

```cpp
VkResult result = vkCreateBuffer(device, &createInfo, nullptr, &buffer);
if (result != VK_SUCCESS) {
    return tcu::TestStatus::fail("Buffer creation failed");
}
```

### 4.2 State Verification

Tests verify that Vulkan state is correctly updated:

```cpp
// Query state after calling API
VkMemoryRequirements requirements;
vkGetBufferMemoryRequirements(device, buffer, &requirements);

// Verify requirements are valid
if (requirements.size == 0) {
    return tcu::TestStatus::fail("Invalid memory requirements");
}
```

### 4.3 Output Verification

For rendering tests, verify output using:

- **Image comparison**: Compare rendered image against reference
- **Buffer verification**: Check buffer contents
- **Query results**: Verify query pool results
- **Pipeline state**: Verify pipeline properties

### 4.4 Error Handling Tests

Some tests intentionally exercise unsupported or invalid usage paths, but the exact verification depends on the API being tested.

For commands that return [`VkResult`](../modules/vulkan/api/vktApiTests.cpp:86), the test can validate the returned status code directly:

```cpp
VkResult result = vkCreateBuffer(device, &createInfo, nullptr, &buffer);
if (result != VK_SUCCESS)
    return tcu::TestStatus::fail("Buffer creation failed as part of negative-path validation");
```

For commands that do not return a value, the test must verify observable behavior through other means such as follow-up queries, output validation, or ensuring the CTS catches the expected condition through its own checks.


## 5. Parameter Definition and Combination

### 5.1 Parameter Categories

Vulkan tests typically vary parameters across these dimensions:

1. **Device Features**
   - Required extensions (VK_KHR_*, VK_EXT_*)
   - Feature flags (robustBufferAccess, fragmentStoresAndAtomics)
   - Limits (maxImageDimension, maxComputeWorkGroupSize)

2. **API Parameters**
   - Handle types (buffer, image, shader)
   - Create info structures
   - Flags (VK_BUFFER_USAGE_*)
   - Queue families

3. **Data Parameters**
   - Sizes (small, medium, large)
   - Formats (R8, R16, R32G32, etc.)
   - Configurations (1D, 2D, 3D arrays)

### 5.2 Parameter Combination Strategy

Tests use several strategies for parameter combinations:

**1. All Combinations (Cartesian Product)**
```cpp
// Test all combinations of format and usage
for (const auto &format : formats) {
    for (const auto &usage : usages) {
        for (const auto &tiling : tilings) {
            runTest(format, usage, tiling);
        }
    }
}
```

**2. Representative Sampling**
```cpp
// Test representative subset for quick validation
const auto &testCases = {
    {VK_FORMAT_R8G8B8A8_UNORM, VK_IMAGE_TILING_OPTIMAL, 1024},
    {VK_FORMAT_R32G32B32A32_SFLOAT, VK_IMAGE_TILING_LINEAR, 4096},
    // ... more representative cases
};
```

**3. Boundary Values**
```cpp
// Test edge cases
const int sizes[] = {0, 1, 1024, MAX_SIZE - 1, MAX_SIZE};
```

### 5.3 Test Instance Creation with Parameters

```cpp
class ImageTestCase : public TestCase
{
public:
    ImageTestCase(TestContext &ctx, const std::string &name,
                  VkFormat format, VkImageTiling tiling)
        : TestCase(ctx, name)
        , m_format(format)
        , m_tiling(tiling) {}

    TestInstance *createInstance(Context &ctx) override;

private:
    VkFormat m_format;
    VkImageTiling m_tiling;
};
```

## 6. Test Result Codes

Vulkan CTS tests typically report results through [`tcu::TestStatus`](../../../framework/common/tcuTestCase.hpp:253), which wraps an underlying `qpTestResult` code.

### 6.1 Commonly Used Result Outcomes

- **Pass** - Test passed successfully
- **Fail** - Test failed and indicates a conformance problem
- **NotSupported** - Required feature or capability is unavailable, typically signaled via an exception such as `NotSupportedError`
- **QualityWarning** - Test completed with a quality-related warning
- **CompatibilityWarning** - Test completed with a compatibility-related warning
- **InternalError** - Test or framework infrastructure encountered an unexpected internal problem
- **Waiver** - Result covered by an approved waiver

The generic framework also defines additional low-level result codes, but the items above are the most relevant ones to typical Vulkan CTS test implementations.

### 6.2 Result Reporting

```cpp
// Successful test
return tcu::TestStatus::pass("Buffer created and used correctly");

// Failed test
return tcu::TestStatus::fail("Buffer creation failed with error: " +
                             vkResultToString(result));

// Not supported (feature not available)
if (!ctx.isDeviceFeatureSupported(myFeature)) {
    TCU_THROW(NotSupportedError, "Feature not supported");
}

// Quality warning
m_testCtx.getLog() << tcu::TestLog::Message
                   << "Performance may be suboptimal"
                   << tcu::TestLog::EndMessage;
return tcu::TestStatus::qualityWarning("Suboptimal performance");
```


## 7. Mustpass List

### 7.1 Purpose

The mustpass files identify the test set used for conformance runs.

### 7.2 Location

```text
external/vulkancts/mustpass/main/
├── vk-default.txt    # Vulkan mustpass entry file
└── vksc-default.txt  # Vulkan SC mustpass entry file
```

### 7.3 Structure

The top-level mustpass files are include lists rather than flat lists of individual test cases. As documented in [`README.md`](../README.md:245), [`vk-default.txt`](../mustpass/main/vk-default.txt) and [`vksc-default.txt`](../mustpass/main/vksc-default.txt) reference additional files under their corresponding subdirectories, and those included files collectively define the full mustpass set.

### 7.4 Generation

The mustpass set can be regenerated with:

```bash
python3 external/vulkancts/scripts/build_mustpass.py
```


## 8. Vulkan SC Overview

### 8.1 What is Vulkan SC?

**Vulkan SC** (Safety Critical) is a variant of Vulkan designed for **safety-critical applications** such as:
- Automotive systems (ADAS, infotainment)
- Aerospace and aviation
- Medical devices
- Industrial control systems

### 8.2 Key Differences from Regular Vulkan

| Aspect | Vulkan | Vulkan SC |
|--------|--------|-----------|
| **Target** | General-purpose graphics/compute | Safety-critical systems |
| **Certification** | None required | Must meet ISO 26262, DO-178C, etc. |
| **Dynamic Features** | Full dynamic state, shader compilation | Limited or pre-compiled only |
| **Error Handling** | Layers and validation | Deterministic, no undefined behavior |
| **SPIR-V** | Runtime compilation allowed | Pre-compiled shaders only |
| **Extensions** | Many optional extensions | Strictly defined subset |
| **Memory** | Dynamic allocation common | Pre-allocated memory pools |
| **Threading** | Flexible | Strictly defined threading model |

### 8.3 Vulkan SC CTS

Vulkan SC has its own CTS variant:

- **Executable**: `deqp-vksc` (vs `deqp-vk` for regular Vulkan)
- **Mustpass**: `vksc-default.txt` (vs `vk-default.txt`)
- **Test Scope**: Subset of Vulkan tests, excluding features not in Vulkan SC

From the directory structure, you can see both mustpass lists exist:
```
external/vulkancts/mustpass/main/
├── vk-default.txt    # Vulkan mustpass
└── vksc-default.txt  # Vulkan SC mustpass
```

### 8.4 Why Vulkan SC Matters

Even if you're not working on safety-critical systems, understanding Vulkan SC is valuable because:

1. **Stricter Testing**: Vulkan SC tests often catch edge cases that regular Vulkan tests miss
2. **Best Practices**: Patterns required for Vulkan SC often improve regular Vulkan code quality
3. **Future-Proofing**: Some Vulkan SC restrictions may become best practices for regular Vulkan

## 9. Command Line Options

### 9.1 Essential Options for Running CTS

```bash
# Must specify mustpass file
--deqp-caselist-file=vk-default.txt

# Disable logging to reduce overhead
--deqp-log-images=disable
--deqp-log-shader-sources=disable

# Optional: Specify device
--deqp-vk-device-id=1

# Optional: Disable flush for performance
--deqp-log-flush=disable
```

### 9.2 Execution Modes

```bash
# Run all tests in mustpass
deqp-vk --deqp-caselist-file=vk-default.txt

# Run specific test
deqp-vk --deqp-case=dEQP-VK.api.buffer.create

# Run tests matching pattern
deqp-vk --deqp-case=dEQP-VK.api.buffer.*

# Parallel execution (N fractions)
deqp-vk --deqp-caselist-file=vk-default.txt --deqp-fraction=0,4
```

## 10. Framework Components

### 10.1 dEQP Framework

Vulkan CTS is built on **dEQP** (Draw Elements Quality Program), which provides:

- **Test Case Management**: Hierarchical test organization
- **Test Execution**: Test runner and iteration
- **Result Reporting**: XML-based test logs
- **Platform Abstraction**: Multi-platform support

### 10.2 Key Framework Classes

```cpp
// Test hierarchy
tcu::TestContext       // Overall test context
tcu::TestPackage       // Top-level test package
tcu::TestCaseGroup     // Group of tests
tcu::TestCase          // Individual test case
tcu::TestInstance      // Runtime instance of a test

// Vulkan-specific
vkt::Context           // Vulkan context (instance, device, queue)
vkt::TestCase          // Vulkan test case base class
vkt::TestInstance      // Vulkan test instance base class
```

### 10.3 Framework Utilities

Located in `framework/vulkan/`:

- **vkRef.hpp**: Smart pointer wrappers for Vulkan handles
- **vkPrograms.hpp**: Shader program management
- **vkBuilderUtil.hpp**: Common build patterns
- **vkCmdUtil.hpp**: Command buffer utilities
- **vkImageUtil.hpp**: Image format utilities
- **vkBarrierUtil.hpp**: Pipeline barrier helpers
- **vkStrUtil.hpp**: String utilities for Vulkan enums

## 11. Build and Execution

### 11.1 Building

```bash
# Step 1: Download dependencies (run from project root)
cd <project-root>
python3 external/fetch_sources.py

# Step 2: Create build directory (separate from source)
mkdir build-vulkancts
cd build-vulkancts

# Step 3: Configure with CMake (from build directory)
cmake .. -G"Visual Studio 18 2026" -A x64

# Step 4: Build deqp-vk executable
cmake --build . --config Debug --target deqp-vk
```

**Important**: Always build in a separate directory to avoid polluting the source tree with generated files.

### 11.2 Running

```bash
# Navigate to the test directory (NOT the Debug subdirectory)
cd build-vulkancts/external/vulkancts/modules/vulkan

# Run all mustpass tests
Debug/deqp-vk.exe --deqp-caselist-file=vk-default.txt \
                  --deqp-log-images=disable \
                  --deqp-log-shader-sources=disable
```

**Note**: Do NOT enter the `Debug` subdirectory. Running from `modules/vulkan` ensures relative paths to test data files are correct.

### 11.3 Interpreting Results

Results are written to `TestResults.qpa`:

```xml
<?xml version="1.0"?>
<TestResults>
    <TestCaseResult name="dEQP-VK.api.buffer.create.destroy">
        <Result StatusCode="Pass">Not validated</Result>
        ...
    </TestCaseResult>
</TestResults>
```

## 12. Important Concepts for Framework Understanding

### 12.1 Test Case Filter

Tests can be filtered using `m_caseListFilter` to run only specific tests:

```cpp
addRootChild("api", m_caseListFilter, api::createTests);
```

### 12.2 Support Checks

Before running tests, `checkSupport()` determines if the device supports required features:

```cpp
void MyTestCase::checkSupport(Context &ctx)
{
    if (!ctx.isInstanceExtensionSupported("VK_KHR_device_group")) {
        TCU_THROW(NotSupportedError, "VK_KHR_device_group not supported");
    }
}
```

### 12.3 Delayed Initialization

Some tests use `delayedInit()` for deferred initialization:

```cpp
void MyTestCase::delayedInit()
{
    // Create resources that depend on device capabilities
}
```

### 12.4 Resource Management

Tests use RAII patterns for Vulkan resources:

```cpp
class BufferWithMemory
{
    VkBuffer buffer;
    de::MovePtr<Allocation> allocation;
public:
    BufferWithMemory(Context &ctx, const VkBufferCreateInfo &info);
    ~BufferWithMemory();
};
```

## 13. Key Files for Framework Understanding

### 13.1 Entry Points

- [vktTestPackage.cpp](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/vktTestPackage.cpp) - Main test package, test registration
- `tcuMain.cpp` - Framework entry point

### 13.2 Core Framework

- [vkRef.hpp](file:///f:/repos/VK-GL-CTS/framework/vulkan/vkRef.hpp) - Handle wrappers
- [vkPrograms.hpp](file:///f:/repos/VK-GL-CTS/framework/vulkan/vkPrograms.hpp) - Shader programs
- [vkCmdUtil.hpp](file:///f:/repos/VK-GL-CTS/framework/vulkan/vkCmdUtil.hpp) - Command utilities

### 13.3 Test Infrastructure

- [vktApiTests.cpp](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/api/vktApiTests.cpp) - API test registration
- [vktApiBufferTests.cpp](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/api/vktApiBufferTests.cpp) - Buffer tests
- [vktTestGroupUtil.hpp](file:///f:/repos/VK-GL-CTS/external/vulkancts/modules/vulkan/vktTestGroupUtil.hpp) - Test group utilities

### 13.4 Documentation

- [README.md](file:///f:/repos/VK-GL-CTS/external/vulkancts/README.md) - Build and run instructions
- [Objectives.md](file:///f:/repos/VK-GL-CTS/external/vulkancts/wiki/Objectives.md) - Project objectives
- [doc/testspecs/VK/apitests.adoc](file:///f:/repos/VK-GL-CTS/doc/testspecs/VK/apitests.adoc) - API test specifications

## Summary

Vulkan CTS is a comprehensive test suite built on the dEQP framework with:

1. **Hierarchical Organization**: Tests organized by category (api, memory, pipeline, etc.)
2. **Automated Registration**: Tests registered using factory pattern
3. **Parameter Variation**: Comprehensive parameter testing across formats, sizes, features
4. **Multiple Verification Methods**: Return values, state queries, output validation
5. **Mustpass List**: Defined minimum tests for conformance
6. **Detailed Reporting**: XML-based logs with Pass/Fail/Waiver/NotSupported
7. **Platform Abstraction**: Supports Windows, Linux, Android, macOS
8. **Vulkan SC Variant**: Separate test suite for safety-critical systems

This framework ensures comprehensive validation of Vulkan implementations across all aspects of the API.
