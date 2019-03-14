import boto3
import json
from datetime import datetime
import calendar
import random
import time
import pandas as pd

my_stream_name = 'Kinesis_stream_name'
kinesis_client = boto3.client('kinesis', region_name='us-east-1')

df = pd.read_csv('dados/df_min_max_scaling_truncated.csv')

def put_to_stream(thing_id, property_value, property_timestamp):
    payload = {
                'prop': str(property_value),
                'timestamp': str(property_timestamp),
                'id': thing_id
              }

    print( payload)

    put_response = kinesis_client.put_record(
                        StreamName=my_stream_name,
                        Data=json.dumps(payload),
                        PartitionKey=thing_id)

                       
for index, row in df[332:].iterrows():
    put_to_stream(str(row['time']), row['v2'], calendar.timegm(datetime.utcnow().timetuple()))
    time.sleep(5)

