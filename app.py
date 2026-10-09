import logging
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")
logger = logging.getLogger("bookwise")


def load_pickle(filename):
    with open(BASE_DIR / filename, 'rb') as f:
        return pickle.load(f)


popular_df = load_pickle('popular_df.pkl')
pt = load_pickle('pt.pkl')
books = load_pickle('books.pkl')
similarity_scores = load_pickle('similarity_scores.pkl')

# Titles available for recommendations, in pivot-table order (used by autocomplete)
available_books = pt.index.tolist()

# Fallback book cover images for missing posters
FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=600&fit=crop",
    "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=600&fit=crop",
    "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop",
    "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=400&h=600&fit=crop",
    "https://images.unsplash.com/photo-1495640388908-05fa85288e61?w=400&h=600&fit=crop",
    "https://images.unsplash.com/photo-1509021436665-8f07dbf5bf1d?w=400&h=600&fit=crop",
    "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=600&fit=crop"
]


def get_book_image(image_url, index):
    """Return the image URL or a fallback image if the original is missing/invalid"""
    if pd.isna(image_url) or image_url == '' or 'http' not in str(image_url):
        return FALLBACK_IMAGES[index % len(FALLBACK_IMAGES)]
    return image_url


app = FastAPI(title="BookWise", description="Book recommendation system")
templates = Jinja2Templates(directory=BASE_DIR / 'templates')


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    # Get the top 8 most popular books
    top_books = popular_df.head(8)

    # Process images to handle missing ones
    processed_images = []
    for i, image_url in enumerate(top_books['Image-URL-M'].values):
        processed_images.append(get_book_image(image_url, i))

    return templates.TemplateResponse(request, 'index.html', {
        'book_name': list(top_books['Book-Title'].values),
        'image': processed_images,
        'author': list(top_books['Book-Author'].values),
    })


@app.get('/recommend', response_class=HTMLResponse)
def recommend(request: Request):
    return templates.TemplateResponse(request, 'recommend.html', {'data': None, 'message': None})


@app.get('/about', response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(request, 'about.html')


@app.get('/popular')
def popular():
    # Popular books are shown on the home page
    return RedirectResponse(url='/')


@app.get('/get_book_suggestions')
def get_book_suggestions(q: str = ''):
    query = q.strip().lower()
    if len(query) < 2:  # Only search if query is at least 2 characters
        return JSONResponse([])

    # Filter books that start with the query
    suggestions = []
    for book in available_books:
        if book.lower().startswith(query):
            suggestions.append(book)
            if len(suggestions) >= 10:  # Limit to 10 suggestions
                break

    # If no exact matches, search for partial matches
    if len(suggestions) < 5:
        for book in available_books:
            if query in book.lower() and book not in suggestions:
                suggestions.append(book)
                if len(suggestions) >= 10:
                    break

    return JSONResponse(suggestions)


@app.post('/recommend_books', response_class=HTMLResponse)
def recommend_books(request: Request, user_input: Optional[str] = Form(None)):
    # Check if input is empty or None
    if not user_input or user_input.strip() == '':
        return templates.TemplateResponse(request, 'recommend.html', {
            'data': None, 'message': "Please enter a book name"})

    # Check if the book exists in our dataset
    if user_input not in pt.index:
        return templates.TemplateResponse(request, 'recommend.html', {
            'data': None, 'message': f"Book '{user_input}' not found in our database"})

    index = np.where(pt.index == user_input)[0][0]
    distances = similarity_scores[index]
    similar_items = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:9]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))

        # Handle missing images in recommendations
        image_url = list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values)[0]
        processed_image = get_book_image(image_url, len(data))
        item.append(processed_image)

        data.append(item)
    logger.info("Recommendations for %r: %s", user_input, data)
    return templates.TemplateResponse(request, 'recommend.html', {
        'data': data, 'message': None, 'book_name': user_input})


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('app:app', host='127.0.0.1', port=8000, reload=True,
                app_dir=str(BASE_DIR), reload_dirs=[str(BASE_DIR)])
