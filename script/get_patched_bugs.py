import os
import json
import re
import datetime

benchmarks = ["Bears", "Bugs.jar", "Defects4J", "IntroClassJava", "QuixBugs"]
tools = ["Arja", "GenProg", "Kali", "RSRepair", "Cardumen", "jGenProg", "jKali", "jMutRepair", "Nopol", "DynaMoth", "NPEFix"]

def percent(value, total):
    return int(value * 10000 / total)/100.0

def percent_round(value, total):
    return int(round(percent(value, total), 0))

def bench_name(name):
    benchmarks = ["Bears", "Bugs.jar", "Defects4J", "IntroClassJava", "QuixBugs", "xtotal"]
    benchmark_names = ["Bears", "Bugs.jar", "Defects4J", "IntroClassJava", "QuixBugs", "Average"]
    return benchmark_names[benchmarks.index(name)]

def tool_name(name):
    t = tools + ["xtotal"]
    tool_names = ["ARJA", "GenProg-A", "Kali-A", "RSRepair-A", "Cardumen","jGenProg", "jKali", "jMutRepair", "Nopol", "DynaMoth", "NPEFix", "Average"]
    return tool_names[t.index(name)]

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
    "Bugs.jar": 1158,
    "Defects4J": 395,
    "IntroClassJava": 297,
    "QuixBugs": 40,
}
nb_bugs = 0
for benchmark in benchmarks:
    nb_bugs += nb_bugs_bench[benchmark]

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

rvs = {}
not_runned = []

total_time = 0
for benchmark in benchmarks:
    benchmark_path = os.path.join(ROOT, "results", benchmark)

    if benchmark not in rvs:
        rvs[benchmark] = []
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
                        repair_log_path = os.path.join(seed_path, "repair.log.gz")
                    
                    if not os.path.exists(repair_log_path): 
                        is_error = True
                        not_runned.append("%s\t%s\t%s_%s" % (repair_tool, bench_name(benchmark), project, bug_id))
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
                                rvs[benchmark].append('patches' in data and len(data['patches']) > 0)
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
                                        "tool": tool_name(repair_tool),
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
                        rvs[benchmark].append(False)
                    else:
                        rvs[benchmark].append(False)
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
print("|  #  |    Benchmark   |          Bug           | # Repair Tools | Repair Tools |")
print("| ---:| -------------- | ---------------------- | --------------:| ------------ |")
for i in natural_sort(repaired_bugs.iterkeys()):
    bug = repaired_bugs[i]
    index += 1
    bug_id = bug['bug_id']
    if len(bug_id) > 8:
        bug_id = bug_id[-8:]
    project = bug['project'].split("-")[-1]
    t = ""
    for repair_tool in bug['tools']:
    	t += tool_name(repair_tool) + " "
    print ("| {:3} | {:14} | {:22} | {:16} | {:11} |".format(index, bench_name(bug['benchmark']), ("%s %s" % (project, bug_id)).strip(), len(bug['tools']), t))

print("\n")
line = " Repair Tools "
for benchmark in benchmarks:
    line += "& {:} ".format(bench_name(benchmark))
line += "& Total \\\\\\midrule"
print(line)

nb_patch_tool = {}
nb_patch_tool_bench = {}
for repair_tool in tools:
    line = " {:12} ".format(tool_name(repair_tool))
    nb_patch_tool[repair_tool] = 0
    nb_patch_tool_bench[repair_tool] = {}
    for benchmark in benchmarks:
        nb_patches = 0
        t = benchmark
        if t != 'Defects4J':
            t = 'Others'
        if t not in nb_patch_tool_bench[repair_tool]:
            nb_patch_tool_bench[repair_tool][t] = 0
        if benchmark in patch_per_tool[repair_tool]:
            nb_patches = len(patch_per_tool[repair_tool][benchmark])
        nb_patch_tool_bench[repair_tool][t] += nb_patches
        nb_patch_tool[repair_tool] += nb_patches
	if nb_patches > 0 and percent(nb_patches, nb_bugs_bench[benchmark]) < 1:
		line += "& {:{width}} ".format("%d (<1\\%%)" % (nb_patches), width=len(bench_name(benchmark)))
	else:
        	line += "& {:{width}} ".format("%d (%d\\%%)" % (nb_patches, percent(nb_patches, nb_bugs_bench[benchmark])), width=len(bench_name(benchmark)))
    if nb_patch_tool[repair_tool] > 0 and percent(nb_patch_tool[repair_tool], nb_bugs) < 1:
	line += "& {:5} \\\\".format("%d (<1\\%%)" % (nb_patch_tool[repair_tool]))
    else:
	line += "& {:5} \\\\".format("%d (%d\\%%)" % (nb_patch_tool[repair_tool], percent(nb_patch_tool[repair_tool], nb_bugs)))
    print(line)
print(" \\midrule")
line = "Total "
for benchmark in benchmarks:
    nb_patches = 0
    if benchmark in patch_per_bench:
        nb_patches = patch_per_bench[benchmark]
    line += "& {:{width}} ".format(nb_patches, width=len(bench_name(benchmark)))
line += "& {:5} \\\\".format(nb_patch)
print(line)

repaired_benchmarks = {}
for i in natural_sort(repaired_bugs.iterkeys()):
	bug = repaired_bugs[i]
	if bug['benchmark'] not in repaired_benchmarks:
	    repaired_benchmarks[bug['benchmark']] = 0            
	repaired_benchmarks[bug['benchmark']] += 1

