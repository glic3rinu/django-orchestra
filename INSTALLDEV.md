Development and Testing Setup
-----------------------------
If you are planing to do some development you may want to consider doing it under the following setup


1. Create a basic [LXC](http://linuxcontainers.org/) container, start it and get inside.
    ```bash
    wget -O /tmp/create.sh \
      https://raw.github.com/glic3rinu/django-orchestra/master/scripts/container/create.sh
    sudo bash /tmp/create.sh
    sudo lxc-start -n orchestra
    # root/root
    ```

2. Deploy Django-orchestra development environment **inside the container**
    ```bash
    # Make sure your container is connected to the Internet
    # Probably you will have to configure the NAT first:
    #   sudo iptables -t nat -A POSTROUTING -s `container_ip` -j MASQUERADE
    wget -O /tmp/deploy.sh \
      https://raw.github.com/glic3rinu/django-orchestra/master/scripts/container/deploy.sh
    cd /tmp/ # Moving away from /root before running deploy.sh
    bash /tmp/deploy.sh
    ```
    Django-orchestra source code should be now under `~orchestra/django-orchestra` and an Orchestra instance called _panel_ under `~orchestra/panel`


3. Nginx should be serving on port 80, but Django's development server can be used as well:
    ```bash
    su - orchestra
    cd panel
    python manage.py runserver 0.0.0.0:8888
    ```

4. A convenient practice can be mounting `~orchestra` on your host machine so you can code with your favourite IDE, sshfs can be used for that
    ```bash
    # On your host
    mkdir ~<user>/orchestra
    sshfs orchestra@<container-ip>: ~<user>/orchestra
    ```

5. To upgrade to current master just re-run the deploy script
    ```bash
    sudo ~orchestra/django-orchestra/scripts/container/deploy.sh
    ```

