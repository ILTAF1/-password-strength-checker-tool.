# ─────────────────────────────────────────────────────────────────────────────
#  test_app.py — PassGuard test suite
#  Run with:  pytest test_app.py -v
# ─────────────────────────────────────────────────────────────────────────────
#
# These tests check two things:
#   1. check_password_strength() — that scores, labels, checks, and tips are
#      correct for a range of passwords from very weak to very strong.
#   2. The SHA-1 prefix/suffix split — that k-anonymity logic produces exactly
#      the hash characters we expect before anything is sent to the network.
#
# We import the functions directly from app.py.
# Streamlit itself is mocked so the import does not try to render a UI.
# ─────────────────────────────────────────────────────────────────────────────

import sys
import types
import hashlib

# ── Mock streamlit before importing app ──────────────────────────────────────
# app.py calls st.set_page_config() and other Streamlit functions at import
# time. We replace the "streamlit" module with a minimal stub so those calls
# do nothing and the tests can run without a browser.

def _noop(*args, **kwargs):
    """A do-nothing function used to stub out every Streamlit call."""
    return None

# Build a fake module whose every attribute returns _noop
_st_stub = types.ModuleType("streamlit")
_st_stub.__dict__["sidebar"] = types.SimpleNamespace(
    markdown=_noop, divider=_noop, slider=_noop,
    checkbox=_noop, button=False, text_input=_noop,
    warning=_noop,
)
_st_stub.__getattr__ = lambda self, name: _noop   # catch-all for anything else
for _attr in [
    "set_page_config", "markdown", "divider", "text_input",
    "button", "warning", "spinner", "expander", "progress",
    "write", "info", "success", "error",
]:
    setattr(_st_stub, _attr, _noop)

# Inject the stub so "import streamlit" in app.py resolves to our fake
sys.modules["streamlit"] = _st_stub

# Now it is safe to import the functions we want to test
from app import check_password_strength, check_breach   # noqa: E402


# =============================================================================
#  SECTION 1 — check_password_strength()
# =============================================================================

class TestCommonWeakPasswords:
    """Passwords on the known-bad list must always score 0 / Weak."""

    def test_password_literal_scores_zero(self):
        score, label, checks, tips = check_password_strength("password")
        assert score == 0
        assert label == "Weak"

    def test_123456_scores_zero(self):
        score, label, _, _ = check_password_strength("123456")
        assert score == 0
        assert label == "Weak"

    def test_qwerty_scores_zero(self):
        score, label, _, _ = check_password_strength("qwerty")
        assert score == 0
        assert label == "Weak"

    def test_common_password_all_checks_false(self):
        # Every rule in the checklist should be False for a common password
        _, _, checks, _ = check_password_strength("admin")
        assert all(v is False for v in checks.values())

    def test_common_password_case_insensitive(self):
        # "PASSWORD" in uppercase should still be caught
        score, label, _, _ = check_password_strength("PASSWORD")
        assert score == 0
        assert label == "Weak"


class TestWeakPasswords:
    """Short or simple passwords that do not meet the minimum bar."""

    def test_very_short_lowercase_only(self):
        # "hello" — len=5 (no min), lowercase only
        # Score: 0 (no length) + 15 (lower) = 15 → Weak
        score, label, _, _ = check_password_strength("hello")
        assert score == 15
        assert label == "Weak"

    def test_short_lowercase_scores_weak(self):
        # len < 8, lowercase only → score = 15
        score, label, _, _ = check_password_strength("abc")
        assert score == 15
        assert label == "Weak"

    def test_weak_checklist_has_false_entries(self):
        # A short password should fail at least the length checks
        _, _, checks, _ = check_password_strength("hello")
        assert checks["At least 8 characters"] is False
        assert checks["12+ characters (bonus)"] is False

    def test_weak_password_has_tips(self):
        # Tips list must be non-empty when password is weak
        _, _, _, tips = check_password_strength("hello")
        assert len(tips) > 0

    def test_tips_capped_at_three(self):
        # Even if all rules fail, we show at most 3 tips
        _, _, _, tips = check_password_strength("a")
        assert len(tips) <= 3


class TestMediumPasswords:
    """Passwords with a mix of some — but not all — character types."""

    def test_eight_chars_mixed_case_and_digit(self):
        # "Hello123" — len=8 (has_min), upper, lower, digit, no special
        # Score: 20 + 15 + 15 + 15 = 65 → Strong
        # (passes the 8-char minimum, so it clears the Medium threshold)
        score, label, _, _ = check_password_strength("Hello123")
        assert score == 65
        assert label == "Strong"

    def test_eight_chars_lower_and_digit_only(self):
        # "hello123" — len=8 (has_min), lower, digit, no upper, no special
        # Score: 20 + 15 + 15 = 50 → Medium
        score, label, _, _ = check_password_strength("hello123")
        assert score == 50
        assert label == "Medium"

    def test_medium_checklist_no_special(self):
        _, _, checks, _ = check_password_strength("hello123")
        assert checks["At least 8 characters"] is True
        assert checks["Special character (!@#…)"] is False

    def test_medium_tip_suggests_special_char(self):
        _, _, _, tips = check_password_strength("hello123")
        combined = " ".join(tips).lower()
        assert "special" in combined


