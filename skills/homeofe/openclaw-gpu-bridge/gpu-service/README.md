# GPU Service — FastAPI Backend

Runs on the GPU machine (Windows or Linux) and exposes ML inference via REST.

## Hardware Requirements

- **GPU:** NVIDIA with ≥8GB VRAM (tested: RTX 2080 Ti 11GB)
- **CUDA:** 12.1+ recommended
- **RAM:** 16GB+ system RAM
- **Python:** 3.10+

## Windows Setup (Recommended for v0.1)

### 1. Install Python 3.10+

Download from [python.org](https://www.python.org/downloads/) or use `winget`:
```cmd
winget install Python.Python.3.12
```

### 2. Create virtual environment

```cmd
cd gpu-service
python -m venv venv
venv\Scripts\activate
```

### 3. Install PyTorch with CUDA

```cmd
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 4. Install dependencies

```cmd
pip install -r requirements.txt
```

### 5. Run the service

```cmd
uvicorn gpu_service:app --host 0.0.0.0 --port 8765
```

Or directly:
```cmd
python gpu_service.py
```

The service will:
1. Auto-detect your GPU via `torch.cuda.is_available()`
2. Pre-load BERTScore (`roberta-large`) and embedding (`all-MiniLM-L6-v2`) models
3. Listen on `http://0.0.0.0:8765`

First startup takes 1-2 minutes (model downloads). Subsequent starts are ~15s.

### 6. Verify

```cmd
curl http://localhost:8765/health
curl http://localhost:8765/info
```

### Windows Firewall

Allow inbound TCP port 8765 so the OpenClaw Linux server can reach the service:
```powershell
New-NetFirewallRule -DisplayName "GPU Service" -Direction Inbound -Port 8765 -Protocol TCP -Action Allow
```

## Linux Setup

Same steps but with bash:
```bash
cd gpu-service
python3 -m venv venv
source venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
uvicorn gpu_service:app --host 0.0.0.0 --port 8765
```

## Docker (Optional)

A `Dockerfile` is included for containerized NVIDIA/CUDA deployment:

```bash
docker build -t gpu-service .
docker run --gpus all -p 8765:8765 gpu-service
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TORCH_DEVICE` | auto-detect | Force device (`cuda`, `cpu`) |
| `MODEL_BERTSCORE` | `roberta-large` | BERTScore model |
| `MODEL_EMBED` | `all-MiniLM-L6-v2` | Embedding model |
| `GPU_MAX_CONCURRENT` | `2` | Max concurrent GPU requests |
| `API_KEY` | (none) | If set, requires `X-API-Key` header |

## AMD ROCm (Future)

The architecture supports AMD GPUs via PyTorch's ROCm build. `torch.cuda.is_available()` returns `True` for both CUDA and ROCm. To run on AMD:

1. Install PyTorch ROCm build: `pip install torch --index-url https://download.pytorch.org/whl/rocm6.0`
2. Everything else is identical — no code changes needed.

A `Dockerfile.rocm` will be added when AMD hardware is available for testing.

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Liveness check |
| `/info` | GET | GPU info + loaded models |
| `/bertscore` | POST | BERTScore computation |
| `/embed` | POST | Text embeddings |
