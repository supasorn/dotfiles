from commands_helper import confirm
import os

def activate_default(): return rf"""source /opt/miniconda3/bin/activate /conda_envs/default"""

def activate_video_depth_anything(): 
    return """source /opt/miniconda3/bin/activate /conda_envs/video_depth_anything"""


def meminfo(): return rf"""
    python ~/dotfiles/scripts/mem_info.py
"""

def nas_to_v26(): return rf"""
    sudo rsync -avh --delete /ist-nas/users/supasorn/sing/ /home/supasorn/sing/
    sudo rsync -avh --delete /ist-nas/users/supasorn/conda_envs/default /home/supasorn/conda_envs/
"""

def nas_to_v3(): return rf"""
    sudo rsync -avh --delete /ist-nas/users/supasorn/sing/ /data/supasorn/sing/
"""

@confirm
def nas_to_ist(): return rf"""
    sudo rsync -avh /ist-nas/users/supasorn/sing/ /ist/users/supasorn/sing/
"""

@confirm
def nas_to_ist_del(): return rf"""
    sudo rsync -avh --delete /ist-nas/users/supasorn/sing/ /ist/users/supasorn/sing/
"""

@confirm
def ist_to_nas(): return rf"""
    sudo rsync -avh /ist/users/supasorn/sing/ /ist-nas/users/supasorn/sing/
"""

@confirm
def ist_to_nas_del(): return rf"""
    sudo rsync -avh --delete /ist/users/supasorn/sing/ /ist-nas/users/supasorn/sing/
"""

# comment
def download(url): return f"""
    curl -SL -O {url}
"""

def comfyui(): return rf"""
    {activate_default()} &&
    cd /projects/ComfyUI &&
    eval_and_hist CUDA_VISIBLE_DEVICES=0 python main.py --listen --port 9876
"""

# diffusion webui forge version
def dwui_forge(gpu="0"): return rf"""
    {activate_default()} &&
    cd /projects/stable-diffusion-webui-forge &&
    eval_and_hist CUDA_VISIBLE_DEVICES={gpu} ./webui.sh \
        --gradio-auth-path au \
        --disable-safe-unpickle \
        --listen
"""

def depth_anything(gpu="0"): return rf"""
    {activate_video_depth_anything()} && 
    cd /projects/DAVDA && 
    eval_and_hist CUDA_VISIBLE_DEVICES={gpu} python run.py --image
"""

def video_depth_anything(gpu="0"): return rf"""
    {activate_video_depth_anything()} && 
    cd /projects/DAVDA && 
    eval_and_hist CUDA_VISIBLE_DEVICES={gpu} python run.py --video
"""

def framepack(): return rf"""
    {activate_default()} &&
    cd /projects/FramePack &&
    eval_and_hist CUDA_VISIBLE_DEVICES=0 python demo_gradio.py --server 0.0.0.0 --port 9875
"""

def mnt_v3(): return rf"""
    fusermount -u ~/mnt/v3 || true
    mkdir -p ~/mnt/v3 
    sshfs -o IdentityFile=~/.ssh/id_rsa -o idmap=user v3:/ ~/mnt/v3
    ls ~/mnt/v3
"""

def open_commands(): return rf"""
    nvim {os.path.abspath(__file__)}
"""

def tmux_remote_shells(): return rf"""
    ~/dotfiles/scripts/tmux_remote_shells.sh v1-v24
"""

def find_recent_files(): return rf"""
    find . -type f -name "*.*" -mmin -200
"""

def delete_recent_media_files(minutes="180"): return rf"""
    ~/dotfiles/scripts/delete_recent_files.sh {minutes}
"""

def rg_files_recursive(file): return rf"""
    rg --files --no-ignore | rg {file}
"""

def rg_search_text_one_level(text): return rf"""
    rg --max-depth=1 {text}
"""

def python_http_server(port="8000"): return rf"""
    python -m http.server {port}
"""
