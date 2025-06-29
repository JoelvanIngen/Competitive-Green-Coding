# Competitive Green Coding

## Introduction
This project aims to implement a platform where users can submit write code on coding exercises/problems,
where the submissions are graded on their energy usage.
Exercises are created by administrators, and implemented by users in an online code editor.
Grading these submissions, the energy consumption of different coding solutions to a given problem can be compared,
promoting sustainable software development practices.

## Key Features
* On-website code editor
* User authentication and profile management
* Backend-end service for automatically running and grading user submitted code

### For the implemented microservices, please refer to their dedicated README files:
* [Server Interface](server/src/server/README.md)
* [Database Microservice](db/src/db/README.md)

## Getting started

### Prerequisites
* Docker

### Running application
1. Ensure the directory name of this project is `Competitive-Green-Coding` (capital insensitive), otherwise Docker won't run
2. Copy `.env.example` to `.env` in the project root directory, set values as desired, filling empty values
3. Run `scripts/run_prod.sh` to start all services in a production environment
4. Access the website on [localhost:3000](localhost:3000)

### First-time setup
1. Run `scripts/create_admin_user.sh` to create an initial admin user who can elevate permissions of other users
2. Run `scripts/create_test_exercises.sh` to populate the database with initial exercises

## Project structure

### Git root directory
* `/common_python_modules`: Contains Python modules that are shared between back-end services
* `/db`: Contains the Database service
* `/documentation`: Contains documentation on API usage for communication between front-end and back-end
* `/execution_engine`: Contains the back-end service that receives and executes submissions
* `/frontend`: Contains the website that the end user will interact with.
* `/scripts`: Contains Docker helper scripts for development
* `/server`: Contains the interface that handles communication between front-end and back-end
* `/storage-example`: Contains starter files that populate the initial database, and serves as an example of the internal storage directory structure

### Backend services
Each back-end service has a standard lay-out
* `.docker/`: Contains Dockerfiles for different run configurations, such as production, development and CI.
* `scripts/`: Contains auxiliary scripts that are executed inside the Docker container, mostly for testing and initial database population services
* `src/{service}/`: Code for the service itself
* `tests/unit/`: Contains unit tests for the service
* `tests/integration/`: Contains integration tests for the service

### Front-end services

The `frontend/` directory contains the web application built with Next.js and React.

**Main folders:**
- `/app/`: Contains application pages and route-based components that connect to the backend.
- `/components/`: Shared UI components.
- `/lib/`: Utility functions(lofin/register) and API helpers.
- `/public/`: Static assets (images, icons, etc.).
- `/types/`: TypeScript type definitions.
- `/tests/`: End-to-end and setup tests.

