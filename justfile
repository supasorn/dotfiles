set shell := ["bash", "-uc"]
# Just activate the default env
activatedefault:
    source ~/miniconda3/bin/activate /conda_envs/default

# Show memory info
meminfo:
    python ~/dotfiles/scripts/mem_info.py

# Sync from NAS to IST
[confirm]
nas-to-ist:
    sudo rsync -avh /ist-nas/users/supasorn/singularity_slim/ /ist/users/supasorn/singularity_slim/

[confirm]
nas-to-ist-del:
    sudo rsync -avh --delete /ist-nas/users/supasorn/singularity_slim/ /ist/users/supasorn/singularity_slim/

# Sync from IST to NAS
[confirm]
ist-to-nas:
    sudo rsync -avh /ist/users/supasorn/singularity_slim/ /ist-nas/users/supasorn/singularity_slim/

[confirm]
ist-to-nas-del:
    sudo rsync -avh --delete /ist/users/supasorn/singularity_slim/ /ist-nas/users/supasorn/singularity_slim/

# Download a file (pass the URL as the argument)
download url:
    curl -SL -O {{url}}

gotocomfyui:
    source ~/miniconda3/bin/activate && \
    conda activate /conda_envs/default && \
    cd /projects/ComfyUI

gotocomfyui-sg:
    sg --cmd "source ~/miniconda3/bin/activate && \
            conda activate /conda_envs/default && \
            cd /projects/ComfyUI"

# Launch Stable-Diffusion WebUI via sg
dwui:
    source ~/miniconda3/bin/activate && \
               conda activate /conda_envs/default && \
               cd /projects/stable-diffusion-webui && \
               CUDA_VISIBLE_DEVICES=1 ./webui.sh \
                 --gradio-auth-path pw.txt \
                 --disable-safe-unpickle \
                 --listen

dwui-sg:
    sg --cmd "source ~/miniconda3/bin/activate && \
               conda activate /conda_envs/default && \
               cd /projects/stable-diffusion-webui && \
               CUDA_VISIBLE_DEVICES=1 ./webui.sh \
                 --gradio-auth-path pw.txt \
                 --disable-safe-unpickle \
                 --listen"

# Depth-Anything (image)
depth_anything:
    source ~/miniconda3/bin/activate && \
               conda activate /conda_envs/video_depth_anything && \
               cd /projects/DAVDA && \
               CUDA_VISIBLE_DEVICES=0 python run.py \
                 --image \
                 --path=/host/home/supasorn/mnt/v3/data/supasorn/img3dviewer/images/

depth_anything-sg:
    sg --cmd "source ~/miniconda3/bin/activate && \
               conda activate /conda_envs/video_depth_anything && \
               cd /projects/DAVDA && \
               CUDA_VISIBLE_DEVICES=0 python run.py \
                 --image \
                 --path=/host/home/supasorn/mnt/v3/data/supasorn/img3dviewer/images/"

video_depth_anything:
    source ~/miniconda3/bin/activate && \
               conda activate /conda_envs/video_depth_anything && \
               cd /projects/DAVDA && \
               CUDA_VISIBLE_DEVICES=0 python run.py \
                 --video \
                 --path=/host/home/supasorn/mnt/v3/data/supasorn/img3dviewer/images/


video_depth_anything-sg:
    sg --cmd "source ~/miniconda3/bin/activate && \
               conda activate /conda_envs/video_depth_anything && \
               cd /projects/DAVDA && \
               CUDA_VISIBLE_DEVICES=0 python run.py \
                 --video \
                 --path=/host/home/supasorn/mnt/v3/data/supasorn/img3dviewer/images/"

framepack: 
    sg --cmd "source ~/miniconda3/bin/activate /conda_envs/default; cd /projects/FramePack; CUDA_VISIBLE_DEVICES=0 python demo_gradio.py --server 0.0.0.0 --port 9875"
