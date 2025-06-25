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

## Getting started

### Prerequisites
* Docker

### Running application
1. Ensure the directory name of this project is `Competitive-Green-Coding` (capital insensitive), otherwise Docker won't run
2. Copy `.env.example` to `.env` in the project root directory, set values as desired, filling empty values
3. Run `docker compose up -d` to start all services
4. Access the website on `[localhost:3000](localhost:3000)

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
TODO

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
