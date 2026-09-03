import numpy as np

def precision_at_k(recommended_ids, test_relevant_ids, k=10):
    """
    Computes Precision@K: fraction of top-K recommendations that are in the user's relevant test set.
    """
    if not recommended_ids or not test_relevant_ids:
        return 0.0
        
    # Squeeze to top K
    rec_k = recommended_ids[:k]
    
    # Count matches
    matches = len(set(rec_k).intersection(test_relevant_ids))
    return matches / k

def recall_at_k(recommended_ids, test_relevant_ids, k=10):
    """
    Computes Recall@K: fraction of the user's relevant test items that are recommended in the top-K.
    """
    if not recommended_ids or not test_relevant_ids:
        return 0.0
        
    rec_k = recommended_ids[:k]
    matches = len(set(rec_k).intersection(test_relevant_ids))
    
    return matches / len(test_relevant_ids)

def ndcg_at_k(recommended_ids, test_relevant_ids, k=10):
    """
    Computes NDCG@K (Normalized Discounted Cumulative Gain) using binary relevance (1 if in relevant set, 0 otherwise).
    """
    if not recommended_ids or not test_relevant_ids:
        return 0.0
        
    rec_k = recommended_ids[:k]
    
    # Calculate DCG
    dcg = 0.0
    for idx, item in enumerate(rec_k):
        rel = 1.0 if item in test_relevant_ids else 0.0
        dcg += rel / np.log2(idx + 2)  # idx + 2 because idx starts at 0 (rank 1 -> log2(2))
        
    # Calculate IDCG (Ideal DCG)
    # The ideal ranking has all relevant items at the top
    n_relevant = len(test_relevant_ids)
    n_hits = min(n_relevant, k)
    
    idcg = 0.0
    for idx in range(n_hits):
        idcg += 1.0 / np.log2(idx + 2)
        
    if idcg == 0.0:
        return 0.0
        
    return dcg / idcg
