// api-quebrada.js – API de DEMONSTRAÇÃO que quebra o contrato de propósito.
//
// O que faz:
//   Levanta um servidor mínimo na porta 9000 que responde como a API da Loja, MAS
//   com o campo "valor" no lugar de "preco" (como se alguém tivesse renomeado o
//   campo na API sem avisar ninguém).
//
// Porque existe:
//   Para provarmos que o teste de contrato APANHA esta quebra: os testes da API
//   (pytest) passariam todos, porque testam a API nova, e o frontend só falharia
//   em produção. O Pact falha logo na verificação.
//
// Não faz parte da loja e nunca vai para o cluster; só serve para esta demonstração.
//
// Como usar (dois terminais, na pasta tests/pact):
//   Terminal 1:  node api-quebrada.js
//   Terminal 2:  $env:API_URL = "http://localhost:9000"; npm run test:fornecedor

import http from 'node:http';

let proximoId = 1;

const servidor = http.createServer((pedido, resposta) => {
  const enviar = (codigo, corpo) => {
    resposta.writeHead(codigo, { 'Content-Type': 'application/json' });
    resposta.end(corpo === undefined ? '' : JSON.stringify(corpo));
  };

  if (pedido.method === 'GET' && pedido.url === '/produtos') {
    // "valor" em vez de "preco": é aqui que o contrato é quebrado.
    return enviar(200, [{ id: 1, nome: 'Caneta', valor: 12.5 }]);
  }

  if (pedido.method === 'POST' && pedido.url === '/produtos') {
    let texto = '';
    pedido.on('data', (pedaco) => (texto += pedaco));
    pedido.on('end', () => {
      const dados = JSON.parse(texto || '{}');
      if (!dados.nome || !(dados.preco > 0)) return enviar(422, { detail: 'inválido' });
      return enviar(201, { id: proximoId++, nome: dados.nome, valor: dados.preco });
    });
    return;
  }

  enviar(404, { detail: 'não existe' });
});

servidor.listen(9000, () => console.log('API quebrada a escutar em http://localhost:9000'));