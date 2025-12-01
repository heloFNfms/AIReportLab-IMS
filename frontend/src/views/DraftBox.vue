<template>
  <div class="draft-box">
    <div class="header">
      <h2>草稿箱</h2>
      <div class="header-actions">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-button type="primary" @click="createNew">
          <el-icon><Plus /></el-icon>
          新建报告
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ statistics.total }}</div>
          <div class="stat-label">总计</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon draft">
          <el-icon><Edit /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ statistics.draft_count }}</div>
          <div class="stat-label">草稿</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon completed">
          <el-icon><Check /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ statistics.completed_count }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="filters">
      <el-radio-group v-model="statusFilter" @change="handleFilterChange">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="draft">草稿</el-radio-button>
        <el-radio-button label="completed">已完成</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 草稿列表 -->
    <div class="draft-list">
      <div v-if="loading" class="loading">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="drafts.length === 0" class="empty-state">
        <el-empty description="暂无草稿">
          <el-button type="primary" @click="createNew">创建第一个报告</el-button>
        </el-empty>
      </div>
      <div v-else class="draft-grid">
        <div 
          v-for="draft in drafts" 
          :key="draft.id"
          class="draft-card"
          @click="openDraft(draft)"
        >
          <div class="draft-header">
            <h3 class="draft-title">{{ draft.title }}</h3>
            <span class="status-badge" :class="draft.status">
              {{ draft.status === 'draft' ? '草稿' : '已完成' }}
            </span>
          </div>
          <div class="draft-meta">
            <span><el-icon><Clock /></el-icon> {{ formatDate(draft.updated_at) }}</span>
            <span><el-icon><Document /></el-icon> 版本 {{ draft.current_version }}</span>
            <span>{{ draft.word_count }} 字</span>
          </div>
          <div class="draft-actions" @click.stop>
            <el-button size="small" @click="openDraft(draft)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteDraft(draft)">删除</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus, Document, Edit, Check, Clock } from '@element-plus/icons-vue'
import { useDraftStore } from '@/stores/draft'
import { formatDate } from '@/utils/format'
import type { Draft } from '@/types'

const router = useRouter()
const draftStore = useDraftStore()

const drafts = ref<Draft[]>([])
const statistics = ref({ total: 0, draft_count: 0, completed_count: 0 })
const loading = ref(false)
const statusFilter = ref('')

const loadDrafts = async () => {
  loading.value = true
  try {
    await draftStore.fetchDrafts(statusFilter.value || undefined)
    drafts.value = draftStore.drafts
    await draftStore.fetchStatistics()
    statistics.value = draftStore.statistics
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => loadDrafts()

const openDraft = (draft: Draft) => router.push(`/draft-editor/${draft.id}`)

const createNew = () => router.push('/template-select')

const goBack = () => router.push('/')

const deleteDraft = async (draft: Draft) => {
  try {
    await ElMessageBox.confirm('确定要删除这个草稿吗？', '确认删除', { type: 'warning' })
    await draftStore.deleteDraft(draft.id)
    await loadDrafts()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

onMounted(() => loadDrafts())
</script>

<style scoped>
.draft-box { max-width: 1200px; margin: 0 auto; padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header h2 { margin: 0; color: #303133; }
.header-actions { display: flex; gap: 12px; }
.stats-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { display: flex; align-items: center; gap: 16px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; background: #409eff; color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; }
.stat-icon.draft { background: #67c23a; }
.stat-icon.completed { background: #e6a23c; }
.stat-value { font-size: 24px; font-weight: 600; color: #303133; }
.stat-label { font-size: 14px; color: #909399; }
.filters { margin-bottom: 20px; }
.draft-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.draft-card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); cursor: pointer; transition: all 0.3s; }
.draft-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.draft-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.draft-title { margin: 0; font-size: 16px; color: #303133; }
.status-badge { padding: 2px 8px; border-radius: 12px; font-size: 12px; }
.status-badge.draft { background: #e1f3d8; color: #67c23a; }
.status-badge.completed { background: #fdf6ec; color: #e6a23c; }
.draft-meta { display: flex; gap: 16px; font-size: 12px; color: #909399; margin-bottom: 16px; }
.draft-meta span { display: flex; align-items: center; gap: 4px; }
.draft-actions { display: flex; gap: 8px; }
.empty-state { text-align: center; padding: 60px 20px; }
.loading { padding: 40px; }
</style>
