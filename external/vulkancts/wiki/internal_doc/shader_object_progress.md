## shader_object progress

## Scope
- Category: `shader_object`
- Test-plan search: no `shader_object`, `shader object`, or `VK_EXT_shader_object` matches found in `doc/testspecs/VK/apitests.adoc`.
- `performance` branch is explicitly excluded from mustpass by `excluded-tests.txt` (glob `dEQP-VK.shader_object.performance.*`).

## Root evidence
- Root file: `external/vulkancts/modules/vulkan/shader_object/vktShaderObjectTests.cpp`
- Root `createTests()` creates the category group from caller-provided name and directly adds ten children.
- Root includes ten branch headers plus root/common include; `CMakeLists.txt` also lists `vktShaderObjectCreateUtil.*` as utility-only files.

## Header/source index and verified groups

| Header/source index | Root registered directly | Verified group name | Level-3 status | Notes |
|---|---:|---|---|---|
| `vktShaderObjectTests.hpp` / `vktShaderObjectTests.cpp` | root | `shader_object` via caller-provided category name | reviewed | Dispatcher/root file. |
| `vktShaderObjectApiTests.hpp` / `vktShaderObjectApiTests.cpp` | yes | `api` | reviewed | Verified from `TestCaseGroup(testCtx, "api")`. |
| `vktShaderObjectCreateTests.hpp` / `vktShaderObjectCreateTests.cpp` | yes | `create` | reviewed | Verified from `TestCaseGroup(testCtx, "create")`. |
| `vktShaderObjectLinkTests.hpp` / `vktShaderObjectLinkTests.cpp` | yes | `link` | reviewed | Verified from `TestCaseGroup(testCtx, "link")`. |
| `vktShaderObjectTessellationTests.hpp` / `vktShaderObjectTessellationTests.cpp` | yes | `tessellation` | reviewed | Verified from `TestCaseGroup(testCtx, "tessellation")`. |
| `vktShaderObjectBinaryTests.hpp` / `vktShaderObjectBinaryTests.cpp` | yes | `binary` | reviewed | Verified from `TestCaseGroup(testCtx, "binary")`. |
| `vktShaderObjectPipelineInteractionTests.hpp` / `vktShaderObjectPipelineInteractionTests.cpp` | yes | `pipeline_interaction` | reviewed | Verified from `TestCaseGroup(testCtx, "pipeline_interaction")`. |
| `vktShaderObjectBindingTests.hpp` / `vktShaderObjectBindingTests.cpp` | yes | `binding` | reviewed | Verified from `TestCaseGroup(testCtx, "binding")`. |
| `vktShaderObjectPerformanceTests.hpp` / `vktShaderObjectPerformanceTests.cpp` | yes | `performance` | reviewed | Verified from `TestCaseGroup(testCtx, "performance")`. Excluded from mustpass. |
| `vktShaderObjectRenderingTests.hpp` / `vktShaderObjectRenderingTests.cpp` | yes | `rendering` | reviewed | Verified from `TestCaseGroup(testCtx, "rendering")`. |
| `vktShaderObjectMiscTests.hpp` / `vktShaderObjectMiscTests.cpp` | yes | `misc` | reviewed | Verified from `TestCaseGroup(testCtx, "misc")`. |
| `vktShaderObjectCreateUtil.hpp` / `vktShaderObjectCreateUtil.cpp` | no | n/a | no page | Utility-only per CMake/source usage. |

## Verified root group names
- `api`
- `create`
- `link`
- `tessellation`
- `binary`
- `pipeline_interaction`
- `binding`
- `performance` (excluded from mustpass)
- `rendering`
- `misc`

## Consistency review completed
- [x] All Level-3 docs have consistent section ordering and formatting
- [x] All source-code links use GitHub `#L` fragment syntax (no colon-style references)
- [x] All implementation docs that include `vktShaderObjectCreateUtil.hpp` now list it in Source Code section
- [x] All docs now have consistent `CMakeLists.txt#L6-L44` reference in Related Inspected Files
- [x] `shader_object.api.scissor_exclusive` added to API doc verifier extraction paths
- [x] `shader_object.performance` FAIL resolved: removed backtick-wrapped path from root doc evidence, added excluded-tests.txt reference
- [x] Registration path verifier: all 42 paths OK (exit code 0)
- [x] Wiki link validator: reports broken links for source-code paths due to known validator limitation (same issue affects all completed categories); source files verified to exist at correct paths

## Remaining work
- Create Level-2 category doc `categories/shader_object.md`
- Update `README.md` status
- Remove this progress tracker after category is complete
