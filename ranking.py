import pandas as pd
import subprocess
import webbrowser
import random
from difflib import get_close_matches
import os

def calcular_premiacao(views, posicao):
    premios = [1200, 900, 500, 300, 300, 200, 200, 200, 100, 100]
    bonus = 300 if views >= 3000000 else 200 if views >= 2000000 else 100 if views >= 1000000 else 0
    return premios[posicao - 1] + bonus

def get_available_contests():
    contests = []
    ignore_dirs = {'cookies', 'logs'}
    
    try:
        for item in os.listdir('database'):
            if os.path.isdir(os.path.join('database', item)) and item not in ignore_dirs:
                contests.append(item)
    except Exception as e:
        print(f"Erro ao listar concursos: {str(e)}")
        return []
    
    return sorted(contests)

def select_contest():
    contests = get_available_contests()
    if not contests:
        print("Nenhum concurso encontrado na pasta database!")
        return None
    
    print("\nConcursos disponíveis:")
    for i, contest in enumerate(contests, 1):
        print(f"{i}. {contest}")
    
    while True:
        try:
            choice = int(input("\nSelecione o número do concurso: "))
            if 1 <= choice <= len(contests):
                selected = contests[choice - 1]
                if not os.path.exists(os.path.join('database', selected, 'results')):
                    print(f"Erro: Pasta 'results' não encontrada para o concurso {selected}")
                    return None
                return selected
            print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")

