// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@nuxt/eslint', '@pinia/nuxt', '@vueuse/nuxt'],

  css: ['~~/assets/css/main.css'],

  app: {
    head: {
      title: 'Async Web Scraper',
      meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }]
    }
  },

  runtimeConfig: {
    public: {
      // URL of the Django backend; override with NUXT_PUBLIC_SCRAPER_API_URL.
      scraperApiUrl: 'http://localhost:8000'
    }
  },

  devtools: { enabled: true },

  compatibilityDate: '2025-07-15'
})
