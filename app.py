import streamlit as st
import re
import hashlib
import requests
import secrets
import string

# ─────────────────────────────────────────────
#  PASSWORD STRENGTH CHECKER FUNCTION
# ─────────────────────────────────────────────
# Returns four things:
#   score  – number from 0 to 100
#   label  – "Weak", "Medium", "Strong", or "Very Strong"
#   checks – dict with True/False for each rule (used for the checklist)
#   tips   – up to 3 short improvement suggestions

def check_password_strength(password):

    # ── RULE 1: Common weak passwords ───────────────────────────────────────
    common_weak = [
        "password", "123456", "12345678", "qwerty", "abc123",
        "111111", "password1", "iloveyou", "admin", "letmein",
        "welcome", "monkey", "dragon", "master", "123456789"
    ]
    if password.lower() in common_weak:
        # All checks fail; return immediately with a single tip
        checks = {
            "At least 8 characters":    False,
            "12+ characters (bonus)":   False,
            "Uppercase letter (A–Z)":   False,
            "Lowercase letter (a–z)":   False,
            "Number (0–9)":             False,
            "Special character (!@#…)": False,
        }
        return 0, "Weak", checks, ["This is one of the most common passwords. Choose something unique."]

    # ── Evaluate each rule individually ─────────────────────────────────────
    length      = len(password)
    has_long    = length >= 12                              # bonus rule
    has_min     = length >= 8                               # minimum rule
    has_upper   = bool(re.search(r"[A-Z]", password))
    has_lower   = bool(re.search(r"[a-z]", password))
    has_digit   = bool(re.search(r"[0-9]", password))
    has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>_\-\[\]\/\\]", password))

    # ── Build the checklist dict (shown as ticks / crosses in the UI) ────────
    checks = {
        "At least 8 characters":    has_min,
        "12+ characters (bonus)":   has_long,
        "Uppercase letter (A–Z)":   has_upper,
        "Lowercase letter (a–z)":   has_lower,
        "Number (0–9)":             has_digit,
        "Special character (!@#…)": has_special,
    }

    # ── Calculate score ──────────────────────────────────────────────────────
    score = 0
    if has_long:
        score += 35   # 12+ chars is a big win
    elif has_min:
        score += 20   # 8–11 chars is acceptable
    if has_upper:   score += 15
    if has_lower:   score += 15
    if has_digit:   score += 15
    if has_special: score += 20
    score = min(score, 100)

    # ── Assign label ─────────────────────────────────────────────────────────
    if score < 40:
        label = "Weak"
    elif score < 60:
        label = "Medium"
    elif score < 80:
        label = "Strong"
    else:
        label = "Very Strong"

    # ── Build improvement tips (max 3, only for failed rules) ────────────────
    all_tips = []
    if not has_min:
        all_tips.append("Use at least 8 characters — longer passwords are much harder to crack.")
    if not has_long:
        all_tips.append("Aim for 12+ characters to get a significant strength boost.")
    if not has_upper:
        all_tips.append("Mix in uppercase letters (e.g. replace 'hello' with 'Hello').")
    if not has_lower:
        all_tips.append("Include lowercase letters alongside capitals.")
    if not has_digit:
        all_tips.append("Add at least one number (0–9) to increase complexity.")
    if not has_special:
        all_tips.append("Throw in a special character like !, @, # or $ for extra strength.")

    # Keep only the first 3 tips so the UI stays clean
    tips = all_tips[:3]

    # If everything passed, show a single congratulations message
    if not tips:
        tips = ["Your password passes all checks — well done!"]

    return score, label, checks, tips


# ─────────────────────────────────────────────
#  BREACH CHECK FUNCTION  (Have I Been Pwned)
# ─────────────────────────────────────────────
#
# HOW K-ANONYMITY KEEPS YOUR PASSWORD SAFE
# ─────────────────────────────────────────────
# We never send the actual password — or even the full hash — to any server.
# Instead we use a technique called "k-anonymity":
#
#   Step 1: Hash the password locally with SHA-1
#           e.g.  "hello" → "AAF4C61DDCC5E8A2DABEDE0F3B482CD9AEA9434D"
#
#   Step 2: Send only the FIRST 5 characters of that hash to the API
#           e.g.  "AAF4C" → https://api.pwnedpasswords.com/range/AAF4C
#
#   Step 3: The API returns ~500–800 hash suffixes that all start with "AAF4C".
#           We search that list LOCALLY for our own suffix ("1DDCC5E8…").
#
# The server only ever sees 5 hex characters. That prefix matches thousands of
# different passwords, so the server has no idea which one you checked.
# Your full password and its full hash never leave your machine.

