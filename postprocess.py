#!/usr/bin/env python

import os
import argparse
import errno

import hashlib
import re
from numpy.random import RandomState

RNG = RandomState(214421)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def randint(m):
    return RNG.randint(0, m + 1)


def random_combinations(n, k, count):
    for _ in range(count):
        c = randint(2 ** (k) - 1)

        res = []
        cap = []
        i = 0
        cap.append(randint(1) == 1)
        for _ in range(n):
            res.append(i)
            if c % 2 == 1:
                cap.append(randint(1) == 1)
                i += 1
            c = c // 2

        yield res, cap


def fixidentifiers(sent, maxids, samples):
    ids = set()
    for m in re.finditer('i(\d+)', sent):
        ids.add(m.group(0))
    ids = sorted(ids)

    # print(ids)
    if len(ids) == 0:
        yield sent
        return

    k = len(ids)
    if k > maxids:
        k = maxids

    ids_map = dict(reversed(t) for t in enumerate(ids))
    for comb, cap in random_combinations(len(ids), k, samples):
        res = []
        i = 0
        for m in re.finditer('i(\d+)', sent):
            res.append(sent[i:m.span()[0]])
            key = m.group(0)
            new_id = comb[ids_map[key]]
            first = 'I' if cap[new_id] else 'i'
            res.append(first + str(new_id))
            i = m.span()[1]
        res.append(sent[i:])
        yield ''.join(res)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('filename', type=str)
    argparser.add_argument('outdir', type=str)
    argparser.add_argument('-m', '--maxids', type=int, default=8)
    argparser.add_argument('-s', '--samples', type=int, default=8)
    args = argparser.parse_args()

    mkdir_p(args.outdir)

    seen = set()

    for i, chunk in enumerate(open(args.filename, 'rt').read().split('\1')):
        chunk = chunk.strip()

        for chunk in fixidentifiers(chunk, args.maxids, args.samples):
            name = hashlib.sha1(chunk.encode('utf-8')).hexdigest()

            if name in seen:
                continue
            seen.add(name)

            outfn = os.path.join(args.outdir, '%s.scala' % name)
            with open(outfn, 'wt+') as f:
                f.write(chunk)
