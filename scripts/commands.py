from test_commands import confirm

def activatedefault(): return rf"""
    source /opt/miniconda3/bin/activate /conda_envs/default
"""

def meminfo(): return rf"""
    python ~/dotfiles/scripts/mem_info.py
"""

def nas_to_v26(): return rf"""
    sudo rsync -avh --delete /ist-nas/users/supasorn/sing/ /home/supasorn/sing/
    sudo rsync -avh --delete /ist-nas/users/supasorn/conda_envs/default /home/supasorn/conda_envs/
"""

def nas_to_ist(delete=False): return rf"""
    sudo rsync -avh {"--delete" if delete else ""} /ist-nas/users/supasorn/sing/ /ist/users/supasorn/sing/
"""

def source_video_depth_anything(): 
    return """source /opt/miniconda3/bin/activate /conda_envs/video_depth_anything"""

def depth_anything(gpu = "0"): return rf"""
    {source_video_depth_anything()} && 
    cd /projects/DAVDA && 
    eval_and_hist CUDA_VISIBLE_DEVICES={gpu} python run.py --image
"""

def video_depth_anything(gpu = "0"): return rf"""
    {source_video_depth_anything()} && 
    cd /projects/DAVDA && 
    eval_and_hist CUDA_VISIBLE_DEVICES={gpu} python run.py --video
"""

def test(arg0, gpu = "0"): return rf"""
    {source_video_depth_anything()} && 
    cd /projects/DAVDA && 
    eval_and_hist CUDA_VISIBLE_DEVICES={gpu} python run.py --video {arg0}
"""

# diffusion webui
def dwui(gpu="0"): return rf"""
    source /opt/miniconda3/bin/activate /conda_envs/default &&
    cd /projects/stable-diffusion-webui &&
    eval_and_hist CUDA_VISIBLE_DEVICES={gpu} ./webui.sh \
        --gradio-auth-path au \
        --disable-safe-unpickle \
        --listen
"""

# comment
@confirm
def download(url): return f"""
    curl -SL -O {url}
"""
