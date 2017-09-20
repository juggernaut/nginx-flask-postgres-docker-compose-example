This is a working example of a multi-container flask application with Postgres as the database fronted by the nginx reverse proxy. See my [blog post](http://www.ameyalokare.com/docker/2017/09/20/nginx-flask-postgres-docker-compose.html) for a detailed explanation.

## Usage

1. Bootstrap the DB
```bash
$ docker-compose up -d db
$ docker-compose run --rm flaskapp /bin/bash -c "cd /opt/services/flaskapp/src && python -c  'import database; database.init_db()'"
```

2. Bring up the cluster
```bash
$ docker-compose up -d
```

3. Browse to localhost:8080 to see the app in action.
