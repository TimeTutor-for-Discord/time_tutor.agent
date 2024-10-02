# Python環境情報
PYTHON := python3
VENV := venv
REQUIREMENTS := requirements.txt
APP := writeStudyTime.py


#==================================================
# ローカル環境で直接APPを動かすためのターゲット群
#==================================================
# preparation: 仮想環境セットアップと依存関係解決
.PHONY: _preparation 
_preparation: 
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)

.PHONY: venv/activate
venv/activate: _preparation 
	@echo "Activating virtual environment and installing dependencies..."
	$(VENV)/bin/pip3 install --upgrade pip
	$(VENV)/bin/pip3 install -r $(REQUIREMENTS)

# アプリケーション実行
.PHONY: run
run: venv/activate 
	@echo "Running $(APP)..."
	$(VENV)/bin/$(PYTHON) $(APP)

# ビルドターゲット: バイナリまたはパッケージを作成する
.PHONY: build
build: venv/activate
	@echo "Building the application..."
	# ここにビルドプロセスを定義（例: パッケージの作成、Dockerイメージのビルドなど）
	@echo "Build complete!"

# テストターゲット: アプリケーションのテストを実行
.PHONY: test
test: venv/activate
	@echo "Running tests..."
	$(VENV)/bin/$(PYTHON) -m pytest tests

# 仮想環境をクリーンアップするターゲット
.PHONY: clean
clean:
	@echo "Cleaning up the environment..."
	rm -rf $(VENV)

# helpターゲット: 使用可能なターゲットを表示
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make run        - Run the application"
	@echo "  make build      - Build the application"
	@echo "  make test       - Run the tests"
	@echo "  make clean      - Clean the virtual environment"

#==============================
# localstack関連
#==============================
.PHONY: local/setup
local/setup: venv/activate
	@docker run --rm -it -p 4566:4566 -p 4510-4559:4510-4559 localstack/localstack
	@aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name test-queue
# ❯ aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name test-queue
# {
#     "QueueUrl": "http://sqs.ap-northeast-1.localhost.localstack.cloud:4566/000000000000/test-queue"
# }

.PHONY: local/conndb
local/conndb:
	@mycli -h localhost -P3306 -uroot -plocalp -Dtimetutor

.PHONY: update_submodules
update_submodules:
	@bash bin/submodules/getToken.sh
	# git submodule add https://github.com/TimeTutor-for-Discord/time_tutor.schema.git schema
	git submodule update --remote --rebase

# docker run --name timetutor-mysql -e MYSQL_ROOT_PASSWORD=localp -e MYSQL_DATABASE=timetutor -p 3306:3306 -d mysql

#==============================
# Json schema関連
#==============================
.PHONY: update_models
update_models:
	bash bin/models/update.sh   
