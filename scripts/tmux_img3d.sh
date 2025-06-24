tmux new-session \; \
split-window -h \; \
select-pane -t 1 \; \
split-window -v \; \
select-pane -t 3 \; \
split-window -v \; \
select-pane -t 3 \; \
split-window -v \; \
select-pane -t 1 \; send-keys "\ssh -t v3 'zsh -i -c \"r --sing img3dviewer\"'" C-m \; \
select-pane -t 2 \; send-keys "\ssh -t v3 'zsh -i -c \"r --sing dwui 0\"'" C-m \; \
select-pane -t 3 \; send-keys "\ssh -t v3 'zsh -i -c \"r --sing depth_anything 1\"'" C-m \; \
select-pane -t 4 \; send-keys "\ssh -t v2 'zsh -i -c \"r --sing video_depth_anything 0\"'" C-m  \; \
select-pane -t 5 \; send-keys "\ssh -t v3 'zsh -i -c \"cd /data/supasorn/img3dviewer && exec zsh\"'" C-m 
