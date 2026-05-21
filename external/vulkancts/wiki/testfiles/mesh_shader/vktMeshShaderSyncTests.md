# vktMeshShaderSyncTests

## Overview

NV synchronization tests cover dependencies between host, transfer, task, mesh, and fragment stages.

## File Role

This is a registered mesh-shader test source file. Its registered group names and direct children are documented from the inspected registration code in [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).

## Source Links

| Item | Link |
|------|------|
| Source file | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp) |
| Registration code | [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332) |

## Registration Hierarchy

```text
mesh_shader.nv.synchronization
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
└── mesh_to_host
```

## Test Families

### host_to_task — Registered child

The `host_to_task` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).
### host_to_mesh — Registered child

The `host_to_mesh` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).
### transfer_to_task — Registered child

The `transfer_to_task` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).
### transfer_to_mesh — Registered child

The `transfer_to_mesh` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).
### task_to_mesh — Registered child

The `task_to_mesh` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).
### task_to_frag — Registered child

The `task_to_frag` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).
### task_to_transfer — Registered child

The `task_to_transfer` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).
### task_to_host — Registered child

The `task_to_host` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).
### mesh_to_frag — Registered child

The `mesh_to_frag` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).
### mesh_to_transfer — Registered child

The `mesh_to_transfer` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).
### mesh_to_host — Registered child

The `mesh_to_host` child is documented from the registration tree for `mesh_shader.nv.synchronization` and from the implementation source [vktMeshShaderSyncTests.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderSyncTests.cpp#L1332).

## Parameter Dimensions

Dimensions include stage pair, resource type, barrier type, and write/read access pair.

## Support and Feature Requirements

Mesh shader tests require the corresponding extension and requested task/mesh feature bits through the shared helpers in [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111) and [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126). Additional per-file gates are described where observed in the implementation.

## Verification Methods

Verification is implemented by the individual cases or function cases in this source file; this page does not claim one common verification method for every child.

## Test Principles

The file contributes one focused portion of the `mesh_shader` category: it registers tests under the path shown above and varies the directly registered children through code-visible parameter arrays, loops, or explicit `addChild` calls.

## Notes and Uncertainties

This page is evidence-first and limited to source under `external/vulkancts/modules/vulkan/mesh_shader/` plus the general API test-plan context. Utility-only files are not given Level-3 pages because they do not register tests.
