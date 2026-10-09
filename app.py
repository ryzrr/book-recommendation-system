from flask import Flask
from flask import request,render_template,jsonify
import pandas as pd
import pickle
import numpy as np

popular_df=pickle.load(open('popular_df.pkl','rb'))
pt=pickle.load(open('pt.pkl','rb'))
books=pickle.load(open('books.pkl','rb'))
similarity_scores=pickle.load(open('similarity_scores.pkl','rb'))

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

app=Flask(__name__)

@app.route('/')
def index():
    # Get the top 8 most popular books
    top_books = popular_df.head(8)
    
    # Process images to handle missing ones
    processed_images = []
    for i, image_url in enumerate(top_books['Image-URL-M'].values):
        processed_images.append(get_book_image(image_url, i))
    
    return render_template('index.html',
        book_name=list(top_books['Book-Title'].values),
        image=processed_images,
        author=list(top_books['Book-Author'].values))
    

@app.route('/recommend')
def recommend():
    return render_template('recommend.html', data=None, message=None)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/popular')
def popular():
    return render_template('popular.html', popular_books=[])

@app.route('/get_book_suggestions')
def get_book_suggestions():
    query = request.args.get('q', '').strip().lower()
    if len(query) < 2:  # Only search if query is at least 2 characters
        return jsonify([])
    
    # Get all book titles that are available for recommendations (from pt.index)
    available_books = pt.index.tolist()
    
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
    
    return jsonify(suggestions)

@app.route('/recommend_books',methods=['post'])
def recommend_books():
    user_input=request.form.get('user_input')
    
    # Check if input is empty or None
    if not user_input or user_input.strip() == '':
        return render_template('recommend.html', data=None, message="Please enter a book name")
    
    # Check if the book exists in our dataset
    if user_input not in pt.index:
        return render_template('recommend.html', data=None, message=f"Book '{user_input}' not found in our database")
    
    index=np.where(pt.index==user_input)[0][0]
    distances=similarity_scores[index]
    similar_items=sorted(list(enumerate(distances)),key=lambda x:x[1],reverse=True)[1:9]
    
    data=[]
    for i in similar_items:
        item=[]
        temp_df=books[books['Book-Title']==pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        
        # Handle missing images in recommendations
        image_url = list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values)[0]
        processed_image = get_book_image(image_url, len(data))
        item.append(processed_image)
        
        data.append(item)
    print(data)
    return render_template('recommend.html',data=data, message=None, book_name=user_input)

if __name__=='__main__':
    app.run(debug=True)