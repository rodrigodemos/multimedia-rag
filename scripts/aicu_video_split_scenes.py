import json
import os
import re

def reshape_scene(scene):
    data = scene

    # Remove keyFrame.jpg references from markdown
    data["markdown"] = re.sub(r'!\[.*?\]\(.*?keyFrame.*?\.jpg\)', '![]', data["markdown"])

    # Convert fields to remove 'type' and only keep the value
    new_fields = {}
    for field_name, field_data in data["fields"].items():
        if field_data["type"] == "string":
            new_fields[field_name] = field_data["valueString"]
        elif field_data["type"] == "array":
            arr = []
            for item in field_data["valueArray"]:
                arr.append(item.get("valueString", "")) 
            new_fields[field_name] = arr
        else:
            new_fields[field_name] = None
    data["fields"] = new_fields

    return data


print('starting job')

filename = '[FILENAME].json'
with open(filename, 'r', encoding='utf-8') as f:
    data = json.load(f)

print('loaded file')

#filename without extension
filename_wo_ext = filename.split('.')[0]

# print id from data
print(f'id: {data.get("id")}')

print(f'contents: {data.get("result.contents")}')

contents = data.get('result').get('contents', [])

print('extracted contents')

print(len(contents))

if not os.path.exists(f'./videos/{filename_wo_ext}'):
    os.makedirs(f'./videos/{filename_wo_ext}')

for i, doc in enumerate(contents, 1):
    reshape_scene(doc)
    filename = f'./videos/{filename_wo_ext}/{filename_wo_ext}_scene_{i}.json'
    print(f'writing {filename}')
    with open(filename, 'w', encoding='utf-8') as out:
        json.dump(doc, out, indent=2, ensure_ascii=False)


print('ending job')

# print working dir
print(os.getcwd())