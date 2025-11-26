<template>
  <router-view />
</template>

<script setup lang="ts">
// 主应用组件
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  /* 品牌色彩 - 更加鲜艳和现代 */
  --brand-gradient-start: #4facfe;
  --brand-gradient-mid: #00f2fe;
  --brand-gradient-end: #43e97b;
  
  --brand-primary: #3b82f6;
  --brand-primary-light: #60a5fa;
  --brand-primary-dark: #2563eb;
  
  /* 文字颜色 */
  --text-primary: #1e293b;
  --text-secondary: #475569;
  --text-tertiary: #94a3b8;
  
  /* 背景色 */
  --bg-page: #f8fafc;
  --bg-card: rgba(255, 255, 255, 0.8);
  --bg-overlay: rgba(255, 255, 255, 0.65);
  
  /* 边框和分割线 */
  --border-color: rgba(226, 232, 240, 0.8);
  --border-color-light: rgba(241, 245, 249, 0.8);
  
  /* 间距系统 */
  --space-2: 2px;
  --space-4: 4px;
  --space-8: 8px;
  --space-12: 12px;
  --space-16: 16px;
  --space-20: 20px;
  --space-24: 24px;
  --space-32: 32px;
  
  /* 圆角 - 更圆润 */
  --radius-sm: 8px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-xl: 32px;
  
  /* 阴影系统 - 更柔和 */
  --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
  --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
  --shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  --shadow-glow: 0 0 20px rgba(59, 130, 246, 0.3);
  
  /* 玻璃拟态 */
  --glass-blur: blur(16px);
  --glass-border: 1px solid rgba(255, 255, 255, 0.3);
  
  /* 表格样式 */
  --table-header-bg: rgba(248, 250, 252, 0.8);
  --table-header-text: #64748b;
  --table-row-hover: rgba(59, 130, 246, 0.05);
  
  /* 焦点环 */
  --focus-ring: rgba(59, 130, 246, 0.4);
  
  /* Element Plus 主题变量映射 */
  --el-color-primary: var(--brand-primary);
  --el-color-primary-light-3: var(--brand-primary-light);
  --el-color-primary-light-5: #93c5fd;
  --el-color-primary-light-7: #bfdbfe;
  --el-color-primary-dark-2: var(--brand-primary-dark);
  --el-border-radius-base: var(--radius-sm);
}

:root.dark {
  /* 品牌色彩 - 暗色模式 */
  --brand-gradient-start: #3b82f6;
  --brand-gradient-mid: #8b5cf6;
  --brand-gradient-end: #ec4899;
  
  --brand-primary: #60a5fa;
  --brand-primary-light: #93c5fd;
  --brand-primary-dark: #3b82f6;
  
  /* 文字颜色 */
  --text-primary: #f1f5f9;
  --text-secondary: #cbd5e1;
  --text-tertiary: #94a3b8;
  
  /* 背景色 */
  --bg-page: #0f172a;
  --bg-card: rgba(30, 41, 59, 0.7);
  --bg-overlay: rgba(15, 23, 42, 0.8);
  
  /* 边框和分割线 */
  --border-color: rgba(51, 65, 85, 0.6);
  --border-color-light: rgba(71, 85, 105, 0.6);
  
  /* 阴影系统 */
  --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
  --shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
  --shadow-glow: 0 0 25px rgba(96, 165, 250, 0.2);
  
  /* 玻璃拟态 */
  --glass-border: 1px solid rgba(255, 255, 255, 0.1);
  
  /* 表格样式 */
  --table-header-bg: rgba(30, 41, 59, 0.8);
  --table-header-text: #94a3b8;
  --table-row-hover: rgba(96, 165, 250, 0.1);
  
  /* 焦点环 */
  --focus-ring: rgba(96, 165, 250, 0.4);
  
  /* Element Plus 主题变量映射 */
  --el-color-primary: var(--brand-primary);
  --el-color-primary-light-3: var(--brand-primary-light);
  --el-color-primary-light-5: #3b82f6;
  --el-color-primary-light-7: #2563eb;
  --el-color-primary-dark-2: var(--brand-primary-dark);
}

/* 全局动画关键帧 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: var(--bg-page);
  color: var(--text-primary);
}

/* 平滑过渡 */
* {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--text-tertiary);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>
