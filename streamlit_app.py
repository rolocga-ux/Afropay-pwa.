import streamlit as st
import pandas as pd
import numpy as np
import datetime

# Configuration de la page Streamlit
st.set_page_config(
    page_title="AfroPay Bridge - Application & Dashboard v7",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés pour reproduire l'interface sombre (Navy Blue & Gold)
st.markdown("""
<style>
    /* Fond principal sombre */
    .stApp {
        background-color: #081735;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    
    /* Cartes d'information */
    .metric-card {
        background: linear-gradient(135deg, #0d2352 0%, #122f6d 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #1d428a;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }

    .agent-card {
        background: linear-gradient(135deg, #102a5c 0%, #183875 100%);
        border-radius: 12px;
        padding: 18px;
        border: 1px solid #2551a8;
        box-shadow: 0 4px 10px rgba(0,0,0,0.25);
        margin-bottom: 15px;
        height: 100%;
    }

    .card-badge {
        background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
        border: 1px solid #FFC107;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .gold-text {
        color: #FFC107;
        font-weight: bold;
    }
    
    .blue-bg {
        background-color: #1a4fba;
        color: white;
        padding: 15px;
        border-radius: 10px;
    }
    
    .green-bg {
        background-color: #0f7b53;
        color: white;
        padding: 15px;
        border-radius: 10px;
    }
    
    .yellow-bg {
        background-color: #d97706;
        color: white;
        padding: 15px;
        border-radius: 10px;
    }
    
    .purple-bg {
        background-color: #6b21a8;
        color: white;
        padding: 15px;
        border-radius: 10px;
    }

    .red-card-bg {
        background-color: #991b1b;
        color: white;
        padding: 15px;
        border-radius: 10px;
    }
    
    /* Titres et en-têtes */
    h1, h2, h3, h4 {
        color: #FFFFFF !important;
    }
    
    /* Style des boutons */
    .stButton>button {
        width: 100%;
        background-color: #1e5bb8;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 18px;
        font-size: 15px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2b6cb0;
        color: #FFC107;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    
    /* Badge de statut */
    .status-success {
        background-color: rgba(46, 196, 182, 0.2);
        color: #2ec4b6;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid #2ec4b6;
    }
    
    .rate-badge {
        background-color: #d97706;
        color: #ffffff;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .tier-card {
        background-color: #102a5c;
        border-left: 4px solid #FFC107;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    }

    .receipt-box {
        background-color: #0b1d3a;
        border: 1px dashed #2251a3;
        border-radius: 10px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        color: #48bb78;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Function to compute rate based on transaction amount if tiered rate is active
def get_tiered_rate(montant):
    if montant < 100000:
        return 3.0
    elif montant <= 500000:
        return 2.0
    else:
        return 1.0

# Initialisation des états globaux (session_state)
if 'solde_fcfa' not in st.session_state:
    st.session_state.solde_fcfa = 15500.0
if 'taux_cny' not in st.session_state:
    st.session_state.taux_cny = 0.001184
if 'commissions_totales' not in st.session_state:
    st.session_state.commissions_totales = 1845200.0
if 'nb_transactions' not in st.session_state:
    st.session_state.nb_transactions = 343

if 'julia_security_alerts' not in st.session_state:
    st.session_state.julia_security_alerts = [
        {"timestamp": "Aujourd'hui · 12:42", "type": "Tentative de Reverse Engineering (APK)", "niveau": "CRITIQUE", "source": "IP 197.234.12.8", "statut": "Bloqué & Patché par Julia Guard", "action": "Obfuscation réappliquée & IP bannie"},
        {"timestamp": "Aujourd'hui · 09:15", "type": "Injection SQL détectée sur API Alipay", "niveau": "ÉLEVÉ", "source": "Requête malveillante /v1/transfer", "statut": "Bloqué & Patché par Julia Guard", "action": "Requête neutralisée & Pare-feu mis à jour"},
        {"timestamp": "Hier · 22:04", "type": "Appareil Rooté / Jailbreaké détecté", "niveau": "MOYEN", "source": "Session ID #88412", "statut": "Accès Refusé par Julia Guard", "action": "Fermeture de session & Invalidation Token"},
    ]
if 'anti_crack_enabled' not in st.session_state:
    st.session_state.anti_crack_enabled = True
if 'ssl_pinning_active' not in st.session_state:
    st.session_state.ssl_pinning_active = True
if 'aes_256_active' not in st.session_state:
    st.session_state.aes_256_active = True
if 'anti_root_active' not in st.session_state:
    st.session_state.anti_root_active = True

if 'mode_commission' not in st.session_state:
    st.session_state.mode_commission = "Par Tranches de Montant (1% à 4%)"

# Grille de taux de commission configurables (plage 1% à 4%)
if 'taux_commissions' not in st.session_state:
    st.session_state.taux_commissions = {
        "alipay_envoi": 2.0,
        "alipay_reception": 1.5,
        "carte_bancaire": 1.5,
        "mtn": 1.5,
        "orange": 4.0,
        "moov": 2.0,
        "airtel": 2.0
    }

if 'historique_transactions' not in st.session_state:
    st.session_state.historique_transactions = [
        {"id": "TX-9843", "type": "Paiement Carte Visa", "destinataire": "Jean Dupont", "compte": "**** **** **** 4242", "montant_fcfa": 150000, "commission_fcfa": 3000, "taux_pct": 2.0, "date": "Aujourd'hui · 10:14", "statut": "Réussi"},
        {"id": "TX-9842", "type": "Envoyé vers Alipay", "destinataire": "Li Wei", "compte": "liwei88@alipay", "montant_fcfa": 750000, "commission_fcfa": 7500, "taux_pct": 1.0, "date": "Aujourd'hui · 09:21", "statut": "Réussi"},
        {"id": "TX-9841", "type": "Recharge MTN MoMo", "destinataire": "Fatou D.", "compte": "+225 07 01 02 03", "montant_fcfa": 300000, "commission_fcfa": 6000, "taux_pct": 2.0, "date": "Aujourd'hui · 08:15", "statut": "Réussi"},
        {"id": "TX-9840", "type": "Retrait Orange Money", "destinataire": "Awa Koné", "compte": "+225 05 04 05 06", "montant_fcfa": 80000, "commission_fcfa": 2400, "taux_pct": 3.0, "date": "Hier · 16:45", "statut": "Réussi"},
        {"id": "TX-9839", "type": "Reçu d'Alipay", "destinataire": "Chen Yu", "compte": "chenyu_gz@alipay", "montant_fcfa": 282000, "commission_fcfa": 5640, "taux_pct": 2.0, "date": "Hier · 14:32", "statut": "Réussi"},
    ]

# Navigation latérale
st.sidebar.image("https://img.icons8.com/color/96/000000/globe--v1.png", width=60)
st.sidebar.title("AfroPay Bridge 🌍")
st.sidebar.caption("Passerelle Afrique - Chine, Cartes Bancaires & Limova AI")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Accueil Client (Paiement 1-Clic)", 
        "💳 Carte Bancaire (Visa/Mastercard/CB)",
        "💸 Envoyer vers Alipay (Express)", 
        "📱 Recharge & Retrait Mobile Money",
        "📞 Support Vocal & Déblocage Compte (Tom AI)",
        "🛡️ Agent Cyber-Sécurité & Anti-Crack (Julia Guard)",
        "🤖 10 Agents Limova AI & Auto-Update",
        "📊 Portefeuille Commission (Admin)", 
        "⚙️ Configuration Taux & Sécurité (1% à 4%)"
    ]
)

# -----------------------------------------------------------------------------
# 1. ACCUEIL CLIENT
# -----------------------------------------------------------------------------
if menu == "🏠 Accueil Client (Paiement 1-Clic)":
    st.title("🌍 AfroPay Bridge - Tableau de bord Multi-Moyens de Paiement")
    
    # Carte du solde du compte
    solde_cny = st.session_state.solde_fcfa * st.session_state.taux_cny
    
    st.markdown(f"""
    <div class="metric-card" style="text-align: center;">
        <p style="color: #a0aec0; margin-bottom: 5px; font-size: 16px;">Solde du Compte AfroPay</p>
        <h1 style="color: #FFC107; font-size: 42px; margin: 0;">{st.session_state.solde_fcfa:,.0f} FCFA</h1>
        <p style="color: #e2e8f0; font-size: 18px; margin-top: 5px;">≈ {solde_cny:,.2f} CNY &nbsp;•&nbsp; <span style="color: #48bb78;">Taux du jour (1 FCFA = {st.session_state.taux_cny:.6f} CNY)</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Règle de commission en avant
    st.info("💡 **Tous Moyens de Paiement Pris en Charge** : Cartes Bancaires (Visa, Mastercard, UnionPay, CB), Mobile Money & Alipay. Commission dégressive de **1% à 4%** (montants illimités) !")
    
    st.subheader("Actions Rapides")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="red-card-bg" style="text-align: center;">
            <p style="font-size: 24px; margin: 0;">💳</p>
            <p style="font-weight: bold; margin: 5px 0;">Carte Bancaire</p>
            <span class="rate-badge">Frais : 1.0% à 3.0%</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="blue-bg" style="text-align: center;">
            <p style="font-size: 24px; margin: 0;">↗️</p>
            <p style="font-weight: bold; margin: 5px 0;">Envoyer Alipay</p>
            <span class="rate-badge">Frais : 1.0% à 3.0%</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="green-bg" style="text-align: center;">
            <p style="font-size: 24px; margin: 0;">↙️</p>
            <p style="font-weight: bold; margin: 5px 0;">Recevoir Alipay</p>
            <span class="rate-badge">Frais : 1.0% à 2.0%</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="yellow-bg" style="text-align: center;">
            <p style="font-size: 24px; margin: 0;">👛</p>
            <p style="font-weight: bold; margin: 5px 0;">Recharge Mobile</p>
            <span class="rate-badge">Frais : 1.5% à 3.0%</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown("""
        <div class="purple-bg" style="text-align: center;">
            <p style="font-size: 24px; margin: 0;">⬆️</p>
            <p style="font-weight: bold; margin: 5px 0;">Retrait Mobile</p>
            <span class="rate-badge">Frais : 1.5% à 3.0%</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # Cartes & Moyens de Paiement Acceptés
    st.subheader("💳 Cartes Bancaires & Partenaires Acceptés")
    c_b1, c_b2, c_b3, c_b4, c_b5 = st.columns(5)
    c_b1.info("💳 **Visa International**\nToutes banques")
    c_b2.info("💳 **Mastercard**\nToutes banques")
    c_b3.info("💳 **UnionPay (Chine)**\nDirect CNY/FCFA")
    c_b4.info("💳 **Cartes Locales CB**\nUEMOA / CEMAC")
    c_b5.info("📱 **Mobile Money**\nMTN, Orange, Moov, Airtel")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grille par tranches de montant
    st.subheader("Tranches de Commission Selon le Volume (Cartes & Transferts)")
    t_c1, t_c2, t_c3 = st.columns(3)
    with t_c1:
        st.markdown("""
        <div class="tier-card">
            <h4 style="color: #FFC107; margin:0;">Moins de 100 000 FCFA</h4>
            <p style="font-size: 22px; font-weight: bold; margin: 5px 0;">Commission : 3.0%</p>
            <p style="color: #a0aec0; font-size: 13px;">Petits paiements par carte & retraits</p>
        </div>
        """, unsafe_allow_html=True)
    with t_c2:
        st.markdown("""
        <div class="tier-card">
            <h4 style="color: #FFC107; margin:0;">100 000 à 500 000 FCFA</h4>
            <p style="font-size: 22px; font-weight: bold; margin: 5px 0;">Commission : 2.0%</p>
            <p style="color: #a0aec0; font-size: 13px;">Paiements carte & transferts moyens</p>
        </div>
        """, unsafe_allow_html=True)
    with t_c3:
        st.markdown("""
        <div class="tier-card">
            <h4 style="color: #FFC107; margin:0;">Plus de 500 000 FCFA</h4>
            <p style="font-size: 22px; font-weight: bold; margin: 5px 0;">Commission : 1.0%</p>
            <p style="color: #a0aec0; font-size: 13px;">Gros volumes carte, import-export & Alipay</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Transactions récentes
    st.subheader("Transactions Récentes")
    for tx in st.session_state.historique_transactions:
        c_left, c_right = st.columns([3, 1])
        with c_left:
            st.markdown(f"**{tx['type']}** · {tx['destinataire']} <small style='color:#a0aec0;'>({tx.get('id','TX')})</small><br><small style='color: #a0aec0;'>{tx['date']} (Commission {tx['taux_pct']:.1f}%)</small>", unsafe_allow_html=True)
        with c_right:
            st.markdown(f"<span style='color: #FFC107; font-weight: bold;'>{tx['montant_fcfa']:,.0f} FCFA</span><br><span class='status-success'>✓ {tx['statut']}</span>", unsafe_allow_html=True)
        st.divider()

# -----------------------------------------------------------------------------
# 2. CARTE BANCAIRE (VISA / MASTERCARD / UNIONPAY)
# -----------------------------------------------------------------------------
elif menu == "💳 Carte Bancaire (Visa/Mastercard/CB)":
    st.title("💳 Paiement & Recharge par Carte Bancaire")
    st.markdown("Effectuez un paiement, rechargez votre solde ou alimentez directement un transfert vers **Alipay** avec **n'importe quelle carte bancaire** (Visa, Mastercard, UnionPay, CB régionale).")

    tab_card_pay, tab_card_transfer = st.tabs(["💳 Paiement / Recharge Directe par Carte", "🌐 Transfert Carte Bancaire ➔ Alipay Chine"])

    with tab_card_pay:
        st.subheader("Formulaire de Paiement / Recharge par Carte")
        
        col_card_in, col_card_sum = st.columns([1.2, 1])

        with col_card_in:
            type_carte = st.selectbox("Type de Carte Bancaire", ["💳 Visa (International)", "💳 Mastercard (International)", "💳 UnionPay (Chine / Intl)", "💳 Carte Bancaire Régionale (GIM-UEMOA / GIMAC)"])
            nom_porteur = st.text_input("Nom figurant sur la carte", "Jean Dupont")
            num_carte = st.text_input("Numéro de carte (16 chiffres)", "4111 2222 3333 4242")
            
            c_exp, c_cvv = st.columns(2)
            with c_exp:
                exp_carte = st.text_input("Date d'expiration (MM/AA)", "12/28")
            with c_cvv:
                cvv_carte = st.text_input("Code de sécurité CVV", "321", type="password")

            montant_cb = st.number_input("Montant de la transaction (FCFA)", min_value=1.0, value=250000.0, step=5000.0)

            # Calcul du taux de commission
            if st.session_state.mode_commission == "Par Tranches de Montant (1% à 4%)":
                pct_cb = get_tiered_rate(montant_cb)
                explication_cb = f"Taux dégressif automatique ({montant_cb:,.0f} FCFA)"
            else:
                pct_cb = st.session_state.taux_commissions.get('carte_bancaire', 1.5)
                explication_cb = "Taux fixe par carte bancaire"

            comm_cb = montant_cb * (pct_cb / 100.0)
            total_cb = montant_cb + comm_cb

            st.markdown("""
            <div style="background-color: #0f2b5c; padding: 10px; border-radius: 8px; border: 1px solid #1e4f9c; margin-top: 10px;">
                <p style="color: #2ec4b6; margin:0; font-size: 13px;">🔒 <strong>Paiement Sécurisé 3D Secure & PCI-DSS</strong> — Cryptage SSL 256 bits conforme aux normes bancaires internationales.</p>
            </div>
            """, unsafe_allow_html=True)

        with col_card_sum:
            st.subheader("Récapitulatif du Débit Carte")
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="color: #FFC107; font-size: 32px; text-align: center; margin-bottom: 0;">{montant_cb:,.0f} FCFA</h2>
                <p style="text-align: center; color: #cbd5e0; font-size: 16px;">Moyen : {type_carte.split('(')[0]}</p>
                <hr style="border-color: #2d3748;">
                <p><strong>Titulaire :</strong> {nom_porteur}</p>
                <p><strong>Carte :</strong> **** **** **** {num_carte[-4:] if len(num_carte)>=4 else '4242'}</p>
                <p><strong>Commission ({pct_cb:.1f}%) :</strong> <span style="color: #48bb78; font-weight: bold;">{comm_cb:,.0f} FCFA</span></p>
                <small style="color: #a0aec0;">{explication_cb}</small>
                <hr style="border-color: #2d3748;">
                <p><strong>Total prélevé sur la carte :</strong> <span style="font-weight: bold; font-size: 20px; color: #FFC107;">{total_cb:,.0f} FCFA</span></p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("💳 Valider le Paiement par Carte"):
                tx_id_cb = f"TX-{np.random.randint(1000, 9999)}"
                new_tx = {
                    "id": tx_id_cb,
                    "type": f"Paiement {type_carte.split('(')[0].strip()}",
                    "destinataire": nom_porteur,
                    "compte": f"**** **** **** {num_carte[-4:] if len(num_carte)>=4 else '4242'}",
                    "montant_fcfa": montant_cb,
                    "commission_fcfa": comm_cb,
                    "taux_pct": pct_cb,
                    "date": f"Aujourd'hui · {datetime.datetime.now().strftime('%H:%M')}",
                    "statut": "Réussi"
                }
                st.session_state.historique_transactions.insert(0, new_tx)
                st.session_state.solde_fcfa += montant_cb
                st.session_state.commissions_totales += comm_cb
                st.session_state.nb_transactions += 1
                st.session_state.latest_tx_cb = new_tx
                st.success(f"Paiement Carte {tx_id_cb} de {montant_cb:,.0f} FCFA validé avec succès ! Solde crédité.")
                st.balloons()

        if 'latest_tx_cb' in st.session_state:
            st.divider()
            st.subheader("📲 Notifications & Reçus via les Agents IA Limova")
            ltxcb = st.session_state.latest_tx_cb
            col_cb_a1, col_cb_a2 = st.columns(2)
            with col_cb_a1:
                if st.button("💬 Envoyer Reçu Carte par WhatsApp (Charly+)", key="btn_cb_wa"):
                    st.info(f"🤖 **Charly+** : Reçu de paiement carte transmis à {ltxcb['destinataire']} pour un montant de {ltxcb['montant_fcfa']:,.0f} FCFA.")
            with col_cb_a2:
                if st.button("📧 Envoyer Facture PDF par Email (Manue)", key="btn_cb_em"):
                    st.success(f"🤖 **Manue** : Facture bancaire officielle transmise par email sous la référence FACT-{ltxcb['id']}.")

    with tab_card_transfer:
        st.subheader("Transfert Direct : Carte Bancaire ➔ Alipay Chine")
        st.markdown("Payez directement par carte Visa/Mastercard/UnionPay pour envoyer des Yuans (CNY) à un compte Alipay en Chine.")

        c_tr1, c_tr2 = st.columns([1.2, 1])

        with c_tr1:
            nom_carte_tr = st.text_input("Nom de l'émetteur (Carte)", "Jean Dupont", key="tr_nom")
            num_carte_tr = st.text_input("Numéro de carte Visa/Mastercard", "4532 **** **** 8899", key="tr_num")
            nom_alipay_tr = st.text_input("Nom du bénéficiaire Alipay Chine", "Zhang Wei", key="tr_ali_nom")
            compte_alipay_tr = st.text_input("Compte Alipay du bénéficiaire", "zhangwei_sh@alipay", key="tr_ali_acc")
            montant_direct = st.number_input("Montant à envoyer vers la Chine (FCFA)", min_value=1.0, value=1500000.0, step=50000.0, key="tr_m")

            pct_tr = get_tiered_rate(montant_direct) if st.session_state.mode_commission == "Par Tranches de Montant (1% à 4%)" else st.session_state.taux_commissions['alipay_envoi']
            comm_tr = montant_direct * (pct_tr / 100.0)
            total_tr = montant_direct + comm_tr
            cny_tr = montant_direct * st.session_state.taux_cny

        with c_tr2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #FFC107;">Décompte Transfert Carte ➔ Alipay</h3>
                <p><strong>Montant envoi :</strong> {montant_direct:,.0f} FCFA</p>
                <p><strong>Commission ({pct_tr:.1f}%) :</strong> <span style="color: #48bb78;">{comm_tr:,.0f} FCFA</span></p>
                <p><strong>Total débité carte :</strong> {total_tr:,.0f} FCFA</p>
                <hr>
                <p style="background-color: #1a365d; padding: 12px; border-radius: 8px; text-align: center;">
                    <strong>Bénéficiaire reçoit à Shanghai/Guangzhou :</strong><br>
                    <span style="color: #FFC107; font-weight: bold; font-size: 24px;">{cny_tr:,.2f} CNY</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Valider le transfert Carte ➔ Alipay", key="btn_tr_card"):
                tx_id_tr = f"TX-{np.random.randint(1000, 9999)}"
                new_tx = {
                    "id": tx_id_tr,
                    "type": "Transfert Carte ➔ Alipay",
                    "destinataire": nom_alipay_tr,
                    "compte": compte_alipay_tr,
                    "montant_fcfa": montant_direct,
                    "commission_fcfa": comm_tr,
                    "taux_pct": pct_tr,
                    "date": f"Aujourd'hui · {datetime.datetime.now().strftime('%H:%M')}",
                    "statut": "Réussi"
                }
                st.session_state.historique_transactions.insert(0, new_tx)
                st.session_state.commissions_totales += comm_tr
                st.session_state.nb_transactions += 1
                st.success(f"Transfert {tx_id_tr} réussi ! {cny_tr:,.2f} CNY crédités sur le compte Alipay de {nom_alipay_tr}.")
                st.balloons()

# -----------------------------------------------------------------------------
# 3. ENVOYER VERS ALIPAY
# -----------------------------------------------------------------------------
elif menu == "💸 Envoyer vers Alipay (Express)":
    st.title("💸 Envoyer des fonds vers Alipay (Chine)")
    
    col_input, col_summary = st.columns([1.2, 1])
    
    with col_input:
        st.subheader("Calculateur de Transfert (Sommes Libres)")
        moyen_source = st.selectbox("Moyen de paiement source :", ["Solde AfroPay", "💳 Carte Bancaire Visa / Mastercard", "🟡 MTN MoMo", "🟧 Orange Money", "🟦 Moov Money", "🔴 Airtel Money"])
        montant_fcfa = st.number_input("Montant à envoyer (FCFA)", min_value=1.0, value=750000.0, step=5000.0)
        destinataire_nom = st.text_input("Nom du destinataire", "Li Wei")
        destinataire_alipay = st.text_input("Compte Alipay (Email / Tél)", "liwei88@alipay")
        
        # Calcul du taux de commission selon le mode choisi
        if st.session_state.mode_commission == "Par Tranches de Montant (1% à 4%)":
            pct_commission = get_tiered_rate(montant_fcfa)
            explication_rate = f"Taux dégressif automatique selon le montant ({montant_fcfa:,.0f} FCFA)"
        else:
            pct_commission = st.session_state.taux_commissions['alipay_envoi']
            explication_rate = "Taux fixe défini par l'administrateur"
            
        comm_fcfa = montant_fcfa * (pct_commission / 100.0)
        total_debite = montant_fcfa + comm_fcfa
        montant_recu_cny = montant_fcfa * st.session_state.taux_cny
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>Bénéficiaire Alipay</h4>
            <p><strong>Nom:</strong> {destinataire_nom}</p>
            <p><strong>Compte:</strong> {destinataire_alipay} <span class="status-success">✓ Compte vérifié</span></p>
            <p><strong>Source de paiement :</strong> {moyen_source}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_summary:
        st.subheader("Détails du Décompte")
        
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #FFC107; font-size: 32px; text-align: center; margin-bottom: 0;">{montant_fcfa:,.0f} FCFA</h2>
            <p style="text-align: center; color: #cbd5e0; font-size: 18px;">≈ {montant_recu_cny:,.2f} CNY</p>
            <hr style="border-color: #2d3748;">
            <p><strong>Commission de l'app (<span style="color: #FFC107;">{pct_commission:.1f}%</span>) :</strong> <span style="color: #48bb78; font-weight: bold;">{comm_fcfa:,.0f} FCFA</span></p>
            <small style="color: #a0aec0;">{explication_rate}</small>
            <p style="margin-top: 8px;"><strong>Taux appliqué :</strong> 1 FCFA = {st.session_state.taux_cny:.6f} CNY</p>
            <p><strong>Total débité ({moyen_source}) :</strong> <span style="font-weight: bold; font-size: 18px;">{total_debite:,.0f} FCFA</span></p>
            <p style="background-color: #1a365d; padding: 12px; border-radius: 8px; text-align: center; margin-top: 10px;">
                <strong>Le destinataire reçoit en Chine :</strong><br>
                <span style="color: #FFC107; font-weight: bold; font-size: 24px;">{montant_recu_cny:,.2f} CNY</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        tx_id_new = f"TX-{np.random.randint(1000, 9999)}"
        if st.button("🚀 Confirmer l'envoi"):
            new_tx = {
                "id": tx_id_new,
                "type": f"Envoyé vers Alipay ({moyen_source})",
                "destinataire": destinataire_nom,
                "compte": destinataire_alipay,
                "montant_fcfa": montant_fcfa,
                "commission_fcfa": comm_fcfa,
                "taux_pct": pct_commission,
                "date": f"Aujourd'hui · {datetime.datetime.now().strftime('%H:%M')}",
                "statut": "Réussi"
            }
            st.session_state.historique_transactions.insert(0, new_tx)
            st.session_state.commissions_totales += comm_fcfa
            st.session_state.nb_transactions += 1
            st.session_state.latest_tx = new_tx
            st.success(f"Transaction {tx_id_new} réussie ! {montant_recu_cny:,.2f} CNY envoyés à {destinataire_nom}.")
            st.balloons()

    # Module d'envoi automatique de reçu
    if 'latest_tx' in st.session_state and "Alipay" in st.session_state.latest_tx['type']:
        st.divider()
        st.subheader("📲 Envoi Automatique du Reçu via les Agents IA Limova")
        ltx = st.session_state.latest_tx
        
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            if st.button("💬 Envoyer le reçu WhatsApp via Charly+"):
                st.info(f"""🤖 **Charly+ (Agent WhatsApp Limova)** : 
                
💬 *Message WhatsApp envoyé avec succès au destinataire ({ltx['destinataire']}) :*
------------------------------------------------
🟢 **AFROPAY BRIDGE - REÇU DE TRANSFERT**
🆔 Transaction : {ltx['id']}
👤 Bénéficiaire : {ltx['destinataire']} ({ltx['compte']})
💵 Montant envoyé : {ltx['montant_fcfa']:,.0f} FCFA
📊 Commission ({ltx['taux_pct']:.1f}%) : {ltx['commission_fcfa']:,.0f} FCFA
🇨🇳 Montant perçu en Chine : {ltx['montant_fcfa']*st.session_state.taux_cny:,.2f} CNY
✅ Statut : Confirmé & Crédité
------------------------------------------------""")
        with col_w2:
            if st.button("📧 Générer & Envoyer la Facture PDF via Manue"):
                st.success(f"""🤖 **Manue (Agent Comptable Limova)** : 
                
📄 *Facture comptable officielle générée et envoyée par email !*
- Ref Pièce : FACT-{ltx['id']}
- Débit Total Client : {ltx['montant_fcfa'] + ltx['commission_fcfa']:,.0f} FCFA
- TVA & Taxes : Incluses
- Archivage comptable : Effectué dans le Drive AfroPay.""")

# -----------------------------------------------------------------------------
# 4. RECHARGE & RETRAIT MOBILE MONEY
# -----------------------------------------------------------------------------
elif menu == "📱 Recharge & Retrait Mobile Money":
    st.title("📱 Recharge & Retrait via Mobile Money")
    
    tab1, tab2 = st.tabs(["⚡ Recharge / Dépôt", "💸 Retrait"])
    
    with tab1:
        st.subheader("Simulateur de Recharge Mobile Money")
        col_m1, col_m2 = st.columns([1, 1])
        
        with col_m1:
            operateur = st.selectbox("Choisir l'opérateur", ["MTN MoMo", "Orange Money", "Moov Money", "Airtel Money"])
            montant_depot = st.number_input("Montant à recharger (FCFA)", min_value=1.0, value=100000.0, step=5000.0, key="depot")
            client_nom = st.text_input("Nom de l'utilisateur", "Fatou D.", key="client_dep")
            client_tel = st.text_input("Numéro de téléphone", "+225 07 00 11 22", key="tel_dep")
            
            if st.session_state.mode_commission == "Par Tranches de Montant (1% à 4%)":
                rate = get_tiered_rate(montant_depot)
            else:
                if "MTN" in operateur:
                    rate = st.session_state.taux_commissions["mtn"]
                elif "Orange" in operateur:
                    rate = st.session_state.taux_commissions["orange"]
                elif "Moov" in operateur:
                    rate = st.session_state.taux_commissions["moov"]
                else:
                    rate = st.session_state.taux_commissions["airtel"]
                
            comm_val = montant_depot * (rate / 100.0)
            total_paye = montant_depot + comm_val
            
        with col_m2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>Récapitulatif Dépôt ({operateur})</h4>
                <p><strong>Commission appliquée :</strong> <span class="rate-badge">{rate:.1f}%</span></p>
                <p><strong>Montant rechargé :</strong> {montant_depot:,.0f} FCFA</p>
                <p><strong>Frais de service :</strong> <span style="color: #FFC107;">{comm_val:,.0f} FCFA</span></p>
                <hr>
                <p><strong>Total prélevé :</strong> <span style="font-size: 20px; font-weight: bold;">{total_paye:,.0f} FCFA</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Valider la recharge", key="btn_depot"):
                tx_id = f"TX-{np.random.randint(1000, 9999)}"
                new_tx = {
                    "id": tx_id,
                    "type": f"Recharge {operateur}",
                    "destinataire": client_nom,
                    "compte": client_tel,
                    "montant_fcfa": montant_depot,
                    "commission_fcfa": comm_val,
                    "taux_pct": rate,
                    "date": f"Aujourd'hui · {datetime.datetime.now().strftime('%H:%M')}",
                    "statut": "Réussi"
                }
                st.session_state.historique_transactions.insert(0, new_tx)
                st.session_state.commissions_totales += comm_val
                st.session_state.nb_transactions += 1
                st.session_state.latest_tx_mobile = new_tx
                st.success(f"Recharge {tx_id} de {montant_depot:,.0f} FCFA effectuée avec succès pour {client_nom}.")
                
        if 'latest_tx_mobile' in st.session_state:
            ltxm = st.session_state.latest_tx_mobile
            st.divider()
            st.subheader("📱 Notification Instantanée")
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                if st.button("💬 Envoyer reçu SMS/WhatsApp via Charly+"):
                    st.info(f"🤖 **Charly+** : Notification WhatsApp transmise à {ltxm['destinataire']} ({ltxm['compte']}) pour la recharge de {ltxm['montant_fcfa']:,.0f} FCFA.")
            with c_a2:
                if st.button("📊 Archiver reçu comptable via Manue"):
                    st.success(f"🤖 **Manue** : Reçu comptable enregistré sous la référence RECU-{ltxm['id']}.")

    with tab2:
        st.subheader("Simulateur de Retrait Mobile Money")
        col_r1, col_r2 = st.columns([1, 1])
        
        with col_r1:
            op_retrait = st.selectbox("Choisir l'opérateur pour retrait", ["Orange Money", "MTN MoMo", "Moov Money", "Airtel Money"], key="op_ret")
            montant_retrait = st.number_input("Montant du retrait (FCFA)", min_value=1.0, value=200000.0, step=10000.0, key="retrait")
            retrait_nom = st.text_input("Nom du client", "Awa Koné", key="client_ret")
            
            if st.session_state.mode_commission == "Par Tranches de Montant (1% à 4%)":
                rate_ret = get_tiered_rate(montant_retrait)
            else:
                if "Orange" in op_retrait:
                    rate_ret = st.session_state.taux_commissions["orange"]
                elif "MTN" in op_retrait:
                    rate_ret = st.session_state.taux_commissions["mtn"]
                elif "Moov" in op_retrait:
                    rate_ret = st.session_state.taux_commissions["moov"]
                else:
                    rate_ret = st.session_state.taux_commissions["airtel"]
                
            comm_ret = montant_retrait * (rate_ret / 100.0)
            net_recu = montant_retrait - comm_ret
            
        with col_r2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>Récapitulatif Retrait ({op_retrait})</h4>
                <p><strong>Commission appliquée :</strong> <span class="rate-badge">{rate_ret:.1f}%</span></p>
                <p><strong>Montant demandé :</strong> {montant_retrait:,.0f} FCFA</p>
                <p><strong>Frais de retrait ({rate_ret:.1f}%) :</strong> <span style="color: #e53e3e;">{comm_ret:,.0f} FCFA</span></p>
                <hr>
                <p><strong>Montant net versé :</strong> <span style="font-size: 20px; color: #48bb78; font-weight: bold;">{net_recu:,.0f} FCFA</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Valider le retrait", key="btn_retrait"):
                new_tx = {
                    "id": f"TX-{np.random.randint(1000, 9999)}",
                    "type": f"Retrait {op_retrait}",
                    "destinataire": retrait_nom,
                    "montant_fcfa": montant_retrait,
                    "commission_fcfa": comm_ret,
                    "taux_pct": rate_ret,
                    "date": f"Aujourd'hui · {datetime.datetime.now().strftime('%H:%M')}",
                    "statut": "Réussi"
                }
                st.session_state.historique_transactions.insert(0, new_tx)
                st.session_state.commissions_totales += comm_ret
                st.session_state.nb_transactions += 1
                st.success(f"Retrait validé. {net_recu:,.0f} FCFA versés à {retrait_nom}.")

# -----------------------------------------------------------------------------
# 5. LES 8 AGENTS LIMOVA AI & REÇUS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# 5. AGENT CYBER-SÉCURITÉ & ANTI-CRACKING (JULIA GUARD)
# -----------------------------------------------------------------------------
elif menu == "📞 Support Vocal & Déblocage Compte (Tom AI)":
    st.title("📞 Assistant Vocal Multilingue IA (Tom AI) & Centre de Déblocage Sécurisé")
    st.markdown("""
    L'agent **Tom AI** gère l'assistance téléphonique en temps réel dans **toutes les langues** et prend en charge la **procédure de déblocage sécurisé** en cas de blocage de compte (fausses manipulations, tentatives suspectes ou fausses consignes d'IA).
    """)
    
    st.info("🛡️ **Règle de Sécurité Absolue** : Aucun compte ne peut être débloqué sans vérification formelle de l'identité du **propriétaire légitime** (Photo Selfie + Pièce d'Identité/Passeport/Permis + Contrôle biométrique croisé par Tom AI et Julia Guard).")
    
    tab_voice, tab_unblock = st.tabs(["🎙️ Centre d'Appels Vocal Multilingue", "🔓 Procédure de Déblocage de Compte Bloqué (KYC)"])
    
    with tab_voice:
        st.subheader("🎙️ Générateur & Récepteur d'Appels Vocaux IA (Toutes Langues)")
        st.markdown("Testez le module de réponse vocale intelligente capable de générer et de traiter les appels téléphoniques des clients.")
        
        col_v1, col_v2 = st.columns([1, 1.2])
        
        with col_v1:
            st.markdown("#### ⚙️ Configuration de l'Appel Vocal")
            langue_call = st.selectbox(
                "Langue parlée par le client :",
                [
                    "🇫🇷 Français (Afrique de l'Ouest / Centrale)",
                    "🇨🇳 Mandarin / Chinois (Alipay & Fournisseurs)",
                    "🇬🇧 Anglais (Ghana, Nigeria, International)",
                    "🇸🇳 Wolof (Sénégal)",
                    "🇲🇱 Bambara / Dioula (Mali, RCI)",
                    "🇰🇪 Swahili (Afrique de l'Est)",
                    "🇳🇬 Hausa (Nigeria, Niger)",
                    "🇨🇩 Lingala (RDC, Congo)",
                    "🇦🇪 Arabe (Afrique du Nord / Moyen-Orient)"
                ]
            )
            
            type_call = st.radio(
                "Type d'interaction vocale :",
                [
                    "📞 Appel Entrant : Client demande de l'aide sur un transfert Alipay",
                    "📱 Appel Sortant : Alerte de sécurité automatique suite à une fausse manip",
                    "🚨 Assistance Urgente : Compte bloqué suite à une fausse consigne ou erreur PIN"
                ]
            )
            
            num_client_call = st.text_input("Numéro du client à appeler / appelant :", "+225 07 12 34 56 78")
            
            btn_start_call = st.button("📞 Lancer l'Appel Vocal IA avec Tom")
            
        with col_v2:
            st.markdown("#### 🎧 Console d'Appel en Direct & Transcription Tom AI")
            
            if btn_start_call or 'call_active' not in st.session_state:
                st.session_state.call_active = True
                
                st.success(f"🟢 **APPEL EN COURS VIA TOM AI** — Langue : {langue_call.split(' ')[0]} {langue_call.split(' ')[1]}")
                st.caption(f"Ligne sécurisée établie avec {num_client_call} • Latence audio : 12ms")
                
                if "Mandarin" in langue_call:
                    transcription = """👤 Client : 您好，我的Alipay转账未到账，请帮我查询。(Bonjour, mon transfert Alipay n'est pas arrivé.)
🤖 Tom AI (Chinois) : 您好！请不要担心。我正在核对您的交易记录。为保障您的资金安全，请提供您的交易单号。
👤 Client : 好的，单号是 TX-9842。
🤖 Tom AI : 验证成功！您的750,000 FCFA已成功兑换为888.40 CNY并实时存入您的Alipay账户。收据已发送至您的WhatsApp。"""
                elif "Wolof" in langue_call:
                    transcription = """👤 Client : Na nga def, dama beugua xam ndax sama xalis bi dem na Chine? (Bonjour, je veux savoir si mon argent est parti en Chine?)
🤖 Tom AI (Wolof) : Jama rekk! Bul jaaxle, AfroPay mu ngi saytu sa dund. Reçu bi mungi ci sa WhatsApp.
👤 Client : Dieuredief, jëfëndëlikat bu baax la!
🤖 Tom AI : Amul solo, AfroPay mu ngi fi ngir yeen saa sune!"""
                elif "Anglais" in langue_call:
                    transcription = """👤 Client: Hello Tom, I mistakenly typed the wrong PIN code three times and my account is locked.
🤖 Tom AI (English): Hello! Don't panic. To protect your account from fraud, I have placed it in safe mode. I will guide you through the instant ID verification process to restore your access safely."""
                else:
                    transcription = """👤 Client : Bonjour Tom, suite à une fausse manipulation sur mon téléphone, mon compte s'est bloqué.
🤖 Tom AI (Français) : Bonjour ! Soyez rassuré. Par mesure de sécurité anti-fraude, le compte a été suspendu automatiquement. Je vais vous accompagner immédiatement dans la procédure de vérification d'identité pour vous réattribuer l'accès."""
                
                st.markdown(f"""
                <div class="receipt-box">
                    <p style="color: #FFC107; font-weight: bold; margin-bottom: 5px;">📜 Transcription Vocale & Traduction Instantanée :</p>
                    <pre style="white-space: pre-wrap; font-size: 13px; color: #48bb78;">{transcription.strip()}</pre>
                </div>
                """, unsafe_allow_html=True)
                
                st.info("💡 **Synthèse vocale multilingue active** : Tom AI adapte son accent, son vocabulaire régional et son niveau de langage en fonction de la langue sélectionnée.")

    with tab_unblock:
        st.subheader("🔓 Procédure Strictement Sécurisée de Déblocage de Compte")
        st.markdown("""
        En cas de blocage de compte (fausses manipulations, fausses consignes d'IA ou tentatives de connexion suspectes), **Tom AI** impose la vérification complète de la propriété du compte avant toute réactivation.
        """)
        
        st.error("🔒 **STATUT ACTUEL : COMPTE SUSPENDU (SÉCURITÉ ACTIVES)** — Motif : Détection de 3 tentatives PIN erronées ou manipulation suspecte.")
        
        st.markdown("#### 📋 Étapes Obligatoires de Vérification du Propriétaire Légitime")
        
        col_kyc1, col_kyc2 = st.columns(2)
        
        with col_kyc1:
            st.markdown("##### 1. 📸 Photo / Selfie de Contrôle (FaceMatch)")
            st.file_uploader("Prendre ou charger votre photo / selfie en direct :", type=["jpg", "png", "jpeg"], key="selfie")
            st.caption("✓ Analyse Liveness (détection de présence réelle anti-deepfake)")
            
            st.markdown("##### 2. 🪪 Pièce d'Identité Officielle du Titulaire")
            type_id_doc = st.selectbox("Type de document officiel :", ["Carte Nationale d'Identité (CNI)", "Passeport International", "Permis de Conduire"])
            st.file_uploader(f"Charger votre {type_id_doc} (Recto / Verso) :", type=["jpg", "png", "pdf"], key="iddoc")
            
        with col_kyc2:
            st.markdown("##### 3. 🔍 Identification du Titulaire Légitime")
            nom_proprio = st.text_input("Nom & Prénoms complets du propriétaire :", "Jean Toto")
            tel_proprio = st.text_input("Numéro de téléphone lié au compte :", "+225 07 01 02 03")
            piece_num = st.text_input("Numéro de la pièce d'identité :", "CI-2026-984210")
            
            st.markdown("##### 4. 🛡️ Validation de Sécurité par Tom AI & Julia Guard")
            st.checkbox("Je certifie être le propriétaire légitime et agir de mon propre gré.", value=True)
            
            btn_verify_unblock = st.button("🔓 Lancer la Vérification & Débloquer le Compte")
            
        if btn_verify_unblock:
            st.success("✅ **VÉRIFICATION DE SÉCURITÉ REUSSIE À 100% PAR TOM AI & JULIA GUARD !**")
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #48bb78;">🎉 Compte AfroPay Réactivé avec Succès !</h4>
                <ul>
                    <li><b>Biométrie FaceMatch :</b> Correspondance 99.8% avec le selfie du propriétaire ({nom_proprio}).</li>
                    <li><b>Document Validé :</b> {type_id_doc} N° {piece_num} authentifié.</li>
                    <li><b>Titulaire Vérifié :</b> {nom_proprio} ({tel_proprio}) confirmé comme unique propriétaire légitime.</li>
                    <li><b>Sécurité Réseau :</b> Réinitialisation du code PIN et déblocage instantané de l'application.</li>
                </ul>
                <span class="status-success">✓ Certificat de Déblocage N° UNBLOCK-2026-8890 Émis par Tom AI</span>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

elif menu == "🛡️ Agent Cyber-Sécurité & Anti-Crack (Julia Guard)":
    st.title("🛡️ Agent IA Cyber-Sécurité & Bouclier Anti-Cracking - Julia Guard")
    st.markdown("L'agent **Julia Guard (Cyber-AI Limova)** surveille en continu l'application AfroPay Bridge, détecte les failles de sécurité, neutralise les tentatives de piratage/cracking et colmate automatiquement les failles 24h/24.")

    # Status de sécurité global
    st.markdown("""
    <div class="metric-card" style="border-left: 5px solid #2ec4b6; background: linear-gradient(135deg, #0a2540 0%, #10345e 100%);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="color: #FFC107; margin:0;">🟢 Bouclier Anti-Faille & Anti-Crack : ACTIF</h2>
                <p style="color: #cbd5e0; margin-top:5px;">Système 100% sécurisé & crypté — Protection proactive par l'Agent Julia Guard</p>
            </div>
            <div style="text-align: right;">
                <span class="status-success" style="font-size: 14px; padding: 6px 14px;">0 Faille Active</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_sec1, tab_sec2, tab_sec3 = st.tabs(["🔒 Suite Anti-Cracking & Cryptage", "🤖 Agent Julia Guard (Détection 24/7)", "🚨 Journal des Attaques Neutralisées"])

    with tab_sec1:
        st.subheader("1. Protections Anti-Cracking & Anti-Piratage Intégrées")
        st.markdown("Pour empêcher que l'application soit débloquée, décompilée ou piratée ('crackée'), 5 niveaux de protection militaire sont déployés :")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("""
            <div class="agent-card">
                <h4 style="color: #FFC107;">1️⃣ Anti-Reverse Engineering & Obfuscation</h4>
                <p style="color: #a0aec0; font-size: 13px;">Le code binaire APK/IPA est offusqué et les clés cryptographiques sont masquées. Impossibilité de décompiler l'application avec Ghidra, IDA Pro ou APKTool.</p>
                <span class="status-success">✓ Chiffrement Binaire Actif</span>
            </div>
            <br>
            <div class="agent-card">
                <h4 style="color: #FFC107;">2️⃣ Détection Anti-Root & Anti-Jailbreak</h4>
                <p style="color: #a0aec0; font-size: 13px;">L'application bloque automatiquement son exécution sur les téléphones modifiés, rootés, jailbreakés ou exécutés dans des émulateurs malveillants.</p>
                <span class="status-success">✓ Verrouillage Système Actif</span>
            </div>
            <br>
            <div class="agent-card">
                <h4 style="color: #FFC107;">3️⃣ Chiffrement Militaire AES-GCM 256-bit</h4>
                <p style="color: #a0aec0; font-size: 13px;">Toutes les données en mémoire, les transactions et les jetons utilisateur sont chiffrés avec AES-256 de bout en bout.</p>
                <span class="status-success">✓ Clé AES-256 Active</span>
            </div>
            """, unsafe_allow_html=True)

        with col_p2:
            st.markdown("""
            <div class="agent-card">
                <h4 style="color: #FFC107;">4️⃣ SSL/TLS Pinning & Tokens Dynamiques</h4>
                <p style="color: #a0aec0; font-size: 13px;">Empêche l'interception de données par Man-in-the-Middle (Wi-Fi public pirate). Le certificat TLS est verrouillé dans l'app avec tokens HMAC dynamiques.</p>
                <span class="status-success">✓ Epingleur SSL Actif</span>
            </div>
            <br>
            <div class="agent-card">
                <h4 style="color: #FFC107;">5️⃣ Anti-Bruteforce & Authentification Biométrique</h4>
                <p style="color: #a0aec0; font-size: 13px;">Validation instantanée par Face ID / Touch ID / Code PIN à 4 chiffres. Blocage du compte après 3 tentatives erronées.</p>
                <span class="status-success">✓ Biométrie & Anti-Bruteforce</span>
            </div>
            """, unsafe_allow_html=True)

    with tab_sec2:
        st.subheader("2. Simulateur de Détection & Auto-Correction de Failles par Julia Guard")
        st.markdown("Testez la capacité de l'agent **Julia Guard** à détecter un essai d'intrusion, colmater la faille immédiatement et sécuriser l'application :")

        attaque_type = st.selectbox(
            "Simuler une tentative d'attaque ou de faille :",
            [
                "👾 Tentative de décompilation / Cracking de l'APK (Reverse Engineering)",
                "💉 Injection SQL / XSS sur le formulaire de transfert Alipay",
                "🔓 Tentative de contournement d'authentification (Bruteforce PIN)",
                "🌐 Interception de trafic réseau (Attaque Man-in-the-Middle Wi-Fi)",
                "📱 Connexion depuis un Smartphone Rooté / Jailbreaké"
            ]
        )

        if st.button("🚀 Lancer l'attaque simulée & Tester l'Agent Julia Guard"):
            st.info("🤖 **Julia Guard** analyse la requête et scrute la vulnérabilité en millisecondes...")
            
            if "Cracking" in attaque_type:
                st.error("🚨 **ALERTE SÉCURITÉ : Tentative de Reverse Engineering détectée !**")
                st.success("🛡️ **RÉSOLUTION PAR JULIA GUARD :** 'Code APK obfusqué et altéré. Signature binaire non reconnue. La session a été immédiatement verrouillée, l'IP a été bannie et la faille a été neutralisée !'")
                new_alert = {"timestamp": f"Aujourd'hui · {datetime.datetime.now().strftime('%H:%M')}", "type": "Cracking APK / Reverse Eng.", "niveau": "CRITIQUE", "source": "Simulateur App", "statut": "Bloqué & Patché par Julia", "action": "IP Bannie & Obfuscation"}
            elif "SQL" in attaque_type:
                st.error("🚨 **ALERTE SÉCURITÉ : Injection de code malveillant détectée !**")
                st.success("🛡️ **RÉSOLUTION PAR JULIA GUARD :** 'Requête SQL/XSS assainie. Les paramètres de requête ont été isolés et la faille d'entrée a été corrigée en temps réel.'")
                new_alert = {"timestamp": f"Aujourd'hui · {datetime.datetime.now().strftime('%H:%M')}", "type": "Injection SQL / XSS", "niveau": "ÉLEVÉ", "source": "Formulaire Alipay", "statut": "Bloqué & Patché par Julia", "action": "Nettoyage Input & Pare-feu"}
            elif "Bruteforce" in attaque_type:
                st.error("🚨 **ALERTE SÉCURITÉ : Tentatives d'accès répétées anormales !**")
                st.success("🛡️ **RÉSOLUTION PAR JULIA GUARD :** '3 échecs de PIN enregistrés. Compte temporairement gelé pour 15 minutes et demande de vérification Face ID / SMS envoyée à l'administrateur.'")
                new_alert = {"timestamp": f"Aujourd'hui · {datetime.datetime.now().strftime('%H:%M')}", "type": "Bruteforce Code PIN", "niveau": "MOYEN", "source": "Écran Connexion", "statut": "Compte Gelé par Julia", "action": "Déclenchement Face ID obligatoire"}
            elif "Man-in-the-Middle" in attaque_type:
                st.error("🚨 **ALERTE SÉCURITÉ : Certificat SSL réseau modifié !**")
                st.success("🛡️ **RÉSOLUTION PAR JULIA GUARD :** 'Épinglage SSL (SSL Pinning) activé. Le certificat suspect a été rejeté. Connexion cryptée forcée.'")
                new_alert = {"timestamp": f"Aujourd'hui · {datetime.datetime.now().strftime('%H:%M')}", "type": "Attaque Man-in-the-Middle", "niveau": "ÉLEVÉ", "source": "Réseau Wi-Fi Public", "statut": "Connexion Rejetée", "action": "Rejet du certificat & SSL Pinning"}
            else:
                st.error("🚨 **ALERTE SÉCURITÉ : Environnement système non sécurisé (Root/Jailbreak) !**")
                st.success("🛡️ **RÉSOLUTION PAR JULIA GUARD :** 'Système d'exploitation modifié détecté. Accès aux transactions désactivé par précaution.'")
                new_alert = {"timestamp": f"Aujourd'hui · {datetime.datetime.now().strftime('%H:%M')}", "type": "Appareil Rooté / Jailbreaké", "niveau": "MOYEN", "source": "OS Android/iOS", "statut": "Accès Bloqué par Julia", "action": "Interdiction de transaction"}

            st.session_state.julia_security_alerts.insert(0, new_alert)
            st.balloons()

    with tab_sec3:
        st.subheader("3. Journal d'Audit & Incidents Filtrés par Julia Guard")
        st.markdown("Historique en temps réel des failles détectées et colmatées par l'agent **Julia Guard** :")

        for al in st.session_state.julia_security_alerts:
            color_badge = "#e53e3e" if al["niveau"] == "CRITIQUE" else "#d97706"
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin:0; color: #FFC107;">🚨 {al['type']}</h4>
                    <span style="background-color: {color_badge}; color: white; padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: bold;">{al['niveau']}</span>
                </div>
                <p style="margin: 5px 0 0 0; font-size: 13px; color: #a0aec0;">Horodatage : {al['timestamp']} | Source : {al['source']}</p>
                <p style="margin: 5px 0 0 0; color: #48bb78; font-weight: bold;">Statut : {al['statut']}</p>
                <p style="margin: 2px 0 0 0; font-size: 13px; color: #cbd5e0;">Action Corrective Automatique : {al['action']}</p>
            </div>
            """, unsafe_allow_html=True)

elif menu == "🤖 10 Agents Limova AI & Auto-Update":
    st.title("🤖 Équipe d'Agents IA Limova AI & Hub de Reçus Automatiques")
    st.markdown("Découvrez les **10 agents autonomes Limova AI (dont Axel pour les Mises à Jour Automatiques)** et utilisez le hub de notification pour envoyer automatiquement des reçus d'opérations par **WhatsApp (Charly+)** ou **Email (Manue)**.")

    tab_agents, tab_autoupdate_axel, tab_audit_julia, tab_receipts = st.tabs(["🤖 Présentation des 10 Agents", "🔄 Auto-Update & DevOps (Axel)", "⚖️ Audit Juridique & CGU (Julia)", "🧾 Hub d'Automatisation de Reçus & Notifications"])

    agents = [
        {"nom": "Tom", "role": "📞 Support Vocal Multilingue 24/7 & Déblocage Sécurisé (IA Voice & KYC)", "desc": "Génère et répond aux appels vocaux en toutes langues (Français, Mandarin, Anglais, Wolof, Bambara, Swahili, Lingala...). En cas de blocage de compte (fausse manip ou consigne piège), Tom exige selfie, pièce d'identité/passeport/permis et vérifie la propriété du compte avant déblocage.", "icon": "📞"},
        {"nom": "John", "role": "📣 Marketing & Réseaux Sociaux", "desc": "Rédige et programme les posts LinkedIn, Instagram et Facebook, crée des visuels et évalue la qualité.", "icon": "📣"},
        {"nom": "Lou", "role": "✍️ Spécialiste SEO & Rédaction Blog", "desc": "Génère et publie des articles de blog optimisés sur WordPress, gère les mots-clés et le référencement.", "icon": "✍️"},
        {"nom": "Elio", "role": "🚀 Prospection Commerciale B2B", "desc": "Automatisations de prospection ciblée sur LinkedIn et séquences d'emails pour commerçants import-export.", "icon": "🚀"},
        {"nom": "Charly+", "role": "💬 Assistant Général Polyvalent & WhatsApp", "desc": "Répond aux requêtes d'équipe, envoie des reçus instantanés sur WhatsApp et assiste au quotidien.", "icon": "💬"},
        {"nom": "Manue", "role": "📊 Comptabilité & Suivi Facturation", "desc": "Analyse les pièces comptables, calcule les bilans, édite les reçus officiels et factures PDF.", "icon": "📊"},
        {"nom": "Julia", "role": "⚖️🛡️ Juridique, Conformité & Cyber-Sécurité (Julia Guard)", "desc": "Supervise les CGU, détecte les failles de sécurité, bloque les piratages/cracking et patche les failles 24/7.", "icon": "🛡️"},
        {"nom": "Rony", "role": "👥 Recrutement & Ressources Humaines", "desc": "Rédige les fiches de poste, pré-qualifie les candidats et gère le sourcing RH pour le réseau AfroPay.", "icon": "👥"},
        {"nom": "Sora", "role": "🇨🇳 Concierge Import-Export & Sourcing Chine", "desc": "Vérifie la légitimité des fournisseurs chinois sur Alipay/1688/Taobao, traduit les factures proforma et estime les frais de douane.", "icon": "🇨🇳"},
        {"nom": "Axel", "role": "🔄 DevOps & Auto-Update Sécurisé (DevSecOps)", "desc": "Collabore avec Julia Guard pour auditer, chiffrer (AES-256/Ed25519) et déployer chaque mise à jour sans faille anti-crack.", "icon": "🔄"},
    ]

    with tab_agents:
        st.subheader("Les 8 Assistants Virtuels Intégrés")
        col_a1, col_a2 = st.columns(2)
        for idx, ag in enumerate(agents):
            target_col = col_a1 if idx % 2 == 0 else col_a2
            with target_col:
                st.markdown(f"""
                <div class="agent-card">
                    <h3 style="color: #FFC107; margin-top:0;">{ag['icon']} {ag['nom']}</h3>
                    <p style="color: #2ec4b6; font-weight: bold; font-size: 14px; margin-bottom: 8px;">{ag['role']}</p>
                    <p style="color: #e2e8f0; font-size: 14px;">{ag['desc']}</p>
                    <span class="status-success">🟢 Actif & Disponible 24/7</span>
                </div>
                """, unsafe_allow_html=True)

    
    with tab_autoupdate_axel:
        st.subheader("🔄 Système de Mise à Jour Automatique (Agent Axel - DevOps AI)")
        st.markdown("""
        L'agent **Axel (DevOps & Auto-Update Limova AI)** surveille l'intégrité de l'application, applique automatiquement les correctifs de sécurité transmis par **Julia Guard** et déploie les nouvelles fonctionnalités en temps réel via la technologie **Over-The-Air (OTA)** sans nécessiter de téléchargement manuel depuis le Play Store ou l'App Store.
        """)

        col_ax1, col_ax2 = st.columns([1.2, 1])

        with col_ax1:
            st.markdown("#### 📲 Module de Déploiement & Patchs Instantanés")
            st.info("🟢 **Statut Système : v10.0-PROD (À jour)** — canal de distribution sécurisé HTTPS / TLS 1.3")
            
            canal = st.selectbox("Canal de Mise à Jour :", ["Production (Stable - OTA)", "Bêta Testeurs (Early Access)", "Hotfix Sécurité Prioritaire"])
            
            st.markdown("**Paramètres de Mise à Jour Automatique :**")
            auto_download = st.checkbox("Téléchargement automatique en arrière-plan (Wi-Fi & Data)", value=True)
            auto_apply = st.checkbox("Application automatique des patchs de sécurité (0 interruption)", value=True)
            check_integrity = st.checkbox("Vérification d'empreinte cryptographique SHA-256 avant installation", value=True)

            btn_check_update = st.button("🔍 Rechercher une Mise à Jour avec l'Agent Axel")

        with col_ax2:
            st.markdown("#### 📊 Journal des Mises à Jour & Builds")

            if btn_check_update or 'axel_updated' not in st.session_state:
                st.session_state.axel_updated = True
                st.success("✅ **SYSTÈME À JOUR — Version 10.0.4**")
                st.markdown("""
                <div class="metric-card">
                    <h4 style="color: #FFC107;">📋 Dépôt de Patch Axel (Dernières MAJ Automatiques)</h4>
                    <ul>
                        <li><b>v10.0.4 (Aujourd'hui · 02:15) :</b> Auto-patch de sécurité transmis par Julia Guard (Injections neutralisées).</li>
                        <li><b>v10.0.3 (Hier · 18:40) :</b> Optimisation du temps de réponse du paiement Carte 1-Clic (< 0.8s).</li>
                        <li><b>v10.0.2 (19/09/2026) :</b> Mise à jour automatique des taux de change CNY/FCFA en direct.</li>
                        <li><b>v10.0.1 (18/09/2026) :</b> Intégration du module d'authentification biométrique Face ID / Touch ID.</li>
                    </ul>
                    <span class="status-success">✓ Signature Cryptographique Valide (SHA-256 Ok)</span>
                </div>
                """, unsafe_allow_html=True)
                st.info("💡 **Mode Over-The-Air (OTA) Actif** : Vos utilisateurs reçoivent les améliorations et correctifs directement au lancement de l'application sans aucune action requise !")

    with tab_audit_julia:
        st.subheader("⚖️ Validation des Mentions Légales & CGU par l'Agent Julia")
        st.markdown("""
        L'agent **Julia (Juridique & Conformité Limova AI)** passe en revue et certifie en temps réel les documents juridiques, les mentions légales et les Conditions Générales d'Utilisation (CGU) d'AfroPay Bridge.
        """)

        col_j1, col_j2 = st.columns([1.2, 1])

        with col_j1:
            st.markdown("#### 🔍 Sélection de l'élément à auditer par Julia")
            doc_type = st.radio(
                "Document ou composant réglementaire :",
                [
                    "📜 Conditions Générales d'Utilisation (CGU / CGV)",
                    "⚖️ Mentions Légales & Éditeur de la Plateforme",
                    "🔒 Politique de Confidentialité & Protection des Données (RGPD/APDP)",
                    "🛡️ Cadre de Conformité KYC / AML (Anti-Blanchiment)"
                ]
            )

            strict_level = st.select_slider(
                "Niveau de rigueur du contrôle de conformité :",
                options=["Standard", "Sévère (Banque centrale)", "Ultra-Strict (International PBOC/PCI-DSS)"],
                value="Sévère (Banque centrale)"
            )

            btn_run_julia = st.button("⚖️ Exécuter l'Audit de Conformité Juridique avec Julia")

        with col_j2:
            st.markdown("#### 📋 Certificat de Validation Officiel par Julia")

            if btn_run_julia or 'julia_certified' not in st.session_state:
                st.session_state.julia_certified = True
                if "CGU" in doc_type:
                    st.success("✅ **STATUS : CGU / CGV VALIDÉES ET CONFORMES (Score : 99/100)**")
                    st.markdown("""
                    <div class="metric-card">
                        <h4 style="color: #FFC107;">📜 Synthèse d'Audit CGU / CGV par Julia</h4>
                        <ul>
                            <li><b>Tarification (1% - 4%) :</b> Information précontractuelle claire, affichage en direct avant validation de chaque envoi.</li>
                            <li><b>Acceptation des Cartes Bancaires :</b> Mandat de traitement conforme aux normes d'acquisition monétique (Visa / Mastercard).</li>
                            <li><b>Transferts Alipay :</b> Responsabilités de conversion FCFA/CNY clairement délimitées.</li>
                            <li><b>Droit de Rétractation :</b> Conforme à l'exemption légale sur les services financiers à exécution immédiate.</li>
                        </ul>
                        <span class="status-success">✓ Tampon d'Approbation Juridique Julia (Legal AI)</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "Mentions Légales" in doc_type:
                    st.success("✅ **STATUS : MENTIONS LÉGALES VALIDÉES (Score : 98/100)**")
                    st.markdown("""
                    <div class="metric-card">
                        <h4 style="color: #FFC107;">⚖️ Mentions Légales Officiellement Certifiées</h4>
                        <ul>
                            <li><b>Raison Sociale :</b> AfroPay Bridge SAS — Capital Social : 100 000 000 FCFA.</li>
                            <li><b>Partenaires Financiers :</b> Établissements de Monnaie Électronique (EME) agréés BCEAO / BEAC.</li>
                            <li><b>Directeur de Publication :</b> Jean Toto (Propriétaire / Fondateur).</li>
                            <li><b>Hébergement :</b> Infrastructure sécurisée certifiée ISO/IEC 27001 & PCI-DSS Level 1.</li>
                        </ul>
                        <span class="status-success">✓ Tampon d'Approbation Juridique Julia (Legal AI)</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif "Confidentialité" in doc_type:
                    st.success("✅ **STATUS : CONFORMITÉ RGPD & PROTECTION DES DONNÉES (Score : 100/100)**")
                    st.markdown("""
                    <div class="metric-card">
                        <h4 style="color: #FFC107;">🔒 Rapport de Protection des Données Personnelles</h4>
                        <ul>
                            <li><b>Chiffrement :</b> Cryptage AES-256 de bout en bout des transactions bancaires et téléphones.</li>
                            <li><b>Données Biométriques (Face ID) :</b> Traitement local sécurisé sans stockage externe.</li>
                            <li><b>Consentement :</b> Consentement explicite requis pour les notifications WhatsApp/Email des reçus.</li>
                        </ul>
                        <span class="status-success">✓ Tampon d'Approbation Juridique Julia (Legal AI)</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.success("✅ **STATUS : CONFORMITÉ AML / KYC CERTIFIÉE (Score : 100/100)**")
                    st.markdown("""
                    <div class="metric-card">
                        <h4 style="color: #FFC107;">🛡️ Dispositif LCB-FT (Lutte Contre le Blanchiment)</h4>
                        <ul>
                            <li><b>Vérification des Destinataires :</b> Contrôle préalable automatisé des comptes Alipay et cartes.</li>
                            <li><b>Monitoring des Transactions :</b> Surveillance en temps réel du fractionnement anormal de sommes.</li>
                            <li><b>Conservation des Registres :</b> Archivage sécurisé pendant 5 ans conformément aux directives financières.</li>
                        </ul>
                        <span class="status-success">✓ Conforme aux recommandations du GAFI</span>
                    </div>
                    """, unsafe_allow_html=True)


    with tab_receipts:
        st.subheader("🧾 Générateur & Envoyeur Automatique de Reçus")
        st.markdown("Sélectionnez n'importe quelle transaction enregistrée pour générer et expédier un reçu officiel via nos agents d'IA.")

        options_tx = [f"{t.get('id','TX')} | {t['type']} - {t['destinataire']} ({t['montant_fcfa']:,.0f} FCFA)" for t in st.session_state.historique_transactions]
        tx_selected_str = st.selectbox("Choisir une transaction :", options_tx)
        
        idx_sel = options_tx.index(tx_selected_str)
        selected_tx = st.session_state.historique_transactions[idx_sel]

        st.markdown(f"""
        <div class="metric-card">
            <h4>Détails de la Transaction Sélectionnée ({selected_tx.get('id','TX')})</h4>
            <p><strong>Type :</strong> {selected_tx['type']}</p>
            <p><strong>Bénéficiaire :</strong> {selected_tx['destinataire']} ({selected_tx.get('compte', 'Compte vérifié')})</p>
            <p><strong>Montant :</strong> {selected_tx['montant_fcfa']:,.0f} FCFA</p>
            <p><strong>Commission prélevée ({selected_tx['taux_pct']:.1f}%) :</strong> {selected_tx['commission_fcfa']:,.0f} FCFA</p>
            <p><strong>Date & Heure :</strong> {selected_tx['date']}</p>
        </div>
        """, unsafe_allow_html=True)

        col_send1, col_send2 = st.columns(2)

        with col_send1:
            st.markdown("#### 📱 Envoi WhatsApp via Charly+")
            num_whatsapp = st.text_input("Numéro WhatsApp destinataire :", "+225 07 88 99 00 11")
            if st.button("📲 Envoyer Reçu WhatsApp"):
                cny_val = selected_tx['montant_fcfa'] * st.session_state.taux_cny
                msg = f"""🟢 *AFROPAY BRIDGE - REÇU OFFICIEL*
Ref : {selected_tx.get('id', 'TX-1001')}
Client : {selected_tx['destinataire']}
Montant : {selected_tx['montant_fcfa']:,.0f} FCFA (≈ {cny_val:,.2f} CNY)
Commission : {selected_tx['commission_fcfa']:,.0f} FCFA ({selected_tx['taux_pct']:.1f}%)
Statut : {selected_tx['statut']}
Merci pour votre confiance ! 🌍"""
                st.success(f"Message transmis par **Charly+** à {num_whatsapp} !")
                st.markdown(f'<div class="receipt-box"><pre>{msg}</pre></div>', unsafe_allow_html=True)

        with col_send2:
            st.markdown("#### 📧 Envoi Facture Email via Manue")
            email_client = st.text_input("Adresse email du destinataire :", "client@afropay.com")
            if st.button("📧 Expédier la Facture PDF"):
                st.success(f"Facture officielle PDF transmise par l'agent **Manue** à {email_client} !")
                st.info(f"📄 Document joint : `Facture_AfroPay_{selected_tx.get('id', 'TX-1001')}.pdf`")

# -----------------------------------------------------------------------------
# 6. PORTEFEUILLE COMMISSION (ADMIN)
# -----------------------------------------------------------------------------
elif menu == "📊 Portefeuille Commission (Admin)":
    st.title("📊 Espace Administrateur - Portefeuille Commission")
    
    st.markdown("""
    <div style="background-color: #1a202c; padding: 10px 15px; border-radius: 8px; margin-bottom: 20px;">
        <span style="color: #48bb78;">🔒 Accès Administrateur Authentifié (Face ID)</span> — <strong>Jean Toto · Propriétaire</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Général
    st.markdown(f"""
    <div class="metric-card" style="text-align: center; background: linear-gradient(135deg, #1b365d 0%, #0d2240 100%);">
        <p style="color: #a0aec0; margin-bottom: 5px;">Commissions Totales Cumulées</p>
        <h1 style="color: #FFC107; font-size: 40px; margin: 0;">{st.session_state.commissions_totales:,.0f} FCFA</h1>
        <p style="color: #cbd5e0; margin-top: 5px;">Depuis le lancement &nbsp;•&nbsp; <strong>{st.session_state.nb_transactions} transactions</strong> effectuées</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3 Stat Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <p style="color: #a0aec0; font-size: 14px; margin: 0;">📅 Aujourd'hui</p>
            <h2 style="color: #FFC107; margin: 5px 0;">82 500 FCFA</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <p style="color: #a0aec0; font-size: 14px; margin: 0;">📆 Cette semaine</p>
            <h2 style="color: #FFC107; margin: 5px 0;">348 000 FCFA</h2>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card">
            <p style="color: #a0aec0; font-size: 14px; margin: 0;">🗓️ Ce mois</p>
            <h2 style="color: #FFC107; margin: 5px 0;">1 210 400 FCFA</h2>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Graphique des commissions par jour
    st.subheader("📈 Commissions par jour (7 derniers jours)")
    jours = ['Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim', 'Lun']
    commissions_jours = [70000, 105000, 135000, 92000, 81000, 58000, 148000]
    
    df_chart = pd.DataFrame({
        'Jour': jours,
        'Commission (FCFA)': commissions_jours
    })
    
    st.bar_chart(df_chart.set_index('Jour'), color="#FFC107")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Historique détaillé des commissions
    st.subheader("📜 Historique des Commissions Prélevées")
    
    for tx in st.session_state.historique_transactions:
        col_icon, col_details, col_rate, col_amount = st.columns([0.5, 3, 1, 1.5])
        with col_icon:
            st.markdown("🔹")
        with col_details:
            st.markdown(f"**{tx['type']}** · {tx['destinataire']} <small style='color:#a0aec0;'>({tx.get('id','TX')})</small><br><small style='color: #a0aec0;'>{tx['date']}</small>", unsafe_allow_html=True)
        with col_rate:
            st.markdown(f"<span style='background-color: #2b6cb0; color: white; padding: 2px 8px; border-radius: 12px; font-weight: bold;'>{tx['taux_pct']:.1f}%</span>", unsafe_allow_html=True)
        with col_amount:
            st.markdown(f"<span style='color: #FFC107; font-weight: bold; font-size: 16px;'>+{tx['commission_fcfa']:,.0f} FCFA</span>", unsafe_allow_html=True)
        st.divider()

# -----------------------------------------------------------------------------
# 7. CONFIGURATION TAUX & COMMISSIONS (1% à 4%)
# -----------------------------------------------------------------------------
elif menu == "⚙️ Configuration Taux & Sécurité (1% à 4%)":
    st.title("⚙️ Configuration du Barème de Commission (1% à 4%)")
    st.markdown("Paramétrez ici le comportement du système de commission adapté à la règle de **1% à 4%**.")
    
    st.subheader("1. Mode de Calcul de la Commission")
    mode_choisi = st.radio(
        "Sélectionner la logique d'application des frais :",
        ["Par Tranches de Montant (1% à 4%)", "Taux Fixe Séparé par Opérateur (1% à 4%)"],
        index=0 if st.session_state.mode_commission == "Par Tranches de Montant (1% à 4%)" else 1
    )
    st.session_state.mode_commission = mode_choisi
    
    st.divider()
    
    if mode_choisi == "Par Tranches de Montant (1% à 4%)":
        st.subheader("2. Grille Tarifaire Dégressive Automatique")
        st.markdown("""
        Le taux est calculé **automatiquement en fonction du montant de la transaction** :
        - 🟢 **> 500 000 FCFA** ➔ **1.0 %** *(Grandes transactions commerçants)*
        - 🟡 **100 000 à 500 000 FCFA** ➔ **2.0 %** *(Transactions de taille moyenne)*
        - 🔴 **< 100 000 FCFA** ➔ **3.0 %** *(Petits transferts)*
        """)
    else:
        st.subheader("2. Ajustement des Taux Fixes par Canal (Strictement 1.0% à 3.0%)")
        
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.markdown("#### 🇨🇳 Alipay & Cartes Bancaires")
            t_alipay_env = st.slider(
                "Envoi Alipay (%)", 
                min_value=1.0, max_value=3.0, 
                value=float(st.session_state.taux_commissions["alipay_envoi"]), 
                step=0.1
            )
            t_alipay_rec = st.slider(
                "Réception Alipay (%)", 
                min_value=1.0, max_value=3.0, 
                value=float(st.session_state.taux_commissions["alipay_reception"]), 
                step=0.1
            )
            t_cb = st.slider(
                "Cartes Bancaires Visa/Mastercard (%)", 
                min_value=1.0, max_value=3.0, 
                value=float(st.session_state.taux_commissions.get("carte_bancaire", 1.5)), 
                step=0.1
            )
            
        with c_right:
            st.markdown("#### 📱 Mobile Money Afrique")
            t_mtn = st.slider(
                "MTN MoMo (%)", 
                min_value=1.0, max_value=3.0, 
                value=float(st.session_state.taux_commissions["mtn"]), 
                step=0.1
            )
            t_orange = st.slider(
                "Orange Money (%)", 
                min_value=1.0, max_value=3.0, 
                value=float(st.session_state.taux_commissions["orange"]), 
                step=0.1
            )
            t_moov = st.slider(
                "Moov Money (%)", 
                min_value=1.0, max_value=3.0, 
                value=float(st.session_state.taux_commissions["moov"]), 
                step=0.1
            )
            t_airtel = st.slider(
                "Airtel Money (%)", 
                min_value=1.0, max_value=3.0, 
                value=float(st.session_state.taux_commissions["airtel"]), 
                step=0.1
            )
            
        if st.button("💾 Enregistrer la grille fixe (1% à 4%)"):
            st.session_state.taux_commissions["alipay_envoi"] = t_alipay_env
            st.session_state.taux_commissions["alipay_reception"] = t_alipay_rec
            st.session_state.taux_commissions["carte_bancaire"] = t_cb
            st.session_state.taux_commissions["mtn"] = t_mtn
            st.session_state.taux_commissions["orange"] = t_orange
            st.session_state.taux_commissions["moov"] = t_moov
            st.session_state.taux_commissions["airtel"] = t_airtel
            st.success("Taux enregistrés avec succès !")

    st.divider()
    st.subheader("3. Testeur & Simulateur de Montants Personnalisés Libres")
    test_montant = st.number_input("Saisir n'importe quelle somme personnalisée (FCFA) :", min_value=1.0, value=1250000.0, step=10000.0)
    rate_test = get_tiered_rate(test_montant) if mode_choisi == "Par Tranches de Montant (1% à 4%)" else st.session_state.taux_commissions["alipay_envoi"]
    comm_test = test_montant * (rate_test / 100.0)
    cny_test = test_montant * st.session_state.taux_cny
    
    st.info(f"Pour **{test_montant:,.0f} FCFA** ➔ Taux : **{rate_test:.1f}%** | Commission : **{comm_test:,.0f} FCFA** | Le destinataire reçoit : **{cny_test:,.2f} CNY**")

st.markdown("<br><hr><p style='text-align: center; color: #718096;'>AfroPay Bridge © 2026 — Intégration Cartes Bancaires & Agents IA Limova.</p>", unsafe_allow_html=True)


# --- V15 ENHANCEMENTS ATTACHED ---
