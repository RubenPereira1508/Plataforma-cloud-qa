// app.js – Lógica da página da Loja (Projeto A).
//
// O que faz:
//   Mostra os produtos e permite criar novos, falando com a API através do
//   endereço /api (o nginx reencaminha para a API; ver nginx.conf).
//
// Porque está num ficheiro à parte (e não dentro do index.html):
//   Para a Content Security Policy do nginx poder proibir JavaScript "inline"
//   (escrito no HTML), que é a via típica de ataques XSS. O ZAP avisou da falta
//   de CSP no Passo 8, Parte C. Ver também estilo.css.
//
// Passo 8, Parte D: os pedidos HTTP à API passaram para o api-cliente.js, que este
// ficheiro importa. É um módulo (<script type="module">), por isso corre depois
// de a página estar carregada, sem precisar de "defer".
//
// Boa prática mantida: os dados vindos da API são inseridos com textContent
// (e não innerHTML), para evitar XSS.

import { listarProdutos, criarProduto } from "./api-cliente.js";

// Prefixo dos pedidos à API. O nginx reencaminha /api/... para a API.
// Como o browser só fala com UM endereço (o do nginx), não há problemas de CORS.
const API = "/api";

const listaEl = document.getElementById("lista-produtos");
const estadoEl = document.getElementById("estado");
const erroEl = document.getElementById("erro");
const formEl = document.getElementById("form-produto");

// Formata números como moeda em português (ex.: 49,90 €).
const euros = new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR" });

// Vai buscar os produtos à API e desenha a lista.
async function carregarProdutos() {
  estadoEl.textContent = "A carregar...";
  try {
    const produtos = await listarProdutos(API);

    listaEl.replaceChildren(); // limpa a lista
    for (const p of produtos) {
      const li = document.createElement("li");
      li.dataset.testid = "produto";
      li.textContent = `${p.nome} – ${euros.format(p.preco)}`; // textContent: seguro contra XSS
      listaEl.appendChild(li);
    }
    estadoEl.textContent = produtos.length === 0 ? "Ainda não há produtos." : "";
  } catch (e) {
    estadoEl.textContent = "Não foi possível carregar os produtos.";
  }
}

// Envia o formulário para criar um produto.
formEl.addEventListener("submit", async (evento) => {
  evento.preventDefault(); // evita que o browser recarregue a página
  erroEl.textContent = "";

  const dados = {
    nome: document.getElementById("nome").value,
    preco: parseFloat(document.getElementById("preco").value),
  };

  try {
    const resultado = await criarProduto(API, dados);

    if (resultado.estado === "invalido") {
      // A API rejeitou os dados (validação do servidor, código 422).
      erroEl.textContent = "Dados inválidos: o nome tem de ter 1 a 100 caracteres e o preço tem de ser maior que 0.";
      return;
    }

    formEl.reset();
    await carregarProdutos(); // atualiza a lista com o produto novo
  } catch (e) {
    erroEl.textContent = "Não foi possível criar o produto. Tenta de novo.";
  }
});

// Ao abrir a página, carrega os produtos.
carregarProdutos();