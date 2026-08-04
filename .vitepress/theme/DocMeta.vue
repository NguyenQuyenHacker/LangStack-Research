<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'

const { frontmatter } = useData()

const meta = computed(() => frontmatter.value as Record<string, string>)
const show = computed(() => Boolean(meta.value.doc_source || meta.value.status))
// YAML parse `accessed: 2026-07-22` thanh Date -> ve chuoi ISO, cat lay YYYY-MM-DD
const accessed = computed(() => String(meta.value.accessed ?? '').slice(0, 10))
</script>

<template>
  <div v-if="show" class="doc-meta">
    <span v-if="meta.status" class="doc-meta__badge" :data-status="meta.status">
      {{ meta.status }}
    </span>
    <span v-if="meta.lc_version" class="doc-meta__item">version: {{ meta.lc_version }}</span>
    <span v-if="accessed" class="doc-meta__item">đọc docs ngày {{ accessed }}</span>
    <a v-if="meta.doc_source" class="doc-meta__item" :href="meta.doc_source" target="_blank" rel="noreferrer">
      nguồn ↗
    </a>
    <a v-if="meta.lab" class="doc-meta__item" :href="meta.lab">lab</a>
  </div>
</template>

<style scoped>
.doc-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin: 0 0 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--vp-c-divider);
  font-size: 13px;
  color: var(--vp-c-text-2);
}

.doc-meta__badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 11px;
  background: var(--vp-c-default-soft);
  color: var(--vp-c-text-1);
}

.doc-meta__badge[data-status='draft'] {
  background: var(--vp-c-warning-soft);
}

.doc-meta__badge[data-status='done'],
.doc-meta__badge[data-status='reviewed'] {
  background: var(--vp-c-tip-soft);
}

.doc-meta__item {
  white-space: nowrap;
}

a.doc-meta__item {
  color: var(--vp-c-brand-1);
}
</style>
