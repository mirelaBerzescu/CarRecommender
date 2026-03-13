
import re
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import util
import numpy as np

def extract_criteria(query):
  criteria = {}
  query_lower = query.lower()

  budget_match = re.search(r"(under|below|less than|max)\s*([\d ,]+)\s*(k)?",
  query_lower,
  re.IGNORECASE
  )

  year_match = re.search(r"\b(19|20)\d{2}\b", query_lower)

  millage_match = re.search(
  r'(\d{1,3}(?:[ ,]?\d{3})?|[1-9]\d?k)\s*(?:km|kilometers)',
  query_lower
  )

  #budget
  if budget_match:
    budget_str = budget_match.group(2).replace(' ', '').replace(',', '')
    budget = int(budget_str)

    if budget_match.group(3):
      budget *= 1000
    criteria['budget'] = budget

  # model year
  if year_match:
    criteria['model_year'] = int(year_match.group())

  # millage
  if millage_match:
    if millage_match:
      millage_str = millage_match.group(1).replace(' ', '').replace(',', '')
    if millage_str.endswith('k'):
      criteria['millage'] = int(millage_str[:-1]) * 1000
    else:
      criteria['millage'] = int(millage_str)

  # Engine size
  engine_match = re.search(r'(\d\.\d)', query_lower)
  if engine_match:
    criteria['engine'] = engine_match.group(1)

  if 'automatic' in query_lower:
    criteria['transmission'] = 'Automatic'
  elif 'manual' in query_lower:
    criteria['transmission'] = 'Manual'

  if 'petrol' in query_lower or 'gasoline' in query_lower:
    criteria['fuel_type'] = 'Petrol'
  elif 'diesel' in query_lower:
      criteria['fuel_type'] = 'Diesel'
  elif 'hybrid' in query_lower:
    criteria['fuel_type'] = 'Hybrid'
  elif 'electric' in query_lower:
    criteria['fuel_type'] = 'Electric'

  if 'accident-free' in query_lower or 'no accident' in query_lower:
    criteria['accident'] = 0

  return criteria



def filter_cars_by_criteria(df, criteria):
  filtered_df = df.copy()

  # Filter by budget
  if 'budget' in criteria:
    filtered_df = filtered_df[filtered_df['price'] <= criteria['budget']]

  # Filter by transmission
  if 'transmission' in criteria:
    filtered_df = filtered_df[filtered_df['transmission'] == criteria['transmission']]

  # Filter by fuel type
  if 'fuel_type' in criteria:
    filtered_df = filtered_df[filtered_df['fuel_type'] == criteria['fuel_type']]

  # Filter by engine
  if 'engine' in criteria:
    filtered_df = filtered_df[filtered_df['engine'].str.startswith(criteria['engine'])]

  # Filter model year
  if 'model_year' in criteria:
    filtered_df = filtered_df[filtered_df['model_year'] == criteria['model_year']]

  # Filter milage
  if 'millage' in criteria:
    filtered_df = filtered_df[filtered_df['milage'] <= criteria['millage']]

  # Filter by accident
  if 'accident' in criteria:
    filtered_df = filtered_df[filtered_df['accident'] == criteria['accident']]

  return filtered_df



def process_query(query):
  query = query.lower().strip()
  return query

def get_car_data(car, score):
  return {'description': car['description'],'brand': car['brand'], 'model': car['model'], 'price': float(car['price']), 'engine': car['engine'], 'model_year': int(car['model_year']), 'fuel_type': car['fuel_type'], 'transmission': car['transmission'], 'milage': int(car["milage"]), 'int_col': car['int_col'], 'ext_col': car['ext_col'], 'score': float(score)}

# add the semantic search function that uses a sentence transformer model
def semantic_car_search(df,model, query, top_k=5):
  results = []
  criteria = extract_criteria(query)
  filtered_df = filter_cars_by_criteria(df, criteria)

  if len(filtered_df) == 0:
    return []

  descriptions_filtered = filtered_df['description'].tolist()
  embeddings_filtered = model.encode(descriptions_filtered, convert_to_tensor=True)

  query_emb = model.encode(query, convert_to_tensor=True)
  cos_scores = util.cos_sim(query_emb, embeddings_filtered)[0]

  top_results = torch.topk(cos_scores, k=min(top_k, len(filtered_df)))
  results = []

  for score, idx in zip(top_results.values, top_results.indices):
    idx = idx.item()
    car = filtered_df.iloc[idx]
    results.append(get_car_data(car, score))

  return results


# add a function that searches by keyword using TF-IDF
def keyword_car_search(vectorizer, tfidf_matrix, query,df, top_k=5):
  results = []
  criteria = extract_criteria(query)
  filtered_df = filter_cars_by_criteria(df, criteria)

  if len(filtered_df) == 0:
    return []

  vector_intrebare = vectorizer.transform([query])
  tfidf_filtered = tfidf_matrix[filtered_df.index]

  # compute cosine similarity between the query vector and the TF-IDF vectors of the filtered cars
  scoruri = cosine_similarity(vector_intrebare, tfidf_filtered)[0]
  indici_top = np.argsort(scoruri)[::-1][:top_k]

  results = []

  for idx in indici_top:
    car = filtered_df.iloc[idx]
    results.append(get_car_data(car, scoruri[idx]))

  return results



def hybrid_retrieval(model, embeddings,vectorizer, tfidf_matrix,query, filtered_df, top_k=20, alpha=0.75):

  filtered_indices = filtered_df.index
  device = "cuda" if torch.cuda.is_available() else "cpu"
  embeddings_filtered = embeddings[filtered_indices]
  tfidf_filtered = tfidf_matrix[filtered_indices]

  # semantic
  query_emb = model.encode([query], convert_to_tensor=True, device=device)
  emb_tensor = torch.tensor(embeddings_filtered, device=device)

  semantic_scores = util.cos_sim(query_emb, emb_tensor)[0].cpu().numpy()

  # keyword
  query_tfidf = vectorizer.transform([query])
  keyword_scores = cosine_similarity(query_tfidf, tfidf_filtered)[0]

  # normalize
  semantic_scores = (semantic_scores - semantic_scores.min()) / (
      semantic_scores.max() - semantic_scores.min() + 1e-9
  )

  keyword_scores = (keyword_scores - keyword_scores.min()) / (
      keyword_scores.max() - keyword_scores.min() + 1e-9
  )

  # hybrid score
  beta = 1 - alpha
  scores = alpha * semantic_scores + beta * keyword_scores

  top_indices = np.argsort(scores)[::-1][:top_k]

  return filtered_df.iloc[top_indices]


def recommend_cars(sentence_model, embeddings, tfidf_vectorizer, tfidf_matrix, df, cross_encoder, query, top_k=5):
  criteria = extract_criteria(query)
  filtered_df = filter_cars_by_criteria(df, criteria)

  if len(filtered_df) == 0:
      return []

  candidates = hybrid_retrieval(sentence_model, embeddings, tfidf_vectorizer, tfidf_matrix, query, filtered_df)
  pairs = [
      (query, desc)
      for desc in candidates["description_norm"]
  ]
  scores = cross_encoder.predict(pairs)
  ranked_indices = np.argsort(scores)[::-1][:top_k]
  cross_encoder_results = candidates.iloc[ranked_indices]
  results = []

  for rank_pos, idx in enumerate(ranked_indices):
    row = cross_encoder_results.iloc[rank_pos]  # row in top results
    score = scores[idx]                   # corresponding score
    results.append(get_car_data(row, float(score)))

  return results