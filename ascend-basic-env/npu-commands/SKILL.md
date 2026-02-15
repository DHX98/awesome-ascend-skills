---
name: npu-commands
description: Ascend NPU command-line utilities and hardware management. Use for npu-smi usage, device management, monitoring, and basic hardware operations. Routes to specialized sub-skills for query, configuration, upgrade, virtualization, and certificate management.
---

# npu-smi Command Reference

Master skill for npu-smi command-line utilities. This skill routes to specialized sub-skills based on command type.

## Quick Reference

```bash
# List all devices
npu-smi info -l

# Check device health
npu-smi info -t health -i <id>

# View chip details
npu-smi info -t npu -i <id> -c <chip_id>

# Monitor metrics
npu-smi info -t temp -i <id> -c <chip_id>
npu-smi info -t power -i <id> -c <chip_id>
npu-smi info -t memory -i <id> -c <chip_id>
```

## Prerequisites

- npu-smi tool installed
- Root permissions (most configuration/upgrade commands)
- Runtime user group permissions (some query commands)

## Parameter Reference

| Parameter | Description | How to Get |
|-----------|-------------|------------|
| `id` | Device ID | `npu-smi info -l` |
| `chip_id` | Chip ID | `npu-smi info -m` |
| `vnpu_id` | vNPU ID | Auto-assigned or specified |
| `phy_id` | Physical chip ID | `ls /dev/davinci*` |

## Sub-Skills

| Command Type | Sub-Skill | Use When |
|--------------|-----------|----------|
| **Query Commands** | [npu-smi-query/](npu-smi-query/SKILL.md) | Retrieving device info, monitoring status |
| **Configuration** | [npu-smi-config/](npu-smi-config/SKILL.md) | Setting thresholds, modes, ECC |
| **Firmware Upgrade** | [npu-smi-upgrade/](npu-smi-upgrade/SKILL.md) | Upgrading MCU, bootloader, VRD |
| **Virtualization** | [npu-smi-virtualization/](npu-smi-virtualization/SKILL.md) | Managing vNPU, AVI mode |
| **Certificates** | [npu-smi-certificates/](npu-smi-certificates/SKILL.md) | TLS certificates, CSR |

## Quick Navigation

### Query Operations
→ [npu-smi-query/](npu-smi-query/SKILL.md)
- Device listing and health checks
- Temperature, power, memory monitoring
- Process and utilization queries
- ECC error checking

### Configuration Operations
→ [npu-smi-config/](npu-smi-config/SKILL.md)
- Temperature thresholds
- Power limits
- ECC mode
- Fan control
- MAC addresses
- Clear operations

### Firmware Management
→ [npu-smi-upgrade/](npu-smi-upgrade/SKILL.md)
- Version queries
- Firmware upgrades
- Upgrade status monitoring
- Activation and restart

### Virtualization
→ [npu-smi-virtualization/](npu-smi-upgrade/SKILL.md)
- AVI mode configuration
- vNPU creation/destruction
- Template management
- Resource allocation

### Security
→ [npu-smi-certificates/](npu-smi-certificates/SKILL.md)
- CSR generation
- TLS certificate import
- Expiration monitoring
- Certificate validation

## Supported Platforms

- Atlas 200I DK A2 Developer Kit
- Atlas 500 A2 Smart Station
- Atlas 200I A2 Acceleration Module (RC/EP scenarios)

## Important Notes

- Most configuration/upgrade commands require **root permissions**
- Device ID from `npu-smi info -l`
- Chip ID from `npu-smi info -m`
- Command availability varies by hardware platform
- MAC address and boot medium changes require restart
- MCU firmware requires restart after activation
- VRD requires power cycle (30+ seconds off) to activate
- Concurrent MCU firmware upgrades not supported

## Official Documentation

- **npu-smi Reference**: https://www.hiascend.com/document/detail/zh/canncommercial/81RC1/envdeployment/instg/instg_0045.html
- **hccn_tool**: https://www.hiascend.com/document/detail/zh/canncommercial/81RC1/envdeployment/instg/instg_0052.html
