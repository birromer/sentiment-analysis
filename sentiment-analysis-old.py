import csv
import unidecode

def limpa(entrada):
    temp = entrada.split()
    saida = []
    i=0
    while i < len(temp):
        if len(temp[i]) > 2:
            tchum = unidecode.unidecode(temp[i]).lower()
            tchuru = ""
            for c in tchum:
                if c >= 'a' and c <= 'z':
                    tchuru += c
            if len(tchuru) > 2:
                saida.append(tchuru)
        i+=1
    return saida

def limpaConteudo(conteudo):
    for i in range(len(conteudo)):
        conteudo[i][0] = limpa(conteudo[i][0])
    return conteudo

def leArquivo(nome):
    with open(nome, encoding="utf8") as arqCSV:
        leitura = csv.reader(arqCSV)
        conteudo = [linha for linha in leitura]
    return conteudo


class nodoA(object):
    def __init__(self, sent=0, acu=0, nro=0):
        self.filhos = [None]*26
        self.sent = sent
        self.acu = acu
        self.nro = nro


class trie(object):
    #inicializa arvore com raiz sendo um nodo simples
    def __init__(self):
        self.raiz = nodoA()

    #busca palavra na arvore e realiza operacoes de acordo com as opcoes descritas
    def buscaPalavra(self, palavra, op=0, pol=0):
        """
        op = 0 -> retorna se palavra existe
        op = 1 -> retorna se palavra existe e atualiza dados
        op = 2 -> retorna o nodo terminal da palavra
        op = 3 -> retorna a polaridade da palavra
        """
        raiz = self.raiz
        for i in range(len(palavra)):
            if raiz.filhos[ord(palavra[i]) - ord('a')] == None:
                return False
            else:
                if i == len(palavra)-1:
                    if op == 1:
                        raiz.filhos[ord(palavra[i]) - ord('a')].acu += int(pol)
                        raiz.filhos[ord(palavra[i]) - ord('a')].nro += 1
                        raiz.filhos[ord(palavra[i]) - ord('a')].sent = raiz.filhos[ord(palavra[i]) - ord('a')].acu / raiz.filhos[ord(palavra[i]) - ord('a')].nro
                    elif op == 2:
                        return raiz.filhos[ord(palavra[i]) - ord('a')]
                    elif op == 3:
                        return raiz.filhos[ord(palavra[i]) - ord('a')].sent
                    return True
                else:
                    raiz = raiz.filhos[ord(palavra[i]) - ord('a')]

    #insere uma palavra na arvore e atualiza dados relacionados a ela
    def inserePalavra(self, palavra, polaridade):
        raiz = self.raiz
        if self.buscaPalavra(palavra):
            self.buscaPalavra(palavra, op=1, pol=polaridade)
#            print("Palavra ja existem incrementando valor do nodo final")
#            print(palavra[-1])
            return True
        for i in range(len(palavra)):
            if raiz.filhos[ord(palavra[i]) - ord('a')] == None:
                if i == len(palavra)-1:
                    raiz.filhos[ord(palavra[i]) - ord('a')] = nodoA()
                    raiz.filhos[ord(palavra[i]) - ord('a')].sent = polaridade
                    raiz.filhos[ord(palavra[i]) - ord('a')].acu = polaridade
                    raiz.filhos[ord(palavra[i]) - ord('a')].nro = 1
#                    print("Chegou no fim da palavra e inseriu o nodo")
#                    print(palavra[i])
                    return True
                else:
                    raiz.filhos[ord(palavra[i]) - ord('a')] = nodoA()
                    raiz = raiz.filhos[ord(palavra[i]) - ord('a')]
#                    print("Inseriu nodo")
#                    print(palavra[i])
            else:
                raiz = raiz.filhos[ord(palavra[i]) - ord('a')]
