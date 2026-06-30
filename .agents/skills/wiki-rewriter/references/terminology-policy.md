# Terminology Policy

Use exact mustpass and registration path names as authoritative identifiers.

## Hierarchy Terms

Use `test category` for Level-2 path components, such as `memory_model`.

Use `test family` for Level-3 path components/page scopes, such as `shared`, `message_passing`, or `padding`.

Use `intermediate node` for deeper path components below a test family, such as `16bit` or `arrays_of_arrays` in `dEQP-VK.memory_model.shared.16bit.arrays_of_arrays.3`.

Use `test case` or `test case leaf` for final executable leaves, such as `3` in `dEQP-VK.memory_model.shared.16bit.arrays_of_arrays.3`.

## Terms To Avoid

Do not call a test category a `node`.

Do not call a test family a `node`.

Avoid `below-family node`; use `intermediate node` instead.

Avoid `test group` in authored wiki prose unless explicitly quoting or explaining CTS internal/framework terminology.

Avoid `subgroup` as a wiki hierarchy term because it conflicts with Vulkan subgroup terminology.

## Technical Terms

Preserve exact mustpass/registration path identifiers and technical Vulkan/GLSL terms, including `subgroup`, `workgroup`, and `gl_SubgroupInvocationID` when they describe graphics or shader behavior.

Do not normalize or paraphrase registered path tokens when they are being used as identifiers.
