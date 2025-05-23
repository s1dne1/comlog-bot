// Importa os módulos necessários:
// - venom-bot: para criar e gerenciar o bot do WhatsApp.
// - express: para criar a API HTTP que possibilita a interação externa com o bot.
// - axios: para fazer requisições HTTP para APIs internas.
const venom = require('venom-bot');
const express = require('express');
const axios = require('axios');

// Cria uma instância do Express e configura para tratar JSON nas requisições.
const app = express();
app.use(express.json());

// Variáveis globais para o cliente do WhatsApp e para armazenar o contexto da conversa de cada usuário.
let clientGlobal = null;
const contextoUsuario = new Map(); // Armazena o contexto da conversa por número.
const ultimaMensagemUsuario = new Map(); // Armazena a última mensagem enviada para cada número.
const inscricaoPendente = new Map(); // Armazena agendamento que o usuário acabou de consultar

// Localização da portaria 
const PORTARIA = { lat: -23.9865964, lng: -48.9161002};
//const PORTARIA = { lat: -23.532673599176753, lng: -47.49531101866294};


const RAIO_PERMITIDO_KM = 1.0;

function calcularDistancia(lat1, lon1, lat2, lon2) {
  const R = 6371; // km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}



// 🔁 Cria a sessão do WhatsApp com as configurações desejadas.
venom
  .create({
    session: './sessions/bot-whatsapp', // Caminho onde a sessão será salva.
    multidevice: true, // Permite a conexão em múltiplos dispositivos.
    headless: false, // Abre o navegador visivelmente para depuração.
    useChrome: true, // Usa o Google Chrome para a sessão.
    disableWelcome: true, // Desativa a mensagem de boas-vindas padrão do venom.
    puppeteerOptions: {
      args: ['--no-sandbox', '--disable-setuid-sandbox'] // Configurações adicionais para o Puppeteer.
    }
  })
  .then((client) => {
    // Se a sessão for criada com sucesso, armazena o cliente e inicia a função principal.
    clientGlobal = client;
    start(client);
  })
  .catch((erro) => {
    // Em caso de erro ao iniciar a sessão, exibe o erro no console.
    console.error('❌ Erro ao iniciar o bot:', erro);
  });

// 🤖 Função principal que inicia o bot e configura o listener para as mensagens recebidas.
function start(client) {
  console.log('🤖 Bot conectado com sucesso!');

// 📝 Mensagens customizáveis
const MENSAGENS = {
  menu_inicial: "menu_principal",
  saudacoes: ["oi", "olá", "menu", "início"],
  erro_opcao: "❗ Opção inválida. Tente novamente.",
  msg_agendamento: "🆔 Informe o número do agendamento:",
  msg_atendimento: "📞 Um atendente entrará em contato com você em breve.",
  erro_padrao: "🤖 Não entendi. Digite \"menu\" para ver as opções.",
  erro_numero_invalido: "❗ Envie um número válido.",
  msg_avisar_chegada:"🆔 Informe o número do agendamento:"
};




  // Configura o listener para eventos de mensagem.
  client.onMessage(async (message) => {
    const numero = message.from;
    const texto = message.body.trim().toLowerCase();
    const contexto = contextoUsuario.get(numero);
    

    console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD001');
  

  
    console.log(`[${new Date().toLocaleTimeString()}] 📩 ${numero}: ${texto}`);
  

  
    // RESET universal
    if (["reset", "reiniciar", "voltar", "menu"].includes(texto)) {
      contextoUsuario.delete(numero);
      const menu = await axios.get('http://127.0.0.1:8001/api/menu-texto/', {
        params: { id_menu: MENSAGENS.menu_inicial }
      });
      contextoUsuario.set(numero, `menu:${MENSAGENS.menu_inicial}`);
      await client.sendText(numero, menu.data.texto);
      await axios.post('http://127.0.0.1:8001/api/historico/', {
        numero,
        mensagem_recebida: texto,
        mensagem_enviada: menu.data.texto
      });
      return;
      

    }

    //Trecho para recurso de avisar que motorista chegou na planta.


    
    if (contexto === 'acao:avisar_chegada') {
      console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD002');
      const agendamentoId = texto.match(/\d+/)?.[0];
      contextoUsuario.delete(numero);
    
      try {
        const resp = await axios.get(`http://127.0.0.1:8001/api/resposta-agendamento/${agendamentoId}`);
        const textoResposta = resp.data.resposta;
        const linhaStatus = textoResposta.split('\n').find(l => l.includes("Status"));
        console.log("[DEBUG] Linha do status:", linhaStatus);
    
        if (!linhaStatus || !linhaStatus.includes("AGENDADO")) {
          await client.sendText(numero, `⚠️ O status atual é *${linhaStatus}*. Só é possível avisar que chegou se estiver como *Agendado*.`);
          await registrarHistorico(numero, texto, `Status inválido para chegada: ${linhaStatus}`);
          contextoUsuario.delete(numero);
          return;
        } else{
          contextoUsuario.set(numero, "aguardando_localizacao_avisar_chegada");
          inscricaoPendente.set(numero, agendamentoId);
          await client.sendText(numero, "📍 Por favor, envie sua localização para confirmar que você chegou à planta.");
          await registrarHistorico(numero, texto, "Solicitação de localização enviada.");
          return; // para teste 02 - colocado por mim para tentar tirar erro de duas msgs...
        }
      } catch (err) {
        await client.sendText(numero, '❌ Não foi possível consultar o agendamento. Verifique o número e tente novamente.');
        console.error("Erro na consulta de agendamento:", err.message);
        return;
      }
    }
    
    if (contexto === 'aguardando_localizacao_avisar_chegada' && message.type === 'location') {
      console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD003');
      const lat = message.lat;
      const lng = message.lng;
      const agendamentoId = inscricaoPendente.get(numero);
    
      // Limpa o contexto para não repetir
      contextoUsuario.delete(numero);
      inscricaoPendente.delete(numero);
    
      // Valida se está próximo da portaria
      const distancia = calcularDistancia(lat, lng, PORTARIA.lat, PORTARIA.lng);
      console.log(`[DEBUG] Distância do ponto: ${distancia.toFixed(3)} km`);
    
      if (distancia > RAIO_PERMITIDO_KM) {
        const msgErro = "🚫 Você está muito longe da portaria. Envie a localização novamente ao chegar no local correto.";
        await client.sendText(numero, msgErro);
        await registrarHistorico(numero, 'LOCALIZAÇÃO FORA', msgErro);
        return;
      }
    
      // ✅ Agora sim, dentro do raio → registra a chegada
      try {
        const resp = await axios.post('http://127.0.0.1:8001/api/confirmar-chegada/', {
          numero: numero,
          latitude: lat,
          longitude: lng,
          ordem_carregamento: agendamentoId
        });

      
    
        await client.sendText(numero, resp.data.status || "✅ Chegada registrada com sucesso.");
        await registrarHistorico(numero, 'LOCALIZAÇÃO', resp.data.status);
      } catch (err) {
        await client.sendText(numero, "❌ Erro ao registrar sua chegada. Tente novamente.");
        await registrarHistorico(numero, 'LOCALIZAÇÃO', 'Erro');
        console.error("Erro ao confirmar chegada:", err.message);
      }
    
      return;
    }
    


    if (contexto === 'acao:resposta_automatica') {
      console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD004');
      contextoUsuario.delete(numero);
      const respAuto = await axios.get('http://127.0.0.1:8001/api/resposta/', {
        params: { q: texto }
      });
    
      const resposta = respAuto.data.resposta || '🤖 Nenhuma resposta configurada.';
      await client.sendText(numero, resposta);
      await registrarHistorico(numero, texto, resposta);
      return;
    }
    
    


    // Fluxo de agendamento (prioridade antes de menus)
    if (contexto === 'acao:agendamento') {
      console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD005');
      contextoUsuario.delete(numero);
      const id = texto.match(/\d+/)?.[0];
      if (!id) {
        await client.sendText(numero, MENSAGENS.erro_numero_invalido);
        await registrarHistorico(numero, texto, MENSAGENS.erro_numero_invalido);
        return;
      }
    
      const resposta = await axios.get(`http://127.0.0.1:8001/api/resposta-agendamento/${id}`);
      const msg = resposta.data.resposta + '\n\n🔔 Deseja receber atualizações sobre esse processo? (sim/não)';
    
      await client.sendText(numero, msg);
      await registrarHistorico(numero, texto, msg);
    
      inscricaoPendente.set(numero, id);
      contextoUsuario.set(numero, 'espera_confirmacao_notificacao');
      return;
    }

    if (contexto === 'espera_confirmacao_notificacao') {
      console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD006');
      const agendamentoId = inscricaoPendente.get(numero);
      inscricaoPendente.delete(numero);
    
      if (["sim", "quero", "sim, quero"].includes(texto)) {
        
        // Inscrição realizada
        await axios.post('http://127.0.0.1:8001/api/inscrever-notificacao/', {
          numero,
          agendamento_id: agendamentoId
        });
        const confirmacao = "✅ Ok! Você será avisado sempre que o status do agendamento mudar.";
        await client.sendText(numero, confirmacao);
        await registrarHistorico(numero, texto, confirmacao);
        
      } else {
        // Inscrição cancelada
        const cancelado = "👍 Sem problemas! Você pode consultar manualmente quando quiser.";
        await client.sendText(numero, cancelado);
        await registrarHistorico(numero, texto, cancelado);
      }
     


    
      return;
    }
    
  
    // Navegação entre menus dinâmicos
    if (contexto && contexto.startsWith('menu:')) {
      console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD007');
      const menu_atual = contexto.split(':')[1];
      try {
        const resp = await axios.get('http://127.0.0.1:8001/api/menu/', {
          params: {
            id_menu: menu_atual,
            opcao: texto
          }
        });
  
        const proximo = resp.data.proximo;
  
        if (proximo.startsWith('acao:')) {
          const acao = proximo.split(':')[1];

         
            if (acao === 'avisar_chegada') {
              contextoUsuario.set(numero, 'acao:avisar_chegada');
              await client.sendText(numero, MENSAGENS.msg_avisar_chegada);
              await registrarHistorico(numero, texto, MENSAGENS.msg_avisar_chegada);
              return;
            }
          


  
          if (acao === 'chamada_api_agendamento') {
            console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD008');
            contextoUsuario.set(numero, 'acao:agendamento');
            
            await client.sendText(numero, MENSAGENS.msg_agendamento);
            await axios.post('http://127.0.0.1:8001/api/historico/', {
              numero,
              mensagem_recebida: texto,
              mensagem_enviada: MENSAGENS.msg_agendamento
            });
            return;
          }






          if (acao === 'resposta_automatica') {
            console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD009');
            // Usa o próprio texto (ex: "2") como chave
            try {
              const resposta = await axios.get('http://127.0.0.1:8001/api/resposta/', {
                params: { q: texto }
              });
          
              await client.sendText(numero, resposta.data.resposta || '🤖 Nenhuma resposta configurada.');
              await registrarHistorico(numero, texto, resposta.data.resposta);
            } catch (err) {
              await client.sendText(numero, '❌ Erro ao buscar resposta automática.');
              console.error('Erro na resposta_automatica:', err.message);
            }
          
            return;
          }

          
  
          if (acao === 'atendimento') {
            console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD010');
            contextoUsuario.delete(numero);
            await client.sendText(numero, MENSAGENS.msg_atendimento);
            await axios.post('http://127.0.0.1:8001/api/historico/', {
              numero,
              mensagem_recebida: texto,
              mensagem_enviada: MENSAGENS.msg_atendimento
            });
            return;
          }
        } else {
          console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD011');
          const proxMenu = await axios.get('http://127.0.0.1:8001/api/menu-texto/', {
            params: { id_menu: proximo }
          });
          contextoUsuario.set(numero, `menu:${proximo}`);
          await client.sendText(numero, proxMenu.data.texto);
          await axios.post('http://127.0.0.1:8001/api/historico/', {
            numero,
            mensagem_recebida: texto,
            mensagem_enviada: proxMenu.data.texto
          });
          return;
        }
      } catch (e) {
        console.error('Erro ao navegar no menu:', e.message);
        await client.sendText(numero, MENSAGENS.erro_opcao);
        await axios.post('http://127.0.0.1:8001/api/historico/', {
          numero,
          mensagem_recebida: texto,
          mensagem_enviada: MENSAGENS.erro_opcao
        });
        return;
      }
    }

        // Consulta resposta automática no backend (com regra)
        try {
          console.log(`[DEBUG] Contexto atual de ${numero}:`, contexto,texto,'COD012');
          const respAuto = await axios.get('http://127.0.0.1:8001/api/resposta/', {
            params: { q: texto }
          });
      
          if (respAuto.data.resposta) {
            await client.sendText(numero, respAuto.data.resposta);
            await axios.post('http://127.0.0.1:8001/api/historico/', {
              numero,
              mensagem_recebida: texto,
              mensagem_enviada: respAuto.data.resposta
            });
            contextoUsuario.set(numero, respAuto.data.contexto); // Add por mim... teste contexto nas msg automatica
            return;
            
          }
        } catch (err) {
          console.error('Erro ao consultar resposta automática:', err.message);
        }
  
    // Fallback final — sugere o menu ao usuário
    
    const textosaudacao = ["oi", "ola", "olá", "bom dia", "boa noite", "boa tarde"];
    const horaAtual = new Date().getHours();
    
    let saudacao = "";
    if (horaAtual < 12) {
      saudacao = "🌞 Bom dia!";
    } else if (horaAtual < 18) {
      saudacao = "🌤️ Boa tarde!";
    } else {
      saudacao = "🌙 Boa noite!";
    }
    
    let mensagemResposta = '🤖 Não entendi sua mensagem. Deseja ver o menu? Digite *menu*.';
    
    if (textosaudacao.includes(texto)) {
      mensagemResposta = `${saudacao} Para iniciar Digite *menu* para ver as opções.`;
    }
    
    await client.sendText(numero, mensagemResposta);
    
    await axios.post('http://127.0.0.1:8001/api/historico/', {
      numero,
      mensagem_recebida: texto,
      mensagem_enviada: mensagemResposta
    });
    

  });
  
}

// 🧾 Função para registrar o histórico de mensagens enviadas e recebidas.
// Essa função envia os dados para uma API interna que registra o histórico.
async function registrarHistorico(numero, recebida, enviada) {
  try {
    await axios.post('http://127.0.0.1:8001/api/historico/', {
      numero: numero,
      mensagem_recebida: recebida,
      mensagem_enviada: enviada
    });
  } catch (err) {
    console.error('Erro ao salvar histórico:', err.message);
  }
}

// 📤 Endpoint da API para envio de mensagens externamente.
// Permite que outras aplicações enviem mensagens via WhatsApp utilizando o bot.
app.post('/enviar', async (req, res) => {
  const { numero, mensagem } = req.body; // Extrai o número e a mensagem do corpo da requisição.
  console.log('📨 API recebeu:', numero, mensagem);

  // Verifica se o bot está conectado.
  if (!clientGlobal) {
    return res.status(500).json({ status: 'Bot não conectado' });
  }

  try {
    // Formata o número para o padrão esperado pelo WhatsApp.
    const id = numero.includes('@') ? numero : `${numero}@c.us`;
    // Envia a mensagem para o número especificado.
    await clientGlobal.sendText(id, mensagem);
    return res.status(200).json({ status: 'Mensagem enviada com sucesso' });
  } catch (err) {
    console.error('❌ Erro ao enviar via API:', err);
    return res.status(500).json({ status: 'Erro ao enviar', erro: err.message });
  }
});

// 🚀 Inicia o servidor Express na porta 3000.
app.listen(3000, () => {
  console.log('🚀 API do bot rodando em http://127.0.0.1:3000/enviar');
});
