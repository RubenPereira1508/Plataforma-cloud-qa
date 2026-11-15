// fornecedor.test.js – Verificação do FORNECEDOR do contrato (Pact).
//
// O que faz:
//   O fornecedor é a API. O Pact lê o contrato escrito pelo consumidor
//   (pacts/loja-frontend-loja-api.json), repete cada pedido contra a API
//   VERDADEIRA e compara as respostas com o que o contrato exige.
//
// Como se usa:
//   1) A API tem de estar a correr e acessível em API_URL (por defeito
//      http://localhost:8000, ex.: kubectl port-forward svc/api -n loja 8000:8000).
//   2) Na pasta tests/pact:  npm run test:fornecedor
//
//   Para verificar outra API (por exemplo a versão "quebrada" de demonstração):
//      $env:API_URL = "http://localhost:9000"; npm run test:fornecedor
//
// Estados do fornecedor (stateHandlers):
//   Algumas interações pressupõem dados ("existe pelo menos um produto"). Aqui
//   dizemos ao Pact como preparar esse estado: criamos um produto através da
//   própria API. Sem isto o verificador ignorava o estado e avisava.
//
// Efeito secundário: o pedido "criar um produto válido" do contrato cria um
// produto de verdade na API (e a API não tem DELETE). Pouco, mas fica registado.

import { test } from 'node:test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Verifier } from '@pact-foundation/pact';

const aqui = path.dirname(fileURLToPath(import.meta.url));
const API_URL = process.env.API_URL ?? 'http://localhost:8000';

test('a API cumpre o contrato do frontend', async () => {
  const verificador = new Verifier({
    provider: 'loja-api',
    providerBaseUrl: API_URL,
    pactUrls: [path.resolve(aqui, 'pacts', 'loja-frontend-loja-api.json')],
    logLevel: 'warn',

    stateHandlers: {
      'existe pelo menos um produto': async () => {
        const resposta = await fetch(`${API_URL}/produtos`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nome: 'Produto de estado Pact', preco: 1.5 }),
        });
        if (!resposta.ok) {
          throw new Error(`Não foi possível preparar o estado (HTTP ${resposta.status})`);
        }
      },
    },
  });

  // Falha (com a lista do que não bate certo) se a API não cumprir o contrato.
  await verificador.verifyProvider();
});