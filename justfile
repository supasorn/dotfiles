set shell := ["bash", "-uc"]

# Just activate the default env
activatedefault:
    source ~/miniconda3/bin/activate /conda_envs/default

# Show memory info
meminfo:
    python ~/dotfiles/scripts/mem_info.py

nas-to-v26:
    sudo rsync -avh --delete /ist-nas/users/supasorn/singularity_slim/ /home/supasorn/singularity_slim/
    sudo rsync -avh --delete /ist-nas/users/supasorn/conda_envs/default/ /home/supasorn/conda_envs/

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

comfyui:
    source ~/miniconda3/bin/activate /conda_envs/default &&
    cd /projects/ComfyUI &&
    eval_and_hist CUDA_VISIBLE_DEVICES=0 python main.py --listen --port 9876

# Launch Stable-Diffusion WebUI via sg
dwui gpu="0":
    source ~/miniconda3/bin/activate /conda_envs/default &&
    cd /projects/stable-diffusion-webui &&
    eval_and_hist CUDA_VISIBLE_DEVICES={{gpu}} ./webui.sh \
        --gradio-auth-path au \
        --disable-safe-unpickle \
        --listen

dwui-forge gpu="0":
    source ~/miniconda3/bin/activate /conda_envs/default &&
    cd /projects/stable-diffusion-webui-forge &&
    eval_and_hist CUDA_VISIBLE_DEVICES={{gpu}} ./webui.sh \
        --gradio-auth-path au \
        --disable-safe-unpickle \
        --listen

depth_anything gpu="0":
    source ~/miniconda3/bin/activate /conda_envs/video_depth_anything && 
    cd /projects/DAVDA && 
    eval_and_hist CUDA_VISIBLE_DEVICES={{gpu}} python run.py --image

video_depth_anything gpu="0":
    source ~/miniconda3/bin/activate /conda_envs/video_depth_anything && 
    cd /projects/DAVDA && 
    eval_and_hist CUDA_VISIBLE_DEVICES={{gpu}} python run.py --video

framepack:
    source ~/miniconda3/bin/activate /conda_envs/default &&
    cd /projects/FramePack &&
    eval_and_hist CUDA_VISIBLE_DEVICES=0 python demo_gradio.py --server 0.0.0.0 --port 9875

mnt_v3:
    fusermount -u ~/mnt/v3 || true
    mkdir -p ~/mnt/v3
    sshfs -o IdentityFile=~/.ssh/id_rsa -o idmap=user v3:/ ~/mnt/v3

open-justfile-config:
    v ~/dotfiles/justfile

install-just:
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to DEST && sudo cp DEST/just /usr/bin && rm -rf DEST

img3dviewer:
    source ~/miniconda3/bin/activate /conda_envs/default &&
    cd /host/data/supasorn/img3dviewer && load_nvm &&
    eval_and_hist node web.js -pw

tmux-remote-shells:
    ~/dotfiles/scripts/tmux_remote_shells.sh v1-v23

find-recent-files:
    find . -type f -name "*.*" -mmin -200

delete-recent-media-files minutes="180":
    ~/dotfiles/scripts/delete_recent_files.sh {{minutes}}

rg-files-recursive file:
    rg --files --no-ignore | rg {{file}}

rg-search-text-one-level text:
    rg --max-depth=1 {{text}}

python-http-server port="8000":
    python -m http.server {{port}}

