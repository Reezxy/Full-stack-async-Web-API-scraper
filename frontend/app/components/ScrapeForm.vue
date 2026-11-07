<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import type { ScrapeRequest } from '~/types/scrape'

defineProps<{
  loading: boolean
  apiError: string | null
}>()

const emit = defineEmits<{
  submit: [request: ScrapeRequest]
  edit: []
}>()

const formState = reactive<Partial<ScrapeRequest>>({
  url: '',
  call_count: 3
})

watch(formState, () => emit('edit'))

function onSubmit(event: FormSubmitEvent<ScrapeRequest>) {
  emit('submit', event.data)
}
</script>

<template>
  <UForm
    :schema="scrapeRequestSchema"
    :state="formState"
    :disabled="loading"
    class="space-y-4"
    @submit="onSubmit"
  >
    <div class="grid gap-4 sm:grid-cols-[1fr_10rem]">
      <UFormField
        label="URL"
        name="url"
        required
      >
        <UInput
          v-model="formState.url"
          inputmode="url"
          autocomplete="url"
          placeholder="https://example.com"
          icon="i-lucide-globe"
          class="w-full"
        />
      </UFormField>

      <UFormField
        label="Attempts"
        name="call_count"
        :help="`1 to ${MAX_CALL_COUNT}`"
        required
      >
        <UInputNumber
          v-model="formState.call_count"
          :step="1"
          class="w-full"
        />
      </UFormField>
    </div>

    <UAlert
      v-if="apiError"
      color="error"
      variant="subtle"
      icon="i-lucide-triangle-alert"
      title="The API rejected the request"
      :description="apiError"
      role="alert"
    />

    <div class="flex justify-end">
      <UButton
        type="submit"
        icon="i-lucide-download"
        :loading="loading"
        :label="loading ? 'Scraping' : 'Scrape'"
      />
    </div>
  </UForm>
</template>
