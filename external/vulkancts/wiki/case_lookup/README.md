# CTS Registration Path 查询工具

这个工具接收一个以 `dEQP-VK.` 开头的完整 Vulkan CTS registration path，并返回对应的中文 Level-3 Wiki 页面链接。当前索引覆盖 `wiki_rewrite_checklist.md` 中 33 个已完成 rewrite 的 category。

## 设计边界

系统分为两个阶段：人工监督的数据构建，以及不做任何数据转换的静态运行。

```text
Wiki Registration Hierarchy + mustpass + build helpers
                         │
                         ▼
                     build.py
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
本地 SQLite 中间产物                 site/mappings.json
(db/ 和 final DB，ignored)           (最终 runtime data，tracked)
                                          │
                         ┌────────────────┴────────────────┐
                         ▼                                 ▼
                  本地静态 HTTP server                 GitLab Pages
                         │                                 │
                         └────────── site/index.html ──────┘
                                      +
                                site/mappings.json
```

关键原则：

1. `build.py` 是唯一的数据生成入口；
2. build 可能暴露 Wiki tree、ownership、mustpass coverage 或 category projection 问题，因此只在本地、人工监督下运行；
3. SQLite 用于可靠的 category build、merge、约束和诊断，但只是 ignored intermediate artifact；
4. `site/index.html` 与 `site/mappings.json` 是唯一的 runtime artifact，提交到 repository；
5. CLI、本地浏览器 E2E 和 GitLab Pages 都读取同一个 tracked JSON；
6. CI 不运行 builder 或 exporter，只检查并发布 commit 中的 `site/`。

## 本地受控构建

完整构建：

```bash
python3 external/vulkancts/wiki/case_lookup/build.py
```

默认生成：

```text
external/vulkancts/wiki/case_lookup/db/<category>.sqlite3
external/vulkancts/wiki/case_lookup/vkcts_lookup.sqlite3
external/vulkancts/wiki/case_lookup/site/mappings.json
```

前两类 SQLite 文件被 `.gitignore` 忽略；只有 `site/mappings.json` 是需要 review 和 commit 的最终数据。

构建流程：

1. 从 canonical English Level-3 页面的 `## Registration Hierarchy` 收集 ownership evidence；
2. 用 mustpass 定义 executable path universe，并验证 full coverage；
3. 应用有 source/mustpass 依据的 category projections；
4. 独立写入各 category DB；
5. 验证并合并 final SQLite DB；
6. `build_helper/export.py` 验证 final DB，原子写入 deterministic、可 review 的 `site/mappings.json`；
7. 检查 build summary 和 JSON diff，必要时修复页面/helper 后重新构建。

只构建选中的 category intermediate DB：

```bash
python3 external/vulkancts/wiki/case_lookup/build.py \
  --mode categories --categories api pipeline image
```

合并已有 category DB 并更新 runtime JSON：

```bash
python3 external/vulkancts/wiki/case_lookup/build.py \
  --mode merge --categories api pipeline image
```

可覆盖默认路径：

```bash
python3 external/vulkancts/wiki/case_lookup/build.py \
  --wiki-base-url https://example.test/-/wikis \
  --categories rasterization \
  --db-dir /tmp/case_lookup-db \
  --database /tmp/case_lookup.sqlite3 \
  --json /tmp/mappings.json
```

Category/final SQLite 写入和 runtime JSON 写入都使用临时文件加原子替换。失败不会用部分结果覆盖原 artifact。

## Ownership 构建模型

构建采用 Wiki-evidence-first 模型：

1. canonical English Level-3 页面的 `## Registration Hierarchy` 是 page ownership 的 primary evidence；
2. builder 将 tree root 或 `root.direct_child` 转换成 exact prefix-to-page mapping；
3. `vk-default` mustpass files 定义真实 executable path universe，并用于 namespace discovery 和 full coverage validation；
4. `build_helper/category_handlers.py` 只处理有 source/mustpass 依据的 construction variants、generated families 和 shared category namespaces；
5. explicit alias 和 generic anchor 不能让正式 build 通过；缺少 exact evidence 或合法 projection 时 build hard-fail；
6. runtime JSON 只保存已经验证的真实 registration prefixes，不保存 runtime alias 或 suffix fallback。

