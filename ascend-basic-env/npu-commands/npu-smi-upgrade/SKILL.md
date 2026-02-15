---
name: npu-smi-upgrade
description: npu-smi firmware upgrade commands for Huawei Ascend NPU. Use when upgrading MCU, bootloader, or VRD firmware. Covers the complete upgrade workflow including version queries, upgrades, status checks, and activation.
---

# npu-smi Upgrade Commands

Manage firmware upgrades using `npu-smi upgrade`.

## Quick Reference

```bash
# Query current firmware version
npu-smi upgrade -b mcu -i <id>

# Upgrade firmware
npu-smi upgrade -t mcu -i <id> -f <file_path>

# Check upgrade status
npu-smi upgrade -q mcu -i <id>

# Activate firmware
npu-smi upgrade -a mcu -i <id>
```

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| npu-smi | Tool installed |
| Permissions | Root required |
| Firmware file | Valid .hpm firmware package |
| Device ID | From `npu-smi info -l` |

## Firmware Components

| Component | Description | Restart Required |
|-----------|-------------|------------------|
| MCU | Microcontroller Unit | Yes |
| Bootloader | System bootloader | Yes |
| VRD | Voltage Regulator Driver | Power cycle (30s) |

## Upgrade Workflow

Complete firmware upgrade process:

```
Query Version → Upgrade → Check Status → Activate → Restart
```

## Commands

### Query Firmware Version

Check current firmware version before upgrade.

```bash
npu-smi upgrade -b <item> -i <id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item | string | Yes | Firmware type: mcu, bootloader, vrd |
| id | integer | Yes | Device ID |

**Example:**
```bash
# Query MCU version
npu-smi upgrade -b mcu -i 0

# Query bootloader version
npu-smi upgrade -b bootloader -i 0

# Query VRD version
npu-smi upgrade -b vrd -i 0
```

**Output:**
```
Version : 24.15.19
```

### Upgrade Firmware

Start firmware upgrade process.

```bash
npu-smi upgrade -t <item> -i <id> -f <file_path>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item | string | Yes | Firmware type: mcu, bootloader, vrd |
| id | integer | Yes | Device ID |
| file_path | string | Yes* | Path to .hpm firmware file |

**Note:** VRD upgrades don't require file_path parameter.

**Example:**
```bash
# Upgrade MCU
npu-smi upgrade -t mcu -i 0 -f ./Ascend-hdk-310b-mcu_24.15.19.hpm

# Upgrade bootloader
npu-smi upgrade -t bootloader -i 0 -f ./Ascend-hdk-310b-bootloader_1.0.0.hpm

# Upgrade VRD (no file needed)
npu-smi upgrade -t vrd -i 0
```

**Output:**
| Field | Description |
|-------|-------------|
| Validity | File validation result |
| transfile | Transfer status |
| Status | Upgrade status |
| Message | Status message |

### Query Upgrade Status

Check current upgrade progress.

```bash
npu-smi upgrade -q <item> -i <id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item | string | Yes | Firmware type: mcu, bootloader, vrd |
| id | integer | Yes | Device ID |

**Example:**
```bash
# Check MCU upgrade status
npu-smi upgrade -q mcu -i 0
```

**Output:**
| Field | Description | Values |
|-------|-------------|--------|
| Conclusion | Upgrade result | PASS, Running, FAIL |
| Message | Detailed status | - |

### Activate Firmware

Activate upgraded firmware.

```bash
npu-smi upgrade -a <item> -i <id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item | string | Yes | Firmware type: mcu, bootloader, vrd |
| id | integer | Yes | Device ID |

**Example:**
```bash
# Activate MCU firmware
npu-smi upgrade -a mcu -i 0

# Activate bootloader
npu-smi upgrade -a bootloader -i 0

# Activate VRD
npu-smi upgrade -a vrd -i 0
```

**Output:**
| Field | Description |
|-------|-------------|
| Status | Activation status |
| Message | Status details |

## Complete Upgrade Examples

### MCU Upgrade

```bash
#!/bin/bash

NPU=0
FIRMWARE="./Ascend-hdk-310b-mcu_24.15.19.hpm"

echo "=== MCU Firmware Upgrade ==="

# 1. Query current version
echo "Step 1: Querying current version..."
npu-smi upgrade -b mcu -i $NPU

# 2. Start upgrade
echo "Step 2: Starting upgrade..."
npu-smi upgrade -t mcu -i $NPU -f $FIRMWARE

# 3. Wait and check status
echo "Step 3: Checking upgrade status..."
sleep 5
npu-smi upgrade -q mcu -i $NPU

# 4. Activate
echo "Step 4: Activating firmware..."
npu-smi upgrade -a mcu -i $NPU

# 5. Restart device
echo "Step 5: Restarting device (MCU requires restart)..."
echo "Please restart the device manually or run:"
echo "  npu-smi set -t power-state -i $NPU -c 0 -d 200"

echo "=== Upgrade complete ==="
```

### Bootloader Upgrade

```bash
#!/bin/bash

NPU=0
FIRMWARE="./Ascend-hdk-310b-bootloader_1.0.0.hpm"

echo "=== Bootloader Firmware Upgrade ==="

# Check current version
npu-smi upgrade -b bootloader -i $NPU

# Upgrade
npu-smi upgrade -t bootloader -i $NPU -f $FIRMWARE

# Check status
npu-smi upgrade -q bootloader -i $NPU

# Activate
npu-smi upgrade -a bootloader -i $NPU

echo "Bootloader upgrade complete. Restart required."
```

