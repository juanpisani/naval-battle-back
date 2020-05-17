SERVER_UBUNTU_DIR_DEV=ubuntu@ec2-18-218-17-31.us-east-2.compute.amazonaws.com
PROJECT_NAME=project
GIT_PROJECT_NAME=project-back
GIT_URL=https://oauth2:PtZruczF7cXCQ8DD_med@gitlab.com/siriussystem/project/project-back.git

ssh -i "project-dev.pem" $SERVER_UBUNTU_DIR_DEV "cd && \
	cd $PROJECT_NAME/'$PROJECT_NAME'env && \
	git clone --single-branch --branch qa $GIT_URL && \
	source bin/activate && \
	pip install django gunicorn psycopg2-binary && \
	cd '$GIT_PROJECT_NAME' && \
	pip install -r requirements.txt && \
	sudo cp deploy/gunicorn.socket /etc/systemd/system/ && \
	sudo cp deploy/gunicorn.service /etc/systemd/system/ && \
	sudo cp deploy/$PROJECT_NAME /etc/nginx/sites-available/$PROJECT_NAME && \
	sudo ln -s /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/ && \
	sudo systemctl daemon-reload && \
	sudo systemctl start gunicorn.socket && \
	sudo systemctl enable gunicorn.socket && \
	sudo systemctl restart nginx"