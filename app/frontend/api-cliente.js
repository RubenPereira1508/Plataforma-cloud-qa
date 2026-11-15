// api-cliente.js – As chamadas do frontend à API da Loja (Projeto A).
//
// O que faz:
//   Reúne num só sítio os pedidos HTTP que a página faz à API: listar produtos e
//   criar um produto. Não mexe na página (não há aqui nada de HTML).
//
// Porque existe (Passo 8, Parte D):
//   O teste de contrato (Pact) tem de usar o MESMO código que a página usa para
//   falar com a API. Se o teste usasse uma cópia, podia passar mesmo que o código
//   verdadeiro estivesse errado. Por isso estas funções estão num módulo à parte,
//   importado pelo app.js (no browser) e pelo teste do Pact (em Node).
//
// O endereço da API vem sempre de fora (parâmetro "base"): na página é "/api"
// (o nginx reencaminha), no teste do Pact é o endereço do servidor falso do Pact.

// Pede a lista de produtos. Devolve um array de { id, nome, preco }.
// Se a API não responder com sucesso, lança um erro (a página mostra o aviso).
export async function listarProdutos(base) {
  const resposta = await fetch(`${base}/produtos`);
  if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
  return resposta.json();
}

// Pede a criação de um produto ({ nome, preco }).
// Devolve:
//   { estado: "criado", produto }  – a API respondeu 201 e devolveu o produto
//   { estado: "invalido" }         – a API recusou os dados (422)
// Qualquer outro erro (ex.: 500, API em baixo) lança uma exceção.
export async function criarProduto(base, dados) {
  const resposta = await fetch(`${base}/produtos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  });

  if (resposta.status === 422) return { estado: "invalido" };
  if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
  return { estado: "criado", produto: await resposta.json() };
}