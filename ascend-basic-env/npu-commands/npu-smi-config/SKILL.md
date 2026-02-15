---
name: npu-smi-config
description: npu-smi configuration commands for Huawei Ascend NPU. Use when setting thresholds, configuring modes, managing ECC, fan control, and device settings. Covers all npu-smi set and clear subcommands.
---

# npu-smi Configuration Commands

Configure NPU settings using `npu-smi set` and `npu-smi clear`.

## Quick Reference

```bash
# Set temperature threshold
npu-smi set -t temperature -i <id> -c <chip_id> -d <value>

# Set power limit
npu-smi set -t power-limit -i <id> -c <chip_id> -d <value>

# Enable ECC mode
npu-smi set -t ecc-mode -i <id> -c <chip_id> -d 1

# Set fan mode
npu-smi set -t pwm-mode -d 0
npu-smi set -t pwm-duty-ratio -d 50

# Clear ECC errors
npu-smi clear -t ecc-info -i <id> -c <chip_id>
```

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| npu-smi | Tool installed |
| Permissions | Root for most config commands |
| Device IDs | From `npu-smi info -l` |
| Chip IDs | From `npu-smi info -m` |

## Configuration Commands

### Set Temperature Threshold

Set temperature alarm threshold.

```bash
npu-smi set -t temperature -i <id> -c <chip_id> -d <value>
```

**Parameters:**
| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| value | integer | - | Temperature threshold in °C |

**Example:**
```bash
# Set threshold to 85°C for device 0, chip 0
npu-smi set -t temperature -i 0 -c 0 -d 85
```

### Set Power Limit

Configure maximum power consumption.

```bash
npu-smi set -t power-limit -i <id> -c <chip_id> -d <value>
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| value | integer | Watts (W) | Maximum power limit |

**Example:**
```bash
# Set power limit to 300W
npu-smi set -t power-limit -i 0 -c 0 -d 300
```

### Set ECC Mode

Enable or disable ECC (Error Correcting Code).

```bash
npu-smi set -t ecc-mode -i <id> -c <chip_id> -d <mode>
```

**Modes:**
| Value | Mode | Description |
|-------|------|-------------|
| 0 | Disable | Turn off ECC |
| 1 | Enable | Turn on ECC |

**Example:**
```bash
# Enable ECC
npu-smi set -t ecc-mode -i 0 -c 0 -d 1

