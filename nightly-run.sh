#!/bin/bash

# set -e
# set -x

#cleanup
# mkdir -p log


echo "Installing python2"
rm -rf /var/lib/dpkg/lock-frontend
# sudo apt update
sudo apt install python2
echo "python version:"

echo $(python -c 'import sys; print(sys.version_info[:])')

# mem_balancer_dir=$PWD
# deps_par_dir="$mem_balancer_dir/../.."
# cd $mem_balancer_dir

# if [ ! -d  "$deps_par_dir/depot_tools" ]; then 
#     echo "Pulling depot_tools"
#     cd "$deps_par_dir/"
#     git clone https://chromium.googlesource.com/chromium/tools/depot_tools
# else
#     echo "depot_tool exists"
# fi


# cd $mem_balancer_dir
# export PATH="$deps_par_dir/depot_tools:$PATH"
# export PATH=":$PATH"
# # # ./clean_log
# # # ./clean_out
# # cd $mem_balancer_dir
# echo "** Pulling submodules **"
# git submodule init
# git submodule update
# git submodule sync

# cd $mem_balancer_dir

# echo "V8 should be in $PWD"
# if [ ! -d  "$deps_par_dir/v8" ]; then
#     echo "** fetching changes in v8 **"
#     cd $deps_par_dir/
#     /usr/bin/bash "$mem_balancer_dir/fetch.sh"
#     gclient sync
# else 
#     echo "v8 already present"
# fi
# cd $mem_balancer_dir

# # sudo apt install generate-ninja
# # rm -rf "$deps_par_dir/v8/src/out.gn"
# # if [ ! -d "$deps_par_dir/v8/src/out.gn" ]; then
# #     cd $deps_par_dir/v8/src/
# #     export PATH="/home/pranav/Python-2.7.7/python:$PATH"
# #     echo $(which python)
# #     /home/pranav/Python-2.7.7/python tools/dev/v8gen.py x64.release.sample -vv
# # fi 


# if [ ! -d  "$deps_par_dir/WebKit" ]; then
#     echo "** pulling Webkit **"    
#     cd $deps_par_dir/
#     git clone git@github.com:WebKit/WebKit.git
# else 
#     echo "webkit present"
# fi

# # sudo chmod -R 777 $deps_par_dir/v8
# # sudo chown -R nightlies $deps_par_dir/v8

# cd $deps_par_dir/v8/src/
# git stash
# git checkout origin/2020-12-24
# git pull origin 2020-12-24
# gclient sync -f --no-history

# pip install ninja
# cd $mem_balancer_dir
# echo "** building v8 **"
# python -c 'import sys; print(sys.version_info[:])'
# make v8
# echo "** building memorybalancer **"
# make



# # # echo "** running eval **"
# # # python3 python/eval.py "jetstream"
# # # python3 python/eval.py "acdc"
# # # python3 python/gen.py --action=open
# # # echo "** uploading results **"
# # # result_dir=`ls "out" | sort -r | head -1`
# # # if command -v nightly-results &>/dev/null; then
# # #     nightly-results url "http://membalancer.uwplse.org/$result_dir"
# # # fi
