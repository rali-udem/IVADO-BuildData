import os
import sys
import json


def get_id(cur_region: dict):
    """
    Finds id of type fpto-11.01.10.2030Z from bulletin info.
    :param cur_region: The dict for the current region bulleting.
    :return: A string.
    """
    station = cur_region['header'][0][0].lower()
    year = int(cur_region['header'][0][4])
    month = int(cur_region['header'][0][5])
    day = int(cur_region['header'][0][6])
    zulu_hour = int(cur_region['header'][0][7])
    result = f"{station}-{year}-{month}-{day}-{zulu_hour}"
    return result


def main():
    if len(sys.argv) != 3:
        print("Usage: prog output_dir output_file.json", file=sys.stderr)
        sys.exit(1)

    input_dirname = sys.argv[1]
    output_filename = sys.argv[2]
    all_data = {}
    nb_bulletins_found = 0

    for dirpath, dirs, files in os.walk(input_dirname):
        region_files = [os.path.join(dirpath, f) for f in files if f.startswith("r") and f.endswith(".json")]
        for cur_filename in region_files:
            cur_region: dict = json.load(open(cur_filename, 'rt'))
            all_data[get_id(cur_region)] = cur_region

            nb_bulletins_found += 1
            if nb_bulletins_found % 100 == 0:
                print(nb_bulletins_found, file=sys.stderr, end=' ', flush=True)
            if nb_bulletins_found % 2000 == 0:
                print('', file=sys.stderr, flush=True)

    print(f'\n\nSaving {nb_bulletins_found} bulletings in {output_filename}', file=sys.stderr)
    json.dump(all_data, open(output_filename, 'wt'))
    print("Done.", file=sys.stderr)


if __name__ == '__main__':
    main()
