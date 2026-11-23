# Bielik 11B and Polish grammatical tense

On 21 November 2026, OBLITERATUS stopped during validation, before changing weights. The saved report returned `fail` with reason `lexical_confound`. A simple text classifier could distinguish tenses almost as well as the signal found in the model using the written verb forms alone. The AUC gap was 0.033, below the project's required minimum of 0.05. [Original validation report](data/isolated-form-validation.json)

| Measurement | Result |
| --- | --- |
| Polish Belebele, original model | 782/900 correct (86.9%). The model selected one of four letters by next-token probability. |
| Tense recognition, original model | 64/64 correct for 32 held-out verb pairs. None of these verbs was used to extract the concept. |
| Concept extraction | 64 pairs of past/present forms from UD Polish-LFG training data. OBLITERATUS examined 50 layers and selected layer index 0. |
| Validation | Model signal AUC 0.998817; text classifier AUC 0.965915. Validation blocked the intervention. |

No edited weights, post-edit results or completed-procedure `community_results` record were produced. The baseline and validation report remain available for reproduction. [Protocol and pinned revisions](data/protocol.json) · [900-question results](data/belebele-before.json) · [UD Polish-LFG](https://universaldependencies.org/treebanks/pl_lfg/index.html) · [Belebele](https://huggingface.co/datasets/facebook/belebele)
