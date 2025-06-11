Below is a set of unique HTTP status codes for the specific scenarios where the webserver would require one of our custom 'fouttypes': `perms`, `username`, `password`, `email`, `other`.
The interface will receive one of the HTTP status codes below together with a problem ID and communicate this to the webserver in the right format using the fouttypes:

| HTTP Status | Reason                          | Problem ID                   | FoutType |
|------------:|---------------------------------|------------------------------|----------|
|         403 | Admin Required                  | `PROB_NO_ADMIN`              | perms    |
|         409 | Username Already Exists         | `PROB_USERNAME_EXISTS`       | username |
|         422 | Invalid Email Format            | `PROB_INVALID_EMAIL`         | email    |
|         409 | Email Already Registered        | `PROB_EMAIL_REGISTERED`      | email    |
|         422 | Username Constraints Violation  | `PROB_USERNAME_CONSTRAINTS`  | username |
|         422 | Password Constraints Violation  | `PROB_PASSWORD_CONSTRAINTS`  | password |
