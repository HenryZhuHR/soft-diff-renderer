# 如果不存在目录 downloads/ 则创建、
if [ ! -d downloads ]; then
    mkdir -p downloads
fi

cd downloads

# 函数，用于clone指定的仓库
function clone_repo() {
    tdir=$1
    url=$2
    if [ ! -d $tdir ]; then
        git clone $url
    else
        cd $tdir
        # git pull
        cd ..
    fi
}


clone_repo DEODR git@github.com:martinResearch/DEODR.git
clone_repo SoftRas git@github.com:ShichenLiu/SoftRas.git
clone_repo neural_renderer git@github.com:wangyida/neural_renderer.git