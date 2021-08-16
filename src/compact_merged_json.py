import hashlib
import json
import re
import sys

from nltk.tokenize import sent_tokenize, word_tokenize
from tqdm import tqdm


LANG_KEYS = {'en': 'english', 'fr': 'french'}


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
            for useless_nest in ['header', 'regions']:
                bulletin[useless_nest] = bulletin[useless_nest][0]  # remove useless nest
            assert type(bulletin['names-en'][0]) != list and type(bulletin['names-fr'][0]) != list, \
                f"Double-nested in {bulletin['id']}"

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


def get_type(sep: str, lang):
    result = None

    if lang == 'fr':
        if sep == "Aujourd'hui..":
            result = "today"
        elif sep == "Ce soir et cette nuit..":
            result = "tonight"
        elif ' ' not in sep:
            result = "tomorrow"
        elif sep.endswith("et nuit.."):
            result = "tomorrow_night"
        else:
            raise ValueError("Invalid sep " + sep)
    if lang == 'en':
        if sep == "Today..":
            result = "today"
        elif sep == "Tonight..":
            result = "tonight"
        elif ' ' not in sep and sep.endswith('day..'):
            result = "tomorrow"
        elif sep.endswith(" night.."):
            result = "tomorrow_night"
        else:
            raise ValueError("Invalid sep " + sep)

    return result


def tokenize_text(text: str, lang: str):
    """
    Tokenizes in sentences and words.
    :param text:
    :param lang:
    :return:
    """
    return [word_tokenize(sent, lang) for sent in sent_tokenize(text, lang)]


def tokenize_bulletin(bulletin: dict):
    keys = {'en': [], 'fr': []}

    for lang in ['en', 'fr']:
        tok_result = {}

        prev_sep = None
        prev_end = -1
        simplified = '\n' + bulletin[lang]['tok']
        for m in re.finditer(r'\n[^.]+\.\.', simplified):
            if prev_end != -1:
                cur_seg = simplified[prev_end:m.start()]
                tok_result[get_type(prev_sep.lstrip(), lang)] = cur_seg

            prev_end = m.end()
            prev_sep = m.group(0)

        tok_result[get_type(prev_sep.lstrip(), lang)] = simplified[prev_end:]

        bulletin[lang]['tok'] = {}
        for key, text in tok_result.items():
            keys[lang].append(key)
            bulletin[lang]['tok'][key] = tokenize_text(text, LANG_KEYS[lang])

    assert keys['en'] == keys['fr'], "Asymmetrical keys " + bulletin['id']


def strip_regions(bulletin):
    for lang in ['en', 'fr']:
        to_strip = '\n'.join(bulletin['names-' + lang]) + '.\n'
        assert bulletin[lang]['orig'].lower().startswith(to_strip.lower()), f"To strip {to_strip} from id {bulletin['id']}" \
                                                            f" not found in {bulletin[lang]['orig']}"
        bulletin[lang]['tok'] = bulletin[lang]['orig'][len(to_strip):]


def main_tokenize():
    if len(sys.argv) != 4:
        print("Usage: prog [partition] input_file.jsonl output_file.jsonl", file=sys.stderr)
        sys.exit(1)

    input_filename = sys.argv[2]
    output_json_filename = sys.argv[3]

    with open(input_filename, 'rt', encoding='utf-8') as fin, open(output_json_filename, 'wt', encoding='utf-8') as fout:
        for cur_line in tqdm(fin.readlines()):
            bulletin: dict = json.loads(cur_line)
            bulletin['en'] = {'orig': bulletin['en'], 'tok': None}  # prepare data structure
            bulletin['fr'] = {'orig': bulletin['fr'], 'tok': None}
            strip_regions(bulletin)
            tokenize_bulletin(bulletin)
            fout.write(json.dumps(bulletin, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    if sys.argv[1] == 'trim':
        main_compact()
    elif sys.argv[1] == 'partition':
        main_partition()
    elif sys.argv[1] == 'tokenize':
        main_tokenize()
