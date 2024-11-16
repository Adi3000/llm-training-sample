## Prerequistes

### Using CUDA 12.4

```bash
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
pip install bitsandbytes
conda install --yes --file requirements.txt  -c pytorch -c nvidia -c conda-forge
```

### Using CPU

```bash


conda install pytorch torchvision torchaudio cpuonly -c pytorch
pip install bitsandbytes
conda install --yes --file requirements.txt -c pytorch  -c conda-forge
```