import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import subprocess
from datetime import datetime, timedelta
import threading
import os
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

file_lock = threading.Lock()

def load_cookies(driver, cookies_file):
    with open(cookies_file, "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.execute_script(
                "document.cookie = arguments[0] + '=' + arguments[1] + '; domain=' + arguments[2] + '; path=' + arguments[3] + '; secure=' + arguments[4] + ';';",
                cookie['name'], cookie['value'], cookie['domain'], cookie['path'], 'true' if cookie['secure'] else 'false'
            )

def login_with_cookies(driver, cookies_file):
    driver.get("https://www.facebook.com/")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        load_cookies(driver, cookies_file)
        driver.refresh()
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-click='profile_icon']"))
            )
        except TimeoutException:
            pass
    except TimeoutException:
        pass
    except NoSuchElementException as e:
        pass
    except Exception as e:
        pass

def verificar_ou_criar_pastas(concurso):
    base_path = f"database/{concurso}"
    subdirs = ["logs/instagram", "logs/facebook", "logs/tiktok", "logs/youtube", "results", "users"]
    user_files = ["usersFace.txt", "usersIg.txt", "usersTtk.txt", "usersYt.txt"]

    for subdir in subdirs:
        path = os.path.join(base_path, subdir)
        os.makedirs(path, exist_ok=True)

    for user_file in user_files:
        path = os.path.join(base_path, "users", user_file)
        if not os.path.exists(path):
            with open(path, "w") as f:
                pass

def scroll_down(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_post_date(video_element):
    try:
        print("\n=== DEBUG: Aguardando carregamento do conteúdo ===")
        
        # Espera até que o estado de carregamento desapareça
        try:
            WebDriverWait(video_element, 10).until_not(
                lambda x: x.find_elements(By.CSS_SELECTOR, "[data-visualcompletion='loading-state']")
            )
            print("Conteúdo carregado com sucesso")
        except:
            print("Timeout esperando o carregamento")
            return None

        print("=== Conteúdo completo do vídeo ===")
        print(video_element.get_attribute('outerHTML'))
        
        # Lista de meses em inglês e português
        meses = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
            'fev': 2, 'abr': 4, 'mai': 5, 'ago': 8, 'set': 9, 'out': 10, 'dez': 12
        }
        
        # Procura spans com a classe específica de data
        date_spans = video_element.find_elements(By.CSS_SELECTOR, 
            "span.x4k7w5x.x1h91t0o.x1h9r5lt.x1jfb8zj.xv2umb2.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1qrby5j")
        
        print(f"Encontrados {len(date_spans)} spans com a classe de data")
        for span in date_spans:
            text = span.text.strip().lower()
            print(f"Texto encontrado em span de data: '{text}'")
            
            # Tenta extrair mês e dia
            parts = text.split()
            if len(parts) == 2:
                # Verifica se é "Nov 7" ou "7 Nov"
                if parts[0] in meses:
                    month, day = parts
                elif parts[1] in meses:
                    day, month = parts
                else:
                    continue
                
                # Remove qualquer texto não numérico do dia
                day = ''.join(filter(str.isdigit, day))
                normalized_date = f"{day} de {month}"
                print(f"Data normalizada: {normalized_date}")
                return normalized_date
                
        print("Nenhuma data válida encontrada")
        return None
        
    except Exception as e:
        print(f"Erro ao buscar data: {str(e)}")
        return None

def scroll_to_top(driver):
    print("Scrollando para o topo da página...")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

def click_publications_tab(driver):
    try:
        # Primeiro scroll para o topo
        scroll_to_top(driver)
        
        # Aguarda um momento para a página estabilizar
        time.sleep(2)
        
        print("Procurando botão de publicações...")
        publications_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/a[1]/div[1]/span"))
        )
        
        print("Tentando clicar no botão de publicações...")
        # Tenta clicar usando JavaScript
        driver.execute_script("arguments[0].click();", publications_button)
        time.sleep(2)
        
        print("Botão de publicações clicado com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao clicar na aba publicações: {str(e)}")
        return False

