import hashlib
import json
import sys

from tqdm import tqdm


def get_slice(cur_id: str):
    slice_index = hashlib.md5(cur_id.encode('utf-8')).digest()[0] % 20
    result = None
    if slice_index == 0:
        result = 'dev'
    elif slice_index == 1:
        result = 'test'
    else:
        result = 'train'

    return result


def convert_element(element):
    if type(element) == list:
        return convert_list(element)
    else:
        return element


def convert_list(cur_list: list):
    return tuple([convert_element(element) for element in cur_list])


def convert_lists_to_tuples(obj: dict):
    for key, value in obj.items():
        if type(value) == list:
            obj[key] = convert_list(value)


def main_compact():
    if len(sys.argv) != 4:
        print("Usage: prog [trim] input_file.jsonl output_file.jsonl", file=sys.stderr)
        sys.exit(1)

    input_filename = sys.argv[2]
    output_json_filename = sys.argv[3]

    with open(input_filename, 'rt', encoding='utf-8') as fin, open(output_json_filename, 'wt',
                                                                   encoding='utf-8') as fout:
        for cur_line in tqdm(fin.readlines(), total=230218):
            cur_line = cur_line.replace('point_intermediaire', 'pi')  # shorten point_intermediaire
            bulletin: dict = json.loads(cur_line)
            bulletin.pop('indice_qa', None)  # remove air_quality
            bulletin.pop('neige_sol', None)  # remove neige_sol
            for useless_nest in ['header', 'names-en', 'names-fr', 'regions']:
                bulletin[useless_nest] = bulletin[useless_nest][0]  # remove useless nest

            fout.write(json.dumps(bulletin, ensure_ascii=False) + '\n')  # serialize to non-ascii properly


def main_partition():
    if len(sys.argv) != 4:
        print("Usage: prog [partition] input_file.jsonl output_file_root", file=sys.stderr)
        print("Compacts, then write partition at output_file_root_{dev,test,train}.jsonl")
        sys.exit(1)

    input_filename = sys.argv[2]
    output_json_filename_root = sys.argv[3]

    partition = {'train': [], 'dev': [], 'test': []}

    with open(input_filename, 'rt', encoding='utf-8') as fin:
        for cur_line in tqdm(fin.readlines(), total=230218):
            bulletin: dict = json.loads(cur_line)
            convert_lists_to_tuples(bulletin)  # to fit in ram
            cur_slice = get_slice(bulletin['id'])
            partition[cur_slice].append(bulletin)

    print(f"Partition is {len(partition['dev'])} dev, {len(partition['test'])} test, {len(partition['train'])} train, "
          f"in that order")

    for slice_name in ['dev', 'test', 'train']:
        with open(output_json_filename_root + '_' + slice_name + '.jsonl', 'wt', encoding='utf-8') as fout:
            for bulletin in partition[slice_name]:
                fout.write(json.dumps(bulletin, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    if sys.argv[1] == 'trim':
        main_compact()
    elif sys.argv[1] == 'partition':
        main_partition()
