import boto3
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class S3CSVUploader:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-northeast-1"),
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME")

    def upload_csv_file(
        self, local_file_path: str, user_id: str = "test"
    ) -> Optional[str]:
        """
        Upload a local CSV file to S3 and return the public URL.
        Stores in format: {user_id}/data/data.csv

        Args:
            local_file_path: Path to the local CSV file
            user_id: The user/analysis ID

        Returns:
            Public S3 URL if successful, None if failed
        """
        try:
            # Check if file exists
            if not os.path.exists(local_file_path):
                print(f"Error: File {local_file_path} does not exist")
                return None

            file_name = os.path.basename(local_file_path)
            # Store under user_id/data/data.csv format
            s3_key = f"projects/KHH_Airport/file_folder/{user_id}/data/{file_name}"

            # Upload file to S3
            self.s3_client.upload_file(
                local_file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={"ACL": "public-read", "ContentType": "text/csv"},
            )

            # Generate public URL (Virtual Hosted Style - recommended by AWS)
            public_url = (
                # f"https://{self.bucket_name}.s3.ap-northeast-1.amazonaws.com/{s3_key}"
                f"https://s3.ap-northeast-1.amazonaws.com/{self.bucket_name}/{s3_key}"
            )

            print(f"CSV file uploaded successfully: {public_url}")
            return public_url

        except Exception as e:
            print(f"Error uploading CSV file to S3: {e}")
            return None

    def delete_csv(self, user_id: str) -> bool:
        """
        Delete CSV file from S3

        Args:
            user_id: The user/analysis ID

        Returns:
            True if successful, False if failed
        """
        try:
            s3_key = f"projects/KHH_Airport/file_folder/{user_id}/data/data.csv"

            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)

            print(f"CSV deleted successfully: {s3_key}")
            return True

        except Exception as e:
            print(f"Error deleting CSV from S3: {e}")
            return False

    def list_user_csvs(self, user_id: str) -> list:
        """
        List all CSV files for a specific user

        Args:
            user_id: The user/analysis ID

        Returns:
            List of CSV keys
        """
        try:
            prefix = f"projects/KHH_Airport/file_folder/{user_id}/data/"

            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )

            csvs = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    csvs.append(obj["Key"])

            return csvs

        except Exception as e:
            print(f"Error listing CSV files: {e}")
            return []


# Global instance
s3_csv_uploader = S3CSVUploader()

if __name__ == "__main__":
    # Test CSV upload and delete
    # test_csv_path = "agents/search_agent/csv/test/data_20250909_100000.csv"
    print(s3_csv_uploader.list_user_csvs("test"))
    # s3_csv_uploader.upload_csv_file(test_csv_path, "test")
    # print(s3_csv_uploader.list_user_csvs("test"))
    # s3_csv_uploader.delete_csv("test")
    # print(s3_csv_uploader.list_user_csvs("test"))
