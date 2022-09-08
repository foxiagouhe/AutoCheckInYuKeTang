import csv
import datetime
import json
import logging
import os
import time

from main import YuKeTang

if __name__ == '__main__':
    startTime = time.time()
    url = 'https://changjiang.yuketang.cn/web'
    path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.exists(path=path + '/log/' + str(datetime.date.today())):
        os.mkdir(path=path + '/log/' + str(datetime.date.today()))

    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(
        filename=path + '/log/' + str(datetime.date.today()) + '/' + 'addUser-' +
                 time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time())) + ".log",
        format="%(asctime)s - %(filename)s - %(levelname)s:%(message)s",
        level=logging.INFO,
        filemode='w',
        datefmt="%Y-%m-%d %I:%M:%S")
    logging.info("script start up\n")

    logging.info("start time: " + time.strftime("%Y-%m-%d- %H:%M:%S", time.localtime(startTime)))
    logging.info("loading user data json")
    with open(path + "/data/user_data.json", 'r') as uj:
        user_data_list = json.loads(uj.read())

    logging.info("loading add user csv")
    with open(path + '/data/adduser.csv') as f:
        user_data_csv_list = [x for x in csv.DictReader(f)]
        logging.info("read csv finished, start execute all user")
        while len(user_data_csv_list) > 0:
            try:
                user = user_data_csv_list.pop()
                logging.info("now execute user: " + user['name'])
                tencent = YuKeTang(url, user['user'], user['pwd'], user['type'])
                tencent.re_start()
                user_data_json = tencent.saveData()
                user_data_json['apikey'] = user['apikey']
                user_data_list.append(user_data_json)
                tencent.end()
                logging.info("user " + user['name'] + ' execute success')
                logging.info('sleep 45s')
                time.sleep(45)
            except Exception:
                logging.info("user " + user['name'] + ' execute failed')
                user_data_csv_list.insert(0, user)
                tencent.end()
                logging.info('sleep 45s')
                time.sleep(45)
        with open(path + "/data/user_data.json", 'w') as ad:
            logging.info('override user data json success')
            json.dump(user_data_list, ad, ensure_ascii=False)

    logging.info("add to user csv")
    with open(path + '/data/user.csv', 'a+') as f:
        cw = csv.writer(f)
        with open(path + '/data/adduser.csv', 'r') as a:
            add_user_list = csv.DictReader(a)
            for ul in add_user_list:
                cw.writerow(list(ul.values()))

        logging.info("clear adduser csv")
        with open(path + '/data/adduser.csv', 'w') as p:
            p.writelines('name,user,pwd,type,apikey')

    endTime = time.time()
    logging.info("end time: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(endTime)))
    logging.info("total run time(s): " + str(endTime - startTime))
