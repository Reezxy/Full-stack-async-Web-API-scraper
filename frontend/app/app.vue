<script setup lang="ts">
const repoUrl = 'https://github.com/Reezxy/Full-stack-async-Web-API-scraper'
</script>

<template>
  <UApp>
    <div class="flex min-h-screen flex-col bg-default">
      <header class="sticky top-0 z-10 border-b border-default bg-default/80 backdrop-blur">
        <nav class="mx-auto flex max-w-5xl items-center gap-3 px-4 py-3 sm:px-6">
          <UIcon
            name="i-lucide-scan-search"
            class="size-5 text-primary"
          />
          <span class="font-semibold text-highlighted">Async Web Scraper</span>
          <div class="ms-auto flex items-center gap-1">
            <UButton
              :to="repoUrl"
              target="_blank"
              icon="i-lucide-github"
              color="neutral"
              variant="ghost"
              aria-label="Source code on GitHub"
            />
            <UColorModeButton />
          </div>
        </nav>
      </header>

      <main class="mx-auto w-full max-w-5xl flex-1 px-4 py-8 sm:px-6">
        <NuxtPage />
      </main>
    </div>
  </UApp>
</template>
