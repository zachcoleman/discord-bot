
.PHONY: docker-build
docker-build:
	docker build -t gitbot .

.PHONY: docker-run
docker-run:
	docker run -v ~/discord-bot/data:/app/data/ --net=host gitbot