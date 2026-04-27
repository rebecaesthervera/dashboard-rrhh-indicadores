with tab2:
        st.subheader("🎂 Celebraciones del Mes")
        
        # Intentamos obtener la fecha de ingreso para calcular antigüedad
        # Si no existe en la hoja de cumpleaños, intentamos cruzar datos con la hoja principal
        if not df_cump.empty:
            # 1. Preparar datos
            df_cump['FECHA_NAC'] = pd.to_datetime(df_cump[col_fecha], errors='coerce', dayfirst=True)
            mes_actual = datetime.now().month
            hoy = datetime.now()
            
            # Filtro de los que cumplen este mes
            cumples_mes = df_cump[df_cump['FECHA_NAC'].dt.month == mes_actual].copy()
            
            if not cumples_mes.empty:
                cumples_mes['DIA'] = cumples_mes['FECHA_NAC'].dt.day
                cumples_mes = cumples_mes.sort_values('DIA')
                
                # 2. Diseño de Tarjetas
                cols_c = st.columns(3) # 3 tarjetas por fila
                
                for i, row in cumples_mes.reset_index().iterrows():
                    with cols_c[i % 3]:
                        with st.container(border=True):
                            # Encabezado: Día y Nombre
                            st.markdown(f"### 📅 Día {int(row['DIA'])}")
                            st.markdown(f"**{row['APELLIDO Y NOMBRE']}**")
                            
                            # 3. Lógica de Antigüedad
                            # Buscamos la fecha de ingreso en el archivo principal (df_main) usando el nombre
                            ingreso = None
                            if 'APELLIDO Y NOMBRE' in df_main.columns and 'FECHA INGRESO' in df_main.columns:
                                match = df_main[df_main['APELLIDO Y NOMBRE'] == row['APELLIDO Y NOMBRE']]
                                if not match.empty:
                                    ingreso = pd.to_datetime(match['FECHA INGRESO'].values[0], errors='coerce')

                            if ingreso and not pd.isnull(ingreso):
                                anos = hoy.year - ingreso.year - ((hoy.month, hoy.day) < (ingreso.month, ingreso.day))
                                st.markdown(f"⭐ **Trayectoria:** {max(0, anos)} años")
                                
                                # Etiquetas de reconocimiento
                                if anos >= 10:
                                    st.success("🏆 Personal Histórico")
                                elif anos >= 5:
                                    st.info("🎖️ Trayectoria Consolidada")
                                elif anos == 0:
                                    st.caption("🌱 ¡Su primer año!")
                            
                            st.divider()
                            st.button("Felicitar ✨", key=f"hb_{i}", use_container_width=True)
            else:
                st.info("No hay cumpleaños registrados para este mes.")
