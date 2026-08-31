import boto3

def enviar_para_s3(bucket, arquivo_local, nome_no_s3):
    s3 = boto3.client("s3")
    try:
        s3.upload_file(arquivo_local, bucket, nome_no_s3)
        print("✅ Upload realizado com sucesso no S3!")
    except Exception as erro:
        print("❌ Erro durante o upload:")
        print(erro)
