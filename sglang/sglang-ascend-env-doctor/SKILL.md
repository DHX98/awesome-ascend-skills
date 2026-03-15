---
name: sglang-ascend-env-doctor
description: Diagnose whether SGLang can run on Ascend NPU at the lowest possible cost before real inference. Use this whenever users report Ascend startup failures (torch/torch_npu mismatch, CANN-driver mismatch, SGLang backend missing, launch argument errors, NPU visible but unusable), or when users want a reproducible environment health report without downloading real model weights.
---

# SGLang Ascend Env Doctor

## What this skill does

Run a low-cost, reproducible diagnosis flow to determine whether SGLang can start on Ascend NPU.

This skill validates:
- environment health
- Ascend backend availability in SGLang
- minimal launch viability

This skill **does not** validate:
- model quality
- inference correctness
- benchmark accuracy

## When to use

Use this skill when users say things like:
- "sglang cannot start on Ascend"
- "torch_npu import fails"
- "`npu-smi` sees cards but PyTorch cannot use NPU"
- "SGLang installed but Ascend backend seems missing"
- "Need quick environment check without downloading model weights"

## Runtime inputs

Required:
- none

Optional:
- `output_dir`: output root (default: `./sglang-ascend-env-doctor-output`)
- `model_path`: optional user model path
- `device_id`: optional preferred NPU device id
- `port`: optional server port
- `mem_fraction_static`: optional minimal launch memory fraction (default `0.3`)
- `launch_timeout_sec`: optional launch timeout seconds (default `40`)
- `skills_root`: optional path to local skills root for composition discovery

## Output contract

Under `output_dir`, always create:
- `logs/`: step logs and command outputs
- `reports/`: markdown + json reports
- `tmp/`: temporary probe assets (including stub model when needed)

Reports:
- `reports/<timestamp>-env-doctor-report.md`
- `reports/<timestamp>-env-doctor-report.json`
- `reports/latest-env-doctor-report.md`
- `reports/latest-env-doctor-report.json`

Status meanings:
- `green`: pass
- `yellow`: partial / blocked / uncertain / fallback path used
- `red`: fail

## Execution flow

Run in this order:

1) Static environment collection
- collect `date`, `hostname`, `whoami`, `pwd`
- collect `which python`, `python --version`
- collect `pip list`, `pip show` for `sglang`, `torch`, `torch_npu`, `transformers`, `sgl-kernel-npu`
- collect env vars `ASCEND_HOME`, `LD_LIBRARY_PATH`, `PYTHONPATH`, `PATH`
- collect `npu-smi info`

2) PyTorch / NPU probe
- `import torch`
- `import torch_npu`
- `torch.npu.is_available()`
- `torch.npu.device_count()`
- tiny tensor on NPU

3) SGLang probe
- run `python -m sglang.check_env` as best-effort only
- run `python -m sglang.launch_server --help`
- parse Ascend-related options in help output

4) HCCL-related probe (lightweight)
- collect HCCL env vars and distributed hints
- classify single-node minimal readiness vs distributed hints
- no full distributed test in v1

5) NPU device availability
- inspect `npu-smi info` and torch probe signals
- if user passed `device_id`, validate first
- prefer idle card
- if no safe idle card, skip launch probe and mark blocked

6) Model path selection strategy
- Priority A: use user `model_path` if valid
- Priority B: auto-discover small local HF-style model directory
- Priority C: create local stub model in `tmp/` for launch-path validation
- default behavior avoids downloading large model weights

7) Minimal low-cost launch probe
- use `python -m sglang.launch_server`
- prefer options:
  - `--device npu`
  - `--attention-backend ascend`
  - `--sampling-backend ascend` (when supported)
  - `--load-format dummy`
  - `--skip-tokenizer-init`
  - `--skip-server-warmup`
  - `--tp 1`
  - conservative `--mem-fraction-static`
- localhost + temporary/default port
- skip probe if no safe idle NPU

8) Structured diagnosis
- write markdown + json report
- include executive summary, per-check status, evidence, likely root causes, exact next commands
- include composition section (reused skills vs fallback checks)

## Composition / reuse behavior

This skill behaves as an orchestrator when possible.

First, discover available local skills:
- scan `<skills_root>` if provided
- otherwise scan `.cursor/skills` from current directory and parent directories

If suitable skills are found (for example `npu-smi`, `hccl-test`, `torch_npu`):
- mark them as discovered and used in report
- reuse their capability intent by running equivalent low-cost checks

If reusable skills are unavailable or fail:
- continue with built-in fallback checks
- explicitly record fallback usage and reason

This ensures the skill remains usable in minimal environments.

## Failure modes and heuristics

Typical diagnoses:
- `torch_npu` import fails -> likely package missing or Python env mismatch
- `npu-smi` sees cards but `torch.npu.is_available()` is false -> likely driver/CANN/env mismatch
- `sglang.launch_server --help` lacks Ascend options/text -> likely SGLang build/version mismatch
- minimal launch fails with backend import errors -> likely missing/incompatible `sgl-kernel-npu` stack
- all NPUs occupied -> launch probe blocked; free one card or specify idle card
- if minimal launch fails, report includes:
  - current SGLang-related dependency versions (for example `sglang`, `sgl_kernel_npu`, `torch`, `torch_npu`, `transformers`)
  - launch log tail snippet
  - log-signature-based possible root causes

`python -m sglang.check_env` failure is non-fatal in this skill: mark yellow and continue.

## Safety and reproducibility

- no destructive system operations
- no large model download by default
- all artifacts isolated under `output_dir`
- timestamped logs and reports
- rerunnable without deleting prior outputs

## Example invocation

```bash
bash .cursor/skills/sglang-ascend-env-doctor/scripts/run_env_doctor.sh \
  --output-dir ./sglang-ascend-env-doctor-output \
  --device-id 0
```

With explicit model path:

```bash
bash .cursor/skills/sglang-ascend-env-doctor/scripts/run_env_doctor.sh \
  --output-dir ./sglang-ascend-env-doctor-output \
  --model-path /path/to/local/model \
  --port 31000
```

## Limitations

- v1 uses lightweight HCCL checks only; no full distributed communication validation
- `npu-smi` process parsing is best-effort and may be vendor-output-version dependent
- launch viability is judged by startup behavior/port readiness, not inference correctness

