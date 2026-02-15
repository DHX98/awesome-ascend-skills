---
name: npu-smi-certificates
description: npu-smi certificate management commands for Huawei Ascend NPU. Use when managing TLS certificates, CSR generation, certificate validation, and security settings. Covers TLS certificate import, expiration settings, and rootkey management.
---

# npu-smi Certificate Management Commands

Manage TLS certificates and security using `npu-smi` certificate commands.

## Quick Reference

```bash
# Generate CSR
npu-smi info -t tls-csr-get -i <id> -c <chip_id>

# Import TLS certificate
npu-smi set -t tls-cert -i <id> -c <chip_id> -f "<tls> <ca> <subca>"

# View certificate info
npu-smi info -t tls-cert -i <id> -c <chip_id>

# Set expiration threshold
npu-smi set -t tls-cert-period -i <id> -c <chip_id> -s <days>

# Restore default threshold
npu-smi clear -t tls-cert-period -i <id> -c <chip_id>
```

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| npu-smi | Tool installed |
| Permissions | Root required |
| Certificates | Valid PEM format certificates |
| CSR | Certificate Signing Request (optional) |

## Certificate Files

| File | Description | Format |
|------|-------------|--------|
| TLS Certificate | Device certificate | PEM (.pem) |
| CA Root Certificate | Root authority | PEM (.pem) |
| Sub-CA Certificate | Intermediate authority | PEM (.pem) |

## Query Commands

### Get CSR

Generate Certificate Signing Request.

```bash
npu-smi info -t tls-csr-get -i <id> -c <chip_id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID |
| chip_id | integer | Yes | Chip ID |

**Output:**
- CSR content in PEM format

**Example:**
```bash
$ npu-smi info -t tls-csr-get -i 0 -c 0
-----BEGIN CERTIFICATE REQUEST-----
MIICijCCAXICAQIwRTELMAkGA1UEBhMCQ04xEzARBgNVBAgMClNvbWUtU3RhdGUx
...
-----END CERTIFICATE REQUEST-----
```

**Usage:**
1. Generate CSR
2. Submit to Certificate Authority
3. Receive signed certificate
4. Import certificate

### View Certificate Info

Display current TLS certificate information.

```bash
npu-smi info -t tls-cert -i <id> -c <chip_id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID |
| chip_id | integer | Yes | Chip ID |

**Output Fields:**
| Field | Description |
|-------|-------------|
| Subject | Certificate subject |
| Issuer | Certificate issuer |
| Valid From | Start date |
| Valid Until | Expiration date |
| Serial Number | Certificate serial |
| Version | Certificate version |

**Example:**
```bash
$ npu-smi info -t tls-cert -i 0 -c 0
Device 0, Chip 0:
    Subject       : CN=device-0, O=Organization
    Issuer        : CN=CA-Root, O=CertificateAuthority
    Valid From    : 2024-01-01 00:00:00
    Valid Until   : 2025-01-01 00:00:00
    Serial Number : 1234567890ABCDEF
```

### Query Certificate Expiration Threshold

Check current expiration warning threshold.

```bash
npu-smi info -t tls-cert-period -i <id> -c <chip_id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID |
| chip_id | integer | Yes | Chip ID |

**Output:**
```
Expiration Threshold : 90 days
```

### Query Rootkey Status

Check rootkey security status.

```bash
npu-smi info -t rootkey -i <id> -c <chip_id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID |
| chip_id | integer | Yes | Chip ID |

**Output:**
```
Rootkey Status : Present
```

## Configuration Commands

### Import/Update TLS Certificate

Install or update TLS certificates.

```bash
npu-smi set -t tls-cert -i <id> -c <chip_id> -f "<tls_cert> <ca_root_cert> <sub_ca_cert>"
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID |
| chip_id | integer | Yes | Chip ID |
| tls_cert | string | Yes | Path to TLS certificate file |
| ca_root_cert | string | Yes | Path to CA root certificate |
| sub_ca_cert | string | Yes | Path to sub-CA certificate |

**Example:**
```bash
# Import certificates
npu-smi set -t tls-cert -i 0 -c 0 -f "device.pem ca-root.pem ca-sub.pem"

# Using absolute paths
npu-smi set -t tls-cert -i 0 -c 0 \
  -f "/etc/npu/certs/device.pem /etc/npu/certs/ca-root.pem /etc/npu/certs/ca-sub.pem"
