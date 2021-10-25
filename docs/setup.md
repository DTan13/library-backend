# Setup for Testing Backend

## Tools

- Git

- Docker

- Python

- Heroku

- Postman

## Get Code

- Clone Github repository

  ```zsh
      git clone https://github.com/DTan13/library-backend.git

      cd library-backend
  ```

## Setup for each tool

### Docker

- Install Docker

- pull mongo

  ```zsh
    docker pull mongo:latest
  ```

- Run docker container

  PS: This should be done each time before testing

  ```zsh
    docker container run --name mongo -p 27017:27017 -v ~/data/mongodb:/data/db mongo
  ```

### Python

- Version 3.9.0

- pip uninstall jwt #there is a conflict between jwt and PyJWT

- pip install -r requirements.txt

### Heroku

- Install heroku-cli

- Run following command

  ```zsh
    heroku local web
  ```

- This command will prompt a url on which the server is started

### Postman

- Install Postman
