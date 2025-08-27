from string import punctuation

def remove_punctuation(text:str):
    return text.translate(str.maketrans('','',punctuation))