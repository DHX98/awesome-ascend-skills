---
name: npu-smi-query
description: npu-smi query commands for Huawei Ascend NPU. Use when retrieving device information, monitoring status, checking health, temperature, power, memory, and processes. Covers all npu-smi info subcommands.
---

# npu-smi Query Commands

Query device status, health, and metrics using `npu-smi info`.

## Quick Reference

```bash
# List all devices
npu-smi info -l

# Check device health
npu-smi info -t health -i <id>

# View device details
npu-smi info -t board -i <id>
npu-smi info -t npu -i <id> -c <chip_id>

# Monitor metrics
npu-smi info -t temp -i <id> -c <chip_id>
npu-smi info -t power -i <id> -c <chip_id>
npu-smi info -t memory -i <id> -c <chip_id>
```

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| npu-smi | Tool installed and in PATH |
| Permissions | Runtime user group for queries |
| Device IDs | Get from `npu-smi info -l` |
| Chip IDs | Get from `npu-smi info -m` |

## Commands

### List Devices

List all NPU devices in the system.

```bash
npu-smi info -l
```

**Output Fields:**
| Field | Description | Example |
|-------|-------------|---------|
| NPU ID | Device identifier | 0, 1, 2... |
| Name | Device name | Ascend910B |

**Example:**
```bash
$ npu-smi info -l
+-----------+-----------+
| NPU ID    | Name      |
+-----------+-----------+
| 0         | 910B      |
| 1         | 910B      |
+-----------+-----------+
```

### Query Device Health

Check health status of a specific NPU.

```bash
npu-smi info -t health -i <id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID from `info -l` |

**Output Fields:**
| Field | Description | Values |
|-------|-------------|--------|
| Healthy | Health status | OK, Warning, Error |

**Example:**
```bash
$ npu-smi info -t health -i 0
Device 0:
    Healthy      : OK
```

### Query Board Information

View detailed board info including firmware version.

```bash
npu-smi info -t board -i <id>
```

**Output Fields:**
| Field | Description |
|-------|-------------|
| NPU ID | Device identifier |
| Name | Board name |
| Health | Health status |
| Power Usage | Current power draw |
| Temperature | Board temperature |
| Firmware Version | Current firmware |
| Software Version | Driver version |

### Query NPU/Chip Details

View chip-level details.

```bash
npu-smi info -t npu -i <id> -c <chip_id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID |
| chip_id | integer | Yes | Chip ID from `info -m` |

**Output Fields:**
| Field | Description |
|-------|-------------|
| Chip ID | Chip identifier |
| Name | Chip name |
| Health | Health status |
| Power Usage | Power consumption |
| Temperature | Chip temperature |
| Memory Usage | Memory utilization |
| AI Core Usage | AI Core utilization |

### List All Chips

Query summary of all chips.

```bash
npu-smi info -m
```

**Output Fields:**
| Field | Description |
|-------|-------------|
| NPU ID | Parent device |
| Chip ID | Chip identifier |
| Name | Chip name |
| Health | Health status |

### Query Temperature

```bash
npu-smi info -t temp -i <id> -c <chip_id>
```

**Output:**
- NPU Temperature (°C)
- AI Core Temperature (°C)

**Example:**
```bash
$ npu-smi info -t temp -i 0 -c 0
Device 0, Chip 0:
    NPU Temperature     : 45 C
    AI Core Temperature : 48 C
```

### Query Power

```bash
npu-smi info -t power -i <id> -c <chip_id>
```

**Output:**
- Power Usage (W)
- Power Limit (W)

**Example:**
```bash
$ npu-smi info -t power -i 0 -c 0
Device 0, Chip 0:
    Power Usage : 67 W
    Power Limit : 310 W
```

### Query Memory

```bash
npu-smi info -t memory -i <id> -c <chip_id>
```

**Output:**
- Memory Usage (MB)
- Memory Total (MB)
- Memory Usage Rate (%)

**Example:**
```bash
$ npu-smi info -t memory -i 0 -c 0
Device 0, Chip 0:
    Memory Usage      : 1024 MB
    Memory Total      : 32768 MB
    Memory Usage Rate : 3.1%
```

