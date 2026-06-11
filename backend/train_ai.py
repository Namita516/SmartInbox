import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import os

def train_model():
    if not os.path.exists('train_data.csv'):
        print("Error: train_data.csv not found!")
        return

    # Load with header=0 to ensure the first line is treated as the column names
    df = pd.read_csv('train_data.csv', header=0, encoding='utf-8-sig')
    
    # Strip spaces just in case
    df.columns = df.columns.str.strip()
    
    print(f"DEBUG: Successfully found columns: {df.columns.tolist()}")

    # Use column names directly for clarity
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(df['Text Content'].astype(str)) 
    y = df['Category Label']

    # Train
    model = MultinomialNB()
    model.fit(X, y)

    # Save
    joblib.dump(model, 'email_model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')
    print("✅ Brain updated: Model and Vectorizer saved.")

if __name__ == "__main__":
    train_model()