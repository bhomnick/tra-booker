SHELL=/bin/bash
CYAN=\\033[0;36m
NC=\\033[0m

# Docker-compose
build: ## Build all docker images.
	docker-compose build
test: ## Run test suite.
	docker-compose run core bash -c "bin/test.sh $(M)"
clean: ## Clean the application.
	find . -name '*.py[co]' -delete
	find . -type d -name "__pycache__" -delete
help: ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
