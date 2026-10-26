"""
generate_report.py
──────────────────
Builds PROJECT_REPORT.docx for the PassGuard project.
Run:  python generate_report.py

Requires python-docx:
    pip install python-docx
"""

import datetime
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ── helpers ──────────────────────────────────────────────────────────────────

def set_line_spacing(paragraph, spacing=1.5):
    """Apply 1.5× line spacing to a paragraph."""
    pf = paragraph.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = spacing


def justify(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def add_body(doc, text, bold=False, italic=False, spacing=True):
    """Add a justified 12 pt Times New Roman paragraph."""
    p = doc.add_paragraph()
    if spacing:
        set_line_spacing(p)
    justify(p)
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    return p


def add_heading1(doc, text):
    """Numbered bold heading, 16 pt, Times New Roman."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)
    return p


def add_heading2(doc, text):
    """Sub-heading, 14 pt bold, Times New Roman."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    return p


def add_code(doc, text):
    """Inline code block: Consolas 10 pt, light grey shading."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(1)
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(10)
    # light grey background via XML shading
    rpr = run._r.get_or_add_rPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F0F0F0")
    rpr.append(shd)
    return p


def add_bullet(doc, text):
    """Bulleted list item, 12 pt Times New Roman."""
    p = doc.add_paragraph(style="List Bullet")
    set_line_spacing(p)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    return p


def add_page_number(doc):
    """Insert a centre-aligned page number field in the footer."""
    section = doc.sections[0]
    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.text = " PAGE "
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


def bordered_table(doc, headers, rows, col_widths=None):
    """Create a table with borders, bold header row."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.style = "Table Grid"

    # Header row
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        # grey header background
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "D9D9D9")
        tcPr.append(shd)

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row = table.rows[r_idx + 1]
        for c_idx, cell_text in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = str(cell_text)
            for run in cell.paragraphs[0].runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(11)

    return table


