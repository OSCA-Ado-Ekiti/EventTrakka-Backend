# Contributing

If you already cloned the [EventTrakka-Backend](https://github.com/OSCA-Ado-Ekiti/EventTrakka-Backend) repository, and 
you want to deep dive in the code, here are some guidelines to set up your environment.

## Prerequisites

The structure is adopted from the backend of [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)

- All pull requests should be sent to the `development` branch of the project as the `main` branch is reserved for 
deploying the project.
- Keep your local copy of the `main` and `development` branch clean and create your feature specific branch for your
  contributions.
- All your feature branches should check out from the `development` branch.
- Sync your `development` branch regularly.
- For the two choices for setting up this project locally, you will need to populate a `.env` file that you should create
in the project's root with the following environmental variables required for the project to work correctly.
    ```dotenv
    PROJECT_NAME = "EventTrakka Backend"
    SECRET_KEY = "" # Your app secret key (e.g. X3kKmb-T085Gybe9wby9NUPZFxuy8YNvRyQ1br7EBvY0 )
    POSTGRES_HOST = "" # Your postgress db host (The value should be "database" if you're using docker)
    POSTGRES_PORT = "" # Your postgres db port (e.g. "5432")
    POSTGRES_USER = "" # Your postgres db user (e.g. "eventtrakka_admin")
    POSTGRES_PASSWORD = "" # Your postgres db password (e.g. "password123")
    POSTGRES_DB = "" # Your posgres db name (e.g. "eventrakka_db")
    BACKEND_CORS_ORIGINS = "" # Comma separated values of all the allowed CORS origin (e.g. "http://127.0.0.1:3000,http://127.0.0.1:5173")
    ```
- This project also uses [uv](https://docs.astral.sh/uv/) for managing its dependencies, its required to have in installed.

## Setting up locally via Docker

When setting up the project via docker, the postgres db related environmental variables in the `.env` file are used to
set up a postgres database.

### Spinning up a container

From the project's root spin up a container to run in the background (You can view the container in docker desktop if
installed or remove the `-d` flag to run the container in the current shell)

```commandline
docker-compose up -d
```

### Apply pending migrations

To apply all pending database migrations from the project's root run.

```commandline
docker-compose exec web alemic upgrade head
```


## Setting up locally without docker

When setting up the project locally without docker, you will have to set up a postgres database and provide it's 
connection credentials via the postgres related environmental variables in the `.env` file.

### Installing projects dependencies

We'll need install the project's dependencies to our local machine via

```commandline
uv sync
```

### Activate your virtual env

The command above creates a `.venv` folder in the project's root that houses a virtual env for the project. activate the
virtual env as you would for your specific operating system e.g. `source .venv/bin/activate`

### Apply pending migrations

To apply all pending database migrations from the project's root run.

```commandline
alemic upgrade head
```

Thank you!!! Awaiting your contributions 😎