### VRD Upgrade

```bash
#!/bin/bash

NPU=0

echo "=== VRD Firmware Upgrade ==="

# Check current version
npu-smi upgrade -b vrd -i $NPU

# Upgrade (no file needed for VRD)
npu-smi upgrade -t vrd -i $NPU

# Check status
npu-smi upgrade -q vrd -i $NPU

# Activate
npu-smi upgrade -a vrd -i $NPU

echo "VRD upgrade complete."
echo "IMPORTANT: Power cycle required (keep powered off for 30+ seconds)"
```

### Batch Upgrade All Components

```bash
#!/bin/bash

NPU=0
MCU_FW="./Ascend-hdk-310b-mcu_24.15.19.hpm"
BOOT_FW="./Ascend-hdk-310b-bootloader_1.0.0.hpm"

upgrade_component() {
    local component=$1
    local firmware=$2
    local needs_restart=$3
    
    echo ""
    echo "=== Upgrading $component ==="
    
    # Query current version
    echo "Current version:"
    npu-smi upgrade -b $component -i $NPU
    
    # Upgrade
    if [ -n "$firmware" ]; then
        echo "Upgrading with $firmware..."
        npu-smi upgrade -t $component -i $NPU -f $firmware
    else
        echo "Upgrading..."
        npu-smi upgrade -t $component -i $NPU
    fi
    
    # Wait for upgrade
    echo "Waiting for upgrade to complete..."
    sleep 10
    
    # Check status
    local status=$(npu-smi upgrade -q $component -i $NPU | grep Conclusion | awk '{print $2}')
    if [ "$status" = "PASS" ]; then
        echo "Upgrade successful!"
        
        # Activate
        echo "Activating..."
        npu-smi upgrade -a $component -i $NPU
        
        if [ "$needs_restart" = "yes" ]; then
            echo "RESTART REQUIRED for $component"
        fi
    else
        echo "Upgrade failed or in progress: $status"
        npu-smi upgrade -q $component -i $NPU
    fi
}

# Upgrade MCU
upgrade_component "mcu" "$MCU_FW" "yes"

# Upgrade Bootloader  
upgrade_component "bootloader" "$BOOT_FW" "yes"

# Upgrade VRD
upgrade_component "vrd" "" "power-cycle"

echo ""
echo "=== All upgrades initiated ==="
echo "Please follow restart/power cycle requirements for each component"
```

## Monitoring Upgrade Progress

### Real-time Status Monitor

```bash
#!/bin/bash

NPU=0
COMPONENT="mcu"

echo "Monitoring $COMPONENT upgrade on NPU $NPU..."
echo "Press Ctrl+C to stop"

while true; do
    clear
    echo "=== Upgrade Status $(date) ==="
    npu-smi upgrade -q $COMPONENT -i $NPU
    
    status=$(npu-smi upgrade -q $COMPONENT -i $NPU 2>/dev/null | grep Conclusion | awk '{print $2}')
    if [ "$status" = "PASS" ] || [ "$status" = "FAIL" ]; then
        echo ""
        echo "Upgrade finished with status: $status"
        break
    fi
    
    sleep 5
done
```

## Upgrade Checklist

Before upgrading:

- [ ] Backup current configuration
- [ ] Verify firmware file integrity
- [ ] Check current firmware version
- [ ] Ensure stable power supply
- [ ] Close all applications using NPU

After upgrading:

- [ ] Verify new version: `npu-smi upgrade -b <item> -i <id>`
- [ ] Check device health: `npu-smi info -t health -i <id>`
- [ ] Restart/power cycle as required
- [ ] Verify functionality

## Important Notes

### MCU Upgrade
- **Restart required** after activation
- Can be restarted via `power-state` or physical power cycle

### Bootloader Upgrade
- **Restart required** after activation
- Critical component - ensure power stability during upgrade

### VRD Upgrade
- **Power cycle required** after activation
- Must keep device powered off for **30+ seconds**
- Simply restarting is not sufficient

### General Warnings
- Do not power off during upgrade
- Ensure firmware file is valid
- Verify device ID before upgrading
- One upgrade at a time (concurrent MCU upgrades not supported)
- Some features may be unavailable during upgrade

## Troubleshooting

### Upgrade Fails

```bash
# Check error message
npu-smi upgrade -q mcu -i 0

# Verify firmware file exists and is valid
ls -la firmware.hpm
file firmware.hpm

# Check device health
npu-smi info -t health -i 0
```

### Activation Fails

- Ensure upgrade completed successfully first
- Check if restart/power cycle is needed
- Verify device is responsive: `npu-smi info -l`

### Version Not Changed After Upgrade

- Verify activation was successful
- Ensure restart/power cycle was performed
- Check upgrade status for errors

## Related Skills

- [../npu-smi-query/](npu-smi-query/SKILL.md) - Query commands
- [../npu-smi-config/](npu-smi-config/SKILL.md) - Configuration commands
- [../npu-smi-virtualization/](npu-smi-virtualization/SKILL.md) - vNPU management
- [../npu-smi-certificates/](npu-smi-certificates/SKILL.md) - Certificate management

## Official Documentation

- **Firmware Upgrade Guide**: https://www.hiascend.com/document/detail/zh/canncommercial/81RC1/envdeployment/instg/instg_0053.html
