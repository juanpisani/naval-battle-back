SERVER_UBUNTU_DIR_DEV=ubuntu@ec2-18-218-17-31.us-east-2.compute.amazonaws.com
PROJECT_NAME=project

echo 'Starting instance config for '$SERVER_UBUNTU_DIR_DEV

ssh -i "project-dev.pem" $SERVER_UBUNTU_DIR_DEV "cd && \
	sudo apt update && \
	sudo apt install nginx && \
	sudo ufw allow 'Nginx HTTP' && \
	sudo apt install python3-pip python3-dev libpq-dev curl mysql-client-core-5.7 mysql-server libmysqlclient-dev && \
	sudo -H pip3 install --upgrade pip && \
	sudo -H pip3 install virtualenv && \
	mkdir $PROJECT_NAME && \
	cd $PROJECT_NAME && \
	virtualenv '$PROJECT_NAME'env && \
	source '$PROJECT_NAME'env/bin/activate"
