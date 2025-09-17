# ADR-004: ML Strategy and Data Approach

## Status
Accepted

## Context
Need to choose ML approach and data strategy for game recommendation system. Key constraints:
- No user data available (no authentication/history)
- Need fast inference for web app
- Limited development time and resources
- Must work with IGDB API data structure

## Decision
Implement **Content-Based Filtering** with **Stratified Sampling** for development dataset.

### ML Approach: Content-Based Filtering
```python
# Primary recommendation method
recommendations = cosine_similarity(game_features, target_game_features)
```

### Data Strategy: Stratified Sampling
```python
# Development dataset (2000 games)
sampling_strategy = {
    'genres': 200_per_major_genre,    # Action, RPG, Strategy, Adventure
    'platforms': 100_per_platform,    # PC, PS4, Xbox One, Switch
    'eras': 50_per_decade,            # 2010s, 2020s, etc.
    'rating_range': balanced_spread   # High, medium, low rated
}
```

### Feature Priority (ML Performance Based)
1. **Genre Features** - High impact, fast training
2. **Text Description** - High impact, slower training
3. **Platform Features** - Medium impact, fast training
4. **Theme Features** - Medium impact, medium training

## Rationale

### Why Content-Based Filtering?
- **No Cold Start Problem**: Works immediately without user data
- **Interpretable**: Can explain why games are recommended
- **Fast Inference**: Suitable for web app performance
- **Scalable**: Easy to add new games
- **IGDB Data Compatible**: Works well with available data

### Why Stratified Sampling?
- **Representative Sample**: Avoids bias from "top games only"
- **Genre Balance**: Ensures all major genres included
- **Platform Diversity**: Tests cross-platform recommendations
- **Temporal Spread**: Includes games from different eras
- **Development Speed**: 2000 games train in 2-5 minutes

### Why This Feature Priority?
- **Genre**: Strongest signal for game preferences
- **Text**: Captures nuanced preferences but slower training
- **Platform**: Practical constraint (PC vs Console)
- **Theme**: Atmospheric preferences, medium impact

## Consequences

### Positive
- ✅ Fast development and iteration
- ✅ No user data dependency
- ✅ Interpretable recommendations
- ✅ Good performance on limited hardware
- ✅ Easy to scale to full dataset

### Negative
- ❌ No personalization (user-specific preferences)
- ❌ Limited to content similarity
- ❌ May miss cross-genre recommendations
- ❌ Requires good feature engineering

### Risks
- **Feature Quality**: Poor features = poor recommendations
- **Data Bias**: Stratified sampling may not capture all patterns
- **Scalability**: Need to test with full dataset (350k games)

## Implementation Plan

### Phase 1: Minimal Features
```python
features = {
    'genres': one_hot_encoding,      # High impact, fast training
    'platforms': multi_hot_encoding, # Medium impact, fast training
    'ratings': numerical             # Medium impact, fast training
}
```

### Phase 2: Add Text Features
```python
features.update({
    'description': tfidf_vectors,    # High impact, slower training
    'themes': one_hot_encoding      # Medium impact, medium training
})
```

### Phase 3: Advanced Features
```python
features.update({
    'description_embeddings': sentence_transformers,  # High impact, slow training
    'genre_combinations': custom_features,           # Medium impact, medium training
    'company_reputation': numerical                  # Low impact, fast training
})
```

## Future Considerations
- **Hybrid Approach**: Add collaborative filtering when user data available
- **Deep Learning**: Consider neural networks for complex feature interactions
- **Real-time Updates**: Incremental model updates for new games
- **A/B Testing**: Compare different recommendation strategies

## Success Metrics
- **Development**: >70% recommendation accuracy on test set
- **Performance**: <200ms API response time
- **Training**: <5 minutes for 2000 games
- **Scalability**: Successful training on full 350k dataset
