// Programa válido completo da MiniLang: atribuição, aritmética com
// precedência, while, for, if/else, booleanos e comentários.

/* Parte 1: contagem regressiva com while */
x = 10;
y = 2 * (x + 5);        // precedência: y = 2 * 15 = 30
print(y);

while (x > 0) {
    print(x);
    x = x - 1;
}

/* Parte 2: soma de 0 a 4 com for */
soma = 0;
for (i = 0; i < 5; i = i + 1) {
    soma = soma + i;
}

if (soma > 20) {
    print(soma);
} else {
    print(0);
}

/* Parte 3: fatorial de 5 e booleanos */
fat = 1;
for (n = 1; n <= 5; n = n + 1) {
    fat = fat * n;
}
print(fat);             // 120

par = (fat / 2) * 2 == fat;
print(par);             // true
