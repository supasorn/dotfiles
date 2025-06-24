import torch
import time
import argparse

def burn_gpu(duration_sec=60, vram_gb=8.0):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.set_default_dtype(torch.float16)  # use float16 for max compute density
    print(f"Using device: {torch.cuda.get_device_name(device)}")

    # Step 1: Allocate large tensors to fill VRAM
    print("Allocating tensors to fill VRAM...")
    gb = 1024 ** 3
    element_size = 2  # float16
    max_bytes = int(vram_gb * gb)
    tensor_list = []
    allocated = 0
    try:
        while allocated < max_bytes:
            side = 4096  # 4096x4096 ~= 128MB (float16)
            t = torch.randn((side, side), device=device)
            tensor_list.append(t)
            allocated += t.nelement() * element_size
    except RuntimeError:
        print("OOM during tensor allocation.")
    print(f"Allocated ~{allocated / gb:.2f} GB VRAM across {len(tensor_list)} tensors")

    # Step 2: Burn compute on all tensors in loop
    print(f"Running compute for {duration_sec} seconds...")
    start = time.time()
    dummy = torch.zeros_like(tensor_list[0])
    while time.time() - start < duration_sec:
        for i in range(len(tensor_list) - 1):
            a = tensor_list[i]
            b = tensor_list[i + 1]
            dummy += torch.matmul(a, b)  # actively uses memory and compute
        dummy = dummy * 0.99  # avoid optimization away

    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--vram", type=float, default=16.0, help="VRAM to allocate in GB")
    args = parser.parse_args()

    burn_gpu(args.duration, args.vram)

