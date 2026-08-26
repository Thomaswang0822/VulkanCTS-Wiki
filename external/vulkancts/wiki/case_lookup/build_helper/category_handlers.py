"""Category-specific build-time registration path handling.

Generic ownership extraction remains in ``build.py``. This module owns only
categories whose mustpass paths or Wiki page locations need special handling.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import TypeVar

OwnerValue = TypeVar("OwnerValue")
PIPELINE_CONSTRUCTION_VARIANTS = frozenset(
    {
        "pipeline_library",
        "fast_linked_library",
        "shader_object_unlinked_spirv",
        "shader_object_unlinked_binary",
        "shader_object_linked_spirv",
        "shader_object_linked_binary",
    }
)
PIPELINE_CANONICAL_FAMILIES = {
    "multisample_with_fragment_shading_rate": "multisample",
}

DYNAMIC_STATE_CONSTRUCTION_VARIANTS = frozenset(
    {
        "pipeline_library",
        "fast_linked_library",
        "shader_object_unlinked_spirv",
        "shader_object_unlinked_binary",
        "shader_object_linked_spirv",
        "shader_object_linked_binary",
    }
)
COMPUTE_CONSTRUCTION_VARIANTS = frozenset(
    {"shader_object_spirv", "shader_object_binary"}
)
DRAW_DYNAMIC_RENDERING_MODES = frozenset(
    {
        "primary_cmd_buff",
        "partial_secondary_cmd_buff",
        "complete_secondary_cmd_buff",
        "nested_partial_secondary_cmd_buff",
        "nested_complete_secondary_cmd_buff",
    }
)
WSI_PLATFORM_VARIANTS = frozenset(
    {"android", "direct", "direct_drm", "metal", "wayland", "win32", "xcb", "xlib"}
)
SPARSE_DEVICE_GROUP_FAMILIES = {
    "device_group_image_sparse_memory_aliasing": "image_sparse_memory_aliasing",
    "device_group_mipmap_sparse_residency": "mipmap_sparse_residency",
}


# synchronization2 pages are intentionally shared with the synchronization
# category. The two categories still have independent mustpass universes.
SHARED_PAGE_CATEGORY = {"synchronization2": "synchronization"}

GENERATED_FAMILY_ROOTS = {
    "api": (
        (
            "dEQP-VK.api.command_buffers.indirect_compute_dispatch_offsets_0_0",
            "dEQP-VK.api.command_buffers",
        ),
        (
            "dEQP-VK.api.ds_color_copy.d16_unorm_r16_sfloat_depth_level0_to_level0",
            "dEQP-VK.api.ds_color_copy",
        ),
        (
            "dEQP-VK.api.maintenance3_check.support_count_combined_image_sampler",
            "dEQP-VK.api.maintenance3_check",
        ),
        (
            "dEQP-VK.api.copy_and_blit.core.buffer_to_buffer_with_offset.0_0",
            "dEQP-VK.api.copy_and_blit.core.buffer_to_buffer_with_offset",
        ),
    ),
    "synchronization2": (
        (
            "dEQP-VK.synchronization2.internally_synchronized_queues.small2_small2",
            "dEQP-VK.synchronization2.internally_synchronized_queues",
        ),
        (
            "dEQP-VK.synchronization2.none_stage.color_attachment_to_general",
            "dEQP-VK.synchronization2.none_stage",
        ),
    ),
    "dynamic_state": (
        (
            "dEQP-VK.dynamic_state.monolithic.ds_state.depth_bounds_1",
            "dEQP-VK.dynamic_state.monolithic.ds_state",
        ),
        (
            "dEQP-VK.dynamic_state.monolithic.rs_state.depth_bias",
            "dEQP-VK.dynamic_state.monolithic.rs_state",
        ),
    ),
    "query_pool": (
        (
            "dEQP-VK.query_pool.occlusion_query.basic_conservative",
            "dEQP-VK.query_pool.occlusion_query",
        ),
    ),
    "draw": (
        (
            "dEQP-VK.draw.renderpass.depth_clamp.d16_unorm",
            "dEQP-VK.draw.renderpass.depth_clamp",
        ),
        (
            "dEQP-VK.draw.renderpass.discard_rectangles.inclusive_rect_1",
            "dEQP-VK.draw.renderpass.discard_rectangles",
        ),
        (
            "dEQP-VK.draw.renderpass.shader_layer.vertex_shader_1",
            "dEQP-VK.draw.renderpass.shader_layer",
        ),
        (
            "dEQP-VK.draw.renderpass.shader_viewport_index.vertex_shader_1",
            "dEQP-VK.draw.renderpass.shader_viewport_index",
        ),
    ),
    "tessellation": (
        (
            "dEQP-VK.tessellation.misc_draw.fill_cover_quads_equal_spacing_draw",
            "dEQP-VK.tessellation.misc_draw",
        ),
    ),
    "wsi": (
        (
            "dEQP-VK.wsi.headless.incremental_present.scale_none",
            "dEQP-VK.wsi.headless.incremental_present",
        ),
    ),
}

API_COPY_PARENT_VARIANTS = frozenset(
    {"core", "dedicated_allocation", "copy_commands2", "device_address", "sparse"}
)
API_COPY_CANONICAL_FAMILIES = {
    "image_to_buffer_transfer_queue": "image_to_buffer",
    "image_to_buffer_compute_queue": "image_to_buffer",
    "image_to_buffer_general_layout": "image_to_buffer",
    "image_to_buffer_indirect": "image_to_buffer",
    "image_to_buffer_indirect_transfer_queue": "image_to_buffer",
    "image_to_buffer_indirect_compute_queue": "image_to_buffer",
    "image_to_image_general_layout": "image_to_image",
    "image_to_image_transfer_queue": "image_to_image",
    "image_to_image_transfer_queue_secondary": "image_to_image",
    "image_to_image_transfer_sparse": "image_to_image",
}


def wiki_page_category(category: str) -> str:
    """Return the testfiles directory containing pages for ``category``."""
    return SHARED_PAGE_CATEGORY.get(category, category)


def allowed_root_categories(category: str) -> frozenset[str]:
    """Return category prefixes accepted in a page's hierarchy roots."""
    page_category = wiki_page_category(category)
    if page_category == "synchronization":
        return frozenset({"synchronization", "synchronization2"})
    return frozenset({page_category})


