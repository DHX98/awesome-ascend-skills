#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'EOF'
Usage:
  run_env_doctor.sh [options]

Options:
  --output-dir <dir>          Output root directory. Default: ./sglang-ascend-env-doctor-output
  --model-path <path>         Optional model path for launch probe.
  --device-id <id>            Optional preferred NPU device id.
  --port <port>               Optional preferred port for launch probe.
  --mem-fraction-static <v>   Optional static memory fraction (default: 0.3).
  --launch-timeout-sec <sec>  Optional launch probe timeout seconds (default: 40).
  --skills-root <dir>         Optional skills root for composition discovery.
  -h, --help                  Show this help.

Examples:
  ./run_env_doctor.sh
  ./run_env_doctor.sh --output-dir ./out --device-id 0
  ./run_env_doctor.sh --model-path /path/to/local/model --port 31000
EOF
}

OUTPUT_DIR=""
MODEL_PATH=""
DEVICE_ID=""
PORT=""
MEM_FRACTION_STATIC="0.3"
LAUNCH_TIMEOUT_SEC="40"
SKILLS_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --model-path)
      MODEL_PATH="${2:-}"
      shift 2
      ;;
    --device-id)
      DEVICE_ID="${2:-}"
      shift 2
      ;;
    --port)
      PORT="${2:-}"
      shift 2
      ;;
    --mem-fraction-static)
      MEM_FRACTION_STATIC="${2:-}"
      shift 2
      ;;
    --launch-timeout-sec)
      LAUNCH_TIMEOUT_SEC="${2:-}"
      shift 2
      ;;
    --skills-root)
      SKILLS_ROOT="${2:-}"
      shift 2
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      show_help >&2
      exit 2
      ;;
  esac
done

if [[ -z "${OUTPUT_DIR}" ]]; then
  OUTPUT_DIR="$(pwd)/sglang-ascend-env-doctor-output"
fi

mkdir -p "${OUTPUT_DIR}/logs" "${OUTPUT_DIR}/reports" "${OUTPUT_DIR}/tmp"

RUN_TS="$(date +%Y%m%d-%H%M%S)"
RUN_LOG="${OUTPUT_DIR}/logs/${RUN_TS}-run_env_doctor.log"

{
  echo "[INIT] task=sglang-ascend-env-doctor"
  echo "[INIT] timestamp=${RUN_TS}"
  echo "[INIT] hostname=$(hostname 2>/dev/null || true)"
  echo "[INIT] whoami=$(whoami 2>/dev/null || true)"
  echo "[INIT] pwd=$(pwd)"
  echo "[INIT] output_dir=${OUTPUT_DIR}"
  echo "[INIT] python=${PYTHON_BIN:-python}"
  echo "[INIT] params model_path=${MODEL_PATH:-<none>} device_id=${DEVICE_ID:-<none>} port=${PORT:-<auto>} mem_fraction_static=${MEM_FRACTION_STATIC} launch_timeout_sec=${LAUNCH_TIMEOUT_SEC} skills_root=${SKILLS_ROOT:-<auto-discover>}"
} >> "${RUN_LOG}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD=("${PYTHON_BIN:-python}" "${SCRIPT_DIR}/env_doctor.py" "--output-dir" "${OUTPUT_DIR}" "--mem-fraction-static" "${MEM_FRACTION_STATIC}" "--launch-timeout-sec" "${LAUNCH_TIMEOUT_SEC}")

if [[ -n "${MODEL_PATH}" ]]; then
  PYTHON_CMD+=("--model-path" "${MODEL_PATH}")
fi
if [[ -n "${DEVICE_ID}" ]]; then
  PYTHON_CMD+=("--device-id" "${DEVICE_ID}")
fi
if [[ -n "${PORT}" ]]; then
  PYTHON_CMD+=("--port" "${PORT}")
fi
if [[ -n "${SKILLS_ROOT}" ]]; then
  PYTHON_CMD+=("--skills-root" "${SKILLS_ROOT}")
fi

{
  echo "[CMD] ${PYTHON_CMD[*]}"
} >> "${RUN_LOG}"

set +e
"${PYTHON_CMD[@]}" >> "${RUN_LOG}" 2>&1
RC=$?
set -e

{
  echo "[RESULT] exit_code=${RC}"
  if [[ ${RC} -eq 0 ]]; then
    echo "[STAGE] completed"
  else
    echo "[STAGE] failed"
  fi
  echo "[ARTIFACT] reports_dir=${OUTPUT_DIR}/reports"
  echo "[ARTIFACT] logs_dir=${OUTPUT_DIR}/logs"
  echo "[ARTIFACT] tmp_dir=${OUTPUT_DIR}/tmp"
} >> "${RUN_LOG}"

echo "Run log: ${RUN_LOG}"
echo "Reports: ${OUTPUT_DIR}/reports"
exit "${RC}"
