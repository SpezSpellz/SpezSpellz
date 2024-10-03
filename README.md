## SpezSpellz: A Django-based web application for sharing spells and rituals.
[![Lint](https://github.com/SpezSpellz/SpezSpellz/actions/workflows/lints.yml/badge.svg)](https://github.com/SpezSpellz/SpezSpellz/actions/workflows/lints.yml) [![Unit tests](https://github.com/SpezSpellz/SpezSpellz/actions/workflows/tests.yml/badge.svg)](https://github.com/SpezSpellz/SpezSpellz/actions/workflows/tests.yml)  
### Key Features
- Spell and rituals Upload - Enable users to upload spells and rituals with details like spell name, description, ingredients, steps, etc.
- Spell and rituals Search - Allow users to search for spells and rituals based on keywords, categories, or tags.
- Ratings and Reviews - Each spell/ritual will include user ratings and reviews as well as comments.
- Spell Categories and Tags - spells and rituals will be given tags and categories making it easier to search for them.
- Provide users with a profile page where they can manage their uploaded spells, reviews, ratings, and account settings. The account settings will consist of stuff like privacy settings, notification settings, about me, and profile picture.
- Allow users to comment on spells to share additional insights or ask questions.
- Enable users to favorite or bookmark spells for quick access later.
- Provide personalized spell recommendations based on user activity, preferences and ratings.
- Allow users to sort and filter spells based on criteria like popularity, ratings, newest, etc.
- A notification system to notify the user when certain actions need to be performed when doing a ritual, The uploader will have to specify these times.
- Spell history - view spells that have been viewed in the past.
## Installation
### Prerequisites
Before installing the SpezSpellz app, make sure you have the following software installed on your system:

- Python 3.11+
- Git
- pip (Python package installer)

### Installation Steps

1. Clone the repository:
   - `$ git clone https://github.com/SpezSpellz/SpezSpellz.git`

2. Navigate to the project directory:
   - `$ cd SpezSpellz

3. Create and activate a virtual environment:
   - `$ python -m venv .venv`
   - `$ source ./.venv/bin/activate` (Linux/Mac) or `.\venv\Scripts\activate` (Windows)

4. Install the required packages:
   - `$ pip install -r requirements.txt`

5. Run database migrations:
   - `$ python manage.py migrate`
6. Set environment (Optional):
   - `$ cat sample.env > .env` (Linux/Mac) or `type sample.env > .env` (Windows)
   - Edit the `.env` file with the editor of your choice.  
   The details of how to set each variable is in the .env file.  
   `$ nvim .env`
7. Run tests (Optional):
   - `$ python manage.py test`

### Starting the Development Server
To start the development server, run the following command:

- `$ python manage.py runserver`

Access the application at <http://127.0.0.1:8000/>.

### Data in data fixtures
Currently, have 2 data fixtures called `dummy-spell.json` and `dummy-user.json`.
Here is what they contain

**Spell**

|  Title  |User |
|:-------:|:---:|
| Spell 1 |demo1|
| Spell 2 |demo1|

**User**

| Username | Password  |
|:--------:|:---------:|
|  demo1   | demo_man1 |

**Admin user**
| Username | Password  |
|:--------:|:---------:|
| admin    | password  |

## Project Documents
The project documents below are all available in the [Wiki](../../wiki/Home).
