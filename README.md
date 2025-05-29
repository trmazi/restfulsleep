# RestfulSleep

The PhaseII backend API, based on SQLAlchemy and Flask-restful.

Connect applications to the PhaseII Database using REST and JSON.

Currently used by the following PhaseII tools:
- PhaseWeb3: Vue based PhaseII Web UI
- BadManiac: Discord bot for scorecards and playvideos

## WARNING!
This documentation is insanely out of date and needs work! Please read api/utils/main.py for endpoints.

## Auth flow
Currently, application keys are not used. I plan on using them but for now it's not too important.

`POST`, `DELETE`, and `UPDATE` require a Session, which is encrypted by this API.
Anything `Arcade`, `Admin`, and `User` also require a Session.

Generarate a Session with `POST /v1/auth/createSession`, check a Session with `/v1/auth/deleteSession`, and delete a Session with `/v1/auth/deleteSession`.

## Schema
All request paths start with `/v1/` (minus the video sharing ones).

Status Codes (inside response):
- `success`: OK
- `warn`: Non-fatal warnings
- `error`: Fatal errors

All responses are in the format of `{status: response status, error_code: if status is error or warn, data: response data}`

## Requests
### `/`
- `GET`
  - Returns a status message to confirm that the API is alive.

### `/v1/arcade/<arcadeId>`
- `GET`
  - Given an Arcade ID, return information about an arcade.
  - Requires an active session and requires that you own the arcade.

### `/v1/arcade/<arcadeId>/paseli`
- `GET`
  - Given an Arcade ID, return an arcade's PASELI data.
  - Requires an active session and requires that you own the arcade.
 
### `/v1/news/getAllNews` - TODO: rename this.
- `GET`
  - Return all news data.
  - No session required.

 ### `/v1/news/getNews/<newsId>` - TODO: rename this.
- `GET`
  - Given a News ID, return all news data.
  - No session required.

### `/v1/auth/createSession` - TODO: redo Session requests.
- `POST`
  - Given a username, password and return an encrypted Session ID if credentials are correct.

### `/v1/auth/checkSession` - TODO: redo Session requests.
- `POST`
  - Given a Session ID and return its status.

### `/v1/auth/deleteSession` - TODO: redo Session requests.
- `POST`
  - Given a Session ID and delete it. Always returns `success`.

### `/v1/user/<userId>`
- `GET`
  - Given a User ID and return a minified user profile.
  - If a valid Session is sent to the server, and if the requested user is the Session's user, return more information about a user.
    - `User.email`
    - `User.data`
   
### `/v1/user/cards`
- `GET`
  - Returns the Session's user's saved cards.
  - Requires a valid Session.
 
### `/v1/game/<game>/profiles`
- `GET`
  - Given a Game code and load all profiles.

### `/v1/profile/<game>`
- `GET`
  - Given a Game and User ID and get user's profile for said game.
  - Queries:
    - `version`: Version code for the profile. Defaults to the newest profile a user has.
    - `userId`: Requird. The User ID for the profile.
