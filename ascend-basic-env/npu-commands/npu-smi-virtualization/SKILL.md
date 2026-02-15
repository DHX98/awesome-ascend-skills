---
name: npu-smi-virtualization
description: npu-smi virtualization commands for Huawei Ascend NPU. Use when managing vNPU (virtual NPU), AVI mode, and virtualization templates. Covers vNPU creation, destruction, and configuration.
---

# npu-smi Virtualization Commands

Manage NPU virtualization using `npu-smi` AVI (Ascend Virtualization Infrastructure) commands.

## Quick Reference

```bash
# Query AVI mode
npu-smi info -t vnpu-mode

# Query templates
npu-smi info -t template-info

# Create vNPU
npu-smi set -t create-vnpu -i <id> -c <chip_id> -f <template> -v <vnpu_id>

# Query vNPU info
npu-smi info -t info-vnpu -i <id> -c <chip_id>

# Destroy vNPU
npu-smi set -t destroy-vnpu -i <id> -c <chip_id> -v <vnpu_id>
```

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| npu-smi | Tool installed |
| Permissions | Root required for configuration |
| Hardware | Supported platform with AVI support |
| Templates | AVI templates configured |

## AVI Modes

| Mode | Value | Description |
|------|-------|-------------|
| Container | 0 | Container-based virtualization |
| VM | 1 | Virtual Machine mode |

## Query Commands

### Query AVI Mode

Check current AVI operation mode.

```bash
npu-smi info -t vnpu-mode
```

**Output:**
```
Mode : 0 (Container)
```

**Modes:**
| Value | Mode | Description |
|-------|------|-------------|
| 0 | Container | Container-based vNPU |
| 1 | VM | Virtual Machine vNPU |

### Query Template Info

List available AVI templates.

```bash
# Query all templates
npu-smi info -t template-info

# Query templates for specific device
npu-smi info -t template-info -i <id>
```

**Output Fields:**
| Field | Description |
|-------|-------------|
| Template Name | Template identifier |
| AI Core Num | Number of AI cores |
| Memory Size | Memory allocation |
| Other Resources | Additional resources |

**Example:**
```bash
$ npu-smi info -t template-info
+---------------+------------+-------------+
| Template Name | AI Core    | Memory(MB)  |
+---------------+------------+-------------+
| vir01         | 2          | 4096        |
| vir02         | 4          | 8192        |
| vir04         | 8          | 16384       |
+---------------+------------+-------------+
```

### Query vNPU Info

View vNPU status and configuration.

```bash
npu-smi info -t info-vnpu -i <id> -c <chip_id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID |
| chip_id | integer | Yes | Chip ID |

**Output Fields:**
| Field | Description |
|-------|-------------|
| vNPU ID | Virtual NPU identifier |
| vNPU Group ID | Group assignment |
| AI Core Num | Allocated AI cores |
| Memory Size | Allocated memory |
| Status | vNPU status |

**Example:**
```bash
$ npu-smi info -t info-vnpu -i 0 -c 0
Device 0, Chip 0:
    vNPU ID        : 100
    vNPU Group ID  : 0
    AI Core Num    : 4
    Memory Size    : 8192 MB
    Status         : Running
```

### Query vNPU Config Recovery Status

Check configuration recovery settings.

```bash
npu-smi info -t vnpu-cfg-recover
```

**Output:**
```
Recovery Mode : 1 (Enabled)
```

## Configuration Commands

### Set AVI Mode

Change AVI operation mode.

```bash
npu-smi set -t vnpu-mode -d <mode>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mode | integer | Yes | 0=Container, 1=VM |

**Example:**
```bash
# Set to Container mode
npu-smi set -t vnpu-mode -d 0

# Set to VM mode
npu-smi set -t vnpu-mode -d 1
```

**Note:** Mode change may require restart.

### Create vNPU

Create a new virtual NPU.

