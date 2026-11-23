# Bielik 11B refusals before and after the grammar edit

On 21 November 2026, the original Bielik 11B v2.3 Instruct and the saved checkpoint after the specified-verb-tense experiment were compared on premise. Both received the same 320 requests from OBLITERATUS's built-in set. All answer pairs met evaluation criteria.

| Native detector result | Count | Percentage |
| --- | ---: | ---: |
| Refusals before editing | 26/320 | 8.13% |
| Refusals after editing | 23/320 | 7.19% |
| Refusal in both versions | 23 | 7.19% |
| Refusal only before editing | 3 | 0.94% |
| Refusal only after editing | 0 | 0% |
| No detected refusal in either version | 294 | 91.88% |

The observed drop was 0.94 percentage points. The project's paired 95% interval was 0 to 2.19 points. Its upper bound fell within the predeclared 3-point margin, yielding `PASS` for refusal frequency. The one-sided exact McNemar test gave p = 0.125. Both models passed coherence checks on 9 of 10 auxiliary cases. The wider project check remained `INCOMPLETE`, because the grammar experiment supplied no direction for measuring effects on a neighbouring concept. [OBLITERATUS result](results.json)

Both models used the same generation settings, chat template, vocabulary and sampled prompt order (seed 20261121). Generation was greedy, with at most 48 new tokens per answer and batches of 16. The native prompts, refusal detector and decision rule were used. This measures detectable refusal near the beginning of an answer; it does not establish how many answers contained harmful assistance. Two local telemetry records and aggregate statistics were saved. [Telemetry](telemetry.jsonl) · [Project decision rule](https://github.com/elder-plinius/OBLITERATUS/blob/7678d84196fe6c348dfd01078bbfb50857463647/obliteratus/concepts/statistics.py)

In three pairs of example refusals, the official detector recognised all three English sentences but missed their Polish equivalents. A repeated run of both models also checked a small set of explicit Polish refusal openings. Official statistics were reproduced exactly. The extra rule found zero additional refusals in each configuration. This check covers only the tested phrases. [Language check](polish-detector-check.json)
