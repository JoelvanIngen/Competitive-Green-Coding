# FastAPI - SQLite Database Documentation

## Overview

## Database Schema

### User Table
Stores user account information and authentication data.

| Column | SQLite Type | Description | Constraints |
|--------|-------------|-------------|-------------|
| `uuid` | `INTEGER` | Unique user identifier | `PRIMARY KEY` |
| `username` | `TEXT(32)` | User's display name | `NOT NULL, UNIQUE` |
| `email` | `TEXT(64)` | User's email address | `NOT NULL, UNIQUE` |
| `password_hash` | `TEXT` | Hashed password (length varies by algorithm) | `NOT NULL` |

### Problem Table
Contains problem definitions and metadata.

| Column | SQLite Type | Description | Constraints |
|--------|-------------|-------------|-------------|
| `problem_id` | `INTEGER` | Unique problem identifier | `PRIMARY KEY AUTOINCREMENT` |
| `tags` | `INTEGER` | Bitmap for problem categorization | `NOT NULL` |
| `description` | `TEXT(256)` | Problem description | `NOT NULL` |

### Submission Table
Records user submissions for problems with scoring and metadata.

| Column | SQLite Type | Description | Constraints |
|--------|-------------|-------------|-------------|
| `sid` | `INTEGER` | Submission identifier | `PRIMARY KEY AUTOINCREMENT` |
| `problem_id` | `INTEGER` | Reference to problem | `NOT NULL, FOREIGN KEY` |
| `uuid` | `INTEGER` | Reference to user | `NOT NULL, FOREIGN KEY` |
| `score` | `INTEGER` | Points awarded for submission | `NOT NULL` |
| `timestamp` | `INTEGER` | Unix timestamp of submission | `NOT NULL` |
| `successful` | `INTEGER` | Boolean flag (0/1) for success | `NOT NULL` |

## Relationships
### https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/define-relationships-attributes/#what-are-these-relationship-attributes

- **User ↔ Submission**: One-to-Many (One user can have multiple submissions)
- **Problem ↔ Submission**: One-to-Many (One problem can have multiple submissions)


## API

## SQLite-Specific Notes

