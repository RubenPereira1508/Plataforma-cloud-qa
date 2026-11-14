// 00-fumo.js – Teste de FUMO de desempenho (k6).
//
// O que faz:
//   Um único utilizador virtual (VU) faz alguns pedidos durante 10 segundos.
//
// Porque existe:
//   Antes de gerar carga a sério, confirma duas coisas: que o teste está bem
//   escrito (endereços certos, respostas esperadas) e que a loja responde. Se este
//   falhar, não vale a pena subir a carga.
//
// Como correr (a partir da pasta tests\k6):
//   k6 run 00-fumo.js
//   k6 run -e BASE_URL=http://localhost:8080 00-fumo.js   (contra o Compose)

import http from 'k6/http';
import { check, sleep } from 'k6';

// Endereço da loja (o nginx, que reencaminha /api/ para a API).
// Por defeito é o cluster; pode mudar-se com -e BASE_URL=...
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8081';

export const options = {
  vus: 1,
  duration: '10s',

  // Regras de aprovação (thresholds). Se alguma falhar, o k6 termina com erro.
  thresholds: {
    http_req_failed: ['rate<0.01'],   // menos de 1 % de pedidos com erro
    http_req_duration: ['p(95)<500'], // 95 % dos pedidos abaixo de 500 ms
    checks: ['rate==1'],              // todas as verificações têm de passar
  },
};

// O que cada utilizador virtual repete em ciclo.
export default function () {
  const saude = http.get(`${BASE_URL}/api/saude`);
  check(saude, { '/api/saude responde 200': (r) => r.status === 200 });

  const lista = http.get(`${BASE_URL}/api/produtos`);
  check(lista, {
    '/api/produtos responde 200': (r) => r.status === 200,
    '/api/produtos devolve uma lista': (r) => Array.isArray(r.json()),
  });

  sleep(1); // pausa de 1 s: um utilizador real não faz pedidos sem parar
}