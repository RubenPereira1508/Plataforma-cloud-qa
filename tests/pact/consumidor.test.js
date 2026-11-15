// consumidor.test.js – Teste do CONSUMIDOR do contrato (Pact).
//
// O que faz:
//   O consumidor é o frontend. Este teste declara, para cada pedido que o frontend
//   faz à API, qual é a resposta de que ele precisa. O Pact levanta um servidor
//   falso (mock), o código REAL do frontend (api-cliente.js) fala com ele, e no
//   fim o Pact escreve o contrato em pacts/loja-frontend-loja-api.json.
//
// Porque é assim:
//   - Usamos matchers (like, eachLike, integer, number, string): o contrato diz
//     a FORMA da resposta ("uma lista de objetos com id inteiro, nome texto,
//     preco número"), não valores exatos. Assim não parte por mudar um nome.
//   - O contrato só exige o que o frontend realmente usa. Para o caso inválido,
//     o frontend só olha para o código 422, por isso o contrato só exige o 422.
//   - Os endereços aqui são os da API (/produtos). O prefixo /api é do nginx e é
//     testado pelos testes E2E (Playwright), não por este contrato.
//
// Como correr (na pasta tests/pact):  npm run test:consumidor

import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { PactV4, MatchersV3 } from '@pact-foundation/pact';

// O código REAL do frontend, o mesmo que a página usa no browser.
import { listarProdutos, criarProduto } from '../../app/frontend/api-cliente.js';

const { eachLike, integer, number, string } = MatchersV3;

const aqui = path.dirname(fileURLToPath(import.meta.url));

// Quem é quem no contrato.
const pact = new PactV4({
  consumer: 'loja-frontend',
  provider: 'loja-api',
  dir: path.resolve(aqui, 'pacts'), // onde o contrato é escrito
});

// A forma de um produto, tal como o frontend o usa (id, nome e preco).
const formaDoProduto = {
  id: integer(1),
  nome: string('Caneta'),
  preco: number(12.5),
};

test('listar produtos: a API devolve uma lista de produtos', async () => {
  await pact
    .addInteraction()
    // Estado que a API tem de preparar antes de responder (ver fornecedor.test.js).
    .given('existe pelo menos um produto')
    .uponReceiving('um pedido para listar os produtos')
    .withRequest('GET', '/produtos')
    .willRespondWith(200, (resposta) => {
      resposta.headers({ 'Content-Type': 'application/json' });
      resposta.jsonBody(eachLike(formaDoProduto)); // lista com pelo menos 1 produto
    })
    .executeTest(async (servidorFalso) => {
      const produtos = await listarProdutos(servidorFalso.url);

      assert.ok(Array.isArray(produtos));
      assert.equal(typeof produtos[0].id, 'number');
      assert.equal(typeof produtos[0].nome, 'string');
      assert.equal(typeof produtos[0].preco, 'number');
    });
});

test('criar produto: a API devolve 201 e o produto criado', async () => {
  await pact
    .addInteraction()
    .uponReceiving('um pedido para criar um produto válido')
    .withRequest('POST', '/produtos', (pedido) => {
      pedido.headers({ 'Content-Type': 'application/json' });
      pedido.jsonBody({ nome: string('Produto do Pact'), preco: number(9.99) });
    })
    .willRespondWith(201, (resposta) => {
      resposta.headers({ 'Content-Type': 'application/json' });
      resposta.jsonBody(formaDoProduto);
    })
    .executeTest(async (servidorFalso) => {
      const resultado = await criarProduto(servidorFalso.url, {
        nome: 'Produto do Pact',
        preco: 9.99,
      });

      assert.equal(resultado.estado, 'criado');
      assert.equal(typeof resultado.produto.id, 'number');
    });
});

test('criar produto inválido: a API responde 422', async () => {
  await pact
    .addInteraction()
    .uponReceiving('um pedido para criar um produto com nome vazio')
    .withRequest('POST', '/produtos', (pedido) => {
      pedido.headers({ 'Content-Type': 'application/json' });
      // Valores exatos (sem matchers): este é o caso inválido de propósito.
      pedido.jsonBody({ nome: '', preco: 5 });
    })
    // Só o código: é só isso que o frontend usa (mostra a mensagem de erro).
    .willRespondWith(422)
    .executeTest(async (servidorFalso) => {
      const resultado = await criarProduto(servidorFalso.url, { nome: '', preco: 5 });

      assert.equal(resultado.estado, 'invalido');
    });
});