def check_breach(password):
    """
    Returns (count, error_message).
      count         – number of times the password appeared in breaches (0 = safe)
      error_message – None if successful, or a string describing what went wrong
    """

    # Step 1: Hash the password with SHA-1 and convert to uppercase hex
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()

    # Step 2: Split the hash — first 5 chars go to the API, the rest we keep locally
    prefix = sha1_hash[:5]   # sent to the API
    suffix = sha1_hash[5:]   # compared locally — never leaves this machine

    # Step 3: Call the HIBP range API with just the 5-char prefix
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()   # raises an error for 4xx / 5xx responses
    except requests.exceptions.ConnectionError:
        return None, "No internet connection. Breach check skipped."
    except requests.exceptions.Timeout:
        return None, "Request timed out. Breach check skipped."
    except requests.exceptions.RequestException as e:
        return None, f"Could not reach HIBP API: {e}"

    # Step 4: Parse the response — each line looks like "SUFFIX:COUNT"
    # We search for our local suffix to see if it appears in the list
    for line in response.text.splitlines():
        returned_suffix, count = line.split(":")
        if returned_suffix == suffix:
            return int(count), None   # found — password has been breached

    # If our suffix was not in the list, the password has not been breached
    return 0, None


# ─────────────────────────────────────────────
#  PASSWORD GENERATOR FUNCTION
# ─────────────────────────────────────────────
# Builds a random password from the character sets the user chose.
#
# WHY secrets AND NOT random?
# Python's built-in "random" module is designed for simulations and games —
# it uses a predictable algorithm that can be reversed if an attacker knows
# the seed. "secrets" uses the operating system's cryptographically secure
# random source (e.g. /dev/urandom on Linux), making the output impossible
# to predict. Always use secrets for anything security-related.

def generate_password(length, use_upper, use_digits, use_symbols):
    # Always include lowercase letters as the base character set
    alphabet = string.ascii_lowercase                      # a–z

    if use_upper:
        alphabet += string.ascii_uppercase                 # A–Z
    if use_digits:
        alphabet += string.digits                          # 0–9
    if use_symbols:
        alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?"          # special chars

    # Build the password one character at a time using secrets.choice(),
    # which picks a cryptographically random item from the alphabet.
    password = "".join(secrets.choice(alphabet) for _ in range(length))

    return password


# ─────────────────────────────────────────────
#  PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PassGuard",
    page_icon="🔐",
    layout="centered"
)

