import os
import json
import re
import datetime

def percent(value, total):
    return int(value * 10000 / total)/100.0

def bench_name(name):
    benchmarks = ["Bears", "Bug_dot_jar", "Defects4J", "IntroClassJava", "QuixBugs", "xtotal"]
    benchmark_names = ["Bears", "Bugs.jar", "Defects4J", "IntroClassJava", "QuixBugs", "Average"]
    return benchmark_names[benchmarks.index(name)]

def tool_name(name):
    tools = ["Arja", "Cardumen", "DynaMoth", "GenProg", "Kali", "NPEFix", "Nopol", "RSRepair", "jGenProg", "jKali", "jMutRepair", "xtotal"]
    tool_names = ["Arja", "Cardumen", "DynaMoth", "GenProg-A", "Kali-A", "NPEFix", "Nopol", "RSRepair-A", "jGenProg", "jKali", "jMutRepair", "Average"]
    return tool_names[tools.index(name)]

def format_time(t):
    t = str(datetime.timedelta(seconds=average_tool)).split('.', 2)[0]
    if t[0] == "0":
        return t[2:]
    return t

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

ROOT = os.path.join(os.path.dirname(__file__), "..")

nb_bugs_bench = {
    "Bears": 251,
    "Bug_dot_jar": 1158,
    "Defects4J": 395,
    "IntroClassJava": 297,
    "QuixBugs": 40,
}
nb_bugs = 2051
total_nb_patch = 0
nb_patch = 0
total_attempts = 0
patch_per_tool = {}
patch_per_bench = {}
repaired_bugs = {}
tool_bugs = {}
bugs_tool = {}
results = []
times = {
    'patched': {},
    'timeout': {},
    'nopatch': {},
    'error': {}
}

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
                    total_attempts += 1
                    seed_path = os.path.join(tool_path, seed)
                    
                    is_error = False
                    stat = None
                    repair_log_path = os.path.join(seed_path, "repair.log")
                    if not os.path.exists(repair_log_path): 
                        is_error = True
                    else:
                        stat = os.stat(repair_log_path)
                        #if stat.st_size < 20000:
                        with open(repair_log_path) as fd:
                            content = fd.read()
                            if 'Exception in thread "main"' in content or 'Usage: ' in content:
                                is_error = True
                    results_path = os.path.join(seed_path, "result.json")
                    if os.path.exists(results_path):
                        with open(results_path) as fd:
                            data = json.load(fd)
                            if 'repair_begin' in data:
                                begin = datetime.datetime.strptime(data['repair_begin'], "%Y-%m-%d %H:%M:%S.%f")
                                end = datetime.datetime.strptime(data['repair_end'], "%Y-%m-%d %H:%M:%S.%f")
                                time_spend = (end - begin).total_seconds()

                                times_dict = times['nopatch']
                                if 'patches' in data and len(data['patches']) > 0:
                                    times_dict = times['patched']
                                elif is_error:
                                    times_dict = times['error']
                                elif time_spend > 2 * 3600:
                                    times_dict = times['timeout']
                                
                                if benchmark not in times_dict:
                                    times_dict[benchmark] = {}
                                
                                if repair_tool not in times_dict[benchmark]:
                                    times_dict[benchmark][repair_tool] = []

                                times_dict[benchmark][repair_tool].append(time_spend)

                                total_time += time_spend
                            if repair_tool not in patch_per_tool:
                                patch_per_tool[repair_tool] = {}
                            if benchmark not in patch_per_bench:
                                patch_per_bench[benchmark] = 0
                            if benchmark not in patch_per_tool[repair_tool]:
                                patch_per_tool[repair_tool][benchmark] = []
                                
                            if 'patches' in data and len(data['patches']) > 0:
                                unique_bug_id = "%s_%s_%s" % (benchmark, project, bug_id)
                                if unique_bug_id not in tool_bugs:
                                    tool_bugs[unique_bug_id] = []
                                tool_bugs[unique_bug_id].append(repair_tool)

                                if repair_tool not in bugs_tool:
                                    bugs_tool[repair_tool] = []
                                bugs_tool[repair_tool].append(unique_bug_id)


                                patch_per_tool[repair_tool][benchmark].append(unique_bug_id)
                                patch_per_bench[benchmark] += 1 
                                nb_patch += 1
                                
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
                    elif is_error:
                        times_dict = times['error']
                        if benchmark not in times_dict:
                            times_dict[benchmark] = {}
                        
                        if repair_tool not in times_dict[benchmark]:
                            times_dict[benchmark][repair_tool] = []

                        times_dict[benchmark][repair_tool].append(1)
                    stderr_path = os.path.join(seed_path, "grid5k.stderr.log")
                    if os.path.exists(stderr_path):
                        with open(stderr_path) as fd:
                            # timeout
                            if "KILLED" in fd.read():
                                times_dict = times['timeout']
                                if benchmark not in times_dict:
                                    times_dict[benchmark] = {}
                                
                                if repair_tool not in times_dict[benchmark]:
                                    times_dict[benchmark][repair_tool] = []
                                    
                                times_dict[benchmark][repair_tool].append(2 * 3600)
                                
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
    print ("| {:3} | {:14} | {:21} | {:1} | {:11} |".format(index, bench_name(bug['benchmark']), ("%s %s" % (project, bug_id)).strip(), len(bug['tools']), " ".join(bug['tools'])))

