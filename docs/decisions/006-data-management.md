# ADR-006: Data Management and Storage Strategy

## Status
Accepted

## Context
Need to design data management strategy for the IGDB data pipeline that handles:
- Deduplication of games across multiple ingestion runs
- Incremental updates to avoid re-fetching existing data
- Pipeline state management between ingestion, processing, and training
- Data storage strategy for development and production
- Data quality and integrity across pipeline stages

## Decision
Implement **Database-First** approach with **Incremental Ingestion** and **Pipeline State Tracking**.

### Data Storage Strategy
```python
# Development: SQLite
# Production: PostgreSQL + Cloud Storage

class DataPipeline:
    def __init__(self):
        self.db = GameDatabase()  # SQLite/PostgreSQL
        self.storage = CloudStorage()  # GCP Cloud Storage
```

### Database Schema
```sql
-- Games table with IGDB data
CREATE TABLE games (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    summary TEXT,
    genres JSON,
    platforms JSON,
    themes JSON,
    rating REAL,
    rating_count INTEGER,
    first_release_date INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ingestion tracking
CREATE TABLE ingestion_log (
    id INTEGER PRIMARY KEY,
    batch_id TEXT,
    games_fetched INTEGER,
    games_new INTEGER,
    games_updated INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT
);

-- Pipeline state tracking
CREATE TABLE processing_status (
    game_id INTEGER,
    feature_extraction_status TEXT,
    model_training_status TEXT,
    last_processed_at TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games (id)
);
```

### Incremental Ingestion Strategy
```python
def ingest_incremental(self, batch_size=100):
    # 1. Get last sync timestamp
    last_sync = self.db.get_last_sync()

    # 2. Fetch batch from IGDB (sorted by updated_at)
    query = f"""
    fields *;
    where updated_at > {last_sync};
    limit {batch_size};
    sort updated_at asc;
    """

    # 3. Deduplicate and store
    new_games = self._deduplicate_and_store(games)

    # 4. Update sync timestamp
    self.db.update_last_sync()
```

## Rationale

### Why Database-First?
- **Deduplication**: UNIQUE constraints prevent duplicate games
- **Data Integrity**: ACID transactions ensure consistency
- **Query Flexibility**: SQL for complex data operations
- **Pipeline State**: Easy tracking of processing status
- **Incremental Updates**: Efficient WHERE clauses for new data

### Why Incremental Ingestion?
- **Efficiency**: Only fetch new/updated games
- **Rate Limit Compliance**: Respects IGDB's 4 req/s limit
- **Cost Optimization**: Reduces API calls and storage
- **Real-time Updates**: Keep data fresh without full refresh

### Why Pipeline State Tracking?
- **Reliability**: Know which games are processed
- **Resumability**: Restart pipeline from last checkpoint
- **Monitoring**: Track pipeline performance and errors
- **Debugging**: Identify where pipeline fails

## Consequences

### Positive
- ✅ Automatic deduplication via database constraints
- ✅ Efficient incremental updates
- ✅ Reliable pipeline state management
- ✅ Easy data querying and analysis
- ✅ Scalable to production with PostgreSQL
- ✅ Backup and recovery capabilities

### Negative
- ❌ Database dependency (SQLite/PostgreSQL)
- ❌ More complex than file-based approach
- ❌ Requires database schema management
- ❌ Additional infrastructure for production

### Risks
- **Database Locking**: Concurrent access issues
- **Schema Changes**: Migration complexity
- **Data Corruption**: Database integrity issues
- **Performance**: Large dataset query performance

## Implementation Plan

### Phase 1: Database Setup
```python
# Create database schema
# Implement GameDatabase class
# Add ingestion_log tracking
# Test with small dataset
```

### Phase 2: Incremental Ingestion
```python
# Implement incremental fetch logic
# Add deduplication logic
# Test with multiple ingestion runs
# Validate data integrity
```

### Phase 3: Pipeline State Management
```python
# Add processing_status tracking
# Implement checkpoint system
# Add monitoring and logging
# Test pipeline resumability
```

### Phase 4: Production Readiness
```python
# Migrate to PostgreSQL
# Add Cloud Storage backup
# Implement monitoring and alerting
# Add data quality checks
```

## Data Quality Strategy

### Validation Rules
- **Required Fields**: name, summary, genres, platforms
- **Data Types**: Validate JSON fields, numeric ranges
- **Consistency**: Check genre/platform IDs against reference tables
- **Completeness**: Flag games with missing critical data

### Quality Metrics
- **Coverage**: Percentage of games with complete data
- **Freshness**: Age of data vs IGDB updates
- **Accuracy**: Validation against IGDB reference data
- **Completeness**: Missing field analysis

## Future Considerations
- **Real-time Updates**: Webhook integration with IGDB
- **Data Versioning**: Track changes over time
- **Analytics**: Data quality dashboards
- **Backup Strategy**: Automated backup and recovery
- **Performance Optimization**: Indexing and query optimization

## Success Metrics
- **Deduplication**: 0% duplicate games in database
- **Incremental Efficiency**: <10% redundant API calls
- **Pipeline Reliability**: >99% successful ingestion runs
- **Data Quality**: >95% games with complete required fields
- **Performance**: <5 minutes for 1000 game batch processing
