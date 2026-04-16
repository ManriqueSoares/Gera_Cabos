# Vamos mesclar dois Projetos

## 1. Codigo modelo:

arquivo: `GerarCabos.py`

parte que deve ser adicionado ao projeto atual:
```py
if st.sidebar.button("Executar Simulação", type="primary"):
    start_time = time.time()
    
    # --- BARRA DE PROGRESSO E STATUS ---
    progress_bar = st.progress(0)
    status_text = st.empty()
    logs = ["Limpando simulação antiga e iniciando..."]
    status_text.text("\n".join(logs))

    # --- CÁLCULOS INICIAIS ---
    area_rect_total = QTD_RECT * LARG_RECT * ALT_RECT
    r_redondo_total = DIAM_REDONDO_TOTAL / 2
    area_redondo_total = np.pi * r_redondo_total**2
    area_total_ocupada = area_rect_total + area_redondo_total

    nome_exibicao = escolha_luva

    # --- RESOLUÇÃO AUTOMÁTICA DE LUVA ---
    if escolha_luva == "Automático":
        logs.append("Fase 1: Selecionando Luva...")
        status_text.text("\n".join(logs))
        t_phase = time.time()
        opcoes_ordenadas = sorted([(k, v) for k, v in OPCOES_LUVA.items() if k != "Personalizado"], key=lambda x: x[1])
        encontrou_auto = False
        
        for nome, diam in opcoes_ordenadas:
            r_cand = diam / 2
            area_cand = np.pi * r_cand**2
            
            # 1. Validação de Área
            if area_total_ocupada / area_cand > LIMITE_OCUPACAO:
                continue
            
            # 2. Validação Física Rápida (Passo 0.1)
            if QTD_RECT == 0:
                DIAM_LUVA = diam
                nome_exibicao = nome
                encontrou_auto = True
                break
            
            grade_cand = gerar_grade_ordenada(r_cand, 0.1)
            encaixou_cand = False
            
            # Definição das estratégias baseada na paridade
            configs_auto = []
            if QTD_RECT % 2 == 0:
                # Para PARES: Tenta primeiro simetria estrita (gap central), depois simetria relaxada (preenche centro se necessário)
                configs_auto = [(0, "DuploX"), (0, "DuploY"), (1, "DuploX"), (1, "DuploY"), 
                                (0, "DuploX_Full"), (0, "DuploY_Full"), (1, "DuploX_Full"), (1, "DuploY_Full")]
            else:
                # Para ÍMPARES: Prioriza o Centro, mas permite estratégias duplas (assimétricas)
                configs_auto = [(0, "Centro"), (1, "Centro"), 
                                (0, "DuploX"), (0, "DuploY"), (1, "DuploX"), (1, "DuploY"),
                                (0, "DuploX_Full"), (0, "DuploY_Full"), (1, "DuploX_Full"), (1, "DuploY_Full")]
            
            for sentido, estrategia in configs_auto:
                w = LARG_RECT if sentido == 0 else ALT_RECT
                h = ALT_RECT if sentido == 0 else LARG_RECT
                
                if estrategia == "Centro":
                    grade_sorted = grade_cand
                    rects_temp = []
                    for _ in range(QTD_RECT):
                        for p in grade_sorted:
                            tx, ty = p[0] - w/2, p[1] - h/2
                            if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                rects_temp.append(Retangulo(tx, ty, w, h))
                                break
                elif estrategia == "DuploX": # Divide em X (Esquerda/Direita)
                    # Filtra pontos estritamente em cada lado para garantir o gap central
                    mask_L = grade_cand[:,0] <= -w/2 + 1e-5
                    mask_R = grade_cand[:,0] >= w/2 - 1e-5
                    
                    d_L = (grade_cand[mask_L][:,0] + w/2)**2 + grade_cand[mask_L][:,1]**2
                    d_R = (grade_cand[mask_R][:,0] - w/2)**2 + grade_cand[mask_R][:,1]**2
                    
                    g_L = grade_cand[mask_L][np.argsort(d_L)]
                    g_R = grade_cand[mask_R][np.argsort(d_R)]
                    
                    rects_temp = []
                    idx_L, idx_R = 0, 0
                    # Alterna estritamente: Esq, Dir, Esq, Dir...
                    for i in range(QTD_RECT):
                        placed = False
                        if i % 2 == 0: # Tenta Esquerda
                            while idx_L < len(g_L):
                                p = g_L[idx_L]; idx_L += 1
                                tx, ty = p[0] - w/2, p[1] - h/2
                                if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                    rects_temp.append(Retangulo(tx, ty, w, h))
                                    placed = True; break
                        else: # Tenta Direita
                            while idx_R < len(g_R):
                                p = g_R[idx_R]; idx_R += 1
                                tx, ty = p[0] - w/2, p[1] - h/2
                                if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                    rects_temp.append(Retangulo(tx, ty, w, h))
                                    placed = True; break
                        if not placed: break

                elif estrategia == "DuploX_Full": # Divide em X mas permite preencher o centro (sem mask)
                    d2 = np.minimum((grade_cand[:,0] + w/2)**2 + grade_cand[:,1]**2, (grade_cand[:,0] - w/2)**2 + grade_cand[:,1]**2)
                    grade_sorted = grade_cand[np.argsort(d2)]
                    rects_temp = []
                    for _ in range(QTD_RECT):
                        for p in grade_sorted:
                            tx, ty = p[0] - w/2, p[1] - h/2
                            if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                rects_temp.append(Retangulo(tx, ty, w, h))
                                break
                elif estrategia == "DuploY_Full": # Divide em Y mas permite preencher o centro (sem mask)
                    d2 = np.minimum(grade_cand[:,0]**2 + (grade_cand[:,1] - h/2)**2, grade_cand[:,0]**2 + (grade_cand[:,1] + h/2)**2)
                    grade_sorted = grade_cand[np.argsort(d2)]
                    rects_temp = []
                    for _ in range(QTD_RECT):
                        for p in grade_sorted:
                            tx, ty = p[0] - w/2, p[1] - h/2
                            if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                rects_temp.append(Retangulo(tx, ty, w, h))
                                break

                elif estrategia == "DuploY": # Divide em Y (Cima/Baixo)
                    mask_T = grade_cand[:,1] >= h/2 - 1e-5
                    mask_B = grade_cand[:,1] <= -h/2 + 1e-5
                    
                    d_T = grade_cand[mask_T][:,0]**2 + (grade_cand[mask_T][:,1] - h/2)**2
                    d_B = grade_cand[mask_B][:,0]**2 + (grade_cand[mask_B][:,1] + h/2)**2
                    
                    g_T = grade_cand[mask_T][np.argsort(d_T)]
                    g_B = grade_cand[mask_B][np.argsort(d_B)]
                    
                    rects_temp = []
                    idx_T, idx_B = 0, 0
                    for i in range(QTD_RECT):
                        placed = False
                        if i % 2 == 0: # Tenta Cima
                            while idx_T < len(g_T):
                                p = g_T[idx_T]; idx_T += 1
                                tx, ty = p[0] - w/2, p[1] - h/2
                                if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                    rects_temp.append(Retangulo(tx, ty, w, h))
                                    placed = True; break
                        else: # Tenta Baixo
                            while idx_B < len(g_B):
                                p = g_B[idx_B]; idx_B += 1
                                tx, ty = p[0] - w/2, p[1] - h/2
                                if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                    rects_temp.append(Retangulo(tx, ty, w, h))
                                    placed = True; break
                        if not placed: break

                if len(rects_temp) == QTD_RECT:
                    encaixou_cand = True
                    break
            
            if encaixou_cand:
                DIAM_LUVA = diam
                nome_exibicao = nome
                encontrou_auto = True
                break
        
        if not encontrou_auto:
            nome_exibicao = opcoes_ordenadas[-1][0]
            DIAM_LUVA = opcoes_ordenadas[-1][1]
            st.warning(f"Automático: Nenhuma luva padrão atende aos critérios. Usando a maior disponível ({nome_exibicao}).")
        else:
            st.success(f"Automático: Luva selecionada **{nome_exibicao}** ({DIAM_LUVA} mm)")
        logs[-1] += f" ({time.time() - t_phase:.2f}s)"
        status_text.text("\n".join(logs))

    progress_bar.progress(33)
    r_luva = DIAM_LUVA / 2
    area_luva = np.pi * r_luva**2
    r_micro = DIAM_MICRO_FIO / 2
    area_micro = np.pi * r_micro**2
    
    qtd_micro_fios = 0
    if area_redondo_total > 0 and area_micro > 0:
        # Utiliza a área total do envelope, ajustada pelo limite geométrico de empacotamento (aprox 90%)
        # para evitar solicitar uma quantidade fisicamente impossível (100% sólido).
        qtd_micro_fios = int((area_redondo_total * 0.90) / area_micro)
        
    taxa = area_total_ocupada / area_luva

    if area_total_ocupada > area_luva:
        st.error("ERRO FATAL: A área dos cabos é maior que a área da luva! Impossível calcular.")
        st.stop()

    if taxa > LIMITE_OCUPACAO:
        st.warning(f"ALERTA: Taxa de ocupação acima do limite configurado ({LIMITE_OCUPACAO*100:.0f}%)")

    # --- FASE 1: RETÂNGULOS ---
    logs.append("Fase 2: Posicionando Fio Retangular...")
    status_text.text("\n".join(logs))
    t_phase = time.time()
    grade_rect = gerar_grade_ordenada(r_luva, 0.05)
    
    melhor_rects = []
    melhor_score = -1
    orientacao_final = ""
    
    # Definição das estratégias para Fase 2
    configs = []
    if QTD_RECT % 2 == 0:
        # Pares: Prioriza simetria estrita, mas tenta relaxada se couber mais
        configs = [(0, "DuploX"), (0, "DuploY"), (1, "DuploX"), (1, "DuploY"), (0, "DuploX_Full"), (0, "DuploY_Full"), (1, "DuploX_Full"), (1, "DuploY_Full")]
    else:
        # Ímpares: Centro + Simétricas + Full (permite assimetria para melhor encaixe)
        configs = [(0, "Centro"), (1, "Centro"), 
                   (0, "DuploX"), (0, "DuploY"), (1, "DuploX"), (1, "DuploY"),
                   (0, "DuploX_Full"), (0, "DuploY_Full"), (1, "DuploX_Full"), (1, "DuploY_Full")]

    for sentido, estrategia in configs:
        w = LARG_RECT if sentido == 0 else ALT_RECT
        h = ALT_RECT if sentido == 0 else LARG_RECT
        
        # Ordena a grade de pontos baseada na estratégia
        if estrategia == "Centro":
            grade_sorted = grade_rect
            rects_temp = []
            for _ in range(QTD_RECT):
                for p in grade_sorted:
                    tx, ty = p[0] - w/2, p[1] - h/2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        break
        elif estrategia == "DuploX":
            mask_L = grade_rect[:,0] <= -w/2 + 1e-5
            mask_R = grade_rect[:,0] >= w/2 - 1e-5
            
            d_L = (grade_rect[mask_L][:,0] + w/2)**2 + grade_rect[mask_L][:,1]**2
            d_R = (grade_rect[mask_R][:,0] - w/2)**2 + grade_rect[mask_R][:,1]**2
            
            g_L = grade_rect[mask_L][np.argsort(d_L)]
            g_R = grade_rect[mask_R][np.argsort(d_R)]
            
            rects_temp = []
            idx_L, idx_R = 0, 0
            for i in range(QTD_RECT):
                placed = False
                if i % 2 == 0: # Tenta Esquerda
                    while idx_L < len(g_L):
                        p = g_L[idx_L]; idx_L += 1
                        tx, ty = p[0] - w/2, p[1] - h/2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h))
                            placed = True; break
                else: # Tenta Direita
                    while idx_R < len(g_R):
                        p = g_R[idx_R]; idx_R += 1
                        tx, ty = p[0] - w/2, p[1] - h/2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h))
                            placed = True; break
                if not placed: break

        elif estrategia == "DuploX_Full":
            d2 = np.minimum((grade_rect[:,0] + w/2)**2 + grade_rect[:,1]**2, (grade_rect[:,0] - w/2)**2 + grade_rect[:,1]**2)
            grade_sorted = grade_rect[np.argsort(d2)]
            rects_temp = []
            for _ in range(QTD_RECT):
                for p in grade_sorted:
                    tx, ty = p[0] - w/2, p[1] - h/2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        break
        elif estrategia == "DuploY_Full":
            d2 = np.minimum(grade_rect[:,0]**2 + (grade_rect[:,1] - h/2)**2, grade_rect[:,0]**2 + (grade_rect[:,1] + h/2)**2)
            grade_sorted = grade_rect[np.argsort(d2)]
            rects_temp = []
            for _ in range(QTD_RECT):
                for p in grade_sorted:
                    tx, ty = p[0] - w/2, p[1] - h/2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        break

        elif estrategia == "DuploY":
            mask_T = grade_rect[:,1] >= h/2 - 1e-5
            mask_B = grade_rect[:,1] <= -h/2 + 1e-5
            
            d_T = grade_rect[mask_T][:,0]**2 + (grade_rect[mask_T][:,1] - h/2)**2
            d_B = grade_rect[mask_B][:,0]**2 + (grade_rect[mask_B][:,1] + h/2)**2
            
            g_T = grade_rect[mask_T][np.argsort(d_T)]
            g_B = grade_rect[mask_B][np.argsort(d_B)]
            
            rects_temp = []
            idx_T, idx_B = 0, 0
            for i in range(QTD_RECT):
                placed = False
                if i % 2 == 0: # Tenta Cima
                    while idx_T < len(g_T):
                        p = g_T[idx_T]; idx_T += 1
                        tx, ty = p[0] - w/2, p[1] - h/2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h))
                            placed = True; break
                else: # Tenta Baixo
                    while idx_B < len(g_B):
                        p = g_B[idx_B]; idx_B += 1
                        tx, ty = p[0] - w/2, p[1] - h/2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h))
                            placed = True; break
                if not placed: break
        
        if len(rects_temp) > melhor_score:
            melhor_score = len(rects_temp)
            melhor_rects = rects_temp
            orientacao_final = "Horizontal" if sentido == 0 else "Vertical"
            if "Duplo" in estrategia:
                orientacao_final += " (Simétrico)"
    
    logs[-1] += f" ({time.time() - t_phase:.2f}s)"
    status_text.text("\n".join(logs))
    
    progress_bar.progress(66)

    # --- FASE 2: CABO FLEXÍVEL ---
    micro_fios = []
    if not excluir_circular:
        logs.append("Fase 3: Posicionando Cabo Circular...")
        status_text.text("\n".join(logs))
        t_phase = time.time()
        fios_restantes = qtd_micro_fios
        grade_fios = gerar_grade_ordenada(r_luva, DIAM_MICRO_FIO * 0.2)

        for p in grade_fios:
            if fios_restantes <= 0: break
            cx, cy = p[0], p[1]
            if ponto_livre(cx, cy, r_micro, r_luva, melhor_rects, micro_fios):
                micro_fios.append(Circulo(cx, cy, r_micro))
                fios_restantes -= 1
        
        logs[-1] += f" ({time.time() - t_phase:.2f}s)"
        status_text.text("\n".join(logs))
    
    progress_bar.progress(100)
    area_real_fios = len(micro_fios) * area_micro

    end_time = time.time()
    elapsed_time = end_time - start_time
    logs.append(f"Simulação Concluída! ({elapsed_time:.1f}s)")
    status_text.text("\n".join(logs))

    # --- CÁLCULO REAL PÓS-SIMULAÇÃO ---
    # A área total ocupada é a soma da área dos retângulos que couberam
    # mais a área dos micro-fios que couberam, para refletir a realidade visual.
    area_rect_real = len(melhor_rects) * LARG_RECT * ALT_RECT
    area_total_ocupada_real = area_rect_real + area_real_fios
    taxa_real = area_total_ocupada_real / area_luva if area_luva > 0 else 0
    
    # --- Armazena todos os resultados em session_state ---
    st.session_state.simulation_results = {
        "area_rect_total": area_rect_total, "area_redondo_total": area_redondo_total, # Áreas teóricas para referência
        "area_luva": area_luva, "DIAM_LUVA": DIAM_LUVA, "LARG_RECT": LARG_RECT,
        "ALT_RECT": ALT_RECT, "QTD_RECT": QTD_RECT, "excluir_circular": excluir_circular,
        "melhor_rects": melhor_rects, "micro_fios": micro_fios, "taxa": taxa_real,
        "LIMITE_OCUPACAO": LIMITE_OCUPACAO, "area_total_ocupada": area_total_ocupada_real,
        "orientacao_final": orientacao_final, "qtd_micro_fios": qtd_micro_fios,
        "nome_exibicao": nome_exibicao, "elapsed_time": elapsed_time, "logs": logs,
        "cabo_selecionado": escolha_cabo if not excluir_circular else "N/A", "DIAM_MICRO_FIO": DIAM_MICRO_FIO
    }
    st.rerun()

# --- Bloco de Renderização (executado sempre que há resultados) ---
if st.session_state.simulation_results:
    st.progress(100)
    res = st.session_state.simulation_results

    # --- RENDERIZAÇÃO DOS RESULTADOS ---
    col_dados, col_desenho = st.columns([1.2, 1])

    with col_dados:
        st.markdown("#### Dados das Seções")
        if not res["excluir_circular"]:
            c1, c2, c3 = st.columns(3)
            c1.metric("Fio Retangular", f"{res['area_rect_total']:.2f} mm²", help=f"Unitário: {res['LARG_RECT']}x{res['ALT_RECT']} mm | Qtd: {res['QTD_RECT']}")
            c2.metric("Cabo Circular", f"{res['area_redondo_total']:.2f} mm²")
            c3.metric("Luva", f"{res['area_luva']:.2f} mm²", help=f"Diâmetro: {res['DIAM_LUVA']} mm")
        else:
            c1, c2 = st.columns(2)
            c1.metric("Fio Retangular", f"{res['area_rect_total']:.2f} mm²", help=f"Unitário: {res['LARG_RECT']}x{res['ALT_RECT']} mm | Qtd: {res['QTD_RECT']}")
            c2.metric("Luva", f"{res['area_luva']:.2f} mm²", help=f"Diâmetro: {res['DIAM_LUVA']} mm")

        st.markdown("---")
        st.markdown("#### Indicadores")
        
        i1, i2, i3 = st.columns(3)
        delta_rect = len(res["melhor_rects"]) - res["QTD_RECT"]
        i1.metric("Fios", f"{len(res['melhor_rects'])} / {res['QTD_RECT']}", delta=int(delta_rect) if delta_rect < 0 else None)

        delta_taxa = (res["taxa"] - res["LIMITE_OCUPACAO"]) * 100
        i2.metric("Ocupação", f"{res['taxa']*100:.1f}%", delta=f"{delta_taxa:.1f}%", delta_color="inverse")
        
        i3.metric("Área Total", f"{res['area_total_ocupada']:.2f} mm²")

    with col_desenho:
        # --- VISUALIZAÇÃO ---
        fig, ax = plt.subplots(figsize=(2.5, 2.5))
        r_luva = res["DIAM_LUVA"] / 2
        
        # Desenhos
        ax.add_patch(patches.Circle((0,0), r_luva, color='#F0F0F0', zorder=0))
        ax.add_patch(patches.Circle((0,0), r_luva, fill=False, color='black', lw=0.75, zorder=10))
        
        for r in res["melhor_rects"]:
            
            ax.add_patch(patches.Rectangle((r.x, r.y), r.w, r.h, ec='black', fc='#4169E1', zorder=5, lw=0.5))

        for c in res["micro_fios"]:
            ax.add_patch(patches.Circle((c.cx, c.cy), c.r, color='#FF8C00', zorder=4))

        # Adiciona a cruz vermelha no centro
        ax.axhline(0, color='red', linewidth=0.6, linestyle='--', zorder=11)
        ax.axvline(0, color='red', linewidth=0.6, linestyle='--', zorder=11)

        ax.set_xlim(-r_luva*1.1, r_luva*1.1)
        ax.set_ylim(-r_luva*1.1, r_luva*1.1)
        ax.set_aspect('equal')
        
        # Configuração dos eixos e grade
        max_tick = int(np.ceil(res["DIAM_LUVA"]))
        max_tick = ((max_tick + 4) // 5) * 5
        
        # Labels de 0 até o diâmetro
        tick_labels = np.arange(0, max_tick + 1, 5)
        # Posições no gráfico (deslocadas pelo raio, pois o centro é 0,0)
        tick_positions = tick_labels - r_luva
        
        ax.set_xticks(tick_positions)
        ax.set_yticks(tick_positions)
        ax.set_xticklabels(tick_labels)
        ax.set_yticklabels(tick_labels)
        
        ax.tick_params(axis='both', which='major', labelsize=4) # Fonte bem pequena
        ax.set_xlabel("Radial", fontsize=4)
        ax.set_ylabel("Axial", fontsize=4)
        ax.grid(True, linestyle=':', linewidth=0.4, color='grey')

        ax.set_title(f"Luva {res['nome_exibicao']} - Diâmetro {res['DIAM_LUVA']} mm", fontsize=8)

        # Salva imagem temporária para o relatório PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, format='png', dpi=300, bbox_inches='tight')
            tmp_img_path = tmpfile.name

        st.pyplot(fig, use_container_width=False)
        plt.close(fig) # Libera memória da figura

    # Resultados Finais em Texto
    # Define as condições de falha/sucesso
    falha_retangulos = len(res["melhor_rects"]) < res["QTD_RECT"]
    falha_ocupacao = res["taxa"] > res["LIMITE_OCUPACAO"]
    
    falha_circular = False
    if not res["excluir_circular"] and res["qtd_micro_fios"] > 0:
        if len(res["micro_fios"]) < res["qtd_micro_fios"]:
            falha_circular = True

    simulacao_aprovada = not (falha_retangulos or falha_ocupacao or falha_circular)

    if simulacao_aprovada:
        mensagem = f"Simulação Aprovada! Orientação: {res['orientacao_final']} | Retangular: {len(res['melhor_rects'])}/{res['QTD_RECT']}"
        if not res["excluir_circular"]:
            percentual_circular = 0
            if res["qtd_micro_fios"] > 0:
                percentual_circular = (len(res["micro_fios"]) / res["qtd_micro_fios"]) * 100
            mensagem += f" | Circular: {percentual_circular:.0f}%"
        st.success(f"{mensagem} | Tempo: {res['elapsed_time']:.2f}s")
    else:
        motivos = []
        if falha_retangulos:
            motivos.append(f"Fios: {len(res['melhor_rects'])}/{res['QTD_RECT']}")
        if falha_circular:
            percentual = (len(res["micro_fios"]) / res["qtd_micro_fios"]) * 100
            motivos.append(f"Circular: {len(res['micro_fios'])}/{res['qtd_micro_fios']} ({percentual:.0f}%)")
        if falha_ocupacao:
            motivos.append(f"Ocupação: {res['taxa']*100:.1f}% (Limite: {res['LIMITE_OCUPACAO']*100:.0f}%)")
        
        st.error(f"Simulação Reprovada! Motivo(s): {', '.join(motivos)} | Tempo: {res['elapsed_time']:.2f}s")

    st.markdown("#### Logs da Simulação")
    st.text("\n".join(res["logs"]))
```

## 2. Projeto:

Código da interface: `app\layout\pages\home.py`

Neste código de interface eu quero que o botão `ELEVATE_BUTTON_EXECUTAR_SIMULACAO` inicie a simulação.


## Pontos Importantes:

1. Deve ser gerado um código novo que quando o botão é clicado chama este botão. Este código deve ser adicionado no caminho `app\services` com o nome de simulacao.py

2. A imagem do matplotlib não precisa ser adicionado na interface, mas deve ser salva no diretório `assets` com o nome de simulacao.png

