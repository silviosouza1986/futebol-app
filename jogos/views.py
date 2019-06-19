from django.shortcuts import render
from django.http import HttpResponse
import sqlite3
from bs4 import BeautifulSoup
import requests
from datetime import date
from os import system

# Create your views here.
def lista_jogos(request):
    cabecalhos = ['Probabilidade da Casa Vencer',
                  'Time da Casa',
                  'Probabilidade de Empate',
                  'Time Visitante',
                  'Probabilidade do Visitante Vencer',
                  'Possível Resultado']
    def listadados():
        conn = sqlite3.connect('jogos/futebol.db')
        #sql = "SELECT * FROM jogosdehoje ORDER BY `Prob_Casa` DESC"
        sql = """SELECT
        `Prob_Casa`,
        `Time_da_Casa`,
        `Prob_Empate`,
        `Time_Visitante`,
        `Prob_Visitante`,
        `Previsão_de_Resultado`
        FROM jogosdehoje ORDER BY `Prob_Casa` DESC"""
        cursor = conn.cursor()
        jogos = cursor.execute(sql)
        jogos = jogos.fetchall()
        listajogos = []
        for jogo in jogos:
            detalhesjogo = []
            for i in jogo:
                if type(i) == int and i != 1 and i != 2:
                    novoitem = str(i) + '%'
                    detalhesjogo.append(novoitem)
                elif i == '1':
                    novoitem = 'Casa Vence'
                    detalhesjogo.append(novoitem)
                elif i == '2':
                    novoitem = 'Visitante Vence'
                    detalhesjogo.append(novoitem)
                elif i == 'X':
                    novoitem = 'Empate'
                    detalhesjogo.append(novoitem)
                else:
                    detalhesjogo.append(i)
            listajogos.append(detalhesjogo)
        return listajogos
    
    jogos = listadados()
    
    return render(request, 'jogos/listajogos.html', {'cabecalhos': cabecalhos, 'jogos': jogos})
    
    
