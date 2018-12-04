import os
import gzip
import shutil

ROOT = os.path.join(os.path.dirname(__file__), "..")

nb_patch = 0
patch_per_tool = {}
patch_per_bench = {}

for benchmark in (os.listdir(os.path.join(ROOT, "results"))):
    benchmark_path = os.path.join(ROOT, "results", benchmark)
    for project in sorted(os.listdir(benchmark_path)):
        project_path = os.path.join(benchmark_path, project)
        folders = os.listdir(project_path)
        if benchmark == "QuixBugs":
            folders = [""]
        for bug_id in sorted(folders):
            bug_path = os.path.join(project_path, bug_id)
            for repair_tool in sorted(os.listdir(bug_path)):
                tool_path = os.path.join(bug_path, repair_tool)
                for seed in sorted(os.listdir(tool_path)):
                    seed_path = os.path.join(tool_path, seed)
                    for f in os.listdir(seed_path):
                        if f[-4:] != '.log':
                            continue
                        file_path = os.path.join(seed_path, f)
                        size = os.stat(file_path).st_size
                        if size >= 50 * 1024*1024:
                            print file_path, size/ (1024*1024)
                            with open(file_path, 'rb') as f_in, gzip.open(file_path.replace(".log", ".log.gz"), 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                            os.remove(file_path)
                        elif size == 0:
                            os.remove(file_path)