def get_video_containers(driver):
    try:
        container = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div/div"))
        )
        return container.find_elements(By.CSS_SELECTOR, "div.x1ey2m1c.x78zum5.xdt5ytf.xozqiw3.x17qophe.x13a6bvl.x10l6tqk.x13vifvy.xq2gx43.xh8yej3")
    except Exception as e:
        print(f"Erro ao obter containers de vídeo: {str(e)}")
        return []

def validate_views_and_dates(driver, days, views_list):
    total_views = 0
    videos_processados = 0
    continue_scrolling = True
    last_height = driver.execute_script("return document.body.scrollHeight")
    processed_dates = []
    empty_scroll_count = 0
    max_empty_scrolls = 3

    while continue_scrolling and empty_scroll_count < max_empty_scrolls:
        try:
            # Espera o container principal carregar
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, 
                    "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]"))
            )
            time.sleep(2)
            
            # Busca todas as informações dos posts usando a classe específica
            post_elements = container.find_elements(By.CSS_SELECTOR, 
                "span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x4zkp8e.x3x7a5m.x1nxh6w3.x1sibtaa.xo1l8bm.x14ctfv")

            date_elements = []
            # Loop em cada post element
            for post in post_elements:
                # Checa se "Reels" esta presente
                if "Reels" in post.text:
                    date_element = post.find_element(By.CSS_SELECTOR,
                        "span.x4k7w5x.x1h91t0o.x1h9r5lt.x1jfb8zj.xv2umb2.x1beo9mf")
                    date_elements.append(date_element)

            new_dates_found = False
            print(f"\nEncontradas {len(date_elements)} datas na página")
            
            for date_element in date_elements:
                date_text = date_element.text.strip()
                
                # Evita processar datas já vistas
                if date_text in processed_dates:
                    continue
                
                print(f"Nova data encontrada: {date_text}")
                
                if not date_text:
                    print("Data vazia encontrada, pulando...")
                    continue
                    
                if not is_within_days(date_text, days):
                    print(f"Data fora do período: {date_text}")
                    continue_scrolling = False
                    break
                
                processed_dates.append(date_text)
                videos_processados += 1
                new_dates_found = True
                
                print(f"Data válida processada: {date_text}")
            
            if not new_dates_found:
                empty_scroll_count += 1
                print(f"Nenhuma nova data encontrada. Tentativa {empty_scroll_count} de {max_empty_scrolls}")
            else:
                empty_scroll_count = 0

            if continue_scrolling:
                last_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    empty_scroll_count += 1

        except Exception as e:
            print(f"Erro durante validação: {str(e)}")
            break

    if videos_processados > 0:
        total_views = sum(views_list[:videos_processados])
        print(f"\nResumo final:")
        print(f"Total de vídeos válidos encontrados: {videos_processados}")
        print(f"Datas processadas: {processed_dates}")
        print(f"Visualizações consideradas: {views_list[:videos_processados]}")
        print(f"Total de visualizações: {total_views}")
    else:
        print("\nNenhum vídeo válido encontrado")
        total_views = 0

    return total_views

def parse_views_count(views_text):
    try:
        text = views_text.lower().strip()
        
        # Remove espaços extras e vírgulas
        text = text.replace(' ', '').replace(',', '.')
        
        # Processa diferentes formatos de números
        if 'k' in text:
            number = float(text.replace('k', ''))
            return int(number * 1000)
        elif 'm' in text:
            number = float(text.replace('m', ''))
            return int(number * 1000000)
        elif 'mil' in text:
            number = float(text.replace('mil', ''))
            return int(number * 1000)
        elif 'mi' in text:
            number = float(text.replace('mi', ''))
            return int(number * 1000000)
        else:
            return int(float(text))
    except Exception as e:
        print(f"Erro ao converter número '{views_text}': {str(e)}")
        return 0