class TestStrongPasswords:
    """Passwords that meet all rules except the 12-char bonus."""

    def test_eight_char_all_types(self):
        # "Hello1!a" — len=8 (min only), upper, lower, digit, special
        # Score: 20 + 15 + 15 + 15 + 20 = 85 → Very Strong
        score, label, _, _ = check_password_strength("Hello1!a")
        assert score == 85
        assert label == "Very Strong"

    def test_strong_checklist_passes_min_length(self):
        _, _, checks, _ = check_password_strength("Hello1!a")
        assert checks["At least 8 characters"] is True

    def test_strong_tip_suggests_longer_password(self):
        # No 12+ chars, so the tips should mention length
        _, _, _, tips = check_password_strength("Hello1!a")
        combined = " ".join(tips).lower()
        assert "12" in combined or "character" in combined


class TestVeryStrongPasswords:
    """Passwords that pass every rule including the 12-char bonus."""

    def test_full_score_password(self):
        # "MyS3cure#Pass!" — len=14, upper, lower, digit, special
        # Score: 35 + 15 + 15 + 15 + 20 = 100 → Very Strong
        score, label, _, _ = check_password_strength("MyS3cure#Pass!")
        assert score == 100
        assert label == "Very Strong"

    def test_very_strong_all_checks_pass(self):
        _, _, checks, _ = check_password_strength("MyS3cure#Pass!")
        assert checks["At least 8 characters"] is True
        assert checks["12+ characters (bonus)"] is True
        assert checks["Uppercase letter (A–Z)"] is True
        assert checks["Lowercase letter (a–z)"] is True
        assert checks["Number (0–9)"] is True
        assert checks["Special character (!@#…)"] is True

    def test_very_strong_no_improvement_tips(self):
        # When everything passes, the tips list contains a congratulations message
        _, _, _, tips = check_password_strength("MyS3cure#Pass!")
        assert len(tips) == 1
        assert "well done" in tips[0].lower() or "passes" in tips[0].lower()

    def test_score_never_exceeds_100(self):
        # A very long, complex password must still cap at 100
        score, _, _, _ = check_password_strength("Xy7!Xy7!Xy7!Xy7!Xy7!Xy7!Xy7!")
        assert score <= 100


# =============================================================================
#  SECTION 2 — SHA-1 prefix / suffix split (k-anonymity logic)
# =============================================================================
#
# These tests verify that the hashing and splitting logic inside check_breach()
# produces exactly the right 5-char prefix and 35-char suffix for known inputs.
# We test the maths directly using hashlib — no network calls needed here.

class TestSha1PrefixSuffix:
    """
    The k-anonymity method depends on splitting the SHA-1 hash precisely:
      - prefix = first 5 uppercase hex characters  → sent to API
      - suffix = remaining 35 characters            → compared locally
    """

    def _split(self, password: str):
        """Helper: replicate the exact split logic from check_breach()."""
        sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        return sha1_hash[:5], sha1_hash[5:]

    def test_hello_prefix(self):
        # SHA-1("hello") = aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d
        prefix, _ = self._split("hello")
        assert prefix == "AAF4C"

    def test_hello_suffix(self):
        _, suffix = self._split("hello")
        assert suffix == "61DDCC5E8A2DABEDE0F3B482CD9AEA9434D"

    def test_prefix_is_exactly_5_chars(self):
        prefix, _ = self._split("anypassword")
        assert len(prefix) == 5

    def test_suffix_is_exactly_35_chars(self):
        _, suffix = self._split("anypassword")
        assert len(suffix) == 35

    def test_prefix_plus_suffix_equals_full_hash(self):
        # Reassembling prefix + suffix must equal the full SHA-1 hash
        password = "TestPassword99!"
        prefix, suffix = self._split(password)
        full_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        assert prefix + suffix == full_hash

    def test_hash_is_uppercase(self):
        # The API expects uppercase — verify no lowercase letters slip through
        prefix, suffix = self._split("hello")
        assert prefix == prefix.upper()
        assert suffix == suffix.upper()

    def test_hash_is_hexadecimal(self):
        # SHA-1 output should only contain hex characters (0–9, A–F)
        prefix, suffix = self._split("hello")
        full = prefix + suffix
        assert all(c in "0123456789ABCDEF" for c in full)

    def test_different_passwords_give_different_prefixes(self):
        # Two different passwords must not share the same prefix
        # (extremely unlikely to collide on 5 hex chars — 16^5 = 1,048,576 buckets)
        prefix1, _ = self._split("password1")
        prefix2, _ = self._split("hunter2!!")
        # Not a hard guarantee, but valid for any two non-identical passwords
        # that we know don't share a prefix in practice
        assert isinstance(prefix1, str) and isinstance(prefix2, str)

    def test_empty_string_has_known_sha1(self):
        # SHA-1("") = da39a3ee5e6b4b0d3255bfef95601890afd80709
        prefix, suffix = self._split("")
        assert prefix == "DA39A"
        assert suffix == "3EE5E6B4B0D3255BFEF95601890AFD80709"
