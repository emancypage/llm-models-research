# Token exposure in the quality benchmarks

Post hoc analysis after closeout (26 November 2026, exploratory).

D500 is the selected list and KR500 is the random list. Each contains 500 output token IDs. One loss means an originally correct item lost credit. One gain means an originally incorrect item gained credit. [Methods and file definitions](README.md) · [Machine-readable counts](summary.json)

## Categories in each list

| Model | List | A–D pieces | Actual MMLU letters edited | Digits | Punctuation | Whitespace only | Contains newline | ≤2 characters | Alphabetic words or pieces |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Llama | D500 | 0 | None | 10 | 0 | 0 | 0 | 48 | 470 |
| Llama | KR500 | 1 | A | 5 | 8 | 0 | 2 | 39 | 473 |
| Qwen | D500 | 0 | None | 0 | 0 | 0 | 0 | 124 | 492 |
| Qwen | KR500 | 1 | B | 3 | 6 | 0 | 3 | 35 | 483 |

## GSM8K at 1024 tokens

Each line partitions the same 400 reference answers into two groups. Losses can occur only among originally correct items.

| Model | List | Reference text | Token group | Exposed | Original correct (exposed) | Losses (exposed) | Gains (exposed) | Unexposed | Original correct (unexposed) | Losses (unexposed) | Gains (unexposed) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Llama | D500 | Whole solution | Any listed ID | 193 | 161 | 49 | 2 | 207 | 180 | 3 | 1 |
| Llama | D500 | Whole solution | All digit IDs | 82 | 64 | 45 | 1 | 318 | 277 | 7 | 2 |
| Llama | D500 | Whole solution | Five review IDs | 75 | 58 | 42 | 1 | 325 | 283 | 10 | 2 |
| Llama | D500 | Final number | Any listed ID | 26 | 19 | 17 | 0 | 374 | 322 | 35 | 3 |
| Llama | D500 | Final number | All digit IDs | 26 | 19 | 17 | 0 | 374 | 322 | 35 | 3 |
| Llama | D500 | Final number | Five review IDs | 23 | 16 | 15 | 0 | 377 | 325 | 37 | 3 |
| Llama | KR500 | Whole solution | Any listed ID | 371 | 315 | 221 | 6 | 29 | 26 | 1 | 0 |
| Llama | KR500 | Whole solution | All digit IDs | 285 | 240 | 208 | 3 | 115 | 101 | 14 | 3 |
| Llama | KR500 | Final number | Any listed ID | 26 | 24 | 24 | 0 | 374 | 317 | 198 | 6 |
| Llama | KR500 | Final number | All digit IDs | 26 | 24 | 24 | 0 | 374 | 317 | 198 | 6 |
| Qwen | D500 | Whole solution | Any listed ID | 146 | 125 | 2 | 1 | 254 | 223 | 3 | 6 |
| Qwen | D500 | Whole solution | All digit IDs | 0 | 0 | 0 | 0 | 400 | 348 | 5 | 7 |
| Qwen | D500 | Final number | Any listed ID | 0 | 0 | 0 | 0 | 400 | 348 | 5 | 7 |
| Qwen | D500 | Final number | All digit IDs | 0 | 0 | 0 | 0 | 400 | 348 | 5 | 7 |
| Qwen | KR500 | Whole solution | Any listed ID | 397 | 345 | 285 | 7 | 3 | 3 | 0 | 0 |
| Qwen | KR500 | Whole solution | All digit IDs | 361 | 313 | 280 | 7 | 39 | 35 | 5 | 0 |
| Qwen | KR500 | Final number | Any listed ID | 228 | 207 | 207 | 0 | 172 | 141 | 78 | 7 |
| Qwen | KR500 | Final number | All digit IDs | 228 | 207 | 207 | 0 | 172 | 141 | 78 | 7 |

## GSM8K at 256 tokens

Each line partitions the same 400 reference answers into two groups. Losses can occur only among originally correct items.

| Model | List | Reference text | Token group | Exposed | Original correct (exposed) | Losses (exposed) | Gains (exposed) | Unexposed | Original correct (unexposed) | Losses (unexposed) | Gains (unexposed) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Llama | D500 | Whole solution | Any listed ID | 193 | 161 | 49 | 2 | 207 | 180 | 3 | 1 |
| Llama | D500 | Whole solution | All digit IDs | 82 | 64 | 45 | 1 | 318 | 277 | 7 | 2 |
| Llama | D500 | Whole solution | Five review IDs | 75 | 58 | 42 | 1 | 325 | 283 | 10 | 2 |
| Llama | D500 | Final number | Any listed ID | 26 | 19 | 17 | 0 | 374 | 322 | 35 | 3 |
| Llama | D500 | Final number | All digit IDs | 26 | 19 | 17 | 0 | 374 | 322 | 35 | 3 |
| Llama | D500 | Final number | Five review IDs | 23 | 16 | 15 | 0 | 377 | 325 | 37 | 3 |
| Llama | KR500 | Whole solution | Any listed ID | 371 | 315 | 221 | 5 | 29 | 26 | 1 | 0 |
| Llama | KR500 | Whole solution | All digit IDs | 285 | 240 | 208 | 2 | 115 | 101 | 14 | 3 |
| Llama | KR500 | Final number | Any listed ID | 26 | 24 | 24 | 0 | 374 | 317 | 198 | 5 |
| Llama | KR500 | Final number | All digit IDs | 26 | 24 | 24 | 0 | 374 | 317 | 198 | 5 |
| Qwen | D500 | Whole solution | Any listed ID | 146 | 102 | 2 | 3 | 254 | 195 | 9 | 7 |
| Qwen | D500 | Whole solution | All digit IDs | 0 | 0 | 0 | 0 | 400 | 297 | 11 | 10 |
| Qwen | D500 | Final number | Any listed ID | 0 | 0 | 0 | 0 | 400 | 297 | 11 | 10 |
| Qwen | D500 | Final number | All digit IDs | 0 | 0 | 0 | 0 | 400 | 297 | 11 | 10 |
| Qwen | KR500 | Whole solution | Any listed ID | 397 | 294 | 240 | 9 | 3 | 3 | 0 | 0 |
| Qwen | KR500 | Whole solution | All digit IDs | 361 | 265 | 237 | 9 | 39 | 32 | 3 | 0 |
| Qwen | KR500 | Final number | Any listed ID | 228 | 173 | 173 | 0 | 172 | 124 | 67 | 9 |
| Qwen | KR500 | Final number | All digit IDs | 228 | 173 | 173 | 0 | 172 | 124 | 67 | 9 |

