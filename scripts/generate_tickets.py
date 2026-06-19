"""Gera support_tickets.csv — chamados de atendimento BeFly em PT-BR livre.

Cada ticket é uma mensagem que um cliente mandaria pro time de atendimento
da BeFly (agência de viagens). Os campos a serem extraídos via ai_query
incluem destino, dadas, orçamento, perfil, urgência, intenção etc.
Regex puro aqui é impossível — mesmo conceito aparece em 5 formas.
"""
from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(7)

OUT = Path(__file__).resolve().parent.parent / "data" / "support_tickets.csv"

TICKETS = [
    "Oi! Tô pensando em levar minha família pra Cancún em janeiro. Somos 4 (eu, esposa, 2 filhos de 8 e 12). Queria all inclusive perto da praia, mas não muito caro. Já viajamos com vocês ano passado pra Punta Cana e adoramos. Pode ser entre 10 e 20 de janeiro. Precisamos sair de Curitiba, se possível direto.",
    "Bom dia, gostaria de remarcar a minha passagem do dia 15/07 para o dia 22/07, mesmo voo se possível. Localizador BF89X12.",
    "URGENTE: cheguei no aeroporto e o voo está cancelado. Ninguém me atende no balcão. Voo BF1234 GIG→GRU. O que eu faço??",
    "Olá, vocês têm pacote para Bariloche em julho? Lua de mel, 2 adultos. Orçamento até 18 mil reais total. Saindo de São Paulo.",
    "Bom dia. Preciso de um relatório consolidado dos gastos com viagens corporativas da nossa empresa (Tech XYZ) do último trimestre. Pode ser por e-mail.",
    "Quero cancelar a viagem que comprei semana passada pra Salvador. Mudaram o feriado da empresa. Preciso de reembolso integral, é dentro do prazo de 7 dias.",
    "Vocês operam viagens corporativas com NDC da Latam? Estamos avaliando trocar de TMC.",
    "Comprei seguro viagem mas perdi o número da apólice. Pode me reenviar? Email cadastrado: maria.silva@empresa.com.br",
    "Oi! Sou viajante Diamond, 12 anos de casa. Tô bem incomodada porque na minha última viagem fiquei mais de 6h num aeroporto e ninguém me ofereceu lounge nem reacomodação. Espero solução à altura do meu tier.",
    "Pacote família p/ Disney em outubro, 5 pessoas (eu, esposa, 3 crianças de 5, 8 e 14 anos). Queria hotel da Disney mesmo. Quanto fica? Saída de BH.",
    "Boa tarde, peço orçamento de Réveillon em Búzios, 4 noites, casal, hotel de praia 4 estrelas, com transfer. Total ideal até 8k.",
    "Oi, sou agente de uma franquia BeFly Travel em POA. Pode me ajudar com a comissão sobre o booking BF55-2026?",
    "Minha bagagem sumiu no voo BF7700 ontem. Cheguei em Recife e a mala não veio. Já fui no balcão e abri o RIR mas precisava de ajuda pra rastrear.",
    "Tem promoção pra Europa pra setembro? Queria conhecer Itália + Grécia. 2 adultos. Flexível em datas, max ~25k.",
    "Estou tentando emitir uma nota fiscal do meu pacote pra Maceió mas o sistema dá erro. Localizador BF44ZZ1. Empresa: Tech Ltda CNPJ 12.345.678/0001-99.",
    "Olá. Sou cliente da Belvitur Corporate. Posso usar meus pontos pra pagar parte de uma viagem de lazer?",
    "URGENTE: passageiro nosso (CEO) está retido em Lisboa, voo de retorno cancelado por greve. Precisamos de remarcação imediata para BR-GRU hoje. Custo não é problema. Booking BF11X44.",
    "Olá! Queria fazer uma viagem solo pra Chile pra esquiar em julho, primeira vez fora do Brasil. Tô meio perdido, vocês ajudam com seguro, hospedagem, transfer? Budget ~12k.",
    "Vocês têm pacote feito pra advogados (curso de pós em Boston, agosto)? Preciso de hospedagem perto de Harvard.",
    "Reclamação: o atendimento de vocês no WhatsApp é PÉSSIMO. Mandei mensagem 4 vezes ontem e ninguém respondeu. Cliente Gold desde 2018.",
    "Cliente da agência Vai Voando aqui, preciso de uma cotação para 30 colaboradores irem pra uma convenção em Foz em novembro. Inclui transfer, hotel 4 estrelas, e jantar de gala. Posso mandar a planilha?",
    "Oi, comprei seguro viagem pra Europa e estou doente em Roma. Como aciono o atendimento médico?",
    "Quero alterar a refeição especial do meu voo pra vegana. BF9988, embarque dia 03/08.",
    "Posso parcelar minha viagem em 12x sem juros se eu fechar hoje?",
    "Tô vendo no site valores diferentes pra mesmo voo dependendo do horário. Tem alguma forma de garantir o melhor preço?",
    "Bom dia, sou produtora de evento corporativo. Preciso de tarifa especial pra grupo de 20 jornalistas indo cobrir Olimpíadas LA 2028.",
    "Minha esposa precisa de cadeira de rodas no aeroporto. Como solicitamos? Voo BF4499 GRU→FOR, próxima sexta.",
    "Cancelaram nosso voo de volta de Maceió. Estamos com 2 crianças pequenas e mais R$ 0 no cartão. O que vocês fazem?",
    "Promo de Black Friday pra Disney funciona pra viagem em 2027 ou só esse ano?",
    "Pré aprovado um pacote pra Maldivas, 7 noites, all inclusive, lua de mel. Casal 30s, saindo SP. Limite 60k total. Datas: out/nov 2026.",
    "Mudei de empresa, agora sou da Acme. Como atualizo o contrato corporativo BeFly Conecta no meu CPF?",
    "Vocês ainda mantêm parceria com a Smiles? Quero usar pontos pra Madrid.",
    "Sou da imprensa, gostaria de uma entrevista com o CEO sobre os planos da BeFly após a aquisição da Queensberry.",
    "Voo BF2200 atrasou 4 horas ontem (GRU→REC), perdi conexão pra Fernando de Noronha. Companhia paga reacomodação?",
    "Quero comprar miles pra completar resgate. Como faço?",
    "Bom dia! Sou da agência Instaviagem, parceira de vocês. Cliente meu pediu Punta del Este Carnaval, 4 noites, 2 adultos. Faz um orçamento por favor?",
    "Reclamação séria: o hotel que vocês reservaram pra mim em Gramado estava em obras, não dormi a noite toda. Quero compensação.",
    "Vocês têm seguro viagem que cobre esportes radicais? Vou pra NZ fazer bungee jump.",
    "Oi! Quero programa pra solteiros em julho, algum destino bom pra conhecer gente nova. 28 anos, profissional. Budget ~10k.",
    "Quem é o gerente de conta da Acme Corp? Preciso falar com ele urgente sobre os SLAs do contrato.",
    "Tem mais detalhes do pacote 'Caminhos além do imaginável' de vocês? Vi no Instagram.",
    "Tô em Tóquio, perdi o passaporte. O seguro de vocês ajuda?",
    "Quero migrar minha conta de Silver pra Gold, quantos voos faltam?",
    "Pacote pra esquiar nos Andes Argentinos, fim de agosto, 2 adultos + 1 criança 10 anos. Saída de Floripa preferencialmente.",
    "BeFly Conecta funciona com integração SAP Concur? Pergunto pra trazer pra nossa companhia.",
    "Voo BF5500 hoje cedo: o piloto fez pouso de emergência em Brasília. Estamos sentados há 3h no aeroporto sem informação. Por favor avisem nossas famílias e nos digam o que fazer.",
    "Quero comprar pacote Cancun all inclusive saindo de POA, sou Diamond. Que tarifa eu tenho disponível?",
    "Aniversário de 40 anos da minha mãe, surpresa, em Buenos Aires. 2 noites, 4 adultos. Hotel central, jantar de gala. Budget total 18k.",
    "Tem voucher de R$ 500 que vocês me deram em jul/2025 que ainda não usei. Validade era 12 meses, expira semana que vem. Posso usar pra qualquer destino?",
    "Posso usar pontos da Gol pra pagar pacote BeFly?",
]

