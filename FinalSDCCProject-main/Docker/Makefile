all:
	cd app && docker build -t docker-app .
	cd face-rec && docker build -t docker-face-rec .
	cd mail && docker build -t docker-mail .
	docker-compose up
