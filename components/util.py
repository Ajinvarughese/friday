import re

def clean_for_tts(text):
    text = text.encode('utf-8', 'ignore').decode('utf-8')

    # normalize quotes
    text = text.replace("’", "'").replace("‘", "'")

    # 🔥 REMOVE markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # inline code
    text = re.sub(r'#+\s', '', text)              # headings
    text = re.sub(r'[-–—]', ' ', text)            # dashes → space

    # remove emojis
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)

    # remove escaped unicode
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)

    # normalize spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def split_text(text, max_len=300):
    sentences = text.split(". ")
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < max_len:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "

    if current:
        chunks.append(current.strip())

    return chunks

def extract_emotion(text):

    match = re.match(r"\[(.*?)\]", text)
    if match:
        emotion = match.group(1).lower()
        text = re.sub(r"^\[.*?\]\s*", "", text)  # remove tag
        return emotion, text

    return "default", text