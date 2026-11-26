# GSM8K items that lost benchmark credit after the edit

Each case shows the question and both saved answers. The flexible-extraction scorer awarded the original answer 1 point and the selected-list answer 0. A score of 0 can reflect a wrong solution, an unfinished answer or a mismatch between the extracted text and the reference. These are all such cases among the first 400 GSM8K test problems at a limit of 1024 new tokens.

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

In Qwen items 19 and 109, the edited answer states the correct mathematical result. The scorer extracted 4 after the model gave the required speed of 6, and rejected `$28.00.` against `28`. [Two examples in context](qwen-01-05.md)

Case numbers show the order within each model. The GSM8K item number is the zero-based test-set row. The expected answer comes from the dataset. The extracted value is what the benchmark used for scoring. Both model answers are shown in their original wording, including mistakes, repetition and abrupt endings.

Math problems and reference numbers come from [GSM8K](https://github.com/openai/grade-school-math), copyright 2021 OpenAI. [Dataset license](LICENSE.txt)