CHANNELS = ["whatsapp", "email", "telefone", "chat_site", "instagram_dm", "presencial"]
CHANNEL_WEIGHTS = [40, 25, 15, 12, 5, 3]
SOURCES = ["BeFly", "BeFly Travel", "BeFly Conecta", "Flytour", "Belvitur", "Vai Voando", "Instaviagem", "Queensberry"]
SOURCE_WEIGHTS = [30, 20, 15, 10, 10, 8, 5, 2]

rows = []
for i in range(1, 1501):
    msg = random.choice(TICKETS)
    if random.random() < 0.4:
        msg = msg + " " + random.choice([
            "Aguardo retorno, obrigado!",
            "Por favor responder no whatsapp 11 9XXXX-XXXX.",
            "Estou muito chateado, espero solução.",
            "Cliente desde 2019, espero atendimento à altura.",
            "Já mandei essa mensagem 2 vezes, ninguém respondeu.",
        ])
    ts = datetime(2026, 1, 1) + timedelta(minutes=random.randint(0, 170 * 24 * 60))
    rows.append((
        i,
        ts.isoformat(timespec="seconds"),
        random.choices(SOURCES, weights=SOURCE_WEIGHTS)[0],
        random.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0],
        random.randint(1, 500),  # customer_id (faz join com silver_customers)
        msg,
    ))

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticket_id", "received_at", "marca", "canal", "customer_id", "mensagem"])
    w.writerows(rows)

print(f"Generated {len(rows)} tickets → {OUT}")