### Query Processes

View running processes on NPU.

```bash
npu-smi info proc -i <id> -c <chip_id>
```

**Note:** Not supported on all platforms (e.g., Ascend 910B series).

**Output Fields:**
| Field | Description |
|-------|-------------|
| PID | Process ID |
| Process Name | Application name |
| Memory Usage | Memory used |
| AI Core Usage | AI Core utilization |

### Query ECC Errors

```bash
npu-smi info -t ecc -i <id> -c <chip_id>
```

**Output:**
- ECC Error Count
- ECC Mode (Enabled/Disabled)

### Query Utilization

```bash
npu-smi info -t usages -i <id> -c <chip_id>
```

**Output:**
- AI Core Usage (%)
- Memory Usage (%)
- Bandwidth Usage (%)

### Query Sensors

```bash
npu-smi info -t sensors -i <id> -c <chip_id>
```

**Output:**
- Temperature sensors
- Voltage readings
- Current readings

### Query Frequency

```bash
npu-smi info -t freq -i <id> -c <chip_id>
```

**Output:**
- AI Core Frequency (MHz)
- Memory Frequency (MHz)

### Query P2P Status

```bash
npu-smi info -t p2p -i <id> -c <chip_id>
```

**Output:**
- P2P Status
- P2P Mode

### Query PCIe Info

```bash
npu-smi info -t pcie-info -i <id> -c <chip_id>
```

**Output:**
- PCIe Speed (GT/s)
- PCIe Width (x16, x8, etc.)

### Query Product Info

```bash
npu-smi info -t product -i <id> -c <chip_id>
```

**Output:**
- Product Name
- Product Serial Number

## Examples

### Basic Monitoring Script

```bash
#!/bin/bash

# Get all devices
npus=$(npu-smi info -l | grep -E '^\|\s+[0-9]+' | awk '{print $2}')

for npu in $npus; do
    echo "=== NPU $npu ==="
    
    # Health
    npu-smi info -t health -i $npu
    
    # Get all chips for this NPU
    chips=$(npu-smi info -m | grep "^| $npu " | awk '{print $4}')
    
    for chip in $chips; do
        echo "--- Chip $chip ---"
        npu-smi info -t temp -i $npu -c $chip
        npu-smi info -t power -i $npu -c $chip
        npu-smi info -t memory -i $npu -c $chip
    done
    echo ""
done
```

### Check All Devices Health

```bash
# Quick health check for all devices
npu-smi info -l | grep -E '^\|\s+[0-9]+' | while read line; do
    npu=$(echo $line | awk '{print $2}')
    health=$(npu-smi info -t health -i $npu | grep Healthy | awk '{print $2}')
    echo "NPU $npu: $health"
done
```

## Parameter Reference

| Parameter | Description | Range |
|-----------|-------------|-------|
| `id` | Device ID | 0-N |
| `chip_id` | Chip ID | 0-M |
| `temp` | Temperature query | - |
| `power` | Power query | - |
| `memory` | Memory query | - |
| `health` | Health status | - |
| `board` | Board info | - |
| `npu` | Chip details | - |
| `ecc` | ECC errors | - |
| `usages` | Utilization | - |
| `sensors` | Sensor data | - |
| `freq` | Frequency | - |
| `p2p` | P2P status | - |
| `pcie-info` | PCIe info | - |
| `product` | Product info | - |

## Related Skills

- [../npu-smi-config/](npu-smi-config/SKILL.md) - Configuration commands
- [../npu-smi-upgrade/](npu-smi-upgrade/SKILL.md) - Firmware upgrade
- [../npu-smi-virtualization/](npu-smi-virtualization/SKILL.md) - vNPU management
- [../npu-smi-certificates/](npu-smi-certificates/SKILL.md) - Certificate management

## Official Documentation

- **npu-smi Reference**: https://www.hiascend.com/document/detail/zh/canncommercial/81RC1/envdeployment/instg/instg_0045.html
