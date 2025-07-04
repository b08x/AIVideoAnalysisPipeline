# subtitle_processor/topic_extractor.py
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import logging
from subtitle_processor.models import Utterance, Topic
from subtitle_processor.summarizer import summarize_text

# Set up logging
logger = logging.getLogger(__name__)

# Load a pre-trained model for sentence embeddings
# This model is downloaded once and cached.
logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("SentenceTransformer model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load SentenceTransformer model: {e}")
    raise

def extract_topics(utterances: List[Utterance], num_topics: int = 5) -> List[Topic]:
    """
    Extracts topics from a list of utterances using sentence embeddings and K-Means clustering.
    """
    logger.info(f"Starting topic extraction for {len(utterances)} utterances")
    
    if not utterances:
        logger.warning("No utterances provided for topic extraction")
        return []

    try:
        # Generate embeddings for each utterance text
        logger.info("Extracting text from utterances...")
        texts = [u.text for u in utterances]
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        
        embeddings = model.encode(texts, show_progress_bar=False)
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")

        # Perform K-Means clustering
        # Ensure num_topics is not greater than the number of utterances
        actual_num_topics = min(num_topics, len(utterances))
        logger.info(f"Performing K-Means clustering with {actual_num_topics} clusters...")
        
        kmeans = KMeans(n_clusters=actual_num_topics, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(embeddings)
        logger.info(f"K-Means clustering completed, labels: {len(labels)}")

        # Group utterances by topic
        logger.info("Grouping utterances by topic...")
        topics_data = {i: [] for i in range(actual_num_topics)}
        for i, label in enumerate(labels):
            topics_data[label].append(i)
        
        logger.info(f"Grouped utterances into {len(topics_data)} topics")

        # Create Topic objects
        topics = []
        logger.info("Creating topic objects with AI-generated names...")
        
        for topic_id, utterance_indices in topics_data.items():
            logger.info(f"Processing topic {topic_id} with {len(utterance_indices)} utterances...")
            
            topic_texts = " ".join([utterances[i].text for i in utterance_indices])
            logger.debug(f"Topic {topic_id} text length: {len(topic_texts)} characters")
            
            # Summarize the topic from its constituent texts
            logger.info(f"Generating AI summary for topic {topic_id}...")
            try:
                topic_name = summarize_text(topic_texts, model="anthropic/claude-3-haiku")
                logger.info(f"Topic {topic_id} name generated: {topic_name[:50]}...")
            except Exception as e:
                logger.error(f"Failed to generate name for topic {topic_id}: {e}")
                topic_name = f"Topic {topic_id + 1}"
            
            topics.append(Topic(
                topic_id=topic_id,
                topic_name=topic_name,
                utterance_indices=utterance_indices
            ))
            logger.info(f"Topic {topic_id} created successfully")
        
        logger.info(f"Topic extraction completed successfully. Generated {len(topics)} topics")
        return topics
        
    except Exception as e:
        logger.error(f"Error during topic extraction: {e}")
        raise

