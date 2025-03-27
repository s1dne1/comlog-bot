const venom = require('venom-bot');
const express = require('express');
const app = express();

app.use(express.json());

let clientGlobal = null;

// 🔁 Cria a sessão do WhatsApp com configurações visuais
venom
  .create({
    session: 'bot-whatsapp',
    multidevice: true,
    headless: false, // <-- MUITO IMPORTANTE: mostra o navegador
    useChrome: true,
    disableWelcome: true,
    puppeteerOptions: {
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    },
    // Se necessário, adicione:
    // executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe'
  })
  .then((client) => {
    clientGlobal = client;
    start(client);
  })
  .catch((erro) => {
    console.error('❌ Erro ao iniciar o bot:', erro);
  });

// 🤖 Função principal do bot
function start(client) {
  console.log('🤖 Bot conectado com sucesso!');
  const numeroPermitido = '5515997836336@c.us'; // seu número de teste

  // Escuta mensagens recebidas no WhatsApp
  client.onMessage(async (message) => {
    if (message.from !== numeroPermitido) return;

    const texto = message.body.toLowerCase();
    console.log(`📩 Mensagem recebida de ${message.from}: ${texto}`);

    if (texto.includes('agendamento')) {
      await client.sendText(message.from, '📦 Seu agendamento está em análise. Aguarde confirmação.');
    } else if (texto.includes('pesagem')) {
      await client.sendText(message.from, '⚖️ A pesagem ocorre no Galpão 3, após o portão principal.');
    } else if (texto.includes('tempo')) {
      await client.sendText(message.from, '🕒 O tempo médio de espera hoje é de 45 minutos.');
    } else if (['oi', 'olá', 'bom dia', 'boa tarde', 'boa noite'].includes(texto)) {
      await client.sendText(message.from, '👋 Olá! Como posso te ajudar?');
    } else {
      await client.sendText(message.from, '🤖 Não entendi sua mensagem. Tente algo como "agendamento", "pesagem" ou "tempo".');
    }
  });
}

// 📤 Rota para envio de mensagem via API
app.post('/enviar', async (req, res) => {
  const { numero, mensagem } = req.body;
  console.log('📨 Requisição recebida via API:', numero, mensagem);

  if (!clientGlobal) {
    return res.status(500).json({ status: 'Bot não conectado' });
  }

  try {
    const id = numero.includes('@') ? numero : `${numero}@c.us`;
    await clientGlobal.sendText(id, mensagem);
    return res.status(200).json({ status: 'Mensagem enviada com sucesso' });
  } catch (err) {
    console.error('❌ Erro ao enviar via API:', err);
    return res.status(500).json({ status: 'Erro ao enviar', erro: err.message });
  }
});

// 🚀 Inicia o servidor da API na porta 3000
app.listen(3000, () => {
  console.log('🚀 API do bot rodando em http://localhost:3000/enviar');
});
