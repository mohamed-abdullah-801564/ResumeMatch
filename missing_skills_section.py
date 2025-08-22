                # Missing Skills Section
                st.markdown("""
                <div class="section-card">
                    <div class="section-title">
                        <span class="section-title-icon">🔍</span>
                        <span>Missing Skills</span>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Technical Skills")
                    if analysis_result['missing']['technical']:
                        missing_tech_list = list(analysis_result['missing']['technical'])[:10]
                        # Display as bulleted list
                        bullet_list = "\n".join([f"- {skill}" for skill in missing_tech_list])
                        st.markdown(f"**Missing Technical Skills:**\n{bullet_list}")
                    else:
                        create_info_card("✅", "Great Job!", "All technical skills are covered", "success")
                
                with col2:
                    st.markdown("##### Soft Skills")
                    if analysis_result['missing']['soft_skills']:
                        missing_soft_list = list(analysis_result['missing']['soft_skills'])[:10]
                        # Display as bulleted list
                        bullet_list = "\n".join([f"- {skill}" for skill in missing_soft_list])
                        st.markdown(f"**Missing Soft Skills:**\n{bullet_list}")
                    else:
                        create_info_card("✅", "Great Job!", "All soft skills are covered", "success")
                
                st.markdown("</div>", unsafe_allow_html=True)