# First, make sure that Python is installed on your Raspberry Pi
python3 --version

# If Python is not installed, you can install it by running the following command:
sudo apt-get install python3

# Next, install pip, which is the package manager for Python
sudo apt-get install python3-pip

# Now you can use pip to install Flask and any other dependencies for your website
pip3 install flask

pip3 install -r "requirements.txt"


set -e&
apt-get update && apt-get install mysql-server mysql-client&
mysql_secure_installation&
mysql -u myuser -pmypassword mydb < dump.sql
# Start the server using the Flask app script
python3 waitress_server.py