# Results: vocabulary-row edits (OBLITERATUS PR #595)

**Status: in progress.** Stage 0 (tools, protocol and pilots) is complete. Llama-3.1-8B is complete apart from the manual review and the LLM judges. Qwen2.5-7B and two small models with a shared matrix are running. Stage 3 (Inkling-2-Mini, the model of the original claim) waits for disk space. This page is updated as stages finish.

The study asks whether editing a few vocabulary rows (`vocab_surgery`) reduces refusals by itself, whether it adds anything beyond a prefill, and what it costs in capability. Interim findings on Llama-3.1-8B (keyword detector):
- the token list from the post changed 1 of 200 refusal flags (170 → 169), with or without the prefill; only 19 of the 170 refusals contain a token from that list;
- the full 34-token list from the PR lowered refusals by 7.0 pp alone and by 18.5 pp on top of the prefill (152 → 115);
- the edit leaves benchmark scores almost unchanged (mean −0.31 pp) but removes the normal use of the edited words.

On 24 November the author of the original claim published a correction: the 97.4% result had a prefill in the chat template by mistake. This study separates the prefill from the edit by design; the correction is recorded in the protocol.

Limitations at this stage:
- refusal counts come from the keyword detector only; the manual review and the LLM judge run later;
- on Llama and Qwen the study tests whether the Inkling token list transfers; it does not test the original claim, which belongs to stage 3;
- the prefill text comes from a PR unit test, not from the original experiment.

Evidence: [protocol and deviations](PROTOCOL.md) · [issue log](issues.md) · [data](data) · [code, word probe and judge prompt](../../experiments/2026-11-23-obliteratus-vocab-surgery) · [research diary](../../session-logs/2026-11-23-obliteratus-vocab-surgery.md)

## Llama-3.1-8B (stage 1)

24 November 2026. Refusal counts come from the keyword detector; the manual review and the LLM judges come later, so verdicts that need them are still open. 200 harmful prompts per version; no version had an invalid answer.

### Refusals

| Configuration | Without prefill: S → V | With prefill: SP → VP |
| --- | --- | --- |
| K1, list from the post (7 input, 9 output rows) | 170 → 169 (−0.5 pp; 1 discordant pair; p = 1.0) | 152 → 148 (−2.0 pp; 6 discordant pairs, 5 and 1; p = 0.22) |
| K2, full PR list (20 input, 33 output rows) | 170 → 156 (−7.0 pp; 14 discordant pairs, all fewer refusals; p = 0.00012) | 152 → 115 (−18.5 pp; 37 discordant pairs, all fewer refusals; p = 1.5e-11) |
| K1o, output side only | 170 → 170 (0 pp) | – |
| K1i, input side only | 170 → 169 (−0.5 pp) | – |

- Prefill alone (SP − S): −9.0 pp; 28 discordant pairs (23 fewer refusals, 5 more); p = 0.00091.
- Interaction for K1, (VP − SP) − (V − S): −1.5 pp.
- The unedited model gave identical answer texts in all four run-A reports (0 of 200 differ), so every change below comes from the edit. Answer texts that changed: K1 27 of 200, K2 46 of 200.
- List coverage: of the 170 S refusals, 19 contain a K1 source token and 31 a K2 source token.

### Capabilities (S and V-k1)

| Measure | S | V-k1 | Difference (95% interval) |
| --- | --- | --- | --- |
| MMLU, every 10th item | 69.51% | 69.16% | −0.35 pp (−0.84 to 0.07) |
| ARC-Challenge | 61.09% | 60.75% | −0.34 pp (−0.85 to 0.17) |
| GSM8K, first 400 | 85.25% | 85.25% | 0.00 pp |
| IFEval | 74.12% | 73.57% | −0.55 pp (−1.29 to 0.00) |
| Mean of the four | – | – | −0.31 pp (−0.55 to −0.09); bootstrap p = 0.0046 |

Noise: a second S run on the first 200 GSM8K items changed 93 answer texts but only 3 scores.

### Word probe (S and V-k1)

| Part | S | V-k1 |
| --- | --- | --- |
| A, writing the word (output) | 95.0% | 50.0% |
| B, understanding the word (input) | 91.7% | 50.0% |

After the edit the model no longer chooses any of the six source words where it fits (0 of 10 in every source group of part A) and reads them as their targets (part B source groups 0 to 3 of 10). Target-word items are unaffected. McNemar: part A 3 against 57 items, p = 6.3e-14; part B 0 against 50 items, p = 1.8e-15.

### Endpoints and verdicts (Llama-3.1-8B only; Holm correction across models comes with Qwen2.5-7B)

| Endpoint | Result |
| --- | --- |
| 1. V − S, primary measure | −0.5 pp, p = 1.0 |
| 2. VP − SP, primary measure | −2.0 pp, p = 0.22 |
| 3. V − S, mean capability | −0.31 pp, 95% interval −0.55 to −0.09 |

