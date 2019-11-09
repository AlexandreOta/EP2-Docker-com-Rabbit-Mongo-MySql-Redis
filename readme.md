EP2-DOCKER COMPOSE

Para executar(no diretório dos arquivos):
>>docker-compose up



O exercício utiliza os seguintes serviços:

RABBITMQ (Imagem rabbitmq:3-management) 
    O RabbitMQ é serviço de gerenciamento de filas para recebimento e entrega de mensagens entre aplicações, mesmo que tenham sido desenvolvidas em diferentes linguagens de programação. 
    Nesse exercício estaremos controlando 3 filas (c1,c2,c3), através da "exchange" (filas) e utilizando o protocolo "fanout" (que copia a mensagem para todas as filas).

MONGO (Imagem mongo)
    MongoDB é um software de banco de dados orientado a documentos livre, de código aberto e multiplataforma
    O mongo foi utilizado para armazenar o log das transações. 
    Na coleção: "LogsSenac" temos os seguintes atributos:
            'comando'   : insert/delete/update
            'id'        : id informado
            'nome'      : nome informado
            'data'      : datetime do sistema  

REDIS (Imagem redis)
    O Redis é um armazenamento de estrutura de dados de chave-valor de código aberto e na memória.
    Foi utilizado uma chave "inserts" onde fazenmos o incremento a cada comando de insert.

MYSQL (Imagem mysql:5.7)
    O MySQL é um sistema de gerenciamento de banco de dados, que utiliza a linguagem SQL como interface-Banco de dados relacional.
    Foi criado o banco de dados "DBSenac" e dentro a tabela "Usuarios" com os seguintes campos:
            id    int        PRIMARY KEY
            nome VARCHAR(20)
    A inicialização do banco foi através do arquivo /db/init.sql - chamado dentro do docker-compose.yml na criação do volume do container.

PRODUTOR
    Criado em python e utilizando flask, envia para o RabbitMQ os comandos.
    Acesso por: http://localhost:5000

RECEPTOR1
    Acessa a fila C1 e com os dados armazena os logs no mongo
RECEPTOR2
    Acessa a fila C2 e caso encontre um comando de insert faz um incremento na chave inserts do redis
RECEPTOR3
    Acessa a fila C3 e atualiza no MySql os comandos de atualização na tabela de Usuarios

MONITOR
    Acessa os diversos bancos e mostra o conteúdo dos dados
    Acesso por: http://localhost:5005





Problemas e soluções(ou não):
    1)Os receptores inicializam as filas do RabbitMQ e subiam antes do RabbitMQ estar ok. 
        Foi implementado(copiado) a função "wait-for-it.sh" para controlar a inicialização dos receptores.
    2) A tabela de usuários no MySql foi implementada com chave primária no campo "id"
        Como não fazemos o controle de volta não apresentamos erros.
    3) Os receptores foram criados em um único código ("recebe.py").
        Poderiam ser separados pois cada receptor trata funções diferentes e acredito que pode afetar a performance do docker, pois em todos eles, subimos sempre os 3 bancos de dados.






Para testar o Mongo
docker exec -it <<<05_ep2_db_mongo_1>>> mongo

Para testar o MYSQL
docker exec -it <<<05_ep2_db_mysql_1>>> mysql -uroot -proot
