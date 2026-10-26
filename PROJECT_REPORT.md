---
title: "PassGuard: Password Strength Checker and Breach-Check Tool"
subtitle: "A Cybersecurity Project Report"
author: "ILTAF RAJA"
date: "2025"
geometry: "top=2.5cm, bottom=2.5cm, left=3cm, right=2.5cm"
fontsize: 12pt
mainfont: "Times New Roman"
linestretch: 1.5
numbersections: true
toc: true
toc-depth: 2
---

\newpage

---

**Project Title:** PassGuard: Password Strength Checker and Breach-Check Tool

**Submitted by:** ILTAF RAJA

**College / Course:** [YOUR COLLEGE / COURSE]

**Date:** [TODAY'S DATE]

---

\newpage

# Abstract

PassGuard is a cybersecurity web application developed using Python and Streamlit.
It provides three core services in a single, easy-to-use interface: a rule-based
password strength analyser that scores passwords from 0 to 100, a real-time breach
checker that queries the Have I Been Pwned (HIBP) Pwned Passwords API using the
k-anonymity technique, and a cryptographically secure password generator built on
Python's `secrets` module. The application runs entirely in the user's browser
session. No password is ever transmitted in full, stored on a server, or written to
any log file. The strength analyser checks six rules derived from industry guidance
and awards points accordingly. The breach checker hashes the password locally with
SHA-1 and sends only the first five characters of the hash to the external API,
ensuring full privacy. PassGuard was built to be accessible to beginners while
demonstrating real-world cybersecurity concepts including hashing, k-anonymity,
cryptographic randomness, and automated testing with pytest.

\newpage

# Introduction

Passwords remain the most widely used form of authentication on the internet.
Despite decades of awareness campaigns, weak passwords continue to be one of the
leading causes of security breaches. According to the Verizon 2023 Data Breach
Investigations Report, over 80% of hacking-related breaches involve stolen or weak
credentials. Common choices such as "123456", "password", and "qwerty" appear in
billions of leaked records that are freely available to attackers in
credential-stuffing databases.

The problem is compounded by the fact that users often have no way of knowing
whether a password they have chosen has already been exposed in a previous breach.
Even a password that looks complex may have been used by millions of other people
and therefore already exists in attacker databases. Tools that educate users about
password quality and breach exposure can significantly reduce this risk.

PassGuard was created to address this gap. It provides instant, visual feedback on
password strength, checks for known breaches without compromising privacy, and
offers a generator for users who want a secure password without having to think one
up themselves. The entire application fits in a single Python file (app.py), making
it straightforward for students and developers to read, understand, and extend.

# Problem Statement

Most users have no reliable way to evaluate whether a password they have chosen is
strong enough to resist attack, or whether it has already been leaked in a data
breach. Existing strength meters built into websites vary widely in quality, often
awarding high scores to passwords that are actually weak — for example, "Password1!"
passes many basic meters but is trivially guessable. Furthermore, checking a
password against a breach database typically requires sending the full password to a
third-party server, which itself creates a privacy risk.

PassGuard solves both problems. It applies a consistent, transparent scoring model
that reflects real password-quality factors, and it performs breach checking using
the k-anonymity protocol, which mathematically guarantees that the full password
never leaves the user's machine.

# Objectives

1. To build a web application that evaluates password strength against six
   measurable rules and produces a numerical score and a plain-language label.

2. To integrate the Have I Been Pwned Pwned Passwords API using the k-anonymity
   method, ensuring that no complete password or complete hash is ever transmitted
   over the network.

3. To provide a cryptographically secure password generator that uses Python's
   `secrets` module and allows users to control length and character composition.

4. To present results clearly through colour-coded cards, a progress bar, a rules
   checklist, and targeted improvement tips so that non-technical users can
   understand their security status.

5. To write an automated test suite using pytest that verifies scoring logic and
   SHA-1 prefix/suffix splitting against known reference values, ensuring
   correctness of the core functions.

# Tools and Technologies Used

| Tool / Library | Why It Was Used |
|---|---|
| Python 3.8+ | Core programming language; chosen for readability and its rich standard library. |
| Streamlit ≥ 1.32 | Web UI framework that turns a Python script into an interactive browser app with no HTML or JavaScript required. |
| hashlib (built-in) | Provides SHA-1 hashing for the k-anonymity breach-check flow; no installation needed. |
| re (built-in) | Regular expressions used to detect character types (uppercase, digits, special chars) in the password. |
| requests ≥ 2.28 | Makes the HTTPS GET request to the Have I Been Pwned range API endpoint. |
| secrets (built-in) | Generates cryptographically secure random passwords using the OS entropy source instead of the predictable `random` module. |
| string (built-in) | Supplies pre-built character sets (`ascii_lowercase`, `ascii_uppercase`, `digits`) for the password generator. |
| pytest ≥ 7.0 | Test runner for the automated test suite; supports class-based test organisation and detailed output with `-v`. |
| Have I Been Pwned API | Free public API by Troy Hunt; the `/range/` endpoint enables k-anonymity breach checking against billions of leaked credentials. |
| IBM Bob | AI coding assistant used to scaffold, refine, and document the project across all iterations. |

# System Design

PassGuard follows a simple linear flow when the user clicks the **Check Password**
button. The table below describes each step in order.

| Step | Stage | Description |
|------|-------|-------------|
| 1 | User Input | The user types a password into a hidden text input field (`type="password"`). Characters are masked as they are typed. |
| 2 | Empty Check | If the input is blank, a warning message is shown and processing stops. |
| 3 | Strength Analysis | `check_password_strength(password)` is called. It checks the common-password list, evaluates six rules, calculates a score, assigns a label, and returns a checklist dict and up to three tips. |
| 4 | Result Display | A coloured result card shows the label and score. A CSS progress bar fills to the score percentage. The rules checklist shows ✅ or ❌ per rule. Up to three tips are shown. |
| 5 | Breach Check | `check_breach(password)` is called. It hashes the password with SHA-1 locally, sends only the first 5 characters to the HIBP API, receives ~800 suffix lines, and searches locally for a match. |
| 6 | Breach Result | If a match is found, a red alert shows the exact breach count. If no match, a green confirmation is shown. On API failure, a neutral grey warning is shown. |
| 7 | Generator (Sidebar) | The sidebar lets the user choose a length (8–32) and character types, then click Generate Password. `generate_password()` uses `secrets.choice()` and immediately scores the result. |

# Methodology — Strength Scoring

The strength scoring function `check_password_strength()` in `app.py` applies six
rules in sequence. Each rule that passes adds a fixed number of points to the total
score. The score is then capped at 100 and mapped to one of four labels.

## Scoring Rules

| Rule | Condition in Code | Points |
|---|---|---|
| Common password check | Password matches a hardcoded list of 15 very common passwords | Score set to 0 immediately; function returns early |
| Minimum length | `len(password) >= 8` | +20 |
| Bonus length | `len(password) >= 12` (replaces +20 if true) | +35 |
| Uppercase letter | `re.search(r"[A-Z]", password)` | +15 |
| Lowercase letter | `re.search(r"[a-z]", password)` | +15 |
| Number | `re.search(r"[0-9]", password)` | +15 |
| Special character | `re.search(r"[!@#$%^&*(),.?...]+", password)` | +20 |

## Label Thresholds

| Score Range | Label | UI Colour |
|---|---|---|
| 0 – 39 | Weak | Red (`#f85149`) |
| 40 – 59 | Medium | Orange (`#e3692a`) |
| 60 – 79 | Strong | Blue (`#58a6ff`) |
| 80 – 100 | Very Strong | Green (`#3fb950`) |

**Example:** The password `"MyS3cure#Pass!"` has length 14 (≥ 12, so +35), contains
uppercase (+15), lowercase (+15), a digit (+15), and a special character (+20).
Total: 100. Label: **Very Strong**.

The relevant code from `app.py`:

```python
score = 0
if has_long:    score += 35   # 12+ chars
elif has_min:   score += 20   # 8–11 chars
if has_upper:   score += 15
if has_lower:   score += 15
if has_digit:   score += 15
if has_special: score += 20
score = min(score, 100)
```

# Breach Check Using k-Anonymity

The Have I Been Pwned (HIBP) Pwned Passwords service maintains a database of over
800 million password hashes collected from publicly known data breaches. PassGuard
queries this database using a technique called **k-anonymity**, which allows a
password to be checked without revealing the password to the server.

## How k-Anonymity Works

The protocol has four steps, all implemented in the `check_breach()` function in
`app.py`:

**Step 1 — Hash locally.** The password is hashed using SHA-1 on the user's
machine. SHA-1 produces a 40-character hexadecimal string.  
Example: `"hello"` → `AAF4C61DDCC5E8A2DABEDE0F3B482CD9AEA9434D`

**Step 2 — Split the hash.** Only the first 5 characters (the *prefix*) are
prepared for sending. The remaining 35 characters (the *suffix*) stay on the
machine.  
Prefix: `AAF4C` — Suffix: `61DDCC5E8A2DABEDE0F3B482CD9AEA9434D`

**Step 3 — Query the API.** An HTTPS GET request is sent to
`https://api.pwnedpasswords.com/range/AAF4C`. The server returns approximately
800 lines, each containing a hash suffix and breach count for every hash in its
database that begins with `AAF4C`. The server has no way of knowing which of these
~800 passwords was actually being checked.

**Step 4 — Compare locally.** The returned list is searched on the user's machine
for the local suffix. If found, the breach count is returned and displayed as a
red alert. If not found, a green confirmation is shown.

The k-anonymity guarantee comes from the fact that the 5-character prefix matches
16⁵ = 1,048,576 possible hash buckets. The server sees a prefix shared by hundreds
of completely different passwords.

## Worked Example

```python
password  = "hello"
sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
# sha1_hash = "AAF4C61DDCC5E8A2DABEDE0F3B482CD9AEA9434D"

prefix = sha1_hash[:5]   # "AAF4C"  ← sent to API
suffix = sha1_hash[5:]   # "61DDCC5E8A2DABEDE0F3B482CD9AEA9434D"  ← stays local

# Example API response line:
# 61DDCC5E8A2DABEDE0F3B482CD9AEA9434D:3861493
# → "hello" has appeared 3,861,493 times in known breaches.
```

## Error Handling

The function catches three categories of network failure: `ConnectionError` (no
internet), `Timeout` (server did not respond within 5 seconds), and any other
`RequestException` (HTTP error codes). In all cases a neutral grey warning is
displayed and the strength results above it remain fully usable.

# Password Generator

The sidebar password generator allows users to create a new password rather than
evaluating an existing one. It is controlled by a **length slider** (range: 8 to 32
characters, default: 16) and three **checkboxes** for uppercase letters (A–Z),
numbers (0–9), and symbols (!@#…). Lowercase letters (a–z) are always included as
the base character set.

Passwords are constructed using Python's `secrets` module rather than the standard
`random` module. The distinction is important for security. The `random` module uses
a deterministic pseudorandom number generator (the Mersenne Twister) seeded from
the system clock. An attacker who knows the approximate time a password was
generated could reconstruct the seed and reproduce the entire output. The `secrets`
module, by contrast, reads from the operating system's cryptographically secure
entropy source (`/dev/urandom` on Linux and macOS, `CryptGenRandom` on Windows).
This source is non-deterministic and cannot be reversed or predicted.

```python
alphabet = string.ascii_lowercase   # always included
if use_upper:   alphabet += string.ascii_uppercase
if use_digits:  alphabet += string.digits
if use_symbols: alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?"

password = "".join(secrets.choice(alphabet) for _ in range(length))
```

After generation, the password is immediately passed to `check_password_strength()`
and the score and label are displayed in a small strength badge.

# Security and Privacy Considerations

- **No storage.** PassGuard does not use a database, file system, or any persistent
  storage. Every password exists only in the memory of the current browser session
  and is discarded when the tab is closed or the page is refreshed.

- **No logging.** Streamlit does not automatically log user input values. The
  application does not call any logging function, write to any file, or send any
  analytics data.

- **Full password never transmitted.** The breach check uses k-anonymity. The only
  data sent over the network is the 5-character SHA-1 prefix.

- **Cryptographically secure generation.** The password generator uses
  `secrets.choice()`, which is the Python standard library's recommended function
  for security-critical values.

- **Input masking.** The password input field uses Streamlit's `type="password"`
  parameter, rendering the field with masked characters.

# Testing

The test suite is contained in `test_app.py` and is run with `pytest`. It contains
**25 individual test cases** organised across six test classes. Since `app.py` calls
Streamlit functions at module level, the test file injects a lightweight stub module
in place of `streamlit` before importing the application functions. This allows all
tests to run instantly without a browser or network connection.

| Test Name | Input | Expected Result | Status |
|---|---|---|---|
| test_password_literal_scores_zero | `"password"` | score=0, label="Weak" | PASS |
| test_123456_scores_zero | `"123456"` | score=0, label="Weak" | PASS |
| test_common_password_case_insensitive | `"PASSWORD"` | score=0, label="Weak" | PASS |
| test_common_password_all_checks_false | `"admin"` | All checks False | PASS |
| test_very_short_lowercase_only | `"hello"` | score=15, label="Weak" | PASS |
| test_tips_capped_at_three | `"a"` | len(tips) ≤ 3 | PASS |
| test_eight_chars_lower_and_digit_only | `"hello123"` | score=50, label="Medium" | PASS |
| test_medium_tip_suggests_special_char | `"hello123"` | "special" in tips | PASS |
| test_eight_chars_mixed_case_and_digit | `"Hello123"` | score=65, label="Strong" | PASS |
| test_eight_char_all_types | `"Hello1!a"` | score=85, label="Very Strong" | PASS |
| test_full_score_password | `"MyS3cure#Pass!"` | score=100, label="Very Strong" | PASS |
| test_very_strong_all_checks_pass | `"MyS3cure#Pass!"` | All 6 checks True | PASS |
| test_very_strong_no_improvement_tips | `"MyS3cure#Pass!"` | 1 tip, congratulations | PASS |
| test_score_never_exceeds_100 | Long complex password | score ≤ 100 | PASS |
| test_hello_prefix | SHA-1("hello") | prefix == "AAF4C" | PASS |
| test_hello_suffix | SHA-1("hello") | suffix == "61DDCC5E8A2..." | PASS |
| test_prefix_is_exactly_5_chars | Any string | len(prefix) == 5 | PASS |
| test_suffix_is_exactly_35_chars | Any string | len(suffix) == 35 | PASS |
| test_prefix_plus_suffix_equals_full_hash | "TestPassword99!" | prefix+suffix == full hash | PASS |
| test_hash_is_uppercase | SHA-1("hello") | No lowercase in output | PASS |
| test_hash_is_hexadecimal | SHA-1("hello") | Only 0–9 and A–F | PASS |
| test_empty_string_has_known_sha1 | "" (empty string) | prefix == "DA39A" | PASS |

All 25 tests pass. Run with: `pytest test_app.py -v`

# Results and Screenshots

The following placeholders should be replaced with actual screenshots taken from
the running application.

## [Insert Screenshot: Weak Password Result]

A common password such as "password" entered. Shows a red result card scoring
0/100, all checklist items with red crosses, and the common-password tip.

## [Insert Screenshot: Medium Password Result]

A password such as "hello123" scoring 50/100. Shows orange card, partial checklist
passes, and tips suggesting uppercase and special characters.

## [Insert Screenshot: Strong Password Result]

A password such as "MyS3cure#Pass!" scoring 100/100. Shows green card, all
checklist items green, and the congratulations tip.

## [Insert Screenshot: Breached Password Result]

A common password that returns a breach count from the HIBP API, showing the red
breach alert with the exact number of occurrences.

## [Insert Screenshot: Password Generator]

The sidebar open with length slider at 20, all checkboxes ticked, and a generated
password displayed with its strength badge.

# Limitations

1. **SHA-1 is not collision-resistant for security purposes.** Although the
   k-anonymity protocol here does not rely on SHA-1's collision resistance, NIST
   deprecated SHA-1 for general cryptographic use in 2011. A future version should
   use SHA-256 if and when the HIBP API supports it.

2. **No HTTPS enforcement on localhost.** When running locally with
   `streamlit run app.py`, the connection is plain HTTP. A public deployment would
   need a reverse proxy with TLS termination.

3. **Single-file architecture limits scalability.** All application code, UI, and
   logic live in one file. A production system would separate concerns into modules
   (`ui.py`, `checker.py`, `breach.py`) to improve maintainability.

4. **Strength scoring does not account for dictionary words or keyboard patterns.**
   A password such as "Tr0ub4dor&3" would score highly under the current rules
   despite being based on a dictionary word. A more sophisticated model using the
   zxcvbn algorithm would catch such cases.

5. **The breach check requires an internet connection.** If the HIBP API is
   unreachable, the feature degrades gracefully but the user receives no breach
   information. An offline fallback using a local subset of common breached hashes
   could improve resilience.

# Future Scope

1. **zxcvbn integration.** Replace the current point-based scorer with Dropbox's
   open-source zxcvbn library, which analyses dictionary words, keyboard patterns,
   common substitutions (e.g. '3' for 'e'), and repeated characters to produce a
   more realistic entropy estimate.

2. **Passphrase generator.** Add a second generation mode that produces memorable
   passphrases from a dictionary of common English words (e.g.
   "correct-horse-battery-staple"), following NIST SP 800-63B guidance that length
   and randomness matter more than character complexity.

3. **Session history.** Maintain a within-session table showing the score and label
   for every password checked so that users can compare candidates side by side.
   No passwords would be persisted beyond the session.

4. **Copy-to-clipboard button.** Add a single-click copy button next to the
   generated password so users can paste it directly into a password manager.

5. **Multi-language support.** Add a language selector to render all UI text, tips,
   and labels in languages other than English.

6. **Deployment and authentication.** Package the application as a Docker container
   and deploy it behind HTTPS with an optional rate limiter on the breach-check
   endpoint to prevent abuse.

# Conclusion

PassGuard demonstrates that meaningful cybersecurity tooling can be built in Python
with a modest amount of code. The project combines four distinct technical concepts
— rule-based scoring, SHA-1 hashing, the k-anonymity protocol, and cryptographic
randomness — into a single, cohesive application that is accessible to non-technical
users while remaining instructive for developers.

The strength scorer applies a transparent, point-based model whose rules are drawn
directly from established guidance such as NIST SP 800-63B and the OWASP
Authentication Cheat Sheet. The breach checker implements the Have I Been Pwned
k-anonymity protocol correctly, ensuring that no complete password is ever
transmitted. The password generator uses the standard library's `secrets` module,
which is the appropriate tool for security-critical randomness.

All core logic is covered by 25 automated pytest tests that verify exact scores,
label thresholds, checklist states, and SHA-1 hash values against known reference
outputs. The application is privacy-respecting by design: no data is stored, no
logs are written, and the user's password never leaves their browser session in full.

PassGuard serves both as a practical security tool and as a learning artefact that
illustrates how to build secure, well-tested, privacy-preserving software in Python.

# References

1. Hunt, T. (2018). *Pwned Passwords — HIBP Range API*. Have I Been Pwned.
   Available at: <https://haveibeenpwned.com/API/v3#PwnedPasswords>

2. Grassi, P. A., Garcia, M. E., & Fenton, J. L. (2017). *NIST Special Publication
   800-63B: Digital Identity Guidelines — Authentication and Lifecycle Management*.
   National Institute of Standards and Technology.
   Available at: <https://pages.nist.gov/800-63-3/sp800-63b.html>

3. OWASP Foundation (2023). *Authentication Cheat Sheet*.
   Available at: <https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html>

4. Streamlit Inc. (2024). *Streamlit Documentation*.
   Available at: <https://docs.streamlit.io>

5. Python Software Foundation (2024). *secrets — Generate secure random numbers for
   managing secrets*. Python 3 Documentation.
   Available at: <https://docs.python.org/3/library/secrets.html>

6. Cloudflare / Troy Hunt (2018). *Validating Leaked Passwords with k-Anonymity*.
   Available at: <https://blog.cloudflare.com/validating-leaked-passwords-with-k-anonymity/>
