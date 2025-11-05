import boto3
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class S3HtmlUploader:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-northeast-1"),
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME")

    def upload_html(
        self, local_file_path: str, user_id: str = "test"
    ) -> Optional[str]:
        """
        Upload HTML file to S3 with correct headers for browser rendering.
        """
        try:
            file_name = os.path.basename(local_file_path)
            s3_key = f"projects/KHH_Airport/file_folder/{user_id}/html/{file_name}"

            # Upload with correct Content-Type for HTML rendering
            self.s3_client.upload_file(
                local_file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": "text/html",           # ← Renders in browser!
                    "CacheControl": "no-cache",           # ← Fresh content
                    "ContentDisposition": "inline"        # ← Display, don't download
                }
            )

            public_url = (
                f"https://s3.ap-northeast-1.amazonaws.com/{self.bucket_name}/{s3_key}"
            )
            print(f"HTML uploaded successfully: {public_url}")
            return public_url

        except Exception as e:
            print(f"Error uploading HTML to S3: {e}")
            return None

    def delete_html(self, user_id: str, file_name: str) -> bool:
        """
        Delete an HTML file from S3

        Args:
            user_id: The user/analysis ID
            file_extension: File extension (e.g., '.html')

        Returns:
            True if successful, False if failed
        """
        try:
            s3_key = f"projects/KHH_Airport/file_folder/{user_id}/html/{file_name}"

            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)

            print(f"HTML deleted successfully: {s3_key}")
            return True

        except Exception as e:
            print(f"Error deleting HTML from S3: {e}")
            return False

    def list_user_html(self, user_id: str) -> list:
        """
        List all HTML for a specific user

        Args:
            user_id: The user/analysis ID

        Returns:
            List of HTML keys
        """
        try:
            prefix = f"projects/KHH_Airport/file_folder/{user_id}/html/"

            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )

            html = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    html.append(obj["Key"])

            return html

        except Exception as e:
            print(f"Error listing HTML: {e}")
            return []


# Global instance
s3_uploader = S3HtmlUploader()

if __name__ == "__main__":
    import os

    # print(os.getenv('AWS_ACCESS_KEY_ID'))
    s3_uploader = S3HtmlUploader()
    # print(s3_uploader.list_user_images("test"))
    # s3_uploader.upload_html("agents/plot_agent/plots/test_plot_1/plot_20251104_112157.html", "test_plot_1")
    print(s3_uploader.list_user_html("test_plot_1"))
    s3_uploader.delete_html("test_plot_1", "plot_20251104_112157.html")
    print(s3_uploader.list_user_html("test_plot_1"))