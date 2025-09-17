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
Implement **SQLite-Only** approach with **Smart Ingestion** and **Pipeline State Tracking**.

### Data Storage Strategy
```python
# Development: SQLite
# Production: SQLite + Cloud Storage Backup

class DataPipeline:
    def __init__(self, db_path="data/games.db"):
        self.db = sqlite3.connect(db_path)  # SQLite only
        self.storage = CloudStorage()  # GCP Cloud Storage for backup
```

### Why SQLite-Only?
- **350,000 games** is not "big data" - SQLite handles this easily
- **Simple queries** (filter, sort, search) - SQLite is optimized for this
- **Single-server deployment** - web app and database on same server
- **Cost-effective** - $0 database costs vs $50-200/month for PostgreSQL
- **Development simplicity** - no database server to manage

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

### Smart Ingestion Strategy
```python
def smart_ingest(self, target_count=100):
    # 1. Check current database count
    current_count = self.db.count_games()

    if current_count >= target_count:
        logger.info(f"✅ Already have {current_count} games, no need to fetch")
        return current_count

    # 2. Calculate how many more games needed
    needed = target_count - current_count
    logger.info(f"📥 Need {needed} more games, fetching from IGDB...")

    # 3. Fetch from IGDB with rate limiting
    games = self.igdb.fetch_games_sample(needed)

    # 4. Save to SQLite (automatic deduplication via PRIMARY KEY)
    self.db.save_games(games)

    # 5. Return new count
    return self.db.count_games()
```

## Rationale

### Why SQLite-Only?
- **Simplicity**: File-based database, no server management
- **Performance**: <1ms queries for 350k games with proper indexing
- **Cost**: $0 database costs vs $50-200/month for PostgreSQL
- **Portability**: Database file can be easily backed up and moved
- **Development**: Perfect for single-developer projects

### Why Smart Ingestion?
- **Avoid Re-fetching**: Check database count before fetching
- **Rate Limit Compliance**: Respects IGDB's 4 req/s limit
- **Cost Optimization**: Reduces unnecessary API calls
- **Flexibility**: Easy to scale from 100 to 350k games

### Why Pipeline State Tracking?
- **Reliability**: Know which games are processed
- **Resumability**: Restart pipeline from last checkpoint
- **Monitoring**: Track pipeline performance and errors
- **Debugging**: Identify where pipeline fails

## Consequences

### Positive
- ✅ Automatic deduplication via PRIMARY KEY constraints
- ✅ Smart ingestion avoids unnecessary re-fetching
- ✅ Reliable pipeline state management
- ✅ Easy data querying and analysis
- ✅ Zero database infrastructure costs
- ✅ Simple backup (copy SQLite file)
- ✅ Perfect for single-server deployment

### Negative
- ❌ Limited concurrent write access (not needed for our use case)
- ❌ No network access (not needed - same server as web app)
- ❌ File-based (requires file system access)

### Risks
- **Concurrent Writes**: SQLite locks database during writes (mitigated by offline ingestion)
- **File Corruption**: SQLite file corruption (mitigated by regular backups)
- **Performance**: Large dataset queries (mitigated by proper indexing)
- **Scaling**: If we need >100 concurrent users (migration path to PostgreSQL available)

## Implementation Plan

### Phase 1: SQLite Database Setup
```python
# Create SQLite database schema
# Implement DataManager class with SQLite
# Add proper indexing for performance
# Test with small dataset (100 games)
```

### Phase 2: Smart Ingestion
```python
# Implement smart ingestion logic
# Add re-fetching avoidance
# Test with multiple ingestion runs
# Validate data integrity and deduplication
```

### Phase 3: Pipeline State Management
```python
# Add processing_status tracking
# Implement checkpoint system
# Add monitoring and logging
# Test pipeline resumability
```

### Phase 4: Production Deployment
```python
# Deploy SQLite database to production
# Add Cloud Storage backup automation
# Implement monitoring and alerting
# Add data quality checks
# Create migration path to PostgreSQL if needed
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
- **Migration Path**: Easy migration to PostgreSQL if scaling needed
- **Real-time Updates**: Webhook integration with IGDB
- **Data Versioning**: Track changes over time
- **Analytics**: Data quality dashboards
- **Backup Strategy**: Automated SQLite file backup to Cloud Storage
- **Performance Optimization**: SQLite indexing and query optimization

## Migration Path to PostgreSQL
If we encounter SQLite limitations:
```python
# Migration script: SQLite → PostgreSQL
def migrate_to_postgresql():
    # 1. Export SQLite data
    sqlite_data = export_sqlite_data()

    # 2. Create PostgreSQL schema
    create_postgresql_schema()

    # 3. Import data to PostgreSQL
    import_to_postgresql(sqlite_data)

    # 4. Update DataManager to use PostgreSQL
    # 5. Deploy with PostgreSQL connection
```

## Success Metrics
- **Deduplication**: 0% duplicate games in database
- **Smart Ingestion**: <5% redundant API calls
- **Pipeline Reliability**: >99% successful ingestion runs
- **Data Quality**: >95% games with complete required fields
- **Performance**: <1ms for simple queries, <100ms for complex queries
- **Cost**: $0 database costs (vs $50-200/month for PostgreSQL)
