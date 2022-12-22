# First, make sure that Python is installed on your Raspberry Pi
python3 --version

# If Python is not installed, you can install it by running the following command:
apt-get install python3 -y

# Next, install pip, which is the package manager for Python
apt-get install python3-pip -y

# Now you can use pip to install Flask and any other dependencies for your website
pip3 install flask

pip3 install -r "requirements.txt"


set -e&
apt-get update && apt-get install default-mysql-server default-mysql-client&
mysql_secure_installation&
mysql -u myuser -pmypassword mydb < dump.sql
# Start the server using the Flask app script
python3 waitress_server.py