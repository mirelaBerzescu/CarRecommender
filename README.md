
# Car Recommendation System using NLP and Hybrid Retrieval

## Project Overview

This project presents the design and implementation of an intelligent **car recommendation system** that leverages **Natural Language Processing (NLP)** and **machine learning techniques** to assist users in identifying suitable vehicles based on natural language queries.

The main goal of the application is to simplify the process of searching for a car by allowing users to describe their desired vehicle using natural language (e.g., preferred brand, price range, mileage, transmission type, etc.). The system then processes the query and returns the **top 5 most relevant vehicle recommendations** from the dataset.

This approach eliminates the need for users to manually browse large inventories or consult multiple sales representatives, providing a more efficient and user-friendly search experience.

---

# Dataset

The dataset used in this project was obtained from Kaggle:

https://www.kaggle.com/datasets/taeefnajib/used-car-price-prediction-dataset

The dataset contains **4008 entries of used cars** and includes the following attributes:

- Brand
- Model
- Year of manufacture
- Mileage (km driven)
- Fuel type
- Transmission type
- Exterior color
- Interior color
- Accident history
- Price

These attributes provide both **structured information** and **textual information**, making the dataset suitable for building a hybrid recommendation system.

---

# Data Preprocessing

The first stage of the project involved **data exploration and preprocessing**.

### Handling missing values

The dataset was inspected for missing values and anomalous data. Missing entries were handled to ensure they do not negatively affect the recommendation process.

### Feature normalization

Several features were normalized to ensure consistency:

- **Price** and **mileage** were converted from strings to numeric values.
- **Transmission types** were standardized to:
  - Automatic
  - Manual
- **Fuel types** were normalized to:
  - Petrol
  - Diesel
  - Hybrid
- **Accident history** was converted into a binary feature.

### Description Feature

A new **description column** was created by concatenating multiple vehicle attributes such as:

- brand
- model
- fuel type
- transmission
- mileage
- price
- interior color
- exterior color

This textual representation allows the system to perform **semantic similarity search**.

---

# Exploratory Data Analysis

Several visualizations were generated to better understand the dataset.

Key observations:

- Approximately **3000 vehicles have no accident history**, while **1000 vehicles have accident records**.
- Vehicles without accidents generally have **higher prices**.
- **Hybrid vehicles** tend to be more expensive than **diesel vehicles**, which are typically more expensive than **petrol vehicles**.

These insights helped validate the dataset distribution.

---

# Query Understanding and Filtering

A query-processing function using **regular expressions (regex)** extracts structured constraints from user queries.

Detected constraints include:

- price limits
- mileage constraints
- transmission type
- fuel type
- vehicle brand

These constraints are used to **filter the dataset before retrieval**, reducing the search space and improving accuracy.

---

# Hybrid Retrieval Architecture

The recommendation system uses a **hybrid retrieval pipeline** consisting of:

1. Semantic Search
2. Keyword-based Search
3. Cross-Encoder Reranking

### Semantic Search

Semantic similarity is computed using the Sentence Transformer model:

`all-MiniLM-L6-v2`

This model converts car descriptions and queries into embeddings for semantic comparison.

---

### Keyword Search

A **TF-IDF model** is used to capture keyword-based similarity between queries and car descriptions.

---

### Hybrid Scoring

The system combines both retrieval strategies:

- Semantic similarity: **75%**
- Keyword similarity: **25%**

The hybrid retrieval returns the **top 20 candidate vehicles**.

---

### Cross-Encoder Reranking

A **Cross-Encoder model**

`cross-encoder/ms-marco-MiniLM-L-6-v2`

reranks the top candidates by directly evaluating the relevance between the query and the candidate descriptions.

The final output consists of the **top 5 recommended vehicles**.

---

# Evaluation

To evaluate system performance, a **golden test dataset** of **10 queries** was created with expected results.

Performance comparison:

| Method | Accuracy |
|------|------|
| Keyword search | 40% |
| Semantic search | 50% |
| Hybrid search + Cross Encoder | **90%** |

The hybrid approach significantly improved recommendation quality.

---

# Model Persistence

Trained models and artifacts were serialized using **Pickle**.

Stored artifacts:

- TF-IDF vectorizer
- Sentence embeddings
- Processed dataset

This enables fast inference without retraining.

---

# System Architecture

The system follows a **client-server architecture**.

### Backend

The backend is implemented using **FastAPI**, exposing an API endpoint for recommendations.

### Frontend

The user interface was developed using **React**, allowing users to submit natural language queries.

---

# Running the Project

## Install dependencies

```
pip install -r requirements.txt
```

## Run notebooks

```
cd notebooks
jupyter notebook
```

Run all three notebooks in order.

## Start backend

```
uvicorn app:app --reload
```

## Start frontend

```
cd car-ui/src
npm start
```

---

# Conclusion

This project demonstrates how **natural language processing and hybrid retrieval techniques** can be combined to build an effective recommendation system.

The architecture integrates:

- structured filtering
- semantic embeddings
- keyword similarity
- neural reranking

This approach significantly improves recommendation relevance compared to traditional search methods.
