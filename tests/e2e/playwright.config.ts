// playwright.config.ts – Configuração dos testes ponta a ponta (E2E) da Loja.
//
// O que faz:
//   Diz ao Playwright onde está a aplicação, que browser usar e o que guardar
//   quando um teste falha (captura de ecrã, vídeo e "trace").
//
// Porque é assim:
//   - BASE_URL vem de uma variável de ambiente, tal como o API_URL no Passo 7.
//     Assim o mesmo teste corre contra o cluster (8081) ou contra o Compose (8080)
//     sem mudar código.
//   - Só usamos o Chromium: um browser chega para provar os fluxos; testar vários
//     browsers aumenta o tempo sem aumentar muito o que aprendemos.
//   - Os ficheiros de falha só são guardados quando algo falha, para não encher o disco.

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',

  // Tempo máximo de cada teste (30 s). Se passar, o teste falha em vez de ficar preso.
  timeout: 30_000,

  // Sem repetições automáticas: um teste que só passa à segunda tentativa
  // esconde um problema (teste instável), por isso preferimos vê-lo falhar.
  retries: 0,

  // Resultado no terminal + relatório HTML navegável.
  reporter: [['list'], ['html', { open: 'never' }]],

  use: {
    // Endereço da aplicação. Por defeito, o cluster (porta 8081 → nginx do frontend).
    baseURL: process.env.BASE_URL ?? 'http://localhost:8081',

    // O que guardar quando um teste falha (ajuda a perceber porquê, sem adivinhar).
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },

  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
