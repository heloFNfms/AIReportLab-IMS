import oss2
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
import uuid
import os
from datetime import datetime

class OSSService:
    """阿里云OSS服务类"""
    
    def __init__(self):
        """初始化OSS客户端"""
        self.auth = oss2.Auth(
            settings.OSS_ACCESS_KEY_ID,
            settings.OSS_ACCESS_KEY_SECRET
        )
        self.bucket = oss2.Bucket(
            self.auth,
            settings.OSS_ENDPOINT,
            settings.OSS_BUCKET_NAME
        )
    
    async def upload_file(self, upload_file: UploadFile, user_id: int, file_type: str) -> dict:
        """
        上传文件到OSS
        
        Args:
            upload_file: 上传的文件
            user_id: 用户ID
            file_type: 文件类型
            
        Returns:
            dict: 包含文件URL和OSS路径的字典
        """
        try:
            # 读取文件内容
            content = await upload_file.read()
            
            # 检查文件大小
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE} bytes)"
                )
            
            # 生成OSS上的文件路径
            file_extension = os.path.splitext(upload_file.filename)[1]
            timestamp = datetime.now().strftime("%Y%m%d")
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            oss_path = f"uploads/{user_id}/{file_type}/{timestamp}/{unique_filename}"
            
            # 上传到OSS
            result = self.bucket.put_object(oss_path, content)
            
            if result.status != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="OSS上传失败"
                )
            
            # 生成访问URL
            file_url = f"{settings.OSS_URL_PREFIX}/{oss_path}"
            
            return {
                "oss_path": oss_path,
                "file_url": file_url,
                "original_filename": upload_file.filename,
                "file_size": len(content),
                "mime_type": upload_file.content_type
            }
            
        except HTTPException:
            # 重新抛出HTTPException（如文件大小超限）
            raise
        except oss2.exceptions.OssError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OSS错误: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"上传失败: {str(e)}"
            )
    
    def delete_file(self, oss_path: str) -> bool:
        """
        从OSS删除文件
        
        Args:
            oss_path: OSS上的文件路径
            
        Returns:
            bool: 是否删除成功
        """
        try:
            self.bucket.delete_object(oss_path)
            return True
        except oss2.exceptions.OssError as e:
            print(f"OSS删除失败: {str(e)}")
            return False
    
    def get_file_url(self, oss_path: str, expires: int = 3600) -> str:
        """
        获取文件的签名URL（用于私有bucket）
        
        Args:
            oss_path: OSS上的文件路径
            expires: URL过期时间（秒），默认1小时
            
        Returns:
            str: 签名URL
        """
        try:
            url = self.bucket.sign_url('GET', oss_path, expires)
            return url
        except oss2.exceptions.OssError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取URL失败: {str(e)}"
            )

# 创建全局OSS服务实例
oss_service = OSSService()
