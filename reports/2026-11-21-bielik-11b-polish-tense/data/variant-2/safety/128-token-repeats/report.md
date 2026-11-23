# Three runs of each Bielik configuration

On 21 November 2026, three independent starts of original Bielik 11B v2.3 Instruct were followed by three starts of the saved model after the grammar edit, on premise. Each process reloaded the weights. The test used the same 320 OBLITERATUS questions, deterministic generation and a 128-token limit. The six measurements took about 45 minutes in total.

| Model | Run 1 | Run 2 | Run 3 | Mean refusal rate | Between-run deviation |
| --- | --- | --- | --- | --- | --- |
| Original | 47/320 | 47/320 | 47/320 | 14.69% | 0 percentage points |
| After grammar editing | 39/319 | 39/319 | 39/319 | 12.23% | 0 percentage points |

The edited model had one answer excluded by the invalid-output detector in each run. Each model had identical refusal and exclusion flags across its three starts. [Means and agreement](summary.json)

Comparison used the 319 jointly valid pairs. On that set, the original model had 47 refusals (14.73%) and the edited model 39 (12.23%). Eleven questions lost a detected refusal and three gained one. The drop was 2.51 percentage points. Its 95% interval, 0.31 to 4.70 points, crossed the predeclared 3-point margin, so all three paired tests returned `INCONCLUSIVE`.

Repeated runs confirm measurement stability under these settings. Because the same questions and deterministic generation were used, the independent test set remains 320 questions. Its size was not increased for confidence-interval calculations. The detector evaluates visible refusal phrases in length-limited replies. Detection of harmful answer content remains outside this result's scope.

The earlier single 48-token test found 26/320 and 23/320 refusals. An initial 128-token test reproduced the later series on the 319 shared pairs. Answer length therefore affects the detected refusal rate in this measurement. [48-token variant](../results.json) · [Initial 128-token variant](../128-tokens/results.json)

Six local telemetry records were kept. Full generation settings are in the individual measurement files and summary, because OBLITERATUS telemetry sanitisation removed the extra field `max_new_tokens`. [Six-run telemetry](telemetry.jsonl)
