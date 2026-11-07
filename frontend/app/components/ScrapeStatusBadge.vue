<script setup lang="ts">
const props = defineProps<{
  status: number
  success: boolean
}>()

const label = computed(() => {
  const phrase = httpReasonPhrase(props.status)
  return phrase ? `${props.status} ${phrase}` : String(props.status)
})
</script>

<template>
  <UBadge
    :color="success ? 'success' : 'error'"
    :icon="success ? 'i-lucide-circle-check' : 'i-lucide-circle-x'"
    variant="subtle"
    size="lg"
    :label="label"
    :aria-label="`HTTP status ${label}, ${success ? 'succeeded' : 'failed'}`"
  />
</template>
