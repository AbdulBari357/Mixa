"""Build ml/testsets/uae_lid.tsv: a small hand-labelled test set for the UAE mix.

Public code-switching benchmarks (e.g. LinCE) have Hinglish but no Arabizi and no
three-way Hindi/Urdu + Arabic + English messages, which is exactly what people in
the UAE write. These 52 sentences were written and labelled by one Mixa team member
(no second annotator). They are TEST ONLY: never train on them, tune on them, or show
them to an LLM that generates training data. The 8 "gulf" sentences were added after an
audit found the others contain almost no Gulf spellings; they were written before the
current model and silver data existed.

Labels per word token as produced by our tokenizer (punctuation, emoji and plain
numbers are excluded, as at inference): e=en, h=hi-ur, a=ar, n=ne.
Conventions: a word gets the language it is used in, by meaning in context (Arabic "ana"
= I is ar even inside a Hindi sentence); established English loans keep en (mummy,
tension, late); Arabic formulas (inshallah, wallah, mashallah) are ar wherever they
appear; days and language names are en; every word of a multi-word place or brand name
is ne (Sheikh Zayed road, Dubai Mall).

    docker compose run --rm api python ml/build_uae_testset.py
"""

from pathlib import Path

from mixa.pipeline.tokenize import tokenize

CODES = {"e": "en", "h": "hi-ur", "a": "ar", "n": "ne"}

SENTENCES = [
    # Hinglish
    ("hinglish", "yaar kal ki party cancel ho gayi kya", "h h h e e h h h"),
    ("hinglish", "main abhi office se nikal raha hoon", "h h e h h h h"),
    ("hinglish", "the main problem is ki koi reply nahi karta", "e e e e h h e h h"),
    ("hinglish", "bro ye movie bohot boring thi, I slept halfway", "e h e h e h e e e"),
    ("hinglish", "mujhe lagta hai we should leave early", "h h h e e e e"),
    ("hinglish", "assignment submit karne ki last date kab hai", "e e h h e e h h"),
    ("hinglish", "mummy bol rahi thi ke tum late aaoge", "e h h h h h e h"),
    ("hinglish", "he is so annoying yaar, har baar same joke", "e e e e h h h e e"),
    ("hinglish", "chal theek hai, see you tomorrow", "h h h e e e"),
    ("hinglish", "Rahul ne bola tha ki meeting 5 baje hai", "n h h h h e h h"),
    ("hinglish", "please mujhe notes bhej do jab free ho", "e h e h h h e h"),
    ("hinglish", "to phir kya plan hai weekend ka", "h h h e h e h"),
    # Roman Urdu
    ("roman-urdu", "aap kaisay hain, bohat din ho gaye", "h h h h h h h"),
    ("roman-urdu", "mera phone kharab ho gaya hai, repair karwana hai", "h e h h h h e h h"),
    ("roman-urdu", "kal Karachi ja raha hoon, wapas Monday ko aaunga", "h n h h h h e h h"),
    ("roman-urdu", "yar mujhe samajh nahi aa raha ke kya karoon", "h h h h h h h h h"),
    ("roman-urdu", "shukriya, aap ka kaam bohat acha tha", "h h h h h h h"),
    ("roman-urdu", "main ne email kar di hai, check kar lein", "h h e h h h e h h"),
    ("roman-urdu", "exam ki tayyari kaisi chal rahi hai", "e h h h h h h"),
    ("roman-urdu", "bas thora sa wait karo, main aa raha hoon", "h h h e h h h h h"),
    # Arabizi + English
    ("arabizi", "ana fel mall, enta wein?", "a a e a a"),
    ("arabizi", "yalla habibi, the movie starts ba3d 10 minutes", "a a e e e a e"),
    ("arabizi", "shu el plan today?", "a a e e"),
    ("arabizi", "wallah I forgot, sorry 7abibti", "a e e e a"),
    ("arabizi", "3ndi exam bukra, need to study", "a e a e e e"),
    ("arabizi", "khalas, ana jay now", "a a a e"),
    ("arabizi", "el traffic kteer 3al Sheikh Zayed road", "a e a a n n n"),
    ("arabizi", "inshallah we'll meet next week", "a e e e e"),
    ("arabizi", "mashallah your Arabic is getting better", "a e e e e e"),
    ("arabizi", "la2 ma 3ndi wa2t today, maybe bukra", "a a a a e e a"),
    ("arabizi", "keefak? kil shi tamam?", "a a a a"),
    ("arabizi", "ya3ni I don't know, shoof enta", "a e e e a a"),
    # Three-way: Hindi/Urdu + Arabic + English
    ("three-way", "bhai ana coming ba3d shwaya, traffic bohot hai", "h a e a a e h h"),
    ("three-way", "khalas yaar, kal baat karte hain inshallah", "a h h h h h a"),
    ("three-way", "habibi tension mat lo, sab theek ho jayega", "a e h h h h h h"),
    ("three-way", "yalla chalo, we're getting late yaar", "a h e e e h"),
    ("three-way", "wallah bohot mushkil exam tha", "a h h e h"),
    ("three-way", "ana bhi aa raha hoon, wait karo", "a h h h h e h"),
    ("three-way", "shukran bhai, you saved me today", "a h e e e e"),
    ("three-way", "mafi mushkil, kal milte hain", "a a h h h"),
    # Gulf Arabizi: 6 = ط, 9 = ص, 3' = غ, ch = ك, Emirati vocabulary
    ("gulf", "shlonak? wayed ta3ban today", "a a a e"),
    ("gulf", "ana abi a7jiz table for dinner", "a a a e e e"),
    ("gulf", "el jaw 7ar wayed, 6ab3an I'm staying home", "a a a a a e e e"),
    ("gulf", "zain, meeting 3la 9 o'clock", "a e a e"),
    ("gulf", "ya 7ayyak habibi, 9ar lana zaman", "a a a a a a"),
    ("gulf", "chan zain if you told me before", "a a e e e e e"),
    ("gulf", "bro 5alni a3ref when you reach Dubai Mall", "e a a e e e n n"),
    ("gulf", "yalla bhai, 3'ada at Al Mallah", "a h a e n n"),
    # English only: must not be tagged as Hindi/Arabic
    ("english", "Can you send me the report before the meeting", "e e e e e e e e e"),
    ("english", "The main gate is closed so use the side door", "e e e e e e e e e e"),
    ("english", "He said he will be late today", "e e e e e e e"),
    ("english", "I have a bus to catch at six", "e e e e e e e e"),
]

OUT = Path(__file__).parent / "testsets" / "uae_lid.tsv"


def main() -> None:
    lines = []
    for group, text, codes in SENTENCES:
        words = [t.text for t in tokenize(text) if t.kind == "word"]
        labels = [CODES[c] for c in codes.split()]
        if len(words) != len(labels):
            raise SystemExit(f"{len(words)} words vs {len(labels)} labels in: {text}\n{words}")
        lines.append(f"# {group}\t{text}")
        lines += [f"{w}\t{label}" for w, label in zip(words, labels)]
        lines.append("")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {len(SENTENCES)} sentences to {OUT}")


if __name__ == "__main__":
    main()