def placeholder(doc, label):
    """Insert a grey placeholder box for a screenshot."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"[ {label} ]")
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    run.font.italic = True
    return p


# ── build document ───────────────────────────────────────────────────────────

doc = Document()

# Page margins
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.5)

add_page_number(doc)

# ════════════════════════════════════════════════════════════════
#  TITLE PAGE
# ════════════════════════════════════════════════════════════════

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

def centre_bold(doc, text, size):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    return p

centre_bold(doc, "PassGuard", 28)
centre_bold(doc, "Password Strength Checker and Breach-Check Tool", 18)

doc.add_paragraph()
doc.add_paragraph()

def centre_normal(doc, text, size=12):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    return p

centre_normal(doc, "Submitted by:")
centre_bold(doc, "ILTAF RAJA", 14)
doc.add_paragraph()
centre_normal(doc, "College / Course:")
centre_bold(doc, "[YOUR COLLEGE / COURSE]", 14)
doc.add_paragraph()
centre_normal(doc, "Date:")
centre_bold(doc, datetime.date.today().strftime("%d %B %Y"), 14)
doc.add_paragraph()
doc.add_paragraph()
centre_normal(doc, "A Cybersecurity Project Report", 12)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
#  TABLE OF CONTENTS  (static — update field in Word with F9)
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "Table of Contents")

toc_entries = [
    ("1.", "Abstract"),
    ("2.", "Introduction"),
    ("3.", "Problem Statement"),
    ("4.", "Objectives"),
    ("5.", "Tools and Technologies Used"),
    ("6.", "System Design"),
    ("7.", "Methodology — Strength Scoring"),
    ("8.", "Breach Check Using k-Anonymity"),
    ("9.", "Password Generator"),
    ("10.", "Security and Privacy Considerations"),
    ("11.", "Testing"),
    ("12.", "Results and Screenshots"),
    ("13.", "Limitations"),
    ("14.", "Future Scope"),
    ("15.", "Conclusion"),
    ("16.", "References"),
]

for num, title in toc_entries:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{num}  {title}")
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
#  1. ABSTRACT
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "1. Abstract")

add_body(doc,
    "PassGuard is a cybersecurity web application developed using Python and Streamlit. "
    "It provides three core services in a single, easy-to-use interface: a rule-based password "
    "strength analyser that scores passwords from 0 to 100, a real-time breach checker that "
    "queries the Have I Been Pwned (HIBP) Pwned Passwords API using the k-anonymity technique, "
    "and a cryptographically secure password generator built on Python's secrets module. "
    "The application runs entirely in the user's browser session. No password is ever transmitted "
    "in full, stored on a server, or written to any log file. The strength analyser checks six "
    "rules derived from industry guidance and awards points accordingly. The breach checker hashes "
    "the password locally with SHA-1 and sends only the first five characters of the hash to the "
    "external API, ensuring full privacy. PassGuard was built to be accessible to beginners while "
    "demonstrating real-world cybersecurity concepts including hashing, k-anonymity, cryptographic "
    "randomness, and automated testing with pytest."
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
#  2. INTRODUCTION
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "2. Introduction")

add_body(doc,
    "Passwords remain the most widely used form of authentication on the internet. Despite decades "
    "of awareness campaigns, weak passwords continue to be one of the leading causes of security "
    "breaches. According to the Verizon 2023 Data Breach Investigations Report, over 80% of "
    "hacking-related breaches involve stolen or weak credentials. Common choices such as \"123456\", "
    "\"password\", and \"qwerty\" appear in billions of leaked records that are freely available to "
    "attackers in credential-stuffing databases."
)

add_body(doc,
    "The problem is compounded by the fact that users often have no way of knowing whether a "
    "password they have chosen has already been exposed in a previous breach. Even a password that "
    "looks complex may have been used by millions of other people and therefore already exists in "
    "attacker databases. Tools that educate users about password quality and breach exposure can "
    "significantly reduce this risk."
)

add_body(doc,
    "PassGuard was created to address this gap. It provides instant, visual feedback on password "
    "strength, checks for known breaches without compromising privacy, and offers a generator for "
    "users who want a secure password without having to think one up themselves. The entire "
    "application fits in a single Python file, making it straightforward for students and developers "
    "to read, understand, and extend."
)

# ════════════════════════════════════════════════════════════════
#  3. PROBLEM STATEMENT
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "3. Problem Statement")

add_body(doc,
    "Most users have no reliable way to evaluate whether a password they have chosen is strong "
    "enough to resist attack, or whether it has already been leaked in a data breach. Existing "
    "strength meters built into websites vary widely in quality, often awarding high scores to "
    "passwords that are actually weak (for example, \"Password1!\" passes many basic meters but is "
    "trivially guessable). Furthermore, checking a password against a breach database typically "
    "requires sending the full password to a third-party server, which itself creates a privacy risk."
)

add_body(doc,
    "PassGuard solves both problems. It applies a consistent, transparent scoring model that "
    "reflects real password-quality factors, and it performs breach checking using the k-anonymity "
    "protocol, which mathematically guarantees that the full password never leaves the user's machine."
)

# ════════════════════════════════════════════════════════════════
#  4. OBJECTIVES
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "4. Objectives")

objectives = [
    "To build a web application that evaluates password strength against six measurable rules "
    "and produces a numerical score and a plain-language label.",

    "To integrate the Have I Been Pwned Pwned Passwords API using the k-anonymity method, "
    "ensuring that no complete password or complete hash is ever transmitted over the network.",

    "To provide a cryptographically secure password generator that uses Python's secrets module "
    "and allows users to control length and character composition.",

    "To present results clearly through colour-coded cards, a progress bar, a rules checklist, "
    "and targeted improvement tips so that non-technical users can understand their security status.",

    "To write an automated test suite using pytest that verifies scoring logic and SHA-1 "
    "prefix/suffix splitting against known reference values, ensuring correctness of the core functions.",
]

for i, obj in enumerate(objectives, 1):
    add_bullet(doc, f"{i}.  {obj}")

# ════════════════════════════════════════════════════════════════
#  5. TOOLS AND TECHNOLOGIES
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "5. Tools and Technologies Used")

tech_rows = [
    ("Python 3.8+",          "Core programming language; chosen for readability and its rich standard library."),
    ("Streamlit ≥ 1.32",     "Web UI framework that turns a Python script into an interactive browser app with no HTML or JavaScript required."),
    ("hashlib (built-in)",   "Provides SHA-1 hashing for the k-anonymity breach-check flow; no installation needed."),
    ("re (built-in)",        "Regular expressions used to detect character types (uppercase, digits, special chars) in the password."),
    ("requests ≥ 2.28",      "Makes the HTTPS GET request to the Have I Been Pwned range API endpoint."),
    ("secrets (built-in)",   "Generates cryptographically secure random passwords using the OS entropy source instead of the predictable random module."),
    ("string (built-in)",    "Supplies pre-built character sets (ascii_lowercase, ascii_uppercase, digits) for the password generator."),
    ("pytest ≥ 7.0",         "Test runner used for the automated test suite; supports class-based test organisation and detailed output with -v."),
    ("Have I Been Pwned API","Free public API by Troy Hunt; the /range/ endpoint enables k-anonymity breach checking against billions of leaked credentials."),
    ("IBM Bob",              "AI coding assistant used to scaffold, refine, and document the project across all iterations."),
]

bordered_table(doc, ["Tool / Library", "Why It Was Used"], tech_rows, col_widths=[4, 10])

# ════════════════════════════════════════════════════════════════
#  6. SYSTEM DESIGN
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "6. System Design")

add_body(doc,
    "PassGuard follows a simple linear flow when the user clicks the Check Password button. "
    "The table below describes each step in order."
)

design_rows = [
    ("1", "User Input",          "The user types a password into a hidden text input field (st.text_input with type='password'). Characters are masked as they are typed."),
    ("2", "Empty Check",         "If the input is blank, a warning message is shown and processing stops. No function is called."),
    ("3", "Strength Analysis",   "check_password_strength(password) is called. It checks the common-password list, evaluates six rules, calculates a score, assigns a label, and returns a checklist dict and up to three tips."),
    ("4", "Result Display",      "A coloured result card shows the label and score. A CSS progress bar fills to the score percentage in the matching colour. The rules checklist shows a green tick or red cross per rule. Up to three tips are shown."),
    ("5", "Breach Check",        "check_breach(password) is called. It hashes the password with SHA-1 locally, sends only the first 5 characters to the HIBP API, receives ~800 suffix lines, and searches locally for a match."),
    ("6", "Breach Result",       "If a match is found, a red alert shows the exact breach count. If no match, a green confirmation is shown. If the API is unreachable, a neutral grey warning is shown instead."),
    ("7", "Generator (Sidebar)", "Independently, the sidebar lets the user choose a length (8–32) and character types, then click Generate Password. generate_password() builds a password using secrets.choice() and immediately scores it with check_password_strength()."),
]

bordered_table(doc, ["Step", "Stage", "Description"], design_rows)

# ════════════════════════════════════════════════════════════════
#  7. METHODOLOGY — STRENGTH SCORING
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "7. Methodology — Strength Scoring")

add_body(doc,
    "The strength scoring function check_password_strength() in app.py applies six rules in "
    "sequence. Each rule that passes adds a fixed number of points to the total score. "
    "The score is then capped at 100 and mapped to one of four labels. The complete ruleset "
    "is shown in the table below."
)

scoring_rows = [
    ("Common password check", "Password matches a hardcoded list of 15 very common passwords (e.g. '123456', 'password', 'qwerty')", "Score set to 0 immediately; all checks False; function returns early"),
    ("Minimum length",        "len(password) >= 8",  "+20 points"),
    ("Bonus length",          "len(password) >= 12 (replaces the +20 if true)", "+35 points"),
    ("Uppercase letter",      "re.search(r'[A-Z]', password)", "+15 points"),
    ("Lowercase letter",      "re.search(r'[a-z]', password)", "+15 points"),
    ("Number",                "re.search(r'[0-9]', password)", "+15 points"),
    ("Special character",     "re.search(r'[!@#$%^&*(),.?...]+', password)", "+20 points"),
]

bordered_table(doc, ["Rule", "Condition in Code", "Points"], scoring_rows)

add_body(doc, "")
add_body(doc,
    "The label is assigned based on the final score after all rules are evaluated and the "
    "100-point cap is applied:"
)

label_rows = [
    ("0 – 39",   "Weak",        "Red card (#f85149)"),
    ("40 – 59",  "Medium",      "Orange card (#e3692a)"),
    ("60 – 79",  "Strong",      "Blue card (#58a6ff)"),
    ("80 – 100", "Very Strong", "Green card (#3fb950)"),
]

bordered_table(doc, ["Score Range", "Label", "UI Colour"], label_rows)

add_body(doc, "")
add_body(doc,
    "Example: the password \"MyS3cure#Pass!\" has length 14 (≥12, so +35), contains uppercase "
    "(+15), lowercase (+15), a digit (+15), and a special character (+20). Total: 100. Label: "
    "Very Strong. The function also generates up to three improvement tips by collecting every "
    "failed rule and returning only the first three, keeping the UI uncluttered."
)

add_code(doc,
    "score = 0\n"
    "if has_long:    score += 35   # 12+ chars\n"
    "elif has_min:   score += 20   # 8–11 chars\n"
    "if has_upper:   score += 15\n"
    "if has_lower:   score += 15\n"
    "if has_digit:   score += 15\n"
    "if has_special: score += 20\n"
    "score = min(score, 100)"
)

# ════════════════════════════════════════════════════════════════
#  8. BREACH CHECK — K-ANONYMITY
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "8. Breach Check Using k-Anonymity")

add_body(doc,
    "The Have I Been Pwned (HIBP) Pwned Passwords service maintains a database of over 800 million "
    "password hashes collected from publicly known data breaches. PassGuard queries this database "
    "using a technique called k-anonymity, which allows a password to be checked without revealing "
    "the password to the server."
)

add_heading2(doc, "8.1  How k-Anonymity Works")

add_body(doc,
    "The protocol has four steps, all implemented in the check_breach() function in app.py:"
)

steps = [
    "Hash locally. The password is hashed using SHA-1 on the user's machine. "
    "SHA-1 produces a 40-character hexadecimal string. Example: "
    "\"hello\" → aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d (converted to uppercase: AAF4C61DDCC5E8A2DABEDE0F3B482CD9AEA9434D).",

    "Split the hash. Only the first 5 characters (the prefix) are prepared for sending. "
    "The remaining 35 characters (the suffix) stay on the machine. "
    "Prefix: AAF4C. Suffix: 61DDCC5E8A2DABEDE0F3B482CD9AEA9434D.",

    "Query the API. An HTTPS GET request is sent to https://api.pwnedpasswords.com/range/AAF4C. "
    "The server returns approximately 800 lines, each containing a hash suffix and breach count "
    "for every hash in its database that begins with AAF4C. The server has no way of knowing "
    "which of these ~800 passwords was actually being checked.",

    "Compare locally. The returned list is searched on the user's machine for the local suffix "
    "(61DDCC5E8A2DABEDE0F3B482CD9AEA9434D). If it is found, the breach count on that line is "
    "returned and displayed as a red alert. If it is not found, a green confirmation is shown.",
]

for i, step in enumerate(steps, 1):
    add_bullet(doc, f"Step {i}: {step}")

add_body(doc, "")
add_body(doc,
    "The k-anonymity guarantee comes from the fact that the 5-character prefix matches "
    "16^5 = 1,048,576 possible hash buckets. The server sees only a prefix that is shared by "
    "hundreds of completely different passwords, so it cannot determine what the user actually typed."
)

add_heading2(doc, "8.2  Worked Example")

add_code(doc,
    "password  = \"hello\"\n"
    "sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()\n"
    "# sha1_hash = 'AAF4C61DDCC5E8A2DABEDE0F3B482CD9AEA9434D'\n\n"
    "prefix = sha1_hash[:5]   # 'AAF4C'  ← sent to API\n"
    "suffix = sha1_hash[5:]   # '61DDCC5E8A2DABEDE0F3B482CD9AEA9434D'  ← stays local\n\n"
    "# API response line (example):\n"
    "# 61DDCC5E8A2DABEDE0F3B482CD9AEA9434D:3861493\n"
    "# → 'hello' has appeared 3,861,493 times in known breaches."
)

add_heading2(doc, "8.3  Error Handling")

add_body(doc,
    "The function catches three categories of network failure: ConnectionError (no internet), "
    "Timeout (server did not respond within 5 seconds), and any other RequestException (HTTP "
    "error codes). In all cases a neutral grey warning is displayed and the strength results "
    "above it remain fully usable."
)

# ════════════════════════════════════════════════════════════════
#  9. PASSWORD GENERATOR
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "9. Password Generator")

add_body(doc,
    "The sidebar password generator allows users to create a new password rather than evaluating "
    "an existing one. It is controlled by a length slider (range: 8 to 32 characters, default: 16) "
    "and three checkboxes for uppercase letters (A–Z), numbers (0–9), and symbols (!@#…). "
    "Lowercase letters (a–z) are always included as the base character set."
)

add_body(doc,
    "Passwords are constructed using Python's secrets module rather than the standard random module. "
    "The distinction is important for security. The random module uses a deterministic pseudorandom "
    "number generator (the Mersenne Twister) seeded from the system clock. An attacker who knows "
    "the approximate time a password was generated could reconstruct the seed and reproduce the "
    "entire output. The secrets module, by contrast, reads from the operating system's "
    "cryptographically secure entropy source (/dev/urandom on Linux and macOS, CryptGenRandom "
    "on Windows). This source is non-deterministic and cannot be reversed or predicted."
)

add_code(doc,
    "alphabet = string.ascii_lowercase   # always included\n"
    "if use_upper:   alphabet += string.ascii_uppercase\n"
    "if use_digits:  alphabet += string.digits\n"
    "if use_symbols: alphabet += '!@#$%^&*()_+-=[]{}|;:,.<>?'\n\n"
    "password = ''.join(secrets.choice(alphabet) for _ in range(length))"
)

add_body(doc,
    "After generation, the password is immediately passed to check_password_strength() and the "
    "score and label are displayed alongside the password in a small strength badge. If all "
    "character-type checkboxes are left unchecked (resulting in a lowercase-only password), a "
    "warning is shown encouraging the user to enable more options."
)

# ════════════════════════════════════════════════════════════════
#  10. SECURITY AND PRIVACY
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "10. Security and Privacy Considerations")

privacy_points = [
    "No storage. PassGuard does not use a database, file system, or any persistent storage. "
    "Every password entered into the tool exists only in the memory of the current browser session "
    "and is discarded when the tab is closed or the page is refreshed.",

    "No logging. Streamlit does not automatically log user input values. The application does not "
    "call any logging function, write to any file, or send any analytics data.",

    "Full password never transmitted. The breach check uses k-anonymity (described in Section 8). "
    "The only data sent over the network is the 5-character SHA-1 prefix. The full password and "
    "the full hash are computed and remain local.",

    "Cryptographically secure generation. The password generator uses secrets.choice(), which is "
    "the Python standard library's recommended function for generating tokens, passwords, and other "
    "security-critical values.",

    "Input masking. The password input field uses Streamlit's type='password' parameter, which "
    "renders the field with masked characters so the password is not visible on screen.",
]

for point in privacy_points:
    add_bullet(doc, point)

# ════════════════════════════════════════════════════════════════
#  11. TESTING
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "11. Testing")

add_body(doc,
    "The test suite is contained in test_app.py and is run with pytest. It contains 25 individual "
    "test cases organised across six test classes. Since app.py calls Streamlit functions at "
    "module level (during import), the test file injects a lightweight stub module in place of "
    "streamlit before importing the application functions. This allows all tests to run instantly "
    "without a browser or network connection."
)

test_rows = [
    ("test_password_literal_scores_zero",         "\"password\"",            "score=0, label=\"Weak\"",        "PASS"),
    ("test_123456_scores_zero",                    "\"123456\"",              "score=0, label=\"Weak\"",        "PASS"),
    ("test_common_password_case_insensitive",      "\"PASSWORD\"",            "score=0, label=\"Weak\"",        "PASS"),
    ("test_common_password_all_checks_false",      "\"admin\"",               "All checks dict values = False", "PASS"),
    ("test_very_short_lowercase_only",             "\"hello\"",               "score=15, label=\"Weak\"",       "PASS"),
    ("test_tips_capped_at_three",                  "\"a\"",                   "len(tips) <= 3",                 "PASS"),
    ("test_eight_chars_lower_and_digit_only",      "\"hello123\"",            "score=50, label=\"Medium\"",     "PASS"),
    ("test_medium_tip_suggests_special_char",      "\"hello123\"",            "\"special\" in tips text",       "PASS"),
    ("test_eight_chars_mixed_case_and_digit",      "\"Hello123\"",            "score=65, label=\"Strong\"",     "PASS"),
    ("test_eight_char_all_types",                  "\"Hello1!a\"",            "score=85, label=\"Very Strong\"","PASS"),
    ("test_full_score_password",                   "\"MyS3cure#Pass!\"",      "score=100, label=\"Very Strong\"","PASS"),
    ("test_very_strong_all_checks_pass",           "\"MyS3cure#Pass!\"",      "All checks True",                "PASS"),
    ("test_very_strong_no_improvement_tips",       "\"MyS3cure#Pass!\"",      "len(tips)==1, congratulations",  "PASS"),
    ("test_score_never_exceeds_100",               "Long complex password",   "score <= 100",                   "PASS"),
    ("test_hello_prefix",                          "SHA-1(\"hello\")",        "prefix == \"AAF4C\"",            "PASS"),
    ("test_hello_suffix",                          "SHA-1(\"hello\")",        "suffix == \"61DDCC5E8A2...\"",   "PASS"),
    ("test_prefix_is_exactly_5_chars",             "Any string",              "len(prefix) == 5",               "PASS"),
    ("test_suffix_is_exactly_35_chars",            "Any string",              "len(suffix) == 35",              "PASS"),
    ("test_prefix_plus_suffix_equals_full_hash",   "\"TestPassword99!\"",     "prefix + suffix == full hash",   "PASS"),
    ("test_hash_is_uppercase",                     "SHA-1(\"hello\")",        "No lowercase in output",         "PASS"),
    ("test_hash_is_hexadecimal",                   "SHA-1(\"hello\")",        "Only 0-9 and A-F chars",         "PASS"),
    ("test_empty_string_has_known_sha1",           "\"\" (empty string)",     "prefix==\"DA39A\"",              "PASS"),
]

bordered_table(doc,
    ["Test Name", "Input", "Expected Result", "Status"],
    test_rows
)

add_body(doc, "")
add_body(doc,
    "All 25 tests pass. The suite can be run at any time with the command: "
    "pytest test_app.py -v"
)

# ════════════════════════════════════════════════════════════════
#  12. RESULTS AND SCREENSHOTS
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "12. Results and Screenshots")

add_body(doc,
    "The following screenshots illustrate the application's behaviour across different scenarios. "
    "Replace each placeholder with an actual screenshot taken from the running application."
)

screenshot_items = [
    ("Insert Screenshot: Weak Password Result",
     "A common password such as \"password\" entered. Shows a red result card scoring 0/100, "
     "all checklist items with red crosses, and the common-password tip."),
    ("Insert Screenshot: Medium Password Result",
     "A password such as \"hello123\" scoring 50/100. Shows orange card, partial checklist passes, "
     "and tips suggesting uppercase and special characters."),
    ("Insert Screenshot: Strong Password Result",
     "A password such as \"MyS3cure#Pass!\" scoring 100/100. Shows green card, all checklist "
     "items green, and the congratulations tip."),
    ("Insert Screenshot: Breached Password Result",
     "A common password that returns a breach count from the HIBP API, showing the red breach "
     "alert with the exact number of occurrences."),
    ("Insert Screenshot: Password Generator",
     "The sidebar open with length slider at 20, all checkboxes ticked, and a generated password "
     "displayed with its strength badge."),
]

for label_text, desc in screenshot_items:
    add_heading2(doc, label_text)
    add_body(doc, desc)
    placeholder(doc, label_text)
    doc.add_paragraph()

# ════════════════════════════════════════════════════════════════
#  13. LIMITATIONS
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "13. Limitations")

limitations = [
    "SHA-1 is not collision-resistant for security purposes. Although the k-anonymity protocol "
    "here does not rely on SHA-1's collision resistance (it only uses it to map a password to a "
    "stable identifier), NIST deprecated SHA-1 for general cryptographic use in 2011. A future "
    "version should use SHA-256 if and when the HIBP API supports it.",

    "No HTTPS enforcement on localhost. When running locally with streamlit run app.py, the "
    "connection is plain HTTP. This is acceptable for local development but would need a reverse "
    "proxy with TLS termination for any public deployment.",

    "Single-file architecture limits scalability. All application code, UI, and logic live in "
    "one file (app.py). While this is ideal for learning, a production system would separate "
    "concerns into modules (ui.py, checker.py, breach.py) to improve maintainability.",

    "Strength scoring does not account for dictionary words or keyboard patterns. A password "
    "such as \"Tr0ub4dor&3\" would score highly under the current rules despite being based on a "
    "dictionary word. A more sophisticated model using the zxcvbn algorithm would catch such cases.",

    "The breach check requires an internet connection. If the HIBP API is unreachable, the "
    "feature degrades gracefully but the user receives no breach information. An offline fallback "
    "using a local subset of common breached hashes could improve resilience.",
]

for lim in limitations:
    add_bullet(doc, lim)

# ════════════════════════════════════════════════════════════════
#  14. FUTURE SCOPE
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "14. Future Scope")

future = [
    "zxcvbn integration. Replace the current point-based scorer with Dropbox's open-source "
    "zxcvbn library, which analyses dictionary words, keyboard patterns, common substitutions "
    "(e.g. '3' for 'e'), and repeated characters to produce a more realistic entropy estimate.",

    "Passphrase generator. Add a second generation mode that produces memorable passphrases "
    "from a dictionary of common English words (e.g. 'correct-horse-battery-staple'), following "
    "NIST SP 800-63B guidance that length and randomness matter more than character complexity.",

    "Session history. Maintain a within-session table showing the score and label for every "
    "password checked so that users can compare candidates side by side before choosing one. "
    "No passwords would be persisted beyond the session.",

    "Copy-to-clipboard button. Add a single-click copy button next to the generated password "
    "so users can paste it directly into a password manager without manually selecting the text.",

    "Multi-language support. Add a language selector to render all UI text, tips, and labels in "
    "languages other than English, making the tool accessible to a wider audience.",

    "Deployment and authentication. Package the application as a Docker container and deploy it "
    "behind HTTPS with an optional rate limiter on the breach-check endpoint to prevent abuse.",
]

for item in future:
    add_bullet(doc, item)

# ════════════════════════════════════════════════════════════════
#  15. CONCLUSION
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "15. Conclusion")

add_body(doc,
    "PassGuard demonstrates that meaningful cybersecurity tooling can be built in Python with "
    "a modest amount of code. The project combines four distinct technical concepts — rule-based "
    "scoring, SHA-1 hashing, the k-anonymity protocol, and cryptographic randomness — into a "
    "single, cohesive application that is accessible to non-technical users while remaining "
    "instructive for developers."
)

add_body(doc,
    "The strength scorer applies a transparent, point-based model whose rules are drawn directly "
    "from established guidance such as NIST SP 800-63B and the OWASP Authentication Cheat Sheet. "
    "The breach checker implements the Have I Been Pwned k-anonymity protocol correctly, ensuring "
    "that no complete password is ever transmitted. The password generator uses the standard "
    "library's secrets module, which is the appropriate tool for security-critical randomness."
)

add_body(doc,
    "All core logic is covered by 25 automated pytest tests that verify exact scores, label "
    "thresholds, checklist states, and SHA-1 hash values against known reference outputs. "
    "The application is privacy-respecting by design: no data is stored, no logs are written, "
    "and the user's password never leaves their browser session in full."
)

add_body(doc,
    "PassGuard serves both as a practical security tool and as a learning artefact that "
    "illustrates how to build secure, well-tested, privacy-preserving software in Python."
)

# ════════════════════════════════════════════════════════════════
#  16. REFERENCES
# ════════════════════════════════════════════════════════════════

add_heading1(doc, "16. References")

references = [
    "Hunt, T. (2018). \"Pwned Passwords — HIBP Range API\". Have I Been Pwned. "
    "Available at: https://haveibeenpwned.com/API/v3#PwnedPasswords [Accessed: "
    + datetime.date.today().strftime("%d %B %Y") + "].",

    "Grassi, P. A., Garcia, M. E., & Fenton, J. L. (2017). "
    "NIST Special Publication 800-63B: Digital Identity Guidelines — Authentication and "
    "Lifecycle Management. National Institute of Standards and Technology. "
    "Available at: https://pages.nist.gov/800-63-3/sp800-63b.html",

    "OWASP Foundation (2023). Authentication Cheat Sheet. "
    "Available at: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",

    "Streamlit Inc. (2024). Streamlit Documentation. "
    "Available at: https://docs.streamlit.io",

    "Python Software Foundation (2024). secrets — Generate secure random numbers for managing "
    "secrets. Python 3 Documentation. "
    "Available at: https://docs.python.org/3/library/secrets.html",

    "Cloudflare / Troy Hunt (2018). \"k-Anonymity: A model for protecting privacy\" — "
    "description of the HIBP implementation. "
    "Available at: https://blog.cloudflare.com/validating-leaked-passwords-with-k-anonymity/",
]

for ref in references:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent  = Cm(1.0)
    p.paragraph_format.first_line_indent = Cm(-1.0)
    p.paragraph_format.space_after  = Pt(6)
    set_line_spacing(p)
    run = p.add_run(ref)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)

# ════════════════════════════════════════════════════════════════
#  SAVE
# ════════════════════════════════════════════════════════════════

output_path = "PROJECT_REPORT.docx"
doc.save(output_path)
print(f"Report saved: {output_path}")
