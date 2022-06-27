import pandas as pd
import parsivar
import hazm
import re

from pip import main


class Preprocess:
    def __init__(self):
        self.normalizer = parsivar.Normalizer(pinglish_conversion_needed=True)
        self.tokenizer = parsivar.Tokenizer()
        self.stemmer = parsivar.FindStems()
        self.stop_words = hazm.stopwords_list()
        self.to_remove = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹',
                          '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                          '(', ')', '[', ']', '«', '»', '<<', '>>', '{', '}',
                          '?', '،', '.', ':', '-', '_', '/', '=', '؛', '&', "%", "#", "*",
                          'https://', 'http://', 'انتهای پیام', '://']

    def normalize(self, sentence):
        return self.normalizer.normalize(sentence)

    def tokenize(self, sentence):
        sentence = sentence.replace("انتهای پیام", "")
        tokens = self.tokenizer.tokenize_words(sentence)

        return tokens

    def stem(self, tokens):
        stem_tokens_indexed = []
        for token in tokens:
            stem_tokens = self.stemmer.convert_to_stem(token)

            stem_tokens_indexed.append(stem_tokens)

        return stem_tokens_indexed

    def redact_stops(self, tokens):
        temp = set(self.stop_words)
        to_redact1 = [_ for _ in tokens if _ in temp]

        temp2 = set(self.to_remove)
        to_redact2 = [_ for _ in tokens if _ in temp2]

        to_redact = to_redact1 + to_redact2

        tokens = list(filter(lambda k: k not in to_redact, tokens))

        return " ".join(tokens)

    def query_preprocess(self, query):

        query_normalized = self.normalize(query)
        query_tokenized = self.tokenize(query_normalized)
        query_stemmed = self.stem(query_tokenized)
        return self.redact_stops(query_stemmed)


def query_parser(query):
    preprocess = Preprocess()

    phrases = re.findall('"([^"]*)"', query)

    nots = []
    seen = False
    for term in query.split(" "):
        if seen:
            nots.append(term)
            seen = False
        if term == '!':
            seen = True

    normal = []
    regex = r'".*?"|(\w+)'
    matches = re.finditer(regex, query, re.MULTILINE)
    for match in matches:
        if match.group(1):
            if match.group(1) not in nots:
                normal.append(match.group(1))

    phrases = list(map(preprocess.query_preprocess, phrases))
    # nots = list(map(preprocess.query_preprocess, nots))
    normal = preprocess.query_preprocess(" ".join(normal))

    return phrases, nots, normal


if __name__ == '__main__':
    query = "\" تحریم هسته‌ای \" آمریکا فرانسه ! ایران"
    phrases, nots, normal = query_parser(query)
    print(phrases)
    print(nots)
    print(normal)