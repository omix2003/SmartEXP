# AI Collaboration Notes

This note outlines how I used AI tools (specifically FastAPI boilerplate generators and code assistants) to help build this API, and the changes I made to make the code production-grade.

## What was AI-generated vs. What I wrote

### AI-Generated Parts
I used AI to generate the initial project structure and standard FastAPI boilerplate code:
- The base CRUD routes and response models (specifically the UUID generation and standard HTTP status responses).
- The basic `JSONDatabase` structure with the thread lock. I wanted to make sure reading and writing to the JSON file was thread-safe since FastAPI is asynchronous, and the AI provided a clean lock implementation.
- The standard calculations for the analytics endpoint (percentages, average counts).

### What I wrote / modified myself
- **Real-world INR Data Seeding:** The AI originally generated mock transactions in USD and with generic names. I replaced all 100 transaction records with realistic INR values matching Indian context services like Swiggy, Zomato, Jio, and local Kirana shops to represent actual user spending.
- **Advanced Query Filters:** I wrote the database filters that handle date ranges (`start_date` and `end_date`), amount boundaries (`min_amount` and `max_amount`), and specific payment types.
- **Search Logic:** I implemented the substring-matching logic for the general `search` parameter, making sure it queries both transaction titles and receivers.

---

## Validations, Testing, and Adjustments to AI Output

1. **Improving Payment Type Handling (Pre-validators):**
   The AI schema generated standard Pydantic literals for `payment_type` (like `"credit_card"`, `"cash"`). However, when testing the API endpoints, I noticed that users naturally type inputs with spaces or capital letters (e.g. `"Credit Card"` or `"  cash  "`), which threw validation errors. I wrote a custom pre-validator to strip spaces and convert spaces to underscores so that inputs are automatically normalized without failing the request.

2. **Fixing Date Serialization Errors:**
   Initially, the generated Pydantic code tried to store `datetime.date` objects directly in the JSON database. This caused serialization errors on write. I changed the code to convert the date object to an ISO-8601 string (`str(date)`) before writing it to the database file.

3. **Ensuring Test Isolation and OS Compatibility:**
   When testing on Windows, I ran into `PermissionError` locks on the test JSON database during the pytest teardown. I modified the test fixtures to safely catch permission errors on file deletion. I also added path injection (`sys.path.insert`) to the test file so that `pytest` works seamlessly from the project root.

---

## Discarded AI Suggestions and Rationale

* **Using an ORM / SQLite database:**
  The AI suggested using SQLAlchemy and SQLite for transaction persistence. I decided not to do this because the assignment description explicitly stated that data could be stored in a local JSON file and that no database was required. Keeping it a simple, thread-safe JSON file avoids unnecessary overhead.
* **Auto-generation Scripts (`generate_mock_data.py`):**
  The AI suggested having a Python script run on startup to generate fake data. I discarded this because it adds bloat to the workspace. Instead, I pre-seeded the `expenses.json` file directly so that the reviewer has immediate access to 100 realistic data points without needing to run extra commands.
* **Complex JWT Authentication:**
  The AI recommended setting up security dependencies and JWT login routes. I decided against this to keep the API focused entirely on the core requirements of the take-home test.

---

## Appendix: Initial Project Brief & Context

At the start of this assignment, I defined a set of strict guidelines to ensure that the code followed production-grade standards rather than looking like a standard prototype boilerplate. I wanted the API structure, validation schemas, and response formats to be clean, professional, and completely free of emojis. I also established a structured Git commit workflow, manually reviewing and approving each implementation step before staging it for commit and pushing to GitHub. 

Below is the initial brief I wrote to set these engineering standards and guide the AI collaboration from day one:

```text
at this point we arent supposed to make any dashboard so, we can continue with the implementation. but since this is an important project, we need to make sure, right from the start to the end, we dont make any mistakes, right from the structuring the APIs to the response structure everything should be clean. Make sure you review the code and give me a clean API response. I dont want any use of emojis.
Start with initializing a git repo, and wait till i provide you a git repo link.
Once we are connected to github, 
after completing implementation of each feature/ API, commit and push the code to git.
but do make sure that you ask me before commiting/pushing the code.
Update the Implementation plan.

Let me know if you have any questions and lets begin with the implementation.
```
