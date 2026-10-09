# Book Recommendation Project

A FastAPI-based web application that recommends books based on user input, using collaborative filtering and a precomputed similarity matrix.The app also uses a popularity based recommendation model which displays popular books on the home page. The app features autocomplete suggestions, popular books, and robust handling of missing book cover images.

## Features
- Book recommendations based on collaborative filtering
- Autocomplete book title suggestions
- Popular books display
- Large files managed with Git LFS

## Project Structure
```
Book-Recommendation-Project/
├── app.py                  # Main FastAPI application
├── requirements.txt        # Python dependencies
├── Books.csv               # Book metadata (large file, tracked by LFS)
├── Ratings.csv             # User ratings (large file, tracked by LFS)
├── Users.csv               # User data (large file, tracked by LFS)
├── books.pkl               # Pickled book DataFrame (LFS)
├── popular_df.pkl          # Pickled popular books DataFrame (LFS)
├── pt.pkl                  # Pickled pivot table (LFS)
├── similarity_scores.pkl   # Pickled similarity matrix (LFS)
├── templates/              # HTML templates
├── .gitattributes          # Git LFS tracking
└── README.md               # This file
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/Book-Recommendation-Project.git
cd Book-Recommendation-Project
```

### 2. Install Python dependencies
It is recommended to use a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 3. Install Git LFS and pull large files
```bash
git lfs install
git lfs pull
```

### 4. Run the application
```bash
python app.py
```
or, equivalently:
```bash
uvicorn app:app --reload
```
Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Interactive API docs are available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Routes
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Home page with the top 8 popular books |
| GET | `/recommend` | Recommendation search page |
| POST | `/recommend_books` | Form submit (`user_input`); renders 8 similar books |
| GET | `/get_book_suggestions?q=` | Autocomplete JSON (up to 10 titles, min 2 chars) |
| GET | `/about` | About page |
| GET | `/popular` | Redirects to `/` |

## Example Usage
- Go to the homepage to see popular books.
- Use the recommendation page to get book suggestions by typing a book title.
- The app will suggest similar books and display their covers and authors.

## Notes
- This app is for demonstration/educational purposes and runs with auto-reload enabled.
- Large files are managed with Git LFS. Make sure to install LFS before cloning/pulling.

## Credits
- Built by Dhruv
- Book data from [Book-Crossing Dataset](http://www2.informatik.uni-freiburg.de/~cziegler/BX/)

---
Feel free to contribute or open issues for suggestions!