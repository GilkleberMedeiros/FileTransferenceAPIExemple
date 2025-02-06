## Objetivo
Exemplificar como a transferência de arquivos poderia ser feitas através de requisições de API

## Como funciona
A API recebe o nome do arquivo e o sufixo (Ex: .txt) separados junto com o conteúdo do arquivo em string hexadecimal. A mesma string hexadecimal é devolvida quando requisitado.

Documentação completa em `http://localhost:8000/docs/`

#### Dificuldades no desenvolvimento
Quando a delete view estava sendo desenvolvida eu acabei executando ela sem garantir que os arquivos no sistema de arquivos seriam deletados juntos, o que resultou em um registro fantasma que quando eu tentava apagar normalmente com `file.delete()` e `file.file.delete(save=False)` ele não era deletado e só passava para o id `id + 1`. Isso não acontecia com nenhum outro id, só com esse que ficava pulando para o próximo.

Depois de uma conversa com o chatgpt não consegui obter uma solução satisfatória, à não ser o fato de que meu problema estava realmente sendo causado pelos arquivos orfãs, resultantes das primeiras execuções. 
Sabendo disso, deletei todos os arquivos que ainda restavam
Não funcionou.
Reiniciei o django e o mysql pra ver se as alterações eram gravadas
Não funcinou.
Usei `del(file)` para deletar a referência do arquivo fantasma
De alguma forma funcionou.
Perguntando para o chatgpt depois, ele me falou que `del(model)` no django funcionava igual qualquer outro del, ou seja ele apenas deletava a referência. Não cheguei à investigar diretamente no BD e não consegui reproduzir o erro.