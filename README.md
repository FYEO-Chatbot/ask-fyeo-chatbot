# ASK-FYEO-Chatbot

This is the backend API that powers the TMU First Year Engineering Office chatbot, designed to assist first-year engineering students and staff by answering their questions. It stores and manages a student/staff FAQ, along with key information and statistics related to each conversation, in a PostgreSQL database. 

(DEPRECATED) The chatbot is created with a pytorch deep neural network and it is accessed via this API. The chatbot trains on the FAQ data stored in the database.

There are multiple types of chatbot supported with this app each using different techniques:
- Bag Of Words (BOW) model 
- BERT transformer based model
- Sentence-Transformer (SBERT) model (no neural network)

(UPDATED) The updated chatbot used in production has been decoupled from this API and is now available as a Streamlit app. You can find the repository [here](https://github.com/Panchofdez/ask-fyeo-chatbot-streamlit) and access the app [here](https://ask-fyeo-chatbot.streamlit.app/).


## Pre-requisites
1. Download and install docker on local machine
2. Git clone repository onto local machine


## Usage

### Development Setup (Local Database)
- using a database solely for development purposes
- will create/run a docker container for the chatbot API and another container for development database (postgres)
- ensure you have a .env file with the environment variables defined in docker-compose-dev.yml file

Commands:    
- Run app for the first time or if there are any new changes
    ```
    docker-compose -f docker-compose-dev.yml up --build
    ```
- Re-run app
    ```
    docker-compose -f docker-compose-dev.yml up
    ```
- Stop app
    ```
    docker-compose -f docker-compose-dev.yml down
    ```


### Production-like Local Testing
- if you want to use the database used in production (**use with caution**)
- will create/run a docker container only for the chatbot API
- ensure you have a .env file with the environment variables defined in docker-compose.yml file

Commands:
- Run app for the first time or if there are any new changes
    ```
    docker-compose up --build
    ```
- Re-run app
    ```
    docker-compose up
    ```
- Stop app
    ```
    docker-compose down
    ```


### Database Initialization
- To populate a fresh database with initial FAQ data (defined in intents.json) and a staff user, set the environment variable DB_INIT=True in the corresponding docker-compose file. 
- **Important**: Only enable this for an empty database to avoid unintended data duplication or conflicts


### Flask Commands 

- Run the following command to enter the docker container for the flask chatbot api
    ```
    docker exec -it chatbot bash
    ```
- There are 5 commands available when inside container:
    | Command               | Description                                      | Flags                     |
    |-----------------------|--------------------------------------------------|---------------------------|
    | `flask train_model`   | Trains the model using FAQ data; saves to `.pth`.| `--for_staff` / `-fs`     |
    | `flask test_model`    | Test the chatbot on the current FAQ data.        | `--for_staff` / `-fs`     |
    | `flask chat`          | Interactive chat with the trained chatbot model. | `--for_staff` / `-fs`     |
    | `flask view_intents`  | Displays the current FAQ data used.              | *(None)*                  |
    | `flask backup_faq`    | Backup the all FAQ data to a intents.json file   | *(None)*                  |
- If `--for_staff` / `-fs` flag is set it will use the Staff FAQ, otherwise will use the Student FAQ as default. 

### Database Migration
1. Update env variable `DB_MIGRATE=True` in corresponding docker-compose file
    -  `docker-compose-dev.yml` (development database)  
    - `docker-compose.yml` (production database)

2. Start up container      
    - Dev: `docker-compose -f docker-compose-dev.yml up --build`
    - Prod: `docker-compose up --build`

    
3. Get inside running container: `docker exec -it chatbot bash`
4. If there is no existing migrations folder then run the following command to initialize one.     
    `flask db init --directory="{MIGRATION FOLDER}"`    
    The following migrations folders should exist:
    - `migrations` (development database)  
    - `migrations_prod` (production database)        
    

5. If this is the first time migrations have been ran on the corresponding database then mark the current state of the database as being up to date to the latest migration.      
    `flask db stamp head --directory="{MIGRATION FOLDER}"`


5. Create migration scripts
    `flask db migrate -m "..." --directory="{MIGRATION FOLDER}"` 

6. Transfer the migration folder from container to local machine:      
    `docker cp {CONTAINER ID}:/app/{MIGRATION FOLDER} .`

7. Make any necessary edits to the generated migration script.
    - Reference this [article](https://medium.com/the-andela-way/alembic-how-to-add-a-non-nullable-field-to-a-populated-table-998554003134) to "Add a Non-Nullable Field to a Populated Table"

8. Transfer the migration folder back into container: `docker cp {MIGRATION FOLDER} chatbot:/app`

9. Run the migration: `flask db upgrade --directory="{MIGRATION FOLDER}"`

10. Push updates to migration folder to Github

### Train model (DEPRECATED)

1. Start docker container 
2. Enter docker container
`docker exec -it chatbot bash`
3. Train model
`flask train_model`
4. Open new terminal tab
5. Find the id of running docker container 
`docker ps`
6. Copy file from docker container to local machine
`docker cp {id}:app/{filename}.pth . `