def is_within_days(date_text, days):
    try:
        current_date = datetime.now()
        
        # Converte formato "Nov 7" ou "Oct 30" para "7 de nov" ou "30 de out"
        parts = date_text.lower().split()
        if len(parts) == 2:
            month, day = parts if parts[0] in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'] else parts[::-1]
            
            # Mapeia meses em inglês para português
            month_map = {
                'jan': 'jan', 'feb': 'fev', 'mar': 'mar', 'apr': 'abr', 
                'may': 'mai', 'jun': 'jun', 'jul': 'jul', 'aug': 'ago',
                'sep': 'set', 'oct': 'out', 'nov': 'nov', 'dec': 'dez'
            }
            
            normalized_date = f"{day} de {month_map.get(month, month)}"
            return super_is_within_days(normalized_date, days)
            
        return super_is_within_days(date_text, days)
        
    except Exception as e:
        print(f"Erro ao processar data '{date_text}': {str(e)}")
        return False

def super_is_within_days(date_text, days):
    # Código original da função is_within_days aqui
    try:
        current_date = datetime.now()
        
        # Processa datas no formato "dia de mês"
        if "de" in date_text:
            parts = date_text.split(" de ")
            dia = int(parts[0])
            mes = parts[1].lower()
            
            # Mapeamento de meses em português
            meses = {
                'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
                'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
            }
            
            # Pega os primeiros 3 caracteres do mês para normalizar
            mes_num = meses[mes[:3]]
            
            # Define o ano baseado no mês
            ano = current_date.year
            if mes_num > current_date.month:
                ano -= 1
                
            post_date = datetime(ano, mes_num, dia)
            
        # Processamento existente para outros formatos
        elif 'minuto' in date_text:
            minutes_ago = int(date_text.split(' ')[0])
            post_date = current_date - timedelta(minutes=minutes_ago)
        elif 'hora' in date_text:
            hours_ago = int(date_text.split(' ')[0])
            post_date = current_date - timedelta(hours=hours_ago)
        elif 'dia' in date_text:
            days_ago = int(date_text.split(' ')[0])
            post_date = current_date - timedelta(days=days_ago)
        elif 'semana' in date_text:
            weeks_ago = int(date_text.split(' ')[0])
            post_date = current_date - timedelta(weeks=weeks_ago)
        else:
            raise ValueError(f"Formato de data não reconhecido: {date_text}")
            
        delta = current_date - post_date
        is_valid = delta.days <= days
        print(f"Data do post: {post_date.strftime('%d/%m/%Y')}, dentro do período? {is_valid}")
        return is_valid
        
    except Exception as e:
        print(f"Erro ao processar data '{date_text}': {str(e)}")
        return False

def is_ad_post(driver):
    try:
        ad_element = driver.find_element(By.CSS_SELECTOR, "span[data-testid='ad_label']")
        if "Patrocinado" in ad_element.text:
            return True
        return False
    except NoSuchElementException:
        return False

def zoom_out(driver):
    driver.execute_script("document.body.style.zoom='25%'")

def scroll_and_collect_views(driver):
    views = []
    processed_views = set()  # Conjunto para controlar visualizações já coletadas
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Coleta as visualizações na posição atual da página
        new_views = get_views(driver)
        
        # Adiciona apenas visualizações não processadas anteriormente
        for view in new_views:
            if view not in processed_views:
                views.append(view)
                processed_views.add(view)

        # Rola para baixo na página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Verifica se chegou ao fim da página
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return views

