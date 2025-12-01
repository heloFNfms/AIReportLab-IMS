import { defineStore } from 'pinia'
import { ref } from 'vue'
import { draftApi } from '@/api/drafts'
import type { Draft, DraftCreate, DraftUpdate, DraftVersion, DraftStatistics } from '@/types'
import { ElMessage } from 'element-plus'

export const useDraftStore = defineStore('draft', () => {
  const drafts = ref<Draft[]>([])
  const currentDraft = ref<Draft | null>(null)
  const versions = ref<DraftVersion[]>([])
  const statistics = ref<DraftStatistics>({ total: 0, draft_count: 0, completed_count: 0 })
  const loading = ref(false)

  const fetchDrafts = async (status?: string) => {
    try {
      loading.value = true
      drafts.value = await draftApi.getList(status)
    } catch (error) {
      ElMessage.error('获取草稿列表失败')
    } finally {
      loading.value = false
    }
  }

  const createDraft = async (data: DraftCreate) => {
    const draft = await draftApi.create(data)
    drafts.value.unshift(draft)
    ElMessage.success('草稿创建成功')
    return draft
  }

  const fetchDraftDetail = async (id: number) => {
    loading.value = true
    try {
      const draft = await draftApi.getDetail(id)
      currentDraft.value = draft
      versions.value = draft.versions || []
      return draft
    } finally {
      loading.value = false
    }
  }

  const updateDraft = async (id: number, data: DraftUpdate) => {
    const draft = await draftApi.update(id, data)
    currentDraft.value = draft
    const index = drafts.value.findIndex((d: Draft) => d.id === id)
    if (index !== -1) drafts.value[index] = draft
    return draft
  }

  const completeDraft = async (id: number, data?: { title?: string; content?: string }) => {
    const draft = await draftApi.complete(id, data)
    currentDraft.value = draft
    const index = drafts.value.findIndex((d: Draft) => d.id === id)
    if (index !== -1) drafts.value[index] = draft
    ElMessage.success('报告完成！')
    return draft
  }

  const reopenDraft = async (id: number) => {
    const draft = await draftApi.reopen(id)
    currentDraft.value = draft
    const index = drafts.value.findIndex((d: Draft) => d.id === id)
    if (index !== -1) drafts.value[index] = draft
    ElMessage.success('报告已重新打开')
    return draft
  }

  const rollbackVersion = async (id: number, version: number) => {
    const draft = await draftApi.rollback(id, version)
    currentDraft.value = draft
    ElMessage.success(`已回滚到版本 ${version}`)
    return draft
  }

  const deleteDraft = async (id: number) => {
    await draftApi.delete(id)
    drafts.value = drafts.value.filter((d: Draft) => d.id !== id)
    ElMessage.success('草稿删除成功')
  }

  const fetchStatistics = async () => {
    try {
      statistics.value = await draftApi.getStatistics()
    } catch (error) {
      console.error('获取统计信息失败:', error)
    }
  }

  const clearCurrentDraft = () => {
    currentDraft.value = null
    versions.value = []
  }

  return {
    drafts, currentDraft, versions, statistics, loading,
    fetchDrafts, createDraft, fetchDraftDetail, updateDraft,
    completeDraft, reopenDraft, rollbackVersion, deleteDraft,
    fetchStatistics, clearCurrentDraft
  }
})