def tree_belongs_to_category(root: str, category: str) -> bool:
    """Select the requested side of the shared synchronization page set."""
    return root == category or root.startswith(f"{category}.")


def canonicalize_mustpass_path(path: str, category: str) -> str:
    """Map construction-variant paths to the canonical evidence namespace."""
    parts = path.split(".")
    if category == "pipeline" and len(parts) > 2:
        if parts[2] in PIPELINE_CONSTRUCTION_VARIANTS:
            parts[2] = "monolithic"
        if len(parts) > 3:
            parts[3] = PIPELINE_CANONICAL_FAMILIES.get(parts[3], parts[3])
        return ".".join(parts)
    if category == "dynamic_state" and len(parts) > 2:
        if parts[2] in DYNAMIC_STATE_CONSTRUCTION_VARIANTS:
            parts[2] = "monolithic"
        return ".".join(parts)
    if category == "compute" and len(parts) > 2:
        if parts[2] in COMPUTE_CONSTRUCTION_VARIANTS:
            parts[2] = "pipeline"
        return ".".join(parts)
    if category == "image_processing" and len(parts) > 3:
        if parts[2] == "compute":
            parts[2:3] = ["graphics", "monolithic"]
        elif parts[2] == "graphics" and parts[3] in {"fast_lib", "shader_objects"}:
            parts[3] = "monolithic"
        return ".".join(parts)
    if category == "wsi" and len(parts) > 2:
        if len(parts) > 3 and parts[3] == "surface" and (
            parts[2] in WSI_PLATFORM_VARIANTS or parts[2] == "headless"
        ):
            parts[2] = "xcb"
        elif parts[2] in WSI_PLATFORM_VARIANTS:
            parts[2] = "headless"
        return ".".join(parts)
    if category == "draw" and len(parts) > 3:
        if parts[2] == "dynamic_rendering" and parts[3] in DRAW_DYNAMIC_RENDERING_MODES:
            parts[2:4] = ["renderpass"]
        return ".".join(parts)
    if category == "sparse_resources" and len(parts) > 2:
        parts[2] = SPARSE_DEVICE_GROUP_FAMILIES.get(parts[2], parts[2])
        return ".".join(parts)
    return path


