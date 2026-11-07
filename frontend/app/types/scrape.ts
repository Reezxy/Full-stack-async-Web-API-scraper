export interface ScrapeRequest {
  url: string
  call_count: number
}

/** 201 body. `status` is the HTTP status of the scraped site, not of the API call. */
export interface ScrapeResponse {
  status: number
  success: boolean
  content: string
}

/** 400, 422 and 500 body. */
export interface ApiErrorBody {
  error: string
}

export type ScrapeState
  = | { phase: 'idle' }
    | { phase: 'loading', request: ScrapeRequest }
    | { phase: 'completed', request: ScrapeRequest, response: ScrapeResponse }
    | { phase: 'rejected', request: ScrapeRequest, message: string }
    | { phase: 'failed', request: ScrapeRequest, message: string }