```bash
npu-smi set -t create-vnpu -i <id> -c <chip_id> -f <template> [-v <vnpu_id>] [-g <vgroup_id>]
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID |
| chip_id | integer | Yes | Chip ID |
| template | string | Yes | Template name from `template-info` |
| vnpu_id | integer | No | vNPU ID [phy_id*16+100, phy_id*16+115] |
| vgroup_id | integer | No | Group ID [0,1,2,3] |

**Example:**
```bash
# Create vNPU with auto-assigned ID
npu-smi set -t create-vnpu -i 0 -c 0 -f vir02

# Create vNPU with specific ID
npu-smi set -t create-vnpu -i 0 -c 0 -f vir02 -v 103

# Create vNPU with ID and group
npu-smi set -t create-vnpu -i 0 -c 0 -f vir04 -v 104 -g 1
```

**vNPU ID Range:**
- Formula: `[phy_id*16 + 100, phy_id*16 + 115]`
- Example: For physical chip 0: IDs 100-115
- Example: For physical chip 1: IDs 116-131

### Destroy vNPU

Remove a virtual NPU.

```bash
npu-smi set -t destroy-vnpu -i <id> -c <chip_id> -v <vnpu_id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID |
| chip_id | integer | Yes | Chip ID |
| vnpu_id | integer | Yes | vNPU ID to destroy |

**Example:**
```bash
# Destroy vNPU 103
npu-smi set -t destroy-vnpu -i 0 -c 0 -v 103
```

**Warning:** Ensure vNPU is not in use before destroying.

### Set vNPU Config Recovery

Enable/disable automatic vNPU recovery.

```bash
npu-smi set -t vnpu-cfg-recover -d <mode>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mode | integer | Yes | 0=Disable, 1=Enable |

**Example:**
```bash
# Enable recovery (default)
npu-smi set -t vnpu-cfg-recover -d 1

# Disable recovery
npu-smi set -t vnpu-cfg-recover -d 0
```

## Examples

### vNPU Lifecycle Management

```bash
#!/bin/bash

NPU=0
CHIP=0
TEMPLATE="vir02"

echo "=== vNPU Lifecycle Demo ==="

# 1. Check AVI mode
echo "Step 1: Checking AVI mode..."
npu-smi info -t vnpu-mode

# 2. List available templates
echo ""
echo "Step 2: Available templates:"
npu-smi info -t template-info

# 3. Create vNPU
echo ""
echo "Step 3: Creating vNPU with template $TEMPLATE..."
npu-smi set -t create-vnpu -i $NPU -c $CHIP -f $TEMPLATE -v 103

# 4. Verify creation
echo ""
echo "Step 4: Verifying vNPU creation..."
npu-smi info -t info-vnpu -i $NPU -c $CHIP

# 5. Destroy vNPU (uncomment to destroy)
# echo ""
# echo "Step 5: Destroying vNPU..."
# npu-smi set -t destroy-vnpu -i $NPU -c $CHIP -v 103

echo ""
echo "=== vNPU lifecycle demo complete ==="
```

### Batch Create vNPU

```bash
#!/bin/bash

NPU=0
CHIP=0
TEMPLATE="vir02"
START_ID=100
COUNT=4

echo "Creating $COUNT vNPUs on NPU $NPU, Chip $CHIP..."

for i in $(seq 0 $((COUNT-1))); do
    VNPU_ID=$((START_ID + i))
    echo "Creating vNPU $VNPU_ID..."
    npu-smi set -t create-vnpu -i $NPU -c $CHIP -f $TEMPLATE -v $VNPU_ID
done

echo ""
echo "All vNPUs created. Current status:"
npu-smi info -t info-vnpu -i $NPU -c $CHIP
```

### Multi-Tenant vNPU Setup

```bash
#!/bin/bash

# Setup vNPUs for different tenants/teams

NPU=0
CHIP=0

echo "Setting up multi-tenant vNPU environment..."

