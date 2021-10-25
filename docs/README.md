# Backend

> Prefer [Local](#local) for now as main development environment.

## Setting up Development Environment for Docker

- Build image

  ```bash
      docker image build --rm -t library-backend .
  ```

- Start container for development

  ```zsh
      # here "~/dev/library-backend/" is location of project
      docker container run --rm -it -v ~/dev/library-backend:/code/backend/ -p 0.0.0.0:8000:8000 library-backend
  ```

    <h2>Demo</h2>

- You will be able to work further in the terminal.

<br/>

## Setting up Development Environment for Local Development<a id="local"></a>

- Install python and pip

- Install dependencies

  ```zsh
    pip install django pymongo bcrypt pyjwt
  ```
