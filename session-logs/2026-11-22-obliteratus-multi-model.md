# Multi-model repair study: research diary, 22 November 2026

This is an anonymized research-only version of the early session handoff. It records an intermediate state, before the final reports. The later [protocol](../reports/2026-11-22-obliteratus-multi-model/PROTOCOL.md) and [results](../reports/2026-11-22-obliteratus-multi-model/results.md) contain the final decisions and measurements. Operational instructions, private paths, identities and communication drafts are omitted.

## Stage 0 and acceptance checks

The study extended the [Qwen2.5-1.5B capability study](../reports/2026-11-21-qwen2.5-1.5b-recipe/capabilities/results.md) to several models and repair settings. It tested `adapter.lora_repair` (OBLITERATUS #578). Stage-0 tooling passed its acceptance checks; the English and Polish protocol and an issue log with 8 entries existed at this point. The issue log was expanded later.

OBLITERATUS revision: `7678d84` (full revision in the protocol). The study-1 material was mounted read-only in study containers. Builds used the v2 recipe on CPU in fp32 and exported both projection P and repair R in bf16; fp32 copies were temporary intermediates. Repair placement followed the projection layers. A preset kept its template placement.

The refusal wrapper retained the per-prompt refusal and invalid flags that `verify_edit.runner._strip` otherwise discards. It reproduced the study-1 E/P/R refusal counts exactly: 15/199, 14/199 and 22/200; over-refusals: 3/199, 3/199 and 4/199. Stock-model flags were identical between the checks.

The multi-model analysis reproduced the study-1 capability summary, secondary summary and per-item vectors exactly. Its configuration mapped arms to evaluation outputs and could name a stock repeat, verification reports and comparisons. Outputs included per-model JSON and endpoints. An acceptance configuration used study-1 data. A leak check found 625 distinct repair prompts disjoint from `tune`, `final_test` and the 4 benchmark question sets.

## Resource and scheduling observations

Separate CPU and GPU queues ran unattended on an on premise machine. Jobs had a name, dependencies and a command. The runner reread its queue on each cycle; a failed dependency caused dependent jobs to be skipped. Per-job exit state, logs and a summary were retained privately. A disk guard stopped the runner below 20 GB free. A memory guard stopped study containers when available memory was below 16 GiB. Job time and peak whole-system memory were measured. These measures included other services.

Q1 PS1, projection only, had been built in 330 s. Q3, L3 and L8 had been downloaded. At this snapshot Q3 R0 self-distillation ran on the GPU without batching and was slow. A Q3 CPU build pilot used 50 steps and about 33 GB; its completion was still pending. The pilot checkpoint was disposable; its timing and memory were to be recorded before full builds. Historical search timing from the study-1 research draft: 5 recipe variants took about 57 min.

## Model and design state at this snapshot

Llama access was granted on 22 November. Llama tokenizers lacked a pad token required by repair training. A stock copy set `pad_token` to `<|finetune_right_pad_id|>`, id 128004. Every Llama arm used that copy, a recorded protocol deviation.

The L3 family preset was `qwen38_e03`, with `middle60` resolving to layers 5–21. L8 used accepted recipe `llama3.1-8b-e03-reg02`, layers 6–24, a 100 GB build memory limit and no parallel jobs during its build. Q3 recipe selection was not complete: 5 variants were planned, with `kl_policy: advisory`, ranked by fewest tune refusals and then lowest next-token KL.

The PS screening set used every 10th MMLU item per subject (1430 items), full ARC and the first 400 GSM8K questions. The acceptance rule was a mean drop of at least 3 pp against stock and a harmless valid rate of at least 95%. Candidate order: widened layers with 1 direction; recipe layers with 4 directions; widened layers with 2 directions and regularization 0. Selection had to be recorded before full PS/RS evaluation. RS repair placement follows PS, so it is not an equal-placement comparison with R0.

RK was blocked at this stage: `recovery-distill` rejected every `BUILTIN_HARMFUL` prompt, which covered the protocol's harmful prompts. No replacement harmful-prompt dataset had been selected. This is a historical state; the later protocol records a disjointness-check deviation and the completed RK result.

## Planned but unfinished work at this snapshot

The GPU queue included Q1 RB distillation, L3 R0 distillation, Q1 S/PS1 screening, Q1 PS1 verification, Q3 recipe search, Q1 RG build/evaluation/verification through the adapter, seed evaluations and verifications, Q3 S evaluation/repeat, and L3 P verification plus S evaluation/repeat. The CPU queue included Q1 R0 seeds 43 and 44, Q1 RB and L3 R0 builds.

Q3 builds waited for its recipe search: R0, seeds 43 and 44 and PS candidates were planned, followed by RS after PS selection. Full P/R0/PS/RS evaluations and verifications for Q3, L3 and L8, L3 seeds, the L8 stage and final reports remained. The L8 fallback was RG if a CPU build exceeded 10 h. The later shortened plan dropped several of these jobs; this diary does not claim they ran.

## Research safeguards and limits

There was no recipe confirmation, weight upload or model publication. The study-1 search checkpoints were retained at this stage (15 GB). In lm-eval, `--samples` and `--limit` were not to be combined. Prompt/answer texts, raw logs and model checkpoints were not part of the research publication. The correspondence drafts repeat results already available in the reports and are omitted.
