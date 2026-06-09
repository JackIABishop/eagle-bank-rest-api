# Jack Notes
> These notes are my raw, un-edited thoughts on this take home task, to help paint a picture of my thinking throughout it.

Implementation tracking lives in [`docs/implementation-checklist.md`](docs/implementation-checklist.md).

## Total Time taken: 
### 6th June: 2h 30m
### 7th June: 4h
### 8th June: 2h 
### 9th June: 2h

## 6th June 2026 
### 17:00 init
- I am going to record my time spent on this task, to give a feel for how long this took me. 
- I would consider myself a beginner database programmer, and this is the first time that I will be setting one up from scratch. 
- I will not pretend to know all frameworks and tech stacks related to this task, but if I have committed the code, I do have an understanding of the concepts and how to use them.
- I will be using AI to aid me in my decision making in the interest of time on this task, but I will be using my own knowledge and understanding to make the final decisions.
- I can code C++, Python, & JavaScript (years of experience in that order), I will use Python for this task as it is the language that I enjoy the most and I feel I will be able to get quick results. 
- I will commit atomically as I usually do for new features, but to also show train of thought for the reviewer if they wish to see. 

### 17:30 understanding req's
- The aim is to create a REST API conforming to the OpenAPI spec and scenarios in the brief.
- My understanding so far is that the API needs to cover users, bank accounts, and transactions.
- Transactions seem to be append-only in practice: create and fetch, but not update or delete.
- The brief does not expect every endpoint to be completed, but I do want to go further than the bare minimum so I can discuss trade-offs and extension work properly.
- My own goal is to cover at least one of each CRUD-style operation across the elements, with error handling and tests, so I have an easy platform for follow-up discussion in interview.
- For each scenario, appropriate error handling should be included for invalid or missing credentials.
- After reading the scenarios, my initial thought is that every task after user creation requires authentication, so the application should be structured in a way that auth is checked consistently rather than ad hoc in each route.
- ⚠️ If this was a real system, I would be wary of returning very specific errors if a user, account, or transaction does not exist, as that can reveal information to an attacker. For this task, I will likely need to follow the contract first, but it is still worth raising as a security consideration.

### 18:30 yaml
- OpenAPI spec structure is broadly:
  - tags
  - paths
  - components
- The main endpoint groups are:
  - users
  - accounts
  - accounts/{accountNumber}/transactions
- The `components` section defines the schemas, so this tells me what data I should be sending and receiving.
- This also defines the expected response bodies and status codes, so it is effectively the API contract rather than just a loose guide.

- Auth
  - `bearerAuth`
  - format: JWT
  - client logs in -> client receives a bearer token -> client sends `Authorization: Bearer <token>` on protected requests
  - the spec defines bearer auth but does NOT define the login endpoint itself, so I need to update the OpenAPI spec with the auth endpoint I implement
  - if a protected endpoint is called without valid authentication, that should return `401`


### 19:30 tech stack
- I think it is useful to think about the stack by area rather than as one big blob:
  - Language: Python
    - This is the language I will write the application logic in. It is the base layer that everything else is built with, and it is the language I am most comfortable moving quickly in and explaining clearly in review.
  - Web framework / API layer: FastAPI
    - This is the part that exposes the backend as an HTTP API. It handles routes, requests, responses, and works neatly with typed models. I like it here because it maps well to an OpenAPI-driven API, and it gives me generated interactive documentation at `/docs` from the implementation itself.
  - Data / ORM layer: SQLAlchemy
    - This is the layer that helps the Python application talk to the database in a structured way, without me writing raw SQL for everything. I like it because it gives me a standard ORM/data layer rather than hand-rolling database access.
  - Database engine: SQLite
    - This is where the actual data is stored. It keeps the setup local and simple for a take-home task, which is exactly what I want here rather than extra infrastructure.
  - Authentication approach: JWT bearer auth
    - This is how protected endpoints know who the user is. The client logs in, receives a token, and sends it with later requests. I like it because it fits the brief and maps cleanly to the `bearerAuth` security scheme already described in the OpenAPI spec.

- In Python, I would use Pydantic models for the definition and validation of structured data for use with FastAPI.
  - request bodies
  - response bodies
  - validation rules


### Completed Today
- [x] Understood requirements
- [x] Worked with GPT to understand the available tech stack options and pick a direction

## 7th June 2026
### 10:00 Authenticating a user 
- I want authentication to be simple and defensible:
  - `POST /v1/auth/login`
  - request body: `email` and `password`
  - validate both fields on the server side
  - validate email format on the server side as well, rather than assuming the client has done it
  - if the credentials are correct, return a JWT bearer token
  - if the credentials are wrong, return `401`
