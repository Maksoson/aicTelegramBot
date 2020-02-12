TOKEN = '1092261236:AAGz-OItiVwTyQbokHP_0BJezxYveI0GQWw'
TIMEZONE = 'Europe/Moscow'
TIMEZONE_COMMON_NAME = 'Moscow'
URL = 'https://immense-sands-85048.herokuapp.com/'

DBHOST = 'ec2-52-202-185-87.compute-1.amazonaws.com'
DBUSER = 'pilycauudbivdy'
DBPASSWORD = '24216c938f74ef3fc5f3c87caea1421c3de81f64be4301595ea6d921024f4da5'
DBNAME = 'd8eb3mv6o3of1t'
DBPORT = '5432'
DBCHARSET = 'utf8mb4'
DATABASELINK = "postgres://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}".format(USER=DBUSER, PASSWORD=DBPASSWORD,
                                                                          HOST=DBHOST, PORT=DBPORT, NAME=DBNAME)
