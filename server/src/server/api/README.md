Below is a set of unique HTTP status codes for the specific scenarios where the webserver would require one of our custom 'fouttypes': `perms`, `username`, `password`, `email`, `other`.
The interface will receive one of the HTTP status codes below together with a reason-phrase and communicate this to the webserver in the right format using the fouttypes:

| Scenario                                | HTTP Status | Reason-Phrase                   | Problem ID                   | FoutType |
|-----------------------------------------|------------:|---------------------------------|------------------------------|----------|
| No admin permissions for action         |         403 | Admin Required                  | `PROB_NO_ADMIN`              | perms    |
| Username already exists                 |         409 | Username Already Exists         | `PROB_USERNAME_EXISTS`       | username |
| Not valid email                         |         422 | Invalid Email Format            | `PROB_INVALID_EMAIL`         | email    |
| Already registered email                |         409 | Email Already Registered        | `PROB_EMAIL_REGISTERED`      | email    |
| Username does not hold to constraints   |         422 | Username Constraints Violation  | `PROB_USERNAME_CONSTRAINTS`  | username |
| Password does not hold onto constraints |         422 | Password Constraints Violation  | `PROB_PASSWORD_CONSTRAINTS`  | password |
