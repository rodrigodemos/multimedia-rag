import argparse
import json
import logging
import os
import re

logger = logging.getLogger("scripts")

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process the output of AICU JSON file and reshape its contents."
    )
    parser.add_argument("file", nargs="?", help="Files to be processed")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])
        # We only set the level to INFO for our logger,
        # to avoid seeing the noisy INFO level logs from the Azure SDKs
        logger.setLevel(logging.DEBUG)

    #TODO: Support multiple files 
    filename = args.file

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print('loaded file')

    #filename without extension
    filename_wo_ext = os.path.splitext(os.path.basename(filename))[0]

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
