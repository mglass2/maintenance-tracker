## CLI: register local operator as a user

The application needs to register each CLI session with an active user in the system, similar to logging into the system.  This functionality gives each request from CLI to API a context about which user is making the request.  Refer to this user as the "active user".

Once the operator chooses a user (the active user), the active user's identity should be stored in the CLI service during the active CLI session.  Active user should not persist between CLI sessions - it should be chosen upon starting the CLI service each time.

Present 2 options about how to implement this functionality.  One option should be very simple, and the other option should be JWT based.  There will not be any passwords or authentication involved, the application is still only running locally.  The interface should prompt the operator to select from a list of users in the system.