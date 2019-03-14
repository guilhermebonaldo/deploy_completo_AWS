import boto3
import pandas as pd
import io
import time
import json

athenaclient = boto3.client('athena')
s3 = boto3.resource('s3')
bucket = s3.Bucket('bucket_AWS')
s3client = boto3.client('s3')
sageclient = boto3.client('sagemaker-runtime')



def faz_query():
	
	query_ = 'SELECT * from teste ORDER BY time DESC LIMIT 300'
	database_ = 'nome_database_athena'
	bucket_ = 'output_bucket_name'
	output_bucket_ = 's3://output_bucket_name/queries/'
	
    response = athenaclient.start_query_execution(
            QueryString= query_,
            QueryExecutionContext={
                'Database': database_
                },
            ResultConfiguration={
                'OutputLocation': output_bucket_,
                }
            )
    execution_id = response['QueryExecutionId']
    #print('Execution ID: ' + execution_id)

    result = athenaclient.get_query_execution(QueryExecutionId = execution_id)

    key__ = 'queries/'+execution_id+'.csv'

    key_nova = 1
    while key_nova == 1:
        for obj in bucket.objects.filter(Prefix=key__):
            #print (obj.key)
            key_nova = obj.key

    #print('nova key', key_nova)


    obj = s3client.get_object(Bucket=bucket_, Key=key__)
    #print(obj)

    #print(io.BytesIO(obj['Body'].read()))
    #print(type(s))
    #s=1


    df = pd.read_csv(io.BytesIO(obj['Body'].read()))

    ss = ''
    for value in df['v2']:
        ss = ss+str(value)+'\n'


    for item in bucket.objects.filter(Prefix='queries/'):
        #print(item)
        item.delete()
    #time.sleep(15)
    print('df obtido com sucesso')
    return df, ss


def chama_modelo(payload_sage, end_point_name):

    response = sageclient.invoke_endpoint(
            EndpointName=end_point_name,
            Body=payload_sage,
            #Body = teste,
            ContentType='text/csv'
            #Accept='text/csv'
        )
        
    #response['Body'].read().decode('ascii')
    result = response['Body'].read().decode('ascii')
    dic = json.loads(result)

    return dic