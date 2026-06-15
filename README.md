# COMP-DIS
Projeto realizado por Miguel Lopes (115046), Rodrigo Amaral (15318) e Martim Ceirão (15316)
Neste projeto foi usado como base o projeto criado no semestre anterior na Unidade Curricular Programação Web, na qual nós criamos um website usado para mapeamento de lojas registadas e fotos e ou/vídeos das mesmas. O projeto feito este semestre fui feito em 3 partes distintas.

Fase 1: 
No projeto de Programação Web era usado um local server, nesta fase passamos a usar um cliente e um server que comunicavam usando mensagens em formato JSON, usamos também contentores Docker e um ficheiro de configuração de tal (“composse.yaml”), foi também adicionado uma norma de segurança do sistema onde o contentor só podia ser acedido no computador que estava a dar host.
Fase 2:
Nesta fase foi introduzida uma interface que recolhe as informações do backend e apresenta-as ao cliente, a interface intermédia foi introduzida usando a API REST usada para passar as informações entre as interfaces e a última interface corresponde a contentores utilizando Dockerfiles. Os contentores têm apenas contacto com a API REST que envia as informações pedidas pelo cliente para a interface do cliente.
Fase 3:
Nesta fase adicionamos um dashboard dinâmico para a adição de sensores fornecidos pelo professor. Para os sensores nós conectamo-nos á rede MQTT dos sensores fornecidos para termos uma ligação assíncrona aos dados, dados estes que apenas quando requisitados pelo utilizador eram enviados através da API Rest para o dashboard.

Durante este projeto deparamo-nos com pequenos problemas inicialmente com os Dockerfiles (versão inicial apresentada ao professor que foi corrigida posteriormente) e também nas ligações á rede de sensores.
Este projeto juntamente com o projeto do semestre passado a nível dos alunos que o fizeram demonstra várias limitações do uso dos sistemas pedidos e também o potencial e as vantagens de tal, devido a neste projeto, apenas ter sido apenas adicionado os sensores e modificado para funcionar com uma ligação server cliente, e demonstrar váras mudanças visuais e várias funções tanto aprese
