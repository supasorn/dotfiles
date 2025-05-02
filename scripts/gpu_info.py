import subprocess

def get_gpu_users_with_processes():
    try:
        # Get the list of GPU processes: PID + full process name
        result = subprocess.run(
            ['nvidia-smi', '--query-compute-apps=pid,process_name', '--format=csv,noheader'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

        processes = []
        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) == 2 and parts[0].isdigit():
                pid, pname = parts
                # Get user
                ps_result = subprocess.run(
                    ['ps', '-o', 'user=', '-p', pid],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                user = ps_result.stdout.strip()
                processes.append((pid, user, pname))

        if processes:
            print("GPU Processes and their users:")
            for pid, user, pname in processes:
                print(f"PID: {pid} | User: {user} | Process: {pname}")
        else:
            print("No GPU processes found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_gpu_users_with_processes()