# ─────────────────────────────────────────────
#  CUSTOM CSS — DARK THEME
# ─────────────────────────────────────────────
st.markdown("""
    <style>
        /* Dark page background */
        .stApp {
            background-color: #0e1117;
            color: #e0e0e0;
        }

        /* Centered title */
        .title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #58a6ff;
            text-align: center;
            margin-bottom: 0.2rem;
        }

        /* Subtitle below the title */
        .subtitle {
            font-size: 1rem;
            color: #8b949e;
            text-align: center;
            margin-bottom: 1.5rem;
        }

        /* Score result card — colour is set inline via the 'style' attribute */
        .result-card {
            border-radius: 10px;
            padding: 1.1rem 1.5rem;
            margin-top: 1rem;
            text-align: center;
            font-size: 1.15rem;
            font-weight: 700;
        }

        /* Progress bar track (grey background) */
        .bar-track {
            background-color: #2e3440;
            border-radius: 999px;
            height: 14px;
            margin: 0.8rem 0 0.3rem 0;
            overflow: hidden;
        }

        /* Progress bar fill — width and colour are set inline */
        .bar-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.4s ease;
        }

        /* Small label under the bar showing the score number */
        .bar-label {
            font-size: 0.8rem;
            color: #8b949e;
            text-align: right;
            margin-bottom: 1rem;
        }

        /* Section heading (e.g. "Rules Checklist", "Tips") */
        .section-heading {
            font-size: 0.85rem;
            font-weight: 600;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin: 1.2rem 0 0.5rem 0;
        }

        /* One checklist row */
        .check-row {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.35rem 0;
            font-size: 0.95rem;
            border-bottom: 1px solid #1e2329;
        }
        .check-row:last-child { border-bottom: none; }

        /* Icon inside each checklist row */
        .check-icon { font-size: 1rem; min-width: 1.2rem; text-align: center; }

        /* Text colour: green for pass, muted-red for fail */
        .check-pass { color: #3fb950; }
        .check-fail { color: #f85149; }

        /* Breach check result box */
        .breach-found {
            background-color: #3a1a1a;
            border: 1px solid #f85149;
            border-radius: 8px;
            padding: 0.85rem 1.1rem;
            color: #f85149;
            font-weight: 600;
            font-size: 0.95rem;
            margin-top: 0.5rem;
        }
        .breach-safe {
            background-color: #1a3a2a;
            border: 1px solid #3fb950;
            border-radius: 8px;
            padding: 0.85rem 1.1rem;
            color: #3fb950;
            font-weight: 600;
            font-size: 0.95rem;
            margin-top: 0.5rem;
        }
        .breach-warn {
            background-color: #2a2618;
            border: 1px solid #8b949e;
            border-radius: 8px;
            padding: 0.85rem 1.1rem;
            color: #8b949e;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }

        /* Tips box */
        .tips-box {
            background-color: #1c1f26;
            border: 1px solid #2e3440;
            border-radius: 8px;
            padding: 0.85rem 1.1rem;
            font-size: 0.9rem;
            color: #c9d1d9;
            line-height: 1.9;
        }

        /* Check Password button */
        .stButton > button {
            width: 100%;
            background-color: #58a6ff;
            color: #0e1117;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1rem;
            font-size: 1rem;
        }
        .stButton > button:hover { background-color: #79b8ff; }

        /* Input label colour */
        label { color: #c9d1d9 !important; font-weight: 500; }

        /* "How it works" info box rows */
        .info-box {
            background-color: #1c1f26;
            border: 1px solid #2e3440;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            color: #c9d1d9;
            line-height: 1.75;
        }
        .info-box b { color: #e0e0e0; }

        /* Privacy note bar */
        .privacy-note {
            background-color: #16213a;
            border: 1px solid #1f3a6e;
            border-radius: 8px;
            padding: 0.6rem 1rem;
            font-size: 0.82rem;
            color: #8b949e;
            margin-bottom: 1rem;
            text-align: center;
        }

        /* Page footer */
        .footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #2e3440;
            text-align: center;
            font-size: 0.8rem;
            color: #57606a;
        }
        .footer a { color: #58a6ff; text-decoration: none; }
        .footer a:hover { text-decoration: underline; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR — PASSWORD GENERATOR
# ─────────────────────────────────────────────
# st.sidebar.* puts widgets in the collapsible panel on the left.

with st.sidebar:
    st.markdown("## 🔑 Password Generator")
    st.markdown(
        "<small style='color:#8b949e;'>Generate a strong password using your preferred options.</small>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Length slider ────────────────────────────────────────────────────────
    # The user drags this to pick how many characters they want (8 to 32).
    gen_length = st.slider(
        label="Password length",
        min_value=8,
        max_value=32,
        value=16,          # default starting position
        step=1,
    )

    # ── Character-set checkboxes ─────────────────────────────────────────────
    # Each checkbox adds a new group of characters to the generator's alphabet.
    gen_upper   = st.checkbox("Uppercase letters (A–Z)", value=True)
    gen_digits  = st.checkbox("Numbers (0–9)",           value=True)
    gen_symbols = st.checkbox("Symbols (!@#…)",          value=True)

    st.divider()

    # ── Generate button ──────────────────────────────────────────────────────
    if st.button("⚡ Generate Password"):

        # Build the password with the chosen settings
        gen_password = generate_password(gen_length, gen_upper, gen_digits, gen_symbols)

        # Show the generated password in a copyable text box
        st.text_input(
            label="Your generated password",
            value=gen_password,
            key="gen_output",
        )

        # Run it through the same strength checker used on the main page
        gen_score, gen_label, _, _ = check_password_strength(gen_password)

        # Pick the right colour for the score badge
        badge_color = {
            "Weak":        "#f85149",
            "Medium":      "#e3692a",
            "Strong":      "#58a6ff",
            "Very Strong": "#3fb950",
        }[gen_label]

        # Show a small inline strength badge under the password
        st.markdown(
            f'<div style="'
            f'background-color:#1c1f26; border:1px solid {badge_color}; '
            f'border-radius:6px; padding:0.5rem 0.75rem; '
            f'color:{badge_color}; font-weight:600; font-size:0.9rem; '
            f'text-align:center; margin-top:0.3rem;">'
            f'Strength: {gen_label} — {gen_score}/100'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Tip: if all checkboxes are off, lowercase-only passwords score poorly
        if not gen_upper and not gen_digits and not gen_symbols:
            st.warning("Tip: enable more options to generate a stronger password.")


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="title">🔐 PassGuard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Check how strong your password is — instantly and privately.</div>',
    unsafe_allow_html=True
)

st.divider()

# ─────────────────────────────────────────────
#  HOW IT WORKS — EXPANDABLE SECTION
# ─────────────────────────────────────────────
# st.expander() creates a collapsible panel. It is collapsed by default
# so it does not clutter the page, but curious users can open it.

with st.expander("ℹ️ How does PassGuard work?"):
    st.markdown("""
        <div class="info-box">
            <b>🔢 Strength score (0–100)</b><br>
            Your password is tested against five rules. Each rule that passes
            adds points to your score:
            <ul style="margin:0.4rem 0 0 1rem; padding:0;">
                <li><b>Length:</b> 8+ characters = 20 pts &nbsp;|&nbsp; 12+ characters = 35 pts</li>
                <li><b>Uppercase letter</b> (A–Z) = 15 pts</li>
                <li><b>Lowercase letter</b> (a–z) = 15 pts</li>
                <li><b>Number</b> (0–9) = 15 pts</li>
                <li><b>Special character</b> (!@#…) = 20 pts</li>
            </ul>
            A score of 0–39 is <b>Weak</b>, 40–59 is <b>Medium</b>,
            60–79 is <b>Strong</b>, and 80–100 is <b>Very Strong</b>.
            Common passwords like "123456" or "password" score 0 immediately.
        </div>

        <div class="info-box" style="margin-top:0.5rem;">
            <b>🔎 Breach check &amp; k-anonymity</b><br>
            We check your password against the
            <a href="https://haveibeenpwned.com/Passwords" target="_blank"
               style="color:#58a6ff;">Have I Been Pwned</a>
            database of billions of leaked passwords — <b>without ever sending
            your password to the internet</b>. Here's how:
            <ol style="margin:0.4rem 0 0 1rem; padding:0;">
                <li>Your password is hashed with SHA-1 <em>on your machine</em>.</li>
                <li>Only the <b>first 5 characters</b> of that hash are sent to the API.</li>
                <li>The API returns ~800 matching hash suffixes. We search them <b>locally</b>.</li>
            </ol>
            The server never sees your full password or its full hash.
            This technique is called <b>k-anonymity</b>.
        </div>

        <div class="info-box" style="margin-top:0.5rem;">
            <b>⚡ Password generator</b><br>
            The sidebar generator uses Python's <code>secrets</code> module,
            which draws from your operating system's cryptographically secure
            random source. This is far stronger than the standard
            <code>random</code> module, whose output can be predicted if an
            attacker knows when it was seeded.
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PASSWORD INPUT
# ─────────────────────────────────────────────
# type="password" hides the characters as the user types
password = st.text_input(
    label="Enter your password",
    type="password",
    placeholder="Type your password here..."
)

# Privacy note — shown directly below the input, before the button
st.markdown(
    '<div class="privacy-note">'
    '🔒 Your password is <strong>never sent, saved, or logged</strong>. '
    'All analysis runs locally in your browser session.'
    '</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  CHECK BUTTON
# ─────────────────────────────────────────────
# Everything inside this 'if' block runs only when the button is clicked
if st.button("Check Password"):

    if password == "":
        st.warning("⚠️ Please enter a password first.")

    else:
        # Call our strength checker — get score, label, checks dict, and tips
        score, label, checks, tips = check_password_strength(password)

        # ── 1. RESULT CARD ──────────────────────────────────────────────────
        # Pick colours and emoji to match the label
        label_styles = {
            "Weak":        ("🔴", "#f85149", "#3a1a1a"),
            "Medium":      ("🟠", "#e3692a", "#3a2418"),
            "Strong":      ("🔵", "#58a6ff", "#1a2e3a"),
            "Very Strong": ("🟢", "#3fb950", "#1a3a2a"),
        }
        emoji, color, bg = label_styles[label]

        st.markdown(
            f'<div class="result-card" style="background-color:{bg}; border:1px solid {color}; color:{color};">'
            f'{emoji} {label} — {score} / 100'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── 2. COLOURED PROGRESS BAR ────────────────────────────────────────
        # The bar colour matches the label: red → orange → green
        # We use a CSS gradient that runs from red (left) to green (right),
        # clipped at the current score percentage so it always looks right.
        bar_colors = {
            "Weak":        "#f85149",   # red
            "Medium":      "#e3692a",   # orange
            "Strong":      "#58a6ff",   # blue
            "Very Strong": "#3fb950",   # green
        }
        bar_color = bar_colors[label]

        st.markdown(
            f'<div class="bar-track">'
            f'  <div class="bar-fill" style="width:{score}%; background-color:{bar_color};"></div>'
            f'</div>'
            f'<div class="bar-label">{score} / 100</div>',
            unsafe_allow_html=True
        )

        # ── 3. RULES CHECKLIST ──────────────────────────────────────────────
        # Loop through every rule and show a green tick or red cross
        st.markdown('<div class="section-heading">Rules Checklist</div>', unsafe_allow_html=True)

        checklist_html = ""
        for rule_name, passed in checks.items():
            if passed:
                icon  = "✅"
                style = "check-pass"
            else:
                icon  = "❌"
                style = "check-fail"
            checklist_html += (
                f'<div class="check-row">'
                f'  <span class="check-icon">{icon}</span>'
                f'  <span class="{style}">{rule_name}</span>'
                f'</div>'
            )

        st.markdown(checklist_html, unsafe_allow_html=True)

        # ── 4. IMPROVEMENT TIPS ─────────────────────────────────────────────
        # Show up to 3 short tips (or a success message if everything passed)
        st.markdown('<div class="section-heading">💡 Tips</div>', unsafe_allow_html=True)

        tips_html = "<br>".join(f"• {tip}" for tip in tips)
        st.markdown(f'<div class="tips-box">{tips_html}</div>', unsafe_allow_html=True)

        # ── 5. BREACH CHECK ─────────────────────────────────────────────────
        # Call the Have I Been Pwned API using k-anonymity (see function above)
        st.markdown('<div class="section-heading">🔎 Breach Check</div>', unsafe_allow_html=True)

        with st.spinner("Checking against known breach databases…"):
            breach_count, breach_error = check_breach(password)

        if breach_error:
            # Something went wrong (no internet, timeout, etc.) — show a neutral warning
            st.markdown(
                f'<div class="breach-warn">⚠️ {breach_error}</div>',
                unsafe_allow_html=True
            )
        elif breach_count > 0:
            # Password was found in breach data — show a red alert with the count
            st.markdown(
                f'<div class="breach-found">'
                f'🚨 This password appeared <strong>{breach_count:,}</strong> time{"s" if breach_count != 1 else ""} '
                f'in known data breaches. Do not use it.'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            # Password was not found — show a green confirmation
            st.markdown(
                '<div class="breach-safe">✅ Not found in known breaches.</div>',
                unsafe_allow_html=True
            )

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
# Shown at the bottom of the page regardless of whether the button was clicked.

st.markdown(
    '<div class="footer">'
    'Built with '
    '<a href="https://www.python.org/" target="_blank">Python</a> · '
    '<a href="https://streamlit.io/" target="_blank">Streamlit</a> · '
    '<a href="https://haveibeenpwned.com/Passwords" target="_blank">Have I Been Pwned API</a> · '
    '<a href="https://www.ibm.com/products/ibm-bob" target="_blank">IBM Bob</a>'
    '</div>',
    unsafe_allow_html=True,
)