def busca_jogos(request):

    conn = sqlite3.connect('jogos/futebol.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
        create table jogosdehoje (`Time_da_Casa` char (30),
        `ODD_Casa` float,
        `Prob_Casa` int,
        `ODD_Empate` float,
        `Prob_Empate` int,
        `Time_Visitante` char (30),
        `ODD_Visitante` float,
        `Prob_Visitante` int,
        `Previsão_de_Resultado` char (1))
        """)
        print("Tabela criada com sucesso")
    except sqlite3.Error:
        cursor.execute("DROP TABLE jogosdehoje")
        cursor.execute("""
        create table jogosdehoje (`Time_da_Casa` char (30),
        `ODD_Casa` float,
        `Prob_Casa` int,
        `ODD_Empate` float,
        `Prob_Empate` int,
        `Time_Visitante` char (30),
        `ODD_Visitante` float,
        `Prob_Visitante` int,
        `Previsão_de_Resultado` char (1))
        """)

    cursor.close()
    conn.close()

    hoje = date.today()
    page = requests.get("http://pt.scometix.com/arquivo/previsoes_de_" + str(hoje) + ".htm")

    # Substituir (content) por (page.text)


    def time_da_casa(content):
        soup = BeautifulSoup(content, "html.parser")
        time = soup.find_all("span", class_="HomeTeam Cufon")  # retorna uma lista
        return time[0].text

    def time_visitante(content):
        soup = BeautifulSoup(content, "html.parser")
        time = soup.find_all("span", class_="AwayTeam Cufon")  # retorna uma lista
        return time[0].text

    def odd_time_da_casa(content):
        soup = BeautifulSoup(content, "html.parser")
        odd = soup.find_all("span", class_="Quote CufonSymb")
        return odd[0].text

    def odd_empate(content):
        soup = BeautifulSoup(content, "html.parser")
        odd = soup.find_all("span", class_="Quote CufonSymb")
        return odd[1].text

    def odd_visitante(content):
        soup = BeautifulSoup(content, "html.parser")
        odd = soup.find_all("span", class_="Quote CufonSymb")
        return odd[2].text

    def percent_time_da_casa(content):
        soup = BeautifulSoup(content, "html.parser")
        percent = soup.find_all("span", class_="Percent CufonSymb")
        percent = percent[0].text
        percent = percent[0:len(percent) - 1]  # Removendo o sinal de %
        return percent

    def percent_empate(content):
        soup = BeautifulSoup(content, "html.parser")
        percent = soup.find_all("span", class_="Percent CufonSymb")
        percent = percent[1].text
        percent = percent[0:len(percent) - 1]  # Removendo o sinal de %
        return percent

    def percent_visitante(content):
        soup = BeautifulSoup(content, "html.parser")
        percent = soup.find_all("span", class_="Percent CufonSymb")
        percent = percent[2].text
        percent = percent[0:len(percent) - 1]  # Removendo o sinal de %
        return percent

    def prev_resultado(content):
        soup = BeautifulSoup(content, "html.parser")
        resultado = soup.find_all("p", class_="Segno")
        return resultado[0].text

    def busca_dados(casa,
                    oddcasa,
                    percentcasa,
                    oddempate,
                    percentempate,
                    visit,
                    oddvisit,
                    percentvisit,
                    prevresult):
        dados = [casa,
                 oddcasa,
                 percentcasa,
                 oddempate,
                 percentempate,
                 visit,
                 oddvisit,
                 percentvisit,
                 prevresult]
        return dados

    def extract_links(content):
        soup = BeautifulSoup(content, "html.parser")
        links = []

        for tag in soup.find_all("a", href=True):
            if tag["href"].startswith("http://pt.scometix.com/"):
                links.append(tag["href"])

        return links[:len(links) - 1]

    jogos = extract_links(page.text)
    cabecalhos = ['Time da Casa',
                  'Odd-Casa',
                  'Percent-Casa',
                  'Odd-Empate',
                  'Percent-Empate',
                  'Time Visitante',
                  'Odd-Visitante',
                  'Percent-Visitante',
                  'Previsão de Resultado']

    #file = open("previsao.csv", "w")
    #file.write(",".join(cabecalhos) + "\n")


    for link in jogos:
        contador = 0
        try:
            linkdados = requests.get(link).text
            dados = busca_dados(time_da_casa(linkdados),
                                odd_time_da_casa(linkdados),
                                percent_time_da_casa(linkdados),
                                odd_empate(linkdados),
                                percent_empate(linkdados),
                                time_visitante(linkdados),
                                odd_visitante(linkdados),
                                percent_visitante(linkdados),
                                prev_resultado(linkdados))
        except Exception:
            continue

        previsao = ",".join(dados)

        #file.write(previsao + "\n")

        listadados = []

        for dado in dados:
            listadados.append(dados[contador])
            print(cabecalhos[contador] + ": " + dados[contador])
            contador += 1
        print("\n")
        conn = sqlite3.connect('jogos/futebol.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO jogosdehoje (`Time_da_Casa`,
                `ODD_Casa`,
                `Prob_Casa`,
                `ODD_Empate`,
                `Prob_Empate`,
                `Time_Visitante`,
                `ODD_Visitante`,
                `Prob_Visitante`,
                `Previsão_de_Resultado`)
            VALUES ('%s', %f, %d, %f, %d, '%s', %f, %d, '%s')""" % (str(listadados[0]),
                                                                    float(listadados[1]),
                                                                    int(listadados[2]),
                                                                    float(listadados[3]),
                                                                    int(listadados[4]),
                                                                    str(listadados[5]),
                                                                    float(listadados[6]),
                                                                    int(listadados[7]),
                                                                    str(listadados[8])))
            conn.commit()
            cursor.close()
            conn.close()
        except sqlite3.Error:
            continue




    #file.close()
    return HttpResponse('Jogos Atualizados!')
