# AI Agent Directives[cite: 1]

* Instructions for AI development tools (e.g., Cursor, or Kimi Claw if adopted) interacting with this codebase[cite: 1].

## Project Scope[cite: 1]
* **Purpose:** Maintain and optimize the MyShows to Trakt data migration tool[cite: 1].
* **Stack:** Python 3, `requests`[cite: 1].

## Agent Constraints[cite: 1]
* Format all outputs and documentation using bullet points[cite: 1].
* Keep explanations and code changes short and concise[cite: 1].
* Minimize third-party dependencies; rely on standard Python libraries when possible[cite: 1].
* Handle API errors and edge cases (e.g., missing dates, failed auth) silently but safely[cite: 1].
* Do not introduce heavy architectural patterns for simple scripts[cite: 1].

## Reference Documentation
* [Migration Plan](MIGRATION_PLAN.md): Roadmap for data export and import strategies.
* [MyShows API Swagger](docs/myshows_swagger.json): Specification for the MyShows JSON-RPC 2.0 API.
* [Trakt CSV Import Instructions](docs/trakt_csv_instruction.md): Format requirements for importing data into Trakt via CSV.
