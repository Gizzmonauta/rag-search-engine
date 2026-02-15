from .search_utils import load_movies, DEFAULT_SEARCH_LIMIT, load_stopwords, PROJECT_ROOT
import string
import os
import pickle
from nltk.stem import PorterStemmer
from collections import defaultdict

class InvertedIndex:
    def __init__(self):
        self.index: dict[str, set[int]] = defaultdict(set)
        self.docmap: dict[int, dict] = {}

    def __add_document(self, doc_id: int, text: str) -> None:
        tokens = tokenize_text(text)
        for token in tokens:
            self.index[token].add(doc_id)

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
        os.makedirs(os.path.join(PROJECT_ROOT, "cache"), exist_ok=True)
        cache_path_index = os.path.join(PROJECT_ROOT, "cache", "index.pkl")
        with open(cache_path_index, "wb") as f:
            pickle.dump(self.index, f)
        cache_path_docmap = os.path.join(PROJECT_ROOT, "cache", "docmap.pkl")
        with open(cache_path_docmap, "wb") as f:
            pickle.dump(self.docmap, f)

def search_movies(query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> list[dict]:
    movies: list[dict] = load_movies()
    results: list[dict] = []
    for movie in movies:
        tokenized_query = tokenize_text(query)
        tokenized_title = tokenize_text(movie["title"])
        if has_matching_token(tokenized_query, tokenized_title):
            results.append(movie)
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

def main():
    query = input("Enter your search query: ")
    results = search_movies(query)


if __name__ == "__main__":
    main()