def get_likes(driver, days):
    total_likes = 0
    posts_considerados = 0
    post_index = 1

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-pagelet='ProfileTimeline']"))
        )

        zoom_out(driver)
        scroll_down(driver)

        post_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileTimeline'] div[role='article']")
        likes_elements = driver.find_elements(By.CSS_SELECTOR, "span[data-testid='UFI2TopReactions/tooltip_LIKE']")

        if len(post_elements) != len(likes_elements):
            return total_likes

        for post_index in range(len(post_elements)):
            try:
                likes_text = likes_elements[post_index].text.replace(' curtidas', '').replace(' curtida', '')
                
                if 'mil' in likes_text:
                    number = float(likes_text.replace(' mil', ''))
                    likes = int(number * 1000)
                elif 'Nenhuma' in likes_text or 'Nenhum' in likes_text:
                    likes = 0
                else:
                    likes = int(likes_text.replace('.', ''))

                post_element = post_elements[post_index]
                post_element.click()
                time.sleep(2)

                if is_ad_post(driver):
                    driver.back()
                    time.sleep(2)
                    continue

                post_date_text = get_post_date(driver)
                
                if not post_date_text:
                    driver.back()
                    time.sleep(2)
                    continue

                if not is_within_days(post_date_text, days):
                    if posts_considerados >= 3:
                        break
                    else:
                        driver.back()
                        time.sleep(2)
                        continue

                total_likes += likes
                posts_considerados += 1

                driver.back()
                time.sleep(2)

            except Exception:
                break

    except Exception:
        pass

    return total_likes

def get_views(driver):
    views = []
    try:
        print("Tentando localizar elementos de visualização...")
        print("URL atual:", driver.current_url)
        
        # Tenta encontrar o container principal
        base_xpath = "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[3]/div/div"
        
        # Encontra todos os elementos de visualização usando XPath relativo
        views_elements = []
        index = 1
        while True:
            try:
                element = driver.find_element(By.XPATH, f"{base_xpath}[{index}]/a/div[1]/div/div[2]/span/span")
                views_elements.append(element)
                index += 1
            except:
                break

        print(f"Encontrados {len(views_elements)} elementos com XPath")

        # Se não encontrar elementos pelo XPath, tenta pelo seletor CSS
        if not views_elements:
            print("Tentando seletor CSS...")
            views_elements = driver.find_elements(By.CSS_SELECTOR, "span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft")
            print(f"Encontrados {len(views_elements)} elementos com seletor CSS")

        print("Elementos de visualização encontrados:")
        for idx, view in enumerate(views_elements):
            try:
                text_content = view.text.strip()
                print(f"Visualização {idx + 1}: {text_content}")
                views.append(parse_views_count(text_content))
            except Exception as e:
                print(f"Erro ao processar elemento {idx + 1}: {str(e)}")
                views.append(0)
                
        print(f"Total de visualizações coletadas: {len(views)}")
        print(f"Lista de visualizações: {views}")
        
    except Exception as e:
        print(f"Erro ao coletar visualizações: {str(e)}")
        print("HTML da página:")
        try:
            print(driver.page_source[:500] + "...")
        except:
            print("Não foi possível obter o HTML da página")
    return views

def identify_profile_type(url):
    """Identifica o tipo de perfil baseado na URL"""
    if '/videos' in url or '&sk=videos' in url:
        return 'videos'
    elif '/reels' in url or 'reels_tab' in url:
        return 'reels'
    return 'unknown'

def handle_reels_profile(driver, days):
    """Manipula perfis que usam o formato /reels ou reels_tab"""
    try:
        print("Aguardando carregamento da página de reels...")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main']"))
        )
        
        print("Aplicando zoom out...")
        zoom_out(driver)
        time.sleep(1)
        
        print("Coletando visualizações iniciais...")
        initial_views = scroll_and_collect_views(driver)
        print(f"Visualizações coletadas na página de reels: {len(initial_views)}")
        
        print("Preparando para clicar na aba publicações...")
        if click_publications_tab(driver):
            print("Validando vídeos na aba publicações com scroll contínuo...")
            validated_views = validate_views_and_dates(driver, days, initial_views)
            return validated_views
        else:
            print("Não foi possível acessar a aba publicações, usando visualizações não validadas")
            return sum(initial_views)
    except Exception as e:
        print(f"Erro ao processar perfil de reels: {str(e)}")
        return 0

