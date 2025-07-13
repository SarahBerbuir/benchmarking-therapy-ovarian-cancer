import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_cosine_similarity(text1: str, text2: str) -> float:
    """
    Calculate the cosine similarity between two text strings.
    :param text1: First text string
    :param text2: Second text string
    :return: Cosine similarity score rounded to 4 decimal places
    """

    if not text1 or not text2:
        return 0.0

    vectorizer = TfidfVectorizer().fit([text1, text2])
    vectors = vectorizer.transform([text1, text2])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(score, 4)

def apply_cosine_similarity(
        df: pd.DataFrame,
        cosine_similarity_col,
        output_col_reco,
        gold_standard_col) -> pd.DataFrame:
    """
    Apply cosine similarity calculation to the DataFrame.
    :param df: DataFrame containing the recommendations and gold standard
    :param cosine_similarity_col: Name of the column to store cosine similarity results
    :param output_col_reco: Column containing the LLM recommendations
    :param gold_standard_col: Column containing the gold standard recommendations
    :return: DataFrame with cosine similarity scores added
    """
    if cosine_similarity_col not in df.columns:
        df[cosine_similarity_col] = 0.0

    for index, row in df.iterrows():
        try:
            reco = str(row[output_col_reco])
            gold = str(row[gold_standard_col])
            similarity = calculate_cosine_similarity(reco, gold)
            df.at[index, cosine_similarity_col] = similarity
        except Exception:
            df.at[index, cosine_similarity_col] = -1.0

    return df