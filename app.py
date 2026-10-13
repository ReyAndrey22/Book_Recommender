from flask import Flask, render_template, request
from models.recommender import available_titles, recommend_book 

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = None
    selected_title = None
    
    if request.method == 'POST':
        selected_title = request.form.get('book_title')
        
        if selected_title and selected_title in available_titles:
            
            recommendations = recommend_book(selected_title) 
        elif selected_title:
            
            recommendations = []
            
    return render_template('index.html', 
                           book_titles=available_titles, 
                           recommendations=recommendations,
                           selected_title=selected_title)

if __name__ == '__main__':
    print("--- Pornirea Serverului Flask ---")
    app.run(debug=True)