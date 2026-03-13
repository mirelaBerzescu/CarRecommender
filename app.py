from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pickle
from sentence_transformers import SentenceTransformer, CrossEncoder
from utils import recommend_cars


app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    text: str
    top_k: int = 5

# Load artifacts
with open("models/artifacts.pkl", "rb") as f:
    artifacts = pickle.load(f)

df = artifacts["df"]
embeddings = artifacts["embeddings"]
tfidf_vectorizer = artifacts["tfidf_vectorizer"]
tfidf_matrix = artifacts["tfidf_matrix"]

# Load models
bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")
cross_encoder = CrossEncoder("models/cross_encoder_model")

@app.post("/recommend")
def recommend(request: QueryRequest):
    results =  recommend_cars(
        bi_encoder,
        embeddings,
        tfidf_vectorizer,
        tfidf_matrix,
        df,
        cross_encoder,
        request.text,
        request.top_k
    )

    return {
        "query": request.text,
        "results": results
    }