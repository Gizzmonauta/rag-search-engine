from .search_utils import load_movies, DEFAULT_SEARCH_LIMIT
import string

def search_movies(query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> list[dict]:
    movies: list[dict] = load_movies()
    results: list[dict] = []
    for movie in movies:
        preprocessed_query = preprocess_text(query)
        preprocessed_title = preprocess_text(movie["title"])
        if preprocessed_query in preprocessed_title:
            results.append(movie)
            if len(results) >= limit:
                break

    return results

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

def main():
    query = input("Enter your search query: ")
    search_movies(query)


if __name__ == "__main__":
    main()