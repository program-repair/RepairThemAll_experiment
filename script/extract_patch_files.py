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
            tool_path = os.path.dirname(root)
            tool_name = os.path.basename(tool_path)             # DynaMoth
            bug_path = os.path.dirname(tool_path)
            bug_id = os.path.basename(bug_path)                 # 86545dab
            project_path = os.path.dirname(bug_path)
            project_name = os.path.basename(project_path)       # Commons-Math
            benchmark_path = os.path.dirname(project_path)
            benchmark_name = os.path.basename(benchmark_path)   # Bugs.jar

            # Content of 'result.json' file       
            json_content = ""
            with open(file_path, "r", encoding="utf8") as file:
                json_content = file.read()
            results  = json.loads(json_content)

            # Iterate over all 'patches'
            for r in results:
                patches_num = len(results['patches'])
                if 'patches' in r and patches_num > 0:
                    for patch_index in range(patches_num):
                        patch_tag = ""
                        if 'jMutRepair' not in root and 'Cardumen' not in root and 'jGenProg' not in root and 'jKali' not in root:
                            patch_tag = 'patch'
                        else:
                            patch_tag = 'PATCH_DIFF_ORIG'
                        if patch_tag in results['patches'][patch_index] and results['patches'][patch_index][patch_tag]:
                            total_num = total_num + 1
                            patch = results['patches'][patch_index][patch_tag]
                            if 'QuixBugs' in root:
                                patch_file_path = os.path.join(output_dir,project_name,bug_id,tool_name)
                            else:
                                patch_file_path = os.path.join(output_dir,benchmark_name,project_name,bug_id,tool_name)
                            if not os.path.exists(patch_file_path):
                                    os.makedirs(patch_file_path)
                            if 'jMutRepair' in root or 'Cardumen' in root or 'jGenProg' in root or 'jKali' in root:
                                patch = patch.split("\\n",1)[1].replace("\\/","/").replace("\\n","\n").replace("\\t","\t")
                            with open(os.path.join(patch_file_path,str(patch_index)+".patch"), 'w') as file2:
                                file2.write(patch)    


print(f"TOTAL_NUM: {total_num}")
