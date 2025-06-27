# FastAPI – SQLite Database Documentation

## Overview
The DB microservice uses FastAPI together with SQLModel to manage a local SQLite database (`database.db`). Models are defined in `/db/models/db_schemas.py`, the engine is built in `/db/engine/builder.py`, and endpoints in `/db/api/endpoints.py`. On startup, tables are created automatically via `SQLModel.metadata.create_all()`.

## Database Schema

### User Table
Stores account and authentication information.

| Column             | SQLite Type | Description                                   | Constraints                    |
|--------------------|-------------|-----------------------------------------------|--------------------------------|
| `uuid`             | `TEXT`      | Unique user identifier (UUIDv4)               | `PRIMARY KEY`                  |
| `username`         | `TEXT`      | User’s display name                           | `NOT NULL, UNIQUE`             |
| `email`            | `TEXT`      | User’s email address                          | `NOT NULL, UNIQUE`             |
| `hashed_password`  | `BLOB`      | Hashed password                               | `NOT NULL`                     |
| `permission_level` | `TEXT`      | Enum: user’s permission level (e.g. ADMIN)    | `NOT NULL`                     |
| `private`          | `INTEGER`   | Opt-out of public leaderboard (0 = false, 1)  | `NOT NULL, DEFAULT 0`          |
| `avatar_id`        | `INTEGER`   | Index of chosen avatar                        | `NOT NULL, DEFAULT 0`          |

### Problem Table
Holds problem definitions and metadata.

| Column             | SQLite Type | Description                                    | Constraints               |
|--------------------|-------------|------------------------------------------------|---------------------------|
| `problem_id`       | `INTEGER`   | Unique problem identifier                      | `PRIMARY KEY`             |
| `name`             | `TEXT`      | Problem title                                  | `NOT NULL`                |
| `language`         | `TEXT`      | Enum: default language for templates           | `NOT NULL`                |
| `difficulty`       | `TEXT`      | Enum: EASY, MEDIUM, HARD                       | `NOT NULL`                |
| `short_description`| `TEXT`      | Brief summary                                  | `NOT NULL`                |
| `long_description` | `TEXT`      | Full problem statement                         | `NOT NULL`                |

### ProblemTag Table
Maps problems to tags (many-to-one).

| Column       | SQLite Type | Description                  | Constraints                                    |
|--------------|-------------|------------------------------|------------------------------------------------|
| `problem_id` | `INTEGER`   | FK → `ProblemEntry.problem_id` | `PRIMARY KEY`, `FOREIGN KEY ON DELETE CASCADE` |
| `tag`        | `TEXT`      | Single tag value             | `PRIMARY KEY`                                  |

### Submission Table
Tracks each code submission and its results.

| Column              | SQLite Type | Description                                            | Constraints                                    |
|---------------------|-------------|--------------------------------------------------------|------------------------------------------------|
| `submission_uuid`   | `TEXT`      | Unique submission identifier (UUIDv4)                  | `PRIMARY KEY`                                  |
| `problem_id`        | `INTEGER`   | FK → `ProblemEntry.problem_id`                         | `NOT NULL, FOREIGN KEY ON DELETE CASCADE`      |
| `user_uuid`         | `TEXT`      | FK → `UserEntry.uuid`                                  | `NOT NULL, FOREIGN KEY ON DELETE CASCADE`      |
| `language`          | `TEXT`      | Language used (enum)                                   | `NOT NULL`                                     |
| `runtime_ms`        | `REAL`      | Execution time in milliseconds                         | `NOT NULL, DEFAULT 0.0`                        |
| `emissions_kg`      | `REAL`      | CO₂ emissions estimate                                 | `NOT NULL, DEFAULT 0.0`                        |
| `energy_usage_kwh`  | `REAL`      | Energy used                                           | `NOT NULL, DEFAULT 0.0`                        |
| `timestamp`         | `REAL`      | Unix timestamp when submission was received            | `NOT NULL`                                     |
| `executed`          | `INTEGER`   | Flag indicating execution occurred (0/1)               | `NOT NULL, DEFAULT 0`                          |
| `successful`        | `INTEGER`   | Flag for correct solution (0/1)                        | `NULLABLE`                                     |
| `error_reason`      | `TEXT`      | Enum: reason for failure, if any                       | `NULLABLE`                                     |
| `error_msg`         | `TEXT`      | Detailed error message from execution                  | `NULLABLE`                                     |

## Relationships
- **User ↔ Submission**: One-to-Many  
- **Problem ↔ Submission**: One-to-Many  
- **Problem ↔ ProblemTag**: One-to-Many  

## API

| Method | Path                             | Description                                      | Auth Required |
|--------|----------------------------------|--------------------------------------------------|---------------|
| `POST` | `/auth/register`                 | Register a new user                              | No            |
| `POST` | `/auth/login`                    | Authenticate and receive JWT                     | No            |
| `PUT`  | `/settings`                      | Update user profile                              | Yes (JWT)     |
| `GET`  | `/settings`                      | Retrieve current user info                       | Yes (JWT)     |
| `POST` | `/framework`                     | Download language framework archive              | No            |
| `POST` | `/leaderboard`                   | Fetch leaderboard for a problem                  | No            |
| `POST` | `/problems/all`                  | List all problems metadata                       | No            |
| `GET`  | `/problems/{problem_id}`         | Get detailed problem (with user’s last code)     | Yes (JWT)     |
| `POST` | `/submission`                    | Create a new submission entry                    | No            |
| `GET`  | `/submission/{problem_id}/{user_uuid}` | Retrieve most recent submission                   | No            |
| `POST` | `/submission-result`             | Fetch execution result for a submission          | Yes (JWT)     |
| `POST` | `/write-submission-result`       | (Dev) Append execution result to submission      | No            |
| `POST` | `/admin/add-problem`             | Create a new problem (admin only)                | Yes (JWT)     |
| `POST` | `/admin/change-permission`       | Change a user’s permission level (admin only)    | Yes (JWT)     |
| `POST` | `/admin/remove-problem`          | Remove an existing problem (admin only)          | Yes (JWT)     |
| `GET`  | `/health`                        | Health check                                     | No            |

## SQLite-Specific Notes
- **File Location**: `database.db` in the service root.  
- **Concurrency**: Uses `connect_args={"check_same_thread": False}` for multithreading in FastAPI.  
- **Foreign Keys**: Ensure `PRAGMA foreign_keys = ON` if using raw SQLite clients.  
- **Journaling**: Default `DELETE` mode; consider `WAL` for higher write throughput.  
- **Migrations**: No built-in migration tool—dropping and recreating tables via `SQLModel.metadata.create_all()` may erase data. Consider external tools (Alembic) for production.  
- **Limits**: SQLite holds all data in a single file—monitor file size and backups accordingly.
