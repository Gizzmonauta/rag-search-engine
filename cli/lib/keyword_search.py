import os
import pickle
import string
from collections import defaultdict, Counter

from nltk.stem import PorterStemmer

from .search_utils import (
    CACHE_DIR,
    DEFAULT_SEARCH_LIMIT, 
    load_movies, 
    load_stopwords
    )

class InvertedIndex:
    def __init__(self):
        self.index: dict[str, set[int]] = defaultdict(set)
        self.docmap: dict[int, dict] = {}
        self.term_frequencies: dict[int, Counter] = defaultdict(Counter)
        self.index_path = os.path.join(CACHE_DIR, "index.pkl")
        self.docmap_path = os.path.join(CACHE_DIR, "docmap.pkl")
        self.term_frequencies_path = os.path.join(CACHE_DIR, "term_frequencies.pkl")


    def __add_document(self, doc_id: int, text: str) -> None:
        tokens = tokenize_text(text)
        for token in tokens:
            self.index[token].add(doc_id)
        self.term_frequencies[doc_id].update(tokens)

    def get_tf(self, doc_id: int, term: str) -> int:
        tokens = tokenize_text(term)
        if len(tokens) != 1:
            raise ValueError("Term must be a single token.")
        token = tokens[0]
        return self.term_frequencies[doc_id][token]

    def get_documents(self, term: str) -> list[int]:
        doc_ids: set[int] = set()
        tokens = tokenize_text(term)
        for token in tokens:
            if token in self.index:
                for doc_id in self.index[token]:
                    doc_ids.add(doc_id)
        if not doc_ids:
            return []
        return sorted(list(doc_ids))

    def build(self) -> None:
        movies: list[dict] = load_movies()
        for movie in movies:
            self.docmap[movie["id"]] = movie
            self.__add_document(movie["id"], f"{movie['title']} {movie['description']}")

    def save(self) -> None:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(self.index_path, "wb") as f:
            pickle.dump(self.index, f)
        with open(self.docmap_path, "wb") as f:
            pickle.dump(self.docmap, f)
        with open(self.term_frequencies_path, "wb") as f:
            pickle.dump(self.term_frequencies, f)

    def load(self) -> None:
        with open(self.index_path, "rb") as f:
            self.index = pickle.load(f)
        with open(self.docmap_path, "rb") as f:
            self.docmap = pickle.load(f)
        with open(self.term_frequencies_path, "rb") as f:
            self.term_frequencies = pickle.load(f)

def tf_command(doc_id: int, term: str) -> int:
    index: InvertedIndex = InvertedIndex()
    try:
        index.load()
    except FileNotFoundError:
        return 0
    return index.get_tf(doc_id, term)

def search_command(query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> list[dict]:
    index: InvertedIndex = InvertedIndex()
    try:
        index.load()
    except FileNotFoundError:
        print("Inverted index not found. Please run 'build' command first.")
        return []
    seen_docs: set[int] = set()
    results: list[dict] = []
    tokenized_query = tokenize_text(query)
    for token in tokenized_query:
        if token in index.index:
            for doc_id in index.get_documents(token):
                if doc_id not in seen_docs:
                    seen_docs.add(doc_id)
                    results.append(index.docmap[doc_id])
                if len(results) >= limit:
                    break
    return results
    
def preprocess_text(text: str) -> str:
    text: str = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

def tokenize_text(text: str) -> list[str]:
    text: str= preprocess_text(text)
    tokens: list[str] = text.split()
    valid_tokens: list[str] = []
    for token in tokens:
        if token:
            valid_tokens.append(token)
    
    stop_words: list[str] = load_stopwords()
    filtered_words: list[str] = []
    for token in valid_tokens:
        if token not in stop_words:
            filtered_words.append(token)

    stemmer = PorterStemmer()
    stemmed_words: list[str] = []
    for token in filtered_words:
        stemmed_words.append(stemmer.stem(token))

    return stemmed_words

def has_matching_token(query_tokens: list[str], title_tokens: list[str]) -> bool:
    for qt in query_tokens:
        for tt in title_tokens: 
            if qt in tt:
                return True
    return False

def build_command() -> None:
    index: InvertedIndex = InvertedIndex()
    index.build()
    index.save()


def main():
    pass


if __name__ == "__main__":
    main()