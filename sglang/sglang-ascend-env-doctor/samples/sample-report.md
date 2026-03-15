# SGLang Ascend Env Doctor Report (Sample)

- Run ID: `20260315-100000`
- Timestamp: `2026-03-15T10:00:00`
- Overall: `yellow`

## Executive summary
Overall status is yellow. Environment and backend checks are mostly available, but minimal launch is blocked because no idle NPU device was detected.

## Scope
This doctor validates Ascend environment readiness, SGLang backend availability, and minimal launch viability at low cost. It does not validate model quality or accuracy.

## Reuse / composition
- Skills roots scanned: `.cursor/skills`
- Skills discovered: `npu-smi, hccl-test, torch_npu`
- Skills used: `npu-smi, hccl-test, torch_npu`
- Fallback checks used: `static_environment_collection, torch_npu_probe, sglang_probe, npu_device_availability, model_path_selection, minimal_launch_probe`

## Check-by-check status

### static_environment_collection
- Status: `green`
- Source: `reused-skill:npu-smi + fallback:local-static`
- Summary: Static environment collection completed.

### torch_npu_probe
- Status: `green`
- Source: `fallback:python-probe`
- Summary: PyTorch/NPU probe passed.

### sglang_probe
- Status: `yellow`
- Source: `fallback:sglang-check`
- Summary: `sglang.check_env` failed, but doctor continued with fallback probes.

### hccl_probe
- Status: `green`
- Source: `reused-skill:hccl-test + fallback:local-hccl-check`
- Summary: Lightweight HCCL env probe collected.

### npu_device_availability
- Status: `yellow`
- Source: `reused-skill:npu-smi + fallback:device-selection`
- Summary: No free/idle NPU detected for safe launch probe.

### model_path_selection
- Status: `green`
- Source: `fallback:model-selection`
- Summary: Model path selected via synthetic-stub-model.

### minimal_launch_probe
- Status: `yellow`
- Source: `fallback:launch-probe`
- Summary: Launch probe skipped: no free/idle NPU detected for safe launch test.

## Likely root causes
- No free/idle NPU available for safe launch probe; free one card or specify an idle device.

## Exact next commands
- `npu-smi info`
- `bash .cursor/skills/sglang-ascend-env-doctor/scripts/run_env_doctor.sh --output-dir ./sglang-ascend-env-doctor-output --device-id <idle_id>`
