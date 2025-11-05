#!/usr/bin/env python3
"""
AccessibilityAgent
Agente de IA para Avaliação de Acessibilidade Web
Alinhado com WCAG 2.2 e ABNT NBR 17225:2025
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import re
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime
import colorsys

class NivelConformidade(Enum):
    """Níveis de conformidade WCAG 2.2"""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class SeveridadeProblema(Enum):
    """Severidade dos problemas encontrados"""
    CRITICO = "Crítico"
    GRAVE = "Grave"
    MODERADO = "Moderado"
    LEVE = "Leve"


@dataclass
class ProblemaAcessibilidade:
    """Representa um problema de acessibilidade encontrado"""
    criterio: str
    descricao: str
    severidade: SeveridadeProblema
    nivel_wcag: NivelConformidade
    elemento: str
    linha: Optional[int] = None
    sugestao: str = ""
    referencia_wcag: str = ""
    referencia_abnt: str = ""
    codigo_exemplo: str = ""


@dataclass
class RelatorioAcessibilidade:
    """Relatório completo de acessibilidade"""
    url: str
    data_avaliacao: str
    pontuacao_geral: float
    total_problemas: int
    problemas_por_severidade: Dict[str, int]
    problemas: List[ProblemaAcessibilidade]
    recomendacoes_priorizadas: List[str]
    conformidade_wcag: Dict[str, bool]
    conformidade_abnt: Dict[str, bool]


class AgenteAcessibilidade:
    """
    Agente de IA para avaliação de acessibilidade web
    Implementa heurísticas baseadas em WCAG 2.2 e ABNT NBR 17225:2025
    """
    
    def __init__(self):
        self.problemas: List[ProblemaAcessibilidade] = []
        self.soup: Optional[BeautifulSoup] = None
        self.url: str = ""
        
        # Mapeamento de critérios WCAG 2.2 para ABNT NBR 17225:2025
        self.mapeamento_normas = {
            "1.1.1": "ABNT 5.1 - Alternativas em texto",
            "1.3.1": "ABNT 5.3 - Estrutura semântica",
            "1.4.3": "ABNT 5.4.3 - Contraste mínimo",
            "2.1.1": "ABNT 6.1 - Navegação por teclado",
            "2.4.1": "ABNT 6.4.1 - Bypass de blocos",
            "2.4.2": "ABNT 6.4.2 - Títulos de página",
            "3.1.1": "ABNT 7.1 - Idioma da página",
            "4.1.1": "ABNT 8.1 - Parsing HTML",
            "4.1.2": "ABNT 8.2 - Nome, função e valor",
        }
    
    def avaliar_website(self, url: str) -> RelatorioAcessibilidade:
        """
        Avalia a acessibilidade de um website
        
        Args:
            url: URL do website a ser avaliado
            
        Returns:
            RelatorioAcessibilidade com resultados da análise
        """
        self.url = url
        self.problemas = []
        
        try:
            # Buscar conteúdo da página
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
            
            # Executar todas as verificações
            self._verificar_alternativas_texto()
            self._verificar_estrutura_semantica()
            self._verificar_contraste_cores()
            self._verificar_navegacao_teclado()
            self._verificar_formularios()
            self._verificar_multimedia()
            self._verificar_titulos_pagina()
            self._verificar_idioma()
            self._verificar_links()
            self._verificar_tabelas()
            self._verificar_aria()
            self._verificar_responsividade()
            
            # Gerar relatório
            return self._gerar_relatorio()
            
        except Exception as e:
            print(f"Erro ao avaliar website: {str(e)}")
            return self._gerar_relatorio_erro(str(e))
    
    def _verificar_alternativas_texto(self):
        """
        WCAG 2.2 - 1.1.1 Conteúdo Não Textual (Nível A)
        ABNT NBR 17225:2025 - 5.1 Alternativas em texto
        """
        # Verificar imagens sem alt
        imagens = self.soup.find_all('img')
        for img in imagens:
            alt = img.get('alt')
            src = img.get('src', 'src_desconhecido')
            
            if alt is None:
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="1.1.1 - Alternativas em Texto",
                    descricao=f"Imagem sem atributo alt: {src}",
                    severidade=SeveridadeProblema.CRITICO,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(img)[:100],
                    sugestao="Adicione um atributo alt descritivo para a imagem",
                    referencia_wcag="WCAG 2.2 - 1.1.1",
                    referencia_abnt=self.mapeamento_normas["1.1.1"],
                    codigo_exemplo=f'<img src="{src}" alt="Descrição clara da imagem">'
                ))
            elif alt.strip() == "" and not self._is_decorative(img):
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="1.1.1 - Alternativas em Texto",
                    descricao=f"Imagem com alt vazio (não decorativa): {src}",
                    severidade=SeveridadeProblema.GRAVE,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(img)[:100],
                    sugestao="Forneça uma descrição textual significativa",
                    referencia_wcag="WCAG 2.2 - 1.1.1",
                    referencia_abnt=self.mapeamento_normas["1.1.1"],
                    codigo_exemplo=f'<img src="{src}" alt="Descrição do conteúdo da imagem">'
                ))
        
        # Verificar inputs de imagem
        inputs_img = self.soup.find_all('input', {'type': 'image'})
        for inp in inputs_img:
            if not inp.get('alt'):
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="1.1.1 - Alternativas em Texto",
                    descricao="Input tipo imagem sem atributo alt",
                    severidade=SeveridadeProblema.CRITICO,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(inp)[:100],
                    sugestao="Adicione alt descrevendo a ação do botão",
                    referencia_wcag="WCAG 2.2 - 1.1.1",
                    referencia_abnt=self.mapeamento_normas["1.1.1"],
                    codigo_exemplo='<input type="image" alt="Enviar formulário">'
                ))
    
    def _verificar_estrutura_semantica(self):
        """
        WCAG 2.2 - 1.3.1 Informações e Relações (Nível A)
        ABNT NBR 17225:2025 - 5.3 Estrutura semântica
        """
        # Verificar hierarquia de cabeçalhos
        headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            self.problemas.append(ProblemaAcessibilidade(
                criterio="1.3.1 - Estrutura Semântica",
                descricao="Página sem cabeçalhos (h1-h6)",
                severidade=SeveridadeProblema.GRAVE,
                nivel_wcag=NivelConformidade.A,
                elemento="<body>",
                sugestao="Use cabeçalhos para estruturar o conteúdo",
                referencia_wcag="WCAG 2.2 - 1.3.1",
                referencia_abnt=self.mapeamento_normas["1.3.1"],
                codigo_exemplo="<h1>Título Principal</h1>\n<h2>Seção</h2>"
            ))
        
        # Verificar múltiplos H1
        h1_count = len(self.soup.find_all('h1'))
        if h1_count > 1:
            self.problemas.append(ProblemaAcessibilidade(
                criterio="1.3.1 - Estrutura Semântica",
                descricao=f"Múltiplos elementos H1 encontrados ({h1_count})",
                severidade=SeveridadeProblema.MODERADO,
                nivel_wcag=NivelConformidade.A,
                elemento="<h1>",
                sugestao="Use apenas um H1 por página como título principal",
                referencia_wcag="WCAG 2.2 - 1.3.1",
                referencia_abnt=self.mapeamento_normas["1.3.1"],
                codigo_exemplo="<h1>Título único da página</h1>"
            ))
        
        # Verificar uso de landmarks HTML5
        landmarks = ['header', 'nav', 'main', 'footer', 'aside', 'section']
        found_landmarks = [tag for tag in landmarks if self.soup.find(tag)]
        
        if len(found_landmarks) < 3:
            self.problemas.append(ProblemaAcessibilidade(
                criterio="1.3.1 - Estrutura Semântica",
                descricao="Uso limitado de elementos HTML5 semânticos",
                severidade=SeveridadeProblema.MODERADO,
                nivel_wcag=NivelConformidade.A,
                elemento="<body>",
                sugestao="Use <header>, <nav>, <main>, <footer> para estruturar",
                referencia_wcag="WCAG 2.2 - 1.3.1",
                referencia_abnt=self.mapeamento_normas["1.3.1"],
                codigo_exemplo="<header>...</header>\n<nav>...</nav>\n<main>...</main>"
            ))
        
        # Verificar listas apropriadas
        divs_como_listas = self.soup.find_all('div', class_=re.compile(r'list|item', re.I))
        if len(divs_como_listas) > 3:
            self.problemas.append(ProblemaAcessibilidade(
                criterio="1.3.1 - Estrutura Semântica",
                descricao="Possível uso de divs em vez de listas semânticas",
                severidade=SeveridadeProblema.LEVE,
                nivel_wcag=NivelConformidade.A,
                elemento="<div class='list/item'>",
                sugestao="Use <ul>, <ol> e <li> para listas",
                referencia_wcag="WCAG 2.2 - 1.3.1",
                referencia_abnt=self.mapeamento_normas["1.3.1"],
                codigo_exemplo="<ul>\n  <li>Item 1</li>\n  <li>Item 2</li>\n</ul>"
            ))
    
    def _verificar_contraste_cores(self):
        """
        WCAG 2.2 - 1.4.3 Contraste Mínimo (Nível AA)
        ABNT NBR 17225:2025 - 5.4.3 Contraste de cores
        """
        # Verificar estilos inline e CSS
        elementos_com_estilo = self.soup.find_all(style=True)
        
        for elem in elementos_com_estilo:
            style = elem.get('style', '')
            # Extrair cores do estilo
            cores = re.findall(r'color:\s*([^;]+)', style)
            bg_cores = re.findall(r'background(?:-color)?:\s*([^;]+)', style)
            
            if cores and bg_cores:
                # Aviso genérico sobre verificação de contraste
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="1.4.3 - Contraste de Cores",
                    descricao="Verifique contraste entre texto e fundo",
                    severidade=SeveridadeProblema.MODERADO,
                    nivel_wcag=NivelConformidade.AA,
                    elemento=str(elem)[:100],
                    sugestao="Razão de contraste mínima: 4.5:1 para texto normal, 3:1 para texto grande",
                    referencia_wcag="WCAG 2.2 - 1.4.3",
                    referencia_abnt=self.mapeamento_normas["1.4.3"],
                    codigo_exemplo="Use ferramentas como WebAIM Contrast Checker"
                ))
    
    def _verificar_navegacao_teclado(self):
        """
        WCAG 2.2 - 2.1.1 Teclado (Nível A)
        ABNT NBR 17225:2025 - 6.1 Acessibilidade por teclado
        """
        # Verificar elementos interativos sem tabindex adequado
        elementos_interativos = self.soup.find_all(['div', 'span'], 
                                                   onclick=True)
        
        for elem in elementos_interativos:
            tabindex = elem.get('tabindex')
            role = elem.get('role')
            
            if tabindex is None and role not in ['button', 'link']:
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="2.1.1 - Navegação por Teclado",
                    descricao="Elemento interativo não acessível por teclado",
                    severidade=SeveridadeProblema.CRITICO,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(elem)[:100],
                    sugestao="Use elementos nativos (<button>, <a>) ou adicione tabindex='0' e role apropriado",
                    referencia_wcag="WCAG 2.2 - 2.1.1",
                    referencia_abnt=self.mapeamento_normas["2.1.1"],
                    codigo_exemplo='<div role="button" tabindex="0" onkeypress="...">Clique</div>'
                ))
        
        # Verificar skip links
        skip_links = self.soup.find_all('a', href=re.compile(r'^#'))
        if not skip_links:
            self.problemas.append(ProblemaAcessibilidade(
                criterio="2.4.1 - Bypass de Blocos",
                descricao="Ausência de links para pular navegação (skip links)",
                severidade=SeveridadeProblema.GRAVE,
                nivel_wcag=NivelConformidade.A,
                elemento="<body>",
                sugestao="Adicione link 'Pular para conteúdo principal' no início da página",
                referencia_wcag="WCAG 2.2 - 2.4.1",
                referencia_abnt=self.mapeamento_normas["2.4.1"],
                codigo_exemplo='<a href="#main-content" class="skip-link">Pular para conteúdo</a>'
            ))
    
    def _verificar_formularios(self):
        """
        WCAG 2.2 - 4.1.2 Nome, Função e Valor (Nível A)
        ABNT NBR 17225:2025 - 8.2 Identificação de campos
        """
        # Verificar inputs sem labels
        inputs = self.soup.find_all(['input', 'select', 'textarea'])
        
        for inp in inputs:
            input_type = inp.get('type', 'text')
            if input_type in ['hidden', 'submit', 'button', 'image']:
                continue
            
            input_id = inp.get('id')
            aria_label = inp.get('aria-label')
            aria_labelledby = inp.get('aria-labelledby')
            title = inp.get('title')
            
            # Procurar label associado
            label_encontrado = False
            if input_id:
                label = self.soup.find('label', {'for': input_id})
                if label:
                    label_encontrado = True
            
            # Verificar se está dentro de um label
            if inp.find_parent('label'):
                label_encontrado = True
            
            if not (label_encontrado or aria_label or aria_labelledby or title):
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="4.1.2 - Nome, Função e Valor",
                    descricao=f"Campo de formulário sem label: {input_type}",
                    severidade=SeveridadeProblema.CRITICO,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(inp)[:100],
                    sugestao="Associe um <label> ao campo ou use aria-label",
                    referencia_wcag="WCAG 2.2 - 4.1.2",
                    referencia_abnt=self.mapeamento_normas["4.1.2"],
                    codigo_exemplo='<label for="nome">Nome:</label>\n<input type="text" id="nome">'
                ))
        
        # Verificar campos obrigatórios
        required_inputs = self.soup.find_all(['input', 'select', 'textarea'], required=True)
        for inp in required_inputs:
            aria_required = inp.get('aria-required')
            if aria_required != 'true':
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="4.1.2 - Nome, Função e Valor",
                    descricao="Campo obrigatório sem aria-required='true'",
                    severidade=SeveridadeProblema.LEVE,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(inp)[:100],
                    sugestao="Adicione aria-required='true' para leitores de tela",
                    referencia_wcag="WCAG 2.2 - 4.1.2",
                    referencia_abnt=self.mapeamento_normas["4.1.2"],
                    codigo_exemplo='<input type="text" required aria-required="true">'
                ))
    
    def _verificar_multimedia(self):
        """
        WCAG 2.2 - 1.2 Multimídia Baseada em Tempo
        ABNT NBR 17225:2025 - 5.2 Alternativas para multimídia
        """
        # Verificar vídeos
        videos = self.soup.find_all(['video', 'iframe'])
        
        for video in videos:
            if video.name == 'video':
                # Verificar legendas/tracks
                tracks = video.find_all('track', kind='captions')
                if not tracks:
                    self.problemas.append(ProblemaAcessibilidade(
                        criterio="1.2.2 - Legendas",
                        descricao="Vídeo sem legendas/closed captions",
                        severidade=SeveridadeProblema.CRITICO,
                        nivel_wcag=NivelConformidade.A,
                        elemento=str(video)[:100],
                        sugestao="Adicione <track kind='captions'> com legendas",
                        referencia_wcag="WCAG 2.2 - 1.2.2",
                        referencia_abnt="ABNT 5.2.2 - Legendas sincronizadas",
                        codigo_exemplo='<video>\n  <track kind="captions" src="legendas.vtt" srclang="pt-BR">\n</video>'
                    ))
                
                # Verificar autoplay
                if video.get('autoplay'):
                    self.problemas.append(ProblemaAcessibilidade(
                        criterio="1.4.2 - Controle de Áudio",
                        descricao="Vídeo com autoplay pode causar distração",
                        severidade=SeveridadeProblema.GRAVE,
                        nivel_wcag=NivelConformidade.A,
                        elemento=str(video)[:100],
                        sugestao="Remova autoplay ou forneça controle de pausa",
                        referencia_wcag="WCAG 2.2 - 1.4.2",
                        referencia_abnt="ABNT 5.4.2 - Controle de reprodução",
                        codigo_exemplo='<video controls>\n  <!-- sem autoplay -->\n</video>'
                    ))
        
        # Verificar áudios
        audios = self.soup.find_all('audio')
        for audio in audios:
            if audio.get('autoplay'):
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="1.4.2 - Controle de Áudio",
                    descricao="Áudio com autoplay",
                    severidade=SeveridadeProblema.GRAVE,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(audio)[:100],
                    sugestao="Remova autoplay de elementos de áudio",
                    referencia_wcag="WCAG 2.2 - 1.4.2",
                    referencia_abnt="ABNT 5.4.2 - Controle de reprodução",
                    codigo_exemplo='<audio controls src="audio.mp3"></audio>'
                ))
    
    def _verificar_titulos_pagina(self):
        """
        WCAG 2.2 - 2.4.2 Título da Página (Nível A)
        ABNT NBR 17225:2025 - 6.4.2 Títulos descritivos
        """
        title = self.soup.find('title')
        
        if not title:
            self.problemas.append(ProblemaAcessibilidade(
                criterio="2.4.2 - Título da Página",
                descricao="Página sem elemento <title>",
                severidade=SeveridadeProblema.CRITICO,
                nivel_wcag=NivelConformidade.A,
                elemento="<head>",
                sugestao="Adicione <title> descritivo no <head>",
                referencia_wcag="WCAG 2.2 - 2.4.2",
                referencia_abnt=self.mapeamento_normas["2.4.2"],
                codigo_exemplo='<head>\n  <title>Nome da Página - Nome do Site</title>\n</head>'
            ))
        elif len(title.get_text().strip()) < 3:
            self.problemas.append(ProblemaAcessibilidade(
                criterio="2.4.2 - Título da Página",
                descricao="Título da página muito curto ou vazio",
                severidade=SeveridadeProblema.GRAVE,
                nivel_wcag=NivelConformidade.A,
                elemento=str(title),
                sugestao="Forneça título descritivo e significativo",
                referencia_wcag="WCAG 2.2 - 2.4.2",
                referencia_abnt=self.mapeamento_normas["2.4.2"],
                codigo_exemplo='<title>Página Inicial - Minha Empresa</title>'
            ))
    
    def _verificar_idioma(self):
        """
        WCAG 2.2 - 3.1.1 Idioma da Página (Nível A)
        ABNT NBR 17225:2025 - 7.1 Identificação do idioma
        """
        html = self.soup.find('html')
        
        if not html or not html.get('lang'):
            self.problemas.append(ProblemaAcessibilidade(
                criterio="3.1.1 - Idioma da Página",
                descricao="Atributo lang ausente no elemento <html>",
                severidade=SeveridadeProblema.CRITICO,
                nivel_wcag=NivelConformidade.A,
                elemento="<html>",
                sugestao="Adicione atributo lang no elemento html",
                referencia_wcag="WCAG 2.2 - 3.1.1",
                referencia_abnt=self.mapeamento_normas["3.1.1"],
                codigo_exemplo='<html lang="pt-BR">'
            ))
    
    def _verificar_links(self):
        """
        WCAG 2.2 - 2.4.4 Finalidade do Link (Nível A)
        ABNT NBR 17225:2025 - 6.4.4 Links descritivos
        """
        links = self.soup.find_all('a', href=True)
        
        for link in links:
            texto = link.get_text().strip()
            aria_label = link.get('aria-label')
            title = link.get('title')
            
            # Links vazios
            if not texto and not aria_label and not link.find('img'):
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="2.4.4 - Finalidade do Link",
                    descricao="Link sem texto ou descrição",
                    severidade=SeveridadeProblema.CRITICO,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(link)[:100],
                    sugestao="Adicione texto descritivo ou aria-label",
                    referencia_wcag="WCAG 2.2 - 2.4.4",
                    referencia_abnt="ABNT 6.4.4 - Propósito dos links",
                    codigo_exemplo='<a href="/sobre" aria-label="Sobre nossa empresa">Saiba mais</a>'
                ))
            
            # Links genéricos
            textos_genericos = ['clique aqui', 'saiba mais', 'leia mais', 'aqui', 'mais']
            if texto.lower() in textos_genericos and not aria_label:
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="2.4.4 - Finalidade do Link",
                    descricao=f"Link com texto genérico: '{texto}'",
                    severidade=SeveridadeProblema.MODERADO,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(link)[:100],
                    sugestao="Use texto descritivo do destino do link",
                    referencia_wcag="WCAG 2.2 - 2.4.4",
                    referencia_abnt="ABNT 6.4.4 - Propósito dos links",
                    codigo_exemplo='<a href="/servicos">Conheça nossos serviços</a>'
                ))
            
            # Links que abrem em nova janela
            target = link.get('target')
            if target == '_blank':
                aviso_nova_janela = 'nova janela' in texto.lower() or 'new window' in texto.lower()
                if not aviso_nova_janela and not aria_label:
                    self.problemas.append(ProblemaAcessibilidade(
                        criterio="3.2.5 - Mudança de Contexto",
                        descricao="Link abre em nova janela sem aviso",
                        severidade=SeveridadeProblema.LEVE,
                        nivel_wcag=NivelConformidade.AAA,
                        elemento=str(link)[:100],
                        sugestao="Avise que o link abre em nova janela",
                        referencia_wcag="WCAG 2.2 - 3.2.5",
                        referencia_abnt="ABNT 7.2 - Previsibilidade",
                        codigo_exemplo='<a href="..." target="_blank" rel="noopener">Link (abre em nova janela)</a>'
                    ))
    
    def _verificar_tabelas(self):
        """
        WCAG 2.2 - 1.3.1 Info e Relações (Tabelas)
        ABNT NBR 17225:2025 - 5.3.1 Estrutura de tabelas
        """
        tabelas = self.soup.find_all('table')
        
        for tabela in tabelas:
            # Verificar caption
            caption = tabela.find('caption')
            if not caption:
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="1.3.1 - Estrutura de Tabelas",
                    descricao="Tabela sem <caption>",
                    severidade=SeveridadeProblema.MODERADO,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(tabela)[:100],
                    sugestao="Adicione <caption> descrevendo o propósito da tabela",
                    referencia_wcag="WCAG 2.2 - 1.3.1",
                    referencia_abnt=self.mapeamento_normas["1.3.1"],
                    codigo_exemplo='<table>\n  <caption>Vendas por região em 2024</caption>\n  ...\n</table>'
                ))
            
            # Verificar cabeçalhos
            thead = tabela.find('thead')
            th_elements = tabela.find_all('th')
            
            if not thead and not th_elements:
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="1.3.1 - Estrutura de Tabelas",
                    descricao="Tabela sem elementos <th> para cabeçalhos",
                    severidade=SeveridadeProblema.GRAVE,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(tabela)[:100],
                    sugestao="Use <th> para células de cabeçalho e <thead> para agrupar",
                    referencia_wcag="WCAG 2.2 - 1.3.1",
                    referencia_abnt=self.mapeamento_normas["1.3.1"],
                    codigo_exemplo='<table>\n  <thead>\n    <tr><th>Coluna 1</th><th>Coluna 2</th></tr>\n  </thead>\n  <tbody>...</tbody>\n</table>'
                ))
            
            # Verificar scope em th
            for th in th_elements:
                if not th.get('scope'):
                    self.problemas.append(ProblemaAcessibilidade(
                        criterio="1.3.1 - Estrutura de Tabelas",
                        descricao="Elemento <th> sem atributo scope",
                        severidade=SeveridadeProblema.LEVE,
                        nivel_wcag=NivelConformidade.A,
                        elemento=str(th)[:100],
                        sugestao="Adicione scope='col' ou scope='row' ao <th>",
                        referencia_wcag="WCAG 2.2 - 1.3.1",
                        referencia_abnt=self.mapeamento_normas["1.3.1"],
                        codigo_exemplo='<th scope="col">Nome da Coluna</th>'
                    ))
    
    def _verificar_aria(self):
        """
        WCAG 2.2 - 4.1.2 Nome, Função e Valor (ARIA)
        ABNT NBR 17225:2025 - 8.2 ARIA e tecnologias assistivas
        """
        # Verificar roles ARIA
        elementos_com_role = self.soup.find_all(attrs={"role": True})
        
        roles_validos = [
            'alert', 'alertdialog', 'application', 'article', 'banner', 
            'button', 'checkbox', 'complementary', 'contentinfo', 'dialog',
            'directory', 'document', 'form', 'grid', 'gridcell', 'group',
            'heading', 'img', 'link', 'list', 'listbox', 'listitem',
            'log', 'main', 'marquee', 'math', 'menu', 'menubar', 'menuitem',
            'menuitemcheckbox', 'menuitemradio', 'navigation', 'note',
            'option', 'presentation', 'progressbar', 'radio', 'radiogroup',
            'region', 'row', 'rowgroup', 'rowheader', 'scrollbar', 'search',
            'separator', 'slider', 'spinbutton', 'status', 'tab', 'tablist',
            'tabpanel', 'textbox', 'timer', 'toolbar', 'tooltip', 'tree',
            'treegrid', 'treeitem'
        ]
        
        for elem in elementos_com_role:
            role = elem.get('role')
            if role not in roles_validos:
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="4.1.2 - ARIA Válido",
                    descricao=f"Role ARIA inválido: '{role}'",
                    severidade=SeveridadeProblema.GRAVE,
                    nivel_wcag=NivelConformidade.A,
                    elemento=str(elem)[:100],
                    sugestao="Use apenas roles ARIA válidos da especificação",
                    referencia_wcag="WCAG 2.2 - 4.1.2",
                    referencia_abnt=self.mapeamento_normas["4.1.2"],
                    codigo_exemplo='<div role="navigation">...</div>'
                ))
        
        # Verificar aria-labelledby referenciando IDs inexistentes
        elementos_com_labelledby = self.soup.find_all(attrs={"aria-labelledby": True})
        for elem in elementos_com_labelledby:
            labelledby_ids = elem.get('aria-labelledby').split()
            for id_ref in labelledby_ids:
                if not self.soup.find(id=id_ref):
                    self.problemas.append(ProblemaAcessibilidade(
                        criterio="4.1.2 - ARIA Referências",
                        descricao=f"aria-labelledby referencia ID inexistente: '{id_ref}'",
                        severidade=SeveridadeProblema.GRAVE,
                        nivel_wcag=NivelConformidade.A,
                        elemento=str(elem)[:100],
                        sugestao="Certifique-se que o ID referenciado existe na página",
                        referencia_wcag="WCAG 2.2 - 4.1.2",
                        referencia_abnt=self.mapeamento_normas["4.1.2"],
                        codigo_exemplo='<h2 id="titulo-secao">Título</h2>\n<div aria-labelledby="titulo-secao">...</div>'
                    ))
    
    def _verificar_responsividade(self):
        """
        WCAG 2.2 - 1.4.10 Reflow (Nível AA)
        ABNT NBR 17225:2025 - 5.4.10 Adaptação de conteúdo
        """
        # Verificar viewport meta tag
        viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        
        if not viewport:
            self.problemas.append(ProblemaAcessibilidade(
                criterio="1.4.10 - Reflow/Responsividade",
                descricao="Meta tag viewport ausente",
                severidade=SeveridadeProblema.GRAVE,
                nivel_wcag=NivelConformidade.AA,
                elemento="<head>",
                sugestao="Adicione meta viewport para responsividade",
                referencia_wcag="WCAG 2.2 - 1.4.10",
                referencia_abnt="ABNT 5.4.10 - Adaptação visual",
                codigo_exemplo='<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            ))
        else:
            content = viewport.get('content', '')
            if 'user-scalable=no' in content or 'maximum-scale=1' in content:
                self.problemas.append(ProblemaAcessibilidade(
                    criterio="1.4.4 - Redimensionamento de Texto",
                    descricao="Viewport bloqueia zoom do usuário",
                    severidade=SeveridadeProblema.CRITICO,
                    nivel_wcag=NivelConformidade.AA,
                    elemento=str(viewport),
                    sugestao="Não bloqueie o zoom: remova user-scalable=no",
                    referencia_wcag="WCAG 2.2 - 1.4.4",
                    referencia_abnt="ABNT 5.4.4 - Redimensionamento",
                    codigo_exemplo='<meta name="viewport" content="width=device-width, initial-scale=1.0">'
                ))
    
    def _is_decorative(self, img) -> bool:
        """Verifica se uma imagem é decorativa"""
        # Imagens dentro de links com texto
        parent_link = img.find_parent('a')
        if parent_link and parent_link.get_text().strip():
            return True
        
        # Classes ou atributos que indicam decoração
        classes = ' '.join(img.get('class', []))
        if any(word in classes.lower() for word in ['icon', 'decor', 'bg', 'background']):
            return True
        
        return False
    
    def _calcular_pontuacao(self) -> float:
        """
        Calcula pontuação de acessibilidade (0-100)
        Baseado na severidade e quantidade de problemas
        """
        if not self.problemas:
            return 100.0
        
        pesos_severidade = {
            SeveridadeProblema.CRITICO: 10,
            SeveridadeProblema.GRAVE: 5,
            SeveridadeProblema.MODERADO: 2,
            SeveridadeProblema.LEVE: 1
        }
        
        pontos_perdidos = sum(
            pesos_severidade[p.severidade] for p in self.problemas
        )
        
        # Normalizar para escala 0-100
        pontuacao = max(0, 100 - pontos_perdidos)
        return round(pontuacao, 2)
    
    def _gerar_recomendacoes_priorizadas(self) -> List[str]:
        """Gera lista de recomendações priorizadas"""
        recomendacoes = []
        
        # Agrupar por severidade
        criticos = [p for p in self.problemas if p.severidade == SeveridadeProblema.CRITICO]
        graves = [p for p in self.problemas if p.severidade == SeveridadeProblema.GRAVE]
        
        if criticos:
            recomendacoes.append(
                f"PRIORIDADE CRÍTICA: Corrigir {len(criticos)} problemas críticos "
                "(imagens sem alt, formulários sem labels, elementos não acessíveis por teclado)"
            )
        
        if graves:
            recomendacoes.append(
                f"PRIORIDADE ALTA: Resolver {len(graves)} problemas graves "
                "(estrutura semântica, contraste, navegação)"
            )
        
        # Recomendações por categoria
        categorias = {}
        for p in self.problemas:
            cat = p.criterio.split('-')[0].strip()
            categorias[cat] = categorias.get(cat, 0) + 1
        
        categoria_mais_problemas = max(categorias.items(), key=lambda x: x[1]) if categorias else None
        if categoria_mais_problemas:
            recomendacoes.append(
                f"Categoria com mais problemas: '{categoria_mais_problemas[0]}' "
                f"({categoria_mais_problemas[1]} ocorrências)"
            )
        
        # Conformidade
        nivel_a = sum(1 for p in self.problemas if p.nivel_wcag == NivelConformidade.A)
        if nivel_a > 0:
            recomendacoes.append(
                f"{nivel_a} violações do Nível A da WCAG (requisitos mínimos obrigatórios)"
            )
        
        recomendacoes.append(
            "Consulte WCAG 2.2 e ABNT NBR 17225:2025 para diretrizes completas"
        )
        
        return recomendacoes
    
    def _avaliar_conformidade(self) -> Tuple[Dict[str, bool], Dict[str, bool]]:
        """Avalia conformidade com WCAG e ABNT"""
        # WCAG
        problemas_nivel_a = [p for p in self.problemas if p.nivel_wcag == NivelConformidade.A]
        problemas_nivel_aa = [p for p in self.problemas if p.nivel_wcag == NivelConformidade.AA]
        
        conformidade_wcag = {
            'Nível A': len(problemas_nivel_a) == 0,
            'Nível AA': len(problemas_nivel_a) == 0 and len(problemas_nivel_aa) == 0,
            'Nível AAA': False  # Requer análise mais profunda
        }
        
        # ABNT - Mapear critérios principais
        criterios_abnt = {
            '5.1 - Alternativas em texto': True,
            '5.3 - Estrutura semântica': True,
            '6.1 - Navegação por teclado': True,
            '8.2 - Identificação de campos': True
        }
        
        for problema in self.problemas:
            if problema.referencia_abnt:
                criterio_base = problema.referencia_abnt.split('-')[0].strip()
                if any(criterio_base in key for key in criterios_abnt.keys()):
                    for key in criterios_abnt.keys():
                        if criterio_base in key:
                            criterios_abnt[key] = False
        
        return conformidade_wcag, criterios_abnt
    
    def _gerar_relatorio(self) -> RelatorioAcessibilidade:
        """Gera relatório completo de acessibilidade"""
        pontuacao = self._calcular_pontuacao()
        
        problemas_por_severidade = {
            'Crítico': sum(1 for p in self.problemas if p.severidade == SeveridadeProblema.CRITICO),
            'Grave': sum(1 for p in self.problemas if p.severidade == SeveridadeProblema.GRAVE),
            'Moderado': sum(1 for p in self.problemas if p.severidade == SeveridadeProblema.MODERADO),
            'Leve': sum(1 for p in self.problemas if p.severidade == SeveridadeProblema.LEVE)
        }
        
        conformidade_wcag, conformidade_abnt = self._avaliar_conformidade()
        recomendacoes = self._gerar_recomendacoes_priorizadas()
        
        return RelatorioAcessibilidade(
            url=self.url,
            data_avaliacao=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pontuacao_geral=pontuacao,
            total_problemas=len(self.problemas),
            problemas_por_severidade=problemas_por_severidade,
            problemas=self.problemas,
            recomendacoes_priorizadas=recomendacoes,
            conformidade_wcag=conformidade_wcag,
            conformidade_abnt=conformidade_abnt
        )
    
    def _gerar_relatorio_erro(self, erro: str) -> RelatorioAcessibilidade:
        """Gera relatório em caso de erro"""
        return RelatorioAcessibilidade(
            url=self.url,
            data_avaliacao=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pontuacao_geral=0.0,
            total_problemas=0,
            problemas_por_severidade={},
            problemas=[],
            recomendacoes_priorizadas=[f"Erro ao avaliar: {erro}"],
            conformidade_wcag={},
            conformidade_abnt={}
        )
    
    def exportar_relatorio_json(self, relatorio: RelatorioAcessibilidade, 
                                arquivo: str = "relatorio_acessibilidade.json"):
        """Exporta relatório em formato JSON"""
        dados = {
            'url': relatorio.url,
            'data_avaliacao': relatorio.data_avaliacao,
            'pontuacao_geral': relatorio.pontuacao_geral,
            'total_problemas': relatorio.total_problemas,
            'problemas_por_severidade': relatorio.problemas_por_severidade,
            'conformidade_wcag': relatorio.conformidade_wcag,
            'conformidade_abnt': relatorio.conformidade_abnt,
            'recomendacoes': relatorio.recomendacoes_priorizadas,
            'problemas': [
                {
                    'criterio': p.criterio,
                    'descricao': p.descricao,
                    'severidade': p.severidade.value,
                    'nivel_wcag': p.nivel_wcag.value,
                    'sugestao': p.sugestao,
                    'referencia_wcag': p.referencia_wcag,
                    'referencia_abnt': p.referencia_abnt,
                    'codigo_exemplo': p.codigo_exemplo
                }
                for p in relatorio.problemas
            ]
        }
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        print(f"Relatório exportado para: {arquivo}")
    
    def imprimir_relatorio(self, relatorio: RelatorioAcessibilidade):
        """Imprime relatório formatado no console"""
        print("\n" + "="*80)
        print("RELATÓRIO DE AVALIAÇÃO DE ACESSIBILIDADE WEB")
        print("="*80)
        print(f"\nURL Avaliada: {relatorio.url}")
        print(f"Data da Avaliação: {relatorio.data_avaliacao}")
        print(f"\nPONTUAÇÃO GERAL: {relatorio.pontuacao_geral}/100")
        
        # Classificação
        if relatorio.pontuacao_geral >= 90:
            classificacao = "Excelente!"
        elif relatorio.pontuacao_geral >= 70:
            classificacao = "Bom."
        elif relatorio.pontuacao_geral >= 50:
            classificacao = "Regular."
        else:
            classificacao = "Necessita Melhorias Urgentes"
        
        print(f"Classificação: {classificacao}")
        
        # Resumo de problemas
        print(f"\nTotal de Problemas: {relatorio.total_problemas}")
        print("\nDistribuição por Severidade:")
        for severidade, count in relatorio.problemas_por_severidade.items():
            if count > 0:
                emoji = {"Crítico": "", "Grave": "", "Moderado": "", "Leve": ""}
                print(f"  {emoji.get(severidade, '•')} {severidade}: {count}")
        
        # Conformidade
        print("\nCONFORMIDADE COM NORMAS:")
        print("\nWCAG 2.2:")
        for nivel, conforme in relatorio.conformidade_wcag.items():
            status = "Conforme" if conforme else "Não Conforme"
            print(f"  {nivel}: {status}")
        
        print("\nABNT NBR 17225:2025:")
        for criterio, conforme in relatorio.conformidade_abnt.items():
            status = "Conforme" if conforme else "Não Conforme"
            print(f"  {criterio}: {status}")
        
        # Recomendações
        print("\nRECOMENDAÇÕES PRIORIZADAS:")
        for i, rec in enumerate(relatorio.recomendacoes_priorizadas, 1):
            print(f"\n{i}. {rec}")
        
        # Detalhes dos problemas
        if relatorio.problemas:
            print("\n" + "="*80)
            print("DETALHAMENTO DOS PROBLEMAS ENCONTRADOS")
            print("="*80)
            
            for i, problema in enumerate(relatorio.problemas[:10], 1):  # Primeiros 10
                print(f"\n{i}. {problema.criterio}")
                print(f"   Severidade: {problema.severidade.value}")
                print(f"   Descrição: {problema.descricao}")
                print(f"   Sugestão: {problema.sugestao}")
                print(f"   Referência: {problema.referencia_wcag} | {problema.referencia_abnt}")
                if problema.codigo_exemplo:
                    print(f"   Exemplo: {problema.codigo_exemplo[:80]}...")
            
            if len(relatorio.problemas) > 10:
                print(f"\n... e mais {len(relatorio.problemas) - 10} problemas.")
                print("Exporte o relatório completo em JSON para ver todos os detalhes.")
        
        print("\n" + "="*80)
        print("Avaliação concluída!")
        print("="*80 + "\n")


def main():
    """Função principal - exemplo de uso do agente"""
    print("Agente de IA - Avaliador de Acessibilidade Web")
    print("Alinhado com WCAG 2.2 e ABNT NBR 17225:2025\n")
    
    # Exemplo de uso
    url = input("Digite a URL do website a ser avaliado: ").strip()
    
    if not url:
        url = "https://example.com"  # URL padrão para teste
        print(f"Usando URL padrão: {url}\n")
    
    # Criar agente e avaliar
    agente = AgenteAcessibilidade()
    print(f"\nAvaliando acessibilidade de: {url}\n")
    
    relatorio = agente.avaliar_website(url)
    
    # Exibir relatório
    agente.imprimir_relatorio(relatorio)
    
    # Exportar JSON
    exportar = input("\nDeseja exportar o relatório em JSON? (s/n): ").lower()
    if exportar == 's':
        nome_arquivo = input("Nome do arquivo (deixe em branco para usar padrão): ").strip()
        if nome_arquivo:
            agente.exportar_relatorio_json(relatorio, nome_arquivo)
        else:
            agente.exportar_relatorio_json(relatorio)


if __name__ == "__main__":
    main()
