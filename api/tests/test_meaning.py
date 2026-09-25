import pytest

from mixa.pipeline import analyze, meaning
from mixa.schemas import Meaning

MIXED_TAGS = [("yaar", "hi-ur"), ("plan", "en"), ("cancel", "en"), ("kya", "hi-ur")]
TEXT = "yaar plan cancel kya"


class FakeProvider:
    def __init__(self, name, reply=None, error=None, en="Is the plan cancelled?"):
        self.name, self.reply, self.error, self.en, self.calls = name, reply, error, en, 0

    def generate(self, system, user):
        self.calls += 1
        if self.error:
            raise self.error
        return Meaning(en=self.en, reply=self.reply)


@pytest.fixture
def chain(monkeypatch):
    cache = meaning.MeaningCache(":memory:")
    limiter = meaning.CallLimiter(per_minute=100)
    monkeypatch.setattr(meaning, "_get_cache", lambda: cache)
    monkeypatch.setattr(meaning, "_get_limiter", lambda: limiter)

    def use(*providers):
        monkeypatch.setattr(meaning, "_get_providers", lambda choice=meaning.AUTO: providers)
        return providers

    return use


def test_no_providers_means_no_meaning(chain):
    chain()
    assert meaning.explain(TEXT, MIXED_TAGS) is None


def test_failing_provider_falls_through_to_the_next(chain):
    broken, ok = chain(
        FakeProvider("a", error=RuntimeError("429")), FakeProvider("b", reply="haan yaar")
    )
    result = meaning.explain(TEXT, MIXED_TAGS)
    assert result.provider == "b" and result.register_kept
    assert broken.calls == ok.calls == 1


def test_failures_are_visible_until_the_model_succeeds_again(chain):
    (provider,) = chain(FakeProvider("a", error=RuntimeError("down")))
    meaning.explain(TEXT, MIXED_TAGS)
    assert meaning.recent_failures()["a"] == "RuntimeError"
    provider.error, provider.reply = None, "haan yaar"
    meaning.explain(TEXT, MIXED_TAGS)
    assert "a" not in meaning.recent_failures()


def test_english_only_reply_to_mixed_message_tries_the_next_provider(chain):
    chain(FakeProvider("a", reply="Yes, it was cancelled."), FakeProvider("b", reply="haan yaar"))
    assert meaning.explain(TEXT, MIXED_TAGS).provider == "b"


def test_english_reply_is_returned_when_no_provider_keeps_the_register(chain):
    chain(FakeProvider("a", reply="Yes, it was cancelled."))
    result = meaning.explain(TEXT, MIXED_TAGS)
    assert result.provider == "a" and not result.register_kept


def test_echoing_the_message_back_is_rejected(chain):
    chain(FakeProvider("a", reply="Yaar plan cancel kya?"), FakeProvider("b", reply="haan yaar"))
    assert meaning.explain(TEXT, MIXED_TAGS).provider == "b"


def test_an_echo_is_still_returned_as_a_last_resort(chain):
    chain(FakeProvider("a", reply="Salam!", en="Hello (a greeting)."))
    result = meaning.explain("salam", [("salam", "ar")])
    assert result is not None and result.en == "Hello (a greeting)."
    assert not result.register_kept


@pytest.mark.parametrize("reply", ["", "   ", "x" * 301])
def test_empty_or_overlong_replies_are_rejected(chain, reply):
    chain(FakeProvider("a", reply=reply), FakeProvider("b", reply="haan yaar"))
    assert meaning.explain(TEXT, MIXED_TAGS).provider == "b"


def test_english_message_may_get_an_english_reply(chain):
    chain(FakeProvider("a", reply="Sure, sending it now."))
    text = "Can you send me the report before 5pm?"
    tags = [(t.text, t.lang) for t in analyze(text, with_meaning=False).tokens]
    assert meaning.explain(text, tags).register_kept


@pytest.mark.parametrize(
    "reply",
    [
        "Yes, the plan got cancelled.",
        "Tell me when you are free",
        "I'll be at the main gate by 7pm",
    ],
)
@pytest.mark.parametrize("sender_langs", [{"hi-ur", "en"}, {"ar", "en"}])
def test_english_replies_with_ambiguous_words_do_not_count_as_kept(reply, sender_langs):
    assert not meaning.keeps_register(sender_langs, reply)


def test_reply_must_keep_a_language_the_sender_actually_used():
    assert not meaning.keeps_register({"ar", "en"}, "haan yaar")  # Hindi reply to Arabizi
    assert meaning.keeps_register({"ar", "en"}, "tamam habibi, see you")


def test_good_answers_are_cached(chain):
    (provider,) = chain(FakeProvider("a", reply="haan yaar"))
    first = meaning.explain(TEXT, MIXED_TAGS)
    assert meaning.explain(TEXT, MIXED_TAGS) == first
    assert provider.calls == 1


def test_each_provider_choice_has_its_own_cache_entry(chain):
    (provider,) = chain(FakeProvider("a", reply="haan yaar"))
    meaning.explain(TEXT, MIXED_TAGS, provider="auto")
    meaning.explain(TEXT, MIXED_TAGS, provider="a")
    assert provider.calls == 2


def test_english_fallback_is_not_cached(chain):
    (provider,) = chain(FakeProvider("a", reply="Yes, it was cancelled."))
    meaning.explain(TEXT, MIXED_TAGS)
    meaning.explain(TEXT, MIXED_TAGS)
    assert provider.calls == 2


def test_call_limiter_stops_llm_calls(chain, monkeypatch):
    (provider,) = chain(FakeProvider("a", reply="haan yaar"))
    monkeypatch.setattr(meaning, "_get_limiter", lambda: meaning.CallLimiter(per_minute=0))
    assert meaning.explain(TEXT, MIXED_TAGS) is None
    assert provider.calls == 0


def test_unreadable_cache_rows_are_a_miss():
    cache = meaning.MeaningCache(":memory:")
    cache._db.execute("INSERT INTO meaning VALUES ('k', 'not json')")
    assert cache.get("k") is None


def test_meaning_failure_never_takes_down_the_language_output(monkeypatch):
    def boom(*args, **kwargs):
        raise PermissionError("cache dir not writable")

    monkeypatch.setattr("mixa.pipeline.explain", boom)
    result = analyze("yaar kal milte hain")
    assert result.tokens and result.meaning is None


def test_gemini_timeout_never_goes_below_googles_10s_minimum_deadline():
    from mixa.pipeline.llm import gemini_timeout_ms

    assert gemini_timeout_ms(8) == 10_000
    assert gemini_timeout_ms(15) == 15_000


def test_build_provider_skips_missing_keys_and_rejects_unknown_kinds():
    from mixa.pipeline.llm import build_provider

    assert build_provider("gemini:gemini-3.5-flash-lite", "", "", 5) is None
    assert build_provider("groq:openai/gpt-oss-120b", "", "", 5) is None
    with pytest.raises(ValueError):
        build_provider("openai:gpt-9", "key", "key", 5)
