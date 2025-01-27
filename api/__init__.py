from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from chatbot.chatbot_interface import ChatbotInterface
from .database import db, FAQ, Staff
from .routes import routes
from .commands import backup_faq, train_model, chat, view_intents, test_model, backup_faq, get_data
from enums import Mode
import json
from flask_apscheduler import APScheduler
from github import Github, Auth

# app.config['CORS_HEADERS'] = 'Content-Type'
migrate = Migrate()
cors = CORS()

scheduler = APScheduler()

@scheduler.task("cron", id="update_streamlit_repo", hour=0, minute=0, misfire_grace_time=900) 
def update_streamlit_repo():
    print("Updating Streamlit chatbot repo")
    REPO_NAME = "Panchofdez/ask-fyeo-chatbot-streamlit"
    BRANCH_NAME = "main"

    auth = Auth.Token(os.environ.get('GIT_TOKEN'))
    g = Github(auth=auth)
    
    # Get the repository
    repo = g.get_repo(REPO_NAME)

    # Get the reference to the branch
    branch_ref = repo.get_git_ref(f"heads/{BRANCH_NAME}")

    # Get the current commit of the branch
    latest_commit = repo.get_git_commit(branch_ref.object.sha)

    # Create a tree identical to the current commit's tree
    tree = repo.get_git_tree(latest_commit.tree.sha)

    # Create a new commit with no changes
    empty_commit_message = "Keep Streamlit app awake (empty commit)"
    empty_commit = repo.create_git_commit(
        message=empty_commit_message,
        tree=tree,
        parents=[latest_commit]
    )
    # Update the branch reference to point to the new commit
    branch_ref.edit(sha=empty_commit.sha)

    print(f"Empty commit pushed: {empty_commit.sha}")
    
    g.close()


def create_app(mode=Mode.PROD,chatbot_mode=Mode.PROD,chatbot_type=ChatbotInterface.bow_model,init=False):
    app = Flask(__name__)

    if mode == Mode.PROD:
        #database string needs to start with postgresql:// not postgres:// which is what heroku sets it to by default and is unchangeable 
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
        app.debug = False
    else:
        load_dotenv() #load environment variable
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL_DEV')#***REMOVED***
        app.debug = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('MY_SECRET_KEY')
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }

    db.init_app(app)    
    cors.init_app(app)
    migrate.init_app(app, db)
    
    scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()
    
    update_streamlit_repo()
    
    with app.app_context():
        if not init:
            data = get_data()
            chatbot = ChatbotInterface(type=chatbot_type, data=data, mode=chatbot_mode)
            app.config["chatbot"] = chatbot
        else:
            #initialize the tables in postgres
            try:
                db.create_all()
                with open('intents.json', 'r', encoding='utf8') as f:
                    file_data = json.loads(f.read())
                    for q in file_data['intents']:
                        tag = q['tag']
                        patterns = q['patterns']
                        responses = q['responses']
                    
                        if len(list(filter(lambda p: p.find('|') != -1, patterns))) > 0 or len(list(filter(lambda r: r.find('|') != -1, responses))) > 0:
                            continue

                        patterns = '|'.join(patterns)
                        responses = '|'.join(responses)
                        
                        new_faq = FAQ(tag=tag, patterns=patterns, responses=responses)
                        db.session.add(new_faq)
                        db.session.commit()

                new_staff = Staff(email="pancho.fernandez@ryerson.ca")
                db.session.add(new_staff)
                db.session.commit()
            except Exception as e:
                print("ERROR", e)
            

    
    app.register_blueprint(routes, url_prefix='')
    app.cli.add_command(train_model)
    app.cli.add_command(chat)
    app.cli.add_command(view_intents)
    app.cli.add_command(test_model)
    app.cli.add_command(backup_faq)

    return app 






