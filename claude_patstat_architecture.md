# PATSTAT Database Architecture Reference

Generated: 2025-09-28 20:20:35
Source: Complete schema export

## Database Information

- **Project ID**: p-epo-tip-prj-3a1f
- **Database Time**: 2025-09-28 18:19:40.711541
- **Tables Discovered**: 66


## Overview

PATSTAT (Patent Statistical Database) consists of two main components:
- **Global Database (TLS Tables)**: 28 tables
- **Register Database (REG Tables)**: 38 tables

## PATSTAT ORM Access Guide

### Initial Setup

```python
# Required imports
from epo.tipdata.patstat import PatstatClient
from epo.tipdata.patstat.database.models import (
    TLS201_APPLN, TLS202_APPLN_TITLE, TLS206_PERSON,
    TLS207_PERS_APPLN, TLS209_APPLN_IPC, TLS211_PAT_PUBLN
)
from sqlalchemy import func, text
```

### Connection Management

```python
# Establish connection
patstat = PatstatClient(env='PROD')
db = patstat.orm()

# Basic query example
query = db.query(TLS201_APPLN.appln_id, TLS201_APPLN.appln_auth).limit(10)
results = query.all()
```

### Proper Session Cleanup

```python
# Method 1: Manual cleanup
try:
    # Your PATSTAT operations here
    results = db.query(TLS201_APPLN).limit(10).all()
finally:
    # Clean close to avoid warnings
    if db:
        db.close()
    if patstat:
        if hasattr(patstat, '_session') and patstat._session:
            patstat._session.close()
        if hasattr(patstat, 'close_session'):
            patstat.close_session()

# Method 2: Context manager (recommended)
class PatstatConnection:
    def __init__(self):
        self.patstat = PatstatClient(env='PROD')
        self.db = self.patstat.orm()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()
        if self.patstat:
            if hasattr(self.patstat, '_session') and self.patstat._session:
                self.patstat._session.close()
            if hasattr(self.patstat, 'close_session'):
                self.patstat.close_session()

# Usage:
with PatstatConnection() as db:
    results = db.query(TLS201_APPLN).limit(10).all()
```

### Common Query Patterns

```python
# Basic application query
apps = db.query(TLS201_APPLN).filter(
    TLS201_APPLN.appln_auth == 'EP',
    TLS201_APPLN.appln_filing_year >= 2020
).limit(100).all()

# Join with person data
app_persons = db.query(
    TLS201_APPLN.appln_id,
    TLS201_APPLN.appln_nr,
    TLS206_PERSON.psn_name
).join(
    TLS207_PERS_APPLN, TLS201_APPLN.appln_id == TLS207_PERS_APPLN.appln_id
).join(
    TLS206_PERSON, TLS207_PERS_APPLN.person_id == TLS206_PERSON.person_id
).filter(
    TLS207_PERS_APPLN.applt_seq_nr > 0  # Applicants only
).limit(100).all()

# Aggregation query
stats = db.query(
    TLS201_APPLN.appln_auth,
    func.count(TLS201_APPLN.appln_id).label('count')
).filter(
    TLS201_APPLN.appln_filing_year >= 2020
).group_by(TLS201_APPLN.appln_auth).all()
```

## Global Database (TLS Tables)

### Core Application Tables
- **tls201_appln**: Patent applications - Main table for all patent applications
  - Sample data: 10 rows available
- **tls202_appln_title**: Application titles in multiple languages
  - Sample data: 10 rows available
- **tls203_appln_abstr**: Application abstracts in multiple languages
  - Sample data: 10 rows available
- **tls204_appln_prior**: Priority relationships between applications
  - Sample data: 10 rows available
- **tls205_tech_rel**: Technical relationships between applications
  - Sample data: 10 rows available
- **tls206_person**: Standardized person/organization data (applicants, inventors)
  - Sample data: 10 rows available
- **tls207_pers_appln**: Person-application relationships (roles)
  - Sample data: 10 rows available
- **tls209_appln_ipc**: IPC (International Patent Classification) codes
  - Sample data: 10 rows available


### Key Statistics
- Total Global Tables: 28
- Total Columns: 235
- Tables with Foreign Keys: 0

## Register Database (REG Tables)

### Key Statistics
- Total Register Tables: 38
- Total Columns: 330
- Tables with Foreign Keys: 0

## Usage Examples

```python
# Load schema data
global_schema = load_schema_from_json('patstat_global_schema.json')
register_schema = load_schema_from_json('patstat_register_schema.json')

# Search for application-related tables
app_tables = search_tables_by_pattern(global_schema, 'appln')

# Find all ID columns
id_columns = search_columns_by_pattern(global_schema, '_id')

# Get foreign key relationships
relationships = extract_foreign_key_relationships(global_schema)

# Access sample data for a table
table_info = global_schema['tables']['tls201_appln']
if 'sample_data' in table_info:
    sample_rows = table_info['sample_data']['sample_rows']
    print(f"Sample data: {len(sample_rows)} rows")
```

## Files Generated
- **patstat_global_schema.json**: Complete TLS table metadata with sample data
- **patstat_register_schema.json**: Complete REG table metadata with sample data
- **claude_patstat_architecture.md**: This documentation file

## Schema File Structure

Each JSON file contains:
- Database version information
- Complete table schemas with column details
- Sample data (10 rows per table) for content analysis
- Foreign key relationships
- Export statistics and metadata

---
*Generated by PATSTAT Schema Exporter*