def solicitar_xpath_container(driver):
    while True:
        xpath = input("Por favor, forneça o XPath do contêiner principal de vídeos: ")
        try:
            container = driver.find_element(By.XPATH, xpath)
            print("Contêiner principal encontrado com sucesso.")
            return container
        except NoSuchElementException:
            print("Contêiner não encontrado. Por favor, tente novamente.")

def solicitar_xpath_video(driver, video_index):
    while True:
        xpath = input(f"Por favor, forneça o XPath do vídeo {video_index}: ")
        try:
            video_element = driver.find_element(By.XPATH, xpath)
            print(f"Vídeo {video_index} encontrado com sucesso.")
            return video_element
        except NoSuchElementException:
            print(f"Vídeo {video_index} não encontrado. Por favor, tente novamente.")

def solicitar_xpath_elemento(driver, descricao):
    while True:
        xpath = input(f"Por favor, forneça o XPath do {descricao}: ")
        try:
            elemento = driver.find_element(By.XPATH, xpath)
            print(f"{descricao.capitalize()} encontrado com sucesso.")
            return xpath, elemento
        except NoSuchElementException:
            print(f"{descricao.capitalize()} não encontrado. Por favor, tente novamente.")

def salvar_xpaths_validos(xpaths):
    with open("xpaths_validos.txt", "w") as file:
        for descricao, xpath in xpaths.items():
            file.write(f"{descricao}: {xpath}\n")

def get_date_from_elements(container):
    date_parts = []
    index = 1
    while True:
        try:
            # Tenta encontrar o elemento da data pelo índice
            element = container.find_element(By.XPATH, f".//b[{index}]")
            date_parts.append(element.text.strip())
            index += 1
        except NoSuchElementException:
            break
    return ''.join(date_parts)

def get_date_from_elements_js(driver):
    script = """
    // Função para converter XPath em elemento
    function getElementByXPath(xpath) {
        return document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    }

    // XPath fornecido
    const xpath = '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div/div/div[2]/div[1]/div/div[1]/div/div/div[1]/div[1]/div[2]/div/div[2]/span/div/span[1]/span/span/a/span';

    // Obtém os elementos pelo XPath
    const elementsSnapshot = getElementByXPath(xpath);

    // Array para armazenar os textos visíveis e filtrados
    const visibleTexts = [];

    // Itera sobre os elementos e extrai os textos visíveis
    for (let i = 0; i < elementsSnapshot.snapshotLength; i++) {
        const element = elementsSnapshot.snapshotItem(i);
        if (element.offsetParent !== null) { // Verifica se o elemento está visível
            // Remove os hífens do texto e adiciona ao array
            const filteredText = element.textContent.replace(/-/g, '').trim();
            visibleTexts.push(filteredText);
        }
    }

    // Retorna o array de textos visíveis e filtrados
    return visibleTexts.join(' ');
    """
    return driver.execute_script(script)

