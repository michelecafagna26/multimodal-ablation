from copy import copy
from itertools import combinations, chain
import numpy as np
import spacy
from spacy.tokens import Span

from ablation.util import load_config


def apply_ablation(seg, noun_phrase):

    ablated = []
    for i in range(len(seg)):
        if seg[i] == noun_phrase:
            start_idx = i
            end_idx = i + 1

            if i < len(seg) - 1 and (seg[i + 1]._.span_tag == "VP" or seg[i + 1]._.span_tag == "CON_ADV"):
                end_idx += 1

            if i > 0 and seg[i - 1]._.span_tag == "CON_ADV":
                start_idx -= 1

            ablated = seg[0:start_idx] + seg[end_idx:]
            break

    return ablated


class TextualAblator():

    def __init__(self):

        self.config = load_config()
        self.nlp = spacy.load(self.config['spacy_model'])
        Span.set_extension('span_tag', default="UNK", force=True)
        Span.set_extension('NP_IDX', default=-1, force=True)


    def pos_matcher(self, doc, pos_list, span_tag="UNK"):
        def is_pos_matched(pos_tag, pos_list):  # equivalent of if doc[i].pos_ == "VERB" or doc[i].pos_ == "AUX":
            res = False
            for pos_item in pos_list:
                if pos_item == pos_tag:
                    res = True
                    break
            return res

        span_start = -1
        span_end = -1
        vps = []

        for i in range(len(doc)):

            if is_pos_matched(doc[i].pos_, pos_list):
                if span_start == -1:
                    span_start = i
                    span_end = i + 1
                else:
                    span_end = i + 1
            else:
                # span caught
                if span_start != -1 and span_end != -1:
                    span = doc[span_start:span_end]
                    span._.span_tag = span_tag
                    vps.append(span)

                    span_start = -1

        return vps

    def __call__(self, cap, strategy="all"):

        vps = self.pos_matcher(self.nlp(cap), ['VERB', 'AUX'], span_tag="VP")
        con_adv = self.pos_matcher(self.nlp(cap), ['ADP', 'CCONJ', 'SCONJ'], span_tag="CON_ADV")

        nps = []
        for i, noun_phrase in enumerate(self.nlp(cap).noun_chunks):
            noun_phrase._.span_tag = "NP"
            noun_phrase._.NP_IDX = i
            nps.append(noun_phrase)

        seg = vps + nps + con_adv
        seg.sort(key=lambda t: t.start)

        nps_comb = []

        if strategy == "all":
            nps_comb = [abl for abl in chain.from_iterable(list(combinations(nps, r)) for r in range(len(nps)))][1:]

        elif strategy == "incr":

            comb = []
            for noun_phrase in nps:
                comb.append(noun_phrase)
                nps_comb.append(copy(comb))

        else:
            raise ValueError(f"'{strategy}'' not supported!. Available are: 'all' and 'incr'")

        ablations = []
        nps_index = []

        for comb in nps_comb:

            ablated_sen = copy(seg)
            for noun_phrase in comb:
                if strategy == "all":
                    nps_index.append(noun_phrase._.NP_IDX)
                ablated_sen = apply_ablation(ablated_sen, noun_phrase)

            if strategy == "incr":
                nps_index.append(comb[-1]._.NP_IDX)

            ablations.append({
                "nps": comb,
                "nps_index": nps_index,
                "ablated_caption": " ".join([token.text for token in ablated_sen])
            })
            nps_index = []

        return ablations