- I do think the token should expire.
  - That is a sensible default for a banking-style API.
  - It also gives me something concrete to explain in review rather than pretending tokens last forever.
- My current thinking for the success response is:
  - `accessToken`
  - `tokenType`
  - `expiresIn`
- Example request:

```json
{
  "email": "user@example.com",
  "password": "correct-horse-battery"
}
```

- Example success response:

```json
{
  "accessToken": "eyJhbGciOi...",
  "tokenType": "Bearer",
  "expiresIn": 3600
}
```

- Important implementation note:
  - I do not think the access token itself should be stored against the user and matched on every request.
  - My understanding is that the server signs the JWT, the client presents it later, and the server validates the token signature, expiry, and payload before using the referenced user identity.
  - I still like the idea of checking that the referenced user in the token still exists.
  - The existing `CreateUserRequest`/`UpdateUserRequest` schema did not require a password, so I have added this to support the auth flow properly.

### 11:00 Configuring FastAPI
- I now have the first application scaffold in place, and this is how I am thinking about the structure:
  - `app/main.py`
    - FastAPI entrypoint. This creates the app, registers exception handlers, and includes routers.
  - `app/config.py`
    - Application settings such as app name, database URL, JWT secret, algorithm, and token expiry.
  - `app/db.py`
    - SQLAlchemy engine, session factory, base model class, and database session dependency.
  - `app/models/`
    - ORM models representing database tables. At the moment this starts with `User`.
  - `app/schemas/`
    - Pydantic models for request and response validation.
  - `app/routers/`
    - HTTP endpoints. At the moment this includes health and auth routes.
  - `app/services/`
    - Business logic, so the routes stay thinner and less cluttered.
  - `app/errors.py`
    - Global exception handling so validation and HTTP errors return in a format closer to the API contract.
  - `tests/`
    - API and service tests once I start building out the actual behaviour.
- I used AI here to help create the initial scaffold and boilerplate, but I still need to review and understand each part of the structure before building further on top of it.

### 12:00 Building out the User endpoint
- I do want to be explicit that I have used AI to help with scaffolding, boilerplate, and some of the repetitive setup work in this project.
- I do not think that is a problem for this task, because the brief allows AI assistance and I am not trying to pass off code I do not understand.
- The important line for me is that if I commit the code, I need to understand what it is doing and be able to explain it in review.
- My aim is to use AI to save time on setup and repetitive structure, then spend my own time understanding, reviewing, and shaping the code into something I can defend properly.

### 20:00 Testing
- `conftest.py` is set up to provide a temporary test database, so my real local development database is not affected. This is important both for protecting local data and for keeping the tests repeatable.
- `test_user_auth.py` currently contains tests for:
  - creating a user
  - logging in successfully
  - rejecting invalid login credentials
  - fetching the authenticated user's own record
  - rejecting unauthenticated access
  - rejecting access to another user's record
- Each test will follow a similar structure too:
    1. What setup data is created? 
    2. What API call is made? 
    3. What status code is expected? 
    4. What JSON body is expected? 
    5. What rule does this prove? 
- I expect this to scale cleanly, and later I can add `tests/test_accounts.py` and `tests/test_transactions.py` and reuse `conftest.py`. 
- I noticed that some response codes are documented in the route decorators for completeness and alignment with the API contract, even where they are not all raised explicitly in the route body itself.
- I need to stay aware of where each response actually comes from: route logic, dependencies, validation handlers, or unexpected failures.

## 8th June 2026
### 19:00 Accounts
- It would be nice to have a UI to interact with this API - make that is take home test 2! 
- Using Swagger UI to test database outside of the `tests/`
- I used the account area as my demonstration of the more complete REST flow, because by this point I already had the user/auth foundations in place and wanted to show I could extend the structure consistently.
- I now have:
  - an account model
  - account request/response schemas
  - an account service layer
  - account routes for create, list, fetch, update, and delete
  - account tests covering both happy paths and important error cases
- The shape is intentionally the same as the user slice:
  - `models/` for database structure
  - `schemas/` for Pydantic request/response validation
  - `services/` for business logic
  - `routers/` for the HTTP layer and status codes
- That matters because I do not want each area of the API to look like it was built by a different person. I want one repeatable pattern I can explain and extend.
- The account table links back to the authenticated user via `user_id`, so ownership checks are a core part of this slice.
- The main rules in the router are:
  - create account for the authenticated user
  - list only the authenticated user's accounts
  - fetch only your own account
  - update only your own account
  - delete only your own account
- The tests for accounts currently cover:
  - create account
  - list only the authenticated user's accounts
  - fetch own account
  - reject access to another user's account
  - update account
  - delete account
  - reject unauthenticated access
  - return `404` for a missing account
