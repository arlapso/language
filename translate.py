#!/usr/bin/env python3
"""
Bevel Language Translation Tool

Translates a word or phrase into all Bevel-supported languages,
shows character/word counts, and highlights the longest translation.

Usage:
    python translate.py "Hello, how are you?"
    python translate.py --json "Settings"
"""

import argparse
import json
import sys

import site
site.addsitedir(site.getusersitepackages())

try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("Installing deep-translator...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "deep-translator", "-q"])
    site.addsitedir(site.getusersitepackages())
    from deep_translator import GoogleTranslator


LANGUAGES = [
    ("en", "English"),
    ("zh-CN", "Chinese, Simplified", "简体中文"),
    ("zh-TW", "Chinese, Traditional", "繁體中文"),
    ("nl", "Dutch", "Nederlands"),
    ("fr", "French", "Français"),
    ("de", "German", "Deutsch"),
    ("it", "Italian", "Italiano"),
    ("ja", "Japanese", "日本語"),
    ("es", "Spanish", "Español"),
    ("vi", "Vietnamese", "Tiếng Việt"),
    ("ru", "Russian", "Русский"),
    ("pt", "Portuguese", "Português"),
    ("pl", "Polish", "Polski"),
]


def translate_all(text: str) -> list[dict]:
    results = []
    for lang_entry in LANGUAGES:
        code = lang_entry[0]
        label = lang_entry[1]
        native = lang_entry[2] if len(lang_entry) > 2 else "English"

        if code == "en":
            translated = text
        else:
            try:
                translated = GoogleTranslator(source="en", target=code).translate(text)
            except Exception as e:
                translated = f"[error: {e}]"

        chars = len(translated)
        words = len(translated.split())

        results.append({
            "code": code,
            "language": label,
            "native_name": native,
            "translation": translated,
            "chars": chars,
            "words": words,
        })

    return results


def print_table(text: str, results: list[dict]):
    longest = max(results, key=lambda r: r["chars"])

    # Column widths
    lang_w = max(len(f"{r['native_name']} ({r['language']})") for r in results)
    trans_w = max(max(len(r["translation"]) for r in results), len("Translation"))
    # Cap translation column for very long texts
    trans_w = min(trans_w, 80)

    header_lang = "Language".ljust(lang_w)
    header_trans = "Translation".ljust(trans_w)

    print()
    print(f"  Source (English): \033[1m{text}\033[0m")
    print()
    print(f"  {'─' * (lang_w + trans_w + 24)}")
    print(f"  {header_lang}  │  {header_trans}  │  Chars  │  Words")
    print(f"  {'─' * (lang_w + trans_w + 24)}")

    for r in results:
        lang_label = f"{r['native_name']} ({r['language']})"
        translation = r["translation"]
        if len(translation) > 80:
            translation = translation[:77] + "..."

        is_longest = r["code"] == longest["code"]

        if is_longest:
            # Highlight with yellow background
            line = (
                f"  \033[43m\033[30m"
                f"{lang_label.ljust(lang_w)}  │  "
                f"{translation.ljust(trans_w)}  │  "
                f"{str(r['chars']).rjust(5)}  │  {str(r['words']).rjust(5)}"
                f" ◀ LONGEST\033[0m"
            )
        else:
            line = (
                f"  {lang_label.ljust(lang_w)}  │  "
                f"{translation.ljust(trans_w)}  │  "
                f"{str(r['chars']).rjust(5)}  │  {str(r['words']).rjust(5)}"
            )
        print(line)

    print(f"  {'─' * (lang_w + trans_w + 24)}")
    print()
    print(f"  Longest translation: \033[1m{longest['native_name']} ({longest['language']})\033[0m"
          f" — {longest['chars']} chars, {longest['words']} words")
    print()


def main():
    parser = argparse.ArgumentParser(description="Translate text into all Bevel-supported languages")
    parser.add_argument("text", help="Word or phrase to translate (English)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = translate_all(args.text)

    if args.json:
        output = {
            "source": args.text,
            "translations": results,
            "longest": max(results, key=lambda r: r["chars"]),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_table(args.text, results)


if __name__ == "__main__":
    main()