#                print("Nodo ja existe, atualizando raiz")
#                print(palavra[i])

    #insere palavra na arvore a partir da matriz de conteudo
    def inserePalavras(self, conteudo):
        for i in range(len(conteudo)):
            for w in conteudo[i][0]:
                self.inserePalavra(palavra = w, polaridade=int(conteudo[i][1]))

    #busca recursiva por profundidade, acumulando as palavras e caracteristicas encontradas
    def vaiFundo(self, nod, palavra, palavras, sentimento, acumulado, numero, charAtual):
        if nod != None:
            if nod.nro != 0:
                palavras.append(palavra)
                sentimento.append(nod.sent)
                acumulado.append(nod.acu)
                numero.append(nod.nro)
            for i in range(26):
                novaPal = palavra + chr(i + ord('a'))
                self.vaiFundo(nod.filhos[i], novaPal, palavras, sentimento, acumulado, numero, chr(i + ord('a')))

    #Gera matriz com todas palavras, polaridade relacionada, sentimento acumulado e total de ocorrencias
    def buscaPalavras(self, prefixo=""):
        raiz = self.raiz
        palavras = []
        sentimento = []
        acumulado = []
        numero = []
        if prefixo != "":
            raiz = self.buscaPalavra(prefixo, 2)
        self.vaiFundo(raiz, prefixo, palavras, sentimento, acumulado, numero, '')
        return [palavras, sentimento, acumulado, numero]

    #recebe um tweet e retorna polaridade dele, consultando o dicionario de sentimentos relacionados
    def geraPolaridade(self, tuite):
        tw = limpa(tuite)
        polaridade = 0
        for w in tw:
            polaridade += self.buscaPalavra(w, op=3)
        if polaridade >= 0.1:
            return 1
        elif polaridade <= -0.1:
            return -1
        else:
            return 0

    #gera arquivo csv com 4 colunas, contendo as palavras armazenadas e as caracteristicas relacionadas
    def geraSaidaArvore(self, arquivo, prefixo=""):
        palsM = self.buscaPalavras(prefixo)
        with open(arquivo, 'w') as f:
            topo = ['palavra', 'sentimento', 'acumulado', 'numero']
            writer = csv.DictWriter(f, topo)
            writer.writeheader()
            for i in range(len(palsM[0])):
                writer.writerow({'palavra': palsM[0][i], 'sentimento': palsM[1][i], 'acumulado': palsM[2][i], 'numero': palsM[3][i]})

    #gera arquivo csv com a polaridade do arquivo de entrada de tweets sem polaridade
    def geraSaidaPolarizados(self, arqTuites, arqSaida):
        with open(arqTuites, encoding="utf8") as arqT:
            leitura = csv.reader(arqT)
            tuites = [linha for linha in leitura]
        with open(arqSaida, 'w', encoding="utf8") as arqS:
            topo = ['tweet', 'polaridade']
            writer = csv.DictWriter(arqS, topo)
            writer.writeheader()
            for i in range(len(tuites)):
                polaridade = self.geraPolaridade(str(tuites[i]))
                writer.writerow({'tweet': tuites[i][0], 'polaridade': polaridade})

    def procPalN(self, palavra):
        pals = self.buscaPalavras(prefixo="")
        for i in range(len(pals[0])):
            if pals[0][i] == palavra:
                return pals[1][i]
        return 0


class nodoH(object):
    def __init__(self, palavra=0, ocupado=0, usado=0):
        self.palavra = palavra
        self.tuites = []
        self.ocupado = 0
        self.usado = 0


class raxixe(object):
    def __init__(self):
        self.tabela = [nodoH() for i in range(599)]
        self.proxTabela = []

    def func(self, palavra):
        acu = 0
        for i in range(len(palavra)-1):
            acu += ord(palavra[i])
            acu *= 11
        acu += ord(palavra[-1])
        return acu % 599

    def buscaPalavra(self, palavra, tuite=0, polaridade=0, op=0):
        """
        op = 0 -> insere ou atualiza palavra com tuite e polaridade dele
        op = 1 -> busca palavra e retorna lista de tuites
        """
        chave = self.func(palavra)
        encontrou = 0
        if self.tabela[chave].palavra == palavra:
            if op == 0:
                if [tuite, polaridade] not in self.tabela[chave].tuites:
                    self.tabela[chave].tuites.append([tuite, polaridade])
            elif op == 1:
                return self.tabela[chave].tuites
        else:
            for i in range(chave, len(self.tabela)):
                 if self.tabela[i].usado == 1:
                    if self.tabela[i].palavra == palavra:
                        if op == 0:
                            if [tuite, polaridade] not in self.tabela[i].tuites:
                                self.tabela[i].tuites.append([tuite, polaridade])
                        elif op == 1:
                            return self.tabela[i].tuites
                        encontrou = 1
                        break
                 else:
                    self.tabela[i].palavra = palavra
                    self.tabela[i].tuites.append([tuite, polaridade])
                    self.tabela[i].usado = 1
                    self.tabela[i].ocupado = 1
                    return
            if encontrou == 0:
                if i == len(self.tabela):
                    for j in range(chave):
                        if self.tabela[j].ocupado == 1:
                            if self.tabela[j].palavra == palavra:
                                if op == 0:
                                    if [tuite, polaridade] not in self.tabela[j].tuites:
                                        self.tabela[j].tuites.append([tuite, polaridade])
                                elif op == 1:
                                    return self.tabela[j].tuites
                                encontrou = 1
                                break
                        else:
                            self.tabela[j].palavra = palavra
                            self.tabela[j].tuites.append([tuite, polaridade])
                            self.tabela[j].usado = 1
                            self.tabela[j].ocupado = 1
                            return
                    if encontrou == 0:
                        if j == chave-1:
                            for k in range(len(self.proxTabela)):
                                if self.proxTabela[k].palavra == palavra:
                                    if op == 0:
                                        if [tuite, polaridade] not in self.proxTabela[k].tuites:
                                            self.proxTabela[k].tuites.append([tuite, polaridade])
                                    elif op == 1:
                                        return self.tabela[k].tuites
                                    encontrou = 1
                                    break
                            if encontrou == 0:
                                self.proxTabela.append(nodoH(palavra=palavra, ocupado=1, usado=1))
                                self.proxTabela[-1].tuites.append([tuite, polaridade])
                        else:
                            if op == 0:
                                self.tabela[j].palavra = palavra
                                self.tabela[j].tuites.append([tuite, polaridade])
                                self.tabela[j].usado = 1
                                self.tabela[j].ocupado = 1
                            elif op == 1:
                                return []
                else:
                    if op == 0:
                        self.tabela[i].palavra = palavra
                        self.tabela[i].tuites.append([tuite, polaridade])
                        self.tabela[i].usado = 1
                        self.tabela[i].ocupado = 1
                    elif op == 1:
                        return []

    def insereTuites(self, conteudoO, conteudoL):
        for i in range(len(conteudoL)):
            for w in conteudoL[i][0]:
                self.buscaPalavra(palavra = w, tuite = conteudoO[i][0], polaridade = conteudoL[i][1], op = 0)

    def geraSaidaBusca(self, arqSaida, palavraB):
        with open(arqSaida, 'w', encoding="utf8") as arqS:
            topo = [palavraB]
            writer = csv.DictWriter(arqS, topo)
            writer.writeheader()
            toiotes = self.buscaPalavra(palavra = palavraB, op=1)
            for t in toiotes:
                writer.writerow({palavraB: str(t[0]) + '; ' + str(t[1])})


