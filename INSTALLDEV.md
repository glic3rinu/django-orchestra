Development and Testing Setup
-----------------------------
If you are planing to do some development you may want to consider doing it under the following setup


1. Install Docker
    ```sh
    curl https://get.docker.com/ | sh
    ```


2. Build a new image, create and start a container
    ```bash
    curl -L http://git.io/orchestra-Dockerfile > /tmp/Dockerfile
    docker build -t orchestra /tmp/
    docker create --name orchestra -i -t -u orchestra -w /home/orchestra orchestra bash
    docker start orchestra
    docker attach orchestra
    ```


3. Deploy django-orchestra development environment, inside the container
    ```bash
    bash <( curl -L http://git.io/orchestra-deploy ) --dev
    ```

3. Nginx should be serving on port 80, but Django's development server can be used as well:
    ```bash
    cd panel
    python3 manage.py runserver 0.0.0.0:8888
    ```


5. To upgrade to current master just re-run the deploy script
    ```bash
    git pull origin master
    bash <( curl -L http://git.io/orchestra-deploy ) --dev
    ```