# Disable ECC
npu-smi set -t ecc-mode -i 0 -c 0 -d 0
```

### Set Persistence Mode

Control driver persistence.

```bash
npu-smi set -t persistence-mode -i <id> -d <mode>
```

**Modes:**
| Value | Mode |
|-------|------|
| 0 | Disable |
| 1 | Enable |

### Set Compute Mode

Configure compute access mode.

```bash
npu-smi set -t compute-mode -i <id> -c <chip_id> -d <mode>
```

**Modes:**
| Value | Mode | Description |
|-------|------|-------------|
| 0 | Default | Normal access |
| 1 | Exclusive | Exclusive process access |
| 2 | Prohibited | No compute allowed |

### Set Fan Mode

Configure fan control mode.

```bash
npu-smi set -t pwm-mode -d <mode>
```

**Modes:**
| Value | Mode | Description |
|-------|------|-------------|
| 0 | Manual | Manual fan control |
| 1 | Automatic | Automatic fan control (default) |

**Note:** In automatic mode, max fan speed ratio is limited to 39.

### Set Fan Speed Ratio

Set fan speed (manual mode only).

```bash
npu-smi set -t pwm-duty-ratio -d <ratio>
```

**Parameters:**
| Parameter | Range | Description |
|-----------|-------|-------------|
| ratio | [0-100] | Fan speed percentage |

**Example:**
```bash
# Set fan to 50% speed (must be in manual mode)
npu-smi set -t pwm-mode -d 0
npu-smi set -t pwm-duty-ratio -d 50
```

### Set MAC Address

Configure network MAC address.

```bash
npu-smi set -t mac-addr -i <id> -c <chip_id> -d <mac_id> -s <mac_string>
```

**Parameters:**
| Parameter | Description | Format |
|-----------|-------------|--------|
| mac_id | Port index | 0=eth0, 1=eth1, 2=eth2, 3=eth3 |
| mac_string | MAC address | "XX:XX:XX:XX:XX:XX" |

**Example:**
```bash
npu-smi set -t mac-addr -i 0 -c 0 -d 0 -s "00:11:22:33:44:55"
```

**Note:** System restart required after setting MAC address.

### Set Power State (Sleep)

Configure sleep timeout.

```bash
npu-smi set -t power-state -i <id> -c <chip_id> -d <value>
```

**Parameters:**
| Parameter | Range | Unit | Description |
|-----------|-------|------|-------------|
| value | [200, 604800000] | ms | Sleep time in milliseconds |

**Example:**
```bash
# Set 5 minute sleep timeout
npu-smi set -t power-state -i 0 -c 0 -d 300000
```

### Set Boot Medium

Select boot device.

```bash
npu-smi set -t boot-select -i <id> -c <chip_id> -d <value>
```

**Values:**
| Value | Medium |
|-------|--------|
| 3 | M.2 SSD |
| 4 | eMMC |

**Example:**
```bash
# Boot from M.2 SSD
npu-smi set -t boot-select -i 0 -c 0 -d 3
```

**Note:** Power cycle required. Ensure OS is installed on selected medium.

### Set CPU Frequency

Configure CPU and AI Core frequencies.

```bash
npu-smi set -t cpu-freq-up -i <id> -d <value>
```

**Values:**
| Value | CPU Frequency | AI Core Frequency |
|-------|---------------|-------------------|
| 0 | 1.9 GHz | 800 MHz |
| 1 | 1.0 GHz | 800 MHz |

### Set System Log Persistence

Enable/disable persistent system logging.

```bash
npu-smi set -t sys-log-enable -d <mode>
```

**Modes:**
| Value | Mode |
|-------|------|
| 0 | Disable |
| 1 | Enable |

### Collect System Logs

Dump system logs to file.

```bash
npu-smi set -t sys-log-dump -s <level> -f <path>
```

**Parameters:**
| Parameter | Range | Description |
|-----------|-------|-------------|
| level | [1-10] | Log verbosity level |
| path | string | Absolute path for log file |

**Example:**
```bash
npu-smi set -t sys-log-dump -s 5 -f /var/log/npu-sys.log
```

**Note:** Target directory must exist.

### Clear Log Configuration

Reset system log settings to defaults.

```bash
npu-smi set -t clear-syslog-cfg
```

### Set AI CPU Custom Op Security Verification

Enable/disable custom operator verification.

```bash
npu-smi set -t custom-op-secverify-enable -i <id> -d <mode>
```

**Modes:**
| Value | Mode |
|-------|------|
| 0 | Disable verification |
| 1 | Enable verification |

### Set AI CPU Custom Op Verification Mode

Configure certificate verification mode.

```bash
npu-smi set -t custom-op-secverify-mode -i <id> -d <mode>
```

**Modes:**
| Value | Mode | Description |
|-------|------|-------------|
| 0 | Disable | No verification |
| 1 | Huawei | Huawei certificate only |
| 2 | Customer | Customer certificate only |
| 3 | Huawei/Customer | Either certificate |
| 4 | Community | Community certificate |
| 5 | Huawei/Community | Huawei or community |
| 6 | Customer/Community | Customer or community |
| 7 | All | Any valid certificate |

### Set AI CPU Op Timeout

Configure operator timeout.

```bash
npu-smi set -t op-timeout-cfg -i <id> -c <chip_id> -d <value>
```

**Parameters:**
| Parameter | Range | Description |
|-----------|-------|-------------|
| value | [20, 32] | Timeout value |

### Set AI CPU Custom Op Verification Certificate

Import verification certificates.

```bash
npu-smi set -t custom-op-secverify-cert -i <id> -f "<cert_path>"
```

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| cert_path | Certificate file path(s), space-separated |

**Note:** Total certificate content must not exceed 8192 bytes.

### Set P2P Memory Copy Configuration

Enable/disable P2P memory copy.

```bash
# For all chips on device
npu-smi set -t p2p-mem-cfg -i <id> -d <value>

