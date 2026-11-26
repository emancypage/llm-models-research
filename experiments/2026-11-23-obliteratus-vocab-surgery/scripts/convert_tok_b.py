"""Builds a fast tokenizer for judge B from its SentencePiece tokenizer.model with protobuf only (no new packages).

usage: convert_tok_b.py <judge-b-dir> <out-dir>
Checks: added tokens keep their IDs, chat markers are single tokens, encode/decode round trips on the study texts.
"""
import json
import sys
from pathlib import Path

from transformers import PreTrainedTokenizerFast
import transformers.convert_slow_tokenizer as cst
from transformers.convert_slow_tokenizer import LlamaConverter


def _extractor_init(self, model):
    # Same as SentencePieceExtractor.__init__ without the sentencepiece check: extract() only reads the protobuf.
    m = cst.import_protobuf().ModelProto()
    with open(model, "rb") as f:
        m.ParseFromString(f.read())
    self.proto = m


def _extract(self, vocab_scores=None):
    # The converter calls the older extract(vocab_scores) -> (vocab, merges) form; rebuild it from the protobuf.
    import inspect

    from transformers.tokenization_utils_base import generate_merges

    vocab = {piece.piece: index for index, piece in enumerate(self.proto.pieces)}
    if "vocab_scores" in inspect.signature(generate_merges).parameters and vocab_scores is not None:
        return vocab, generate_merges(vocab, vocab_scores)
    return vocab, generate_merges(vocab)


cst.SentencePieceExtractor.__init__ = _extractor_init
cst.SentencePieceExtractor.extract = _extract

src, out = Path(sys.argv[1]), Path(sys.argv[2])
config = json.loads((src / "tokenizer_config.json").read_text())


class Original:
    vocab_file = str(src / "tokenizer.model")
    legacy = config.get("legacy", False)
    add_prefix_space = config.get("add_prefix_space")
    add_bos_token = config.get("add_bos_token", True)
    add_eos_token = config.get("add_eos_token", False)
    bos_token, eos_token, unk_token = "<s>", "</s>", "<unk>"

    def __init__(self):
        from transformers.convert_slow_tokenizer import import_protobuf

        proto = import_protobuf().ModelProto()
        proto.ParseFromString(Path(self.vocab_file).read_bytes())
        self.pieces = [p.piece for p in proto.pieces]

    def convert_ids_to_tokens(self, index):
        return self.pieces[index]

    def __getattr__(self, name):
        return None


backend = LlamaConverter(Original()).converted()
tok = PreTrainedTokenizerFast(tokenizer_object=backend, bos_token="<s>", eos_token="</s>", unk_token="<unk>",
                              add_bos_token=Original.add_bos_token, add_eos_token=Original.add_eos_token)
added = json.loads((src / "added_tokens.json").read_text()) if (src / "added_tokens.json").exists() else {}
for text, token_id in sorted(added.items(), key=lambda kv: kv[1]):
    if tok.convert_tokens_to_ids(text) != token_id:
        tok.add_tokens([text], special_tokens=True)
problems = {t: (tok.convert_tokens_to_ids(t), i) for t, i in added.items() if tok.convert_tokens_to_ids(t) != i}
markers = {m: tok.encode(m, add_special_tokens=False) for m in ("<|user|>", "<|assistant|>", "[INST]", "[/INST]")}
from rows import harmful_prompts  # noqa: E402
from obliteratus.verify_edit.heldout import load_heldout  # noqa: E402

spec = json.loads(Path("/work/runs/spec.json").read_text())
held = load_heldout(spec["heldout"], None)
texts = list(held["harmful"]) + list(held["harmless"]) + [i["text"] for i in json.loads(Path("/work/probe/items.json").read_text())]
report = json.loads(Path("/work/runs/l8/verify-V-k1/report.json").read_text())["measurement"]
texts += report["stock"]["harmful"]["texts"] + report["edited"]["harmful"]["texts"]
roundtrip = sum(tok.decode(tok.encode(t, add_special_tokens=False)) != t for t in texts)
unk = sum(tok.unk_token_id in tok.encode(t, add_special_tokens=False) for t in texts)
out.mkdir(parents=True, exist_ok=True)
tok.save_pretrained(out)
result = {"vocab_size": len(tok), "added_id_problems": problems, "markers": markers, "texts": len(texts),
          "roundtrip_mismatches": roundtrip, "texts_with_unk": unk, "bos_first": tok("Hi").input_ids[:1] == [tok.bos_token_id]}
(out / "conversion-check.json").write_text(json.dumps(result, indent=1) + "\n")
print(json.dumps(result))
