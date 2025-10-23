import request from './request'
import type { FileInfo, FileStatistics, FileType } from '@/types'

/**
 * 上传文件到本地
 */
export const uploadFile = (file: File, fileType: FileType) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return request<FileInfo>({
    url: '/files/upload',
    method: 'post',
    params: { file_type: fileType },
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * 上传文件到阿里云OSS
 */
export const uploadFileToOSS = (file: File, fileType: FileType) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return request<FileInfo>({
    url: '/files/upload-oss',
    method: 'post',
    params: { file_type: fileType },
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * 获取用户文件列表
 */
export const getFiles = (fileType?: FileType) => {
  return request<FileInfo[]>({
    url: '/files/',
    method: 'get',
    params: fileType ? { file_type: fileType } : undefined,
  })
}

/**
 * 获取文件统计信息
 */
export const getFileStatistics = () => {
  return request<FileStatistics>({
    url: '/files/statistics',
    method: 'get',
  })
}

/**
 * 获取单个文件信息
 */
export const getFileInfo = (fileId: number) => {
  return request<FileInfo>({
    url: `/files/${fileId}`,
    method: 'get',
  })
}

/**
 * 下载文件
 */
export const downloadFile = (fileId: number, filename: string) => {
  return request({
    url: `/files/${fileId}/download`,
    method: 'get',
    responseType: 'blob',
  }).then((blob: Blob) => {
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  })
}

/**
 * 删除文件
 */
export const deleteFile = (fileId: number) => {
  return request<{ message: string }>({
    url: `/files/${fileId}`,
    method: 'delete',
  })
}
