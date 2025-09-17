# ADR-007: Middle Ground Development Approach

## Status
Accepted

## Context
After establishing the project foundation, we need to balance development speed with production readiness. The challenge is to develop efficiently with small datasets while ensuring the system can scale to handle the full 350,000+ games from IGDB.

## Decision
Implement a **Middle Ground Approach** that:
- **Develops with 10-100 games** for rapid iteration and testing
- **Designs for 350k games** to ensure production scalability
- **Avoids unnecessary re-fetching** through smart data management
- **Maintains end-to-end functionality** at all scales

### Core Principles

1. **Smart Data Management**
   - Use SQLite for development (simple, file-based)
   - Design for PostgreSQL in production (scalable, cloud-native)
   - Implement deduplication via database constraints
   - Track ingestion state to avoid re-fetching

2. **Scalable Pipeline Architecture**
   - Same codebase works for 100 games and 350k games
   - Parameterized limits for different environments
   - Robust error handling and retry logic
   - Memory-efficient batch processing

3. **Development Workflow**
   ```bash
   # Development (100 games)
   python -m data_pipeline.main --limit 100

   # Testing (10k games)
   python -m data_pipeline.main --limit 10000

   # Production (350k games)
   python -m data_pipeline.main --limit 350000
   ```

### Data Management Strategy

```python
class DataManager:
    def __init__(self, db_path="data/games.db"):
        self.db = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        # Simple schema for games
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                summary TEXT,
                genres TEXT,  # JSON string
                platforms TEXT,  # JSON string
                themes TEXT,  # JSON string
                rating REAL,
                rating_count INTEGER,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def save_games(self, games):
        # Upsert - insert or update
        for game in games:
            self.db.execute('''
                INSERT OR REPLACE INTO games
                (id, name, summary, genres, platforms, themes, rating, rating_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (...))
        self.db.commit()
```

### Smart Ingestion Strategy

```python
class SmartIngestion:
    def fetch_if_needed(self, target_count=100):
        current_count = self.data_manager.count_games()

        if current_count >= target_count:
            logger.info(f"✅ Already have {current_count} games, no need to fetch")
            return current_count

        needed = target_count - current_count
        logger.info(f"📥 Need {needed} more games, fetching from IGDB...")

        # Fetch from IGDB
        games = self.igdb.fetch_games_sample(needed)

        # Save to database
        self.data_manager.save_games(games)

        return self.data_manager.count_games()
```

## Rationale

### Why This Approach?

1. **Development Speed**: Working with 100 games allows rapid iteration
2. **Production Readiness**: Same architecture scales to 350k games
3. **Cost Efficiency**: Avoid unnecessary API calls and processing
4. **Data Integrity**: Database constraints prevent duplicates
5. **Flexibility**: Easy to test different scales (100 → 10k → 350k)

### Why Not Other Approaches?

- **File-based storage**: Insufficient for deduplication and querying
- **Full dataset from start**: Too slow for development iteration
- **Complex incremental updates**: Unnecessary complexity for project timeline
- **Cloud-first development**: Too expensive and slow for initial development

## Consequences

### Positive
- ✅ Fast development iteration with small datasets
- ✅ Production-ready architecture from day one
- ✅ No unnecessary re-fetching of data
- ✅ Easy scaling from 100 to 350k games
- ✅ Cost-effective development approach

### Negative
- ❌ Requires database setup (even if lightweight)
- ❌ More complex than simple file storage

### Risks
- **Data Schema Evolution**: Changes to IGDB API might require schema updates
- **Performance at Scale**: Need to monitor performance as dataset grows

## Implementation Plan

1. **Phase 1**: Implement DataManager with SQLite
2. **Phase 2**: Create SmartIngestion to avoid re-fetching
3. **Phase 3**: Build end-to-end pipeline with 100 games
4. **Phase 4**: Test scaling to 10k games
5. **Phase 5**: Production deployment with 350k games

## Success Metrics
- **Development**: Complete pipeline with 100 games in < 1 hour
- **Testing**: Scale to 10k games without code changes
- **Production**: Handle 350k games with acceptable performance
- **Data Integrity**: Zero duplicate games in database
- **Cost**: Minimize unnecessary API calls and processing

## Future Considerations
- **Real-time Updates**: Add incremental update capability if needed
- **Data Versioning**: Implement more sophisticated data versioning
- **Performance Optimization**: Add indexing and query optimization
- **Monitoring**: Add comprehensive monitoring and alerting
