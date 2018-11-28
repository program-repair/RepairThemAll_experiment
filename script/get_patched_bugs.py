import os
import json
import re

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

ROOT = os.path.join(os.path.dirname(__file__), "..")

nb_patch = 0
patch_per_tool = {}
patch_per_bench = {}

print("|  #  | Repair Tool | Benchmark | Bug |")
print("| --- | ----------- | --------- | --- |")
for benchmark in natural_sort(os.listdir(os.path.join(ROOT, "results"))):
    benchmark_path = os.path.join(ROOT, "results", benchmark)
    for project in natural_sort(os.listdir(benchmark_path)):
        project_path = os.path.join(benchmark_path, project)
        folders = os.listdir(project_path)
        if benchmark == "QuixBugs":
            folders = [""]
        for bug_id in natural_sort(folders):
            bug_path = os.path.join(project_path, bug_id)
            for repair_tool in natural_sort(os.listdir(bug_path)):
                tool_path = os.path.join(bug_path, repair_tool)
                for seed in natural_sort(os.listdir(tool_path)):
                    seed_path = os.path.join(tool_path, seed)
                    results_path = os.path.join(seed_path, "result.json")
                    if os.path.exists(results_path):
                        with open(results_path) as fd:
                            data = json.load(fd)
                            if repair_tool not in patch_per_tool:
                                patch_per_tool[repair_tool] = {}
                            if benchmark not in patch_per_bench:
                                patch_per_bench[benchmark] = 0
                            if benchmark not in patch_per_tool[repair_tool]:
                                patch_per_tool[repair_tool][benchmark] = 0
                                
                            if 'patches' in data and len(data['patches']) > 0:
                                patch_per_tool[repair_tool][benchmark] += 1 
                                patch_per_bench[benchmark] += 1 
                                nb_patch += 1
                                print ("| {:3} | {:11} | {:9} | {:4} {} |".format(nb_patch,repair_tool, benchmark, project, bug_id))
                            if 'patch' in data and len(data['patch']) > 0:
                                patch_per_tool[repair_tool][benchmark] += 1 
                                patch_per_bench[benchmark] += 1 
                                nb_patch += 1
                                print ("| {:3} | {:11} | {:9} | {:4} {} |".format(nb_patch,repair_tool, benchmark, project, bug_id))

print("\n")
benchmarks = ["Bears", "Bugs.jar", "Defects4J", "IntroClassJava", "QuixBugs"]
line = "| Repair Tools |"
for benchmark in benchmarks:
    line += " {:} |".format(benchmark)
line += " Total |"
print(line)
line = "| ------------ |"
for benchmark in benchmarks:
    line += " {:-<{width}} |".format("-", width=len(benchmark))
line += " ----- |"
print(line)

for repair_tool in patch_per_tool:
    line = "| {:12} |".format(repair_tool)
    nb_patch_tool = 0
    for benchmark in benchmarks:
        nb_patches = 0
        if benchmark in patch_per_tool[repair_tool]:
            nb_patches = patch_per_tool[repair_tool][benchmark]
        nb_patch_tool += nb_patches
        line += " {:{width}} |".format(nb_patches, width=len(benchmark))
    line += " {:5} |".format(nb_patch_tool)
    print(line)

line = "|     Total    |"
for benchmark in benchmarks:
    nb_patches = 0
    if benchmark in patch_per_bench:
        nb_patches = patch_per_bench[benchmark]
    line += " {:{width}} |".format(nb_patches, width=len(benchmark))
line += " {:5} |".format(nb_patch)
print(line)