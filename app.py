#!/usr/bin/env python3
"""Bevel Translation Tool — Web Interface"""

import site
site.addsitedir(site.getusersitepackages())

from flask import Flask, request, jsonify, send_from_directory
from deep_translator import GoogleTranslator
import os

app = Flask(__name__)

LANGUAGES = [
    ("en", "English", "English"),
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


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    results = []
    for code, label, native in LANGUAGES:
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

    longest = max(results, key=lambda r: r["chars"])

    return jsonify({
        "source": text,
        "translations": results,
        "longest_code": longest["code"],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)
