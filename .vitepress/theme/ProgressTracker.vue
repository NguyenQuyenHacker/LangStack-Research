<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vitepress'

const route = useRoute()

// Define stats for each stack
const stacks = {
  LangChain: {
    name: 'LangChain',
    status: 'Đang viết',
    statusClass: 'status-writing',
    totalFiles: 36,
    completed: 18, // Show active progress for visual appeal
    percentage: 50,
    color: '#0d9488',
    description: 'Xây dựng Agent & Core components'
  },
  LangGraph: {
    name: 'LangGraph',
    status: 'Khung rỗng',
    statusClass: 'status-stub',
    totalFiles: 26,
    completed: 0,
    percentage: 10, // tiny progress for starting setup
    color: '#0d9488', // Teal accent matching key requirements
    description: 'State machine & Orchestration'
  },
  Langfuse: {
    name: 'Langfuse',
    status: 'Chưa bắt đầu',
    statusClass: 'status-pending',
    totalFiles: 0,
    completed: 0,
    percentage: 0,
    color: '#64748b',
    description: 'Observability & Evaluation'
  }
}

const activeStack = computed(() => {
  const path = route.path
  if (path.includes('/LangChain/')) return stacks.LangChain
  if (path.includes('/LangGraph/')) return stacks.LangGraph
  if (path.includes('/Langfuse/')) return stacks.Langfuse
  return null
})
</script>

<template>
  <div v-if="activeStack" class="progress-card">
    <div class="progress-card__header">
      <div class="progress-card__title-group">
        <span class="progress-card__tag">STACK RESEARCH</span>
        <h4 class="progress-card__title">{{ activeStack.name }}</h4>
      </div>
      <span class="progress-card__status" :class="activeStack.statusClass">
        {{ activeStack.status }}
      </span>
    </div>

    <p class="progress-card__description">{{ activeStack.description }}</p>

    <div class="progress-card__body">
      <div class="progress-card__stat-row">
        <span class="stat-label">Tiến độ nghiên cứu</span>
        <span class="stat-value">{{ activeStack.completed }}/{{ activeStack.totalFiles }} bài</span>
      </div>
      
      <div class="progress-card__bar-bg">
        <div 
          class="progress-card__bar-fill" 
          :style="{ 
            width: `${activeStack.percentage}%`,
            backgroundColor: activeStack.color
          }"
        ></div>
      </div>
      
      <div class="progress-card__percentage-label" :style="{ color: activeStack.color }">
        {{ activeStack.percentage }}% hoàn thành
      </div>
    </div>
  </div>
</template>

<style scoped>
.progress-card {
  margin: 16px 0;
  padding: 16px;
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
  transition: all 0.2s ease;
}

.progress-card:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 4px 12px rgba(13, 148, 136, 0.05);
}

.progress-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.progress-card__title-group {
  display: flex;
  flex-direction: column;
}

.progress-card__tag {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--vp-c-text-3);
  text-transform: uppercase;
}

.progress-card__title {
  margin: 2px 0 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.progress-card__status {
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.status-writing {
  background: rgba(13, 148, 136, 0.1);
  color: #0d9488;
}

.status-stub {
  background: rgba(13, 148, 136, 0.1); /* Match Teal accent color */
  color: #0d9488;
}

.status-pending {
  background: rgba(100, 116, 139, 0.1);
  color: #64748b;
}

.progress-card__description {
  margin: 0 0 16px;
  font-size: 12px;
  color: var(--vp-c-text-2);
  line-height: 1.4;
}

.progress-card__stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  margin-bottom: 6px;
}

.stat-label {
  color: var(--vp-c-text-2);
}

.stat-value {
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.progress-card__bar-bg {
  height: 6px;
  background: var(--vp-c-bg-mute);
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 6px;
}

.progress-card__bar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-card__percentage-label {
  font-size: 10px;
  font-weight: 600;
  text-align: right;
}
</style>
