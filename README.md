# goitneo-cs-hw-06

## Prerequisites

0. Clone this repository to your local computer.
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install [Docker Compose](https://docs.docker.com/compose/install/)
3. Install [Mongo Compass](https://www.mongodb.com/products/tools/compass)

## HOWTO

Run the following command to start the services defined in the [docker-compose.yml](./docker-compose.yaml):

```shell
docker-compose up
```

Or, if you prefer to run in detached mode (in the background):

```shell
docker-compose up -d
```

You can also run [main.py](./main.py) with the `--help` switch for more information on how to use it. Please note that this script reads credentials from the [.env](./.env) file.

```shell
python3 ./main.py --help
```

To stop and delete all resources that were created using the `docker-compose up` command in the current Docker Compose project, run the command:

```shell
docker-compose down --volumes
```

Use [Mongo Compass](https://www.mongodb.com/products/tools/compass) to connect to MongoDB to find your Mongo database. The connection credentials can be found in the file [.env](./.env).
