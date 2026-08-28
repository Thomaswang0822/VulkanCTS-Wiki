# Tessellation category：待实现维护者确认的 Source-Level Findings

> 本文从 [Tessellation audit summary](tessellation_audit_summary.md) 抽取 1 项未解决发现，供 Vulkan CTS 实现维护者评估。它不表示 wiki 审计未完成，也不等同于已经确认的 Vulkan 实现缺陷。当前观察集中在 `Invariance` 的 Rule 8 测试路径：源码对 tessellation-coordinate invocation 数量的覆盖和错误结果传播可能不完整。
>
> 本文只记录当前观察和需要确认的问题，不替维护者决定测试是否需要修改，也不直接把任何失败归因于 Vulkan 实现或驱动。审计阶段没有修改 Vulkan CTS C++ 源码、mustpass、规范文件或驱动实现。对应 Level-3 页面已经修正文档表述，使其反映当前实际行为和这两个检查限制。

## 处理建议

建议把该项作为独立的源码调查或 issue：先确认 Rule 8 对实际 tessellation-evaluation invocation 数量的预期、允许的额外 invocation 范围，以及 CTS 应如何传播 coordinate-comparison failure；再决定是否修改测试实现。若确认需要修复，应补充能分别覆盖“坐标数量不足”和“坐标值非法”的回归场景，并重新检查相关 mustpass 覆盖。

## 1. `Invariance` Rule 8：坐标检查可能漏掉缺失 invocation，并把已记录的错误报告成通过

**对应页面：** [Invariance.md](../testfiles/tessellation/Invariance.md)

**对应源码：** [`vktTessellationInvarianceTests.cpp`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2082-L2428)

### 背景：Rule 8 测试在检查什么

Rule 8 的两个测试族检查 tessellation coordinate 的两个性质：

- `tess_coord_component_range`：每个相关坐标分量都必须位于 `[0, 1]`；
- `one_minus_tess_coord_component`：对每个相关分量 `x`，`x + (1.0 - x)` 必须精确等于 `1.0`。

这两个测试族不会由 host 端直接重建所有坐标。测试生成 TES，让每个 tessellation-evaluation invocation 把自己的 `gl_TessCoord` 写入 storage buffer，同时用原子操作记录实际执行了多少次：

```glsl
int index = atomicAdd(sb_out.numInvocations, 1);
sb_out.tessCoord[index] = gl_TessCoord;
```

对应的源码生成路径见 [`TessCoordComponent::initPrograms()`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2147-L2243)，其中 storage-buffer 计数器和坐标数组在 [lines 2225-2237](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2225-L2237) 生成。

### 观察到的代码路径：host 只检查已经记录的坐标

测试执行结束后，host 端先从 storage buffer 读出 shader 实际写入的数量：

```cpp
const int32_t numVertices =
    *static_cast<int32_t *>(resultAlloc.getHostPtr());

const std::vector<tcu::Vec3> vertices = readInterleavedData<tcu::Vec3>(
    numVertices,
    resultAlloc.getHostPtr(),
    resultBufferTessCoordsOffset,
    sizeof(tcu::Vec4));
```

随后，检查循环只遍历已经读出的 `vertices`：

```cpp
for (每个已经读到的 vertex)
    for (每个相关坐标分量)
        if (!compare(...))
        {
            log failure;
            tcu::TestStatus::fail("Invalid tessellation coordinate component");
        }
```

对应源码：

- 读取实际 invocation 数量和坐标：[`vktTessellationInvarianceTests.cpp#L2375-L2386`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2375-L2386)；
- 逐分量比较：[`vktTessellationInvarianceTests.cpp#L2388-L2408`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2388-L2408)。

### 观察一：没有确认 invocation 数量达到应有数量

源码确实计算了一个 `referenceVertexCount(...)`，但当前用途主要是估算 storage buffer 容量：

```cpp
maxNumVerticesInDrawCall = max(
    maxNumVerticesInDrawCall,
    referenceVertexCount(...));

// We may get more invocations than expected, so add some more space
maxNumVerticesInDrawCall += 4;
```

对应源码见 [`referenceVertexCount` 的容量计算](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2258-L2269)。每个 case 结束后，代码只保留了一个上界断言：

```cpp
DE_ASSERT(numVertices <= maxNumVerticesInDrawCall);
```

这个断言防止 shader 写入数量超过已分配的 buffer 容量，但没有检查：

```text
实际 numVertices 是否达到当前 tessellation levels 应生成的最小数量。
```

