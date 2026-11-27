// Programa inválido: laço for mal formado (falta a cláusula de atualização).
//
// Resultado esperado ao executar:
//   Erro sintático [linha 13, coluna 19]: esperado ';' após a condição do for
//   (o for exige as três cláusulas), encontrado ')'
//
// Regra violada: for = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco
// Após a condição "i < 10" a gramática exige ";" e depois a atualização.

soma = 0;

// erro: for com apenas duas cláusulas
for (i = 0; i < 10) {
    soma = soma + i;
}

print(soma);
