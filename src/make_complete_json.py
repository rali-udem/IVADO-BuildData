import json
import os

from ppJson import ppJson
import sys
from buildJSON import parseMeteocode, save_bulletin_texts


def read_bulletins(code_dir, texte_dir, year: int, output_dir: str):
    for prov in ['ont', 'que']:
        prov_code_dir = os.path.join(code_dir, prov)
        _, _, filenames = next(os.walk(prov_code_dir), (None, None, []))
        for cur_filename in filenames:
            print(f"Processing {cur_filename}...", file=sys.stderr)
            cur_code = parseMeteocode(os.path.join(prov_code_dir, cur_filename))
            json_filename = os.path.join(output_dir, f'{str(year)}-{prov}-{cur_filename}.json')
            if not os.path.exists(json_filename):
                ppJson(open(json_filename, "w"), cur_code, 0, False)
                region_dir_name = json_filename + "_regions"
                os.mkdir(region_dir_name)
                save_bulletin_texts(os.path.join(texte_dir, f'output_{prov}_{str(year)}', cur_filename), cur_code,
                                    region_dir_name)


def main():
    if len(sys.argv) != 3:
        print("Usage: prog configfile.json output_dir")
        sys.exit(1)

    config = json.load(open(sys.argv[1]))
    output_dir = sys.argv[2]

    read_bulletins(config['2018_meteocode'], config['2018_texte'], 2018, output_dir)
    read_bulletins(config['2019_meteocode'], config['2019_texte'], 2018, output_dir)


if __name__ == '__main__':
    main()
