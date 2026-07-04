.PHONY: up down restart train train-docker logs test

up:
	docker compose up --build -d
	@echo "Backend: http://localhost:8000"
	@echo "Grafana: http://localhost:3000 (admin/admin)"

down:
	docker compose down

restart: down up

train:
	python -m ml.pipeline

train-docker:
	docker compose exec backend python -m ml.pipeline

logs:
	docker compose logs -f

test:
	@echo "--- Health check ---"
	curl -s http://localhost:8000/ | python -m json.tool
	@echo "\n--- Search test ---"
	curl -s "http://localhost:8000/search/?query=lofi&max_results=2" | python -m json.tool
	@echo "\n--- Play test (log + SQLite persistence) ---"
	curl -s -X POST "http://localhost:8000/play/?video_id=kPa7bsKwL-c&user_id=test_user"
	curl -s -X POST "http://localhost:8000/play/?video_id=lTRiuFIWV54&user_id=test_user"
	@echo "\n--- Recommend (needs model trained) ---"
	curl -s "http://localhost:8000/recommend/user?user_id=user_1" | python -m json.tool
