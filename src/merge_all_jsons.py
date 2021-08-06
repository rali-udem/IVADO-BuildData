import hashlib
import os
import pickle
import sys
import json

import orjson


def get_id(cur_region: dict):
    """
    Finds id of type fpto-11-01-10-2030Z from bulletin info.
    :param cur_region: The dict for the current region bulleting.
    :return: A string.
    """
    station = cur_region['header'][0][0].lower()
    year = int(cur_region['header'][0][4])
    month = int(cur_region['header'][0][5])
    day = int(cur_region['header'][0][6])
    zulu_hour = int(cur_region['header'][0][7])
    first_region = sorted(cur_region['regions'][0])[0]
    result = f"{station}-{year}-{month:02d}-{day:02d}-{zulu_hour}-{first_region}"
    return result


def get_slice(id: str):
    slice_index = hashlib.md5(id.encode('utf-8')).digest()[0] % 10
    result = None
    if slice_index == 0:
        result = 'dev'
    elif slice_index == 1:
        result = 'test'
    else:
        result = 'train'

    return result


def main():
    if len(sys.argv) != 3:
        print("Usage: prog output_dir output_file.pkl", file=sys.stderr)
        sys.exit(1)

    input_dirname = sys.argv[1]
    output_filename = sys.argv[2]
    all_data = {'bulletins': {}, 'partition': {'dev': [], 'train': [], 'test': []}}
    nb_bulletins_found = 0

    for dirpath, dirs, files in os.walk(input_dirname):
        region_files = [os.path.join(dirpath, f) for f in files if f.startswith("r") and f.endswith(".json")]
        for cur_filename in region_files:
            cur_region: dict = json.load(open(cur_filename, 'rt'))
            cur_id = get_id(cur_region)
            cur_slice = get_slice(cur_id)

            assert cur_id not in all_data['bulletins'], f"Duplicate id {cur_id}!!"

            all_data['bulletins'][cur_id] = cur_region
            all_data['partition'][cur_slice].append(cur_id)

            nb_bulletins_found += 1
            if nb_bulletins_found % 100 == 0:
                print(nb_bulletins_found, file=sys.stderr, end=' ', flush=True)
            if nb_bulletins_found % 2000 == 0:
                print('', file=sys.stderr, flush=True)

    print(f"\n\nPartition is train: {len(all_data['partition']['train']) / len(all_data['bulletins']):.2f},"
          f" dev: {len(all_data['partition']['dev']) / len(all_data['bulletins']):.2f}"
          f" test: {len(all_data['partition']['test']) / len(all_data['bulletins']):.2f}", file=sys.stderr, flush=True)

    # print(f'\n\nSaving {nb_bulletins_found} bulletins in {output_filename}', file=sys.stderr)
    # json.dump(all_data, open(output_filename, 'wt'))
    # print("Done.", file=sys.stderr)
    print(f'\n\nSaving {nb_bulletins_found} bulletins in {output_filename}', file=sys.stderr)
    pickle.dump(all_data, open(output_filename, 'wb'))
    print("Done.", file=sys.stderr)


if __name__ == '__main__':
    main()
