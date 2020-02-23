TOKEN = '1092261236:AAGz-OItiVwTyQbokHP_0BJezxYveI0GQWw'
TIMEZONE = 'Europe/Moscow'
TIMEZONE_COMMON_NAME = 'Moscow'
URL = 'https://immense-sands-85048.herokuapp.com/'

SECRET_WORD = 'iamworkatRR'

DBHOST = 'ec2-23-22-156-110.compute-1.amazonaws.com'
DBUSER = 'hhuwdcgaqmruay'
DBPASSWORD = '7e555a110871cbc96edaf607c8937eba8e043575a3fc56f0fbacbe0c1199e34b'
DBNAME = 'dchqedcsvf6170'
DBPORT = '5432'
DBCHARSET = 'utf8mb4'
DATABASELINK = "postgres://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}".format(USER=DBUSER, PASSWORD=DBPASSWORD,
                                                                          HOST=DBHOST, PORT=DBPORT, NAME=DBNAME)
