import torch
import torch.utils.data as data
import torch.nn as nn
import os
from tqdm import tqdm
import pandas as pd
import torchaudio


class DataVAE(data.Dataset):
    def __init__(self, csv_path, data_path):
        self.csv = pd.read_csv(csv_path, sep='\t')
        self.path = [os.path.join(data_path, fpath) for fpath in self.csv['path']]
        self.sorted_paths = []
    
    def sort_len(self):
        lengths = []
        for p in tqdm(self.path):
            sig, sr = torchaudio.load(p)
            lengths.append((p, sig.shape[-1]))
        lengths = sorted(lengths, key=lambda x:x[1])
        for t in lengths:
            self.sorted_paths.append(t[0])
        
    def __len__(self):
        return len(self.csv)
    
    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        return self.sorted_paths[idx]


def collate_vae(data):
    '''
    For batch
    '''
    sample_rate = 160000
    get_MFCC = torchaudio.transforms.MFCC(sample_rate=sample_rate,
                                          n_mfcc=13,
                                          log_mels=True)
    get_deltas = torchaudio.transforms.ComputeDeltas()
    get_melspec = torchaudio.transforms.MelSpectrogram()

    def maxlen_fn(paths, fn):
        max_len=0
        for f in paths:
            sig, sr = torchaudio.load(f)
            sig = fn(sig)
            if sig.shape[1] > max_len:
                max_len = sig.shape[2]
        return int(max_len)

    
    batch = []
    maxlen = maxlen_fn(data, get_melspec)
    for audio in data:
        audio, sr = torchaudio.load(audio)
        #Extract features...
        mfcc = get_MFCC(audio)
        deltas = get_deltas(mfcc)
        ddeltas = get_deltas(deltas)
        feature = torch.cat([mfcc, deltas, ddeltas], dim=1).squeeze(0)
        batch_audio = nn.ZeroPad2d(padding=(0, maxlen-feature.shape[1], 0, 0))(feature)
        batch.append(batch_audio)

    return torch.stack(batch)