# Tenant A: Small instances
echo "Creating vNPUs for Tenant A (small)..."
npu-smi set -t create-vnpu -i $NPU -c $CHIP -f vir01 -v 100 -g 0
npu-smi set -t create-vnpu -i $NPU -c $CHIP -f vir01 -v 101 -g 0

# Tenant B: Medium instances
echo "Creating vNPUs for Tenant B (medium)..."
npu-smi set -t create-vnpu -i $NPU -c $CHIP -f vir02 -v 102 -g 1
npu-smi set -t create-vnpu -i $NPU -c $CHIP -f vir02 -v 103 -g 1

# Tenant C: Large instances
echo "Creating vNPUs for Tenant C (large)..."
npu-smi set -t create-vnpu -i $NPU -c $CHIP -f vir04 -v 104 -g 2

echo ""
echo "Multi-tenant setup complete!"
npu-smi info -t info-vnpu -i $NPU -c $CHIP
```

### Cleanup All vNPUs

```bash
#!/bin/bash

NPU=0
CHIP=0

echo "Cleaning up all vNPUs on NPU $NPU, Chip $CHIP..."

# Get list of vNPUs
vnpus=$(npu-smi info -t info-vnpu -i $NPU -c $CHIP | grep "vNPU ID" | awk '{print $3}')

for vnpu in $vnpus; do
    echo "Destroying vNPU $vnpu..."
    npu-smi set -t destroy-vnpu -i $NPU -c $CHIP -v $vnpu
done

echo ""
echo "Cleanup complete!"
npu-smi info -t info-vnpu -i $NPU -c $CHIP
```

## Template Selection Guide

| Template | AI Cores | Memory | Use Case |
|----------|----------|--------|----------|
| vir01 | 2 | 4GB | Light inference |
| vir02 | 4 | 8GB | Standard inference |
| vir04 | 8 | 16GB | Heavy inference/training |

**Selection Tips:**
- Match AI core count to model requirements
- Ensure sufficient memory for model + overhead
- Consider concurrent workload requirements
- Physical chip limits total resources

## Important Notes

### Resource Limits
- Total vNPU resources cannot exceed physical chip capacity
- Multiple vNPUs share physical AI cores and memory
- Monitor resource usage to avoid overcommitment

### vNPU ID Allocation
- Use formula: `[phy_id*16 + 100, phy_id*16 + 115]`
- Keep ID assignment consistent
- Document ID allocations for management

### Cleanup Requirements
- Always destroy vNPUs when no longer needed
- Verify no processes using vNPU before destruction
- Orphaned vNPUs waste resources

### Configuration Recovery
- Enabled by default
- Automatically restores vNPU config after restart
- Disable if manual management preferred

## Troubleshooting

### vNPU Creation Fails

```bash
# Check available resources
npu-smi info -t npu -i 0 -c 0

# Verify template exists
npu-smi info -t template-info

# Check if ID is already in use
npu-smi info -t info-vnpu -i 0 -c 0
```

### vNPU Not Responding

```bash
# Check vNPU status
npu-smi info -t info-vnpu -i 0 -c 0

# Verify AVI mode
npu-smi info -t vnpu-mode

# Check chip health
npu-smi info -t health -i 0
```

### Cannot Destroy vNPU

- Ensure no processes using the vNPU
- Check if vNPU is locked
- Verify correct vNPU ID
- Try force cleanup if necessary

## Related Skills

- [../npu-smi-query/](npu-smi-query/SKILL.md) - Query commands
- [../npu-smi-config/](npu-smi-config/SKILL.md) - Configuration commands
- [../npu-smi-upgrade/](npu-smi-upgrade/SKILL.md) - Firmware upgrade
- [../npu-smi-certificates/](npu-smi-certificates/SKILL.md) - Certificate management

## Official Documentation

- **AVI Guide**: https://www.hiascend.com/document/detail/zh/canncommercial/81RC1/envdeployment/instg/instg_0054.html
