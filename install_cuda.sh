cuda_version=12
while getopts v: flag
do
    case "${flag}" in
        v) cuda_version=${OPTARG};;
    esac
done
echo "Installing cuda_version: $cuda_version";
cuda = nvidia-cuda-runtime-cu${version}
python3 -m pip install --upgrade setuptools pip wheel
python3 -m pip install nvidia-pyindex
python3 -m pip install --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org ${cuda}