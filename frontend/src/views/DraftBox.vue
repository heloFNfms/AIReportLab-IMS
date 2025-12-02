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
.draft-box { 
  max-width: 1280px; 
  margin: 0 auto; 
  padding: 24px 32px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 32px;
  padding: 20px 0;
}

.header h2 { 
  margin: 0; 
  color: #1f2937;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions { 
  display: flex; 
  gap: 12px; 
}
.stats-cards { 
  display: grid; 
  grid-template-columns: repeat(3, 1fr); 
  gap: 20px; 
  margin-bottom: 32px; 
}

.stat-card { 
  display: flex; 
  align-items: center; 
  gap: 18px; 
  padding: 24px; 
  background: white; 
  border-radius: 16px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 0 1px rgba(0,0,0,0.1);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transform: scaleX(0);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12), 0 0 1px rgba(0,0,0,0.1);
}

.stat-card:hover::before {
  transform: scaleX(1);
}

.stat-icon { 
  width: 56px; 
  height: 56px; 
  border-radius: 14px; 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-size: 26px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.stat-icon.draft { 
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.stat-icon.completed { 
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.stat-value { 
  font-size: 28px; 
  font-weight: 700; 
  color: #1f2937;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label { 
  font-size: 14px; 
  color: #6b7280;
  font-weight: 500;
}
.filters { 
  margin-bottom: 24px;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.draft-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
  gap: 20px; 
}

.draft-card { 
  background: white; 
  border-radius: 16px; 
  padding: 24px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 0 1px rgba(0,0,0,0.1);
  cursor: pointer; 
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  border: 2px solid transparent;
}

.draft-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transform: scaleX(0);
  transition: transform 0.3s;
}

.draft-card:hover { 
  transform: translateY(-6px); 
  box-shadow: 0 12px 24px rgba(0,0,0,0.15), 0 0 1px rgba(0,0,0,0.1);
  border-color: #e5e7eb;
}

.draft-card:hover::before {
  transform: scaleX(1);
}
.draft-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: flex-start; 
  margin-bottom: 14px;
  gap: 12px;
}

.draft-title { 
  margin: 0; 
  font-size: 17px; 
  color: #1f2937;
  font-weight: 600;
  line-height: 1.4;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.status-badge { 
  padding: 4px 12px; 
  border-radius: 20px; 
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}

.status-badge.draft { 
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
}

.status-badge.completed { 
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
}

.draft-meta { 
  display: flex; 
  flex-wrap: wrap;
  gap: 14px; 
  font-size: 13px; 
  color: #6b7280; 
  margin-bottom: 18px;
  padding-top: 8px;
  border-top: 1px solid #f3f4f6;
}

.draft-meta span { 
  display: flex; 
  align-items: center; 
  gap: 5px;
  font-weight: 500;
}

.draft-actions { 
  display: flex; 
  gap: 10px; 
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.empty-state { 
  text-align: center; 
  padding: 80px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.loading { 
  padding: 60px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
</style>
