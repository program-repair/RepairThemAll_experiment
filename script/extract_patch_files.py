import os
import shutil
import json

path = '../results'
output_dir = '../Extracted_Patch_Files'

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

total_num = 0

for root, dirs, files in os.walk(path):
    for f in files:
        # .../results/Bugs.jar/Commons-Math/86545dab/DynaMoth/7/result.json
        file_path = os.path.join(root, f)
        if ".json" in f and "detailed" not in f:
            json_content = ""
            with open(file_path, "r", encoding="utf8") as file:
                json_content = file.read()
            results  = json.loads(json_content)
            for r in results:
                if 'patches' in r and len(results['patches']) > 0:
                    tool_path = os.path.dirname(root)
                    tool_name = os.path.basename(tool_path)             # DynaMoth
                    bug_path = os.path.dirname(tool_path)
                    bug_id = os.path.basename(bug_path)                 # 86545dab
                    project_path = os.path.dirname(bug_path)
                    project_name = os.path.basename(project_path)       # Commons-Math
                    benchmark_path = os.path.dirname(project_path)
                    benchmark_name = os.path.basename(benchmark_path)   # Bugs.jar
                    patches_num = len(results['patches'])
                    for patch_index in range(patches_num):
                        if 'patch' in results['patches'][patch_index] and results['patches'][patch_index]['patch']:
                            total_num = total_num + 1
                            patch = results['patches'][patch_index]['patch']
                            if 'QuixBugs' in root:
                                patch_file_path = os.path.join(output_dir,project_name,bug_id,tool_name)
                            else:
                                patch_file_path = os.path.join(output_dir,benchmark_name,project_name,bug_id,tool_name)
                            if not os.path.exists(patch_file_path):
                                    os.makedirs(patch_file_path)
                            with open(os.path.join(patch_file_path,str(patch_index)+".patch"), 'w') as file2: 
                                file2.write(patch)    


print(f"TOTAL_NUM: {total_num}")




