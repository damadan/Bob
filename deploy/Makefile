.PHONY: up down restart logs ps
up:
	docker compose --env-file ./.env.prod -f docker-compose.prod.yml up -d --build
down:
	docker compose --env-file ./.env.prod -f docker-compose.prod.yml down
restart:
	docker compose --env-file ./.env.prod -f docker-compose.prod.yml restart
logs:
	docker compose --env-file ./.env.prod -f docker-compose.prod.yml logs -f --tail=200
ps:
	docker compose --env-file ./.env.prod -f docker-compose.prod.yml ps