def generate_html(ranking, full_ranking, contest_name):
    html_filename = f"ranking_{contest_name}.html"
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ranking de Views</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            body { 
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f7fa;
                color: #2d3748;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: transparent;
            }
            header {
                background: #fff;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.04);
                margin-bottom: 30px;
                text-align: center;
            }
            header h1 {
                margin: 0;
                font-size: 28px;
                font-weight: 600;
                color: #1a202c;
            }
            .ranking {
                background: #fff;
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            }
            .ranking h2 {
                color: #2d3748;
                font-size: 24px;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #edf2f7;
            }
            .ranking ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            .ranking li {
                padding: 16px 24px;
                margin-bottom: 12px;
                background: #f8fafc;
                border-radius: 8px;
                display: grid;
                grid-template-columns: 1fr 1fr 1fr; /* Distribuição igual das colunas */
                align-items: center;
                gap: 20px;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .ranking li:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }
            .ranking li .user {
                flex: 2;
                font-weight: 500;
                color: #2d3748;
            }
            .ranking li .views {
                flex: 1;
                text-align: center;
                color: #4a5568;
                justify-self: center;
            }
            .ranking li .premiacao {
                flex: 1;
                text-align: right;
                color: #38a169;
                font-weight: 600;
                justify-self: end;
            }
            .toggle-button {
                background: #3182ce;
                color: #fff;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 15px;
                font-weight: 500;
                transition: background 0.2s ease;
                display: block;
                margin: 20px auto;
            }
            .toggle-button:hover {
                background: #2c5282;
            }
            @media (max-width: 768px) {
                body {
                    padding: 10px;
                }
                .container {
                    padding: 0;
                }
                .ranking {
                    padding: 15px;
                }
                .ranking li {
                    grid-template-columns: 1fr;
                    padding: 16px;
                    gap: 8px;
                }
                .user-info {
                    justify-content: center;
                    margin-bottom: 8px;
                }
                .position {
                    margin-right: 10px;
                }
                .user {
                    font-size: 16px;
                }
                .views {
                    grid-column: 1;
                    font-size: 15px;
                    margin: 4px 0;
                }
                .premiacao {
                    grid-column: 1;
                    text-align: center;
                    justify-self: center;
                    font-size: 15px;
                }
                header {
                    padding: 20px;
                    margin-bottom: 15px;
                }
                header h1 {
                    font-size: 20px;
                }
                .ranking h2 {
                    font-size: 18px;
                    margin-bottom: 15px;
                }
                .toggle-button {
                    width: 100%;
                    max-width: 280px;
                    margin: 15px auto;
                    font-size: 14px;
                    padding: 10px;
                }
            }
            .position {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                background: #edf2f7;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 15px;
                font-weight: 600;
                color: #4a5568;
            }
            .top-3 {
                background: linear-gradient(45deg, #4299e1, #3182ce);
                color: white;
            }
            .user-info {
                grid-column: 1;
                display: flex;
                align-items: center;
            }
            .stats {
                display: grid;
                grid-template-columns: 1fr 1fr;
                align-items: center;
                gap: 20px;
                grid-column: 2 / span 2;
            }
            .views {
                grid-column: 2;
                text-align: center;
                color: #4a5568;
                justify-self: center;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .premiacao {
                grid-column: 3;
                text-align: right;
                color: #38a169;
                font-weight: 600;
                justify-self: end;
            }
            @media (max-width: 768px) {
                .ranking li {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 16px;
                    gap: 8px;
                }
                .user-info {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                }
                .stats {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    width: 100%;
                    gap: 8px;
                }
                .views, 
                .premiacao {
                    width: 100%;
                    text-align: center;
                }
            }
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const button = document.getElementById('toggleButton');
                const top10 = document.getElementById('top10');
                const fullRanking = document.getElementById('fullRanking');
                
                button.addEventListener('click', function() {
                    const isTop10Visible = top10.style.display !== 'none';
                    
                    requestAnimationFrame(() => {
                        top10.style.display = isTop10Visible ? 'none' : 'block';
                        fullRanking.style.display = isTop10Visible ? 'block' : 'none';
                        button.textContent = isTop10Visible ? 'Ver Top 10' : 'Ver Todos os Competidores';
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    });
                });
            });
        </script>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Ranking de Visualizações</h1>
            </header>
            <div id="top10" class="ranking">
                <h2>Top 10 Competidores</h2>
                <ul>
    """
    
    for i, (user, views_dict) in enumerate(ranking):
        total_views = sum(views_dict.values())
        formatted_views = f"{total_views:,}".replace(",", ".")
        premiacao = calcular_premiacao(total_views, i + 1)
        position_class = "top-3" if i < 3 else ""
        html_content += f"""
            <li>
                <div class="user-info">
                    <div class="position {position_class}">{i + 1}</div>
                    <span class="user">{user}</span>
                </div>
                <span class="views">{formatted_views} views</span>
                <span class="premiacao">R$ {premiacao},00</span>
            </li>
        """

    html_content += """
                </ul>
            </div>
            <div id="fullRanking" class="ranking" style="display: none;">
                <h2>Todos os Competidores</h2>
                <ul>
    """
    
    for i, (user, views_dict) in enumerate(full_ranking):
        total_views = sum(views_dict.values())
        formatted_views = f"{total_views:,}".replace(",", ".")
        html_content += f"""
            <li>
                <div class="user-info">
                    <div class="position">{i + 1}</div>
                    <span class="user">{user}</span>
                </div>
                <span class="views">{formatted_views} views</span>
            </li>
        """

    html_content += """
                </ul>
            </div>
            <button id="toggleButton" class="toggle-button">Ver Todos os Competidores</button>
        </div>
    </body>
    </html>
    """
    with open(html_filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    return html_filename

def clean_result_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors='ignore') as file:
        lines = file.readlines()
    
    lines = [line for line in lines if line.strip()]
    
    with open(filepath, "w", encoding="utf-8", errors='ignore') as file:
        file.writelines(lines)

def read_results(filepath):
    with open(filepath, "r", encoding="utf-8", errors='ignore') as file:
        lines = file.readlines()
    
    results = [(line.split(" - ")[0].strip(), int(line.split(": ")[1].strip())) for line in lines if " - " in line and ": " in line]
    return sorted(results, key=lambda x: x[1], reverse=True)

def combine_results(tiktok_results, shorts_results):
    combined_results = {}
    
    for user, views in tiktok_results:
        combined_results[user] = combined_results.get(user, 0) + views
    
    for user, views in shorts_results:
        matches = get_close_matches(user, combined_results.keys(), n=1, cutoff=0.8)
        if matches:
            combined_results[matches[0]] += views
        else:
            combined_results[user] = views
    
    return list(combined_results.items())

def add_missing_users(combined_results, all_users):
    processed_users = {user for user, _ in combined_results}
    for user in all_users:
        if not get_close_matches(user, processed_users, n=1, cutoff=0.8):
            combined_results.append((user, 0))

def sort_results_file(filepath, platform):
    with open(filepath, "r", encoding="utf-8", errors='ignore') as file:
        lines = file.readlines()
    
    results = [(line.split(f" - {platform}: ")[0].strip(), int(line.split(f" - {platform}: ")[1].strip())) for line in lines if f" - {platform}: " in line]
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    
    with open(filepath, "w", encoding="utf-8", errors='ignore') as file:
        for user, views in sorted_results:
            file.write(f"{user} - {platform}: {views}\n")

def generate_excel(ranking, contest_name, platforms):
    filepath = f"ranking_{contest_name}.xlsx"
    try:
        users = [user for user, _ in ranking]
        data = {'Perfis': users}
        
        for platform in platforms:
            data[platform] = [0] * len(users)
        
        for user, views in ranking:
            for platform in platforms:
                if platform in views:
                    matches = get_close_matches(user, data['Perfis'], n=1, cutoff=0.8)
                    if matches:
                        data[platform][data['Perfis'].index(matches[0])] = views[platform]
                    else:
                        data[platform][users.index(user)] = views[platform]
        
        df = pd.DataFrame(data)
        platforms_list = list(platforms)
        df['Total'] = df[platforms_list].sum(axis=1)
        df = df.sort_values(by='Total', ascending=False).drop(columns=['Total'])
        
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            workbook  = writer.book
            worksheet = writer.sheets['Sheet1']
            
            center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
            number_format = workbook.add_format({'num_format': '#,##0', 'align': 'center', 'valign': 'vcenter'})
            header_format = workbook.add_format({'bold': True, 'bg_color': '#4dd0e1', 'align': 'center', 'valign': 'vcenter'})
            color1_format = workbook.add_format({'bg_color': '#FFFFFF', 'align': 'center', 'valign': 'vcenter'})
            color2_format = workbook.add_format({'bg_color': '#e0f7fa', 'align': 'center', 'valign': 'vcenter'})
            
            worksheet.set_column('A:A', 30, center_format)
            worksheet.set_column('B:B', 30, number_format)
            worksheet.set_column('C:C', 30, number_format)
            worksheet.set_column('D:D', 30, number_format)
            worksheet.set_column('E:E', 30, number_format)
            worksheet.set_column('F:F', 30, number_format)
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            for row_num in range(1, len(df) + 1):
                format_to_use = color1_format if row_num % 2 == 0 else color2_format
                for col_num in range(len(df.columns)):
                    if col_num == 0:
                        worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], format_to_use)
                    else:
                        worksheet.write_number(row_num, col_num, int(df.iloc[row_num - 1, col_num]), format_to_use)
    except PermissionError:
        print(f"Erro: Permissão negada ao tentar escrever no arquivo {filepath}. Feche o arquivo se ele estiver aberto e tente novamente.")

def generate_ranking(contest_name):
    result_files = [f for f in os.listdir(f"database/{contest_name}/results") if f.endswith(".txt")]
    
    combined_results = {}
    platforms = set()
    for result_file in result_files:
        platform = result_file.split("Results")[0]
        platforms.add(platform)
        platform_results = read_results(os.path.join(f"database/{contest_name}/results", result_file))
        platform_results = sorted(platform_results, key=lambda x: x[1], reverse=True)
        for user, views in platform_results:
            matches = get_close_matches(user, combined_results.keys(), n=1, cutoff=0.8)
            if matches:
                combined_results[matches[0]][platform] = combined_results[matches[0]].get(platform, 0) + views
            else:
                if user not in combined_results:
                    combined_results[user] = {}
                combined_results[user][platform] = views
    
    with open(f"database/{contest_name}/users/usersYt.txt", "r") as file:
        yt_users = [line.strip() for line in file.readlines()]
    with open(f"database/{contest_name}/users/usersTtk.txt", "r") as file:
        ttk_users = [line.strip() for line in file.readlines()]
    with open(f"database/{contest_name}/users/usersIg.txt", "r") as file:
        ig_users = [line.strip() for line in file.readlines()]
    
    all_users = set(yt_users + ttk_users + ig_users)
    add_missing_users(list(combined_results.items()), all_users)
    
    full_ranking = sorted(combined_results.items(), key=lambda x: sum(x[1].values()), reverse=True)
    top_10_ranking = full_ranking[:10]
    
    html_filename = generate_html(top_10_ranking, full_ranking, contest_name)
    generate_excel(full_ranking, contest_name, platforms)
    return html_filename

def sort_platform_results(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors='ignore') as file:
            lines = file.readlines()
        
        platform = os.path.basename(filepath).split("Results")[0]
        results = []
        
        for line in lines:
            if " - " in line and ": " in line:
                user = line.split(" - ")[0].strip()
                try:
                    views = int(line.split(": ")[1].strip())
                except ValueError:
                    views = 0
                results.append((user, views))
        
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        
        with open(filepath, "w", encoding="utf-8", errors='ignore') as file:
            for user, views in sorted_results:
                file.write(f"{user} - {platform}: {views}\n")
                
    except Exception as e:
        print(f"Erro ao ordenar {filepath}: {str(e)}")

def main():
    contest_name = select_contest()
    if not contest_name:
        return
    
    results_dir = os.path.join("database", contest_name, "results")

    try:
        result_files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if f.endswith(".txt")]
        
        if not result_files:
            print(f"Nenhum arquivo .txt encontrado em: {results_dir}")
            return
            
        for file_path in result_files:
            print(f"Processando arquivo: {file_path}")
            sort_platform_results(file_path)
        
        html_filename = generate_ranking(contest_name)
        webbrowser.open(html_filename)
        
    except Exception as e:
        print(f"Erro ao processar o concurso: {str(e)}")

if __name__ == "__main__":
    main()