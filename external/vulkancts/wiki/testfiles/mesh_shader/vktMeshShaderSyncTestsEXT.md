# vktMeshShaderSyncTestsEXT

## Overview

EXT synchronization expands the NV matrix and adds `other` secondary-command-buffer coverage.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp) |
| Registration code | [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772) |

## Registration Hierarchy

```text
mesh_shader.ext.synchronization
├── host_to_task
├── host_to_mesh
├── transfer_to_task
├── transfer_to_mesh
├── task_to_mesh
├── task_to_frag
├── task_to_transfer
├── task_to_host
├── mesh_to_frag
├── mesh_to_transfer
├── mesh_to_host
├── mesh_to_task
├── frag_to_task
├── frag_to_mesh
└── other
```

## Test Families

### host_to_task — Registered child

The `host_to_task` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### host_to_mesh — Registered child

The `host_to_mesh` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### transfer_to_task — Registered child

The `transfer_to_task` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### transfer_to_mesh — Registered child

The `transfer_to_mesh` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### task_to_mesh — Registered child

The `task_to_mesh` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### task_to_frag — Registered child

The `task_to_frag` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### task_to_transfer — Registered child

The `task_to_transfer` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### task_to_host — Registered child

The `task_to_host` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### mesh_to_frag — Registered child

The `mesh_to_frag` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### mesh_to_transfer — Registered child

The `mesh_to_transfer` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### mesh_to_host — Registered child

The `mesh_to_host` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### mesh_to_task — Registered child

The `mesh_to_task` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### frag_to_task — Registered child

The `frag_to_task` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### frag_to_mesh — Registered child

The `frag_to_mesh` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).
### other — Registered child

The `other` child is documented from the registration tree for `mesh_shader.ext.synchronization` and from the implementation source [vktMeshShaderSyncTestsEXT.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTestsEXT.cpp#L1772).

## Parameter Dimensions

Dimensions include stage pair, resource type, barrier type including subpass dependency, access pair, and the `barrier_across_secondary` case under `other`.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
