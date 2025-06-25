Below is a set of unique HTTP status codes for the specific scenarios where the webserver would require one of our custom ErrorType: `perms`, `username`, `password`, `email`, `problem`, `other`.
The interface will receive one of the HTTP status codes below together with a problem ID and communicate this to the webserver in the right format using the ErrorTypes:

# User Register

| HTTP Status | Reason                          | Problem ID (detail)          | ErrorType | Implemented |
|------------:|---------------------------------|------------------------------|-----------|-------------|
|         409 | Username Already Exists         | `PROB_USERNAME_EXISTS`       | username  |     ✔️     |
|         422 | Invalid Email Format            | `PROB_INVALID_EMAIL`         | email     |     ✔️     |
|         409 | Email Already Registered        | `PROB_EMAIL_REGISTERED`      | email     |     ✔️     |
|         422 | Username Constraints Violation  | `PROB_USERNAME_CONSTRAINTS`  | username  |     ✔️     |
|         422 | Password Constraints Violation  | `PROB_PASSWORD_CONSTRAINTS`  | password  |     ❎     |

# User Login

| HTTP Status | Reason                          | Problem ID (detail)          | ErrorType | Implemented |
|------------:|---------------------------------|------------------------------|-----------|-------------|
|         422 | Username Constraints Violation  | `PROB_USERNAME_CONSTRAINTS`  | username  |     ✔️     |
|         401 | Invalid login                   | `Unauthorized`               | invalid   |     ✔️     |

# Admin page

| HTTP Status | Reason                          | Problem ID (detail)          | ErrorType | Implemented |
|------------:|---------------------------------|------------------------------|-----------|-------------|
|         403 | Admin Required                  | `PROB_NO_ADMIN`              | perms     |     :question:     |

# User Update

| HTTP Status | Reason                          | Problem ID (detail)          | ErrorType| Implemented |
|------------:|---------------------------------|------------------------------|----------|-------------|
|         401 | User uuid does not match JWT    | `PROB_INVALID_UUID`          | uuid     |     ✔️     |
|         404 | User not found                  | `ERROR_USER_NOT_FOUND`       | uuid     |     ✔️     |
|         422 | Given key is not an option      | `PROB_INVALID_KEY`           | key      |     ✔️     |

# Get/Read Problem

| HTTP Status | Reason                          | Problem ID (detail)          | ErrorType | Implemented |
|------------:|---------------------------------|------------------------------|-----------|-------------|
|         404 | Problem not found               | `ERROR_PROBLEM_NOT_FOUND`    | problem   |     ✔️     |

# Post Submission

| HTTP Status | Reason                          | Problem ID (detail)          | ErrorType | Implemented |
|------------:|---------------------------------|------------------------------|-----------|-------------|
|         404 | Problem not found               | `ERROR_PROBLEM_NOT_FOUND`    | problem   |     ✔️     |
