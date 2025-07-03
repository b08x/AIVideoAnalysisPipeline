# subtitle_processor/topic_extractor.py
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
from models import Utterance, Topic
from summarizer import summarize_text

# Load a pre-trained model for sentence embeddings
# This model is downloaded once and cached.
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_topics(utterances: List[Utterance], num_topics: int = 5) -> List[Topic]:
    """
    Extracts topics from a list of utterances using sentence embeddings and K-Means clustering.
    """
    if not utterances:
        return []

    # Generate embeddings for each utterance text
    texts = [u.text for u in utterances]
    embeddings = model.encode(texts, show_progress_bar=False)

    # Perform K-Means clustering
    # Ensure num_topics is not greater than the number of utterances
    actual_num_topics = min(num_topics, len(utterances))
    kmeans = KMeans(n_clusters=actual_num_topics, random_state=42, n_init='auto')
    labels = kmeans.fit_predict(embeddings)

    # Group utterances by topic
    topics_data = {i: [] for i in range(actual_num_topics)}
    for i, label in enumerate(labels):
        topics_data[label].append(i)

    # Create Topic objects
    topics = []
    for topic_id, utterance_indices in topics_data.items():
        topic_texts = " ".join([utterances[i].text for i in utterance_indices])
        
        # Summarize the topic from its constituent texts
        topic_name = summarize_text(topic_texts, model="anthropic/claude-3-haiku")
        
        topics.append(Topic(
            topic_id=topic_id,
            topic_name=topic_name,
            utterance_indices=utterance_indices
        ))
        
    return topics