```

**Certificate Format:**
- Format: PEM encoded
- Extensions: .pem, .crt
- Encoding: Base64 ASCII

### Set Certificate Expiration Threshold

Configure expiration warning threshold.

```bash
npu-smi set -t tls-cert-period -i <id> -c <chip_id> -s <period>
```

**Parameters:**
| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| period | integer | [7-180] | 90 | Days before expiration to warn |

**Example:**
```bash
# Set 60-day warning threshold
npu-smi set -t tls-cert-period -i 0 -c 0 -s 60

# Set 30-day warning (urgent)
npu-smi set -t tls-cert-period -i 0 -c 0 -s 30

# Set maximum 180-day warning
npu-smi set -t tls-cert-period -i 0 -c 0 -s 180
```

## Clear Commands

### Restore Default Certificate Expiration Threshold

Reset expiration threshold to default (90 days).

```bash
npu-smi clear -t tls-cert-period -i <id> -c <chip_id>
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Device ID |
| chip_id | integer | Yes | Chip ID |

**Example:**
```bash
# Restore default threshold
npu-smi clear -t tls-cert-period -i 0 -c 0
```

## Examples

### Complete Certificate Lifecycle

```bash
#!/bin/bash

NPU=0
CHIP=0

echo "=== Certificate Lifecycle Management ==="

# 1. Generate CSR
echo "Step 1: Generating CSR..."
npu-smi info -t tls-csr-get -i $NPU -c $CHIP > device.csr

# 2. View current certificate (if exists)
echo ""
echo "Step 2: Current certificate info:"
npu-smi info -t tls-cert -i $NPU -c $CHIP

# 3. After receiving signed certificate, import it
echo ""
echo "Step 3: Import certificates (when ready)..."
echo "Command: npu-smi set -t tls-cert -i $NPU -c $CHIP -f 'device.pem ca-root.pem ca-sub.pem'"

# 4. Verify import
echo ""
echo "Step 4: Verify imported certificate:"
npu-smi info -t tls-cert -i $NPU -c $CHIP

# 5. Check expiration threshold
echo ""
echo "Step 5: Expiration threshold:"
npu-smi info -t tls-cert-period -i $NPU -c $CHIP

echo ""
echo "=== Certificate lifecycle complete ==="
```

### Certificate Renewal Script

```bash
#!/bin/bash

NPU=0
CHIP=0
NEW_CERT="new-device.pem"
CA_ROOT="ca-root.pem"
CA_SUB="ca-sub.pem"

echo "Renewing certificate for NPU $NPU, Chip $CHIP..."

# Backup current certificate info
echo "Backing up current certificate..."
npu-smi info -t tls-cert -i $NPU -c $CHIP > cert-backup-$(date +%Y%m%d).txt

# Check expiration
echo "Checking current certificate expiration..."
npu-smi info -t tls-cert -i $NPU -c $CHIP | grep "Valid Until"

# Import new certificate
echo "Importing new certificate..."
npu-smi set -t tls-cert -i $NPU -c $CHIP -f "$NEW_CERT $CA_ROOT $CA_SUB"

# Verify new certificate
echo "Verifying new certificate..."
npu-smi info -t tls-cert -i $NPU -c $CHIP

echo "Certificate renewal complete!"
```

### Batch Certificate Management

```bash
#!/bin/bash

# Manage certificates for all chips on all devices

echo "=== Batch Certificate Management ==="

# Get all devices
npus=$(npu-smi info -l | grep -E '^\|\s+[0-9]+' | awk '{print $2}')

for npu in $npus; do
    # Get all chips for this NPU
    chips=$(npu-smi info -m | grep "^| $npu " | awk '{print $4}')
    
    for chip in $chips; do
        echo ""
        echo "=== NPU $npu, Chip $chip ==="
        
        # Check current certificate
        echo "Current certificate:"
        npu-smi info -t tls-cert -i $npu -c $chip
        
        # Check expiration threshold
        echo "Expiration threshold:"
        npu-smi info -t tls-cert-period -i $npu -c $chip
    done
done
```

### Certificate Expiration Monitor

```bash
#!/bin/bash

# Monitor certificate expiration dates

THRESHOLD=30  # Days before expiration to warn

echo "=== Certificate Expiration Monitor ==="
echo "Warning threshold: $THRESHOLD days"
echo ""

# Get all devices
npus=$(npu-smi info -l | grep -E '^\|\s+[0-9]+' | awk '{print $2}')

for npu in $npus; do
    chips=$(npu-smi info -m | grep "^| $npu " | awk '{print $4}')
    
    for chip in $chips; do
        cert_info=$(npu-smi info -t tls-cert -i $npu -c $chip 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            expiry=$(echo "$cert_info" | grep "Valid Until" | cut -d: -f2- | xargs)
            
            if [ -n "$expiry" ]; then
                # Calculate days until expiration
                expiry_ts=$(date -d "$expiry" +%s 2>/dev/null || echo "0")
                now_ts=$(date +%s)
                days_left=$(( (expiry_ts - now_ts) / 86400 ))
                
                if [ $days_left -lt $THRESHOLD ]; then
                    echo "WARNING: NPU $npu, Chip $chip certificate expires in $days_left days ($expiry)"
                else
                    echo "OK: NPU $npu, Chip $chip certificate valid for $days_left days"
                fi
            fi
        fi
    done
done
```

