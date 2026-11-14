// 20-esforco.js – Teste de ESFORÇO (stress) (k6).
//
// O que faz:
//   Sobe a carga por degraus (10 → 30 → 60 → 100 VUs) para descobrir ONDE a loja
//   começa a degradar-se e COMO falha (mais lenta? erros? reinícios?).
//
// Porque existe:
//   O teste de carga prova que aguenta o normal. Este procura o limite. Saber como
//   o sistema falha é tão importante como saber que aguenta.
//
// Proteção do cluster:
//   O cluster corre no teu PC. Se mais de 5 % dos pedidos falharem, o k6 aborta o
//   teste sozinho (abortOnFail) para não deixar os Pods a reiniciar sem parar.
//   Um aborto aqui não é um erro do teste: É O RESULTADO (encontrámos o limite).
//
// Como correr:  k6 run 20-esforco.js
// Enquanto corre, vê noutro terminal:  kubectl get pods -n loja -w

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8081';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '30s', target: 30 },
    { duration: '30s', target: 60 },
    { duration: '30s', target: 100 },
    { duration: '20s', target: 0 }, // desce: vê-se se a loja recupera
  ],

  thresholds: {
    // Aborta se os erros passarem 5 % (avalia só passados 10 s, para ignorar o arranque).
    http_req_failed: [{ threshold: 'rate<0.05', abortOnFail: true, delayAbortEval: '10s' }],
    // Informativo: o p95 não faz abortar, mas aparece no relatório.
    http_req_duration: ['p(95)<1000'],
  },
};

export default function () {
  const lista = http.get(`${BASE_URL}/api/produtos`);
  check(lista, { 'lista responde 200': (r) => r.status === 200 });
  sleep(0.5);
}