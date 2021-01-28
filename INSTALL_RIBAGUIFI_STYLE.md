We need have python3.6

#Install Packages
```bash
apt=(
    bind9utils 
    ca-certificates 
    gettext 
    libcrack2-dev
    libxml2-dev
    libxslt1-dev
    ssh-client
    wget
    xvfb
    zlib1g-dev
    git
    iceweasel
    dnsutils
    postgresql-contrib
)
sudo apt-get install --no-install-recommends -y ${apt[@]}
```

It is necessary install *wkhtmltopdf*
You can install it from https://wkhtmltopdf.org/downloads.html

Clone this repository
```bash
git clone https://github.com/ribaguifi/django-orchestra
```

Prepare env and install requirements
```bash
cd django-orchestra
python3.6 -m venv env
source env/bin/activate
pip3 install --upgrade pip
pip3 install -r total_requirements.txt
pip3 install -e .
```

Configure project using environment file (you can use provided example as quickstart):
```bash
cp .env.example .env
```

Prepare your Postgres database (create database, user and grant permissions):
```sql
CREATE DATABASE myproject;
CREATE USER myuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE myproject TO myuser;
```

Prepare a new project:

```bash
django-admin.py startproject PROJECT_NAME --template="orchestra/conf/ribaguifi_template"
```

Run migrations:                                                                                         
```bash                                                                                                 
python3 manage.py migrate                                                                               
```

(Optional) You can start a Django development server to check that everything is ok.                    
```bash                                                                                                 
python3 manage.py runserver                                                                             
```
 
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