def project_category_mappings(
    mappings: Mapping[str, OwnerValue], paths: Iterable[str], category: str
) -> dict[str, OwnerValue]:
    """Return explicit construction-variant and generated-family projections."""
    projected: dict[str, OwnerValue] = {}
    generated_rules = GENERATED_FAMILY_ROOTS.get(category, ())
    for path in paths:
        if category == "api":
            actual_parts = path.split(".")
            if (
                len(actual_parts) > 4
                and actual_parts[:3] == ["dEQP-VK", "api", "copy_and_blit"]
                and actual_parts[3] in API_COPY_PARENT_VARIANTS
            ):
                canonical_parts = list(actual_parts)
                canonical_parts[3] = "core"
                canonical_parts[4] = API_COPY_CANONICAL_FAMILIES.get(
                    canonical_parts[4], canonical_parts[4]
                )
                for end in range(5, len(canonical_parts) + 1):
                    owner = mappings.get(".".join(canonical_parts[:end]))
                    if owner is not None:
                        projected[".".join(actual_parts[:end])] = owner

        elif category in {
            "pipeline",
            "dynamic_state",
            "compute",
            "image_processing",
            "wsi",
            "draw",
            "sparse_resources",
        }:
            canonical_parts = canonicalize_mustpass_path(path, category).split(".")
            actual_parts = path.split(".")
            component_delta = len(actual_parts) - len(canonical_parts)
            for end in range(3, len(canonical_parts) + 1):
                owner = mappings.get(".".join(canonical_parts[:end]))
                if owner is not None:
                    actual_end = end + component_delta
                    if actual_end >= 3:
                        projected[".".join(actual_parts[:actual_end])] = owner
            if category == "wsi" and len(actual_parts) > 3:
                if actual_parts[2] == "headless" and actual_parts[3] == "surface":
                    xcb_root = "dEQP-VK.wsi.xcb.surface"
                    owner = mappings.get(xcb_root)
                    if owner is not None:
                        projected["dEQP-VK.wsi.headless.surface"] = owner
                else:
                    headless_root = ".".join(
                        ["dEQP-VK", "wsi", "headless", actual_parts[3]]
                    )
                    owner = mappings.get(headless_root)
                    if owner is not None:
                        projected[".".join(actual_parts[:4])] = owner

        canonical_path = canonicalize_mustpass_path(path, category)
        canonical_parts = canonical_path.split(".")
        actual_parts = path.split(".")
        component_delta = len(actual_parts) - len(canonical_parts)
        for representative, root in generated_rules:
            if canonical_path.startswith(f"{root}."):
                owner = mappings.get(representative)
                if owner is not None:
                    root_end = len(root.split(".")) + component_delta
                    projected[".".join(actual_parts[:root_end])] = owner
    return projected


def level3_pages_dir(repo_root: Path, category: str) -> Path:
    """Return the canonical Level-3 page directory for a build category."""
    return repo_root / "external/vulkancts/wiki/testfiles" / wiki_page_category(category)


def allows_multiple_hierarchy_snippets(category: str) -> bool:
    """Return whether a category uses the shared synchronization exception."""
    return wiki_page_category(category) == "synchronization"