### Secure Certificate Deployment

```bash
#!/bin/bash

# Deploy certificates with verification

NPU=0
CHIP=0
CERT_DIR="/secure/certs"

echo "=== Secure Certificate Deployment ==="

# Verify certificate files exist
echo "Verifying certificate files..."
for file in "$CERT_DIR/device.pem" "$CERT_DIR/ca-root.pem" "$CERT_DIR/ca-sub.pem"; do
    if [ ! -f "$file" ]; then
        echo "ERROR: Certificate file not found: $file"
        exit 1
    fi
done
echo "All certificate files found."

# Backup current certificate
echo "Backing up current certificate..."
npu-smi info -t tls-cert -i $NPU -c $CHIP > "$CERT_DIR/backup-$(date +%Y%m%d-%H%M%S).txt"

# Import new certificates
echo "Importing new certificates..."
npu-smi set -t tls-cert -i $NPU -c $CHIP \
  -f "$CERT_DIR/device.pem $CERT_DIR/ca-root.pem $CERT_DIR/ca-sub.pem"

if [ $? -eq 0 ]; then
    echo "Import successful!"
    
    # Verify
    echo "Verifying imported certificate..."
    npu-smi info -t tls-cert -i $NPU -c $CHIP
    
    # Set reasonable expiration threshold
    echo "Setting 60-day expiration threshold..."
    npu-smi set -t tls-cert-period -i $NPU -c $CHIP -s 60
else
    echo "ERROR: Certificate import failed!"
    exit 1
fi

echo ""
echo "=== Deployment complete ==="
```

## Certificate File Formats

### PEM Format Example

```
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAJC1HiIAZAiUMA0GCSqGSIb3Qa3BajELMAkGA1UEBhMC
U0cxDzANBgNVBAgTBlNpbmdhcG9yZTEPMA0GA1UEBxMGU2luZ2Fwb3JlMRMwEQYD
...
-----END CERTIFICATE-----
```

### CSR Format Example

```
-----BEGIN CERTIFICATE REQUEST-----
MIICijCCAXICAQIwRTELMAkGA1UEBhMCQ04xEzARBgNVBAgMClNvbWUtU3RhdGUx
ITAfBgNVBAoMGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDEMMAoGA1UEAwwDZHNj
...
-----END CERTIFICATE REQUEST-----
```

## Important Notes

### Certificate Requirements
- Valid PEM format
- Not expired
- Properly signed by CA
- Matching private key (if applicable)

### Security Best Practices
- Store certificates securely
- Use appropriate file permissions (600)
- Regular certificate rotation
- Monitor expiration dates
- Keep CA certificates updated

### Threshold Recommendations
| Environment | Recommended Threshold |
|-------------|----------------------|
| Production | 30 days |
| Staging | 60 days |
| Development | 90 days |

### Common Issues
- Certificate format errors
- Mismatched certificate chain
- Expired certificates
- Incorrect file paths
- Permission denied

## Troubleshooting

### Certificate Import Fails

```bash
# Verify certificate format
openssl x509 -in device.pem -text -noout

# Check certificate chain
openssl verify -CAfile ca-root.pem -untrusted ca-sub.pem device.pem

# Check file permissions
ls -la *.pem
```

### Certificate Not Recognized

```bash
# Verify certificate is installed
npu-smi info -t tls-cert -i 0 -c 0

# Check for errors in dmesg
dmesg | grep -i certificate

# Verify device is responsive
npu-smi info -t health -i 0
```

### CSR Generation Issues

```bash
# Verify CSR format
openssl req -in device.csr -text -noout

# Check CSR details
openssl req -in device.csr -noout -subject
```

## Related Skills

- [../npu-smi-query/](npu-smi-query/SKILL.md) - Query commands
- [../npu-smi-config/](npu-smi-config/SKILL.md) - Configuration commands
- [../npu-smi-upgrade/](npu-smi-upgrade/SKILL.md) - Firmware upgrade
- [../npu-smi-virtualization/](npu-smi-virtualization/SKILL.md) - vNPU management

## Official Documentation

- **Security Guide**: https://www.hiascend.com/document/detail/zh/canncommercial/81RC1/security/security_0000.html
