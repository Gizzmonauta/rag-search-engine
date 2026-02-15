from .search_utils import load_movies, DEFAULT_SEARCH_LIMIT, load_stopwords
import string

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

    return filtered_words

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