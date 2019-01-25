import os
import json
import re
import datetime

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

ROOT = os.path.join(os.path.dirname(__file__), "..")

total_nb_patch = 0
nb_patch = 0
patch_per_tool = {}
patch_per_bench = {}
repaired_bugs = {}
results = []

total_time = 0
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
                            if 'repair_begin' in data:
                                begin = datetime.datetime.strptime(data['repair_begin'], "%Y-%m-%d %H:%M:%S.%f")
                                end = datetime.datetime.strptime(data['repair_end'], "%Y-%m-%d %H:%M:%S.%f")
                                total_time += (end - begin).total_seconds()
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
                                unique_bug_id = "%s_%s_%s" % (benchmark, project, bug_id)
                                nb_tool_patch = len(data['patches'])
                                total_nb_patch += nb_tool_patch
                                data['patches'] = [data['patches'][0]]
                                if unique_bug_id not in repaired_bugs:
                                    repaired_bugs[unique_bug_id] = {
                                        "benchmark": benchmark,
                                        "project": project,
                                        "bug_id": bug_id,
                                        "tools": []
                                    }
                                results.append(
                                    {
                                        "benchmark": benchmark,
                                        "project": project,
                                        "bug_id": bug_id,
                                        "tool": repair_tool,
                                        "result": data,
                                        "nb_patch": nb_tool_patch
                                    }
                                )
                                    
                                repaired_bugs[unique_bug_id]['tools'].append(repair_tool)
                    else:
                        stderr_path = os.path.join(seed_path, "grid5k.stderr.log")
                        if os.path.exists(stderr_path):
                            with open(stderr_path) as fd:
                                # timeout
                                if "KILLED" in fd.read():
                                    total_time += 2 * 3600 # 2h
                            

with open(os.path.join(ROOT, "docs", "data", "patches.json"), "w+") as fd:
    json.dump(results, fd)
      
index = 0
print("|  #  |    Benchmark   |         Bug           |   | Repair Tool |")
print("| --- | -------------- | --------------------- | - | ----------- |")
for i in natural_sort(repaired_bugs.iterkeys()):
    bug = repaired_bugs[i]
    index += 1
    bug_id = bug['bug_id']
    if len(bug_id) > 8:
        bug_id = bug_id[-8:]
    project = bug['project'].split("-")[-1]
    print ("| {:3} | {:14} | {:21} | {:1} | {:11} |".format(index, bug['benchmark'], ("%s %s" % (project, bug_id)).strip(), len(bug['tools']), " ".join(bug['tools'])))

print("\n")
benchmarks = ["Bears", "Bug_dot_jar", "Defects4J", "IntroClassJava", "QuixBugs"]
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
print(line + "\n")

print("Total generated patch: %d\n" % total_nb_patch)


print "Execution time %s " % datetime.timedelta(seconds=total_time)
