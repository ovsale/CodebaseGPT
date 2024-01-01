# CodebaseGPT

## Overview
CodebaseGPT is an application that allows developers to chat with whole codebase of a software project.

The main feature of CodebaseGPT is that it creates brief descriptions of each project file and provides these descriptions to the LLM in the first system prompt. Thus, the model has generalized information about whole project in its context at each step of communication with the user.

Fragment of the first system prompt:

```
Project files with its descriptions:

./codebasegpt/__init__.py
File is empty

./codebasegpt/app.py
The app.py file contains the main function that initializes the app state, performs
initialization, description, and chat logic based on the app state.

./codebasegpt/app_config.py
app_config.py: Pydantic BaseModel for project configuration with default values for
project folder, models, file inclusion/exclusion, gitignore, comments removal, and
verbose logging.

./codebasegpt/app_state.py
The app_state.py file contains a class AppState with attributes for app and project
configurations, file paths, project state, and OpenAI integration.

...
```

Also, the 🤖 bot can load any project file or search through the codebase (both semantically and textually) when needed to answer user questions. It can even update project files (with confirmation) upon user request. And, of course, it supports all programming languages.

## Chat example
Let's check CodebaseGPT code for external connectivity security. CodebaseGPT will explore its own code:
```
👤 You: is this app accessing the web somehow?

Waiting for model response...

find_in_files function, query: requests.get, isCaseSensitive: False, page: 0
result:
Nothing found

Waiting for model response...

Next input cost: $0.01 (system: $0.01, chat: $0.00)
Request cost: $0.04 (input: $0.03, output: $0.00)
Session cost: $0.04

🤖 Bot: The app does not appear to be accessing the web using the `requests.get` method,
as no instances of this method were found in the project files. If the app is accessing
the web, it might be using a different method or library. Would you like me to search for
other common web access methods or libraries?

👤 You: yes please

Waiting for model response...

find_in_files function, query: http.client, isCaseSensitive: False, page: 0
result:
Nothing found

find_in_files function, query: urllib, isCaseSensitive: False, page: 0
result:
Nothing found

find_in_files function, query: urlopen, isCaseSensitive: False, page: 0
result:
Nothing found

find_in_files function, query: requests, isCaseSensitive: False, page: 0
result:
Nothing found

Waiting for model response...

Next input cost: $0.02 (system: $0.01, chat: $0.00)
Request cost: $0.04 (input: $0.04, output: $0.01)
Session cost: $0.08

🤖 Bot: After searching for common web access methods and libraries, including
`http.client`, `urllib`, `urlopen`, and `requests`, no instances of these were found in
the project files. This suggests that the app does not contain code for accessing the web
using these methods or libraries. If there are any other specific methods or libraries
you would like me to check for, please let me know.

👤 You: 
```
Yes. 🤖 is correct.

## Installation
1. Ensure python 3 is installed. App has been tested with 3.12
```
python --version
```

2. Create a python virtual environment for project and activate it. In case of venv:
```
python -m venv venv  
source venv/bin/activate
```

3. Install project dependencies
```
pip install -r requirements.txt
```

4. Set OPENAI_API_KEY environment variable with your OpenAI key, or create .env file in project root with it
```
OPENAI_API_KEY=........
```  

5. Run app
```
python main.py
```

6. Follow app prompts

## First start and config files
CodebaseGPT can store information about multiple projects so it generates several key files in the '_data' folder to support it:
```
CodebaseGPT/_data
├── app_config.json
└── project_folder
    ├── proj_config.json
    └── proj_state.json
```
During first start with new project, application will ask you to edit config files it created and then restart the application.  
Example of application configuration file:  
**app_config.json**
```
{
    "proj_folder": "CodebaseGPT",          <- current project
    "description_model": "gpt-3.5-turbo-1106", <- model to create file descriptions. 3.5 is enough
    "chat_model": "gpt-4-1106-preview",        <- model to power chat. 3.5 is NOT enough 
    "default_project_include": [               <- default values for new project config
        "README.md",
        "package.json"
    ],
    "default_project_exclude": [],
    "default_project_gitignore": true,
    "default_project_remove_comments": false,
    "verbose_log": false                        // detailed log
}
```
Example of project configuration file when CodebaseGPT explores itself code:  
**proj_config.json**
```
{
    "path": "here will be path to CodebaseGPT on your computer",
    "include": [        <- glob patterns to include
        "codebasegpt/**/*",
        "test/**/*",
        "main.py",
        "test.py",
    ],
    "exclude": [],      <- glob patterns to exclude
    "gitignore": true,
    "remove_comments": true
}
```

