from abc import ABC, abstractmethod
from enum import Enum
from tempfile import TemporaryDirectory
from uuid import uuid4

import aiofiles
import boto3
from fastapi import UploadFile

from app.core.config import settings


class ThirdPartyStorageProvider(str, Enum):
    AMAZON = "aws_s3"


def get_storage(provider: ThirdPartyStorageProvider) -> "AbstractThirdPartyStorage":
    storage_class = {ThirdPartyStorageProvider.AMAZON: AWSS3Storage}[provider]
    return storage_class()


class AbstractThirdPartyStorage(ABC):
    @abstractmethod
    async def save(self, file: UploadFile) -> str: ...

    @abstractmethod
    async def delete(self, url): ...


class AWSS3Storage(AbstractThirdPartyStorage):
    def __init__(self):
        self._bucket_region = "eu-west-1"
        self.s3_resource = boto3.resource(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        if settings.AWS_BUCKET_NAME not in [
            bucket.name for bucket in self.s3_resource.buckets.all()
        ]:
            self._create_default_bucket()

    async def save(self, file: UploadFile) -> str:
        filename = self._randomize_filename(file.filename)
        with TemporaryDirectory() as temp_dir:
            file_path = f"{temp_dir}/{file.filename}"
            async with aiofiles.open(file_path, mode="wb") as f:
                await f.write(await file.read())
            self.s3_resource.Object(settings.AWS_BUCKET_NAME, filename).upload_file(
                Filename=file_path
            )
        return f"https://{settings.AWS_BUCKET_NAME}.s3.{self._bucket_region}.amazonaws.com/{filename}"

    async def delete(self, url: str):
        filename = url.split("/", 2)[-1]
        self.s3_resource.Object(settings.AWS_BUCKET_NAME, filename).delete()

    def _create_default_bucket(self):
        self.s3_resource.create_bucket(
            Bucket=settings.AWS_BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": self._bucket_region},
        )

    def _randomize_filename(self, filename: str) -> str:
        name_and_extension = filename.split(".", 2)
        if len(name_and_extension) < 2:
            raise ValueError("unable to determine file extension")
        return f"{uuid4()}.{name_and_extension[-1]}"
