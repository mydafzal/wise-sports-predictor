import os
import boto3
from botocore.exceptions import NoCredentialsError
from WiseSportsAI_MLB.logging import logger
from WiseSportsAI_MLB.utils import read_yaml
from typing import Optional, Dict
from box import ConfigBox

class DataIngestion:
    def __init__(self, config_path: str = "config/config.yaml"):

        self.config = read_yaml(config_path)
        self.aws_config = self.config.AWS_S3  
        self._validate_config()
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_config.access_key_id,
            aws_secret_access_key=self.aws_config.secret_access_key,
            region_name=self.aws_config.get('region_name', 'us-east-1')
        )

    def _validate_config(self):
        required_keys = ['access_key_id', 'secret_access_key', 'bucket_name', 's3_folder', 'local_dir']
        
        for key in required_keys:
            if not self.aws_config.get(key):
                raise ValueError(f"Missing required AWS_S3 configuration in config.yaml: {key}")

    def download_files_from_s3(self, prefix: Optional[str] = None) -> ConfigBox:
        result = {
            'status': False,
            'downloaded_files': [],
            'message': '',
            'error': None
        }
        
        try:
            bucket_name = self.aws_config.bucket_name
            s3_folder = self.aws_config.s3_folder
            local_dir = self.aws_config.local_dir
            
            os.makedirs(local_dir, exist_ok=True)
            
            kwargs = {'Bucket': bucket_name}
            if prefix:
                kwargs['Prefix'] = os.path.join(s3_folder, prefix).replace('\\', '/')
            else:
                kwargs['Prefix'] = s3_folder

            objects = self.s3_client.list_objects_v2(**kwargs)
            
            if 'Contents' not in objects:
                msg = f"No files found in S3 bucket {bucket_name} with prefix {kwargs['Prefix']}"
                logger.warning(msg)
                result['message'] = msg
                return ConfigBox(result)

            downloaded_count = 0
            for obj in objects['Contents']:
                if obj['Key'].endswith('/'):
                    continue
                    
                relative_path = obj['Key'][len(s3_folder):].lstrip('/')
                local_path = os.path.join(local_dir, relative_path)
                
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                self.s3_client.download_file(bucket_name, obj['Key'], local_path)
                logger.info(f"Downloaded {obj['Key']} to {local_path}")
                downloaded_count += 1
                result['downloaded_files'].append({
                    's3_key': obj['Key'],
                    'local_path': local_path
                })

            if downloaded_count > 0:
                msg = f"Successfully downloaded {downloaded_count} files to {local_dir}"
                logger.info(msg)
                result.update({
                    'status': True,
                    'message': msg,
                    'downloaded_count': downloaded_count
                })
            else:
                msg = "No files were downloaded"
                logger.warning(msg)
                result['message'] = msg

            return ConfigBox(result)

        except NoCredentialsError:
            error_msg = "AWS credentials not available"
            logger.error(error_msg)
            result['error'] = error_msg
            raise
        except Exception as e:
            error_msg = f"Error downloading files from S3: {e}"
            logger.error(error_msg)
            result['error'] = error_msg
            raise