from flask import Flask, render_template, request
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)



# Absolute path example
data = pd.read_csv("recipe_cleaned.csv")
data = data.drop(columns='Unnamed: 0')

# Preprocess Ingredients
vectorizer = TfidfVectorizer()
X_ingredients = vectorizer.fit_transform(data['ingredients_list'][:30000])

# Normalize Numerical Features
scaler = StandardScaler()
X_numerical = scaler.fit_transform(data[['calories(in kcal)','protein(in PDV)', 'minutes', 'n_steps']][:30000])
# Combine Features
X_combined = np.hstack([X_numerical, X_ingredients.toarray()])

# Train KNN Model
knn = NearestNeighbors(n_neighbors=3, metric='euclidean')
knn.fit(X_combined)

# Function to Recommend Recipes
def recommend_recipes(input_features):
    input_features_scaled = scaler.transform([input_features[:4]])
    input_ingredients_transformed = vectorizer.transform([input_features[4]])
    input_combined = np.hstack([input_features_scaled, input_ingredients_transformed.toarray()])
    distances, indices = knn.kneighbors(input_combined)
    recommendations = data.iloc[indices[0]]
    return recommendations[['recipe_name', 'ingredients_list', 'precedure_steps', 'description']]



# from sklearn.metrics.pairwise import cosine_similarity

# # Function to Recommend Recipes Using Cosine Similarity
# def recommend_recipes(input_features):
#     # Scale and transform the input features
#     input_features_scaled = scaler.transform([input_features[:4]])
#     input_ingredients_transformed = vectorizer.transform([input_features[4]])
#     input_combined = np.hstack([input_features_scaled, input_ingredients_transformed.toarray()])
    
#     # Compute cosine similarity
#     similarities = cosine_similarity(input_combined, X_combined)
    
#     # Get top 3 recommendations
#     top_indices = np.argsort(similarities[0])[-3:][::-1]  # Get indices of top 3 similar items
#     recommendations = data.iloc[top_indices]
    
#     return recommendations[['recipe_name', 'ingredients_list', 'precedure_steps', 'description']]


# Function to truncate product name
def truncate(text, length):
    if len(text) > length:
        return text[:length] + "..."
    else:
        return text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        calories = float(request.form['calories'])
        protein = float(request.form['protein'])
        ingredients = request.form['ingredients']

        minutes = float(request.form['minutes'])
        n_steps = float(request.form['n_steps'])

        input_features = [calories, protein, minutes, n_steps, ingredients]
        recommendations = recommend_recipes(input_features)
        return render_template('index.html', recommendations=recommendations.to_dict(orient='records'),truncate = truncate)
    return render_template('index.html', recommendations=[])

if __name__ == '__main__':
    app.run(debug=True)
