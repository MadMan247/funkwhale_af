# Protect your front against bots

We provide an [anubis](https://anubis.techaro.lol/) setup that you can use to protect your frontend against bots. This guide shows how to setup Anubis as a new layer after the reverse proxy, Anubis do not manage tls and only forward traffic from the reverse proxy to the front container. The reverse proxy will sent it's requests to Anubis, which will do a challenge to the client if needed.

1. Navigate to the project directory.

   ```{code-block} sh
   cd /srv/funkwhale
   ```

2. Set a `FUNKWHALE_VERSION` variable to your installation version (can be found on the `.env` file).

```{parsed-literal}
export FUNKWHALE_VERSION={sub-ref}`version`
```

3. Enable the anubis service on `docker-compose.yml`. This container will be exposed to the internet instead of the `front` service.

4. Remove port mapping from the `front` container (delete or comment this lines).

   ```{code-block} sh
   ports:
       - '${FUNKWHALE_API_IP}:${FUNKWHALE_API_PORT}:8080'
   ```

5. Get the bot policy files.

```{code-block} sh
  curl -L -o /srv/funkwhale/botPolicy.yaml "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/${FUNKWHALE_VERSION}/deploy/botPolicy.yaml"
```

```{note}
Backend endpoints are protected though [rate limiting](..rate-limiting). That's why they are excluded from the `botPolicy.yaml` file.
```

6. Restart everything

```{code-block} sh
  docker compose stop
  docker compose up
```