print("\n")
benchmarks = ["Bears", "Bug_dot_jar", "Defects4J", "IntroClassJava", "QuixBugs"]
line = " Repair Tools "
for benchmark in benchmarks:
    line += "& {:} ".format(bench_name(benchmark))
line += "& Total \\\\\\midrule"
print(line)

for repair_tool in sorted(patch_per_tool):
    line = " {:12} ".format(tool_name(repair_tool))
    nb_patch_tool = 0
    for benchmark in benchmarks:
        nb_patches = 0
        if benchmark in patch_per_tool[repair_tool]:
            nb_patches = len(patch_per_tool[repair_tool][benchmark])
        nb_patch_tool += nb_patches
        line += "& {:{width}} ".format(nb_patches, width=len(bench_name(benchmark)))
    line += "& {:5} \\\\".format(nb_patch_tool)
    print(line)
print(" \\midrule")
line = "     Total    "
for benchmark in benchmarks:
    nb_patches = 0
    if benchmark in patch_per_bench:
        nb_patches = patch_per_bench[benchmark]
    line += "& {:{width}} ".format(nb_patches, width=len(bench_name(benchmark)))
line += "& {:5} \\\\".format(nb_patch)
print(line + "\n")

print("\nTotal generated patch: %d\n" % total_nb_patch)

line = "            "
for repair_tool in sorted(patch_per_tool):
    line += ("& {0:11} ").format(tool_name(repair_tool))
print("%s \\\\\\midrule" % line)

for repair_tool_line in sorted(patch_per_tool):
    line = " {0:10} ".format(tool_name((repair_tool_line)))
    for repair_tool_column in sorted(patch_per_tool):
        number = 0
        if repair_tool_line == repair_tool_column:
            if repair_tool_column in bugs_tool:
                # count unique
                for p in bugs_tool[repair_tool_column]:
                    if len(tool_bugs[p]) == 1:
                        number += 1
		line += ("& {0:11} ").format("\\textbf{" + str(number) + "}")
		print("%s \\\\" % line)
		break
        else:
            if repair_tool_column in bugs_tool:
                for p in bugs_tool[repair_tool_column]:
                    if repair_tool_line in bugs_tool and p in bugs_tool[repair_tool_line]:
                        number += 1
        	line += ("& {0:11} ").format(number)

