import os
import json

ROOT = os.path.join(os.path.dirname(__file__), "..")

nb_patch = 0
print("  #  | Repair Tool | Benchmark | Bug ")
print(" --- | ----------- | --------- | --- ")
for benchmark in os.listdir(os.path.join(ROOT, "results")):
    benchmark_path = os.path.join(ROOT, "results", benchmark)
    for project in os.listdir(benchmark_path):
        project_path = os.path.join(benchmark_path, project)
        folders = os.listdir(project_path)
        if benchmark == "QuixBugs":
            folders = [""]
        for bug_id in folders:
            bug_path = os.path.join(project_path, bug_id)
            for repair_tool in os.listdir(bug_path):
                tool_path = os.path.join(bug_path, repair_tool)
                for seed in os.listdir(tool_path):
                    seed_path = os.path.join(tool_path, seed)
                    results_path = os.path.join(seed_path, "result.json")
                    if os.path.exists(results_path):
                        with open(results_path) as fd:
                            data = json.load(fd)
                            if 'patches' in data and len(data['patches']) > 0:
                                nb_patch += 1
                                print (" {:3} | {:11} | {:9} | {:4} | {:5}".format(nb_patch,repair_tool, benchmark, project, bug_id))
                            if 'patch' in data and len(data['patch']) > 0:
                                nb_patch += 1
                                print (" {:3} | {:11} | {:9} | {:4} | {:5}".format(nb_patch,repair_tool, benchmark, project, bug_id))