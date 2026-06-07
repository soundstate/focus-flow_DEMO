.PHONY: integration-test integration-stack-up integration-stack-down integration-full

integration-stack-up:
	docker-compose up -d --build
	@echo "Waiting ~25s for healthchecks..."
	@sleep 25
	@docker-compose ps

integration-stack-down:
	docker-compose down

integration-test:
	pytest tests/integration/ -o testpaths=tests/integration -o pythonpath= -v

integration-full: integration-stack-up integration-test
