import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from collections import defaultdict
from util import tex_def, tex_fmt, new_browser
import paper
import pyppeteer

SCROLL_PIX = 50
SCROLL_SLEEP = 1
EVAL_SLEEP = 5
GMAIL_WAIT_TIME = 5
GMAIL_INBOX_TIME = 10
GMAIL_EMAIL_TIME = 5


assert(len(sys.argv) == 3)
cfg = eval(sys.argv[1])["CFG"]
result_directory = sys.argv[2] + "/"

print(f"running: {cfg}")
LIMIT_MEMORY = cfg["LIMIT_MEMORY"]
DEBUG = cfg["DEBUG"]
if LIMIT_MEMORY:
    MEMORY_LIMIT = cfg["MEMORY_LIMIT"]
BENCH = cfg["BENCH"]
BALANCER_CFG = cfg["BALANCER_CFG"]
BALANCE_STRATEGY = BALANCER_CFG["BALANCE_STRATEGY"]
RESIZE_CFG = BALANCER_CFG["RESIZE_CFG"]
RESIZE_STRATEGY = RESIZE_CFG["RESIZE_STRATEGY"]
if RESIZE_STRATEGY == "constant":
    RESIZE_AMOUNT = RESIZE_CFG["RESIZE_AMOUNT"]
if RESIZE_STRATEGY == "after-balance":
    GC_RATE = RESIZE_CFG["GC_RATE"]
if RESIZE_STRATEGY == "gradient":
    GC_RATE_D = RESIZE_CFG["GC_RATE_D"]
BALANCE_FREQUENCY = BALANCER_CFG["BALANCE_FREQUENCY"]

TYPE = cfg["TYPE"]

MB_IN_BYTES = 1024 * 1024

def env_vars_str(env_vars):
    ret = ""
    for k, v in env_vars.items():
        ret = f"{k}={v} {ret}"
    return ret

def run_jetstream(v8_env_vars, benchmark):
    command = f"""build/MemoryBalancer v8_experiment --benchmark={benchmark} --heap-size={int(10 * 1000 * 1e6)} --log-path={result_directory+"v8_log"}""" # a very big heap size to essentially have no limit
    main_process_result = subprocess.run(f"{env_vars_str(v8_env_vars)} {command}", shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with open(os.path.join(result_directory, "v8_out"), "w") as f:
        f.write(main_process_result.stdout)
    if main_process_result.returncode != 0:
        j = {}
        j["OK"] = False
        j["ERROR"] = main_process_result.stdout
        with open(os.path.join(result_directory, "score"), "w") as f:
            json.dump(j, f)
    else:
        j = {}
        j["OK"] = True
        with open(os.path.join(result_directory, "score"), "w") as f:
            json.dump(j, f)

def run_acdc(v8_env_vars):
    command = f"""build/MemoryBalancer acdc""" # a very big heap size to essentially have no limit
    main_process_result = subprocess.run(f"{env_vars_str(v8_env_vars)} {command}", shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with open(os.path.join(result_directory, "v8_out"), "w") as f:
        f.write(main_process_result.stdout)
        j = {}
    if main_process_result.returncode == 0:
        j["OK"] = True
    else:
        j["OK"] = False
        j["ERROR"] = main_process_result.stdout
    with open(os.path.join(result_directory, "score"), "w") as f:
        json.dump(j, f)

time.sleep(10)
with open(result_directory+"balancer_out", "w") as balancer_out:
    v8_env_vars = {"LOG_GC": "1", "LOG_DIRECTORY": result_directory}

    if not RESIZE_STRATEGY == "ignore":
        v8_env_vars["USE_MEMBALANCER"] = "1"
        v8_env_vars["SKIP_RECOMPUTE_LIMIT"] = "1"
        v8_env_vars["SKIP_MEMORY_REDUCER"] = "1"
        v8_env_vars["C_VALUE"] = str(GC_RATE_D)
        if BALANCE_STRATEGY == "YG_BALANCER":
            v8_env_vars["YG_BALANCER"] = "1"
    if TYPE == "jetstream":
        run_jetstream(v8_env_vars, BENCH)
    elif TYPE == "acdc":
        run_acdc(v8_env_vars)
    else:
        raise Exception(f"unknown benchmark type: {TYPE}")