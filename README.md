# 🔐 PassGuard

> A cybersecurity web app that checks password strength, detects breached passwords, and generates strong passwords — built with Python and Streamlit.

---

## 📋 Project Description

PassGuard is a beginner-friendly password security tool that runs entirely in your browser. You type a password and instantly see:

- A **strength score out of 100** with a colour-coded label (Weak → Very Strong)
- A **rules checklist** showing exactly which criteria pass or fail
- A **breach check** against billions of leaked passwords using the Have I Been Pwned API
- **Improvement tips** tailored to what the password is missing
- A **sidebar generator** to create a cryptographically secure password on demand

Everything is private by design — your password is never sent, saved, or logged.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔢 Strength score | 0–100 score based on length, uppercase, lowercase, numbers, and special characters |
| 🚦 Strength label | Weak / Medium / Strong / Very Strong with colour-coded card and progress bar |
| ✅ Rules checklist | Green tick or red cross for each of the 6 rules |
| 💡 Improvement tips | Up to 3 actionable suggestions based on which rules failed |
| 🔎 Breach check | Checks against Have I Been Pwned database using k-anonymity — without exposing your password |
| ⚡ Password generator | Sidebar generator using Python's `secrets` module with length slider and character-type checkboxes |
| 🌙 Dark theme | Custom dark CSS with colour-coded result cards |
| ℹ️ How it works | Collapsible panel explaining the scoring and k-anonymity in plain English |

---

## 🔒 How It Works

### Strength scoring

Each password is tested against six rules. Points are awarded for each rule that passes:

| Rule | Points |
|---|---|
| At least 8 characters | +20 |
| 12 or more characters | +35 (replaces the 8-char bonus) |
| Uppercase letter (A–Z) | +15 |
| Lowercase letter (a–z) | +15 |
| Number (0–9) | +15 |
| Special character (!@#…) | +20 |

Passwords on a built-in list of the 15 most common passwords (e.g. `password`, `123456`, `qwerty`) automatically score **0** regardless of any other rule.

Final score thresholds:

| Score | Label |
|---|---|
| 0 – 39 | 🔴 Weak |
| 40 – 59 | 🟠 Medium |
| 60 – 79 | 🔵 Strong |
| 80 – 100 | 🟢 Very Strong |

---

### Breach check & k-anonymity

PassGuard checks whether a password has ever appeared in a known data breach by querying the [Have I Been Pwned Pwned Passwords API](https://haveibeenpwned.com/Passwords). Crucially, **your password never leaves your machine**. The technique used is called **k-anonymity**:

1. **Hash locally.** Your password is hashed with SHA-1 on your own computer.
   `"hello"` → `AAF4C61DDCC5E8A2DABEDE0F3B482CD9AEA9434D`

2. **Send only 5 characters.** Only the first 5 characters of the hash are sent to the API.
   `AAF4C` → `https://api.pwnedpasswords.com/range/AAF4C`

3. **Compare locally.** The API returns ~800 hash suffixes that all begin with `AAF4C`. PassGuard searches through them **on your machine** to see if your suffix appears.

The server never sees your full password or its full hash. The 5-character prefix matches thousands of completely different passwords, so it is impossible for the server to know which one was checked.

---

### Password generator

The sidebar generator uses Python's built-in `secrets` module rather than the standard `random` module. `secrets` draws from the operating system's cryptographically secure entropy source (`/dev/urandom` on Linux/macOS, `CryptGenRandom` on Windows). Unlike `random`, whose output can be predicted if an attacker knows the seed, `secrets` is suitable for generating passwords and tokens.

---

## 🛠 Installation

### Prerequisites

- Python 3.8 or higher — download from [python.org](https://www.python.org/)
- pip (comes with Python)

### Step 1 — Clone or download the project

```bash
git clone https://github.com/your-username/passguard.git
cd passguard
```

Or simply place `app.py`, `test_app.py`, and `requirements.txt` in the same folder.

### Step 2 — Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Your terminal prompt will show `(venv)` when the environment is active.

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs Streamlit, Requests, and pytest.

---

## ▶️ How to Run

### Start the app

```bash
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) and open it in your browser automatically.

### Run the tests

```bash
pytest test_app.py -v
```

The `-v` flag shows each test name and result individually. You should see all tests pass with a green summary line.

---

## 📁 File Structure

```
passguard/
├── app.py            # Main Streamlit application (all features in one file)
├── test_app.py       # pytest test suite for the core functions
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## 🔮 Ideas for Future Improvements

1. **Password history & session comparison**
   Keep a table within the session (never saved to disk) showing the scores of every password the user has checked, so they can compare multiple candidates side by side before choosing one.

2. **Passphrase generator**
   Add a second generator mode that builds memorable passphrases from random English words (e.g. `correct-horse-battery-staple`), following the XKCD-style approach. Passphrases are often stronger than random character strings and much easier to remember.

3. **Strength meter animations and copy-to-clipboard button**
   Add a one-click copy button next to the generated password so users can paste it directly into a password manager without selecting the text manually. Also animate the progress bar fill on load for a more polished feel.

---

## 🧪 Running Tests — What Is Covered

| Test group | What is tested |
|---|---|
| `TestCommonWeakPasswords` | Known bad passwords always score 0, all checks False, case-insensitive |
| `TestWeakPasswords` | Short passwords score correctly, tips are present and capped at 3 |
| `TestMediumPasswords` | 8-char lowercase+digit passwords score 50 and label as Medium |
| `TestStrongPasswords` | All types at 8 chars score 85 / Very Strong |
| `TestVeryStrongPasswords` | 12+ char full-mix scores 100, all checks True, no improvement tips |
| `TestSha1PrefixSuffix` | Prefix is 5 chars, suffix is 35 chars, uppercase hex, known hash values |

---

## 🔗 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥ 1.32.0 | Web UI framework |
| `requests` | ≥ 2.28.0 | HTTP calls to the HIBP API |
| `pytest` | ≥ 7.0.0 | Test runner |
| `hashlib` | built-in | SHA-1 hashing for k-anonymity |
| `secrets` | built-in | Cryptographically secure password generation |
| `re` | built-in | Regex checks for character types |

---

## 👤 Credits

- [Have I Been Pwned](https://haveibeenpwned.com/) by Troy Hunt — breach database and k-anonymity API
- Built with [Python](https://www.python.org/), [Streamlit](https://streamlit.io/), and [IBM Bob](https://www.ibm.com/products/ibm-bob)
