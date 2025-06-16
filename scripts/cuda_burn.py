import torch
import time
import argparse

def burn_gpu(duration_sec=60, vram_gb=8):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {torch.cuda.get_device_name(device)}")

    # Allocate VRAM (fill with large float32 tensors)
    tensors = []
    gb = 1024 ** 3
    tensor_size = (1024, 1024, 256)  # ~1 GB
    allocated = 0
    print("Allocating VRAM...")
    while allocated < vram_gb:
        try:
            t = torch.randn(tensor_size, device=device)
            tensors.append(t)
            allocated += t.element_size() * t.nelement() / gb
        except RuntimeError:
            print("Out of memory at {:.2f} GB".format(allocated))
            break
    print(f"Total allocated: {allocated:.2f} GB")

    # Burn compute
    print(f"Starting compute burn for {duration_sec} seconds...")
    A = torch.randn((2048, 2048), device=device)
    B = torch.randn((2048, 2048), device=device)
    start = time.time()
    i = 0
    while time.time() - start < duration_sec:
        C = torch.matmul(A, B)
        A, B = B, C  # rotate to keep data changing
        i += 1
        if i % 50 == 0:
            print(f"{i} matmuls done")

    print("Burn test finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--vram", type=float, default=8.0, help="Amount of VRAM to fill in GB")
    args = parser.parse_args()

    burn_gpu(args.duration, args.vram)

