"""Explicit build-time ownership aliases and exclusions."""


OWNERSHIP_ALIASES: dict[str, dict[str, str]] = {
}


# Gateway pages may describe delegated registration-only branches. Exclude only
# that duplicated evidence; the owning page remains authoritative.
OWNERSHIP_EXCLUSIONS: dict[str, dict[str, frozenset[str]]] = {
    "info": {
        "InfoTests": frozenset(
            {
                "info.physical_devices",
                "info.physical_device_groups",
                "info.instance_layers",
                "info.instance_extensions",
                "info.instance_extension_dependencies",
                "info.instance_extension_device_functions",
                "info.device_features",
                "info.device_properties",
                "info.device_queue_family_properties",
                "info.device_memory_properties",
                "info.device_layers",
                "info.device_extensions",
                "info.device_extension_dependencies",
                "info.device_no_khx_extensions",
                "info.device_memory_budget",
                "info.device_mandatory_features",
                "info.device_group_peer_memory_features",
            }
        )
    },
    "spirv_assembly": {
        "InstructionTests": frozenset(
            {"spirv_assembly.instruction.maint9_vectorization"}
        )
    },
    "pipeline": {
        "Multisample": frozenset(
            {
                "pipeline.monolithic.multisample.sampled_image",
                "pipeline.monolithic.multisample.storage_image",
                "pipeline.monolithic.multisample.standardsampleposition",
                "pipeline.monolithic.multisample.samples_mapping_order",
                "pipeline.monolithic.multisample.3d",
            }
        ),
        "NoQueues": frozenset({"pipeline.no_queues.pipeline_binary"}),
    },
}