total = 0
line = "Total unique "
for benchmark in natural_sort(repaired_benchmarks):
    line += "& {:{width}} ".format("%d (%d\\%%)" % (repaired_benchmarks[benchmark], percent(repaired_benchmarks[benchmark], nb_bugs_bench[benchmark])), width=len(bench_name(benchmark)))
    total += repaired_benchmarks[benchmark]
line += "& {:5} \\\\".format("%d (%d\\%%)" % (total, percent(total, nb_bugs)))
print(line + "\n")



for repair_tool in tools:
    print('|                | # Patched | # Non-Patched |')
    print('| -------------- | --------- | ------------- |')
    print('| %s on Defects4J  | %d | %d |' % (tool_name(repair_tool), nb_patch_tool_bench[repair_tool]['Defects4J'], nb_bugs_bench['Defects4J'] - nb_patch_tool_bench[repair_tool]['Defects4J']))
    print('| %s on Others  | %d | %d |' % (tool_name(repair_tool), nb_patch_tool_bench[repair_tool]['Others'], (nb_bugs - nb_bugs_bench['Defects4J']) - nb_patch_tool_bench[repair_tool]['Others']))

print("\nTotal generated patch: %d\n" % total_nb_patch)

# for graph
tool_totals = []

line = "            "
for repair_tool in tools:
    line += ("& {0:11} ").format("\\multicolumn{1}{c}{%s}" % tool_name(repair_tool))
print("%s \\\\\\midrule" % line)

overlaps = {}
for repair_tool_line in tools:
    line = " {0:10} ".format(tool_name(repair_tool_line))
    for repair_tool_column in tools:
        number = 0
        if repair_tool_line == repair_tool_column:
            if repair_tool_column in bugs_tool:
                # count unique
                for p in bugs_tool[repair_tool_column]:
                    if len(tool_bugs[p]) == 1:
                        number += 1
            line += ("& {0:11} ").format("\\textbf{%s\\%% (%d)}" % (percent_round(number, nb_patch_tool[repair_tool_column]), number))
	    tool_totals.append(
				  {
					"tool": tool_name(repair_tool_line),
				        "unique": number,
				        "overlapped": len(bugs_tool[repair_tool_column]) - number,
					"total": len(bugs_tool[repair_tool_column])
			           }
			      )
        else:
            if repair_tool_column in bugs_tool:
                for p in bugs_tool[repair_tool_column]:
                    if repair_tool_line in bugs_tool and p in bugs_tool[repair_tool_line]:
                        number += 1
            p = percent_round(number, nb_patch_tool[repair_tool_line])

            if repair_tool_line not in overlaps:
                overlaps[repair_tool_line] = {
                    "40-50": [],
                    "50-60": [],
                    "60-70": [],
                    "70-80": [],
                    "80-100": [],
                }
            
            for s in overlaps[repair_tool_line]:
                (min, max) = s.split("-")
                if int(min)<= p and p < int(max):
                    overlaps[repair_tool_line][s].append('%s (%d)' % (tool_name(repair_tool_column), number)) 
                    break
	    if number < 10:
		line += ("& {0:11} ").format("\\cca{%s}\\%% \\enspace(%d)"  % (p, number))
	    else:
            	line += ("& {0:11} ").format("\\cca{%s}\\%% (%d)"  % (p, number))
    print("%s \\\\" % line)

print("\n {0:10} & 0-20 \\% & 20-40 \\% & 40-60 \\% & 60-80 \\% & 80-100 \\% \\\\ \\midrule".format(''))
for tool in sorted(overlaps):
    line = " {0:10} ".format(tool_name(tool))
    for c in sorted(overlaps[tool]):
        line += '& %s ' % ", ".join(overlaps[tool][c])
    print("%s \\\\" % line)

print "\nFor repairability graph"
tool_totals_view = sorted(tool_totals, key = lambda i: i['total'],reverse=True)
for repair_tool in tool_totals_view:
    print "%s,%d,%d" % (repair_tool['tool'], repair_tool['unique'], repair_tool['overlapped'])


times_tools = {
    'patched': {},
    'timeout': {},
    'nopatch': {},
    'error': {}
}
for state in times:
    for bench in sorted(times[state]):
        for tool in tools:
            if tool not in times_tools[state]:
                times_tools[state][tool] = {}
            if bench not in times_tools[state][tool]:
                times_tools[state][tool][bench] = {}
            if tool not in times[state][bench]:
                continue
            times_tools[state][tool][bench] = times[state][bench][tool]

for state in times_tools:
    print("\n" + state)

    line = " {0:11} ".format(' ')
    for benchmark in sorted(benchmarks):
        line += "& {0} ".format(bench_name(benchmark))
    print("%s& Average \\\\\\midrule" % line)

    total_bench = {}
    for tool in tools:
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
                tmp = nb_bugs_bench[bench] * len(tools)
            line += "& {:{width}} ".format(percent(len(total_bench[bench]), tmp), width=len(bench_name(bench)))
            continue
        total = sum(total_bench[bench])
        average_tool = 0
        if len(total_bench[bench]) != 0:
            average_tool = total/len(total_bench[bench])
        line += "& {:{width}} ".format(format_time(datetime.timedelta(seconds=average_tool)), width=len(bench_name(bench)))
    print("%s \\\\" % line)

print("Execution time %s " % datetime.timedelta(seconds=total_time))

with open('not_runned.csv', 'w') as fd:
    for t in not_runned:
        fd.write(t +'\n')