def handle_videos_profile(driver, days):
    """Manipula perfis que usam o formato /videos"""
    total_views = 0
    video_index = 1
    xpaths = {
        "contêiner principal": "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]",
        "vídeo base": "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[3]/div/div[",
        "visualização base": "/html/body/div[1]/div/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div/div/div[2]/div[1]/div/div[1]/div/div/div[2]/div[1]/div/div[2]/div[2]/span/span/div/div[1]"
    }
    
    try:
        print("\n=== DEBUG: Iniciando processamento de perfil de vídeos ===")
        print(f"URL atual: {driver.current_url}")
        
        container_xpath = xpaths["contêiner principal"]
        try:
            videos_container = driver.find_element(By.XPATH, container_xpath)
            print("Contêiner principal encontrado com sucesso.")
        except NoSuchElementException:
            print("Contêiner não encontrado. Por favor, verifique o XPath.")
            return 0
        
        print("\n=== DEBUG: Estrutura da página ===")
        print("Conteúdo do container:")
        print(videos_container.get_attribute('outerHTML'))
        
        print("\nRealizando zoom out inicial...")
        zoom_out(driver)
        time.sleep(3)
        
        while True:
            try:
                print(f"\n=== DEBUG: Tentando processar vídeo {video_index} ===")
                
                # Constrói o XPath do vídeo atual
                video_xpath = f"{xpaths['vídeo base']}{video_index}]"
                try:
                    video_element = driver.find_element(By.XPATH, video_xpath)
                    print(f"Vídeo {video_index} encontrado com sucesso.")
                except NoSuchElementException:
                    print(f"Vídeo {video_index} não encontrado. Encerrando processamento.")
                    break
                
                print("Tentando clicar no vídeo...")
                try:
                    video_element.click()
                except:
                    print("Click direto falhou, tentando com JavaScript")
                    driver.execute_script("arguments[0].click();", video_element)
                time.sleep(3)
                
                print("\n=== DEBUG: Processando dados do vídeo ===")
                
                # Usa o XPath das visualizações fornecido
                views_xpath = xpaths["visualização base"]
                try:
                    views_element = driver.find_element(By.XPATH, views_xpath)
                    views_text = views_element.text.strip()
                    print(f"Visualizações encontradas: {views_text}")
                except NoSuchElementException:
                    print(f"Contador de visualizações não encontrado para o vídeo {video_index}.")
                    break
                
                print("Coletando partes da data...")
                date_text = get_date_from_elements_js(driver)
                print(f"Data completa encontrada: {date_text}")
                
                if not date_text:
                    print("Data não encontrada, tentando novamente...")
                    continue
                
                # Temporariamente não verificando se a data está dentro do período
                views = parse_views_count(views_text)
                total_views += views
                print(f"Vídeo válido - Adicionando {views} visualizações ao total")
                
                print("Fechando vídeo atual...")
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(2)
                video_index += 1
                
            except TimeoutException:
                print(f"Timeout ao procurar vídeo {video_index}")
                break
            except Exception as e:
                print(f"ERRO inesperado ao processar vídeo {video_index}: {str(e)}")
                print("Stack trace completo:", e.__traceback__)
                break
                
        # Salva os XPaths válidos em um arquivo
        salvar_xpaths_validos(xpaths)
                
    except Exception as e:
        print(f"ERRO CRÍTICO no processamento do perfil: {str(e)}")
        print("Stack trace completo:", e.__traceback__)
    
    print(f"\n=== DEBUG: Resumo final ===")
    print(f"Total de vídeos processados: {video_index - 1}")
    print(f"Total de visualizações coletadas: {total_views}")
    return total_views

def scrape_user(driver, user, days, concurso):
    print(f"\nIniciando scraping do perfil: {user}")
    print(f"Acessando URL: {user}")
    
    driver.get(user)
    time.sleep(3)
    
    profile_type = identify_profile_type(user)
    print(f"Tipo de perfil identificado: {profile_type}")
    
    try:
        total_views = 0
        
        if profile_type == 'videos':
            print("Processando perfil formato /videos")
            total_views = handle_videos_profile(driver, days)
        elif profile_type == 'reels':
            print("Processando perfil formato /reels")
            total_views = handle_reels_profile(driver, days)
        else:
            print("Tentando processar como perfil de reels...")
            total_views = handle_reels_profile(driver, days)
            
        print(f"Total de visualizações coletadas: {total_views}")
            
        with file_lock:
            with open(f"database/{concurso}/results/FacebookResults.txt", "a", encoding="utf-8") as file:
                file.write(f"{user} - Visualizações: {total_views}\n")
        
        return user, total_views

    except Exception as e:
        print(f"Erro ao processar usuário: {str(e)}")
        return user, 0

