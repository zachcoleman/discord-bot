
.PHONY: docker-build
docker-build:
	docker build -t gitbot .

.PHONY: docker-run
docker-run:
	docker run -v discord-bot-db:/app/data/ --net=host gitbot