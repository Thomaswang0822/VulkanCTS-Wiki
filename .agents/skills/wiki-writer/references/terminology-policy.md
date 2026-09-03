# Terminology Policy

Use exact mustpass and registration path names as authoritative identifiers.

## Hierarchy Terms

Use `test category` for Level-2 path components, such as `memory_model`.

Use `test family` for Level-3 path components/page scopes, such as `shared`, `message_passing`, or `padding`.

Use `intermediate node` for deeper path components below a test family, such as `16bit` or `arrays_of_arrays` in `dEQP-VK.memory_model.shared.16bit.arrays_of_arrays.3`.

Use `test case` or `test case leaf` for final executable leaves, such as `3` in `dEQP-VK.memory_model.shared.16bit.arrays_of_arrays.3`.

## Terms To Avoid

- Prefer `test category` over the ambiguous bare `category`; the Chinese equivalent is `测试类别`, not `类别`.
- Do not call a test category or test family a `node`.
- Use `intermediate node`, not `below-family node`.
- Avoid `test group` unless quoting or explaining CTS framework terminology.
- Avoid `subgroup` as a hierarchy term because it conflicts with Vulkan subgroup terminology.

## Technical Terms

Preserve exact mustpass/registration path identifiers and technical Vulkan/GLSL terms, including `subgroup`, `workgroup`, and `gl_SubgroupInvocationID` when they describe graphics or shader behavior.

Do not normalize or paraphrase registered path tokens when they are being used as identifiers.
