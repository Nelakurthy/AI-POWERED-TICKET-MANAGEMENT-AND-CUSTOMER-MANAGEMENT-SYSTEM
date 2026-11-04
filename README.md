# AI-POWERED-TICKET-MANAGEMENT-AND-CUSTOMER-MANAGEMENT-SYSTEM
The AI-Powered Ticket Management and Customer Management System is a full-stack web application designed to streamline customer support operations through Artificial Intelligence. It provides a centralized platform where customers can raise support tickets, track their status, and communicate with support agents.


## Authentication and authorization

The API uses Django REST Framework token authentication and role-based permissions.

### Apply database migrations

```powershell
python manage.py migrate
```

### Authentication endpoints

Base URL: `/api/auth/`

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| POST | `register/` | Create a customer account | Public |
| POST | `login/` | Obtain an API token | Public |
| POST | `logout/` | Revoke the current token | Authenticated |
| GET | `me/` | Get the signed-in user's profile | Authenticated |

Example registration body:

```json
{
  "email": "customer@example.com",
  "password": "Use-A-Strong-Password-Here",
  "first_name": "Alex",
  "last_name": "Customer",
  "phone_number": "9876543210"
}
```

Example login body:

```json
{
  "email": "customer@example.com",
  "password": "Use-A-Strong-Password-Here"
}
```

Send the returned token on protected API requests:

```
Authorization: Token YOUR_TOKEN
```

### Roles and permissions

- `CUSTOMER`: standard customer account; public registration always assigns this role.
- `AGENT`: support-agent role; assign only through a trusted administrator workflow.
- `ADMIN`: administrative role; Django superusers also pass admin role checks.

Reusable permission classes are available in `accounts/permissions.py`:
`IsAdmin`, `IsAgent`, `IsCustomer`, `IsAdminOrAgent`,
`IsAdminOrReadOnly`, and `IsOwnerOrAdmin`.

Use `IsOwnerOrAdmin` as an object-level permission on views that retrieve an object.
For list endpoints, also filter the queryset to the current user's records; object
permissions do not automatically filter list results.

### Run authorization tests

```powershell
python manage.py test accounts
```

### Important security notes

- Never commit production secrets or database credentials. Load `SECRET_KEY` and database
  credentials from environment variables and rotate any credentials that were previously
  committed to a public repository.
- Serve the API over HTTPS in production.
- Token authentication is suitable as a straightforward API baseline; use short-lived
  tokens or a refresh-token strategy if your deployment requires token expiry.
