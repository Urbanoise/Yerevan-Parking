# -*- coding: utf-8 -*-
"""Output 8 - Logit comments of 1/24 Sep 2026: threaded replies in the STS response copy.

Adds a reply from Nikoloz Archvadze under each comment acted on, using the same raw
OOXML reply builder as Output 10 (build_o10_logit_responses.add_replies). "Done." where
the comment was simply acted upon.

Left open on purpose (user, 29-30 Sep): C22 missed plates, C68 zone-level data,
C92 Palace lot average occupancy.

Run:  python apply_o8_sep_replies.py            (refuses to reply twice)
"""
import zipfile

import build_o10_logit_responses as o10
from apply_o8_sep_comments import DST

REPLIES = {  # Word comment id -> reply
    "28": "Done.",  # supply maps
    "60": "Done.",  # retained / removed map
    "66": "Done.",  # occupancy prints
    "69": "Done.",  # zone defined
    "70": "Done.",  # occupancy explanation rewritten
    "72": "Done.",  # six-area map
    "82": "Done.",  # chapter moved
    "86": "Done.",  # 1,123 explained
    "96": "Generalising from the six representative areas was agreed with the client "
          "from the outset.",
    "97": "Done.",  # courtyard caveat
}


def main():
    with zipfile.ZipFile(DST) as z:
        if o10.AUTHOR.encode() in z.read("word/comments.xml"):
            raise SystemExit("replies already added - refusing to reply twice")
    o10.REPLIES = REPLIES
    o10.add_replies(DST)
    print("replied to", len(REPLIES), "comments in", DST)


if __name__ == "__main__":
    main()
