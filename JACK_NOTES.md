# Jack Notes
> These notes are my raw, un-edited thoughts on this take home task, to help paint a picture of my thinking throughout it.

Implementation tracking lives in [`docs/implementation-checklist.md`](docs/implementation-checklist.md).

## Total Time taken: 
### 6th June: 2h 30m
### 7th June: 



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

### Configuring FastAPI
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




### Plan for tomorrow
- [x] Review `openapi.yaml` path by path and confirm the user/account/transaction flows
- [x] Decide and document the auth endpoint contract for `POST /v1/auth/login`
- [x] Scaffold the actual project structure for the FastAPI application
- [x] Set up FastAPI app entrypoint, config, and SQLAlchemy database session
- [ ] Build user schemas, model, service, and router together as the first full vertical slice
- [ ] Add the core user error scenarios and tests
- [ ] If time allows, start the account layer after the user/auth path is working cleanly

### Commit plan
- [ ] Commit scaffold: app structure, config, dependency wiring
- [ ] Commit auth contract: update `openapi.yaml` with login endpoint
- [ ] Commit user vertical slice: model, schemas, service, router
- [ ] Commit user tests and error handling
- [ ] Commit account vertical slice once user/auth is stable

### Completed Today
- [x] Set up git repo and planning/admin files
- [x] Scaffold project structure
- [x] Set up FastAPI app entrypoint, config, and SQLAlchemy database session
- [x] Add a first auth route and health route
- [x] Get the scaffold running locally with `/health` and `/docs`


## Questions / things I want to clear up
- [x] Create a TODO list of all scenarios in a clean format, so it is easy to show what I have and have not implemented
- [x] Update the OpenAPI spec with the details of the auth endpoint I implement
- [x] Understand JWT properly at a high level: it is an auth token passed by the client, somewhat similar in purpose to a browser cookie, but implemented differently
- [x] Confirm what should happen if protected endpoints are called without authenticating first
- [ ] Decide what extra work best demonstrates ability beyond the minimum expected scope

## Test / error handling mindset
- I want each main area to have both success-path tests and failure-path tests.
- I want to be able to explain not just the endpoint itself, but also the validation, ownership checks, and auth checks around it.
- If they ask me to extend the project later, I want the existing structure to make that feel natural rather than bolted on.