Lets ask CodebaseGPT about other properties of this file:
```
👤 You: what 'gitignore' property means in proj_config.json?

Waiting for model response...

get_file function, path: ./codebasegpt/proj_config.py
returned ./codebasegpt/proj_config.py file content

Waiting for model response...

Next input cost: $0.02 (system: $0.01, chat: $0.00)
Request cost: $0.04 (input: $0.03, output: $0.00)
Session cost: $0.04

🤖 Bot: The 'gitignore' property in the `ProjConfig` class within the `proj_config.py`
file is a boolean attribute. When set to `True`, it indicates that the project
configuration should take into account the `.gitignore` file present in the project
directory. This means that the files and directories specified in the `.gitignore` file
will be excluded from certain operations, such as file searches, statistics gathering,
and other project management tasks. If set to `False`, the `.gitignore` file will be
ignored, and all files will be considered regardless of the `.gitignore` settings.

👤 You: and remove_comments?

Waiting for model response...

Next input cost: $0.02 (system: $0.01, chat: $0.00)
Request cost: $0.02 (input: $0.02, output: $0.00)
Session cost: $0.06

🤖 Bot: The `remove_comments` property in the `ProjConfig` class within the
`proj_config.py` file is also a boolean attribute. When set to `True`, it indicates that
comments should be removed from the code files when processing them. This could be
relevant for operations such as generating descriptions, creating summaries, or any other
task where the actual code content is needed without the comments. If set to `False`, the
comments within the code files will be preserved during these operations.

👤 You: 
```
Yes. 🤖 is correct. If .gitignore file is present in project folder and "gitignore" is true - files and directories specified in the '.gitignore' file will be excluded from set of included (via "include") files. And when "remove_comments" is true files will be cleared from comments when loaded for any purpose. 

## Commands
Lets ask CodebaseGPT about what commands it supports during chat phase:
```
👤 You: what commands user can use when chatting with bot?

Waiting for model response...

get_file function, path: ./codebasegpt/chat_logic.py
returned ./codebasegpt/chat_logic.py file content

Waiting for model response...

Next input cost: $0.05 (system: $0.01, chat: $0.04)
Request cost: $0.07 (input: $0.07, output: $0.01)
Session cost: $0.07

🤖 Bot: Users can interact with the chatbot using the following commands:

1. `/exit` - This command allows the user to exit the chat session.
2. `/clear` - This command clears the message history except for the initial system
prompt.

Additionally, the chatbot can perform several functions based on user requests:

- `get_file` - Loads file content for user inspection. The user needs to provide the path
to the file.
- `find_files_semantic` - Searches for files using semantic (embedding-based) search. The
user needs to provide a search string and can page through results.
- `find_in_files` - Searches for a query string in files' content. The search can be
case-sensitive or case-insensitive, and the user can page through results.
- `update_file` - Updates or creates a file. The user needs to provide the path to the
file and the new content.

These functions are integrated into the chatbot's responses and are used to assist the
user in interacting with the software project.

👤 You: 
```
Yes. 🤖 is correct.  
For now CodebaseGPT supports two commands:
- /exit - exits app
- /clear - clears chat history. All messages but first system prompt (with list of all files with its descriptions) will be removed. It useful then you change chat subject and like to reduce cost. 

## Cost log explanation:
```
Next input cost: $0.02 (system: $0.01, chat: $0.00) <- cost of all input tokens = cost
of first system prompt + cost of chat messages.

Request cost: $0.04 (input: $0.03, output: $0.00)   <- cost of last request = cost of
input tokens + cost of output tokens

Session cost: $0.04                                 <- total session cost so far
```

**Happy chatting!**

