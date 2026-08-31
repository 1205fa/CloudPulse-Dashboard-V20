import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError

def enviar_para_s3(bucket, arquivo_local, nome_no_s3):
    logging.info(f"☁️ Upload iniciado para o S3: {bucket}/{nome_no_s3}...")
    s3 = boto3.client("s3")
    
    try:
        s3.upload_file(arquivo_local, bucket, nome_no_s3)
        logging.info("✔ Upload concluído com sucesso!")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            logging.error("❌ Erro: Bucket inexistente.")
        elif error_code == 'AccessDenied':
            logging.error("❌ Erro: AccessDenied (Permissão negada).")
        else:
            logging.error(f"❌ Erro na AWS: {error_code}")
        return False
        
    except NoCredentialsError:
        logging.error("❌ Erro: Credenciais inválidas ou não configuradas.")
        return False
        
    except Exception as erro:
        logging.error(f"❌ Erro inesperado durante o upload: {erro}")
        return False