def scrape_users(driver, users, days, result_file, concurso):
    existing_results = {}
    with file_lock:
        try:
            with open(result_file, "r", encoding="utf-8") as file:
                for line in file:
                    if " - Facebook: " in line:
                        user, likes = line.split(" - Facebook: ")
                        existing_results[user.strip()] = int(likes.strip())
        except FileNotFoundError:
            pass

    new_results = {}
    for user in users:
        result = scrape_user(driver, user, days, concurso)
        if result:
            new_results[result[0]] = result[1]

    with file_lock:
        try:
            with open(result_file, "r", encoding="utf-8") as file:
                for line in file:
                    if " - Facebook: " in line:
                        user, likes = line.split(" - Facebook: ")
                        existing_results[user.strip()] = int(likes.strip())
        except FileNotFoundError:
            pass

        existing_results.update(new_results)

        results = [(user, likes) for user, likes in existing_results.items()]
        results.sort(key=lambda x: x[1], reverse=True)

        with open(result_file, "w", encoding="utf-8") as file:
            for user, likes in results:
                file.write(f"{user} - Facebook: {likes}\n")

def verificar_usuarios_com_zero_likes(driver, users, days, result_file, concurso):
    for user in users:
        try:
            scrape_user(driver, user, days, concurso)
        except Exception as e:
            print(f"Erro ao processar o perfil {user}: {e}")

def perguntar_gerar_resultado():
    resposta = input("Deseja gerar o resultado executando o arquivo ranking.py? (s/n): ")
    if resposta.lower() == 's':
        subprocess.run(["python", "ranking.py"])

def recheck_zero_likes(drivers, days, concurso):
    if not isinstance(drivers, list):
        drivers = [drivers]

    with open(f"database/{concurso}/results/FacebookResults.txt", "r") as file:
        lines = file.readlines()

    zero_like_users = [line.split(" - ")[0] for line in lines if " - Facebook: 0" in line]

    if not zero_like_users:
        print("Nenhum usuário com 0 curtidas encontrado.")
        return

    print("Usuários com 0 curtidas:")
    for user in zero_like_users:
        print(user)

    resposta = input("Deseja recheckar esses usuários? (s/n): ")
    if resposta.lower() == 's':
        num_instances = len(drivers)
        user_chunks = [zero_like_users[i::num_instances] for i in range(num_instances)]

        threads = []
        results = {}

        def recheck_user_chunk(driver, users_chunk, days, concurso):
            for user in users_chunk:
                try:
                    user, likes = scrape_user(driver, user, days, concurso)
                    results[user] = likes
                except Exception as e:
                    print(f"Erro ao processar o perfil {user}: {e}")

        for i in range(num_instances):
            thread = threading.Thread(target=recheck_user_chunk, args=(drivers[i], user_chunks[i], days, concurso))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        with open(f"database/{concurso}/results/FacebookResults.txt", "w", encoding="utf-8") as file:
            for line in lines:
                user = line.split(" - ")[0]
                if user in results:
                    file.write(f"{user} - Facebook: {results[user]}\n")
                else:
                    file.write(line)

def perguntar_acao_inicial():
    resposta = input("Deseja iniciar um novo check ou verificar os usuários com 0 curtidas? (novo/verificar): ")
    return resposta.lower()

def run_scrape(driver, users, days, result_file, concurso):
    scrape_users(driver, users, days, result_file, concurso)
    driver.quit()

def parse_date_input(date_str):
    today = datetime.now()
    
    try:
        days = int(date_str)
        target_date = today - timedelta(days=days)
        return target_date, days
    except ValueError:
        pass
    
    date_str = date_str.replace('/', '-')
    date_patterns = [
        ('%d-%m-%Y', True),  
        ('%d-%m', False)     
    ]
    
    for pattern, is_full in date_patterns:
        try:
            if not is_full:
                date_str = f"{date_str}-{today.year}"
            target_date = datetime.strptime(date_str, '%d-%m-%Y')
            
            if target_date > today:
                target_date = target_date.replace(year=target_date.year - 1)
                
            days = (today - target_date).days
            return target_date, days
        except ValueError:
            continue
    
    raise ValueError("Formato de data inválido. Use dias (ex: 28) ou data (ex: 08-09-2024, 08-09)")

