$cuda_version="12"
Write-Output "Installing cuda_version: $cuda_version"
$cuda = "nvidia-cuda-runtime-cu$cuda_version"
python3 -m pip install --upgrade setuptools pip wheel
python3 -m pip install nvidia-pyindex
Write-Output "Installing cuda: $cuda"
pip install --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org $cuda
#cffi without MINGW64
$env:PLAT_TO_VCVARS="--plat-name win32"