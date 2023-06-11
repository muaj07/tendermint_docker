
# List all containers (only IDs)
docker ps -aq
# Stop all running containers
docker stop $(docker ps -aq)
# Remove all containers
docker rm $(docker ps -aq)
# Remove all images
docker rmi $(docker images -q)

cd app
docker build -t my_image .
cd ../swarm/tendermint
docker build -f DOCKER/Dockerfile -t "tendermint/tendermint" .
# docker network create --scope swarm -d overlay --subnet=192.167.10.0/16 localnet
cd ../../
docker compose up
