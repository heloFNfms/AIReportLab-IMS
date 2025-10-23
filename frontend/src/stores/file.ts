import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FileInfo, FileStatistics, FileType } from '@/types'
import { 
  getFiles, 
  getFileStatistics, 
  uploadFile as uploadFileApi,
  deleteFile as deleteFileApi,
  downloadFile as downloadFileApi
} from '@/api'
import { ElMessage } from 'element-plus'

export const useFileStore = defineStore('file', () => {
  const files = ref<FileInfo[]>([])
  const statistics = ref<FileStatistics>({
    total_files: 0,
    total_templates: 0,
    total_data_files: 0,
    total_size: 0,
  })
  const loading = ref(false)

  // 获取文件列表
  const fetchFiles = async (fileType?: FileType) => {
    loading.value = true
    try {
      files.value = await getFiles(fileType)
      return true
    } catch (error) {
      console.error('获取文件列表失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 获取文件统计
  const fetchStatistics = async () => {
    try {
      statistics.value = await getFileStatistics()
      return true
    } catch (error) {
      console.error('获取统计信息失败:', error)
      return false
    }
  }

  // 上传文件
  const uploadFile = async (file: File, fileType: FileType) => {
    loading.value = true
    try {
      const res = await uploadFileApi(file, fileType)
      ElMessage.success('文件上传成功')
      // 刷新文件列表和统计信息
      await fetchFiles()
      await fetchStatistics()
      return true
    } catch (error) {
      console.error('文件上传失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 删除文件
  const deleteFile = async (fileId: number) => {
    loading.value = true
    try {
      await deleteFileApi(fileId)
      ElMessage.success('文件删除成功')
      // 刷新文件列表和统计信息
      await fetchFiles()
      await fetchStatistics()
      return true
    } catch (error) {
      console.error('文件删除失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 下载文件
  const downloadFile = async (fileId: number, filename: string) => {
    try {
      await downloadFileApi(fileId, filename)
      ElMessage.success('文件下载成功')
      return true
    } catch (error) {
      console.error('文件下载失败:', error)
      return false
    }
  }

  return {
    files,
    statistics,
    loading,
    fetchFiles,
    fetchStatistics,
    uploadFile,
    deleteFile,
    downloadFile,
  }
})