因此，假设某组 levels 应生成 100 个坐标，但实现或 capture path 只记录了 60 个：

```text
numVertices = 60
host 只检查这 60 个坐标
缺失的 40 个坐标没有进入比较循环
```

如果已经记录的 60 个坐标都满足 Rule 8，当前路径可能不会因为“少了 40 个 invocation”而失败。

这里需要维护者确认的是：

- Rule 8 是否允许实际 invocation 数量大于某个参考数量；
- 如果允许额外 invocation，是否仍应至少检查 `numVertices >= referenceVertexCount(...)`；
- 当前 `referenceVertexCount(...)` 是否适合作为每个 case 的数量下限，而不只是 buffer 容量估算；
- “多预留 4 个槽位”是否只是容量保护，还是也反映了测试意图允许额外 invocation。

### 观察二：发现非法坐标后，failure status 没有返回

比较函数本身能够发现错误。例如：

- `compareTessCoordRange()` 在值不属于 `[0, 1]` 时记录 failure 并返回 `false`；
- `compareOneMinusTessCoord()` 在 `x + (1.0 - x) != 1.0` 时记录 failure 并返回 `false`。

对应实现见 [`compareTessCoordRange()` 和 `compareOneMinusTessCoord()`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2122-L2145)。

但是调用方在收到 `false` 后只构造了一个临时失败状态：

```cpp
tcu::TestStatus::fail("Invalid tessellation coordinate component");
```

没有 `return` 这个状态，也没有保存一个 `anyFailure` 标志。检查循环结束后，函数无条件执行：

```cpp
return tcu::TestStatus::pass("OK");
```

对应源码见 [`vktTessellationInvarianceTests.cpp#L2397-L2411`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2397-L2411)。

因此，假设第 37 个坐标分量非法，当前可观察行为可能是：

```text
host 打印坐标错误日志
继续检查剩余坐标
循环结束
测试函数仍然返回 pass("OK")
```

也就是说，测试日志可能记录了 Rule 8 violation，但 CTS 结果传播路径没有把这个 violation 传给测试框架。

### 为什么需要维护者确认

这两个观察都首先指向 **CTS 测试自身的检查覆盖和结果传播问题**，而不是已经确认的 Vulkan 实现缺陷：

- 测试通过，可能只说明已记录的坐标合法，不说明所有应有 invocation 都被记录；
- 日志出现非法坐标，也不一定会转化为最终的 CTS failure；
- 如果发生 capture、storage-buffer、同步或 host-readback 问题，当前路径也可能表现为数量不足或坐标集合不完整。

因此，不能仅凭当前源码直接断定：

- 哪些具体设备会触发问题；
- 缺失 invocation 一定来自 tessellator，而不是 capture path；
- `referenceVertexCount(...)` 是否就是 Rule 8 所需的准确 failure threshold；
- 修复应当立即返回 failure，还是在检查全部坐标后统一返回 failure。

这就是为什么该项保持为 **UNRESOLVED source-level finding**：源码行为和测试意图之间存在明确的风险，但最终修复方式和回归范围仍需要 CTS 实现维护者确认。

### 需要维护者确认的问题

1. `referenceVertexCount(...)` 是否为每组 tessellation levels 提供了准确的最小 invocation 数量？
2. Rule 8 是否允许实际 invocation 数量超过该参考数量？如果允许，额外 invocation 应如何验证？
3. host 是否应检查当前 case 的 `numVertices` 至少达到参考数量，而不是只检查 buffer 容量上界？
4. 坐标比较失败时，测试是否应立即返回 `tcu::TestStatus::fail(...)`，或记录 `anyFailure` 后在所有坐标检查结束时返回 failure？
5. 是否需要分别新增回归覆盖：
   - invocation 数量不足；
   - invocation 数量足够但坐标越界；
   - `x + (1.0 - x)` 不等于 `1.0`；
   - 额外 invocation 合法但数量高于参考值。
6. 修改后是否需要重新检查两个 Rule 8 测试族的完整 mustpass 覆盖？

相关证据：

- [`TessCoordComponent::test()`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2245-L2428)
- [`referenceVertexCount()` 使用路径](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2258-L2269)
- [`compareTessCoordRange()` / `compareOneMinusTessCoord()`](../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2122-L2145)
- [Rule 8 页面说明](../testfiles/tessellation/Invariance.md#runtime-execution-and-result-checking)
- [Vulkan tessellation invariance rules](../../../vulkan-docs/src/appendices/invariance.adoc#tessellation-invariance)