if __name__ == "__main__":
    """
    arq com os tuites = pt.csv
    arq de saida dicionario = tchum.csv  
    arq com tuites a serem polarizados = tweetsparaPrevisaoUFT8.csv
    arq saida tuites polarizados = tchururu.csv
    """
    
    arqConteudo = input('Digite o nome do arquivo com os tweets avaliados (nao esqueca do .csv): ')
    conteudoO = leArquivo(arqConteudo)
    conteudoL = limpaConteudo(conteudoO)

    #cria arvore r-trie
    arvore = trie()
    #cria hash table
    tabela = raxixe()
    #insere conteudo do arquivo na arvore
    arvore.inserePalavras(conteudoL)   
    #insere conteudo do arquivo na hash table
    tabela.insereTuites(conteudoO = conteudoO, conteudoL = conteudoL)
    #testa input para atualizar o dicionario com novos tweets
    atualizar = input("Deseja atualizar o dicionario com mais tweets? (s/n)")    
    while atualizar == 's':
        arqConteudo = input('Digite o nome do arquivo com os tweets avaliados (nao esqueca do .csv): ')
        #cria matriz com conteudo bruto do arquivo de entrada
        conteudoO = leArquivo(arqConteudo)
        #limpa a entrada e separa em listas de string os tweets
        conteudoL = limpaConteudo(conteudoO)
        #insere todos tweets na arvore
        arvore.inserePalavras(conteudoL)
        #insere todas palavras na hash table
        tabela.insereTuites(conteudoO = conteudoO, conteudoL = conteudoL)
        atualizar = input("Deseja continuar atualizando? (s/n)")    
    #gera arquivo csv com o dicionario de palavras e sentimentos
    arqSaidaArvore = input("Digite o nome do arquivo de saida do dicionario (palavras e seus sentimentos): ")
    arvore.geraSaidaArvore(arqSaidaArvore)
    #recebe arquivo com tweets a serem polarizados e gera arquivo com eles avaliados
    arqTuitesParaPolarizar = input("Digite o nome do arquivo com os tweets a sere polarizados: ")
    arqSaidaPolarizados = input("Digite o nome do arquivo de saida com os tweets polarizados: ")
    arvore.geraSaidaPolarizados(arqTuites=arqTuitesParaPolarizar, arqSaida=arqSaidaPolarizados)
    #entra no loop de pesquisa por palavras:
    palavraBuscada = input("Digite a palavra a ter seus tweets buscados: ")
    arqSaidaHashPal = input("Digite o nome do arquivo de saida com os tweets relacionados a palavra previamente digitada: ")
    tabela.geraSaidaBusca(arqSaida = arqSaidaHashPal, palavraB = palavraBuscada)
    continua = input("Deseja pesquisar por mais tweets relacionados a uma palavra? (s/n)")
    while continua == 's':
        palavraBuscada = input("Digite a palavra a ter seus tweets buscados: ")
        arqSaidaHashPal = input("Digite o nome do arquivo de saida com os tweets relacionados a palavra previamente digitada: ")
        tabela.geraSaidaBusca(arqSaida = arqSaidaHashPal, palavraB = palavraBuscada)
        continua = input("Deseja pesquisar por mais tweets relacionados a uma palavra? (s/n)")
