# Diagnosis logic (quick reference)

1. Collect static signals and package versions (`python`, `pip`, `npu-smi`, env vars).
2. Probe PyTorch/NPU runtime with a tiny tensor.
3. Probe SGLang entrypoints (`check_env`, `launch_server --help`) and parse Ascend-related options.
4. Capture lightweight HCCL/distributed env hints.
5. Select an idle NPU device safely (or block launch probe if none idle).
6. Choose model path by priority:
   - user-specified
   - auto-discovered local model
   - synthetic local stub model
7. Attempt minimal low-cost launch using Ascend options and dummy load where supported.
8. Generate structured markdown/json diagnosis with green/yellow/red statuses and actionable next commands.