def format_date_range(target_date):
    """Formata o período de busca de forma amigável"""
    today = datetime.now()
    days = (today - target_date).days
    
    def format_date(date):
        return date.strftime('%d/%m/%Y')
    
    range_str = (
        f"🔍 Período de busca:\n"
        f"• De: {format_date(target_date)}\n"
    )
    
    return range_str

def reset_facebook_results(concurso):
    with file_lock:
        with open(f"database/{concurso}/results/FacebookResults.txt", "w", encoding="utf-8") as file:
            file.write("")

def main():
    start_time = time.time()
    service = Service()

    concurso = input("Digite o nome do concurso: ")
    verificar_ou_criar_pastas(concurso)

    num_instances = int(input("Digite o número de instâncias do Chrome para iniciar: ")) 

    drivers = []
    max_retries = 3
    
    try:
        for _ in range(num_instances):
            retry_count = 0
            while retry_count < max_retries:
                try:
                    options = uc.ChromeOptions()
                    prefs = {
                        "profile.default_content_setting_values.notifications": 2,
                        "profile.default_content_setting_values.media_stream": 2,
                        "profile.default_content_setting_values.media_stream_mic": 2,
                        "profile.default_content_setting_values.media_stream_camera": 2,
                        "profile.default_content_setting_values.geolocation": 2,
                        "profile.default_content_setting_values.auto_play": 2
                    }
                    options.add_experimental_option("prefs", prefs)
                    options.add_argument("--disable-background-timer-throttling")
                    options.add_argument("--disable-backgrounding-occluded-windows")
                    options.add_argument("--disable-renderer-backgrounding")
                    options.add_argument("--window-size=1920,1080")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    
                    driver = uc.Chrome(service=service, options=options, headless=False)
                    drivers.append(driver)
                    break
                except Exception as e:
                    retry_count += 1
                    print(f"Tentativa {retry_count} de {max_retries} falhou: {str(e)}")
                    if retry_count == max_retries:
                        raise Exception(f"Falha ao iniciar Chrome após {max_retries} tentativas")
                    time.sleep(5)  # Espera 5 segundos antes de tentar novamente

        login_with_cookies(drivers[0], f"database/cookies/cookieFacebook.json")

        with open(f"database/{concurso}/users/usersFace.txt", "r", encoding="utf-8") as file:
            users = [line.strip() for line in file.readlines()]
        
        while True:
            try:
                date_input = input("Digite o período de busca (dias ou data): ")
                target_date, days = parse_date_input(date_input)
                print("\n" + format_date_range(target_date) + "\n")
                confirm = input("Confirmar período? (s/n): ").lower()
                if confirm == 's':
                    break
            except ValueError as e:
                print(f"Erro: {e}")

        acao_inicial = perguntar_acao_inicial()

        if acao_inicial == "verificar":
            recheck_zero_likes(drivers, days, concurso)
        else:
            reset_facebook_results(concurso)  # Reseta o arquivo de resultados
            user_chunks = [[] for _ in range(num_instances)]
            for i, user in enumerate(users):
                user_chunks[i % num_instances].append(user)

            threads = []
            for i in range(num_instances):
                thread = threading.Thread(
                    target=run_scrape,
                    args=(drivers[i], user_chunks[i], days, f"database/{concurso}/results/FacebookResults.txt", concurso)
                )
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            threads = []
            for i in range(num_instances):
                thread = threading.Thread(
                    target=verificar_usuarios_com_zero_likes,
                    args=(drivers[i], user_chunks[i], days, f"database/{concurso}/results/FacebookResults.txt", concurso)
                )
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

    except Exception as e:
        print(f"Erro durante a execução: {e}")
    finally:
        for driver in drivers:
            try:
                driver.quit()
            except:
                pass

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nTempo total de execução: {elapsed_time:.2f} segundos")
    input("\nPressione Enter para fechar o programa...")

if __name__ == "__main__":
    main()
