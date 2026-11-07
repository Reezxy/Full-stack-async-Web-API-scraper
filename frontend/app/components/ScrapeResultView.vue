<script setup lang="ts">
import type { ScrapeResponse } from '~/types/scrape'

const props = defineProps<{
  url: string
  response: ScrapeResponse
}>()

const toast = useToast()
const wrapLines = ref(false)

const stats = computed(() => {
  const { content } = props.response
  return {
    characters: content.length,
    bytes: new TextEncoder().encode(content).length,
    lines: content === '' ? 0 : content.split('\n').length
  }
})

const { copy, isSupported } = useClipboard({ legacy: true })

async function copyContent() {
  try {
    await copy(props.response.content)
    toast.add({ title: 'HTML copied to clipboard', icon: 'i-lucide-check', color: 'success' })
  }
  catch {
    toast.add({ title: 'Could not copy to clipboard', icon: 'i-lucide-x', color: 'error' })
  }
}
</script>

<template>
  <UCard :ui="{ body: 'space-y-4' }">
    <template #header>
      <div class="flex flex-wrap items-center gap-3">
        <ScrapeStatusBadge
          :status="response.status"
          :success="response.success"
        />
        <ULink
          :to="url"
          target="_blank"
          rel="noopener noreferrer"
          external
          class="min-w-0 flex-1 truncate text-sm text-muted hover:text-default"
          :title="url"
        >
          {{ url }}
        </ULink>
      </div>
    </template>

    <UAlert
      v-if="!response.success"
      color="error"
      variant="subtle"
      icon="i-lucide-circle-x"
      title="Scrape failed"
      :description="`The site answered with HTTP ${response.status} on the last attempt. The response body is shown below.`"
    />

    <div class="flex flex-wrap items-center justify-between gap-3">
      <p class="text-sm text-muted">
        {{ formatNumber(stats.characters) }} characters
        <span aria-hidden="true">·</span>
        {{ formatBytes(stats.bytes) }}
        <span aria-hidden="true">·</span>
        {{ formatNumber(stats.lines) }} lines
      </p>

      <div class="flex items-center gap-3">
        <USwitch
          v-model="wrapLines"
          label="Wrap lines"
          size="sm"
        />
        <UButton
          v-if="isSupported"
          icon="i-lucide-copy"
          label="Copy HTML"
          color="neutral"
          variant="outline"
          size="sm"
          :disabled="stats.characters === 0"
          @click="copyContent"
        />
      </div>
    </div>

    <p
      v-if="stats.characters === 0"
      class="rounded-md border border-dashed border-default p-6 text-center text-sm text-muted"
    >
      The response body was empty.
    </p>
    <pre
      v-else
      class="max-h-[32rem] overflow-auto rounded-md border border-default bg-elevated p-4 font-mono text-xs leading-relaxed text-default"
      :class="wrapLines ? 'whitespace-pre-wrap break-all' : 'whitespace-pre'"
      tabindex="0"
      aria-label="Scraped HTML"
    ><code>{{ response.content }}</code></pre>
  </UCard>
</template>
