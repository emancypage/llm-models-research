# GSM8K • correct before the edit, incorrect after it

Each case shows the same math problem and both saved answers. The original model gave the expected number. The version with 500 selected vocabulary entries gave a different number or the scorer could not extract the expected number. These are all such cases among the first 400 GSM8K test problems at a limit of 1024 new tokens.

## Llama 3.1 8B Instruct

Original **341/400** correct. Edited **292/400** correct. The edit changed 52 scores from correct to incorrect and 3 from incorrect to correct.

- [Cases 1–8](llama-01-08.md)
- [Cases 9–16](llama-09-16.md)
- [Cases 17–24](llama-17-24.md)
- [Cases 25–32](llama-25-32.md)
- [Cases 33–40](llama-33-40.md)
- [Cases 41–48](llama-41-48.md)
- [Cases 49–52](llama-49-52.md)

Edited answers that re-encode to the 1024-token limit in these cases: **16 of 52**. The evaluation saved the text without a per-answer stop reason.

## Qwen2.5 7B Instruct

Original **348/400** correct. Edited **350/400** correct. The edit changed 5 scores from correct to incorrect and 7 from incorrect to correct.

- [Cases 1–5](qwen-01-05.md)

Edited answers that re-encode to the 1024-token limit in these cases: **0 of 5**. The evaluation saved the text without a per-answer stop reason.

## How to read the cases

Case numbers show the order within each model. The GSM8K item number is the zero-based test-set row. The expected answer comes from the dataset. The extracted value is what the benchmark used for scoring. Both model answers are shown in their original wording, including mistakes, repetition and abrupt endings.

Math problems and reference numbers come from [GSM8K](https://github.com/openai/grade-school-math), copyright 2021 OpenAI. [Dataset license](LICENSE.txt)
