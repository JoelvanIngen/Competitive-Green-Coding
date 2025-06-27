## Server Interface
The Server Interface acts as the gateway between the frontend application and our backend services (Database service and Execution Engine). Built with FastAPI, it validates incoming requests using Pydantic schemas, applies authentication and authorization via OAuth2, and forwards calls to the appropriate microservice endpoints. This separation ensures that the frontend never interacts directly with core services, maintaining clear functionality and security.

### Key Features
* Authentication & Authorization
  * OAuth2 Password Bearer (JWT) for protected routes
  * Public endpoints for login, registration and health checks
* Request Proxying
  * Centralized `db_request` wrapper for all calls to the Database service
  * Integrated with Execution engine for code execution
* Pydantic Validation
  * Strict request and response models defined in `common/schemas.py`
  * Automatic request parsing and error handling
* Environment-Based
  * We seperate dev-only endpoints through `endpoints_dev.py`

### Structure
#### `/api/actions.py`:
* Contains functions that build and forward requests to the Database service via `db_request` such as formating payloads for code execution and submission tracking.
#### `/api/config.py`:
* Centralizes all runtime settings, all server interface modules import `settings` to read environment variables.
#### `/api/endpoints.py`:
FastAPI router definitions, organized by feature
| **Feature**                   | **Endpoints**                                                        |
|-------------------------------|----------------------------------------------------------------------|
| **Auth**                      | `/auth/login`, `/auth/register`                                      |
| **User Settings & Profile**   | `/settings`, `/profile/{username}`                                   |
| **Problems**                  | `/problems/all`, `/problem`                                          |
| **Submissions**               | `/submission`, `/submission-result`                                  |
| **Leaderboard**               | `/leaderboard`                                                       |
| **Admin**                     | `/admin/add-problem`, `/admin/change-permission`, `/admin/remove-problem` |
| **Health Check**              | `/health`                                                            |
