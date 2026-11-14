// 10-carga.js – Teste de CARGA (k6).
//
// O que faz:
//   Simula utilizadores a navegar na loja: sobe até 10 VUs, mantém-nos durante
//   1 minuto e volta a descer. Cada VU abre a página, pede a lista de produtos e
//   verifica a saúde da API, com pausas entre ações como um utilizador real.
//
// Porque existe:
//   Responde à pergunta "aguenta o dia a dia dentro dos limites?". Os thresholds
//   são os critérios de aprovação e vão servir de quality gate na Parte E.
//
// Só fazemos LEITURAS (GET): a API não tem DELETE, por isso milhares de POST
// encheriam a base de dados de lixo para sempre.
//
// Nota: os números valem para ESTE computador (cluster kind dentro do Docker
// Desktop). Servem para comparar antes e depois de uma alteração, não como
// capacidade real de produção.
//
// Como correr:  k6 run 10-carga.js

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8081';

export const options = {
  // Etapas: sobe, mantém, desce.
  stages: [
    { duration: '30s', target: 10 }, // 0 → 10 utilizadores em 30 s
    { duration: '1m', target: 10 },  // mantém 10 utilizadores durante 1 minuto
    { duration: '15s', target: 0 },  // desce até 0
  ],

  thresholds: {
    http_req_failed: ['rate<0.01'],   // menos de 1 % de erros
    http_req_duration: ['p(95)<300'], // p95 abaixo de 300 ms
    checks: ['rate>0.99'],            // mais de 99 % das verificações a passar
  },
};

export default function () {
  // 1. Abre a página da loja (nginx a servir o index.html).
  const pagina = http.get(`${BASE_URL}/`);
  check(pagina, { 'página responde 200': (r) => r.status === 200 });
  sleep(1);

  // 2. A página pede a lista de produtos à API.
  const lista = http.get(`${BASE_URL}/api/produtos`);
  check(lista, {
    'lista responde 200': (r) => r.status === 200,
    'lista é um array': (r) => Array.isArray(r.json()),
  });
  sleep(1);

  // 3. Verificação de saúde (o que um monitor faria).
  const saude = http.get(`${BASE_URL}/api/saude`);
  check(saude, { 'saúde responde 200': (r) => r.status === 200 });
  sleep(1);
}