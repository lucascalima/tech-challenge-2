# start-glue-job-b3

import json
import boto3

def lambda_handler(event, context):
    glue = boto3.client('glue')

    # Nome do seu Glue Job
    job_name = 'etl-b3-job'  

    try:
        response = glue.start_job_run(JobName=job_name)
        print(f"Glue Job iniciado: {response['JobRunId']}")
        return {
            'statusCode': 200,
            'body': json.dumps(f"Glue Job iniciado com sucesso: {response['JobRunId']}")
        }
    except Exception as e:
        print("Erro ao iniciar Glue Job:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps("Erro ao iniciar Glue Job")
        }
