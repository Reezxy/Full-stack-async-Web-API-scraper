import { FetchError } from 'ofetch'
import type { ApiErrorBody, ScrapeRequest, ScrapeState } from '~/types/scrape'

function isApiErrorBody(data: unknown): data is ApiErrorBody {
  return typeof data === 'object' && data !== null && typeof (data as ApiErrorBody).error === 'string'
}

function toErrorState(request: ScrapeRequest, error: unknown): ScrapeState {
  if (!(error instanceof FetchError) || !error.response) {
    return { phase: 'failed', request, message: 'Could not reach the API. Check that the server is running.' }
  }

  const status = error.response.status
  const apiMessage = isApiErrorBody(error.data) ? error.data.error : null

  if (status === 400 || status === 422) {
    return { phase: 'rejected', request, message: apiMessage ?? 'The request was rejected.' }
  }
  if (status >= 500) {
    return { phase: 'failed', request, message: apiMessage ?? 'Internal server error' }
  }
  return { phase: 'failed', request, message: apiMessage ?? `Unexpected response from the API (HTTP ${status}).` }
}

export const useScrapeStore = defineStore('scrape', () => {
  const { scrape } = useScraperApi()

  const state = ref<ScrapeState>({ phase: 'idle' })
  const isLoading = computed(() => state.value.phase === 'loading')

  async function submit(request: ScrapeRequest): Promise<void> {
    if (isLoading.value) return

    const payload: ScrapeRequest = { ...request }
    state.value = { phase: 'loading', request: payload }

    try {
      const response = await scrape(payload)
      state.value = { phase: 'completed', request: payload, response }
    }
    catch (error) {
      state.value = toErrorState(payload, error)
    }
  }

  /** Resend the exact payload of the last failed request. */
  async function retry(): Promise<void> {
    if (state.value.phase === 'failed') {
      await submit(state.value.request)
    }
  }

  /** Drop a 400/422 message once the user starts correcting the input. */
  function dismissRejection(): void {
    if (state.value.phase === 'rejected') {
      state.value = { phase: 'idle' }
    }
  }

  return { state, isLoading, submit, retry, dismissRejection }
})
