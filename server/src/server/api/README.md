Below is a set of unique HTTP status codes for the specific scenarios where the webserver would require one of our custom 'fouttypes': `perms`, `username`, `password`, `email`, `other`.
The interface will receive one of the HTTP status codes below together with a problem ID and communicate this to the webserver in the right format using the fouttypes:

# User Register

| HTTP Status | Reason                          | Problem ID (detail)          | FoutType | Implemented |
|------------:|---------------------------------|------------------------------|----------|-------------|
|         409 | Username Already Exists         | `PROB_USERNAME_EXISTS`       | username |     [x]     |
|         422 | Invalid Email Format            | `PROB_INVALID_EMAIL`         | email    |     [x]     |
|         409 | Email Already Registered        | `PROB_EMAIL_REGISTERED`      | email    |     [x]     |
|         422 | Username Constraints Violation  | `PROB_USERNAME_CONSTRAINTS`  | username |     [x]     |
|         422 | Password Constraints Violation  | `PROB_PASSWORD_CONSTRAINTS`  | password |     [ ]     |

# User Login

| HTTP Status | Reason                          | Problem ID (detail)          | FoutType | Implemented |
|------------:|---------------------------------|------------------------------|----------|-------------|
|         422 | Username Constraints Violation  | `PROB_USERNAME_CONSTRAINTS`  | username |     [x]     |
|         401 | Invalid login                   | `Unauthorized`               | invalid  |     [x]     |

# Admin page

| HTTP Status | Reason                          | Problem ID (detail)          | FoutType | Implemented |
|------------:|---------------------------------|------------------------------|----------|-------------|
|         403 | Admin Required                  | `PROB_NO_ADMIN`              | perms    |     [ ]     |
