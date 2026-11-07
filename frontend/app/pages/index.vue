<script setup lang="ts">
const store = useScrapeStore()
const { state, isLoading } = storeToRefs(store)

const rejection = computed(() => (state.value.phase === 'rejected' ? state.value.message : null))
</script>

<template>
  <div class="space-y-8">
    <div>
      <h1 class="text-2xl font-semibold text-highlighted">
        Scrape a URL
      </h1>
      <p class="mt-1 text-sm text-muted">
        Submit a URL to scrape and see what the API returns.
      </p>
    </div>

    <UCard>
      <ScrapeForm
        :loading="isLoading"
        :api-error="rejection"
        @submit="store.submit"
        @edit="store.dismissRejection"
      />
    </UCard>

    <section aria-live="polite">
      <UCard v-if="state.phase === 'loading'">
        <div class="flex items-center gap-3 text-sm text-muted">
          <UIcon
            name="i-lucide-loader-circle"
            class="size-5 shrink-0 animate-spin"
          />
          <span class="min-w-0 truncate">Scraping {{ state.request.url }}</span>
        </div>
        <div class="mt-4 space-y-2">
          <USkeleton class="h-4 w-1/3" />
          <USkeleton class="h-48 w-full" />
        </div>
      </UCard>

      <UAlert
        v-else-if="state.phase === 'failed'"
        color="error"
        variant="subtle"
        icon="i-lucide-server-crash"
        title="Something went wrong on the server"
        :description="state.message"
        :actions="[{ label: 'Retry', icon: 'i-lucide-rotate-cw', color: 'error', variant: 'solid', onClick: store.retry }]"
        role="alert"
      />

      <ScrapeResultView
        v-else-if="state.phase === 'completed'"
        :url="state.request.url"
        :response="state.response"
      />

      <UEmpty
        v-else
        icon="i-lucide-file-code"
        title="No results yet"
        description="Enter a URL above. The scraped HTML will appear here."
        variant="naked"
      />
    </section>
  </div>
</template>
