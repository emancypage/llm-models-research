# Publication guidelines

Publish research on locally run language models, including the methods, measurements, code, failures and limitations of each study.

## Directory layout for new studies

Give each study one ID: `YYYY-MM-DD-short-research-question`. Use the study's start date and a descriptive English slug in lowercase with hyphens, for example `2026-11-23-qwen-answer-length`. Use the same ID wherever that study has files.

```text
reports/
  <study-id>/
    PROTOCOL.md          Question, model revisions, conditions and scoring
    results.md           Main findings, limitations and links to the evidence
    data/                Measurements and tables used in the report
      <condition>/       Separate a pilot, model variant or repeat when needed
    issues.md            Substantial failures and their effect on the findings
experiments/
  <study-id>/            Evaluation and analysis code specific to this study
    README.md            How to reproduce the measurements
session-logs/
  <study-id>.md          Dated decisions made during the study
```

- Start by checking the study index in the published root `README.md`. A new research question gets a new ID. A pilot, additional model, new seed, correction or follow-up that answers the same question belongs to the existing study. For earlier studies, use their existing paths.
- Create only the files and directories the study needs. Record a small caveat in `results.md`. Use `issues.md` for a longer investigation and the session log for decisions that explain changes to the protocol.
- Keep one main report. Give comparable runs separate paths under `data/` when their filenames would collide, for example `data/pilot/run-01/` and `data/pilot/run-02/`. Preserve earlier measurements and identify the run behind each reported result.
- Reuse an existing evaluation script when it fits. Link to it from the protocol without copying it into a new study. Keep model weights, caches, raw generations and runtime logs outside the tracked tree.
- When publishing a new study, add one entry to the root `README.md` linking to its report. Link the protocol, supporting data and applicable code from the report using relative paths. Check those links in a clean checkout.

## Publication language

Write reports, protocols, READMEs, tables and research notes in English. Use English filenames without a language suffix, such as `README.md` and `results.md`. Translate any outstanding text before publishing. Check that links work in a clean checkout.

Keep Polish translations locally under names such as `README.pl.md` and `results.pl.md`. The `*.pl.*` rule in `.gitignore` excludes them. Never stage or force-add these files. Preserve the original wording of prompts, model responses and scoring targets used as experimental data.
