VENV_NAME=soft_render

CONDA_PREFIX=$(conda info --base)

if [ ! -d $CONDA_PREFIX/envs/$VENV_NAME ]; then
    SYS_PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    conda create -n $VENV_NAME python=$SYS_PYTHON_VERSION -y
else
    echo "Conda environment '$VENV_NAME' already exists."
fi

eval "$(conda shell.bash hook)"
conda activate $VENV_NAME

echo "Activated $(python --version) in ($CONDA_PREFIX/envs/$VENV_NAME)"

python3 -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
python3 -m pip install -r requirements.txt

PROJECT_HOME=$(pwd)

function install_3rd_party() {
    tdir=$1
    cd $tdir
    python3 setup.py install
    cd $PROJECT_HOME
}



install_3rd_party downloads/DEODR
install_3rd_party downloads/SoftRas
install_3rd_party downloads/neural_renderer