- For the tests, I created a `helpers.py` for common test functions such as `create_user_payload()` - with the idea that this file is maintained for simple functions to reduce complex dependency between tests. 
- I like this as a demonstration area because it shows the full route pattern more clearly than the user slice currently does, since user update/delete are still de-prioritised.
- One gap I want to keep visible is account deletion once transactions exist.
- The brief / OpenAPI definitely says transactions can be created and retrieved but not modified or deleted.
- It does not explicitly say "do not delete an account if it has transactions", so I am treating that as a follow-up business rule rather than pretending it is already fully specified.
- My instinct is that once the transaction layer is in place, account delete should probably return a conflict instead of hard-deleting an account with history.

### 20:40 SQLite lock issue
- I hit a local development issue here rather than an API design issue: `sqlite3.OperationalError: database is locked`.
- The cause turned out not to be the account code itself, but the fact that I had `DB Browser for SQLite` open against the local `eagle_bank.db` file while Uvicorn was starting up.
- That meant SQLite could not create the new `bank_accounts` table at startup.
- Two useful takeaways from that:
  - SQLite is simple and good for a take-home, but because it is file-based I need to be aware of local tooling holding locks on the file.
  - I should treat the database viewer as an inspection tool, not something to leave attached while the app is trying to create tables or write data.
- The app startup was also improved so table creation happens on application startup rather than at import time, which is cleaner and helped keep the test environment isolated from the real local database.

### 21:00 Current state
- I now have a working FastAPI application with:
  - user creation
  - login with JWT bearer auth
  - fetch own user
  - full account slice: create, list, fetch, update, delete
  - pytest coverage for the current user/auth and account flows
- The project is now beyond the initial scaffold stage and into meaningful feature coverage.
- Swagger UI at `/docs` is now a useful way to demonstrate and manually test the current implementation.

## 9th June 2026
### Final night priorities
- I only have one proper evening left for implementation, so I need to be disciplined about what adds the most value.
- The best remaining work is the transaction slice:
  - [x] create deposit
  - [x] create withdrawal
  - [x] reject insufficient funds with `422`
  - [x] list transactions
  - [x] fetch a specific transaction
- I think this is the right use of the remaining time because it completes the core banking behaviour far better than spending the last night polishing lower-value CRUD edges.
- It also gives me a better interview story -- because insufficient funds and transaction history are more meaningful business rules than simply adding more endpoint coverage for the sake of it.

### Transaction slice
- Building the first transaction scenarios felt relatively straightforward once the user/auth/account structure was already in place.
- The main thing I needed to stay careful about was following the OpenAPI contract properly rather than improvising:
  - the permitted transaction types
  - the minimum / maximum amount rules
  - the `422` insufficient-funds case
  - ownership and not-found behaviour on the new list / fetch routes
- This is one of the clearer examples of why the earlier scaffold and layering work mattered. Once the account ownership and database patterns were already there, I could add the transaction create flow without inventing a new structure.
- One useful hardening step after the first pass was noticing that the OpenAPI contract caps exposed account balances at `10000.00`, so deposits also need a guard for "valid transaction amount but invalid resulting balance".
- I also tightened account deletion so it now refuses to delete an account that already has transaction history. That was not just polish: once transactions exist, hard-deleting the account would leave the model in a bad state conceptually, even if a simple demo app could get away with it.

### Debugging through VS Code
- I have been using the FastAPI debug configuration in VS Code to run the service under the debugger and hit breakpoints from Swagger UI.
- My current debugging options now feel like:
  - Swagger UI + temporary `print()` statements for quick manual debugging
  - tests for repeatable behaviour checks
  - FastAPI debug configuration in VS Code when I want to step through the code line by line

### Authentication and correct account refactor
- I noticed the same account lookup + ownership check pattern repeated across both the account routes and the transaction routes.
- Because the behaviour is the same each time -- fetch the account, return `404` if it does not exist, return `403` if it does not belong to the authenticated user -- I think it is cleaner to centralise that in one helper rather than keep copying it.
- My aim with this refactor is to:
  - reduce repetition
  - keep the `404` / `403` behaviour consistent
  - make later account-based routes easier to add
  - avoid having one route drift away from the others by accident
- I still want to keep the helper simple and readable rather than hiding too much behind abstraction.
- I also prefer that helper living outside the account service itself. The account service should stay focused on account business logic, while the ownership guard is more of a reusable access-control helper used by multiple routers.

## Test / error handling mindset
- I want each main area to have both success-path tests and failure-path tests.
- I want to be able to explain not just the endpoint itself, but also the validation, ownership checks, and auth checks around it.
- If they ask me to extend the project later, I want the existing structure to make that feel natural rather than bolted on.
