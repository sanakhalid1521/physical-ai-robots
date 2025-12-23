from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from typing import Optional


# Set seed for consistent results
DetectorFactory.seed = 0


def detect_language(text: str) -> Optional[str]:
    """
    Detect the language of the given text.

    Args:
        text: Input text to detect language for

    Returns:
        Detected language code ('en', 'ur', etc.) or None if detection fails
    """
    if not text or not text.strip():
        return None

    try:
        detected_lang = detect(text)
        return detected_lang
    except LangDetectException:
        # If detection fails, return None
        return None


def is_urdu(text: str) -> bool:
    """
    Check if the given text is in Urdu.

    Args:
        text: Input text to check

    Returns:
        True if text is in Urdu, False otherwise
    """
    detected_lang = detect_language(text)
    return detected_lang == 'ur'


def is_english(text: str) -> bool:
    """
    Check if the given text is in English.

    Args:
        text: Input text to check

    Returns:
        True if text is in English, False otherwise
    """
    detected_lang = detect_language(text)
    return detected_lang == 'en'


def get_preferred_language(input_text: str, user_preference: Optional[str] = None) -> str:
    """
    Determine the preferred language for response based on input and user preference.

    Args:
        input_text: The input text from the user
        user_preference: User's preferred language ('en' or 'ur')

    Returns:
        Preferred language code ('en' or 'ur')
    """
    # If user has a preference, use that
    if user_preference in ['en', 'ur']:
        return user_preference

    # Otherwise, detect from input text
    detected_lang = detect_language(input_text)

    # If detected as Urdu, prefer Urdu response
    if detected_lang == 'ur':
        return 'ur'

    # Default to English
    return 'en'


def normalize_language_code(lang_code: str) -> Optional[str]:
    """
    Normalize language code to 'en' or 'ur' format.

    Args:
        lang_code: Input language code

    Returns:
        Normalized language code ('en' or 'ur') or None
    """
    if not lang_code:
        return None

    lang_code = lang_code.lower().strip()

    # Map various language codes to our supported ones
    if lang_code in ['en', 'eng', 'english']:
        return 'en'
    elif lang_code in ['ur', 'urd', 'urdu']:
        return 'ur'
    else:
        return None