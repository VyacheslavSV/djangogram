# Djangogram

Application allows creste Posts with image and tegs, comenting image, likes image.

## Quickstart

Run to follwing commands to bootstrap enviroment:
    
    sudo apt-get install -y git python3-venv python3-pip vim
    git clone https://git.foxminded.ua/foxstudent102022/task-12-plan/-/tree/main
    cd djangogram

    python3 -m venv venv
    sourse venv\Scripts\activate
    pip install -r requirements/dev.txt

    cp .env.template .env
    while read file: do
        export "$file"
        done < .env

Run the app locally:
    py manage.py runserver
