import numpy as np
import pandas as pd
from scipy.io import loadmat, savemat

# frames per second
fps = 15.0
# frames per task
fpt = 420
TR = 1.49

# 16 seconds of instructions
frame_sequence = np.zeros([768, 768, 300*fps])

ind = [0, 1, 0, 1, 2, 3, 2, 3]
reverse = [false, false, true, true, false, false, true, true]
#(check for all subjects, different version?...)
onsets = [15.982484, 47.265644, 78.564675, 109.847278, 153.145752, 184.427856, 215.727613, 247.010122]

task_frames = loadmat('bars.mat')['bars'].astype('float32')
#frames = np.load('apertures_bars.npz')['apertures']
print(task_frames.shape)

# Normalize to  values between 0 and 1... Current values ranges between 0 and 255
scaled_frames = task_frames / 255.0

def get_cycle(frames, index, flip_order):
    f = frames[:, :, index:index+fpt]
    if flip_order:
        f = np.flip(f, axis=2)
    return f

for i in range(8):
    idx_frames = ind[i]*28*15
    idx_seq = int(np.round(onsets[i] / (1.0/fps)))
    frame_sequence[:, :, ind_seq:ind_seq+fpt] = get_cycle(scaled_frames, idx_frames, reverse[i])

frame_TR = np.zeros([768, 768, int(np.ceil(300/TR))])

for f in range(frame_TR.shape[2]):
    idx_0 = int(np.round(f*fps*TR))
    idx_n = int(np.round((f+1)*fps*TR))
    frame_TR[:, :, f] = np.mean(frame_sequence[:, :, idx_0:idx_n], axis=2)

# Save output
dict = {}
dict['frames'] = frame_TR
savemat('/apertures', dict)
