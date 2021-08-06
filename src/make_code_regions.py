import os
import sys

from ppJson import ppJson


def load_regions(fin, regions):
    lines = [x.strip() for x in fin.readlines()]
    for l in lines:
        parts = l.split('|')
        assert len(parts) == 5, "Invalid line " + l
        regions[parts[1]] = {"en": parts[4], "fr": parts[3]}


def main():
    ivado_srcdir = sys.argv[1]
    codes_regions_filename = sys.argv[2]

    regions = {}
    load_regions(open(os.path.join(ivado_srcdir, 'ont.ivado'), 'rt', encoding='iso-8859-1'), regions)
    load_regions(open(os.path.join(ivado_srcdir, 'que.ivado'), 'rt', encoding='iso-8859-1'), regions)
    ppJson(open(codes_regions_filename, 'wt', encoding='utf-8'), regions, sortkeys=False)


if __name__ == "__main__":
    main()
