import subprocess
from pathlib import Path, PurePath
import time
import random
import sys
import json
import shutil
import os
import matplotlib.pyplot as plt
from git_check import get_commit
from util import tex_def, tex_fmt
import paper
from EVAL import *
import glob
import copy

# assert len(sys.argv) == 3
# mode = sys.argv[1]
# assert mode in ["jetstream", "browseri", "browserii", "browseriii", "acdc", "all", "macro"]

def make_path(in_path):
    path = in_path.joinpath(time.strftime("%Y-%m-%d-%H-%M-%S"))
    path.mkdir()
    return path

argc = len(sys.argv)
if argc > 1:
    root_dir = sys.argv[1]
else:
    root_dir = make_path(Path("log"))




BASELINE = {
    "BALANCE_STRATEGY": "ignore",
    "RESIZE_CFG": {"RESIZE_STRATEGY": "ignore"},
    "BALANCE_FREQUENCY": 0
}

YG_BALANCER = {
    "BALANCE_STRATEGY": "YG_BALANCER",
    "RESIZE_CFG": {"RESIZE_STRATEGY": "YG_BALANCER", "GC_RATE_D": 1},
    "BALANCE_FREQUENCY": 0
}

# js_c_range = [3, 5, 10, 20, 30] * 2
js_c_range = [3, 4, 5, 7, 10, 13, 15, 17, 20, 30] * 2
browser_c_range = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9]
acdc_c_range = [0.1 * i for i in range(1, 11)] + [1 * i for i in range(1, 11)]


def BALANCER_CFG(c_range, baseline_time=3, yg_balancer=10):
    return QUOTE(NONDET(*[{
        "BALANCE_STRATEGY": "classic",
        "RESIZE_CFG": {"RESIZE_STRATEGY": "gradient", "GC_RATE_D":NONDET(*[x / -1e9 for x in c_range])},
        "BALANCE_FREQUENCY": 0
    }] + baseline_time * [BASELINE] + yg_balancer * [YG_BALANCER]))

cfg_jetstream = {
    "LIMIT_MEMORY": True,
    "DEBUG": True,
    "TYPE": "jetstream",
    "MEMORY_LIMIT": 10000,
    # "BENCH": "box2d.js",
    # "BENCH": NONDET("pdfjs.js", "splay.js", "typescript.js", "box2d.js", "early-boyer.js"),
    "BALANCER_CFG": BALANCER_CFG(js_c_range, baseline_time=5)
}

eval_jetstream = {
    "Description": "Jetstream2 experiment",
    "NAME": "jetstream",
    "CFG": cfg_jetstream
}



flattened_cfgs = []
def flatten_config(cfg):
    if has_meta(cfg):
        for x in strip_quote(flatten_nondet(cfg)).l:
            flatten_config(x)
    else:
        flattened_cfgs.append(cfg)
flatten_config(eval_jetstream)


def add_more_benchmarks_to(config):
    all_cfgs = []
    for bm in ["pdfjs.js", "splay.js", "typescript.js", "box2d.js", "earley-boyer.js"]:
        for cfg in flattened_cfgs:
            new_cfg = copy.deepcopy(cfg)
            new_cfg["CFG"]["BENCH"] = bm
            all_cfgs.append(new_cfg)
    return all_cfgs


def run(cfgs, root_dir):
    for (idx, cfg) in enumerate(cfgs):
        exp_path = root_dir.joinpath(str(idx))
        exp_path.mkdir()
        with open(exp_path.joinpath("cfg"), "w") as f:
                f.write(str(cfg))
        cmd = f'python3 python/single_eval.py "{cfg}" {exp_path}'
        subprocess.run(cmd, shell=True, check=True)
        print(str(idx) + " " + str(cfg))

def get_dirs(path):
    dirs = glob.glob(path+"/*/")
    return dirs


def get_values_from(filename, key):
    res = []
    with open(filename) as f:
        for line in f.readlines():
            j = json.loads(line)
            # major_gc_time = j["total_major_gc_time"]
            res.append(j[key])
    return sum(res)
    

def compute_values(gc_file, mem_file):
    x = get_values_from(gc_file, "before_memory") - get_values_from(gc_file, "after_memory")
    y = get_values_from(gc_file, "total_gc_time")  #total_gc_time  total_major_gc_time
    return (x, y)


def read_cfg(dir):
    cfg = {}

    line = ""
    path = os.path.join(dir, "cfg")
    with open(path) as f:
        for l in f.readlines():
            line +=  l
    line = line.replace("'", '"')
    line = line.replace("True", "true")
    line = line.replace("False", "false")
    cfg = json.loads(line)
    print(cfg)
    return cfg


# res = {yg:{x: [val], y: [val]}, classic:{x: [val], y: [val]}, ignore:{x: [val], y: [val]}]}
def eval_jetstream(benchmark, root_dir):
    dirs = get_dirs(root_dir)
    result = {}
    for dir in dirs:
        cfg = read_cfg(dir)
        if cfg['CFG']['BENCH'] != benchmark:
            continue
        balance_type = cfg['CFG']['BALANCER_CFG']['BALANCE_STRATEGY']
        gc_file = glob.glob(dir+'/*.gc.log')[0]
        mem_file = glob.glob(dir+'/*.memory.log')[0]
        x, y = compute_values(gc_file, mem_file)
        if balance_type not in result.keys():
            result[balance_type] = {}
            result[balance_type]["x"] = []
            result[balance_type]["y"] = []
        result[balance_type]["x"].append(x)
        result[balance_type]["y"].append(y)

    return result

def plot(values, root_dir):
    colors = ["orange", "black", "blue"]
    plt.xlabel("Heap Memory (Bytes)")
    plt.ylabel("gc time (ns)")
    for (idx, key) in enumerate(values.keys()):
        size = len(values[key]["x"])
        plt.scatter([ x / size for x in values[key]["x"]], [ y / size for y in values[key]["y"]], label=key, linewidth=0.1, s=20, color=colors[idx])
    path = os.path.join(root_dir, "plot.png")
    plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left")
    plt.savefig(path, bbox_inches='tight')

#uncomment to run experiments
cfgs = add_more_benchmarks_to(eval_jetstream)
run(cfgs, root_dir)

# result = eval_jetstream("box2d.js", root_dir)
# plot(result, root_dir)    









