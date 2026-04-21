import re

def clean_text(text: str) -> str:
    if text is None:
        return ""
    text = text.strip()
    text = re.sub(r"http\S+|www\.\S+", "", text)        # remove urls
    text = re.sub(r"\s+", " ", text)                   # normalize spaces
    return text

class TextPreprocessor:
    def clean(self, text: str) -> str:
        return clean_text(text)
    
