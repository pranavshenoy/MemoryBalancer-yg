#!/bin/bash

set -e
set -x

#cleanup
mkdir -p log

mem_balancer_dir=$PWD
cd $mem_balancer_dir

# if [ ! -d  "$mem_balancer_dir/../depot_tools" ]; then 
#     echo "Pulling depot_tools"
#     cd ../
#     git clone https://chromium.googlesource.com/chromium/tools/depot_tools
# else
#     echo "depot_tool exists"
# fi
# export PATH="$PWD/depot_tools:$PATH"
# # ./clean_log
# # ./clean_out
# cd $mem_balancer_dir
# echo "** Pulling submodules **"
# git submodule init
# git submodule update
# git submodule sync

cd $mem_balancer_dir

echo "V8 should be in $PWD"
if [ ! -d  "$mem_balancer_dir/../v8" ]; then
    echo "** fetching changes in v8 **"
    cd ../
    /usr/bash fetch.sh
else 
    echo "v8 already present"
fi
# cd $mem_balancer_dir
# cd ../
# echo "** pulling Webkit if not present**"
# if [ ! -d  WebKit ] && git clone git@github.com:WebKit/WebKit.git

# cd $mem_balancer_dir
# cd ../v8/src
# git stash
# git checkout STABLE
# git pull origin STABLE
# gclient sync -f --no-history


# # echo "** cloning membalancer-paper **"
# # cd $mem_balancer_dir
# # cd "../"
# # [ ! -d "membalancer-paper" ] && git clone git@github.com:cputah/membalancer-paper.git

# cd $mem_balancer_dir
# echo "** building v8 **"
# make v8
# echo "** building memorybalancer **"
# make


# # echo "** running eval **"
# # python3 python/eval.py "jetstream"
# # python3 python/eval.py "acdc"
# # python3 python/gen.py --action=open
# # echo "** uploading results **"
# # result_dir=`ls "out" | sort -r | head -1`
# # if command -v nightly-results &>/dev/null; then
# #     nightly-results url "http://membalancer.uwplse.org/$result_dir"
# # fi
