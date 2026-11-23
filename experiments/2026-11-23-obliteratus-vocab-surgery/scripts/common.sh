# Paths and container settings. Replace the three placeholders before use.
M=${STUDY_DIR:?set STUDY_DIR to the study working directory}
V=${OBLITERATUS_DIR:?set OBLITERATUS_DIR to an OBLITERATUS checkout at 1de580f7a13f185488dc31ff27f2e027545ad82d}
IMG=${IMAGE:?set IMAGE to a CUDA PyTorch image with transformers 5.17.0}
PY=/state/venv/bin/python
MEM=${MEM:-40g}
BASE=(--rm --network none --memory "$MEM" --memory-swap "$MEM" --user 1000:1000 -v "$M:/work"
  --env-file "$M/scripts/docker.env" -e HF_HUB_OFFLINE=1 -e HF_DATASETS_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1)
UP=(-v "$V:/upstream:ro" -v "$M/state-venv:/state/venv:ro" -e PYTHONPATH=/upstream)
GPU=(--gpus all --shm-size 4g -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True)
dock() { local name=$1; shift; docker run --name "om-$name" "$@"; }
model_env() { source "$M/scripts/models/$1.env"; }
