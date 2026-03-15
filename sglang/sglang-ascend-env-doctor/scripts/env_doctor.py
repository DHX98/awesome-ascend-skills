#!/usr/bin/env python3
import argparse
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


STATUS_GREEN = "green"
STATUS_YELLOW = "yellow"
STATUS_RED = "red"


def now_ts() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def safe_text(text: str, limit: int = 12000) -> str:
    if text is None:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[truncated {len(text) - limit} chars]"


@dataclass
class CommandResult:
    cmd: List[str]
    returncode: int
    stdout: str
    stderr: str
    log_file: str
    duration_sec: float
    source: str = "fallback"

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class EnvDoctor:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.output_dir = Path(args.output_dir).resolve()
        self.logs_dir = self.output_dir / "logs"
        self.reports_dir = self.output_dir / "reports"
        self.tmp_dir = self.output_dir / "tmp"
        self.run_id = now_ts()

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        self.stage_log = self.logs_dir / f"{self.run_id}-stage.log"
        self.report: Dict = {
            "meta": {
                "run_id": self.run_id,
                "timestamp": datetime.now().isoformat(),
                "cwd": str(Path.cwd()),
                "python_executable": sys.executable,
                "output_dir": str(self.output_dir),
            },
            "summary": {
                "overall_status": STATUS_YELLOW,
                "executive_summary": "",
                "likely_root_causes": [],
                "next_commands": [],
                "scope_note": "This doctor validates environment/backend/minimal launch path only; it does not validate model quality or accuracy.",
            },
            "composition": {
                "skills_roots_scanned": [],
                "skills_discovered": [],
                "skills_used": [],
                "fallback_checks": [],
                "notes": [],
            },
            "checks": [],
            "artifacts": {
                "logs_dir": str(self.logs_dir),
                "reports_dir": str(self.reports_dir),
                "tmp_dir": str(self.tmp_dir),
            },
        }

    def stage(self, message: str) -> None:
        line = f"[{datetime.now().isoformat()}] {message}\n"
        with self.stage_log.open("a", encoding="utf-8") as f:
            f.write(line)

    def run_cmd(
        self,
        cmd: List[str],
        stage_name: str,
        allow_fail: bool = True,
        timeout_sec: Optional[int] = None,
        source: str = "fallback",
    ) -> CommandResult:
        log_file = self.logs_dir / f"{self.run_id}-{stage_name}.log"
        start = time.time()
        self.stage(f"CMD {stage_name}: {' '.join(shlex.quote(c) for c in cmd)} source={source}")
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
            rc = proc.returncode
            out = proc.stdout or ""
            err = proc.stderr or ""
        except subprocess.TimeoutExpired as e:
            rc = 124
            out = e.stdout or ""
            err = (e.stderr or "") + f"\nTimeout after {timeout_sec} seconds."
        duration = time.time() - start

        payload = {
            "cmd": cmd,
            "source": source,
            "returncode": rc,
            "duration_sec": round(duration, 3),
            "stdout": out,
            "stderr": err,
        }
        with log_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        result = CommandResult(
            cmd=cmd,
            returncode=rc,
            stdout=out,
            stderr=err,
            log_file=str(log_file),
            duration_sec=duration,
            source=source,
        )
        if (not result.ok) and (not allow_fail):
            raise RuntimeError(f"Command failed in {stage_name}: {cmd}, see {log_file}")
        return result

    def discover_skills(self) -> Dict[str, List[str]]:
        roots = []
        if self.args.skills_root:
            roots.append(Path(self.args.skills_root).resolve())
        else:
            # Generic discovery: check current working dir and parents for ".cursor/skills".
            cwd = Path.cwd().resolve()
            for candidate in [cwd] + list(cwd.parents):
                roots.append(candidate / ".cursor" / "skills")
        # De-duplicate while preserving order.
        uniq_roots = []
        seen = set()
        for r in roots:
            key = str(r)
            if key not in seen:
                seen.add(key)
                uniq_roots.append(r)

        discovered = {}
        for root in uniq_roots:
            self.report["composition"]["skills_roots_scanned"].append(str(root))
            if not root.exists() or not root.is_dir():
                continue
            for skill_dir in root.iterdir():
                if not skill_dir.is_dir():
                    continue
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    discovered[skill_dir.name] = str(skill_md)
                    self.report["composition"]["skills_discovered"].append(
                        {"name": skill_dir.name, "skill_md": str(skill_md)}
                    )
        return discovered

    def add_check(
        self,
        name: str,
        status: str,
        source: str,
        summary: str,
        evidence: Dict,
        log_files: Optional[List[str]] = None,
    ) -> None:
        self.report["checks"].append(
            {
                "name": name,
                "status": status,
                "source": source,
                "summary": summary,
                "evidence": evidence,
                "log_files": log_files or [],
            }
        )
        if source.startswith("fallback"):
            self.report["composition"]["fallback_checks"].append(name)

    def check_static_env(self, skills: Dict[str, str]) -> Dict:
        source = "fallback:local-static"
        if "npu-smi" in skills:
            source = "reused-skill:npu-smi + fallback:local-static"
            self.report["composition"]["skills_used"].append(
                {
                    "skill": "npu-smi",
                    "input": {"command": "npu-smi info"},
                    "note": "Reused npu-smi capability by invoking npu-smi diagnostics command.",
                }
            )

        commands = [
            ("date", ["date"]),
            ("hostname", ["hostname"]),
            ("whoami", ["whoami"]),
            ("pwd", ["pwd"]),
            ("which_python", ["which", "python"]),
            ("python_version", ["python", "--version"]),
            ("pip_list", ["python", "-m", "pip", "list"]),
            ("pip_show_sglang", ["python", "-m", "pip", "show", "sglang"]),
            ("pip_show_torch", ["python", "-m", "pip", "show", "torch"]),
            ("pip_show_torch_npu", ["python", "-m", "pip", "show", "torch_npu"]),
            ("pip_show_transformers", ["python", "-m", "pip", "show", "transformers"]),
            ("pip_show_sgl_kernel_npu", ["python", "-m", "pip", "show", "sgl-kernel-npu"]),
            ("npu_smi_info", ["npu-smi", "info"]),
        ]
        collected = {}
        failed = []
        log_files = []
        for key, cmd in commands:
            res = self.run_cmd(cmd, f"static-{key}", allow_fail=True, source=source)
            collected[key] = {
                "returncode": res.returncode,
                "stdout": safe_text(res.stdout),
                "stderr": safe_text(res.stderr),
            }
            log_files.append(res.log_file)
            if not res.ok:
                failed.append(key)

        env_vars = {
            "ASCEND_HOME": os.environ.get("ASCEND_HOME", ""),
            "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH", ""),
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            "PATH": os.environ.get("PATH", ""),
        }
        env_log = self.logs_dir / f"{self.run_id}-static-env-vars.json"
        env_log.write_text(json.dumps(env_vars, ensure_ascii=False, indent=2), encoding="utf-8")
        log_files.append(str(env_log))

        if failed:
            status = STATUS_YELLOW
            summary = f"Static collection completed with partial failures: {', '.join(failed)}."
        else:
            status = STATUS_GREEN
            summary = "Static environment collection completed."

        self.add_check(
            name="static_environment_collection",
            status=status,
            source=source,
            summary=summary,
            evidence={"failed_commands": failed, "env_vars": env_vars, "commands": collected},
            log_files=log_files,
        )
        return collected

    def check_torch_npu_probe(self) -> Dict:
        probe_code = textwrap.dedent(
            """
            import json
            result = {
                "import_torch": False,
                "import_torch_npu": False,
                "torch_version": None,
                "torch_npu_version": None,
                "torch_npu_is_available": False,
                "torch_npu_device_count": 0,
                "tensor_on_npu_ok": False,
                "errors": []
            }

            try:
                import torch
                result["import_torch"] = True
                result["torch_version"] = getattr(torch, "__version__", None)
            except Exception as e:
                result["errors"].append(f"import torch failed: {e}")
                print(json.dumps(result, ensure_ascii=False))
                raise SystemExit(0)

            try:
                import torch_npu
                result["import_torch_npu"] = True
                result["torch_npu_version"] = getattr(torch_npu, "__version__", None)
            except Exception as e:
                result["errors"].append(f"import torch_npu failed: {e}")
                print(json.dumps(result, ensure_ascii=False))
                raise SystemExit(0)

            try:
                avail = bool(torch.npu.is_available())
                result["torch_npu_is_available"] = avail
            except Exception as e:
                result["errors"].append(f"torch.npu.is_available failed: {e}")
                avail = False

            try:
                count = int(torch.npu.device_count())
                result["torch_npu_device_count"] = count
            except Exception as e:
                result["errors"].append(f"torch.npu.device_count failed: {e}")
                count = 0

            if avail and count > 0:
                try:
                    x = torch.tensor([1.0], device="npu:0")
                    y = x + 1
                    result["tensor_on_npu_ok"] = bool(float(y.cpu().item()) == 2.0)
                except Exception as e:
                    result["errors"].append(f"tiny tensor probe failed: {e}")

            print(json.dumps(result, ensure_ascii=False))
            """
        ).strip()
        res = self.run_cmd(
            ["python", "-c", probe_code],
            "probe-torch-npu",
            allow_fail=True,
            source="fallback:python-probe",
        )
        data = {}
        try:
            data = json.loads(res.stdout.strip() or "{}")
        except json.JSONDecodeError:
            data = {"parse_error": "Unable to parse probe output", "raw_stdout": safe_text(res.stdout)}

        status = STATUS_GREEN
        summary = "PyTorch/NPU probe passed."
        if not data.get("import_torch", False):
            status = STATUS_RED
            summary = "torch import failed."
        elif not data.get("import_torch_npu", False):
            status = STATUS_RED
            summary = "torch_npu import failed, likely Python/package mismatch."
        elif not data.get("torch_npu_is_available", False):
            status = STATUS_RED
            summary = "torch.npu.is_available() is False although torch_npu imported."
        elif not data.get("tensor_on_npu_ok", False):
            status = STATUS_YELLOW
            summary = "NPU is visible but tiny tensor creation failed."

        self.add_check(
            name="torch_npu_probe",
            status=status,
            source="fallback:python-probe",
            summary=summary,
            evidence=data,
            log_files=[res.log_file],
        )
        return data

    def parse_help_options(self, help_text: str) -> Dict[str, bool]:
        def has(opt: str) -> bool:
            return opt in help_text

        return {
            "device": has("--device"),
            "attention_backend": has("--attention-backend"),
            "sampling_backend": has("--sampling-backend"),
            "load_format": has("--load-format"),
            "skip_tokenizer_init": has("--skip-tokenizer-init"),
            "skip_server_warmup": has("--skip-server-warmup"),
            "model_path": has("--model-path"),
            "port": has("--port"),
            "host": has("--host"),
            "tp": has("--tp"),
            "mem_fraction_static": has("--mem-fraction-static"),
            "device_id": has("--device-id"),
            "base_gpu_id": has("--base-gpu-id"),
        }

    def check_sglang_probe(self) -> Dict:
        check_env_res = self.run_cmd(
            ["python", "-m", "sglang.check_env"],
            "probe-sglang-check-env",
            allow_fail=True,
            source="fallback:sglang-check",
        )
        help_res = self.run_cmd(
            ["python", "-m", "sglang.launch_server", "--help"],
            "probe-sglang-launch-help",
            allow_fail=True,
            source="fallback:sglang-check",
        )

        opts = self.parse_help_options(help_res.stdout + "\n" + help_res.stderr) if help_res.stdout or help_res.stderr else {}
        ascend_related = {
            "contains_ascend_text": ("ascend" in (help_res.stdout + help_res.stderr).lower()),
            "device_option": opts.get("device", False),
            "attention_backend_option": opts.get("attention_backend", False),
            "sampling_backend_option": opts.get("sampling_backend", False),
        }

        status = STATUS_GREEN
        summary = "SGLang probes passed and launch help was parsed."
        if help_res.returncode != 0:
            status = STATUS_RED
            summary = "Failed to run sglang launch_server --help."
        elif not ascend_related["contains_ascend_text"]:
            status = STATUS_YELLOW
            summary = "SGLang help available but Ascend-related text/options not obvious."
        if check_env_res.returncode != 0 and status == STATUS_GREEN:
            status = STATUS_YELLOW
            summary = "sglang.check_env failed, but doctor continued with fallback probes."

        self.add_check(
            name="sglang_probe",
            status=status,
            source="fallback:sglang-check",
            summary=summary,
            evidence={
                "check_env_returncode": check_env_res.returncode,
                "check_env_stdout": safe_text(check_env_res.stdout),
                "check_env_stderr": safe_text(check_env_res.stderr),
                "launch_help_returncode": help_res.returncode,
                "launch_help_options": opts,
                "ascend_related": ascend_related,
            },
            log_files=[check_env_res.log_file, help_res.log_file],
        )
        return {"help_options": opts, "check_env_rc": check_env_res.returncode, "help_rc": help_res.returncode}

    def check_hccl(self, skills: Dict[str, str]) -> Dict:
        source = "fallback:local-hccl-check"
        if "hccl-test" in skills:
            source = "reused-skill:hccl-test + fallback:local-hccl-check"
            self.report["composition"]["skills_used"].append(
                {
                    "skill": "hccl-test",
                    "input": {"mode": "lightweight-env-only"},
                    "note": "Reused HCCL skill intent for environment signal capture without distributed test.",
                }
            )

        interesting_vars = {}
        for k, v in os.environ.items():
            if k.startswith("HCCL") or k.startswith("RANK_") or k in {
                "ASCEND_DEVICE_ID",
                "ASCEND_RT_VISIBLE_DEVICES",
                "ASCEND_VISIBLE_DEVICES",
            }:
                interesting_vars[k] = v

        ready_single_node = True
        distributed_hints = []
        if "RANK_TABLE_FILE" in interesting_vars or "HCCL_IF_IP" in interesting_vars:
            distributed_hints.append("Distributed environment hints found.")
        if "ASCEND_RT_VISIBLE_DEVICES" not in interesting_vars and "ASCEND_VISIBLE_DEVICES" not in interesting_vars:
            ready_single_node = True  # Not required for local single-card probe.

        status = STATUS_GREEN if ready_single_node else STATUS_YELLOW
        summary = "Lightweight HCCL env probe collected."
        if distributed_hints:
            summary += " Distributed hints detected."

        self.add_check(
            name="hccl_probe",
            status=status,
            source=source,
            summary=summary,
            evidence={
                "hccl_env_vars": interesting_vars,
                "single_node_ready": ready_single_node,
                "distributed_hints": distributed_hints,
            },
            log_files=[],
        )
        return {"single_node_ready": ready_single_node, "vars": interesting_vars}

    def _parse_npu_ids_from_text(self, text: str) -> List[int]:
        ids = set()
        # Common patterns seen in npu-smi outputs.
        for m in re.finditer(r"NPU\s*ID\s*[:=]\s*(\d+)", text, flags=re.IGNORECASE):
            ids.add(int(m.group(1)))
        for m in re.finditer(r"\|\s*(\d+)\s+\w+", text):
            val = int(m.group(1))
            if 0 <= val <= 63:
                ids.add(val)
        return sorted(ids)

    def _parse_busy_npus_from_text(self, text: str) -> List[int]:
        busy = set()
        lines = text.splitlines()
        in_proc = False
        for line in lines:
            if re.search(r"process|pid", line, flags=re.IGNORECASE):
                in_proc = True
                continue
            if in_proc:
                if re.match(r"^\s*[-=]+\s*$", line):
                    continue
                # Best-effort: first integer in process section can be device id.
                nums = re.findall(r"\b\d+\b", line)
                if len(nums) >= 2:
                    did = int(nums[0])
                    pid = int(nums[1])
                    if pid > 0 and 0 <= did <= 63:
                        busy.add(did)
        return sorted(busy)

    def select_device(self, static_cmds: Dict, torch_probe: Dict, skills: Dict[str, str]) -> Dict:
        source = "fallback:device-selection"
        if "npu-smi" in skills:
            source = "reused-skill:npu-smi + fallback:device-selection"

        npu_text = ""
        npu_entry = static_cmds.get("npu_smi_info", {})
        npu_text += npu_entry.get("stdout", "") + "\n" + npu_entry.get("stderr", "")
        ids_from_smi = self._parse_npu_ids_from_text(npu_text)
        busy_from_smi = self._parse_busy_npus_from_text(npu_text)
        count_from_torch = int(torch_probe.get("torch_npu_device_count", 0) or 0)
        ids_from_torch = list(range(count_from_torch)) if count_from_torch > 0 else []

        all_ids = sorted(set(ids_from_smi + ids_from_torch))
        preferred = self.args.device_id
        selected = None
        blocked_reason = ""

        if preferred is not None:
            if preferred not in all_ids:
                blocked_reason = f"Requested device_id={preferred} is not in detected devices {all_ids}."
            elif preferred in busy_from_smi:
                blocked_reason = f"Requested device_id={preferred} appears busy in npu-smi."
            else:
                selected = preferred
        else:
            idle = [d for d in all_ids if d not in busy_from_smi]
            if idle:
                selected = idle[0]
            elif all_ids:
                blocked_reason = "No free/idle NPU detected for safe launch probe."
            else:
                blocked_reason = "No NPU device detected from torch probe or npu-smi output."

        if selected is not None:
            status = STATUS_GREEN
            summary = f"Selected device_id={selected} for launch probe."
        else:
            status = STATUS_YELLOW if all_ids else STATUS_RED
            summary = blocked_reason

        evidence = {
            "detected_ids_from_npu_smi": ids_from_smi,
            "detected_ids_from_torch": ids_from_torch,
            "busy_ids_from_npu_smi": busy_from_smi,
            "selected_device_id": selected,
            "preferred_device_id": preferred,
            "blocked_reason": blocked_reason,
        }
        self.add_check(
            name="npu_device_availability",
            status=status,
            source=source,
            summary=summary,
            evidence=evidence,
            log_files=[],
        )
        return evidence

    def _candidate_model_roots(self) -> List[Path]:
        roots = []
        if os.environ.get("HF_HOME"):
            roots.append(Path(os.environ["HF_HOME"]))
        if os.environ.get("HUGGINGFACE_HUB_CACHE"):
            roots.append(Path(os.environ["HUGGINGFACE_HUB_CACHE"]))
        if os.environ.get("MODELSCOPE_CACHE"):
            roots.append(Path(os.environ["MODELSCOPE_CACHE"]))

        cwd = Path.cwd()
        roots.extend(
            [
                cwd / "models",
                cwd / "model",
                cwd / ".cache" / "huggingface" / "hub",
                Path.home() / ".cache" / "huggingface" / "hub",
                Path.home() / ".cache" / "modelscope",
            ]
        )
        uniq = []
        seen = set()
        for r in roots:
            key = str(r.resolve()) if r.exists() else str(r)
            if key not in seen:
                seen.add(key)
                uniq.append(r)
        return uniq

    def _is_hf_model_dir(self, p: Path) -> bool:
        if not p.is_dir():
            return False
        markers = ["config.json", "tokenizer.json", "tokenizer_config.json", "model_index.json"]
        return any((p / m).exists() for m in markers)

    def _dir_size_bytes(self, p: Path, max_walk_files: int = 2000) -> int:
        total = 0
        count = 0
        for root, _, files in os.walk(p):
            for name in files:
                fp = Path(root) / name
                try:
                    total += fp.stat().st_size
                except OSError:
                    pass
                count += 1
                if count >= max_walk_files:
                    return total
        return total

    def select_model_path(self) -> Dict:
        source = "fallback:model-selection"
        selected = None
        method = ""
        reasons = []
        searched = []

        if self.args.model_path:
            p = Path(self.args.model_path).expanduser().resolve()
            if p.exists():
                selected = p
                method = "user-specified"
                reasons.append("User provided model path and it exists.")
            else:
                reasons.append(f"User-provided model path does not exist: {p}")

        if selected is None:
            candidates = []
            for root in self._candidate_model_roots():
                searched.append(str(root))
                if not root.exists():
                    continue
                # bounded scan, depth <= 3
                for d1 in [root] + [x for x in root.iterdir() if x.is_dir()][:120]:
                    if self._is_hf_model_dir(d1):
                        size_b = self._dir_size_bytes(d1)
                        candidates.append((size_b, d1))
                    for d2 in [x for x in d1.iterdir() if x.is_dir()][:40] if d1.is_dir() else []:
                        if self._is_hf_model_dir(d2):
                            size_b = self._dir_size_bytes(d2)
                            candidates.append((size_b, d2))

            if candidates:
                candidates.sort(key=lambda x: x[0])
                selected = candidates[0][1]
                method = "auto-discovered-local"
                reasons.append(f"Selected smallest discovered local HF-style model dir: {selected}")

        if selected is None:
            stub = self.tmp_dir / "stub-hf-model"
            stub.mkdir(parents=True, exist_ok=True)
            (stub / "config.json").write_text(
                json.dumps(
                    {
                        "architectures": ["LlamaForCausalLM"],
                        "hidden_size": 8,
                        "intermediate_size": 16,
                        "num_attention_heads": 1,
                        "num_hidden_layers": 1,
                        "vocab_size": 256,
                        "model_type": "llama",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (stub / "tokenizer_config.json").write_text(
                json.dumps({"model_max_length": 128, "tokenizer_class": "PreTrainedTokenizerFast"}, indent=2),
                encoding="utf-8",
            )
            (stub / "special_tokens_map.json").write_text(
                json.dumps({"bos_token": "<s>", "eos_token": "</s>", "unk_token": "<unk>"}, indent=2),
                encoding="utf-8",
            )
            selected = stub
            method = "synthetic-stub-model"
            reasons.append("No user/local model found; created tiny local stub model for launch-path validation.")

        status = STATUS_GREEN
        summary = f"Model path selected via {method}: {selected}"
        self.add_check(
            name="model_path_selection",
            status=status,
            source=source,
            summary=summary,
            evidence={
                "selected_model_path": str(selected),
                "selection_method": method,
                "search_roots": searched,
                "reasons": reasons,
            },
            log_files=[],
        )
        return {"path": str(selected), "method": method}

    def _pick_port(self, preferred: Optional[int] = None) -> int:
        if preferred:
            return preferred
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return int(s.getsockname()[1])

    def _is_port_open(self, host: str, port: int, timeout: float = 0.3) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            try:
                s.connect((host, port))
                return True
            except OSError:
                return False

    def minimal_launch_probe(self, sglang_help: Dict, device_sel: Dict, model_sel: Dict) -> Dict:
        opts = sglang_help.get("help_options", {}) or {}
        selected_device = device_sel.get("selected_device_id")
        if selected_device is None:
            self.add_check(
                name="minimal_launch_probe",
                status=STATUS_YELLOW,
                source="fallback:launch-probe",
                summary="Launch probe skipped: no free/idle NPU detected for safe launch test.",
                evidence={"blocked_reason": device_sel.get("blocked_reason", "unknown")},
                log_files=[],
            )
            return {"skipped": True}

        # Basic launch command construction with option-awareness.
        if not opts.get("model_path", False):
            self.add_check(
                name="minimal_launch_probe",
                status=STATUS_RED,
                source="fallback:launch-probe",
                summary="Cannot build launch command: --model-path option not found in sglang launch help.",
                evidence={"help_options": opts},
                log_files=[],
            )
            return {"skipped": False, "error": "missing-model-path-option"}

        host = "127.0.0.1"
        port = self._pick_port(self.args.port)
        cmd = ["python", "-m", "sglang.launch_server", "--model-path", model_sel["path"]]

        if opts.get("host", False):
            cmd += ["--host", host]
        if opts.get("port", False):
            cmd += ["--port", str(port)]
        if opts.get("device", False):
            cmd += ["--device", "npu"]
        if opts.get("attention_backend", False):
            cmd += ["--attention-backend", "ascend"]
        if opts.get("sampling_backend", False):
            cmd += ["--sampling-backend", "ascend"]
        if opts.get("load_format", False):
            cmd += ["--load-format", "dummy"]
        if opts.get("skip_tokenizer_init", False):
            cmd += ["--skip-tokenizer-init"]
        if opts.get("skip_server_warmup", False):
            cmd += ["--skip-server-warmup"]
        if opts.get("tp", False):
            cmd += ["--tp", "1"]
        if opts.get("mem_fraction_static", False):
            cmd += ["--mem-fraction-static", str(self.args.mem_fraction_static)]

        if opts.get("device_id", False):
            cmd += ["--device-id", str(selected_device)]
        elif opts.get("base_gpu_id", False):
            cmd += ["--base-gpu-id", str(selected_device)]

        launch_log = self.logs_dir / f"{self.run_id}-minimal-launch.log"
        self.stage(f"CMD minimal-launch: {' '.join(shlex.quote(c) for c in cmd)}")
        started = time.time()
        ready = False
        rc = None
        error_msg = ""
        proc = None
        try:
            with launch_log.open("w", encoding="utf-8") as f:
                f.write(json.dumps({"cmd": cmd, "selected_device_id": selected_device, "port": port}, indent=2) + "\n")
                proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)
                timeout = int(self.args.launch_timeout_sec)
                for _ in range(timeout):
                    if proc.poll() is not None:
                        rc = proc.returncode
                        break
                    if self._is_port_open(host, port):
                        ready = True
                        break
                    time.sleep(1)
                if rc is None and proc.poll() is not None:
                    rc = proc.returncode
        except Exception as e:
            error_msg = str(e)
            rc = -1
        finally:
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()

        elapsed = round(time.time() - started, 3)
        status = STATUS_GREEN if ready else STATUS_RED
        summary = "Minimal launch probe passed (server port became reachable)." if ready else "Minimal launch probe failed."
        if (not ready) and rc is None:
            status = STATUS_YELLOW
            summary = "Minimal launch probe inconclusive before timeout."

        evidence = {
            "command": cmd,
            "host": host,
            "port": port,
            "selected_device_id": selected_device,
            "model_selection_method": model_sel["method"],
            "ready": ready,
            "returncode": rc,
            "elapsed_sec": elapsed,
            "error": error_msg,
        }
        self.add_check(
            name="minimal_launch_probe",
            status=status,
            source="fallback:launch-probe",
            summary=summary,
            evidence=evidence,
            log_files=[str(launch_log)],
        )
        return evidence

    def diagnose(self) -> None:
        self.stage("START diagnose")
        skills = self.discover_skills()
        if "torch_npu" in skills:
            self.report["composition"]["skills_used"].append(
                {
                    "skill": "torch_npu",
                    "input": {"probe": "python import torch/torch_npu + torch.npu checks"},
                    "note": "Reused torch_npu skill intent via equivalent low-cost probe commands.",
                }
            )
        if not skills:
            self.report["composition"]["notes"].append(
                "No reusable local skills discovered from scanned roots; all checks ran via fallback logic."
            )

        static_cmds = self.check_static_env(skills)
        torch_probe = self.check_torch_npu_probe()
        sglang_probe = self.check_sglang_probe()
        self.check_hccl(skills)
        device_sel = self.select_device(static_cmds, torch_probe, skills)
        model_sel = self.select_model_path()
        self.minimal_launch_probe(sglang_probe, device_sel, model_sel)

        # Summary and heuristics.
        statuses = [c["status"] for c in self.report["checks"]]
        if statuses and all(s == STATUS_GREEN for s in statuses):
            overall = STATUS_GREEN
        elif any(s == STATUS_RED for s in statuses):
            overall = STATUS_RED
        else:
            overall = STATUS_YELLOW
        self.report["summary"]["overall_status"] = overall

        root_causes = []
        check_map = {c["name"]: c for c in self.report["checks"]}
        torch_check = check_map.get("torch_npu_probe", {})
        sgl_check = check_map.get("sglang_probe", {})
        launch_check = check_map.get("minimal_launch_probe", {})
        device_check = check_map.get("npu_device_availability", {})

        torch_e = torch_check.get("evidence", {})
        if not torch_e.get("import_torch_npu", True):
            root_causes.append("torch_npu import failed; likely Python env mismatch or package missing.")
        if torch_e.get("import_torch_npu", False) and not torch_e.get("torch_npu_is_available", True):
            root_causes.append("npu-smi may see cards but torch.npu.is_available() is false; likely driver/CANN/env mismatch.")
        sgl_e = sgl_check.get("evidence", {})
        if sgl_e.get("launch_help_returncode", 0) != 0:
            root_causes.append("SGLang launch entrypoint unavailable or broken in current Python environment.")
        elif not sgl_e.get("ascend_related", {}).get("contains_ascend_text", True):
            root_causes.append("SGLang build/help output lacks obvious Ascend options; possible incompatible or incomplete build.")
        if launch_check.get("status") == STATUS_RED:
            root_causes.append("Minimal launch failed; check sgl-kernel-npu/backend compatibility and launch args.")
        if device_check.get("status") in {STATUS_YELLOW, STATUS_RED} and not device_check.get("evidence", {}).get("selected_device_id", None):
            root_causes.append("No free/idle NPU available for safe launch probe; free one card or specify an idle device.")

        self.report["summary"]["likely_root_causes"] = root_causes
        self.report["summary"]["executive_summary"] = (
            f"Overall status is {overall}. "
            "This report validates Ascend environment readiness, SGLang backend availability, and minimal launch viability at low cost."
        )
        self.report["summary"]["next_commands"] = [
            f"python -m sglang.launch_server --help",
            f"python -c \"import torch, torch_npu; print(torch.npu.is_available(), torch.npu.device_count())\"",
            f"npu-smi info",
            f"bash {str(Path(__file__).with_name('run_env_doctor.sh'))} --output-dir {shlex.quote(str(self.output_dir))}",
        ]

        self.write_reports()
        self.stage("END diagnose")

    def write_reports(self) -> None:
        json_path = self.reports_dir / f"{self.run_id}-env-doctor-report.json"
        md_path = self.reports_dir / f"{self.run_id}-env-doctor-report.md"
        latest_json = self.reports_dir / "latest-env-doctor-report.json"
        latest_md = self.reports_dir / "latest-env-doctor-report.md"

        json_text = json.dumps(self.report, ensure_ascii=False, indent=2)
        json_path.write_text(json_text, encoding="utf-8")
        latest_json.write_text(json_text, encoding="utf-8")

        lines = []
        lines.append("# SGLang Ascend Env Doctor Report")
        lines.append("")
        lines.append(f"- Run ID: `{self.report['meta']['run_id']}`")
        lines.append(f"- Timestamp: `{self.report['meta']['timestamp']}`")
        lines.append(f"- Overall: `{self.report['summary']['overall_status']}`")
        lines.append("")
        lines.append("## Executive summary")
        lines.append(self.report["summary"]["executive_summary"])
        lines.append("")
        lines.append("## Scope")
        lines.append(self.report["summary"]["scope_note"])
        lines.append("")
        lines.append("## Reuse / composition")
        lines.append(f"- Skills roots scanned: `{', '.join(self.report['composition']['skills_roots_scanned'])}`")
        lines.append(
            f"- Skills discovered: `{', '.join([x['name'] for x in self.report['composition']['skills_discovered']]) or 'none'}`"
        )
        lines.append(
            f"- Skills used: `{', '.join([x['skill'] for x in self.report['composition']['skills_used']]) or 'none'}`"
        )
        lines.append(
            f"- Fallback checks used: `{', '.join(self.report['composition']['fallback_checks']) or 'none'}`"
        )
        if self.report["composition"]["notes"]:
            for n in self.report["composition"]["notes"]:
                lines.append(f"- Note: {n}")
        lines.append("")
        lines.append("## Check-by-check status")
        for c in self.report["checks"]:
            lines.append(f"### {c['name']}")
            lines.append(f"- Status: `{c['status']}`")
            lines.append(f"- Source: `{c['source']}`")
            lines.append(f"- Summary: {c['summary']}")
            if c["log_files"]:
                lines.append(f"- Logs: `{', '.join(c['log_files'])}`")
            ev = json.dumps(c["evidence"], ensure_ascii=False, indent=2)
            lines.append("")
            lines.append("```json")
            lines.append(safe_text(ev, limit=4000))
            lines.append("```")
            lines.append("")
        lines.append("## Likely root causes")
        if self.report["summary"]["likely_root_causes"]:
            for rc in self.report["summary"]["likely_root_causes"]:
                lines.append(f"- {rc}")
        else:
            lines.append("- No obvious root cause found.")
        lines.append("")
        lines.append("## Exact next commands")
        for cmd in self.report["summary"]["next_commands"]:
            lines.append(f"- `{cmd}`")

        md_text = "\n".join(lines) + "\n"
        md_path.write_text(md_text, encoding="utf-8")
        latest_md.write_text(md_text, encoding="utf-8")

        print(f"[REPORT] {json_path}")
        print(f"[REPORT] {md_path}")
        print(f"[REPORT] {latest_json}")
        print(f"[REPORT] {latest_md}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnose whether SGLang can run on Ascend NPU with minimum cost and no large model downloads by default."
    )
    parser.add_argument("--output-dir", required=True, help="Output directory root.")
    parser.add_argument("--model-path", default="", help="Optional model path.")
    parser.add_argument("--device-id", type=int, default=None, help="Optional preferred NPU device id.")
    parser.add_argument("--port", type=int, default=None, help="Optional preferred server port.")
    parser.add_argument("--mem-fraction-static", type=float, default=0.3, help="Memory fraction for minimal launch probe.")
    parser.add_argument("--launch-timeout-sec", type=int, default=40, help="Launch probe timeout in seconds.")
    parser.add_argument("--skills-root", default="", help="Optional skill root for composition discovery.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    doctor = EnvDoctor(args)
    try:
        doctor.diagnose()
    except Exception as e:
        doctor.stage(f"FATAL {e}")
        fatal_json = {
            "fatal_error": str(e),
            "run_id": doctor.run_id,
            "stage_log": str(doctor.stage_log),
        }
        fatal_path = doctor.reports_dir / f"{doctor.run_id}-fatal.json"
        fatal_path.write_text(json.dumps(fatal_json, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[FATAL] {e}", file=sys.stderr)
        print(f"[FATAL] {fatal_path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