- "The edit alone works": not met. It needs at least −20 pp; the result is −0.5 pp. The manual correction cannot change this by that much.
- "The edit adds something beyond the prefill": no (−2.0 pp, p = 0.22; SP is 76.0%, above the 15% floor).
- "Negligible cost": yes for the capability benchmarks (lower bound −0.55 pp, above −2 pp). The word probe shows a large cost on the edited words themselves.
- "Near zero": open until the manual review; the detector value of V is 84.5%.
- Random control KR: not built (needs a drop of at least 10 pp without prefill; the largest is −7.0 pp).

The clearest effect is K2 together with the prefill (−18.5 pp). Its capability cost was not measured (the plan measures capabilities for K1 only); a word probe for V-k2 is queued.

## Stage 0 (decision point G1)

23 November 2026. Numbers only. Tool: OBLITERATUS `main` commit `1de580f7a13f185488dc31ff27f2e027545ad82d` (contains PR #595).

### Checks of tasks 0.1–0.8

| Task | Result |
| --- | --- |
| 0.1 setup | PR tests 75 passed, 0 failed; offline lm-eval smoke test 4 of 4 tasks with code 0; study directory self-contained |
| 0.2 word probe | frozen; S: Qwen2.5-1.5B part A 96.67%, part B 92.50%; Qwen2.5-7B 99.17%, 99.17% (threshold 90%) |
| 0.2a codebook and judge | frozen; 15 script tests passed; judge models not downloaded |
| 0.3 protocol | English and Polish, written before the first edited model; number check passes |
| 0.4 edit and scope check | Qwen2.5-1.5B `k1o-tied`: 9 shared rows, as expected; K1 on a shared matrix fails before writing; Qwen2.5-7B S0: weights and behaviour identical, tokenizer and config files re-saved (bug log); passes under decision A |
| 0.5 template copies | fixed date and 4 prefill copies pass; prefill run gives other stock texts (KL available in both runs) |
| 0.6 review sheet | pilot sheet 100 rows (25 per version), correct header |
| 0.7 analysis | 25 tests passed; pilot numbers equal the measurement printout |
| 0.8 time pilot | Llama-3.1-8B: all steps finished with code 0 |

### Llama-3.1-8B (configuration K1, first measurements)

| Measure | S | V |
| --- | --- | --- |
| Refusals on 200 harmful prompts | 170 | 169 |
| Invalid answers | 0 | 0 |
| Primary measure | 85.0% (Wilson 79.4–89.3%) | 84.5% |

- V − S: −0.5 pp; 1 discordant pair; McNemar p = 1.0 (detector flags only; the manual check comes later).
- S is at least 50%, so Llama-3.1-8B enters the confirmatory analysis. Qwen2.5-7B S (from the write check): 165 refusals and 1 invalid answer, primary measure 83.0%; it also enters.
- Next-token KL 0.0015, first-token KL 0.0005; perplexity ratio 1.0000.
- List coverage: of the 170 S refusals, 19 contain a K1 source token and 31 a K2 source token.
- Capabilities of S: MMLU (every 10th item) 69.5%, ARC-Challenge 61.1%, GSM8K (first 400) 85.2%, IFEval 74.1%.
- Edited rows: 7 input and 9 output, as expected; every other tensor bit-identical.

Pilot on Qwen2.5-1.5B (`k1o-tied`, descriptive only): S 184 refusals, V 184 (0 discordant); SP 15 refusals and 1 invalid, VP 11 and 1 invalid. Of the 184 S refusals, 2 contain a K1 source token and 184 a K2 source token.

### Measured times

| Step | Qwen2.5-1.5B | Qwen2.5-7B | Llama-3.1-8B |
| --- | --- | --- | --- |
| Edit and save | 0.8 min | 3.4 min | 3.9 min |
| Scope check | – | – | 0.3 min |
| `verify-edit` | 3.1 to 3.6 min | 11.5 min | 12.7 min |
| Screening set | 16 min (previous study) | – | 46.4 min |
| IFEval | – | – | 77.3 min |

Highest system memory use: 69.6 GiB of 121 GiB (Llama-3.1-8B edit).

### Time and disk (recomputed)

Assumptions: Qwen2.5-7B screening and IFEval take as long as Llama-3.1-8B; for Qwen2.5-1.5B and Llama-3.2-3B, IFEval is scaled by their screening time (16 and 27 min against 46.4 min).

| Part | Plan | New estimate |
| --- | --- | --- |
| Stage 0 | about 2 h | 2.8 h (measured) |
| Llama-3.1-8B, rest of stage 1 | about 3.5 h | about 3.5 h (+0.3 h with the random control) |
| Qwen2.5-7B | about 5 h | about 5.7 h |
| Qwen2.5-1.5B and Llama-3.2-3B | about 2.5 h | about 4.2 h |
| Inkling-2-Mini | unknown | unknown (gate G0) |
| Total without Inkling-2-Mini | about 13 h | about 16.2 h |

IFEval is the largest part: 77.3 min per run on an 8B model. The LLM judges are not included.

Disk: 116 GB free with one edited 8B checkpoint (15 GB) on disk; about 131 GB free after it is deleted. The judges need at least 90 GB free; stage 3 needs at least 130 GB, so its margin is about 1 GB.