times_tools = {
    'patched': {},
    'timeout': {},
    'nopatch': {},
    'error': {}
}
for state in times:
    for bench in sorted(times[state]):
        for tool in sorted(patch_per_tool):
            if tool not in times_tools[state]:
                times_tools[state][tool] = {}
            if bench not in times_tools[state][tool]:
                times_tools[state][tool][bench] = {}
            if tool not in times[state][bench]:
                continue
            times_tools[state][tool][bench] = times[state][bench][tool]

for state in times_tools:
    print(state)

    line = " {0:11} ".format(' ')
    for benchmark in sorted(benchmarks):
        line += "& {0} ".format(bench_name(benchmark))
    print("%s& Average \\\\\\midrule" % line)

    total_bench = {}
    for tool in sorted(times_tools[state]):
        line = " {0:11} ".format(tool_name(tool))

        total_tools = []
        for bench in sorted(benchmarks):
            if bench not in total_bench:
                total_bench[bench] = []
            if bench not in times_tools[state][tool]:
                line += "& {:{width}} ".format('N.A.', width=len(bench_name(bench)))
            else:
                total_bench[bench] += times_tools[state][tool][bench]
                total_tools += times_tools[state][tool][bench]

                if state == "timeout" or state == 'error':
                    line += "& {:{width}} ".format(
                        percent(len(times_tools[state][tool][bench]), nb_bugs_bench[bench]), width=len(bench_name(bench)))
                    continue
                total_tool = sum(times_tools[state][tool][bench])
                average_tool = 0
                if len(times_tools[state][tool][bench]) != 0:
                    average_tool = total_tool/len(times_tools[state][tool][bench])
                line += "& {:{width}} ".format(format_time(datetime.timedelta(seconds=average_tool)), width=len(bench_name(bench)))

        if 'xtotal' not in total_bench:
            total_bench['xtotal'] = []
        total_bench['xtotal'] += total_tools
        if state == "timeout" or state == 'error':
            line += "& {:{width}} ".format(percent(len(total_tools), nb_bugs), width=8)
        else:
            total_tool = sum(total_tools)
            average_tool = 0
            if len(total_tools) != 0:
                average_tool = total_tool/len(total_tools)
            line += "& {:{width}} ".format(format_time(datetime.timedelta(seconds=average_tool)), width=8)
        print("%s \\\\" % line)
    print(" \\midrule")
    line = ' {0:11} '.format('Average')
    for bench in sorted(total_bench):
        if state == "timeout" or state == 'error':
            tmp = total_attempts
            if bench != "xtotal":
                tmp = nb_bugs_bench[bench] * 11
            line += "& {:{width}} ".format(percent(len(total_bench[bench]), tmp), width=len(bench_name(bench)))
            continue
        total = sum(total_bench[bench])
        average_tool = 0
        if len(total_bench[bench]) != 0:
            average_tool = total/len(total_bench[bench])
        line += "& {:{width}} ".format(format_time(datetime.timedelta(seconds=average_tool)), width=len(bench_name(bench)))
    print("%s \\\\" % line)

repaired_benchmarks = {}
for i in natural_sort(repaired_bugs.iterkeys()):
	bug = repaired_bugs[i]
	if bug['benchmark'] not in repaired_benchmarks:
	    repaired_benchmarks[bug['benchmark']] = 0            
	repaired_benchmarks[bug['benchmark']] += 1

print("Benchmark      & \# Fixed bugs &    \% \\\\\\midrule")
total = 0
for benchmark in natural_sort(repaired_benchmarks):
    print (("{:" + str(len("IntroClassJava")) + "} & {:" + str(len("\# Fixed bugs")) + "} & {:5} \\\\").format(bench_name(benchmark), repaired_benchmarks[benchmark], percent(repaired_benchmarks[benchmark], nb_bugs_bench[benchmark])))
    total += repaired_benchmarks[benchmark]

print("\\midrule")
print(("{:" + str(len("IntroClassJava")) + "} & {:" + str(len("\# Fixed bugs")) + "} & {:5} \\\\").format("Total", total, percent(total, nb_bugs)))

print("Execution time %s " % datetime.timedelta(seconds=total_time))
