import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import warnings
warnings.filterwarnings('ignore') 

print("--- 1. Încărcarea și Preprocesarea Datelor ---")

try:
    books = pd.read_csv('data/BX-Books.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    books.columns = ['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Image-URL-S', 'Image-URL-M', 'Image-URL-L']
    
    ratings = pd.read_csv('data/BX-Book-Ratings.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    ratings.columns = ['User-ID', 'ISBN', 'Book-Rating']
except FileNotFoundError:
    print("EROARE:'BX-Books.csv' și 'BX-Book-Ratings.csv' nu au fost găsite.")
    exit()


books_df = books[['ISBN', 'Book-Title', 'Book-Author']]

counts = ratings['ISBN'].value_counts()
popular_books_ratings = ratings[ratings['ISBN'].isin(counts[counts >= 50].index)]

user_counts = popular_books_ratings['User-ID'].value_counts()
active_users_ratings = popular_books_ratings[popular_books_ratings['User-ID'].isin(user_counts[user_counts >= 50].index)]

final_ratings = active_users_ratings.merge(books_df, on='ISBN')


book_pivot = final_ratings.pivot_table(index='Book-Title', columns='User-ID', values='Book-Rating')
book_pivot.fillna(0, inplace=True)

print(f"Dimensiunea Matricei Pivot: {book_pivot.shape}")

book_sparse = csr_matrix(book_pivot)
similarity_scores = cosine_similarity(book_sparse)

print("--- 2. Modelul de Similaritate a fost calculat ---")

available_titles = book_pivot.index.tolist()


def recommend_book(book_title, pivot_matrix=book_pivot, similarity_matrix=similarity_scores, k=5):
    
    if book_title not in pivot_matrix.index:
        return []

    
    index = np.where(pivot_matrix.index == book_title)[0][0]
    
    
    similar_items = sorted(list(enumerate(similarity_matrix[index])), key=lambda x: x[1], reverse=True)
    
    recommended_books = []
    
    for i in similar_items:
       
        if i[0] != index and i[1] > 0.1:
            recommended_books.append(pivot_matrix.index[i[0]])
        
        if len(recommended_books) >= k:
            break
            
    final_recs = []
    for title in recommended_books:
        author = books_df[books_df['Book-Title'] == title]['Book-Author'].iloc[0] if not books_df[books_df['Book-Title'] == title]['Book-Author'].empty else 'Necunoscut'
        final_recs.append({'Title': title, 'Author': author})
        
    return final_recs