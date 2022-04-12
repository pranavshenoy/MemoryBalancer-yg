import json
import os
import statistics as stats
import glob
import sys
from  util import tex_fmt, fmt

def tex_def_table(row_num, col_name, definitions):
    return f"\def\{col_name}{row_num}{{{definitions}\\xspace}}\n"
	
def combine(membalancer_data, baseline_data, membalancer_dir, baseline_dir):
	tex_data = {}
	
	for data in membalancer_data:
		name = data["name"]
		tex_data[name] = {}
		tex_data[name]["w"] = data["mem_diff"]
		tex_data[name]["g"] = data["gc_rate"]
		tex_data[name]["s"] = data["gc_speed"]
		tex_data[name]["membalancer_exta_mem"] = data["extra_mem"]
		tex_data[name]["membalancer_dir"] = membalancer_dir
		
	for data in baseline_data:
		name = data["name"]
		tex_data[name]["current_v8_extra_mem"] = data["extra_mem"]
		tex_data[name]["baseline_dir"] = baseline_dir
	return tex_data
	
def convert_to_tex(data):
	one_key = list(data.keys())[0]
	tex_str = "% membalancer_dir: "+ data[one_key]["membalancer_dir"]+ "baseline_dir: "+data[one_key]["baseline_dir"]+" \n"
# 	tex_str = ""
	row = 'A'
	for (idx, key) in enumerate(data.keys()):
		w = data[key]["w"]
		g = data[key]["g"]
		s = data[key]["s"]
		mb_extra = data[key]["membalancer_exta_mem"]
		curr_extra = data[key]['current_v8_extra_mem']
		tex_str += tex_def_table(row, "name", key)
		tex_str += tex_def_table(row, "w", f"{tex_fmt(w)}")
		tex_str += tex_def_table(row, "g", f"{tex_fmt(g)}")
		tex_str += tex_def_table(row, "s", f"{tex_fmt(s)}")
		tex_str += tex_def_table(row, "mbextra", f"{tex_fmt(mb_extra)}")
		tex_str += tex_def_table(row, "currextra", f"{tex_fmt(curr_extra)}")
		row = ord(row)
		row += 1
		row = chr(row)
	return tex_str

def write_tex(tex_str, path):
	with open(path, "w") as tex_file:
		tex_file.write(tex_str)


def get_optimal_table(data):
	
	for each_row in data:
		for each_pgm in each_row:
			if each_pgm["name"] == "pdfjs.js":
				if each_pgm["mem_diff"] <= 55 and each_pgm["mem_diff"] >= 45:
					print("choosing optimal table data")
					return each_row
	return data[0]

def get_tex_data(dirname):
	with open(dirname+"/tex_data") as f:
		data = []
		for line in f.read().splitlines():
			data = json.loads(line)
		return data
	return []

def get_table_data(mb_dir, baseline_dir):
	
	mb_raw_data = get_tex_data(mb_dir)
	sz = int(len(mb_raw_data)/3)
	mb_data =  get_optimal_table(mb_raw_data[sz:])
	
	baseline_raw_data = get_tex_data(baseline_dir)
	sz = int(len(baseline_raw_data)/3)
	baseline_data = get_optimal_table(baseline_raw_data[sz:])
	return (mb_data, baseline_data)
	
def main(membalancer_log_dir, baseline_log_dir):
	(data1, data2) = get_table_data(membalancer_log_dir, baseline_log_dir)
	combined_data = combine(data1, data2, membalancer_log_dir, baseline_log_dir)
	converted_tex = convert_to_tex(combined_data)
	write_tex(converted_tex, "../membalancer-paper/js_table.tex")
	
if __name__ == "__main__":
	assert(len(sys.argv) == 3)
	membalancer_log_dir = sys.argv[1]
	baseline_log_dir = sys.argv[2]
	main(membalancer_log_dir, baseline_log_dir)
	print("done creating tex file for table!")

		
		
	
