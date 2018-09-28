# Authority Migration Helpers
These scripts are designed for customers that will be migrating their on-prem Code42 authority into the Code42 multi-tenant cloud.  Two of the most common tasks that admins need to do are to remove any custom roles, and to make sure all of their usernames are in an e-mail format.

### roleChanger.py
This is a standalone Python script which will walk the admin through mass role changes in their environment to get rid of custom roles, and to add roles that can be translated into the cloud easier than going one-by-one in the web interface.

### usernamesToEmails.py
This is a standalone Python script which will change users' usernames to the e-mail format required by the Code42 cloud based on one of three methods that the admin can specify:
1. Make user's email their username
    * This method simply copies whatever is used in the Code42 `email` field and pastes it into their `username` field
    * For the example user below, the username would get changed to ` bob@company.com`
2. Append a static domain to the username
    * This method takes the current username and appends an admin-defined suffix (` @company.com`) at the end
    * For the example user below, the username would get changed to ` bsmith@company.com`
3. Use the user's first and last name, along with a static domain
    * This method uses the `First Name` and `Last Name` fields of a Code42 user account as well as an admin-defined domain suffix and puts the result in the username field.
    * For the example user below, the username would get changed to ` bob.smith@company.com`

Example User (beginning state):
* username: `bsmith`
* email: ` bob@company.com`
* First Name: `Bob`
* Last Name: `Smith`
