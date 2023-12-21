import enum


# Language code
class LANGUAGES(enum.Enum):
    ENGLISH = "en"
    JAPANESE = "jp"


# Prompt
class PROMPTS(enum.Enum):
    # English
    INSTRUCT_ENGLISH = """I want you to be my assistant. You follow my rules:

    1. The answers are written in English.
    2. Please give only short answers or short detailed answers. However, the main content must remain.
    
    Let's start!
    """
    INSTRUCT_ENGLISH_MODEL_RESPONSE = """Hello, I am a virtual assistant. I can help you find the answer to your question."""
    FORCE_ENGLISH_INSTRUCT = """. Please write the answer in English."""

    # Japanese
    INSTRUCT_JAPANESE = """あなたを私のアシスタントにしてほしいのです。 あなたは私のルールに従います:
    
    1. 答えは日本語で書かれています。(Japanese)
    2. 短い回答または短い詳細な回答のみをお願いします。ただし、主要な内容は残しておく必要があります。
    
    はじめましょう！
    """
    INSTRUCT_JAPANESE_MODEL_RESPONSE = """こんにちは、私はバーチャルアシスタントです。 質問の答えを見つけるのに役立ちます。"""
    FORCE_JAPANESE_INSTRUCT = """. 日本語で答えを書いてください。"""