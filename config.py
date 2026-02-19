# Key:   Display name shown to user
# Value: (ISO language code, INCEpTION project name)
LANGUAGES: dict[str, tuple[str, str]] = {
    "Ukrainian": ("uk", "ukrainian"),
    "Russian":   ("ru", "russian"),
    "English":   ("en", "english"),
    "Irish":     ("ga", "irish"),
    "German":    ("de", "german"),
    "Czech":     ("cs", "czech"),
}

# Map language code → instruction JSON file
# Add entries here as you create instruction files for other languages
LANGUAGE_JSON_FILES: dict[str, str] = {
    "de": "data/annotation_setup_de.json",
    "en": "data/annotation_setup_en.json",
    "uk": "data/annotation_setup_uk.json",
    "ru": "data/annotation_setup_ru.json",
    "ga": "data/annotation_setup_ga.json",
    "cs": "data/annotation_setup_cs.json",
}

TU_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/TU-Berlin-Logo.svg/1280px-TU-Berlin-Logo.svg.png"

NATIONALITIES = sorted([
    "Afghan", "Albanian", "Algerian", "American", "Argentinian", "Armenian",
    "Australian", "Austrian", "Azerbaijani", "Bangladeshi", "Belarusian",
    "Belgian", "Bolivian", "Bosnian", "Brazilian", "British", "Bulgarian",
    "Cambodian", "Cameroonian", "Canadian", "Chilean", "Chinese", "Colombian",
    "Croatian", "Czech", "Danish", "Dutch", "Egyptian", "Ethiopian",
    "Finnish", "French", "Georgian", "German", "Ghanaian", "Greek",
    "Hungarian", "Indian", "Indonesian", "Iranian", "Iraqi", "Irish",
    "Israeli", "Italian", "Japanese", "Jordanian", "Kazakh", "Kenyan",
    "Korean", "Kuwaiti", "Lebanese", "Libyan", "Malaysian", "Mexican",
    "Moroccan", "Nigerian", "Norwegian", "Pakistani", "Palestinian",
    "Peruvian", "Philippine", "Polish", "Portuguese", "Romanian", "Russian",
    "Saudi", "Serbian", "Slovak", "South African", "Spanish", "Swedish",
    "Swiss", "Syrian", "Taiwanese", "Thai", "Tunisian", "Turkish",
    "Ukrainian", "Uruguayan", "Venezuelan", "Vietnamese", "Other",
])

NATIVE_LANGUAGES = sorted([
    "Arabic", "Bengali", "Chinese (Mandarin)", "Chinese (Cantonese)",
    "Czech", "Dutch", "English", "Farsi/Persian", "French", "German",
    "Greek", "Hebrew", "Hindi", "Hungarian", "Indonesian", "Irish (Gaelic)",
    "Italian", "Japanese", "Korean", "Malay", "Norwegian", "Polish",
    "Portuguese", "Romanian", "Russian", "Serbian/Croatian", "Spanish",
    "Swedish", "Thai", "Turkish", "Ukrainian", "Vietnamese", "Other",
])

EDUCATION_LEVELS = [
    "High school / Secondary education",
    "Bachelor's degree (ongoing)",
    "Bachelor's degree (completed)",
    "Master's degree (ongoing)",
    "Master's degree (completed)",
    "PhD (ongoing)",
    "PhD (completed)",
    "Other",
]