完整 page-tree contract 和 helper 边界见：

```text
build_helper/tree_and_handler_spec.md
```

## Runtime lookup

### CLI

```bash
python3 external/vulkancts/wiki/case_lookup/lookup.py lookup \
  dEQP-VK.api.buffer.basic.max_size
```

`lookup.py` 默认读取：

```text
external/vulkancts/wiki/case_lookup/site/mappings.json
```

它与浏览器执行相同的 component-boundary longest-prefix lookup。

### 本地静态页面

```bash
python3 -m http.server 8766 \
  --directory external/vulkancts/wiki/case_lookup/site
```

浏览器打开：

```text
http://127.0.0.1:8766/
```

HTTP server 只提供两个 tracked files：

```text
GET /index.html
GET /mappings.json
```

浏览器加载 JSON 后，所有查询都在 JavaScript 中完成，不向 backend 发送 lookup request。这个 runtime path 与 GitLab Pages 完全相同。

## GitLab Pages

CI 直接发布 tracked `site/`：

```yaml
create-pages:
  tags:
    - case-lookup-shell
  pages:
    publish: external/vulkancts/wiki/case_lookup/site
  rules:
    - if: '$CI_COMMIT_BRANCH == "case_lookup_tool"'
  script:
    - test -s external/vulkancts/wiki/case_lookup/site/index.html
    - test -s external/vulkancts/wiki/case_lookup/site/mappings.json
```

`script` 只检查两个文件存在且非空；它不 build、不 export、不改变部署内容。GitLab Pages 发布的就是本地 E2E 使用、code review 看到的同一份 `site/`。

准备 merge 到 default branch 时，将 rule 改为：

```yaml
rules:
  - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## 验证

单元与集成测试：

```bash
python3 -m unittest discover \
  -s external/vulkancts/wiki/case_lookup/tests \
  -p 'test_*.py' -v
```

Mustpass runtime coverage：

```bash
python3 external/vulkancts/wiki/case_lookup/lookup.py validate \
  external/vulkancts/mustpass/main/vk-default/api.txt
```

纯静态浏览器 E2E：

```bash
python3 -m http.server 8766 \
  --directory external/vulkancts/wiki/case_lookup/site

python3 external/vulkancts/wiki/case_lookup/tests/e2e_test.py \
  --url http://127.0.0.1:8766/
```

E2E 使用临时 Chromium profile，在同一个页面中执行成功 lookup、无匹配和非法输入检查，然后关闭页面和浏览器。

## 目录结构

```text
case_lookup/
├── build.py
├── build_helper/
│   ├── category_inputs.py
│   ├── category_handlers.py
│   ├── ownership_aliases.py
│   ├── export.py                   # final SQLite → tracked runtime JSON
│   └── tree_and_handler_spec.md
├── lookup.py                       # JSON-backed CLI lookup/coverage
├── site/
│   ├── index.html                  # 唯一前端，tracked
│   └── mappings.json               # 唯一 runtime data，tracked/generated
├── db/                             # ignored category intermediates
├── vkcts_lookup.sqlite3            # ignored final SQLite intermediate
└── tests/
    ├── test_builder.py
    ├── test_export.py
    ├── test_lookup.py
    └── e2e_test.py
```

## Artifact ownership

提交：

```text
case_lookup/site/index.html
case_lookup/site/mappings.json
```

不提交：

```text
case_lookup/db/
case_lookup/vkcts_lookup.sqlite3
case_lookup/**/__pycache__/
```

任何影响 mapping 的 Wiki tree、mustpass input 或 build helper 修改，都应在本地完整 build、审查诊断与 `site/mappings.json` diff，并在同一个变更中提交更新后的 JSON。
