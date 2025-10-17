# Local Deployment Guide

## Overview

The vGPU Sizing Advisor now includes a simple one-click deployment feature. After calculating your recommended vGPU configuration, you can immediately deploy and test vLLM locally using Docker.

## User Workflow

1. **Calculate vGPU Profile**
   - Chat with the AI to describe your workload
   - Receive recommended vGPU configuration

2. **Click "Apply Configuration"**
   - A simple modal opens

3. **Enter HuggingFace Token**
   - Only requirement - no SSH, no VM configuration needed
   - Used for model downloads from HuggingFace

4. **Click "Apply Configuration" Button**
   - Docker container starts automatically
   - Real-time progress and monitoring info

5. **View Results**
   - **DEPLOYMENT RESULTS** section (shown first) with GPU monitoring
   - **DEBUG OUTPUT** section (shown at bottom)
   - Export logs if needed

## What Gets Deployed

The deployment:
- Runs `docker run` with NVIDIA GPU support
- Starts vLLM container (`my_vllm_container`)
- Exposes API on port 8000
- Configures based on your vGPU profile
- Tests inference endpoint

## Output Format

### Header
```
=== vLLM Deployment Export ===
Date: 10/17/2025, 02:15:30 PM
Mode: Local Docker Deployment
============================================================
```

### DEPLOYMENT RESULTS (Shown First)
```
NVIDIA Driver: 575.64.03
=== vLLM Server Configuration Completed Successfully ===
• Model: mistralai/Mistral-7B-Instruct-v0.3
• Status: ✅ vLLM running and allocated 22.05 GB
• GPU Detected: NVIDIA L40S
• GPU Memory Utilization Setting: 46%
• Max Model Length: 8192 tokens
• KV Cache: 8192 tokens
Hardware Usage During Test:
• GPU Compute Utilization: 0%
• GPU Memory Active: 48%
• GPU Temperature: 39°C
• Power Draw: 240.73W / 350.00W
Advisor System Configuration:
• vGPU Profile: L40S-24Q
• vCPUs: 8
• System RAM: 64 GB
• GPU Memory Size: 21 GB
Configuration Validation:
✅ GPU matches recommended profile (L40S-24Q)
✅ GPU memory usage (22.1GB) matches estimate (21.0GB)
Actual usage vs expected usage: 105%
vLLM deployment successful
```

### DEBUG OUTPUT (Shown at Bottom)
```
=== DEBUG OUTPUT ===

Starting configuration test...
Checking NVIDIA GPU availability...
GPU detected: NVIDIA L40S, 46068 MiB
NVIDIA Driver: 575.64.03
GPU matches requested profile: L40S-24Q (match score: 0.53)
Checking Docker installation...
Docker version: Docker version 24.0.5
Checking for existing vLLM processes...
Cleared any existing vLLM processes
Starting vLLM server with model: mistralai/Mistral-7B-Instruct-v0.3...
Starting vLLM (GPU util: 46%, max tokens: 8192)...
vLLM server starting (Container: a1b2c3d4e5f6)
Waiting for vLLM server to initialize...
vLLM server is ready
Verifying vLLM process is running...
Testing inference endpoint with prompt: Explain what a vGPU is
Inference response: GPU virtualization is a technology that enables...
```

## Prerequisites

- **Docker** with NVIDIA Container Toolkit installed
- **NVIDIA GPU** with drivers installed
- **HuggingFace Token** for model downloads

**No SSH setup needed** - everything runs locally!

## Testing the Deployment

After deployment completes, test the API:

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  --data '{
    "model": "mistralai/Mistral-7B-Instruct-v0.3",
    "messages": [
      {
        "role": "user",
        "content": "Explain what a vGPU is"
      }
    ]
  }'
```

## Managing the Container

```bash
# View logs
docker logs my_vllm_container

# Stop container
docker stop my_vllm_container

# Remove container
docker rm my_vllm_container

# Check status
docker ps | grep my_vllm_container
```

## Files Modified

### Backend
- `src/apply_configuration.py`:
  - `deploy_vllm_local()` function - Runs Docker containers
  - `ApplyConfigurationRequest` model - Simplified to only require HF token
  - Removed all SSH-related code
  - Collects debug logs during execution
  - Outputs DEPLOYMENT RESULTS first, DEBUG OUTPUT at end

- `src/server.py`:
  - `/apply-configuration` endpoint - Always deploys locally
  - Removed `/test-ssh-connection` endpoint
  - Removed all SSH imports and functions

### Frontend
- `frontend/src/app/api/apply-configuration/route.ts`:
  - Handles local deployment requests only
  - Always uses `deployment_mode: 'local'`
  - Simplified request validation

- `frontend/src/app/components/Chat/ApplyConfigurationForm.tsx`:
  - Removed deployment mode tabs
  - Removed all VM/SSH/remote fields
  - Only requires HuggingFace token
  - Simple "Apply Configuration" button

### Documentation
- `README.md` - Local-only deployment instructions
- `CHANGELOG.md` - Version 2.3.0 changes
- `DEPLOYMENT_GUIDE.md` - This guide

## Troubleshooting

### Container won't start
```bash
# Check if port 8000 is in use
sudo lsof -i :8000

# Check Docker logs
docker logs my_vllm_container
```

### GPU not detected
```bash
# Verify NVIDIA drivers
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Out of memory
- Lower `gpu_memory_utilization` in configuration
- Reduce `max_kv_tokens`
- Use a smaller model variant

## Summary

The deployment is now fully integrated into the UI with a simple workflow:
1. Calculate vGPU profile via chat
2. Click "Apply Configuration" button
3. Enter HuggingFace token (that's it!)
4. Click "Apply Configuration" to start
5. Watch container start and monitor GPU usage
6. View comprehensive deployment results and metrics

**Everything runs locally with Docker:**
- ✅ No SSH keys to manage
- ✅ No remote VM configuration
- ✅ No network complexity
- ✅ Just Docker + HuggingFace token
- ✅ Real-time GPU monitoring info
- ✅ Simple one-click deployment

