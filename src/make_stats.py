import json
import os
from pprint import pprint
import sys
from tqdm import tqdm


def check_bulletin(cur_bulletin: dict, cur_stats: dict, textes: dict):
    for k, v in cur_bulletin.items():
        cur_stats[k] = cur_stats.get(k, 0) + 1

    nb_regions_en = len(cur_bulletin['names-en'])
    assert nb_regions_en == len(cur_bulletin['names-fr']), "Inconsistent nb of regions"
    cur_stats['nb_regions'][nb_regions_en] = stats['nb_regions'].get(nb_regions_en, 0) + 1
    textes['en'].append(' '.join(cur_bulletin['en'].split()) + '\n')
    textes['fr'].append(' '.join(cur_bulletin['fr'].split()) + '\n')

    # names_en = ', '.join(cur_bulletin['names-en'])
    # en_text = cur_bulletin['en']
    #
    # print(f"\n\n{names_en}\n{en_text}\n")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: prog input.jsonl output.en output.fr", file=sys.stderr)
        sys.exit(1)

    input_filename = sys.argv[1]
    stats = {'nb_regions': dict()}
    nb_bulletins = 0
    textes = {'en': [], 'fr': []}

    with open(input_filename, 'rt', encoding='utf-8') as fin:
        for cur_line in tqdm(fin.readlines(), total=230218):
            bulletin = json.loads(cur_line)
            check_bulletin(bulletin, stats, textes)
            nb_bulletins += 1

    print(f"Found {nb_bulletins} bulletins.")
    pprint(stats)

    for corpus, filename in zip([textes['en'], textes['fr']], sys.argv[2:]):
        with open(filename, 'wt', encoding='utf-8') as fout:
            fout.writelines(corpus)
