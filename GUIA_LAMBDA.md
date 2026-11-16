# ETL no modelo Lambda (disparada por evento do S3)

```
máquina monitorada --(captura.py/s3.py)--> S3 raw/ (capturas, depois processos) --evento--> Lambda etlTrusted --> S3 trusted/ --evento--> Lambda etlClient --> S3 client/

Jira --(a cada 1 hora)--> Lambda etlTrusted --> S3 trusted/chamados/chamados.csv
                                                      |--evento--> Lambda etlClient --> S3 client/previsoes/previsoes.json (UM JSON, por máquina)
                                                                                              |
Banco MySQL (SELECT: empresas, SLA, máquinas, analistas) --> back Node (filtra o JSON por gerente e calcula) --> página de Previsões
```

Cada Lambda recebe do S3 o **nome do arquivo que acabou de chegar** e processa só ele.

> **Por que o gatilho da etlTrusted é a pasta `processos/` e não a de `capturas/`?**
> A coleta envia o CSV de capturas **primeiro** e o de processos **depois**. A etlTrusted junta os dois
> (resumo de processos + capturas). Se ela disparasse no CSV de capturas, poderia rodar antes de o de processos
> chegar. Disparando no de processos (o último), os dois arquivos do lote já estão no S3.
> Ela descobre sozinha o CSV de capturas correspondente (`processos_<MAC>_<data>.csv` -> `dados_<MAC>_<data>.csv`).
Não precisa mais do nome do bucket no código: ele vem no próprio evento.

## Criar as 2 Lambdas (repita para cada uma)

| | etlTrusted | etlClient |
|---|---|---|
| Arquivo | `etlTrusted.py` | `etlClient.py` |
| Handler | `etlTrusted.lambda_handler` | `etlClient.lambda_handler` |
| Trigger (prefixo) | `raw/dispositivos/processos/` | `trusted/dispositivos/capturas/` |
| Trigger (sufixo) | `.csv` | `.csv` |

1. **Runtime:** Python 3.12. **Memória:** 256 MB. **Timeout:** 1 minuto.
2. **Pandas:** em *Layers* > *Add a layer* > *AWS layers* > escolha **AWSSDKPandas-Python312**
   (o Lambda já tem boto3, mas não tem pandas).
3. **Permissão (role da Lambda):** `s3:GetObject` e `s3:PutObject` no bucket (`arn:aws:s3:::SEU-BUCKET/*`).
4. **Trigger:** *Add trigger* > S3 > seu bucket > evento *All object create events* >
   prefixo e sufixo da tabela acima.
5. Importante: nunca use o mesmo prefixo na entrada e na saída, senão a Lambda dispara a si mesma sem parar.

## Testar sem esperar o S3

Na aba *Test* da Lambda, use este evento (troque bucket e arquivo por um que exista):

```json
{
  "Records": [
    { "s3": { "bucket": { "name": "SEU-BUCKET" },
              "object": { "key": "raw/dispositivos/processos/30%3A56%3A0f%3A06%3A7a%3A88/2026/11/10/processos_30560f067a88_20261110_100000.csv" } } }
  ]
}
```

Local (com credenciais AWS configuradas): `python etlTrusted.py SEU-BUCKET raw/dispositivos/processos/.../processos_<MAC>_<data>.csv`

## Atenção

- Se o CSV de processos de um lote não chegar ao S3, esse lote não gera arquivo no trusted.
- A Lambda só processa arquivos **novos**. Arquivos que já estavam em `raw/` antes de criar o trigger
  não são processados sozinhos (ela não varre mais o bucket). Para reprocessar um arquivo, envie-o de novo ao S3.
- Se uma Lambda der erro, o S3 tenta de novo automaticamente 2 vezes; veja o log no CloudWatch.

---

# Previsões: o que mais configurar nas MESMAS duas Lambdas

Não existe uma terceira Lambda, e **a ETL não acessa o banco de dados**.

- **etlTrusted** (também por horário): busca os chamados no Jira e guarda em `trusted/chamados/chamados.csv`
  (só chamados que têm o MAC da máquina na descrição).
- **etlClient** (quando chega `trusted/chamados/chamados.csv`): monta **um único JSON**, `client/previsoes/previsoes.json`,
  com os números de cada máquina (MAC): chamados por semana (8 semanas), concluídos por semana, tempo de resolução
  e mapa dia da semana x horário. É o mesmo JSON para todo mundo.
- **Back (Node):** faz o SELECT no banco (empresas, SLA, máquinas e analistas do gerente), filtra o JSON da ETL
  pelos MACs desse gerente e calcula a previsão. A página só desenha.

## etlTrusted — acrescentar

1. **Variáveis de ambiente:**

   | Variável | Valor |
   |---|---|
   | `BUCKET_S3` | nome do bucket |
   | `JIRA_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`, `JIRA_PROJECT_KEY` | os mesmos do java-jira |

2. **Segundo gatilho:** *Add trigger > EventBridge (schedule)* com `rate(1 hour)`. (O gatilho do S3 continua como está.)
3. **Timeout:** aumente para **2 minutos**.
4. Não coloque a Lambda dentro de uma VPC (ela precisa acessar a internet para falar com o Jira).
   Não precisa de layer nova nem de acesso ao banco.

## etlClient — acrescentar

1. **Segundo gatilho do S3:** mesmo bucket, evento *All object create events*,
   prefixo `trusted/chamados/` e sufixo `.csv`. (O gatilho de `trusted/dispositivos/capturas/` continua.)
2. **Timeout:** aumente para **1 minuto**. Não precisa de variável de ambiente nem de layer nova.

## Permissões

- Role da etlTrusted: `s3:PutObject` também em `trusted/chamados/*`.
- Role da etlClient: `s3:GetObject` em `trusted/chamados/*` e `s3:PutObject` em `client/previsoes/*`.
- O back Node (credenciais AWS da máquina dele) precisa de `s3:GetObject` em `client/previsoes/*`.

## Testar

Na etlTrusted, aba *Test* com o evento `{}`. Ela grava o `chamados.csv`, o S3 dispara a etlClient, e deve aparecer
`client/previsoes/previsoes.json`. Até a primeira execução, a página mostra "DADOS SIMULADOS".

Quem recebe previsão: usuários com `cargo = 'gerente'`. Os chamados de cada gerente são os das máquinas (MAC)
das empresas vinculadas a ele em `usuario_empresa`.