# For specific chip
npu-smi set -t p2p-mem-cfg -i <id> -c <chip_id> -d <value>
```

**Values:**
| Value | Mode |
|-------|------|
| 0 | Disable |
| 1 | Enable |

## Clear Commands

### Clear ECC Error Count

Clear ECC error counters.

```bash
# Clear all chips on device
npu-smi clear -t ecc-info -i <id>

# Clear specific chip
npu-smi clear -t ecc-info -i <id> -c <chip_id>
```

## Examples

### Configure New Device

```bash
#!/bin/bash

NPU=0
CHIP=0

# Set temperature threshold
echo "Setting temperature threshold..."
npu-smi set -t temperature -i $NPU -c $CHIP -d 85

# Set power limit
echo "Setting power limit..."
npu-smi set -t power-limit -i $NPU -c $CHIP -d 300

# Enable ECC
echo "Enabling ECC..."
npu-smi set -t ecc-mode -i $NPU -c $CHIP -d 1

# Configure fan
echo "Setting fan to automatic mode..."
npu-smi set -t pwm-mode -d 1

echo "Configuration complete!"
```

### Fan Control Script

```bash
#!/bin/bash

# Set manual fan control with speed based on temperature
TEMP=$(npu-smi info -t temp -i 0 -c 0 | grep "NPU Temperature" | awk '{print $4}')

if [ "$TEMP" -gt 80 ]; then
    SPEED=100
elif [ "$TEMP" -gt 70 ]; then
    SPEED=80
elif [ "$TEMP" -gt 60 ]; then
    SPEED=60
else
    SPEED=40
fi

npu-smi set -t pwm-mode -d 0
npu-smi set -t pwm-duty-ratio -d $SPEED

echo "Fan speed set to $SPEED% (temperature: ${TEMP}°C)"
```

### Reset Device Configuration

```bash
#!/bin/bash

NPU=0
CHIP=0

# Reset to safe defaults
echo "Resetting device $NPU, chip $CHIP to defaults..."

# Temperature threshold to 85°C
npu-smi set -t temperature -i $NPU -c $CHIP -d 85

# Power limit to maximum
npu-smi set -t power-limit -i $NPU -c $CHIP -d 310

# Enable ECC
npu-smi set -t ecc-mode -i $NPU -c $CHIP -d 1

# Default compute mode
npu-smi set -t compute-mode -i $NPU -c $CHIP -d 0

# Automatic fan
npu-smi set -t pwm-mode -d 1

# Clear any ECC errors
npu-smi clear -t ecc-info -i $NPU -c $CHIP

echo "Reset complete!"
```

## Parameter Summary

### Set Commands

| Command | Type | Range | Description |
|---------|------|-------|-------------|
| `temperature` | integer | - | Temperature threshold (°C) |
| `power-limit` | integer | - | Power limit (W) |
| `ecc-mode` | enum | 0-1 | ECC enable/disable |
| `persistence-mode` | enum | 0-1 | Driver persistence |
| `compute-mode` | enum | 0-2 | Compute access mode |
| `pwm-mode` | enum | 0-1 | Fan control mode |
| `pwm-duty-ratio` | integer | 0-100 | Fan speed (%) |
| `mac-addr` | string | - | MAC address |
| `power-state` | integer | 200-604800000 | Sleep timeout (ms) |
| `boot-select` | enum | 3-4 | Boot medium |
| `cpu-freq-up` | enum | 0-1 | CPU frequency |
| `sys-log-enable` | enum | 0-1 | Log persistence |
| `p2p-mem-cfg` | enum | 0-1 | P2P memory copy |

### Clear Commands

| Command | Description |
|---------|-------------|
| `ecc-info` | Clear ECC error count |

## Related Skills

- [../npu-smi-query/](npu-smi-query/SKILL.md) - Query commands
- [../npu-smi-upgrade/](npu-smi-upgrade/SKILL.md) - Firmware upgrade
- [../npu-smi-virtualization/](npu-smi-virtualization/SKILL.md) - vNPU management
- [../npu-smi-certificates/](npu-smi-certificates/SKILL.md) - Certificate management

## Important Notes

- **Root permissions** required for most configuration commands
- **Restart required** after changing MAC address or boot medium
- **Power cycle required** for some settings to take effect
- **Manual fan mode** required before setting fan speed ratio
- **Automatic fan mode** limits max speed to 39%
- Verify changes with query commands after configuration
