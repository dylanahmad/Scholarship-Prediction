import numpy as np
import pandas as pd
import skfuzzy as fuz
import csv
import streamlit as st

# Load the dataset



def OurRange(_lo, _hi, _step):
    return np.arange(_lo, _hi, _step)

# 500k sampe 6,9jt
xto = OurRange(500000, 6900001, 1000)
rto = np.array([
    [500000, 2000000, 4500000],
    [4000000, 5000000, 6000000],
    [5500000, 6500000, 6900000]
], dtype=object)

xips = OurRange(0, 4.01, 0.01)
rips = np.array([
    [0, 0, 1.4, 2.8],
    [2.4, 2.9, 3.8],
    [3.7, 3.9, 4, 4]
], dtype=object)
xipk = OurRange(0, 4.01, 0.01)
ripk = np.array([
    [0, 0, 1.4, 2.8],
    [2.4, 2.9, 3.8],
    [3.6, 3.9, 4, 4]
], dtype=object)
def MembershipFunc1 (_rule, _our_range):
    low = fuz.trimf(_our_range, _rule[0])
    middle = fuz.trimf(_our_range, _rule[1])
    high = fuz.trimf(_our_range, _rule[2])
    return low, middle, high

def MembershipFunc2(_rule, _our_range):
    low = fuz.trapmf(_our_range, _rule[0])
    middle = fuz.trimf(_our_range, _rule[1])
    high = fuz.trapmf(_our_range, _rule[2])
    return low, middle, high

def MembershipDeg1(_range, _lo, _mi, _hi, _val):
    low = fuz.interp_membership(_range, _lo, _val)
    middle = fuz.interp_membership(_range, _mi, _val)
    high = fuz.interp_membership(_range, _hi, _val)
    return low, middle, high

def Status1(_membership, _label0, _label1, _label2):
    if _membership[0] > _membership[1] and _membership[0] > _membership[2]:
        return _label0
    elif _membership[1] > _membership[0] and _membership[1] > _membership[2]:
        return _label1
    elif _membership[2] > _membership[0] and _membership[2] > _membership[1]:
        return _label2
    return 'unknown'

def RuleBased(_ipk_status, _ips_status):
    if ((_ips_status == 'rendah' or _ips_status == 'sedang' or _ips_status == 'tinggi') and _ipk_status == 'rendah') or (_ips_status == 'rendah' and (_ipk_status == 'rendah' or _ipk_status == 'sedang' or _ipk_status == 'tinggi')) :
        return "tidak diterima"
    elif ((_ips_status == 'sedang' or _ips_status == 'tinggi') and (_ipk_status == 'sedang' or _ipk_status == 'tinggi')):
        return "diterima"
    else:
        return "unknown"

def PotonganUkt(_ipk_status, _ips_status):
    print(_ipk_status, _ips_status)
    potongan_status = ""
    potongan_beasiswa = 0
    if RuleBased(_ipk_status, _ips_status) == 'diterima':
        if _ipk_status == 'tinggi' and _ips_status == 'tinggi':  # Jika IPK 4, UKT gratis
            potongan_status = "Potongan UKT Fully Funded 100%"
            potongan_beasiswa = 100
        elif _ipk_status == 'sedang' and _ips_status == 'tinggi' or _ipk_status == 'tinggi' and _ips_status == 'sedang':  # Jika IPK di bawah 4 dan UKT sedikit
            potongan_status = "Potongan UKT Parsial sebesar 50%"
            potongan_beasiswa = 50
        elif _ipk_status == 'sedang' and _ips_status == 'sedang':  # Jika IPK di bawah 4 dan UKT sedang
            potongan_status = "Potongan UKT Parsial sebesar 25%"
            potongan_beasiswa = 25
    else:
        potongan_status = "Tidak mendapatkan potongan UKT"
        potongan_beasiswa = 0
    
    return potongan_status, potongan_beasiswa

lo_to, mi_to, hi_to = MembershipFunc1(rto, xto)
lo_ipk, mi_ipk, hi_ipk = MembershipFunc2(ripk, xipk)
lo_ips, mi_ips, hi_ips = MembershipFunc2(rips, xips)
# Streamlit app for new data prediction
st.title(' PREDIKSI PENERIMA BEASISWA BERPRESTASI DI UNIVERSITAS SINGAPERBANGSA KARAWANG (UNSIKA)')
@st.experimental_fragment
def fragment():
    with st.form(key='prediction_form'):
        
        input_ipk = st.number_input('Enter IPK:', min_value=0.0, max_value=4.0, step=0.01)
        input_ips = st.number_input('Enter IPS:', min_value=0.0, max_value=4.0, step=0.01)
        input_ukt = st.number_input('Besaran UKT:', min_value=500000, max_value=15000000, step=100000)
    
        submit_button = st.form_submit_button(label='Submit')
        if submit_button:
            new_ipk_member = MembershipDeg1(xipk, lo_ipk, mi_ipk, hi_ipk, input_ipk)
            new_to_member = MembershipDeg1(xto, lo_to, mi_to, hi_to, input_ukt)
            new_to_status = Status1(new_to_member, 'sedikit', 'sedang', 'banyak')
            new_ipk_status = Status1(new_ipk_member, 'rendah', 'sedang', 'tinggi')
            
            new_ips_member = MembershipDeg1(xips, lo_ips, mi_ips, hi_ips, input_ips)
            new_ips_status = Status1(new_ips_member, 'rendah', 'sedang', 'tinggi')
            
            new_status = RuleBased(new_ipk_status, new_ips_status)
            
            st.write(f'IPK Status: {new_ipk_status}')
            st.write(f'IPS Status: {new_ips_status}')
            st.write(f'Status Beasiswa: {new_status}')
            #ukt potongan
            st.write(f'Potongan UKT: {PotonganUkt(new_ipk_status, new_ips_status)[0]}')

input_ukt = None  # Define input_ukt outside the fragment function
fragment()