## Listed IDs in re-tokenized GSM8K answers

| Model | List | Token limit | Original answers with a listed ID | Edited answers with a listed ID | Edited answers with a listed digit | Listed occurrences in edited answers |
| --- | --- | --- | --- | --- | --- | --- |
| Llama | D500 | 1024 | 177 | 0 | 0 | 0 |
| Llama | D500 | 256 | 176 | 0 | 0 | 0 |
| Llama | KR500 | 1024 | 381 | 0 | 0 | 0 |
| Llama | KR500 | 256 | 381 | 0 | 0 | 0 |
| Qwen | D500 | 1024 | 219 | 0 | 0 | 0 |
| Qwen | D500 | 256 | 216 | 0 | 0 | 0 |
| Qwen | KR500 | 1024 | 398 | 10 | 0 | 10 |
| Qwen | KR500 | 256 | 398 | 3 | 0 | 3 |

## MMLU by correct letter

| Model | List | Correct letter | Letter edited | Items | Original correct | Losses | Gains |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Llama | D500 | A | No | 316 | 200 | 0 | 0 |
| Llama | D500 | B | No | 344 | 247 | 0 | 0 |
| Llama | D500 | C | No | 390 | 271 | 0 | 0 |
| Llama | D500 | D | No | 380 | 276 | 0 | 0 |
| Llama | KR500 | A | Yes | 316 | 200 | 200 | 0 |
| Llama | KR500 | B | No | 344 | 247 | 0 | 22 |
| Llama | KR500 | C | No | 390 | 271 | 0 | 19 |
| Llama | KR500 | D | No | 380 | 276 | 0 | 13 |
| Qwen | D500 | A | No | 316 | 225 | 0 | 0 |
| Qwen | D500 | B | No | 344 | 268 | 0 | 0 |
| Qwen | D500 | C | No | 390 | 310 | 0 | 0 |
| Qwen | D500 | D | No | 380 | 297 | 0 | 0 |
| Qwen | KR500 | A | No | 316 | 225 | 0 | 18 |
| Qwen | KR500 | B | Yes | 344 | 268 | 268 | 0 |
| Qwen | KR500 | C | No | 390 | 310 | 0 | 16 |
| Qwen | KR500 | D | No | 380 | 297 | 0 | 18 |

## ARC-Challenge by correct and incorrect option text

| Model | List | Correct option exposed | Any incorrect option exposed | Items | Original correct | Losses | Gains |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Llama | D500 | Yes | Yes | 44 | 23 | 16 | 0 |
| Llama | D500 | Yes | No | 48 | 26 | 26 | 0 |
| Llama | D500 | No | Yes | 136 | 79 | 0 | 14 |
| Llama | D500 | No | No | 944 | 588 | 3 | 1 |
| Llama | KR500 | Yes | Yes | 611 | 384 | 151 | 30 |
| Llama | KR500 | Yes | No | 45 | 23 | 23 | 0 |
| Llama | KR500 | No | Yes | 166 | 104 | 0 | 15 |
| Llama | KR500 | No | No | 350 | 205 | 1 | 2 |
| Qwen | D500 | Yes | Yes | 40 | 26 | 17 | 0 |
| Qwen | D500 | Yes | No | 50 | 32 | 30 | 0 |
| Qwen | D500 | No | Yes | 118 | 76 | 0 | 10 |
| Qwen | D500 | No | No | 964 | 654 | 1 | 0 |
| Qwen | KR500 | Yes | Yes | 426 | 286 | 148 | 19 |
| Qwen | KR500 | Yes | No | 60 | 39 | 36 | 0 |
| Qwen | KR500 | No | Yes | 298 | 215 | 0 | 27 |
| Qwen | KR500 | No | No | 388 | 248 | 1 | 4 |

## GSM8K original repeat and selected edit at 256 tokens

Each row uses the same original run and the same subset of the first 200 questions. Exposure refers to tokens in the full reference solution.

| Model | D500 reference group | Items | Original correct | Repeat losses | Repeat gains | D500 losses | D500 gains |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Llama | digits unexposed | 162 | 142 | 2 | 1 | 4 | 2 |
| Llama | review five unexposed | 166 | 145 | 2 | 1 | 5 | 2 |
| Llama | digits exposed | 38 | 25 | 0 | 0 | 17 | 0 |
| Llama | review five exposed | 34 | 22 | 0 | 0 | 16 | 0 |
| Qwen | digits unexposed | 200 | 147 | 5 | 3 | 6 | 5 |
