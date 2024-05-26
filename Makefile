export DOCKER_DEFAULT_PLATFORM=linux/amd64

up:
	docker-compose -f docker-compose-local.yaml up -d

down:
	docker-compose -f docker-compose-local.yaml down && docker network prune --force