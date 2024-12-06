# Develop using Docker

Funkwhale can be run in Docker containers for local development. You can work on any part of the Funkwhale codebase and run the container setup to test your changes. To work with Docker:

## Prerequisites

1. [Install Docker](https://docs.docker.com/install)
2. [Install Docker Compose](https://docs.docker.com/compose/install)
3. [Install mkcert](https://github.com/FiloSottile/mkcert#installation)
4. [Install pre-commit](https://pre-commit.com/#install)
5. Clone the Funkwhale repository to your system. The `develop` branch is checked out by default.

   ::::{tab-set}

   :::{tab-item} SSH

   ```sh
   git clone git@dev.funkwhale.audio/funkwhale/funkwhale.git
   cd funkwhale
   ```

   :::

   :::{tab-item} HTTPS

   ```sh
   git clone https://dev.funkwhale.audio/funkwhale/funkwhale.git
   cd funkwhale
   ```

   :::

   ::::

6. Activate the pre-commit hook:
   ```sh
   pre-commit install
   ```
7. Finally, initialise the environment:
   ```sh
   cp .env.example .env
   ```

## Set up the Docker environment

```{note}
Funkwhale provides a `compose.yml` file following the default file naming convention of a Docker Compose manifest. For Linux users, we assume that you finished the post-install steps to [manage Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).
```

To set up your Docker environment:

1. Create a network for federation support via the web proxy:
   ```sh
   docker network create web
   ```
2. Then build the application containers. Run this command any time there are upstream changes or dependency changes to ensure you're up-to-date.

   ```sh
   docker compose build
   ```

## Set up auxiliary services

To support ActivityPub in the local development environment, we use a
combination of auxiliary services that provide DNS-based discovery, local email delivery and web/TLS termination. This also has the benefit that we can talk to
our development instance(s) with using regular domain names.

The needed certificate is generated and installed to system and
browser with `mkcert`. Dynamic DNS resolution of local domain names in the
`funkwhale.test` zone is provided by dnsmasq. Proxying secure web traffic
between the containers and between the host and the containers is provided by
Træfik.

The services bind to the following ports on the default Docker bridge network:

| Service                                              | Description                           | Protocol | Port(s)         |
| ---------------------------------------------------- | ------------------------------------- | -------- | --------------- |
| [dnsmasq](https://dnsmasq.org/docs/dnsmasq-man.html) | Name server and recursive resolver    | DNS      | 172.17.0.1:53   |
| [Træfik v2](https://doc.traefik.io/traefik/v2.11/)   | TLS offloader and web proxy           | HTTP     | 172.17.0.1:80   |
| &nbsp;                                               | &nbsp;                                | HTTPS    | 172.17.0.1:443  |
| &nbsp;                                               | API dashboard                         | HTTP     | 172.17.0.1:8008 |
| [Mailpit](https://mailpit.axllent.org/docs/)         | Mail-delivery agent (MDA), Nullmailer | SMTP     | 172.17.0.1:1025 |
| &nbsp;                                               | &nbsp;                                | HTTP     | 172.17.0.1:8025 |

1. Create a wildcard certificate for the Common Name (CN) `funkwhale.test` and
   the Subject Alternative Name (SAN) `*.funkwhale.test` which will be
   installed into your system and browser trust stores with:
   ```sh
   mkcert -install -cert-file compose/var/test.crt -key-file compose/var/test.key "funkwhale.test" "*.funkwhale.test"
   ```
   It will be used by Træefik to secure connections, which is needed for
   ActivityPub to work locally.

Then run the network services used for convenient access to application
containers.

2. Launch the Træfik web proxy, the dnsmasq resolver and the nullmailer using
   the `net` manifest:

   ```sh
   docker compose -f compose.net.yml up -d
   ```

   <details><summary>Manage the networking services with regular <a href="https://docs.docker.com/reference/cli/docker/compose/" target="_blank">Compose life cycle commands</a>.</summary>

   :::{hint}

   ```sh
   docker compose -f compose.net.yml config
   docker compose -f compose.net.yml ps
   docker compose -f compose.net.yml stop
   docker compose -f compose.net.yml rm
   docker compose -f compose.net.yml down
   docker compose -f compose.net.yml …
   ```

   :::

   </details>

3. Add the DNS search domain for `~funkwhale.test` to your system. This allows your system to dereference our domain names `funkwhale.funkwhale.test`, `node1.funkwhale.test`, `node2.…`, `…` to the IP address of the Træfik reverse proxy listening at `172.17.0.1`.

   ::::{tab-set}

   :::{tab-item} Linux

   Considering your Linux uses systemd-resolved for local DNS resolution, apply:

   ```sh
   sudo resolvectl dns docker0 172.17.0.1
   sudo resolvectl domain docker0 '~funkwhale.test.'
   ```

   This is a temporary setting that will be lost after a reboot.

   A superuser of the system can persist this setting by providing a
   systemd service that `BindsTo=` the `docker0` device. This requires `sudo`
   privilege.

   ```sh
   sudo sh -c "umask 133; tee /etc/systemd/system/funkwhale-dns-docker0.service" <<< "[Unit]
   Description=Funkwhale per-link DNS configuration for docker0
   BindsTo=sys-subsystem-net-devices-docker0.device
   After=sys-subsystem-net-devices-docker0.device

   [Service]
   Type=oneshot
   ExecStart=/usr/bin/resolvectl dns docker0 172.17.0.1
   ExecStart=/usr/bin/resolvectl domain docker0 '~funkwhale.test.'
   ExecStopPost=/usr/bin/resolvectl revert docker0
   RemainAfterExit=yes

   [Install]
   WantedBy=sys-subsystem-net-devices-docker0.device
   "
   sudo systemctl daemon-reload
   sudo systemctl enable --now funkwhale-dns-docker0.service
   ```

   This gives you a systemd unit, whose life cycle is bound to the `docker0`
   network device.

   ```sh
   systemctl status \
     funkwhale-dns-docker0.service \
     sys-subsystem-net-devices-docker0.device
   ```

   Please refer to the manual of your distribution for other configurations,
   e.g. with system installations of netplan, systemd-networkd, NetworkManager, resolvconf or dnsmasq. Ensure the search domain is set to `funkwhale.test.`
   and the nameserver address is set to `172.17.0.1`.

   :::

   :::{tab-item} Mac

   To set up `172.17.0.1` as the search domain for the `funkwhale.test` zone on
   your mac OS system, please follow the instructions at
   [macOS: Using Custom DNS Resolvers](https://vninja.net/2020/02/06/macos-custom-dns-resolvers/).

   For [Docker on Mac](https://docs.docker.com/desktop/install/mac-install/) you
   will also need to install and use [recap/docker-mac-routes](https://github.com/recap/docker-mac-routes)
   each time the Docker VM is restarted.

   For [OrbStack]() make sure:

   - to configure the
     [Container IP ranges](https://docs.orbstack.dev/docker/network#container-ip-ranges)
     of the Docker daemon to resemble the default Docker configuration. This
     helps to recreate the expected environment for DNS + HTTPS networking.
     E.g.:

     ```json
     {
       "bip": "172.17.0.1/23",
       "default-address-pools": [
         { "base": "172.17.0.0/19", "size": 23 },
         { "base": "172.18.0.0/19", "size": 23 }
       ]
     }
     ```

   - to disable its
     [HTTPS for containers](https://docs.orbstack.dev/features/https)
     function, as we are supplying our own Træfik instance.

   :::

   ::::

:::{hint}
You can now reach your Træfik dashboard at
[http://172.17.0.1:8008/dashboard/](http://172.17.0.1:8008/dashboard/). The DNS
server will answer requests to `172.17.0.1:53`. The SMTP MDA listens on
`172.17.0.1:1025` and has a web interface at
[http://172.17.0.1:8025/](http://172.17.0.1:8025/)

When all works as expected, you can also access
[https://traefik.funkwhale.test/dashboard/](https://traefik.funkwhale.test/dashboard/)
and [https://mailpit.funkwhale.test/](https://mailpit.funkwhale.test/).
:::

:::{note}
If your `docker0` network has running containers not belonging to Funkwhale
already attached to it, comment out the `net.helpers.docker0.yml` rule in
`compose.net.yml`. Then restart the networking stack with
`docker compose -f compose.net.yml up -d`.
:::

## Set up application services

Once you have set up the dependencies, launch all services to start developing:

```sh
docker compose up -d
```

Find instructions for [starting multiple instances for federation](#running-multiple-instances) further below.

:::{tip}
This gives you access to the following:

- The Funkwhale web app on [https://funkwhale.funkwhale.test](https://funkwhale.funkwhale.test)
- The Funkwhale API on [https://funkwhale.funkwhale.test/api/v1](https://funkwhale.funkwhale.test/api/v1)
- The Django admin interface on [https://funkwhale.funkwhale.test/api/admin](https://funkwhale.funkwhale.test/api/admin)
  :::

Create a local superuser to be able to login and to manage the service:

```sh
docker compose run --rm api funkwhale-manage fw users create --superuser
```

Review the configuration:

```sh
docker compose config
```

### Set up local data for development

You can create local data to mimic a live environment.

Add some fake data to populate the database. The following command creates 25 artists with random albums, tracks, and metadata.

```sh
artists=25 # Adds 25 fake artists
command="from funkwhale_api.music import fake_data; fake_data.create_data($artists)"
echo $command | docker compose run --rm -T api funkwhale-manage shell -i python
```

This will launch a development funkwhale instance with a super user having `COMPOSE_PROJECT_NAME` as username and `funkwhale` as password. Libraries, listenings and music data will be associated with the superuser :

```sh
export COMPOSE_PROJECT_NAME=node2 ;  export VUE_PORT=8882 ; docker compose run --rm api funkwhale-manage migrate ; echo "from funkwhale_api.music import fake_data; fake_data.create_data(super_user_name=\"$COMPOSE_PROJECT_NAME\")" | docker compose run --rm -T api funkwhale-manage shell -i python ;  docker compose up

```

### Lifecycle

Recycle individual containers:

```sh
docker compose rm -sf api celeryworker; docker compose up -d api celeryworker
```

Once you're done with the containers, you can stop them all:

```sh
docker compose stop
```

If you want to destroy your containers, run the following:

```sh
docker compose down
```

Destroy all state of your containers:

```sh
docker compose down --volumes
```

Remove all state of all Funkwhale-related containers, incl. from additional
instances:

```sh
rm -rf .state/
```

### Running multiple instances

Set up as many different projects as you need. Make sure the
`COMPOSE_PROJECT_NAME` and `VUE_PORT` variables are unique per instance.

```sh
export COMPOSE_PROJECT_NAME=node2
# VUE_PORT this has to be unique for each instance
export VUE_PORT=1234
docker compose run --rm api funkwhale-manage fw users create --superuser
docker compose up -d
```

You can access your project at `https://{COMPOSE_PROJECT_NAME}.funkwhale.test`.

:::{admonition} Running and accessing multiple instances in parallel
:class: hint

You may as well address the different Compose projects by using ad hoc
environment variables:

```
COMPOSE_PROJECT_NAME=node1 VUE_PORT=1234 docker compose run --rm api funkwhale-manage fw users create --superuser
COMPOSE_PROJECT_NAME=node1 VUE_PORT=1234 docker compose up -d
```

The `node1` instance will be available at [https://node1.funkwhale.test](https://node1.funkwhale.test).

```
COMPOSE_PROJECT_NAME=node2 VUE_PORT=1235 docker compose run --rm api funkwhale-manage fw users create --superuser
COMPOSE_PROJECT_NAME=node2 VUE_PORT=1235 docker compose up -d
```

The `node2` instance will be available at [https://node2.funkwhale.test](https://node2.funkwhale.test).

Proceed freely with different sets of values for `COMPOSE_PROJECT_NAME` and
`VUE_PORT`.

:::

::::{tab-set}

:::{tab-item} Stop everything

In case you wanted to stop everything after a day's work, you can remove all
running containers:

```sh
docker compose -f compose.docs.yml rm -sf
docker compose -f compose.net.yml rm -sf
docker compose rm -sf
```

Repeat these steps for every additional instance:

```sh
COMPOSE_PROJECT_NAME=node1 docker compose rm -sf
COMPOSE_PROJECT_NAME=node2 docker compose rm -sf
COMPOSE_PROJECT_NAME=… docker compose rm -sf
```

:::

:::{tab-item} Discover projects and containers

List all currently running Compose projects to get an overview:

```sh
docker compose ls
```

Show all projects for which containers exist, including stopped ones:

```sh
docker compose ls -a
```

Ultimately Docker gives you an overview what is running:

```sh
docker ps
```

And also which containers are not running, but existing:

```sh
docker ps -a
```

Refer to the [Docker CLI documentation](https://docs.docker.com/reference/cli/docker/)
to learn how else you may interact directly with containers, when needed.

:::

::::

## Local documentation

To build the documentation locally run:

```sh
docker compose -f compose.docs.yml up -d
```

The documentation is then accessible at [https://docs.funkwhale.test](https://docs.funkwhale.test). The OpenAPI schema is available at [https://openapi.funkwhale.test](https://openapi.funkwhale.test).

Fallback ports are available for the documentation at
[http://localhost:8001/](http://localhost:8001/) and for the OpenAPI schema at
[http://localhost:8002/](http://localhost:8002/).

Maintain their life cycle with similar commands to those used to
[set up auxiliary services (point 2.)](#set-up-auxiliary-services).
