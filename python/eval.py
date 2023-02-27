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
import numpy as np

assert len(sys.argv) > 1
mode = sys.argv[1]
assert mode in ["run", "eval"]

def make_path(in_path):
    path = in_path.joinpath(time.strftime("%Y-%m-%d-%H-%M-%S"))
    path.mkdir()
    return path

if mode == "run":
    root_dir = make_path(Path("log"))
else:
    assert len(sys.argv) > 2
    root_dir = sys.argv[2]
    
benchmarks = ["pdfjs.js", "splay.js", "typescript.js", "box2d.js", "earley-boyer.js"]

js_c_range = [3, 5, 10, 20, 30]
# js_c_range = [3, 4, 5, 7, 10, 13, 15, 17, 20, 30] * 2
acdc_c_range = [0.1 * i for i in range(1, 11)] + [1 * i for i in range(1, 11)]



BASELINE = {
    "BALANCE_STRATEGY": "ignore",
    "RESIZE_CFG": {"RESIZE_STRATEGY": "ignore"},
    "BALANCE_FREQUENCY": 0
}

def get_cfg(balance_strategy, c_range):
    cfg = {
        "BALANCE_STRATEGY": balance_strategy,
        "RESIZE_CFG": {"RESIZE_STRATEGY": "gradient", "GC_RATE_D":NONDET(*[x / -1e9 for x in c_range])},
        "BALANCE_FREQUENCY": 0
    }
    return cfg

def BALANCER_CFG(c_range, baseline_time=5):
    # return QUOTE(NONDET(*[get_cfg("YG_BALANCER", c_range)]))
    return QUOTE(NONDET(*[get_cfg("classic", c_range)] + baseline_time * [BASELINE] + [get_cfg("YG_BALANCER", c_range)]))

cfg_jetstream = {
    "LIMIT_MEMORY": True,
    "DEBUG": True,
    "TYPE": "jetstream",
    "MEMORY_LIMIT": 10000,
    "BALANCER_CFG": BALANCER_CFG(js_c_range, baseline_time=2)
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
    for bm in benchmarks:
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
        # print(str(idx) + " " + str(cfg))

def get_dirs(path):
    print(path)
    dirs = glob.glob(str(path)+'/*/')
    return dirs


def get_values_from(filename, key):
        res = []
        with open(filename) as f:
            for line in f.readlines():
                j = json.loads(line)
                # major_gc_time = j["total_major_gc_time"]
                res.append(j[key])
        return res
    

def compute_values(gc_file, mem_file):
    x = sum(get_values_from(gc_file, "size_of_objects"))
    y = sum(get_values_from(gc_file, "total_gc_time"))
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
    # print(cfg)
    return cfg


# res = {yg:{x: [val], y: [val]}, classic:{x: [val], y: [val]}, ignore:{x: [val], y: [val]}]}
def eval_jetstream(benchmark, root_dir):
    dirs = get_dirs(root_dir)
    result = {}
    for dir in dirs:
        cfg =  read_cfg(dir)
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

def plot(values, root_dir, benchmark):
    colors = {"YG_BALANCER":"orange", "ignore": "black", "classic":"blue"}
    plt.figure()
    plt.xlabel("Heap Memory (Bytes)")
    plt.ylabel("gc time (ns)")
    for (idx, key) in enumerate(values.keys()):
        size = len(values[key]["x"])
        plt.scatter([ x / size for x in values[key]["x"]], [ y / size for y in values[key]["y"]], label=key, linewidth=0.1, s=20, color=colors[key])
    path = os.path.join(root_dir, benchmark+"-plot.png")
    plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left")
    plt.savefig(path, bbox_inches='tight')
    plt.close()

# class Wrapper: 
#     key = ""
#     legend = ""
#     label = ""
#     def __init__(self, key, legend, label):
#         self.key = key
#         self.legend = legend
#         self.label = label
        
class ParamWrapper:
    key = ""
    legend = ""
    operation = None
    def __init__(self, key, legend, operation):
        self.key = key
        self.legend = legend
        self.operation = operation        

class PlotWrapper:
    filename = ""
    x_axis = ""
    y_axis = ""
    items = []
    def __init__(self, filename, x_axis, y_axis, items):
        self.filename = filename
        self.y_axis = y_axis
        self.x_axis = x_axis
        self.items = items




def eval_single_run(config):

    colors = ["blue", "red", "black"]
    def plot(dir, config):
        cfg =  read_cfg(dir)
        balance_type = cfg['CFG']['BALANCER_CFG']['BALANCE_STRATEGY']
        if balance_type == "YG_BALANCER":
            print(dir)
        gc_file = glob.glob(dir+'/*.gc.log')[0]
        mem_file = glob.glob(dir+'/*.memory.log')[0]
        plt.figure()
        plt.title = balance_type
        plt.xlabel(config.x_axis)
        plt.ylabel(config.y_axis)
        for idx, item in enumerate(config.items):
            y = item.operation(gc_file)
            x = np.arange(0, len(y), 1)
            plt.plot(x, y, color=colors[idx], label=item.legend, linewidth=1)
        path = os.path.join(dir +config.filename)
        plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left")
        plt.savefig(path, bbox_inches='tight')
        plt.close()

    dirs = get_dirs(root_dir)
    result = {}
    for dir in dirs:
        plot(dir, config)



def eval_and_plot():
    for bm in benchmarks:
        result = eval_jetstream(bm, root_dir)
        print("Benchmark: "+ bm + " result: " + str(result))
        plot(result, root_dir, bm)

def old_gen_size_of_obj(gc_file):
    total = get_values_from(gc_file, "size_of_objects")
    yg = get_values_from(gc_file, "yg_size_of_object")
    res = []
    for idx, cur_total in enumerate(total):
        res.append(cur_total - yg[idx])
    return res

new_capacity = ParamWrapper("new_space_capacity", "young gen capacity (semispace)", lambda gc_file: get_values_from(gc_file, "new_space_capacity"))
old_capacity = ParamWrapper("Limit", "Old gen capacity", lambda gc_file: get_values_from(gc_file, "Limit"))
capacity_plot = PlotWrapper("capacity.png", "Progress", "Heap Limits (B)", [new_capacity, old_capacity])

yg_soo = ParamWrapper("yg_size_of_object", "yg", lambda gc_file: get_values_from(gc_file, "yg_size_of_object"))
og_soo = ParamWrapper("size_of_objects", "og", lambda gc_file: old_gen_size_of_obj(gc_file))
size_of_object_plot = PlotWrapper("size_of_obj.png", "Progress", "Size of objects (B)", [yg_soo, og_soo])


# yg_gc_time = ParamWrapper("yg_size_of_object", "young gen", lambda gc_file: get_values_from(gc_file, "yg_size_of_object"))
# og_gc_time = ParamWrapper("total_major_gc_time", "old gen", lambda gc_file: get_values_from(gc_file, "total_major_gc_time"))
# size_of_object_plot = PlotWrapper("size_of_obj.png", "Progress", "Size of objects (B)", [yg_soo, og_soo])

if mode == "run":
    cfgs = add_more_benchmarks_to(eval_jetstream)
    run(cfgs, root_dir)
eval_and_plot()
# eval_single_run(size_of_object_plot)

    









