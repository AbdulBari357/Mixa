import pytest

from mixa.pipeline import analyze, compute_stats
from mixa.pipeline.soundkey import sound_key
from mixa.pipeline.tokenize import tokenize


@pytest.mark.parametrize(
    "group",
    [
        ["bahut", "bohot", "bahot", "bht", "bahuttt"],
        ["hai", "he", "hy", "hay"],
        ["samajh", "samaj", "samjh"],
        ["kya", "kia"],
        ["nahi", "nhi"],
        ["7abibi", "habibi"],
        ["ba3d", "baad"],
    ],
)
def test_spellings_by_ear_share_a_key(group):
    assert len({sound_key(w) for w in group}) == 1, {w: sound_key(w) for w in group}


def test_short_words_with_different_final_vowels_stay_apart():
    assert sound_key("hai") != sound_key("ho")


def test_non_latin_word_has_no_key():
    assert sound_key("बहुत") is None


def test_tokenizer_keeps_arabizi_devanagari_and_apostrophes_whole():
    words = [t.text for t in tokenize("ana coming ba3d, I'll call 7abibi भाई 😂😂")]
    assert words == ["ana", "coming", "ba3d", ",", "I'll", "call", "7abibi", "भाई", "😂😂"]


def test_tokenizer_offsets_point_back_into_the_text():
    text = "kal meeting hai?"
    assert all(text[t.start : t.end] == t.text for t in tokenize(text))


def test_code_mixing_index():
    assert compute_stats(["en", "en", "other"]).cmi == 0
    stats = compute_stats(["hi-ur", "en", "hi-ur", "hi-ur", "other"])
    assert stats.cmi == 25.0
    assert stats.switch_points == 2
    assert stats.languages == ["hi-ur", "en"]


@pytest.mark.parametrize(
    "english",
    ["Can you send me the report before 5pm?", "Got it, will follow the guidelines!"],
)
def test_plain_english_is_not_tagged_as_hindi(english):
    langs = {t.lang for t in analyze(english, with_meaning=False).tokens}
    assert langs <= {"en", "other"}


def test_analyze_labels_a_mixed_sentence_without_meaning():
    res = analyze("bhai kal meeting hai, ana coming ba3d", with_meaning=False)
    langs = {t.text: t.lang for t in res.tokens}
    assert langs["bhai"] == "hi-ur"
    assert langs["meeting"] == "en"
    assert langs["ba3d"] == "ar"
    assert langs[","] == "other"
    assert set(res.stats.languages) == {"hi-ur", "en", "ar"}
