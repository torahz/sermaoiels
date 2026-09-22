# Sermões · Igreja Esperança

Site estático para GitHub Pages e integrador gráfico Windows. O acervo está no
`index.html`, em um bloco JSON e em cartões HTML gerados a partir dele. A página
também permite abrir as gravações quando JavaScript está desativado.

## Uso do integrador

1. Abra **Integrador-Sermoes.exe**. Não precisa instalar Python nem bibliotecas.
2. Localize o `index.html` **atualizado** deste projeto. O programa lembra o caminho
   quando consegue salvar `integrador-config.json` ao lado do executável.
3. Selecione o ano e um domingo. Estação, celebração e ciclo são automáticos.
4. Preencha série, preletor, título e o link original do Drive. As caixas de série
   e preletor também oferecem os nomes já cadastrados.
5. Confira a prévia e clique em **Salvar novo sermão**.
6. Publique o `index.html` atualizado pelo seu fluxo habitual do GitHub.

O programa inclui novos sermões; a aba Acervo preservado permite consultar os
existentes. Ela não modifica registros históricos. Uma data ou URL repetida gera
um aviso, pois pode representar outro culto ou um erro de cadastro.

Cada salvamento cria `backups/index-AAAAMMDD-HHMMSS-....html`. Para restaurar,
feche o integrador, copie o backup desejado por cima de `index.html` e abra-o de
novo. Se outro programa alterar o HTML enquanto ele está aberto, o integrador
recusa o salvamento até que você reabra o arquivo.

O EXE atual é para **Windows x64**. O código-fonte usa somente a biblioteca padrão
do Python (incluindo Tkinter). Para executar a versão fonte, use uma instalação
Python com Tcl/Tk completo. Para reconstruir o EXE, em um ambiente Windows de
desenvolvimento: `python -m pip install pyinstaller` e
`python -m PyInstaller --onefile --windowed --name Integrador-Sermoes integrador.py`.
O usuário do EXE não precisa dessas ferramentas.

## Calendário

O calendário usa o cômputo gregoriano da Páscoa. A interface aceita anos de 2026 a
4099; não há uma tabela que precise ser preenchida a cada ano. Os domingos são
calculados, inclusive em anos com 53 domingos. Testes cobrem todos os anos de
2026 a 2200 e comparam os 52 domingos de 2026 com a lista fornecida pela igreja.

Regras locais aprovadas:

- Natal até 5 de janeiro; se 6 de janeiro cair no domingo, celebra-se Epifania.
- Primeiro domingo após Epifania: Batismo; último antes da Quaresma: Transfiguração.
- Quaresma, Ramos, Páscoa, Ascensão, Pentecostes e Trindade são relativos à Páscoa.
- Após Pentecostes até junho; Tempo Comum a partir de julho.
- Todos os domingos de setembro são da Estação da Criação; o segundo é o aniversário.
- A numeração após Pentecostes continua durante setembro.
- Último domingo de outubro: Reforma Protestante.
- Cristo Rei é o domingo anterior ao Advento; Advento tem quatro domingos antes do Natal.
- Natal em um domingo recebe o nome Domingo de Natal; os seguintes são numerados depois do Natal.
- O ciclo litúrgico é identificado pelo ano em que termina, começando no Advento anterior.

Os nomes abreviados do PDF foram expandidos no calendário novo (Dom. → Domingo).
Os 78 registros originais mantêm seus textos, datas, estações e URLs, mesmo quando
diferem do calendário aprovado. As novas regras só são aplicadas aos novos cadastros.

## Site e aplicativo instalável

- Último sermão em destaque; ordenação inicial pela data da pregação, decrescente.
- Busca ignora acentos e caixa; filtros Ano, Mês, Preletor, Série e Estação se combinam.
- Variantes de caixa e acentos no nome de uma série são agrupadas somente no filtro.
  O texto original de cada sermão permanece intacto.
- Anos são extraídos automaticamente do acervo; os próximos anos aparecem ao cadastrar.
- A opção Adicionados recentemente usa a data de cadastro dos novos sermões. O
  histórico não recebeu datas de publicação inventadas e vem depois, pela data da pregação.
- Links compartilháveis por sermão e por filtros. As URLs originais do Drive não mudam.
- Botão com instruções de instalação para Android, iPhone e computador.
- Service worker usa a pasta do projeto, rede primeiro e catálogo em cache como alternativa.
  Gravações do Drive não são baixadas para o cache do site e continuam exigindo internet.
- Um novo `index.html` é buscado online a cada acesso. Mudanças no service worker
  entram em vigor ao fechar todas as janelas do aplicativo e reabri-lo.

Para testar localmente com cache/PWA, execute `python -m http.server 8000` nesta
pasta e abra `http://localhost:8000`. Abrir o HTML diretamente também mostra o
acervo, mas não habilita o service worker. A instalação real em Android/iOS não
foi testada em aparelhos físicos durante esta atualização.

## Publicação

A primeira publicação precisa incluir **index.html, styles.css, core.js, app.js,
sw.js, manifest.json, background.webp e background-mobile.webp**, mantendo logo e
ícones existentes. Não publique somente o HTML nessa primeira atualização.

Depois, os novos cadastros pelo integrador alteram apenas o `index.html`.
O EXE, os backups e a configuração local estão no `.gitignore`; não precisam ir
para o GitHub Pages. O PNG original foi mantido, mas a página usa os WebP menores.

Nenhum commit, push ou publicação é feito pelo integrador.

## Validação

```text
python -m unittest discover -s tests -p "test_*.py" -v
node tests/site.test.cjs
node tests/sw.test.cjs
```

O workflow `.github/workflows/validar.yml` executa as mesmas verificações.
`tests/acervo-original.json` é o registro de referência para proteger os 78
sermões anteriores; não o atualize para mascarar uma diferença de dados.
