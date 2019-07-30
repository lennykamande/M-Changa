import pymysql
import sys
import datetime
import pytz
import json
import requests
import urllib

from air_settings import *

rds_host = "secure.changa.db.prod"
name = "root"
password = "!@pplasddHXKL)_"
db_name = "sec_changa"
port = 3306

internal_apikey = INTERNAL_APIKEY


try:
    connection = pymysql.connect(
        rds_host, user=name,
        passwd=password,
        db=db_name,
        connect_timeout=50)
    # print "connected to db"
except:
    # By lenny if this is python 3 this i
    print "DB connection failed"
    # return "Database connection failed"
    sys.exit()


# Set timezone to 'Africa/Nairobi' timezone
tz = pytz.timezone(TIMEZONE)
now = datetime.datetime.now(tz)


"""
Main Lambda handler: Start of lambda execution
"""


def lambda_handler(event, context):
    # def get_fundraisers():
    stepper = {}
    stepper[0] = 3
    stepper[1] = 5
    stepper[2] = 7
    stepper[3] = 9
    stepper[4] = 11

    response_data = "Uncaptured Response"

    for val in stepper:
        contributor_counter = stepper[val]

        if (contributor_counter == ""):
            response_data = "Unknown Function Call"
        else:
            # get all fundraiser with count contributor_counter
            counter_status = {}
            with connection.cursor(pymysql.cursors.DictCursor) as cur:
                # get now date time
                counter_status[3] = "1"
                counter_status[5] = "2"
                counter_status[7] = "3"
                counter_status[9] = "4"
                counter_status[11] = "5"

                if contributor_counter in counter_status:
                    s_counter = counter_status[contributor_counter]
                else:
                    return "Invalid Request Counter"

                v_sql = "SELECT con.campaign_id, cc.number, count(con.contributor_id) AS con_count FROM campaigns cc " \
                        "JOIN contributors con on con.campaign_id = cc.campaign_id " \
                        "LEFT JOIN airtime_logs cal ON cal.phone_number = cc.number AND cal.airtime_channel = '"+str(s_counter)+"' " \
                        "WHERE cal.phone_number IS NULL AND cc.status = 1 AND con.paid_amt > 0 AND cc.number > 1 " \
                        "GROUP BY campaign_id HAVING con_count = '"+str(contributor_counter)+"' " \
                        "ORDER BY campaign_id DESC LIMIT 3"
                try:
                    row_count = cur.execute(v_sql)
                except pymysql.err.InternalError as e:
                    code, msg = e.args
                    print code, msg
                    row_count = 0

                if row_count > 0:
                    result = cur.fetchall()

                    for row in result:
                        airtime_params = {}
                        airtime_params['phoneNumber'] = row['number']
                        airtime_params['amount'] = "10"
                        airtime_params['request_source'] = row['campaign_id']
                        airtime_params['airtime_channel'] = s_counter
                        airtime_params['apikey'] = internal_apikey
                        airtime_params['sms_alert'] = "1"
                        airtime_params = json.dumps(airtime_params)

                        url = "https://secure.changa.co.ke/myairtime/processME"
                        headers = {'Accept': 'application/json'}
                        response_data = requests.post(
                            url, airtime_params, verify=False, headers=headers)
                        response_data = response_data.text
                        print response_data.text
                else:
                    return "No records"

    return response_data

#resp = get_fundraisers()
# print resp
