// loja.spec.ts – Testes ponta a ponta (E2E) da página da Loja.
//
// O que faz:
//   Abre a página num browser verdadeiro (Chromium) e usa-a como um utilizador:
//   vê a lista, preenche o formulário e clica. Passa por tudo: nginx, frontend,
//   API e base de dados.
//
// Porque são poucos:
//   Pela pirâmide de testes, os testes de browser são lentos e frágeis. Cobrem só
//   os caminhos que mais importam; os detalhes (limites, tipos) já estão nos 52
//   testes da API do Passo 7.
//
// Regras que seguimos:
//   - Cada teste usa um nome único, porque a API não tem DELETE e a base de dados
//     guarda tudo. Assim um teste nunca depende de dados de execuções anteriores.
//   - Os elementos são encontrados pelos atributos data-testid do index.html.

import { test, expect } from '@playwright/test';

// Gera um nome diferente a cada chamada (evita colisões entre testes e execuções).
function nomeUnico(prefixo = 'E2E'): string {
  return `${prefixo} ${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
}

test.describe('Página da Loja', () => {
  test('a página abre e deixa de mostrar "A carregar..."', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle('Loja');
    await expect(page.getByRole('heading', { name: 'Loja', level: 1 })).toBeVisible();
    await expect(page.getByTestId('form-produto')).toBeVisible();

    // Quando a API responde, o texto de estado deixa de ser "A carregar...".
    await expect(page.getByTestId('estado')).not.toHaveText('A carregar...');
    await expect(page.getByTestId('estado')).not.toHaveText('Não foi possível carregar os produtos.');
  });

  test('criar um produto faz com que ele apareça na lista', async ({ page }) => {
    const nome = nomeUnico();
    await page.goto('/');

    await page.getByTestId('input-nome').fill(nome);
    await page.getByTestId('input-preco').fill('12.5');
    await page.getByTestId('botao-criar').click();

    // O produto aparece na lista, com o preço formatado em euros (12,50 €).
    // \s* aceita o espaço (inclusive o "espaço não separável") antes do símbolo €.
    const item = page.getByTestId('produto').filter({ hasText: nome });
    await expect(item).toBeVisible();
    await expect(item).toHaveText(/12,50\s*€/);

    // Depois de criar, o formulário fica limpo.
    await expect(page.getByTestId('input-nome')).toHaveValue('');
    await expect(page.getByTestId('input-preco')).toHaveValue('');
  });

  test('o produto criado continua lá depois de recarregar a página', async ({ page }) => {
    const nome = nomeUnico();
    await page.goto('/');
    await page.getByTestId('input-nome').fill(nome);
    await page.getByTestId('input-preco').fill('3.99');
    await page.getByTestId('botao-criar').click();
    await expect(page.getByTestId('produto').filter({ hasText: nome })).toBeVisible();

    // Recarregar prova que o produto foi mesmo guardado na base de dados
    // (e não apenas desenhado na página).
    await page.reload();
    await expect(page.getByTestId('produto').filter({ hasText: nome })).toBeVisible();
  });

  test('preço zero é recusado pela API e a página mostra o erro', async ({ page }) => {
    const nome = nomeUnico('Preco-zero');
    await page.goto('/');

    await page.getByTestId('input-nome').fill(nome);
    await page.getByTestId('input-preco').fill('0');
    await page.getByTestId('botao-criar').click();

    await expect(page.getByTestId('erro')).toContainText('Dados inválidos');

    // Nada foi criado: nem agora, nem depois de recarregar.
    await page.reload();
    await expect(page.getByTestId('estado')).not.toHaveText('A carregar...');
    await expect(page.getByTestId('produto').filter({ hasText: nome })).toHaveCount(0);
  });

  test('nome só com espaços é recusado (regressão do DEF-03)', async ({ page }) => {
    await page.goto('/');

    // O browser deixa passar "   " (o campo não está vazio), por isso quem recusa é a API.
    await page.getByTestId('input-nome').fill('   ');
    await page.getByTestId('input-preco').fill('5');
    await page.getByTestId('botao-criar').click();

    await expect(page.getByTestId('erro')).toContainText('Dados inválidos');
  });

  test('o nome é mostrado como texto e nunca interpretado como HTML', async ({ page }) => {
    const unico = nomeUnico('XSS');
    const nome = `<b>${unico}</b>`;
    await page.goto('/');

    await page.getByTestId('input-nome').fill(nome);
    await page.getByTestId('input-preco').fill('1');
    await page.getByTestId('botao-criar').click();

    const item = page.getByTestId('produto').filter({ hasText: unico });
    await expect(item).toBeVisible();
    // As etiquetas aparecem literalmente no texto...
    await expect(item).toContainText('<b>');
    // ...e não foi criado nenhum elemento <b> dentro do item.
    await expect(item.locator('b')).toHaveCount(0);
  });

  test('se a API não responder, a página avisa em vez de ficar em branco', async ({ page }) => {
    // Simulamos uma falha de rede: o pedido à lista de produtos é cortado.
    await page.route('**/api/produtos', (route) => route.abort());

    await page.goto('/');

    await expect(page.getByTestId('estado')).toHaveText('Não foi possível carregar os produtos.');
  });
});
