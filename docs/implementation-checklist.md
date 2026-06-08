# Implementation Checklist

This is the implementation tracking checklist for the Eagle Bank take-home task.

The aim is to cover at least one of each CRUD-style operation across the main elements, with proper error handling and tests, so that the solution is easy to discuss and easy to extend in follow-up conversation.

## Priority Markers

- `★` Must implement. These are the scenarios I think are most important to get done in order to demonstrate a complete, defensible solution.
- Unmarked items are still worth doing, but can be deprioritised if time becomes tight.

## Why these are marked

- The brief explicitly calls out Create and Fetch as the minimum expected operations for User, Account, and Transaction.
- Authentication is central because nearly everything after user creation depends on it.
- Ownership checks, validation failures, unauthenticated access, and insufficient funds are the most important non-happy-path behaviours to demonstrate.
- A test structure is important early, because I do not want to leave validation and error handling unproven until the end.
- Update and Delete flows are still useful to implement because they show you can take the design beyond the minimum and extend it in a consistent way.
## Foundations

- [x] ★ Confirm final stack and repo structure
- [ ] ★ Review `openapi.yaml` in full
- [x] ★ Define auth endpoint and update OpenAPI spec
- [x] ★ Set up app scaffold, config, and database session
- [x] ★ Set up test structure

## User

- [x] ★ Create user
- [x] ★ Fetch own user
- [ ] Update own user
- [ ] Delete own user
- [x] ★ Handle validation errors
- [x] ★ Handle unauthenticated access
- [x] ★ Handle forbidden access to another user's record
- [x] ★ Handle non-existent user
- [x] ★ Add tests for user flows

## Authentication

- [x] ★ Implement login endpoint
- [x] ★ Return JWT bearer token
- [x] ★ Reject invalid credentials
- [x] Add tests for authentication flows

## Account

- [x] ★ Create account
- [x] List own accounts
- [x] ★ Fetch own account
- [x] Update own account
- [x] Delete own account
- [ ] ★ Handle validation errors
- [x] ★ Handle unauthenticated access
- [x] ★ Handle forbidden access to another user's account
- [x] ★ Handle non-existent account
- [x] Add tests for account flows

## Transaction

- [ ] ★ Create deposit transaction
- [ ] ★ Create withdrawal transaction
- [ ] ★ Reject withdrawal with insufficient funds
- [ ] List account transactions
- [ ] ★ Fetch specific transaction
- [ ] ★ Handle validation errors
- [ ] ★ Handle unauthenticated access
- [ ] ★ Handle forbidden access to another user's account or transaction
- [ ] ★ Handle non-existent account or transaction
- [ ] Add tests for transaction flows

## Submission

- [ ] Write README properly
- [ ] Review `JACK_NOTES.md`
- [ ] ★ Review commit structure
- [ ] ★ Prepare walkthrough talking points
