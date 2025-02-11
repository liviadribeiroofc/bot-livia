import asyncio
import logging
import json
import requests
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Configurações
API_TOKEN = '8181161126:AAFn5WTIbaPmgk3O5iKXoiNZOpoZGow-9dA'
MERCADO_PAGO_ACCESS_TOKEN = '4541980271030306'
GRUPO_PRIVADO_BASE_LINK = 'https://t.me/+Eu8z8aoY_fE1ZTU5'

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

dp.include_router(router)

# Mensagem de saudação
SAUDACAO = """
💦 Mundo da Lívia 🔥
👄 Olá bebê! Bem vindo(a), ao meu grupo exclusivo!
Aqui nós vamos nos ver bastante, eu quero deixar você surtando com as minhas mídias

💍 O pagamento é vitalício, você vai pagar uma única vez e vai me ter para sempre.
Eu quero que a gente se divirta muuuuito juntos. Eu tenho MUITA coisa pra te mostrar, e quero te mostrar tuuuudinho bebê

🔥 Chega perder tempo! EU QUERO VOCÊ. Vem pra mim, é só o fazer um PIX baratinho e eu vou ser sua pra sempre 🤤
"""

def gerar_pagamento_pix(valor: float):
    url = "https://api.mercadopago.com/v1/payments"
    headers = {
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "transaction_amount": valor,
        "description": "Acesso ao grupo exclusivo",
        "payment_method_id": "pix",
        "payer": {"email": "comprador@email.com"}
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@router.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Pagamento vitalício", callback_data="vitalicio"))
    
    await message.reply(SAUDACAO, reply_markup=keyboard)

@router.callback_query_handler(lambda c: c.data == 'vitalicio')
async def process_payment(callback_query: types.CallbackQuery):
    valor = 19.99
    pagamento = gerar_pagamento_pix(valor)
    qr_code = pagamento.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code")
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Verificar pagamento", callback_data="verificar"))
    keyboard.add(InlineKeyboardButton("Voltar ↩️", callback_data="voltar"))
    
    if qr_code:
        mensagem = f"Escaneie o QR Code PIX abaixo:\n{qr_code}"
        await bot.send_message(callback_query.from_user.id, mensagem, reply_markup=keyboard)
    else:
        await bot.send_message(callback_query.from_user.id, "Erro ao gerar pagamento. Tente novamente mais tarde.")

@router.callback_query_handler(lambda c: c.data == 'verificar')
async def verificar_pagamento(callback_query: types.CallbackQuery):
    url = f"https://api.mercadopago.com/v1/payments/search?sort=date_created&criteria=desc"
    headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers).json()
    
    for pagamento in response.get("results", []):
        if pagamento.get("status") == "approved":
            await bot.send_message(callback_query.from_user.id, f"Pagamento confirmado! Acesse o grupo: {GRUPO_PRIVADO_BASE_LINK}")
            return
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Verificar pagamento", callback_data="verificar"))
    await bot.send_message(callback_query.from_user.id, "Pagamento não efetuado. Tente novamente.", reply_markup=keyboard)

@router.callback_query_handler(lambda c: c.data == 'voltar')
async def voltar(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Pagamento vitalício", callback_data="vitalicio"))
    
    await bot.send_message(callback_query.from_user.id, "Escolha novamente o tipo de pagamento:", reply_markup=keyboard)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