**Development workflow:**
- `npm install` — Install dependencies.
- `npm run dev` — Start the development server at [localhost:3000](http://localhost:3000).
- `npm run build` — Build the app for production.

Configuration files like `package.json`, `tsconfig.json`, and `next.config.ts` are used to manage dependencies, TypeScript, and Next.js settings.
## Frontend In-depth

### Frontend App

The `app/` directory is the central piece of the frontend, built using the Next.js App Router. It contains all pages of the website and is organized based on routing, making the structure both intuitive and scalable.

#### Architectural Overview

- **Footer**: Pages that include the common website footer are grouped under the special layout folder `(footer)/`. This ensures layout consistency across major user-facing pages without duplicating layout logic.
- **Route-based structure**: Folders that contain a `page.tsx` file correspond to a routable URL path. These define what’s rendered on that route in the browser.
- **Dynamic routing**: Folders like `[username]` or `[threadId]` enable user-specific or content-specific pages without hardcoding routes.
- **API integration**: API routes under `app/api/` proxy requests to the backend and handle server-side logic.
- **Client components**: The project uses Next.js App Router conventions, separating client-side interactivity using `"use client"` components where necessary. These components handle dynamic behavior like state updates and user interactions (e.g., charts, filters, buttons).

The route-based structure keeps related UI and logic grouped intuitively, making the codebase easy to navigate and extend.

### Session management and middleware

The authentication system uses **JSON Web Tokens (JWT)** for secure session management. When users log in or register, they receive a JWT from the backend containing their user information *(uuid, username, permission level, avatar ID, and expiration time)*.

**Session Management (`lib/session.ts`):**
This module handles all JWT-related operations. When a user successfully authenticates, the JWT is stored in an HTTP-only cookie named "session" with appropriate security settings. The module provides functions to set, retrieve, decrypt, and verify JWTs, as well as log users out by deleting their session cookie. The session automatically expires when the JWT expires, eliminating the need for server-side session storage.

> **Note:** encoding and signing of JWTs is handled by the backend. Therefore `lib/session.ts` is a "read-only" module that can work with the JWT, but is not able to change or create one.

**Route Protection (`middleware.ts`):**
The middleware runs before every request to enforce authentication and authorization rules. It checks the user's JWT from the session cookie and protects routes based on authentication status and permission levels. The middleware handles automatic redirects for unauthorized access attempts. For specific implementation details and route configurations, refer to the `middleware.ts` file.

### Frontend components
The `/components/` folder contains all reusable UI React components. Each file defines a React component that can be imported and used across different pages in the application. This structure enhances modularity and maintainability by keeping UI logic organized and encapsulated. Any changes made to a component here will automatically apply wherever that component is used. The folder includes both Shadcn components and custom-built ones.

### Frontend tests: 
The frontend testing setup is built around **Vitest** and **@testing-library/react** with a **JSDOM** environment, designed for running efficient, browser-like tests on React components and Next.js pages.

**Directory structure and purpose:**

* `/tests/`: Contains test setup files, global mocks, and e2e tests.
* Tests within page directories (e.g., `/app/(footer)/u/[username]/`): Contain component-specific unit tests.

**Main files:**

* `vitest.config.ts`: Configures the Vitest test runner, sets up JSDOM as the testing environment, defines path aliases (`@`), and ensures there is only one React instance through deduplication and aliasing of React dependencies.
* `/tests/setup/vitest.setup.ts`: Contains global setup logic, including global mocks for common browser APIs (e.g., `fetch`) and Jest DOM extensions for improved assertion readability.

**What is tested:**

* Rendering of components and pages with mocked backend API responses.
* Accessibility roles and elements to ensure the UI is compliant and elements are interactable.
* Basic integration tests to ensure that data fetching, component rendering, and user interaction logic (tabs, buttons, and dynamic content) work correctly.

**Current state:**

* The testing infrastructure and environment have been established, allowing for easy addition of new tests.
* Initial tests have been written for the Profile page (`app/(footer)/u/[username]/page.test.tsx`), including checks for data fetching, UI rendering, and interactive elements.

**Test writing workflow:**

1. Place your tests alongside the React component or page you're testing (e.g., `page.test.tsx`).
2. Mock backend API calls using `vitest`'s global mocks or per-test setup.
3. Render components using React Testing Library functions (`render`, `screen`, `act`).
4. Write assertions using built-in Jest matchers and accessibility-aware queries (`getByRole`, `findByText`, etc.).

**Running the tests:**

* Use `npm run test` to execute all frontend tests.

### Frontend lib/api.ts
> This file (frontend/lib/api.ts) serves as the central hub for all client-side API calls in the frontend. It provides a set of organized, reusable functions for interacting with the backend, such as fetching problems, leaderboards, user profiles, authentication, and more.
>
> The API functions are organized by feature for clarity and maintainability. Importantly, by using relative paths (like /api/problems instead of a full URL), these functions allow the frontend to proxy requests through the Next.js server. This means API calls work seamlessly both on the client and during server-side rendering, without hardcoding backend URLs.
>
> To add a new API call, simply add a new function to frontend/lib/api.ts following the existing patterns. This keeps all API logic in one place and ensures consistent error handling and request formatting across the app.

**What APIs are in here?**

- **problemsApi:**
  - `getAllProblems(limit?)`: Fetches all problems from the backend, optionally limited by a number.

- **leaderboardApi:**
  - `postLeaderboard(problemId, firstRow, lastRow)`: Fetches leaderboard data for a specific problem and row range.

- **addProblemAPI:**
  - `addProblem(problemData, token)`: Allows admins to add new problems to the platform (requires authentication token).

- **removeProblemAPI:**
  - `removeProblem(problemData, token)`: Allows admins to remove problems from the platform (requires authentication token).

- **profileApi:**
  - `getUserProfile(username)`: Gets user profile information.
  - `updateProfile(username, updates)`: Updates user profile information.

### Remaining files in frontend
* `.docker`: The `.docker` folder contains the docker files that are responsible for the frontend. The frontend team did not add something to these files. 
* `.next`: The web application is built with Next.js and the `.next` folder contains all the build output and intermediate files that Next.js needs to serve and render the application efficiently. While running `npm run dev`, the `.next` folder is created to store page cache and other features to speed up the development process. If  the `.next` folder is deleted while the project is running, it can lead to errors, and the development server should be restarted. Similarly, during the build process, the `.next` folder is used to store compiled files, and it is essential for the proper functioning of the application.
* `lib/session.ts`: The `lib/session.ts` file creates and assigns JWT cookies to log a user in. This file also contains functions to log an user out, retrieve the user's session, retrieve the user's JWT string and decrypt and verify a JWT.
* `mocks`: The `mocks` folder contains mock data that is used for the frontend if the real data is not available (yet).
* `node_modules` & `package.json`: The `node_modules` folder contains all the dependencies installed via npm. This folder can be regenerated using the `package.json` file.
* `public`: The `publlic` folder contains the images used by the frontend that is not stored in the database.
* `scripts`: The `scripts` folder is meant for scripts that are used by the frontend, but is empty.
* `tests`: The `tests` folder contains tests that are used by the frontend.
* `types`: The `types` folder contains the file where the types of all the API's their JSON's are defined.
* `README.md`: The `README.md` file contains information about how to use Next.js and run the web application.

## Running tests
Start a CI environment using `docker compose -f compose.yml -f compose.ci.yml up --build -d`.
This command will build and start all services in their own container, and set up volumes and networks.

The testable services are _db_handler_, _server_interface_ and _execution_engine_.

* Unit tests can be run using `docker exec [service-name] python -m pytest tests/unit`.
* Integration tests can be run using `docker exec [service-name] python -m pytest tests/integration`.

## Security

### Docker networks
All of our individual services are run in different containers. 
The end user only interacts with the website in the `frontend/` folder.
This website uses server-side rendering, so the end user does not have a method of communicating directly with the back-end services.
The front-end can only communicate with the _server_interface_ module, and does not have access to other back-end services.
This ensures that, even if the website server were to be compromised, it cannot access sensitive data, but can only utilise API endpoints exposed by _server_interface_.

### User-submitted Code Execution
Running user-written code safely is a challenge.
However, we have taken extensive measures to ensure this can be done safely.
Here, we will detail those measures and their impact on security.

#### Implemented security measures
* Docker containers: user code is executed in a separate environment. This ensures that, even if a user writes malicious code, it will only impact the runtime container.
* The user inside the runtime container is non-root.
* All capabilities are dropped (`--cap-drop ALL`)
* No new privileges (`--security-opt="no-new-privileges"`)
* The runtime container has no network access (`--network none`)
* The resources of the runtime container are limited to prevent DoS attacks
  * CPUs are limited to a single logical core
  * RAM usage is limited to 512 MB per container
  * Nproc is limited to 1000 to prevent fork bombs
  * Max file size limit is 1MB
  * Each runtime container has a maximum time before it is forcibly shut down.
* Containers are removed after each run
* Containers are not run in privileged mode, as it would make some aspects of the implementation easier, but it would be a security hole.

#### Future security measures
There are measures we did not have the time or resources for to implement.
They are listed here for completeness, and to provide our vision on security.
* Code analysis
  * Before running the code, we can analyse for library imports or include statements.
  * We can choose to only allow a select set of imports, or even ban them outright.
* Docker-In-Docker (DinD)
  * Currently, Docker containers are executed by the host Docker daemon, as sibling containers of the Execution Engine container.
  * DinD brings security benefits, since the Docker daemon itself would be running in side a container.
  * Ensures that, even if user code manages to control the Docker daemon, that only the runtime daemon would be affected.
* IO using Docker interactions
  * Currently, the test cases input file is read from local storage in the runtime container, and fed into the user program's stdin by the entrypoint bash script.
  * Moving all implementation files and scripts out of the runtime container would remove user knowledge of internal working of our program, and this would make it more difficult to find exploits.
* Separate, remote machine for code execution
  * Having a separate machine for code execution would ensure that, even if the machine were to get compromised, the damage would be limited to the execution host, and malicious actors would have no access to any user data.
* Seccomp profiles
  * Seccomp profiles would allow us to manually blacklist/whitelist syscalls that the user process can make.
  * This would further reduce attack vectors by blocking dangerous (or unnecessary for the coding problem) system calls.
