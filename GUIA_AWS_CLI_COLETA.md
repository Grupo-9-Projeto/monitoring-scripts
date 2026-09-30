# Configuração do AWS CLI

Este documento apresenta os passos necessários para configurar o AWS CLI em uma máquina local utilizando as credenciais temporárias disponibilizadas pelo ambiente **AWS Academy / VocLabs**.

## 1. Verificar a instalação

Abra o CMD ou terminal e execute:

```cmd
aws --version
```

Caso o AWS CLI esteja instalado, será exibida a versão instalada.

---

## 2. Obter as credenciais da AWS

As credenciais necessárias são disponibilizadas pelo próprio ambiente AWS Academy.

No laboratório do AWS Academy/VocLabs:

1. Acesse o ambiente da AWS.
2. Abra a seção **AWS Details**.
3. Localize **AWS CLI**.
4. Copie as informações de acesso disponibilizadas pelo ambiente.

Normalmente serão fornecidos:

* **AWS Access Key ID**
* **AWS Secret Access Key**
* **AWS Session Token**
* **Região padrão (Region)**

> As credenciais são temporárias e vinculadas à sessão do laboratório. Não compartilhe esses valores nem os adicione ao código-fonte ou ao repositório do projeto.

---

## 3. Configurar o AWS CLI

Execute:

```cmd
aws configure
```

O terminal solicitará algumas informações:

```text
AWS Access Key ID: <Access Key ID>
AWS Secret Access Key: <Secret Access Key>
Default region name: <Region>
Default output format: json
```

Informe os valores correspondentes aos dados disponibilizados em **AWS Details → Cloud Access**.

### Session Token

Como o AWS Academy utiliza credenciais temporárias, também é necessário configurar o **Session Token**:

```cmd
aws configure set aws_session_token "<Session Token>"
```

Substitua `<Session Token>` pelo token fornecido pelo ambiente.

---

## 4. Validar a configuração

Após configurar as credenciais, execute:

```cmd
aws sts get-caller-identity
```

Se a configuração estiver correta, o comando retornará informações sobre a identidade da sessão AWS, confirmando que o cliente está autenticado.

---

## 5. Renovação das credenciais

As credenciais fornecidas pelo AWS Academy/VocLabs possuem validade limitada.

Quando a sessão do laboratório expirar, será necessário:

1. Acessar novamente o **AWS Details → Cloud Access**.
2. Obter as novas credenciais.
3. Executar novamente `aws configure`.
4. Atualizar o `aws_session_token`.

Não é necessário alterar o código da aplicação para renovar as credenciais.

---

## 6. Utilização pelo Python/Boto3

Depois que o AWS CLI estiver configurado, aplicações Python que utilizam o **Boto3** podem utilizar automaticamente essas credenciais.

Por exemplo:

```python
import boto3

s3 = boto3.client("s3")
```

Não é necessário colocar Access Key, Secret Key ou Session Token diretamente no código.

Dessa forma, as credenciais permanecem separadas da aplicação e o mesmo ambiente configurado pelo AWS CLI pode ser utilizado pelo Boto3.
