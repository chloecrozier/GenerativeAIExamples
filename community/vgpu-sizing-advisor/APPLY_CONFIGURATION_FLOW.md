# Apply Configuration Flow

## Overview
This document describes the updated "Apply Configuration" flow for the vGPU Sizing Advisor.

## Flow Steps

### 1. User Clicks "Apply Configuration"
- Frontend sends request to `/api/apply-configuration` with HuggingFace token and vGPU configuration

### 2. Backend Process (deploy_vllm_local)

#### Step-by-Step Execution:

1. **Starting configuration test**
   - Initializes deployment process

2. **Check NVIDIA GPU availability**
   - Runs `nvidia-smi` to detect GPU
   - Captures: GPU name, total memory, driver version
   - Output: `✓ GPU detected: NVIDIA L40S, 46068 MiB`
   - Output: `✓ NVIDIA Driver: 575.64.03`

3. **Check Docker installation**
   - Verifies Docker is available
   - Output: `✓ Docker version 24.0.x`

4. **Authenticate with HuggingFace**
   - Validates HF token is provided
   - Output: `✓ HuggingFace token provided` or warning if missing

5. **Check for existing vLLM containers**
   - Stops and removes any existing `my_vllm_container`
   - Output: `✓ Cleared any existing vLLM processes`

6. **Pull vLLM Docker image**
   - Docker pulls `vllm/vllm-openai:latest`
   - Output: `Step 6: Pulling vLLM Docker image (this may take a few minutes)...`

7. **Start vLLM server with model**
   - Starts container with:
     - Model from HuggingFace
     - GPU memory utilization setting
     - Max model length (KV cache size)
     - HF token for authentication
   - Output: `✓ vLLM container started (Container ID: abc123...)`

8. **Wait for vLLM initialization**
   - Polls health endpoint every 10s (max 10 minutes)
   - Waits for model download and loading
   - Progress updates: `⏳ Waiting for vLLM to start listening on port 8000... (30s elapsed)`
   - Output: `✓ vLLM server is ready (took 60s)`

9. **Verify process and capture metrics**
   - Captures GPU metrics:
     - GPU memory used (MB)
     - GPU compute utilization (%)
     - GPU memory active (%)
     - GPU temperature (°C)
     - Power draw (W) / Power limit (W)
     - KV cache size (tokens)

10. **Test inference endpoint**
    - Sends test prompt: "Explain the concept of GPU virtualization in 2-3 sentences."
    - Captures inference response
    - Output: `✓ Inference test successful`

11. **Stop and remove container (cleanup)**
    - Stops the vLLM container
    - Removes the container
    - Output: `✓ Container stopped`
    - Output: `✓ Container removed`

### 3. Display Results

#### Deployment Results Format:
```
=== DEPLOYMENT RESULTS ===

NVIDIA Driver: 575.64.03
=== vLLM Server Configuration Completed Successfully ===
• Model: mistralai/Mistral-7B-Instruct-v0.3
• Status: ✅ vLLM running and allocated 22.05 GB
• GPU Detected: NVIDIA L40S
• GPU Memory Utilization Setting: 46%
• Max Model Length: 8192 tokens
• KV Cache: 57088 tokens
Hardware Usage During Test:
• GPU Compute Utilization: 0%
• GPU Memory Active: 0%
• GPU Temperature: 39°C
• Power Draw: 240.73W / 350.00W
Advisor System Configuration:
• vGPU Profile: L40S-24Q
• vCPUs: 8
• System RAM: 64 GB
• GPU Memory Size: 21 GB
Configuration Validation:
✅ GPU matches recommended profile (L40S-24Q)
✅ GPU memory usage (22.1GB) within expected range (21.0GB target)
Actual usage vs expected: 105%

Inference Test Result:
GPU virtualization is a technology that enables multiple applications to share a single physical GPU...

✅ vLLM deployment successful
```

#### Debug Output:
```
=== DEBUG OUTPUT ===

Starting configuration test...
Checking NVIDIA GPU availability...
GPU detected: NVIDIA L40S, 46068 MiB
NVIDIA Driver: 575.64.03
GPU matches requested profile: L40S-24Q (match score: 0.53)
Checking Docker installation...
Docker version: Docker version 24.0.7
HuggingFace token configured
Checking for existing vLLM processes...
Cleared any existing vLLM processes
Starting vLLM server with model: mistralai/Mistral-7B-Instruct-v0.3...
Starting vLLM (GPU util: 46%, max tokens: 8192)...
vLLM server starting (Container: abc123def456)
Waiting for vLLM server to initialize (model download + loading may take 5-10 minutes)...
Waiting for vLLM to start listening on port 8000... (10s elapsed)
Waiting for vLLM to start listening on port 8000... (20s elapsed)
Waiting for vLLM to start listening on port 8000... (30s elapsed)
vLLM server is ready
Verifying vLLM process is running...
Testing inference endpoint with prompt: Explain the concept of GPU virtualization in 2-3 sentences.
Inference response: GPU virtualization is a technology...
Stopping vLLM container...

Deployment completed successfully!
Stopping vLLM container (cleanup)...

✅ vLLM deployment successful
```

## Key Features

### Real-time Progress Updates
- UI shows step-by-step progress during deployment
- Users can see what's happening at each stage
- Clear visual feedback with ✓, ⏳, and ⚠ symbols

### Comprehensive Metrics
- GPU driver information
- GPU type and memory
- Expected vs actual memory usage comparison
- Hardware utilization (compute, memory, temperature, power)
- KV cache size
- Inference response validation

### Automatic Cleanup
- Container is stopped and removed after testing
- Cleanup occurs even on error
- No lingering containers consuming resources

### Error Handling
- Timeouts after 10 minutes if model doesn't load
- Container cleanup on any error
- Clear error messages to user

## Files Modified

1. **src/server.py**
   - Fixed SSE stream closure issues (removed empty yields)
   - Ensured proper stream termination

2. **src/apply_configuration.py**
   - Added step-by-step progress updates
   - Added HuggingFace authentication visibility
   - Added automatic container cleanup after inference
   - Enhanced error handling with cleanup
   - Improved output formatting to match requirements

## Testing

To test the flow:
1. Open the vGPU Sizing Advisor UI
2. Generate a vGPU configuration recommendation
3. Click "Apply Configuration"
4. Enter HuggingFace token
5. Watch the step-by-step progress
6. Verify results show all metrics
7. Confirm container is cleaned up (run `docker ps` - should not see my_vllm_container)

