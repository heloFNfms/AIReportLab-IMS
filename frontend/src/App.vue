<template>
  <router-view />
</template>

<script setup lang="ts">
// 主应用组件
</script>

<style>
:root {
  --brand-gradient-start: #667eea;
  --brand-gradient-end: #764ba2;
  --brand-primary: #409EFF;
  --text-primary: #303133;
  --text-secondary: #909399;
  --bg-page: #f5f7fa;
  --card-radius: 12px;
  --space-2: 2px;
  --space-4: 4px;
  --space-8: 8px;
  --space-12: 12px;
  --space-16: 16px;
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 6px 16px rgba(0, 0, 0, 0.12);
  --shadow-lg: 0 10px 20px rgba(0, 0, 0, 0.16);
  --table-header-bg: #fafafa;
  --table-header-text: #606266;
  --table-row-hover: rgba(64, 158, 255, 0.06);
  /* Element Plus 主题变量映射 */
  --el-color-primary: var(--brand-primary);
  --el-color-primary-light-3: #79bbff;
  --el-color-primary-light-5: #a0cfff;
  --el-color-primary-light-7: #d9ecff;
  --el-color-primary-dark-2: #337ecc;
  /* 语义变量扩充 */
  --bg-card: #ffffff;
  --border-color: #e4e7ed;
  --focus-ring: rgba(64, 158, 255, 0.35);
}

:root.dark {
  --brand-gradient-start: #3a3a3a;
  --brand-gradient-end: #1f1f1f;
  --brand-primary: #79bbff;
  --text-primary: #e5eaf3;
  --text-secondary: #c0c4cc;
  --bg-page: #121212;
  --card-radius: 12px;
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.5);
  --shadow-md: 0 6px 16px rgba(0, 0, 0, 0.55);
  --shadow-lg: 0 10px 20px rgba(0, 0, 0, 0.6);
  --table-header-bg: #1a1a1a;
  --table-header-text: #c0c4cc;
  --table-row-hover: rgba(121, 187, 255, 0.12);
  /* Element Plus 主题变量映射 */
  --el-color-primary: var(--brand-primary);
  --el-color-primary-light-3: #a0cfff;
  --el-color-primary-light-5: #b3d8ff;
  --el-color-primary-light-7: #c6e2ff;
  --el-color-primary-dark-2: #79bbff;
  /* 语义变量扩充 */
  --bg-card: #1f1f1f;
  --border-color: #303133;
  --focus-ring: rgba(121, 187, 255, 0.45);
}
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
