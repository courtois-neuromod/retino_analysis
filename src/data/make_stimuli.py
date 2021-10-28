import os
import numpy as np
import pandas as pd
from scipy.io import loadmat, savemat

tasks = ['bars', 'rings', 'wedges']
TR = 1.49
# frames per second
fps = 15.0

stim_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/retinotopy/stimuli'
out_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/output'

for task in tasks:
    # frames per task
    fpt = 469 if task is 'wedges' else 420

    if task is 'bars':
        ind = [0, 1, 0, 1, 2, 3, 2, 3]
        reverse = [False, False, True, True, False, False, True, True]
        #task_frames = loadmat('bars.mat')['bars'].astype('float32')
        task_frames = np.load(os.path.join(stim_path, 'apertures_bars.npz'))['apertures']
    else:
        ind = np.repeat(0, 8)
        reverse = [False, False, False, False, True, True, True, True]
        if task is 'wedges':
            #task_frames = loadmat('wedges_newtr.mat')['wedges'].astype('float32')
            task_frames = np.load(os.path.join(stim_path, 'apertures_wedge_newtr.npz'))['apertures']
        else:
            #task_frames = loadmat('ring.mat')['ring'].astype('float32')
            task_frames = np.load(os.path.join(stim_path, 'apertures_ring.npz'))['apertures']

    print(task_frames.shape)
    # Normalize to  values between 0 and 1... Current values ranges between 0 and 255
    scaled_frames = task_frames / 255.0

    # Validated across 3 tasks, over sessions, for 3 subjects
    # Avg from sub-01, sub-02 and sub-03, ses-002 to ses-006
    onsets = [16.033847, 47.3222376, 78.615124, 109.897517, 153.194802, 184.478802, 215.772451, 247.061259]

    # 16 seconds of instructions, 4 cycles of ~32s, 12s pause, 4 cycles of ~32s, 16s of instructions
    # 202 TRs acquired
    frame_sequence = np.zeros([768, 768, int(300*fps)])

    def get_cycle(frames, index, flip_order):
        f = frames[:, :, index:index+fpt]
        if flip_order:
            f = np.flip(f, axis=2)
        return f

    # 8 cycles
    for i in range(8):
        idx_frames = ind[i]*28*15
        idx_seq = int(np.round(onsets[i] / (1.0/fps)))
        frame_sequence[:, :, idx_seq:idx_seq+fpt] = get_cycle(scaled_frames, idx_frames, reverse[i])

    savemat(os.path.join(out_path, task+'_per_frame.mat'), {task: frame_sequence.astype('bool')})

    # creating a set of frames for a particular slice
    # 15 = brain slices per TR (60 slices/ TR, with 4 multibands)
    # 300s / 1.49s = number of TRs (202)
    bslice_per_TR = 15

    total_slices = int(np.floor(300/TR)*15)
    frame_slice = np.zeros([768, 768, total_slices])

    for slice in range(total_slices):
        idx = int(np.round((slice * TR * fps) / bslice_per_TR))
        frame_slice[:, :, slice] = frame_sequence[:, :, idx]

    savemat(os.path.join(out_path, task+'_per_slice.mat'), {task: frame_slice.astype('bool')})

    for slice_num in range(bslice_per_TR):
        slice_frames = np.zeros([768, 768, int(np.ceil(300/TR))])

        for t in range(int(np.ceil(300/TR))):
            #idx = int(np.round((TR * t * fps) + slice_num*(TR/bslice_per_TR)*fps))
            idx = int(np.round(TR*fps*(t + (slice_num/bslice_per_TR))))
            slice_frames[:, :, t] = frame_sequence[:, :, idx]

        savemat(os.path.join(out_path, task+'_per_TR_slice' + str(slice_num) + '.mat'), {task + '_slice' + str(slice_num): slice_frames.astype('bool')})

    # frames averaged per TR
    frame_TR = np.zeros([768, 768, int(np.ceil(300/TR))])

    for f in range(frame_TR.shape[2]):
        idx_0 = int(np.round(f*fps*TR))
        idx_n = int(np.round((f+1)*fps*TR))
        frame_TR[:, :, f] = np.mean(frame_sequence[:, :, idx_0:idx_n], axis=2)

    # Save output
    dict = {}
    dict[task] = frame_TR.astype('f4')
    savemat(os.path.join(out_path, task+'_per_TR.mat'), dict)
