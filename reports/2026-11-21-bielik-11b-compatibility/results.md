# Bielik 11B compatibility check

This check tested whether OBLITERATUS could modify one feed-forward layer in Bielik 11B and then restore the original weights. The model answered eight Polish prompts before and after the edit. It matched the reference answer on seven items before the edit and six after it. After restoration, the control logits exactly matched the original values. [First measurement](data/first-measurement.json) · [Results](data/results.json) · [Evaluation code](../../experiments/2026-11-21-bielik-11b-compatibility/check.py)

The table gives English descriptions of the original tasks. The Polish prompts, targets and recorded answers are preserved so that the scores can be checked against the wording the model saw. [Original questions and targets](../../experiments/2026-11-21-bielik-11b-compatibility/polish-questions.json)

| Item ID | Task |
| --- | --- |
| `odmiana` | Supply the correct grammatical form of “cat” in a sentence about looking at two cats. |
| `polskie-znaki` | Remove the first letter of the Polish word for “turtle” and preserve the remaining diacritics. |
| `czytanie` | Name the person who received a key. |
| `arytmetyka` | Calculate how many crayons remain after seven are given away and three are added to an initial 24. |
| `ekstrakcja` | Extract the application identifier from a note. |
| `brak-informacji` | Report missing information when a note gives a train’s arrival day but no time. |
| `negacja` | Identify which of two invited people attended. |
| `json` | Extract a city and parcel count into a JSON object with the requested Polish field names. |

The question file uses `pytanie` for the prompt and `wzorzec` for the reference answer. In both result files, `odpowiedz` is the model’s answer, `zgodna_ze_wzorcem` indicates whether it matched the reference, and `wygenerowane_tokeny` is the number of generated tokens.

[Measurement protocol](PROTOCOL.md) · [Reproduction instructions](../../experiments/2026-11-21-bielik-11b-compatibility/README.md)
