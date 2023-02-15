import subprocess
from pathlib import Path, PurePath
import time
import random
import sys
import json
import shutil
import os
from git_check import get_commit
from util import tex_def, tex_fmt
import paper
from EVAL import *
import glob

assert len(sys.argv) == 3
mode = sys.argv[1]
assert mode in ["jetstream", "browseri", "browserii", "browseriii", "acdc", "all", "macro"]

root_dir = sys.argv[2]



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
tex = ""
tex += tex_def("JSMinC", f"{tex_fmt(min(js_c_range))}\,\%/MB")
tex += tex_def("JSMaxC", f"{tex_fmt(max(js_c_range))}\,\%/MB")
tex += tex_def("WEBMinC", f"{tex_fmt(min(browser_c_range))}\,\%/MB")
tex += tex_def("WEBMaxC", f"{tex_fmt(max(browser_c_range))}\,\%/MB")
tex += tex_def("ACDCMinC", f"{tex_fmt(min(acdc_c_range))}\,\%/MB")
tex += tex_def("ACDCMaxC", f"{tex_fmt(max(acdc_c_range))}\,\%/MB")



if mode == "macro":
    exit()

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
    "BENCH": "box2d.js",
    # "BENCH": NONDET("pdfjs.js", "splay.js", "typescript.js", "box2d.js", "early-boyer.js"),
    "BALANCER_CFG": BALANCER_CFG(js_c_range, baseline_time=5)
}

eval_jetstream = {
    "Description": "Jetstream2 experiment",
    "NAME": "jetstream",
    "CFG": cfg_jetstream
}

cfg_acdc = {
    "LIMIT_MEMORY": True,
    "DEBUG": True,
    "TYPE": "acdc",
    "MEMORY_LIMIT": 10000,
    "BENCH": ["acdc"],
    "BALANCER_CFG": BALANCER_CFG(acdc_c_range, baseline_time = 20)
}

eval_acdc = {
    "Description": "ACDC-JS experiment",
    "NAME": "acdc",
    "CFG": cfg_acdc,
}

evaluation = []
if mode in ["jetstream", "all"]:
    evaluation.append(QUOTE(eval_jetstream))
if mode in ["acdc", "all"]:
    evaluation.append(QUOTE(eval_acdc))

# TODO:  PRANAV remove
# subprocess.run("make", shell=True)

# def run(config, in_path):
#     def make_path():
#         path = in_path.joinpath(time.strftime("%Y-%m-%d-%H-%M-%S"))
#         path.mkdir()
#         with open(path.joinpath("cfg"), "w") as f:
#             f.write(str(config))
#         return path
#     if has_meta(config):
#         path = make_path()
#         for x in strip_quote(flatten_nondet(config)).l:
#             run(x, path)
#     else:
#         for i in range(5):
#             try:
#                 path = make_path()
#                 cmd = f'python3 python/single_eval.py "{config}" {path}'
#                 subprocess.run(cmd, shell=True, check=True)
#                 break
#             except subprocess.CalledProcessError as e:
#                 print(e.output)
#                 subprocess.run("pkill -f chrome", shell=True)
#                 if os.path.exists(path):
#                     shutil.rmtree(path)

# run(NONDET(*evaluation), Path("log"))

# print(eval_jetstream)

def make_path(in_path):
    path = in_path.joinpath(time.strftime("%Y-%m-%d-%H-%M-%S"))
    path.mkdir()
    return path

cfgs = []

def flatten_config(cfg):
    if has_meta(cfg):
        for x in strip_quote(flatten_nondet(cfg)).l:
            flatten_config(x)
    else:
        cfgs.append(cfg)

flatten_config(eval_jetstream)


def run(log_path):
    for (idx, cfg) in enumerate(cfgs):
        exp_path = log_path.joinpath(str(idx))
        exp_path.mkdir()
        with open(exp_path.joinpath("cfg"), "w") as f:
                f.write(str(cfg))
        cmd = f'python3 python/single_eval.py "{cfg}" {exp_path}'
        subprocess.run(cmd, shell=True, check=True)
        print(str(idx) + " " + str(cfg))

def get_dirs(path):
    dirs = glob.glob(path+"/*/")
    return dirs


def get_values_in(filename, key):
    res = []
    with open(filename) as f:
        for line in f.readlines():
            j = json.loads(line)
            # major_gc_time = j["total_major_gc_time"]
            res.append(j[key])
    return res
    

def compute_values(gc_file, mem_file):
    x = get_values_in(mem_file, "Limit")
    y = get_values_in(gc_file, "total_major_gc_time")
    return (x, y)


def read_cfg(dir):
    cfg = {}
    
    with open(os.path.join(dir, "cfg")) as f:
        cfg = json.load(f)
    return cfg


# res = [yg:{x: [val], y: [val]}, classic:{x: [val], y: [val]}, ignore:{x: [val], y: [val]}]]
def eval_jetstream(benchmark, root_dir):
    dirs = get_dirs(root_dir)
    result = []
    for dir in dirs:
        cfg = read_cfg(dir)
        if cfg['CFG']['BENCH'] != benchmark:
            continue
        balance_type = cfg['CFG']['BALANCER_CFG']['BALANCE_STRATEGY']
        gc_file = glob.glob('*.gc.log')[0]
        mem_file = glob.glob('*.memory.log')[0]
        x, y = compute_values(gc_file, mem_file)
        result[balance_type]['x'].append(x)
        result[balance_type]['y'].append(y)

    return result

result = eval_jetstream("box2d.js", root_dir)
print(result)
    
# log_path = make_path(Path("log"))

# run()






